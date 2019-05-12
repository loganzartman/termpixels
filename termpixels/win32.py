import platform
import ctypes
import threading
from ctypes import windll
from ctypes import byref
from ctypes import Structure, Union
from termpixels.color import Color
from termpixels.color import color_to_16
from termpixels.observable import Observable
from termpixels.keys import Key, Mouse
from termpixels.win32_keys import vk_to_key
from termpixels.util import terminal_len
from time import sleep

def detect_win10_console():
    """Check whether new console features are supported"""
    try:
        build = platform.version().split(".")[2]
        return int(build) >= 10586
    except:
        return False

# Windows types
WORD = ctypes.c_ushort
DWORD = ctypes.c_uint
CHAR = ctypes.c_byte
WCHAR = ctypes.c_ushort
UINT = ctypes.c_uint
BOOL = ctypes.c_int

# Windows structs
class CharUnion(Union):
    _fields_ = [
        ("UnicodeChar", WCHAR),
        ("AsciiChar", CHAR)
    ]

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
        ("wAttributes", WORD),
        ("srWindow", SMALL_RECT),
        ("dwMaximumWindowSize", COORD)
    ]

class CHAR_INFO(Structure):
    _fields_ = [
        ("Char", CharUnion),
        ("Attributes", WORD)
    ]

class CONSOLE_CURSOR_INFO(Structure):
    _fields_ = [
        ("dwSize", DWORD),
        ("bVisible", BOOL)
    ]

# Misc Windows constants
INFINITE = 0xFFFFFFFF
STD_INPUT_HANDLE = DWORD(-10)
STD_OUTPUT_HANDLE = DWORD(-11)
STD_ERROR_HANDLE = DWORD(-12)
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

ENABLE_ECHO_INPUT = 0x0004
ENABLE_EXTENDED_FLAGS = 0x0080
ENABLE_INSERT_MODE = 0x0020
ENABLE_LINE_INPUT = 0x0002
ENABLE_MOUSE_INPUT = 0x0010
ENABLE_PROCESSED_INPUT = 0x0001
ENABLE_QUICK_EDIT_MODE = 0x0040
ENABLE_WINDOW_INPUT = 0x0008
ENABLE_VIRTUAL_TERMINAL_INPUT = 0x0200

ENABLE_PROCESSED_OUTPUT = 0x0001
ENABLE_WRAP_AT_EOL_OUTPUT = 0x0002
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
DISABLE_NEWLINE_AUTO_RETURN = 0x0008
ENABLE_LVB_GRID_WORLDWIDE = 0x001

# Input structures and constants
FOCUS_EVENT = 0x0010
KEY_EVENT = 0x0001
MENU_EVENT = 0x0008
MOUSE_EVENT = 0x0002
WINDOW_BUFFER_SIZE_EVENT = 0x0004

FROM_LEFT_1ST_BUTTON_PRESSED = 0x0001
FROM_LEFT_2ND_BUTTON_PRESSED = 0x0004
FROM_LEFT_3RD_BUTTON_PRESSED = 0x0008
FROM_LEFT_4TH_BUTTON_PRESSED = 0x0010
RIGHTMOST_BUTTON_PRESSED = 0x0002

DOUBLE_CLICK = 0x0002
MOUSE_HWHEELED = 0x0008
MOUSE_MOVED = 0x0001
MOUSE_WHEELED = 0x0004

class KEY_EVENT_RECORD(Structure):
    _fields_ = [
        ("bKeyDown", BOOL),
        ("wRepeatCount", WORD),
        ("wVirtualKeyCode", WORD),
        ("wVirtualScanCode", WORD),
        ("uChar", CharUnion),
        ("dwControlKeyState", DWORD)
    ]

class MOUSE_EVENT_RECORD(Structure):
    _fields_ = [
        ("dwMousePosition", COORD),
        ("dwButtonState", DWORD),
        ("dwControlKeyState", DWORD),
        ("dwEventFlags", DWORD)
    ]

class WINDOW_BUFFER_SIZE_RECORD(Structure):
    _fields_ = [
        ("dwSize", COORD)
    ]

class MENU_EVENT_RECORD(Structure):
    _fields_ = [
        ("dwCommandId", UINT)
    ]

class FOCUS_EVENT_RECORD(Structure):
    _fields_ = [
        ("bSetFocus", BOOL)
    ]

class InputRecordEvent(Union):
    _fields_ = [
        ("KeyEvent", KEY_EVENT_RECORD),
        ("MouseEvent", MOUSE_EVENT_RECORD),
        ("WindowBufferSizeEvent", WINDOW_BUFFER_SIZE_RECORD),
        ("MenuEvent", MENU_EVENT_RECORD),
        ("FocusEvent", FOCUS_EVENT_RECORD)
    ]

class INPUT_RECORD(Structure):
    _fields_ = [
        ("EventType", WORD),
        ("Event", InputRecordEvent)
    ]

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
        # set up buffers
        self._stdout = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        self._back_buffer = None
        self._char_data = None
        self._out_buffer = self._stdout
        windll.kernel32.SetConsoleMode(self._out_buffer, ENABLE_PROCESSED_OUTPUT)

        self.size_dirty = True
        self._size = None
        self.update_size()

        self._fg = Color.rgb(1,1,1)
        self._bg = Color.rgb(0,0,0)
        self.color_mode = "16-color"
        self._cursor_pos = None
        self._show_cursor = None
        self._attr = WORD(0)

        self._termname = "Windows Console"
        if detect_win10_console():
            self._termname = "Windows Console (Win10)"
    
    @property
    def terminal_name(self):
        return self._termname
    
    @property
    def size(self):
        if self.size_dirty:
            self.update_size()
        return self._size
    
    def update_size(self):
        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        windll.kernel32.GetConsoleScreenBufferInfo(self._out_buffer, byref(csbi))
        w = csbi.srWindow.Right - csbi.srWindow.Left + 1
        h = csbi.srWindow.Bottom - csbi.srWindow.Top + 1
        self.size_dirty = False
        if self._size != (w, h):
            self._size = (w, h)
            self._create_buffers()

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
    def application_keypad(self):
        return NotImplemented
    
    @application_keypad.setter
    def application_keypad(self, v):
        return NotImplemented
    
    @property
    def cursor_pos(self):
        return self._cursor_pos
    
    @cursor_pos.setter
    def cursor_pos(self, pos):
        if self._cursor_pos != pos:
            self._cursor_pos = (pos[0], pos[1])
    
    @property
    def show_cursor(self):
        return self._show_cursor
    
    @show_cursor.setter
    def show_cursor(self, show_cursor):
        if self._show_cursor != show_cursor:
            info = CONSOLE_CURSOR_INFO(100, show_cursor)
            windll.kernel32.SetConsoleCursorInfo(self._out_buffer, byref(info))
            self._show_cursor = show_cursor
    
    def _create_buffers(self):
        # clean up old buffer
        reenter_alt_buffer = self._out_buffer == self._back_buffer 
        old_buffer = self._back_buffer

        # create alt buffer
        self._back_buffer = windll.kernel32.CreateConsoleScreenBuffer(
            GENERIC_READ | GENERIC_WRITE,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            None,
            CONSOLE_TEXTMODE_BUFFER,
            None
        )

        # change mode of buffer to disable default features (text selection, etc.)
        windll.kernel32.SetConsoleMode(self._back_buffer, ENABLE_PROCESSED_OUTPUT)

        # create character data buffer
        self._char_data_size = self.size
        self._char_data = (CHAR_INFO * (self._char_data_size[0] * self._char_data_size[1]))()
        if reenter_alt_buffer:
            self.enter_alt_buffer()
        if old_buffer:
            windll.kernel32.CloseHandle(old_buffer)
    
    def enter_alt_buffer(self):
        windll.kernel32.SetConsoleActiveScreenBuffer(self._back_buffer)
        self._out_buffer = self._back_buffer
    
    def exit_alt_buffer(self):
        windll.kernel32.SetConsoleActiveScreenBuffer(self._stdout)
        self._out_buffer = self._stdout
    
    def clear_screen(self):
        return NotImplemented

    def _update_char_attrs(self):
        attr = 0
        attr |= color_win32(self.fg, False)
        attr |= color_win32(self.bg, True)
        self._attr = WORD(attr)
    
    def write(self, text):
        n_written = DWORD()
        x, y = self._cursor_pos
        idx = y * self._char_data_size[0] + x
        self._char_data[idx].Char.UnicodeChar = ord(text[0])
        self._char_data[idx].Attributes = self._attr
        self._cursor_pos = (self._cursor_pos[0] + terminal_len(text), self._cursor_pos[1])
    
    def flush(self):
        # copy character data to active screen buffer
        lpWriteRegion = SMALL_RECT(0, 0, *self._char_data_size)
        windll.kernel32.WriteConsoleOutputW(
            self._out_buffer,
            self._char_data,
            COORD(*self._char_data_size),
            COORD(0, 0),
            byref(lpWriteRegion)
        )
        # position cursor for aesthetic purposes
        windll.kernel32.SetConsoleCursorPosition(
            self._out_buffer,
            COORD(self._cursor_pos[0], self._cursor_pos[1])
        )


class Win32Input(Observable):
    def __init__(self):
        super().__init__()
        self._stdin = windll.kernel32.GetStdHandle(STD_INPUT_HANDLE)
        self._old_mode = None
        self._old_cp = None

        self._exit_event = threading.Event()
        self._reader = threading.Thread(target=self._read, daemon=True)
    
    def _read(self):
        MAX_RECORDS = 16
        buf = (INPUT_RECORD * MAX_RECORDS)()
        while not self._exit_event.is_set():
            numRecords = DWORD()
            windll.kernel32.WaitForSingleObject(self._stdin, INFINITE)
            windll.kernel32.ReadConsoleInputW(self._stdin, buf, MAX_RECORDS, byref(numRecords))
            for i in range(numRecords.value):
                e = buf[i].Event
                t = buf[i].EventType
                self.emit("raw_input", buf[i])
                if t == KEY_EVENT:
                    char = e.KeyEvent.uChar.UnicodeChar
                    code = e.KeyEvent.wVirtualKeyCode
                    if e.KeyEvent.bKeyDown:
                        key = vk_to_key(code)
                        if key is not None:
                            self.emit("key", key)
                        elif char != 0:
                            self.emit("key", Key(char=chr(char)))
                if t == MOUSE_EVENT:
                    pos = e.MouseEvent.dwMousePosition
                    
                    btn = e.MouseEvent.dwButtonState
                    button = None
                    if btn == FROM_LEFT_1ST_BUTTON_PRESSED:
                        button = "left"
                    elif btn == FROM_LEFT_2ND_BUTTON_PRESSED:
                        button = "middle"
                    elif btn == RIGHTMOST_BUTTON_PRESSED:
                        button = "right"

                    evt = e.MouseEvent.dwEventFlags
                    action = None
                    if evt == MOUSE_MOVED:
                        action = "moved"
                    elif button is not None:
                        action = "down"
                    # no way to detect up

                    mouse = Mouse(x=pos.X, y=pos.Y, button=button, action=action)
                    self.emit("mouse", mouse)
                if t == WINDOW_BUFFER_SIZE_EVENT:
                    self.emit("resize")

    def start(self):
        self._old_cp = windll.kernel32.GetConsoleCP()
        windll.kernel32.SetConsoleCP(65001) # UTF-8 code page

        self._old_mode = DWORD()
        windll.kernel32.GetConsoleMode(self._stdin, byref(self._old_mode))
        windll.kernel32.SetConsoleMode(self._stdin, ENABLE_EXTENDED_FLAGS | ENABLE_PROCESSED_INPUT | ENABLE_WINDOW_INPUT | ENABLE_MOUSE_INPUT)
        
        self._reader.start()
    
    def stop(self):
        windll.kernel32.SetConsoleMode(self._stdin, self._old_mode)
        windll.kernel32.SetConsoleCP(self._old_cp)
        self._exit_event.set()
