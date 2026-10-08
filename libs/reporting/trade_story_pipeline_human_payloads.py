from __future__ import annotations

from typing import Any, Dict, List, Mapping

from libs.reporting.trade_execution_outcome_text import build_execution_outcome_human_payload
from libs.reporting.trade_report_common import (
    clip_text as clip,
    format_ratio_pct,
    list_text as _list_text,
    safe_float,
)


def normalize_stop_thresholds(thresholds: Dict[str, Any]) -> Dict[str, Any]:
    data = thresholds if isinstance(thresholds, dict) else {}
    nested = data.get("thresholds") if isinstance(data.get("thresholds"), dict) else {}
    return nested or data


def resolve_strategist_adaptive_exit(monitor: Dict[str, Any]) -> Dict[str, Any]:
    data = monitor if isinstance(monitor, dict) else {}
    for candidate in (
        ((data.get("policy_ref") or {}).get("exit_plan") or {}).get("adaptive_exit"),
        (((data.get("decision_trace") or {}).get("policy_ref") or {}).get("exit_plan") or {}).get("adaptive_exit"),
        (((data.get("timing_assessment") or {}).get("entry_plan") or {}).get("adaptive_exit")),
    ):
        if isinstance(candidate, dict) and candidate:
            return candidate
    return {}


def resolve_adaptive_stop_loss_pct(monitor: Dict[str, Any], thresholds: Dict[str, Any]) -> Any:
    thresholds = normalize_stop_thresholds(thresholds)
    adaptive_exit = monitor.get("adaptive_exit") if isinstance(monitor.get("adaptive_exit"), dict) else {}
    if adaptive_exit.get("stop_loss_pct") not in (None, ""):
        return adaptive_exit.get("stop_loss_pct")
    if thresholds.get("adaptive_stop_loss_pct") not in (None, ""):
        return thresholds.get("adaptive_stop_loss_pct")
    threshold_snapshot = monitor.get("threshold_snapshot") if isinstance(monitor.get("threshold_snapshot"), dict) else {}
    if threshold_snapshot.get("adaptive_stop_loss_pct") not in (None, ""):
        return threshold_snapshot.get("adaptive_stop_loss_pct")
    return None


def build_monitor_stop_policy_trace(monitor: Dict[str, Any], thresholds: Dict[str, Any]) -> Dict[str, Any]:
    thresholds = normalize_stop_thresholds(thresholds)
    strategist_adaptive_exit = resolve_strategist_adaptive_exit(monitor)
    adaptive_stop_loss_pct = resolve_adaptive_stop_loss_pct(monitor, thresholds)
    hard_stop_pct = (
        thresholds.get("hard_stop_pct")
        if thresholds.get("hard_stop_pct") not in (None, "")
        else monitor.get("hard_stop_pct")
    )
    effective_stop_loss_pct = (
        thresholds.get("effective_stop_loss_pct")
        if thresholds.get("effective_stop_loss_pct") not in (None, "")
        else adaptive_stop_loss_pct
        if adaptive_stop_loss_pct not in (None, "")
        else hard_stop_pct
    )
    return {
        "hard_stop_pct": hard_stop_pct,
        "adaptive_stop_loss_pct": adaptive_stop_loss_pct,
        "effective_stop_loss_pct": effective_stop_loss_pct,
        "trailing_stop_pct": thresholds.get("trailing_stop_pct"),
        "take_profit_pct": thresholds.get("take_profit_pct"),
        "partial_take_profit_pct": thresholds.get("partial_take_profit_pct"),
        "partial_take_profit_fraction": thresholds.get("partial_take_profit_fraction"),
        "profit_ladder_levels_pct": thresholds.get("profit_ladder_levels_pct"),
        "profit_ladder_fraction": thresholds.get("profit_ladder_fraction"),
        "risk_reward_take_profit_r": thresholds.get("risk_reward_take_profit_r"),
        "risk_reward_take_profit_rungs": thresholds.get("risk_reward_take_profit_rungs"),
        "risk_reward_take_profit_fraction": thresholds.get("risk_reward_take_profit_fraction"),
        "risk_reward_take_profit_min_pct": thresholds.get("risk_reward_take_profit_min_pct"),
        "vwap_extension_take_profit_pct": thresholds.get("vwap_extension_take_profit_pct"),
        "vwap_extension_take_profit_min_pct": thresholds.get("vwap_extension_take_profit_min_pct"),
        "resistance_take_profit_near_pct": thresholds.get("resistance_take_profit_near_pct"),
        "resistance_take_profit_min_pct": thresholds.get("resistance_take_profit_min_pct"),
        "profit_time_stop_sec": thresholds.get("profit_time_stop_sec"),
        "profit_time_stop_min_pct": thresholds.get("profit_time_stop_min_pct"),
        "profit_time_stop_peak_giveback_pct": thresholds.get("profit_time_stop_peak_giveback_pct"),
        "volume_exhaustion_take_profit_min_pct": thresholds.get("volume_exhaustion_take_profit_min_pct"),
        "volume_exhaustion_volume_ratio_max": thresholds.get("volume_exhaustion_volume_ratio_max"),
        "volume_exhaustion_strength_max": thresholds.get("volume_exhaustion_strength_max"),
        "opening_gap_profit_take_min_pct": thresholds.get("opening_gap_profit_take_min_pct"),
        "opening_gap_profit_take_window_sec": thresholds.get("opening_gap_profit_take_window_sec"),
        "opening_gap_profit_take_fraction": thresholds.get("opening_gap_profit_take_fraction"),
        "cost_aware_profit_floor_enabled": thresholds.get("cost_aware_profit_floor_enabled"),
        "round_trip_cost_floor_pct": thresholds.get("round_trip_cost_floor_pct"),
        "min_net_profit_buffer_pct": thresholds.get("min_net_profit_buffer_pct"),
        "cost_aware_profit_floor_pct": thresholds.get("cost_aware_profit_floor_pct"),
        "strategist_baseline_stop_loss_pct": strategist_adaptive_exit.get("stop_loss_pct"),
        "strategist_baseline_take_profit_pct": strategist_adaptive_exit.get("take_profit_pct"),
        "strategist_baseline_trailing_stop_pct": strategist_adaptive_exit.get("trailing_stop_pct"),
    }


def build_monitor_blocker_trace(monitor: Dict[str, Any]) -> Dict[str, Any]:
    data = monitor if isinstance(monitor, dict) else {}
    entry_metrics = data.get("entry_metrics") if isinstance(data.get("entry_metrics"), dict) else {}
    entry_thresholds = data.get("entry_thresholds") if isinstance(data.get("entry_thresholds"), dict) else {}
    timing_assessment = data.get("timing_assessment") if isinstance(data.get("timing_assessment"), dict) else {}
    policy_ref = data.get("policy_ref") if isinstance(data.get("policy_ref"), dict) else {}
    threshold_shortfalls: List[str] = []
    if entry_metrics.get("volume_ratio") not in (None, "") and entry_thresholds.get("volume_ratio_min") not in (None, ""):
        volume_ratio = safe_float(entry_metrics.get("volume_ratio"), 0.0)
        volume_ratio_min = safe_float(entry_thresholds.get("volume_ratio_min"), 0.0)
        if volume_ratio < volume_ratio_min:
            threshold_shortfalls.append(f"volume ratio {volume_ratio:.2f} below min {volume_ratio_min:.2f}")
    if entry_metrics.get("extended_from_vwap_pct") not in (None, "") and entry_thresholds.get("max_extended_from_vwap_pct") not in (None, ""):
        extended = safe_float(entry_metrics.get("extended_from_vwap_pct"), 0.0)
        extended_max = safe_float(entry_thresholds.get("max_extended_from_vwap_pct"), 0.0)
        if extended > extended_max:
            threshold_shortfalls.append(
                f"VWAP extension {format_ratio_pct(extended)}% above max {format_ratio_pct(extended_max)}%"
            )
    if entry_metrics.get("pullback_depth_pct") not in (None, "") and entry_thresholds.get("pullback_min_pct") not in (None, ""):
        pullback_depth = safe_float(entry_metrics.get("pullback_depth_pct"), 0.0)
        pullback_min = safe_float(entry_thresholds.get("pullback_min_pct"), 0.0)
        if pullback_depth < pullback_min:
            threshold_shortfalls.append(
                f"pullback depth {format_ratio_pct(pullback_depth)}% below min {format_ratio_pct(pullback_min)}%"
            )
    return {
        "entry_check_summary": clip(data.get("entry_check_summary"), max_len=260),
        "entry_blockers": _list_text(data.get("entry_blockers"), limit=8, max_len=120),
        "threshold_shortfalls": threshold_shortfalls[:4],
        "timing_assessment": dict(timing_assessment or {}),
        "policy_ref": dict(policy_ref or {}),
        "entry_condition_path": clip(data.get("entry_condition_path"), max_len=80),
        "entry_condition_paths_passed": _list_text(data.get("entry_condition_paths_passed"), limit=4, max_len=80),
        "condition_scores": dict(data.get("condition_scores") or {}),
        "grouped_logic_trace": dict(data.get("grouped_logic_trace") or {}),
    }


def build_execution_outcome_human(
    execution: Dict[str, Any],
    executor: Dict[str, Any],
    *,
    story_type: str,
    mode_label: str,
) -> Dict[str, Any]:
    return build_execution_outcome_human_payload(
        execution,
        executor,
        story_type=story_type,
        mode_label=mode_label,
    )

# P1.5.2 R2-C: market / scanner / monitor human payload owners.


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



def build_scanner_reason_human(scanner: Dict[str, Any], strategist: Dict[str, Any], *, deps: Mapping[str, Any]) -> Dict[str, Any]:
    _build_news_scanner_contribution_trace = deps["build_news_scanner_contribution_trace"]
    _build_scanner_selection_trace = deps["build_scanner_selection_trace"]
    _list_text = deps["list_text"]
    _scanner_chart_fit_payload = deps["scanner_chart_fit_payload"]
    _scanner_macro_chart_fit_payload = deps["scanner_macro_chart_fit_payload"]
    clip = deps["clip"]
    confidence_label = deps["confidence_label"]
    normalized_feature_coverage = deps["normalized_feature_coverage"]
    safe_float = deps["safe_float"]
    safe_int = deps["safe_int"]
    selected = scanner.get("selected_candidate") if isinstance(scanner.get("selected_candidate"), dict) else {}
    selected_symbol = str(selected.get("symbol") or scanner.get("top_stock") or "").strip()
    ranking_table = [dict(row) for row in list(scanner.get("ranking_table") or []) if isinstance(row, dict)]
    top_ranked_symbols = [str(row.get("symbol") or "").strip() for row in ranking_table if str(row.get("symbol") or "").strip()]
    if not top_ranked_symbols:
        top_ranked_symbols = [str(x or "") for x in list(scanner.get("top_ranked_symbols") or []) if str(x or "").strip()]
    selected_rank = 0
    selected_row = next(
        (row for row in ranking_table if str(row.get("symbol") or "").strip() == selected_symbol),
        {},
    )
    if selected_row:
        selected_rank = safe_int(selected_row.get("rank"), 0)
    elif selected_symbol and selected_symbol in top_ranked_symbols:
        selected_rank = int(top_ranked_symbols.index(selected_symbol) + 1)
    elif selected_symbol:
        selected_rank = 1
    universe_size = max(
        0,
        safe_int(scanner.get("universe_size"), 0)
        or safe_int(scanner.get("candidate_pool_after_filter"), 0)
        or safe_int(scanner.get("candidate_pool_before_filter"), 0)
        or len(ranking_table)
        or len(top_ranked_symbols),
    )
    selected_sources = [str(x or "") for x in list(selected.get("sources") or []) if str(x or "").strip()]
    score_breakdown = selected.get("score_breakdown") if isinstance(selected.get("score_breakdown"), dict) else {}
    component_snapshot = selected.get("component_snapshot") if isinstance(selected.get("component_snapshot"), dict) else {}
    preview_map = {
        str(row.get("symbol") or "").strip(): dict(row)
        for row in list(scanner.get("candidate_preview") or [])
        if isinstance(row, dict) and str(row.get("symbol") or "").strip()
    }
    basis: List[str] = []
    if safe_float(score_breakdown.get("trading_value"), 0.0) > 0:
        basis.append("trading value")
    if safe_float(score_breakdown.get("volume_surge"), 0.0) > 0 or "top_volume" in selected_sources:
        basis.append("turnover and volume")
    if safe_float(score_breakdown.get("theme_boost"), 0.0) > 0 or "sector_theme" in selected_sources:
        basis.append("theme and sector alignment")
    if safe_float(score_breakdown.get("sentiment"), 0.0) > 0:
        basis.append("sentiment support")
    if not basis:
        basis.append("combined scanner ranking score")
    coverage = normalized_feature_coverage(scanner, selected)
    selected_score = selected.get("score_total")
    if selected_score in (None, ""):
        selected_score = selected_row.get("score_total")
    selected_risk = selected.get("risk_score")
    if selected_risk in (None, ""):
        selected_risk = selected_row.get("risk_score")
    selected_confidence = selected.get("confidence")
    if selected_confidence in (None, ""):
        selected_confidence = selected_row.get("confidence")
    scanner_chart_fit = _scanner_chart_fit_payload(selected)
    if not scanner_chart_fit:
        scanner_chart_fit = _scanner_chart_fit_payload(selected_row)
    if not scanner_chart_fit:
        scanner_chart_fit = _scanner_chart_fit_payload(scanner)
    scanner_macro_chart_fit = _scanner_macro_chart_fit_payload(selected)
    if not scanner_macro_chart_fit:
        scanner_macro_chart_fit = _scanner_macro_chart_fit_payload(selected_row)
    if not scanner_macro_chart_fit:
        scanner_macro_chart_fit = _scanner_macro_chart_fit_payload(scanner)
    news_scanner_contribution = _build_news_scanner_contribution_trace(
        selected_symbol=selected_symbol,
        selected_score=selected_score,
        selected_sources=selected_sources,
        score_breakdown=score_breakdown,
        component_snapshot=component_snapshot,
        strategist=strategist if isinstance(strategist, dict) else {},
    )
    top_reasons: List[str] = [
        f"highest combined scanner score ({safe_float(selected_score, 0.0):.3f})",
        f"selected from {', '.join(selected_sources) if selected_sources else 'captured scanner sources'}",
        f"chart feature coverage {coverage['present']}/{coverage['total']}" if coverage["total"] > 0 else "chart feature coverage was not captured",
        f"aligned with strategist playbook {strategist.get('playbook') or 'not_captured'}",
    ]
    runner_ups: List[Dict[str, Any]] = []
    ranked_preview = ranking_table[:3] if ranking_table else []
    for row in ranked_preview:
        symbol = str(row.get("symbol") or "").strip()
        if not symbol or symbol == selected_symbol:
            continue
        preview = preview_map.get(symbol, {})
        why_parts: List[str] = []
        preview_why = clip(preview.get("why") or row.get("why"), max_len=140)
        if preview_why:
            why_parts.append(preview_why)
        score_gap = None
        if selected_score not in (None, "") and row.get("score_total") not in (None, ""):
            score_gap = safe_float(selected_score, 0.0) - safe_float(row.get("score_total"), 0.0)
            why_parts.append(f"score gap {score_gap:.3f}")
        row_risk = row.get("risk_score")
        if selected_risk not in (None, "") and row_risk not in (None, "") and safe_float(row_risk, 0.0) > safe_float(selected_risk, 0.0):
            why_parts.append(
                f"higher risk ({safe_float(row_risk, 0.0):.3f} vs {safe_float(selected_risk, 0.0):.3f})"
            )
        row_confidence = row.get("confidence")
        if selected_confidence not in (None, "") and row_confidence not in (None, "") and safe_float(row_confidence, 0.0) < safe_float(selected_confidence, 0.0):
            why_parts.append(
                f"lower confidence ({safe_float(row_confidence, 0.0):.3f} vs {safe_float(selected_confidence, 0.0):.3f})"
            )
        runner_ups.append(
            {
                "symbol": symbol,
                "rank": safe_int(row.get("rank"), 0),
                "score_total": row.get("score_total"),
                "risk_score": row.get("risk_score"),
                "confidence": row.get("confidence"),
                "scanner_chart_fit": _scanner_chart_fit_payload(row),
                "scanner_macro_chart_fit": _scanner_macro_chart_fit_payload(row),
                "why": "; ".join(why_parts) if why_parts else "lower final ranking than the selected symbol",
            }
        )
        if len(runner_ups) >= 2:
            break
    top_candidates: List[Dict[str, Any]] = []
    for row in ranked_preview:
        symbol = str(row.get("symbol") or "").strip()
        if not symbol:
            continue
        top_candidates.append(
            {
                "rank": safe_int(row.get("rank"), 0),
                "symbol": symbol,
                "score_total": row.get("score_total"),
                "risk_score": row.get("risk_score"),
                "confidence": row.get("confidence"),
                "scanner_chart_fit": _scanner_chart_fit_payload(row),
                "scanner_macro_chart_fit": _scanner_macro_chart_fit_payload(row),
            }
        )
    bullets = [
        f"Universe scanned: {universe_size}",
        f"Selected rank: #{selected_rank}" if selected_rank else "Selected rank: not_captured",
        f"Ranking basis: {', '.join(basis)}",
        f"Selected because: {top_reasons[0]}",
        f"Selection sources: {', '.join(selected_sources) if selected_sources else 'not captured'}",
        f"Chart / feature coverage: {coverage['present']}/{coverage['total']}" if coverage["total"] else "Chart / feature coverage: not captured",
        (
            "Scanner chart-fit: "
            f"{safe_float(scanner_chart_fit.get('score'), 0.0):.3f} "
            f"({scanner_chart_fit.get('authority') or 'not_captured'})"
        )
        if scanner_chart_fit
        else "Scanner chart-fit: not captured",
        (
            "Scanner macro chart-fit: "
            f"{safe_float(scanner_macro_chart_fit.get('score'), 0.0):.3f} "
            f"(bias {safe_float(scanner_macro_chart_fit.get('bias'), 0.0):+.3f})"
        )
        if scanner_macro_chart_fit
        else "Scanner macro chart-fit: not captured",
        (
            "Core score contributions: "
            f"trading_value {safe_float(score_breakdown.get('trading_value'), 0.0):+.3f}, "
            f"momentum {safe_float(score_breakdown.get('momentum'), 0.0):+.3f}, "
            f"trend {safe_float(score_breakdown.get('trend'), 0.0):+.3f}, "
            f"theme_boost {safe_float(score_breakdown.get('theme_boost'), 0.0):+.3f}, "
            f"sentiment {safe_float(score_breakdown.get('sentiment'), 0.0):+.3f}"
        ),
    ]
    sentiment_inputs = news_scanner_contribution.get("sentiment_inputs") if isinstance(news_scanner_contribution.get("sentiment_inputs"), dict) else {}
    if any(sentiment_inputs.get(key) is not None for key in ("news_sentiment_score", "global_sentiment_score", "blended_sentiment_component")):
        bullets.append(
            "Sentiment input trace: "
            f"news={safe_float(sentiment_inputs.get('news_sentiment_score'), 0.0):+.3f}, "
            f"global={safe_float(sentiment_inputs.get('global_sentiment_score'), 0.0):+.3f}, "
            f"blended={safe_float(sentiment_inputs.get('blended_sentiment_component'), 0.0):+.3f}, "
            f"weighted_score={safe_float(sentiment_inputs.get('weighted_sentiment_score_contribution'), 0.0):+.3f}"
        )
    theme_trace = news_scanner_contribution.get("theme_alignment_trace") if isinstance(news_scanner_contribution.get("theme_alignment_trace"), dict) else {}
    bullets.append(
        "Theme linkage: "
        f"matched={bool(theme_trace.get('theme_source_matched'))}, "
        f"theme_boost={safe_float(theme_trace.get('theme_boost_score_contribution'), 0.0):+.3f}, "
        f"themes={', '.join(_list_text(theme_trace.get('strategist_themes'), limit=4, max_len=60)) or 'none captured'}, "
        f"source={theme_trace.get('theme_source') or 'not_captured'}, "
        f"status={theme_trace.get('theme_source_status') or 'not_captured'}, "
        f"reason={theme_trace.get('theme_source_reason') or 'not_captured'}"
    )
    news_linkage = news_scanner_contribution.get("news_linkage_trace") if isinstance(news_scanner_contribution.get("news_linkage_trace"), dict) else {}
    if safe_int(news_linkage.get("symbol_headline_count"), 0) > 0 or safe_int(news_linkage.get("market_headline_count"), 0) > 0:
        bullets.append(
            "News linkage to scanner: "
            f"symbol_headlines={safe_int(news_linkage.get('symbol_headline_count'), 0)}, "
            f"market_headlines={safe_int(news_linkage.get('market_headline_count'), 0)}, "
            f"query_targets={', '.join(_list_text(news_linkage.get('news_query_targets'), limit=5, max_len=60)) or 'not captured'}"
        )
    if top_candidates:
        bullets.append(
            "Top candidates: "
            + "; ".join(
                f"#{safe_int(row.get('rank'), 0)} {row.get('symbol')} score {safe_float(row.get('score_total'), 0.0):.3f}"
                for row in top_candidates
            )
        )
    if runner_ups:
        bullets.append("Why not others: " + "; ".join(f"{row['symbol']} was weaker because {row['why']}" for row in runner_ups))
    scanner_selection_trace = _build_scanner_selection_trace(
        {
            "selected_symbol": selected_symbol,
            "selected_rank": selected_rank,
            "top_candidates": top_candidates,
            "score_breakdown": score_breakdown,
            "selection_basis": "; ".join(top_reasons[:3]) if top_reasons else "",
            "summary": (
                f"Scanner selected {selected_symbol or '-'} as rank #{selected_rank or 1} out of {universe_size or 0} candidates."
            ),
            "scanner_chart_fit": dict(scanner_chart_fit or {}),
            "scanner_macro_chart_fit": dict(scanner_macro_chart_fit or {}),
        },
        scanner,
    )
    scanner_selection_trace["news_scanner_contribution"] = dict(news_scanner_contribution)
    return {
        "selected_symbol": selected_symbol,
        "selected_rank": selected_rank,
        "universe_size": universe_size,
        "selected_score": selected_score,
        "selected_sources": selected_sources,
        "source_scores": selected.get("source_scores") if isinstance(selected.get("source_scores"), dict) else {},
        "score_breakdown": score_breakdown,
        "ranking_basis": basis,
        "confidence": selected_confidence,
        "confidence_label": confidence_label(selected_confidence),
        "top_reasons": top_reasons,
        "top_candidates": top_candidates,
        "runner_ups": runner_ups,
        "ranked_candidates": list(scanner_selection_trace.get("ranked_candidates") or [])[:5],
        "selection_reason": clip(scanner_selection_trace.get("selection_reason"), max_len=260),
        "selected_symbol_score_drivers": dict(scanner_selection_trace.get("selected_symbol_score_drivers") or {}),
        "scanner_chart_fit": dict(scanner_chart_fit or {}),
        "scanner_macro_chart_fit": dict(scanner_macro_chart_fit or {}),
        "news_scanner_contribution": dict(news_scanner_contribution),
        "scanner_selection_trace": dict(scanner_selection_trace or {}),
        "q9_decision_id": str(scanner.get("q9_decision_id") or ""),
        "q9_decision_snapshot": dict(scanner.get("q9_decision_snapshot") or {})
        if isinstance(scanner.get("q9_decision_snapshot"), dict)
        else {},
        "q9_decision_snapshot_path": str(scanner.get("q9_decision_snapshot_path") or ""),
        "summary": (
            f"Scanner selected {selected_symbol or '-'} as rank #{selected_rank or 1} out of {universe_size or 0} candidates "
            f"with score {safe_float(selected_score, 0.0):.3f} because it led on {', '.join(basis[:3])}."
        ),
        "comparison": (
            f"{selected_symbol} ranked #{selected_rank} out of {universe_size} because it had the strongest overall blend of "
            f"{', '.join(basis[:3])}."
            if selected_symbol
            else "Scanner did not record a selected symbol for this run."
        ),
        "bullets": bullets,
    }



def build_monitor_reason_human(monitor: Dict[str, Any], execution: Dict[str, Any], *, deps: Mapping[str, Any]) -> Dict[str, Any]:
    _build_monitor_blocker_trace = deps["build_monitor_blocker_trace"]
    _build_monitor_stop_policy_trace = deps["build_monitor_stop_policy_trace"]
    _list_text = deps["list_text"]
    _merge_missing_values = deps["merge_missing_values"]
    format_exit_label = deps["format_exit_label"]
    format_ratio_pct = deps["format_ratio_pct"]
    safe_float = deps["safe_float"]
    safe_int = deps["safe_int"]
    action = str(execution.get("action") or "").upper()
    decision_trace = monitor.get("decision_trace") if isinstance(monitor.get("decision_trace"), dict) else {}
    thresholds = monitor.get("thresholds") if isinstance(monitor.get("thresholds"), dict) else {}
    thresholds_guards_used = (
        decision_trace.get("thresholds_guards_used")
        if isinstance(decision_trace.get("thresholds_guards_used"), dict)
        else (
            monitor.get("thresholds_guards_used")
            if isinstance(monitor.get("thresholds_guards_used"), dict)
            else {}
        )
    )
    threshold_snapshot = (
        monitor.get("threshold_snapshot")
        if isinstance(monitor.get("threshold_snapshot"), dict)
        else {}
    )
    thresholds = _merge_missing_values(
        thresholds,
        thresholds_guards_used.get("thresholds") if isinstance(thresholds_guards_used.get("thresholds"), dict) else {},
    )
    for key in (
        "stop_loss_pct",
        "effective_stop_loss_pct",
        "effective_stop_reason",
        "take_profit_pct",
        "peak_drawdown_exit_pct",
        "trailing_stop_pct",
        "vwap_breakdown_pct",
        "intraday_low_break_pct",
        "trend_strength_floor",
    ):
        if thresholds.get(key) in (None, "", [], {}):
            thresholds[key] = monitor.get(key)
    trigger_details = monitor.get("trigger_details") if isinstance(monitor.get("trigger_details"), dict) else {}
    decision_reason_chain = [str(x or "") for x in list(monitor.get("decision_reason_chain") or []) if str(x or "").strip()]
    timing_assessment = decision_trace.get("timing_assessment") if isinstance(decision_trace.get("timing_assessment"), dict) else {}
    policy_ref = decision_trace.get("policy_ref") if isinstance(decision_trace.get("policy_ref"), dict) else {}
    received_policy = (
        monitor.get("received_policy")
        if isinstance(monitor.get("received_policy"), dict)
        else (
            threshold_snapshot.get("received_policy")
            if isinstance(threshold_snapshot.get("received_policy"), dict)
            else (
                policy_ref.get("received_policy")
                if isinstance(policy_ref.get("received_policy"), dict)
                else {}
            )
        )
    )
    effective_policy = (
        monitor.get("effective_policy")
        if isinstance(monitor.get("effective_policy"), dict)
        else (
            threshold_snapshot.get("effective_policy")
            if isinstance(threshold_snapshot.get("effective_policy"), dict)
            else (
                policy_ref.get("effective_policy")
                if isinstance(policy_ref.get("effective_policy"), dict)
                else {}
            )
        )
    )
    policy_adjustment_summary = str(
        monitor.get("policy_adjustment_summary")
        or threshold_snapshot.get("policy_adjustment_summary")
        or policy_ref.get("policy_adjustment_summary")
        or ""
    ).strip()
    effective_policy_deltas = [
        dict(row)
        for row in list(
            monitor.get("effective_policy_deltas")
            or threshold_snapshot.get("effective_policy_deltas")
            or policy_ref.get("effective_policy_deltas")
            or []
        )[:8]
        if isinstance(row, dict)
    ]
    entry_check_summary = str(decision_trace.get("entry_check_summary") or "").strip()
    entry_blockers = [str(x or "") for x in list(decision_trace.get("entry_blockers") or []) if str(x or "").strip()]
    entry_reason = str(
        timing_assessment.get("entry_reason")
        or monitor.get("entry_reason")
        or ""
    ).strip()
    entry_pattern = str(
        timing_assessment.get("entry_pattern")
        or monitor.get("entry_pattern")
        or ""
    ).strip()
    entry_signal_chain = [str(x or "") for x in list(monitor.get("entry_signal_chain") or []) if str(x or "").strip()]
    entry_condition_path = str(monitor.get("entry_condition_path") or "").strip()
    entry_condition_paths_passed = [str(x or "") for x in list(monitor.get("entry_condition_paths_passed") or []) if str(x or "").strip()]
    entry_condition_scores = monitor.get("entry_condition_scores") if isinstance(monitor.get("entry_condition_scores"), dict) else {}
    entry_grouped_logic_trace = monitor.get("entry_grouped_logic_trace") if isinstance(monitor.get("entry_grouped_logic_trace"), dict) else {}
    entry_metrics = monitor.get("entry_metrics") if isinstance(monitor.get("entry_metrics"), dict) else {}
    human_chart_detail_observed = (
        entry_metrics.get("human_chart_detail_observed")
        if isinstance(entry_metrics.get("human_chart_detail_observed"), dict)
        else {}
    )
    human_chart_detail_context = (
        monitor.get("human_chart_detail_context")
        if isinstance(monitor.get("human_chart_detail_context"), dict)
        else {}
    )
    if not human_chart_detail_observed and isinstance(human_chart_detail_context.get("observed"), dict):
        human_chart_detail_observed = dict(human_chart_detail_context.get("observed") or {})
    entry_thresholds = (
        monitor.get("entry_thresholds")
        if isinstance(monitor.get("entry_thresholds"), dict)
        else {}
    )
    if not entry_thresholds and isinstance(effective_policy, dict):
        entry_thresholds = dict(effective_policy or {})
    if not entry_thresholds and isinstance(monitor.get("applied_policy"), dict):
        entry_thresholds = dict(monitor.get("applied_policy") or {})
    if not entry_thresholds and isinstance(threshold_snapshot.get("entry_thresholds"), dict):
        entry_thresholds = dict(threshold_snapshot.get("entry_thresholds") or {})
    if not entry_thresholds and isinstance(threshold_snapshot.get("applied_policy"), dict):
        entry_thresholds = dict(threshold_snapshot.get("applied_policy") or {})
    entry_guard_blocked = bool(monitor.get("entry_guard_blocked"))
    entry_guard_reason = str(monitor.get("entry_guard_reason") or "").strip()
    entry_evaluated = bool(monitor.get("entry_evaluated"))
    entry_triggered = bool(monitor.get("entry_triggered"))
    exit_reason = str(monitor.get("exit_reason") or "").strip()
    monitor_reason = str(monitor.get("monitor_reason") or monitor.get("evaluation_summary") or "").strip()
    price_source = str(monitor.get("price_source") or "").strip()
    price_source_policy = str(monitor.get("price_source_policy") or "").strip()
    feature_source = str(monitor.get("feature_source") or "").strip()
    current_price = monitor.get("current_price")
    if current_price in (None, ""):
        current_price = monitor.get("price")
    average_price = monitor.get("average_price")
    if average_price in (None, ""):
        average_price = monitor.get("avg_price")
    peak_price = monitor.get("peak_price")
    peak_drawdown = monitor.get("peak_drawdown")
    current_drawdown = monitor.get("current_drawdown")
    vwap_distance = monitor.get("vwap_distance")
    hold_limit_sec = monitor.get("hold_limit_sec")
    if hold_limit_sec in (None, ""):
        hold_limit_sec = (
            thresholds.get("time_stop_sec")
            if safe_int(thresholds.get("time_stop_sec"), 0) > 0
            else thresholds.get("max_hold_sec")
        )
    time_limit_reached = bool(monitor.get("time_limit_reached"))
    time_limit_reason = str(monitor.get("time_limit_reason") or "").strip()
    time_limit_reassessment_required = bool(monitor.get("time_limit_reassessment_required"))
    time_limit_reassessment_blocked = bool(monitor.get("time_limit_reassessment_blocked"))
    time_limit_reassessment_blocked_reason = str(
        monitor.get("time_limit_reassessment_blocked_reason") or ""
    ).strip()
    if current_drawdown in (None, "") and current_price not in (None, "") and peak_price not in (None, ""):
        current_drawdown = (safe_float(current_price, 0.0) / max(safe_float(peak_price, 1.0), 1e-9)) - 1.0
    if current_drawdown in (None, "") and peak_drawdown not in (None, ""):
        current_drawdown = peak_drawdown

    watch_axes: List[str] = [str(x or "") for x in list(monitor.get("watch_axes") or trigger_details.get("watch_axes") or []) if str(x or "").strip()]
    if "Hard stop" not in watch_axes and (thresholds.get("hard_stop_pct") not in (None, "") or thresholds.get("stop_loss_pct") not in (None, "")):
        watch_axes.append("Hard stop")
    if "Take profit" not in watch_axes and thresholds.get("take_profit_pct") not in (None, ""):
        watch_axes.append("Take profit")
    if "Partial take profit" not in watch_axes and safe_float(thresholds.get("partial_take_profit_pct"), 0.0) > 0.0:
        watch_axes.append("Partial take profit")
    if "Profit ladder" not in watch_axes and isinstance(thresholds.get("profit_ladder_levels_pct"), list) and thresholds.get("profit_ladder_levels_pct"):
        watch_axes.append("Profit ladder")
    if "Risk/reward take profit" not in watch_axes and safe_float(thresholds.get("risk_reward_take_profit_r"), 0.0) > 0.0:
        watch_axes.append("Risk/reward take profit")
    elif "Risk/reward take profit" not in watch_axes and isinstance(thresholds.get("risk_reward_take_profit_rungs"), list) and thresholds.get("risk_reward_take_profit_rungs"):
        watch_axes.append("Risk/reward take profit")
    if "VWAP extension take profit" not in watch_axes and safe_float(thresholds.get("vwap_extension_take_profit_pct"), 0.0) > 0.0:
        watch_axes.append("VWAP extension take profit")
    if "Resistance take profit" not in watch_axes and safe_float(thresholds.get("resistance_take_profit_near_pct"), 0.0) > 0.0:
        watch_axes.append("Resistance take profit")
    if "Volume exhaustion take profit" not in watch_axes and safe_float(thresholds.get("volume_exhaustion_take_profit_min_pct"), 0.0) > 0.0:
        watch_axes.append("Volume exhaustion take profit")
    if "Opening gap profit take" not in watch_axes and safe_float(thresholds.get("opening_gap_profit_take_min_pct"), 0.0) > 0.0:
        watch_axes.append("Opening gap profit take")
    if "Time-decay profit exit" not in watch_axes and safe_float(thresholds.get("profit_time_stop_sec"), 0.0) > 0.0:
        watch_axes.append("Time-decay profit exit")
    if "Trailing stop" not in watch_axes and thresholds.get("trailing_stop_pct") not in (None, ""):
        watch_axes.append("Trailing stop")
    if "Peak drawdown" not in watch_axes and thresholds.get("peak_drawdown_exit_pct") not in (None, ""):
        watch_axes.append("Peak drawdown")
    if "VWAP breakdown" not in watch_axes and thresholds.get("vwap_breakdown_pct") not in (None, ""):
        watch_axes.append("VWAP breakdown")
    if "Intraday low break" not in watch_axes and thresholds.get("intraday_low_break_pct") not in (None, ""):
        watch_axes.append("Intraday low break")
    if "Trend breakdown" not in watch_axes and thresholds.get("trend_strength_floor") not in (None, ""):
        watch_axes.append("Trend breakdown")
    if "Volatility expansion" not in watch_axes and thresholds.get("vol_expansion_ratio") not in (None, ""):
        watch_axes.append("Volatility expansion")

    trigger_type = str(monitor.get("trigger_type") or "").strip()
    if not trigger_type:
        trigger_type = exit_reason if action == "SELL" else entry_reason or monitor_reason
    if not trigger_type and decision_reason_chain:
        trigger_type = decision_reason_chain[-1]
    active_exit_axis = str(monitor.get("active_exit_axis") or trigger_details.get("active_exit_axis") or "").strip()
    if str(monitor_reason or "").strip().lower() in {"hold", "hold_position", "eod_carry_approved"} and not bool(monitor.get("exit_triggered")):
        active_exit_axis = "Hold"
    elif not active_exit_axis:
        active_exit_axis = format_exit_label(trigger_type)
    confirm_required = safe_int(
        thresholds_guards_used.get("exit_confirm_ticks"),
        safe_int(thresholds_guards_used.get("exit_confirm_required"), safe_int(monitor.get("exit_confirm_required"), 0)),
    )
    confirm_count = safe_int(
        thresholds_guards_used.get("exit_confirm_count"),
        safe_int(monitor.get("exit_confirm_count"), 0),
    )
    guard_blocked = bool(trigger_details.get("sell_guard_blocked") or monitor.get("guard_blocked") or monitor.get("sell_guard_blocked"))
    guard_reason = str(trigger_details.get("sell_guard_reason") or monitor.get("guard_reason") or monitor.get("sell_guard_reason") or "").strip()
    exit_pending_confirmation = (
        guard_reason.startswith("exit_confirmation_pending:")
        or exit_reason.startswith("exit_confirmation_pending:")
        or monitor_reason == "exit_signal_pending_confirmation"
    )
    hold_without_confirmed_exit = bool(
        action == "SELL"
        and not bool(monitor.get("exit_triggered"))
        and str(trigger_type or monitor_reason or "").strip().lower() in {"hold", "hold_position"}
    )
    monitor_execution_mismatch = bool(
        action == "SELL"
        and not bool(monitor.get("exit_triggered"))
        and (exit_pending_confirmation or hold_without_confirmed_exit)
    )
    eod_carry_evaluated = bool(monitor.get("eod_carry_evaluated"))
    eod_carry_approved = bool(monitor.get("eod_carry_approved"))
    eod_carry_action = str(monitor.get("eod_carry_action") or "").strip()
    eod_carry_reason = str(monitor.get("eod_carry_reason") or "").strip()
    eod_carry_positive_signals = _list_text(monitor.get("eod_carry_positive_signals"), limit=6, max_len=120)
    eod_carry_blockers = _list_text(monitor.get("eod_carry_blockers"), limit=6, max_len=120)
    eod_carry_anomaly = bool(monitor.get("eod_carry_anomaly"))
    eod_carry_anomaly_reason = str(monitor.get("eod_carry_anomaly_reason") or "").strip()
    minutes_to_close = monitor.get("minutes_to_close")
    entry_threshold_gaps: List[str] = []
    if entry_metrics.get("volume_ratio") not in (None, "") and entry_thresholds.get("volume_ratio_min") not in (None, ""):
        volume_ratio = safe_float(entry_metrics.get("volume_ratio"), 0.0)
        volume_ratio_min = safe_float(entry_thresholds.get("volume_ratio_min"), 0.0)
        if volume_ratio < volume_ratio_min:
            entry_threshold_gaps.append(f"volume ratio {volume_ratio:.2f} below min {volume_ratio_min:.2f}")
    if entry_metrics.get("extended_from_vwap_pct") not in (None, "") and entry_thresholds.get("max_extended_from_vwap_pct") not in (None, ""):
        extended = safe_float(entry_metrics.get("extended_from_vwap_pct"), 0.0)
        extended_max = safe_float(entry_thresholds.get("max_extended_from_vwap_pct"), 0.0)
        if extended > extended_max:
            entry_threshold_gaps.append(
                f"VWAP extension {format_ratio_pct(extended)}% above max {format_ratio_pct(extended_max)}%"
            )
    if entry_metrics.get("pullback_depth_pct") not in (None, "") and entry_thresholds.get("pullback_min_pct") not in (None, ""):
        pullback_depth = safe_float(entry_metrics.get("pullback_depth_pct"), 0.0)
        pullback_min = safe_float(entry_thresholds.get("pullback_min_pct"), 0.0)
        if pullback_depth < pullback_min:
            entry_threshold_gaps.append(
                f"pullback depth {format_ratio_pct(pullback_depth)}% below min {format_ratio_pct(pullback_min)}%"
            )
    monitor_stop_policy_trace = _build_monitor_stop_policy_trace(monitor, thresholds)
    monitor_blocker_trace = _build_monitor_blocker_trace(
        {
            "entry_check_summary": entry_check_summary,
            "entry_blockers": entry_blockers,
            "entry_metrics": entry_metrics,
            "entry_thresholds": entry_thresholds,
            "timing_assessment": timing_assessment,
            "policy_ref": policy_ref,
            "entry_condition_path": entry_condition_path,
            "entry_condition_paths_passed": entry_condition_paths_passed,
            "condition_scores": entry_condition_scores,
            "grouped_logic_trace": entry_grouped_logic_trace,
        }
    )
    if eod_carry_approved and action not in ("BUY", "SELL"):
        summary = (
            f"Monitor kept the position into the close because overnight carry was approved "
            f"{safe_float(minutes_to_close, 0.0):.1f} minutes before the close."
        )
    elif action == "BUY":
        summary = f"BUY was triggered because {entry_reason or monitor_reason or 'the intraday entry condition passed'}."
        if entry_pattern:
            summary += f" Pattern: {entry_pattern}."
        if entry_condition_path:
            summary += f" Path: {entry_condition_path.replace('_', ' ')}."
    elif action == "SELL":
        if monitor_execution_mismatch:
            pending_label = (
                guard_reason
                or exit_reason
                or monitor_reason
                or (
                    "monitor posture was hold without a confirmed exit trigger"
                    if hold_without_confirmed_exit
                    else "exit confirmation was pending"
                )
            )
            summary = (
                "Executor recorded SELL, but the monitor had not confirmed the exit yet "
                f"({pending_label}). This is a monitor/executor mismatch, not a confirmed exit trigger."
            )
        elif eod_carry_evaluated and not eod_carry_approved and str(trigger_type or "").strip().lower() in ("eod_flat", "carry_overnight_approved"):
            summary = (
                f"SELL was triggered to flatten before the close because overnight carry was not approved "
                f"({eod_carry_reason or 'carry conditions were not met'})."
            )
        else:
            summary = f"SELL was triggered because {trigger_type or monitor_reason or 'the exit condition passed'}."
    elif eod_carry_anomaly:
        summary = (
            f"Monitor kept the position without a valid end-of-day carry decision because "
            f"{eod_carry_anomaly_reason or 'the carry evaluation context was incomplete'}."
        )
    elif entry_evaluated and not entry_triggered:
        summary = f"Monitor stayed on WAIT because {entry_check_summary or entry_reason or monitor_reason or 'the intraday entry signal was not confirmed'}."
        if entry_threshold_gaps:
            summary += " Threshold gaps: " + "; ".join(entry_threshold_gaps[:3]) + "."
    else:
        summary = f"Monitor posture was {action or 'WAIT'} with trigger {trigger_type or 'not_captured'}."
    bullets = [
        f"Posture: {action or 'WAIT'}",
        (
            f"Trigger type: {trigger_type or 'not_captured'} (pending, not confirmed)"
            if monitor_execution_mismatch
            else f"Trigger type: {trigger_type or 'not_captured'}"
        ),
        f"Monitor reason: {monitor_reason or trigger_type or 'not_captured'}",
        f"Position age: {safe_int(monitor.get('position_age_seconds'), 0)} seconds",
        f"Hold time limit: {safe_int(hold_limit_sec, 0)} seconds" if safe_int(hold_limit_sec, 0) > 0 else "Hold time limit: not configured",
        f"Stop loss: {format_ratio_pct(thresholds.get('stop_loss_pct'))}%",
        f"Effective stop: {format_ratio_pct(thresholds.get('effective_stop_loss_pct'))}%",
        f"Effective stop reason: {str(thresholds.get('effective_stop_reason') or 'not_captured')}",
        f"Take profit: {format_ratio_pct(thresholds.get('take_profit_pct'))}%",
        f"Active exit axis: {active_exit_axis or 'not_captured'}",
        f"Exit confirmation: {confirm_count}/{confirm_required}" if confirm_required > 0 else "Exit confirmation: not required",
        f"Min hold blocked: {'yes' if monitor.get('min_hold_blocked') else 'no'}",
        f"Sell cooldown blocked: {'yes' if monitor.get('sell_cooldown_blocked') else 'no'}",
        f"Exit triggered: {'yes' if monitor.get('exit_triggered') else 'no'}",
    ]
    if time_limit_reassessment_required:
        bullets.append(
            "Time-limit reassessment: "
            f"{'blocked by profit floor' if time_limit_reassessment_blocked else 'allowed'} "
            f"({time_limit_reassessment_blocked_reason or time_limit_reason or 'time limit reached'})"
        )
    if monitor_stop_policy_trace.get("hard_stop_pct") not in (None, ""):
        bullets.append(
            f"Hard fail-safe stop: {format_ratio_pct(monitor_stop_policy_trace.get('hard_stop_pct'))}%"
        )
    if monitor_stop_policy_trace.get("adaptive_stop_loss_pct") not in (None, ""):
        bullets.append(
            f"Active adaptive stop: {format_ratio_pct(monitor_stop_policy_trace.get('adaptive_stop_loss_pct'))}%"
        )
    if monitor_stop_policy_trace.get("strategist_baseline_stop_loss_pct") not in (None, ""):
        bullets.append(
            f"Strategist baseline adaptive stop: {format_ratio_pct(monitor_stop_policy_trace.get('strategist_baseline_stop_loss_pct'))}%"
        )
    if monitor_stop_policy_trace.get("effective_stop_loss_pct") not in (None, ""):
        bullets.append(
            f"Effective stop in this run: {format_ratio_pct(monitor_stop_policy_trace.get('effective_stop_loss_pct'))}%"
        )
    if monitor_stop_policy_trace.get("trailing_stop_pct") not in (None, ""):
        bullets.append(
            f"Trailing stop: {format_ratio_pct(monitor_stop_policy_trace.get('trailing_stop_pct'))}%"
        )
    if monitor_stop_policy_trace.get("strategist_baseline_trailing_stop_pct") not in (None, ""):
        bullets.append(
            f"Strategist baseline trailing stop: {format_ratio_pct(monitor_stop_policy_trace.get('strategist_baseline_trailing_stop_pct'))}%"
        )
    if monitor_stop_policy_trace.get("take_profit_pct") not in (None, ""):
        bullets.append(
            f"Take profit target: {format_ratio_pct(monitor_stop_policy_trace.get('take_profit_pct'))}%"
        )
    if bool(monitor_stop_policy_trace.get("cost_aware_profit_floor_enabled")) and safe_float(
        monitor_stop_policy_trace.get("cost_aware_profit_floor_pct"), 0.0
    ) > 0.0:
        bullets.append(
            "Cost-aware profit floor: "
            f"{format_ratio_pct(monitor_stop_policy_trace.get('cost_aware_profit_floor_pct'))}% "
            f"(round-trip cost {format_ratio_pct(monitor_stop_policy_trace.get('round_trip_cost_floor_pct'))}% "
            f"+ buffer {format_ratio_pct(monitor_stop_policy_trace.get('min_net_profit_buffer_pct'))}%)"
        )
    if safe_float(monitor_stop_policy_trace.get("partial_take_profit_pct"), 0.0) > 0.0:
        bullets.append(
            f"Partial take profit: {format_ratio_pct(monitor_stop_policy_trace.get('partial_take_profit_pct'))}%"
        )
    if isinstance(monitor_stop_policy_trace.get("profit_ladder_levels_pct"), list) and monitor_stop_policy_trace.get("profit_ladder_levels_pct"):
        bullets.append(
            "Profit ladder levels: "
            + ", ".join(f"{format_ratio_pct(level)}%" for level in list(monitor_stop_policy_trace.get("profit_ladder_levels_pct") or [])[:4])
        )
    if safe_float(monitor_stop_policy_trace.get("risk_reward_take_profit_r"), 0.0) > 0.0:
        bullets.append(f"Risk/reward take profit R: {monitor_stop_policy_trace.get('risk_reward_take_profit_r')}")
    elif isinstance(monitor_stop_policy_trace.get("risk_reward_take_profit_rungs"), list) and monitor_stop_policy_trace.get("risk_reward_take_profit_rungs"):
        bullets.append(
            "Risk/reward take profit rungs: "
            + ", ".join(str(x) for x in list(monitor_stop_policy_trace.get("risk_reward_take_profit_rungs") or [])[:4])
        )
    if safe_float(monitor_stop_policy_trace.get("vwap_extension_take_profit_pct"), 0.0) > 0.0:
        bullets.append(
            "VWAP extension take profit: "
            f"{format_ratio_pct(monitor_stop_policy_trace.get('vwap_extension_take_profit_pct'))}%"
        )
    if safe_float(monitor_stop_policy_trace.get("resistance_take_profit_near_pct"), 0.0) > 0.0:
        bullets.append(
            "Resistance take profit near: "
            f"{format_ratio_pct(monitor_stop_policy_trace.get('resistance_take_profit_near_pct'))}%"
        )
    if safe_float(monitor_stop_policy_trace.get("volume_exhaustion_take_profit_min_pct"), 0.0) > 0.0:
        bullets.append(
            "Volume exhaustion take profit min: "
            f"{format_ratio_pct(monitor_stop_policy_trace.get('volume_exhaustion_take_profit_min_pct'))}%"
        )
    if safe_float(monitor_stop_policy_trace.get("opening_gap_profit_take_min_pct"), 0.0) > 0.0:
        bullets.append(
            "Opening gap profit take min: "
            f"{format_ratio_pct(monitor_stop_policy_trace.get('opening_gap_profit_take_min_pct'))}%"
        )
    if safe_float(monitor_stop_policy_trace.get("profit_time_stop_sec"), 0.0) > 0.0:
        bullets.append(f"Profit time stop: {safe_int(monitor_stop_policy_trace.get('profit_time_stop_sec'), 0)} seconds")
    if monitor_stop_policy_trace.get("strategist_baseline_take_profit_pct") not in (None, ""):
        bullets.append(
            f"Strategist baseline take profit: {format_ratio_pct(monitor_stop_policy_trace.get('strategist_baseline_take_profit_pct'))}%"
        )
    if entry_evaluated:
        bullets.append(f"Entry triggered: {'yes' if entry_triggered else 'no'}")
        bullets.append(f"Entry pattern: {entry_pattern or 'not_captured'}")
        if entry_signal_chain:
            bullets.append("Entry signal chain: " + " -> ".join(entry_signal_chain[:6]))
        if entry_condition_path:
            bullets.append(f"Grouped entry path: {entry_condition_path}")
        if entry_condition_paths_passed:
            bullets.append("Grouped paths passed: " + ", ".join(entry_condition_paths_passed[:3]))
        if entry_condition_scores:
            bullets.append(
                "Condition scores: "
                + "; ".join(
                    [
                        f"{key}={safe_float(value, 0.0):.2f}"
                        for key, value in list(entry_condition_scores.items())[:6]
                        if value not in (None, "")
                    ]
                )
            )
        if entry_guard_blocked or entry_guard_reason:
            bullets.append(
                f"Entry guard blocked: {'yes' if entry_guard_blocked else 'no'} "
                f"({entry_guard_reason or 'no guard reason captured'})"
            )
        if entry_metrics.get("timeframe_minutes") not in (None, ""):
            bullets.append(f"Entry timeframe: {safe_int(entry_metrics.get('timeframe_minutes'), 1)}m")
        if entry_metrics.get("recent_high") not in (None, ""):
            bullets.append(f"Recent high: {safe_float(entry_metrics.get('recent_high'), 0.0):.2f}")
        if entry_metrics.get("breakout_level") not in (None, ""):
            bullets.append(f"Breakout level: {safe_float(entry_metrics.get('breakout_level'), 0.0):.2f}")
        if entry_metrics.get("vwap") not in (None, ""):
            bullets.append(f"Entry VWAP: {safe_float(entry_metrics.get('vwap'), 0.0):.2f}")
        if entry_metrics.get("volume_ratio") not in (None, ""):
            bullets.append(
                f"Volume ratio: {safe_float(entry_metrics.get('volume_ratio'), 0.0):.2f} "
                f"(min {safe_float(entry_thresholds.get('volume_ratio_min'), 0.0):.2f})"
            )
        if entry_metrics.get("extended_from_vwap_pct") not in (None, ""):
            bullets.append(
                f"Extended from VWAP: {format_ratio_pct(entry_metrics.get('extended_from_vwap_pct'))}% "
                f"(max {format_ratio_pct(entry_thresholds.get('max_extended_from_vwap_pct'))}%)"
            )
        if entry_metrics.get("pullback_depth_pct") not in (None, ""):
            pullback_bullet = f"Pullback depth: {format_ratio_pct(entry_metrics.get('pullback_depth_pct'))}%"
            if entry_thresholds.get("pullback_min_pct") not in (None, ""):
                pullback_bullet += f" (min {format_ratio_pct(entry_thresholds.get('pullback_min_pct'))}%)"
            if entry_thresholds.get("pullback_max_pct") not in (None, ""):
                pullback_bullet += f" (max {format_ratio_pct(entry_thresholds.get('pullback_max_pct'))}%)"
            bullets.append(pullback_bullet)
        if any(
            entry_metrics.get(key) not in (None, "")
            for key in (
                "human_candle_quality_score",
                "human_vwap_reference_quality_score",
                "human_reward_room_score",
                "human_multi_window_structure_score",
            )
        ):
            bullets.append(
                "Human chart setup quality: "
                f"candle {safe_float(entry_metrics.get('human_candle_quality_score'), 0.0):.2f}, "
                f"VWAP ref {safe_float(entry_metrics.get('human_vwap_reference_quality_score'), 0.0):.2f}, "
                f"reward room {safe_float(entry_metrics.get('human_reward_room_score'), 0.0):.2f}, "
                f"multi-window {safe_float(entry_metrics.get('human_multi_window_structure_score'), 0.0):.2f}"
            )
        if human_chart_detail_observed:
            candle_bits: List[str] = []
            if human_chart_detail_observed.get("close_location") not in (None, ""):
                candle_bits.append(f"close location {safe_float(human_chart_detail_observed.get('close_location'), 0.0):.2f}")
            if human_chart_detail_observed.get("upper_wick_ratio") not in (None, ""):
                candle_bits.append(f"upper wick {safe_float(human_chart_detail_observed.get('upper_wick_ratio'), 0.0):.2f}")
            if human_chart_detail_observed.get("lower_wick_ratio") not in (None, ""):
                candle_bits.append(f"lower wick {safe_float(human_chart_detail_observed.get('lower_wick_ratio'), 0.0):.2f}")
            if human_chart_detail_observed.get("body_ratio") not in (None, ""):
                candle_bits.append(f"body {safe_float(human_chart_detail_observed.get('body_ratio'), 0.0):.2f}")
            if candle_bits:
                bullets.append("Entry candle shape: " + ", ".join(candle_bits))
            vwap_bits: List[str] = []
            if human_chart_detail_observed.get("vwap_source") not in (None, ""):
                vwap_bits.append(f"source {human_chart_detail_observed.get('vwap_source')}")
            if human_chart_detail_observed.get("vwap_bar_count") not in (None, ""):
                vwap_bits.append(f"bars {safe_int(human_chart_detail_observed.get('vwap_bar_count'), 0)}")
            if human_chart_detail_observed.get("explicit_vwap_count") not in (None, ""):
                vwap_bits.append(f"explicit bars {safe_int(human_chart_detail_observed.get('explicit_vwap_count'), 0)}")
            if human_chart_detail_observed.get("explicit_vwap_ratio") not in (None, ""):
                vwap_bits.append(f"explicit ratio {safe_float(human_chart_detail_observed.get('explicit_vwap_ratio'), 0.0):.2f}")
            if vwap_bits:
                bullets.append("VWAP reference quality: " + ", ".join(vwap_bits))
            reward_bits: List[str] = []
            if human_chart_detail_observed.get("prior_resistance") not in (None, ""):
                reward_bits.append(f"resistance {safe_float(human_chart_detail_observed.get('prior_resistance'), 0.0):.2f}")
            if human_chart_detail_observed.get("reward_room_pct") not in (None, ""):
                reward_bits.append(f"room {format_ratio_pct(human_chart_detail_observed.get('reward_room_pct'))}%")
            if human_chart_detail_observed.get("breakout_extension_pct") not in (None, ""):
                reward_bits.append(
                    f"breakout extension {format_ratio_pct(human_chart_detail_observed.get('breakout_extension_pct'))}%"
                )
            if reward_bits:
                bullets.append("Reward room context: " + ", ".join(reward_bits))
        if entry_check_summary:
            bullets.append(f"Entry check summary: {entry_check_summary}")
        if entry_blockers:
            bullets.append("Entry blockers: " + "; ".join(entry_blockers[:6]))
        if entry_threshold_gaps:
            bullets.append("Threshold gaps: " + "; ".join(entry_threshold_gaps[:3]))
        if policy_adjustment_summary:
            bullets.append(f"Policy adjustment summary: {policy_adjustment_summary}")
        if effective_policy_deltas:
            bullets.append(
                "Effective policy deltas: "
                + "; ".join(
                    [
                        f"{str((row or {}).get('field') or '')}: {(row or {}).get('from')} -> {(row or {}).get('to')}"
                        for row in effective_policy_deltas[:4]
                        if str((row or {}).get("field") or "").strip()
                    ]
                )
            )
        if policy_ref:
            policy_bits: List[str] = []
            for key in ("monitor_mission", "flow_instruction", "risk_mode", "command_intent"):
                value = str(policy_ref.get(key) or "").strip()
                if value:
                    policy_bits.append(f"{key}={value}")
            if policy_bits:
                bullets.append("Policy reference: " + ", ".join(policy_bits[:4]))
    if eod_carry_evaluated:
        bullets.append(
            f"EOD carry decision: {'approved' if eod_carry_approved else 'flatten before close'} "
            f"({eod_carry_reason or 'not_captured'})"
        )
        if minutes_to_close not in (None, ""):
            bullets.append(f"Minutes to close at decision: {safe_float(minutes_to_close, 0.0):.1f}")
        if eod_carry_positive_signals:
            bullets.append("Carry positives: " + "; ".join(eod_carry_positive_signals[:4]))
        if eod_carry_blockers:
            bullets.append("Carry blockers: " + "; ".join(eod_carry_blockers[:4]))
    if eod_carry_anomaly:
        bullets.append(
            f"EOD carry anomaly: yes ({eod_carry_anomaly_reason or 'carry evaluation context missing'})"
        )
    if watch_axes:
        bullets.append("Watch axes: " + ", ".join(watch_axes[:8]))
    if decision_reason_chain:
        bullets.append("Decision chain: " + " -> ".join(decision_reason_chain[:5]))
    entry_quant_decision = monitor.get("entry_quant_decision") if isinstance(monitor.get("entry_quant_decision"), dict) else {}
    exit_quant_decision = monitor.get("exit_quant_decision") if isinstance(monitor.get("exit_quant_decision"), dict) else {}
    quant_factor_snapshot = monitor.get("quant_factor_snapshot") if isinstance(monitor.get("quant_factor_snapshot"), dict) else {}
    if entry_quant_decision:
        blockers = [str(x or "") for x in list(entry_quant_decision.get("blockers") or []) if str(x or "").strip()]
        warnings = [str(x or "") for x in list(entry_quant_decision.get("warnings") or []) if str(x or "").strip()]
        bullets.append(
            "Entry quant decision: "
            f"{entry_quant_decision.get('decision') or 'not_captured'} "
            f"(blockers: {', '.join(blockers[:4]) or 'none'}; warnings: {', '.join(warnings[:4]) or 'none'})"
        )
    if exit_quant_decision:
        blockers = [str(x or "") for x in list(exit_quant_decision.get("blockers") or []) if str(x or "").strip()]
        warnings = [str(x or "") for x in list(exit_quant_decision.get("warnings") or []) if str(x or "").strip()]
        bullets.append(
            "Exit quant decision: "
            f"{exit_quant_decision.get('decision') or 'not_captured'} "
            f"(blockers: {', '.join(blockers[:4]) or 'none'}; warnings: {', '.join(warnings[:4]) or 'none'})"
        )
    if guard_blocked or guard_reason:
        bullets.append(f"Guard blocked: {'yes' if guard_blocked else 'no'} ({guard_reason or 'no guard reason captured'})")
    if monitor_execution_mismatch:
        mismatch_label = (
            "SELL recorded while monitor posture was hold"
            if hold_without_confirmed_exit
            else "SELL recorded while monitor exit confirmation was pending"
        )
        bullets.append(f"Monitor/executor mismatch: yes ({mismatch_label})")
    if current_price not in (None, ""):
        bullets.append(f"Current price: {safe_float(current_price, 0.0):.2f}")
    if average_price not in (None, ""):
        bullets.append(f"Average price: {safe_float(average_price, 0.0):.2f}")
    if peak_price not in (None, ""):
        bullets.append(f"Peak price: {safe_float(peak_price, 0.0):.2f}")
    if current_drawdown not in (None, ""):
        bullets.append(f"Current drawdown: {format_ratio_pct(current_drawdown)}%")
    if peak_drawdown not in (None, ""):
        bullets.append(f"Peak drawdown: {format_ratio_pct(peak_drawdown)}%")
    if vwap_distance not in (None, ""):
        bullets.append(f"VWAP distance: {format_ratio_pct(vwap_distance)}%")
    if price_source:
        bullets.append(f"Price source: {price_source}")
    if feature_source:
        bullets.append(f"Feature source: {feature_source}")
    if price_source_policy:
        bullets.append(f"Price source policy: {price_source_policy}")
    return {
        "posture": action or "WAIT",
        "trigger_type": trigger_type,
        "summary": summary,
        "bullets": bullets,
        "position_age_seconds": safe_int(monitor.get("position_age_seconds"), 0),
        "hold_limit_sec": safe_int(hold_limit_sec, 0),
        "time_limit_reached": time_limit_reached,
        "time_limit_reason": time_limit_reason,
        "time_limit_reassessment_required": time_limit_reassessment_required,
        "time_limit_reassessment_blocked": time_limit_reassessment_blocked,
        "time_limit_reassessment_blocked_reason": time_limit_reassessment_blocked_reason,
        "stop_loss_pct": thresholds.get("stop_loss_pct"),
        "hard_stop_pct": monitor_stop_policy_trace.get("hard_stop_pct"),
        "adaptive_stop_loss_pct": monitor_stop_policy_trace.get("adaptive_stop_loss_pct"),
        "effective_stop_loss_pct": monitor_stop_policy_trace.get("effective_stop_loss_pct"),
        "effective_stop_reason": str(thresholds.get("effective_stop_reason") or "").strip(),
        "take_profit_pct": monitor_stop_policy_trace.get("take_profit_pct"),
        "trailing_stop_pct": monitor_stop_policy_trace.get("trailing_stop_pct"),
        "exit_triggered": bool(monitor.get("exit_triggered")),
        "entry_evaluated": entry_evaluated,
        "entry_triggered": entry_triggered,
        "entry_reason": entry_reason,
        "entry_pattern": entry_pattern,
        "entry_signal_chain": entry_signal_chain[:8],
        "entry_condition_path": entry_condition_path,
        "entry_condition_paths_passed": entry_condition_paths_passed[:4],
        "entry_condition_scores": dict(entry_condition_scores),
        "entry_grouped_logic_trace": dict(entry_grouped_logic_trace),
        "entry_metrics": dict(entry_metrics),
        "human_chart_detail_observed": dict(human_chart_detail_observed),
        "entry_thresholds": dict(entry_thresholds),
        "entry_check_summary": entry_check_summary,
        "entry_blockers": entry_blockers[:8],
        "threshold_shortfalls": entry_threshold_gaps[:4],
        "policy_ref": dict(policy_ref),
        "received_policy": dict(received_policy),
        "effective_policy": dict(effective_policy),
        "policy_adjustment_summary": policy_adjustment_summary,
        "effective_policy_deltas": effective_policy_deltas,
        "monitor_stop_policy_trace": monitor_stop_policy_trace,
        "monitor_blocker_trace": monitor_blocker_trace,
        "timing_assessment": dict(timing_assessment),
        "thresholds_guards_used": dict(thresholds_guards_used),
        "quant_factor_snapshot": dict(quant_factor_snapshot),
        "entry_quant_decision": dict(entry_quant_decision),
        "exit_quant_decision": dict(exit_quant_decision),
        "entry_guard_blocked": entry_guard_blocked,
        "entry_guard_reason": entry_guard_reason,
        "current_price": current_price,
        "average_price": average_price,
        "peak_price": peak_price,
        "current_drawdown": current_drawdown,
        "peak_drawdown": peak_drawdown,
        "vwap_distance": vwap_distance,
        "active_exit_axis": active_exit_axis,
        "watch_axes": watch_axes[:8],
        "confirm_required": confirm_required,
        "confirm_count": confirm_count,
        "guard_blocked": guard_blocked,
        "guard_reason": guard_reason,
        "pending_confirmation": exit_pending_confirmation,
        "monitor_execution_mismatch": monitor_execution_mismatch,
        "eod_carry_evaluated": eod_carry_evaluated,
        "eod_carry_approved": eod_carry_approved,
        "eod_carry_action": eod_carry_action,
        "eod_carry_reason": eod_carry_reason,
        "eod_carry_positive_signals": eod_carry_positive_signals,
        "eod_carry_blockers": eod_carry_blockers,
        "eod_carry_anomaly": eod_carry_anomaly,
        "eod_carry_anomaly_reason": eod_carry_anomaly_reason,
        "decision_reason_chain": decision_reason_chain[:6],
        "price_source": price_source,
        "feature_source": feature_source,
        "price_source_policy": price_source_policy,
    }


