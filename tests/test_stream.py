from app.stream import stream_events
import json


def test_stream_reads_events(tmp_path):

    file = tmp_path / "events.json"

    json.dump([{"a": 1}, {"a": 2}], open(file, "w"))

    events = list(stream_events(file))

    assert len(events) == 2