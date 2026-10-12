"""Scanner macro focus derivation (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _scanner_macro_focus_r3_impl(*, playbook, scanner_priority, risk_tone, trade_aggressiveness, facade):
    focus = {
        "trend_alignment": 1.0,
        "relative_strength": 1.0,
        "adx_trend": 1.0,
        "volume_accumulation": 1.0,
        "breakout_base": 1.0,
        "risk_balance": 1.0,
    }
    playbook_text = str(playbook or "").strip().lower()
    if playbook_text == "breakout":
        focus["breakout_base"] += 0.25
        focus["volume_accumulation"] += 0.15
        focus["relative_strength"] += 0.10
    elif playbook_text in {"pullback", "reversal"}:
        focus["trend_alignment"] += 0.15
        focus["risk_balance"] += 0.15
        focus["breakout_base"] -= 0.10
    elif playbook_text == "defensive":
        focus["risk_balance"] += 0.25
        focus["trend_alignment"] += 0.10

    for item in list(scanner_priority or []):
        text = str(item or "").strip().lower()
        if text in {"trend", "trend_strength", "ma_alignment", "ma20", "ma60", "ma120"}:
            focus["trend_alignment"] += 0.10
        elif text in {"relative_strength", "cross_section_rank", "leader", "leaders"}:
            focus["relative_strength"] += 0.10
        elif text in {"adx", "adx14"}:
            focus["adx_trend"] += 0.10
        elif text in {"volume", "volume_surge", "volume_spike", "turnover"}:
            focus["volume_accumulation"] += 0.10
        elif text in {"breakout", "breakout_base", "vwap_reclaim", "momentum"}:
            focus["breakout_base"] += 0.10
        elif text in {"low_risk", "risk", "volatility", "gap"}:
            focus["risk_balance"] += 0.10

    risk_text = str(risk_tone or "").strip().lower()
    if risk_text == "conservative":
        focus["risk_balance"] += 0.20
    elif risk_text == "aggressive":
        focus["breakout_base"] += 0.10
        focus["volume_accumulation"] += 0.10

    aggression_text = str(trade_aggressiveness or "").strip().lower()
    if aggression_text == "high":
        focus["relative_strength"] += 0.10
        focus["breakout_base"] += 0.10
    elif aggression_text == "low":
        focus["risk_balance"] += 0.15
        focus["trend_alignment"] += 0.05

    return {key: facade._clamp(float(value), 0.50, 1.50) for key, value in focus.items()}
