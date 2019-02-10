import os
from os.path import expanduser, exists
import struct
import re
from terminfo_indices import boolean_indices, number_indices, string_indices

TERMINFO_PATHS = ["/usr/share/terminfo", "/usr/lib/terminfo", expanduser("~/.terminfo"), "/etc/terminfo"]
if "TERMINFO" in os.environ: 
    TERMINFO_PATHS.append(os.environ["TERMINFO"], 0)

class Terminfo:
    def __init__(self, *, names, booleans, numbers, strings):
        self.names = names
        self.booleans = booleans
        self.numbers = numbers
        self.strings = strings
    
    def getBoolean(self, name):
        return self.booleans[boolean_indices[name]]
    
    def getNumber(self, name):
        return self.numbers[number_indices[name]]

    def getString(self, name):
        return self.strings[string_indices[name]]

    def get(self, name):
        if name in boolean_indices:
            return self.getBoolean(name)
        if name in number_indices:
            return self.getNumber(name)
        if name in string_indices:
            return self.getString(name)
        raise Exception("Invalid terminfo name")

def terminal_name():
    return os.environ["TERM"] or "xterm"

def get_terminfo(name=terminal_name()):
    for path in TERMINFO_PATHS:
        if exists(path):
            return parse_terminfo("{}/{}/{}".format(path, name[0], name))
    raise FileNotFoundError("Could not find a terminfo database.")

def parse_terminfo(path):
    """Parse a compiled terminfo file (directory tree format).
    See `man 5 term`
    """
    with open(path, "rb") as f:
        magic = _read_short(f)
        if magic == 542:
            return _parse_terminfo_base(f, extended_numbers=True)
        if magic == 282:
            return _parse_terminfo_base(f, extended_numbers=False)
        raise Exception("Invalid magic number")

def _read_short(f):
    """Read little-endian short.
    """
    return struct.unpack("<h", f.read(2))[0]

def _read_int(f):
    """Read little-endian integer.
    """
    return struct.unpack("<i", f.read(4))[0]

def _eat_null(f):
    old = f.tell()
    if f.read(1) != "\x00":
        f.seek(old)

def _parse_terminfo_base(f, extended_numbers=False):
    names_bytes = _read_short(f)    # the size, in bytes, of the names section
    booleans_count = _read_short(f) # the number of bytes in the boolean section
    numbers_count = _read_short(f)  # the number of short integers in the numbers section
    offsets_count = _read_short(f)  # the number of offsets (short integers) in the strings section
    table_bytes = _read_short(f)    # the size, in bytes, of the string table

    names = f.read(names_bytes).decode("ascii").rstrip("\0").split("|")
    booleans = [bool(b) for b in f.read(booleans_count)]

    _eat_null(f) # eat alignment byte if present

    numbers = [_read_int(f) if extended_numbers else _read_short(f) for _ in range(numbers_count)]

    offsets = [_read_short(f) for _ in range(offsets_count)]
    print(offsets)
    string_table = f.read(table_bytes).decode("ascii") + "\0" # extra null terminator to simplify next line
    strings = []
    for o in offsets:
        if o < 0:
            strings.append(None)
        strings.append(string_table[o:string_table.index("\0", o)])
    return Terminfo(names=names, booleans=booleans, numbers=numbers, strings=strings)

get_terminfo()