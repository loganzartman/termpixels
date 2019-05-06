import colorsys
from functools import lru_cache

class Color:
    """Represents an immutable 24-bit RGB color
    
    Since Colors are immutable, it is good practice to re-use instances, and it
    is a BAD IDEA to try to modify their internal values. The most performant
    way of constructing colors is to use the static methods which provide 
    support for various formats and are memoized for efficiency.
    """

    def __init__(self, *args):
        """Construct a Color from one of several formats:
        
        Color(color) - copy constructor
        Color(R,G,B) - three integers in the range [0,255]
        Color(RGB) - one integer in the format 0xRRGGBB
        Color((r,g,b)) - an iterable of three floats in the range [0,1]
        """
        r = 0
        g = 0
        b = 0

        if len(args) == 3:
            r, g, b = args
        elif len(args) == 1:
            if isinstance(args[0], Color):
                r = args[0].r
                g = args[0].g
                b = args[0].b 
            else:
                try:
                    c = Color.unpack(args[0])
                    r = c.r
                    g = c.g
                    b = c.b
                except:
                    try:
                        r = args[0][0] * 255
                        g = args[0][1] * 255
                        b = args[0][2] * 255
                    except:
                        raise Exception("Invalid single argument constructor for Color: {}".format(args[0]))
        else:
            raise Exception("Invalid constructor for Color: {}".format(args))

        clip = lambda c: max(0, min(255, round(c)))
        self._r = clip(r)
        self._g = clip(g)
        self._b = clip(b)
        self._packed = Color.pack(self)
    
    @property
    def r(self):
        """The red component as an integer in the range [0,255]"""
        return self._r
    
    @property
    def g(self):
        """The green component as an integer in the range [0,255]"""
        return self._g
    
    @property
    def b(self):
        """The blue component as an integer in the range [0,255]"""
        return self._b

    def __eq__(self, other):
        try:
            return self._packed == other._packed
        except AttributeError:
            return False

    def __hash__(self):
        return self._packed
        
    def __add__(self, other):
        try:
            return Color(self.r + other.r, self.g + other.g, self.b + other.b)
        except:
            pass
        return Color(self.r + other, self.g + other, self.b + other)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        try:
            return Color(self.r - other.r, self.g - other.g, self.b - other.b)
        except:
            pass
        return Color(self.r - other, self.g - other, self.b - other)

    def __rsub__(self, other):
        try:
            return Color(other.r - self.r, other.g - self.g, other.b - self.b)
        except:
            pass
        return Color(other - self.r, other - self.g, other - self.b)

    def __mul__(self, other):
        try:
            return Color(self.r * other.r, self.g * other.g, self.b * other.b)
        except:
            pass
        return Color(self.r * other, self.g * other, self.b * other)

    def __rmul__(self, other):
        return self * other
    
    def __repr__(self):
        return "Color(r={}, g={}, b={})".format(self.r, self.g, self.b)

    @staticmethod  
    def pack(col):
        """Produce a "packed" color in the format 0xRRGGBB"""
        return (col.r << 16) | (col.g << 8) | (col.b)
    
    @staticmethod
    def unpack(val):
        """Unpack an integer in the format 0xRRGGBB into a Color instance"""
        return Color(val >> 16, (val >> 8) & 0xFF, val & 0xFF)

    @staticmethod
    @lru_cache(1024) # big cache here as it is more likely that we see repeated
                     # inputs since they are only 8 bits each.
    def rgb_int(r, g, b):
        """Construct a Color from RGB values in the range [0,255]"""
        return Color(r, g, b)

    @staticmethod
    @lru_cache(64) # memoizing float params is only useful if user is e.g. 
                   # constructing a lot of Colors with hard-coded float values
    def rgb(r, g, b):
        """Construct a Color from RGB values in the range [0,1]"""
        scale = lambda c: round(max(0, min(1, c)) * 255)
        return Color.rgb_int(scale(r), scale(g), scale(b))
    
    @staticmethod
    @lru_cache(64)
    def hsl(h, s, l):
        """Construct a Color from HSL values in the range [0,1]"""
        return Color.rgb(*colorsys.hls_to_rgb(h, l, s))


def color_to_16(color):
    """Convert color into ANSI 16-color format.
    """
    if color.r == color.g == color.b == 0:
        return 0
    bright = sum((color.r, color.g, color.b)) >= 127 * 3
    r = 1 if color.r > 63 else 0
    g = 1 if color.g > 63 else 0
    b = 1 if color.b > 63 else 0
    return (r | (g << 1) | (b << 2)) + (8 if bright else 0)

def color_to_256(color):
    """Convert color into ANSI 8-bit color format.
    Red is converted to 196
    This converter emits the 216 RGB colors and the 24 grayscale colors.
    It does not use the 16 named colors.
    """
    output = 0
    if color.r == color.g == color.b:
        # grayscale case
        if color.r == 0: # pure black
            output = 16
        elif color.r == 255: # pure white
            output = 231
        else:
            output = 232 + int(color.r / 256 * 24)
    else:
        # 216-color RGB
        scale = lambda c: int(c / 256 * 6)
        output = 16
        output += scale(color.b)
        output += scale(color.g) * 6
        output += scale(color.r) * 6 * 6
    return output