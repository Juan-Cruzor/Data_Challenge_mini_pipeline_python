from app.stream import stream_events
from app.validation import validate_event
from app.idempotency import is_new_event, mark_event_processed
from app.aggregate import init_metrics, update_metrics, flush_metrics
from app.write_parquet import write_parquet
from app.write_csv import write_csv, reset_csv
from app.data_warehouse import insert_metrics
from app.watermark import get_watermark, set_watermark
from app.db import get_conn
from app.logger import logger

BATCH_SIZE = 10_000


def run_pipeline(path):
    conn = get_conn()
    cursor = conn.cursor()

    # Start the CSV fresh so re-running the pipeline doesn't duplicate rows.
    reset_csv()

    try:
        # Incremental processing
        watermark = get_watermark(cursor)

        if watermark:
            logger.info(f"Resuming from watermark: {watermark.isoformat()}")
        else:
            logger.info("No watermark found — processing all events.")

        metrics = init_metrics()
        parquet_buffer = []
        processed = 0
        skipped = 0
        latest_ts = watermark  # will be advanced as we see newer events

        for raw in stream_events(path, after_ts=watermark):

            # Validate and normalize via Pydantic — returns None if invalid.
            event = validate_event(raw)
            if not event:
                skipped += 1
                continue

            # Secondary idempotency guard: catches out-of-order events that
            # share a timestamp right at the watermark boundary.
            if not is_new_event(cursor, event):
                skipped += 1
                continue

            # Mark as processed inside the same transaction so it rolls back
            # together with the metrics insert on failure.
            mark_event_processed(cursor, event)

            parquet_buffer.append(event)
            update_metrics(metrics, event)
            processed += 1

            # Advance the high-water mark.
            event_ts = event["timestamp"]
            if latest_ts is None or event_ts > latest_ts:
                latest_ts = event_ts

            # Flush parquet in batches to keep memory usage bounded.
            if len(parquet_buffer) >= BATCH_SIZE:
                write_parquet(parquet_buffer)
                parquet_buffer.clear()

            # Flush metrics to DB + CSV and commit in batches so that a
            # mid-run crash doesn't lose all progress.
            if len(metrics) >= BATCH_SIZE:
                rows = flush_metrics(metrics)
                insert_metrics(cursor, rows)
                write_csv(rows)
                conn.commit()
                logger.info(f"Committed batch of {len(rows)} metric rows.")

        # Final flush
        if parquet_buffer:
            write_parquet(parquet_buffer)

        rows = flush_metrics(metrics)
        insert_metrics(cursor, rows)
        write_csv(rows)

        # Advance the watermark only after all data is safely written.
        # If we crash before this point the next run re-processes this batch;
        # the idempotency check prevents any duplicates from being written.
        if latest_ts is not None and latest_ts != watermark:
            set_watermark(cursor, latest_ts)
            logger.info(f"Watermark advanced to: {latest_ts.isoformat()}")

        conn.commit()

        logger.info(
            f"Pipeline complete — processed: {processed}, "
            f"skipped/invalid: {skipped}, metric rows: {len(rows)}."
        )

    except Exception as e:
        conn.rollback()
        logger.error(f"Pipeline failed, transaction rolled back: {e}")
        raise

    finally:
        cursor.close()
        conn.close()
