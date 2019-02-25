from termpixels.unix import UnixBackend, UnixInput

def detect_backend():
    return UnixBackend()

def detect_input():
    return UnixInput()
