import json
from datetime import datetime, timezone
from typing import Generator, Optional


def stream_events(path, after_ts):
    """
    Lazily yield events one at a time from a JSON file.

    Supports two formats:
      - JSON array:  [ {...}, {...}, ... ]
      - NDJSON:      {...}\n{...}\n...

    Incremental processing:
      If `after_ts` is provided (the watermark from the previous run), any
      event whose timestamp is at or before that value is skipped. This means
      each pipeline run only sees events that arrived after the last successful
      one — we never re-process already-committed data.

      Events exactly at the watermark are also skipped (<=) because they were
      included in the previous run's commit.

    The per-event idempotency check in idempotency.py still runs as a safety
    net for out-of-order events that slip past the watermark boundary.
    """
    for raw in _iter_file(path):
        if after_ts is not None:
            ts = _parse_ts(raw.get("timestamp", ""))
            if ts is not None and ts <= after_ts:
                continue
        yield raw


def _iter_file(path):
    """Low-level file iterator — handles JSON array and NDJSON.
            Args:
                path (str): The path to the JSON file."""
    
    with open(path, "r") as f:
        first = f.read(1)
        f.seek(0)

        if first == "[":
            for event in json.load(f):
                yield event
        else:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line.endswith(","):
                    line = line[:-1]
                yield json.loads(line)


def _parse_ts(value):
    """Parse an ISO 8601 string into a timezone-aware datetime, or None on failure."""
    try:
        ts = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return ts
    except (ValueError, TypeError):
        return None