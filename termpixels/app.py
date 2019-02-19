from time import sleep
from screen import Screen
from detector import detect_backend, detect_input

class App:
    def __init__(self):
        self.backend = detect_backend()
        self.backend.save_screen()
        self.backend.application_keypad = True
        self.input = detect_input()
        self.input.listen("input", lambda d: self.on_key(d))
        self.screen = Screen(self.backend)
        self.backend.listen("resize", lambda _: self.on_resize())
    
    def start(self):
        self.backend.clear_screen()
        self.input.start()
        try:
            while True:
                self.on_frame()
                sleep(1/60)
        except KeyboardInterrupt:
            pass
        finally:
            self.screen.show_cursor = True
            self.screen.update()
            self.input.stop()
            self.backend.load_screen()
    
    def on_key(self, data):
        pass
    
    def on_resize(self):
        pass
    
    def on_frame(self):
        pass
