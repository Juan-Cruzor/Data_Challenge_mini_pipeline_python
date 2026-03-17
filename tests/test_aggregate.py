import pytest
from collections import defaultdict
from datetime import date, datetime, timezone
 
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
 
from app.aggregate import init_metrics, update_metrics
 
 
# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
 
@pytest.fixture
def metrics():
    """Fresh accumulator for each test."""
    return init_metrics()
 
 
def make_event(event_type: str, user_id: str, ts: str, amount: float = 0) -> dict:
    """Build a validated-style event dict."""
    return {
        "event": event_type,
        "user_id": user_id,
        "timestamp": datetime.fromisoformat(ts.replace("Z", "+00:00")),
        "properties": {"amount": amount},
    }
 
 
# ---------------------------------------------------------------------------
# init_metrics
# ---------------------------------------------------------------------------
 
class TestInitMetrics:
 
    def test_returns_defaultdict(self, metrics):
        assert isinstance(metrics, defaultdict)
 
    def test_missing_key_returns_zero_counts(self, metrics):
        val = metrics[("any_date", "any_user")]
        assert val["searches"] == 0
        assert val["purchases"] == 0
        assert val["amount"] == 0
 
    def test_independent_instances(self):
        m1 = init_metrics()
        m2 = init_metrics()
        m1[("2025-01-15", "u1")]["searches"] = 99
        assert m2[("2025-01-15", "u1")]["searches"] == 0
 
 
# ---------------------------------------------------------------------------
# update_metrics — search events
# ---------------------------------------------------------------------------
 
class TestUpdateMetricsSearch:
 
    def test_increments_searches_by_one(self, metrics):
        ev = make_event("search", "u1", "2025-01-15T08:00:00Z")
        update_metrics(metrics, ev)
        assert metrics[(date(2025, 1, 15), "u1")]["searches"] == 1
 
    def test_does_not_increment_purchases(self, metrics):
        ev = make_event("search", "u1", "2025-01-15T08:00:00Z")
        update_metrics(metrics, ev)
        assert metrics[(date(2025, 1, 15), "u1")]["purchases"] == 0
 
    def test_does_not_increment_amount(self, metrics):
        ev = make_event("search", "u1", "2025-01-15T08:00:00Z")
        update_metrics(metrics, ev)
        assert metrics[(date(2025, 1, 15), "u1")]["amount"] == 0
 
    def test_accumulates_multiple_searches(self, metrics):
        for ts in ["2025-01-15T08:00:00Z", "2025-01-15T09:00:00Z", "2025-01-15T10:00:00Z"]:
            update_metrics(metrics, make_event("search", "u1", ts))
        assert metrics[(date(2025, 1, 15), "u1")]["searches"] == 3
 
    def test_key_uses_date_not_datetime(self, metrics):
        update_metrics(metrics, make_event("search", "u1", "2025-01-15T23:59:59Z"))
        assert (date(2025, 1, 15), "u1") in metrics
 
 
# ---------------------------------------------------------------------------
# update_metrics — purchase events
# ---------------------------------------------------------------------------
 
class TestUpdateMetricsPurchase:
 
    def test_increments_purchases_by_one(self, metrics):
        ev = make_event("purchase_complete", "u1", "2025-01-15T10:00:00Z", amount=1500)
        update_metrics(metrics, ev)
        assert metrics[(date(2025, 1, 15), "u1")]["purchases"] == 1
 
    def test_adds_amount(self, metrics):
        ev = make_event("purchase_complete", "u1", "2025-01-15T10:00:00Z", amount=1500)
        update_metrics(metrics, ev)
        assert metrics[(date(2025, 1, 15), "u1")]["amount"] == 1500
 
    def test_accumulates_multiple_purchases(self, metrics):
        update_metrics(metrics, make_event("purchase_complete", "u1", "2025-01-15T10:00:00Z", amount=500))
        update_metrics(metrics, make_event("purchase_complete", "u1", "2025-01-15T11:00:00Z", amount=300))
        key = (date(2025, 1, 15), "u1")
        assert metrics[key]["purchases"] == 2
        assert metrics[key]["amount"] == 800
 
    def test_does_not_increment_searches(self, metrics):
        ev = make_event("purchase_complete", "u1", "2025-01-15T10:00:00Z", amount=1500)
        update_metrics(metrics, ev)
        assert metrics[(date(2025, 1, 15), "u1")]["searches"] == 0
 
    def test_zero_amount_purchase(self, metrics):
        ev = make_event("purchase_complete", "u1", "2025-01-15T10:00:00Z", amount=0)
        update_metrics(metrics, ev)
        assert metrics[(date(2025, 1, 15), "u1")]["purchases"] == 1
        assert metrics[(date(2025, 1, 15), "u1")]["amount"] == 0
 