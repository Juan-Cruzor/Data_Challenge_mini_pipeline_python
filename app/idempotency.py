from app.logger import logger


def is_new_event(cursor, event):
    """
    Return True if this event has NOT been processed before.

    Keyed on (event_type, user_id, timestamp) — a natural composite key
    since the source data has no explicit event ID field.

    Reuses the already-open cursor from the pipeline to avoid opening
    a new DB connection per event.

    Note: stream_events already skips events at or before the watermark,
    so in theory this check only fires for out-of-order events near the
    watermark boundary.
    """
    cursor.execute(
        """
        SELECT 1 FROM processed_events
        WHERE event_type = %s
          AND user_id    = %s
          AND ts         = %s
        LIMIT 1
        """,
        (event["event"], event["user_id"], event["timestamp"]),
    )
    exists = cursor.fetchone() is not None

    if exists:
        logger.debug(
            f"Skipping duplicate: event={event['event']} "
            f"user={event['user_id']} ts={event['timestamp']}"
        )

    return not exists


def mark_event_processed(cursor, event):
    """
    Record that an event has been processed.

    Called inside the same transaction as the metrics insert so both
    roll back together if something goes wrong.

        Args:
            cursor: The database cursor to execute the query.
            event[dict]: The event to be marked as processed.
    """
    cursor.execute(
        """
        INSERT INTO processed_events (event_type, user_id, ts)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        (event["event"], event["user_id"], event["timestamp"]),
    )