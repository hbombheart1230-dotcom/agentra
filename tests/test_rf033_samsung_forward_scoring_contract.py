"""RF-033 C3: samsung forward_validation scoring (pure) - threshold boundaries, confidence ladder, market state score."""
from __future__ import annotations

import pytest

from libs.reporting.baseline_samsung_hynix.forward_validation import scoring as sc
from libs.reporting.baseline_samsung_hynix.forward_validation.contracts import THRESHOLDS as T


@pytest.mark.parametrize("sox,state,score", [
    (5.0, "STRONG_POSITIVE", 2.0), (4.99, "POSITIVE", 1.0), (3.0, "POSITIVE", 1.0), (2.99, "NEUTRAL", 0.0),
    (-2.99, "NEUTRAL", 0.0), (-3.0, "NEGATIVE", -1.0), (-4.99, "NEGATIVE", -1.0), (-5.0, "STRONG_NEGATIVE", -2.0),
])
def test_sox_base_and_state_for_sk_hynix(sox, state, score):
    out = sc.score_semiconductor_signal({"sox_return_pct": sox})
    assert (out["state"], out["score"]) == (state, score) and out["samsung_sox_sensitivity"] == 1.0


def test_samsung_sensitivity_scales_score_and_can_downgrade_state():
    out = sc.score_semiconductor_signal({"sox_return_pct": 5.0}, samsung=True)
    assert out["score"] == round(2.0 * T["samsung_sox_sensitivity"], 4) == 1.3 and out["state"] == "POSITIVE"   # 1.3 < 1.75
    assert sc.score_semiconductor_signal({"sox_return_pct": -5.0}, samsung=True)["state"] == "NEGATIVE"


def test_samsung_positive_base_falls_below_positive_cut():
    out = sc.score_semiconductor_signal({"sox_return_pct": 3.0}, samsung=True)
    assert out["score"] == 0.65 and out["state"] == "NEUTRAL"


def test_missing_sox_is_insufficient_evidence():
    assert sc.score_semiconductor_signal({}) == {"state": "NEUTRAL", "score": None, "confidence": "INSUFFICIENT_EVIDENCE",
                                                 "reasons": ["sox_return_missing"], "samsung_sox_sensitivity": 1.0}
    assert sc.score_semiconductor_signal({"sox_return_pct": ""}, samsung=True)["samsung_sox_sensitivity"] == T["samsung_sox_sensitivity"]
    assert sc.score_semiconductor_signal({"sox_return_pct": "bad"})["score"] is None


def test_confidence_bonuses_penalties_and_ladder():
    base = {"sox_return_pct": 5.0}
    assert sc.score_semiconductor_signal(base)["confidence"] == "INSUFFICIENT_EVIDENCE"           # no confirmers present
    full = sc.score_semiconductor_signal({**base, "nvidia_return_pct": 1, "micron_return_pct": 1, "hynix_adr_return_pct": 1})
    assert full["confidence_score"] == 1.0 and full["confidence"] == "HIGH"                       # 0.5 + 3*0.2 = 1.1 -> clamp 1.0
    two = sc.score_semiconductor_signal({**base, "nvidia_return_pct": 1, "micron_return_pct": 1})
    assert two["confidence_score"] == 0.9 and two["confidence"] == "HIGH"
    one = sc.score_semiconductor_signal({**base, "nvidia_return_pct": 1})
    assert one["confidence_score"] == 0.7 and one["confidence"] == "MEDIUM"
    opposed = sc.score_semiconductor_signal({**base, "nvidia_return_pct": -1})                    # present but opposing: no bonus, still counted
    assert opposed["confidence_score"] == 0.5 and opposed["confidence"] == "MEDIUM"
    fut = sc.score_semiconductor_signal({**base, "nasdaq100_futures_0850_return_pct": -0.1})
    assert fut["confidence_score"] == 0.0 and fut["confidence"] == "LOW" and any("nasdaq_futures_confidence=-0.50" in r for r in fut["reasons"])
    same_fut = sc.score_semiconductor_signal({**base, "nasdaq100_futures_0850_return_pct": 0.1})
    assert same_fut["confidence_score"] == 0.5


def test_usdkrw_adverse_threshold_is_inclusive_and_direction_aware():
    pos = {"sox_return_pct": 5.0}
    thr = T["usdkrw_adverse_move_pct"]
    assert sc.score_semiconductor_signal({**pos, "usdkrw_0850_change_pct": thr})["confidence_score"] == 0.25          # 0.5 - 0.25
    assert sc.score_semiconductor_signal({**pos, "usdkrw_0850_change_pct": thr - 0.01})["confidence_score"] == 0.5
    assert sc.score_semiconductor_signal({**pos, "usdkrw_0850_change_pct": -thr})["confidence_score"] == 0.5          # favorable for positive
    neg = {"sox_return_pct": -5.0}
    assert sc.score_semiconductor_signal({**neg, "usdkrw_0850_change_pct": -thr})["confidence_score"] == 0.25
    assert sc.score_semiconductor_signal({**neg, "usdkrw_0850_change_pct": thr})["confidence_score"] == 0.5


def test_neutral_direction_gets_no_bonus_or_penalty_but_confirmer_count_still_matters():
    out = sc.score_semiconductor_signal({"sox_return_pct": 0.0, "nvidia_return_pct": 5, "nasdaq100_futures_0850_return_pct": -5, "usdkrw_0850_change_pct": 5})
    assert out["confidence_score"] == 0.5 and out["confidence"] == "MEDIUM" and out["state"] == "NEUTRAL"


@pytest.mark.parametrize("v,exp,direction", [
    (None, "UNKNOWN", "UNKNOWN"), (8.0, "EXTENDED", "UP"), (7.99, "FIRST_MOVE", "UP"), (-8.0, "EXTENDED", "DOWN"), (-7.99, "FIRST_MOVE", "DOWN"), (0, "FIRST_MOVE", "FLAT"),
])
def test_hynix_extension(v, exp, direction):
    out = sc.classify_hynix_extension({"hynix_3d_cumulative_return_pct": v})
    assert out["state"] == exp and out["direction"] == direction and out["threshold_abs_pct"] == 8.0
    assert out["extended"] is (None if v is None else exp == "EXTENDED")


def test_market_state_components_thresholds_and_inversions():
    thr = T["market_equity_move_pct"]
    assert sc.score_korea_market_state({"nasdaq_return_pct": thr})["components"] == {"nasdaq_return_pct": 1.0}          # inclusive
    assert sc.score_korea_market_state({"nasdaq_return_pct": thr - 0.01})["components"] == {}
    out = sc.score_korea_market_state({"usdkrw_0850_change_pct": 0.3, "us10y_yield_change": 0.05, "vix_change_pct": 5.0})
    assert out["components"] == {"usdkrw_0850_change_pct": -1.0, "us10y_yield_change": -0.5, "vix_change_pct": -1.0} and out["score"] == -2.5
    assert out["state"] == "RISK_OFF"
    assert sc.score_korea_market_state({"us10y_yield_change": -0.05})["components"] == {"us10y_yield_change": 0.5}


def test_market_state_risk_on_cut_is_inclusive_at_1_5():
    assert sc.score_korea_market_state({"nasdaq_return_pct": 1.0})["state"] == "NEUTRAL"                               # 1.0
    assert sc.score_korea_market_state({"nasdaq_return_pct": 1.0, "us10y_yield_change": -0.05})["state"] == "RISK_ON"  # 1.5
    assert sc.score_korea_market_state({"nasdaq_return_pct": -1.0, "us10y_yield_change": 0.05})["state"] == "RISK_OFF"  # -1.5
    assert sc.score_korea_market_state({"nasdaq_return_pct": 1, "sp500_return_pct": 1, "sox_return_pct": 4, "vix_change_pct": -6})["score"] == 4.0
    assert sc.score_korea_market_state({"nasdaq_return_pct": 1, "sp500_return_pct": 1, "sox_return_pct": 4, "vix_change_pct": -6})["state"] == "STRONG_RISK_ON"  # >= 4.0


def test_market_state_risk_on_and_strong_levels_and_evidence_status():
    two_plus = {"nasdaq_return_pct": 1.0, "sp500_return_pct": 1.0, "sox_return_pct": 3.0}
    out = sc.score_korea_market_state(two_plus)
    assert out["score"] == 3.0 and out["state"] == "RISK_ON" and out["evidence_status"] == "PARTIAL" and out["available_input_count"] == 3
    strong = {**two_plus, "nasdaq100_futures_0850_return_pct": 0.3, "sp500_futures_0850_return_pct": 0.3}
    assert sc.score_korea_market_state(strong)["state"] == "STRONG_RISK_ON" and sc.score_korea_market_state(strong)["score"] == 5.0
    off = {k: -v for k, v in strong.items()}
    assert sc.score_korea_market_state(off)["state"] == "STRONG_RISK_OFF"
    exactly_normal = {"nasdaq_return_pct": 1, "sp500_return_pct": 1, "sox_return_pct": 4}                                  # 3.0 -> RISK_ON
    assert sc.score_korea_market_state(exactly_normal)["state"] == "RISK_ON"
    cut_1_5 = {"nasdaq_return_pct": 1, "sp500_return_pct": 1, "us10y_yield_change": -0.1, "vix_change_pct": -6}            # 1+1+0.5+1 = 3.5 (RISK_ON)
    assert sc.score_korea_market_state(cut_1_5)["score"] == 3.5
    full = {k: 0.0 for k in ("nasdaq_return_pct", "sp500_return_pct", "sox_return_pct", "nasdaq100_futures_0850_return_pct", "sp500_futures_0850_return_pct",
                             "usdkrw_0850_change_pct", "us10y_yield_change", "vix_change_pct")}
    assert sc.score_korea_market_state(full)["evidence_status"] == "COMPLETE" and sc.score_korea_market_state({})["evidence_status"] == "INSUFFICIENT_EVIDENCE"


def test_semiconductor_state_cuts_are_inclusive():
    f = sc._semiconductor_state
    assert [f(v) for v in (1.75, 1.7499, 0.75, 0.7499, -0.7499, -0.75, -1.7499, -1.75)] == [
        "STRONG_POSITIVE", "POSITIVE", "POSITIVE", "NEUTRAL", "NEUTRAL", "NEGATIVE", "NEGATIVE", "STRONG_NEGATIVE"]


def test_confidence_medium_boundary_at_0_40_is_reachable_and_inclusive():
    out = sc.score_semiconductor_signal({"sox_return_pct": 5.0, "nvidia_return_pct": 1, "micron_return_pct": 1, "nasdaq100_futures_0850_return_pct": -1})
    assert out["confidence_score"] == 0.4 and out["confidence"] == "MEDIUM"


def test_flat_sox_with_flat_futures_gets_no_penalty():
    out = sc.score_semiconductor_signal({"sox_return_pct": 0.0, "nasdaq100_futures_0850_return_pct": 0.0})
    assert out["confidence_score"] == 0.5 and not any("nasdaq_futures" in r for r in out["reasons"])
