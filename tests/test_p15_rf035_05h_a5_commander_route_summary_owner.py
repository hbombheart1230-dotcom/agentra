"""P15 RF-035 (05h): report_source_helpers.build_commander_route_summary moved to report_source_route_summary_projection; parity with the pre-move body."""
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

from libs.reporting import report_source_helpers as m
from libs.reporting import report_source_route_summary_projection as owner

FN = "build_commander_route_summary"
GOLDEN = "61a3e01618b2277ed285f5d5135acb74516b0ebb5b03cbfcc70dfa7e83b57bca"


def _scenarios(fn, root, mod):
    out = [_call(lambda: fn(reports_root=root / "empty", day="2026-10-30"))]
    _write(root, "canonical/2026-10-30/r1/commander.json", {"route_selected": "direct", "strategy_generation_mode": "full", "strategist_fallback_used": False})
    _write(root, "canonical/2026-10-30/r2/commander.json", {})
    _write(root, "canonical/2026-10-30/r4/commander.json", {"route_selected": ""})
    (root / "canonical" / "2026-10-30" / "afile.txt").write_text("x", encoding="utf-8")
    rows = [
        {"run_id": "r1", "stage": "commander_router", "event": "route_selected", "payload": {"route_selected": "fallbackroute"}},
        {"run_id": "r3", "stage": "commander_router", "event": "route_selected", "payload": {"route_selected": "indirect", "strategist_fallback_used": True}},
        {"run_id": "r3", "stage": "strategist", "event": "policy_resolution", "payload": {"strategy_generation_mode": "shadow", "fallback_used": True}},
        {"run_id": "r5", "stage": "other", "event": "x", "payload": {}},
        {"run_id": "r6", "stage": "commander_router", "event": "end", "payload": {}},
    ]
    out.append(_call(lambda: fn(reports_root=root, day="2026-10-30", day_rows=rows)))
    out.append(_call(lambda: fn(reports_root=root, day="2026-10-30", day_rows=iter(rows))))
    out.append(_call(lambda: fn(reports_root=root, day="2026-10-30")))
    out.append(_patched(mod, "read_json", lambda p: {"route_selected": "SEAM"}, lambda: _call(lambda: fn(reports_root=root, day="2026-10-30", day_rows=[]))))
    out.append(_patched(mod, "_event_route_rows", lambda rows: {"zz": {"route_selected": "EV", "route_source": "event_fallback"}}, lambda: _call(lambda: fn(reports_root=root, day="2026-10-30", day_rows=[]))))
    return out


def test_expected_values(tmp_path):
    out = _scenarios(m.build_commander_route_summary, tmp_path, m)
    assert out[0][1]["route_source_run_count"] == 0 and out[0][1]["by_run"] == {}
    res = out[1][1]
    assert res["route_source"] == "canonical_commander_preferred" and res["by_run"]["r1"]["route_selected"] == "direct" and res["by_run"]["r1"]["route_source"] == "canonical_commander"
    assert res["route_selected_total"] == {"direct": 1, "indirect": 1} and res["route_source_run_count"] == 2
    assert res["route_source_missing_count"] == 1 and res["strategist_fallback_total"] == 1
    assert out[4][1]["route_selected_total"] == {"SEAM": 3}
    assert out[5][1]["by_run"]["zz"]["route_selected"] == "EV"


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
