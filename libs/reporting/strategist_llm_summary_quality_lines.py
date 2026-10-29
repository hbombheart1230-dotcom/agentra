"""Strategist LLM summary quality-audit markdown lines (moved verbatim).

Helpers are resolved on ``facade`` (the strategist_llm_summary module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, List


def quality_audit_lines(payload: Dict[str, Any], *, facade: Any) -> List[str]:
    rail = facade._as_dict(payload.get("market_regime_rail"))
    news = facade._as_dict(payload.get("news_quality_audit"))
    risk_policy = facade._as_dict(payload.get("risk_off_exception_policy"))
    risk_conditions = facade._as_list(payload.get("risk_off_exception_conditions"))
    news_event = facade._as_dict(payload.get("news_event_intelligence"))
    news_event_usage = facade._as_dict(payload.get("news_event_intelligence_usage"))
    output = facade._as_dict(payload.get("strategist_output_quality_audit"))
    metrics = facade._as_dict(rail.get("metrics"))
    rail_issues = facade._as_list(rail.get("issues"))
    news_issues = facade._as_list(news.get("issues"))
    output_issues = facade._as_list(output.get("issues"))

    def _issue_text(items: List[Any]) -> str:
        return ", ".join(str(x) for x in items if str(x or "").strip()) or "-"

    def _watch_text(items: List[Any], key: str) -> str:
        values: List[str] = []
        for item in items:
            if isinstance(item, dict):
                text = str(item.get(key) or "").strip()
            else:
                text = str(item or "").strip()
            if text:
                values.append(text)
        return ", ".join(values[:6]) or "-"

    return [
        "## Input/Output Quality Audit",
        "",
        "### Market Regime Rail",
        "",
        f"- market_regime: {facade._text(rail.get('market_regime'), '-')}",
        f"- market_regime_rail: {facade._text(rail.get('market_regime_rail'), '-')}",
        f"- risk_score: {rail.get('risk_score')}",
        f"- kospi_pct: {metrics.get('kospi_pct')}",
        f"- kosdaq_pct: {metrics.get('kosdaq_pct')}",
        f"- breadth_score: {metrics.get('breadth_score')}",
        f"- issues: {_issue_text(rail_issues)}",
        "",
        "### News Quality",
        "",
        f"- status: {facade._text(news.get('status'), '-')}",
        f"- headline_count: {news.get('headline_count')}",
        f"- market_headline_count: {news.get('market_headline_count')}",
        f"- candidate_headline_count: {news.get('candidate_headline_count')}",
        f"- query_target_count: {news.get('query_target_count')}",
        f"- issues: {_issue_text(news_issues)}",
        "",
        "### Risk-Off Exceptions",
        "",
        f"- risk_off_active: {risk_policy.get('risk_off_active')}",
        f"- allowed_exception_conditions: {_issue_text(facade._as_list(risk_policy.get('allowed_exception_conditions')))}",
        f"- strategist_reported_conditions: {_issue_text(risk_conditions)}",
        f"- instruction: {facade._text(risk_policy.get('instruction'), '-')}",
        "",
        "### News Event Intelligence",
        "",
        f"- behavior_effect: {facade._text(news_event.get('behavior_effect'), 'observation_only')}",
        f"- trading_action_allowed: {news_event.get('trading_action_allowed', False)}",
        f"- event_count: {facade._as_dict(news_event.get('input_summary')).get('event_count', 0)}",
        f"- theme_watchlist: {_watch_text(facade._as_list(news_event.get('theme_watchlist')), 'theme')}",
        f"- symbol_watchlist: {_watch_text(facade._as_list(news_event.get('symbol_watchlist')), 'symbol')}",
        f"- llm_usage_status: {facade._text(news_event_usage.get('status'), '-')}",
        f"- llm_usage_reason: {facade._text(news_event_usage.get('reason'), '-')}",
        "",
        "### Strategist Output Quality",
        "",
        f"- status: {facade._text(output.get('status'), '-')}",
        f"- decision: {facade._text(output.get('decision'), '-')}",
        f"- confidence: {output.get('confidence')}",
        f"- final_playbook: {facade._text(output.get('final_playbook'), '-')}",
        f"- tactical_strategy: {facade._text(output.get('tactical_strategy'), '-')}",
        f"- issues: {_issue_text(output_issues)}",
        "",
    ]
