from collections import defaultdict
from queue import Queue, Empty

main_event_queue = Queue()

class Event:
    def __init__(self, source, name, args, kwargs):
        self.source = source
        self.name = name
        self.args = args
        self.kwargs = kwargs

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
    
    def emit(self, event_name, *args, **kwargs):
        """Invoke all listeners for a particular event with arbitrary data."""
        self._event_queue.put(Event(source=self, name=event_name, args=args, kwargs=kwargs))
    
    def on(self, event_name):
        """listen() as a decorator."""
        def decorator(fn):
            def wrapper(*args, **kwargs):
                fn(*args, **kwargs)
            wrapper.off = lambda: self.unlisten(event_name, wrapper)
            self.listen(event_name, wrapper)
            return wrapper
        return decorator

    def propagate_event(self, source, event_name):
        """Create a listener that propagates all events of the given name from another Observable."""
        def propagate(*args, **kwargs):
            self.emit(event_name, *args, **kwargs)
        source.listen(event_name, propagate)

def poll_events(queue=main_event_queue):
    try:
        while True:
            event = queue.get_nowait()
            for l in event.source._listeners[event.name]:
                l(*event.args, **event.kwargs)
    except Empty:
        pass
