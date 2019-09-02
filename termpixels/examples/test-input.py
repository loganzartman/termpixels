from termpixels.detector import detect_input, detect_backend
from termpixels.observable import poll_events
from time import sleep

def main():
    backend = detect_backend()
    backend.mouse_tracking = True
    backend.flush()

    inpt = detect_input()
    inpt.listen("raw_input", lambda chars: print(repr(chars)))
    inpt.start()

    while True:
        poll_events()
        sleep(1/60)

if __name__ == "__main__":
    main()
