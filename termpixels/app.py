import termios
import tty
import sys
from copy import copy
from screen import Screen
from detector import detect_backend
from observable import Observable

class App:
    def __init__(self):
        self.backend = detect_backend()
        self.screen = Screen(80, 20, self.backend)
    
    def start(self):
        inpt = UnixInput()
        inpt.start()

        self.screen.print("Type something:", 0, 0)
        self.screen.update()
        try:
            x = 0
            while True:
                ch = inpt.getch()
                self.screen.print(ch, x, 1)
                self.screen.cursor_pos = (x + 1, 1)
                self.screen.update()
                x += 1
        except Exception as e:
            inpt.stop()
            raise e

class UnixInput(Observable):
    def __init__(self):
        self._old_attr = None
        self._fd_in = 0 # stdin
        self._cbreak = False
    
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

    def stop(self):
        self.set_cbreak(False)
    
    def getch(self):
        if not self.cbreak:
            raise Exception("cbreak not enabled.")
        return sys.stdin.read(1)
