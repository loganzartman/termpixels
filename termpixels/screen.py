from copy import copy
from unix import UnixBackend

class Screen:
    def __init__(self, backend):
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

    def resize(self, w, h):
        self.backend.clear_screen()
        self._pixels = [[self._pixels[x][y] if x < self._w and y < self._h else PixelData() 
                         for y in range(h)] for x in range(w)]
        self._pixelCache = [[None for y in range(h)] for x in range(w)]
        self._w = w
        self._h = h
        self.update()

    @property
    def show_cursor(self):
        return self.backend.show_cursor
    
    @show_cursor.setter
    def show_cursor(self, show):
        self.backend.show_cursor = show
    
    def at(self, x, y):
        if x >= self.w or x < 0:
            raise Exception("x position {} out of bounds".format(x))
        if y >= self.h or y < 0:
            raise Exception("y position {} out of bounds".format(y))
        return self._pixels[x][y]

    def fill(self, pixel, x, y, w, h):
        for i in range(x, x + w):
            for j in range(y, y + h):
                if i < 0 or j < 0  or i >= self.w or j >= self.h:
                    continue
                self._pixels[i][j] = copy(pixel)
    
    def clear_to(self, pixel):
        self.fill(pixel, 0, 0, self.w, self.h)
    
    def update(self):
        for y in range(self.h):
            for x in range(self.w):
                pixel = self.at(x, y)
                if pixel != self._pixelCache[x][y]:
                    self.render(pixel, x, y)
                self._pixelCache[x][y] = copy(pixel)
        self.backend.cursor_pos = self.cursor_pos
        self.backend.flush()
    
    def render(self, pixel, x, y):
        self.backend.cursor_pos = (x, y)
        self.backend.fg = pixel.fg
        self.backend.bg = pixel.bg
        self.backend.write(pixel.char)

    def print(self, text, x, y):
        for ch in text:
            if x >= self.w:
                return
            self.at(x, y).char = ch
            x += 1

class PixelData:
    def __init__(self):
        self.fg = Color(255, 255, 255)
        self.bg = Color(0, 0, 0)
        self.char = " "
    
    @property
    def char(self):
        return self._char
    
    @char.setter
    def char(self, char):
        if len(char) != 1:
            raise Exception("Character must have length 1")
        self._char = char

    def __str__(self):
        return "({}; fg {}; bg {})".format(self.char, self.fg, self.bg)
    
    def __eq__(self, other):
        try:
            return self.fg == other.fg and self.bg == other.bg and self.char == other.char
        except AttributeError:
            return NotImplemented

class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
    
    def __eq__(self, other):
        try:
            return self.r == other.r and self.g == other.g and self.b == other.b
        except AttributeError:
            return NotImplemented
