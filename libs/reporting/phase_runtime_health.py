from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[2]

from libs.runtime.monitor_policy import normalize_monitor_entry_policy_schema
import sys as _health_sys
from libs.reporting import phase_runtime_health_projection_p15 as _health_projection  # P1.5 BATCH05-A2 owner

STRUCTURE_KEYS: Tuple[str, ...] = (
    "entry_policy_contract",
    "policy_interpretation",
    "signal_evidence",
    "policy_interpreter_trace",
    "policy_alignment_summary",
    "policy_aware_gating",
)

MONITOR_EVENT_PRIORITY: Tuple[str, ...] = (
    "monitor.entry_decision_detail",
    "monitor.entry_decision",
    "monitor.score_computed",
    "monitor.threshold_snapshot",
)

POLICY_SOURCE_NAMES: Tuple[str, ...] = (
    "commander_applied_policy",
    "strategist_output.monitor_entry_policy",
    "state.monitor_entry_policy",
    "strategy_policy.monitor_policy.entry_policy",
)


def _build_chart_structure_decision_hint_summary(rows: Any) -> Dict[str, Any]:
    from libs.reporting.chart_structure_decision_hint_summary import build_chart_structure_decision_hint_summary

    return build_chart_structure_decision_hint_summary(rows)


def _build_chart_structure_decision_hint_executive_line(summary: Dict[str, Any]) -> str:
    from libs.reporting.chart_structure_decision_hint_summary import build_chart_structure_decision_hint_executive_line

    return build_chart_structure_decision_hint_executive_line(summary)


def _build_policy_surface_quality_summary(rows: Any) -> Dict[str, Any]:
    from libs.reporting.policy_surface_summary import build_policy_surface_quality_summary

    return build_policy_surface_quality_summary(rows)

EXPLICIT_POLICY_FIELDS: Tuple[str, ...] = (
    "entry_style",
    "required_checks",
    "preferred_checks",
    "relaxable_checks",
    "blockers",
    "priority_hints",
    "evidence_focus",
    "notes",
    "policy_adjustments",
)


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return obj if isinstance(obj, dict) else {}


def _iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []

    def _gen() -> Iterable[Dict[str, Any]]:
        with path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except Exception:
                    continue
                if isinstance(row, dict):
                    yield row

    return _gen()


def _safe_list_of_str(value: Any, *, limit: int = 6) -> List[str]:
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if not isinstance(value, (list, tuple, set)):
        return []
    out: List[str] = []
    for item in value:
        text = str(item or "").strip()
        if not text or text in out:
            continue
        out.append(text)
        if len(out) >= limit:
            break
    return out


def _dict_present(value: Any) -> bool:
    return isinstance(value, Mapping) and len(value) > 0


def _pick_first_dict(*values: Any) -> Dict[str, Any]:
    for value in values:
        if _dict_present(value):
            return dict(value)
    return {}


def _pick_first_value_from_event_payloads(event_payloads: Mapping[str, Dict[str, Any]], *keys: str) -> Any:
    wanted = [str(key or "").strip() for key in keys if str(key or "").strip()]
    if not wanted:
        return None
    for event_name in MONITOR_EVENT_PRIORITY:
        payload = event_payloads.get(event_name) or {}
        if not isinstance(payload, Mapping):
            continue
        for key in wanted:
            if key in payload:
                return payload.get(key)
    return None


def _pick_latest_canonical_day(reports_root: Path) -> str:
    canonical_root = reports_root / "canonical"
    if not canonical_root.exists():
        return date.today().isoformat()
    candidates = [path.name for path in canonical_root.iterdir() if path.is_dir()]
    return sorted(candidates)[-1] if candidates else date.today().isoformat()


def _iter_run_dirs(reports_root: Path, *, day: str = "", run_ids: Optional[Sequence[str]] = None, limit: int = 50) -> List[Path]:
    canonical_root = reports_root / "canonical"
    out: List[Path] = []
    wanted = {str(run_id).strip() for run_id in list(run_ids or []) if str(run_id).strip()}
    if wanted:
        for day_dir in sorted(canonical_root.iterdir()) if canonical_root.exists() else []:
            if not day_dir.is_dir():
                continue
            for run_id in wanted:
                candidate = day_dir / run_id
                if candidate.is_dir():
                    out.append(candidate)
        seen: set[str] = set()
        deduped: List[Path] = []
        for path in out:
            if path.name in seen:
                continue
            deduped.append(path)
            seen.add(path.name)
        return deduped[: max(1, int(limit or 50))]

    effective_day = str(day or "").strip() or _pick_latest_canonical_day(reports_root)
    day_root = canonical_root / effective_day
    if not day_root.exists():
        return []
    candidates = [path for path in day_root.iterdir() if path.is_dir()]
    candidates = sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[: max(1, int(limit or 50))]


def _collect_monitor_event_payloads(
    event_log_path: Path,
    run_ids: Sequence[str],
    *,
    day: str = "",
) -> Dict[str, Dict[str, Dict[str, Any]]]:
    target_ids = {str(run_id).strip() for run_id in run_ids if str(run_id).strip()}
    out: Dict[str, Dict[str, Dict[str, Any]]] = {run_id: {} for run_id in target_ids}
    relevant_names = set(MONITOR_EVENT_PRIORITY)
    if str(day or "").strip():
        from libs.reporting.event_log_reader import iter_jsonl_events

        source_rows = iter_jsonl_events(event_log_path, day=day)
    else:
        source_rows = _iter_jsonl(event_log_path)
    for row in source_rows:
        run_id = str(row.get("run_id") or "").strip()
        if not run_id or run_id not in target_ids:
            continue
        event_name = str(row.get("event_name") or row.get("event") or "").strip()
        if event_name not in relevant_names:
            continue
        payload = row.get("payload")
        if not isinstance(payload, dict):
            continue
        out.setdefault(run_id, {})[event_name] = payload
    return out


def _get_surface_from_event_payloads(event_payloads: Mapping[str, Dict[str, Any]], surface: str) -> Dict[str, Any]:
    for event_name in MONITOR_EVENT_PRIORITY:
        payload = event_payloads.get(event_name) or {}
        if not isinstance(payload, Mapping):
            continue
        if surface == "entry_policy_contract":
            picked = payload.get("policy_contract") or payload.get("entry_policy_contract")
        else:
            picked = payload.get(surface)
        if _dict_present(picked):
            return dict(picked)
    return {}


def _persisted_grouped_logic_trace(monitor: Mapping[str, Any]) -> Dict[str, Any]:
    evaluation = monitor.get("monitor_evaluation") if isinstance(monitor.get("monitor_evaluation"), Mapping) else {}
    signal_snapshot = monitor.get("signal_snapshot") if isinstance(monitor.get("signal_snapshot"), Mapping) else {}
    return _pick_first_dict(
        monitor.get("entry_grouped_logic_trace"),
        evaluation.get("entry_grouped_logic_trace"),
        signal_snapshot.get("entry_grouped_logic_trace"),
    )


def _persisted_monitor_surfaces(monitor: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    trace = _pick_first_dict(monitor.get("policy_interpreter_trace"))
    alignment = _pick_first_dict(monitor.get("policy_alignment_summary"))
    grouped = _persisted_grouped_logic_trace(monitor)
    signal_snapshot = monitor.get("signal_snapshot") if isinstance(monitor.get("signal_snapshot"), Mapping) else {}

    selected_policy = _pick_first_dict(
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
    selected_policy_schema = normalize_monitor_entry_policy_schema(policy_for_schema)
    invalid_specs = list(selected_policy_schema.get("invalid_policy_specs") or [])
    normalized_count = sum(
        len(_safe_list_of_str(selected_policy_schema.get(key), limit=64))
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


def _failed_check_names(rows: Any, *, fail_statuses: Sequence[str]) -> List[str]:
    out: List[str] = []
    if not isinstance(rows, list):
        return out
    allowed = {str(status).strip().lower() for status in fail_statuses}
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        name = str(row.get("name") or "").strip()
        status = str(row.get("status") or "").strip().lower()
        if name and status in allowed and name not in out:
            out.append(name)
    return out


def _safe_bool(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    return None


def _safe_float(value: Any) -> Optional[float]:
    try:
        return float(value)
    except Exception:
        return None


def _source_metadata_keys(contract: Mapping[str, Any], source_name: str) -> List[str]:
    sources = contract.get("sources") if isinstance(contract.get("sources"), Mapping) else {}
    row = sources.get(source_name) if isinstance(sources.get(source_name), Mapping) else {}
    return _safe_list_of_str(row.get("keys"), limit=64)


def _field_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(str(value).strip())
    if isinstance(value, Mapping):
        return any(_field_present(v) for v in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(_field_present(v) for v in value)
    return True


def _key_only_explicit_field_presence(keys: Sequence[str]) -> Dict[str, bool]:
    key_set = {str(key or "").strip() for key in list(keys or []) if str(key or "").strip()}
    return {
        "entry_style": bool({"entry_style", "playbook"} & key_set),
        "required_checks": "required_checks" in key_set,
        "preferred_checks": "preferred_checks" in key_set,
        "relaxable_checks": "relaxable_checks" in key_set,
        "blockers": "blockers" in key_set,
        "priority_hints": "priority_hints" in key_set,
        "evidence_focus": "evidence_focus" in key_set,
        "notes": bool({"notes", "policy_notes"} & key_set),
        "policy_adjustments": "policy_adjustments" in key_set,
    }


def _inspect_policy_source(
    *,
    source_name: str,
    payload: Mapping[str, Any] | None,
    contract: Mapping[str, Any],
) -> Dict[str, Any]:
    metadata_keys = _source_metadata_keys(contract, source_name)
    payload_dict = dict(payload or {}) if isinstance(payload, Mapping) else {}
    if payload_dict:
        schema = normalize_monitor_entry_policy_schema(payload_dict)
        field_presence = {
            field_name: _field_present(schema.get(field_name))
            for field_name in EXPLICIT_POLICY_FIELDS
        }
        return {
            "source_name": str(source_name),
            "available": bool(payload_dict),
            "inspection_mode": "payload",
            "raw_keys": list(schema.get("raw_keys") or []),
            "schema_available": bool(schema.get("available")),
            "schema_version": str(schema.get("schema_version") or ""),
            "explicit_fields_used": list(schema.get("explicit_fields_used") or []),
            "field_presence": field_presence,
            "contract_keys": metadata_keys,
        }

    field_presence = _key_only_explicit_field_presence(metadata_keys)
    explicit_key_fields = [name for name, present in field_presence.items() if present]
    return {
        "source_name": str(source_name),
        "available": bool(metadata_keys),
        "inspection_mode": "contract_keys_only",
        "raw_keys": metadata_keys,
        "schema_available": None,
        "schema_version": None,
        "explicit_fields_used": explicit_key_fields,
        "field_presence": field_presence,
        "contract_keys": metadata_keys,
    }


def _extract_policy_source_inspection(
    run_dir: Path,
    contract: Mapping[str, Any],
) -> Dict[str, Dict[str, Any]]:
    commander = _read_json(run_dir / "commander.json")
    strategist = _read_json(run_dir / "strategist.json")

    commander_applied_policy = commander.get("applied_policy") if isinstance(commander.get("applied_policy"), Mapping) else {}
    strategist_monitor_entry_policy = (
        strategist.get("monitor_entry_policy") if isinstance(strategist.get("monitor_entry_policy"), Mapping) else {}
    )
    strategy_policy = strategist.get("strategy_policy") if isinstance(strategist.get("strategy_policy"), Mapping) else {}
    strategy_monitor_policy = (
        strategy_policy.get("monitor_policy") if isinstance(strategy_policy.get("monitor_policy"), Mapping) else {}
    )
    strategy_entry_policy = (
        strategy_monitor_policy.get("entry_policy") if isinstance(strategy_monitor_policy.get("entry_policy"), Mapping) else {}
    )

    return {
        "commander_applied_policy": _inspect_policy_source(
            source_name="commander_applied_policy",
            payload=commander_applied_policy,
            contract=contract,
        ),
        "strategist_output.monitor_entry_policy": _inspect_policy_source(
            source_name="strategist_output.monitor_entry_policy",
            payload=strategist_monitor_entry_policy,
            contract=contract,
        ),
        "state.monitor_entry_policy": _inspect_policy_source(
            source_name="state.monitor_entry_policy",
            payload=None,
            contract=contract,
        ),
        "strategy_policy.monitor_policy.entry_policy": _inspect_policy_source(
            source_name="strategy_policy.monitor_policy.entry_policy",
            payload=strategy_entry_policy,
            contract=contract,
        ),
    }


def _build_policy_aware_gating_deadness(rows: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    return _health_projection._build_policy_aware_gating_deadness(rows, facade=_health_sys.modules[__name__])


def _build_policy_source_summary(rows: Sequence[Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return _health_projection._build_policy_source_summary(rows, facade=_health_sys.modules[__name__])


def _compact_run_view(row: Mapping[str, Any]) -> Dict[str, Any]:
    return _health_projection._compact_run_view(row, facade=_health_sys.modules[__name__])


def _build_suspicious_flags(*, final_decision: str, alignment_summary: Mapping[str, Any], trace: Mapping[str, Any], gating: Mapping[str, Any]) -> List[str]:
    return _health_projection._build_suspicious_flags(final_decision=final_decision, alignment_summary=alignment_summary, trace=trace, gating=gating, facade=_health_sys.modules[__name__])


def _extract_run_health(run_dir: Path, event_payloads: Mapping[str, Dict[str, Any]]) -> Dict[str, Any]:
    monitor_json_path = run_dir / "monitor.json"
    monitor = _read_json(monitor_json_path)
    final_decision = str(monitor.get("decision") or "").strip().upper()
    reason = (
        str(monitor.get("entry_reason") or "").strip()
        or str(monitor.get("monitor_reason") or "").strip()
        or str(monitor.get("primary_reason_code") or "").strip()
        or str(monitor.get("decision_summary") or "").strip()
    )

    persisted_surfaces = _persisted_monitor_surfaces(monitor)
    surfaces = {
        key: _pick_first_dict(
            _get_surface_from_event_payloads(event_payloads, key),
            persisted_surfaces.get(key),
        )
        for key in STRUCTURE_KEYS
    }
    contract = surfaces["entry_policy_contract"]
    interpretation = surfaces["policy_interpretation"]
    evidence = surfaces["signal_evidence"]
    trace = surfaces["policy_interpreter_trace"]
    alignment = surfaces["policy_alignment_summary"]
    gating = surfaces["policy_aware_gating"]
    chart_structure_decision_hint = _pick_first_dict(
        _get_surface_from_event_payloads(event_payloads, "chart_structure_decision_hint"),
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
    source_inspection = _extract_policy_source_inspection(run_dir, contract)

    structure_presence = {key: _dict_present(value) for key, value in surfaces.items()}
    selected_policy = contract.get("selected_policy") if isinstance(contract.get("selected_policy"), Mapping) else {}
    selected_source = str(contract.get("selected_source") or "").strip()
    source_priority = _safe_list_of_str(contract.get("source_priority"), limit=10)
    interpretation_basis = str(interpretation.get("interpretation_basis") or "").strip()
    policy_schema_available = interpretation.get("policy_schema_available")
    policy_schema_version = str(interpretation.get("policy_schema_version") or "").strip()
    alignment_state = str(alignment.get("alignment_state") or "").strip()
    primary_blocker = str(alignment.get("primary_blocker") or "").strip()
    secondary_blockers = _safe_list_of_str(alignment.get("secondary_blockers"))
    entry_style = str(interpretation.get("entry_style") or "").strip().lower() or None
    spec_validation_notes = _safe_list_of_str(
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
            len(_safe_list_of_str(selected_policy_schema.get(key), limit=64))
            for key in ("required_checks", "preferred_checks", "relaxable_checks", "blockers")
        )
    )
    policy_schema_explicit_fields_used = _safe_list_of_str(
        selected_policy_spec_health.get("explicit_fields_used")
        or selected_policy_schema.get("explicit_fields_used"),
        limit=32,
    )
    policy_schema_raw_keys = _safe_list_of_str(
        selected_policy_spec_health.get("raw_keys")
        or selected_policy_schema.get("raw_keys"),
        limit=64,
    )
    required_failures = _failed_check_names(((trace.get("check_status") or {}) if isinstance(trace.get("check_status"), Mapping) else {}).get("required"), fail_statuses=("fail",))
    preferred_failures = _failed_check_names(((trace.get("check_status") or {}) if isinstance(trace.get("check_status"), Mapping) else {}).get("preferred"), fail_statuses=("fail",))
    relaxable_failures = _failed_check_names(((trace.get("check_status") or {}) if isinstance(trace.get("check_status"), Mapping) else {}).get("relaxable"), fail_statuses=("fail",))
    blockers_active = _failed_check_names(((trace.get("check_status") or {}) if isinstance(trace.get("check_status"), Mapping) else {}).get("blockers"), fail_statuses=("active",))
    evidence_checks = evidence.get("checks") if isinstance(evidence.get("checks"), Mapping) else {}
    evidence_derived = evidence.get("derived") if isinstance(evidence.get("derived"), Mapping) else {}
    legacy_entry_decision = str(
        _pick_first_value_from_event_payloads(event_payloads, "legacy_entry_decision")
        or monitor.get("legacy_entry_decision")
        or ""
    ).strip().upper() or None
    legacy_entry_reason = str(
        _pick_first_value_from_event_payloads(event_payloads, "legacy_entry_reason", "entry_reason")
        or monitor.get("legacy_entry_reason")
        or monitor.get("entry_reason")
        or ""
    ).strip() or None
    suspicious = _build_suspicious_flags(
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
        "reclaim_gate_ok": _safe_bool(evidence_checks.get("reclaim_gate_ok")),
        "breakout_path_ok": _safe_bool(evidence_checks.get("breakout_path_ok")),
        "confidence_ok": _safe_bool(evidence_checks.get("confidence_ok")),
        "volume_ok": _safe_bool(evidence_checks.get("volume_ok")),
        "too_extended": _safe_bool(evidence_derived.get("too_extended")),
        "reclaim_distance_to_ready": _safe_float(evidence_derived.get("reclaim_distance_to_ready")),
        "top_failed_required_checks": required_failures,
        "top_failed_preferred_checks": preferred_failures,
        "top_relaxable_gaps": relaxable_failures,
        "active_blockers": blockers_active,
        "policy_aware_gating": {
            "available": bool(gating.get("available")) if _dict_present(gating) else False,
            "applied": bool(gating.get("applied")) if _dict_present(gating) else False,
            "applied_hints": _safe_list_of_str(gating.get("applied_hints")),
            "required_failures": _safe_list_of_str(gating.get("required_failures")),
            "relaxations_considered": _safe_list_of_str(gating.get("relaxations_considered")),
            "relaxations_applied": _safe_list_of_str(gating.get("relaxations_applied")),
            "blocked_by_required": _safe_list_of_str(gating.get("blocked_by_required")),
            "notes": _safe_list_of_str(gating.get("notes")),
        },
        "chart_structure_decision_hint": {
            "available": bool(chart_structure_decision_hint.get("available")) if _dict_present(chart_structure_decision_hint) else False,
            "applied": bool(chart_structure_decision_hint.get("applied")) if _dict_present(chart_structure_decision_hint) else False,
            "mode": str(chart_structure_decision_hint.get("mode") or "none"),
            "entry_style": str(chart_structure_decision_hint.get("entry_style") or ""),
            "considered_features": _safe_list_of_str(chart_structure_decision_hint.get("considered_features")),
            "matched_features": _safe_list_of_str(chart_structure_decision_hint.get("matched_features")),
            "blocking_features": _safe_list_of_str(chart_structure_decision_hint.get("blocking_features")),
            "notes": _safe_list_of_str(chart_structure_decision_hint.get("notes")),
        },
        "policy_source_inspection": source_inspection,
        "suspicious_flags": suspicious,
    }


def build_phase_5_2_5_3_runtime_health(
    *,
    reports_root: Path,
    event_log_path: Path,
    day: str = "",
    run_ids: Optional[Sequence[str]] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    run_dirs = _iter_run_dirs(reports_root, day=day, run_ids=run_ids, limit=limit)
    if not run_dirs:
        raise FileNotFoundError(f"No canonical monitor runs found for day={day!r} run_ids={list(run_ids or [])!r}")

    event_payloads = _collect_monitor_event_payloads(event_log_path, [path.name for path in run_dirs], day=day)
    run_rows = [_extract_run_health(path, event_payloads.get(path.name, {})) for path in run_dirs]

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

    for structure in STRUCTURE_KEYS:
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
        for note in _safe_list_of_str(row.get("spec_validation_notes"), limit=64):
            policy_validation_notes_counts[note] += 1
            basis_notes[note] += 1

        gating = row.get("policy_aware_gating") if isinstance(row.get("policy_aware_gating"), Mapping) else {}
        if bool(gating.get("applied")):
            gating_applied_true += 1
        if _safe_list_of_str(gating.get("blocked_by_required")):
            gating_required_blocked += 1
        for hint in _safe_list_of_str(gating.get("applied_hints"), limit=20):
            gating_hint_counts[hint] += 1
        for flag in _safe_list_of_str(row.get("suspicious_flags"), limit=20):
            suspicious_counts[flag] += 1

    suspicious_runs = [row for row in run_rows if row.get("suspicious_flags")]
    buy_runs = [_compact_run_view(row) for row in run_rows if str(row.get("final_decision") or "").upper() == "BUY"]
    reclaim_wait_runs = [
        _compact_run_view(row)
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
        "policy_source_field_presence": _build_policy_source_summary(run_rows),
        "policy_aware_gating_deadness": _build_policy_aware_gating_deadness(run_rows),
        "chart_structure_decision_hint_summary": _build_chart_structure_decision_hint_summary(run_rows),
        "final_decision_counts": dict(decision_counts),
        "suspicious_counts": dict(suspicious_counts),
        "suspicious_runs": suspicious_runs,
        "buy_runs": buy_runs,
        "reclaim_wait_runs": reclaim_wait_runs,
        "policy_surface_quality_summary": _build_policy_surface_quality_summary(
            [row for row in run_rows if bool(row.get("policy_evaluable"))]
        ),
        "runs": run_rows,
    }
    return out


def _render_text_table(rows: Sequence[Mapping[str, Any]]) -> str:
    return _health_projection._render_text_table(rows, facade=_health_sys.modules[__name__])


def _render_compact_run_table(rows: Sequence[Mapping[str, Any]]) -> str:
    return _health_projection._render_compact_run_table(rows, facade=_health_sys.modules[__name__])


def _render_reclaim_table(rows: Sequence[Mapping[str, Any]]) -> str:
    return _health_projection._render_reclaim_table(rows, facade=_health_sys.modules[__name__])


def render_phase_5_2_5_3_runtime_health_text(payload: Mapping[str, Any]) -> str:
    return _health_projection.render_phase_5_2_5_3_runtime_health_text(payload, facade=_health_sys.modules[__name__])


def render_policy_surface_quality_summary_text(day: str, summary: Mapping[str, Any] | None) -> str:
    return _health_projection.render_policy_surface_quality_summary_text(day, summary, facade=_health_sys.modules[__name__])


def render_chart_structure_decision_hint_summary_text(day: str, summary: Mapping[str, Any] | None) -> str:
    return _health_projection.render_chart_structure_decision_hint_summary_text(day, summary, facade=_health_sys.modules[__name__])


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect phase 5-2 ~ 5-3 runtime surfaces from canonical monitor artifacts and monitor event payloads."
    )
    parser.add_argument("--reports-root", default="reports")
    parser.add_argument("--event-log-path", default="data/logs/events.jsonl")
    parser.add_argument("--date", default="", help="Canonical day (YYYY-MM-DD). Defaults to latest canonical day.")
    parser.add_argument("--run-id", action="append", default=[], help="Specific run_id(s) to inspect. May be repeated.")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--only-buy", action="store_true", help="Print only recent BUY run table after aggregation.")
    parser.add_argument("--reason", default="", help="Filter compact run view by exact legacy/final reason.")
    parser.add_argument("--show-reclaim-near-ready", action="store_true", help="Print reclaim WAIT table with near-ready fields.")
    parser.add_argument("--show-policy-summary", action="store_true", help="Print only compact policy surface quality summary.")
    parser.add_argument("--show-chart-structure-summary", action="store_true", help="Print only compact chart structure decision hint summary.")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    reports_root = Path(str(args.reports_root).strip())
    event_log_path = Path(str(args.event_log_path).strip())
    if not reports_root.is_absolute():
        reports_root = ROOT / reports_root
    if not event_log_path.is_absolute():
        event_log_path = ROOT / event_log_path

    try:
        out = build_phase_5_2_5_3_runtime_health(
            reports_root=reports_root,
            event_log_path=event_log_path,
            day=str(args.date).strip(),
            run_ids=list(args.run_id or []),
            limit=max(1, int(args.limit or 50)),
        )
    except FileNotFoundError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2

    if bool(args.json):
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        if bool(args.only_buy):
            print(_render_compact_run_table(out.get("buy_runs") if isinstance(out.get("buy_runs"), list) else []))
            return 0
        if str(args.reason or "").strip():
            wanted = str(args.reason or "").strip()
            matched = [
                _compact_run_view(row)
                for row in list(out.get("runs") or [])
                if str(row.get("legacy_entry_reason") or row.get("reason") or "").strip() == wanted
            ]
            print(_render_compact_run_table(matched))
            return 0
        if bool(args.show_reclaim_near_ready):
            print(_render_reclaim_table(out.get("reclaim_wait_runs") if isinstance(out.get("reclaim_wait_runs"), list) else []))
            return 0
        if bool(args.show_policy_summary):
            print(
                render_policy_surface_quality_summary_text(
                    str(out.get("day") or ""),
                    out.get("policy_surface_quality_summary") if isinstance(out.get("policy_surface_quality_summary"), Mapping) else {},
                )
            )
            return 0
        if bool(args.show_chart_structure_summary):
            print(
                render_chart_structure_decision_hint_summary_text(
                    str(out.get("day") or ""),
                    out.get("chart_structure_decision_hint_summary") if isinstance(out.get("chart_structure_decision_hint_summary"), Mapping) else {},
                )
            )
            return 0
        print(render_phase_5_2_5_3_runtime_health_text(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
