"""P15 A5: reporter_feedback ``_build_dominant_patterns`` moved to reporter_feedback_dominant_patterns; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import reporter_feedback as f
from libs.reporting import reporter_feedback_dominant_patterns as owner

GOLDEN = ["4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945", "f24381cf3565513aa3b1f60d1d8dcea7329f4f5c109e526586df6147b6ef06ab", "4e09edd2158e77549e69ea235f58e784d5640541d9e189b0d2319f34dcc447fc", "559e899b61ad7a7d3d3c5ea88ccdf7225afb942646ff7e330b83b3770af269bc", "49a565227aaa2383d54d4693ad8e60cb5f94415f3884a1eee9b9548f145dfeaa", "EXC:TypeError", "EXC:AttributeError"]

PATTERNS = [
    dict(route_summary={}, blocker_totals={}, freshness={}),
    dict(route_summary={"route_selected_total": {"monitor_only": 3, "cached_strategist": 2, "full_cycle": 1}, "strategist_fallback_total": 2}, blocker_totals={"vwap_reclaim_fail": 3, "other": 1},
         freshness={"freshness_status": "fresh", "source_window_summary": "win"}),
    dict(route_summary={"route_selected_total": {"monitor_only": 3, "cached_strategist": 2, "full_cycle": 1}, "strategist_fallback_total": 2}, blocker_totals={"reclaim_x": 3}, freshness={"freshness_status": "fresh"},
         trade_report_summary={"closed_trade_count": 4, "avg_pnl_pct": -0.5, "same_price_cost_loss_count": 2}),
    dict(route_summary={"route_selected_total": {"monitor_only": 0, "full_cycle": "2"}}, blocker_totals={}, freshness={}, trade_report_summary={"closed_trade_count": "2", "avg_pnl_pct": None}),
    dict(route_summary={"route_selected_total": "junk", "strategist_fallback_total": 3}, blocker_totals={"a": 0}, freshness={"freshness_status": None}),
    dict(route_summary={"route_selected_total": {"monitor_only": 1}}, blocker_totals={"reclaim": "x"}, freshness={}),
    dict(route_summary={"route_selected_total": {"monitor_only": 1}}, blocker_totals=None, freshness={}),
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(PATTERNS)))
def test_wrapper_and_owner_match_pre_move_golden_and_input_unchanged(i):
    args = PATTERNS[i]
    snap = copy.deepcopy(args)
    assert _safe(lambda: f._build_dominant_patterns(**args)) == GOLDEN[i]
    assert _safe(lambda: owner.build_dominant_patterns(facade=f, **args)) == GOLDEN[i]
    assert args == snap


def _names(kw):
    return [p["name"] for p in f._build_dominant_patterns(**kw)]


def test_pattern_order_cap_and_values():
    assert f._build_dominant_patterns(**PATTERNS[0]) == []
    assert _names(PATTERNS[1]) == ["monitor_only_ratio", "cached_strategist_ratio", "full_cycle_ratio", "reclaim_blocked_ratio", "strategist_fallback_ratio", "freshness_status"]
    out = f._build_dominant_patterns(**PATTERNS[1])
    assert out[0] == {"name": "monitor_only_ratio", "value": 0.5, "detail": "monitor_only 3/6 runs"} and out[3]["value"] == 0.75 and out[5] == {"name": "freshness_status", "value": "fresh", "detail": "win"}
    assert len(f._build_dominant_patterns(**PATTERNS[2])) == 6 and _names(PATTERNS[2])[-1] == "freshness_status"                  # trade patterns are cut by [:6]
    two = f._build_dominant_patterns(**PATTERNS[3])
    assert [p["name"] for p in two] == ["full_cycle_ratio", "same_day_closed_trade_count", "same_day_avg_pnl_pct"] and two[0]["detail"] == "full_cycle 2/2 runs"


def test_zero_denominators_and_original_exceptions():
    assert f._build_dominant_patterns(**PATTERNS[4]) == [{"name": "freshness_status", "value": "unknown", "detail": ""}]       # junk route totals -> zero denominators, no ratio rows
    with pytest.raises(AttributeError):
        f._build_dominant_patterns(**PATTERNS[6])


def test_facade_helpers_use_time_patches_reach_the_owner(monkeypatch):
    monkeypatch.setattr(f, "_ratio", lambda c, t: "R")
    monkeypatch.setattr(f, "_safe_total", lambda c: 10)
    out = f._build_dominant_patterns(**PATTERNS[1])
    assert out[0]["value"] == "R" and out[0]["detail"] == "monitor_only 3/10 runs"
    monkeypatch.setattr(f, "_safe_int", lambda v, d=0: 0)
    assert "monitor_only_ratio" not in _names(PATTERNS[1])


def test_owner_does_not_import_the_facade_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.reporter_feedback import" not in src and "import reporter_feedback\n" not in src
    assert len(inspect.getsource(f._build_dominant_patterns).splitlines()) <= 8
