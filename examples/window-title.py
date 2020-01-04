from termpixels import App, Color
import time

def main():
    app = App()

    @app.on("frame")
    def on_frame():
        clock_time = time.strftime("%H:%M:%S", time.gmtime())
        app.screen.print("Clock: " + clock_time, 1, 1)
        try:
            app.backend.window_title = clock_time
        except:
            app.screen.print("Terminal does not support setting window title", 1, 2, fg=Color.rgb(1,0,0))
        app.screen.update()
    
    app.start()
    app.await_stop()

if __name__ == "__main__":
    main()
