from time import sleep
from termpixels.color import Color
from termpixels.app import App

class ColorTest(App):
    def __init__(self):
        super().__init__()
    
    def on_frame(self):
        self.screen.clear()
        for x in range(self.screen.w):
            for y in range(self.screen.h):
                fx = x / self.screen.w
                fy = y / self.screen.h
                self.screen.print(" ", x, y, bg=Color.rgb(fx, fy, 0))
        self.screen.update()

ColorTest().start()
