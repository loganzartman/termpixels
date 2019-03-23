from termpixels import App, Color

class MouseTestApp(App):
    def __init__(self):
        super().__init__(mouse=True)
    
    def on_mouse(self, mouse):
        self.screen.clear(bg=Color(0,0,0), fg=Color(255,255,255))
        self.draw_crosshair(mouse.x, mouse.y, fg=Color(127,127,0))
        self.screen.print(repr(mouse), 1, 1)
        self.screen.update()
    
    def draw_crosshair(self, x, y, **kwargs):
        for r in range(self.screen.h):
            self.screen.print("┃", x, r, **kwargs)
        for c in range(self.screen.w):
            self.screen.print("━", c, y, **kwargs)
        self.screen.print("╋", x, y, **kwargs)

MouseTestApp().start()
