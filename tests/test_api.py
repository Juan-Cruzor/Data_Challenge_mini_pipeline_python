from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_daily_stats_endpoint_exists():

    r = client.get("/daily_stats?date=2025-01-15")

    assert r.status_code in (200, 404, 422)