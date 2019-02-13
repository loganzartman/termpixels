from time import sleep
from screen import Screen
from detector import detect_backend, detect_input

class App:
    def __init__(self):
        self.backend = detect_backend()
        self.input = detect_input()
        self.input.listen("key", self.on_key)
        self.screen = Screen(self.backend)
        self.cursor_x = 0

    def on_key(self, ch):
        self.screen.print(ch, self.cursor_x, 1)
        self.screen.cursor_pos = (self.cursor_x + 1, 1)
        self.screen.update()
        self.cursor_x += 1
    
    def start(self):
        self.input.start()
        self.screen.print("Type something:", 0, 0)
        self.screen.update()
        try:
            while True:
                sleep(1/60)
        except KeyboardInterrupt:
            pass
        finally:
            self.input.stop() 
