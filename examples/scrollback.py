from datetime import datetime
from time import time
from termpixels import App, Color, SparseBuffer
from termpixels.util import splitlines_print

a = App()
b = SparseBuffer(0, 0)
b.extend_to(10, 10)

scroll_y = 0
autoscroll = False

def log(s):
    global scroll_y
    for line in splitlines_print(s):
        b.print(line, fg=Color.hsl(time() * 0.2, 0.5, 0.4))
        b.print_pos = (0, b.print_pos[1] + 1)
        b.extend_to(0, b.print_pos[1] + 1)
    if autoscroll:
        scroll_y = b.print_pos[1] - a.screen.h

@a.on("start")
@a.on("resize")
def resize():
    b.resize(a.screen.w, b.h)
    log("Use up/down arrow keys to scroll!")

@a.on("key")
def key(k):
    global autoscroll, scroll_y
    if k == "up":
        scroll_y -= 1
    if k == "down":
        scroll_y += 1
    if k == "a":
        autoscroll = not autoscroll

a.create_interval("print line", 0.5).start()
@a.on("print line")
def print_line():
    log(f"[{datetime.now().time()}] Hi! Autoscroll: {autoscroll} (A to toggle)")

@a.on("frame")
def frame():
    a.screen.clear()
    a.screen.blit(b, 0, -scroll_y)
    a.screen.cursor_pos = (b.print_pos[0], b.print_pos[1] - scroll_y)
    a.screen.show_cursor = True
    a.screen.update()

if __name__ == "__main__":
    a.run()
