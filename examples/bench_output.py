from termpixels import App, Color
from time import perf_counter

def main():
    backend = App().backend
    backend.enter_alt_buffer()
    colors = [Color.rgb(1,0,0), Color.rgb(1,1,0), Color.rgb(0,1,0), Color.rgb(0,1,1), Color.rgb(0,0,1), Color.rgb(1,0,1)]

    t0 = perf_counter()
    frames = 0
    pos = 0

    while frames < 10000:
        backend.bg = colors[frames % len(colors)]
        backend.write(" ")
        backend.flush()
        frames += 1
        t1 = perf_counter()
    
    backend.exit_alt_buffer()
    backend.flush()

    tpf = (t1 - t0) / frames
    print("Terminal: {}\n".format(backend.terminal_name))
    print("Avg time per frame: {:.4f}\n".format(tpf))
    print("Avg framerate: {:.2f}\n".format(1/tpf))

if __name__ == "__main__":
    main()