from collections import defaultdict

class Observable:
    """A base class that implements a simple event emitter.
    
    Events are named by arbitrary strings. An instance of an event can be
    emitted by providing the event name and an arbitrary data object. All 
    listeners will be synchronously invoked and passed the data object.
    """
    def __init__(self):
        self._listeners = defaultdict(list)
    
    def listen(self, event, listener):
        """Register a new event listener for a particular event name."""
        self._listeners[event].append(listener)
    
    def unlisten(self, event, listener):
        """Remove a particular event listener for a particular event name."""
        self._listeners[event].remove(listener)
    
    def emit(self, event, data=None):
        """Invoke all listeners for a particular event with arbitrary data."""
        for l in self._listeners[event]:
            l(data)
