from app.stream import stream_events
from app.validation import validate_event
from app.idempotency import filter_new_events
from app.aggregate import init_metrics, update_metrics, flush_metrics
from app.write_parquet import write_parquet
from app.data_warehouse import insert_metrics
from app.db import get_conn


BATCH_SIZE = 10000
COMMIT_INTERVAL = 50000


def run_pipeline(path):

    conn = get_conn()
    cursor = conn.cursor()

    metrics = init_metrics()

    parquet_buffer = []
    batch = []

    processed_since_commit = 0

    # stream_events function from the stream module.
    for raw in stream_events(path):

        # Normalization is done in the validate_event functio from the validation modulen.
        event = validate_event(raw)
        # Skips the event if it's not valid.
        if not event:
            continue

        batch.append(event)

        if len(batch) >= BATCH_SIZE:

            new_events = filter_new_events(cursor, batch)

            for e in new_events:
                parquet_buffer.append(e)
                update_metrics(metrics, e)

            write_parquet(parquet_buffer)
            parquet_buffer.clear()

            rows = flush_metrics(metrics)
            insert_metrics(cursor, rows)

            processed_since_commit += len(batch)
            batch.clear()

            if processed_since_commit >= COMMIT_INTERVAL:
                conn.commit()
                processed_since_commit = 0

    if batch:

        new_events = filter_new_events(cursor, batch)

        for e in new_events:
            parquet_buffer.append(e)
            update_metrics(metrics, e)

    write_parquet(parquet_buffer)

    rows = flush_metrics(metrics)
    insert_metrics(cursor, rows)

    conn.commit()

    cursor.close()
    conn.close()