from __future__ import annotations

from typing import Any, Dict, Mapping


def build_story_reasoning_provenance(
    bundle_out: Dict[str, Any], *,
    bundle_reasoning_provenance: Dict[str, Any],
    canonical_agent_artifacts: Dict[str, Any], evidence_provenance: Dict[str, Any],
    section_provenance: Dict[str, Any], deps: Mapping[str, Any],
) -> Dict[str, Any]:
    """Canonical/source-preference provenance shared by both story schema paths."""
    _commander_reasoning_flag = deps["_commander_reasoning_flag"]
    _commander_reasoning_source_priority = deps["_commander_reasoning_source_priority"]
    _resolve_commander_source_ref = deps["_resolve_commander_source_ref"]
    build_reasoning_provenance = deps["build_reasoning_provenance"]
    normalize_reasoning_provenance_aliases = deps["normalize_reasoning_provenance_aliases"]
    commander_source_priority = _commander_reasoning_source_priority(bundle_out, dict(bundle_out.get("commander_summary") or {}))
    derived_reasoning_provenance = build_reasoning_provenance(
        commander_context_source="canonical" if canonical_agent_artifacts.get("canonical_commander_json") or canonical_agent_artifacts.get("canonical_commander") else str(evidence_provenance.get("commander") or ""),
        strategist_plan_source=str(
            (section_provenance.get("market_context_human") or {}).get("source")
            or evidence_provenance.get("strategist")
            or ("canonical" if canonical_agent_artifacts.get("canonical_strategist_json") or canonical_agent_artifacts.get("canonical_strategist") else "")
        ),
        scanner_reason_source=str(
            (section_provenance.get("scanner_reason_human") or {}).get("source")
            or evidence_provenance.get("scanner")
            or ("canonical" if canonical_agent_artifacts.get("canonical_scanner_json") or canonical_agent_artifacts.get("canonical_scanner") else "")
        ),
        monitor_reason_source=str(
            (section_provenance.get("monitor_reason_human") or {}).get("source")
            or evidence_provenance.get("monitor")
            or ("canonical" if canonical_agent_artifacts.get("canonical_monitor_json") or canonical_agent_artifacts.get("canonical_monitor") else "")
        ),
        commander_source_ref=_resolve_commander_source_ref(canonical_agent_artifacts, section_provenance),
        strategist_source_ref=str(
            canonical_agent_artifacts.get("canonical_strategist_json")
            or canonical_agent_artifacts.get("canonical_strategist")
            or (section_provenance.get("market_context_human") or {}).get("artifact_path")
            or ""
        ),
        scanner_source_ref=str(
            canonical_agent_artifacts.get("canonical_scanner_json")
            or canonical_agent_artifacts.get("canonical_scanner")
            or (section_provenance.get("scanner_reason_human") or {}).get("artifact_path")
            or ""
        ),
        monitor_source_ref=str(
            canonical_agent_artifacts.get("canonical_monitor_json")
            or canonical_agent_artifacts.get("canonical_monitor")
            or (section_provenance.get("monitor_reason_human") or {}).get("artifact_path")
            or ""
        ),
        shadow_used=_commander_reasoning_flag(bundle_out, dict(bundle_out.get("commander_summary") or {}), "shadow_used"),
        strategist_fallback_used=(
            _commander_reasoning_flag(bundle_out, dict(bundle_out.get("commander_summary") or {}), "strategist_fallback_used")
            or bool((bundle_out.get("strategist_summary") or {}).get("strategist_fallback_used"))
        ),
        source_priority=commander_source_priority,
    )
    reasoning_provenance = normalize_reasoning_provenance_aliases(
        {
            "reasoning_provenance": bundle_reasoning_provenance,
            "latest_reasoning_trace_provenance": bundle_out.get("latest_reasoning_trace_provenance"),
        },
        fallback=derived_reasoning_provenance,
    )
    if isinstance(bundle_out.get("commander"), dict) or isinstance(bundle_out.get("latest_reasoning_trace_provenance"), dict):
        reasoning_provenance["shadow_used"] = _commander_reasoning_flag(
            bundle_out,
            dict(bundle_out.get("commander_summary") or {}),
            "shadow_used",
        )
        reasoning_provenance["strategist_fallback_used"] = (
            _commander_reasoning_flag(
                bundle_out,
                dict(bundle_out.get("commander_summary") or {}),
                "strategist_fallback_used",
            )
            or bool((bundle_out.get("strategist_summary") or {}).get("strategist_fallback_used"))
        )
        if commander_source_priority:
            reasoning_provenance["source_priority"] = list(commander_source_priority)
    return reasoning_provenance
