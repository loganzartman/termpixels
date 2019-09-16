from termpixels.pixeldata import PixelData
from time import perf_counter

_BOX_T = 0
_BOX_B = 1
_BOX_L = 2
_BOX_R = 3
_BOX_TL = 4
_BOX_TR = 5
_BOX_BL = 6
_BOX_BR = 7

BOX_CHARS_LIGHT = "──││┌┐└┘"
BOX_CHARS_HEAVY = "━━┃┃┏┓┗┛"
BOX_CHARS_DOUBLE = "══║║╔╗╚╝"
BOX_CHARS_LIGHT_DOUBLE_TOP = "═─││╒╕└┘"

SPINNER_SIX = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
SPINNER_PIPE = ["-", "\\", "|", "/"]

def draw_hline(buffer, y, char="─", **kwargs):
    """Draw a horizontal line along the given y coordinate.
    """
    for x in range(buffer.w):
        buffer.print(char, x, y, **kwargs)

def draw_vline(buffer, x, char="│", **kwargs):
    """Draw a vertical line along the given x coordinate.
    """
    for y in range(buffer.h):
        buffer.print(char, x, y, **kwargs)

def draw_box(buffer, x, y, w, h, chars=BOX_CHARS_LIGHT):
    """Draw a box using a set of box-drawing characters.
    """
    for px, char_id in ((x, _BOX_L), (x + w - 1, _BOX_R)):
        for py in range(y, y + h):
            buffer.print(chars[char_id], px, py)
    for py, char_id in ((y, _BOX_T), (y + h - 1, _BOX_B)):
        for px in range(x, x + w):
            buffer.print(chars[char_id], px, py)
    buffer.print(chars[_BOX_TL], x, y)
    buffer.print(chars[_BOX_TR], x + w - 1, y)
    buffer.print(chars[_BOX_BL], x, y + h -1)
    buffer.print(chars[_BOX_BR], x + w - 1, y + h - 1)

def draw_spinner(buffer, x, y, *, freq=1, t=None, frames=SPINNER_SIX, **kwargs):
    """Print a repeating animation.

    Given a list of frames, selects a frame based on the given time (defaults to
    the current time) and frequency (defaults to 1hz).

    Typically called within a "frame" event listener to update the animation.
    """
    if t is None:
        t = perf_counter()
    period = 1 / freq
    f = (t % period) / period
    frame = int(f * len(frames))
    buffer.print(frames[frame], x, y, **kwargs)

def draw_colormap(buffer, colormap, x, y, *, w, h, char="█"):
    """Draw a color bitmap where each color is represented as one character cell.

    colormap is a one-dimensional list of colors representing a 2D bitmap. Each
    row of colors should be listed in sequence. The indexing formula is y*w+x.

    colormap may contain Nones, indicating transparent pixels. Drawing a 
    transparent pixel will preserve the cell's contents.

    Provide x and y coordinate for top-left of the bitmap in the destination. 

    Provide the width and height of the colormap.
    """
    for dx in range(w):
        for dy in range(h):
            idx = dy * w + dx
            if colormap[idx] is None:
                continue
            px = x + dx
            py = y + dy
            if not buffer.in_bounds(px, py):
                continue
            pixel = buffer[px, py]
            pixel.char = char
            pixel.fg = colormap[idx]

def draw_colormap_2x(buffer, colormap, x, y, *, w, h, char="▀"):
    """Draw a color bitmap at 2x vertical resolution using a box drawing character.
    
    Creates two sub-pixels per terminal character (super-pixel) by using a box
    drawing character and setting both foreground and background colors.

    colormap is a one-dimensional list of colors representing a 2D bitmap. Each
    row of colors should be listed in sequence. The indexing formula is y*w+x.
    
    colormap may contain Nones, indicating transparent sub-pixels. Drawing a
    super-pixel that is completely transparent will preserve its contents. 
    Drawing a super-pixel with one transparent sub-pixel will cause the 
    super-pixel's background color to show through, but will destroy its 
    contents.

    Provide x and y coordinate for top-left of destination in super-pixel 
    coordinates.
    The y coordinate may be fractional and will be rounded to the nearest
    sub-pixel.

    Provide width and height of colormap (in sub-pixel size). When drawn, the 
    vertical dimension of the colormap will be reduced by half. 
    """
    for dx in range(w):
        for dy in range(h):
            idx = dy * w + dx
            if colormap[idx] is None:
                continue
            px = x + dx
            fy = y + dy * 0.5
            py = int(fy)
            if not buffer.in_bounds(px, py):
                continue
            pixel = buffer[px, py]
            if fy % 1 < 0.5:
                pixel.char = char
                pixel.fg = colormap[idx]
            else:
                if pixel.char != char:
                    pixel.char = char
                    pixel.fg = pixel.bg
                pixel.bg = colormap[idx]
