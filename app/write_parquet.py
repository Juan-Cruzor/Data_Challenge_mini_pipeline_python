import os
import uuid
from datetime import datetime

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

BASE_PATH = "./data/events"


def write_parquet(events: list[dict]) -> None:
    """
    Persist a batch of events to date-partitioned Parquet files.

    Each call writes a new file with a UUID name so that multiple pipeline
    runs — or multiple batch flushes on the same date — never overwrite
    each other.

    Partition layout:
        ./data/events/date=2025-01-15/part-<uuid>.parquet
    """
    if not events:
        return

    # Strip tzinfo: Arrow's from_pylist doesn't handle tz-aware datetimes well.
    normalized = []
    for e in events:
        row = dict(e)
        ts = row.get("timestamp")
        if isinstance(ts, datetime) and ts.tzinfo is not None:
            row["timestamp"] = ts.replace(tzinfo=None)
        normalized.append(row)

    table = pa.Table.from_pylist(normalized)

    dates = {
        e["timestamp"].date() if isinstance(e["timestamp"], datetime) else e["timestamp"]
        for e in events
    }

    for date in dates:
        folder = f"{BASE_PATH}/date={date}"
        os.makedirs(folder, exist_ok=True)

        mask = pc.equal(
            table["timestamp"].cast(pa.date32()),
            pa.scalar(date),
        )

        pq.write_table(table.filter(mask), f"{folder}/part-{uuid.uuid4().hex}.parquet")