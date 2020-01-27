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
from termpixels.unix_keys import Key, Mouse, make_parsers
from termpixels.util import terminal_len

def detect_truecolor(terminfo=None):
    """Detect true-color (24-bit) color support
    """
    if "COLORTERM" in os.environ and "truecolor" in os.environ["COLORTERM"]:
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
    def __init__(self, *, stdout=None):
        super().__init__()
        self._ti = Terminfo()
        self.color_mode = detect_color_mode(self._ti)
        self._cursor_pos = None
        self._fg = None
        self._bg = None
        self._show_cursor = None
        self._mouse_tracking = None
        self.size_dirty = True 
        self._size = None
        self._window_title = None

        # allow output to be redirected to a file, but make sure that a TTY 
        # output is available for ioctl and termios operations.
        self._fd_out = stdout if stdout is not None else sys.stdout.fileno()
        if os.isatty(self._fd_out):
            self._fd_out_tty = self._fd_out
        else:
            self._fd_out_tty = os.open("/dev/tty", os.O_WRONLY)

        self._out_buffer = bytearray()
        
    @property
    def terminal_name(self):
        return self._ti.termname
    
    @property
    def size(self):
        if self.size_dirty:
            self.update_size()
        return self._size
    
    def update_size(self):
        result = fcntl.ioctl(self._fd_out_tty, termios.TIOCGWINSZ, struct.pack("HHHH", 0, 0, 0, 0))
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
        # https://invisible-island.net/xterm/ctlseqs/ctlseqs.html#h2-Mouse-Tracking 
        if not self._ti.string("kmous"):
            raise Exception("Terminal does not support mouse input")

        # https://invisible-island.net/xterm/ctlseqs/ctlseqs.html#h3-Any-event-tracking
        # Enables mouse tracking for any event
        # By default, we get X10 mouse encoding (not great)
        self.write_escape(b"\x1b[?1003" + (b"h" if enabled else b"l")) # xterm all-motion mouse tracking

        # We hope that the terminal ignores any of these it does not support.
        # Ideally, we want SGR mouse encoding. rxvt may have other ideas.
        self.write_escape(b"\x1b[?1005" + (b"h" if enabled else b"l")) # UTF-8 (extended X10) mouse encoding
        self.write_escape(b"\x1b[?1006" + (b"h" if enabled else b"l")) # SGR mouse encoding
    
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
    
    def set_charset_utf8(self, utf8=True):
        """ try to switch the character set to UTF-8, or to default.
        Relies on hardcoded xterm control sequences.
        """

        if utf8:
            self.write_escape("\x1b%G")
        else:
            self.write_escape("\x1b%@")
    
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
    
    def write_escape(self, string):
        if type(string) == str:
            string = string.encode("utf-8")
        self._out_buffer.extend(string)

    def write(self, text):
        self._out_buffer.extend(text.encode("utf-8"))
        if self._cursor_pos is not None:
            self._cursor_pos = (self.cursor_pos[0] + terminal_len(text), self.cursor_pos[1])

    def flush(self):
        try:
            os.write(self._fd_out, self._out_buffer)
        except BrokenPipeError:
            # this can happen if stdout is redirected to a program and the 
            # program exits before termpixels. We switch to TTY output so that
            # the terminal can be reset if necessary.
            self._fd_out = self._fd_out_tty
        
        self._out_buffer.clear()
        termios.tcdrain(self._fd_out_tty)

class UnixInput(Observable):
    def __init__(self):
        super().__init__()
        self._old_attr = None

        # open /dev/tty rather than using stdin in case it is e.g. a pipe
        # also ensures that stdin state is not corrupted if we crash
        self._fd_in = os.open("/dev/tty", os.O_RDONLY)

        self._cbreak = False
        self._ti = Terminfo()
        self._parsers = make_parsers(self._ti)

        self._has_exited = True
        self._has_exited_lock = threading.Lock()

        self._stdin_selector = selectors.DefaultSelector()
        self._stdin_selector.register(self._fd_in, selectors.EVENT_READ)

        self._input_queue = Queue()
        self._sigwinch_event = threading.Event()

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

            try:
                data_bytes = bytes(os.read(self._fd_in, 2048))
                try:
                    data = data_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    data = list(map(chr, data_bytes))
            
                for ch in data:
                    self._input_queue.put(ch)
            except BlockingIOError:
                pass # non-blocking read not possible; try again or exit
    
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
            results = []
            for parser in self._parsers:
                results += parser.parse(chars)
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
            os.set_blocking(self._fd_in, False)

            self._collector = threading.Thread(name="Unix input collector", target=self.collector_func, daemon=True)
            self._grouper = threading.Thread(name="Unix input grouper", target=self.grouper_func, daemon=True)
            self._sigwinch_consumer = threading.Thread(name="Unix SIGWINCH watcher", target=self.watch_sigwinch, daemon=True)

            self._collector.start()
            self._grouper.start()
            self._sigwinch_consumer.start()

    def stop(self):
        with self._has_exited_lock:
            if self._has_exited:
                raise RuntimeError("Input already stopped.")

            # should not be necessary since we (re)open /dev/tty
            os.set_blocking(self._fd_in, True)
            self.set_cbreak(False)

            self._has_exited = True
