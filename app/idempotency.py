import hashlib
import orjson
from psycopg2.extras import execute_values


def event_hash(event):
    """"Function that computes a hash on a sorted json.
        Retruns a hash of the event using orjson for consistent serialization."""
    return hashlib.md5(
        orjson.dumps(event, option=orjson.OPT_SORT_KEYS)
    ).hexdigest()


def is_new_event(cursor, event):
    """The function that checks if the event is new by trying to insert its hash into the database.
        It allows us to ensure idempotency by only processing events that have not been seen before.
        and allows deduplication.
            Returns[bool]: True if the event is new, False if it has been processed before."""
    h = event_hash(event)

    cursor.execute(
        """
        INSERT INTO processed_events(event_hash)
        VALUES(%s)
        ON CONFLICT DO NOTHING
        RETURNING event_hash
        """,
        (h,)
    )

    return cursor.fetchone() is not None


def filter_new_events(cursor, events):

    hashes = [(event_hash(e),) for e in events]

    execute_values(
        cursor,
        """
        INSERT INTO processed_events(event_hash)
        VALUES %s
        ON CONFLICT DO NOTHING
        RETURNING event_hash
        """,
        hashes
    )

    inserted = {row[0] for row in cursor.fetchall()}

    return [e for e in events if event_hash(e) in inserted]