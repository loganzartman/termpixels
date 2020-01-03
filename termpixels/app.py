"""A utility for building complete terminal applications.

The App class wires together various components of termpixels to provide a
complete platform for building terminal applications. It provides the following
pre-built instances as member variables:
    - backend: provides output (rendering) capabilities
    - input: provides input (keyboard, mouse, etc.) capabilities
    - screen: provides higher-level interface for printing text, filling areas,
              reading characters, etc.

The App class is used by instantiating it and then listening to its lifecycle
events to implement business logic. The app can be launched by invoking its
start() method. This method returns immediately, so in order to wait for the
app to finish running, one should call the await_stop() method afterwards. 
Alternatively, these steps can be combined using the run() method.

Example:
```
from termpixels import App
def main():
    app = App()

    @app.on("start")
    def start():
        app.screen.print("Hello world!")
        app.screen.update()
    
    app.run()

if __name__ == "__main__":
    main()
```
"""

from time import sleep, perf_counter
from threading import Event
from termpixels.screen import Screen
from termpixels.detector import detect_backend, detect_input
from termpixels.observable import Observable, start_polling, poll_events, Interval
import termpixels.observable

class App(Observable):
    def __init__(self, *, mouse=False, framerate=30):
        """
        mouse - whether to enable mouse tracking
        framerate - number of "frame" events to emit per second
        """
        super().__init__()
        self.backend = detect_backend()
        self.input = detect_input()
        self.screen = Screen(self.backend, self.input)

        self.propagate_event(self.input, "key")
        self.propagate_event(self.input, "mouse")

        @self.input.on("resize")
        def handle_resize():
            self.backend.size_dirty = True
            self.emit("resize")

        self._stop_event = Event()
        self._exit_event = Event()
        self.listen("_start", self._on_start)
        self.listen("_stop", self._on_stop)
        self.listen("_exit", lambda: self._exit_event.set())

        self._framerate = framerate
        self._mouse = mouse
        self._stopping = False

        self._frame_interval = self.create_interval("frame", 1/self._framerate)

    def run(self, *args, **kwargs):
        """ start() and then await_stop() """
        self.start(*args, **kwargs)
        self.await_stop()

    def start(self, *args, **kwargs):
        """ Start running the App asynchronously.

        Forwards all arguments to the "start" event.
        """
        start_polling()
        self.t0 = perf_counter()
        self.emit("_start", *args, **kwargs)
    
    def _on_start(self, *args, **kwargs):
        self._stopping = False
        
        self.backend.enter_alt_buffer()
        # screen needs to be initialized with alternate buffer active or
        # it will destroy user's screen contents
        
        self.backend.application_keypad = True
        if self._mouse:
            self.backend.mouse_tracking = True
        
        try:
            self.backend.set_charset_utf8(True)
        except AttributeError:
            pass

        self.backend.flush()
        
        self.input.start()
        self.screen.show_cursor = False
        self.backend.flush()

        self._frame_interval.start()
        self.emit("start", *args, **kwargs)
    
    def _on_stop(self):
        self.backend.application_keypad = False
        self.backend.mouse_tracking = False
        self.input.stop()
        self.screen.show_cursor = True
        self.screen.update()
        self.backend.set_charset_utf8(False)
        self.backend.flush()
        self.backend.exit_alt_buffer()
        self.backend.flush()
        self._stop_event.set()

    def await_stop(self):
        """ Block until the App is stopped. """
        try:
            self._stop_event.wait()
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
            poll_events()
            self._exit_event.wait()

    def stop(self):
        """Tell the application to stop running gracefully."""
        # This sequence of four events enables both the before_stop and 
        # after_stop events, which are fired before and after the terminal state
        # is restored, respectively.
        if not self._stopping:
            self._stopping = True
            self._frame_interval.cancel()
            self.emit("before_stop")
            self.emit("_stop")
            self.emit("after_stop")
            self.emit("_exit")

class LegacyApp(App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.listen("start", self.on_start)
        self.listen("frame", self.on_frame)
        self.listen("key", self.on_key)
        self.listen("mouse", self.on_mouse)
        self.listen("before_stop", self.on_before_stop)
        self.listen("after_stop", self.on_after_stop)
    
    def on_start(self, *args, **kwargs):
        pass

    def on_frame(self):
        pass

    def on_key(self, k):
        pass

    def on_mouse(self, m):
        pass

    def on_before_stop(self):
        pass

    def on_after_stop(self):
        pass

