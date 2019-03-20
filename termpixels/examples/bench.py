from termpixels.detector import detect_backend
from termpixels.screen import Color
from time import perf_counter
ITER = 100
WARMUP = 20

b = detect_backend()
b.enter_alt_buffer()
t0 = perf_counter()
for i in range(ITER + WARMUP):
    if i < WARMUP:
        t0 = perf_counter()
    size = b.size
    for x in range(size[0]):
        for y in range(size[1]):
            b.cursor_pos = (x, y)
            b.bg = Color.rgb(x / size[0], y / size[0], 0)
            b.write(" ")
    b.flush()
t1 = perf_counter()
b.exit_alt_buffer()

print((t1 - t0) / ITER)