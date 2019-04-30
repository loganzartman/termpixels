from unicodedata import east_asian_width
from functools import lru_cache

# not sure how to determine how ambiguous characters will be rendered
_ambiguous_is_wide = False
def set_ambiguous_is_wide(is_wide):
    """ set whether ambiguous characters are considered to be wide """
    if _ambiguous_is_wide != is_wide:
        _ambiguous_is_wide = is_wide
        terminal_char_len.clear_cache()

@lru_cache(1024)
def terminal_char_len(ch):
    """ return the width of a character in terminal cells """
    wide = ["F","W","A"] if _ambiguous_is_wide else ["F","W"]
    return 2 if east_asian_width(ch) in wide else 1

def terminal_len(s):
    """ return the width of a string in terminal cells """
    return sum(map(terminal_char_len, s))

