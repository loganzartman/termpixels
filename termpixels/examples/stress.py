from termpixels import App, Color, PixelData
from random import choice

def main():
    app = App(framerate=60)

    colors = [Color.rgb(r,g,b) for r in (0, 1) for g in (0, 1) for b in (0, 1)]
    pixels = [PixelData(char="▄", fg=col1, bg=col2) for col1 in colors for col2 in colors]

    @app.on("frame")
    def on_frame():
        for x in range(app.screen.w):
            for y in range(app.screen.h):
                app.screen[x,y].set(choice(pixels))
        app.screen.update()
    
    app.start()
    app.await_stop()

if __name__ == "__main__":
    main()
