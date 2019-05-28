from termpixels.buffer import Buffer, PixelData
from termpixels.util import terminal_char_len
from time import perf_counter

class Screen(Buffer):
    """Provides a pixel-like terminal abstraction. 

    Screen tries to abstract away the global state of cursor position and 
    current text style that is present in Unix-like terminal interfaces.
    Instead, it seeks to provide an API more similar to an image buffer.

    Screen is a Buffer that is linked to the user's terminal. The Screen 
    assumes the dimensions of the terminal window. If the terminal size is
    changed, the Screen will be resized, potentially losing some of its 
    contents.

    The user manipulates the Screen identically to how they would
    manipulate a Buffer, and then commits the changes to the terminal by 
    calling Screen's update() method. This method checks for changes to the
    contents of the Screen buffer and renders them to the terminal.

    Once the update is complete, Screen will position the terminal's cursor at
    the position specified by the cursor_pos property. This allows the user to
    position the cursor for aesthetic purposes.
    """

    def __init__(self, backend, input):
        self.backend = backend
        super().__init__(backend.size[0], backend.size[1])
        input.listen("resize", lambda _: self.resize(backend.size[0], backend.size[1]))    
        self.show_cursor = False 

    def resize(self, *args, **kwargs):
        super().resize(*args, **kwargs)
        self._pixels_cache = [[PixelData(fg=None, bg=None, char=" ") 
                               for y in range(self.h)] for x in range(self.w)]
        self.update()

    @property
    def show_cursor(self):
        """Get whether the cursor is visible."""
        return self.backend.show_cursor
    
    @show_cursor.setter
    def show_cursor(self, show):
        """Set whether the cursor is visible."""
        self.backend.show_cursor = show

    def update(self):
        """Commit the changes in the screen buffer to the backend (terminal).

        Determines which pixels (characters) have been modified from their 
        previous value, and re-draws those pixels using the backend.

        It should be noted that the pixel attributes are compared to their
        previous values. This means that if you, for example, clear a black
        screen to white, and then clear it back to black, no pixels will be
        re-rendered. This means that it is reasonable to clear and re-render
        the entire screen whenever you make an update, if it seems too
        challenging to manually make only the necessary changes.
        """
        with self.lock:
            t0 = perf_counter()
            self._update_count = 0
            for y in range(self.h):
                for x in range(self.w):
                    pixel = self._pixels[x][y]
                    if pixel._hash == None and pixel != self._pixels_cache[x][y]:
                        self._pixels_cache[x][y].set(pixel)
                        self._update_count += 1
                        # handle fullwidth (double-wide) characters
                        if x > 0 and terminal_char_len(self._pixels[x-1][y].char) > 1:
                            continue
                        self.render(pixel, x, y)
            self.backend.cursor_pos = self.cursor_pos
            self.backend.flush()
            self._update_duration = perf_counter() - t0
    
    def render(self, pixel, x, y):
        """Use the backend to redraw a particular PixelData instance.
        
        This is called internally by update() and generally should not be used.
        """
        self.backend.cursor_pos = (x, y)
        self.backend.fg = pixel.fg
        self.backend.bg = pixel.bg
        self.backend.write(pixel.char)