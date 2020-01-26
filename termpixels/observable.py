from collections import defaultdict, deque
from queue import Queue, Empty
from threading import Thread, Lock
import sys
import threading
import time
import traceback

_EVENT_HISTORY_LENGTH = 8
_DEBUG_EVENTS = True

main_event_queue = Queue()

class Event:
    def __init__(self, *, source, name, args=[], kwargs={}, track_dispatch=False):
        """
        source - the Observable that emitted this event
        name - the event name
        args - arbitrary positional arguments with which to invoke listeners
        kwargs - arbitrary keyword arguments with which to invoke listeners
        track_dispatch - whether to enable await_dispatched() functionality
        """
        self.source = source
        self.name = name
        self.args = args
        self.kwargs = kwargs
        
        if _DEBUG_EVENTS:
            self._traceback = traceback.format_stack()
        else:
            self._traceback = None

        self._dispatched = None
        if track_dispatch:
            self._dispatched = threading.Event()
    
    def __repr__(self):
        return "Event(name='{}', source='{}')".format(self.name, self.source)

    def __str__(self):
        return repr(self)
    
    def await_dispatched(self):
        """Block until this Event is dispatched."""
        assert self._dispatched is not None
        self._dispatched.wait()

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
        """Enqueue an event to trigger all relevant listeners with arbitrary data."""
        self._event_queue.put(Event(source=self, name=event_name, args=args, kwargs=kwargs))
    
    def on(self, event_name):
        """listen() as a decorator.
        
        The wrapper function includes a .off() method which unlistens it.
        """
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
    
    def create_interval(self, *args, **kwargs):
        return Interval(*args, **kwargs, source=self)

class Interval:
    """Emits an event on a fixed interval."""

    def __init__(self, event_name, interval, *, queue=main_event_queue, source, await_dispatched=True, args=[], kwargs={}):
        """
        interval - the time in seconds between event emits
        queue - the queue to which the event will be enqueued
        source - the Observable that will emit the event
        await_dispatched - whether to wait for the emitted event to be dispatched before emitting another
        args - args data to pass to event
        kwargs - keyword args data to pass to event
        """
        self.event_name = event_name
        self.interval = interval
        self.queue = queue
        self.source = source
        self.args = args
        self.kwargs = kwargs
        self._await_dispatched = await_dispatched

        self._cancelled = False
        self._cancelled_lock = Lock()
    
    def _sleep(self, seconds):
        time.sleep(seconds)
    
    def _main(self):
        event = None
        while True:
            self._sleep(self.interval)
            if event and self._await_dispatched:
                event.await_dispatched()
            with self._cancelled_lock:
                if self._cancelled:
                    break
                event = Event(source=self.source, name=self.event_name, args=self.args, kwargs=self.kwargs, track_dispatch=self._await_dispatched)
                self.queue.put(event)

    def start(self):
        """Start emitting the event, first waiting for the specified time to elapse.
        
        Return self.
        """
        with self._cancelled_lock:
            if self._cancelled:
                raise RuntimeError("Interval cannot be started after cancellation")
            thread_name = "Interval emitter for '{}' from 0x{:X}".format(self.event_name, id(self.source))
            self._thread = threading.Thread(name=thread_name, target=self._main, daemon=True)
            self._thread.start()
            return self

    def cancel(self):
        """Stop emitting the event."""
        with self._cancelled_lock:
            self._cancelled = True

def dump_event_log(events, file=sys.stderr):
    """
    Format and print an iterable of Events and the traceback of the most recent one (if _DEBUG_EVENTS is True).
    """

    print("Event log (current event last):", file=file)
    
    events_list = list(events)
    event_name_size = max(len(e.name) for e in events_list)

    def print_event(event, last=False):
        event_name = event.name.ljust(event_name_size)
        event_args_items = [str(a) for a in event.args] + ["{}={}".format(str(k), str(v)) for k, v in event.kwargs.items()]
        event_args = "(" + ", ".join(event_args_items) + ")"
        print("*" if last else " ", event_name, event_args, file=file)

    # print log of recent events and arguments
    for event in events_list[:-1]:
        print_event(event)
    print_event(events_list[-1], last=True)
    print(file=file)
    
    # print call stack for most recent event
    if events_list[-1]._traceback is not None:
        print("Traceback of this event:", file=file)
        for line in events_list[-1]._traceback[:-2]: # slice off extraneous information
            print(line, end="", file=file)
    print(file=file)

def poll_events(queue=main_event_queue):
    """Immediately dispatch (invoke listeners for) all events in a queue."""
    try:
        while True:
            event = queue.get_nowait()
            _dispatch_event(event)
            queue.task_done()
    except Empty:
        pass

def join_event_queue(queue=main_event_queue):
    """Call join() on the queue to wait for event processing."""
    queue.join()

_is_polling = set()
_is_polling_lock = Lock()
def start_polling(queue=main_event_queue):
    """Create and start a daemon to continuously poll a queue.
    Will not start a new daemon if one already exists for the given queue.

    If a daemon was started, returns True.
    If a daemon already exists for the given queue, returns False.
    """
    with _is_polling_lock:
        if id(queue) in _is_polling:
            return False
        _is_polling.add(id(queue))
    
    def fn():
        history = deque(maxlen=_EVENT_HISTORY_LENGTH)
        while True:
            event = queue.get()
            history.append(event)
            try:
                _dispatch_event(event)
            except Exception as e:
                if _DEBUG_EVENTS:
                    dump_event_log(history)
                raise e
            queue.task_done()
    thread = Thread(name="Event loop for queue 0x{:X}".format(id(queue)), target=fn, daemon=True)
    thread.start()
    return True

def _dispatch_event(event):
    """Invoke all listeners with a given Event instance."""
    for listener in event.source._listeners[event.name]:
        listener(*event.args, **event.kwargs)
    if event._dispatched is not None:
        event._dispatched.set()
