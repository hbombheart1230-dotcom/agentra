from __future__ import annotations

from libs.core.event_logger import EventLogger
from libs.core.event_logger_compat import get_event_logger


def test_node_bridge_normalizes_non_mapping_payloads_and_keeps_instance_run_ids(monkeypatch, tmp_path):
    path = tmp_path / "events.jsonl"
    monkeypatch.setenv("EVENT_LOG_PATH", str(path))
    first = get_event_logger("node")
    second = get_event_logger("node")
    first.start([1])
    first.end("bad")
    second.start()
    second.end()
    rows = EventLogger(path).read_all()
    if [row["event"] for row in rows] != ["start", "end", "start", "end"]:
        raise AssertionError(rows)
    if any(row["payload"] != {} for row in rows):
        raise AssertionError(rows)
    if rows[0]["run_id"] != rows[1]["run_id"] or rows[2]["run_id"] != rows[3]["run_id"]:
        raise AssertionError(rows)
    if rows[0]["run_id"] == rows[2]["run_id"] or any(row["stage"] != "node" for row in rows):
        raise AssertionError(rows)
