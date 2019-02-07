import sys
from unix import UnixBackend, UnixInput

def detect_backend():
    if sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
        return UnixBackend()
    else:
        raise NotImplementedError("Unsupported platform.")

def detect_input():
    if sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
        return UnixInput()
    else:
        raise NotImplementedError("Unsupported platform.")
