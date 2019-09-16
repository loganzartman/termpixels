from termpixels import App

def main():
    app = App()

    @app.on("frame")
    def on_frame():
        app.screen.print("Goodbye", 0, 0)        # this should be overwritten completely
        app.screen.print("こんにちは世界", 0, 0) # double-width characters
        app.screen.print(" (Hello World)")       # this should follow the previous printout
        app.screen.update()
    
    app.start()
    app.await_stop()

if __name__ == "__main__":
    main()

