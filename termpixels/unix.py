import termios
import tty
import sys
import threading 
import queue
import curses
import re
import operator
from queue import Queue
from observable import Observable

class UnixBackend:
    def __init__(self):
        curses.setupterm()
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
            pattern = curses.tigetstr("cup").decode("ascii")
            self.write_escape(termcap_format(pattern, row, col)) 
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

def termcap_format(format_str, *args):
    """Evaluate a parameterized termcap string. (it's a full language)
    Doesn't support the %? conditional syntax because it sounded hard.
    https://www.mkssoftware.com/docs/man5/terminfo.5.asp
    """
    arguments = list(args)
    stack = []
    regs = {}
    output = []

    def parse_output(match):
        nonlocal output
        output += match[1] % (stack.pop(),)
    def parse_push(match):
        stack.append(arguments[int(match[1]) - 1])
    def parse_set(match):
        regs[match[1]] = stack.pop()
    def parse_get(match):
        stack.append(regs[match[1]])
    def parse_const_char(match):
        stack.append(match[1])
    def parse_const_int(match):
        stack.append(int(match[1]))
    def parse_binop(match):
        lhs = stack.pop()
        rhs = stack.pop()
        stack.append({
            "+": operator.add,
            "-": operator.sub,
            "*": operator.mul,
            "/": operator.floordiv,
            "m": operator.mod,
            "&": operator.and_,
            "|": operator.or_,
            "^": operator.xor,
            "=": operator.eq,
            "<": operator.lt,
            ">": operator.gt,
            "A": lambda l, r: l and r,
            "O": lambda l, r: l or r
        }[match[1]](lhs, rhs))
    def parse_unop(match):
        operand = stack.pop()
        stack.append({
            "!": operator.not_,
            "~": operator.invert
        }[match[1]](operand))
    def parse_inc(match):
        arguments[0] += 1
        arguments[1] += 1
    def parse_percent(match):
        output.append("%")
    def parse_char(match):
        output.append(match[0])

    patterns = {
        re.compile(r"(%(?:0?\d)?[dx]|c|s)"): parse_output,
        re.compile(r"%p([1-9])"): parse_push,
        re.compile(r"%P([a-z])"): parse_set,
        re.compile(r"%g([a-z])"): parse_get,
        re.compile(r"%'(.)'"): parse_const_char,
        re.compile(r"%{(\d+)}"): parse_const_int,
        re.compile(r"%([+\-*/m&|\^=<>AO])"): parse_binop,
        re.compile(r"%([!~])"): parse_unop,
        re.compile(r"%i"): parse_inc,
        re.compile(r"%%"): parse_percent,
        re.compile(r"."): parse_char
    }
    
    while len(format_str) > 0:
        for p, parser in patterns.items():
            match = p.match(format_str)
            if match:
                parser(match)
                format_str = format_str[len(match[0]):]
                break
            
    return "".join(output)