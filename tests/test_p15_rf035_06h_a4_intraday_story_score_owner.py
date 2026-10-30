"""P15 RF-035 (06h): intraday_trade_reports._story_input_quality_score moved to intraday_report_quality_projection; parity with the pre-move body."""
from __future__ import annotations

import json
import hashlib
from pathlib import Path

import pytest


def _norm(obj, root):
    return json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).replace(str(root), "<T>")


def _h(text):
    return hashlib.sha256(text.encode()).hexdigest()


def _call(fn):
    try:
        return ["ok", fn()]
    except BaseException as exc:  # noqa: BLE001 - parity of exception type/message is the point
        return ["exc", type(exc).__name__, str(exc)]


def _write(root, rel, payload):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return p


def _patched(mod, name, value, fn):
    orig = getattr(mod, name)
    setattr(mod, name, value)
    try:
        return fn()
    finally:
        setattr(mod, name, orig)

from libs.reporting import intraday_trade_reports as m
from libs.reporting import intraday_report_quality_projection as owner

FN = "_story_input_quality_score"
GOLDEN = "2602b17f374c6fe3e863014a954a948555c9352120a2136830af0520d32b96a4"

CASES = [
    {}, None, [1], "x",
    {"status": "open", "symbol": "005930", "run_id": "r"},
    {"status": "open", "symbol": "005930", "run_id": "r", "execution_details": {"order_id": "x", "filled_price": 10}},
    {"status": "closed", "symbol": "A", "selected_symbol": "B", "candidate_count": 3, "scanner_selection_trace": {"ranked_candidates": [1]}, "monitor_stop_policy_trace": {"k": 1}},
    {"status": "CLOSED", "symbol": "A", "scanner_reason_human": {"selected_symbol": "A", "candidate_count": 2.5}, "canonical_monitor": {"current_price": 1, "account_pnl_ratio": 0.1}, "entry_summary": "s"},
    {"execution_details": {"order_id": "o", "filled_qty": 0, "filled_price": 1, "broker_truth_source": "b", "broker_day_truth_source": "d", "broker_day_match_mode": "m", "broker_day_authoritative": True, "broker_realized_pnl": 0, "broker_fee": 1},
     "entry_execution_details": {"broker_tax": 0}, "exit_execution_details": "bad"},
    {"candidate_count": "x", "canonical_monitor": {"effective_pnl_ratio": 0}},
]


def _scenarios(fn, root, mod):
    return [_call(lambda c=c: fn(c)) for c in CASES]


def test_expected_values(tmp_path):
    out = _scenarios(m._story_input_quality_score, tmp_path, m)
    assert [o[1] for o in out[:5]] == [0, 0, 0, 0, 4] and out[5][1] == 7
    assert all(o[0] == "ok" and isinstance(o[1], int) for o in out)
    assert out[8][1] == 14


def test_input_not_mutated():
    import copy
    for c in CASES:
        snap = copy.deepcopy(c)
        m._story_input_quality_score(c)
        assert c == snap


def _run(fn, root, mod):
    return _norm(_scenarios(fn, root, mod), root)


def test_wrapper_owner_and_pre_move_golden(tmp_path):
    a = _run(getattr(m, FN), tmp_path / "a", m)
    b = _run(lambda *a, **k: getattr(owner, FN)(*a, facade=m, **k), tmp_path / "b", m)
    assert a == b and _h(a) == GOLDEN


def test_wrapper_is_thin():
    import ast
    import inspect
    fn = ast.parse(inspect.getsource(getattr(m, FN))).body[0]
    stmts = [n for n in fn.body if not (isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant))]
    assert len(stmts) == 1 and isinstance(stmts[0], ast.Return)
    assert "import intraday_trade_reports" not in inspect.getsource(owner)
