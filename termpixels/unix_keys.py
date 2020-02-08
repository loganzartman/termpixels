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

class SgrMouseParser: 
    # https://invisible-island.net/xterm/ctlseqs/ctlseqs.html#h3-Extended-coordinates   
    def __init__(self, mouse_prefix):
        self.regex = re.compile(r"\x1b\[(?:\<|M)(\d+);(\d+);(\d+)(m|M)")
    
    def parse(self, group):
        match = self.regex.match(group)
        if match is None:
            return []
        
        pressed = match.group(4) == "M"
        button = int(match.group(1))
        x = int(match.group(2)) - 1
        y = int(match.group(3)) - 1
        mouse = Mouse(x, y, **SgrMouseParser.decode_button(button, pressed))
        return [(match.group(0), mouse)]

    @staticmethod
    def decode_button(btn, pressed):
        MASK_MOVED = 0b100000
        MASK_BUTTON = 0b11
        MASK_WHEEL = 0b1000000

        action = None

        # detect action
        if btn & MASK_MOVED:
            action = "moved"
        elif pressed:
            action = "down"
        else:
            action = "up"

        # detect button
        left = False
        middle = False
        right = False
        scroll = 0
        if btn & MASK_WHEEL:
            if btn & MASK_BUTTON == 0:
                scroll = -1
            else:
                scroll = 1
        else:
            code = btn & MASK_BUTTON
            if code == 0:
                left = True
            elif code == 1:
                middle = True
            elif code == 2:
                right = True
        
        return {
            "action": action, 
            "left": left, 
            "middle": middle, 
            "right": right, 
            "scroll": scroll
        }

class X10MouseParser:
    # https://invisible-island.net/xterm/ctlseqs/ctlseqs.html#h2-Mouse-Tracking 
    def __init__(self):
        self.regex = re.compile(r"\x1b\[M(.)(.)(.)")
    
    def parse(self, group):
        match = self.regex.match(group)
        if match is None:
            return []

        event = ord(match.group(1)) - 32
        x = ord(match.group(2)) - 32 - 1
        y = ord(match.group(3)) - 32 - 1
        mouse = Mouse(x, y, **X10MouseParser.decode_event(event))
        return [(match.group(0), mouse)]
    
    @staticmethod
    def decode_event(event_code):
        """ decode an xterm mouse event character not shifted by 32 """
        button_code = event_code & 0b11
        action = "moved"
        left = False
        middle = False
        right = False
        scroll = 0
        if event_code & 0b1000000:
            # wheel event 
            if not event_code & 0b0100000:
                # based on testing in rxvt, we sometimes incorrectly see wheel
                # data repeated in mouse motion events, but with the 32 bit set.

                if button_code == 0:
                    scroll = -1
                elif button_code == 1:
                    scroll = 1
        else:
            # button event
            if button_code == 0:
                left = True
                action = "down"
            elif button_code == 1:
                middle = True
                action = "down"
            elif button_code == 2:
                right = True
                action = "down"
            else:
                # button up is ambiguous in X10 mouse encoding
                left = True
                middle = True
                right = True
                action = "up"
        
        mod_code = (event_code >> 2) & 0b111
        # TODO: implement modifiers
        if mod_code & 0b001:
            pass # shift
        if mod_code & 0b010:
            pass # meta
        if mod_code & 0b100:
            pass # control

        return {
            "action": action,
            "left": left, 
            "middle": middle, 
            "right": right,
            "scroll": scroll 
        }
        

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

def make_parsers(ti):
    return (
        make_key_parser(ti),
        X10MouseParser(),
        SgrMouseParser(ti.string("kmous").decode("ascii"))
    )
