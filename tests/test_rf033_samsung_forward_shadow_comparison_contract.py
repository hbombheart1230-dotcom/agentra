"""RF-033 C3: samsung forward_validation shadow_comparison (pure) - direction, costs, pending, pullback, summaries."""
from __future__ import annotations

import pytest

from libs.reporting.baseline_samsung_hynix.forward_validation import shadow_comparison as sh


def _pt(ts, price):
    return {"ts": ts, "price": price}


def _exp(target="samsung", state="POSITIVE", reaction="FAIR_REACTION", **kw):
    return {"target": target, "expected_state": state, "reaction_state": reaction, "evaluation_bucket": "LEAD_MARKET_SIGNAL", "extension_state": None, **kw}


def _reaction(path_closes, points=None, base_ts=1000, pad=True):
    if pad:
        path_closes = list(path_closes) + [path_closes[-1]] * max(0, 12 - len(path_closes))   # keep a future row for every entry policy
    path = [{"ts": base_ts + 60 * i, "close": c} for i, c in enumerate(path_closes)]
    pts = {"09:00": _pt(base_ts, path_closes[0]), "09:03": _pt(base_ts + 180, path_closes[3]),
           "09:05": _pt(base_ts + 300, path_closes[-1]), "09:10": _pt(base_ts + 600, path_closes[-1]), "CLOSE": _pt(base_ts + 3600, path_closes[-1])}
    pts.update(points or {})
    return {"path": path, "points": pts}


def _run(rows, reactions, cost=0.1, slip=0.05):
    return sh.build_shadow_comparison(expected_actual={"rows": rows}, reactions={"targets": reactions}, cost_pct=cost, slippage_pct=slip)


def test_direction_mapping():
    d = sh._direction
    assert [d(s) for s in ("STRONG_POSITIVE", "POSITIVE", "STRONG_RISK_ON", "RISK_ON")] == [1] * 4
    assert [d(s) for s in ("STRONG_NEGATIVE", "NEGATIVE", "STRONG_RISK_OFF", "RISK_OFF")] == [-1] * 4
    assert d("NEUTRAL") == 0 and d("???") == 0


def test_metric_edges():
    assert sh._metric([]) == {"trade_count": 0, "win_rate": None, "average_return_pct": None, "median_return_pct": None, "profit_factor": None, "max_drawdown_pct": None}
    m = sh._metric([2.0, -3.0, -1.0])
    assert m["max_drawdown_pct"] == -4.0 and m["profit_factor"] == 0.5 and m["win_rate"] == pytest.approx(33.3333) and m["median_return_pct"] == -1.0
    assert sh._metric([1.0])["profit_factor"] == "INF" and sh._metric([-1.0])["profit_factor"] == 0.0 and sh._metric([0.0])["profit_factor"] is None


def test_long_observed_outcome_costs_mfe_mae_and_status():
    r = _reaction([100.0, 101.0, 99.0, 102.0, 103.0], points={"CLOSE": _pt(9999, 110.0)})
    out = _run([_exp()], {"samsung": r})
    o = {x["policy"]: x for x in out["outcomes"]}
    assert set(o) == {"ENTRY_0900", "ENTRY_0903", "ENTRY_0905", "ENTRY_0910", "FIRST_PULLBACK_ENTRY"}
    e = o["ENTRY_0900"]
    assert e["status"] == "OBSERVED" and e["entry_price"] == 100.0 and e["exit_price"] == 110.0
    assert e["gross_eod_return_pct"] == 10.0 and e["net_eod_return_pct"] == pytest.approx(9.85)       # minus cost 0.1 + slippage 0.05
    assert e["mfe_pct"] == 3.0 and e["mae_pct"] == -1.0
    assert o["FIRST_PULLBACK_ENTRY"]["status"] == "PENDING"                                            # only when OVERREACTION
    assert out["cost_model"] == {"round_trip_cost_pct": 0.1, "slippage_pct": 0.05, "total_pct": pytest.approx(0.15)}
    assert out["evidence_status"] == "AVAILABLE"


def test_short_direction_flips_sign_of_returns_and_excursions():
    r = _reaction([100.0, 99.0, 101.0, 98.0], points={"CLOSE": _pt(9999, 90.0)})
    e = {x["policy"]: x for x in _run([_exp(state="STRONG_RISK_OFF")], {"samsung": r})["outcomes"]}["ENTRY_0900"]
    assert e["gross_eod_return_pct"] == 10.0 and e["mfe_pct"] == 2.0 and e["mae_pct"] == -1.0


def test_neutral_expectation_produces_no_outcomes_and_no_summary_rows_for_it():
    out = _run([_exp(state="NEUTRAL")], {"samsung": _reaction([100.0, 101.0])})
    assert out["outcomes"] == [] and out["evidence_status"] == "INSUFFICIENT_EVIDENCE"
    assert len(out["summary"]) == 5 and all(s["trade_count"] == 0 for s in out["summary"])          # summary still lists every target x policy


def test_pending_when_entry_or_close_missing_or_zero():
    base = _reaction([100.0, 101.0, 102.0, 103.0])
    no_entry = dict(base, points={k: v for k, v in base["points"].items() if k != "09:03"})
    out = {x["policy"]: x["status"] for x in _run([_exp()], {"samsung": no_entry})["outcomes"]}
    assert out["ENTRY_0903"] == "PENDING" and out["ENTRY_0900"] == "OBSERVED"
    zero_entry = dict(base, points={**base["points"], "09:00": _pt(1000, 0)})
    assert {x["policy"]: x["status"] for x in _run([_exp()], {"samsung": zero_entry})["outcomes"]}["ENTRY_0900"] == "PENDING"
    no_close = dict(base, points={k: v for k, v in base["points"].items() if k != "CLOSE"})
    assert {x["status"] for x in _run([_exp()], {"samsung": no_close})["outcomes"]} == {"PENDING"}
    pend = _run([_exp()], {"samsung": no_close})["outcomes"][0]
    assert pend == {"target": "samsung", "policy": "ENTRY_0900", "status": "PENDING", "expected_state": "POSITIVE"}
    assert _run([_exp()], {})["outcomes"][0]["status"] == "PENDING"                                  # target without reaction


def test_first_pullback_triggers_on_retrace_from_running_extreme_within_one_hour():
    closes = [100.0, 102.0, 104.0, 103.4, 103.0]                    # extreme 104 -> 0.5% retrace = 103.48 -> 103.4 triggers at idx 3
    r = _reaction(closes)
    entry = sh._first_pullback_entry(r, 1)
    assert entry == {"ts": 1000 + 180, "price": 103.4}
    out = {x["policy"]: x for x in _run([_exp(reaction="OVERREACTION")], {"samsung": dict(r, points={**r["points"], "CLOSE": _pt(9999, 105.0)})})["outcomes"]}
    assert out["FIRST_PULLBACK_ENTRY"]["status"] == "OBSERVED" and out["FIRST_PULLBACK_ENTRY"]["entry_price"] == 103.4


def test_first_pullback_edges():
    assert sh._first_pullback_entry({"path": []}, 1) is None and sh._first_pullback_entry(_reaction([100.0, 99.0]), 0) is None
    assert sh._first_pullback_entry(_reaction([100.0, 100.0, 100.4]), 1) is None                    # exactly-not-enough retrace
    exact = 100.0 * (1 - 0.005)
    assert sh._first_pullback_entry(_reaction([100.0, exact]), 1) is not None                       # boundary is inclusive
    late = {"path": [{"ts": 0, "close": 100.0}, {"ts": 3601, "close": 90.0}]}
    assert sh._first_pullback_entry(late, 1) is None                                                # beyond 60 minutes
    on_time = {"path": [{"ts": 0, "close": 100.0}, {"ts": 3600, "close": 90.0}]}
    assert sh._first_pullback_entry(on_time, 1)["price"] == 90.0                                    # exactly 60 minutes is included
    skip_bad = {"path": [{"ts": 0, "close": 100.0}, {"ts": 60, "close": 0}, {"ts": 120, "close": 99.0}]}
    assert sh._first_pullback_entry(skip_bad, 1)["ts"] == 120
    short = _reaction([100.0, 98.0, 98.6])                          # short: running low 98, +0.5% = 98.49 -> 98.6 triggers
    assert sh._first_pullback_entry(short, -1) == {"ts": 1000 + 120, "price": 98.6}


def test_summary_aggregates_per_target_policy_and_only_observed():
    r1 = _reaction([100.0, 101.0, 102.0, 103.0], points={"CLOSE": _pt(9999, 110.0)})
    r2 = _reaction([100.0, 99.0, 98.0, 97.0], points={"CLOSE": _pt(9999, 95.0)})
    out = _run([_exp("samsung"), _exp("sk_hynix", state="NEGATIVE")], {"samsung": r1, "sk_hynix": r2})
    by = {(s["target"], s["policy"]): s for s in out["summary"]}
    s = by[("samsung", "ENTRY_0900")]
    assert s["trade_count"] == 1 and s["average_return_pct"] == pytest.approx(9.85) and s["average_eod_return_pct"] == s["average_return_pct"]
    assert s["average_mfe_pct"] == 3.0 and s["average_mae_pct"] == 0.0
    h = by[("sk_hynix", "ENTRY_0900")]
    assert h["average_return_pct"] == pytest.approx(4.85) and h["average_mfe_pct"] == 3.0
    assert by[("samsung", "FIRST_PULLBACK_ENTRY")]["trade_count"] == 0 and by[("samsung", "FIRST_PULLBACK_ENTRY")]["average_mfe_pct"] is None
    assert len(out["summary"]) == 10


def test_observed_outcome_without_future_path_rows_crashes_summary_with_typeerror():
    """BASE defect candidate (pinned current behavior): an OBSERVED outcome whose entry has no later path row gets
    mfe/mae None, then the summary does float(None) and the whole comparison raises instead of degrading."""
    r = {"path": [], "points": {"09:00": _pt(1000, 100.0), "CLOSE": _pt(9999, 101.0)}}
    with pytest.raises(TypeError):
        _run([_exp()], {"samsung": r})


def test_first_pullback_short_side_boundary_is_inclusive():
    exact = 98.0 * (1.0 + 0.005)
    assert sh._first_pullback_entry(_reaction([100.0, 98.0, exact]), -1) == {"ts": 1000 + 120, "price": exact}
    assert sh._first_pullback_entry(_reaction([100.0, 98.0, exact - 0.01]), -1) is None
