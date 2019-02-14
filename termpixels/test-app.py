from app import App

class TestApp(App):
    def __init__(self):
        super().__init__()
    
    def on_resize(self):
        self.screen.print("{} x {}    ".format(self.screen.w, self.screen.h), 1, 1)
        self.screen.update()

TestApp().start()
