from app.validation import validate_event
import pytest

def test_invalid_event():
    """"""
    event = {
        "event":"search",
        "user_id":None,
        "timestamp":"2025-01-15T10:00:00Z"
    }

    assert validate_event(event) == False


def test_valid_event():
    """"""
    event = {
        "event":"search",
        "user_id":"123",
        "timestamp":"2025-01-15T10:00:00Z"
    }

    assert validate_event(event) == True