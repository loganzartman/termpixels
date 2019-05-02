import sys
from termpixels import App, Color
from time import perf_counter

AQUA = Color.rgb(0,1,1)

class Bench2(App):
    def __init__(self):
        super().__init__(framerate=float("inf"))

    def on_start(self):
        self.t0 = perf_counter()
        self.frames = 0
        self.pos = 0

    def on_frame(self):
        self.pos = (self.pos + 1) % (self.screen.w * self.screen.h)
        x = self.pos % self.screen.w
        y = self.pos // self.screen.w
        self.screen.clear()
        self.screen.print(" " * 5, x, y, bg=AQUA)
        self.screen.update()
        self.frames += 1
        self.t1 = perf_counter()

    def on_stop(self):
        tpf = (self.t1 - self.t0) / self.frames
        with open("result.txt", "w") as f:
            f.write("Terminal: {} ({}x{})\n".format(self.backend.terminal_name, self.screen.w, self.screen.h))
            f.write("Avg time per frame: {:.4f}\n".format(tpf))
            f.write("Avg framerate: {:.2f}\n".format(1/tpf))

if __name__ == "__main__":
    Bench2().start()
