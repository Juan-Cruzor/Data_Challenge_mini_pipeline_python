import json
import hashlib
from collections import defaultdict
from psycopg2.extras import execute_values

from app.validation import validate_event, normalize_event
from app.db import get_conn
from app.logger import logger


# Buffer to avoid bottleneck on inserting events in processed events table
HASH_BATCH_SIZE = 5000
event_hash_buffer = []


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

        event_hash_buffer.append((h,))

        if len(event_hash_buffer) >= HASH_BATCH_SIZE:

            execute_values(
                cursor,
                """
                INSERT INTO processed_events (event_hash)
                VALUES %s
                ON CONFLICT DO NOTHING
                """,
                event_hash_buffer
            )

            event_hash_buffer.clear()

        valid_events.append(event)

    # Flushing
    if event_hash_buffer:

        execute_values(
            cursor,
            """
            INSERT INTO processed_events (event_hash)
            VALUES %s
            ON CONFLICT DO NOTHING
            """,
            event_hash_buffer
        )
        event_hash_buffer.clear()

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
    # Making sure that it has the actual computed metrics.
    execute_values(
        cursor,
        """
        INSERT INTO daily_user_stats
        (date,user_id,searches,purchases,total_purchased_amount)
        VALUES %s
        ON CONFLICT (date,user_id)
        DO UPDATE SET
            searches = EXCLUDED.searches,
            purchases = EXCLUDED.purchases,
            total_purchased_amount = EXCLUDED.total_purchased_amount
        """,
    rows)

    conn.commit()


from app.stream import stream_events
from app.validation import validate_event
from app.idempotency import is_new_event
from app.aggregate import init_metrics, update_metrics, flush_metrics
from app.storage.parquet_writer import write_parquet
from app.storage.warehouse_writer import insert_metrics
from app.db import get_conn


def run_pipeline(path):

    conn=get_conn()
    cursor=conn.cursor()

    metrics=init_metrics()

    parquet_buffer=[]

    for raw in stream_events(path):

        event=validate_event(raw)

        if not event:
            continue

        if not is_new_event(cursor,event):
            continue

        parquet_buffer.append(event)

        update_metrics(metrics,event)

        if len(parquet_buffer)>=10000:

            write_parquet(parquet_buffer)

            parquet_buffer.clear()

        if len(metrics)>=10000:

            rows=flush_metrics(metrics)

            insert_metrics(cursor,rows)

    write_parquet(parquet_buffer)

    rows=flush_metrics(metrics)

    insert_metrics(cursor,rows)

    conn.commit()