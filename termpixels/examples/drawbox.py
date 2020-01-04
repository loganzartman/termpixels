from termpixels import App, Buffer, Color
from termpixels.drawing import draw_box, BOX_CHARS_DOUBLE
from termpixels.drawing import draw_frame, FRAME_CHARS_DOUBLE
from termpixels.util import corners_to_box
from time import perf_counter

def main():
    app = App(mouse=True, framerate=120)
    buf = Buffer(0, 0)

    dirty = True
    dragging = False
    drag_start = None
    mouse_pos = None

    def do_box(buffer):
        if drag_start is None or mouse_pos is None:
            return
        x, y, w, h = corners_to_box(*drag_start, *mouse_pos)
        # draw_box(buffer, x, y, w, h, chars=BOX_CHARS_DOUBLE, fg=Color.hsl(perf_counter(), 1.0, 0.5))
        draw_frame(buffer, x, y, w, h, chars=FRAME_CHARS_DOUBLE, fg=Color.hsl(perf_counter(), 1.0, 0.5))

    @app.on("start")
    @app.on("resize")
    def on_resize():
        buf.resize(app.screen.w, app.screen.h)
        for x in range(buf.w):
            for y in range(buf.h):
                col = Color.rgb(0,0,0) if (x + y) % 2 else Color.rgb(0.1,0.1,0.1)
                buf.put_char(" ", x, y, bg=col)

    @app.on("mouse")
    def on_mouse(mouse):
        nonlocal dirty, dragging, drag_start, mouse_pos
        if mouse.left:
            if mouse.down:
                dragging = True
                drag_start = (mouse.x, mouse.y)
            if mouse.up:
                do_box(buf)
                dragging = False
            dirty = True
            mouse_pos = (mouse.x, mouse.y)
        else:
            dragging = False

    @app.on("frame")
    def on_frame():
        app.screen.clear()
        app.screen.blit(buf)
        if dragging:
            do_box(app.screen)
        app.screen.update()

    app.run()

if __name__ == "__main__":
    main()
