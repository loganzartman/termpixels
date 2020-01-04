from termpixels import Color
from termpixels.detector import detect_backend
from time import sleep

def main():
    # example of manually controlling terminal
    b = detect_backend()
    b.enter_alt_buffer()
    b.cursor_pos = (0, 0)
    b.fg = Color.rgb(0, 1, 0)
    b.write("Hello world from {}\n".format(b.terminal_name))
    b.cursor_pos = (0, 0)
    b.fg = Color.rgb(1, 0, 0)
    b.write("Hello\n")
    cols, rows = b.size
    b.write("Screen size: {}x{} hello\n".format(cols, rows))
    b.flush()
    sleep(1)
    b.exit_alt_buffer()

if __name__ == "__main__":
    main()
