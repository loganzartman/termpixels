import termios
import tty
import sys
import threading 
import queue
import signal
import fcntl
import struct
from queue import Queue
from observable import Observable
from terminfo import Terminfo

class UnixBackend(Observable):
    def __init__(self):
        super().__init__()
        self._ti = Terminfo()
        self._cursor_pos = None
        self._fg = None
        self._bg = None
        self._show_cursor = None
        self._size_dirty = True 
        self._size = None
        self._handle_sigwinch_lock = threading.Lock()
        self.clear_screen()
        signal.signal(signal.SIGWINCH, self.handle_sigwinch)
    
    def handle_sigwinch(self, signum, frame):
        self._size_dirty = True
        with self._handle_sigwinch_lock:
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
    
    def color_auto(self, color):
        col = 0
        if self._ti.num("colors") == 256:
            col = self.color_to_256(color)
        else:
            col = self.color_to_16(color)
        return col

    def color_to_16(self, color):
        if color.r == color.g == color.b == 0:
            return 0
        bright = sum((color.r, color.g, color.b)) >= 127 * 3
        r = 1 if color.r > 63 else 0
        g = 1 if color.g > 63 else 0
        b = 1 if color.b > 63 else 0
        return (r | (g << 1) | (b << 2)) + (8 if bright else 0)

    def color_to_256(self, color):
        """Convert this color into ANSI 8-bit color format.
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
        while True:
            try:
                timeout = group_timeout if grouping else None
                ch = self._input_queue.get(timeout=timeout)
                buffer.append(ch)
                grouping = True
                if ch == "\x1b":
                    group_timeout = 25/1000
            except queue.Empty:
                if len(buffer) > 0:
                    self.parse_group("".join(buffer))
                    buffer.clear()
                grouping = False
                group_timeout = 0
    
    def parse_group(self, chars):
        if chars.startswith("\x1b"):
            pass
        else:
            for ch in chars:
                self.emit("key", ch)

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
