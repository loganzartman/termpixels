from termpixels.app import App
from termpixels.color import Color
import time

class TestWindowTitleApp(App):
    def __init__(self):
        super().__init__()
    
    def on_frame(self):
        clock_time = time.strftime("%H:%M:%S", time.gmtime())
        self.screen.print("Clock: " + clock_time, 1, 1)
        self.backend.window_title = clock_time
        self.screen.update()

TestWindowTitleApp().start()