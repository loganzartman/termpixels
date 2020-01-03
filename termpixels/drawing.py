from termpixels.pixeldata import PixelData
from time import perf_counter

# Boxes
_BOX_T = 0
_BOX_B = 1
_BOX_L = 2
_BOX_R = 3
_BOX_TL = 4
_BOX_TR = 5
_BOX_BL = 6
_BOX_BR = 7

BOX_CHARS_ASCII = "--||++++"
BOX_CHARS_LIGHT = "──││┌┐└┘"
BOX_CHARS_LIGHT_ARC = "──││╭╮╰╯"
BOX_CHARS_HEAVY = "━━┃┃┏┓┗┛"
BOX_CHARS_DOUBLE = "══║║╔╗╚╝"
BOX_CHARS_LIGHT_DOUBLE_TOP = "═─││╒╕└┘"

# Frames
# logical indices for strings of frame characters
_FRAME_NO = -1 # not a frame character
_FRAME_H = 0   # horizontal index
_FRAME_V = 1   # vertical
_FRAME_TL = 2  # top left corner
_FRAME_TR = 3  # top right corner
_FRAME_BL = 4  # bottom left corner
_FRAME_BR = 5  # bottom right corner
_FRAME_VR = 6  # vertical and right
_FRAME_VL = 7  # vertical and left
_FRAME_HB = 8  # horizontal and bottom
_FRAME_HT = 9  # horizontal and top
_FRAME_VH = 10 # vertical and horizontal
_FRAME_L = 11  # left
_FRAME_T = 12  # top
_FRAME_R = 13  # right
_FRAME_B = 14  # bottom

# bitmask representing left, top, right, bottom
# each bit represents whether a character "points" or "flows" in that direction.
# for example, a top left corner (_FRAME_TL, e.g. "┌") points right and down.
_FRAME_GEOMETRY = {
    _FRAME_NO: 0b0000,
    _FRAME_L:  0b1000,
    _FRAME_T:  0b0100,
    _FRAME_R:  0b0010,
    _FRAME_B:  0b0001,
    _FRAME_H:  0b1010,
    _FRAME_V:  0b0101,
    _FRAME_TL: 0b0011,
    _FRAME_TR: 0b1001,
    _FRAME_BL: 0b0110,
    _FRAME_BR: 0b1100,
    _FRAME_VR: 0b0111,
    _FRAME_VL: 0b1101,
    _FRAME_HB: 0b1011,
    _FRAME_HT: 0b1110,
    _FRAME_VH: 0b1111
}
# inverse mapping of _FRAME_GEOMETRY
_GEOMETRY_FRAME = {geom: char for char, geom in _FRAME_GEOMETRY.items()}

FRAME_CHARS_LIGHT = "─│┌┐└┘├┤┬┴┼╴╵╶╷"
FRAME_CHARS_LIGHT_LONG = "─│┌┐└┘├┤┬┴┼─│─│"
FRAME_CHARS_HEAVY = "━┃┏┓┗┛┣┫┳┻╋╸╹╺╻"
FRAME_CHARS_HEAVY_LONG = "━┃┏┓┗┛┣┫┳┻╋━┃━┃"
FRAME_CHARS_DOUBLE = "═║╔╗╚╝╠╣╦╩╬═║═║"

# Spinners
SPINNER_SIX = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
SPINNER_PIPE = "-\\|/"
SPINNER_BAR = ["[    ]",
               "[=   ]",
               "[==  ]",
               "[=== ]",
               "[ ===]",
               "[  ==]",
               "[   =]",
               "[    ]",
               "[   =]",
               "[  ==]",
               "[ ===]",
               "[=== ]",
               "[==  ]",
               "[=   ]"]
SPINNER_DOTS = ["   ",
                ".  ",
                ".. ",
                "...",
                " ..",
                "  ."]
SPINNER_MOON = "🌑🌒🌓🌔🌕🌖🌗🌘"
SPINNER_CLOCK = "🕛🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚"
SPINNER_BOX = "▖▘▝▗"

PROGRESS_SMOOTH = {
    "start": "",
    "end": "",
    "bar_char": "█",
    "head_chars": " ▏▎▍▌▋▊"
}

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

def draw_box(buffer, x, y, w, h, chars=BOX_CHARS_LIGHT, **kwargs):
    """Draw a box using a set of box-drawing characters.

    w and h must be positive (greater than zero) integers, or nothing is drawn.

    If either dimension is 1, a line is drawn instead of a box.
    If both dimensions are 1, nothing is drawn.
    """
    if w < 1 or h < 1:
        return
    if h > 1:
        for px, char_id in ((max(0, x + w - 1), _BOX_R), (x, _BOX_L)):
            for py in range(y, y + h):
                buffer.print(chars[char_id], px, py, **kwargs)
    if w > 1:
        for py, char_id in ((max(0, y + h - 1), _BOX_B), (y, _BOX_T)):
            for px in range(x, x + w):
                buffer.print(chars[char_id], px, py, **kwargs)
    if w > 1 and h > 1:
        buffer.print(chars[_BOX_TL], x, y, **kwargs)
        buffer.print(chars[_BOX_TR], x + w - 1, y, **kwargs)
        buffer.print(chars[_BOX_BL], x, y + h -1, **kwargs)
        buffer.print(chars[_BOX_BR], x + w - 1, y + h - 1, **kwargs)

def _invert_geometry(geom):
    """Invert (rotate 180 degrees) a 4-bit frame geometry bitmask."""
    return (geom >> 2) | ((geom << 2) & 0b1100)

def _frame_connecting_char(buffer, char, x, y, chars):
    """Connect a frame character to neighbors and return the resuling character index.
    
    For example, imagine we are drawing a horizontal line "─" on top of a corner "└".
    We want to produce the combined character "┴".
    """

    assert char != _FRAME_NO

    def buffer_char(x, y):
        if not buffer.in_bounds(x, y):
            return -1
        char = buffer[x, y].char
        try:
            return chars.index(char)
        except ValueError:
            return -1
    
    geom = _FRAME_GEOMETRY[char]
    geom |= _invert_geometry(_FRAME_GEOMETRY[buffer_char(x - 1, y)] & 0b0010)
    geom |= _invert_geometry(_FRAME_GEOMETRY[buffer_char(x, y - 1)] & 0b0001)
    geom |= _invert_geometry(_FRAME_GEOMETRY[buffer_char(x + 1, y)] & 0b1000)
    geom |= _invert_geometry(_FRAME_GEOMETRY[buffer_char(x, y + 1)] & 0b0100)

    assert geom != _FRAME_NO
    return _GEOMETRY_FRAME[geom]

def draw_frame(buffer, x, y, w, h, chars=FRAME_CHARS_LIGHT, **kwargs):
    """Draw a box, connecting it where it overlaps with an existing box."""

    frame_pixels = []
    def pixel(char_idx, x, y):
        char = chars[_frame_connecting_char(buffer, char_idx, x, y, chars)]
        frame_pixels.append((char, x, y))
    
    if w < 1 or h < 1:
        return
    if h > 1:
        for px in (max(0, x + w - 1), x):
            for py in range(y, y + h):
                pixel(_FRAME_V, px, py)
            if h > 1:
                pixel(_FRAME_B, px, y)
                pixel(_FRAME_T, px, y + h - 1)
    if w > 1:
        for py in (max(0, y + h - 1), y):
            for px in range(x, x + w):
                pixel(_FRAME_H, px, py)
            if w > 1:
                pixel(_FRAME_R, x, py)
                pixel(_FRAME_L, x + w - 1, py)
    if w > 1 and h > 1:
        pixel(_FRAME_TL, x, y)
        pixel(_FRAME_TR, x + w - 1, y)
        pixel(_FRAME_BL, x, y + h -1)
        pixel(_FRAME_BR, x + w - 1, y + h - 1)

    for char, x, y in frame_pixels:
        buffer.put_char(char, x, y, **kwargs)

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

def draw_progress(buffer, x, y, *, w, progress, start="[", end="]", bar_char="=", empty_char=" ", head_chars=">", fg=None, bg=None):
    """Draw a horizontal, left-to-right progress bar.

    w -- the total width of the progress bar, including start and end strings
    progress -- the progress in the range [0, 1]
    start -- a string to display at the left of the progress bar
    end -- a string to display at the right of the progress bar
    bar_char -- a character with which to fill the completed portion of the bar
    empty_char -- a character with which to fill the remaining portion of the bar
    head_chars -- a sequence of characters to display at the "head" of the bar,
                  where the sequence is indexed based on what fraction of the
                  head character should be filled.
    fg -- foreground color (default None to preserve)
    bg -- background color (default None to preserve)
    """

    if len(bar_char) != 1:
        raise ValueError("bar_char must have length 1")
    if len(empty_char) != 1:
        raise ValueError("empty_char must have length 1")
    
    bar_space = w - len(start) - len(end)
    if bar_space < 0:
        return
    progress = min(1, max(0, progress))
    bar_filled_chars = int(progress * bar_space)

    buffer.fill(x, y, w, 1, fg=fg, bg=bg)
    buffer.print(start, x, y)
    buffer.print(bar_char * bar_filled_chars)
    if bar_filled_chars < bar_space:
        f = progress * bar_space - bar_filled_chars
        head_char = head_chars[int(f * len(head_chars))]
        buffer.print(head_char)
    buffer.print(empty_char * (bar_space - bar_filled_chars - 1))
    buffer.print(end)

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
