import random
import math
from termpixels.app import App
from termpixels.color import Color

class ParticleApp(App):
    def __init__(self):
        super().__init__(mouse=True, framerate=60)
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_px = 0
        self.mouse_py = 0
        self.particles = []
    
    def on_mouse(self, m):
        self.mouse_x = m.x
        self.mouse_y = m.y
    
    def on_frame(self):
        dx = self.mouse_x - self.mouse_px
        dy = self.mouse_y - self.mouse_py
        l = math.sqrt(dx ** 2 + dy ** 2)
        d = math.atan2(dy, dx)

        j = min(45, int(l))*2
        for i in range(j):
            f = i / j
            ll = l* random.uniform(0.25, 0.5)
            dd = d + random.uniform(-0.2, 0.2)
            vx = ll * math.cos(dd)
            vy = ll * math.sin(dd)
            self.particles.append(Particle(self.mouse_px + dx * f, self.mouse_py + dy * f, vx, vy))

        self.screen.clear()
        for i, p in enumerate(self.particles):
            col = Color.hsl(i/len(self.particles), 1.0, 0.5)
            self.screen.print(" ", int(p.x), int(p.y), bg=col)
            p.update()
            if p.x < 0 or p.y < 0 or p.x >= self.screen.w or p.y >= self.screen.h:
                self.particles.remove(p)
        self.screen.update()

        self.mouse_px = self.mouse_x
        self.mouse_py = self.mouse_y

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

ParticleApp().start()
