"""RF-031 libs/reporting/trade_story_pipeline_human_payloads: pure payload contracts.

Drives ``build_monitor_reason_human`` through the public facade
(``libs.reporting.trade_story_pipeline``) with synthetic monitor/execution
dicts, plus the small pure helpers. Measured at 78% before this file. No IO,
LLM or network. Explicit raises keep the checks live under ``python -O``.
"""
from __future__ import annotations

import pytest

from libs.reporting import trade_story_pipeline as pipe
from libs.reporting import trade_story_pipeline_human_payloads as hp


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


def test_normalize_stop_thresholds_prefers_nested_and_tolerates_non_dict():
    _eq(hp.normalize_stop_thresholds({"thresholds": {"a": 1}, "b": 2}), {"a": 1})
    _eq(hp.normalize_stop_thresholds({"b": 2}), {"b": 2})
    _eq(hp.normalize_stop_thresholds({"thresholds": {}, "b": 2}), {"thresholds": {}, "b": 2})   # empty nested -> the outer dict
    _eq(hp.normalize_stop_thresholds(None), {})
    _eq(hp.normalize_stop_thresholds("x"), {})


def test_adaptive_stop_loss_resolution_order():
    full = {"adaptive_exit": {"stop_loss_pct": 1.5}, "threshold_snapshot": {"adaptive_stop_loss_pct": 3.5}}
    _eq(hp.resolve_adaptive_stop_loss_pct(full, {"adaptive_stop_loss_pct": 2.5}), 1.5)                 # adaptive_exit first
    _eq(hp.resolve_adaptive_stop_loss_pct({"threshold_snapshot": full["threshold_snapshot"]}, {"adaptive_stop_loss_pct": 2.5}), 2.5)   # then thresholds
    _eq(hp.resolve_adaptive_stop_loss_pct({"threshold_snapshot": full["threshold_snapshot"]}, {}), 3.5)                                    # then the snapshot
    _eq(hp.resolve_adaptive_stop_loss_pct({}, {}), None)
    _eq(hp.resolve_adaptive_stop_loss_pct({"adaptive_exit": {"stop_loss_pct": ""}}, {"thresholds": {"adaptive_stop_loss_pct": 0}}), 0)   # 0 counts as present, "" does not
    _eq(hp.resolve_adaptive_stop_loss_pct({"adaptive_exit": "x", "threshold_snapshot": "y"}, {}), None)


def _human(monitor, execution=None):
    return pipe.build_monitor_reason_human(monitor, execution or {})


def test_buy_summary_includes_pattern_and_path():
    r = _human({"entry_reason": "breakout", "entry_pattern": "pullback", "entry_condition_path": "vwap_reclaim"}, {"action": "BUY"})
    _eq((r["posture"], r["summary"]), ("BUY", "BUY was triggered because breakout. Pattern: pullback. Path: vwap reclaim."))


def test_sell_variants():
    plain = _human({"exit_reason": "stop_loss", "exit_triggered": True}, {"action": "SELL"})
    _eq((plain["posture"], plain["summary"]), ("SELL", "SELL was triggered because stop_loss."))
    mismatch = _human({"monitor_reason": "hold", "guard_reason": "min hold"}, {"action": "SELL"})
    if "monitor/executor mismatch" not in mismatch["summary"] or "(min hold)" not in mismatch["summary"]:
        raise AssertionError(mismatch["summary"])
    if not any(b.startswith("Monitor/executor mismatch: yes") for b in mismatch["bullets"]):
        raise AssertionError(mismatch["bullets"])
    flat = _human({"eod_carry_evaluated": True, "eod_carry_reason": "weak close", "trigger_type": "eod_flat", "exit_triggered": True}, {"action": "SELL"})
    _eq(flat["summary"], "SELL was triggered to flatten before the close because overnight carry was not approved (weak close).")
    # a SELL with a confirmed exit is never labelled a mismatch
    _eq("mismatch" in _human({"monitor_reason": "hold", "exit_triggered": True}, {"action": "SELL"})["summary"], False)


def test_wait_variants_and_eod_carry_bullets():
    approved = _human({"eod_carry_evaluated": True, "eod_carry_approved": True, "eod_carry_reason": "strong", "minutes_to_close": 12.34,
                       "eod_carry_positive_signals": ["a", "b"], "eod_carry_blockers": ["c"]})
    _eq(approved["summary"], "Monitor kept the position into the close because overnight carry was approved 12.3 minutes before the close.")
    b = approved["bullets"]
    for want in ("EOD carry decision: approved (strong)", "Minutes to close at decision: 12.3", "Carry positives: a; b", "Carry blockers: c"):
        if want not in b:
            raise AssertionError((want, b))
    anomaly = _human({"eod_carry_anomaly": True, "eod_carry_anomaly_reason": "no clock"})
    _eq(anomaly["summary"], "Monitor kept the position without a valid end-of-day carry decision because no clock.")
    if "EOD carry anomaly: yes (no clock)" not in anomaly["bullets"]:
        raise AssertionError(anomaly["bullets"])
    wait = _human({"entry_evaluated": True, "entry_check_summary": "score low"})
    _eq(wait["summary"], "Monitor stayed on WAIT because the intraday entry signal was not confirmed.")   # observed: a plain monitor['entry_check_summary'] key does NOT reach the summary text
    _eq(_human({})["summary"], "Monitor posture was WAIT with trigger not_captured.")
    _eq(_human({"trigger_type": "x"})["summary"], "Monitor posture was WAIT with trigger x.")


def test_common_bullets_and_optional_price_block():
    r = _human({"position_age_seconds": 61, "hold_limit_sec": 120, "current_price": 100.0, "average_price": "99.5", "peak_price": 101,
                "current_drawdown": 0.01, "vwap_distance": 0.002, "price_source": "kiwoom", "feature_source": "hydration",
                "price_source_policy": "prefer_live", "min_hold_blocked": True, "sell_cooldown_blocked": True, "exit_triggered": True,
                "guard_blocked": True, "guard_reason": "cooldown",
                "decision_reason_chain": ["a", "b"], "watch_axes": ["x"], "exit_confirm_count": 1, "exit_confirm_required": 2})
    b = r["bullets"]
    for want in ("Posture: WAIT", "Position age: 61 seconds", "Hold time limit: 120 seconds", "Min hold blocked: yes", "Sell cooldown blocked: yes",
                 "Exit triggered: yes", "Guard blocked: yes (cooldown)", "Decision chain: a -> b", "Current price: 100.00", "Average price: 99.50",
                 "Peak price: 101.00", "Price source: kiwoom", "Feature source: hydration", "Price source policy: prefer_live"):
        if want not in b:
            raise AssertionError((want, b))
    _eq((r["position_age_seconds"], r["hold_limit_sec"]), (61, 120))
    base = _human({})
    _eq([x for x in base["bullets"] if x.startswith(("Current price", "Average price", "Peak price", "Price source", "Feature source"))], [])
    if "Hold time limit: not configured" not in base["bullets"] or "Exit confirmation: not required" not in base["bullets"]:
        raise AssertionError(base["bullets"])


def test_quant_decisions_and_time_limit_reassessment_bullets():
    r = _human({"entry_quant_decision": {"decision": "block", "blockers": ["b1", "b2"], "warnings": ["w1"]},
                "exit_quant_decision": {"decision": "hold", "blockers": [], "warnings": []},
                "time_limit_reassessment_required": True, "time_limit_reassessment_blocked": True,
                "time_limit_reassessment_blocked_reason": "profit floor", "hold_limit_sec": 30})
    b = r["bullets"]
    for want in ("Entry quant decision: block (blockers: b1, b2; warnings: w1)", "Exit quant decision: hold (blockers: none; warnings: none)",
                 "Time-limit reassessment: blocked by profit floor (profit floor)"):
        if want not in b:
            raise AssertionError((want, b))


def test_input_dicts_are_not_mutated():
    monitor = {"thresholds": {"stop_loss_pct": 0.02}, "decision_reason_chain": ["a"]}
    execution = {"action": "SELL"}
    before = (repr(monitor), repr(execution))
    _human(monitor, execution)
    _eq((repr(monitor), repr(execution)), before)
