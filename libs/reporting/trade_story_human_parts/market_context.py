from __future__ import annotations

from typing import Any, Dict, List, Mapping

from libs.reporting.trade_execution_outcome_text import build_execution_outcome_human_payload
from libs.reporting.trade_report_common import (
    clip_text as clip,
    format_ratio_pct,
    list_text as _list_text,
    safe_float,
)


def build_market_context_human(strategist: Dict[str, Any], *, deps: Mapping[str, Any]) -> Dict[str, Any]:
    _build_strategist_evidence_trace = deps["build_strategist_evidence_trace"]
    _korea_indices_bullet = deps["korea_indices_bullet"]
    _list_text = deps["list_text"]
    format_pct = deps["format_pct"]
    safe_float = deps["safe_float"]
    safe_int = deps["safe_int"]
    llm_parsed = strategist.get("llm_parsed_output") if isinstance(strategist.get("llm_parsed_output"), dict) else {}
    input_summary = strategist.get("input_summary") if isinstance(strategist.get("input_summary"), dict) else {}
    fear_index = strategist.get("fear_index") if isinstance(strategist.get("fear_index"), dict) else {}
    macro_overlay = strategist.get("macro_stress_overlay") if isinstance(strategist.get("macro_stress_overlay"), dict) else {}
    macro_moves = strategist.get("global_macro_moves") if isinstance(strategist.get("global_macro_moves"), dict) else {}
    news_context = strategist.get("news_context") if isinstance(strategist.get("news_context"), dict) else {}
    regime = str(llm_parsed.get("market_regime") or strategist.get("market_regime") or "not_captured")
    sentiment_state = str(llm_parsed.get("market_sentiment") or strategist.get("market_sentiment") or strategist.get("global_sentiment_status") or "not_captured")
    playbook = str(strategist.get("playbook") or llm_parsed.get("playbook") or "not_captured")
    themes = [str(x or "") for x in list(strategist.get("themes") or []) if str(x or "").strip()][:4]
    decision_frame = strategist.get("decision_frame") if isinstance(strategist.get("decision_frame"), dict) else {}
    theme_packet = strategist.get("theme_strength_packet") if isinstance(strategist.get("theme_strength_packet"), dict) else {}
    if not theme_packet and isinstance(decision_frame.get("theme_strength_packet"), dict):
        theme_packet = dict(decision_frame.get("theme_strength_packet") or {})
    theme_source = str(strategist.get("theme_source") or theme_packet.get("source") or "").strip()
    theme_status = str(strategist.get("theme_source_status") or theme_packet.get("status") or "").strip()
    theme_reason = str(strategist.get("theme_source_reason") or theme_packet.get("reason") or "").strip()
    theme_top = _list_text(theme_packet.get("top_themes"), limit=6, max_len=80)
    theme_scores = dict(theme_packet.get("theme_scores") or {}) if isinstance(theme_packet.get("theme_scores"), dict) else {}
    global_sentiment_score = strategist.get("global_sentiment_score")
    if global_sentiment_score in (None, ""):
        global_sentiment_score = input_summary.get("global_sentiment_score")
    if not fear_index and input_summary:
        fear_index = {
            "level": input_summary.get("vix_level"),
            "change_pct": input_summary.get("vix_change_pct"),
            "level_pressure": input_summary.get("vix_level_pressure"),
        }
    if not macro_moves and input_summary:
        macro_moves = {
            "vix_level": input_summary.get("vix_level"),
            "vix_pct": input_summary.get("vix_change_pct"),
            "vix_level_pressure": input_summary.get("vix_level_pressure"),
        }
    vix_level = (
        fear_index.get("level")
        if fear_index
        else macro_moves.get("vix_level")
        if macro_moves
        else macro_overlay.get("vix_level")
        if macro_overlay
        else input_summary.get("vix_level")
    )
    dxy_pct = (
        macro_moves.get("dxy_pct")
        if macro_moves
        else macro_overlay.get("dxy_pct")
        if macro_overlay
        else None
    )
    news_total = safe_int(
        news_context.get("headline_count"),
        safe_int(
            strategist.get("market_news_total_headlines"),
            safe_int(strategist.get("news_total_headlines"), safe_int(input_summary.get("headline_count"), 0)),
        ),
    )
    query_targets = _list_text(
        strategist.get("news_query_targets") or input_summary.get("news_query_targets") or [],
        limit=8,
        max_len=80,
    )
    query_count = safe_int(
        strategist.get("market_news_query_count"),
        safe_int(strategist.get("news_symbol_count"), len(query_targets)),
    )
    market_signal_total = safe_int(news_context.get("market_signal_total"), safe_int(input_summary.get("market_signal_total"), 0))
    candidate_signal_total = safe_int(news_context.get("candidate_signal_total"), safe_int(input_summary.get("candidate_signal_total"), 0))
    stress_flags = [str(x or "") for x in list(macro_overlay.get("stress_flags") or []) if str(x or "").strip()]
    defensive_mode = bool(macro_overlay.get("active")) or bool(stress_flags) or (safe_float(vix_level, 0.0) >= 25.0)
    market_news_titles = _list_text(input_summary.get("market_news_titles"), limit=3, max_len=140)
    candidate_news_titles = _list_text(input_summary.get("candidate_news_titles"), limit=3, max_len=140)
    key_events_hint = _list_text(input_summary.get("key_events_hint"), limit=5, max_len=180)
    strategist_evidence_trace = _build_strategist_evidence_trace(
        strategist,
        fallback_market_titles=market_news_titles,
        fallback_candidate_titles=candidate_news_titles,
    )
    candidate_hints = _list_text(
        strategist_evidence_trace.get("candidate_hints"),
        limit=8,
        max_len=24,
    )
    market_headlines = _list_text(
        strategist_evidence_trace.get("market_headlines"),
        limit=3,
        max_len=180,
    ) or market_news_titles
    symbol_headlines = _list_text(
        strategist_evidence_trace.get("symbol_headlines"),
        limit=3,
        max_len=180,
    ) or candidate_news_titles
    global_sentiment_signal = (
        dict(strategist_evidence_trace.get("global_sentiment_signal") or {})
        if isinstance(strategist_evidence_trace.get("global_sentiment_signal"), dict)
        else {}
    )
    if not global_sentiment_signal and isinstance(strategist.get("global_sentiment_signal"), dict):
        global_sentiment_signal = dict(strategist.get("global_sentiment_signal") or {})
    korea_indices = (
        dict(strategist.get("korea_indices") or {})
        if isinstance(strategist.get("korea_indices"), dict)
        else dict(global_sentiment_signal.get("korea_indices") or {})
        if isinstance(global_sentiment_signal.get("korea_indices"), dict)
        else dict(input_summary.get("korea_indices") or {})
        if isinstance(input_summary.get("korea_indices"), dict)
        else {}
    )
    korea_indices_text = _korea_indices_bullet(korea_indices)
    fear_index_trace = (
        dict(strategist_evidence_trace.get("fear_index") or {})
        if isinstance(strategist_evidence_trace.get("fear_index"), dict)
        else dict(fear_index or {})
    )
    key_events = _list_text(strategist_evidence_trace.get("key_events"), limit=6, max_len=180) or key_events_hint
    news_summary = (
        f"{news_total} headlines were considered across {query_count} targets "
        f"({market_signal_total} market / {candidate_signal_total} candidate signals)."
        if news_total > 0
        else "No strong news input was captured for this run."
    )
    stress_summary = (
        f"Macro stress was elevated because {', '.join(stress_flags)} remained active."
        if stress_flags
        else "No explicit macro stress flags were active in the strategist frame."
    )
    summary = (
        f"Market regime was {regime} with a {playbook} playbook. "
        f"Global sentiment scored {format_pct(global_sentiment_score)} and VIX was {format_pct(vix_level)}. "
        f"{stress_summary} {news_summary}"
    )
    if korea_indices_text:
        summary = f"{summary} Korea indices: {korea_indices_text}."
    bullets = [
        f"Market regime: {regime}",
        f"Market sentiment: {sentiment_state}",
        f"Playbook: {playbook}",
        f"Global sentiment score: {format_pct(global_sentiment_score)}",
        f"VIX / fear index level: {format_pct(vix_level)}",
        f"Dollar index move: {format_pct(dxy_pct)}%",
        f"Themes detected: {', '.join(themes) if themes else 'none captured'}",
        f"Defensive mode: {'enabled' if defensive_mode else 'not enabled'}",
        f"News input: {news_summary}",
    ]
    if korea_indices_text:
        bullets.append(f"Korea indices: {korea_indices_text}")
    if theme_packet or theme_source or theme_status or theme_reason:
        bullets.append(
            "Kiwoom theme packet: "
            f"source={theme_source or 'not_captured'}, "
            f"status={theme_status or 'not_captured'}, "
            f"reason={theme_reason or 'not_captured'}, "
            f"top_themes={', '.join(theme_top) if theme_top else 'none'}, "
            f"score_count={len(theme_scores)}"
        )
    if query_targets:
        bullets.append(f"News query targets: {', '.join(query_targets)}")
    if key_events_hint:
        bullets.append("Key strategist inputs: " + "; ".join(key_events_hint[:3]))
    if candidate_hints:
        bullets.append("Strategist candidate hints: " + ", ".join(candidate_hints[:5]))
    if market_headlines:
        bullets.append("Strategist market headlines: " + "; ".join(market_headlines[:3]))
    if symbol_headlines:
        bullets.append("Strategist symbol headlines: " + "; ".join(symbol_headlines[:3]))
    return {
        "regime": regime,
        "market_sentiment": sentiment_state,
        "playbook": playbook,
        "themes": themes,
        "theme_strength_packet": theme_packet,
        "theme_source": theme_source,
        "theme_source_status": theme_status,
        "theme_source_reason": theme_reason,
        "theme_strength_top_themes": theme_top,
        "theme_strength_scores": theme_scores,
        "global_sentiment_score": global_sentiment_score,
        "global_sentiment_signal": global_sentiment_signal,
        "korea_indices": korea_indices,
        "vix_level": vix_level,
        "fear_index": fear_index_trace,
        "stress_flags": stress_flags,
        "defensive_mode": defensive_mode,
        "headline_count": news_total,
        "news_query_count": query_count,
        "market_signal_total": market_signal_total,
        "candidate_signal_total": candidate_signal_total,
        "news_query_targets": query_targets,
        "key_events_hint": key_events_hint,
        "key_events": key_events,
        "candidate_hints": candidate_hints,
        "market_headlines": market_headlines,
        "symbol_headlines": symbol_headlines,
        "market_news_titles": market_headlines or market_news_titles,
        "candidate_news_titles": symbol_headlines or candidate_news_titles,
        "strategist_evidence_trace": strategist_evidence_trace,
        "news_input_summary": news_summary,
        "summary": summary,
        "bullets": bullets,
    }



