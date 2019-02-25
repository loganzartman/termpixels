from termpixels.app import App
from termpixels.screen import Color

class TestApp(App):
    def __init__(self):
        super().__init__()
    
    def on_resize(self):
        self.screen.fill(0, 0, self.screen.w, self.screen.h, bg=Color(0,255,0))
        self.screen.fill(1, 1, self.screen.w-2, self.screen.h-2, bg=Color(0,0,0))
        self.screen.print("{} x {}".format(self.screen.w, self.screen.h), 2, 2)
        self.screen.update()

TestApp().start()
