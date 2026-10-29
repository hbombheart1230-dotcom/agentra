from __future__ import annotations

from typing import Any, Dict, List


def _build_strategist_trace_summary(
    *,
    facade: Any,
    strategist_output: Dict[str, Any],
    global_signal: Dict[str, Any],
    macro_overlay: Dict[str, Any],
    news_context: Dict[str, Any],
    themes: List[str],
    avoid_themes: List[str],
    market_regime: str,
    market_sentiment: str,
    playbook: str,
) -> Dict[str, Any]:
    fear_index = facade._dict(global_signal.get("fear_index"))
    strategy_policy_summary = facade._dict(strategist_output.get("strategy_policy_summary"))
    market_policy = facade._dict(strategy_policy_summary.get("market_policy"))
    risk_tone = facade._clip(
        strategist_output.get("risk_tone") or market_policy.get("risk_tone"),
        max_len=40,
    )
    trade_aggressiveness = facade._clip(
        strategist_output.get("trade_aggressiveness") or market_policy.get("trade_aggressiveness"),
        max_len=40,
    )
    monitor_guidance = facade._clip(
        strategist_output.get("monitor_guidance") or market_policy.get("monitor_guidance"),
        max_len=80,
    )
    reason_chain = facade._listify(strategist_output.get("reason_chain"), limit=8, max_len=180)
    if not reason_chain:
        reason_chain = facade._listify(market_policy.get("reason_chain"), limit=8, max_len=180)
    news_targets = facade._listify(strategist_output.get("news_query_targets"), limit=8, max_len=80)
    stress_flags = facade._listify(macro_overlay.get("stress_flags"), limit=6, max_len=60)
    headline_count = facade._safe_int(
        news_context.get("headline_count")
        or strategist_output.get("news_total_headlines")
        or strategist_output.get("market_news_total_headlines")
    )
    query_count = facade._safe_int(
        strategist_output.get("market_news_query_count")
        or len(news_targets)
    )
    global_sentiment_score = strategist_output.get("global_sentiment_score")
    vix_level = (
        fear_index.get("level")
        if fear_index.get("level") not in (None, "")
        else global_signal.get("vix_level")
        if global_signal.get("vix_level") not in (None, "")
        else macro_overlay.get("vix_level")
    )
    missing_flags: List[str] = []
    if global_sentiment_score in (None, ""):
        missing_flags.append("global_sentiment_score_missing")
    if vix_level in (None, ""):
        missing_flags.append("vix_level_missing")
    if headline_count <= 0:
        missing_flags.append("news_headlines_missing")
    if not reason_chain:
        missing_flags.append("reason_chain_missing")
    summary = (
        f"Strategist used regime={market_regime or 'not_captured'}, sentiment={market_sentiment or 'not_captured'}, "
        f"playbook={playbook or 'not_captured'}, risk_tone={risk_tone or 'not_captured'}, "
        f"global_sentiment={facade._format_trace_number(global_sentiment_score, digits=3)}, "
        f"vix={facade._format_trace_number(vix_level, digits=2)}, headlines={headline_count}, targets={query_count}."
    )
    highlights = facade._dedupe_text(
        [
            f"Regime {market_regime or 'not_captured'} / playbook {playbook or 'not_captured'}",
            (
                "Themes: "
                + (", ".join(themes[:4]) if themes else "none")
                + (" | avoid: " + ", ".join(avoid_themes[:4]) if avoid_themes else "")
            ),
            (
                f"Sentiment { facade._format_trace_number(global_sentiment_score, digits=3) } / "
                f"VIX { facade._format_trace_number(vix_level, digits=2) } / "
                f"stress {', '.join(stress_flags) if stress_flags else 'none'}"
            ),
            f"News evidence: {headline_count} headlines across {query_count} targets",
            (
                "Risk tone: "
                + (risk_tone or "not_captured")
                + (f" / aggressiveness: {trade_aggressiveness}" if trade_aggressiveness else "")
            ),
        ],
        limit=6,
        max_len=220,
    )
    return {
        "summary": facade._clip(summary, max_len=320),
        "highlights": highlights,
        "reason_chain": reason_chain,
        "headline_count": headline_count,
        "news_query_count": query_count,
        "news_query_targets": news_targets,
        "global_sentiment_score": global_sentiment_score,
        "vix_level": vix_level,
        "stress_flags": stress_flags,
        "market_regime": market_regime,
        "market_sentiment": market_sentiment,
        "playbook": playbook,
        "risk_tone": risk_tone,
        "trade_aggressiveness": trade_aggressiveness,
        "monitor_guidance": monitor_guidance,
        "themes": list(themes),
        "avoid_themes": list(avoid_themes),
        "missing_flags": missing_flags,
    }



def _build_strategist_decision_frame(
    *,
    facade: Any,
    state: Dict[str, Any],
    strategist_output: Dict[str, Any],
    market_regime: str,
    market_sentiment: str,
    playbook: str,
    themes: List[str],
    avoid_themes: List[str],
) -> Dict[str, Any]:
    event_payload = facade._dict(state.get("strategist_decision_frame"))
    if event_payload:
        out = dict(event_payload)
        theme_packet = facade._dict(strategist_output.get("theme_strength_packet"))
        if theme_packet and not facade._dict(out.get("theme_strength_packet")):
            out["theme_strength_packet"] = theme_packet
        if not out.get("theme_source") and (theme_packet.get("source") or strategist_output.get("theme_source")):
            out["theme_source"] = facade._clip(strategist_output.get("theme_source") or theme_packet.get("source"), max_len=80)
        if not out.get("theme_source_status") and (theme_packet.get("status") or strategist_output.get("theme_source_status")):
            out["theme_source_status"] = facade._clip(
                strategist_output.get("theme_source_status") or theme_packet.get("status"),
                max_len=80,
            )
        if not out.get("theme_source_reason") and (theme_packet.get("reason") or strategist_output.get("theme_source_reason")):
            out["theme_source_reason"] = facade._clip(
                strategist_output.get("theme_source_reason") or theme_packet.get("reason"),
                max_len=160,
            )
        if not out.get("available_themes") and isinstance(strategist_output.get("available_themes"), list):
            out["available_themes"] = list(strategist_output.get("available_themes") or [])[:8]
        if not out.get("selected_themes") and isinstance(strategist_output.get("selected_themes"), list):
            out["selected_themes"] = facade._listify(strategist_output.get("selected_themes"), limit=5, max_len=80)
        if not out.get("theme_strategy") and isinstance(strategist_output.get("theme_strategy"), dict):
            out["theme_strategy"] = facade._dict(strategist_output.get("theme_strategy"))
        return out
    strategy_policy_summary = facade._dict(strategist_output.get("strategy_policy_summary"))
    strategy_memory = facade._dict(strategist_output.get("strategy_memory"))
    theme_packet = facade._dict(strategist_output.get("theme_strength_packet"))
    theme_strength = facade._dict(strategist_output.get("theme_strength")) or facade._dict(theme_packet.get("theme_scores"))
    reason_chain = facade._listify(
        strategist_output.get("reason_chain")
        or facade._dict(strategy_policy_summary.get("market_policy")).get("reason_chain"),
        limit=8,
        max_len=180,
    )
    return {
        "market_regime": market_regime,
        "market_sentiment": market_sentiment,
        "playbook": playbook,
        "themes": list(themes),
        "selected_themes": facade._listify(strategist_output.get("selected_themes"), limit=5, max_len=80),
        "avoid_themes": list(avoid_themes),
        "scanner_bias": facade._clip(strategist_output.get("scanner_bias"), max_len=80),
        "scanner_priority": facade._listify(strategist_output.get("scanner_priority"), limit=8, max_len=80),
        "trade_aggressiveness": facade._clip(strategist_output.get("trade_aggressiveness"), max_len=40),
        "risk_tone": facade._clip(strategist_output.get("risk_tone"), max_len=40),
        "monitor_guidance": facade._clip(strategist_output.get("monitor_guidance"), max_len=80),
        "report_focus": facade._listify(strategist_output.get("report_focus"), limit=8, max_len=80),
        "strategy_memory": strategy_memory,
        "reason_chain": reason_chain,
        "strategy_policy_summary": strategy_policy_summary,
        "theme_strength": theme_strength,
        "theme_strength_packet": theme_packet,
        "available_themes": list(strategist_output.get("available_themes") or [])[:8]
        if isinstance(strategist_output.get("available_themes"), list)
        else [],
        "theme_strategy": facade._dict(strategist_output.get("theme_strategy")),
        "theme_source": facade._clip(strategist_output.get("theme_source") or theme_packet.get("source"), max_len=80),
        "theme_source_status": facade._clip(
            strategist_output.get("theme_source_status") or theme_packet.get("status"),
            max_len=80,
        ),
        "theme_source_reason": facade._clip(
            strategist_output.get("theme_source_reason") or theme_packet.get("reason"),
            max_len=160,
        ),
    }



def _build_strategist_news_evidence_ranked(
    *,
    facade: Any,
    state: Dict[str, Any],
    strategist_output: Dict[str, Any],
    news_context: Dict[str, Any],
    market_news_context: Dict[str, Any],
    candidate_news_context: Dict[str, Any],
) -> Dict[str, Any]:
    event_payload = facade._dict(state.get("strategist_news_evidence_ranked"))
    if event_payload:
        return dict(event_payload)
    return {
        "news_query_targets": facade._listify(strategist_output.get("news_query_targets"), limit=12, max_len=80),
        "candidate_news_ranked": list(candidate_news_context.get("ranked_rows") or [])[:8],
        "market_news_ranked": list(market_news_context.get("ranked_rows") or [])[:8],
        "candidate_news_context": dict(candidate_news_context),
        "market_news_context": dict(market_news_context),
        "news_context": dict(news_context),
    }



def _build_global_sentiment_signal_payload(
    *,
    facade: Any,
    state: Dict[str, Any],
    global_signal: Dict[str, Any],
    macro_overlay: Dict[str, Any],
) -> Dict[str, Any]:
    event_payload = facade._dict(state.get("strategist_global_sentiment_breakdown"))
    if event_payload:
        return dict(event_payload)
    fear_index = facade._dict(global_signal.get("fear_index"))
    return {
        "score": global_signal.get("score"),
        "status": facade._clip(global_signal.get("status"), max_len=40),
        "source": facade._clip(global_signal.get("source"), max_len=80),
        "fear_index": {
            "level": fear_index.get("level"),
            "change_pct": fear_index.get("change_pct"),
            "level_pressure": fear_index.get("level_pressure"),
        },
        "index_moves": facade._dict(global_signal.get("index_moves")),
        "macro_moves": facade._dict(global_signal.get("macro_moves")),
        "stress_flags": facade._listify(macro_overlay.get("stress_flags"), limit=8, max_len=80),
    }



