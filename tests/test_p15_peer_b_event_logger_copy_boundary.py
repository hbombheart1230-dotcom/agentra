"""P15 C02-5 peer probe (FAST-3): EventLogger compat adapter under copy.copy / copy.deepcopy.

Runs only against an isolated B checkout: set ``P15_PEER_B_TREE`` to its root and put it first on PYTHONPATH (the test file
itself must live outside both trees so the checkout wins the import). Skipped in the A tree. Expectations describe the
desired behavior; a RecursionError from ``__getattr__`` is reported as a FAIL for the B owner, never relaxed here.
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path

import pytest

_TREE = os.environ.get("P15_PEER_B_TREE", "")
if not _TREE:
    pytest.skip("P15_PEER_B_TREE not set (peer probe for an isolated B checkout only)", allow_module_level=True)

from libs.core import event_logger_compat as compat  # noqa: E402
from libs.core.event_logger_compat import get_event_logger  # noqa: E402

if not Path(compat.__file__).resolve().is_relative_to(Path(_TREE).resolve()):
    raise AssertionError(f"import provenance: {compat.__file__} is outside {_TREE}")


@pytest.fixture
def logger(tmp_path, monkeypatch):
    log = tmp_path / "events.jsonl"
    monkeypatch.setenv("EVENT_LOG_PATH", str(log))
    return get_event_logger("node_x"), log


def _rows(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def test_original_start_end_two_lines_same_run_id_and_nothing_else_written(logger, tmp_path):
    lg, log = logger
    assert type(lg).__name__ == "_NodeEventLogger"
    lg.start({"a": 1})
    lg.end({"b": 2})
    rows = _rows(log)
    assert [(r["stage"], r["event"]) for r in rows] == [("node_x", "start"), ("node_x", "end")]
    assert rows[0]["run_id"] == rows[1]["run_id"] == lg._run_id
    assert sorted(p.name for p in tmp_path.iterdir()) == ["events.jsonl"]


@pytest.mark.parametrize("fn", [copy.copy, copy.deepcopy], ids=["copy", "deepcopy"])
def test_copy_does_not_raise_and_preserves_node_and_run_id(logger, fn):
    lg, log = logger
    try:
        dup = fn(lg)
    except RecursionError as exc:                                              # defect evidence, handed to the B owner
        pytest.fail(f"RecursionError during {fn.__name__}: {type(exc).__name__}")
    assert dup is not lg and dup.node == "node_x" and dup._run_id == lg._run_id
    dup.start({"c": 3})
    rows = _rows(log)
    assert rows and rows[-1]["stage"] == "node_x" and rows[-1]["run_id"] == lg._run_id


def test_missing_attribute_lookup_still_delegates_or_raises_attribute_error(logger):
    lg, _ = logger
    assert lg.log_path == lg._logger.log_path
    with pytest.raises(AttributeError):
        lg.definitely_not_an_attribute
