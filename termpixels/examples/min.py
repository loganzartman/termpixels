from termpixels.screen import Color
from termpixels.detector import detect_backend

# minimal example program that tests colors and printing
b = detect_backend()
b.fg = Color.rgb(0, 1, 0)
b.write("Hello world from {}\n".format(b.terminal_name))
b.flush()
