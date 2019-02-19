from app import App
from screen import Color

class MouseTestApp(App):
    def __init__(self):
        super().__init__(mouse=True)
    
    def on_mouse(self, mouse):
        self.screen.paint_bg = Color(128,0,0)
        self.screen.print("#", mouse.x, mouse.y)
    
    def on_frame(self):
        self.screen.update()
        self.screen.clear()
        self.screen.paint_bg = Color(0,0,0)
        self.screen.print(str(self.screen._update_count), 1, 1)
        self.screen.print(str(self.screen._update_duration), 1, 2)

MouseTestApp().start()
