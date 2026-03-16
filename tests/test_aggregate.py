from datetime import datetime
from app.aggregate import init_metrics, update_metrics


def test_search_metric_increment():

    metrics = init_metrics()

    e = {
        "event": "search",
        "user_id": "u1",
        "timestamp": datetime.utcnow(),
        "properties": {}
    }

    update_metrics(metrics, e)

    row = list(metrics.values())[0]

    assert row["searches"] == 1