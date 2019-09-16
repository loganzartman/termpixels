import math
import time
from termpixels import App, Color, Buffer
from termpixels.drawing import draw_box, draw_hline, draw_spinner, draw_colormap, draw_colormap_2x
from termpixels.drawing import BOX_CHARS_LIGHT_DOUBLE_TOP, SPINNER_PIPE
from termpixels.util import wrap_text

GREY = Color.rgb(0.5, 0.5, 0.5)
YELLOW = Color.rgb(0.5, 0.5, 0)
GREEN = Color.rgb(0, 0.5, 0)

LIPSUM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed nec erat quis turpis ultrices eleifend id et urna. Praesent ultricies orci fermentum, placerat eros id, scelerisque mi. Aenean lobortis pellentesque diam, vel auctor felis semper in. Aliquam cursus diam sit amet lorem faucibus, eget sagittis eros bibendum. Maecenas dignissim libero."

# a frightening hand-drawn smiley face
SMILEY = list(map(
    lambda b: [None, YELLOW, GREEN, GREY][b],
    [0, 0, 1, 1, 1, 0, 0,
     0, 1, 1, 1, 1, 1, 0,
     1, 1, 2, 1, 2, 1, 1,
     1, 1, 1, 1, 1, 1, 1,
     1, 3, 1, 1, 1, 3, 1,
     0, 1, 3, 3, 3, 1, 0,
     0, 0, 1, 1, 1, 0, 0]
))

def main():
    app = App()
    inner_buffer = Buffer(0, 0)

    outer_pad = 1
    inner_w = 0
    inner_h = 0

    @app.on("start")
    @app.on("resize")
    @app.on("frame")
    def update():
        nonlocal inner_w, inner_h
        app.screen.clear()
        inner_buffer.clear()

        # compute inner dimensions of box
        inner_w = app.screen.w - outer_pad * 2 - 2
        inner_h = app.screen.h - outer_pad * 2 - 2
        inner_buffer.resize(inner_w, inner_h)

        # draw a box with a title
        draw_box(app.screen, outer_pad, outer_pad, inner_w + 2, inner_h + 2, chars=BOX_CHARS_LIGHT_DOUBLE_TOP)
        title = "Hello drawing"
        app.screen.print(title, app.screen.w // 2 - len(title) // 2, outer_pad)

        # draw spinners
        inner_buffer.print("Inner header ", 0, 0)
        draw_spinner(inner_buffer, *inner_buffer.print_pos, freq=2, fg=GREEN)
        inner_buffer.print(" ")
        draw_spinner(inner_buffer, *inner_buffer.print_pos, freq=2, fg=GREY, frames=SPINNER_PIPE)
        inner_buffer.print(" ")
        draw_spinner(inner_buffer, *inner_buffer.print_pos, freq=2, t=math.sin(time.perf_counter()), fg=YELLOW)

        # draw a horizontal line along x=2 within the box
        draw_hline(inner_buffer, 2, fg=GREY)

        # print some word-wrapped text inside the box
        inner_buffer.print(wrap_text(LIPSUM, inner_w), 0, 3, fg=YELLOW)

        # draw a color bitmap at 2x vertical resolution
        draw_colormap_2x(inner_buffer, SMILEY, 2, inner_buffer.h - 3 - 2, w=7, h=7)

        # copy box contents to screen
        app.screen.blit(inner_buffer, outer_pad + 1, outer_pad + 1)
        app.screen.update()
    
    app.start()
    app.await_stop()

if __name__ == "__main__":
    main()
