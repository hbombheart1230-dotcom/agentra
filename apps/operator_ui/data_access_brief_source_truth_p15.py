"""Pure candidate, canonical monitor and policy source selection for Operator Brief.

Caller helpers remain resolved through the supplied facade at each use site.
No I/O, LLM coordination or persistence belongs to this Owner.
"""
from __future__ import annotations


def brief_input_candidate_hints_market_headlines(monitor, scanner_trace, selected, canonical_trade, strategist_artifact, raw_input, strategist_summary, trade_story_input, *, facade):
    monitor_summary = monitor.get("summary") if isinstance(monitor.get("summary"), dict) else {}
    monitor_trace = monitor.get("decision_trace") if isinstance(monitor.get("decision_trace"), dict) else {}
    monitor_artifact = monitor.get("artifact") if isinstance(monitor.get("artifact"), dict) else {}
    monitor_policy_ref = monitor_trace.get("policy_ref") if isinstance(monitor_trace.get("policy_ref"), dict) else {}
    monitor_timing_assessment = monitor_trace.get("timing_assessment") if isinstance(monitor_trace.get("timing_assessment"), dict) else {}
    monitor_thresholds_used = monitor_trace.get("thresholds_guards_used") if isinstance(monitor_trace.get("thresholds_guards_used"), dict) else {}
    monitor_entry_metrics = monitor_summary.get("entry_metrics") if isinstance(monitor_summary.get("entry_metrics"), dict) else {}
    monitor_entry_thresholds = monitor_summary.get("entry_thresholds") if isinstance(monitor_summary.get("entry_thresholds"), dict) else {}
    selected_symbol = str(
        scanner_trace.get("selected_symbol")
        or selected.get("symbol")
        or canonical_trade.get("symbol")
        or ""
    ).strip()
    news_ranked = (
        strategist_artifact.get("news_evidence_ranked")
        if isinstance(strategist_artifact.get("news_evidence_ranked"), dict)
        else {}
    )
    market_headlines = (
        facade._brief_collect_top_headlines(news_ranked.get("market_news_ranked") or [], limit=3)
        or [str((x or {}).get("title") or "") for x in list(raw_input.get("collected_market_news") or []) if isinstance(x, dict)][:3]
        or list(canonical_trade.get("strategist_market_headlines") or canonical_trade.get("market_news_titles") or [])[:3]
    )
    symbol_headlines = (
        facade._brief_collect_top_headlines(news_ranked.get("candidate_news_ranked") or [], limit=3, symbol=selected_symbol)
        or [str((x or {}).get("title") or "") for x in list(raw_input.get("collected_candidate_news") or []) if isinstance(x, dict)][:3]
        or list(canonical_trade.get("strategist_symbol_headlines") or canonical_trade.get("candidate_news_titles") or [])[:3]
    )
    candidate_hints = list(
        strategist_artifact.get("candidate_symbols_hint")
        or strategist_summary.get("candidate_hints")
        or canonical_trade.get("strategist_candidate_hints")
        or []
    )[:8]
    scanner_selection_trace = (
        trade_story_input.get("scanner_selection_trace")
        if isinstance(trade_story_input.get("scanner_selection_trace"), dict)
        else canonical_trade.get("scanner_selection_trace")
        if isinstance(canonical_trade.get("scanner_selection_trace"), dict)
        else {}
    )
    return (candidate_hints, market_headlines, monitor_artifact, monitor_entry_metrics, monitor_entry_thresholds, monitor_policy_ref, monitor_summary, monitor_thresholds_used, monitor_timing_assessment, monitor_trace, scanner_selection_trace, selected_symbol, symbol_headlines)


def brief_input_scanner_selection_trace(scanner_artifact, selected_symbol, score_breakdown, scanner_trace, selected, canonical_trade, *, facade):
    if True:
        score_breakdown_by_symbol = (
            scanner_artifact.get("score_breakdown_by_symbol")
            if isinstance(scanner_artifact.get("score_breakdown_by_symbol"), dict)
            else {}
        )
        scanner_selection_trace = {
            "ranked_candidates": list(canonical_trade.get("top_candidates") or [])[:5],
            "selected_symbol": selected_symbol,
            "selected_rank": scanner_trace.get("selected_rank") or selected.get("rank"),
            "selection_reason": canonical_trade.get("selection_basis")
            or canonical_trade.get("selection_summary")
            or scanner_trace.get("selection_reason_with_bias")
            or selected.get("why"),
            "selected_symbol_score_drivers": facade._brief_top_numeric_drivers(
                score_breakdown_by_symbol.get(selected_symbol)
                if isinstance(score_breakdown_by_symbol.get(selected_symbol), dict)
                else score_breakdown,
                limit=4,
            ),
        }
    return (scanner_selection_trace,)


def brief_input_canonical_monitor_snapshot_stop_policy_t(monitor_artifact, monitor_summary, monitor_trace, canonical_trade, *, facade):
    merged_monitor_stop_source: facade.Dict[str, facade.Any] = {}
    if isinstance(monitor_artifact, dict):
        merged_monitor_stop_source.update(monitor_artifact)
    if isinstance(monitor_summary, dict):
        merged_monitor_stop_source.update(monitor_summary)
    if isinstance(monitor_trace, dict):
        merged_monitor_stop_source.update(monitor_trace)
    monitor_stop_policy_trace = facade._brief_build_stop_policy_trace(merged_monitor_stop_source)
    canonical_monitor_stop_policy_trace = (
        canonical_trade.get("monitor_stop_policy_trace")
        if isinstance(canonical_trade.get("monitor_stop_policy_trace"), dict)
        else {}
    )
    canonical_monitor_snapshot_stop_policy_trace = (
        (canonical_trade.get("monitor_snapshot") or {}).get("monitor_stop_policy_trace")
        if isinstance((canonical_trade.get("monitor_snapshot") or {}).get("monitor_stop_policy_trace"), dict)
        else {}
    )
    return (canonical_monitor_snapshot_stop_policy_trace, canonical_monitor_stop_policy_trace, monitor_stop_policy_trace)


def brief_input_commander_applied_policy_monitor_applied(commander_artifact, commander_decision, monitor_trace, monitor_policy_ref, *, facade):
    commander_applied_policy = (
        commander_artifact.get("applied_policy")
        if isinstance(commander_artifact.get("applied_policy"), dict)
        else (
            commander_decision.get("applied_policy")
            if isinstance(commander_decision.get("applied_policy"), dict)
            else {}
        )
    )
    monitor_applied_policy = (
        monitor_trace.get("applied_policy")
        if isinstance(monitor_trace.get("applied_policy"), dict)
        else (
            monitor_policy_ref.get("applied_policy")
            if isinstance(monitor_policy_ref.get("applied_policy"), dict)
            else {}
        )
    )
    monitor_received_policy = (
        monitor_trace.get("received_policy")
        if isinstance(monitor_trace.get("received_policy"), dict)
        else (
            monitor_policy_ref.get("received_policy")
            if isinstance(monitor_policy_ref.get("received_policy"), dict)
            else {}
        )
    )
    monitor_effective_policy = (
        monitor_trace.get("effective_policy")
        if isinstance(monitor_trace.get("effective_policy"), dict)
        else (
            monitor_policy_ref.get("effective_policy")
            if isinstance(monitor_policy_ref.get("effective_policy"), dict)
            else monitor_applied_policy
        )
    )
    return (commander_applied_policy, monitor_applied_policy, monitor_effective_policy, monitor_received_policy)
