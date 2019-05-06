import termpixels.color
from termpixels.color import Color
import pytest

def test_color_constructor_rgb():
    c = Color(1,2,3)
    assert c.r == 1
    assert c.g == 2
    assert c.b == 3

def test_color_constructor_packed():
    c = Color(0x010203)
    assert c.r == 1
    assert c.g == 2
    assert c.b == 3

def test_color_constructor_tuple():
    c = Color((0.1, 0.2, 0.3))
    assert c.r == round(0.1 * 255)
    assert c.g == round(0.2 * 255)
    assert c.b == round(0.3 * 255)

def test_color_constructor_copy():
    c = Color(Color(1,2,3))
    assert c.r == 1
    assert c.g == 2
    assert c.b == 3

def test_color_constructor_should_clip():
    c = Color(-10,300,10.6)
    assert c.r == 0
    assert c.g == 255
    assert c.b == 11

def test_color_eq():
    a = Color(99,88,77)
    b = Color(99,88,77)
    assert a == b

    c = Color(99,88,0)
    assert a != c
    assert b != c

def test_color_hash():
    # we assume no hash collisions since it should be trivial to create a
    # perfect hash of 3 8-bit integers
    a = Color(1,2,3)
    b = Color(1,2,3)
    assert hash(a) == hash(b)

    c = Color(1,2,4)
    assert hash(a) != hash(c)

    # hash should be computed after normalization
    d = Color(0,2,3)
    e = Color(-1,2,3)
    assert hash(d) == hash(e)

def test_color_add():
    a = Color(1,2,4)
    b = Color(8,16,32)
    assert a + b == Color(9,18,36)

    # can't use negative colors to subtract since they are clipped
    c = Color(10,10,10)
    d = Color(1,0,-1)
    assert c + d == Color(11,10,10)

    # adding a scalar should work
    assert a + 1.1 == Color(2,3,5)

def test_color_radd():
    a = Color(1,2,4)
    old = a
    a += Color(8,16,32)
    assert a == Color(9,18,36)

    # should preserve immutability
    assert old == Color(1,2,4)

    # support scalars
    b = Color(1,2,4)
    b += 1
    assert b == Color(2,3,5)

def test_color_sub():
    a = Color(9,18,36)
    b = Color(1,2,4)
    assert a - b == Color(8,16,32)

    assert a - 1.1 == Color(8,17,35)

def test_color_rsub():
    a = Color(9,18,36)
    old = a
    a -= Color(1,2,4)
    assert a == Color(8,16,32)

    # should preserve immutability
    assert old == Color(9,18,36)

    # support scalars
    b = Color(1,2,4)
    b -= 1
    assert b == Color(0,1,3)

def test_color_mul():
    a = Color(2,2,2)
    b = Color(1,3,5)
    assert a * b == Color(2,6,10)

    assert b * 3 == Color(3,9,15)

def test_color_rmul():
    a = Color(2,2,2)
    old = a
    a *= Color(1,3,5)
    assert a == Color(2,6,10)

    # should preserve immutability
    assert old == Color(2,2,2)

    # support scalars
    b = Color(1,3,5)
    b *= 2
    assert b == Color(2,6,10)

def test_color_pack():
    assert Color.pack(Color(1,2,3)) == 0x010203

def test_color_unpack():
    assert Color.unpack(0x010203) == Color(1,2,3)

def test_color_rgb_int():
    assert Color.rgb_int(1,2,3) == Color(1,2,3)

def test_color_rgb_int_cache():
    # this is tested as it is 
    a = Color.rgb_int(1,2,3)
    b = Color.rgb_int(1,2,3)
    c = Color.rgb_int(1,2,4)
    assert id(a) == id(b)
    assert id(a) != id(c)

def test_color_rgb():
    assert Color.rgb(0.1,0.2,0.3) == Color((0.1,0.2,0.3))

def test_color_hsl():
    assert Color.hsl(0.0,1.0,0.5) == Color(255,0,0)

def test_color_to_16():
    # just a rough test of color outputs
    assert termpixels.color.color_to_16(Color(0, 0, 0)) == 0
    assert termpixels.color.color_to_16(Color(100, 0, 0)) == 0o1
    assert termpixels.color.color_to_16(Color(0, 100, 0)) == 0o2
    assert termpixels.color.color_to_16(Color(0, 0, 100)) == 0o4
    assert termpixels.color.color_to_16(Color(255, 255, 255)) == 0o17

def test_color_to_256():
    # test B/W output
    # prefer usage of 16 and 231 for black and white since 0 and 15 are
    # user-defined
    assert termpixels.color.color_to_256(Color(0,0,0)) == 16
    assert termpixels.color.color_to_256(Color(255,255,255)) == 231 

    # test grayscale output
    assert termpixels.color.color_to_256(Color.rgb(0.2,0.2,0.2)) == 236 
    assert termpixels.color.color_to_256(Color.rgb(0.5,0.5,0.5)) == 244
    assert termpixels.color.color_to_256(Color.rgb(0.8,0.8,0.8)) == 252

    # test a couple RGB colors
    assert termpixels.color.color_to_256(Color(255,0,0)) == 196
    assert termpixels.color.color_to_256(Color(0,255,0)) == 46
    assert termpixels.color.color_to_256(Color(0,0,255)) == 21
    assert termpixels.color.color_to_256(Color(127,127,255)) == 105
