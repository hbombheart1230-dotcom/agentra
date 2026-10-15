"""Strategist: additive AI/manual override application to the deterministic frame.

T4-C (P1.5 Third Pass): contiguous statement run / value expression of `graphs/nodes/strategist_node.py::strategist_node` moved verbatim into a
Strategist Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
source module are resolved at use time as `facade.NAME`. State writes, event emission, logging, persistence, the frame LLM
call and provider IO stay in the orchestrator at their original boundaries.
"""
from __future__ import annotations

from typing import Any, NamedTuple


class AiOverrideFrame(NamedTuple):
    """Result of `apply_ai_overrides_to_frame` (positional order = sorted output names)."""

    avoid_themes: Any
    key_events: Any
    market_regime: Any
    market_regime_summary: Any
    market_sentiment: Any
    monitor_guidance: Any
    playbook: Any
    raw_theme_strategy: Any
    report_focus: Any
    risk_tone: Any
    scanner_bias: Any
    scanner_priority: Any
    selected_themes: Any
    themes: Any
    trade_aggressiveness: Any

def apply_ai_overrides_to_frame(ai_overrides, available_themes, avoid_themes, global_signal, key_events, market_regime, market_sentiment, market_structure, monitor_guidance, playbook, report_focus, risk_tone, scanner_bias, scanner_priority, themes, trade_aggressiveness, *, facade):
    market_regime = str(ai_overrides.get("market_regime") or market_regime).strip() or market_regime
    market_sentiment = str(ai_overrides.get("market_sentiment") or market_sentiment).strip() or market_sentiment
    playbook = str(ai_overrides.get("playbook") or playbook).strip() or playbook
    trade_aggressiveness = str(ai_overrides.get("trade_aggressiveness") or trade_aggressiveness).strip() or trade_aggressiveness
    risk_tone = str(ai_overrides.get("risk_tone") or risk_tone).strip() or risk_tone
    if isinstance(ai_overrides.get("themes"), list) and list(ai_overrides.get("themes") or []):
        themes = facade._merge_override_text_list([], ai_overrides.get("themes"), limit=5)
    else:
        themes = facade._merge_override_text_list(themes, ai_overrides.get("themes"), limit=5)
    raw_theme_strategy = ai_overrides.get("theme_strategy") if isinstance(ai_overrides.get("theme_strategy"), dict) else {}
    raw_selected_themes = ai_overrides.get("selected_themes")
    if not raw_selected_themes and isinstance(raw_theme_strategy, dict):
        raw_selected_themes = raw_theme_strategy.get("selected_themes")
    selected_themes = (
        facade._resolve_selected_themes_from_api(
            available_themes=list(available_themes),
            themes=list(themes),
            raw_selected=raw_selected_themes,
        )
        if available_themes
        else []
    )
    if selected_themes:
        themes = facade._merge_override_text_list([], [*list(selected_themes), *list(themes)], limit=5)
    key_events = facade._merge_override_text_list(key_events, ai_overrides.get("key_events"), limit=5)
    avoid_themes = facade._merge_override_text_list(avoid_themes, ai_overrides.get("avoid_themes"), limit=6)
    scanner_priority = facade._merge_override_text_list(scanner_priority, ai_overrides.get("scanner_priority"), limit=6)
    report_focus = facade._merge_override_text_list(report_focus, ai_overrides.get("report_focus"), limit=6)
    scanner_bias = str(ai_overrides.get("scanner_bias") or scanner_bias).strip().lower() or scanner_bias
    monitor_guidance = str(ai_overrides.get("monitor_guidance") or monitor_guidance).strip().lower() or monitor_guidance
    market_regime_summary = str(
        ai_overrides.get("market_regime_summary")
        or facade._build_market_regime_summary(
            market_regime=market_regime,
            market_sentiment=market_sentiment,
            market_structure=market_structure,
            playbook=playbook,
            global_signal=global_signal,
        )
    ).strip()
    return AiOverrideFrame(avoid_themes, key_events, market_regime, market_regime_summary, market_sentiment, monitor_guidance, playbook, raw_theme_strategy, report_focus, risk_tone, scanner_bias, scanner_priority, selected_themes, themes, trade_aggressiveness)
