"""Lifecycle execution-outcome, reporter-status and operator-conclusion human summaries.

Third Pass T2 (P1.5) intra-function extraction from `libs/reporting/live_execution_bundle_runner.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def lifecycle_outcome_and_reporter_summaries(exit_execution_context, anchor_bundle, anchor_execution, story_type, execution_mode_label_text, resolved_bundle_sources, reporter_obj, *, facade):
    lifecycle_execution_outcome_human = dict(exit_execution_context or anchor_bundle.get("execution_outcome_human") or {})
    if not lifecycle_execution_outcome_human:
        lifecycle_execution_outcome_human = facade.build_execution_outcome_human(
            anchor_execution,
            dict((resolved_bundle_sources.get("agents") or {}).get("executor") or anchor_bundle.get("executor") or {}),
            story_type=story_type,
            mode_label=execution_mode_label_text,
        )
    lifecycle_reporter_status_human = {
        "status": str(reporter_obj.get("status_human") or "missing"),
        "summary": str(reporter_obj.get("summary") or ""),
        "grade": str(reporter_obj.get("grade") or "N/A"),
        "bullets": [str(x or "") for x in list(reporter_obj.get("improvement_points") or [])[:6]],
    }
    lifecycle_operator_conclusion_human = dict(anchor_bundle.get("operator_conclusion_human") or {})
    return (lifecycle_execution_outcome_human, lifecycle_operator_conclusion_human, lifecycle_reporter_status_human)


def lifecycle_operator_conclusion_fallback(anchor_execution, exit_action, status, exit_ctx, lifecycle_monitor_reason_human, lifecycle_execution_outcome_human, lifecycle_reporter_status_human, anchor_bundle, entry_ctx, *, facade):
    conclusion_execution = dict(anchor_execution)
    if status == "closed" and exit_action:
        conclusion_execution["action"] = exit_action
        if exit_ctx.get("qty") not in (None, ""):
            conclusion_execution["qty"] = facade.safe_int(exit_ctx.get("qty"), facade.safe_int(conclusion_execution.get("qty"), 0))
        if exit_ctx.get("ts") not in (None, ""):
            conclusion_execution["ts"] = str(exit_ctx.get("ts") or "")
    lifecycle_operator_conclusion_human = facade.build_operator_conclusion_human(
        execution=conclusion_execution if status == "closed" and exit_action else anchor_execution,
        scanner_reason_human=dict(anchor_bundle.get("scanner_reason_human") or entry_ctx.get("scanner_context") or {}),
        filters_human=dict(anchor_bundle.get("filters_human") or {}),
        monitor_reason_human=lifecycle_monitor_reason_human,
        execution_outcome_human=lifecycle_execution_outcome_human,
        reporter_status_human=lifecycle_reporter_status_human,
    )
    return (conclusion_execution, lifecycle_operator_conclusion_human)
