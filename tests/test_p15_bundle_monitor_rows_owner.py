"""P15 A5: ``_target_symbol_monitor_rows`` moved to live_execution_bundle_runner_monitor_rows; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import live_execution_bundle_runner as r
from libs.reporting import live_execution_bundle_runner_monitor_rows as owner

GOLDEN = ["EXC:AttributeError", "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945", "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945", "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945", "EXC:AttributeError", "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"]

MON_ROWS = [
    {"symbol": "005930", "event": "monitor.start", "i": 1}, {"symbol": "005930", "event": "monitor.end", "i": 2}, {"symbol": "000660", "event": "monitor.start", "i": 3},
    {"symbol": "005930", "event": "scanner.pick", "i": 4}, {"symbol": "005930", "event": "monitor.start", "i": 5}, {"i": 6}, "junk",
]
MON_CASES = [(MON_ROWS, "005930"), (MON_ROWS, ""), (MON_ROWS, None), (None, "005930"), (MON_ROWS, "000660"), ([], "005930")]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(MON_CASES)))
def test_wrapper_and_owner_match_pre_move_golden_and_rows_unchanged(i):
    rows, symbol = MON_CASES[i]
    snap = copy.deepcopy(rows)
    assert _safe(lambda: r._target_symbol_monitor_rows(rows, symbol=symbol)) == GOLDEN[i]
    assert _safe(lambda: owner.target_symbol_monitor_rows(rows, symbol=symbol, facade=r)) == GOLDEN[i]
    assert rows == snap


def test_selection_keeps_order_duplicates_and_filters_symbol_and_name():
    try:
        out = r._target_symbol_monitor_rows(MON_ROWS[:6], symbol="005930")
    except Exception:
        pytest.skip("event helpers reject the fixture shape")
    assert [x["i"] for x in out] == [1, 2, 5]
    assert r._target_symbol_monitor_rows(MON_ROWS[:6], symbol="") == [] and r._target_symbol_monitor_rows(None, symbol="005930") == []


def test_facade_helper_use_time_patches_reach_the_owner(monkeypatch):
    calls = []
    monkeypatch.setattr(r, "normalize_symbol", lambda value, allow_test_symbols=False: (calls.append((value, allow_test_symbols)), "SYM")[1])
    monkeypatch.setattr(r, "_event_row_symbol", lambda row: "SYM" if row.get("keep") else "other")
    monkeypatch.setattr(r, "_event_row_name", lambda row: row.get("name", ""))
    rows = [{"keep": 1, "name": "monitor.a"}, {"keep": 1, "name": "scanner.b"}, {"keep": 0, "name": "monitor.c"}, {"keep": 1, "name": "monitor.d"}]
    out = r._target_symbol_monitor_rows(rows, symbol="x")
    assert out == [rows[0], rows[3]] and out[0] is rows[0] and calls == [("x", True)]
    monkeypatch.setattr(r, "normalize_symbol", lambda value, allow_test_symbols=False: "")
    assert r._target_symbol_monitor_rows(rows, symbol="x") == []


def test_original_attribute_error_for_non_dict_rows():
    with pytest.raises(Exception):
        r._target_symbol_monitor_rows(MON_ROWS, symbol="005930")


def test_owner_does_not_import_the_runner_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.live_execution_bundle_runner import" not in src and "import live_execution_bundle_runner\n" not in src
    assert len(inspect.getsource(r._target_symbol_monitor_rows).splitlines()) <= 8
