"""Pure projections of already-read Operator UI data. No IO or cached work.

Facade helpers are resolved when used, preserving existing monkeypatch seams.
"""
from __future__ import annotations

from typing import List


def _project_trade_identity(
    *,
    lifecycle,
    bundle,
    paths,
    bundle_path,
):
    """Resolve story identity and ordered run aliases from already-read bundles."""
    trade_id = str(
        lifecycle.get("trade_id")
        or bundle.get("trade_id")
        or bundle.get("story_id")
        or paths.get("trade_root", bundle_path.parent).name
    ).strip()
    story_id = trade_id
    run_id = str(bundle.get("run_id") or "").strip()
    linked_run_ids: List[str] = []
    for rid in list(bundle.get("linked_run_ids") or []):
        text = str(rid or "").strip()
        if text:
            linked_run_ids.append(text)
    if isinstance(lifecycle, dict):
        for rid in list(lifecycle.get("run_ids_all") or []):
            text = str(rid or "").strip()
            if text and text not in linked_run_ids:
                linked_run_ids.append(text)
        entry = lifecycle.get("entry") if isinstance(lifecycle.get("entry"), dict) else {}
        exit_ctx = lifecycle.get("exit") if isinstance(lifecycle.get("exit"), dict) else {}
        for rid in (entry.get("run_id"), exit_ctx.get("run_id")):
            text = str(rid or "").strip()
            if text and text not in linked_run_ids:
                linked_run_ids.append(text)
    if run_id and run_id not in linked_run_ids:
        linked_run_ids.append(run_id)

    execution = bundle.get("execution") if isinstance(bundle.get("execution"), dict) else {}
    story_contract = bundle.get("story_contract") if isinstance(bundle.get("story_contract"), dict) else {}
    reporter_status_human = bundle.get("reporter_status_human") if isinstance(bundle.get("reporter_status_human"), dict) else {}
    operator_conclusion_human = bundle.get("operator_conclusion_human") if isinstance(bundle.get("operator_conclusion_human"), dict) else {}
    execution_outcome_human = bundle.get("execution_outcome_human") if isinstance(bundle.get("execution_outcome_human"), dict) else {}
    return (
        trade_id,
        story_id,
        run_id,
        linked_run_ids,
        execution,
        story_contract,
        reporter_status_human,
        operator_conclusion_human,
        execution_outcome_human,
    )


def _project_trade_summary(
    *,
    report,
    lifecycle,
    bundle,
    operator_conclusion_human,
    execution_outcome_human,
    reporter_status_human,
    story_contract,
    facade,
):
    """Apply the existing report/lifecycle/human-summary fallback precedence."""
    executive = report.get("executive_summary") if isinstance(report.get("executive_summary"), dict) else {}
    reporter_eval = report.get("reporter_evaluation") if isinstance(report.get("reporter_evaluation"), dict) else {}
    final_conclusion = report.get("final_operator_conclusion") if isinstance(report.get("final_operator_conclusion"), dict) else {}
    generation = report.get("generation") if isinstance(report.get("generation"), dict) else {}
    lifecycle_summary_obj = lifecycle.get("summary") if isinstance(lifecycle.get("summary"), dict) else {}
    lifecycle_status = str(lifecycle.get("status") or bundle.get("trade_lifecycle_status") or report.get("status") or "").strip().lower()
    lifecycle_summary = (
        facade._trim_text(lifecycle_summary_obj.get("lifecycle_summary_human"), max_len=260)
        or facade._trim_text(bundle.get("trade_lifecycle_summary"), max_len=260)
        or facade._trim_text(final_conclusion.get("summary"), max_len=260)
    )

    story_type = str(story_contract.get("story_type") or lifecycle.get("story_type") or report.get("story_type") or "").strip().lower()
    execution_mode_label = str(story_contract.get("execution_mode_label") or lifecycle.get("execution_mode_label") or report.get("execution_mode_label") or "").strip()
    report_summary = (
        facade._trim_text(executive.get("summary"), max_len=260)
        or facade._trim_text(final_conclusion.get("summary"), max_len=260)
        or facade._trim_text(operator_conclusion_human.get("summary"), max_len=260)
        or facade._trim_text(execution_outcome_human.get("summary"), max_len=260)
    )
    reporter_summary = (
        facade._trim_text(reporter_eval.get("summary"), max_len=220)
        or facade._trim_text(reporter_status_human.get("summary"), max_len=220)
        or "Reporter linkage summary is not available yet."
    )
    return (
        generation,
        lifecycle_status,
        lifecycle_summary,
        story_type,
        execution_mode_label,
        report_summary,
        reporter_summary,
    )


def _project_trade_record(
    *,
    report_exists,
    trade_id,
    story_id,
    run_id,
    linked_run_ids,
    symbol,
    action,
    story_type,
    reporter_summary,
    lifecycle_status,
    generation,
    lifecycle_summary,
    execution_mode_label,
    report_summary,
    report,
    bundle,
    lifecycle,
    trade_health,
    facade,
):
    """Format record fields before the coordinator probes artifact paths."""
    raw_diagnostics = (
        report.get("ai_report_diagnostics")
        if isinstance(report.get("ai_report_diagnostics"), dict)
        else bundle.get("ai_report_diagnostics")
        if isinstance(bundle.get("ai_report_diagnostics"), dict)
        else lifecycle.get("ai_report_diagnostics")
        if isinstance(lifecycle.get("ai_report_diagnostics"), dict)
        else trade_health.get("ai_report_diagnostics")
        if isinstance(trade_health.get("ai_report_diagnostics"), dict)
        else {}
    )
    diagnostics = facade._normalize_ai_report_diagnostics(
        raw_diagnostics,
        report_exists=report_exists,
        lifecycle_status=lifecycle_status,
        story_type=story_type,
        model_hint=generation.get("model"),
        generation=generation,
    )
    report_available = bool(report_exists)
    record = {
        "trade_id": trade_id,
        "story_id": story_id,
        "run_id": run_id,
        "run_id_short": facade._short_run_id(run_id),
        "linked_run_ids": linked_run_ids,
        "symbol": symbol,
        "action": action,
        "story_type": story_type,
        "story_type_label": facade._story_type_label(story_type),
        "story_type_badge_class": facade._story_type_badge_class(story_type),
        "lifecycle_status": lifecycle_status or "unknown",
        "lifecycle_status_label": (lifecycle_status or "unknown").upper(),
        "lifecycle_summary": lifecycle_summary or "Lifecycle summary is not available yet.",
        "execution_mode_label": execution_mode_label or "not captured",
        "report_available": report_available,
        "report_status": str(diagnostics.get("report_status") or ""),
        "report_status_label": str(diagnostics.get("report_status_label") or facade._report_status_label("")),
        "report_status_badge_class": str(diagnostics.get("report_status_badge_class") or "status-badge"),
        "report_reason_code": str(diagnostics.get("report_reason_code") or ""),
        "report_reason_human": str(diagnostics.get("report_reason_human") or ""),
        "report_next_expected_step": str(diagnostics.get("next_expected_step") or ""),
        "report_generation_attempted": bool(diagnostics.get("generation_attempted")),
        "report_generation_ts": str(diagnostics.get("generation_ts") or ""),
        "report_generation_model": str(diagnostics.get("llm_model_used") or ""),
        "report_generation_provider": str(diagnostics.get("llm_provider") or "OpenRouter"),
        "ai_report_diagnostics": diagnostics,
        "report_summary": report_summary or "Per-trade report summary was not generated yet.",
        "reporter_status_human": reporter_summary,
        "report_link": f"/reports/trade/{trade_id}" if trade_id and report_exists else "",
        "operator_brief_available": bool(trade_id),
        "operator_brief_link": f"/reports/trade/{trade_id}/brief" if trade_id else "",
    }
    return record


def _project_trade_indexes(
    *,
    story_id,
    linked_run_ids,
    record,
    by_story_id,
    by_run_id
):
    """Return only winning updates; leave inputs intact and retain record aliases.

    Equal priority and timestamp intentionally replaces the previous record.
    Small update maps avoid copying the entire growing index for each bundle.
    """
    next_by_run_id = {}
    next_by_story_id = {}
    if story_id:
        current_story = by_story_id.get(story_id)
        if (not current_story) or (
            int(record.get("_path_priority") or 0) > int(current_story.get("_path_priority") or 0)
            or (
                int(record.get("_path_priority") or 0) == int(current_story.get("_path_priority") or 0)
                and int(record.get("ts_epoch") or 0) >= int(current_story.get("ts_epoch") or 0)
            )
        ):
            next_by_story_id[story_id] = record
    for rid in linked_run_ids:
        current = next_by_run_id.get(rid, by_run_id.get(rid))
        if (not current) or (
            int(record.get("_path_priority") or 0) > int(current.get("_path_priority") or 0)
            or (
                int(record.get("_path_priority") or 0) == int(current.get("_path_priority") or 0)
                and int(record.get("ts_epoch") or 0) >= int(current.get("ts_epoch") or 0)
            )
        ):
            next_by_run_id[rid] = record
    return next_by_run_id, next_by_story_id
