from termpixels import App, Color
from time import time
from math import sin

class FunTextApp(App):
    def __init__(self):
        super().__init__()
    
    def on_frame(self):
        self.screen.clear()                           # remove everything from the screen
        text = "Hello world, from termpixels!"
        
        for i, c in enumerate(text):
            f = i / len(text)
            color = Color.hsl(f + time(), 1, 0.5)     # create a color from a hue value
            x = self.screen.w // 2 - len(text) // 2   # horizontally center the text
            offset = sin(time() * 3 + f * 5) * 2      # some arbitrary math
            y = round(self.screen.h / 2 + offset)     # vertical center with an offset
            self.screen.print(c, x + i, y, fg=color)  # draw the text to the screen buffer
        
        self.screen.update()                          # commit the changes to the screen

if __name__ == "__main__":
    FunTextApp().start()
