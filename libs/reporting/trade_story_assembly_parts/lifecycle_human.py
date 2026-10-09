from __future__ import annotations

from typing import Any, Dict, Mapping


def build_lifecycle_human_fallback(
    bundle_out: Dict[str, Any], *,
    entry: Dict[str, Any], holding: Dict[str, Any], exit_ctx: Dict[str, Any],
    summary: Dict[str, Any], reporter: Dict[str, Any],
    status: str, entry_action: str, exit_action: str, lifecycle_action: str,
    symbol: str, market_context_human: Dict[str, Any],
    scanner_reason_human: Dict[str, Any], filters_human: Dict[str, Any],
    deps: Mapping[str, Any],
):
    """Preserve lifecycle fallback and canonical human-text precedence at call time."""
    EXECUTION_OUTCOME_NOT_CAPTURED = deps["EXECUTION_OUTCOME_NOT_CAPTURED"]
    LIFECYCLE_CONCLUSION_NOT_CAPTURED = deps["LIFECYCLE_CONCLUSION_NOT_CAPTURED"]
    REPORTER_LINKAGE_NOT_CAPTURED = deps["REPORTER_LINKAGE_NOT_CAPTURED"]
    build_execution_outcome_fallback_from_lifecycle = deps["build_execution_outcome_fallback_from_lifecycle"]
    build_operator_conclusion_human = deps["build_operator_conclusion_human"]
    execution_outcome_summary_is_placeholder = deps["execution_outcome_summary_is_placeholder"]
    lifecycle_conclusion_summary_is_placeholder = deps["lifecycle_conclusion_summary_is_placeholder"]
    normalize_reporter_status_human = deps["normalize_reporter_status_human"]
    monitor_reason_human = dict(bundle_out.get("monitor_reason_human") or {})
    guard_reason_human = dict(bundle_out.get("guard_reason_human") or {})
    execution_outcome_human = dict(bundle_out.get("execution_outcome_human") or {})
    reporter_status_human = normalize_reporter_status_human(dict(bundle_out.get("reporter_status_human") or {}))
    operator_conclusion_human = dict(bundle_out.get("operator_conclusion_human") or {})
    if not market_context_human:
        market_context_human = {
            "summary": str((entry.get("strategist_context") or {}).get("market_context_summary") or "Market context was not captured."),
            "bullets": [
                f"Playbook: {str((entry.get('strategist_context') or {}).get('playbook') or 'not_captured')}",
                "Lifecycle-level entry context was used.",
            ],
        }
    if not scanner_reason_human:
        scanner_reason_human = {
            "summary": str(entry.get("reason_human") or "Scanner selection rationale was not captured."),
            "bullets": [str(entry.get("reason_human") or "no scanner rationale captured")],
        }
    if not monitor_reason_human:
        monitor_reason_human = {
            "summary": (
                f"Holding updates captured from {len(list(holding.get('run_ids') or []))} monitor runs."
                if list(holding.get("run_ids") or [])
                else "Holding monitor updates were not captured."
            ),
            "bullets": [str(x or "") for x in list(holding.get("monitor_updates") or [])[:8]],
        }
    synthesized_execution_outcome = build_execution_outcome_fallback_from_lifecycle(
        entry,
        exit_ctx,
        status=status,
        entry_action=entry_action,
        exit_action=exit_action,
        symbol=symbol,
    )
    if not execution_outcome_human or execution_outcome_summary_is_placeholder(execution_outcome_human.get("summary")):
        execution_outcome_human = dict(synthesized_execution_outcome)
    elif not execution_outcome_human.get("bullets"):
        execution_outcome_human["bullets"] = list(synthesized_execution_outcome.get("bullets") or [])
    if not str(execution_outcome_human.get("summary") or "").strip():
        execution_outcome_human = dict(synthesized_execution_outcome)
    if not str(execution_outcome_human.get("summary") or "").strip():
        execution_outcome_human = {
            "summary": str(summary.get("lifecycle_summary_human") or EXECUTION_OUTCOME_NOT_CAPTURED),
            "bullets": [
                f"Lifecycle status: {status}",
                f"Entry action: {entry_action or 'not_captured'}",
                f"Exit action: {exit_action or 'not_captured'}",
            ],
        }
    if not reporter_status_human:
        reporter_status_human = {
            "status": str(reporter.get("status_human") or "missing"),
            "summary": str(reporter.get("summary") or REPORTER_LINKAGE_NOT_CAPTURED),
            "grade": str(reporter.get("grade") or "N/A"),
            "bullets": [str(x or "") for x in list(reporter.get("improvement_points") or [])[:6]],
        }
    reporter_status_human = normalize_reporter_status_human(reporter_status_human)
    synthesized_operator_conclusion = build_operator_conclusion_human(
        execution={
            "action": lifecycle_action,
            "status": status,
            "symbol": symbol,
        },
        scanner_reason_human=scanner_reason_human,
        filters_human=filters_human,
        monitor_reason_human=monitor_reason_human,
        execution_outcome_human=execution_outcome_human,
        reporter_status_human=reporter_status_human,
    )
    if (
        not operator_conclusion_human
        or lifecycle_conclusion_summary_is_placeholder(operator_conclusion_human.get("summary"))
    ):
        operator_conclusion_human = dict(synthesized_operator_conclusion)
    else:
        if not str(operator_conclusion_human.get("current_action") or "").strip():
            operator_conclusion_human["current_action"] = str(
                synthesized_operator_conclusion.get("current_action") or ("HOLD" if status == "open" else lifecycle_action)
            )
        if not list(operator_conclusion_human.get("watch_next") or []):
            operator_conclusion_human["watch_next"] = list(synthesized_operator_conclusion.get("watch_next") or [])
        if not list(operator_conclusion_human.get("thesis_invalidation") or []):
            operator_conclusion_human["thesis_invalidation"] = list(
                synthesized_operator_conclusion.get("thesis_invalidation") or []
            )
    if not str(operator_conclusion_human.get("summary") or "").strip():
        operator_conclusion_human["summary"] = str(summary.get("operator_conclusion_human") or LIFECYCLE_CONCLUSION_NOT_CAPTURED)
    return (
        market_context_human, scanner_reason_human, monitor_reason_human,
        guard_reason_human, execution_outcome_human, reporter_status_human,
        operator_conclusion_human,
    )
