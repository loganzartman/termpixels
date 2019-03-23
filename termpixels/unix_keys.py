import re
from copy import copy
from termpixels.terminfo import Terminfo
from termpixels.keys import Key, Mouse

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
        action = None
        button = None

        # detect action
        if btn & MASK_MOVED:
            action = "moved"
        elif pressed:
            action = "down"
        else:
            action = "up"

        # detect button
        if btn & MASK_WHEEL:
            if btn & MASK_BUTTON == 0:
                button = "scrollup"
            else:
                button = "scrolldown"
        else:
            code = btn & MASK_BUTTON
            if code == 0:
                button = "left"
            elif code == 1:
                button = "middle"
            elif code == 2:
                button = "right"
        return {"action": action, "button": button}

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
    parser.register_key(chr(8), Key(name="backspace", char="\b"))
    parser.register_key(chr(127), Key(name="backspace", char="\b"))

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
