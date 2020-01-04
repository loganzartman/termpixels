from termpixels import App, Color

def main():
    app = App()

    @app.on("start")
    def on_start():
        app.screen.print("Resize the terminal.", 1, 1, fg=Color.rgb(0,1,0))
        app.screen.update()

    @app.on("resize")
    def on_resize():
        app.screen.clear()
        app.screen.fill(0, 0, app.screen.w, app.screen.h, bg=Color(0,255,0))
        app.screen.fill(1, 1, app.screen.w-2, app.screen.h-2, bg=Color(0,0,0))
        app.screen.print("{} x {}".format(app.screen.w, app.screen.h), 2, 2)
        app.screen.update()
    
    app.start()
    app.await_stop()

if __name__ == "__main__":
    main()
