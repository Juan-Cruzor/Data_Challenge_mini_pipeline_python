import pytest
from datetime import datetime
 
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
 
from app.validation import validate_event

 
 
# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------
 
@pytest.fixture
def valid_search():
    return {
        "event": "search",
        "user_id": "u001",
        "timestamp": "2025-12-01T10:00:00Z",
        "properties": {"origin": "GDL", "destination": "MTY", "date": "2025/12/31"},
    }
 
 
@pytest.fixture
def valid_purchase():
    return {
        "event": "purchase_complete",
        "user_id": "u001",
        "timestamp": "2025-12-01T10:05:00Z",
        "properties": {"amount": 1500, "payment_method": "Card", "phone": "+521331234567"},
    }
 
 
# ---------------------------------------------------------------------------
# validate_event — valid inputs
# ---------------------------------------------------------------------------
 
class TestValidateEventValid:
 
    def test_valid_search_returns_dict(self, valid_search):
        result = validate_event(valid_search)
        assert isinstance(result, dict)
 
    def test_valid_purchase_returns_dict(self, valid_purchase):
        result = validate_event(valid_purchase)
        assert isinstance(result, dict)
 
    def test_valid_search_event_field(self, valid_search):
        assert validate_event(valid_search)["event"] == "search"
 
    def test_valid_purchase_event_field(self, valid_purchase):
        assert validate_event(valid_purchase)["event"] == "purchase_complete"
 
    def test_timestamp_is_datetime_object(self, valid_search):
        result = validate_event(valid_search)
        assert isinstance(result["timestamp"], datetime)
 
    def test_user_id_preserved(self, valid_search):
        assert validate_event(valid_search)["user_id"] == "u001"
 
 
# ---------------------------------------------------------------------------
# validate_event — invalid inputs return None
# ---------------------------------------------------------------------------
 
class TestValidateEventInvalid:
 
    def test_null_user_id_returns_none(self, valid_search):
        valid_search["user_id"] = None
        assert validate_event(valid_search) is None
 
    def test_empty_user_id_returns_none(self, valid_search):
        valid_search["user_id"] = ""
        assert validate_event(valid_search) is None
 
    def test_whitespace_user_id_returns_none(self, valid_search):
        valid_search["user_id"] = "   "
        assert validate_event(valid_search) is None
 
    def test_invalid_timestamp_returns_none(self, valid_search):
        valid_search["timestamp"] = "NOT_A_DATE"
        assert validate_event(valid_search) is None
 
    def test_missing_timestamp_returns_none(self, valid_search):
        del valid_search["timestamp"]
        assert validate_event(valid_search) is None
 
    def test_unknown_event_type_returns_none(self, valid_search):
        valid_search["event"] = "click"
        assert validate_event(valid_search) is None
 
    def test_invalid_phone_returns_none(self, valid_purchase):
        valid_purchase["properties"]["phone"] = "not-a-phone"
        assert validate_event(valid_purchase) is None
 
    def test_short_phone_returns_none(self, valid_purchase):
        valid_purchase["properties"]["phone"] = "123"
        assert validate_event(valid_purchase) is None
 
    def test_empty_dict_returns_none(self):
        assert validate_event({}) is None