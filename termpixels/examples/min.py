from termpixels.screen import Color
from termpixels.detector import detect_backend

# minimal example program that tests colors and printing
b = detect_backend()
b.fg = Color.rgb(1, 1, 1)
b.bg = Color.rgb(0, 0.5, 0)
b.write("Hello world.\n")
b.flush()
