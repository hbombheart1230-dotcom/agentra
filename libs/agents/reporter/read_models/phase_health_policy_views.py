"""Phase 5.2/5.3 runtime-health policy views.

Pure policy-aware gating deadness, policy source summary, compact run view, suspicious flags and the persisted monitor
surface selection moved from ``libs.reporting.phase_runtime_health``. Reads, schema normalization and run discovery stay
in the facade; helpers and constants resolve on the injected facade module at call time. Observational only.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Mapping, Sequence


def _build_policy_aware_gating_deadness(rows: Sequence[Mapping[str, Any]], *, facade: Any) -> Dict[str, Any]:
    rejection_counts: Counter[str] = Counter()
    candidate_run_ids: List[str] = []
    applied_run_ids: List[str] = []

    for row in rows:
        gating = row.get("policy_aware_gating") if isinstance(row.get("policy_aware_gating"), Mapping) else {}
        if not bool(gating.get("available")):
            continue
        entry_style = str(row.get("entry_style") or "").strip().lower()
        relaxations_considered = facade._safe_list_of_str(gating.get("relaxations_considered"), limit=20)
        legacy_reason = str(row.get("legacy_entry_reason") or row.get("reason") or "").strip()
        legacy_decision = str(row.get("legacy_entry_decision") or row.get("final_decision") or "").strip().upper()
        if entry_style != "breakout" or "reclaim_gate_ok" not in relaxations_considered:
            continue
        if legacy_reason not in ("", "below_vwap_reclaim_not_ready"):
            continue

        candidate_run_ids.append(str(row.get("run_id") or ""))
        if bool(gating.get("applied")):
            applied_run_ids.append(str(row.get("run_id") or ""))
            continue

        if facade._safe_list_of_str(gating.get("required_failures")):
            rejection_counts["required_failure"] += 1
        if legacy_decision == "BUY":
            rejection_counts["legacy_already_triggered"] += 1
        if row.get("reclaim_gate_ok") is True:
            rejection_counts["reclaim_gate_already_passed"] += 1

        reclaim_distance = row.get("reclaim_distance_to_ready")
        if reclaim_distance is None:
            rejection_counts["reclaim_distance_missing"] += 1
        else:
            try:
                reclaim_value = float(reclaim_distance)
            except Exception:
                rejection_counts["reclaim_distance_invalid"] += 1
            else:
                if not (-0.0015 <= reclaim_value < 0.0):
                    rejection_counts["reclaim_not_near_ready"] += 1

        if row.get("breakout_path_ok") is not True:
            rejection_counts["breakout_path_not_ready"] += 1
        if row.get("confidence_ok") is not True:
            rejection_counts["confidence_not_ready"] += 1
        if row.get("too_extended") is True:
            rejection_counts["too_extended"] += 1
        if str(row.get("alignment_state") or "").strip().lower() not in {"aligned", "partial"}:
            rejection_counts["alignment_state_not_relaxable"] += 1
        if not (row.get("volume_ok") is True or row.get("breakout_path_ok") is True):
            rejection_counts["supporting_path_not_ready"] += 1

        for note in facade._safe_list_of_str(gating.get("notes"), limit=20):
            rejection_counts[f"note:{note}"] += 1

    return {
        "policy_aware_gating_candidate_count": len(candidate_run_ids),
        "policy_aware_gating_applied_count": len(applied_run_ids),
        "policy_aware_gating_candidate_run_ids": candidate_run_ids[:20],
        "policy_aware_gating_applied_run_ids": applied_run_ids[:20],
        "policy_aware_gating_rejection_reasons": dict(rejection_counts),
    }


def _build_policy_source_summary(rows: Sequence[Mapping[str, Any]], *, facade: Any) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for source_name in facade.POLICY_SOURCE_NAMES:
        field_counts: Counter[str] = Counter()
        explicit_fields_used_counts: Counter[str] = Counter()
        raw_key_counts: Counter[str] = Counter()
        schema_version_counts: Counter[str] = Counter()
        inspection_mode_counts: Counter[str] = Counter()
        schema_true = 0
        schema_false = 0
        schema_unknown = 0
        available_count = 0
        missing_all_explicit = 0
        sample_missing_runs: List[str] = []

        for row in rows:
            inspections = row.get("policy_source_inspection") if isinstance(row.get("policy_source_inspection"), Mapping) else {}
            inspected = inspections.get(source_name) if isinstance(inspections.get(source_name), Mapping) else {}
            if not inspected:
                continue
            available = bool(inspected.get("available"))
            if available:
                available_count += 1
            inspection_mode_counts[str(inspected.get("inspection_mode") or "unknown")] += 1
            schema_value = inspected.get("schema_available")
            if schema_value is True:
                schema_true += 1
            elif schema_value is False:
                schema_false += 1
            else:
                schema_unknown += 1
            schema_version = str(inspected.get("schema_version") or "").strip()
            if schema_version:
                schema_version_counts[schema_version] += 1
            for raw_key in facade._safe_list_of_str(inspected.get("raw_keys"), limit=64):
                raw_key_counts[raw_key] += 1
            field_presence = inspected.get("field_presence") if isinstance(inspected.get("field_presence"), Mapping) else {}
            any_explicit = False
            for field_name in facade.EXPLICIT_POLICY_FIELDS:
                if bool(field_presence.get(field_name)):
                    field_counts[field_name] += 1
                    any_explicit = True
            for field_name in facade._safe_list_of_str(inspected.get("explicit_fields_used"), limit=32):
                explicit_fields_used_counts[field_name] += 1
                any_explicit = True
            if available and not any_explicit:
                missing_all_explicit += 1
                if len(sample_missing_runs) < 10:
                    sample_missing_runs.append(str(row.get("run_id") or ""))

        out[source_name] = {
            "available_count": available_count,
            "inspection_mode_counts": dict(inspection_mode_counts),
            "schema_available_true_count": schema_true,
            "schema_available_false_count": schema_false,
            "schema_available_unknown_count": schema_unknown,
            "explicit_field_presence_counts": dict(field_counts),
            "explicit_fields_used_counts": dict(explicit_fields_used_counts),
            "raw_key_counts": dict(raw_key_counts),
            "schema_version_counts": dict(schema_version_counts),
            "missing_all_explicit_fields_count": missing_all_explicit,
            "sample_runs_missing_all_explicit_fields": sample_missing_runs,
        }
    return out


def _compact_run_view(row: Mapping[str, Any], *, facade: Any) -> Dict[str, Any]:
    gating = row.get("policy_aware_gating") if isinstance(row.get("policy_aware_gating"), Mapping) else {}
    structure_hint = row.get("chart_structure_decision_hint") if isinstance(row.get("chart_structure_decision_hint"), Mapping) else {}
    return {
        "run_id": str(row.get("run_id") or ""),
        "symbol": str(row.get("symbol") or ""),
        "selected_source": row.get("selected_source"),
        "interpretation_basis": row.get("interpretation_basis"),
        "policy_schema_available": row.get("policy_schema_available"),
        "alignment_state": row.get("alignment_state"),
        "primary_blocker": row.get("primary_blocker"),
        "entry_style": row.get("entry_style"),
        "final_decision": row.get("final_decision"),
        "final_reason": row.get("reason"),
        "legacy_entry_decision": row.get("legacy_entry_decision"),
        "legacy_entry_reason": row.get("legacy_entry_reason"),
        "invalid_policy_spec_count": int(row.get("invalid_policy_spec_count") or 0),
        "policy_validation_notes": facade._safe_list_of_str(row.get("spec_validation_notes"), limit=4),
        "policy_aware_gating_applied": bool(gating.get("applied")),
        "policy_aware_gating_applied_hints": facade._safe_list_of_str(gating.get("applied_hints")),
        "chart_structure_hint_applied": bool(structure_hint.get("applied")),
        "chart_structure_hint_mode": str(structure_hint.get("mode") or "none"),
        "chart_structure_blocking_features": facade._safe_list_of_str(structure_hint.get("blocking_features")),
        "required_failures": facade._safe_list_of_str(gating.get("required_failures")),
        "breakout_path_ok": row.get("breakout_path_ok"),
        "confidence_ok": row.get("confidence_ok"),
        "volume_ok": row.get("volume_ok"),
        "too_extended": row.get("too_extended"),
        "reclaim_gate_ok": row.get("reclaim_gate_ok"),
        "reclaim_distance_to_ready": row.get("reclaim_distance_to_ready"),
    }


def _build_suspicious_flags(*, final_decision: str, alignment_summary: Mapping[str, Any], trace: Mapping[str, Any], gating: Mapping[str, Any], facade: Any) -> List[str]:
    out: List[str] = []
    decision = str(final_decision or "").strip().upper()
    primary_blocker = str(alignment_summary.get("primary_blocker") or "").strip()
    alignment_state = str(alignment_summary.get("alignment_state") or "").strip().lower()
    check_status = trace.get("check_status") if isinstance(trace.get("check_status"), Mapping) else {}
    required_failed = facade._failed_check_names((check_status or {}).get("required"), fail_statuses=("fail",))
    preferred_failed = facade._failed_check_names((check_status or {}).get("preferred"), fail_statuses=("fail",))
    relaxable_failed = facade._failed_check_names((check_status or {}).get("relaxable"), fail_statuses=("fail",))
    applied_hints = facade._safe_list_of_str(gating.get("applied_hints"))
    relaxations_applied = facade._safe_list_of_str(gating.get("relaxations_applied"))

    if decision == "WAIT" and not primary_blocker:
        out.append("wait_missing_primary_blocker")
    if decision == "WAIT" and not required_failed:
        out.append("wait_no_failed_required_checks")
    if decision == "BUY" and alignment_state == "misaligned":
        out.append("buy_misaligned_policy_summary")
    if decision == "BUY" and bool(gating.get("applied")) and not (applied_hints or relaxations_applied):
        out.append("buy_gating_applied_without_context")
    if decision == "WAIT" and not required_failed and not preferred_failed and not relaxable_failed and not primary_blocker:
        out.append("wait_without_visible_alignment_gap")
    return out


def _persisted_monitor_surfaces(monitor: Mapping[str, Any], *, facade: Any) -> Dict[str, Dict[str, Any]]:
    trace = facade._pick_first_dict(monitor.get("policy_interpreter_trace"))
    alignment = facade._pick_first_dict(monitor.get("policy_alignment_summary"))
    grouped = facade._persisted_grouped_logic_trace(monitor)
    signal_snapshot = monitor.get("signal_snapshot") if isinstance(monitor.get("signal_snapshot"), Mapping) else {}

    selected_policy = facade._pick_first_dict(
        monitor.get("effective_policy"),
        monitor.get("applied_policy"),
        monitor.get("received_policy"),
    )
    entry_style = str(trace.get("entry_style") or "").strip().lower()
    policy_for_schema = dict(selected_policy)
    if entry_style and not policy_for_schema.get("entry_style"):
        policy_for_schema["entry_style"] = entry_style
    check_status = trace.get("check_status") if isinstance(trace.get("check_status"), Mapping) else {}
    for field_name, trace_name in (
        ("required_checks", "required"),
        ("preferred_checks", "preferred"),
        ("relaxable_checks", "relaxable"),
        ("blockers", "blockers"),
    ):
        if policy_for_schema.get(field_name) is not None:
            continue
        specs: List[str] = []
        for row in list(check_status.get(trace_name) or []):
            if not isinstance(row, Mapping):
                continue
            name = str(row.get("name") or "").strip()
            expected_state = str(row.get("expected_state") or "").strip()
            spec = f"{name}={expected_state}" if name and expected_state else name
            if spec and spec not in specs:
                specs.append(spec)
        if specs:
            policy_for_schema[field_name] = specs
    selected_policy_schema = facade.normalize_monitor_entry_policy_schema(policy_for_schema)
    invalid_specs = list(selected_policy_schema.get("invalid_policy_specs") or [])
    normalized_count = sum(
        len(facade._safe_list_of_str(selected_policy_schema.get(key), limit=64))
        for key in ("required_checks", "preferred_checks", "relaxable_checks", "blockers")
    )
    selected_source = str(
        monitor.get("received_policy_source")
        or monitor.get("effective_policy_source")
        or monitor.get("policy_source")
        or "persisted_monitor_policy"
    ).strip()
    contract = {}
    if selected_policy or bool(selected_policy_schema.get("available")):
        contract = {
            "selected_source": selected_source,
            "selected_policy": selected_policy,
            "selected_policy_schema": selected_policy_schema,
            "selected_policy_spec_health": {
                "schema_available": bool(selected_policy_schema.get("available")),
                "normalized_policy_spec_count": normalized_count,
                "invalid_policy_spec_count": len(invalid_specs),
                "spec_validation_notes": list(selected_policy_schema.get("spec_validation_notes") or []),
                "explicit_fields_used": list(selected_policy_schema.get("explicit_fields_used") or []),
                "raw_keys": list(selected_policy_schema.get("raw_keys") or []),
            },
            "source_priority": [selected_source],
        }

    interpretation = {}
    if contract or trace:
        interpretation = {
            "interpretation_basis": "persisted_monitor_policy",
            "policy_schema_available": bool(selected_policy_schema.get("available") or trace.get("policy_available")),
            "policy_schema_version": str(selected_policy_schema.get("schema_version") or ""),
            "entry_style": entry_style or selected_policy_schema.get("entry_style"),
        }

    volume_confirmation = (
        grouped.get("volume_confirmation")
        if isinstance(grouped.get("volume_confirmation"), Mapping)
        else {}
    )
    checks = {
        "reclaim_gate_ok": grouped.get("reclaim_gate_ok"),
        "breakout_path_ok": grouped.get("breakout_path_ok"),
        "confidence_ok": grouped.get("confidence_gate_ok"),
        "volume_ok": volume_confirmation.get("volume_ok"),
        "extension_ok": grouped.get("extension_ok"),
    }
    checks = {key: value for key, value in checks.items() if isinstance(value, bool)}
    evidence = {"checks": checks, "derived": {}} if checks else {}

    gating = {}
    if grouped:
        gating = {
            "available": bool(grouped.get("policy_aware_gating_available")),
            "applied": bool(grouped.get("policy_aware_gating_applied")),
            "applied_hints": list(grouped.get("policy_aware_gating_hints") or []),
            "required_failures": list(grouped.get("policy_aware_gating_required_failures") or []),
            "relaxations_considered": list(grouped.get("policy_aware_gating_relaxations_considered") or []),
            "relaxations_applied": list(grouped.get("policy_aware_gating_relaxations_applied") or []),
            "blocked_by_required": list(grouped.get("policy_aware_gating_blocked_by_required") or []),
            "notes": ["restored_from_canonical_monitor"],
        }

    chart_hint = {}
    if grouped and bool(grouped.get("chart_structure_decision_hint_available")):
        chart_hint = {
            "available": True,
            "applied": bool(grouped.get("chart_structure_decision_hint_applied")),
            "mode": str(grouped.get("chart_structure_decision_hint_mode") or "none"),
            "entry_style": entry_style,
            "considered_features": [],
            "matched_features": [],
            "blocking_features": list(grouped.get("chart_structure_decision_hint_blocking_features") or []),
            "notes": ["restored_from_canonical_monitor"],
        }

    return {
        "entry_policy_contract": contract,
        "policy_interpretation": interpretation,
        "signal_evidence": evidence,
        "policy_interpreter_trace": trace,
        "policy_alignment_summary": alignment,
        "policy_aware_gating": gating,
        "chart_structure_decision_hint": chart_hint,
        "entry_evaluated": bool(signal_snapshot.get("entry_evaluated")),
    }
