class Key:
    r"""Represents a key press event.

    A key can have a printable "char" or a made-up "name", or both. As an 
    example, the "A" key has char="a", or char="A" if it is typed in uppercase.
    The left arrow key, which does not have a corresponding Unicode character,
    has name="left" but no value for char.

    The __eq__ implementation for Key will check for equality with either char
    or name if you test a Key instance against a string.

    The termpixels names for special keys are as follows:
        backtab - Unix only for now; shift+tab
        backspace - also has char="\b"
        escape
        tab - also has char="\t"
        
        delete
        end
        home
        insert
        pageup - page up (AKA VK_PRIOR)
        pagedown - page down (AKA VK_NEXT)

        f1 - includes f1 through f64 (wow!), the function keys

        down - down arrow key
        left - left arrow key
        right - right arrow key
        up - up arrow key
    
    Termpixels does not yet support modifiers.
    """
    def __init__(self, *, char=None, name=None):
        self.char = char
        self.name = name

    def __str__(self):
        if self.char:
            return self.char
        return ""
    
    def __repr__(self):
        param_names = ["char", "name"]
        params = ["{}={}".format(name, repr(getattr(self, name))) for name in param_names if getattr(self, name)]
        return "Key({})".format(", ".join(params))
    
    def __eq__(self, other):
        if type(other) == str:
            return self.name == other or self.char == other
        try:
            return self.char == other.char and self.name == other.name
        except AttributeError:
            return False

class Mouse:
    """Represents a mouse event.

    There are several kinds of mouse events. All of them have an associated
    position, indicated by the `x` and `y` properties. 
    
    Each event has an `action`, which can be either "moved", "down", or "up". 
    
    If the action is "down" or "up", or if the mouse is being dragged during a 
    "moved", then a `button` will be indicated by name. The possible `button` 
    values are "left", "middle", "right", "scrollup", and "scrolldown".
    """
    def __init__(self, x, y, *, button=None, action=None):
        self.x = x
        self.y = y
        self.button = button
        self.action = action
        self.down = action == "down"
        self.moved = action == "moved"
        self.up = action == "up"
        self.left = button == "left"
        self.right = button == "right"
        self.middle = button == "middle"
        self.scrollup = button == "scrollup"
        self.scrolldown = button == "scrolldown"
    
    def __repr__(self):
        param_names = ["x", "y", "button", "action"]
        params = ["{}={}".format(name, repr(getattr(self, name))) for name in param_names if getattr(self, name)]
        return "Mouse({})".format(", ".join(params))
