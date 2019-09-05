import random
import math
from termpixels import App, Color

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
        app.mouse_y = m.y
        
    @app.on("frame")
    def on_frame():
        dx = app.mouse_x - app.mouse_px
        dy = app.mouse_y - app.mouse_py
        l = math.sqrt(dx ** 2 + dy ** 2)
        d = math.atan2(dy, dx)

        j = min(45, int(l))*2
        for i in range(j):
            f = i / j
            ll = l* random.uniform(0.25, 0.5)
            dd = d + random.uniform(-0.2, 0.2)
            vx = ll * math.cos(dd)
            vy = ll * math.sin(dd)
            app.particles.append(Particle(app.mouse_px + dx * f, app.mouse_py + dy * f, vx, vy))

        app.screen.clear()
        for i, p in enumerate(app.particles):
            col = Color.hsl(i/len(app.particles), 1.0, 0.5)
            app.screen.print(" ", int(p.x), int(p.y), bg=col)
            p.update()
            if p.x < 0 or p.y < 0 or p.x >= app.screen.w or p.y >= app.screen.h:
                app.particles.remove(p)
        app.screen.update()

        app.mouse_px = app.mouse_x
        app.mouse_py = app.mouse_y

    app.start()

if __name__ == "__main__":
    main()
