"""P15 A3: reporter_feedback ``_build_route_analysis`` moved to reporter_feedback_analysis; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import reporter_feedback as F
from libs.reporting import reporter_feedback_analysis as owner

GOLDEN = ["adcc27e60bb6fc3eb22af42823e7f61d8bb6b3597eff799210f7f646b90be812", "5d138fbd2877c9040800cd7f36eedb5a518818e2536fd08da5dd2d9ab519eb59", "5ba4dcb02762c98759eab3b1962cc5997c7f81a56bb3496c94de93a842070987", "93e11c91f160eaaddf458289a0d2fd580f84ebe0eaeb10011fa81ae2674f1a90", "adcc27e60bb6fc3eb22af42823e7f61d8bb6b3597eff799210f7f646b90be812", "EXC:ValueError", "EXC:TypeError", "EXC:AttributeError", "EXC:ValueError"]

ROUTES = [{}, {"route_selected_total": {"monitor_only": 3, "cached_strategist": 2, "full_cycle": 1}, "route_source": "src", "strategy_generation_mode_total": {"llm": 1}, "strategist_fallback_total": "2",
            "route_source_run_count": 6, "route_source_missing_count": "1", "route_source_breakdown": {"a": 1}},
          {"route_selected_total": {"monitor_only": 0}}, {"route_selected_total": {"monitor_only": "2", "other": 2}}, {"route_selected_total": None, "route_source": None},
          {"route_selected_total": "bad"}, {"route_selected_total": [1]}, None, {"strategy_generation_mode_total": "x"}]
INSIGHT = [
    dict(route_analysis={}, blocker_analysis=[]),
    dict(route_analysis={"route_selected_total": {"monitor_only": 3, "cached_strategist": 2, "full_cycle": 1}}, blocker_analysis=[{"blocker": "b1", "count": 4}]),
    dict(route_analysis={"route_selected_total": {"monitor_only": 2, "cached_strategist": 2}}, blocker_analysis=[]),
    dict(route_analysis={"route_selected_total": {"monitor_only": 0, "cached_strategist": 0, "x": 1}}, blocker_analysis=[], trade_report_summary={"closed_trade_count": 3, "win_count": 1, "loss_count": 1, "flat_count": 1, "unknown_pnl_count": 1, "avg_pnl_pct": 0.25, "pnl_pct_sample_count": 2}),
    dict(route_analysis={}, blocker_analysis=[], trade_report_summary={"closed_trade_count": 2, "win_count": 0, "loss_count": 2, "avg_pnl_pct": -1.5, "pnl_pct_sample_count": 0}),
    dict(route_analysis={"route_selected_total": {"full_cycle": "4"}}, blocker_analysis=[{}], trade_report_summary={"closed_trade_count": "1"}),
    dict(route_analysis={"route_selected_total": "junk"}, blocker_analysis=["junk"]),
    dict(route_analysis={"route_selected_total": {"a": "x"}}, blocker_analysis=[]),
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(ROUTES)))
def test_wrapper_and_owner_match_pre_move_golden_and_input_unchanged(i):
    payload = ROUTES[i]
    snap = copy.deepcopy(payload)
    assert _safe(lambda: F._build_route_analysis(payload)) == GOLDEN[i]
    assert _safe(lambda: owner.build_route_analysis(payload, facade=F)) == GOLDEN[i]
    assert payload == snap


def test_default_ratios_key_order_and_alias():
    d = F._build_route_analysis({})
    assert list(d) == ["route_source", "route_selected_total", "strategy_generation_mode_total", "strategist_fallback_total", "route_source_run_count", "route_source_missing_count",
                       "route_source_breakdown", "monitor_only_ratio", "cached_strategist_ratio", "full_cycle_ratio"]
    assert d["route_source"] == "unavailable" and d["monitor_only_ratio"] == 0.0
    out = F._build_route_analysis(ROUTES[1])
    assert (out["monitor_only_ratio"], out["cached_strategist_ratio"], out["full_cycle_ratio"]) == (0.5, 0.3333, 0.1667) and out["strategist_fallback_total"] == 2 and out["route_source_missing_count"] == 1
    assert out["route_selected_total"] is not ROUTES[1]["route_selected_total"] and out["route_selected_total"] == ROUTES[1]["route_selected_total"]    # fresh shallow dict
    mixed = F._build_route_analysis(ROUTES[3])
    assert mixed["monitor_only_ratio"] == 0.5 and F._build_route_analysis(ROUTES[2])["monitor_only_ratio"] == 0.0 and F._build_route_analysis(ROUTES[4])["route_source"] == "unavailable"


def test_malformed_values_keep_original_exceptions():
    for bad, exc in ((ROUTES[5], ValueError), (ROUTES[6], TypeError), (ROUTES[7], AttributeError), (ROUTES[8], ValueError)):
        with pytest.raises(exc):
            F._build_route_analysis(bad)


def test_facade_helpers_use_time_patches_reach_the_owner(monkeypatch):
    monkeypatch.setattr(F, "_safe_total", lambda c: 4)
    monkeypatch.setattr(F, "_safe_int", lambda v, d=0: 2)
    monkeypatch.setattr(F, "_ratio", lambda c, t: f"{c}/{t}")
    out = F._build_route_analysis({"route_selected_total": {"monitor_only": 1}})
    assert out["monitor_only_ratio"] == "2/4" and out["strategist_fallback_total"] == 2


def test_owner_does_not_import_the_facade_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.reporter_feedback import" not in src and "import reporter_feedback\n" not in src
    assert len(inspect.getsource(F._build_route_analysis).splitlines()) <= 3
