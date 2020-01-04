from time import sleep
from termpixels import App, Color

def main():
    app = App()

    @app.on("resize")
    @app.on("start")
    def on_resize():
        app.screen.clear()
        for x in range(app.screen.w):
            for y in range(app.screen.h):
                fx = x / app.screen.w
                fy = y / app.screen.h
                app.screen.print(" ", x, y, bg=Color.rgb(fx, fy, 0))
        app.screen.update()
    
    app.start()
    app.await_stop()

if __name__ == "__main__":
    main()
