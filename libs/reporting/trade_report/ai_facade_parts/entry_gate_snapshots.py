"""AI report entry-gate snapshot compaction and post-entry observation shaping (deterministic, read-only).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _entry_gate_bits_r3_impl(grouped_trace, entry_scores, *, facade):
    scores = entry_scores if isinstance(entry_scores, dict) else {}
    gate_bits: List[str] = []
    if "reclaim_gate_ok" in grouped_trace:
        gate_bits.append(f"{facade._entry_gate_name_label('reclaim')} {facade._entry_gate_state_label(grouped_trace.get('reclaim_gate_ok'))}")
    if "extension_ok" in grouped_trace:
        gate_bits.append(f"{facade._entry_gate_name_label('extension')} {facade._entry_gate_state_label(grouped_trace.get('extension_ok'))}")
    if "confidence_gate_ok" in grouped_trace:
        gate_bits.append(f"{facade._entry_gate_name_label('confidence gate')} {facade._entry_gate_state_label(grouped_trace.get('confidence_gate_ok'))}")
    elif "confidence_gate_ok" in scores:
        gate_bits.append(f"{facade._entry_gate_name_label('confidence gate')} {facade._entry_gate_state_label(scores.get('confidence_gate_ok'))}")
    return gate_bits


def _entry_gate_signature_r3_impl(source, *, facade):
    grouped_trace = facade._as_dict(source.get("entry_grouped_logic_trace"))
    entry_scores = facade._as_dict(source.get("entry_condition_scores"))
    return (
        grouped_trace.get("reclaim_gate_ok"),
        grouped_trace.get("extension_ok"),
        grouped_trace.get("confidence_gate_ok", entry_scores.get("confidence_gate_ok")),
        grouped_trace.get("triggered_path") or source.get("entry_condition_path"),
        entry_scores.get("confidence_score"),
        entry_scores.get("confidence_threshold"),
    )


def _compact_entry_gate_snapshot_r3_impl(source, *, facade):
    grouped_trace = facade._as_dict(source.get("entry_grouped_logic_trace"))
    entry_scores = facade._as_dict(source.get("entry_condition_scores"))
    out: Dict[str, Any] = {}
    if grouped_trace:
        out["entry_grouped_logic_trace"] = grouped_trace
    if entry_scores:
        out["entry_condition_scores"] = entry_scores
    if source.get("entry_condition_path") not in (None, ""):
        out["entry_condition_path"] = source.get("entry_condition_path")
    if source.get("entry_reason") not in (None, ""):
        out["entry_reason"] = source.get("entry_reason")
    return out


def _entry_snapshot_as_post_entry_observation_r3_impl(monitor_reason, *, facade):
    resolved = dict(monitor_reason or {})
    post_entry_snapshot = facade._compact_entry_gate_snapshot(monitor_reason)
    for key in (
        "entry_grouped_logic_trace",
        "entry_condition_scores",
        "entry_condition_path",
        "entry_condition_paths_passed",
        "entry_reason",
        "entry_thresholds",
    ):
        resolved.pop(key, None)
    if post_entry_snapshot:
        resolved["post_entry_gate_observation"] = post_entry_snapshot
        resolved["entry_gate_snapshot_source"] = "post_entry_monitor_snapshot_only"
    return resolved
