from time import sleep
from termpixels.screen import Screen, Color, PixelData
from termpixels.unix import UnixBackend

s = Screen(UnixBackend())
s.show_cursor = False
for x in range(s.w):
    for y in range(s.h):
        fx = x / s.w
        fy = y / s.h
        s.at(x, y).bg = Color(int(fx * 255), int(fy * 255), 0)
s.update()
while True:
    sleep(1/60)
