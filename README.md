# termpixels
*the terminal as a character-cell matrix*

## Purpose
Creating programs that run inside of terminals seems convoluted. The goal of termpixels is to abstract the terminal into a 2D array of "pixels", or character cells, which each contain a single text character, a foreground color, and a background color. termpixels allows you to modify the screen contents anywhere, at any time, and then handles updating the terminal automatically.

## Limitations
There are lots of great libraries for coloring terminal output. This one is designed for full-screen applications that completely control the contents of the screen. That means that it automatically saves and clears the screen, resets the cursor position, and accepts input in cbreak mode.

## Demo
![Demo gif](fun-text.gif)
```python
from termpixels.app import App
from termpixels.screen import Color
from time import time
from math import sin

class FunTextApp(App):
    def __init__(self):
        super().__init__()
    
    def on_frame(self):
        self.screen.clear()                           # remove everything from the screen
        text = "Hello world, from termpixels!"
        
        for i, c in enumerate(text):
            f = i / len(text)
            color = Color.hsl(f + time(), 1, 0.5)     # create a color from a hue value
            x = self.screen.w // 2 - len(text) // 2   # horizontally center the text
            offset = sin(time() * 3 + f * 5) * 2      # some arbitrary math
            y = round(self.screen.h / 2 + offset)     # vertical center with an offset
            self.screen.print(c, x + i, y, fg=color)  # draw the text to the screen buffer
        
        self.screen.update()                          # commit the changes to the screen

if __name__ == "__main__":
    FunTextApp().start()
```

## Features
* Unix terminal feature detection with terminfo (via Python [curses][python-curses])
* Windows support through Win32 Console API
* Terminal (re)size detection
* Asynchronous input
	* Keyboard input with support for special keys like arrows, function keys, escape, etc.
	* Mouse click and move input in terminals supporting xterm mouse
* 16, 256, and true color output (with detection for best supported mode)
* No reliance on ncurses except for terminfo lookup
* 100% Python
* and more

## Get it
This project is on [PyPI][pypi].

Alternatively, just `pip install -e .` in the root directory.

## Inspiration
* [tcell][tcell]
* [ncurses][ncurses]

[python-curses]: https://docs.python.org/3/howto/curses.html
[tcell]: https://github.com/gdamore/tcell
[ncurses]: https://www.gnu.org/software/ncurses/
[pypi]: https://pypi.org/project/termpixels/

