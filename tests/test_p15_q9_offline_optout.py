"""P15 C02-3: Q9 comparison exposes a keyword-only allow_fresh_fetch opt-out; default stays True."""
from __future__ import annotations

import inspect
import json

from libs.reporting.baseline_samsung_hynix import q9_comparison as q9
from libs.reporting.baseline_samsung_hynix.contracts import HORIZONS

DAY = "2026-10-20"
ROLE_LIST = ["P_SCANNER_PRE_STRATEGIST_UNIVERSE", "A_SCANNER_CONTROL", "B_STRATEGIST_RANKED", "C_COMMANDER_FINAL"]


def _setup(tmp_path, monkeypatch):
    root = tmp_path / "q9"
    (root / DAY).mkdir(parents=True)
    rows = [{"q9_decision_id": "w1", "q9_decision_role": r, "symbol": "005930", "rank": 1, "q9_commander_decision": "approve"} for r in ROLE_LIST]
    (root / DAY / "x.json").write_text(json.dumps({"q9_decision_candidates": rows}), encoding="utf-8")
    calls = []
    monkeypatch.setattr(q9, "load_q9_forward_candles", lambda rows, **kw: calls.append(kw) or {})
    monkeypatch.setattr(q9, "attach_forward_outcomes", lambda rows, *, minute_rows_by_symbol=None: [dict(r) for r in rows])
    return root, calls


def _run(root, tmp_path, **kw):
    return q9.build_q9_role_comparison(day=DAY, baseline_summary={}, cost_pct=0.1, slippage_pct=0.05, q9_root=root, state_path=tmp_path / "s.json", **kw)


def test_explicit_false_reaches_loader_and_default_is_true(tmp_path, monkeypatch):
    root, calls = _setup(tmp_path, monkeypatch)
    off = _run(root, tmp_path, allow_fresh_fetch=False)
    assert [c["allow_fresh_fetch"] for c in calls] == [False]
    default = _run(root, tmp_path)
    assert [c["allow_fresh_fetch"] for c in calls] == [False, True]
    assert off == default and off["comparable_complete_window_count"] == 1 and len(off["roles"]) == 4 * len(HORIZONS)
    _run(root, tmp_path, allow_fresh_fetch=True)
    assert calls[-1]["allow_fresh_fetch"] is True and all(c["run_id_prefix"] == "q9_comparison_forward_recovery" for c in calls)


def test_signature_keyword_only_with_true_default():
    for fn in (q9.build_q9_role_comparison, q9._load_q9_rows):
        p = inspect.signature(fn).parameters["allow_fresh_fetch"]
        assert p.kind is inspect.Parameter.KEYWORD_ONLY and p.default is True
    assert list(inspect.signature(q9.build_q9_role_comparison).parameters)[:4] == ["day", "baseline_summary", "cost_pct", "slippage_pct"]
