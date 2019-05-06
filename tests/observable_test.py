from termpixels.observable import Observable
import pytest

def test_observable_listen_emit():
    o = Observable()
    def listener(data):
        raise Exception("fired")
    o.listen("test", listener)

    with pytest.raises(Exception, match="fired"):
        o.emit("test")

def test_observable_listen_multiple_events_emit():
    o = Observable()
    def listener_a(data):
        raise Exception("A")
    def listener_b(data):
        raise Exception("B")
    o.listen("A", listener_a)
    o.listen("B", listener_b)

    with pytest.raises(Exception, match="A"):
        o.emit("A")
    with pytest.raises(Exception, match="B"):
        o.emit("B")

def test_observable_listen_unlisten_emit():
    o = Observable()
    def listener(data):
        raise Exception("fired")
    o.listen("test", listener)

    with pytest.raises(Exception, match="fired"):
        o.emit("test")
    
    o.unlisten("test", listener)
    o.emit("test")

def test_observable_multiple_listeners_emit():
    o = Observable()
    events = set()
    def listener_a(data):
        events.add("A")
    def listener_b(data):
        events.add("B")
    o.listen("test", listener_a)
    o.listen("test", listener_b)
    o.emit("test")
    assert events == {"A", "B"}

def test_observable_emit_data():
    o = Observable()
    result = None
    def listener(data):
        nonlocal result
        result = data
    o.listen("test", listener)
    o.emit("test", 123)
    assert result == 123
