"""RF-033 C3: samsung forward_returns extended checkpoints, EOD rule and summary (attach_forward_outcomes stubbed; pure)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from libs.reporting.baseline_samsung_hynix import forward_returns as fr

KST = timezone(timedelta(hours=9))


def ep(h, m, s=0):
    return int(datetime(2026, 9, 7, h, m, s, tzinfo=KST).timestamp())


def bar(h, m, close, *, high=None, low=None, s=0):
    return {"ts": ep(h, m, s), "close": close, "high": close if high is None else high, "low": close if low is None else low, "raw_ts": f"{h:02d}{m:02d}"}


def test_extended_checkpoint_window_edges_and_excursions():
    base = ep(9, 0)
    rows = [bar(9, 30, 101.0, high=103.0, low=99.0), bar(10, 59, 106.0, high=108.0, low=97.0), bar(11, 0, 110.0, high=111.0, low=100.0), bar(11, 1, 5.0)]
    cp = fr._extended_checkpoint(rows, base_epoch=base, base_price=100.0, minutes=120)
    assert cp["status"] == "observed" and cp["return_pct"] == 10.0 and cp["mfe_pct"] == 111.0 - 100.0 and cp["mae_pct"] == -3.0 and cp["observed_ts"] == "1100"
    assert cp["price"] == 110.0 and cp["high"] == 111.0 and cp["low"] == 97.0
    late = [{"ts": base + 7200 + 91, "close": 110.0}]
    assert fr._extended_checkpoint(late, base_epoch=base, base_price=100.0, minutes=120) == {"status": "pending"}                   # 91s past target is too late
    assert fr._extended_checkpoint([{"ts": base + 7200 + 90, "close": 110.0}], base_epoch=base, base_price=100.0, minutes=120)["status"] == "observed"  # 90s slack is inclusive
    assert fr._extended_checkpoint([bar(10, 59, 110.0)], base_epoch=base, base_price=100.0, minutes=120) == {"status": "pending"}     # before the target
    assert fr._extended_checkpoint([], base_epoch=base, base_price=100.0, minutes=120) == {"status": "pending"}
    assert fr._extended_checkpoint([bar(11, 0, 0.0)], base_epoch=base, base_price=100.0, minutes=120) == {"status": "pending"}        # non-positive close
    only_target_at_base = [{"ts": base + 7200, "close": 110.0}]
    assert fr._extended_checkpoint(only_target_at_base, base_epoch=base, base_price=100.0, minutes=120)["status"] == "observed"        # window includes the observed row itself


def test_extended_checkpoint_falls_back_to_close_when_high_low_missing():
    base = ep(9, 0)
    cp = fr._extended_checkpoint([{"ts": base + 60, "close": 95.0}, {"ts": base + 7200, "close": 105.0}], base_epoch=base, base_price=100.0, minutes=120)
    assert cp["high"] == 105.0 and cp["low"] == 95.0 and cp["observed_ts"] == base + 7200


def test_decision_candidate_rows_flatten_and_filter():
    decisions = [{"decision_id": "D1", "generated_at": "G", "ranked_candidates": [
        {"symbol": "A", "ticker": "A.KS", "rank": 1, "eligible": True, "action": "BUY", "features": {"available": 1, "baseline_epoch": 5, "baseline_price": 10.0, "baseline_raw_ts": "x"}},
        "junk", {"symbol": "B", "rank": 2, "features": "bad"}]}, {"decision_id": "D2"}]
    rows = fr.decision_candidate_rows(decisions)
    assert [r["symbol"] for r in rows] == ["A", "B"] and rows[0]["baseline_decision_id"] == "D1" and rows[0]["_payload_generated_at"] == "G"
    assert rows[0]["shadow_forward_base"] == {"available": True, "baseline_epoch": 5, "baseline_price": 10.0, "baseline_raw_ts": "x", "source": "baseline_existing_candle_provider"}
    assert rows[1]["shadow_forward_base"]["available"] is False and rows[1]["shadow_forward_base"]["baseline_epoch"] is None


@pytest.fixture
def stub_outcomes(monkeypatch):
    def attach(rows, *, minute_rows_by_symbol):
        return [dict(r, shadow_forward_outcome={"available": True, "reason": "r", "checkpoints": {"+5m": {"status": "observed", "return_pct": 1.0}}}) for r in rows]

    monkeypatch.setattr(fr, "attach_forward_outcomes", attach)


def decisions(base_epoch, price=100.0):
    return [{"decision_id": "D1", "ranked_candidates": [{"symbol": "A", "rank": 1, "eligible": True, "features": {"available": True, "baseline_epoch": base_epoch, "baseline_price": price}}]}]


def test_attach_adds_extended_and_eod_checkpoints(stub_outcomes):
    base = ep(9, 0)
    rows = {"A": [bar(9, 0, 100.0), bar(11, 0, 110.0, high=112.0, low=99.0), bar(12, 0, 108.0), bar(15, 30, 120.0, high=125.0, low=98.0)]}
    out = fr.attach_baseline_forward_returns(decisions(base), minute_rows_by_symbol=rows)
    r = out[0]
    assert r["available"] is True and r["reason"] == "r" and r["baseline_decision_id"] == "D1" and r["returns"]["+5m"]["return_pct"] == 1.0
    assert set(fr.HORIZONS) <= set(r["returns"])
    assert r["returns"]["+120m"]["status"] == "observed" and r["returns"]["+180m"]["status"] == "observed" and r["returns"]["+180m"]["return_pct"] == 8.0
    eod = r["returns"]["EOD"]
    assert eod["status"] == "observed" and eod["return_pct"] == 20.0 and eod["mfe_pct"] == 25.0 and eod["mae_pct"] == -2.0 and eod["source"] == "last_regular_session_minute" and eod["observed_ts"] == "1530"


def test_eod_requires_last_row_at_or_after_1530_and_positive_prices(stub_outcomes):
    base = ep(9, 0)
    early = fr.attach_baseline_forward_returns(decisions(base), minute_rows_by_symbol={"A": [bar(9, 0, 100.0), bar(15, 29, 120.0)]})
    assert early[0]["returns"]["EOD"] == {"status": "pending"}
    assert fr.attach_baseline_forward_returns(decisions(base), minute_rows_by_symbol={"A": [bar(9, 0, 100.0), bar(15, 30, 0.0)]})[0]["returns"]["EOD"] == {"status": "pending"}
    nobase = fr.attach_baseline_forward_returns(decisions(base, price=0.0), minute_rows_by_symbol={"A": [bar(9, 0, 100.0), bar(15, 30, 120.0)]})
    assert nobase[0]["returns"]["EOD"] == {"status": "pending"} and nobase[0]["returns"]["+120m"] == {"status": "pending"}
    nobase_epoch = fr.attach_baseline_forward_returns(decisions(0), minute_rows_by_symbol={"A": [bar(15, 30, 120.0)]})
    assert nobase_epoch[0]["returns"]["+120m"] == {"status": "pending"}
    assert fr.attach_baseline_forward_returns(decisions(base), minute_rows_by_symbol={})[0]["returns"]["EOD"] == {"status": "pending"}


def test_rows_before_base_epoch_are_ignored_for_extended_and_eod(stub_outcomes):
    base = ep(10, 0)
    rows = {"A": [bar(9, 0, 1.0, low=0.5), bar(10, 0, 100.0), bar(12, 0, 110.0), bar(15, 30, 120.0)]}
    r = fr.attach_baseline_forward_returns(decisions(base), minute_rows_by_symbol=rows)[0]
    assert r["returns"]["EOD"]["mae_pct"] == 0.0 and r["returns"]["+120m"]["return_pct"] == 10.0


def row(decision, rank, eligible, ret, horizon="+5m", status="observed"):
    return {"baseline_decision_id": decision, "rank": rank, "eligible": eligible, "returns": {horizon: {"status": status, "return_pct": ret}}}


def test_return_helper_edges():
    assert fr._return(row("d", 1, True, 2.0), "+5m") == 2.0
    assert fr._return(row("d", 1, True, 2.0, status="pending"), "+5m") is None and fr._return(row("d", 1, True, "x"), "+5m") is None
    assert fr._return({"returns": {"+5m": "bad"}}, "+5m") is None and fr._return({}, "+5m") is None and fr._return(row("d", 1, True, None), "+5m") is None


def test_summary_top1_both_average_eligible_and_net_costs():
    rows = [row("D1", 1, True, 2.0), row("D1", 2, False, 4.0), row("D2", 2, True, 6.0), row("D3", 1, False, -1.0), row("D4", 1, True, 1.0, status="pending")]
    s = fr.summarize_forward_returns(rows, cost_pct=0.1, slippage_pct=0.05)
    h = next(x for x in s["horizons"] if x["horizon"] == "+5m")
    assert h["top1_observation_count"] == 2 and h["both_symbol_window_count"] == 3 and h["trade_count"] == 2             # D2 has no rank-1; D4 unobserved
    assert h["top1_gross"]["average_return_pct"] == 0.5 and h["top1_net"]["average_return_pct"] == pytest.approx(0.35)
    assert h["both_symbol_average_gross"]["average_return_pct"] == pytest.approx((3.0 + 6.0 - 1.0) / 3, abs=1e-4)
    assert h["eligible_entries_gross"]["count"] == 2 and h["eligible_entries_net"]["average_return_pct"] == pytest.approx((2.0 + 6.0) / 2 - 0.15)
    assert h["top1_minus_both_average_net_pct"] == round(h["top1_net"]["expectancy_pct"] - h["both_symbol_average_net"]["expectancy_pct"], 4)
    assert h["cost_pct"] == 0.1 and h["slippage_pct"] == 0.05 and len(s["horizons"]) == len(fr.HORIZONS)
    empty = fr.summarize_forward_returns([], cost_pct=0.1, slippage_pct=0.05)["horizons"][0]
    assert empty["top1_observation_count"] == 0 and empty["trade_count"] == 0 and empty["top1_minus_both_average_net_pct"] == 0.0


def test_extended_window_excludes_the_base_candle_itself():
    base = ep(9, 0)
    rows = [{"ts": base, "close": 100.0, "high": 100.0, "low": 50.0}, {"ts": base + 7200, "close": 110.0, "high": 110.0, "low": 110.0}]
    cp = fr._extended_checkpoint(rows, base_epoch=base, base_price=100.0, minutes=120)
    assert cp["low"] == 110.0 and cp["mae_pct"] == 10.0                                      # the base-time row's low (50) is not part of the window


def test_zero_base_price_never_divides(stub_outcomes):
    base = ep(9, 0)
    rows = {"A": [bar(9, 0, 100.0), bar(11, 0, 110.0), bar(15, 30, 120.0)]}
    r = fr.attach_baseline_forward_returns(decisions(base, price=0.0), minute_rows_by_symbol=rows)[0]
    assert r["returns"]["+120m"] == {"status": "pending"} and r["returns"]["EOD"] == {"status": "pending"}
