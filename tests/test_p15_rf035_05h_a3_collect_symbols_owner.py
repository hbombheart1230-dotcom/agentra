"""P15 RF-035 (05h): symbol_trade_report.collect_symbols_for_day moved to symbol_trade_symbol_projection; parity with the pre-move body."""
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
from libs.reporting import symbol_trade_symbol_projection as owner

FN = "collect_symbols_for_day"
GOLDEN = "ed530a422fbb58472ecb2b51ba2f6e63f6f0c24a3ce2ef6c91b27438c3086500"
DAY_START = 1793318400  # 2026-10-30T00:00:00Z


def _ev(ts, **payload):
    return json.dumps({"ts": ts, "payload": payload}) + "\n"


def _scenarios(fn, root, mod):
    events = root / "events.jsonl"
    events.parent.mkdir(parents=True, exist_ok=True)
    events.write_text(
        _ev(DAY_START + 100, symbol="000660") + _ev(DAY_START + 200, symbol="005930") + _ev(DAY_START + 300, payload={"symbol": " abc "}) + _ev(DAY_START + 400, order={"symbol": "ord1", "stk_cd": "stk1"})
        + _ev(DAY_START - 5000, symbol="OTHERDAY") + "BAD\n" + _ev(0, symbol="NOTS"), encoding="utf-8")
    out = []
    out.append(_call(lambda: fn(events, root, "2026-10-30", [{"symbol": "005930"}, {"symbol": ""}, {"symbol": "x"}, {}])))
    out.append(_call(lambda: fn(events, root, " 2026-10-30 ", [])))
    out.append(_call(lambda: fn(events, root, "2026-10-30", None)))
    out.append(_call(lambda: fn(root / "nope.jsonl", root, "2026-10-30", [{"symbol": "zzz"}])))
    out.append(_patched(mod, "_to_epoch", lambda ts: DAY_START + 7 if ts else 0, lambda: _call(lambda: fn(events, root, "2026-10-30", []))))
    out.append(_patched(mod, "build_daily_trade_index", lambda r, d: [{"symbol": "IDX"}], lambda: _call(lambda: fn(events, root, "2026-10-30", None))))
    return out


def test_expected_values(tmp_path):
    out = _scenarios(m.collect_symbols_for_day, tmp_path, m)
    assert out[0] == ["ok", ["005930", "X", "000660", "ABC", "ORD1", "STK1"]]
    assert out[3] == ["ok", ["ZZZ"]]
    assert out[5][1][0] == "IDX"


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
