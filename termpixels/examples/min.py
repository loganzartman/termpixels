from termpixels.screen import Color
from termpixels.detector import detect_backend

# minimal example program that tests colors and printing
b = detect_backend()
b.cursor_pos = (0, 0)
b.fg = Color.rgb(0, 1, 0)
b.write("Hello world from {}\n".format(b.terminal_name))
b.cursor_pos = (0, 0)
b.fg = Color.rgb(1, 0, 0)
b.write("Hello\n")
cols, rows = b.size
b.write("Screen size: {}x{} hello\n".format(cols, rows))
b.flush()
