from termpixels import App
from time import sleep

def main():
    app = App()

    @app.on("start")
    def on_start():
        app.screen.print("App start", 0, 0)
        app.screen.update()
        sleep(1)
    
    frame_num = 0

    @app.on("frame")
    def on_frame():
        nonlocal frame_num
        app.screen.print("Frame {}".format(frame_num), 0, 1)
        app.screen.update()
        frame_num += 1
    
    @app.on("before_stop")
    def on_before_stop():
        app.screen.print("Before stop", 0, 2)
        app.screen.update()
        raise Exception("Damn")
    
    @app.on("after_stop")
    def on_after_stop():
        app.screen.print("After stop", 0, 3)
        app.screen.update()
    
    app.start()
    app.await_stop()

if __name__ == "__main__":
    main()
