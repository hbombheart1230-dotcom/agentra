from __future__ import annotations

from typing import Any, Dict, List

from libs.reporting.trade_story_evidence import derive_evidence_provenance as _derive_evidence_provenance
import sys as _r3_sys
from libs.agents.reporter.narrative.story_provenance_bodies_01 import (  # R-4 owner bodies (facade-injected)
    _source_confidence_label_r4_impl,
    _is_present_r4_impl,
    compute_evidence_completeness_r4_impl,
    _safe_ref_map_r4_impl,
    _resolve_commander_source_ref_r4_impl,
    _commander_reasoning_flag_r4_impl,
    _commander_reasoning_source_priority_r4_impl,
    build_commander_evidence_r4_impl,
    _section_source_entry_r4_impl,
    build_section_provenance_r4_impl,
    _section_seed_provenance_entry_r4_impl,
    build_report_section_provenance_seeds_r4_impl,
)


def _source_confidence_label(source: Any) -> str:
    return _source_confidence_label_r4_impl(source, facade=_r3_sys.modules[__name__])


def _is_present(value: Any) -> bool:
    return _is_present_r4_impl(value, facade=_r3_sys.modules[__name__])


def compute_evidence_completeness(story_input: Dict[str, Any]) -> Dict[str, Any]:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    return compute_evidence_completeness_r4_impl(story_input, facade=_r3_sys.modules[__name__])


def _safe_path_text(value: Any) -> str:
    return str(value or "").strip()


def _safe_ref_map(values: Any) -> Dict[str, str]:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    return _safe_ref_map_r4_impl(values, facade=_r3_sys.modules[__name__])


def _resolve_commander_source_ref(refs: Dict[str, Any], section_provenance: Dict[str, Any]) -> str:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    return _resolve_commander_source_ref_r4_impl(refs, section_provenance, facade=_r3_sys.modules[__name__])


def _commander_reasoning_flag(source: Dict[str, Any], commander_summary: Dict[str, Any], key: str) -> bool:
    return _commander_reasoning_flag_r4_impl(source, commander_summary, key, facade=_r3_sys.modules[__name__])


def _commander_reasoning_source_priority(source: Dict[str, Any], commander_summary: Dict[str, Any]) -> List[str]:
    return _commander_reasoning_source_priority_r4_impl(source, commander_summary, facade=_r3_sys.modules[__name__])


def build_commander_evidence(commander_payload: Dict[str, Any]) -> Dict[str, Any]:
    return build_commander_evidence_r4_impl(commander_payload, facade=_r3_sys.modules[__name__])


def _section_source_entry(
    *,
    source: str,
    artifact_path: str = "",
) -> Dict[str, str]:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    return _section_source_entry_r4_impl(source=source, artifact_path=artifact_path, facade=_r3_sys.modules[__name__])


def build_section_provenance(bundle_out: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    return build_section_provenance_r4_impl(bundle_out, facade=_r3_sys.modules[__name__])


def _section_seed_provenance_entry(section_provenance: Dict[str, Any], key: str) -> Dict[str, str]:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    return _section_seed_provenance_entry_r4_impl(section_provenance, key, facade=_r3_sys.modules[__name__])


def build_report_section_provenance_seeds(section_provenance: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    return build_report_section_provenance_seeds_r4_impl(section_provenance, facade=_r3_sys.modules[__name__])
