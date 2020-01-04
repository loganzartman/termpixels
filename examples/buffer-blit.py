from termpixels import App, Color, Buffer
from math import sin, cos
from time import time

def main():
    app = App(framerate=60)

    @app.on("start")
    def on_start():
        app.buffer = Buffer(16,4)
        app.buffer.clear(bg=Color.rgb(0.2,0,0), fg=Color.rgb(1,0.5,0.5))
        app.buffer.print("Hello world")

    @app.on("frame")
    def on_frame():
        t = time()
        app.screen.clear()
        app.screen.blit(
            app.buffer, 
            round(app.screen.w / 2 + sin(t * 3) * 16) - app.buffer.w // 2,
            round(app.screen.h / 2 + cos(t * 1) * 4) - app.buffer.h // 2
        )
        app.screen.print("Update time: {:.2f}ms".format(app.screen._update_duration*1000), 0, 0)
        app.screen.update()

    app.start()
    app.await_stop()        

if __name__ == "__main__":
    main()
