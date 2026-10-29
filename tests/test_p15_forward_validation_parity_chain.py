"""P15 order 4: reaction -> scoring -> shadow comparison -> report chain through the real consumers (no adapters), plus the
shadow_comparison empty-path summary defect (OBSERVED outcome with mfe/mae None used to crash the summary with float(None)).

Files only under tmp_path; the Kiwoom collector module is replaced in sys.modules; no network.
"""
from __future__ import annotations

import json
import sys
import types
from datetime import datetime, timedelta, timezone

import pytest

from libs.reporting.baseline_samsung_hynix.forward_validation import expected_actual as ea
from libs.reporting.baseline_samsung_hynix.forward_validation import reaction_reader as rr
from libs.reporting.baseline_samsung_hynix.forward_validation import report as rp
from libs.reporting.baseline_samsung_hynix.forward_validation import scoring as sc
from libs.reporting.baseline_samsung_hynix.forward_validation import shadow_comparison as sh

KST = timezone(timedelta(hours=9))
DAY = "2026-09-07"


def ep(h, m, s=0):
    return int(datetime(2026, 9, 7, h, m, s, tzinfo=KST).timestamp())


def candle(ts, close, *, volume=100.0, open_=None):
    return {"ts": ts, "open": close if open_ is None else open_, "high": close, "low": close, "close": close, "volume": volume}


@pytest.fixture
def collector(monkeypatch):
    st = {"obs": {"availability": "MISSING", "never_attempted": True}, "evidence": True}
    mod = types.ModuleType("libs.market.q10_index_observation_collector")
    mod.observation_for_slot = lambda day, slot, root=None: st["obs"] if not callable(st["obs"]) else st["obs"](slot)
    mod._has_verification_evidence = lambda indices, **kw: st["evidence"]
    monkeypatch.setitem(sys.modules, "libs.market.q10_index_observation_collector", mod)
    return st


def macro(root, name, at, idx):
    d = root / DAY
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(json.dumps({"generated_at": at, "korea_indices": {"indices": idx}}), encoding="utf-8")


def snapshot_inputs(sox=6.0):
    return {"sox_return_pct": sox, "nvidia_return_pct": 1.0, "nasdaq_return_pct": 1.0, "sp500_return_pct": 1.0, "hynix_previous_close": 100.0, "samsung_previous_close": 100.0}


def run_chain(tmp_path, *, candle_map, inputs, collector_root=None):
    reactions = rr.build_actual_reactions(day=DAY, candle_map=candle_map, macro_root=tmp_path, signal_inputs=inputs, collector_root=collector_root)
    signals = {"sk_hynix": sc.score_semiconductor_signal(inputs), "samsung": sc.score_semiconductor_signal(inputs, samsung=True),
               "hynix_extension": sc.classify_hynix_extension(inputs), "korea_market": sc.score_korea_market_state(inputs)}
    expected = ea.build_expected_actual(signals=signals, reactions=reactions, samsung_event={})
    shadow = sh.build_shadow_comparison(expected_actual=expected, reactions=reactions, cost_pct=0.1, slippage_pct=0.05)
    md = rp.render_forward_validation_report(day=DAY, preopen={"capture_status": "CAPTURED", "signals": signals, "samsung_event": {}}, reactions=reactions,
                                             expected_actual=expected, shadow=shadow, cumulative={"day_count": 0, "observed_outcome_count": 0, "summary": []})
    return reactions, signals, expected, shadow, md


def stock_path(open_price=100.0, close=110.0):
    rows = [candle(ep(9, 0), open_price, volume=0.0), candle(ep(9, 1), open_price), candle(ep(9, 3), open_price + 1), candle(ep(9, 5), open_price + 2), candle(ep(9, 10), open_price + 3)]
    rows += [candle(ep(9, 15) + 60 * i, open_price + 3) for i in range(0, 8)] + [candle(ep(15, 25), close - 1), candle(ep(15, 30), close)]
    return rows


def test_chain_end_to_end_with_real_consumers(tmp_path, collector):
    macro(tmp_path, "a_macro_indicators.json", "2026-09-07T00:00:00Z", {"KOSPI": {"current": 2500, "previous_close": 2490}})
    reactions, signals, expected, shadow, md = run_chain(tmp_path, candle_map={"005930": stock_path(), "000660": stock_path(200.0, 210.0)}, inputs=snapshot_inputs())
    assert list(reactions["targets"]) == ["samsung", "sk_hynix", "kospi", "kosdaq"] and [r["target"] for r in expected["rows"]] == ["samsung", "sk_hynix", "kospi", "kosdaq"]
    s = reactions["targets"]["samsung"]
    assert s["points"]["09:00"]["ts"] == ep(9, 1) and s["points"]["09:00"]["price"] == 100.0           # ③ 09:00 volume=0 placeholder excluded
    assert s["points"]["CLOSE"]["price"] == 110.0 and s["forward_windows"]["09:00"]["return_to_close_pct"] == 10.0
    assert signals["samsung"]["state"] == "POSITIVE" and signals["sk_hynix"]["state"] == "STRONG_POSITIVE"
    outcome = next(o for o in shadow["outcomes"] if o["target"] == "samsung" and o["policy"] == "ENTRY_0900")
    assert outcome["status"] == "OBSERVED" and outcome["entry_price"] == 100.0 and outcome["exit_price"] == 110.0 and outcome["net_eod_return_pct"] == pytest.approx(9.85)
    assert "# Q10 Korea Lead-Market Forward Validation" in md and "| samsung | ENTRY_0900 |" in md and md.endswith("\n")


def test_close_less_index_reference_price_never_enters_returns_or_entries(tmp_path, collector):
    macro(tmp_path, "a_macro_indicators.json", "2026-09-07T06:15:00Z", {"KOSPI": {"current": 2500, "previous_close": 2490}})            # 15:15 KST last snapshot
    reactions, signals, expected, shadow, md = run_chain(tmp_path, candle_map={}, inputs={**snapshot_inputs(), "sox_return_pct": 6.0})
    k = reactions["targets"]["kospi"]
    assert k["points"]["CLOSE"]["status"] == "PENDING" and k["points"]["CLOSE"]["price"] is None                                         # ① reference stays out of CLOSE
    assert k["last_available_point_before_close"]["price"] == 2500.0 and all(w["return_to_close_pct"] is None for w in k["forward_windows"].values())
    assert [o for o in shadow["outcomes"] if o["target"] == "kospi" and o["status"] == "OBSERVED"] == []
    assert all(o["status"] == "PENDING" for o in shadow["outcomes"] if o["target"] == "kospi")
    assert "2500" not in "".join(l for l in md.splitlines() if l.startswith("| kospi | ENTRY"))


def test_verified_collector_close_displayed_and_returned_with_one_price(tmp_path, collector):
    macro(tmp_path, "a_macro_indicators.json", "2026-09-07T00:00:00Z", {"KOSPI": {"current": 2500, "previous_close": 2500, "open": 2500}})
    collector["obs"] = lambda slot: ({"availability": "AVAILABLE", "actual_observed_at_kst": "2026-09-07T15:30:05+09:00", "source": "kiwoom.ka20009",
                                      "indices": {"KOSPI": {"current": 2750.0, "market_observed_at": "2026-09-07T15:30:00+09:00"}}} if slot == "15:30"
                                     else {"availability": "MISSING", "never_attempted": True})
    reactions, *_ , md = run_chain(tmp_path, candle_map={}, inputs=snapshot_inputs())
    k = reactions["targets"]["kospi"]
    assert k["points"]["CLOSE"]["price"] == 2750.0 and k["points"]["CLOSE"]["source"] == "q10_index_observation_collector"             # ② display
    assert k["points"]["CLOSE"]["return_from_previous_close_pct"] == 10.0
    assert "2750.0000" in md


def test_previous_close_zero_or_missing_gives_none_not_division_error(tmp_path, collector):
    for prev in (0.0, None):
        inputs = {**snapshot_inputs(), "samsung_previous_close": prev}
        reactions, signals, expected, shadow, md = run_chain(tmp_path, candle_map={"005930": stock_path()}, inputs=inputs)
        s = reactions["targets"]["samsung"]
        assert s["opening_gap_pct"] is None and s["points"]["09:05"]["return_from_previous_close_pct"] is None and s["day_high_return_pct"] is None
        row = next(r for r in expected["rows"] if r["target"] == "samsung")
        assert row["opening_gap_pct"] is None and row["reaction_state"] == "INSUFFICIENT_EVIDENCE"
        assert any(o["target"] == "samsung" and o["status"] == "OBSERVED" for o in shadow["outcomes"])                                 # entries still computed from prices


def test_missing_scoring_inputs_flow_as_insufficient_evidence(tmp_path, collector):
    reactions, signals, expected, shadow, md = run_chain(tmp_path, candle_map={"005930": stock_path()}, inputs={})
    assert signals["samsung"]["confidence"] == "INSUFFICIENT_EVIDENCE" and signals["sk_hynix"]["score"] is None and signals["korea_market"]["evidence_status"] == "INSUFFICIENT_EVIDENCE"
    assert all(r["expected_state"] == "NEUTRAL" for r in expected["rows"]) and shadow["outcomes"] == [] and shadow["evidence_status"] == "INSUFFICIENT_EVIDENCE"
    assert "INSUFFICIENT_EVIDENCE" in md


def test_no_trade_day_empty_inputs_render_without_rows_and_stable_order(tmp_path, collector):
    reactions, signals, expected, shadow, md = run_chain(tmp_path, candle_map={}, inputs={})
    assert shadow["outcomes"] == [] and len(shadow["summary"]) == 4 * 5 and [s["target"] for s in shadow["summary"][:5]] == ["samsung"] * 5
    assert [s["policy"] for s in shadow["summary"][:5]] == ["ENTRY_0900", "ENTRY_0903", "ENTRY_0905", "ENTRY_0910", "FIRST_PULLBACK_ENTRY"]
    assert all(s["trade_count"] == 0 for s in shadow["summary"]) and md.count("\n| samsung | ENTRY_") == 4 and md.count("\n| samsung | FIRST_PULLBACK_ENTRY") == 1


# ---------- shadow_comparison empty-path defect ----------

def _expected(state="POSITIVE", reaction="FAIR_REACTION"):
    return {"rows": [{"target": "samsung", "expected_state": state, "reaction_state": reaction, "evaluation_bucket": "LEAD_MARKET_SIGNAL", "extension_state": None}]}


def _reaction(points, path):
    return {"targets": {"samsung": {"points": points, "path": path}}}


def _summary_row(out, policy="ENTRY_0900"):
    return next(s for s in out["summary"] if s["target"] == "samsung" and s["policy"] == policy)


def test_empty_path_observed_outcome_no_longer_crashes_summary():
    pts = {"09:00": {"ts": 1, "price": 100}, "CLOSE": {"price": 110}}
    out = sh.build_shadow_comparison(expected_actual=_expected(), reactions=_reaction(pts, []), cost_pct=0, slippage_pct=0)
    o = next(x for x in out["outcomes"] if x["policy"] == "ENTRY_0900")
    assert o["status"] == "OBSERVED" and o["gross_eod_return_pct"] == 10.0 and o["net_eod_return_pct"] == 10.0 and o["mfe_pct"] is None and o["mae_pct"] is None
    s = _summary_row(out)
    assert s["trade_count"] == 1 and s["average_return_pct"] == 10.0 and s["average_eod_return_pct"] == 10.0
    assert s["average_mfe_pct"] is None and s["average_mae_pct"] is None                                      # no valid observation -> None (not 0.0)
    assert out["evidence_status"] == "AVAILABLE"


def _two_reactions(path_a, path_b):
    return {"targets": {"samsung": {"points": {"09:00": {"ts": 1, "price": 100}, "CLOSE": {"price": 110}}, "path": path_a}, "sk_hynix": {"points": {"09:00": {"ts": 1, "price": 100}, "CLOSE": {"price": 120}}, "path": path_b}}}


def test_mixed_empty_and_normal_paths_average_only_observable_values():
    path = [{"ts": 1, "close": 103.0}, {"ts": 2, "close": 98.0}, {"ts": 3, "close": 110.0}]
    exp = {"rows": [{"target": "samsung", "expected_state": "POSITIVE", "reaction_state": "FAIR_REACTION", "evaluation_bucket": "B", "extension_state": None},
                    {"target": "sk_hynix", "expected_state": "POSITIVE", "reaction_state": "FAIR_REACTION", "evaluation_bucket": "B", "extension_state": None}]}
    out = sh.build_shadow_comparison(expected_actual=exp, reactions=_two_reactions([], path), cost_pct=0, slippage_pct=0)
    a, b = _summary_row(out), next(s for s in out["summary"] if s["target"] == "sk_hynix" and s["policy"] == "ENTRY_0900")
    assert a["average_mfe_pct"] is None and a["average_mae_pct"] is None and a["trade_count"] == 1
    assert b["average_mfe_pct"] == 10.0 and b["average_mae_pct"] == -2.0 and b["average_return_pct"] == 20.0


def test_two_observations_same_target_policy_average_mfe_mae_over_both_when_both_valid():
    pts = {"09:00": {"ts": 1, "price": 100}, "CLOSE": {"price": 103}}
    rows = [dict(_expected()["rows"][0]), dict(_expected()["rows"][0])]
    out = sh.build_shadow_comparison(expected_actual={"rows": rows}, reactions=_reaction(pts, [{"ts": 2, "close": 104.0}, {"ts": 3, "close": 99.0}]), cost_pct=0, slippage_pct=0)
    s = _summary_row(out)
    assert s["trade_count"] == 2 and s["average_mfe_pct"] == 4.0 and s["average_mae_pct"] == -1.0


def test_normal_path_values_are_unchanged():
    pts = {"09:00": {"ts": 1, "price": 100}, "CLOSE": {"price": 110}}
    path = [{"ts": 1, "close": 100.0}, {"ts": 2, "close": 105.0}, {"ts": 3, "close": 97.0}]
    out = sh.build_shadow_comparison(expected_actual=_expected(), reactions=_reaction(pts, path), cost_pct=0.1, slippage_pct=0.05)
    s = _summary_row(out)
    assert s["average_mfe_pct"] == 5.0 and s["average_mae_pct"] == -3.0 and s["average_return_pct"] == pytest.approx(9.85) and s["trade_count"] == 1
    assert _summary_row(out, "FIRST_PULLBACK_ENTRY")["average_mfe_pct"] is None and _summary_row(out, "FIRST_PULLBACK_ENTRY")["trade_count"] == 0
