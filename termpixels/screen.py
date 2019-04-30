from threading import Lock
from copy import copy
from time import perf_counter
from termpixels.color import Color
from termpixels.util import terminal_char_len

class Screen:
    def __init__(self, backend, input):
        """Provides a pixel-like abstraction on top of a backend.

        Screen tries to abstract away the global state of cursor position and 
        current text style that is present in Unix-like terminal interfaces.
        Instead, it seeks to provide an API more similar to an image buffer.

        A Screen maintains a two-dimension buffer of PixelData instances. It 
        provides many methods of manipulating them, such as fill() and print(),
        which support positions and colors. Once desired changes are made, the
        user calls the update() method, and the screen updates only the "pixels"
        that have changed in a reasonably efficient manner.

        Once the update is complete, Screen will position the terminal's cursor at
        the position specified by the cursor_pos property. This allows the user to
        position the cursor for aesthetic purposes.
        """
        self.lock = Lock()
        self.backend = backend
        self.cursor_pos = (0, 0)
        self._w = 0
        self._h = 0
        self._pixels = []
        self.resize(backend.size[0], backend.size[1])
        input.listen("resize", lambda _: self.resize(backend.size[0], backend.size[1]))    
        self.show_cursor = False 
    
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
            self._pixels_cache = [[PixelData(fg=None, bg=None, char=" ") for y in range(h)] for x in range(w)]
            self._w = w
            self._h = h
            self.backend.clear_screen()
        self.update()

    @property
    def show_cursor(self):
        """Get whether the cursor is visible."""
        return self.backend.show_cursor
    
    @show_cursor.setter
    def show_cursor(self, show):
        """Set whether the cursor is visible."""
        self.backend.show_cursor = show
    
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
    
    def update(self):
        """Commit the changes in the screen buffer to the backend (terminal).

        Determines which pixels (characters) have been modified from their 
        previous value, and re-draws those pixels using the backend.

        It should be noted that the pixel attributes are compared to their
        previous values. This means that if you, for example, clear a black
        screen to white, and then clear it back to black, no pixels will be
        re-rendered. This means that it is reasonable to clear and re-render
        the entire screen whenever you make an update, if it seems too
        challenging to manually make only the necessary changes.
        """
        with self.lock:
            t0 = perf_counter()
            self._update_count = 0
            for y in range(self.h):
                for x in range(self.w):
                    pixel = self._pixels[x][y]
                    if pixel._hash == None and pixel != self._pixels_cache[x][y]:
                        self._pixels_cache[x][y].set(pixel)
                        self._update_count += 1
                        # handle fullwidth (double-wide) characters
                        if x > 0 and terminal_char_len(self._pixels[x-1][y].char) > 1:
                            continue
                        self.render(pixel, x, y)
            self.backend.cursor_pos = self.cursor_pos
            self.backend.flush()
            self._update_duration = perf_counter() - t0
    
    def render(self, pixel, x, y):
        """Use the backend to redraw a particular PixelData instance.
        
        This is called internally by update() and generally should not be used.
        """
        self.backend.cursor_pos = (x, y)
        self.backend.fg = pixel.fg
        self.backend.bg = pixel.bg
        self.backend.write(pixel.char)

    def print(self, text, x, y, *, fg=None, bg=None):
        """Print a string of text starting at a particular location.

        Prints a string of one or more lines of text starting at the given
        location, ignoring text that falls outside the bounds of the buffer.
        
        Replaces the foreground and background of modified pixels if each is 
        specified. If colors are not specified, they will be left alone. 
        
        This means that you could, for example, use fill() to set a background 
        and foreground color for the whole screen, and then print text on top 
        using print().
        """
        with self.lock:
            y0 = y
            tab = x
            for linenum, line in enumerate(text.splitlines()):
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
        return (x, y)

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
