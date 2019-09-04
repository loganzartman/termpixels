from termpixels.observable import Observable, poll_events
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
