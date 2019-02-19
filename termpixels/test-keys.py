from app import App

class KeyTestApp(App):
    def __init__(self):
        super().__init__()
    
    def on_key(self, k):
        self.screen.clear()
        self.screen.print(repr(k), 1, 1)
        self.screen.update()

KeyTestApp().start()
