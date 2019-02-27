import re
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
    def __init__(self, x, y, *, down=False, moved=False, up=False, left=False, right=False, middle=False, scrollup=False, scrolldown=False):
        self.x = x
        self.y = y
        self.down = down
        self.moved = moved
        self.up = up
        self.left = left
        self.right = right
        self.middle = middle
        self.scrollup = scrollup
        self.scrolldown = scrolldown
    
    def __repr__(self):
        param_names = ["x", "y", "down", "moved", "up", "left", "right", "middle", "scrollup", "scrolldown"]
        params = ["{}={}".format(name, repr(getattr(self, name))) for name in param_names if getattr(self, name)]
        return "Mouse({})".format(", ".join(params))

class KeyParser:
    def __init__(self):
        self.pattern_key_pairs = {}

    def register_key(self, pattern, key):
        self.pattern_key_pairs[pattern] = key
    
    def parse(self, group):
        matches = []
        for pattern, key in self.pattern_key_pairs.items():
            if group.startswith(pattern):
                matches.append((pattern, copy(key)))
        return matches

MASK_MOVED = 0b100000
MASK_BUTTON = 0b11
MASK_WHEEL = 0b1000000
class SgrMouseParser:    
    def __init__(self, mouse_prefix):
        self.regex = re.compile(r"\x1b\[(?:\<|M)(.+);(.+);(.+)(m|M)")
    
    def parse(self, group):
        match = self.regex.match(group)
        if match is None:
            return []
        
        pressed = match.group(4) == "M"
        button = int(match.group(1))
        x = int(match.group(2)) - 1
        y = int(match.group(3)) - 1
        mouse = Mouse(x, y, **SgrMouseParser.decodeButton(button, pressed))
        return [(match.group(0), mouse)]

    @staticmethod
    def decodeButton(btn, pressed):
        result = {
            "moved": False,
            "left": False,
            "right": False,
            "middle": False,
            "scrollup": False,
            "scrolldown": False,
            "down": False,
            "up": False
            }
        # detect action
        if btn & MASK_MOVED:
            result["moved"] = True
        elif pressed:
            result["down"] = True
        else:
            result["up"] = True

        # detect button
        if btn & MASK_WHEEL:
            if btn & MASK_BUTTON == 0:
                result["scrollup"] = True
            else:
                result["scrolldown"] = True
        else:
            button = btn & MASK_BUTTON
            if button == 0:
                result["left"] = True
            elif button == 1:
                result["middle"] = True
            elif button == 2:
                result["right"] = True
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
