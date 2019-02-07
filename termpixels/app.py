from screen import Screen
from detector import detect_backend, detect_input

class App:
    def __init__(self):
        self.backend = detect_backend()
        self.input = detect_input()
        self.screen = Screen(80, 20, self.backend)
    
    def start(self):
        self.input.start()
        self.screen.print("Type something:", 0, 0)
        self.screen.update()
        try:
            x = 0
            while True:
                ch = self.input.getch()
                self.screen.print(ch, x, 1)
                self.screen.cursor_pos = (x + 1, 1)
                self.screen.update()
                x += 1
        except KeyboardInterrupt:
            pass
        finally:
            self.input.stop() 
