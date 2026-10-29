"""RF-045 C1/C2: legacy node callers use the real logger, not silent no-ops."""

from __future__ import annotations

from libs.core.event_logger import EventLogger
from libs.core.event_logger_compat import get_event_logger
from graphs.nodes.assemble_decision_packet import assemble_decision_packet


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


def test_rf045_packet_node_uses_real_compat_logger_without_default_cwd_write(monkeypatch, tmp_path):
    """The safe packet consumer must retain its legacy start/end audit trail.

    This deliberately exercises the real consumer, while routing the logger to
    an explicit temporary file. It neither constructs an executor nor reaches
    any order/broker path.
    """
    path = tmp_path / "packet-events.jsonl"
    monkeypatch.setenv("EVENT_LOG_PATH", str(path))
    monkeypatch.chdir(tmp_path)

    result = assemble_decision_packet(
        {
            "intent": "hold",
            "order_api_id": "demo",
            "symbol": "005930",
            "risk_context": {},
            "exec_context": {},
        }
    )

    rows = EventLogger(log_path=path).read_all()
    if [row["event"] for row in rows] != ["start", "end"]:
        raise AssertionError(rows)
    if [row["stage"] for row in rows] != ["assemble_decision_packet"] * 2:
        raise AssertionError(rows)
    if result["decision_packet"]["intent"]["intent"] != "hold":
        raise AssertionError(result)
    if (tmp_path / "data" / "logs" / "events.jsonl").exists():
        raise AssertionError("consumer ignored explicit temporary event-log path")
