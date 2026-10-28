"""RF-045 C2/C3: event logger compatibility stays fake and preserves node state."""

from __future__ import annotations

from libs.core.event_logger_compat import get_event_logger


def test_rf045_compat_prefers_keyword_node_constructor(monkeypatch):
    class _KeywordLogger:
        def __init__(self, *, node):
            self.node = node

    monkeypatch.setattr("libs.core.event_logger.EventLogger", _KeywordLogger)

    logger = get_event_logger("decision-trace")

    assert isinstance(logger, _KeywordLogger)
    assert logger.node == "decision-trace"


def test_rf045_compat_falls_back_to_positional_name(monkeypatch):
    class _PositionalLogger:
        def __init__(self, name):
            self.name = name

    monkeypatch.setattr("libs.core.event_logger.EventLogger", _PositionalLogger)

    logger = get_event_logger("decision-trace")

    assert isinstance(logger, _PositionalLogger)
    assert logger.name == "decision-trace"


def test_rf045_compat_sets_node_after_noarg_fallback(monkeypatch):
    class _NoArgLogger:
        pass

    monkeypatch.setattr("libs.core.event_logger.EventLogger", _NoArgLogger)

    logger = get_event_logger("decision-trace")

    assert isinstance(logger, _NoArgLogger)
    assert logger.node == "decision-trace"
