"""Operator brief market/news/selected-rank/source and feature evidence sections.

Second Pass (P1.5) intra-function extraction from `apps/operator_ui/data_access_core.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations

from typing import Any, NamedTuple


def brief_market_candidate_hints_defensive_mode(strategist_raw_input, canonical_trade, strategist_summary, strategist, selected_symbol, strategist_trace, selected_candidate, *, facade):
    global_inputs = strategist_raw_input.get("global_sentiment_inputs") if isinstance(strategist_raw_input.get("global_sentiment_inputs"), dict) else {}
    fear_index = global_inputs.get("fear_index") if isinstance(global_inputs.get("fear_index"), dict) else {}
    macro_moves = global_inputs.get("macro_moves") if isinstance(global_inputs.get("macro_moves"), dict) else {}
    global_score = canonical_trade.get("global_sentiment") or global_inputs.get("score")
    vix_level = canonical_trade.get("vix") or fear_index.get("level")
    market_news_titles = [str((x or {}).get("title") or "") for x in list(strategist_raw_input.get("collected_market_news") or []) if isinstance(x, dict)]
    news_targets = list(strategist_summary.get("news_query_targets") or strategist_raw_input.get("news_query_targets") or [])
    news_ranked = (
        strategist.get("artifact", {}).get("news_evidence_ranked")
        if isinstance(strategist.get("artifact"), dict) and isinstance(strategist.get("artifact", {}).get("news_evidence_ranked"), dict)
        else {}
    )
    market_headlines = (
        facade._brief_collect_top_headlines(news_ranked.get("market_news_ranked") or [], limit=3)
        or list(canonical_trade.get("strategist_market_headlines") or canonical_trade.get("market_news_titles") or [])[:3]
        or market_news_titles[:3]
    )
    symbol_headlines = (
        facade._brief_collect_top_headlines(news_ranked.get("candidate_news_ranked") or [], limit=3, symbol=selected_symbol)
        or list(canonical_trade.get("strategist_symbol_headlines") or canonical_trade.get("candidate_news_titles") or [])[:3]
        or [str((x or {}).get("title") or "") for x in list(strategist_raw_input.get("collected_candidate_news") or []) if isinstance(x, dict)][:3]
    )
    candidate_hints = list(
        (
            strategist.get("artifact", {}).get("candidate_symbols_hint")
            if isinstance(strategist.get("artifact"), dict)
            else None
        )
        or strategist_summary.get("candidate_hints")
        or canonical_trade.get("strategist_candidate_hints")
        or []
    )[:8]
    macro_stress_overlay = strategist_trace.get("macro_stress_overlay") if isinstance(strategist_trace.get("macro_stress_overlay"), dict) else {}
    defensive_mode = bool(macro_stress_overlay.get("active")) or str(strategist_summary.get("playbook") or "").lower() == "defensive" or (facade._safe_float(vix_level, 0.0) >= 25.0 if vix_level is not None else False)
    if canonical_trade.get("market_context_summary"):
        news_summary = str(canonical_trade.get("market_context_summary"))
    elif market_news_titles:
        news_summary = "; ".join([title for title in market_news_titles[:2] if title]) or "market news sampled"
    elif news_targets:
        news_summary = "no strong market-moving headline was retained in this run"
    else:
        news_summary = "no meaningful news input was captured"

    detected_themes = facade._clean_brief_list(canonical_trade.get("themes") or strategist_summary.get("themes"), limit=6)
    playbook = facade._clean_brief_text(strategist_summary.get("playbook") or canonical_trade.get("playbook") or "")
    theme_match = facade._clean_brief_text(
        selected_candidate.get("theme_match")
        or selected_candidate.get("sector_theme")
        or selected_candidate.get("theme")
        or ""
    )
    return (candidate_hints, defensive_mode, detected_themes, global_score, macro_moves, market_headlines, news_summary, news_targets, playbook, symbol_headlines, theme_match, vix_level)


def brief_market_anomaly_note_anomaly_status(detected_themes, theme_match, selected_symbol, feature_snapshot, global_score, quote_metrics, feature_coverage, verdict, selected_candidate, *, facade):
    if detected_themes and theme_match:
        priority_alignment = "yes"
        theme_priority = "high-priority theme"
    elif detected_themes and selected_symbol:
        priority_alignment = "partial"
        theme_priority = "fallback theme match"
    elif detected_themes:
        priority_alignment = "unknown"
        theme_priority = "theme detected but symbol linkage unavailable"
    else:
        priority_alignment = "no"
        theme_priority = "no explicit theme detected"

    sector_strength = feature_snapshot.get("engine_sector_relative_strength")
    sentiment_gate_status = "SKIPPED"
    sentiment_gate_note = "sentiment input not available"
    if global_score is not None:
        sentiment_gate_status = "PASS" if facade._safe_float(global_score, 0.0) >= -0.35 else "FAIL"
        sentiment_gate_note = f"global sentiment {facade._format_float(global_score, 2)}"

    liquidity_status = "SKIPPED"
    liquidity_note = "quote volume not available"
    if quote_metrics.get("quote_volume") is not None:
        liquidity_status = "PASS" if facade._safe_float(quote_metrics.get("quote_volume"), 0.0) > 0 else "FAIL"
        liquidity_note = f"quote volume {quote_metrics.get('quote_volume')}"

    turnover_status = "SKIPPED"
    turnover_note = "turnover metric not available"
    if quote_metrics.get("quote_trading_value") is not None:
        turnover_status = "PASS" if facade._safe_float(quote_metrics.get("quote_trading_value"), 0.0) > 0 else "FAIL"
        turnover_note = f"trading value {quote_metrics.get('quote_trading_value')}"

    sector_status = "SKIPPED"
    sector_note = "sector relative strength not available"
    if sector_strength is not None:
        sector_status = "PASS" if facade._safe_float(sector_strength, 0.0) >= 0 else "FAIL"
        sector_note = f"sector relative strength {facade._format_float(sector_strength, 2)}"

    chart_status, chart_note = facade._chart_filter_status_and_note(feature_coverage)

    risk_status = "PASS" if bool(verdict.get("allowed")) else "FAIL"
    risk_note = str(verdict.get("reason") or ("order allowed" if risk_status == "PASS" else "order blocked"))

    change_pct = quote_metrics.get("intraday_change_pct")
    anomaly_status = "SKIPPED"
    anomaly_note = "intraday change metric not available"
    if change_pct is not None:
        anomaly_status = "PASS" if abs(facade._safe_float(change_pct, 0.0)) <= 12.0 else "FAIL"
        anomaly_note = f"intraday change {facade._format_percent(change_pct, 2)}"

    spread_bps = selected_candidate.get("spread_bps")
    spread_status = "SKIPPED"
    spread_note = "spread/slippage metric not available in this run"
    if spread_bps is not None:
        spread_status = "PASS" if facade._safe_float(spread_bps, 9999.0) <= 50.0 else "FAIL"
        spread_note = f"spread {spread_bps} bps"

    ranking_basis: facade.List[str] = []
    return (anomaly_note, anomaly_status, chart_note, chart_status, liquidity_note, liquidity_status, priority_alignment, ranking_basis, risk_note, risk_status, sector_note, sector_status, sentiment_gate_note, sentiment_gate_status, spread_note, spread_status, theme_priority, turnover_note, turnover_status)


class BriefPositionExitAxisEvidence(NamedTuple):
    """Result of `brief_position_exit_axis_evidence` (positional order is the legacy tuple order; unpacking call-sites are unchanged)."""

    active_exit_axis: Any
    avg_price_monitor: Any
    canonical_current_price: Any
    canonical_holding_time: Any
    canonical_posture: Any
    chart_interpretation: Any
    current_drawdown_raw: Any
    current_price: Any
    effective_stop_reason: Any
    effective_stop_text: Any
    holding_time: Any
    missing_feature_names: Any
    peak_drawdown_raw: Any
    peak_price: Any
    positive_factors: Any
    present_feature_names: Any
    scanner_selection_trace: Any
    stop_loss: Any
    stop_loss_text: Any
    take_profit: Any
    take_profit_text: Any
    vwap_distance_raw: Any
    watch_axes: Any
    weak_factors: Any


def brief_position_exit_axis_evidence(trade_story_input, canonical_trade, selected_why, quote_metrics, chart_status, sector_status, feature_coverage, feature_snapshot, sentiment_gate_status, thresholds, monitor_trace, monitor_summary, live_exit_reason, live_monitor_reason, exit_reason, monitor_reason, canonical_monitor_snapshot, shared_facts, *, facade):
    scanner_selection_trace = (
        trade_story_input.get("scanner_selection_trace")
        if isinstance(trade_story_input.get("scanner_selection_trace"), dict)
        else canonical_trade.get("scanner_selection_trace")
        if isinstance(canonical_trade.get("scanner_selection_trace"), dict)
        else {}
    )

    positive_factors: facade.List[str] = []
    if selected_why:
        positive_factors.append(selected_why)
    if facade._safe_float(quote_metrics.get("quote_trading_value"), 0.0) > 0:
        positive_factors.append("strong tradable turnover")
    if chart_status == "PASS":
        positive_factors.append("robust chart feature coverage")
    if sector_status == "PASS":
        positive_factors.append("sector alignment is acceptable")
    if not positive_factors:
        positive_factors.append("selected symbol retained highest available composite rank")

    weak_factors: facade.List[str] = []
    missing_keys = list(feature_coverage.get("missing_keys") or [])
    if missing_keys:
        weak_factors.append(
            "missing features: " + ", ".join(facade._friendly_feature_name(k) for k in missing_keys[:2])
        )
    volatility20 = feature_snapshot.get("engine_volatility20")
    if volatility20 is not None and facade._safe_float(volatility20, 0.0) >= 0.3:
        weak_factors.append("elevated short-term volatility remains")
    if sentiment_gate_status == "FAIL":
        weak_factors.append("negative global sentiment requires tighter monitoring")
    if not weak_factors:
        weak_factors.append("no major weakness persisted in this run snapshot")

    present_feature_names = [facade._friendly_feature_name(k) for k in list(feature_coverage.get("present_keys") or [])[:6]]
    missing_feature_names = [facade._friendly_feature_name(k) for k in missing_keys[:4]]
    if chart_status == "PASS":
        chart_interpretation = "feature coverage is robust enough for scanner ranking confidence"
    elif chart_status == "PARTIAL":
        chart_interpretation = "feature coverage is usable but needs caution on weaker technical inputs"
    else:
        chart_interpretation = "feature coverage is insufficient; treat selection confidence conservatively"

    stop_loss = thresholds.get("stop_loss_pct")
    take_profit = thresholds.get("take_profit_pct")
    effective_stop_loss = thresholds.get("effective_stop_loss_pct")
    effective_stop_reason = str(thresholds.get("effective_stop_reason") or "").strip()
    if stop_loss is None:
        stop_loss = thresholds.get("stop_loss")
    if take_profit is None:
        take_profit = thresholds.get("take_profit")
    stop_loss_text = facade._format_percent(stop_loss, 2) if stop_loss is not None else "-"
    take_profit_text = facade._format_percent(take_profit, 2) if take_profit is not None else "-"
    effective_stop_text = facade._format_percent(effective_stop_loss, 2) if effective_stop_loss not in (None, "") else stop_loss_text
    current_price = monitor_trace.get("price")
    avg_price_monitor = monitor_trace.get("avg_price")
    peak_price = monitor_trace.get("peak_price") or monitor_summary.get("peak_price")
    peak_drawdown_raw = monitor_trace.get("peak_drawdown")
    if peak_drawdown_raw in (None, ""):
        peak_drawdown_raw = monitor_summary.get("peak_drawdown")
    vwap_distance_raw = monitor_trace.get("vwap_distance")
    if vwap_distance_raw in (None, ""):
        vwap_distance_raw = monitor_summary.get("vwap_distance")
    current_drawdown_raw = None
    if facade._safe_float(current_price, 0.0) > 0.0 and facade._safe_float(peak_price, 0.0) > 0.0:
        current_drawdown_raw = (facade._safe_float(current_price, 0.0) / facade._safe_float(peak_price, 1.0)) - 1.0
    elif peak_drawdown_raw not in (None, ""):
        current_drawdown_raw = peak_drawdown_raw
    watch_axes = facade._monitor_watch_axes(thresholds)
    active_exit_axis = facade._friendly_exit_reason(live_exit_reason or effective_stop_reason or live_monitor_reason or exit_reason or monitor_reason or "hold")
    holding_time = facade._format_duration(monitor_summary.get("position_age_seconds") or monitor_trace.get("position_age_seconds"))

    canonical_holding_time = str(
        canonical_monitor_snapshot.get("holding_time")
        or shared_facts.get("holding_duration")
        or ""
    ).strip()
    canonical_posture = str(canonical_monitor_snapshot.get("posture") or "").strip()
    canonical_current_price = str(canonical_monitor_snapshot.get("current_price") or "").strip()
    return BriefPositionExitAxisEvidence(active_exit_axis, avg_price_monitor, canonical_current_price, canonical_holding_time, canonical_posture, chart_interpretation, current_drawdown_raw, current_price, effective_stop_reason, effective_stop_text, holding_time, missing_feature_names, peak_drawdown_raw, peak_price, positive_factors, present_feature_names, scanner_selection_trace, stop_loss, stop_loss_text, take_profit, take_profit_text, vwap_distance_raw, watch_axes, weak_factors)


def build_market_readout(macro_moves, canonical_trade, chart_status, chart_note, liquidity_status, liquidity_note, turnover_status, turnover_note, sector_status, sector_note, sentiment_gate_status, sentiment_gate_note, risk_status, risk_note, anomaly_status, anomaly_note, spread_status, spread_note, *, facade):
    """Compose display-only macro evidence and filter rows; existing guard results are inputs."""
    macro_summary = []
    if macro_moves.get("dxy_pct") is not None:
        macro_summary.append(f"DXY change {facade._format_percent(macro_moves.get('dxy_pct'), 2)}")
    if macro_moves.get("tnx_delta") is not None:
        macro_summary.append(f"US10Y delta {facade._format_float(macro_moves.get('tnx_delta'), 3)}")
    for bullet in list(canonical_trade.get("market_context_bullets") or [])[:4]:
        if bullet not in macro_summary:
            macro_summary.append(bullet)

    filter_rows = [dict(row) for row in list(canonical_trade.get("filter_rows") or []) if isinstance(row, dict)]
    if filter_rows:
        for row in filter_rows:
            name = str(row.get("name") or "").strip().lower()
            if name == "chart completeness filter":
                row["status"] = chart_status
                row["note"] = chart_note
                break
    if filter_rows:
        filters_and_gates = filter_rows[:8]
    else:
        filters_and_gates = [
            {"name": "Liquidity filter", "status": liquidity_status, "note": liquidity_note},
            {"name": "Turnover filter", "status": turnover_status, "note": turnover_note},
            {"name": "Sector strength filter", "status": sector_status, "note": sector_note},
            {"name": "Chart completeness filter", "status": chart_status, "note": chart_note},
            {"name": "Sentiment gate", "status": sentiment_gate_status, "note": sentiment_gate_note},
            {"name": "Risk gate", "status": risk_status, "note": risk_note},
            {"name": "Price anomaly filter", "status": anomaly_status, "note": anomaly_note},
            {"name": "Spread/slippage filter", "status": spread_status, "note": spread_note},
        ]

    return macro_summary, filters_and_gates
