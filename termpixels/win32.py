import platform
import ctypes
from ctypes import windll
from ctypes import byref
from ctypes import Structure
from termpixels.screen import Color
from termpixels.color import color_to_16
from termpixels.observable import Observable

def detect_win10_console():
    """Check whether new console features are supported"""
    try:
        build = platform.version().split(".")[2]
        return int(build) >= 10586
    except:
        return False

# Windows types
c_word = ctypes.c_uint
c_dword = ctypes.c_ulong

# Windows structs
class COORD(Structure):
    _fields_ = [
        ("X", ctypes.c_short),
        ("Y", ctypes.c_short)
    ]

class SMALL_RECT(Structure):
    _fields_ = [
        ("Left", ctypes.c_short),
        ("Top", ctypes.c_short),
        ("Right", ctypes.c_short),
        ("Bottom", ctypes.c_short)
    ]

class CONSOLE_SCREEN_BUFFER_INFO(Structure):
    _fields_ = [
        ("dwSize", COORD),
        ("dwCursorPosition", COORD),
        ("wAttributes", c_word),
        ("srWindow", SMALL_RECT),
        ("dwMaximumWindowSize", COORD)
    ]

# Misc Windows constants
STD_INPUT_HANDLE = c_dword(-10)
STD_OUTPUT_HANDLE = c_dword(-11)
STD_ERROR_HANDLE = c_dword(-12)
FILE_SHARE_READ = 1
FILE_SHARE_WRITE = 2
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
CONSOLE_TEXTMODE_BUFFER = 1

# wincon.h constants
FOREGROUND_BLUE = 1
FOREGROUND_GREEN = 2
FOREGROUND_RED = 4
FOREGROUND_INTENSITY = 8
BACKGROUND_BLUE = 16
BACKGROUND_GREEN = 32
BACKGROUND_RED = 64
BACKGROUND_INTENSITY = 128

def color_win32(col, bg):
    bits = color_to_16(col)
    out = 0
    if bits & 0b1:
        out |= FOREGROUND_RED
    if bits & 0b10:
        out |= FOREGROUND_GREEN
    if bits & 0b100:
        out |= FOREGROUND_BLUE
    if bits & 0b1000:
        out |= FOREGROUND_INTENSITY
    if bg:
        out <<= 4
    return out

class Win32Backend(Observable):
    def __init__(self):
        super().__init__()
        self._stdout = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        self._alt_buffer = None
        self._active_buffer = self._stdout
        
        self._fg = Color.rgb(1,1,1)
        self._bg = Color.rgb(0,0,0)
        self.color_mode = "16-color"
        self._cursor_pos = None

        self._termname = "Windows Console"
        if detect_win10_console():
            self._termname = "Windows Console (Win10)"
    
    @property
    def terminal_name(self):
        return self._termname
    
    @property
    def size(self):
        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        windll.kernel32.GetConsoleScreenBufferInfo(self._active_buffer, byref(csbi))
        w = csbi.srWindow.Right - csbi.srWindow.Left + 1
        h = csbi.srWindow.Bottom - csbi.srWindow.Top + 1
        return (w, h)

    @property
    def fg(self):
        return self._fg
    
    @fg.setter
    def fg(self, fg):
        if self._fg != fg:
            self._fg = fg
            if self.color_mode == "16-color":
                self._update_char_attrs()

    @property
    def bg(self):
        return self._bg
    
    @bg.setter
    def bg(self, bg):
        if self._bg != bg:
            self._bg = bg
            if self.color_mode == "16-color":
                self._update_char_attrs()
    
    @property
    def cursor_pos(self):
        return self._cursor_pos
    
    @cursor_pos.setter
    def cursor_pos(self, pos):
        if self._cursor_pos != pos:
            col, row = pos
            windll.kernel32.SetConsoleCursorPosition(self._active_buffer, COORD(col, row))
            self._cursor_pos = pos
    
    def enter_alt_buffer(self):
        if not self._alt_buffer:
            self._alt_buffer = windll.kernel32.CreateConsoleScreenBuffer(
                GENERIC_READ | GENERIC_WRITE,
                FILE_SHARE_READ | FILE_SHARE_WRITE,
                None, 
                CONSOLE_TEXTMODE_BUFFER, 
                None
            )
        windll.kernel32.SetConsoleActiveScreenBuffer(self._alt_buffer)
        self._active_buffer = self._alt_buffer
    
    def exit_alt_buffer(self):
        windll.kernel32.SetConsoleActiveScreenBuffer(self._stdout)
        self._active_buffer = self._stdout
    
    def _update_char_attrs(self):
        attr = 0
        attr |= color_win32(self.fg, False)
        attr |= color_win32(self.bg, True)
        windll.kernel32.SetConsoleTextAttribute(
            self._active_buffer,
            c_word(attr)
        )
    
    def write(self, text):
        n_written = c_dword()
        windll.kernel32.WriteConsoleW(
            self._active_buffer,
            text,
            len(text),
            byref(n_written),
            None
        )
        self._cursor_pos = (self._cursor_pos[0] + len(text), self._cursor_pos[1])
    
    def flush(self):
        # TODO: create alternate screen buffer in init; swap buffers here
        pass
