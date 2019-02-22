from time import sleep
from random import randint, choice
from math import sin, sqrt 
from termpixels.screen import Screen, Color, PixelData
from termpixels.unix import UnixBackend

s = Screen(UnixBackend())
s.show_cursor = False 
strings = ["Hello world!", "Wow " * 10, "Another few lines...", "3", "2", "1"]
for line, string in enumerate(strings):
    for pos, ch in enumerate(string):
        s.print(ch, pos, line)
        s.update()
        sleep(0.01)
    sleep(0.2)

i = 0
while True:
    r = (sin(i) * 0.5 + 0.5) * 5 + 3
    for x in range(s.w):
        for y in range(s.h):
            offset_x = (x - s.w / 2) / 2
            offset_y = y - s.h / 2
            dist = sqrt(offset_x ** 2 + offset_y ** 2)
            if dist < r:
                s.at(x, y).bg = Color(0, 255, 0)
            else:
                s.at(x, y).bg = Color(0, 0, 0)
    s.update()
    i += 0.1
    # sleep(0.01)
