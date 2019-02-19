from app import App

class MouseTestApp(App):
    def __init__(self):
        super().__init__(mouse=True)
    
    def on_mouse(self, mouse):
        self.screen.clear()
        self.screen.print("#", mouse.x, mouse.y)
    
    def on_frame(self):
        self.screen.update()

MouseTestApp().start()
