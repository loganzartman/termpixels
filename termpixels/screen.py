from threading import Lock
from copy import copy
from time import perf_counter
import colorsys
from termpixels.unix import UnixBackend

class Color:
    def __init__(self, r, g, b):
        clip = lambda c: max(0, min(255, round(c)))
        self._r = clip(r)
        self._g = clip(g)
        self._b = clip(b)
        self._packed = Color.pack(self)
    
    @property
    def r(self):
        return self._r
    
    @property
    def g(self):
        return self._g
    
    @property
    def b(self):
        return self._b

    def __eq__(self, other):
        try:
            return self._packed == other._packed
        except AttributeError:
            return False
        
    def __add__(self, other):
        try:
            return Color(self.r + other.r, self.g + other.g, self.b + other.b)
        except:
            pass
        return Color(self.r + other, self.g + other, self.b + other)

    def __sub__(self, other):
        try:
            return Color(self.r - other.r, self.g - other.g, self.b - other.b)
        except:
            pass
        return Color(self.r - other, self.g - other, self.b - other)

    def __mul__(self, other):
        try:
            return Color(self.r * other.r, self.g * other.g, self.b * other.b)
        except:
            pass
        return Color(self.r * other, self.g * other, self.b * other)
    
    def __repr__(self):
        return "Color(r={}, g={}, b={})".format(self.r, self.g, self.b)

    @staticmethod  
    def pack(col):
        return (col.r << 16) | (col.g << 8) | (col.b)
    
    @staticmethod
    def rgb(r, g, b):
        scale = lambda c: int(max(0, min(1, c)) * 255)
        return Color(scale(r), scale(g), scale(b))
    
    @staticmethod
    def hsl(h, s, l):
        return Color.rgb(*colorsys.hls_to_rgb(h, l, s))

class Screen:
    def __init__(self, backend):
        self.lock = Lock()
        self.backend = backend
        self.cursor_pos = (0, 0)
        self._w = 0
        self._h = 0
        self._pixels = []
        self.resize(backend.size[0], backend.size[1])
        self.backend.listen("resize", lambda size: self.resize(backend.size[0], backend.size[1]))
        self.show_cursor = False 
    
    @property
    def w(self):
        return self._w
    
    @property
    def h(self):
        return self._h
    
    @property
    def paint_fg(self):
        return self._paint_fg
    
    @paint_fg.setter
    def paint_fg(self, value):
        with self.lock:
            self._paint_fg = value
    
    @property
    def paint_bg(self):
        return self._paint_bg
    
    @paint_bg.setter
    def paint_bg(self, value):
        with self.lock:
            self._paint_bg = value

    def resize(self, w, h):
        with self.lock:
            self._pixels = [[self._pixels[x][y] if x < self._w and y < self._h else PixelData() 
                            for y in range(h)] for x in range(w)]
            self._w = w
            self._h = h
            self.backend.clear_screen()
        self.update()

    @property
    def show_cursor(self):
        return self.backend.show_cursor
    
    @show_cursor.setter
    def show_cursor(self, show):
        self.backend.show_cursor = show
    
    def at(self, x, y, *, clip=False):
        with self.lock:
            if clip:
                x = max(0, min(self.w-1, x))
                y = max(0, min(self.h-1, y))
            if x >= self.w or x < 0:
                raise Exception("x position {} out of bounds".format(x))
            if y >= self.h or y < 0:
                raise Exception("y position {} out of bounds".format(y))
            return self._pixels[x][y]

    def fill(self, x, y, w, h, *, fg=None, bg=None, char=None):
        with self.lock:
            for i in range(x, x + w):
                for j in range(y, y + h):
                    if i < 0 or j < 0  or i >= self.w or j >= self.h:
                        continue
                    pixel = self._pixels[i][j]
                    if fg is not None:
                        pixel.fg = fg
                    if bg is not None:
                        pixel.bg = bg
                    if char is not None:
                        pixel.char = char
    
    def clear(self, *, fg=Color(255,255,255), bg=Color(0,0,0), char=" "):
        self.fill(0, 0, self.w, self.h, fg=fg, bg=bg, char=char)
    
    def update(self):
        with self.lock:
            t0 = perf_counter()
            self._update_count = 0
            for y in range(self.h):
                for x in range(self.w):
                    pixel = self._pixels[x][y]
                    if pixel._dirty:
                        self.render(pixel, x, y)
                        pixel._dirty = False
                        self._update_count += 1
            self.backend.cursor_pos = self.cursor_pos
            self.backend.flush()
            self._update_duration = perf_counter() - t0
    
    def render(self, pixel, x, y):
        self.backend.cursor_pos = (x, y)
        self.backend.fg = pixel.fg
        self.backend.bg = pixel.bg
        self.backend.write(pixel.char)

    def print(self, text, x, y, *, fg=None, bg=None):
        with self.lock:
            tab = x
            for line in text.splitlines():
                for ch in line:
                    if y < 0 or x < 0 or y >= self.h or x >= self.w:
                        continue
                    pixel = self._pixels[x][y]
                    pixel.char = ch
                    if fg:
                        pixel.fg = fg
                    if bg:
                        pixel.bg = bg
                    x += 1
                y += 1
                x = tab
        return (x, y)

class PixelData:
    def __init__(self, *, fg=Color(255, 255, 255), bg=Color(0, 0, 0), char=" "):
        self._dirty = True
        self._char = None
        self._fg = None
        self._bg = None
        self.fg = fg
        self.bg = bg
        self.char = char
    
    @property
    def char(self):
        return self._char
    
    @char.setter
    def char(self, char):
        if len(char) != 1:
            raise Exception("Character must have length 1")
        if self._char != char:
            self._char = char
            self._dirty = True
    
    @property
    def fg(self):
        return self._fg

    @fg.setter
    def fg(self, value):
        if self._fg != value:
            self._fg = value
            self._dirty = True
    
    @property
    def bg(self):
        return self._bg
    
    @bg.setter
    def bg(self, value):
        if self._bg != value:
            self._bg = value
            self._dirty = True

    def __str__(self):
        return "({}; fg {}; bg {})".format(self.char, self.fg, self.bg)
    
    def __eq__(self, other):
        try:
            return self.fg == other.fg and self.bg == other.bg and self.char == other.char
        except AttributeError:
            return False
