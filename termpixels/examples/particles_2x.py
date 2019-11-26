import random
import math
from termpixels import App, Color
from termpixels.drawing import draw_colormap_2x

RED = Color.rgb(0.25,0.1,0.05)

class Particle:
    def __init__(self, x, y, vx = 0, vy = 0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1


def main():
    app = App(mouse=True, framerate=60)
    app.mouse_x = 0
    app.mouse_y = 0
    app.mouse_px = 0
    app.mouse_py = 0
    app.particles = []

    @app.on("mouse")
    def on_mouse(m):
        app.mouse_x = m.x
        app.mouse_y = m.y * 2
    
    @app.on("frame")
    def on_frame():
        w = app.screen.w
        h = app.screen.h
        colormap = [Color.rgb(0,0,0) for x in range(w) for y in range(h * 2)]

        dx = app.mouse_x - app.mouse_px
        dy = app.mouse_y - app.mouse_py
        l = math.sqrt(dx ** 2 + dy ** 2)
        d = math.atan2(dy, dx)

        j = min(25, int(l)) * 6
        for i in range(j):
            f = i / j
            ll = l* random.uniform(0.25, 0.5)
            dd = d + random.uniform(-0.25, 0.25)
            vx = ll * math.cos(dd)
            vy = ll * math.sin(dd)
            app.particles.append(Particle(app.mouse_px + dx * f, app.mouse_py + dy * f, vx, vy))

        app.screen.clear()
        for i, p in enumerate(app.particles):
            col = Color.hsl(i/len(app.particles), 1.0, 0.5)
            steps = math.hypot(p.vx, p.vy)
            for step in range(int(steps + 1)):
                f = step / steps
                px = int(p.x - p.vx * f)
                py = int(p.y - p.vy * f)
                if px >= 0 and py >= 0 and px < w and py < h * 2:
                    colormap[py * w + px] += RED
            p.update()
            if p.x < 0 or p.y < 0 or p.x >= w or p.y >= h * 2:
                app.particles.remove(p)
        draw_colormap_2x(app.screen, colormap, 0, 0, w=w, h=h * 2)
        app.screen.update()

        app.mouse_px = app.mouse_x
        app.mouse_py = app.mouse_y

    app.run()

if __name__ == "__main__":
    main()
