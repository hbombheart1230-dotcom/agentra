"""Phase 5.2/5.3 runtime-health aggregate and text projection (P1.5 BATCH05-A2, DEV-A).

Pure policy-aware gating deadness and policy source summaries, compact run views, suspicious flags and the
deterministic text/table rendering moved from ``libs.reporting.phase_runtime_health``. JSON/JSONL reads,
``_iter_run_dirs``, monitor event collection/selection, ``_persisted_monitor_surfaces`` and
``_inspect_policy_source`` (external ``normalize_monitor_entry_policy_schema``), ``main`` and clocks stay in the
facade module; helpers and constants resolve on the injected facade at call time. Observational only.
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
