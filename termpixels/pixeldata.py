from termpixels.color import Color

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
