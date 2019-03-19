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
