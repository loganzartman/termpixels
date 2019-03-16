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