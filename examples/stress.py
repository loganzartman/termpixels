from termpixels import App, Color, PixelData
from random import choice
from time import perf_counter

def main():
    app = App(framerate=float("inf"))

    colors = [Color.rgb(r,g,b) for r in (0, 1) for g in (0, 1) for b in (0, 1)]
    pixels = [PixelData(char="▄", fg=col1, bg=col2) for col1 in colors for col2 in colors]

    t0 = perf_counter()
    n_frames = 0
    n_updates = 0
    update_time = 0

    @app.on("frame")
    def on_frame():
        nonlocal n_frames, n_updates, update_time
        for x in range(app.screen.w):
            for y in range(app.screen.h):
                app.screen[x,y].set(choice(pixels))
        app.screen.update()
        n_frames += 1
        n_updates += app.screen._update_count
        update_time += app.screen._update_duration

    app.run()

    updates_per_ms = n_updates / update_time / 1000
    updates_per_ms_real = n_updates / (perf_counter() - t0) / 1000
    print("Updates per ms (updating): {:.2f}".format(updates_per_ms))
    print("Updates per ms (real time): {:.2f}".format(updates_per_ms_real))
    print("Average update time ms: {:.2f}".format(update_time / n_frames * 1000))
    print("Average potential FPS: {:.2f}".format(n_frames / update_time))

if __name__ == "__main__":
    main()
