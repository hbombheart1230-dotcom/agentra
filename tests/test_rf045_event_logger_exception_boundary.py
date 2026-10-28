"""RF-045 C2/C3: EventLogger writes only a temp path and exposes fsync failure."""

from __future__ import annotations

import os

import pytest

from libs.core.event_logger import EventLogger


def test_rf045_temp_event_log_propagates_fsync_failure(monkeypatch, tmp_path):
    """The append is temp-isolated; a durability failure is not silently swallowed."""
    log_path = tmp_path / "events.jsonl"
    logger = EventLogger(log_path)

    def fail_fsync(_fd: int) -> None:
        raise OSError("rf045 fake fsync failure")

    monkeypatch.setattr(os, "fsync", fail_fsync)
    with pytest.raises(OSError, match="rf045 fake fsync failure"):
        logger.log(run_id="rf045", stage="test", event="durability", payload={"tmp": True})

    assert log_path.exists()
    assert "rf045" in log_path.read_text(encoding="utf-8")
