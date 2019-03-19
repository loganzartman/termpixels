def detect_backend():
    try:
        from termpixels.unix import UnixBackend
        return UnixBackend()
    except:
        from termpixels.win32 import Win32Backend
        return Win32Backend()

def detect_input():
    try:
        from termpixels.unix import UnixInput
        return UnixInput()
    except:
        from termpixels.win32 import Win32Input
        return Win32Input()
