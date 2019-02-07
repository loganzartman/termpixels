class UnixBackend:
    def __init__(self):
        self._cursor_pos = None
        self._fg = None
        self._bg = None
        self._show_cursor = None 
        self.clear_screen()
    
    @property
    def cursor_pos(self):
        return self._cursor_pos
    
    @cursor_pos.setter
    def cursor_pos(self, pos):
        if self._cursor_pos != pos:
            self.write_escape("[{row};{col}H".format(row=pos[1]+1, col=pos[0]+1)) 
            self._cursor_pos = pos

    @property
    def show_cursor(self):
        return self._show_cursor
    
    @show_cursor.setter
    def show_cursor(self, show_cursor):
        if self._show_cursor != show_cursor:
            self.write_escape("[?25" + "h" if show_cursor else "l")
            self._show_cursor = show_cursor
    
    @property
    def fg(self):
        return self._fg
    
    @fg.setter
    def fg(self, color):
        if self._fg != color:
            self.write_escape("[38;2;{r};{g};{b}m".format(r=color.r, g=color.g, b=color.b))
            self._fg = color
    
    @property
    def bg(self):
        return self._bg
    
    @bg.setter
    def bg(self, color):
        if self._bg != color:
            self.write_escape("[48;2;{r};{g};{b}m".format(r=color.r, g=color.g, b=color.b))
            self._bg = color

    def clear_screen(self):
        self.cursor_pos = (0, 0)
        self.write("\x1b[2J")
    
    def write_escape(self, code):
        print("\x1b{}".format(code), end="")

    def write(self, text):
        print(text, end="")
        self._cursor_pos = (self._cursor_pos[0] + len(text), self._cursor_pos[1])

    def flush(self):
        print("", end="", flush=True)
