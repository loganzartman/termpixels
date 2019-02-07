import sys
from unix import UnixBackend

def detect_backend():
    if sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
        return UnixBackend()
    else:
        raise NotImplementedError("Unsupported platform.")
