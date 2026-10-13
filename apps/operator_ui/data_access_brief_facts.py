"""Operator brief canonical-trade/agent facts (read-only; Reporter output is not recomputed).

Second Pass (P1.5) intra-function extraction from `apps/operator_ui/data_access_core.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations

from typing import Any, NamedTuple


class OperatorBriefCanonicalFacts(NamedTuple):
    """Result of `operator_brief_canonical_facts` (positional order is the legacy tuple order; unpacking call-sites are unchanged)."""

    canonical_monitor_snapshot: Any
    execution: Any
    feature_coverage: Any
    feature_snapshot: Any
    live_exit_reason: Any
    live_monitor_reason: Any
    monitor_summary: Any
    monitor_trace: Any
    path_label: Any
    phase: Any
    quote_metrics: Any
    scanner_summary: Any
    scanner_trace: Any
    score_breakdown: Any
    selected_candidate: Any
    selected_symbol: Any
    source_scores: Any
    strategist_raw_input: Any
    strategist_summary: Any
    strategist_trace: Any
    supervisor_reason: Any
    thresholds: Any
    top_candidates: Any
    verdict: Any


def operator_brief_canonical_facts(canonical_trade, strategist, scanner, monitor, supervisor, executor, detail, *, facade):
    canonical_monitor_snapshot = (
        canonical_trade.get("monitor_snapshot")
        if isinstance(canonical_trade.get("monitor_snapshot"), dict)
        else {}
    )

    strategist_summary = strategist.get("summary") if isinstance(strategist.get("summary"), dict) else {}
    strategist_trace = strategist.get("decision_trace") if isinstance(strategist.get("decision_trace"), dict) else {}
    strategist_evidence = strategist.get("evidence") if isinstance(strategist.get("evidence"), dict) else {}
    strategist_raw_input = strategist_evidence.get("raw_input") if isinstance(strategist_evidence.get("raw_input"), dict) else {}

    scanner_summary = scanner.get("summary") if isinstance(scanner.get("summary"), dict) else {}
    scanner_trace = scanner.get("decision_trace") if isinstance(scanner.get("decision_trace"), dict) else {}
    selected_candidate = scanner_trace.get("selected_candidate") if isinstance(scanner_trace.get("selected_candidate"), dict) else {}
    feature_snapshot = selected_candidate.get("feature_snapshot") if isinstance(selected_candidate.get("feature_snapshot"), dict) else {}
    score_breakdown = selected_candidate.get("score_breakdown") if isinstance(selected_candidate.get("score_breakdown"), dict) else {}
    source_scores = selected_candidate.get("source_scores") if isinstance(selected_candidate.get("source_scores"), dict) else {}
    feature_coverage = facade._normalized_feature_coverage(
        scanner.get("feature_coverage") if isinstance(scanner.get("feature_coverage"), dict) else {},
        feature_snapshot,
    )
    quote_metrics = scanner.get("quote_metrics") if isinstance(scanner.get("quote_metrics"), dict) else facade._quote_metrics_snapshot(feature_snapshot)

    monitor_summary = monitor.get("summary") if isinstance(monitor.get("summary"), dict) else {}
    monitor_trace = monitor.get("decision_trace") if isinstance(monitor.get("decision_trace"), dict) else {}
    thresholds = monitor_trace.get("thresholds") if isinstance(monitor_trace.get("thresholds"), dict) else {}
    live_monitor_reason = str(monitor_summary.get("monitor_reason") or monitor_trace.get("monitor_reason") or "").strip()
    live_exit_reason = str(monitor_summary.get("exit_reason") or monitor_trace.get("exit_reason") or "").strip()

    verdict = supervisor.get("verdict") if isinstance(supervisor.get("verdict"), dict) else {}
    execution = facade._normalize_execution_payload(executor.get("execution") if isinstance(executor.get("execution"), dict) else {})
    phase = str(((detail.get("commander") or {}).get("phase") or "session")).strip() or "session"
    path_label = str(((detail.get("commander") or {}).get("path") or "-")).strip() or "-"
    supervisor_reason = facade._clean_brief_text(verdict.get("reason") or supervisor.get("reason") or "")

    selected_symbol = facade.normalize_symbol(
        canonical_trade.get("symbol")
        or execution.get("symbol")
        or scanner_trace.get("selected_symbol")
        or scanner_summary.get("top_stock")
        or selected_candidate.get("symbol")
        or "",
        allow_test_symbols=True,
    ).strip()
    top_candidates = facade._build_top_candidates(scanner_summary, scanner_trace, selected_symbol)
    return OperatorBriefCanonicalFacts(canonical_monitor_snapshot, execution, feature_coverage, feature_snapshot, live_exit_reason, live_monitor_reason, monitor_summary, monitor_trace, path_label, phase, quote_metrics, scanner_summary, scanner_trace, score_breakdown, selected_candidate, selected_symbol, source_scores, strategist_raw_input, strategist_summary, strategist_trace, supervisor_reason, thresholds, top_candidates, verdict)


def brief_facts_confidence_execution_action(canonical_trade, scanner_summary, top_candidates, scanner_trace, execution, live_monitor_reason, live_exit_reason, selected_candidate, *, facade):
    universe_size = facade._safe_int(
        canonical_trade.get("universe_size"),
        facade._safe_int(scanner_summary.get("candidate_pool_after_filter"), facade._safe_int(scanner_trace.get("candidate_pool_size"), len(top_candidates))),
    )

    shared_facts = canonical_trade.get("shared_facts") if isinstance(canonical_trade.get("shared_facts"), dict) else {}
    execution_action = str(execution.get("action") or "").upper()
    report_lifecycle_status = str(shared_facts.get("status") or canonical_trade.get("lifecycle_status") or "").strip().lower()
    canonical_action = str(shared_facts.get("action") or canonical_trade.get("current_action") or "").upper()
    monitor_reason = str(canonical_trade.get("monitor_summary") or live_monitor_reason or "").strip()
    exit_reason = str(shared_facts.get("exit_reason") or canonical_trade.get("exit_reason") or live_exit_reason or "").strip()
    final_action = canonical_action if canonical_action in {"BUY", "SELL", "HOLD", "WAIT"} else "WAIT"

    confidence_raw = (
        selected_candidate.get("confidence")
        if selected_candidate.get("confidence") is not None
        else selected_candidate.get("score_total")
    )
    confidence = facade._format_float(confidence_raw, 2) if confidence_raw is not None else ""

    selection_reasons: facade.List[str] = []
    selected_why = facade._clean_brief_text(selected_candidate.get("why") or scanner_trace.get("selected_reason") or "")
    canonical_selection_basis = facade._clean_brief_text(canonical_trade.get("selection_basis") or "")
    if canonical_trade.get("selection_summary"):
        selection_reasons.append(str(canonical_trade.get("selection_summary")))
    if canonical_selection_basis and canonical_selection_basis not in selection_reasons:
        selection_reasons.append(canonical_selection_basis)
    return (confidence, execution_action, exit_reason, final_action, monitor_reason, report_lifecycle_status, selected_why, selection_reasons, shared_facts, universe_size)
