import termios
import tty
import sys
import threading 
from queue import Queue
from observable import Observable

class UnixBackend:
    def __init__(self):
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
            self.write_escape("[{row};{col}H".format(row=pos[1]+1, col=pos[0]+1)) 
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

        def collector_body():
            while True:
                ch = self.getch()
                self._input_queue.put(ch)
        self._collector = threading.Thread(target=collector_body, daemon=True)

        def processor_body():
            while True:
                ch = self._input_queue.get()
                self.emit("key", ch)
        self._processor = threading.Thread(target=processor_body, daemon=True)

    @property
    def cbreak(self):
        return self._cbreak

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
        self._processor.start()

    def stop(self):
        self.set_cbreak(False)
    
    def getch(self):
        if not self.cbreak:
            raise Exception("cbreak not enabled.")
        return sys.stdin.read(1)
