def detect_backend():
    """Try to construct an appropriate backend for this platform."""
    try:
        from termpixels.unix import UnixBackend
        return UnixBackend()
    except:
        from termpixels.win32 import Win32Backend
        return Win32Backend()

def detect_input():
    """Try to construct an appropriate input implementation for this platform."""
    try:
        from termpixels.unix import UnixInput
        return UnixInput()
    except:
        from termpixels.win32 import Win32Input
        return Win32Input()
