from app.validation import validate_event


def test_invalid_event_returns_none():

    e = {
        "event": "search",
        "user_id": None,
        "timestamp": "2025-01-15T10:01:00Z",
        "properties": {}
    }

    assert validate_event(e) is None


def test_valid_event_passes():

    e = {
        "event": "search",
        "user_id": "123",
        "timestamp": "2025-01-15T10:01:00Z",
        "properties": {}
    }

    assert validate_event(e) is not None