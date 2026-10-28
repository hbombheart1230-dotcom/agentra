"""RF-045 C2/C3: legacy no-arg logger remains usable when node assignment fails."""

from __future__ import annotations

from libs.core.event_logger_compat import get_event_logger


def test_rf045_compat_returns_noarg_logger_when_node_attribute_is_locked(monkeypatch):
    class _LockedNoArgLogger:
        def __setattr__(self, _name, _value):
            raise TypeError("fake immutable logger")

    monkeypatch.setattr("libs.core.event_logger.EventLogger", _LockedNoArgLogger)

    logger = get_event_logger("decision-trace")

    assert isinstance(logger, _LockedNoArgLogger)
    assert not hasattr(logger, "node")
