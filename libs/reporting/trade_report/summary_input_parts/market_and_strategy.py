from __future__ import annotations

from typing import Any


def build_market_and_strategy(
    *,
    _is_not_captured: Any, _listify: Any, _metadata_value: Any, _pick: Any,
    _playbook_label: Any, _risk_mode_label: Any, _sample_news_titles: Any, _sample_news_titles_for_symbol: Any,
    _theme_label: Any, _translate_text: Any, market: Any, report: Any,
    symbol: Any, trace_summary: Any,
) -> dict:
    """Preserve the canonical market_and_strategy input contract and value evaluation order."""
    return {
            "market_summary": _translate_text(market.get("summary")).strip(),
            "vix": market.get("vix_level"),
            "market_sentiment": _metadata_value(market.get("market_sentiment")),
            "playbook": _playbook_label(_pick(market.get("playbook"), market.get("selected_playbook"))),
            "risk_tone": _risk_mode_label(_pick(market.get("risk_tone"), trace_summary.get("risk_tone"), market.get("risk_mode"))),
            "monitor_guidance": _metadata_value(_pick(trace_summary.get("monitor_guidance"), market.get("monitor_guidance"))),
            "themes": [_theme_label(x) for x in _listify(market.get("themes")) if not _is_not_captured(x)],
            "preferred_themes": [_theme_label(x) for x in _listify(market.get("preferred_themes")) if not _is_not_captured(x)],
            "theme_source": _metadata_value(market.get("theme_source")),
            "theme_source_status": _metadata_value(market.get("theme_source_status")),
            "theme_strength_top_themes": [_theme_label(x) for x in _listify(market.get("theme_strength_top_themes")) if not _is_not_captured(x)],
            "market_news_titles": _sample_news_titles(market.get("market_news_titles") or report.get("strategist_market_headlines"), limit=4),
            "symbol_news_titles": _sample_news_titles_for_symbol(
                symbol,
                market.get("symbol_news_titles"),
                report.get("strategist_symbol_headlines"),
                market.get("candidate_news_titles"),
                limit=4,
            ),
        }
