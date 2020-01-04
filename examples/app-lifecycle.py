from termpixels import App
from time import sleep

def main():
    app = App(mouse=True)
    frame_num = 0
    size_text = ""

    @app.on("start")
    def start():
        app.screen.show_cursor = True
        app.screen.print("App start, waiting 1 second.", 0, 0)
        app.screen.update()
        sleep(1)
    
    @app.on("frame")
    def frame():
        nonlocal frame_num
        app.screen.clear()
        app.screen.print(f"Frame: {frame_num}", 0, 0)
        app.screen.print("Press 'q' to quit.", 0, 1)
        app.screen.print(size_text, 0, 2)
        app.screen.update()
        frame_num += 1

    @app.on("resize")
    def resize():
        nonlocal size_text
        size_text = f"Resized to {app.screen.w}x{app.screen.h}"

    @app.on("key")
    def key(k):
        if k == "q":
            app.stop()
    
    @app.on("mouse")
    def mouse(m):
        app.screen.cursor_pos = (m.x, m.y)
    
    @app.on("before_stop")
    def before_stop():
        # Terminal is not reset; we can use the screen.
        app.screen.clear()
        app.screen.print("Before stop", 0, 0)
        app.screen.update()
        sleep(0.5)
    
    @app.on("after_stop")
    def after_stop():
        # Terminal is reset; we can print normally.
        print("After stop")
    
    # the following two method calls are equivalent to calling app.run()
    app.start() # this does not block
    # you could run code concurrently with the App here, but you should not
    # interact with its attributes outside of event listeners due to potential
    # concurrency issues.
    app.await_stop() # this blocks
    print("Exited")

if __name__ == "__main__":
    main()
