"""P15 A4: reporter_feedback ``_build_insight_summary`` moved to reporter_feedback_summary; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import reporter_feedback as F
from libs.reporting import reporter_feedback_summary as owner

GOLDEN = ["04e63f6d9bd5ef05c865c48baffdf278c0ab6de939aea5fa6cfcab337b3f5899", "57e9703bb7ceded2560681b66267edc7562931c10c08c27eb3fdb7890f24ea62", "8cf68b8868b14eb5d652d4742394ad4ffbf7a875e06b9740adc9cfe361117e3e", "825d6b1aa88778114b4069fdc91bf3d5229368ac0f30380dc0276956ea4b73e9", "afa5bb7a41dbb281c3a65726c237d37ef394c128d103f9523d85fefc62a89138", "31d421b9d0f9f2d34c8339a5605907c5c1c75449141f8f8e0b209edb240494ea", "EXC:AttributeError", "04e63f6d9bd5ef05c865c48baffdf278c0ab6de939aea5fa6cfcab337b3f5899"]

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


@pytest.mark.parametrize("i", range(len(INSIGHT)))
def test_wrapper_and_owner_match_pre_move_golden_and_input_unchanged(i):
    kw = INSIGHT[i]
    snap = copy.deepcopy(kw)
    assert _safe(lambda: F._build_insight_summary(**kw)) == GOLDEN[i]
    assert _safe(lambda: owner.build_insight_summary(facade=F, **kw)) == GOLDEN[i]
    assert kw == snap


def test_exact_sentences():
    f = F._build_insight_summary
    assert f(**INSIGHT[0]) == "Feedback packet is available but source evidence is limited."
    assert f(**INSIGHT[1]) == "Route mix is led by monitor_only 3/6; monitor_only 3/6, cached_strategist 2/6. Top blocker is b1 (4)."
    assert f(**INSIGHT[2]).startswith("Route mix is led by monitor_only 2/4;")                                      # tie -> first max in insertion order
    assert f(**INSIGHT[3]) == ("Route mix is led by x 1/1; monitor_only 0/1, cached_strategist 0/1. "
                               "Same-day closed trade reports show 3 trades with 1 wins, 1 losses, 1 flat, 1 unknown pnl, avg pnl pct 0.25.")
    assert f(**INSIGHT[4]) == "Same-day closed trade reports show 2 trades with 0 wins, 2 losses."                  # no samples -> no avg text
    assert f(**INSIGHT[5]).endswith("Top blocker is None (None). Same-day closed trade reports show 1 trades with 0 wins, 0 losses.")


def test_zero_valued_routes_use_the_recorded_decisions_sentence():
    out = F._build_insight_summary(route_analysis={"route_selected_total": {"a": 1, "b": 0}}, blocker_analysis=[])
    assert out.startswith("Route mix is led by a 1/1;")
    out = F._build_insight_summary(route_analysis={"route_selected_total": {"a": "x", "b": 3}}, blocker_analysis=[])
    assert out == "Route mix is led by b 3/3; monitor_only 0/3, cached_strategist 0/3."


def test_original_exceptions_and_facade_helpers():
    with pytest.raises(AttributeError):
        F._build_insight_summary(**INSIGHT[6])
    import libs.reporting.reporter_feedback as mod
    assert mod is F


def test_facade_helpers_use_time_patches_reach_the_owner(monkeypatch):
    monkeypatch.setattr(F, "_safe_total", lambda c: 50)
    monkeypatch.setattr(F, "_safe_int", lambda v, d=0: 5)
    out = F._build_insight_summary(route_analysis={"route_selected_total": {"monitor_only": 1}}, blocker_analysis=[])
    assert out.startswith("Route mix is led by monitor_only 5/50; monitor_only 5/50, cached_strategist 5/50.") and "show 5 trades with 5 wins, 5 losses, 5 flat, 5 unknown pnl" in out


def test_owner_does_not_import_the_facade_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.reporter_feedback import" not in src and "import reporter_feedback\n" not in src
    assert len(inspect.getsource(F._build_insight_summary).splitlines()) <= 8
