"""P15 order 5: BTC forward_returns / vnext report contracts on synthetic data (pure, no network, no files).

Expectations are the current implementation's exact outputs, derived by hand from the candle series below.
"""
from __future__ import annotations

import copy
import json
from datetime import datetime, timedelta, timezone

import pytest

from libs.reporting.baseline_btc_woori_tech import forward_returns as fr
from libs.reporting.baseline_btc_woori_tech.vnext import report as vr
from libs.reporting.baseline_btc_woori_tech.vnext.contract import VERSION

KST = timezone(timedelta(hours=9))


def ep(h, m):
    return int(datetime(2026, 9, 7, h, m, tzinfo=KST).timestamp())


CANDLES = [{"ts": ep(9, 0) + 60 * i, "open": 100.0 + i, "high": 101.0 + i, "low": 99.0 + i, "close": 100.0 + i, "volume": 10} for i in range(400)]


def decision(did, base_min, price, *, eligible, variants=None, action="BUY"):
    return {"decision_id": did, "generated_at": "g", "eligible": eligible, "action": action,
            "local_features": {"available": True, "baseline_epoch": ep(9, base_min), "baseline_price": price, "baseline_raw_ts": f"0{9}{base_min:02d}"},
            **({"policy_variants": variants} if variants is not None else {})}


DECISIONS = [decision("D1", 3, 103.0, eligible=True, variants={"v2": {"eligible": True}, "v1": {"eligible": False}}),
             decision("D2", 10, 110.0, eligible=False, variants={"v2": {"eligible": False}, "v1": {"eligible": True}}, action="HOLD")]


def test_attach_maps_every_decision_to_one_rank1_target_row_and_does_not_mutate_inputs():
    before = copy.deepcopy(DECISIONS), copy.deepcopy(CANDLES)
    rows = fr.attach_forward_returns(DECISIONS, candles=CANDLES)
    assert (DECISIONS, CANDLES) == before
    assert [(r["baseline_decision_id"], r["symbol"], r["ticker"], r["rank"], r["eligible"], r["action"]) for r in rows] == [("D1", "041190", "041190.KQ", 1, True, "BUY"), ("D2", "041190", "041190.KQ", 1, False, "HOLD")]
    r1, r2 = rows[0]["returns"], rows[1]["returns"]
    assert r1["+5m"] == {"status": "observed", "return_pct": 4.8544, "mfe_pct": 5.8252, "mae_pct": -0.9709, "price": 108.0, "high": 109.0, "low": 102.0, "observed_ts": ep(9, 8)}
    assert r2["+5m"]["return_pct"] == 4.5455 and r2["+5m"]["price"] == 115.0
    assert rows[0]["baseline"]["baseline_price"] == 103.0 and rows[0]["baseline"]["source"] == "baseline_existing_candle_provider"
    assert set(r1) >= {"+5m", "+15m", "+30m", "+60m", "+120m", "+180m", "EOD"} 
    eod = r1["EOD"]                                                                                      # candle series ends 15:39 (>= 15:30): EOD observed from the last row
    assert eod["status"] == "observed" and eod["return_pct"] == round((499.0 / 103.0 - 1) * 100, 4) and eod["price"] == 499.0 and eod["source"] == "last_regular_session_minute"
    assert eod["mae_pct"] == -0.9709 and eod["mfe_pct"] == round((500.0 / 103.0 - 1) * 100, 4)
    assert rows[0]["available"] is True


def test_attach_empty_decisions_and_missing_baseline_are_pending_not_errors():
    assert fr.attach_forward_returns([], candles=CANDLES) == []
    no_base = {"decision_id": "D9", "eligible": True, "action": "BUY", "local_features": {}}
    row = fr.attach_forward_returns([no_base], candles=CANDLES)[0]
    assert row["baseline_decision_id"] == "D9" and row["returns"]["+120m"] == {"status": "pending"} and row["returns"]["EOD"] == {"status": "pending"}
    assert fr.attach_forward_returns([{"decision_id": "D8"}], candles=[])[0]["returns"]["+180m"] == {"status": "pending"}


def test_summarize_one_trade_and_costs_exact():
    rows = fr.attach_forward_returns(DECISIONS[:1], candles=CANDLES)
    h = fr.summarize(rows, cost_pct=0.1, slippage_pct=0.05)["horizons"][0]
    assert h["horizon"] == "+5m" and h["trade_count"] == 1 and h["top1_observation_count"] == 1 and h["both_symbol_window_count"] == 1
    assert h["top1_gross"]["average_return_pct"] == 4.8544 and h["top1_net"]["average_return_pct"] == pytest.approx(4.7044, abs=1e-4)
    assert h["cost_pct"] == 0.1 and h["slippage_pct"] == 0.05 and h["top1_minus_both_average_net_pct"] == 0.0


def test_summarize_multiple_trades_counts_only_eligible_entries_and_top1_over_all():
    rows = fr.attach_forward_returns(DECISIONS, candles=CANDLES)
    h = fr.summarize(rows, cost_pct=0.1, slippage_pct=0.05)["horizons"][0]
    assert h["top1_observation_count"] == 2 and h["trade_count"] == 1 and h["eligible_entries_gross"]["count"] == 1
    assert h["top1_gross"]["average_return_pct"] == pytest.approx((4.8544 + 4.5455) / 2, abs=1e-4)
    assert h["eligible_entries_gross"]["average_return_pct"] == 4.8544


def test_summarize_is_independent_of_input_order_and_empty_input_is_well_formed():
    rows = fr.attach_forward_returns(DECISIONS, candles=CANDLES)
    a = fr.summarize(rows, cost_pct=0.1, slippage_pct=0.05)
    b = fr.summarize(list(reversed(rows)), cost_pct=0.1, slippage_pct=0.05)
    assert a == b
    empty = fr.summarize([], cost_pct=0.1, slippage_pct=0.05)["horizons"]
    assert [h["horizon"] for h in empty][:3] == ["+5m", "+15m", "+30m"] and all(h["trade_count"] == 0 and h["top1_observation_count"] == 0 for h in empty)
    assert all(h["top1_gross"]["count"] == 0 for h in empty)


def test_summarize_policy_variant_reassigns_eligibility_without_mutating_rows():
    rows = fr.attach_forward_returns(DECISIONS, candles=CANDLES)
    snapshot = copy.deepcopy(rows)
    v2 = fr.summarize_policy_variant(rows, DECISIONS, policy_id="v2", cost_pct=0.1, slippage_pct=0.05)["horizons"][0]
    v1 = fr.summarize_policy_variant(rows, DECISIONS, policy_id="v1", cost_pct=0.1, slippage_pct=0.05)["horizons"][0]
    none = fr.summarize_policy_variant(rows, DECISIONS, policy_id="missing", cost_pct=0.1, slippage_pct=0.05)["horizons"][0]
    assert rows == snapshot                                                                           # deep copy: caller rows keep their own eligibility
    assert v2["trade_count"] == 1 and v2["eligible_entries_gross"]["average_return_pct"] == 4.8544
    assert v1["trade_count"] == 1 and v1["eligible_entries_gross"]["average_return_pct"] == 4.5455
    assert none["trade_count"] == 0 and none["top1_observation_count"] == 2                           # unknown policy -> nobody eligible, top1 unaffected


# ---------- vnext aggregate / render ----------

def day_record(phase="PROSPECTIVE", label="FAST_BUY_CANDIDATE", eligible=True, ret=1.0, method="OPEN"):
    feature = {"btc_daily_context": {"market_state": "BULL", "breakout_state": "NO_BREAKOUT"}, "woori_opening": {"reaction": "UP"}, "crypto_equity_confirm": "CONFIRM",
               "crypto_time_alignment": {"gap_type": "OVERNIGHT"}, "entry_methods": {method: {"confirmation": "CONFIRMED"}}}
    return {"features": feature, "phase": phase, "A": {"eligible": eligible}, "B": {"label": label}}


def day(records, outcomes):
    return {"records": records, "outcomes": outcomes}


def outcome(ret):
    return {"status": "OBSERVED", "net_return_pct": ret, "gross_return_pct": ret, "mfe_pct": 1.0, "mae_pct": -1.0, "path_status": "COMPLETE"}


def find(rows, **kw):
    return [r for r in rows if all(r[k] == v for k, v in kw.items())]


def test_aggregate_empty_and_arm_selection_rules():
    assert vr.aggregate([]) == []
    d = day({"OPEN": day_record(eligible=True, label="SKIP"), "PULLBACK": day_record(method="PULLBACK", eligible=False, label="WAIT_PULLBACK_CANDIDATE")},
            {"OPEN": {"09:30": outcome(2.0)}, "PULLBACK": {"09:30": outcome(-1.0)}})
    rows = vr.aggregate([d])
    a_open = find(rows, axis="arm", value="A", method="OPEN", horizon="09:30")[0]
    b_open = find(rows, axis="arm", value="B", method="OPEN", horizon="09:30")
    assert a_open["metrics"]["evaluable_count"] == 1 and a_open["metrics"]["avg_return_pct"] == 2.0 and b_open == []                          # B needs FAST_BUY (or PULLBACK+WAIT)
    assert find(rows, axis="arm", value="B", method="PULLBACK", horizon="09:30")[0]["metrics"]["avg_return_pct"] == -1.0                      # WAIT_PULLBACK counts for PULLBACK only
    assert find(rows, axis="arm", value="A", method="PULLBACK", horizon="09:30") == []                                                       # A requires eligible


def test_aggregate_matched_opportunity_control_and_label_axes_and_missing_horizons():
    d = day({"OPEN": day_record(eligible=False, label="SKIP")}, {"OPEN": {"09:30": outcome(3.0)}})
    rows = vr.aggregate([d])
    opp = find(rows, phase="PROSPECTIVE", axis="opportunity", value="ALL", method="OPEN", horizon="09:30")[0]["metrics"]
    assert opp["signal_count"] == 1 and opp["evaluable_count"] == 1 and opp["missing_evidence_count"] == 0 and opp["review_state"] == "ANECDOTAL_ONLY"
    eod = find(rows, axis="opportunity", horizon="EOD")[0]["metrics"]
    assert eod["signal_count"] == 1 and eod["evaluable_count"] == 0 and eod["missing_evidence_count"] == 1 and eod["avg_return_pct"] is None and eod["win_rate"] is None
    axes = {r["axis"] for r in rows}
    assert axes >= {"opportunity", "surge", "session_gap", "breakout", "reaction", "crypto_equity", "surge_x_equity", "local", "shadow_label"}
    assert find(rows, axis="surge_x_equity", value="BULL|CONFIRM", horizon="09:30") and find(rows, axis="session_gap", value="OVERNIGHT", horizon="09:30")
    assert [(r["phase"], r["axis"], r["value"], r["method"], r["horizon"]) for r in rows] == sorted((r["phase"], r["axis"], r["value"], r["method"], r["horizon"]) for r in rows)


def test_aggregate_accumulates_across_days_and_defaults_unknown_gap_type():
    r1 = day_record(eligible=True)
    r2 = day_record(eligible=True)
    del r2["features"]["crypto_time_alignment"]
    rows = vr.aggregate([day({"OPEN": r1}, {"OPEN": {"10:00": outcome(1.0)}}), day({"OPEN": r2}, {"OPEN": {"10:00": outcome(3.0)}})])
    m = find(rows, axis="arm", value="A", method="OPEN", horizon="10:00")[0]["metrics"]
    assert m["evaluable_count"] == 2 and m["avg_return_pct"] == 2.0 and m["median_return_pct"] == 2.0
    assert find(rows, axis="session_gap", value="UNKNOWN", horizon="10:00")[0]["metrics"]["signal_count"] == 1


def test_review_state_thresholds_follow_evaluable_count():
    days = [day({"OPEN": day_record()}, {"OPEN": {"EOD": outcome(1.0)}}) for _ in range(30)]
    state = lambda n: find(vr.aggregate(days[:n]), axis="arm", value="A", method="OPEN", horizon="EOD")[0]["metrics"]["review_state"]  # noqa: E731
    assert (state(9), state(10), state(19), state(20), state(29), state(30)) == ("ANECDOTAL_ONLY", "PRELIMINARY", "PRELIMINARY", "INSUFFICIENT_FOR_PROMOTION", "INSUFFICIENT_FOR_PROMOTION", "REVIEW_ELIGIBLE_NOT_STATISTICAL_PROOF")


def test_render_exact_structure_and_none_float_formatting():
    payload = {"day": "2026-09-07", "evidence_status": "AVAILABLE", "current_features": {"k": "한"},
               "summary": [{"phase": "P", "axis": "a|b", "value": "v", "method": "OPEN", "horizon": "09:30",
                            "metrics": {"signal_count": 2, "evaluable_count": 1, "missing_evidence_count": 1, "win_rate": 0.5, "avg_return_pct": 1.23456, "median_return_pct": None,
                                        "profit_factor": 2, "avg_mfe_pct": None, "avg_mae_pct": -0.5, "review_state": "ANECDOTAL_ONLY"}}]}
    md = vr.render(payload)
    lines = md.splitlines()
    assert lines[0] == "# Q12 vNext Forward Validation" and f"- Version: `{VERSION}`" in lines and "- Through: 2026-09-07" in lines and "- Evidence: AVAILABLE" in lines
    assert "| P | a/b | v | OPEN | 09:30 | 2 | 1 | 1 | 0.5000 | 1.2346 | - | 2 | - | -0.5000 | ANECDOTAL_ONLY |" in lines                      # '|' escaped, floats 4dp, None as '-', int untouched
    assert json.loads(md.split("```json\n")[1].split("\n```")[0]) == {"k": "한"} and md.endswith("\n")
    assert "120-day available high is not an all-time high" in md and "Shadow only." in md
    empty = vr.render({"day": "d", "evidence_status": "INSUFFICIENT_EVIDENCE", "summary": []})
    assert "{}" in empty and not [l for l in empty.splitlines() if l.startswith("| P ")] and sum(1 for l in empty.splitlines() if l.startswith("|---|---|---|---|---|")) == 1


def test_render_zero_values_are_not_dashes():
    payload = {"day": "d", "evidence_status": "X", "summary": [{"phase": "P", "axis": "a", "value": "v", "method": "M", "horizon": "h",
                                                               "metrics": {"signal_count": 0, "evaluable_count": 0, "missing_evidence_count": 0, "win_rate": 0.0, "avg_return_pct": 0, "review_state": "ANECDOTAL_ONLY"}}]}
    assert "| P | a | v | M | h | 0 | 0 | 0 | 0.0000 | 0 | - | - | - | - | ANECDOTAL_ONLY |" in vr.render(payload).splitlines()


def test_variant_summary_treats_rows_without_a_matching_decision_as_not_eligible():
    rows = fr.attach_forward_returns(DECISIONS, candles=CANDLES)
    extra = copy.deepcopy(rows[0])
    extra["baseline_decision_id"] = "UNKNOWN"
    extra["eligible"] = True
    h = fr.summarize_policy_variant(rows + [extra], DECISIONS, policy_id="v2", cost_pct=0.1, slippage_pct=0.05)["horizons"][0]
    assert h["trade_count"] == 1                                                                         # the unknown-id row is forced to eligible=False
