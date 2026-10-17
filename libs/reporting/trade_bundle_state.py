from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Optional

from libs.reporting.trade_execution_truth_merge import merge_preferred_execution_details
from libs.reporting.trade_story_pipeline import build_lifecycle_bundle, safe_int
from libs.reporting.trade_symbol_context import normalize_trade_payload_symbol_context
import sys as _r3_sys
from libs.agents.reporter.read_models.bundle_state_bodies_01 import (  # R-4 owner bodies (facade-injected)
    _safe_float_r4_impl,
    _first_positive_r4_impl,
    _exit_monitor_reference_price_r4_impl,
    _backfill_execution_fields_r4_impl,
    build_component_fingerprint_r4_impl,
    build_ai_trade_report_generation_component_r4_impl,
    build_operator_brief_generation_component_r4_impl,
    build_generation_state_r4_impl,
    _source_type_r4_impl,
    build_bundle_provenance_r4_impl,
    build_bundle_health_r4_impl,
    finalize_bundle_health_r4_impl,
    build_trade_bundle_state_r4_impl,
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_float(value: Any) -> Optional[float]:
    return _safe_float_r4_impl(value, facade=_r3_sys.modules[__name__])


def _first_positive(*values: Any) -> Optional[float]:
    return _first_positive_r4_impl(*values, facade=_r3_sys.modules[__name__])


def _exit_monitor_reference_price(payload: Mapping[str, Any], execution_details: Mapping[str, Any]) -> Optional[float]:
    return _exit_monitor_reference_price_r4_impl(payload, execution_details, facade=_r3_sys.modules[__name__])


def stable_json_text(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def payload_fingerprint(payload: Any) -> str:
    import hashlib

    return hashlib.sha256(stable_json_text(payload).encode("utf-8")).hexdigest()


def _backfill_execution_fields(payload: Dict[str, Any], execution_details: Mapping[str, Any]) -> Dict[str, Any]:
    return _backfill_execution_fields_r4_impl(payload, execution_details, facade=_r3_sys.modules[__name__])


_AI_REPORT_FINGERPRINT_IGNORED_STORY_KEYS = {
    "ai_report_diagnostics",
    "evidence_provenance",
    "evidence_recovery_used",
    "lifecycle_completeness",
    "reasoning_provenance",
    "recovery_sources",
    "section_provenance",
}


def _normalize_story_input_for_fingerprint(payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    out = dict(payload or {})
    for key in _AI_REPORT_FINGERPRINT_IGNORED_STORY_KEYS:
        out.pop(key, None)
    return out


def build_component_fingerprint(
    *,
    component: str,
    trade_id: str,
    run_id: str,
    lifecycle_status: str,
    story_type: str,
    model: str,
    story_input: Mapping[str, Any] | None,
    compact_input: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    return build_component_fingerprint_r4_impl(component=component, trade_id=trade_id, run_id=run_id, lifecycle_status=lifecycle_status, story_type=story_type, model=model, story_input=story_input, compact_input=compact_input, facade=_r3_sys.modules[__name__])


def build_ai_trade_report_generation_component(
    *,
    fingerprint: str,
    trade_id: str,
    run_id: str,
    status: str,
    report_status: str,
    report_generation_reason: str,
    model: str,
    report_json_path: str,
    report_md_path: str,
    llm_response_path: str,
    source_inputs: Mapping[str, Any] | None = None,
    updated_at: str = "",
) -> Dict[str, Any]:
    return build_ai_trade_report_generation_component_r4_impl(fingerprint=fingerprint, trade_id=trade_id, run_id=run_id, status=status, report_status=report_status, report_generation_reason=report_generation_reason, model=model, report_json_path=report_json_path, report_md_path=report_md_path, llm_response_path=llm_response_path, source_inputs=source_inputs, updated_at=updated_at, facade=_r3_sys.modules[__name__])


def build_operator_brief_generation_component(
    *,
    trade_id: str,
    run_id: str,
    llm_brief_status: str,
    report_json_path: str,
    report_md_path: str,
    llm_response_path: str,
    brief_json_exists: bool,
    brief_md_exists: bool,
    brief_llm_exists: bool,
    updated_at: str = "",
) -> Dict[str, Any]:
    return build_operator_brief_generation_component_r4_impl(trade_id=trade_id, run_id=run_id, llm_brief_status=llm_brief_status, report_json_path=report_json_path, report_md_path=report_md_path, llm_response_path=llm_response_path, brief_json_exists=brief_json_exists, brief_md_exists=brief_md_exists, brief_llm_exists=brief_llm_exists, updated_at=updated_at, facade=_r3_sys.modules[__name__])


def build_generation_state(
    *,
    current_state: Mapping[str, Any] | None,
    ai_trade_report_component: Mapping[str, Any],
    operator_brief_component: Mapping[str, Any],
) -> Dict[str, Any]:
    return build_generation_state_r4_impl(current_state=current_state, ai_trade_report_component=ai_trade_report_component, operator_brief_component=operator_brief_component, facade=_r3_sys.modules[__name__])


def _source_type(raw_source: Any, source_path: Any) -> str:
    return _source_type_r4_impl(raw_source, source_path, facade=_r3_sys.modules[__name__])


def build_bundle_provenance(
    *,
    trade_id: str,
    run_id: str,
    day: str,
    lifecycle_status: str,
    recovery_metadata: Mapping[str, Any] | None,
    strategy_anchor_run_id: str,
    evidence_source: str,
    agent_sources: Mapping[str, Any] | None,
    section_provenance: Mapping[str, Any] | None,
    artifacts: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    return build_bundle_provenance_r4_impl(trade_id=trade_id, run_id=run_id, day=day, lifecycle_status=lifecycle_status, recovery_metadata=recovery_metadata, strategy_anchor_run_id=strategy_anchor_run_id, evidence_source=evidence_source, agent_sources=agent_sources, section_provenance=section_provenance, artifacts=artifacts, facade=_r3_sys.modules[__name__])


def build_bundle_health(
    *,
    trade_id: str,
    run_id: str,
    day: str,
    lifecycle_status: str,
    recovery_metadata: Mapping[str, Any] | None,
    diagnostics: Mapping[str, Any] | None,
    report_generation: Mapping[str, Any] | None,
    evidence_completeness_missing_sections: Iterable[str] | None,
    phase3_missing_sections: Iterable[str] | None,
    phase3_completeness_score: float,
    artifact_presence: Mapping[str, Any] | None,
    ai_trade_report_llm_artifact: Mapping[str, Any] | None,
    strategist_event_count: int,
    scanner_event_count: int,
    monitor_event_count: int,
    operator_brief_json_exists: bool,
) -> Dict[str, Any]:
    return build_bundle_health_r4_impl(trade_id=trade_id, run_id=run_id, day=day, lifecycle_status=lifecycle_status, recovery_metadata=recovery_metadata, diagnostics=diagnostics, report_generation=report_generation, evidence_completeness_missing_sections=evidence_completeness_missing_sections, phase3_missing_sections=phase3_missing_sections, phase3_completeness_score=phase3_completeness_score, artifact_presence=artifact_presence, ai_trade_report_llm_artifact=ai_trade_report_llm_artifact, strategist_event_count=strategist_event_count, scanner_event_count=scanner_event_count, monitor_event_count=monitor_event_count, operator_brief_json_exists=operator_brief_json_exists, facade=_r3_sys.modules[__name__])


def finalize_bundle_health(
    health_payload: MutableMapping[str, Any],
    *,
    artifact_presence: Mapping[str, Any] | None,
    diagnostics: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    return finalize_bundle_health_r4_impl(health_payload, artifact_presence=artifact_presence, diagnostics=diagnostics, facade=_r3_sys.modules[__name__])


def build_trade_bundle_state(
    *,
    provenance_kwargs: Mapping[str, Any],
    health_kwargs: Mapping[str, Any],
) -> Dict[str, Any]:
    return build_trade_bundle_state_r4_impl(provenance_kwargs=provenance_kwargs, health_kwargs=health_kwargs, facade=_r3_sys.modules[__name__])


def build_live_trade_bundle_payloads(
    *,
    day: str,
    trade_id: str,
    run_id: str,
    symbol: str,
    status: str,
    lifecycle: Mapping[str, Any] | None,
    lifecycle_bundle: Mapping[str, Any] | None,
    story_input: Mapping[str, Any] | None,
    summary_obj: Mapping[str, Any] | None,
    diagnostics: Mapping[str, Any] | None,
    recovery_metadata: Mapping[str, Any] | None,
    story_contract: Mapping[str, Any] | None,
    anchor_execution: Mapping[str, Any] | None,
    linked_run_ids: Iterable[str] | None,
    same_day_reporter_linkage: Mapping[str, Any] | None,
    failure_classification: Mapping[str, Any] | None,
    execution_details: Mapping[str, Any] | None,
    entry_execution_details: Mapping[str, Any] | None,
    exit_execution_details: Mapping[str, Any] | None,
    holding_phase_observability: Mapping[str, Any] | None,
    strategist_llm_artifact: Mapping[str, Any] | None,
    existing_brief_llm_artifact: Mapping[str, Any] | None,
    ai_trade_report_llm_artifact: Mapping[str, Any] | None,
    trade_report: Mapping[str, Any] | None,
    evidence_completeness_missing_sections: Iterable[str] | None,
    phase3_missing_sections: Iterable[str] | None,
    phase3_completeness_score: float,
    strategist_event_count: int,
    scanner_event_count: int,
    monitor_event_count: int,
    operator_brief_json_exists: bool,
    lifecycle_bundle_path: Path,
    entry_artifact_path: Path,
    hold_artifact_path: Path,
    exit_artifact_path: Path,
    story_input_path: Path,
    story_compact_input_path: Path,
    trade_report_json_path: Path,
    trade_report_md_path: Path,
    strategist_evidence_path: Path,
    scanner_evidence_path: Path,
    monitor_evidence_path: Path,
    commander_evidence_path: Path,
    strategist_llm_response_path: Path,
    ai_trade_report_llm_response_path: Path,
    brief_llm_response_path: Path,
    operator_brief_json_path: Path,
    operator_brief_md_path: Path,
    trade_provenance_path: Path,
    trade_health_path: Path,
    trade_artifact_links_path: Path,
    resolved_operator_brief_json: str,
    resolved_operator_brief_md: str,
    resolved_brief_llm_response_json: str,
    trade_report_json_written: str,
    trade_report_md_written: str,
    ai_trade_report_llm_response_written: str,
) -> Dict[str, Any]:
    lifecycle_obj = dict(lifecycle or {})
    lifecycle_bundle_obj = dict(lifecycle_bundle or {})
    story_input_obj = dict(story_input or {})
    summary_obj = dict(summary_obj or {})
    diagnostics_obj = dict(diagnostics or {})
    recovery_metadata = dict(recovery_metadata or {})
    same_day_reporter_linkage = dict(same_day_reporter_linkage or {})
    failure_classification = dict(failure_classification or {})
    execution_details = dict(execution_details or {})
    entry_execution_details = dict(entry_execution_details or {})
    exit_execution_details = dict(exit_execution_details or {})
    holding_phase_observability = dict(holding_phase_observability or {})
    strategist_llm_artifact = dict(strategist_llm_artifact or {})
    existing_brief_llm_artifact = dict(existing_brief_llm_artifact or {})
    ai_trade_report_llm_artifact = dict(ai_trade_report_llm_artifact or {})
    trade_report = dict(trade_report or {})

    entry_payload = dict(lifecycle_obj.get("entry") or {})
    holding_payload = dict(lifecycle_obj.get("holding") or {})
    exit_payload = dict(lifecycle_obj.get("exit") or {})
    entry_payload["execution_details"] = merge_preferred_execution_details(
        entry_payload.get("execution_details"),
        entry_execution_details,
    )
    entry_payload = _backfill_execution_fields(entry_payload, entry_payload.get("execution_details") or {})
    entry_payload = normalize_trade_payload_symbol_context(entry_payload, executed_symbol=symbol)
    holding_payload.setdefault("hold_duration", holding_phase_observability.get("hold_duration"))
    holding_payload.setdefault("hold_duration_sec", holding_phase_observability.get("hold_duration_sec"))
    holding_payload.setdefault("holding_phase_summary", holding_phase_observability.get("holding_phase_summary"))
    holding_payload.setdefault("hold_events_count", holding_phase_observability.get("hold_events_count"))
    holding_payload.setdefault(
        "monitor_context_snapshots",
        list(holding_phase_observability.get("monitor_context_snapshots") or []),
    )
    holding_payload.setdefault(
        "hold_signal_transitions",
        list(holding_phase_observability.get("hold_signal_transitions") or []),
    )
    holding_payload.setdefault(
        "pre_exit_context_summary",
        dict(holding_phase_observability.get("pre_exit_context_summary") or {}),
    )
    holding_payload.setdefault(
        "deterioration_signals",
        list(holding_phase_observability.get("deterioration_signals") or []),
    )
    holding_payload.setdefault(
        "hold_evidence_thin",
        bool(holding_phase_observability.get("hold_evidence_thin")),
    )
    exit_payload["execution_details"] = merge_preferred_execution_details(
        exit_payload.get("execution_details"),
        exit_execution_details,
    )
    exit_payload = _backfill_execution_fields(exit_payload, exit_payload.get("execution_details") or {})
    exit_payload = normalize_trade_payload_symbol_context(exit_payload, executed_symbol=symbol)

    normalized_lifecycle = dict(lifecycle_obj)
    normalized_lifecycle["entry"] = dict(entry_payload)
    normalized_lifecycle["holding"] = dict(holding_payload)
    normalized_lifecycle["exit"] = dict(exit_payload)
    normalized_lifecycle["summary"] = dict(summary_obj)
    normalized_lifecycle["execution_details"] = merge_preferred_execution_details(
        normalized_lifecycle.get("execution_details"),
        execution_details,
    )
    normalized_lifecycle["same_day_reporter_linkage"] = dict(same_day_reporter_linkage)
    normalized_lifecycle["failure_classification"] = dict(failure_classification)
    normalized_lifecycle["run_ids_all"] = [str(x or "") for x in list(linked_run_ids or []) if str(x or "").strip()]

    lifecycle_bundle_payload = build_lifecycle_bundle(
        day=day,
        trade_id=trade_id,
        run_id=str(run_id or ""),
        symbol=symbol,
        lifecycle=normalized_lifecycle,
        strategist_summary=dict(lifecycle_bundle_obj.get("strategist") or {}),
        scanner_summary=dict(lifecycle_bundle_obj.get("scanner") or {}),
        monitor_summary=dict(lifecycle_bundle_obj.get("monitor") or {}),
        commander_summary=dict(lifecycle_bundle_obj.get("commander") or {}),
        story_input=story_input_obj,
        diagnostics={
            **diagnostics_obj,
            "strategist_llm_status": str(
                strategist_llm_artifact.get("llm_status") or strategist_llm_artifact.get("status") or "skipped"
            ),
        },
        canonical_refs={
            key: value
            for key, value in dict(lifecycle_bundle_obj.get("artifacts") or {}).items()
            if str(key).startswith("canonical_") and str(key).endswith("_json")
        },
        llm_refs={
            "strategist_prompt_ref": str(strategist_llm_artifact.get("prompt_ref") or ""),
            "strategist_response_ref": str(strategist_llm_artifact.get("response_ref") or ""),
            "brief_prompt_ref": str(existing_brief_llm_artifact.get("prompt_ref") or ""),
            "brief_response_ref": str(existing_brief_llm_artifact.get("response_ref") or ""),
            "ai_trade_report_prompt_ref": str(ai_trade_report_llm_artifact.get("prompt_ref") or ""),
            "ai_trade_report_response_ref": str(ai_trade_report_llm_artifact.get("response_ref") or ""),
        },
        artifact_links={
            "lifecycle_bundle": str(lifecycle_bundle_path),
            "entry": str(entry_artifact_path),
            "hold": str(hold_artifact_path),
            "exit": str(exit_artifact_path),
            "operator_brief": str(resolved_operator_brief_json or ""),
            "ai_trade_report": str(trade_report_json_written or trade_report_json_path),
        },
    )
    lifecycle_bundle_payload.update(
        {
            "ts": str(lifecycle_bundle_obj.get("ts") or _utc_now_iso()),
            "story_id": trade_id,
            "linked_run_ids": [str(x or "") for x in list(linked_run_ids or []) if str(x or "").strip()],
            "trade_lifecycle_status": status,
            "trade_origin": str(recovery_metadata.get("trade_origin") or ""),
            "lifecycle_completeness": str(recovery_metadata.get("lifecycle_completeness") or ""),
            "evidence_recovery_used": bool(recovery_metadata.get("evidence_recovery_used")),
            "recovery_missing_sections": list(recovery_metadata.get("recovery_missing_sections") or []),
            "recovery_sources": list(recovery_metadata.get("recovery_sources") or []),
            "trade_lifecycle_summary": str(summary_obj.get("lifecycle_summary_human") or ""),
            "strategist": dict(lifecycle_bundle_obj.get("strategist") or {}),
            "scanner": dict(lifecycle_bundle_obj.get("scanner") or {}),
            "monitor": dict(lifecycle_bundle_obj.get("monitor") or {}),
            "commander": dict(lifecycle_bundle_obj.get("commander") or {}),
            "market_context_human": dict(
                story_input_obj.get("market_context_human")
                or lifecycle_bundle_obj.get("market_context_human")
                or {}
            ),
            "scanner_reason_human": dict(
                story_input_obj.get("scanner_reason_human")
                or lifecycle_bundle_obj.get("scanner_reason_human")
                or {}
            ),
            "monitor_reason_human": dict(
                story_input_obj.get("monitor_reason_human")
                or lifecycle_bundle_obj.get("monitor_reason_human")
                or {}
            ),
            "reporter_status_human": dict(
                story_input_obj.get("reporter_status_human")
                or lifecycle_bundle_obj.get("reporter_status_human")
                or {}
            ),
            "strategist_evidence": dict(story_input_obj.get("strategist_evidence") or {}),
            "strategist_candidate_hints": list(story_input_obj.get("strategist_candidate_hints") or []),
            "strategist_market_headlines": list(story_input_obj.get("strategist_market_headlines") or []),
            "strategist_symbol_headlines": list(story_input_obj.get("strategist_symbol_headlines") or []),
            "strategist_trace_summary": dict(story_input_obj.get("strategist_trace_summary") or {}),
            "scanner_trace_summary": dict(story_input_obj.get("scanner_trace_summary") or {}),
            "selected_symbol": str(story_input_obj.get("selected_symbol") or lifecycle_bundle_obj.get("symbol") or ""),
            "runner_up_symbol": str(story_input_obj.get("runner_up_symbol") or ""),
            "candidate_count": safe_int(story_input_obj.get("candidate_count"), 0),
            "story_contract": dict(story_contract or {}),
            "execution": dict(anchor_execution or {}),
            "artifacts": dict(lifecycle_bundle_obj.get("artifacts") or {}),
            "evidence_provenance": dict(lifecycle_bundle_obj.get("evidence_provenance") or {}),
            "section_provenance": dict(story_input_obj.get("section_provenance") or {}),
            "ai_report_diagnostics": dict(diagnostics_obj),
            "same_day_reporter_linkage": dict(same_day_reporter_linkage),
            "failure_classification": dict(failure_classification),
            "execution_details": dict(execution_details),
            "entry_execution_details": dict(entry_execution_details),
            "exit_execution_details": dict(exit_execution_details),
            "hold_duration": holding_phase_observability.get("hold_duration"),
            "hold_duration_sec": holding_phase_observability.get("hold_duration_sec"),
            "holding_phase_summary": holding_phase_observability.get("holding_phase_summary"),
            "hold_events_count": holding_phase_observability.get("hold_events_count"),
            "monitor_context_snapshots": list(holding_phase_observability.get("monitor_context_snapshots") or []),
            "hold_signal_transitions": list(holding_phase_observability.get("hold_signal_transitions") or []),
            "pre_exit_context_summary": dict(holding_phase_observability.get("pre_exit_context_summary") or {}),
            "timeline": list(normalized_lifecycle.get("timeline") or []),
            "lifecycle_attach_debug": [
                dict(row)
                for row in list(lifecycle_obj.get("lifecycle_attach_debug") or [])
                if isinstance(row, dict)
            ],
            "strategist_llm_status": str(
                (
                    (lifecycle_bundle_payload.get("llm_summary") or {})
                    if isinstance(lifecycle_bundle_payload.get("llm_summary"), dict)
                    else {}
                ).get("strategist_llm_status")
                or diagnostics_obj.get("strategist_llm_status")
                or "skipped"
            ),
            "brief_llm_status": str(
                (
                    (lifecycle_bundle_payload.get("llm_summary") or {})
                    if isinstance(lifecycle_bundle_payload.get("llm_summary"), dict)
                    else {}
                ).get("brief_llm_status")
                or diagnostics_obj.get("llm_brief_status")
                or "skipped"
            ),
            "ai_trade_report_status": str(
                (
                    (lifecycle_bundle_payload.get("llm_summary") or {})
                    if isinstance(lifecycle_bundle_payload.get("llm_summary"), dict)
                    else {}
                ).get("ai_report_status")
                or diagnostics_obj.get("ai_trade_report_status")
                or "skipped"
            ),
            "operator_brief": str(resolved_operator_brief_json or ""),
            "ai_trade_report": str(trade_report_json_written or trade_report_json_path),
            "lifecycle_bundle": str(lifecycle_bundle_path),
        }
    )

    artifact_presence = {
        "lifecycle_bundle_json": lifecycle_bundle_path.exists(),
        "entry_json": entry_artifact_path.exists(),
        "hold_json": hold_artifact_path.exists(),
        "exit_json": exit_artifact_path.exists(),
        "ai_trade_report_input_json": story_input_path.exists(),
        "ai_trade_report_compact_input_json": story_compact_input_path.exists(),
        "ai_trade_report_json": bool(trade_report_json_written),
        "ai_trade_report_md": bool(trade_report_md_written),
        "strategist_evidence_json": strategist_evidence_path.exists(),
        "scanner_evidence_json": scanner_evidence_path.exists(),
        "monitor_evidence_json": monitor_evidence_path.exists(),
        "commander_evidence_json": commander_evidence_path.exists(),
        "strategist_llm_response_json": strategist_llm_response_path.exists(),
        "ai_trade_report_llm_response_json": bool(ai_trade_report_llm_response_written),
        "brief_llm_response_json": brief_llm_response_path.exists(),
    }
    state_payloads = build_trade_bundle_state(
        provenance_kwargs={
            "trade_id": trade_id,
            "run_id": str(run_id or ""),
            "day": day,
            "lifecycle_status": status,
            "recovery_metadata": recovery_metadata,
            "strategy_anchor_run_id": str(story_input_obj.get("strategy_anchor_run_id") or ""),
            "evidence_source": str(story_input_obj.get("evidence_source") or "fallback"),
            "agent_sources": dict(lifecycle_bundle_obj.get("evidence_provenance") or {}),
            "section_provenance": dict(story_input_obj.get("section_provenance") or {}),
            "artifacts": dict(lifecycle_bundle_obj.get("artifacts") or {}),
        },
        health_kwargs={
            "trade_id": trade_id,
            "run_id": str(run_id or ""),
            "day": day,
            "lifecycle_status": status,
            "recovery_metadata": recovery_metadata,
            "diagnostics": dict(diagnostics_obj),
            "report_generation": dict(trade_report.get("generation") or {}) if isinstance(trade_report, dict) else {},
            "evidence_completeness_missing_sections": list(evidence_completeness_missing_sections or []),
            "phase3_missing_sections": list(phase3_missing_sections or []),
            "phase3_completeness_score": float(phase3_completeness_score or 0.0),
            "artifact_presence": artifact_presence,
            "ai_trade_report_llm_artifact": dict(ai_trade_report_llm_artifact),
            "strategist_event_count": int(strategist_event_count or 0),
            "scanner_event_count": int(scanner_event_count or 0),
            "monitor_event_count": int(monitor_event_count or 0),
            "operator_brief_json_exists": bool(operator_brief_json_exists),
        },
    )

    trade_artifact_links_payload = {
        "schema_version": "trade_artifact_links.v2",
        "trade_id": trade_id,
        "run_id": run_id,
        "day": day,
        "canonical_commander": str((lifecycle_bundle_obj.get("artifacts") or {}).get("canonical_commander_json") or ""),
        "canonical_strategist": str((lifecycle_bundle_obj.get("artifacts") or {}).get("canonical_strategist_json") or ""),
        "canonical_scanner": str((lifecycle_bundle_obj.get("artifacts") or {}).get("canonical_scanner_json") or ""),
        "canonical_monitor": str((lifecycle_bundle_obj.get("artifacts") or {}).get("canonical_monitor_json") or ""),
        "lifecycle_bundle": str(lifecycle_bundle_path),
        "entry": str(entry_artifact_path),
        "hold": str(hold_artifact_path),
        "exit": str(exit_artifact_path),
        "operator_brief": str(resolved_operator_brief_json or ""),
        "ai_trade_report": str(trade_report_json_written or ""),
        "llm_prompt_refs": {
            "strategist": str(strategist_llm_artifact.get("prompt_ref") or ""),
            "brief": str(existing_brief_llm_artifact.get("prompt_ref") or ""),
            "ai_trade_report": str(ai_trade_report_llm_artifact.get("prompt_ref") or ""),
        },
        "llm_response_refs": {
            "strategist": str(strategist_llm_artifact.get("response_ref") or ""),
            "brief": str(existing_brief_llm_artifact.get("response_ref") or ""),
            "ai_trade_report": str(ai_trade_report_llm_artifact.get("response_ref") or ""),
        },
        "links": {
            key: str(value or "")
            for key, value in dict(lifecycle_bundle_obj.get("artifacts") or {}).items()
        },
    }
    trade_artifact_links_payload["links"]["brief_json"] = str(resolved_operator_brief_json or "")
    trade_artifact_links_payload["links"]["operator_brief_json"] = str(resolved_operator_brief_json or "")
    trade_artifact_links_payload["links"]["brief_md"] = str(resolved_operator_brief_md or "")
    trade_artifact_links_payload["links"]["brief_llm_response_json"] = str(resolved_brief_llm_response_json or "")
    trade_artifact_links_payload["links"]["strategist_llm_prompt_ref"] = str(strategist_llm_artifact.get("prompt_ref") or "")
    trade_artifact_links_payload["links"]["strategist_llm_response_ref"] = str(strategist_llm_artifact.get("response_ref") or "")
    trade_artifact_links_payload["links"]["strategist_summary_md"] = str(
        strategist_llm_artifact.get("trade_strategist_summary_md_ref")
        or strategist_llm_artifact.get("strategist_summary_md_ref")
        or ""
    )
    trade_artifact_links_payload["links"]["strategist_summary_json"] = str(
        strategist_llm_artifact.get("trade_strategist_summary_json_ref")
        or strategist_llm_artifact.get("strategist_summary_json_ref")
        or ""
    )
    trade_artifact_links_payload["links"]["brief_llm_prompt_ref"] = str(existing_brief_llm_artifact.get("prompt_ref") or "")
    trade_artifact_links_payload["links"]["brief_llm_response_ref"] = str(existing_brief_llm_artifact.get("response_ref") or "")
    trade_artifact_links_payload["links"]["ai_trade_report_llm_prompt_ref"] = str(ai_trade_report_llm_artifact.get("prompt_ref") or "")
    trade_artifact_links_payload["links"]["ai_trade_report_llm_response_ref"] = str(ai_trade_report_llm_artifact.get("response_ref") or "")

    return {
        "entry_payload": entry_payload,
        "holding_payload": holding_payload,
        "exit_payload": exit_payload,
        "normalized_lifecycle": normalized_lifecycle,
        "lifecycle_bundle_payload": lifecycle_bundle_payload,
        "trade_provenance_payload": dict(state_payloads.get("provenance") or {}),
        "trade_health_payload": dict(state_payloads.get("health") or {}),
        "trade_artifact_links_payload": trade_artifact_links_payload,
        "artifact_presence": artifact_presence,
    }


__all__ = [
    "build_ai_trade_report_generation_component",
    "build_bundle_health",
    "build_bundle_provenance",
    "build_component_fingerprint",
    "build_generation_state",
    "build_live_trade_bundle_payloads",
    "build_operator_brief_generation_component",
    "build_trade_bundle_state",
    "finalize_bundle_health",
    "payload_fingerprint",
    "stable_json_text",
]
