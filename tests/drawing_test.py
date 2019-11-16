import pytest
from termpixels.buffer import Buffer
from termpixels.drawing import draw_hline
from termpixels.drawing import draw_vline
from termpixels.drawing import draw_box
from termpixels.drawing import draw_spinner
from tests.utils import assert_buffer_matches

_BOX_CHARS_TEST = "tblrABCD"

def test_drawing_draw_hline():
    buffer = Buffer(3, 3)
    draw_hline(buffer, 1, char="X")
    assert_buffer_matches(
        buffer, 
        "   ",
        "XXX",
        "   ",
    )

def test_drawing_draw_vline():
    buffer = Buffer(3, 3)
    draw_vline(buffer, 1, char="X")
    assert_buffer_matches(
        buffer,
        " X ",
        " X ",
        " X "
    )

def test_drawing_draw_box():
    buffer = Buffer(5, 5)
    draw_box(buffer, 1, 1, 3, 3, chars=_BOX_CHARS_TEST)
    assert_buffer_matches(
        buffer,
        "     ",
        " AtB ",
        " l r ",
        " CbD ",
        "     "
    )

def test_drawing_draw_box_one_wide():
    buffer = Buffer(3, 5)
    draw_box(buffer, 1, 1, 1, 3, chars=_BOX_CHARS_TEST)
    assert_buffer_matches(
        buffer,
        "   ",
        " l ",
        " l ",
        " l ",
        "   "
    )

def test_drawing_draw_box_one_tall():
    buffer = Buffer(5, 3)
    draw_box(buffer, 1, 1, 3, 1, chars=_BOX_CHARS_TEST)
    assert_buffer_matches(
        buffer,
        "     ",
        " ttt ",
        "     "
    )

def test_drawing_draw_box_negative_dim():
    buffer = Buffer(3, 3)
    draw_box(buffer, 1, 1, -1, 1, chars=_BOX_CHARS_TEST)
    assert_buffer_matches(
        buffer,
        "   ",
        "   ",
        "   "
    )

def test_drawing_draw_spinner():
    buffer = Buffer(1, 1)

    draw_spinner(buffer, 0, 0, t=0, freq=1/4, frames="0123")
    assert buffer.at(0, 0).char == "0"

    draw_spinner(buffer, 0, 0, t=1, freq=1/4, frames="0123")
    assert buffer.at(0, 0).char == "1"

    draw_spinner(buffer, 0, 0, t=5, freq=1/4, frames="0123")
    assert buffer.at(0, 0).char == "1"

    draw_spinner(buffer, 0, 0, t=7, freq=1/4, frames="0123")
    assert buffer.at(0, 0).char == "3"
