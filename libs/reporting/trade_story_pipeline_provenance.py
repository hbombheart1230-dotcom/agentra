from __future__ import annotations

from typing import Any, Dict, List

from libs.reporting.trade_story_evidence import derive_evidence_provenance as _derive_evidence_provenance


def _source_confidence_label(source: Any) -> str:
    raw = str(source or "").strip().lower()
    if raw in {"canonical", "normalized_trade_artifact", "normalized_trade"}:
        return "high"
    if raw in {"direct_artifact", "direct"}:
        return "medium"
    if raw in {"event_log", "fallback", "inferred"}:
        return "low"
    return "low"


def _is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def compute_evidence_completeness(story_input: Dict[str, Any]) -> Dict[str, Any]:
    obj = dict(story_input or {})
    required_sections = [
        "market_context_human",
        "scanner_reason_human",
        "filters_human",
        "monitor_reason_human",
        "guard_reason_human",
        "execution_outcome_human",
        "operator_conclusion_human",
    ]
    present_sections: List[str] = []
    missing_sections: List[str] = []
    for key in required_sections:
        value = obj.get(key)
        if isinstance(value, dict) and (_is_present(value.get("summary")) or _is_present(value.get("bullets"))):
            present_sections.append(key)
        elif _is_present(value):
            present_sections.append(key)
        else:
            missing_sections.append(key)
    score = float(len(present_sections)) / float(len(required_sections)) if required_sections else 1.0
    return {
        "required_sections": required_sections,
        "present_sections": present_sections,
        "missing_sections": missing_sections,
        "completeness_score": score,
    }


def _safe_path_text(value: Any) -> str:
    return str(value or "").strip()


def _safe_ref_map(values: Any) -> Dict[str, str]:
    if not isinstance(values, dict):
        return {}
    out: Dict[str, str] = {}
    for key, value in values.items():
        out[str(key)] = _safe_path_text(value)
    return out


def _resolve_commander_source_ref(refs: Dict[str, Any], section_provenance: Dict[str, Any]) -> str:
    ref_map = _safe_ref_map(refs)
    section_map = dict(section_provenance or {})
    return str(
        ref_map.get("canonical_commander_json")
        or ref_map.get("canonical_commander")
        or (section_map.get("market_context_human") or {}).get("artifact_path")
        or (section_map.get("operator_conclusion_human") or {}).get("artifact_path")
        or ""
    )


def _commander_reasoning_flag(source: Dict[str, Any], commander_summary: Dict[str, Any], key: str) -> bool:
    summary_obj = dict(commander_summary or {})
    if key in summary_obj and isinstance(summary_obj.get(key), bool):
        return bool(summary_obj.get(key))
    latest_provenance = source.get("latest_reasoning_trace_provenance")
    if isinstance(latest_provenance, dict) and key in latest_provenance and isinstance(latest_provenance.get(key), bool):
        return bool(latest_provenance.get(key))
    commander_obj = source.get("commander")
    if isinstance(commander_obj, dict) and key in commander_obj and isinstance(commander_obj.get(key), bool):
        return bool(commander_obj.get(key))
    return False


def _commander_reasoning_source_priority(source: Dict[str, Any], commander_summary: Dict[str, Any]) -> List[str]:
    summary_obj = dict(commander_summary or {})
    latest_provenance = source.get("latest_reasoning_trace_provenance") if isinstance(source.get("latest_reasoning_trace_provenance"), dict) else {}
    commander_obj = source.get("commander") if isinstance(source.get("commander"), dict) else {}
    for candidate in (latest_provenance, commander_obj, summary_obj):
        values = [str(x or "").strip() for x in list(candidate.get("source_priority") or []) if str(x or "").strip()]
        if values:
            return values
    return []


def build_commander_evidence(commander_payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(commander_payload or {})
    return {
        "schema_version": "commander_evidence.v1",
        "session_type": str(payload.get("session_type") or ""),
        "market_regime_summary": str(payload.get("market_regime_summary") or ""),
        "goal": str(payload.get("goal") or ""),
        "decision_path": str(payload.get("final_runtime_path") or payload.get("path") or ""),
        "invocation_plan": [str(x or "") for x in list(payload.get("agent_invocation_plan") or []) if str(x or "").strip()],
        "final_reason": str(payload.get("final_reason") or payload.get("reason") or ""),
    }


def _section_source_entry(
    *,
    source: str,
    artifact_path: str = "",
) -> Dict[str, str]:
    return {
        "source": str(source or "fallback"),
        "artifact_path": str(artifact_path or ""),
        "confidence": _source_confidence_label(source),
    }


def build_section_provenance(bundle_out: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    artifacts = bundle_out.get("artifacts") if isinstance(bundle_out.get("artifacts"), dict) else {}
    evidence_provenance = _derive_evidence_provenance(bundle_out)

    def _agent_source(agent: str) -> str:
        return str(evidence_provenance.get(agent) or "fallback").strip().lower()

    def _agent_path(agent: str) -> str:
        canonical_key = f"canonical_{agent}_json"
        canonical_path = str(artifacts.get(canonical_key) or "").strip()
        if canonical_path:
            return canonical_path
        if agent == "reporter":
            return str(artifacts.get("reporter_analysis_json") or "").strip()
        return str(artifacts.get("agent_pipeline_trace_json") or "").strip()

    strategist_entry = _section_source_entry(
        source=_agent_source("strategist"),
        artifact_path=_agent_path("strategist"),
    )
    scanner_entry = _section_source_entry(
        source=_agent_source("scanner"),
        artifact_path=_agent_path("scanner"),
    )
    monitor_entry = _section_source_entry(
        source=_agent_source("monitor"),
        artifact_path=_agent_path("monitor"),
    )
    supervisor_entry = _section_source_entry(
        source=_agent_source("supervisor"),
        artifact_path=_agent_path("supervisor"),
    )
    executor_entry = _section_source_entry(
        source=_agent_source("executor"),
        artifact_path=_agent_path("executor"),
    )
    reporter_entry = _section_source_entry(
        source=_agent_source("reporter"),
        artifact_path=_agent_path("reporter"),
    )
    commander_entry = _section_source_entry(
        source=_agent_source("commander"),
        artifact_path=_agent_path("commander"),
    )
    return {
        "market_context_human": strategist_entry,
        "scanner_reason_human": scanner_entry,
        "filters_human": scanner_entry,
        "monitor_reason_human": monitor_entry,
        "guard_reason_human": supervisor_entry,
        "execution_outcome_human": executor_entry,
        "reporter_status_human": reporter_entry,
        "operator_conclusion_human": commander_entry,
        "timeline": commander_entry,
    }


def _section_seed_provenance_entry(section_provenance: Dict[str, Any], key: str) -> Dict[str, str]:
    entry = section_provenance.get(key) if isinstance(section_provenance.get(key), dict) else {}
    return {
        "source": str(entry.get("source") or "fallback"),
        "artifact_path": str(entry.get("artifact_path") or ""),
        "confidence": str(entry.get("confidence") or _source_confidence_label(entry.get("source"))),
    }


def build_report_section_provenance_seeds(section_provenance: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    provenance = dict(section_provenance or {})
    return {
        "market_context_at_entry": _section_seed_provenance_entry(provenance, "market_context_human"),
        "strategist_summary": _section_seed_provenance_entry(provenance, "market_context_human"),
        "why_this_symbol_was_chosen": _section_seed_provenance_entry(provenance, "scanner_reason_human"),
        "entry_decision": _section_seed_provenance_entry(provenance, "scanner_reason_human"),
        "holding_monitoring_story": _section_seed_provenance_entry(provenance, "monitor_reason_human"),
        "exit_decision": _section_seed_provenance_entry(provenance, "execution_outcome_human"),
        "scanner_filters": _section_seed_provenance_entry(provenance, "filters_human"),
        "execution_quality": _section_seed_provenance_entry(provenance, "execution_outcome_human"),
        "guard_approval_result": _section_seed_provenance_entry(provenance, "guard_reason_human"),
        "reporter_evaluation": _section_seed_provenance_entry(provenance, "reporter_status_human"),
        "final_operator_conclusion": _section_seed_provenance_entry(provenance, "operator_conclusion_human"),
    }
