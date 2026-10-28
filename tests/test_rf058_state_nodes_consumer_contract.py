"""RF-058 C1/C2: StateStore consumers ``graphs/nodes/load_state.py`` / ``save_state.py`` against a tmp state file.

``STATE_STORE_PATH`` is always pointed at tmp_path (StateStore itself has no pytest isolation, so an unset
path would target ./data/state.json). No operational State, broker or network. Explicit raises keep the
checks live under ``python -O``.
"""
from __future__ import annotations

import json

import pytest

from graphs.nodes.load_state import load_state
from graphs.nodes.save_state import save_state
from libs.storage.state_store import StateStore


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


@pytest.fixture()
def state_path(tmp_path, monkeypatch):
    path = tmp_path / "state.json"
    monkeypatch.setenv("STATE_STORE_PATH", str(path))
    monkeypatch.chdir(tmp_path)
    return path


def test_load_state_defaults_when_file_missing_and_creates_nothing(state_path, tmp_path):
    out = load_state({"keep": 1})
    _eq(out["keep"], 1)
    persisted = out["persisted_state"]
    _eq((persisted["last_order_epoch"], persisted["open_positions"], persisted["mock_positions"], persisted["last_trade_side"]),
        (0, 0, [], ""))
    _eq(list(tmp_path.iterdir()), [])


def test_save_then_load_round_trip_merges_over_defaults(state_path):
    save_state({"persisted_state": {"mock_cash": 123.5, "custom": {"a": [1, 2]}}})
    _eq(json.loads(state_path.read_text(encoding="utf-8"))["custom"], {"a": [1, 2]})
    loaded = load_state({})["persisted_state"]
    _eq((loaded["mock_cash"], loaded["custom"], loaded["last_trade_epoch"]), (123.5, {"a": [1, 2]}, 0))


def test_save_state_without_persisted_state_writes_empty_object(state_path):
    out = save_state({})
    _eq(out, {})
    _eq(json.loads(state_path.read_text(encoding="utf-8")), {})


def test_corrupt_file_loads_as_defaults_and_is_replaced_on_next_save(state_path):
    state_path.write_text("{oops", encoding="utf-8")
    _eq(load_state({})["persisted_state"]["open_positions"], 0)
    save_state({"persisted_state": {"open_positions": 2}})
    _eq(json.loads(state_path.read_text(encoding="utf-8")), {"open_positions": 2})


def test_newer_authoritative_broker_truth_is_not_overwritten_by_a_stale_save(state_path):
    marker = "broker_truth_position_reconciliation"
    newer = {marker: {"authoritative": True, "generated_at": "2026-10-28T10:00:00+09:00"},
             "mock_positions": [{"symbol": "005930", "qty": 3}], "open_positions": 1}
    StateStore(str(state_path)).save(newer)
    stale = {marker: {"authoritative": True, "generated_at": "2026-10-28T09:00:00+09:00"},
             "mock_positions": [], "open_positions": 0, "other": "kept"}
    save_state({"persisted_state": stale})
    now = json.loads(state_path.read_text(encoding="utf-8"))
    _eq((now["mock_positions"], now["open_positions"], now["other"]), ([{"symbol": "005930", "qty": 3}], 1, "kept"))
    _eq(now[marker]["generated_at"], "2026-10-28T10:00:00+09:00")
    fresher = {marker: {"authoritative": True, "generated_at": "2026-10-28T11:00:00+09:00"}, "mock_positions": [], "open_positions": 0}
    save_state({"persisted_state": fresher})
    _eq(json.loads(state_path.read_text(encoding="utf-8"))["open_positions"], 0)           # a newer revision wins


def test_non_authoritative_marker_never_protects_older_values(state_path):
    marker = "broker_truth_position_reconciliation"
    StateStore(str(state_path)).save({marker: {"authoritative": False, "generated_at": "2099-01-01T00:00:00+00:00"}, "open_positions": 5})
    save_state({"persisted_state": {"open_positions": 0}})
    _eq(json.loads(state_path.read_text(encoding="utf-8"))["open_positions"], 0)
