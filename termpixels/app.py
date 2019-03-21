from time import sleep, perf_counter
from termpixels.screen import Screen
from termpixels.detector import detect_backend, detect_input

class App:
    def __init__(self, *, mouse=False, framerate=30):
        self.backend = detect_backend()
        self.backend.enter_alt_buffer()
        self.backend.application_keypad = True
        self.backend.mouse_tracking = mouse
        self.input = detect_input()
        self.input.listen("key", lambda d: self.on_key(d))
        self.input.listen("mouse", lambda d: self.on_mouse(d))
        def handle_resize(_):
            self.backend.size_dirty = True
            self.on_resize()
        self.input.listen("resize", handle_resize)
        self.screen = Screen(self.backend, self.input)
        self._framerate = framerate
    
    def start(self):
        self.backend.clear_screen()
        self.input.start()
        try:
            while True:
                t0 = perf_counter()
                self.on_frame()
                dt = perf_counter() - t0
                sleep(max(1/500, 1/self._framerate - dt))
        except KeyboardInterrupt:
            pass
        finally:
            self.backend.application_keypad = False
            self.backend.mouse_tracking = False
            self.input.stop()
            self.screen.show_cursor = True
            self.screen.update()
            self.backend.exit_alt_buffer()
    
    def on_key(self, data):
        pass
    
    def on_mouse(self, data):
        pass
    
    def on_resize(self):
        pass
    
    def on_frame(self):
        pass
