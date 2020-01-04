import termpixels
from termpixels import App, Color

def main():
    app = App(mouse=True)

    @app.on("start")
    def on_start():
        app.mouse = None
        app.key = None
        app.dirty = False
        redraw(app)
    
    @app.on("resize")
    def on_resize():
        redraw(app)

    @app.on("key")
    def on_key(k):
        app.key = k
        app.dirty = True

    @app.on("mouse")
    def on_mouse(m):
        app.mouse = m
        app.dirty = True

    @app.on("frame")
    def on_frame():
        if app.dirty:
            redraw(app)
            app.dirty = False
    
    app.start()
    app.await_stop()

def redraw(app):
    white = Color.rgb(1,1,1)
    gray = Color.rgb(0.5,0.5,0.5)
    yellow = Color.rgb(1,1,0)

    app.screen.clear(bg=Color(0,0,0))
    app.screen.fill(1,1,app.screen.w-2,app.screen.h-2,bg=Color.rgb(0.2,0.2,0.2))

    app.screen.print("Termpixels version {}\n".format(termpixels.__version__), 2, 2, fg=white)

    app.screen.print("Detected terminal: ", x=2, fg=gray)
    app.screen.print(app.backend.terminal_name, fg=yellow)
    app.screen.print("\n")

    app.screen.print("Color support: ", x=2, fg=gray)
    app.screen.print(app.backend.color_mode, fg=yellow)
    app.screen.print("\n")

    steps = app.screen.w - 4
    for x in range(steps):
        app.screen.print(" ", x=x+2, bg=Color.hsl(x / steps, 1, 0.5))
    app.screen.print("\n")

    app.screen.print("Last keypress: ", x=2, fg=gray)
    app.screen.print(repr(app.key), fg=white)
    app.screen.print("\n")

    app.screen.print("Last render time: ", x=2, fg=gray)
    app.screen.print("{:.1f}ms".format(app.screen._update_duration * 1000), fg=white)
    app.screen.print("\n")

    if app.mouse:
        app.screen.print(" ", app.mouse.x, app.mouse.y, bg=white)
    app.screen.update()

if __name__ == "__main__":
    main()
