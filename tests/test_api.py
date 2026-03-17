import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
 
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
 
from app.main import app
 
client = TestClient(app)
 
 
# ---------------------------------------------------------------------------
# Helpers — build mock DB connections
# ---------------------------------------------------------------------------
 
def mock_conn(fetchone=None, fetchall=None):
    """
    Return a mock connection whose cursor returns the given values.
    Supports the `with conn.cursor() as cursor:` context manager pattern.
    """
    cursor = MagicMock()
    cursor.fetchone.return_value = fetchone
    cursor.fetchall.return_value = fetchall if fetchall is not None else []
 
    conn = MagicMock()
    conn.cursor.return_value.__enter__ = MagicMock(return_value=cursor)
    conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    return conn
 
 
# A realistic DB row for /daily_stats
STATS_ROW = ("2025-12-01", 3, 6, 4, 11600.0)
 
# ---------------------------------------------------------------------------
# GET /daily_stats
# ---------------------------------------------------------------------------
 
class TestDailyStats:
 
    def test_returns_200_when_data_found(self):
        with patch("app.main.get_conn", return_value=mock_conn(fetchone=STATS_ROW)):
            response = client.get("/daily_stats?date=2025-12-01")
        assert response.status_code == 200
 
    def test_response_shape(self):
        with patch("app.main.get_conn", return_value=mock_conn(fetchone=STATS_ROW)):
            data = client.get("/daily_stats?date=2025-12-01").json()
        assert set(data.keys()) == {"date", "total_users", "total_searches",
                                     "total_purchases", "total_purchased_amount"}
 
    def test_response_values(self):
        with patch("app.main.get_conn", return_value=mock_conn(fetchone=STATS_ROW)):
            data = client.get("/daily_stats?date=2025-12-01").json()
        assert data["date"] == "2025-12-01"
        assert data["total_users"] == 3
        assert data["total_searches"] == 6
        assert data["total_purchases"] == 4
        assert data["total_purchased_amount"] == 11600.0
 
    def test_total_purchased_amount_is_float(self):
        with patch("app.main.get_conn", return_value=mock_conn(fetchone=STATS_ROW)):
            data = client.get("/daily_stats?date=2025-12-01").json()
        assert isinstance(data["total_purchased_amount"], float)
 
    def test_returns_404_when_no_data(self):
        with patch("app.main.get_conn", return_value=mock_conn(fetchone=None)):
            response = client.get("/daily_stats?date=2025-12-01")
        assert response.status_code == 404
 
    def test_404_detail_mentions_date(self):
        with patch("app.main.get_conn", return_value=mock_conn(fetchone=None)):
            data = client.get("/daily_stats?date=2025-12-01").json()
        assert "2025-12-01" in data["detail"]
 
    def test_missing_date_param_returns_422(self):
        response = client.get("/daily_stats")
        assert response.status_code == 422
 
    def test_db_error_returns_500(self):
        conn = MagicMock()
        conn.cursor.return_value.__enter__ = MagicMock(side_effect=Exception("DB down"))
        conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        with patch("app.main.get_conn", return_value=conn):
            response = client.get("/daily_stats?date=2025-12-01")
        assert response.status_code == 500
 
    def test_connection_closed_on_success(self):
        conn = mock_conn(fetchone=STATS_ROW)
        with patch("app.main.get_conn", return_value=conn):
            client.get("/daily_stats?date=2025-12-01")
        conn.close.assert_called_once()
 
    def test_connection_closed_on_404(self):
        conn = mock_conn(fetchone=None)
        with patch("app.main.get_conn", return_value=conn):
            client.get("/daily_stats?date=2025-12-01")
        conn.close.assert_called_once()
 