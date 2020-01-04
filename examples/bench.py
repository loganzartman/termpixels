import sys
from termpixels import App, Color
from time import perf_counter

AQUA = Color.rgb(0,1,1)

def main():
    app = App(framerate=float("inf"))
    app.t0 = perf_counter()
    app.frames = 0
    app.pos = 0

    @app.on("frame")
    def on_frame():
        app.pos = (app.pos + 1) % (app.screen.w * app.screen.h)
        x = app.pos % app.screen.w
        y = app.pos // app.screen.w
        app.screen.clear()
        app.screen.print(" " * 5, x, y, bg=AQUA)
        app.screen.update()
        app.frames += 1
        app.t1 = perf_counter()

    @app.on("after_stop")
    def on_after_stop():
        tpf = (app.t1 - app.t0) / app.frames
        print("Terminal: {} ({}x{})\n".format(app.backend.terminal_name, app.screen.w, app.screen.h))
        print("Avg time per frame: {:.4f}\n".format(tpf))
        print("Avg framerate: {:.2f}\n".format(1/tpf))

    app.start()
    app.await_stop()

if __name__ == "__main__":
    main()
