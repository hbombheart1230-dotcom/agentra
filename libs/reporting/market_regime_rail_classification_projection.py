"""market_regime_rail_review classify_market_regime_rail (moved verbatim from market_regime_rail_review).

Module globals and helpers are resolved on ``facade`` (the market_regime_rail_review module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping


def classify_market_regime_rail(snapshot: Mapping[str, Any], *, facade: Any) -> Dict[str, Any]:
    if not bool(snapshot.get("available", True)) and not snapshot.get("schema_version"):
        return {
            "schema_version": "market_regime_rail_observation.v1",
            "behavior_effect": "evaluation_only",
            "available": False,
            "rail_id": "not_available",
            "rail_confidence": "none",
            "rationale": "macro snapshot unavailable",
            "market_inputs": {},
            "expected_tactical_behavior": [],
            "q8_review_focus": [],
        }

    korea = snapshot.get("korea_indices") if isinstance(snapshot.get("korea_indices"), Mapping) else {}
    sanity = facade.korea_index_sanity(korea) if korea else {"status": "ok", "warning_count": 0, "warnings": [], "extreme_move_requires_confirmation": False}
    macro_moves = snapshot.get("macro_moves") if isinstance(snapshot.get("macro_moves"), Mapping) else {}
    global_sentiment = snapshot.get("global_sentiment") if isinstance(snapshot.get("global_sentiment"), Mapping) else {}

    inputs = {
        "kospi_pct": facade._change_pct(snapshot, "kospi"),
        "kosdaq_pct": facade._change_pct(snapshot, "kosdaq"),
        "kospi200_pct": facade._change_pct(snapshot, "kospi200"),
        "krx_night_futures_pct": facade._change_pct(snapshot, "krx_night_futures"),
        "breadth": facade._to_float(korea.get("breadth"), 0.0),
        "nasdaq_pct": facade._change_pct(snapshot, "nasdaq"),
        "sp500_pct": facade._change_pct(snapshot, "sp500"),
        "dxy_pct": facade._to_float(macro_moves.get("dxy_pct"), facade._to_float(facade._indicator(snapshot, "dxy").get("change_pct"), 0.0)),
        "usdkrw_pct": facade._to_float(facade._indicator(snapshot, "usdkrw").get("change_pct"), 0.0),
        "vix_level": facade._to_float(macro_moves.get("vix_level"), 0.0),
        "vix_pct": facade._to_float(macro_moves.get("vix_pct"), 0.0),
        "us_10y_delta": facade._to_float(facade._indicator(snapshot, "us_10y_yield").get("delta"), 0.0),
        "global_sentiment_score": facade._to_float(global_sentiment.get("score"), 0.0),
    }
    night = snapshot.get("krx_night_futures") if isinstance(snapshot.get("krx_night_futures"), Mapping) else {}
    inputs["krx_night_futures_status"] = str(night.get("status") or facade._indicator(snapshot, "krx_night_futures").get("status") or "")
    inputs["krx_night_futures_pressure"] = str(
        night.get("direction_pressure") or facade._indicator(snapshot, "krx_night_futures").get("direction_pressure") or ""
    )

    korea_weak = inputs["kosdaq_pct"] <= -1.0 or inputs["kospi_pct"] <= -0.7 or inputs["breadth"] <= -0.35
    night_gap_down = inputs["krx_night_futures_pct"] <= -1.0
    night_gap_up = inputs["krx_night_futures_pct"] >= 1.0
    us_tech_positive = inputs["nasdaq_pct"] >= 0.2 and inputs["sp500_pct"] >= 0.0
    fx_pressure = inputs["usdkrw_pct"] >= 0.4 or inputs["dxy_pct"] >= 0.2
    vix_pressure = inputs["vix_level"] >= 20.0 or inputs["vix_pct"] >= 8.0

    if night_gap_down:
        rail_id = "krx_night_futures_gap_down"
        confidence = "high" if inputs["krx_night_futures_pct"] <= -2.0 else "medium"
        behavior = [
            "treat pre-open derivatives pressure as broad gap-down risk",
            "require confirmed relative strength before entry",
            "keep cost-edge and volume confirmation strict",
            "compare blocked breakouts and reclaim setups against forward shadow outcomes",
        ]
        focus = ["breakout_not_ready", "below_vwap_reclaim_not_ready", "volume_confirmation_missing"]
        rationale = "KRX KOSPI200 night futures showed sharp negative pressure before or near the regular session."
    elif night_gap_up and not korea_weak:
        rail_id = "krx_night_futures_gap_up"
        confidence = "medium"
        behavior = [
            "watch opening momentum but avoid unconfirmed gap chase",
            "compare opening momentum probes against delayed pullback entries",
            "keep cost-edge active unless promoted policy says otherwise",
        ]
        focus = ["opening_momentum_probe", "breakout_not_ready", "pullback_not_mature"]
        rationale = "KRX KOSPI200 night futures showed positive pre-open derivatives pressure."
    elif us_tech_positive and korea_weak:
        rail_id = "us_tech_risk_on_korea_weak"
        confidence = "high" if inputs["breadth"] <= -0.45 or inputs["kosdaq_pct"] <= -1.5 else "medium"
        behavior = [
            "prefer confirmed relative-strength breakout or reclaim over broad pullback",
            "do not weaken cost-edge or volume confirmation globally",
            "review semiconductor and large-cap tech candidates against shadow breakout outcomes",
        ]
        focus = ["breakout_not_ready", "pullback_not_mature", "human_chart_sanity_guard_blocked"]
        rationale = "US technology risk appetite was positive while Korean breadth and KOSDAQ were weak."
    elif korea_weak and (fx_pressure or vix_pressure or inputs["global_sentiment_score"] < -0.2):
        rail_id = "risk_off_breadth_collapse"
        confidence = "high" if inputs["breadth"] <= -0.45 else "medium"
        behavior = [
            "avoid broad chase",
            "require strong relative strength before entry",
            "keep cost-edge and volume confirmation strict",
        ]
        focus = ["volume_confirmation_missing", "below_vwap_reclaim_not_ready", "breakout_not_ready"]
        rationale = "Korean market breadth was weak with macro pressure signals active."
    elif korea_weak:
        rail_id = "defensive_rotation"
        confidence = "medium"
        behavior = [
            "prefer defensive or isolated relative strength setups",
            "avoid weak-volume pullback chase",
            "measure opportunity cost of blocked breakouts",
        ]
        focus = ["breakout_not_ready", "pullback_not_mature"]
        rationale = "Domestic market was weak without enough global confirmation for full risk-off classification."
    elif us_tech_positive and not korea_weak:
        rail_id = "liquidity_leader_rotation"
        confidence = "medium"
        behavior = [
            "watch leader rotation and high-liquidity breakouts",
            "compare selected candidates against scanner top leaders",
            "keep cost-edge active",
        ]
        focus = ["breakout_not_ready", "below_vwap_reclaim_not_ready"]
        rationale = "US technology risk appetite was positive and domestic weakness was not dominant."
    else:
        rail_id = "macro_pressure_no_trade" if fx_pressure or vix_pressure else "neutral_observation"
        confidence = "low" if rail_id == "neutral_observation" else "medium"
        behavior = [
            "keep current gates unchanged",
            "collect Q8 shadow evidence before policy changes",
        ]
        focus = ["volume_confirmation_missing", "below_vwap_reclaim_not_ready"]
        rationale = "No stronger market rail was identified from the latest macro snapshot."

    return {
        "schema_version": "market_regime_rail_observation.v1",
        "behavior_effect": "evaluation_only",
        "available": True,
        "source": snapshot.get("path") or "macro_snapshot",
        "generated_at": snapshot.get("generated_at"),
        "rail_id": rail_id,
        "rail_confidence": confidence,
        "rationale": rationale,
        "market_inputs": inputs,
        "market_input_sanity": sanity,
        "expected_tactical_behavior": behavior,
        "q8_review_focus": focus,
        "secondary_flags": {
            "korea_weak": korea_weak,
            "night_gap_down": night_gap_down,
            "night_gap_up": night_gap_up,
            "us_tech_positive": us_tech_positive,
            "fx_pressure": fx_pressure,
            "vix_pressure": vix_pressure,
        },
    }
