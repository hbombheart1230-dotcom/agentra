"""RF-045 C1/C2: legacy node callers use the real logger, not silent no-ops."""

from __future__ import annotations

from libs.core.event_logger import EventLogger
from libs.core.event_logger_compat import get_event_logger


def test_rf045_real_logger_node_start_end_write_temp_event_log(monkeypatch, tmp_path):
    path = tmp_path / "events.jsonl"
    monkeypatch.setenv("EVENT_LOG_PATH", str(path))

    logger = get_event_logger("assemble_decision_packet")
    logger.start({"order_api_id": "demo"})
    logger.end({"intent": "hold"})

    rows = EventLogger(log_path=path).read_all()
    if [row["event"] for row in rows] != ["start", "end"]:
        raise AssertionError(rows)
    if any(row["stage"] != "assemble_decision_packet" for row in rows):
        raise AssertionError(rows)
    if not path.is_file():
        raise AssertionError("real compatibility logger did not write its explicit temp log")
