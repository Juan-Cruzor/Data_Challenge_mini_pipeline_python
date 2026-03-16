import json
import hashlib
from collections import defaultdict

from app.validation import validate_event, normalize_event
from app.db import get_conn
from app.logger import logger


def event_hash(event):
    return hashlib.md5(json.dumps(event, sort_keys=True).encode()).hexdigest()


def process_events(path):
    """Function that processes the events by validating them, normalizing them."""

    conn = get_conn()
    cursor = conn.cursor()

    with open(path) as f:
        events = json.load(f)

    valid_events = []

    for event in events:

        if not validate_event(event):
            continue

        event = normalize_event(event)

        h = event_hash(event)

        cursor.execute("""
        INSERT INTO processed_events(event_hash)
        VALUES (%s)ON CONFLICT DO NOTHING
        RETURNING event_hash
        """,(h,))

        if cursor.fetchone() is None:
            continue

        cursor.execute(
            "INSERT INTO processed_events VALUES (%s)",
            (h,)
        )

        valid_events.append(event)

    metrics = defaultdict(lambda:{
        "searches":0,
        "purchases":0,
        "amount":0
    })

    for e in valid_events:

        date = e["timestamp"][:10]
        user = e["user_id"]

        key = (date,user)

        if e["event"] == "search":
            metrics[key]["searches"] += 1

        if e["event"] == "purchase_complete":
            metrics[key]["purchases"] += 1
            metrics[key]["amount"] += e["properties"].get("amount",0)

    for (date, user), m in metrics.items():

        cursor.execute("""
        INSERT INTO daily_user_stats
        VALUES (%s,%s,%s,%s,%s)
        ON CONFLICT (date,user_id)
        DO UPDATE SET
        searches = daily_user_stats.searches + EXCLUDED.searches,
        purchases = daily_user_stats.purchases + EXCLUDED.purchases,
        total_purchased_amount =
        daily_user_stats.total_purchased_amount +
        EXCLUDED.total_purchased_amount
        """, (date,user, m["searches"], m["purchases"], m["amount"]))

    conn.commit()

    logger.info(f"Processed events file $s)", path)