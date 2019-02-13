from collections import defaultdict

class Observable:
    def __init__(self):
        self._listeners = defaultdict(list)
    
    def listen(self, event, listener):
        self._listeners[event].append(listener)
    
    def unlisten(self, event, listener):
        self._listeners[event].remove(listener)
    
    def emit(self, event, data=None):
        for l in self._listeners[event]:
            l(data)
