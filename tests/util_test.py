from termpixels.util import corners_to_box
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

def test_corners_to_box():
    assert corners_to_box(0, 0, 0, 0) == (0, 0, 1, 1)
    assert corners_to_box(0, 0, 1, 1) == (0, 0, 2, 2)
    assert corners_to_box(1, 1, 0, 0) == (0, 0, 2, 2)
    assert corners_to_box(5, 6, 7, 8) == (5, 6, 3, 3)
    assert corners_to_box(3, 3, -3, -3) == (-3, -3, 7, 7)

def test_terminal_char_len_narrow():
    assert terminal_char_len(narrow_char) == 1

def test_terminal_char_len_wide():
    assert terminal_char_len(wide_char) == 2

def test_terminal_char_len_control():
    assert terminal_char_len(control_char) == 0

def test_terminal_char_len_tab():
    # no way to tell tab width without context
    assert terminal_char_len("\t") == None

def test_terminal_char_len_ambiguous():
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

def test_terminal_printable_control():
    assert not terminal_printable(control_char)

def test_splitlines_print_unix():
    assert splitlines_print("a\nb") == ["a", "b"]
    assert splitlines_print("a\rb") == ["a", "b"]

def test_splitlines_print_windows():
    assert splitlines_print("a\r\nb") == ["a", "b"]

def test_splitlines_print_empty_lines():
    assert splitlines_print("a\n\nb") == ["a", "", "b"]
    assert splitlines_print("a\n\r\n\nb") == ["a","", "", "b"]

def test_wrap_text():
    assert wrap_text("a b c d e", 3) == "a b\nc d\ne"
    assert wrap_text("alpha beta", 6) == "alpha \nbeta"

def test_wrap_text_fullwidth():
    assert wrap_text("你好", 2) == "你\n好"
