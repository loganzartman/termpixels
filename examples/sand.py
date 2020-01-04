from termpixels import App, Color
from random import random
from time import perf_counter

helptext = """Use mouse or arrow keys to move cursor.
Use left/right click or Z/X to add/remove sand."""

props = {
    "air": {
        "color": Color.rgb(0,0,0),
        "falling": False,
        "density": 1,
        "sliding": False
    },
    "sand": {
        "falling": True,
        "density": 2,
        "sliding": True
    }
}

class P:
    def __init__(self, *, color, falling, density, sliding):
        self.color = color
        self.falling = falling
        self.density = density
        self.sliding = sliding

    @staticmethod
    def update(buf, w, h):
        """
        This is a relatively simple and messy "falling sand" algorithm.
        Some things to note are:
        - it implements falling and "sliding" (so that sand forms triangular piles)
        - the order of iteration (bottom to top, back and forth) is VERY important
          - would not do a good job for upward-moving particles or particles 
            that move more than one vertical pixel at a time
        """
        for y in range(h-1,-1,-1):
            X = range(w) if y % 2 == 0 else range(w-1,-1,-1)
            for x in X:
                p = y*w+x
                if buf[p].falling:
                    if y < h - 1:
                        o = (y+1)*w+x
                        if buf[p].density > buf[o].density:
                            buf[p], buf[o] = buf[o], buf[p]
                    if buf[p].sliding:
                        if y < h - 1:
                            l = (y+1)*w+x-1
                            r = (y+1)*w+x+1
                            lp = None
                            rp = None
                            if x > 0:
                                if buf[l].density < buf[p].density:
                                    lp = buf[l]
                            if x < w-1:
                                if buf[r].density < buf[p].density:
                                    rp = buf[r]
                            if lp and rp:
                                if random() < 0.5:
                                    buf[l], buf[p] = buf[p], buf[l]
                                else:
                                    buf[r], buf[p] = buf[p], buf[r]
                            elif lp:
                                buf[l], buf[p] = buf[p], buf[l]
                            elif rp:
                                buf[r], buf[p] = buf[p], buf[r]
                        

    @staticmethod
    def draw(screen, buf, w, h):
        for x in range(w):
            for y in range(h):
                if y % 2 == 0:
                    screen[x, y // 2].bg = buf[y*w+x].color
                else:
                    screen[x, y // 2].fg = buf[y*w+x].color
                    screen[x, y // 2].char = "▄"

def main():
    app = App(mouse=True, framerate=60)
    app.screen.show_cursor = True

    w = 0
    h = 0
    buf = None
    c_x = 0
    c_y = 0
    show_help = True

    @app.on("start")
    @app.on("resize")
    def make_buffers():
        nonlocal w, h, buf
        w = app.screen.w
        h = app.screen.h * 2
        buf = [P(**props["air"]) for y in range(w) for x in range(h)]
    
    @app.on("frame")
    def on_frame():
        app.screen.clear()
        app.screen.cursor_pos = (c_x, c_y)
        P.update(buf, w, h)
        P.draw(app.screen, buf, w, h)
        if show_help:
            app.screen.print(helptext, 1, 1, fg=Color.rgb(1,1,1))
        app.screen.update()

    def interact(place):
        nonlocal show_help
        show_help = False

        x = c_x
        y = c_y * 2
        if x >= 0 and x < w and y >= 0 and y < h:
            if place:
                buf[y*w+x] = P(color=Color.hsl(perf_counter() * 0.25, 1, 0.5), **props["sand"])
            else:
                buf[y*w+x] = P(**props["air"])

    @app.on("mouse")
    def on_mouse(m):
        nonlocal c_x, c_y

        c_x = m.x
        c_y = m.y

        if m.left:
            interact(True)
        if m.right:
            interact(False)

    @app.on("key")
    def on_key(k):
        nonlocal c_x, c_y

        if k == "left":
            c_x = max(0, c_x - 1)
        if k == "right":
            c_x = min(w-1, c_x + 1)
        if k == "up":
            c_y = max(0, c_y - 1)
        if k == "down":
            c_y = min(w-1, c_y + 1)
        if k == "z":
            interact(True)
        if k == "x":
            interact(False)

    app.start()
    app.await_stop()

if __name__ == "__main__":
    main()
