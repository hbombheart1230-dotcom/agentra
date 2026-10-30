"""P15 RF-035 (05h): symbol_trade_report._build_history_index moved to symbol_trade_history_projection; parity with the pre-move body."""
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

from libs.reporting import symbol_trade_report as m
from libs.reporting import symbol_trade_history_projection as owner

FN = "_build_history_index"
GOLDEN = "f0bec51767ae2d6ae79442d38181acb06ffe593a39c11f7b5869239d15556d9f"


def _life(root, tid, day, symbol, **extra):
    d = {"trade_id": tid, "day": day, "symbol": symbol, "status": "closed", "entry": {"run_id": "R" + tid}, "exit": {"run_id": "X" + tid},
         "summary": {"entry_reason_human": "breakout entry", "exit_reason_human": "stop", "operator_conclusion_human": "done"}, "artifacts": {}}
    d.update(extra)
    _write(root, f"trades/{day}/{tid}/lifecycle/trade_lifecycle.json", d)


def _scenarios(fn, root, mod):
    out = [_call(lambda: fn(root / "empty", "005930"))]
    _life(root, "T2", "2026-10-30", "005930")
    _life(root, "T1", "2026-10-30", "005930", status="open", exit={})
    _life(root, "T0", "2026-10-29", "005930", entry={}, exit={})
    _life(root, "T3", "2026-10-30", "000660")
    out.append(_call(lambda: fn(root, " 005930 ")))
    out.append(_call(lambda: fn(root, "000660")))
    out.append(_call(lambda: fn(root, "999999")))
    out.append(_patched(mod, "_extract_trade_artifact_snapshot", lambda **k: {"artifact_result_pct": 7.5, "report_headline": "SEAM"}, lambda: _call(lambda: fn(root, "005930"))))
    out.append(_patched(mod, "_iter_trade_lifecycles", lambda r: [(root / "x" / "lifecycle" / "trade_lifecycle.json", {"trade_id": "Z", "symbol": "005930", "day": "2026-01-01"})], lambda: _call(lambda: fn(root, "005930"))))
    return out


def test_expected_values(tmp_path):
    out = _scenarios(m._build_history_index, tmp_path, m)
    assert out[0] == ["ok", []]
    rows = out[1][1]
    assert [(r["date"], r["trade_id"]) for r in rows] == [("2026-10-29", "T0"), ("2026-10-30", "T1"), ("2026-10-30", "T2")]
    assert [r["last_action"] for r in rows] == ["", "HOLD", "SELL"]
    assert [r["trade_id"] for r in out[2][1]] == ["T3"] and out[3] == ["ok", []]
    assert all(r["report_headline"] == "SEAM" and r["result_pct"] is not None for r in out[4][1])
    assert out[5][1][0]["trade_id"] == "Z"


def _run(fn, root, mod):
    return _norm(_scenarios(fn, root, mod), root)


def _owner_fn(**fixed):
    return lambda *a, **k: getattr(owner, FN)(*a, facade=m, **k)


def test_wrapper_owner_and_pre_move_golden(tmp_path):
    a = _run(getattr(m, FN), tmp_path / "a", m)
    b = _run(_owner_fn(), tmp_path / "b", m)
    assert a == b and _h(a) == GOLDEN


def test_wrapper_is_thin():
    import inspect
    assert len(inspect.getsource(getattr(m, FN)).strip().splitlines()) <= 12
    assert "import symbol_trade_report" not in inspect.getsource(owner) and "import report_source_helpers" not in inspect.getsource(owner)
