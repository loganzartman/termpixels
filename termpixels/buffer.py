from termpixels.color import Color
from termpixels.util import terminal_char_len, splitlines_print
from termpixels.pixeldata import PixelData

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
        self._pixels = [[self._pixels[x][y] if x < self._w and y < self._h else PixelData() 
                        for y in range(h)] for x in range(w)]
        self._w = w
        self._h = h
    
    def in_bounds(self, x, y):
        return x >= 0 and y >= 0 and x < self.w and y < self.h
    
    def at_unsafe(self, x, y):
        return self._pixels[x][y]

    def at(self, x, y, *, clip=False):
        """Get the PixelData instance for a particular location.

        Setting clip to true clips the provided position to remain inside the
        screen buffer. If clip is not enabled, an Exception will be raised if 
        the provided position is outside the bounds of the screen buffer.

        The returned PixelData instance may be mutated to modify the contents
        of the screen buffer.
        """
        if clip:
            x = max(0, min(self.w-1, x))
            y = max(0, min(self.h-1, y))
        if x >= self.w or x < 0:
            raise Exception("x position {} out of bounds".format(x))
        if y >= self.h or y < 0:
            raise Exception("y position {} out of bounds".format(y))
        return self.at_unsafe(x, y)
    
    def __getitem__(self, xy):
        x, y = xy
        return self.at(x, y)

    def __setitem__(self, xy, val):
        x, y = xy
        self.at(x, y).set(val)

    def fill(self, x, y, w, h, *, fg=None, bg=None, char=None):
        """Fill a rectangular region of the screen with the given attributes.

        If an attribute value is not specified (set to None), then that 
        attribute will not be filled in, and instead be left unchanged.
        
        Any part of the rectangle that lies outside of the screen buffer will
        be silently ignored.
        """
        for i in range(x, x + w):
            for j in range(y, y + h):
                if i < 0 or j < 0  or i >= self.w or j >= self.h:
                    continue
                pixel = self.at_unsafe(i, j)
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
        blank = PixelData(fg=fg, bg=bg, char=char)
        for i in range(0, self.w):
            for j in range(0, self.h):
                self.at_unsafe(i, j).set(blank)
    
    def blit(self, buffer, x=0, y=0, x0=0, y0=0, x1=None, y1=None):
        """ copy a buffer to this buffer 

        Copy a sub-region by specifying two corners (x0, y0) and (x1, y1) where
        all coordinates are inclusive.

        Also supports blitting anything that implements a blit_to() method with
        the same signature, but with the "buffer" argument being the 
        destination rather than the source buffer.
        """
        if not isinstance(buffer, Buffer):
            if hasattr(buffer, "blit_to") and callable(buffer.blit_to):
                return buffer.blit_to(self, x=x, y=y, x0=x0, y0=y0, x1=x1, y1=y1)
            raise ValueError("buffer must be a Buffer instance or have a blit_to() method.")

        if x1 == None:
            x1 = buffer.w
        if y1 == None:
            y1 = buffer.h
        
        x0, x1 = (min(x0, x1), max(x0, x1))
        y0, y1 = (min(y0, y1), max(y0, y1))
        
        for dx in range(min(x1-x0+1, self.w)):
            for dy in range(min(y1-y0+1, self.h)):
                dst_x = x + dx
                dst_y = y + dy
                src_x = x0 + dx
                src_y = y0 + dy
                if not self.in_bounds(dst_x, dst_y) or not buffer.in_bounds(src_x, src_y):
                    continue
                self.at_unsafe(dst_x, dst_y).set(buffer.at_unsafe(src_x, src_y))
    
    def put_char(self, ch, x, y, *, fg=None, bg=None):
        """Put a single character and/or colors at a particular location.

        Puts a single character at the given x, y coordinates, only if those
        coordinates are within the bounds of the buffer. Coordinates are also
        considered out of bounds if the character has a width greater than 1 
        and it would not be entirely within the bounds of the buffer. If the 
        given coordinates are out of bounds, this method has no effect.

        If fg or bg colors are specified, they replace the fg or bg colors at
        the given coordinates. If None is given for either argument, the 
        existing colors are left unchanged.

        Returns the width of the character that was provided, even if it was 
        out of bounds.
        """
        ch_len = terminal_char_len(ch)
        if x >= 0 and y >= 0 and x + ch_len <= self.w and y < self.h:
            pixel = self.at_unsafe(x, y)
            pixel.char = ch
            if fg:
                pixel.fg = fg
            if bg:
                pixel.bg = bg
            
            # handle fullwidth (double-wide) characters.
            # clear character and set fg and bg so that values make sense if
            # the fullwidth character is later removed.
            if ch_len > 1:
                assert ch_len == 2
                shadowed = self.at_unsafe(x+1, y)
                shadowed.char = " "
                if fg:
                    shadowed.fg = fg
                if bg:
                    shadowed.bg = bg
        return ch_len
    
    def print(self, text, x=None, y=None, *, line_start=None, fg=None, bg=None):
        """Print a string of text starting at a particular location.

        Prints a string of one or more lines of text starting at the given
        location, ignoring text that falls outside the bounds of the buffer.
        Newlines can be used to move the cursor down a line and back to the
        line start position. The cursor is NOT necessarily moved all the way
        to the left of the screen. To set the x position to which the cursor
        returns after a newline, provide the line_start keyword argument.
        
        Returns the location of the cursor after the text has been printed.
        
        If a location is not given, then the text will be printed at the end
        of the last text printed, or at (0,0) if nothing has been printed. 
        This location is stored in the Buffer's print_pos attribute.

        Replaces the foreground and background of modified pixels if each is 
        specified. If colors are not specified, they will be left alone. 
        
        This means that you could, for example, use fill() to set a background 
        and foreground color for the whole screen, and then print text on top 
        using print().
        """
        if x is None:
            x = self.print_pos[0]
        if y is None:
            y = self.print_pos[1]
        if line_start is None:
            line_start = x

        y0 = y
        x0 = x
        for linenum, line in enumerate(splitlines_print(text)):
            y = y0 + linenum
            x = x0 if linenum == 0 else line_start
            for ch in line:
                ch_len = self.put_char(ch, x, y, fg=fg, bg=bg)
                x += ch_len
    
        self.print_pos = (x, y)
        return self.print_pos
