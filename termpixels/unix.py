import termios
import tty
import sys
import os
import threading 
import queue
import signal
import fcntl
import struct
import selectors
from queue import Queue
from termpixels.color import color_to_16, color_to_256
from termpixels.observable import Observable
from termpixels.terminfo import Terminfo
from termpixels.unix_keys import Key, Mouse, make_key_parser, make_mouse_parser
from termpixels.util import terminal_len

def detect_truecolor(terminfo=None):
    """Detect true-color (24-bit) color support
    """
    if "COLORTERM" in os.environ:
        return True
    if "truecolor" in os.environ["TERM"]:
        return True
    if terminfo is not None:
        if terminfo.flag("RGB"):
            return True
    return False

def detect_color_mode(terminfo=None):
    if detect_truecolor(terminfo):
        return "truecolor"
    if not terminfo:
        return "16-color" # hopefully

    if terminfo.num("colors") == 256:
        return "256-color"
    if terminfo.num("colors") >= 8:
        return "16-color" 
    return "monochrome"

class UnixBackend(Observable):
    def __init__(self):
        super().__init__()
        self._ti = Terminfo()
        self.color_mode = detect_color_mode(self._ti)
        self._cursor_pos = (0, 0)
        self._fg = None
        self._bg = None
        self._show_cursor = None
        self._mouse_tracking = None
        self.size_dirty = True 
        self._size = None
        self._window_title = None

    @property
    def terminal_name(self):
        return self._ti.termname
    
    @property
    def size(self):
        if self.size_dirty:
            self.update_size()
        return self._size
    
    def update_size(self):
        result = fcntl.ioctl(sys.stdout, termios.TIOCGWINSZ, struct.pack("HHHH", 0, 0, 0, 0))
        r, c, _, _ = struct.unpack("HHHH", result)
        self._size = (c, r) 
        self.size_dirty = False
    
    @property
    def cursor_pos(self):
        return self._cursor_pos
    
    @cursor_pos.setter
    def cursor_pos(self, pos):
        if self._cursor_pos != pos:
            col, row = pos
            self.write_escape(self._ti.parameterize("cup", row, col, require=True)) 
            self._cursor_pos = pos

    @property
    def show_cursor(self):
        return self._show_cursor
    
    @show_cursor.setter
    def show_cursor(self, show_cursor):
        if self._show_cursor != show_cursor:
            if show_cursor:
                self.write_escape(self._ti.parameterize("cnorm"))
            else:
                self.write_escape(self._ti.parameterize("civis"))
            self._show_cursor = show_cursor
    
    @property
    def fg(self):
        return self._fg
    
    @fg.setter
    def fg(self, color):
        if self._fg != color:
            if self.color_mode == "truecolor":
                self.write_escape("\x1b[38;2;{};{};{}m".format(color.r, color.g, color.b))
            else:
                self.write_escape(self._ti.parameterize("setaf", self.color_auto(color)))
            self._fg = color
    
    @property
    def bg(self):
        return self._bg
    
    @bg.setter
    def bg(self, color):
        if self._bg != color:
            if self.color_mode == "truecolor":
                self.write_escape("\x1b[48;2;{};{};{}m".format(color.r, color.g, color.b))
            else:
                self.write_escape(self._ti.parameterize("setab", self.color_auto(color)))
            self._bg = color
    
    @property
    def application_keypad(self):
        return self._application_keypad
    
    @application_keypad.setter
    def application_keypad(self, enabled):
        self._application_keypad = enabled
        self.write_escape(self._ti.parameterize("smkx" if enabled else "rmkx"))
    
    @property
    def mouse_tracking(self):
        return self._mouse_tracking

    @mouse_tracking.setter
    def mouse_tracking(self, enabled):
        if not self._ti.string("kmous"):
            raise Exception("Terminal does not support mouse input")
        self.write_escape(b"\x1b[?1003" + (b"h" if enabled else b"l")) # xterm all-motion mouse tracking
        self.write_escape(b"\x1b[?1006" + (b"h" if enabled else b"l")) # xterm SGR mouse format
    
    @property
    def window_title(self):
        return self._window_title
    
    @window_title.setter
    def window_title(self, title):
        if self.window_title != title:
            self.write_escape(self._ti.parameterize("tsl", require=True)) # to status line
            self.write(title)
            self.write_escape(self._ti.parameterize("fsl", require=True)) # back from status line
            self._window_title = title
    
    def enter_alt_buffer(self):
        self.write_escape(self._ti.parameterize("smcup"))
    
    def exit_alt_buffer(self):
        self.write_escape(self._ti.parameterize("rmcup"))
    
    def color_auto(self, color):
        if self.color_mode == "256-color":
            return color_to_256(color)
        else:
            return color_to_16(color)

    def clear_screen(self):
        self.cursor_pos = (0, 0)
        self.write_escape("\x1b[2J")
    
    def write_escape(self, binary):
        if type(binary) == str:
            sys.stdout.write(binary)
        else:
            sys.stdout.write(binary.decode("ascii"))

    def write(self, text):
        sys.stdout.write(text)
        self._cursor_pos = (self._cursor_pos[0] + terminal_len(text), self._cursor_pos[1])

    def flush(self):
        while True:
            try:
                sys.stdout.flush()
                break
            except BlockingIOError:
                pass

class UnixInput(Observable):
    def __init__(self):
        super().__init__()
        self._old_attr = None
        self._fd_in = sys.stdin.fileno()
        self._cbreak = False
        self._ti = Terminfo()
        self._key_parser = make_key_parser(self._ti)
        self._mouse_parser = make_mouse_parser(self._ti)

        self._has_exited = True
        self._has_exited_lock = threading.Lock()

        self._stdin_selector = selectors.DefaultSelector()
        self._stdin_selector.register(self._fd_in, selectors.EVENT_READ)

        self._input_queue = Queue()
        self._collector = threading.Thread(target=self.collector_func, daemon=True)

        self._grouper = threading.Thread(target=self.grouper_func, daemon=True)

        self._sigwinch_event = threading.Event()
        self._sigwinch_consumer = threading.Thread(target=self.watch_sigwinch, daemon=True)
        signal.signal(signal.SIGWINCH, self.handle_sigwinch)
    
    def handle_sigwinch(self, signum, frame):
        self._sigwinch_event.set()
    
    def watch_sigwinch(self):
        while not self._has_exited:
            self._sigwinch_event.wait()
            self._sigwinch_event.clear()
            self.emit("resize")
    
    @property
    def cbreak(self):
        return self._cbreak

    def collector_func(self):
        while not self._has_exited:
            self._stdin_selector.select()
            data = sys.stdin.read(-1)
            for ch in data:
                self._input_queue.put(ch)
    
    def grouper_func(self):
        buffer = []
        grouping = False
        group_timeout = 0
        def dump():
            self.parse_group("".join(buffer))
            buffer.clear()
        while not self._has_exited:
            try:
                timeout = group_timeout if grouping else None
                ch = self._input_queue.get(timeout=timeout)
                if ch == "\x1b":
                    if len(buffer) > 0:
                        dump()
                    group_timeout = 25/1000
                buffer.append(ch)
                grouping = True
            except queue.Empty:
                if len(buffer) > 0:
                    dump()
                grouping = False
                group_timeout = 0
    
    def parse_group(self, chars):
        self.emit("raw_input", chars)
        while len(chars) > 0:
            results = [*self._key_parser.parse(chars), *self._mouse_parser.parse(chars)]
            if len(results) > 0:
                results.sort(key=lambda i: len(i[0]), reverse=True)
                match, event = results[0]
                if isinstance(event, Key):
                    self.emit("key", event)
                if isinstance(event, Mouse):
                    self.emit("mouse", event)
                chars = chars[len(match):]
            elif chars[0] != "\x1b":
                self.emit("key", Key(char=chars[0]))
                chars = chars[1:]
            else:
                chars = chars[1:]

    def set_cbreak(self, on = True):
        if on and not self._cbreak:
            self._old_attr = termios.tcgetattr(self._fd_in)
            tty.setcbreak(self._fd_in)
            self._cbreak = True
        elif self._cbreak:
            termios.tcsetattr(self._fd_in, termios.TCSAFLUSH, self._old_attr)
            self._cbreak = False
    
    def start(self):
        with self._has_exited_lock:
            if not self._has_exited:
                raise RuntimeError("Input already started.")
            self._has_exited = False
            self.set_cbreak(True)
            set_fd_nonblocking(self._fd_in, True)
            self._collector.start()
            self._grouper.start()
            self._sigwinch_consumer.start()

    def stop(self):
        with self._has_exited_lock:
            if self._has_exited:
                raise RuntimeError("Input already stopped.")
            set_fd_nonblocking(self._fd_in, False)
            self.set_cbreak(False)
            self._has_exited = True

def set_fd_nonblocking(fd, is_nonblocking):
    """ set the NONBLOCK flag on a file descriptor, preserving other flags. """
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    if is_nonblocking:
        flags |= os.O_NONBLOCK
    else:
        flags &= ~os.O_NONBLOCK
    fcntl.fcntl(fd, fcntl.F_SETFL, flags)
