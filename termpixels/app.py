"""A utility for building complete terminal applications.

The App class wires together various components of termpixels to provide a
complete platform for building terminal applications. Namely, it combines:
    - the Backend implementation, which provides output capabilities
    - the Input implementation, which provides input capabilities
    - the Screen, which provides higher-level functionality on top of the
      backend and input.

The App class is generally used by extending it and overriding special event
handler methods to implement the application's business logic. An instance of
the subclass is constructed, and then the start() method is called on it, e.g.

Usage:
    class MyApp(App):
        def __init__(self):
            super().__init__()
        
        def on_frame(self):
            ...
        ...

    if __name__ == "__main__":
        MyApp().start()
"""

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
        """Start collecting input and run the App's main loop.
        
        Starts the application and begins calling the on_frame() method at the
        framerate specified in the constructor.
        """
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
        """Handle a key press event.
        
        This should be overridden in applications that need to respond to 
        keyboard input. It is invoked with a termpixels.keys.Key instance
        asynchronously, whenever a key is pressed.
        """
        pass
    
    def on_mouse(self, data):
        """Handle a mouse event.

        This should be overridden in applications that need to respond to
        mouse input. In addition to overriding this method, subclasses must 
        invoke the App constructor with the `mouse` parameter set to True, or
        no mouse events will be fired. This method is invoked with a 
        termpixels.keys.Mouse instance asynchronously, whenever a mouse event
        occurs.
        """
        pass
    
    def on_resize(self):
        """Handle a terminal resize event.

        This should be overridden in applications that need to respond to 
        changes in the terminal size. It is not strictly necessary to override 
        this method to do so, as the terminal size may be accessed within the
        App instance at any time as `self.screen.w` and `self.screen.h`
        """
        pass
    
    def on_frame(self):
        """Handle a frame event.

        This should be overridden in applications that need to perform updates
        at a regular interval. It is invoked automatically at the framerate
        specified in the App constructor once start() has been called.
        """
        pass
