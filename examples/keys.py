from termpixels import App

def main():
    app = App()
    
    @app.on("key")
    def on_key(k):
        app.screen.clear()
        app.screen.print(repr(k), 1, 1)
        app.screen.update()
    
    app.start()
    app.await_stop()

if __name__ == "__main__":
    main()
