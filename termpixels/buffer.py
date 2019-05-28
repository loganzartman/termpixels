from threading import Lock
from copy import copy
from time import perf_counter
from termpixels.color import Color
from termpixels.util import terminal_char_len, splitlines_print

class Buffer:
    """Stores a 2D buffer of PixelData instances.

    A Buffer maintains a two-dimensional buffer of PixelData instances. It 
    provides many methods of manipulating them, such as fill() and print(),
    as well as direct "pixel" access using the at() method.

    Screen is an extension of Buffer which supports rendering it to a terminal.
    An existing Buffer may be rendered to a terminal by using the blit()
    method of a Screen instance.
    """

    def __init__(self, w, h):
        self.lock = Lock()
        self.cursor_pos = (0, 0)
        self.print_pos = (0, 0)
        self._w = 0
        self._h = 0
        self._pixels = []
        self.resize(w, h)
    
    @property
    def w(self):
        """Get the width of the screen buffer."""
        return self._w
    
    @property
    def h(self):
        """Get the height of the screen buffer."""
        return self._h

    def resize(self, w, h):
        """Resize the screen buffer to the given width and height."""
        with self.lock:
            self._pixels = [[self._pixels[x][y] if x < self._w and y < self._h else PixelData() 
                            for y in range(h)] for x in range(w)]
            self._w = w
            self._h = h
    
    def in_bounds(self, x, y):
        return x >= 0 and y >= 0 and x < self.w and y < self.h

    def at(self, x, y, *, clip=False):
        """Get the PixelData instance for a particular location.

        Setting clip to true clips the provided position to remain inside the
        screen buffer. If clip is not enabled, an Exception will be raised if 
        the provided position is outside the bounds of the screen buffer.

        The returned PixelData instance may be mutated to modify the contents
        of the screen buffer.
        """
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
        """Fill a rectangular region of the screen with the given attributes.

        If an attribute value is not specified (set to None), then that 
        attribute will not be filled in, and instead be left unchanged.
        
        Any part of the rectangle that lies outside of the screen buffer will
        be silently ignored.
        """
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
        """Fill the entire screen buffer with the given attributes.

        Unlike fill(), all attributes must be specified. If not specified, they
        will be given default values instead.
        """
        with self.lock:
            blank = PixelData(fg=fg, bg=bg, char=char)
            for i in range(0, self.w):
                for j in range(0, self.h):
                    self._pixels[i][j].set(blank)
    
    def blit(self, buffer, x=0, y=0, x0=0, y0=0, x1=None, y1=None):
        """ copy a buffer (or a rectangular region of it) to this buffer 

        Also supports blitting anything that implements a blit_to() method with
        the same signature, but with the "buffer" argument being the 
        destination rather than the source buffer.
        """
        if x1 == None:
            x1 = buffer.w
        if y1 == None:
            y1 = buffer.h
        
        if not isinstance(buffer, Buffer):
            if hasattr(buffer, "blit_to") and callable(buffer.blit_to):
                return buffer.blit_to(self, x=x, y=y, x0=x0, y0=y0, x1=x1, y1=y1)
            raise ValueError("buffer must be a Buffer instance or have a blit_to() method.")
        
        for dx in range(min(x1-x0, self.w)):
            for dy in range(min(y1-y0, self.h)):
                dst_x = x + dx
                dst_y = y + dy
                src_x = x0 + dx
                src_y = y0 + dy
                if not self.in_bounds(dst_x, dst_y) or not buffer.in_bounds(src_x, src_y):
                    continue
                self._pixels[dst_x][dst_y].set(buffer._pixels[src_x][src_y])
    
    def print(self, text, x=None, y=None, *, fg=None, bg=None):
        """Print a string of text starting at a particular location.

        Prints a string of one or more lines of text starting at the given
        location, ignoring text that falls outside the bounds of the buffer.
        Newlines can be used to move the cursor down a line and back to the
        initial x position. The cursor is NOT necessarily moved all the way
        to the left of the screen.
        
        Returns the location of the cursor after the text has been printed.
        
        If a location is not given, then the text will be printed at the end
        of the last text printed, or at (0,0) if nothing has been printed.

        Replaces the foreground and background of modified pixels if each is 
        specified. If colors are not specified, they will be left alone. 
        
        This means that you could, for example, use fill() to set a background 
        and foreground color for the whole screen, and then print text on top 
        using print().
        """
        with self.lock:
            if x == None:
                x = self.print_pos[0]
            if y == None:
                y = self.print_pos[1]

            y0 = y
            tab = x
            for linenum, line in enumerate(splitlines_print(text)):
                y = y0 + linenum
                x = tab
                for ch in line:
                    if y < 0 or x < 0 or y >= self.h or x >= self.w:
                        continue
                    ch_len = terminal_char_len(ch)
                    pixel = self._pixels[x][y]
                    pixel.char = ch
                    if fg:
                        pixel.fg = fg
                    if bg:
                        pixel.bg = bg
                    
                    # handle fullwidth (double-wide) characters
                    if ch_len > 1 and x < self.w - 1:
                        shadowed = self._pixels[x+1][y]
                        shadowed.char = " "
                        if fg:
                            shadowed.fg = fg
                        if bg:
                            shadowed.bg = bg

                    x += ch_len
        self.print_pos = (x, y)
        return self.print_pos

class PixelData:
    """Represents a single character cell.

    Encapsulates a character, a foreground color, and a background color.
    Used internally by Screen.
    """

    def __init__(self, *, fg=Color(255, 255, 255), bg=Color(0, 0, 0), char=" "):
        self._hash = None
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
            self._hash = None
    
    @property
    def fg(self):
        return self._fg

    @fg.setter
    def fg(self, value):
        if self._fg != value:
            self._fg = value
            self._hash = None
    
    @property
    def bg(self):
        return self._bg
    
    @bg.setter
    def bg(self, value):
        if self._bg != value:
            self._bg = value
            self._hash = None
    
    def set(self, pixel):
        self._fg = pixel._fg
        self._bg = pixel._bg
        self._char = pixel._char
        self._hash = None

    def __str__(self):
        return "({}; fg {}; bg {})".format(self.char, self.fg, self.bg)
    
    def __eq__(self, other):
        if hash(self) != hash(other):
            return False
        return self.fg == other.fg and self.bg == other.bg and self.char == other.char
    
    def __hash__(self):
        if self._hash is None:
            self._hash = hash((self.char, self.fg, self.bg))
        return self._hash
