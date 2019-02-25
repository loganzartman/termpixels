from copy import copy
from termpixels.terminfo import Terminfo

class Key:
    def __init__(self, *, char=None, name=None):
        self.char = char
        self.name = name

    def __str__(self):
        if self.char:
            return self.char
        return ""
    
    def __repr__(self):
        param_names = ["char", "name"]
        params = ["{}=\"{}\"".format(name, getattr(self, name)) for name in param_names if getattr(self, name)]
        return "Key({})".format(", ".join(params))
    
    def __eq__(self, other):
        if type(other) == str:
            return self.name == other or self.char == other
        try:
            return self.char == other.char and self.name == other.name
        except AttributeError:
            return False

class Mouse:
    def __init__(self, x, y, pressed, *, moved=False, left=False, right=False, middle=False, scrollup=False, scrolldown=False):
        self.x = x
        self.y = y
        self.pressed = pressed and not moved
        self.moved = moved
        self.left = left
        self.right = right
        self.middle = middle
        self.scrollup = scrollup
        self.scrolldown = scrolldown
    
    def __repr__(self):
        param_names = ["x", "y", "pressed", "moved", "left", "right", "middle", "scrollup", "scrolldown"]
        params = ["{}={}".format(name, repr(getattr(self, name))) for name in param_names if getattr(self, name)]
        return "Mouse({})".format(", ".join(params))

class KeyParser:
    def __init__(self):
        self.pattern_key_pairs = {}

    def register_key(self, pattern, key):
        self.pattern_key_pairs[pattern] = key
    
    def parse(self, group):
        for pattern, key in self.pattern_key_pairs.items():
            if group.startswith(pattern):
                return copy(key)
        return None

class SgrMouseParser:
    def __init__(self, mouse_prefix):
        self.mouse_prefix = mouse_prefix
    
    def parse(self, group):
        if group.startswith(self.mouse_prefix):
            pressed = group[-1] == "M"
            parts = group[len(self.mouse_prefix):-1].split(";")
            button = int(parts[0])
            x = int(parts[1]) - 1
            y = int(parts[2]) - 1
            return Mouse(x, y, pressed, **SgrMouseParser.decodeButton(button))

    @staticmethod
    def decodeButton(btn):
        result = {
            "moved": False,
            "left": False,
            "right": False,
            "middle": False,
            "scrollup": False,
            "scrolldown": False
            }
        if btn & 0b100000:
            result["moved"] = True
        if btn & 0b1000000:
            if btn & 0b1:
                result["scrolldown"] = True
            else:
                result["scrollup"] = True
        else:
            if not btn & 0b1 and not btn & 0b10:
                result["left"] = True
            if btn & 0b10:
                result["right"] = True
            if btn & 0b1 and not btn & 0b10:
                result["middle"] = True
        return result

def make_key_parser(ti):
    parser = KeyParser()
    # special keys
    names = {
        "kbs": "backspace",
        "kcbt": "backtab",
        "khome": "home",
        "kend": "end",
        "kich1": "insert",
        "kdch1": "delete",
        "kpp": "pageup",
        "knp": "pagedown",
        "kcub1": "left",
        "kcuf1": "right",
        "kcuu1": "up",
        "kcud1": "down"
    }
    for code, name in names.items():
        seq = ti.parameterize(code)
        if seq:
            parser.register_key(seq.decode("ascii"), Key(name=name))
    
    # terminfo files seem to have bad backspace (kbs) values; just register both
    parser.register_key(chr(8), Key(name="backspace"))
    parser.register_key(chr(127), Key(name="backspace"))

    parser.register_key("\t", Key(name="tab", char="\t"))

    # function keys
    for i in range(1, 64):
        seq = ti.string("kf{}".format(i))
        if seq:
            parser.register_key(seq.decode("ascii"), Key(name="f{}".format(i)))
    
    # must be last
    parser.register_key("\x1b", Key(name="escape"))
    return parser

def make_mouse_parser(ti):
    return SgrMouseParser(ti.string("kmous").decode("ascii"))
