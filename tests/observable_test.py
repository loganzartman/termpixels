from termpixels.observable import Observable, poll_events, Event
import threading
import pytest

def test_observable_listen_emit():
    o = Observable()
    def listener():
        raise Exception("fired")
    o.listen("test", listener)

    with pytest.raises(Exception, match="fired"):
        o.emit("test")
        poll_events()

def test_observable_listen_multiple_events_emit():
    o = Observable()
    def listener_a():
        raise Exception("A")
    def listener_b():
        raise Exception("B")
    o.listen("A", listener_a)
    o.listen("B", listener_b)

    with pytest.raises(Exception, match="A"):
        o.emit("A")
        poll_events()
    with pytest.raises(Exception, match="B"):
        o.emit("B")
        poll_events()

def test_observable_listen_unlisten_emit():
    o = Observable()
    def listener():
        raise Exception("fired")
    o.listen("test", listener)

    with pytest.raises(Exception, match="fired"):
        o.emit("test")
        poll_events()
    
    o.unlisten("test", listener)
    o.emit("test")
    poll_events()

def test_observable_multiple_listeners_emit():
    o = Observable()
    events = set()
    def listener_a():
        events.add("A")
    def listener_b():
        events.add("B")
    o.listen("test", listener_a)
    o.listen("test", listener_b)
    o.emit("test")
    poll_events()
    assert events == {"A", "B"}

def test_observable_emit_data():
    o = Observable()
    result = None
    def listener(data):
        nonlocal result
        result = data
    o.listen("test", listener)
    o.emit("test", 123)
    poll_events()
    assert result == 123

def test_observable_emit_kwargs():
    o = Observable()
    result = None
    def listener(a, b):
        nonlocal result
        result = b
    o.listen("test", listener)
    o.emit("test", a=1, b=2)
    poll_events()
    assert result == 2

def test_observable_on():
    o = Observable()
    result = None

    @o.on("test")
    def listener(data):
        nonlocal result
        result = data
    
    o.emit("test", 1)
    poll_events()
    assert result == 1

    listener.off()
    o.emit("test", 2)
    assert result == 1

def test_observable_propagate_event():
    a = Observable()
    b = Observable()

    b.propagate_event(a, "test")

    result = None
    def listener(data):
        nonlocal result
        result = data
    b.listen("test", listener)

    a.emit("test", 123)
    poll_events()
    assert result == 123

def test_observable_event_ordering():
    # events should be dispatched in the order they are emitted
    o = Observable()
    
    A_fired = False
    B_fired = False
    C_fired = False

    @o.on("A")
    def on_A():
        nonlocal A_fired
        assert not B_fired
        assert not C_fired
        A_fired = True

    @o.on("B")
    def on_B():
        nonlocal B_fired
        assert A_fired
        assert not C_fired
        B_fired = True
    
    @o.on("C")
    def on_C():
        nonlocal C_fired
        assert A_fired
        assert B_fired
        C_fired = True
    
    o.emit("A")
    o.emit("B")
    o.emit("C")
    poll_events()
    assert A_fired and B_fired and C_fired

def test_observable_track_dispatch():
    o = Observable()
    
    event = Event(source=o, name="test", track_dispatch=True)
    o._event_queue.put(event)

    assert not event._dispatched.is_set()
    poll_events()
    assert event._dispatched.is_set()

def test_observable_event_await_dispatched():
    o = Observable()
    
    event = Event(source=o, name="test", track_dispatch=True)
    o._event_queue.put(event)

    done = False
    def awaiter():
        nonlocal done
        event.await_dispatched()
        done = True

    t = threading.Thread(target=awaiter)
    t.start()

    assert not done
    poll_events()
    t.join(timeout=0.5)
    assert done
