from copy import copy
from terminfo import Terminfo

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
        try:
            return self.char == other.char
        except AttributeError:
            return False

class KeyParser:
    def __init__(self):
        self.pattern_key_pairs = {}

    def register_key(self, pattern, key):
        self.pattern_key_pairs[pattern] = key
    
    def parse(self, group):
        for pattern, key in self.pattern_key_pairs.items():
            if group.startswith(pattern.decode("ascii")):
                return copy(key)
        return None

def make_key_parser(ti):
    parser = KeyParser()
    # special keys
    names = {
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
            parser.register_key(seq, Key(name=name))

    # function keys
    for i in range(1, 64):
        seq = ti.string("kf{}".format(i))
        if seq:
            parser.register_key(seq, Key(name="f{}".format(i)))
    return parser
