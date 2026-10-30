"""P15 RF-035 (05h): market_regime_rail_review.classify_market_regime_rail moved to market_regime_rail_classification_projection; parity with the pre-move body."""
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

from libs.reporting import market_regime_rail_review as m
from libs.reporting import market_regime_rail_classification_projection as owner

FN = "classify_market_regime_rail"
GOLDEN = "76a3fe54c3d0ffd37b607fae150495351ae4ddb61657a9553ff707d2f52898f3"


def _snap(**moves):
    return {"index_moves": moves}


SNAPS = [
    {"available": False},
    {},
    _snap(krx_night_futures_pct=-2.1),
    _snap(krx_night_futures_pct=2.5, kospi_pct=1.2),
    _snap(kospi_pct=-1.8, kosdaq_pct=-2.2, nasdaq_pct=-1.5),
    _snap(kospi_pct=2.0, kosdaq_pct=1.5, nasdaq_pct=1.0, sp500_pct=1.0),
    {"macro_moves": {"vix_level": 35.0, "vix_pct": 12.0, "dxy_pct": 1.1}, "index_moves": {"nasdaq_pct": -2.0}},
    {"korea_indices": {"breadth": 0.2, "kospi": {"change_pct": -9.9}}, "global_sentiment": {"score": -0.8}},
    {"macro_indicators": {"indicators": {"usdkrw": {"change_pct": 1.4}, "us_10y_yield": {"delta": 0.2}}}},
    {"available": False, "schema_version": "x"},
    {"macro_moves": "bad", "global_sentiment": [1], "korea_indices": 5},
]


def _scenarios(fn, root, mod):
    out = [_call(lambda s=s: fn(s)) for s in SNAPS]
    out.append(_call(lambda: fn(None)))
    out.append(_patched(mod, "_change_pct", lambda s, k: -3.0, lambda: _call(lambda: fn({}))))
    out.append(_patched(mod, "korea_index_sanity", lambda k: {"status": "warning", "warning_count": 1, "warnings": [{"code": "C"}], "extreme_move_requires_confirmation": True}, lambda: _call(lambda: fn({"korea_indices": {"kospi": {}}}))))
    return out


def test_expected_values(tmp_path):
    out = _scenarios(m.classify_market_regime_rail, tmp_path, m)
    assert out[0][1]["rail_id"] == "not_available" and out[0][1]["available"] is False and out[0][1]["behavior_effect"] == "evaluation_only"
    assert out[2][1]["rail_id"] == "krx_night_futures_gap_down" and out[2][1]["rail_confidence"] == "high"
    assert out[1][1]["rail_id"] == "neutral_observation"
    assert out[11][0] == "exc" and out[11][1] == "AttributeError"
    assert {o[1]["behavior_effect"] for o in out if o[0] == "ok"} == {"evaluation_only"}


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
