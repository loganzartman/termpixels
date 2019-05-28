from termpixels import App, Color, Buffer
from math import sin, cos
from time import time

class BufferBlitApp(App):
    def __init__(self):
        super().__init__(framerate=60)

    def on_start(self):
        self.buffer = Buffer(16,4)
        self.buffer.clear(bg=Color.rgb(1,0,0))
        self.buffer.print("Hello world")

    def on_frame(self):
        t = time()
        self.screen.clear()
        self.screen.blit(
            self.buffer, 
            round(self.screen.w / 2 + sin(t * 7) * 16),
            round(self.screen.h / 2 + cos(t * 4) * 4)
        )
        self.screen.print("Update time: {:.2f}ms".format(self.screen._update_duration*1000), 0, 0)
        self.screen.update()

if __name__ == "__main__":
    BufferBlitApp().start()
