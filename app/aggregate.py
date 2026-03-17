from collections import defaultdict


def init_metrics():
    """Return a fresh accumulator"""
    return defaultdict(lambda: {"searches": 0, "purchases": 0, "amount": 0})


def update_metrics(metrics: defaultdict, event: dict):
    """Increment the counters for the event's key."""
    key = (event["timestamp"].date(), event["user_id"])

    if event["event"] == "search":
        metrics[key]["searches"] += 1

    elif event["event"] == "purchase_complete":
        metrics[key]["purchases"] += 1
        metrics[key]["amount"] += event["properties"]["amount"]


def flush_metrics(metrics: defaultdict):
    """
    Drain the accumulator and return rows ready for DB insertion.

    Each row is a tuple of:
        (date, user_id, searches, purchases, total_purchased_amount)
    """
    rows = [
        (date, user, m["searches"], m["purchases"], m["amount"])
        for (date, user), m in metrics.items()
    ]
    metrics.clear()
    return rows