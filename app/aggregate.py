from collections import defaultdict


def init_metrics():

    return defaultdict(lambda: {
        "searches": 0,
        "purchases": 0,
        "amount": 0
    })


def update_metrics(metrics, event):

    date = event["timestamp"].date()
    user = event["user_id"]

    key = (date, user)

    if event["event"] == "search":

        metrics[key]["searches"] += 1

    elif event["event"] == "purchase_complete":

        metrics[key]["purchases"] += 1
        metrics[key]["amount"] += event["properties"]["amount"]


def flush_metrics(metrics):

    rows = []

    for (date, user), m in metrics.items():

        rows.append(
            (
                date,
                user,
                m["searches"],
                m["purchases"],
                m["amount"]
            )
        )

    metrics.clear()

    return rows