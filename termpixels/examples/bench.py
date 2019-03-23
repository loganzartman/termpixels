from termpixels.detector import detect_backend
from termpixels import Color
from random import random
from time import perf_counter
from math import floor
ITER = 50000
WARMUP = 200

_r_i = 0
_r_ci = 0
_r_l = 128
_r_d = [random() for _ in range(_r_l)]
_r_cd = [Color.rgb(random(), random(), random()) for _ in range(_r_l)]
def rand():
    global _r_i
    _r_i = (_r_i + 1) % _r_l
    return _r_d[_r_i]
def irand(a, b):
    return floor(rand() * (b - a) + a)
def crand():
    global _r_ci
    _r_ci = (_r_ci + 1) % _r_l
    return _r_cd[_r_ci]

b = detect_backend()
b.enter_alt_buffer()
t0 = perf_counter()
for i in range(ITER + WARMUP):
    if i < WARMUP:
        t0 = perf_counter()
    size = b.size
    b.cursor_pos = (irand(0, size[0]), irand(0, size[1]))
    b.bg = crand()
    b.write(" ")
    b.flush()
t1 = perf_counter()
b.exit_alt_buffer()

print((t1 - t0) / ITER)