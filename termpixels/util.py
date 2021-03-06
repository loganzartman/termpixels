from unicodedata import east_asian_width, category
from functools import lru_cache
import re

def corners_to_box(x0, y0, x1, y1):
    """convert two corners (x0, y0, x1, y1) to (x, y, width, height)"""
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    return x0, y0, x1 - x0 + 1, y1 - y0 + 1

# not sure how to determine how ambiguous characters will be rendered
_ambiguous_is_wide = False
def set_ambiguous_is_wide(is_wide):
    """ set whether ambiguous characters are considered to be wide """
    global _ambiguous_is_wide
    if _ambiguous_is_wide != is_wide:
        _ambiguous_is_wide = is_wide
        terminal_char_len.cache_clear()

@lru_cache(1024)
def terminal_char_len(ch):
    """ return the width of a character in terminal cells """
    if ch == "\t":
        # we can't know the width of a tab without context
        # prefer using spaces instead
        return None
    if not terminal_printable(ch):
        return 0
    wide = ["F","W","A"] if _ambiguous_is_wide else ["F","W"]
    return 2 if east_asian_width(ch) in wide else 1

def terminal_len(s):
    """ return the width of a string in terminal cells """
    return sum(map(terminal_char_len, s))

def terminal_printable(ch):
    """ determine if a character is "printable" """
    return not category(ch).startswith("C")

_newline_regex = re.compile(r"\r\n|\r|\n")
def splitlines_print(s):
    """ like str.splitlines() but keeps all empty lines """
    return _newline_regex.split(s)

def wrap_text(text, line_len, *, tab_size=4, word_sep=re.compile(r"\s+|\W"),
              break_word=False, hyphen="", newline="\n"):
    """ returns a terminal-line-wrapped version of text """
    text = text.replace("\t", " " * tab_size)
    hl = terminal_len(hyphen)

    buf = []
    i = 0
    col = 0
    while i < len(text):
        match = word_sep.search(text, i)
        word = text[i:]
        sep = ""
        if match:
            word = text[i:match.start()]
            sep = match.group(0)
            i = match.end()
        else:
            i = len(text)

        # handle wrappable/breakable words
        wl = terminal_len(word)
        while col + wl > line_len:
            if break_word and col < line_len - hl or col == 0:
                while col + terminal_char_len(word[0]) <= line_len - hl:
                    buf.append(word[0])
                    col += terminal_char_len(word[0])
                    word = word[1:]
                buf.append(hyphen)
            buf.append(newline)
            col = 0
            wl = terminal_len(word)
        buf.append(word)
        col += wl

        # handle truncatable separators
        sl = terminal_len(sep)
        if col + sl > line_len:
            while col + terminal_char_len(sep[0]) <= line_len:
                buf.append(sep[0])
                col += terminal_char_len(sep[0])
                sep = sep[1:]
            buf.append(newline)
            col = 0
        else:
            buf.append(sep)
            col += sl

    return "".join(buf)
