import curses
import operator
import re
import os
from functools import lru_cache

class Terminfo:
    def __init__(self):
        curses.setupterm()

    @property
    def termname(self):
        return os.environ["TERM"] 
    
    @lru_cache(128)
    def flag(self, name):
        return curses.tigetflag(name) > 0
    
    @lru_cache(128)
    def num(self, name):
        return curses.tigetnum(name)

    @lru_cache(128)
    def string(self, name):
        return curses.tigetstr(name)

    def parameterize(self, name, *args, require=False):
        string = self.string(name)
        if string is None:
            if not require:
                return ""
            else:
                raise Exception("Terminal does not support required capability: '{}'".format(name))
        return curses.tparm(string, *args)
