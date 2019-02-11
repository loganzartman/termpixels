import curses
import operator
import re
from functools import lru_cache

class Terminfo:
    def __init__(self):
        curses.setupterm()
    
    @lru_cache(128)
    def flag(self, name):
        return curses.tigetflag(name)
    
    @lru_cache(128)
    def num(self, name):
        return curses.tigetnum(name)

    @lru_cache(128)
    def string(self, name):
        return curses.tigetstr(name)

    def parameterize(self, name, *args):
        return curses.tparm(self.string(name), *args)
