from app.stream import stream_events
from app.validation import validate_event
from app.idempotency import is_new_event
from app.aggregate import init_metrics, update_metrics, flush_metrics
from app.write_parquet import write_parquet
from app.data_warehouse import insert_metrics
from app.db import get_conn


def run_pipeline(path):

    conn=get_conn()
    cursor=conn.cursor()

    metrics=init_metrics()

    parquet_buffer=[]
    # stream_events function from the stream module.
    for raw in stream_events(path):

        # Normalization is done in the validate_event functio from the validation modulen.
        event=validate_event(raw)
        # Skips the event if it's not valid.
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