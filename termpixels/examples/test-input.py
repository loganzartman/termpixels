from termpixels import App, Color

class InputTestApp(App):
    def __init__(self):
        super().__init__(mouse=True)
        self.input.listen("raw_input", lambda chars: self.on_raw(chars))
    
    def on_raw(self, chars):
        self.screen.clear()
        self.screen.print(repr(chars), 1, 1)
        self.screen.update()

InputTestApp().start()
