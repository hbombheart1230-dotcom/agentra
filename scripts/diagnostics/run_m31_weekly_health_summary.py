from __future__ import annotations

# Direct execution from the deeper scripts package retains repository imports.
import sys as _migration_sys
from pathlib import Path as _MigrationPath
_migration_root = _MigrationPath(__file__).resolve().parents[2]
if str(_migration_root) not in _migration_sys.path:
    _migration_sys.path.insert(0, str(_migration_root))

import argparse
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from libs.reporting.event_log_reader import iter_jsonl_events


def _to_epoch(ts: Any) -> Optional[int]:
    from scripts.diagnostics.m31_weekly_time_projection import _to_epoch as owner
    return owner(ts, facade=_migration_sys.modules[__name__])


def _utc_day(ts: Any) -> Optional[str]:
    from scripts.diagnostics.m31_weekly_time_projection import _utc_day as owner
    return owner(ts, facade=_migration_sys.modules[__name__])


def _iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    return iter_jsonl_events(path)


def _read_json(path: Path) -> Dict[str, Any]:
    from scripts.diagnostics.m31_weekly_read_projection import _read_json as owner
    return owner(path, facade=_migration_sys.modules[__name__])


def _parse_day(value: str) -> datetime:
    from scripts.diagnostics.m31_weekly_time_projection import _parse_day as owner
    return owner(value, facade=_migration_sys.modules[__name__])


def _window_days(*, week_end: str, days: int) -> List[str]:
    from scripts.diagnostics.m31_weekly_time_projection import _window_days as owner
    return owner(week_end=week_end, days=days, facade=_migration_sys.modules[__name__])


def _item(
    *,
    item_id: str,
    title: str,
    passed: bool,
    evidence: str,
    required: bool = True,
) -> Dict[str, Any]:
    from scripts.diagnostics.m31_weekly_summary_projection import _item as owner
    return owner(item_id=item_id,title=title,passed=passed,evidence=evidence,required=required)


def _build_markdown(out: Dict[str, Any]) -> str:
    from scripts.diagnostics.m31_weekly_markdown_projection import _build_markdown as owner
    return owner(out)


def _build_parser() -> argparse.ArgumentParser:
    from scripts.diagnostics.m31_weekly_cli_projection import _build_parser as owner
    return owner(facade=_migration_sys.modules[__name__])


def main(argv: Optional[List[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    event_log_path = Path(str(args.event_log_path).strip())
    policy_report_dir = Path(str(args.policy_report_dir).strip())
    signoff_report_dir = Path(str(args.signoff_report_dir).strip())
    report_dir = Path(str(args.report_dir).strip())
    week_end = str(args.week_end or "2026-02-21").strip()
    days = max(1, int(args.days))
    max_error_rate = max(0.0, float(args.max_error_rate))
    max_incident_days = max(0, int(args.max_incident_days))
    inject_fail = bool(args.inject_fail)

    window = _window_days(week_end=week_end, days=days)
    week_start = window[0]
    day_set = set(window)

    report_dir.mkdir(parents=True, exist_ok=True)

    event_total = 0
    event_error_total = 0
    run_ids: set[str] = set()
    stage_error_total: Counter[str] = Counter()
    daily_event_total: Counter[str] = Counter()
    daily_error_total: Counter[str] = Counter()

    for row in _iter_jsonl(event_log_path):
        day = _utc_day(row.get("ts"))
        if not day or day not in day_set:
            continue
        event_total += 1
        daily_event_total[day] += 1
        rid = str(row.get("run_id") or "").strip()
        if rid:
            run_ids.add(rid)
        ev = str(row.get("event") or "").strip().lower()
        if ev == "error":
            event_error_total += 1
            daily_error_total[day] += 1
            st = str(row.get("stage") or "unknown").strip() or "unknown"
            stage_error_total[st] += 1

    error_rate = (float(event_error_total) / float(event_total)) if event_total > 0 else 0.0

    level_total: Counter[str] = Counter()
    policy_rows: List[Dict[str, Any]] = []
    incident_manual_approval_violation_total = 0
    for day in window:
        path = policy_report_dir / f"m30_post_golive_policy_{day}.json"
        obj = _read_json(path)
        if not obj:
            continue
        level = str(obj.get("escalation_level") or "").strip().lower()
        policy = obj.get("policy") if isinstance(obj.get("policy"), dict) else {}
        manual_only = bool(policy.get("manual_approval_only"))
        level_total[level] += 1
        if level == "incident" and not manual_only:
            incident_manual_approval_violation_total += 1
        policy_rows.append(
            {
                "day": day,
                "path": str(path),
                "escalation_level": level,
                "manual_approval_only": manual_only,
            }
        )

    signoff_rows: List[Dict[str, Any]] = []
    approved_day_total = 0
    hold_day_total = 0
    for day in window:
        path = signoff_report_dir / f"m30_final_golive_signoff_{day}.json"
        obj = _read_json(path)
        if not obj:
            continue
        approved = bool(obj.get("approved"))
        decision = str(obj.get("go_live_decision") or "").strip()
        if approved:
            approved_day_total += 1
        else:
            hold_day_total += 1
        signoff_rows.append(
            {
                "day": day,
                "path": str(path),
                "approved": approved,
                "go_live_decision": decision,
            }
        )

    checklist: List[Dict[str, Any]] = [
        _item(
            item_id="policy_artifact_presence",
            title="Post-go-live policy artifacts exist in weekly window",
            passed=len(policy_rows) >= 1,
            evidence=f"policy_found_total={len(policy_rows)}",
        ),
        _item(
            item_id="event_error_rate_guard",
            title="Weekly event error rate stays within threshold",
            passed=error_rate <= max_error_rate,
            evidence=f"error_rate={error_rate:.4f}, threshold={max_error_rate:.4f}",
        ),
        _item(
            item_id="incident_day_guard",
            title="Incident escalation day count stays within threshold",
            passed=int(level_total.get("incident", 0)) <= max_incident_days,
            evidence=f"incident_day_total={int(level_total.get('incident', 0))}, threshold={max_incident_days}",
        ),
        _item(
            item_id="incident_manual_mode_guard",
            title="Incident-level policy always enforces manual approval",
            passed=incident_manual_approval_violation_total == 0,
            evidence=f"incident_manual_approval_violation_total={incident_manual_approval_violation_total}",
        ),
        _item(
            item_id="signoff_artifact_presence",
            title="Final signoff artifacts present in weekly window",
            passed=len(signoff_rows) >= 1,
            evidence=f"signoff_found_total={len(signoff_rows)}",
            required=False,
        ),
    ]

    failures: List[str] = []
    for row in checklist:
        if bool(row.get("required")) and not bool(row.get("passed")):
            failures.append(f"check_failed:{row.get('id')}")
    if inject_fail:
        failures.append("inject_fail forced red-path for operator drill")

    required_total = int(sum(1 for x in checklist if bool(x.get("required"))))
    required_pass_total = int(sum(1 for x in checklist if bool(x.get("required")) and bool(x.get("passed"))))
    required_fail_total = int(required_total - required_pass_total)
    ok = len(failures) == 0 and not inject_fail

    out: Dict[str, Any] = {
        "ok": bool(ok),
        "inject_fail": inject_fail,
        "week_start": week_start,
        "week_end": week_end,
        "window_days": window,
        "event_log_path": str(event_log_path),
        "policy_report_dir": str(policy_report_dir),
        "signoff_report_dir": str(signoff_report_dir),
        "report_dir": str(report_dir),
        "thresholds": {
            "max_error_rate": max_error_rate,
            "max_incident_days": max_incident_days,
        },
        "events": {
            "total": int(event_total),
            "error_total": int(event_error_total),
            "error_rate": float(error_rate),
            "run_total": int(len(run_ids)),
            "daily_total": {k: int(v) for k, v in sorted(daily_event_total.items())},
            "daily_error_total": {k: int(v) for k, v in sorted(daily_error_total.items())},
            "stage_error_top": dict(stage_error_total.most_common(5)),
        },
        "policy": {
            "found_total": int(len(policy_rows)),
            "normal_day_total": int(level_total.get("normal", 0)),
            "watch_day_total": int(level_total.get("watch", 0)),
            "incident_day_total": int(level_total.get("incident", 0)),
            "incident_manual_approval_violation_total": int(incident_manual_approval_violation_total),
            "rows": policy_rows,
        },
        "signoff": {
            "found_total": int(len(signoff_rows)),
            "approved_day_total": int(approved_day_total),
            "hold_day_total": int(hold_day_total),
            "rows": signoff_rows,
        },
        "checklist": checklist,
        "required_total": required_total,
        "required_pass_total": required_pass_total,
        "required_fail_total": required_fail_total,
        "failure_total": int(len(failures)),
        "failures": failures,
    }

    js_path = report_dir / f"m31_weekly_health_{week_start}_to_{week_end}.json"
    md_path = report_dir / f"m31_weekly_health_{week_start}_to_{week_end}.md"
    out["report_json_path"] = str(js_path)
    out["report_md_path"] = str(md_path)
    js_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(_build_markdown(out), encoding="utf-8")

    if bool(args.json):
        print(json.dumps(out, ensure_ascii=False))
    else:
        print(
            f"ok={out['ok']} week={week_start}..{week_end} "
            f"event_total={out['events']['total']} error_rate={out['events']['error_rate']:.2%} "
            f"incident_day_total={out['policy']['incident_day_total']} "
            f"failure_total={out['failure_total']}"
        )
        for msg in failures:
            print(msg)
    return 0 if bool(ok) else 3


if __name__ == "__main__":
    raise SystemExit(main())
