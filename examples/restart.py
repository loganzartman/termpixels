from termpixels import App

def main():
    app = App()
    run_count = 0

    @app.on("start")
    def start():
        nonlocal run_count
        run_count += 1
        app.screen.print("Run {}".format(run_count), 0, 0)
        app.screen.print("Press any key to restart...", 0, 1)
        app.screen.update()
    
    @app.on("key")
    def key(k):
        app.stop()

    app.run()
    app.run()
    app.run()

if __name__ == "__main__":
    main()
