"""Phase 5.2/5.3 runtime-health aggregate and text projection.

Pure policy-aware gating deadness and policy source summaries, compact run views, suspicious flags and the
deterministic text/table rendering moved from ``libs.reporting.phase_runtime_health``. JSON/JSONL reads,
``_iter_run_dirs``, monitor event collection/selection, ``_extract_policy_source_inspection``, ``main`` and clocks
stay in the facade module (the external ``normalize_monitor_entry_policy_schema`` is resolved on the facade); helpers and constants resolve on the injected facade at call time. Observational only.
"""
from __future__ import annotations

import json
from collections import Counter
from typing import Any, Dict, List, Mapping, Optional, Sequence


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


def _render_text_table(rows: Sequence[Mapping[str, Any]], *, facade: Any) -> str:
    lines: List[str] = []
    header = "run_id | selected_source | interpretation_basis | alignment_state | primary_blocker | gating_applied | final_decision | reason"
    lines.append(header)
    lines.append("-" * len(header))
    for row in rows:
        gating = row.get("policy_aware_gating") if isinstance(row.get("policy_aware_gating"), Mapping) else {}
        reason = str(row.get("reason") or "").replace("\n", " ").strip()
        if len(reason) > 90:
            reason = reason[:87] + "..."
        line = " | ".join(
            [
                str(row.get("run_id") or ""),
                str(row.get("selected_source") or "missing"),
                str(row.get("interpretation_basis") or "missing"),
                str(row.get("alignment_state") or "unknown"),
                str(row.get("primary_blocker") or ""),
                str(bool(gating.get("applied"))),
                str(row.get("final_decision") or ""),
                reason,
            ]
        )
        lines.append(line)
    return "\n".join(lines)


def _render_compact_run_table(rows: Sequence[Mapping[str, Any]], *, facade: Any) -> str:
    if not rows:
        return "(none)"
    lines: List[str] = []
    header = "run_id | symbol | selected_source | basis | schema | invalid_specs | struct_hint | struct_mode | struct_blockers | decision | reason"
    lines.append(header)
    lines.append("-" * len(header))
    for row in rows:
        reason = str(row.get("final_reason") or row.get("legacy_entry_reason") or "").replace("\n", " ").strip()
        if len(reason) > 72:
            reason = reason[:69] + "..."
        blocking_features = ",".join(facade._safe_list_of_str(row.get("chart_structure_blocking_features"), limit=2))
        if len(blocking_features) > 40:
            blocking_features = blocking_features[:37] + "..."
        lines.append(
            " | ".join(
                [
                    str(row.get("run_id") or ""),
                    str(row.get("symbol") or ""),
                    str(row.get("selected_source") or "missing"),
                    str(row.get("interpretation_basis") or "missing"),
                    str(row.get("policy_schema_available")),
                    str(int(row.get("invalid_policy_spec_count") or 0)),
                    str(bool(row.get("chart_structure_hint_applied"))),
                    str(row.get("chart_structure_hint_mode") or "none"),
                    blocking_features or "-",
                    str(row.get("final_decision") or ""),
                    reason,
                ]
            )
        )
    return "\n".join(lines)


def _render_reclaim_table(rows: Sequence[Mapping[str, Any]], *, facade: Any) -> str:
    if not rows:
        return "(none)"
    lines: List[str] = []
    header = "run_id | symbol | breakout_path_ok | confidence_ok | too_extended | reclaim_distance_to_ready | required_failures | gating_applied | reason"
    lines.append(header)
    lines.append("-" * len(header))
    for row in rows:
        reason = str(row.get("legacy_entry_reason") or row.get("final_reason") or "").replace("\n", " ").strip()
        lines.append(
            " | ".join(
                [
                    str(row.get("run_id") or ""),
                    str(row.get("symbol") or ""),
                    str(row.get("breakout_path_ok")),
                    str(row.get("confidence_ok")),
                    str(row.get("too_extended")),
                    str(row.get("reclaim_distance_to_ready")),
                    ",".join(facade._safe_list_of_str(row.get("required_failures"))),
                    str(bool(row.get("policy_aware_gating_applied"))),
                    reason,
                ]
            )
        )
    return "\n".join(lines)


def render_phase_5_2_5_3_runtime_health_text(payload: Mapping[str, Any], *, facade: Any) -> str:
    policy_surface_quality_summary = payload.get("policy_surface_quality_summary") if isinstance(payload.get("policy_surface_quality_summary"), Mapping) else {}
    chart_structure_decision_hint_summary = payload.get("chart_structure_decision_hint_summary") if isinstance(payload.get("chart_structure_decision_hint_summary"), Mapping) else {}
    lines: List[str] = [
        f"# Phase 5-2 ~ 5-3 Runtime Health ({payload.get('day')})",
        "",
        "## Aggregate Summary",
        "",
        f"- run_count: **{int(payload.get('run_count') or 0)}**",
        f"- selected_source_counts: `{json.dumps(payload.get('selected_source_counts') or {}, ensure_ascii=False)}`",
        f"- interpretation_basis_counts: `{json.dumps(payload.get('interpretation_basis_counts') or {}, ensure_ascii=False)}`",
        f"- policy_schema_available_counts: `{json.dumps(payload.get('policy_schema_available_counts') or {}, ensure_ascii=False)}`",
        f"- final_decision_counts: `{json.dumps(payload.get('final_decision_counts') or {}, ensure_ascii=False)}`",
        "",
        "## Structure Presence",
        "",
    ]

    structure_presence = payload.get("structure_presence") if isinstance(payload.get("structure_presence"), Mapping) else {}
    for structure in facade.STRUCTURE_KEYS:
        row = structure_presence.get(structure) if isinstance(structure_presence.get(structure), Mapping) else {}
        lines.append(
            f"- {structure}: present={int(row.get('present_count') or 0)} missing={int(row.get('missing_count') or 0)}"
        )
        missing_run_ids = list(row.get("missing_run_ids") or [])
        if missing_run_ids:
            lines.append(f"  missing_run_ids: {', '.join(str(x) for x in missing_run_ids[:10])}")

    gating_stats = payload.get("policy_aware_gating_stats") if isinstance(payload.get("policy_aware_gating_stats"), Mapping) else {}
    policy_spec_validation_stats = payload.get("policy_spec_validation_stats") if isinstance(payload.get("policy_spec_validation_stats"), Mapping) else {}
    source_summary = payload.get("policy_source_field_presence") if isinstance(payload.get("policy_source_field_presence"), Mapping) else {}
    deadness = payload.get("policy_aware_gating_deadness") if isinstance(payload.get("policy_aware_gating_deadness"), Mapping) else {}
    lines += [
        "",
        "## Policy Surface Quality Summary",
        "",
        f"- schema_available_rate: **{float(policy_surface_quality_summary.get('schema_available_rate') or 0.0):.4f}**",
        f"- normalized_policy_rate: **{float(policy_surface_quality_summary.get('normalized_policy_rate') or 0.0):.4f}**",
        f"- invalid_spec_rate: **{float(policy_surface_quality_summary.get('invalid_spec_rate') or 0.0):.4f}**",
        f"- total_invalid_specs: **{int(policy_surface_quality_summary.get('total_invalid_specs') or 0)}**",
        f"- top_invalid_features: `{json.dumps(policy_surface_quality_summary.get('top_invalid_features') or [], ensure_ascii=False)}`",
        f"- top_invalid_states: `{json.dumps(policy_surface_quality_summary.get('top_invalid_states') or [], ensure_ascii=False)}`",
        f"- validation_notes_counts: `{json.dumps(policy_surface_quality_summary.get('validation_notes_counts') or {}, ensure_ascii=False)}`",
        f"- invalid_specs_by_selected_source: `{json.dumps(policy_surface_quality_summary.get('invalid_specs_by_selected_source') or {}, ensure_ascii=False)}`",
        f"- validation_notes_by_interpretation_basis: `{json.dumps(policy_surface_quality_summary.get('validation_notes_by_interpretation_basis') or {}, ensure_ascii=False)}`",
        "",
        "## Chart Structure Decision Hint Summary",
        "",
        f"- headline: {facade._build_chart_structure_decision_hint_executive_line(chart_structure_decision_hint_summary) or 'Chart structure guard unknown'}",
        f"- available_run_count: **{int(chart_structure_decision_hint_summary.get('available_run_count') or 0)}**",
        f"- applied_count: **{int(chart_structure_decision_hint_summary.get('applied_count') or 0)}**",
        f"- applied_rate: **{float(chart_structure_decision_hint_summary.get('applied_rate') or 0.0):.4f}**",
        f"- mode_counts: `{json.dumps(chart_structure_decision_hint_summary.get('mode_counts') or {}, ensure_ascii=False)}`",
        f"- blocking_feature_counts: `{json.dumps(chart_structure_decision_hint_summary.get('blocking_feature_counts') or {}, ensure_ascii=False)}`",
        f"- top_blocking_features: `{json.dumps(chart_structure_decision_hint_summary.get('top_blocking_features') or [], ensure_ascii=False)}`",
        f"- reason_counts_when_applied: `{json.dumps(chart_structure_decision_hint_summary.get('reason_counts_when_applied') or {}, ensure_ascii=False)}`",
        "",
        "## Policy-aware Gating",
        "",
        f"- applied_true_count: **{int(gating_stats.get('applied_true_count') or 0)}**",
        f"- applied_hint_counts: `{json.dumps(gating_stats.get('applied_hint_counts') or {}, ensure_ascii=False)}`",
        f"- required_blocked_count: **{int(gating_stats.get('required_blocked_count') or 0)}**",
        f"- candidate_count: **{int(deadness.get('policy_aware_gating_candidate_count') or 0)}**",
        f"- rejection_reasons: `{json.dumps(deadness.get('policy_aware_gating_rejection_reasons') or {}, ensure_ascii=False)}`",
        "",
        "## Policy Spec Validation",
        "",
        f"- normalized_policy_schema_present_count: **{int(policy_spec_validation_stats.get('normalized_policy_schema_present_count') or 0)}**",
        f"- invalid_policy_spec_count: **{int(policy_spec_validation_stats.get('invalid_policy_spec_count') or 0)}**",
        f"- policy_validation_notes_counts: `{json.dumps(policy_spec_validation_stats.get('policy_validation_notes_counts') or {}, ensure_ascii=False)}`",
        f"- invalid_policy_specs_by_selected_source: `{json.dumps(policy_spec_validation_stats.get('invalid_policy_specs_by_selected_source') or {}, ensure_ascii=False)}`",
        "",
        "## Explicit Policy Source Presence",
        "",
    ]
    chart_structure_applied_examples = (
        chart_structure_decision_hint_summary.get("applied_examples")
        if isinstance(chart_structure_decision_hint_summary.get("applied_examples"), list)
        else []
    )
    if chart_structure_applied_examples:
        lines += ["", "### Chart Structure Guard Applied Examples", ""]
        for example in chart_structure_applied_examples[:3]:
            if not isinstance(example, Mapping):
                continue
            lines.append(
                f"- `{example.get('run_id') or '-'}` style={example.get('entry_style') or '-'} "
                f"transition={example.get('reason_transition') or '-'} "
                f"blockers={json.dumps(example.get('blocking_features') or [], ensure_ascii=False)}"
            )

    invalid_examples = policy_spec_validation_stats.get("invalid_policy_spec_examples") if isinstance(policy_spec_validation_stats.get("invalid_policy_spec_examples"), list) else []
    if invalid_examples:
        lines += ["", "### Invalid Policy Spec Examples", ""]
        for row in invalid_examples[:10]:
            notes = ",".join(facade._safe_list_of_str(row.get("validation_notes"), limit=3))
            lines.append(
                f"- `{row.get('run_id')}` source={row.get('selected_source') or '-'} raw=`{row.get('raw') or ''}` notes={notes or '-'}"
            )

    for source_name in facade.POLICY_SOURCE_NAMES:
        row = source_summary.get(source_name) if isinstance(source_summary.get(source_name), Mapping) else {}
        lines.append(
            f"- {source_name}: available={int(row.get('available_count') or 0)} schema_true={int(row.get('schema_available_true_count') or 0)} schema_false={int(row.get('schema_available_false_count') or 0)} unknown={int(row.get('schema_available_unknown_count') or 0)} modes=`{json.dumps(row.get('inspection_mode_counts') or {}, ensure_ascii=False)}`"
        )
        lines.append(
            f"  explicit_field_presence_counts: `{json.dumps(row.get('explicit_field_presence_counts') or {}, ensure_ascii=False)}`"
        )
        lines.append(
            f"  missing_all_explicit_fields_count: **{int(row.get('missing_all_explicit_fields_count') or 0)}**"
        )

    lines += [
        "",
        "## Suspicious Signals",
        "",
        f"- suspicious_counts: `{json.dumps(payload.get('suspicious_counts') or {}, ensure_ascii=False)}`",
    ]

    suspicious_runs = payload.get("suspicious_runs") if isinstance(payload.get("suspicious_runs"), list) else []
    if suspicious_runs:
        lines += ["", "### Suspicious Runs", ""]
        for row in suspicious_runs[:20]:
            lines.append(
                f"- `{row.get('run_id')}` [{row.get('final_decision')}] flags={','.join(row.get('suspicious_flags') or [])} blocker={row.get('primary_blocker') or '-'} reason={row.get('reason') or '-'}"
            )

    buy_runs = payload.get("buy_runs") if isinstance(payload.get("buy_runs"), list) else []
    reclaim_wait_runs = payload.get("reclaim_wait_runs") if isinstance(payload.get("reclaim_wait_runs"), list) else []
    lines += [
        "",
        "## Recent BUY Runs",
        "",
        facade._render_compact_run_table(buy_runs),
        "",
        "## Reclaim WAIT Runs",
        "",
        facade._render_reclaim_table(reclaim_wait_runs),
    ]

    runs = payload.get("runs") if isinstance(payload.get("runs"), list) else []
    lines += ["", "## Run Table", "", facade._render_text_table(runs), ""]
    return "\n".join(lines)


def render_policy_surface_quality_summary_text(day: str, summary: Mapping[str, Any] | None, *, facade: Any) -> str:
    row = dict(summary or {}) if isinstance(summary, Mapping) else {}
    lines = [
        f"=== Policy Surface Quality Summary ({day}) ===",
        f"schema_available_rate: {float(row.get('schema_available_rate') or 0.0):.4f}",
        f"normalized_policy_rate: {float(row.get('normalized_policy_rate') or 0.0):.4f}",
        f"invalid_spec_rate: {float(row.get('invalid_spec_rate') or 0.0):.4f}",
        f"total_invalid_specs: {int(row.get('total_invalid_specs') or 0)}",
        f"top_invalid_features: {json.dumps(row.get('top_invalid_features') or [], ensure_ascii=False)}",
        f"top_invalid_states: {json.dumps(row.get('top_invalid_states') or [], ensure_ascii=False)}",
        f"validation_notes_counts: {json.dumps(row.get('validation_notes_counts') or {}, ensure_ascii=False)}",
        f"invalid_specs_by_selected_source: {json.dumps(row.get('invalid_specs_by_selected_source') or {}, ensure_ascii=False)}",
        f"validation_notes_by_interpretation_basis: {json.dumps(row.get('validation_notes_by_interpretation_basis') or {}, ensure_ascii=False)}",
    ]
    notes = facade._safe_list_of_str(row.get("notes"), limit=8)
    if notes:
        lines.append(f"notes: {json.dumps(notes, ensure_ascii=False)}")
    return "\n".join(lines)


def render_chart_structure_decision_hint_summary_text(day: str, summary: Mapping[str, Any] | None, *, facade: Any) -> str:
    row = dict(summary or {}) if isinstance(summary, Mapping) else {}
    lines = [
        f"=== Chart Structure Decision Hint Summary ({day}) ===",
        f"available_run_count: {int(row.get('available_run_count') or 0)}",
        f"applied_count: {int(row.get('applied_count') or 0)}",
        f"applied_rate: {float(row.get('applied_rate') or 0.0):.4f}",
        f"mode_counts: {json.dumps(row.get('mode_counts') or {}, ensure_ascii=False)}",
        f"blocking_feature_counts: {json.dumps(row.get('blocking_feature_counts') or {}, ensure_ascii=False)}",
        f"top_blocking_features: {json.dumps(row.get('top_blocking_features') or [], ensure_ascii=False)}",
        f"reason_counts_when_applied: {json.dumps(row.get('reason_counts_when_applied') or {}, ensure_ascii=False)}",
    ]
    applied_examples = row.get("applied_examples") if isinstance(row.get("applied_examples"), list) else []
    if applied_examples:
        lines.append("applied_examples:")
        for example in applied_examples[:3]:
            if not isinstance(example, Mapping):
                continue
            lines.append(
                "  - "
                f"run_id={example.get('run_id') or '-'} "
                f"style={example.get('entry_style') or '-'} "
                f"transition={example.get('reason_transition') or '-'} "
                f"blockers={json.dumps(example.get('blocking_features') or [], ensure_ascii=False)}"
            )
    notes = facade._safe_list_of_str(row.get("notes"), limit=8)
    if notes:
        lines.append(f"notes: {json.dumps(notes, ensure_ascii=False)}")
    return "\n".join(lines)


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
