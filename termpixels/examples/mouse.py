from termpixels import App, Color

def main():
    app = App(mouse=True)

    @app.on("mouse")
    def on_mouse(mouse):
        app.screen.clear(bg=Color(0,0,0), fg=Color(255,255,255))
        draw_crosshair(app, mouse.x, mouse.y, fg=Color(127,127,0))
        app.screen.print(repr(mouse), 1, 1)
        app.screen.update()

    app.start()
    app.await_stop()
    
def draw_crosshair(app, x, y, **kwargs):
    for r in range(app.screen.h):
        app.screen.print("┃", x, r, **kwargs)
    for c in range(app.screen.w):
        app.screen.print("━", c, y, **kwargs)
    app.screen.print("╋", x, y, **kwargs)

if __name__ == "__main__":
    main()
