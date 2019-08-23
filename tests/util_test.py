from termpixels.util import set_ambiguous_is_wide
from termpixels.util import terminal_char_len
from termpixels.util import terminal_len
from termpixels.util import terminal_printable
from termpixels.util import splitlines_print
from termpixels.util import wrap_text
from unicodedata import east_asian_width
import pytest

# some characters with known properties
control_char = "\b"
narrow_char = "A"
wide_char = "ᄀ"
ambiguous_char = "§"
assert east_asian_width(narrow_char) == "Na"
assert east_asian_width(wide_char) == "W"
assert east_asian_width(ambiguous_char) == "A"

def test_terminal_char_len():
    assert terminal_char_len(narrow_char) == 1
    assert terminal_char_len(wide_char) == 2
    assert terminal_char_len(control_char) == 0

    # no way to tell tab width without context
    assert terminal_char_len("\t") == None

    set_ambiguous_is_wide(False)
    assert terminal_char_len(ambiguous_char) == 1

    set_ambiguous_is_wide(True)
    assert terminal_char_len(ambiguous_char) == 2

def test_terminal_len():
    test_string = "你好 - Hello"
    assert terminal_len(test_string) == sum(terminal_char_len(i) for i in test_string)

def test_terminal_printable():
    assert terminal_printable(narrow_char)
    assert terminal_printable(wide_char)
    assert not terminal_printable(control_char)

def test_splitlines_print():
    assert splitlines_print("a\nb") == ["a", "b"]
    assert splitlines_print("a\r\nb") == ["a", "b"]
    assert splitlines_print("a\n\nb") == ["a", "", "b"]
    assert splitlines_print("a\n\r\n\nb") == ["a","", "", "b"]

def test_wrap_text():
    assert wrap_text("a b c d e", 3) == "a b\nc d\ne"
    assert wrap_text("alpha beta", 6) == "alpha \nbeta"
    assert wrap_text("你好", 2) == "你\n好"
