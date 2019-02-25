import termios
import tty
import sys
import threading 
import queue
import signal
import fcntl
import struct
from queue import Queue
from termpixels.observable import Observable
from termpixels.terminfo import Terminfo
from termpixels.unix_keys import Key, make_key_parser, make_mouse_parser

class UnixBackend(Observable):
    def __init__(self):
        super().__init__()
        self._ti = Terminfo()
        self._cursor_pos = None
        self._fg = None
        self._bg = None
        self._show_cursor = None
        self._mouse_tracking = None
        self._size_dirty = True 
        self._size = None

        self._sigwinch_event = threading.Event()
        self._sigwinch_consumer = threading.Thread(target=self.watch_sigwinch, daemon=True)
        self._sigwinch_consumer.start()
        signal.signal(signal.SIGWINCH, self.handle_sigwinch)
    
    def handle_sigwinch(self, signum, frame):
        self._sigwinch_event.set()
    
    def watch_sigwinch(self):
        while True:
            self._sigwinch_event.wait()
            self._sigwinch_event.clear()
            self._size_dirty = True
            self.emit("resize")
    
    @property
    def size(self):
        if self._size_dirty:
            self.update_size()
        return self._size
    
    def update_size(self):
        result = fcntl.ioctl(sys.stdout, termios.TIOCGWINSZ, struct.pack("HHHH", 0, 0, 0, 0))
        r, c, _, _ = struct.unpack("HHHH", result)
        self._size = (c, r) 
        self._size_dirty = False
    
    @property
    def cursor_pos(self):
        return self._cursor_pos
    
    @cursor_pos.setter
    def cursor_pos(self, pos):
        if self._cursor_pos != pos:
            col, row = pos
            self.write_escape(self._ti.parameterize("cup", row, col)) 
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
            self.write_escape(self._ti.parameterize("setaf", self.color_auto(color)))
            self._fg = color
    
    @property
    def bg(self):
        return self._bg
    
    @bg.setter
    def bg(self, color):
        if self._bg != color:
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
    
    def save_screen(self):
        self.write_escape(self._ti.parameterize("smcup"))
    
    def load_screen(self):
        self.write_escape(self._ti.parameterize("rmcup"))
    
    def color_auto(self, color):
        col = 0
        if self._ti.num("colors") == 256:
            col = self.color_to_256(color)
        else:
            col = self.color_to_16(color)
        return col

    def color_to_16(self, color):
        """Convert color into ANSI 16-color format.
        """
        if color.r == color.g == color.b == 0:
            return 0
        bright = sum((color.r, color.g, color.b)) >= 127 * 3
        r = 1 if color.r > 63 else 0
        g = 1 if color.g > 63 else 0
        b = 1 if color.b > 63 else 0
        return (r | (g << 1) | (b << 2)) + (8 if bright else 0)

    def color_to_256(self, color):
        """Convert color into ANSI 8-bit color format.
        Red is converted to 196
        This converter emits the 216 RGB colors and the 24 grayscale colors.
        It does not use the 16 named colors.
        """
        output = 0
        if color.r == color.g == color.b:
            # grayscale case
            if color.r == 255: # pure white
                output = 231
            else:
                output = 232 + int(color.r / 256 * 24)
        else:
            # 216-color RGB
            scale = lambda c: int(c / 256 * 6)
            output = 16
            output += scale(color.b)
            output += scale(color.g) * 6
            output += scale(color.r) * 6 * 6
        return output

    def clear_screen(self):
        self.cursor_pos = (0, 0)
        self.write_escape("\x1b[2J")
    
    def write_escape(self, binary):
        if type(binary) == str:
            print(binary, end="")
        else:
            print(binary.decode("ascii"), end="")

    def write(self, text):
        print(text, end="")
        self._cursor_pos = (self._cursor_pos[0] + len(text), self._cursor_pos[1])

    def flush(self):
        print("", end="", flush=True)

class UnixInput(Observable):
    def __init__(self):
        super().__init__()
        self._old_attr = None
        self._fd_in = 0 # stdin
        self._cbreak = False
        self._ti = Terminfo()
        self._key_parser = make_key_parser(self._ti)
        self._mouse_parser = make_mouse_parser(self._ti)

        self._input_queue = Queue()
        self._collector = threading.Thread(target=self.collector_func, daemon=True)
        self._grouper = threading.Thread(target=self.grouper_func, daemon=True)

    @property
    def cbreak(self):
        return self._cbreak

    def collector_func(self):
        while True:
            ch = self.getch()
            self._input_queue.put(ch)
    
    def grouper_func(self):
        buffer = []
        grouping = False
        group_timeout = 0
        def dump():
            self.parse_group("".join(buffer))
            buffer.clear()
        while True:
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
        kpr = self._key_parser.parse(chars)
        if kpr:
            self.emit("key", kpr)
            return
        mpr = self._mouse_parser.parse(chars)
        if mpr:
            self.emit("mouse", mpr)
            return
        if chars[0] != "\x1b":
            for ch in chars:
                self.emit("key", Key(char=ch))

    def set_cbreak(self, on = True):
        if on:
            self._old_attr = termios.tcgetattr(self._fd_in)
            tty.setcbreak(self._fd_in)
            self._cbreak = True
        else:
            termios.tcsetattr(self._fd_in, termios.TCSAFLUSH, self._old_attr)
            self._cbreak = False
    
    def start(self):
        self.set_cbreak(True)
        self._collector.start()
        self._grouper.start()

    def stop(self):
        self.set_cbreak(False)
    
    def getch(self):
        if not self.cbreak:
            raise Exception("cbreak not enabled.")
        return sys.stdin.read(1)
