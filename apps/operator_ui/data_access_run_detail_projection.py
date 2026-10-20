"""Pure projections of already-read Operator UI data. No IO or cached work.

Facade helpers are resolved when used, preserving existing monkeypatch seams.
"""
from __future__ import annotations



def _project_canonical_run(
    *,
    canonical_sources,
    route_row,
    end_row,
    strategist_summary,
    scanner_summary,
    monitor_summary,
    verdict_payload,
    execution_payload,
    strategist_llm,
    strategic_frame,
    candidate_selection,
    entry_exit_decision,
    facade,
):
    """Prefer canonical payloads and preserve deterministic trace/LLM fallbacks."""
    commander_summary, commander_provenance = facade.prefer_canonical_agent_payload(
        canonical_sources,
        "commander",
        {
            "mode": str((route_row.get("payload") or {}).get("mode") or ""),
            "phase": str((route_row.get("payload") or {}).get("phase") or ""),
            "status": str((end_row.get("payload") or {}).get("status") or ""),
            "path": str((end_row.get("payload") or {}).get("path") or ""),
        },
        fallback_source="event_log",
    )
    strategist_summary, strategist_provenance = facade.prefer_canonical_agent_payload(
        canonical_sources,
        "strategist",
        strategist_summary if isinstance(strategist_summary, dict) else {},
        fallback_source="event_log",
    )
    scanner_summary, scanner_provenance = facade.prefer_canonical_agent_payload(
        canonical_sources,
        "scanner",
        scanner_summary if isinstance(scanner_summary, dict) else {},
        fallback_source="event_log",
    )
    monitor_summary, monitor_provenance = facade.prefer_canonical_agent_payload(
        canonical_sources,
        "monitor",
        monitor_summary if isinstance(monitor_summary, dict) else {},
        fallback_source="event_log",
    )
    verdict_payload, supervisor_provenance = facade.prefer_canonical_agent_payload(
        canonical_sources,
        "supervisor",
        verdict_payload if isinstance(verdict_payload, dict) else {},
        fallback_source="event_log",
    )
    execution_payload, executor_provenance = facade.prefer_canonical_agent_payload(
        canonical_sources,
        "executor",
        execution_payload if isinstance(execution_payload, dict) else {},
        fallback_source="event_log",
    )
    normalized_execution = facade._normalize_execution_payload(execution_payload if isinstance(execution_payload, dict) else {})
    if not strategist_llm and isinstance(strategist_summary.get("llm_metadata_summary"), dict):
        strategist_llm = dict(strategist_summary.get("llm_metadata_summary") or {})
    if not isinstance(strategic_frame, dict) or not strategic_frame:
        strategic_frame = dict(strategist_summary or {})
    if (not isinstance(candidate_selection, dict) or not candidate_selection) and isinstance(scanner_summary.get("selected_candidate"), dict):
        candidate_selection = {
            "selected_symbol": scanner_summary.get("selected_symbol") or scanner_summary.get("top_stock"),
            "candidate_pool_size": scanner_summary.get("candidate_pool_after_filter") or scanner_summary.get("universe_size"),
            "selected_candidate": dict(scanner_summary.get("selected_candidate") or {}),
        }
    elif scanner_provenance == "canonical":
        candidate_selection = dict(candidate_selection or {})
        selected_candidate = (
            candidate_selection.get("selected_candidate")
            if isinstance(candidate_selection.get("selected_candidate"), dict)
            else {}
        )
        merged_selected_candidate = dict(selected_candidate or {})
        merged_selected_candidate.update(
            dict(scanner_summary.get("selected_candidate") or {})
            if isinstance(scanner_summary.get("selected_candidate"), dict)
            else {}
        )
        candidate_selection["selected_symbol"] = (
            scanner_summary.get("selected_symbol")
            or scanner_summary.get("top_stock")
            or candidate_selection.get("selected_symbol")
        )
        candidate_selection["candidate_pool_size"] = (
            scanner_summary.get("candidate_pool_after_filter")
            or scanner_summary.get("universe_size")
            or candidate_selection.get("candidate_pool_size")
        )
        candidate_selection["selected_candidate"] = merged_selected_candidate
    if not isinstance(entry_exit_decision, dict) or not entry_exit_decision:
        entry_exit_decision = dict(monitor_summary or {})
    elif monitor_provenance == "canonical":
        entry_exit_decision = {**dict(entry_exit_decision or {}), **dict(monitor_summary or {})}
    primary_symbol = facade.normalize_symbol(
        normalized_execution.get("symbol")
        or scanner_summary.get("top_stock")
        or candidate_selection.get("selected_symbol")
        or "",
        allow_test_symbols=True,
    ).strip()
    return (
        commander_summary,
        commander_provenance,
        strategist_summary,
        strategist_provenance,
        scanner_summary,
        scanner_provenance,
        monitor_summary,
        monitor_provenance,
        verdict_payload,
        supervisor_provenance,
        execution_payload,
        executor_provenance,
        normalized_execution,
        strategist_llm,
        strategic_frame,
        candidate_selection,
        entry_exit_decision,
        primary_symbol,
    )


def _project_run_presentation(
    *,
    portfolio_sync,
    trade_report_card,
    commander_provenance,
    strategist_summary,
    strategist_llm,
    strategist_provenance,
    scanner_summary,
    feature_coverage,
    quote_metrics,
    scanner_provenance,
    monitor_summary,
    monitor_provenance,
    verdict_payload,
    supervisor_provenance,
    execution_payload,
    executor_provenance,
    run_day,
    primary_symbol,
    same_day_symbol_run_chain,
    run_id,
    commander_summary,
    strategic_frame,
    candidate_selection,
    entry_exit_decision,
    same_day_symbol_trades,
    route_row,
    end_row,
    strategist_evidence,
    facade,
):
    """Present already-read roles before the caller's Reporter/brief IO barrier."""
    detail = {
        "found": True,
        "run_id": str(run_id or ""),
        "started_at": facade._iso_to_display(route_row.get("ts")),
        "completed_at": facade._iso_to_display(end_row.get("ts")),
        "commander": {
            "mode": str(commander_summary.get("mode") or commander_summary.get("command") or (route_row.get("payload") or {}).get("mode") or ""),
            "phase": str(commander_summary.get("phase") or ((commander_summary.get("blocked_allowed_details") or {}) if isinstance(commander_summary.get("blocked_allowed_details"), dict) else {}).get("phase") or (route_row.get("payload") or {}).get("phase") or ""),
            "agents": list(commander_summary.get("invoked_agents") or (route_row.get("payload") or {}).get("agents") or []),
            "status": str(commander_summary.get("status") or (end_row.get("payload") or {}).get("status") or ""),
            "path": str(commander_summary.get("path") or commander_summary.get("decision") or (end_row.get("payload") or {}).get("path") or ""),
            "reason": str(commander_summary.get("reason") or ""),
            "provenance": commander_provenance,
            "artifact": commander_summary if isinstance(commander_summary, dict) else {},
        },
        "strategist": {
            "summary": strategist_summary,
            "llm": strategist_llm,
            "decision_trace": strategic_frame if isinstance(strategic_frame, dict) else {},
            "provenance": strategist_provenance,
            "evidence": {
                "raw_input": strategist_evidence.get("raw_input") if isinstance(strategist_evidence.get("raw_input"), dict) else {},
                "llm_prompt": str(strategist_evidence.get("llm_prompt") or ""),
                "llm_response": str(strategist_evidence.get("llm_response") or ""),
                "parsed_output": strategist_evidence.get("parsed_output") if isinstance(strategist_evidence.get("parsed_output"), dict) else {},
            },
        },
        "scanner": {
            "summary": scanner_summary,
            "decision_trace": candidate_selection if isinstance(candidate_selection, dict) else {},
            "feature_coverage": feature_coverage,
            "quote_metrics": quote_metrics,
            "provenance": scanner_provenance,
        },
        "monitor": {
            "summary": monitor_summary,
            "decision_trace": entry_exit_decision if isinstance(entry_exit_decision, dict) else {},
            "provenance": monitor_provenance,
        },
        "supervisor": {
            "verdict": verdict_payload,
            "provenance": supervisor_provenance,
        },
        "executor": {
            "execution": execution_payload,
            "provenance": executor_provenance,
        },
        "portfolio_sync": portfolio_sync,
        "same_day_symbol_trade_history": {
            "day": run_day,
            "symbol": primary_symbol,
            "trade_count": len(same_day_symbol_trades),
            "trades": same_day_symbol_trades[:20],
        },
        "same_day_symbol_run_chain": {
            "day": run_day,
            "symbol": primary_symbol,
            "run_count": len(same_day_symbol_run_chain),
            "runs": same_day_symbol_run_chain,
        },
        "trade_report": trade_report_card,
    }
    return detail
