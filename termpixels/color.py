import colorsys

class Color:
    def __init__(self, *args):
        r = 0
        g = 0
        b = 0

        if len(args) == 3:
            r, g, b = args
        elif len(args) == 1:
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
        return (col.r << 16) | (col.g << 8) | (col.b)
    
    @staticmethod
    def unpack(val):
        return Color(val >> 16, (val >> 8) & 0xFF, val & 0xFF)
    
    @staticmethod
    def rgb(r, g, b):
        scale = lambda c: int(max(0, min(1, c)) * 255)
        return Color(scale(r), scale(g), scale(b))
    
    @staticmethod
    def hsl(h, s, l):
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
        if color.r == 255: # pure white
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