from termpixels import App, Color
from termpixels.keys import Mouse

def main():
    app = App(mouse=True)
    x = 0
    y = 0
    left = False
    middle = False
    right = False
    scroll_total = 0

    @app.on("mouse")
    def mouse(mouse: Mouse):
        nonlocal x, y, left, middle, right, scroll_total

        if mouse.scrollup:
            scroll_total += 1
        elif mouse.scrolldown:
            scroll_total -= 1
        
        if mouse.down:
            if mouse.left:
                left = True
            if mouse.middle:
                middle = True
            if mouse.right:
                right = True
        elif mouse.up:
            if mouse.left:
                left = False
            if mouse.middle:
                middle = False
            if mouse.right:
                right = False
        
        x = mouse.x
        y = mouse.y
    
    @app.on("frame")
    def frame():
        app.screen.clear()
        app.screen.print("".join("#" if b else "_" for b in [left, middle, right]), 1, 1)
        app.screen.print("LMR", 1, 2)
        app.screen.print(f"scroll: {scroll_total}", 7, 2)
        app.screen.show_cursor = True
        app.screen.cursor_pos = (x, y)
        app.screen.update()

    app.run()

if __name__ == "__main__":
    main()
