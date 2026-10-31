from __future__ import annotations

# Direct execution from the deeper scripts package retains repository imports.
import sys as _migration_sys
from pathlib import Path as _MigrationPath
_migration_root = _MigrationPath(__file__).resolve().parents[2]
if str(_migration_root) not in _migration_sys.path:
    _migration_sys.path.insert(0, str(_migration_root))

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from libs.diagnostics.observations import numeric_summary
from libs.reporting.event_log_reader import iter_jsonl_events


def _to_epoch(ts: Any) -> Optional[int]:
    from scripts.diagnostics.incident_timeline_time_projection import _to_epoch as owner
    return owner(ts, facade=_migration_sys.modules[__name__])


def _utc_day(ts: Any) -> str:
    epoch = _to_epoch(ts)
    if epoch is None:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("%Y-%m-%d")


def _iter_rows(path: Path) -> List[Dict[str, Any]]:
    return list(iter_jsonl_events(path))


def _numeric_summary(values: List[float]) -> Dict[str, float]:
    return numeric_summary(values)


def _incident_trigger(row: Dict[str, Any]) -> Tuple[bool, str]:
    from scripts.diagnostics.incident_timeline_trigger_projection import _incident_trigger as owner
    return owner(row)


def _is_recovery(row: Dict[str, Any]) -> Tuple[bool, str]:
    from scripts.diagnostics.incident_timeline_recovery_projection import _is_recovery as owner
    return owner(row)


def _event_reason(row: Dict[str, Any]) -> str:
    from scripts.diagnostics.incident_timeline_reason_projection import _event_reason as owner
    return owner(row)


def _build_markdown(out: Dict[str, Any]) -> str:
    from scripts.diagnostics.incident_timeline_markdown_projection import _build_markdown as owner
    return owner(out)


def _build_parser() -> argparse.ArgumentParser:
    from scripts.diagnostics.incident_timeline_cli_projection import _build_parser as owner
    return owner(facade=_migration_sys.modules[__name__])


def main(argv: Optional[List[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    events_path = Path(str(args.event_log_path).strip())
    report_dir = Path(str(args.report_dir).strip())
    report_dir.mkdir(parents=True, exist_ok=True)

    all_rows = _iter_rows(events_path)
    rows: List[Dict[str, Any]] = []
    for i, row in enumerate(all_rows):
        ts = row.get("ts") or ((row.get("payload") or {}).get("ts") if isinstance(row.get("payload"), dict) else None)
        epoch = _to_epoch(ts)
        rows.append({**row, "_idx": i, "_epoch": epoch, "_day": _utc_day(ts)})

    day = str(args.day or "").strip()
    if not day:
        days = sorted({str(r.get("_day") or "") for r in rows if str(r.get("_day") or "").strip()})
        day = days[-1] if days else datetime.now(timezone.utc).strftime("%Y-%m-%d")

    day_rows = [r for r in rows if str(r.get("_day") or "") == day]
    run_id_filter = str(args.run_id or "").strip()
    if run_id_filter:
        day_rows = [r for r in day_rows if str(r.get("run_id") or "") == run_id_filter]

    sorted_rows = sorted(day_rows, key=lambda r: (int(r.get("_epoch") or 0), int(r.get("_idx") or 0)))
    runs = {str(r.get("run_id") or "") for r in sorted_rows if str(r.get("run_id") or "").strip()}

    incident_rows: List[Tuple[Dict[str, Any], str]] = []
    trigger_total: Dict[str, int] = {}
    for row in sorted_rows:
        ok, trigger = _incident_trigger(row)
        if not ok:
            continue
        incident_rows.append((row, trigger))
        trigger_total[trigger] = int(trigger_total.get(trigger) or 0) + 1

    before_sec = max(0, int(args.window_before_sec or 0))
    after_sec = max(1, int(args.window_after_sec or 1))
    incidents: List[Dict[str, Any]] = []
    recovery_total: Dict[str, int] = {}
    ttr_values: List[float] = []

    for idx, (trigger_row, trigger_key) in enumerate(incident_rows, start=1):
        run_id = str(trigger_row.get("run_id") or "").strip()
        trigger_epoch = int(trigger_row.get("_epoch") or 0)
        start_epoch = trigger_epoch - before_sec
        end_epoch = trigger_epoch + after_sec

        window_rows: List[Dict[str, Any]] = []
        for row in sorted_rows:
            epoch = int(row.get("_epoch") or 0)
            if epoch < start_epoch or epoch > end_epoch:
                continue
            if run_id and str(row.get("run_id") or "").strip() != run_id:
                continue
            window_rows.append(row)

        recovery_epoch: Optional[int] = None
        recovery_type = ""
        for row in window_rows:
            epoch = int(row.get("_epoch") or 0)
            if epoch < trigger_epoch:
                continue
            is_recovery, typ = _is_recovery(row)
            if not is_recovery:
                continue
            recovery_epoch = epoch
            recovery_type = typ
            break

        recovered = recovery_epoch is not None
        ttr_sec: Optional[float] = None
        if recovery_epoch is not None:
            ttr_sec = float(recovery_epoch - trigger_epoch)
            ttr_values.append(float(ttr_sec))
            recovery_total[recovery_type] = int(recovery_total.get(recovery_type) or 0) + 1

        stage_event_total: Dict[str, int] = {}
        event_slice: List[Dict[str, Any]] = []
        for row in window_rows[:80]:
            key = f"{str(row.get('stage') or '')}:{str(row.get('event') or '')}"
            stage_event_total[key] = int(stage_event_total.get(key) or 0) + 1
            event_slice.append(
                {
                    "ts": row.get("ts"),
                    "run_id": row.get("run_id"),
                    "stage": row.get("stage"),
                    "event": row.get("event"),
                    "reason": _event_reason(row),
                }
            )

        incidents.append(
            {
                "incident_id": f"INC-{day.replace('-', '')}-{idx:03d}",
                "run_id": run_id,
                "trigger_ts": trigger_row.get("ts"),
                "trigger_stage": trigger_row.get("stage"),
                "trigger_event": trigger_row.get("event"),
                "trigger_type": trigger_key,
                "trigger_reason": _event_reason(trigger_row),
                "window_start_epoch": int(start_epoch),
                "window_end_epoch": int(end_epoch),
                "event_total_in_window": int(len(window_rows)),
                "stage_event_total_in_window": stage_event_total,
                "recovered": bool(recovered),
                "recovery_type": recovery_type,
                "recovery_ts": (
                    datetime.fromtimestamp(recovery_epoch, tz=timezone.utc).replace(microsecond=0).isoformat()
                    if recovery_epoch is not None
                    else ""
                ),
                "time_to_recovery_sec": ttr_sec,
                "events": event_slice,
            }
        )

    incident_total = int(len(incidents))
    recovered_incident_total = int(sum(1 for x in incidents if bool(x.get("recovered"))))
    unresolved_incident_total = int(incident_total - recovered_incident_total)

    failures: List[str] = []
    if bool(args.require_incidents) and incident_total < 1:
        failures.append("incident_total < 1")
    if bool(args.require_recovered) and unresolved_incident_total > 0:
        failures.append("unresolved_incident_total > 0")

    out: Dict[str, Any] = {
        "ok": len(failures) == 0,
        "day": day,
        "event_log_path": str(events_path),
        "events": int(len(sorted_rows)),
        "runs": int(len(runs)),
        "incident_total": incident_total,
        "recovered_incident_total": recovered_incident_total,
        "unresolved_incident_total": unresolved_incident_total,
        "trigger_total": trigger_total,
        "recovery_total": recovery_total,
        "ttr_sec": _numeric_summary(ttr_values),
        "incidents": incidents,
        "failures": failures,
    }

    js_path = report_dir / f"incident_timeline_{day}.json"
    md_path = report_dir / f"incident_timeline_{day}.md"
    out["report_json_path"] = str(js_path)
    out["report_md_path"] = str(md_path)
    js_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(_build_markdown(out), encoding="utf-8")

    if bool(args.json):
        print(json.dumps(out, ensure_ascii=False))
    else:
        print(
            f"ok={out['ok']} day={day} incident_total={incident_total} "
            f"recovered_incident_total={recovered_incident_total} unresolved_incident_total={unresolved_incident_total}"
        )
        for msg in failures:
            print(msg)

    return 0 if len(failures) == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
