import termpixels
from termpixels.app import App
from termpixels.color import Color
import os

class DemoApp(App):
    def __init__(self):
        super().__init__(mouse=True)
    
    def on_start(self):
        self.mouse = None
        self.key = None
        self.dirty = False
        self.redraw()

    def redraw(self):
        white = Color.rgb(1,1,1)
        gray = Color.rgb(0.5,0.5,0.5)
        yellow = Color.rgb(1,1,0)

        self.screen.clear(bg=Color(0,0,0))
        self.screen.fill(1,1,self.screen.w-2,self.screen.h-2,bg=Color.rgb(0.2,0.2,0.2))

        y = 2
        self.screen.print("Termpixels version {}".format(termpixels.__version__), 2, y, fg=white)
        y += 1

        x, _ = self.screen.print("Detected terminal: ", 2, y, fg=gray)
        self.screen.print(self.backend.terminal_name, x, y, fg=yellow)
        y += 1

        x, _ = self.screen.print("Color support: ", 2, y, fg=gray)
        self.screen.print(self.backend.color_mode, x, y, fg=yellow)
        y += 1

        steps = self.screen.w - 4
        for x in range(steps):
            self.screen.print(" ", x + 2, y, bg=Color.hsl(x / steps, 1, 0.5))
        y += 1

        y += 1
        x, _ = self.screen.print("Last keypress: ", 2, y, fg=gray)
        self.screen.print(repr(self.key), x, y, fg=white)
        y += 1

        x, _ = self.screen.print("Last render time: ", 2, y, fg=gray)
        self.screen.print("{0:.3f}s".format(self.screen._update_duration), x, y, fg=white)
        y += 1

        if self.mouse:
            self.screen.print(" ", self.mouse.x, self.mouse.y, bg=white)
        self.screen.update()
    
    def on_resize(self):
        self.redraw()

    def on_key(self, k):
        self.key = k
        self.dirty = True

    def on_mouse(self, m):
        self.mouse = m
        self.dirty = True

    def on_frame(self):
        if self.dirty:
            self.redraw()
            self.dirty = False

DemoApp().start()

