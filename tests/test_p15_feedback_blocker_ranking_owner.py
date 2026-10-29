"""P15 A2: reporter_feedback ``_build_blocker_analysis`` moved to reporter_feedback_analysis; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import reporter_feedback as F
from libs.reporting import reporter_feedback_analysis as owner

GOLDEN = ["4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945", "17f3786ba79c002f87f631bbc1cca90ac90ebfb9246382d541ed4166c01ddd91", "b1117df4b236fbb8a4f5da66626fcb1bb8c29572ba4c98ff2f5348ff1f55ba86", "05e5032899f23a61f60b40bbb06fb84c1f39572f6c67cabbf1f0545258f144fe", "2160cc58d2de34f8844dc7b94946b91972a96dbe8b98daeec02372298b45dd8f", "c7ba9444517e9866dfe325a1791ce53a2139f2fed266258150c2b96321477938", "EXC:AttributeError", "EXC:AttributeError", "17f3786ba79c002f87f631bbc1cca90ac90ebfb9246382d541ed4166c01ddd91"]

BLOCKERS = [{}, {"a": 0}, {"a": 3, "b": 3, "c": 1}, {"b": "5", "a": "x", "c": 2, "d": 1, "e": 1, "f": 1, "g": 9}, {"z": 1, "y": 1, "x": 1, "w": 1, "v": 1, "u": 1}, {1: 2, "a": None}, None, [("a", 1)], {"a": [1]}]
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


@pytest.mark.parametrize("i", range(len(BLOCKERS)))
def test_wrapper_and_owner_match_pre_move_golden_and_input_unchanged(i):
    payload = BLOCKERS[i]
    snap = copy.deepcopy(payload)
    assert _safe(lambda: F._build_blocker_analysis(payload)) == GOLDEN[i]
    assert _safe(lambda: owner.build_blocker_analysis(payload, facade=F)) == GOLDEN[i]
    assert payload == snap


def test_ranking_ties_top_five_and_zero_denominator():
    f = F._build_blocker_analysis
    assert f({}) == [] and f({"a": 0}) == [{"blocker": "a", "count": 0, "ratio": 0.0}]
    assert [r["blocker"] for r in f(BLOCKERS[2])] == ["a", "b", "c"]                   # tie on count -> name ascending
    top = f(BLOCKERS[3])
    assert [r["blocker"] for r in top] == ["g", "b", "c", "d", "e"] and len(top) == 5 and list(top[0]) == ["blocker", "count", "ratio"]
    assert top[0]["ratio"] == round(9 / 19, 4) and top[1]["count"] == 5                  # "5" converted; "x" -> 0
    assert len(f(BLOCKERS[4])) == 5


def test_original_attribute_errors_for_non_mapping():
    for bad in (None, [("a", 1)]):
        with pytest.raises(AttributeError):
            F._build_blocker_analysis(bad)


def test_facade_helpers_use_time_patches_reach_the_owner(monkeypatch):
    monkeypatch.setattr(F, "_safe_total", lambda c: 100)
    monkeypatch.setattr(F, "_safe_int", lambda v, d=0: 7)
    monkeypatch.setattr(F, "_ratio", lambda c, t: ("R", c, t))
    assert F._build_blocker_analysis({"a": 1, "b": 2}) == [{"blocker": "a", "count": 7, "ratio": ("R", 7, 100)}, {"blocker": "b", "count": 7, "ratio": ("R", 7, 100)}]


def test_owner_does_not_import_the_facade_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.reporter_feedback import" not in src and "import reporter_feedback\n" not in src
    assert len(inspect.getsource(F._build_blocker_analysis).splitlines()) <= 3
