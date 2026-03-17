from datetime import datetime, timezone


def get_watermark(cursor):
    """
    Return the timestamp of the last successfully processed event,
    or None if the pipeline has never run before.
    """
    cursor.execute("SELECT last_ts FROM pipeline_watermark WHERE id = 1")
    row = cursor.fetchone()
    if row is None:
        return None
    ts = row[0]
    # Ensure tz-aware so comparisons with event timestamps are always safe.
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts


def set_watermark(cursor, ts):
    """
    Upsert the watermark to `ts`.

    Works on both first run (INSERT) and subsequent runs (UPDATE via
    ON CONFLICT), so no special-casing is needed in the pipeline.
    """
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)

    cursor.execute(
        """
        INSERT INTO pipeline_watermark (id, last_ts)
        VALUES (1, %s)
        ON CONFLICT (id) DO UPDATE SET last_ts = EXCLUDED.last_ts
        """,
        (ts,),
    )
