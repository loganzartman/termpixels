from termpixels import App, Color
from time import time
from math import sin

def main():
    app = App()

    @app.on("frame")                                 # run this function every frame
    def on_frame():
        app.screen.clear()                           # remove everything from the screen
        text = "Hello world, from termpixels!"
        
        for i, c in enumerate(text):
            f = i / len(text)
            color = Color.hsl(f + time(), 1, 0.5)    # create a color from a hue value
            x = app.screen.w // 2 - len(text) // 2   # horizontally center the text
            offset = sin(time() * 3 + f * 5) * 2     # some arbitrary math
            y = round(app.screen.h / 2 + offset)     # vertical center with an offset
            app.screen.print(c, x + i, y, fg=color)  # draw the text to the screen buffer
        
        app.screen.update()                          # commit the changes to the screen
    
    app.start()                                      # returns immediately; feel free to do other work 
    app.await_stop()                                 # block here until the app exits (e.g. CTRL+C)

if __name__ == "__main__":
    main()
