from __future__ import annotations

from typing import Any, Dict, Mapping


def enrich_lifecycle_story_evidence(
    bundle_out: Dict[str, Any], *, lifecycle: Dict[str, Any],
    exit_ctx: Dict[str, Any], canonical_agent_artifacts: Dict[str, Any],
    symbol: str, market_context_human: Dict[str, Any],
    scanner_reason_human: Dict[str, Any], monitor_reason_human: Dict[str, Any],
    deps: Mapping[str, Any],
):
    """Resolve canonical scanner/strategist/monitor context and enrich story evidence."""
    _attach_news_scanner_contribution = deps["_attach_news_scanner_contribution"]
    _build_monitor_blocker_trace = deps["_build_monitor_blocker_trace"]
    _build_monitor_stop_policy_trace = deps["_build_monitor_stop_policy_trace"]
    _build_scanner_selection_trace = deps["_build_scanner_selection_trace"]
    _build_strategist_evidence_trace = deps["_build_strategist_evidence_trace"]
    _raw_strategist_evidence = deps["_raw_strategist_evidence"]
    _resolve_selection_monitor_artifact = deps["_resolve_selection_monitor_artifact"]
    _set_or_replace_placeholder = deps["_set_or_replace_placeholder"]
    _strategist_trace_source = deps["_strategist_trace_source"]
    build_news_symbol_linkage_view = deps["build_news_symbol_linkage_view"]
    reanchor_scanner_selection_for_monitor_fallback = deps["reanchor_scanner_selection_for_monitor_fallback"]
    canonical_strategist = (
        canonical_agent_artifacts.get("strategist")
        if isinstance(canonical_agent_artifacts.get("strategist"), dict)
        else bundle_out.get("strategist")
        if isinstance(bundle_out.get("strategist"), dict)
        else {}
    )
    canonical_scanner = (
        canonical_agent_artifacts.get("scanner")
        if isinstance(canonical_agent_artifacts.get("scanner"), dict)
        else bundle_out.get("scanner")
        if isinstance(bundle_out.get("scanner"), dict)
        else {}
    )
    canonical_monitor = (
        canonical_agent_artifacts.get("monitor")
        if isinstance(canonical_agent_artifacts.get("monitor"), dict)
        else bundle_out.get("monitor")
        if isinstance(bundle_out.get("monitor"), dict)
        else {}
    )
    strategy_horizon_feedback = (
        dict(bundle_out.get("strategy_horizon_feedback") or {})
        if isinstance(bundle_out.get("strategy_horizon_feedback"), dict)
        else dict(canonical_strategist.get("strategy_horizon_feedback") or {})
        if isinstance(canonical_strategist.get("strategy_horizon_feedback"), dict)
        else {}
    )
    exit_vs_strategy_intent = (
        dict(bundle_out.get("exit_vs_strategy_intent") or {})
        if isinstance(bundle_out.get("exit_vs_strategy_intent"), dict)
        else dict(canonical_monitor.get("exit_vs_strategy_intent") or {})
        if isinstance(canonical_monitor.get("exit_vs_strategy_intent"), dict)
        else dict((exit_ctx.get("monitor_context") or {}).get("exit_vs_strategy_intent") or {})
        if isinstance(exit_ctx.get("monitor_context"), dict)
        and isinstance((exit_ctx.get("monitor_context") or {}).get("exit_vs_strategy_intent"), dict)
        else {}
    )
    post_exit_shadow = (
        dict(bundle_out.get("post_exit_shadow") or {})
        if isinstance(bundle_out.get("post_exit_shadow"), dict)
        else dict(lifecycle.get("post_exit_shadow") or {})
        if isinstance(lifecycle.get("post_exit_shadow"), dict)
        else dict(exit_ctx.get("post_exit_shadow") or {})
        if isinstance(exit_ctx.get("post_exit_shadow"), dict)
        else {}
    )
    selection_monitor = _resolve_selection_monitor_artifact(bundle_out, canonical_agent_artifacts)
    scanner_selection_trace = _build_scanner_selection_trace(scanner_reason_human, canonical_scanner)
    scanner_reason_human, scanner_selection_trace, selected_symbol = reanchor_scanner_selection_for_monitor_fallback(
        scanner_reason_human=scanner_reason_human,
        scanner_selection_trace=scanner_selection_trace,
        scanner_artifact=canonical_scanner,
        monitor_artifact=selection_monitor,
        trade_symbol=symbol or str((bundle_out.get("execution") or {}).get("symbol") or ""),
    )
    raw_strategist_evidence = _raw_strategist_evidence(bundle_out)
    strategist_evidence_trace = _build_strategist_evidence_trace(
        _strategist_trace_source(canonical_strategist, raw_strategist_evidence),
        selected_symbol=selected_symbol,
        fallback_market_titles=market_context_human.get("market_news_titles"),
        fallback_candidate_titles=market_context_human.get("candidate_news_titles"),
    )
    _attach_news_scanner_contribution(
        scanner_reason_human=scanner_reason_human,
        scanner_selection_trace=scanner_selection_trace,
        canonical_scanner=canonical_scanner,
        canonical_strategist=canonical_strategist,
        selected_symbol=selected_symbol,
    )
    ranked_symbols = [
        str(row.get("symbol") or "").strip()
        for row in list(scanner_selection_trace.get("ranked_candidates") or [])
        if isinstance(row, dict) and str(row.get("symbol") or "").strip()
    ]
    news_symbol_linkage = build_news_symbol_linkage_view(
        strategist_summary=canonical_strategist,
        strategist_raw_input=raw_strategist_evidence,
        strategist_parsed_output=dict((bundle_out.get("strategist_summary") or {}).get("llm_parsed_output") or {}),
        selected_symbol=selected_symbol,
        top_ranked_symbols=ranked_symbols or canonical_scanner.get("top_ranked_symbols") or [],
    )
    monitor_stop_thresholds = (
        ((canonical_monitor.get("thresholds_guards_used") or {}).get("thresholds"))
        if isinstance((canonical_monitor.get("thresholds_guards_used") or {}).get("thresholds"), dict)
        else canonical_monitor.get("thresholds")
        if isinstance(canonical_monitor.get("thresholds"), dict)
        else canonical_monitor.get("threshold_snapshot")
        if isinstance(canonical_monitor.get("threshold_snapshot"), dict)
        else {}
    )
    monitor_stop_policy_trace = _build_monitor_stop_policy_trace(
        canonical_monitor,
        monitor_stop_thresholds,
    )
    monitor_blocker_trace = _build_monitor_blocker_trace(monitor_reason_human)
    market_context_human.setdefault("candidate_hints", strategist_evidence_trace.get("candidate_hints") or [])
    market_context_human.setdefault("market_headlines", strategist_evidence_trace.get("market_headlines") or [])
    selected_symbol_headlines = list(strategist_evidence_trace.get("symbol_headlines") or [])
    market_context_human["symbol_headlines"] = selected_symbol_headlines
    market_context_human["symbol_news_titles"] = selected_symbol_headlines
    market_context_human["candidate_news_titles"] = selected_symbol_headlines
    market_context_human["strategist_evidence_trace"] = dict(strategist_evidence_trace)
    market_context_human["news_symbol_linkage"] = dict(news_symbol_linkage)
    _set_or_replace_placeholder(
        scanner_reason_human,
        "scanner_selection_trace",
        dict(scanner_selection_trace),
    )
    _set_or_replace_placeholder(
        scanner_reason_human,
        "ranked_candidates",
        list(scanner_selection_trace.get("ranked_candidates") or []),
    )
    scanner_reason_human.setdefault("selection_reason", scanner_selection_trace.get("selection_reason"))
    scanner_reason_human.setdefault(
        "selected_symbol_score_drivers",
        dict(scanner_selection_trace.get("selected_symbol_score_drivers") or {}),
    )
    _set_or_replace_placeholder(
        monitor_reason_human,
        "monitor_stop_policy_trace",
        dict(monitor_stop_policy_trace),
    )
    _set_or_replace_placeholder(
        monitor_reason_human,
        "monitor_blocker_trace",
        dict(monitor_blocker_trace),
    )
    return (
        canonical_strategist,
        canonical_scanner,
        canonical_monitor,
        strategy_horizon_feedback,
        exit_vs_strategy_intent,
        post_exit_shadow,
        selection_monitor,
        scanner_selection_trace,
        raw_strategist_evidence,
        strategist_evidence_trace,
        news_symbol_linkage,
        monitor_stop_policy_trace,
        monitor_blocker_trace,
        scanner_reason_human,
    )
