from termpixels import App, Color
from unicodedata import category

COL_FG = Color.rgb(0.8, 0.8, 0.8)
COL_CTRL = Color.rgb(0.8, 0.0, 0.8)
COL_NUM = Color.rgb(0.8, 0.4, 0.0)
COL_PUNC = Color.rgb(0.0, 0.4, 0.8)
COL_SEP = Color.rgb(0.2, 0.0, 0.2)

def main():
    app = App(mouse=True)

    in_buffer = []

    @app.input.on("raw_input")
    def on_raw(data):
        in_buffer.append(data)

    def print_escape(line, x, y):
        app.screen.print_pos = (x, y)
        for ch in line:
            fg = COL_FG
            bg = None

            cat = category(ch)
            if "C" in cat:
                fg = COL_CTRL
            elif "N" in cat:
                fg = COL_NUM
            elif "P" in cat:
                fg = COL_PUNC
            elif "Z" in cat:
                bg = COL_SEP
            app.screen.print(repr(ch).lstrip("'").rstrip("'"), fg=fg, bg=bg)

    @app.on("frame")
    @app.on("resize")
    def update():
        max_lines = app.screen.h
        n_lines = min(max_lines, len(in_buffer))
        lines = in_buffer[-n_lines:]

        app.screen.clear()
        for i, line in enumerate(lines):
            print_escape(line, 0, i)

        app.screen.update()

    app.start()
    app.await_stop()

if __name__ == "__main__":
    main()
