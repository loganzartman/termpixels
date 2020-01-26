from termpixels.win32 import *
from termpixels.util import terminal_len
from ctypes import windll

def detect_vt_console():
    """Check whether new console features are supported"""
    try:
        build = platform.version().split(".")[2]
        return int(build) >= 10586
    except:
        return False

class Win32VtBackend(Win32Backend):
    def __init__(self):
        #if not detect_vt_console():
        #    raise Exception("VT processing not supported")
        super().__init__()

        o_flags = ENABLE_PROCESSED_OUTPUT | ENABLE_VIRTUAL_TERMINAL_PROCESSING
        windll.kernel32.SetConsoleMode(self._out_buffer, o_flags)

        self._buffer = []
        self._termname = "Windows Console (VT)"
        self._fg = None
        self.color_mode = "truecolor"
    
    @property
    def fg(self):
        return self._fg
    
    @fg.setter
    def fg(self, color):
        if self._fg != color:
            self.write_escape("\x1b[38;2;{};{};{}m".format(color.r, color.g, color.b))
            self._fg = color
    
    @property
    def bg(self):
        return self._bg
    
    @bg.setter
    def bg(self, color):
        if self._bg != color:
            self.write_escape("\x1b[48;2;{};{};{}m".format(color.r, color.g, color.b))
            self._bg = color
    
    @property
    def cursor_pos(self):
        return self._cursor_pos
    
    @cursor_pos.setter
    def cursor_pos(self, pos):
        if self._cursor_pos != pos:
            col, row = pos
            self.write_escape("\x1b[{};{}H".format(row + 1, col + 1))
            self._cursor_pos = pos
    
    @property
    def show_cursor(self):
        return self._show_cursor
    
    @show_cursor.setter
    def show_cursor(self, show_cursor):
        if self._show_cursor != show_cursor:
            self.write_escape("\x1b[?25{}".format("h" if show_cursor else "l"))
        
    def enter_alt_buffer(self):
        self.write_escape("\x1b[?1049h")
    
    def exit_alt_buffer(self):
        self.write_escape("\x1b[?1049l")
    
    def write(self, text):
        self.write_escape(text)
        if self._cursor_pos is not None:
            self._cursor_pos = (self._cursor_pos[0] + terminal_len(text), self._cursor_pos[1])

    def write_escape(self, text):
        self._buffer.append(text)

    def flush(self):
        buffer = "".join(self._buffer)
        written = WORD()

        windll.kernel32.WriteConsoleW(
            self._out_buffer,
            buffer,
            DWORD(len(buffer)),
            byref(written),
            None
        )
        self._buffer = []
