"""Deterministic Reporter analysis read-model projection (P1.5 CODE BATCH 01/02, DEV-A).

Owns the deterministic section assembly and the pure result/evidence presentation of ``generate_reporter_analysis_report``:
the ``reporter_analysis.v1`` base report, the degraded AI-review fallback payload and the
AI evidence projection. No log reads, LLM calls, memory/ledger writes or report files here;
those stay in the ``libs.reporting.reporter_analysis`` orchestrator.

Helpers (``_safe_int``, ``_build_ai_evidence_catalog``, ``_ensure_min_ai_review_payload``,
``_hydrate_ai_evidence_details``) are resolved on the injected ``facade`` at call time so a
late monkeypatch of the facade module is honoured exactly as before the extraction.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List


def build_analysis_sections(
    *,
    day_rows: List[Dict[str, Any]],
    trade_obj: Dict[str, Any],
    trade_decision: Dict[str, Any],
    intent_flow: Dict[str, Any],
    target_day: str,
    rapid_cycle_threshold_sec: Any,
    facade: Any,
) -> Dict[str, Any]:
    """Compute the deterministic report sections in the original order from already-read inputs.

    ``intent_flow`` (which may read ``intents_path``) and ``trade_decision`` are computed by the caller first.
    Keys match ``build_base_report`` keyword names.
    """
    strategy_eff = facade._build_strategy_effectiveness(day_rows=day_rows, trade_explain_obj=trade_obj)
    report_focus_targets = facade._extract_report_focus_targets(day_rows)
    overtrading = facade._build_overtrading_diagnostics(
        trade_explain_obj=trade_obj,
        intent_flow=intent_flow,
        rapid_threshold_sec=max(1, int(rapid_cycle_threshold_sec)),
    )
    incident = facade._build_incident_postmortem(overtrading=overtrading, intent_flow=intent_flow, day_rows=day_rows)
    market_context = facade._build_market_context(trade_explain_obj=trade_obj, day_rows=day_rows)
    strategy_frame_summary = facade._build_strategy_frame_summary(day_rows)
    decision_chains = facade._build_decision_chains(day_rows, limit=200)
    decision_trace_chain_summary = facade._build_decision_trace_chain_summary(day_rows, limit=200)
    trade_summary = facade._build_trade_summary_section(trade_decision=trade_decision, decision_chains=decision_chains)
    strategist_eval = facade._build_strategist_evaluation(day_rows)
    scanner_eval = facade._build_scanner_evaluation(day_rows)
    monitor_eval = facade._build_monitor_evaluation(day_rows=day_rows, overtrading=overtrading)
    supervisor_activity = facade._build_supervisor_activity(day_rows, intent_flow=intent_flow)
    improvement_suggestions = facade._build_improvement_suggestions(
        strategist_eval=strategist_eval,
        scanner_eval=scanner_eval,
        monitor_eval=monitor_eval,
        supervisor_activity=supervisor_activity,
        incidents=incident,
        report_focus_targets=report_focus_targets,
    )
    report_views = facade._build_report_views(
        day=target_day,
        trade_summary=trade_summary,
        monitor_eval=monitor_eval,
        scanner_eval=scanner_eval,
        supervisor_activity=supervisor_activity,
        incidents=incident,
        improvement_suggestions=improvement_suggestions,
    )
    return {
        "strategy_eff": strategy_eff,
        "report_focus_targets": report_focus_targets,
        "overtrading": overtrading,
        "incident": incident,
        "market_context": market_context,
        "strategy_frame_summary": strategy_frame_summary,
        "decision_chains": decision_chains,
        "decision_trace_chain_summary": decision_trace_chain_summary,
        "trade_summary": trade_summary,
        "strategist_eval": strategist_eval,
        "scanner_eval": scanner_eval,
        "monitor_eval": monitor_eval,
        "supervisor_activity": supervisor_activity,
        "improvement_suggestions": improvement_suggestions,
        "report_views": report_views,
    }


def build_daily_operator_report(
    *,
    op_obj: Dict[str, Any],
    market_context: Dict[str, Any],
    incident: Dict[str, Any],
    facade: Any,
) -> Dict[str, Any]:
    trading_activity = (
        op_obj.get("trading_activity_summary") if isinstance(op_obj.get("trading_activity_summary"), dict) else {}
    )
    return {
        "market_context": market_context,
        "trades_executed": facade._safe_int(trading_activity.get("executions_total"), 0),
        "trades_blocked": facade._safe_int(trading_activity.get("blocked_total"), 0),
        "major_decisions": list((trading_activity.get("strategy_counts") or {}).keys())[:5]
        if isinstance(trading_activity.get("strategy_counts"), dict)
        else [],
        "anomalies": [i.get("type") for i in (incident.get("incidents") or []) if isinstance(i, dict)],
    }


def build_base_report(
    *,
    target_day: str,
    trade_summary: Dict[str, Any],
    decision_chains: Dict[str, Any],
    decision_trace_chain_summary: Dict[str, Any],
    trade_decision: Dict[str, Any],
    strategy_frame_summary: Dict[str, Any],
    strategist_eval: Dict[str, Any],
    scanner_eval: Dict[str, Any],
    monitor_eval: Dict[str, Any],
    supervisor_activity: Dict[str, Any],
    intent_flow: Dict[str, Any],
    strategy_eff: Dict[str, Any],
    overtrading: Dict[str, Any],
    daily_operator: Dict[str, Any],
    incident: Dict[str, Any],
    improvement_suggestions: List[str],
    report_views: Dict[str, Any],
    market_context: Dict[str, Any],
    report_focus_targets: List[str],
    trade_js: Any,
    trade_md: Any,
    op_js: Any,
    op_md: Any,
    generate_decision_story: bool,
    generate_run_cards: bool,
    ds_md: Any,
    rc_md: Any,
    path_exists: Callable[[Any], bool],
    ds_obj: Dict[str, Any],
    rc_obj: Dict[str, Any],
    js_path: Any,
    md_path: Any,
    facade: Any,
) -> Dict[str, Any]:
    """Return the pre-AI report dict (key order is the serialized contract) plus its evidence catalog.

    ``path_exists`` is the caller-injected existence check for the decision-story/run-card files; it is
    evaluated at the same point (and short-circuited the same way) as in the original dict literal.
    """
    out: Dict[str, Any] = {
        "schema_version": "reporter_analysis.v1",
        "day": target_day,
        "trade_summary": trade_summary,
        "decision_chains": decision_chains,
        "decision_trace_chain_summary": decision_trace_chain_summary,
        "trade_decision_summaries": trade_decision,
        "strategy_frame_summary": strategy_frame_summary,
        "strategist_evaluation": strategist_eval,
        "scanner_evaluation": scanner_eval,
        "monitor_evaluation": monitor_eval,
        "supervisor_activity": supervisor_activity,
        "intent_flow_analysis": intent_flow,
        "strategy_effectiveness": strategy_eff,
        "overtrading_diagnostics": overtrading,
        "daily_operator_report": daily_operator,
        "incident_postmortem": incident,
        "incidents": incident,
        "improvement_suggestions": improvement_suggestions,
        "operator_facing_summary": report_views.get("operator_facing_summary", {}),
        "developer_facing_summary": report_views.get("developer_facing_summary", {}),
        "market_context": market_context,
        "report_focus_targets": list(report_focus_targets),
        "source_reports": {
            "trade_explain_json": str(trade_js),
            "trade_explain_md": str(trade_md),
            "operator_summary_json": str(op_js),
            "operator_summary_md": str(op_md),
            "decision_story_enabled": bool(generate_decision_story),
            "run_cards_enabled": bool(generate_run_cards),
            "decision_story_md": str(ds_md) if bool(generate_decision_story) and path_exists(ds_md) else "",
            "run_cards_md": str(rc_md) if bool(generate_run_cards) and path_exists(rc_md) else "",
            "decision_story_total": int(ds_obj.get("story_total") or 0),
            "run_card_total": int(rc_obj.get("card_total") or 0),
        },
        "report_json_path": str(js_path),
        "report_md_path": str(md_path),
    }
    out["ai_evidence_catalog"] = facade._build_ai_evidence_catalog(out)
    return out


def ai_review_error_payload(exc: BaseException, *, enabled: Any, model: Any) -> Dict[str, Any]:
    """Degraded AI-review payload used when the review call raises."""
    return {
        "enabled": bool(enabled),
        "status": "error",
        "reason": f"ai_review_exception:{exc}",
        "model": str(model or ""),
        "ai_summary": "",
        "ai_findings": [],
        "ai_root_causes": [],
        "ai_improvement_suggestions": [],
        "ai_run_grade": "N/A",
        "ai_agent_evaluations": {},
    }


def apply_ai_review_projection(out: Dict[str, Any], ai_review: Any, *, facade: Any) -> Dict[str, Any]:
    """Normalize ``ai_review`` and project it plus hydrated evidence links into ``out`` (in place, same key order)."""
    ai_review = facade._ensure_min_ai_review_payload(out=out, ai_review=dict(ai_review or {}))
    out["ai_review"] = dict(ai_review)
    out["ai_summary"] = str(ai_review.get("ai_summary") or "")
    out["ai_findings"] = list(ai_review.get("ai_findings") or [])
    out["ai_root_causes"] = list(ai_review.get("ai_root_causes") or [])
    out["ai_improvement_suggestions"] = list(ai_review.get("ai_improvement_suggestions") or [])
    out["ai_run_grade"] = str(ai_review.get("ai_run_grade") or "N/A")
    out["ai_agent_evaluations"] = dict(ai_review.get("ai_agent_evaluations") or {})
    out["ai_evidence_links"] = dict(ai_review.get("ai_evidence_links") or {})
    out["ai_findings_detailed"] = facade._hydrate_ai_evidence_details(
        out["ai_findings"],
        (out.get("ai_evidence_links") or {}).get("findings"),
        out["ai_evidence_catalog"],
    )
    out["ai_root_causes_detailed"] = facade._hydrate_ai_evidence_details(
        out["ai_root_causes"],
        (out.get("ai_evidence_links") or {}).get("root_causes"),
        out["ai_evidence_catalog"],
    )
    out["ai_improvement_suggestions_detailed"] = facade._hydrate_ai_evidence_details(
        out["ai_improvement_suggestions"],
        (out.get("ai_evidence_links") or {}).get("improvements"),
        out["ai_evidence_catalog"],
    )
    return out
