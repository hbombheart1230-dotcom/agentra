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
from libs.agents.reporter.read_models import phase_health_projection as _health_projection

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
    return _health_projection._persisted_monitor_surfaces(monitor, facade=_health_sys.modules[__name__])


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
    stage = _health_projection._extract_run_health_surfaces(monitor, event_payloads, facade=_health_sys.modules[__name__])
    source_inspection = _extract_policy_source_inspection(run_dir, stage["contract"])
    return _health_projection._assemble_run_health(run_dir, monitor_json_path, monitor, event_payloads, stage, source_inspection, facade=_health_sys.modules[__name__])


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

    return _health_projection.build_runtime_health_aggregate(run_rows, day=day, reports_root=reports_root, event_log_path=event_log_path, facade=_health_sys.modules[__name__])


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
