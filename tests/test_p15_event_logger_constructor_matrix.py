"""RF-045: exact legacy logger constructor selection and isolated JSONL writes."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from libs.core import event_logger
from libs.core.event_logger_compat import get_event_logger


def test_keyword_only_node_constructor_keeps_original_instance(monkeypatch: pytest.MonkeyPatch) -> None:
    class KeywordOnly:
        def __init__(self, *, node: str) -> None:
            self.node = node

        def start(self, payload=None) -> str:
            return f"start:{self.node}"

    monkeypatch.setattr(event_logger, "EventLogger", KeywordOnly)
    instance = get_event_logger("scanner")
    assert isinstance(instance, KeywordOnly)
    assert instance.node == "scanner"
    assert instance.start() == "start:scanner"


def test_positional_name_constructor_keeps_original_instance(monkeypatch: pytest.MonkeyPatch) -> None:
    class PositionalName:
        def __init__(self, name: str, /) -> None:
            self.node = name

    monkeypatch.setattr(event_logger, "EventLogger", PositionalName)
    instance = get_event_logger("monitor")
    assert isinstance(instance, PositionalName)
    assert instance.node == "monitor"


def test_no_arg_constructor_receives_node(monkeypatch: pytest.MonkeyPatch) -> None:
    class NoArguments:
        def __init__(self) -> None:
            self.created = True

    monkeypatch.setattr(event_logger, "EventLogger", NoArguments)
    instance = get_event_logger("commander")
    assert isinstance(instance, NoArguments)
    assert instance.created
    assert instance.node == "commander"


def test_unexpected_constructor_failure_is_not_masked(monkeypatch: pytest.MonkeyPatch) -> None:
    class BadConstructor:
        def __init__(self, *, node: str) -> None:
            raise ValueError("real constructor failure")

    monkeypatch.setattr(event_logger, "EventLogger", BadConstructor)
    with pytest.raises(ValueError, match="real constructor failure"):
        get_event_logger("scanner")


def test_real_dataclass_jsonl_run_ids_and_nondict_payload(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path = tmp_path / "events" / "events.jsonl"
    monkeypatch.setenv("EVENT_LOG_PATH", str(path))
    # The genuine EventLogger dataclass takes log_path, not a node positional value.
    first = get_event_logger("scanner")
    second = get_event_logger("monitor")
    assert first.node == "scanner"
    assert second.node == "monitor"
    first.start({"x": 1})
    first.end({"y": 2})
    second.start(["not", "a", "dict"])
    assert path.exists()
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert [(r["stage"], r["event"]) for r in rows] == [
        ("scanner", "start"), ("scanner", "end"), ("monitor", "start")
    ]
    assert rows[0]["payload"] == {"x": 1}
    assert rows[1]["payload"] == {"y": 2}
    assert rows[2]["payload"] == {}
    assert rows[0]["run_id"] == rows[1]["run_id"]
    assert rows[0]["run_id"] != rows[2]["run_id"]
    assert str(first._logger.log_path) == str(path)
    assert not (tmp_path / "data").exists()
