from time import sleep
from screen import Screen, Color, PixelData
from unix import UnixBackend

s = Screen(24, 12, UnixBackend())
s.show_cursor = False
for x in range(s.w):
    for y in range(s.h):
        fx = x / s.w
        fy = y / s.h
        s.at(x, y).bg = Color(int(fx * 255), int(fy * 255), 0)
s.update()
while True:
    sleep(1/60)
