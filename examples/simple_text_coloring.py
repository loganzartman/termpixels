from termpixels import App, Color

if __name__ == "__main__":
    # it's possible to not "start" an App and just use its terminal backend.
    term = App().backend
    term.fg = Color.rgb(1,0,1)
    term.write("Hello world\n")
    term.flush()

    term.fg = Color.rgb(1,1,0)
    term.flush()
    print("print() works too; just flush first.")
