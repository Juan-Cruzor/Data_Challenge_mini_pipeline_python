
import json
import pytest
from datetime import datetime, timezone
from pathlib import Path
 
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
 
from app.stream import stream_events, _parse_ts
 
 
# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
 
@pytest.fixture
def tmp_json(tmp_path):
    """Return a helper that writes a list to a temp JSON array file."""
    def _write(events: list) -> str:
        p = tmp_path / "events.json"
        p.write_text(json.dumps(events))
        return str(p)
    return _write
 
 
@pytest.fixture
def tmp_ndjson(tmp_path):
    """Return a helper that writes events as NDJSON to a temp file."""
    def _write(lines: list[str]) -> str:
        p = tmp_path / "events.ndjson"
        p.write_text("\n".join(lines) + "\n")
        return str(p)
    return _write

class TestParseTs:
 
    def test_parses_utc_z_format(self):
        ts = _parse_ts("2025-01-15T10:00:00Z")
        assert ts == datetime(2025, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
 
    def test_parses_offset_format(self):
        ts = _parse_ts("2025-01-15T10:00:00+00:00")
        assert ts is not None
        assert ts.tzinfo is not None