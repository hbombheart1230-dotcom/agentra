"""Phase 5.2/5.3 runtime-health aggregate and text projection.

Run-health surface extraction, run-row assembly and the day aggregate of ``libs.reporting.phase_runtime_health``.
Policy views live in ``phase_health_policy_views`` and text rendering in ``phase_health_text_rendering``. JSON/JSONL
reads, ``_iter_run_dirs``, monitor event collection, ``_extract_policy_source_inspection``, ``main`` and clocks stay in
the facade module (``normalize_monitor_entry_policy_schema`` is resolved on the facade); helpers resolve on the injected
facade at call time. Observational only.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Mapping


def _extract_run_health_surfaces(monitor: Mapping[str, Any], event_payloads: Mapping[str, Dict[str, Any]], *, facade: Any) -> Dict[str, Any]:
    final_decision = str(monitor.get("decision") or "").strip().upper()
    reason = (
        str(monitor.get("entry_reason") or "").strip()
        or str(monitor.get("monitor_reason") or "").strip()
        or str(monitor.get("primary_reason_code") or "").strip()
        or str(monitor.get("decision_summary") or "").strip()
    )

    persisted_surfaces = facade._persisted_monitor_surfaces(monitor)
    surfaces = {
        key: facade._pick_first_dict(
            facade._get_surface_from_event_payloads(event_payloads, key),
            persisted_surfaces.get(key),
        )
        for key in facade.STRUCTURE_KEYS
    }
    contract = surfaces["entry_policy_contract"]
    interpretation = surfaces["policy_interpretation"]
    evidence = surfaces["signal_evidence"]
    trace = surfaces["policy_interpreter_trace"]
    alignment = surfaces["policy_alignment_summary"]
    gating = surfaces["policy_aware_gating"]
    chart_structure_decision_hint = facade._pick_first_dict(
        facade._get_surface_from_event_payloads(event_payloads, "chart_structure_decision_hint"),
        persisted_surfaces.get("chart_structure_decision_hint"),
    )
    selected_policy_schema = (
        dict(contract.get("selected_policy_schema") or {})
        if isinstance(contract.get("selected_policy_schema"), Mapping)
        else {}
    )
    selected_policy_spec_health = (
        dict(contract.get("selected_policy_spec_health") or {})
        if isinstance(contract.get("selected_policy_spec_health"), Mapping)
        else {}
    )
    return {
        "final_decision": final_decision,
        "reason": reason,
        "persisted_surfaces": persisted_surfaces,
        "surfaces": surfaces,
        "contract": contract,
        "interpretation": interpretation,
        "evidence": evidence,
        "trace": trace,
        "alignment": alignment,
        "gating": gating,
        "chart_structure_decision_hint": chart_structure_decision_hint,
        "selected_policy_schema": selected_policy_schema,
        "selected_policy_spec_health": selected_policy_spec_health,
    }


def _assemble_run_health(run_dir: Any, monitor_json_path: Any, monitor: Mapping[str, Any], event_payloads: Mapping[str, Dict[str, Any]],
                         stage: Mapping[str, Any], source_inspection: Any, *, facade: Any) -> Dict[str, Any]:
    final_decision = stage["final_decision"]
    reason = stage["reason"]
    persisted_surfaces = stage["persisted_surfaces"]
    surfaces = stage["surfaces"]
    contract = stage["contract"]
    interpretation = stage["interpretation"]
    evidence = stage["evidence"]
    trace = stage["trace"]
    alignment = stage["alignment"]
    gating = stage["gating"]
    chart_structure_decision_hint = stage["chart_structure_decision_hint"]
    selected_policy_schema = stage["selected_policy_schema"]
    selected_policy_spec_health = stage["selected_policy_spec_health"]

    structure_presence = {key: facade._dict_present(value) for key, value in surfaces.items()}
    selected_policy = contract.get("selected_policy") if isinstance(contract.get("selected_policy"), Mapping) else {}
    selected_source = str(contract.get("selected_source") or "").strip()
    source_priority = facade._safe_list_of_str(contract.get("source_priority"), limit=10)
    interpretation_basis = str(interpretation.get("interpretation_basis") or "").strip()
    policy_schema_available = interpretation.get("policy_schema_available")
    policy_schema_version = str(interpretation.get("policy_schema_version") or "").strip()
    alignment_state = str(alignment.get("alignment_state") or "").strip()
    primary_blocker = str(alignment.get("primary_blocker") or "").strip()
    secondary_blockers = facade._safe_list_of_str(alignment.get("secondary_blockers"))
    entry_style = str(interpretation.get("entry_style") or "").strip().lower() or None
    spec_validation_notes = facade._safe_list_of_str(
        selected_policy_spec_health.get("spec_validation_notes")
        or selected_policy_schema.get("spec_validation_notes"),
        limit=20,
    )
    invalid_policy_specs = list(selected_policy_schema.get("invalid_policy_specs") or []) if isinstance(selected_policy_schema.get("invalid_policy_specs"), list) else []
    invalid_policy_spec_count = int(
        selected_policy_spec_health.get("invalid_policy_spec_count")
        if selected_policy_spec_health.get("invalid_policy_spec_count") is not None
        else len(invalid_policy_specs)
    )
    normalized_policy_spec_count = int(
        selected_policy_spec_health.get("normalized_policy_spec_count")
        if selected_policy_spec_health.get("normalized_policy_spec_count") is not None
        else sum(
            len(facade._safe_list_of_str(selected_policy_schema.get(key), limit=64))
            for key in ("required_checks", "preferred_checks", "relaxable_checks", "blockers")
        )
    )
    policy_schema_explicit_fields_used = facade._safe_list_of_str(
        selected_policy_spec_health.get("explicit_fields_used")
        or selected_policy_schema.get("explicit_fields_used"),
        limit=32,
    )
    policy_schema_raw_keys = facade._safe_list_of_str(
        selected_policy_spec_health.get("raw_keys")
        or selected_policy_schema.get("raw_keys"),
        limit=64,
    )
    required_failures = facade._failed_check_names(((trace.get("check_status") or {}) if isinstance(trace.get("check_status"), Mapping) else {}).get("required"), fail_statuses=("fail",))
    preferred_failures = facade._failed_check_names(((trace.get("check_status") or {}) if isinstance(trace.get("check_status"), Mapping) else {}).get("preferred"), fail_statuses=("fail",))
    relaxable_failures = facade._failed_check_names(((trace.get("check_status") or {}) if isinstance(trace.get("check_status"), Mapping) else {}).get("relaxable"), fail_statuses=("fail",))
    blockers_active = facade._failed_check_names(((trace.get("check_status") or {}) if isinstance(trace.get("check_status"), Mapping) else {}).get("blockers"), fail_statuses=("active",))
    evidence_checks = evidence.get("checks") if isinstance(evidence.get("checks"), Mapping) else {}
    evidence_derived = evidence.get("derived") if isinstance(evidence.get("derived"), Mapping) else {}
    legacy_entry_decision = str(
        facade._pick_first_value_from_event_payloads(event_payloads, "legacy_entry_decision")
        or monitor.get("legacy_entry_decision")
        or ""
    ).strip().upper() or None
    legacy_entry_reason = str(
        facade._pick_first_value_from_event_payloads(event_payloads, "legacy_entry_reason", "entry_reason")
        or monitor.get("legacy_entry_reason")
        or monitor.get("entry_reason")
        or ""
    ).strip() or None
    suspicious = facade._build_suspicious_flags(
        final_decision=final_decision,
        alignment_summary=alignment,
        trace=trace,
        gating=gating,
    )

    return {
        "run_id": run_dir.name,
        "day": str(monitor.get("day") or run_dir.parent.name),
        "symbol": str(monitor.get("symbol") or ""),
        "monitor_json_path": str(monitor_json_path),
        "final_decision": final_decision or "UNKNOWN",
        "reason": reason,
        "policy_evaluable": bool(persisted_surfaces.get("entry_evaluated")) or any(structure_presence.values()),
        "structures": structure_presence,
        "selected_source": selected_source or None,
        "selected_policy_present": bool(selected_policy),
        "source_priority_present": bool(source_priority),
        "source_priority": source_priority,
        "interpretation_basis": interpretation_basis or None,
        "policy_schema_available": policy_schema_available if isinstance(policy_schema_available, bool) else None,
        "policy_schema_version": policy_schema_version or None,
        "alignment_state": alignment_state or None,
        "primary_blocker": primary_blocker or None,
        "secondary_blockers": secondary_blockers,
        "entry_style": entry_style,
        "normalized_policy_spec_count": normalized_policy_spec_count,
        "invalid_policy_spec_count": invalid_policy_spec_count,
        "invalid_policy_specs": invalid_policy_specs,
        "spec_validation_notes": spec_validation_notes,
        "policy_schema_explicit_fields_used": policy_schema_explicit_fields_used,
        "policy_schema_raw_keys": policy_schema_raw_keys,
        "legacy_entry_decision": legacy_entry_decision,
        "legacy_entry_reason": legacy_entry_reason,
        "reclaim_gate_ok": facade._safe_bool(evidence_checks.get("reclaim_gate_ok")),
        "breakout_path_ok": facade._safe_bool(evidence_checks.get("breakout_path_ok")),
        "confidence_ok": facade._safe_bool(evidence_checks.get("confidence_ok")),
        "volume_ok": facade._safe_bool(evidence_checks.get("volume_ok")),
        "too_extended": facade._safe_bool(evidence_derived.get("too_extended")),
        "reclaim_distance_to_ready": facade._safe_float(evidence_derived.get("reclaim_distance_to_ready")),
        "top_failed_required_checks": required_failures,
        "top_failed_preferred_checks": preferred_failures,
        "top_relaxable_gaps": relaxable_failures,
        "active_blockers": blockers_active,
        "policy_aware_gating": {
            "available": bool(gating.get("available")) if facade._dict_present(gating) else False,
            "applied": bool(gating.get("applied")) if facade._dict_present(gating) else False,
            "applied_hints": facade._safe_list_of_str(gating.get("applied_hints")),
            "required_failures": facade._safe_list_of_str(gating.get("required_failures")),
            "relaxations_considered": facade._safe_list_of_str(gating.get("relaxations_considered")),
            "relaxations_applied": facade._safe_list_of_str(gating.get("relaxations_applied")),
            "blocked_by_required": facade._safe_list_of_str(gating.get("blocked_by_required")),
            "notes": facade._safe_list_of_str(gating.get("notes")),
        },
        "chart_structure_decision_hint": {
            "available": bool(chart_structure_decision_hint.get("available")) if facade._dict_present(chart_structure_decision_hint) else False,
            "applied": bool(chart_structure_decision_hint.get("applied")) if facade._dict_present(chart_structure_decision_hint) else False,
            "mode": str(chart_structure_decision_hint.get("mode") or "none"),
            "entry_style": str(chart_structure_decision_hint.get("entry_style") or ""),
            "considered_features": facade._safe_list_of_str(chart_structure_decision_hint.get("considered_features")),
            "matched_features": facade._safe_list_of_str(chart_structure_decision_hint.get("matched_features")),
            "blocking_features": facade._safe_list_of_str(chart_structure_decision_hint.get("blocking_features")),
            "notes": facade._safe_list_of_str(chart_structure_decision_hint.get("notes")),
        },
        "policy_source_inspection": source_inspection,
        "suspicious_flags": suspicious,
    }


def build_runtime_health_aggregate(run_rows: List[Dict[str, Any]], *, day: str, reports_root: Any, event_log_path: Any, facade: Any) -> Dict[str, Any]:
    structure_summary: Dict[str, Dict[str, Any]] = {}
    selected_source_counts: Counter[str] = Counter()
    interpretation_basis_counts: Counter[str] = Counter()
    schema_counts: Counter[str] = Counter()
    gating_hint_counts: Counter[str] = Counter()
    suspicious_counts: Counter[str] = Counter()
    decision_counts: Counter[str] = Counter()
    policy_validation_notes_counts: Counter[str] = Counter()
    invalid_policy_specs_by_source: Counter[str] = Counter()
    validation_notes_by_interpretation_basis: Dict[str, Counter[str]] = {}
    invalid_policy_spec_examples: List[Dict[str, Any]] = []
    invalid_policy_spec_run_ids: List[str] = []
    invalid_policy_spec_count_total = 0
    normalized_policy_schema_present_count = 0
    gating_required_blocked = 0
    gating_applied_true = 0

    for structure in facade.STRUCTURE_KEYS:
        missing = [row["run_id"] for row in run_rows if not bool((row.get("structures") or {}).get(structure))]
        structure_summary[structure] = {
            "present_count": len(run_rows) - len(missing),
            "missing_count": len(missing),
            "missing_run_ids": missing,
        }

    for row in run_rows:
        decision_counts[str(row.get("final_decision") or "UNKNOWN")] += 1
        selected_source_counts[str(row.get("selected_source") or "missing")] += 1
        interpretation_basis_counts[str(row.get("interpretation_basis") or "missing")] += 1
        schema_value = row.get("policy_schema_available")
        if schema_value is True:
            schema_counts["true"] += 1
        elif schema_value is False:
            schema_counts["false"] += 1
        else:
            schema_counts["missing"] += 1
        if schema_value is True:
            normalized_policy_schema_present_count += 1

        invalid_policy_spec_count_total += int(row.get("invalid_policy_spec_count") or 0)
        if int(row.get("invalid_policy_spec_count") or 0) > 0:
            invalid_policy_specs_by_source[str(row.get("selected_source") or "missing")] += int(row.get("invalid_policy_spec_count") or 0)
            invalid_policy_spec_run_ids.append(str(row.get("run_id") or ""))
            if len(invalid_policy_spec_examples) < 10:
                for invalid_spec in list(row.get("invalid_policy_specs") or []):
                    if not isinstance(invalid_spec, Mapping):
                        continue
                    invalid_policy_spec_examples.append(
                        {
                            "run_id": str(row.get("run_id") or ""),
                            "selected_source": str(row.get("selected_source") or ""),
                            "raw": str(invalid_spec.get("raw") or ""),
                            "feature_name": invalid_spec.get("feature_name"),
                            "expected_state": invalid_spec.get("expected_state"),
                            "validation_notes": list(invalid_spec.get("validation_notes") or []),
                        }
                    )
                    if len(invalid_policy_spec_examples) >= 10:
                        break
        basis_key = str(row.get("interpretation_basis") or "missing")
        basis_notes = validation_notes_by_interpretation_basis.setdefault(basis_key, Counter())
        for note in facade._safe_list_of_str(row.get("spec_validation_notes"), limit=64):
            policy_validation_notes_counts[note] += 1
            basis_notes[note] += 1

        gating = row.get("policy_aware_gating") if isinstance(row.get("policy_aware_gating"), Mapping) else {}
        if bool(gating.get("applied")):
            gating_applied_true += 1
        if facade._safe_list_of_str(gating.get("blocked_by_required")):
            gating_required_blocked += 1
        for hint in facade._safe_list_of_str(gating.get("applied_hints"), limit=20):
            gating_hint_counts[hint] += 1
        for flag in facade._safe_list_of_str(row.get("suspicious_flags"), limit=20):
            suspicious_counts[flag] += 1

    suspicious_runs = [row for row in run_rows if row.get("suspicious_flags")]
    buy_runs = [facade._compact_run_view(row) for row in run_rows if str(row.get("final_decision") or "").upper() == "BUY"]
    reclaim_wait_runs = [
        facade._compact_run_view(row)
        for row in run_rows
        if str(row.get("final_decision") or "").upper() in {"WAIT", "NOOP"}
        and str(row.get("legacy_entry_reason") or row.get("reason") or "").strip() == "below_vwap_reclaim_not_ready"
    ]
    out = {
        "schema_version": "phase_5_runtime_health_check.v1",
        "day": str(day or run_rows[0].get("day") or ""),
        "reports_root": str(reports_root),
        "event_log_path": str(event_log_path),
        "run_count": len(run_rows),
        "structure_presence": structure_summary,
        "selected_source_counts": dict(selected_source_counts),
        "interpretation_basis_counts": dict(interpretation_basis_counts),
        "policy_schema_available_counts": dict(schema_counts),
        "policy_aware_gating_stats": {
            "applied_true_count": gating_applied_true,
            "applied_hint_counts": dict(gating_hint_counts),
            "required_blocked_count": gating_required_blocked,
        },
        "policy_spec_validation_stats": {
            "normalized_policy_schema_present_count": normalized_policy_schema_present_count,
            "invalid_policy_spec_count": invalid_policy_spec_count_total,
            "invalid_policy_spec_run_ids": invalid_policy_spec_run_ids[:20],
            "invalid_policy_spec_examples": invalid_policy_spec_examples,
            "policy_validation_notes_counts": dict(policy_validation_notes_counts),
            "invalid_policy_specs_by_selected_source": dict(invalid_policy_specs_by_source),
            "validation_notes_by_interpretation_basis": {
                key: dict(counter)
                for key, counter in validation_notes_by_interpretation_basis.items()
            },
        },
        "policy_source_field_presence": facade._build_policy_source_summary(run_rows),
        "policy_aware_gating_deadness": facade._build_policy_aware_gating_deadness(run_rows),
        "chart_structure_decision_hint_summary": facade._build_chart_structure_decision_hint_summary(run_rows),
        "final_decision_counts": dict(decision_counts),
        "suspicious_counts": dict(suspicious_counts),
        "suspicious_runs": suspicious_runs,
        "buy_runs": buy_runs,
        "reclaim_wait_runs": reclaim_wait_runs,
        "policy_surface_quality_summary": facade._build_policy_surface_quality_summary(
            [row for row in run_rows if bool(row.get("policy_evaluable"))]
        ),
        "runs": run_rows,
    }
    return out
