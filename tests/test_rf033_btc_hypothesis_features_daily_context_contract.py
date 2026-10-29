"""RF-033 C3: BTC hypothesis_features daily context, Woori previous close and gap bands (pure; look-ahead rules pinned)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from libs.reporting.baseline_btc_woori_tech import hypothesis_features as hf

KST = timezone(timedelta(hours=9))
DAY = "2026-10-28"
AS_OF = int(datetime(2026, 10, 28, 8, 55, tzinfo=KST).timestamp())
D = 86400


def daily(n, *, start_close=100.0, step=0.0, high_pad=1.0, end=AS_OF - D):
    """n closed daily bars ending exactly at the 24h look-ahead cutoff, one per day."""
    rows = []
    for i in range(n):
        ts = end - (n - 1 - i) * D
        close = start_close + step * i
        rows.append({"ts": ts, "close": close, "high": close + high_pad, "low": close - 1})
    return rows


def btc(price=100.0, ret=0.0, source="btc_usd"):
    return {"target_epoch": AS_OF, "return_24h_pct": ret, "observations": [{"source": "other", "price": 1.0}, {"source": source, "price": price}]}


def ctx(rows, **kw):
    return hf._daily_context({"research_context": {"btc_usd_daily": rows}}, btc_0855=btc(**kw))


def test_closed_daily_rows_cutoff_is_24h_inclusive_and_filters():
    rows = [{"ts": AS_OF - D, "close": 1.0}, {"ts": AS_OF - D + 1, "close": 2.0}, {"ts": 0, "close": 3.0}, {"ts": AS_OF - 2 * D, "close": 0.0}, {"ts": AS_OF - 3 * D, "close": None}, {"ts": AS_OF - 4 * D, "close": 5.0}]
    out = hf._closed_daily_rows(rows, as_of_epoch=AS_OF)
    assert [r["close"] for r in out] == [5.0, 1.0] and [r["ts"] for r in out] == sorted(r["ts"] for r in out)


def test_missing_when_fewer_than_20_closed_bars_or_no_usd_price_or_bad_container():
    assert ctx(daily(19))["status"] == "MISSING" and ctx(daily(19))["closed_daily_count"] == 19
    assert ctx(daily(20))["status"] == "OBSERVED"                                           # exactly 20 is enough
    m = hf._daily_context({"research_context": {"btc_usd_daily": daily(30)}}, btc_0855=btc(source="btc_krw"))
    assert m["status"] == "MISSING" and m["reason"] == "btc_daily_history_or_usd_price_missing" and m["surge_state"] is None and m["breakout_state"] is None
    assert hf._daily_context({}, btc_0855=btc())["closed_daily_count"] == 0 and hf._daily_context({"research_context": {"btc_usd_daily": "x"}}, btc_0855=btc())["status"] == "MISSING"
    # a bar that is not yet 24h old is ignored (look-ahead guard)
    fresh = daily(19) + [{"ts": AS_OF - 3600, "close": 1.0, "high": 1.0}]
    assert ctx(fresh)["status"] == "MISSING" and ctx(fresh)["closed_daily_count"] == 19


def test_surge_state_first_repeated_none_with_3pct_boundary():
    flat = daily(30, step=0.0)
    assert ctx(flat, ret=3.0)["surge_state"] == "FIRST_SURGE" and ctx(flat, ret=2.99)["surge_state"] == "NO_STRONG_SURGE"
    rows = daily(30, start_close=100.0, step=0.0)
    rows[-3]["close"] = 110.0                                                               # +10% day inside the prior-7 window
    assert ctx(rows, ret=3.0)["surge_state"] == "REPEATED_SURGE" and ctx(rows, ret=3.0)["prior_7d_strong_up_day_count"] >= 1
    rows2 = daily(40, step=0.0)
    rows2[5]["close"] = 120.0                                                               # strong day long before the 7-day window
    assert ctx(rows2, ret=3.0)["surge_state"] == "FIRST_SURGE"
    assert hf._daily_context({"research_context": {"btc_usd_daily": flat}}, btc_0855={**btc(), "return_24h_pct": None})["surge_state"] == "NO_STRONG_SURGE"


def test_breakout_states_use_highs_of_closed_bars_only_and_strict_greater():
    rows = daily(70, high_pad=1.0)                                                          # all highs 101
    assert ctx(rows, price=101.0)["breakout_state"] == "NO_BREAKOUT"                        # equal is not a breakout
    out = ctx(rows, price=101.01)
    assert out["breakout_20d"] is True and out["breakout_60d"] is True and out["breakout_ath"] is True and out["breakout_state"] == "ATH_BREAKOUT"
    older = daily(70, high_pad=1.0)
    older[0]["high"] = 500.0                                                                # ATH only in the oldest bar
    o = ctx(older, price=150.0)
    assert o["breakout_ath"] is False and o["breakout_60d"] is True and o["breakout_state"] == "60D_BREAKOUT"          # 60d window excludes the oldest bar
    short = ctx(daily(30), price=200.0)
    assert short["breakout_60d"] is None and short["breakout_20d"] is True and short["breakout_ath"] is True
    recent = daily(30, high_pad=1.0)
    for r in recent[:10]:
        r["high"] = 300.0
    r = ctx(recent, price=200.0)
    assert r["breakout_20d"] is True and r["breakout_ath"] is False and r["breakout_state"] == "20D_BREAKOUT"
    nohigh = [dict(x, high=None) for x in daily(25)]
    assert ctx(nohigh, price=200.0)["breakout_20d"] is None and ctx(nohigh, price=200.0)["breakout_state"] == "NO_BREAKOUT"


def test_observed_payload_shape_and_policy_text():
    out = ctx(daily(25), price=100.0)
    assert out["status"] == "OBSERVED" and out["reason"] == "" and out["closed_daily_count"] == 25 and "24h before 08:55" in out["lookahead_policy"]
    assert out["prior_7d_strong_up_day_count"] == 0


def woori(*pairs):
    return {"research_context": {"woori_daily": [{"ts": int(datetime(2026, 10, d, 15, 30, tzinfo=KST).timestamp()), "close": c} for d, c in pairs]}}


def test_woori_previous_close_is_latest_strictly_before_target_day():
    assert hf._woori_previous_close(woori((26, 10.0), (27, 11.0), (28, 99.0), (29, 5.0)), day=DAY) == 11.0
    assert hf._woori_previous_close(woori((28, 99.0)), day=DAY) is None and hf._woori_previous_close({}, day=DAY) is None
    assert hf._woori_previous_close(woori((27, 0.0), (26, 9.0)), day=DAY) == 9.0                 # non-positive close skipped
    bad = {"research_context": {"woori_daily": [{"ts": 0, "close": 5.0}, {"ts": None, "close": 5.0}]}}
    assert hf._woori_previous_close(bad, day=DAY) is None and hf._woori_previous_close({"research_context": {"woori_daily": "x"}}, day=DAY) is None


@pytest.mark.parametrize("v,band", [(None, "MISSING"), (-0.01, "NEGATIVE"), (0.0, "0_TO_3"), (2.99, "0_TO_3"), (3.0, "3_TO_5"), (4.99, "3_TO_5"), (5.0, "5_TO_10"), (9.99, "5_TO_10"), (10.0, "GTE_10")])
def test_gap_band_boundaries(v, band):
    assert hf._gap_band(v) == band


def test_prior_window_is_exactly_seven_returns_and_strong_day_is_inclusive_at_3pct():
    rows = daily(40, step=0.0)
    rows[-7]["close"] = 103.0                                          # return into this bar: +3.0% (inclusive), and it is the 7th-from-last return
    rows[-6]["close"] = 103.0
    out = ctx(rows, ret=3.0)
    assert out["prior_7d_strong_up_day_count"] == 1 and out["surge_state"] == "REPEATED_SURGE"
    rows = daily(40, step=0.0)
    rows[-8]["close"] = 120.0                                          # +20% return exactly eight returns back: outside the window
    rows[-7]["close"] = 120.0
    assert ctx(rows, ret=3.0)["prior_7d_strong_up_day_count"] == 0
    rows = daily(40, step=0.0)
    rows[-6]["close"] = 102.99
    assert ctx(rows, ret=3.0)["prior_7d_strong_up_day_count"] == 0


def test_60d_breakout_is_evaluated_at_exactly_60_closed_bars():
    rows = daily(60, high_pad=1.0)
    out = ctx(rows, price=101.5)
    assert out["breakout_60d"] is True and out["closed_daily_count"] == 60
    assert ctx(daily(59), price=101.5)["breakout_60d"] is None
