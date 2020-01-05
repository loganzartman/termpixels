from termpixels import App

def main():
    app = App()
    
    messages = [
        "Press q to exit.",
        "Nice try, press q again.",
        "One last time."
    ]
    run_number = 0

    @app.on("start")
    @app.on("resize")
    def start():
        app.screen.clear()
        app.screen.print(messages[run_number], 0, 0)
        app.screen.update()

    @app.on("key")
    def key(k):
        nonlocal run_number
        if k == "q":
            run_number += 1
            app.stop()

    app.run()
    app.run()
    app.run()

if __name__ == "__main__":
    main()
