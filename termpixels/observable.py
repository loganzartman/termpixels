from collections import defaultdict
from queue import Queue, Empty

main_event_queue = Queue()

class Event:
    def __init__(self, source, name, data):
        self.source = source
        self.name = name
        self.data = data

class Observable:
    """A base class that implements a simple event emitter.
    
    Events are named by arbitrary strings. An instance of an event can be
    emitted by providing the event name and an arbitrary data object. All 
    listeners will be synchronously invoked and passed the data object.
    """
    def __init__(self, queue=main_event_queue):
        self._listeners = defaultdict(list)
        self._event_queue = queue
    
    def listen(self, event_name, listener):
        """Register a new event listener for a particular event name."""
        self._listeners[event_name].append(listener)
    
    def unlisten(self, event_name, listener):
        """Remove a particular event listener for a particular event name."""
        self._listeners[event_name].remove(listener)
    
    def emit(self, event_name, data=None):
        """Invoke all listeners for a particular event with arbitrary data."""
        self._event_queue.put(Event(source=self, name=event_name, data=data))

def poll_events(queue=main_event_queue):
    try:
        while True:
            event = queue.get_nowait()
            for l in event.source._listeners[event.name]:
                l(event.data)
    except Empty:
        pass
