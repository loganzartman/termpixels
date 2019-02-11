import termios
import tty
import sys
import threading 
import queue
from queue import Queue
from observable import Observable
from terminfo import Terminfo, termcap_format

class UnixBackend:
    def __init__(self):
        self._ti = Terminfo()
        self._cursor_pos = None
        self._fg = None
        self._bg = None
        self._show_cursor = None 
        self.clear_screen()
    
    @property
    def cursor_pos(self):
        return self._cursor_pos
    
    @cursor_pos.setter
    def cursor_pos(self, pos):
        if self._cursor_pos != pos:
            col, row = pos
            self.write_escape(termcap_format(self._ti["cup"], row, col)) 
            self._cursor_pos = pos

    @property
    def show_cursor(self):
        return self._show_cursor
    
    @show_cursor.setter
    def show_cursor(self, show_cursor):
        if self._show_cursor != show_cursor:
            self.write_escape("[?25" + "h" if show_cursor else "l")
            self._show_cursor = show_cursor
    
    @property
    def fg(self):
        return self._fg
    
    @fg.setter
    def fg(self, color):
        if self._fg != color:
            self.write_escape("[38;2;{r};{g};{b}m".format(r=color.r, g=color.g, b=color.b))
            self._fg = color
    
    @property
    def bg(self):
        return self._bg
    
    @bg.setter
    def bg(self, color):
        if self._bg != color:
            self.write_escape("[48;2;{r};{g};{b}m".format(r=color.r, g=color.g, b=color.b))
            self._bg = color

    def clear_screen(self):
        self.cursor_pos = (0, 0)
        self.write("\x1b[2J")
    
    def write_escape(self, code):
        print("\x1b{}".format(code), end="")

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
