import os
from os.path import expanduser, exists

TERMINFO_PATHS = ["/usr/share/terminfo", "/usr/lib/terminfo", expanduser("~/.terminfo"), "/etc/terminfo"]

class Terminfo:
    def __init__(self, *, names, booleans, numbers, offsets, strings):
        self.names = names
        self.booleans = booleans
        self.numbers = numbers
        self.offsets = offsets
        self.strings = strings

def terminal_name():
    return os.environ["TERM"]

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
        magic = _read_int(f)
        if magic == 542:
            return _parse_terminfo_base(f, extended=True)
        if magic == 282:
            return _parse_terminfo_base(f, extended=False)
        raise Exception("Invalid magic number")

def _read_int(f, size=2):
    """Read little-endian integer.
    """
    bites = [b for b in f.read(size)]
    num = 0
    if all(b == 255 for b in bites):
        return -1
    for i, b in enumerate(bites):
        num |= b << (8 * i)
    return num

def _eat_null(f):
    old = f.tell()
    if f.read(1) != "\x00":
        f.seek(old)

def _parse_terminfo_base(f, extended=False):
    names_bytes = _read_int(f)    # the size, in bytes, of the names section
    booleans_count = _read_int(f) # the number of bytes in the boolean section
    numbers_count = _read_int(f)  # the number of short integers in the numbers section
    offsets_count = _read_int(f)  # the number of offsets (short integers) in the strings section
    table_bytes = _read_int(f)    # the size, in bytes, of the string table

    names = f.read(names_bytes).decode("ascii").rstrip("\0").split("|")
    booleans = list(map(bool, f.read(booleans_count)))

    _eat_null(f) # eat alignment byte if present

    numbers = [_read_int(f, 4 if extended else 2) for _ in range(numbers_count)]
    offsets = [_read_int(f) for _ in range(offsets_count)]
    strings = f.read(table_bytes).decode("ascii").split("\0")
    return Terminfo(names=names, booleans=booleans, numbers=numbers, offsets=offsets, strings=strings)
