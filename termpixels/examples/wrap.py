from termpixels import App
from termpixels.util import wrap_text

class TestApp(App):
    def __init__(self, text=""):
        super().__init__()
        self.text = text

    def on_frame(self):
        self.screen.clear()
        self.screen.print(wrap_text(self.text, self.screen.w), 0, 0)
        self.screen.update()

if __name__ == "__main__":
    import sys
    TestApp(sys.stdin.read()).start()
