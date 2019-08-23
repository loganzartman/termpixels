from termpixels.buffer import Buffer
from termpixels.buffer import PixelData
import pytest

def test_buffer_constructor_size():
    buffer = Buffer(8, 6)
    assert buffer.w == 8
    assert buffer.h == 6

def test_buffer_resize():
    buffer = Buffer(2, 2)
    buffer.resize(4, 3)
    assert buffer.w == 4
    assert buffer.h == 3

def test_buffer_in_bounds():
    buffer = Buffer(3, 2)
    assert buffer.in_bounds(0, 0)
    assert buffer.in_bounds(2, 1)

def test_buffer_in_bounds_not():
    buffer = Buffer(3, 2)
    assert not buffer.in_bounds(3, 1)
    assert not buffer.in_bounds(0, -1)

def test_buffer_at():
    buffer = Buffer(2, 2)
    assert isinstance(buffer.at(0, 0), PixelData)

def test_buffer_at_distinct():
    buffer = Buffer(2, 1)
    assert buffer.at(0, 0) is not buffer.at(1, 0)

def test_buffer_at_oob_raises():
    buffer = Buffer(2, 1)
    with pytest.raises(Exception, match="bounds"):
        buffer.at(3, 1)

def test_buffer_at_clip():
    buffer = Buffer(2, 2)
    assert buffer.at(2, 1, clip=True) is buffer.at(1, 1)
    assert buffer.at(-1, 0, clip=True) is buffer.at(0, 0)

def test_buffer_fill_char():
    buffer = Buffer(2, 1)
    buffer.fill(0, 0, buffer.w, buffer.h, char="X")
    assert buffer.at(0, 0).char == "X"
    assert buffer.at(1, 0).char == "X"

def test_buffer_fill_char_oob():
    buffer = Buffer(2, 1)
    buffer.fill(-1, -1, buffer.w + 1, buffer.h + 1, char="X")
    assert buffer.at(0, 0).char == "X"
    assert buffer.at(1, 0).char == "X"

def test_buffer_fill_char_none():
    buffer = Buffer(2, 1)
    buffer.at(0, 0).char = "X"
    buffer.at(1, 0).char = "Y"
    buffer.fill(0, 0, buffer.w, buffer.h, char=None)
    assert buffer.at(0, 0).char == "X"
    assert buffer.at(1, 0).char == "Y"

def test_buffer_clear_char():
    buffer = Buffer(2, 1)
    buffer.clear(char="X")
    assert buffer.at(0, 0).char == "X"
    assert buffer.at(1, 0).char == "X"

def test_print():
    buffer = Buffer(5, 1)
    buffer.print("Hello", 0, 0)
    assert buffer.at(0, 0).char == "H"
    assert buffer.at(1, 0).char == "e"
    assert buffer.at(4, 0).char == "o"

def test_print_oob():
    buffer = Buffer(1, 1)
    buffer.print("Hello", 0, 0)
    assert buffer.at(0, 0).char == "H"

def test_print_no_position():
    buffer = Buffer(2, 1)
    buffer.print("X")
    assert buffer.at(0, 0).char == "X"

def test_print_multiple_no_position():
    buffer = Buffer(3, 1)
    buffer.print("X")
    buffer.print("Y")
    assert buffer.at(0, 0).char == "X"
    assert buffer.at(1, 0).char == "Y"

def test_print_newline_origin():
    buffer = Buffer(2, 2)
    buffer.print("X\nY", 0, 0)
    assert buffer.at(0, 0).char == "X"
    assert buffer.at(0, 1).char == "Y"

def test_print_newline_position():
    buffer = Buffer(3, 3)
    buffer.print("X\nY", 1, 1)
    assert buffer.at(1, 1).char == "X"
    assert buffer.at(1, 2).char == "Y"

def test_print_fullwidth_spacing():
    buffer = Buffer(4, 1)
    buffer.print("你好", 0, 0)
    assert buffer.at(0, 0).char == "你"
    assert buffer.at(2, 0).char == "好"

def test_print_fullwidth_shadowing():
    buffer = Buffer(4, 1)
    buffer.clear(char="X")
    buffer.print("你好", 0, 0)
    assert buffer.at(0, 0).char == "你"
    assert buffer.at(1, 0).char == " "
    assert buffer.at(2, 0).char == "好"
    assert buffer.at(3, 0).char == " "
