from collections import defaultdict

from termpixels.buffer import Buffer
from termpixels.color import Color
from termpixels.pixeldata import PixelData

class SparseBuffer(Buffer):
    """An implementation of Buffer that stores pixels in a sparse data structure.

    SparseBuffer stores only pixels which have been accessed since last 
    clearing the buffer. You might want to use it if you need to resize the
    buffer frequently, or if you need a large buffer that will have more
    blank space than content.

    Performance characteristics as compared to Buffer:
    - Resizing and clearing are faster (O(1) vs O(m*n)).
    - Blitting to another buffer can be faster, if few pixels have been accessed.
    - Accessing a pixel can be slower (still O(1) amortized).
    """
    def __init__(self, *params, **kwargs):
        super().__init__(*params, **kwargs)
        self._data = defaultdict(lambda: {})
        self.clear()
        self.bounded = True
    
    def resize(self, w, h):
        self._w = w
        self._h = h

    def extend_to(self, w=0, h=0):
        """Extend the bounds of the SparseBuffer.

        If either of the proposed bounds are smaller than the existing bound, 
        then that bound will be left unchanged.
        """
        self._w = max(w, self._w)
        self._h = max(h, self._h)
    
    def in_bounds(self, x, y):
        if not self.bounded:
            return x >= 0 and y >= 0
        return super().in_bounds(x, y)
    
    def at_unsafe(self, x, y, *, mutable=True):
        """Get the PixelData instance for a particular location.

        Should be used by internal methods for pixel data access.
        No bounds checking is performed.
        If mutable=False, this method is allowed to return an ImmutablePixelData.
        """
        if y not in self._data[x]:
            self._data[x][y] = PixelData().set(self._clear_pixel)
            self._pixel_count += 1
        return self._data[x][y]
    
    def at(self, *args, clip=False, **kwargs):
        """Get the PixelData instance for a particular location.

        Setting clip to true clips the provided position to remain inside the
        screen buffer. If clip is not enabled, an Exception will be raised if 
        the provided position is outside the bounds of the screen buffer.

        The returned PixelData instance may be mutated to modify the contents
        of the screen buffer.
        """
        if not self.bounded:
            return super().at(*args, clip=False, **kwargs)
        return super().at(*args, clip=clip, **kwargs)
    
    def clear(self, *, fg=Color(255,255,255), bg=Color(0,0,0), char=" "):
        """Fill the entire screen buffer with the given attributes.

        Unlike fill(), all attributes must be specified. If not specified, they
        will be given default values instead.
        """
        self._clear_pixel = PixelData(fg=fg, bg=bg, char=char)
        self._data = defaultdict(lambda: {})
        self._pixel_count = 0
