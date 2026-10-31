from __future__ import annotations

# Direct execution from the deeper scripts package retains repository imports.
import sys as _migration_sys
from pathlib import Path as _MigrationPath
_migration_root = _MigrationPath(__file__).resolve().parents[2]
if str(_migration_root) not in _migration_sys.path:
    _migration_sys.path.insert(0, str(_migration_root))

import argparse
import json
import os
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from libs.diagnostics.observations import broker_code_success
from libs.diagnostics.observations import numeric_summary
from libs.reporting.event_log_reader import iter_jsonl_events


def _iter_events(path: Path) -> Iterable[Dict[str, Any]]:
    return iter_jsonl_events(path)


def _to_epoch(ts: Any) -> Optional[int]:
    from scripts.diagnostics.ops_diagnostic_scalar_projection import _to_epoch as owner
    return owner(ts, facade=_migration_sys.modules[__name__])


def _utc_day(ts: Any) -> str:
    from scripts.diagnostics.ops_diagnostic_scalar_projection import _utc_day as owner
    return owner(ts, facade=_migration_sys.modules[__name__])


def _to_float(v: Any) -> Optional[float]:
    from scripts.diagnostics.ops_diagnostic_scalar_projection import _to_float as owner
    return owner(v, facade=_migration_sys.modules[__name__])


def _numeric_summary(values: List[float]) -> Dict[str, float]:
    return numeric_summary(values)


def _broker_code_success(value: Any) -> Optional[bool]:
    return broker_code_success(value)


def _extract_noop_reason(payload: Dict[str, Any]) -> str:
    from scripts.diagnostics.ops_diagnostic_summary_projection import _extract_noop_reason as owner
    return owner(payload, facade=_migration_sys.modules[__name__])


def _build_summary(rows: List[Dict[str, Any]], *, day: str) -> Dict[str, Any]:
    from scripts.diagnostics.ops_diagnostic_summary_projection import _build_summary as owner
    return owner(rows, day=day, facade=_migration_sys.modules[__name__])
def _build_markdown(summary: Dict[str, Any]) -> str:
    from scripts.diagnostics.ops_diagnostic_markdown_projection import _build_markdown as owner
    return owner(summary, facade=_migration_sys.modules[__name__])
def generate_ops_diagnostic_report(events_path: Path, out_dir: Path, day: str | None = None) -> Tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: List[Dict[str, Any]] = []
    for e in _iter_events(events_path):
        ts = e.get("ts") or (e.get("payload") or {}).get("ts")
        rows.append({**e, "_day": _utc_day(ts)})

    if not rows:
        day = day or date.today().isoformat()
        summary = {
            "schema_version": "ops_diagnostic.v1",
            "day": day,
            "events": 0,
            "runs": 0,
            "execution": {
                "execution_total": 0,
                "verdict_block_total": 0,
                "verdict_reason_topN": [],
                "broker_success_total": 0,
                "broker_fail_total": 0,
                "broker_unknown_total": 0,
                "broker_success_rate": 0.0,
                "broker_code_topN": [],
                "broker_failure_topN": [],
            },
            "noop": {"total": 0, "reason_total": {}, "reason_ratio": {}, "focus_reason_ratio": {}},
            "strategist_llm": {"total": 0, "ok_total": 0, "error_total": 0, "latency_ms": _numeric_summary([])},
        }
    else:
        if day is None:
            day = sorted({str(r.get("_day") or "") for r in rows})[-1]
        day_rows = [r for r in rows if str(r.get("_day") or "") == day]
        summary = _build_summary(day_rows, day=str(day))

    md_path = out_dir / f"ops_diagnostic_{day}.md"
    json_path = out_dir / f"ops_diagnostic_{day}.json"
    md_path.write_text(_build_markdown(summary) + "\n", encoding="utf-8")
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return md_path, json_path


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(
        description="Generate daily ops diagnostic report (broker failures / NOOP reasons / LLM latency)."
    )
    p.add_argument("--event-log-path", default=os.getenv("EVENT_LOG_PATH", "./data/logs/events.jsonl"))
    p.add_argument("--report-dir", default="./reports/dev/analysis/ops_diagnostic")
    p.add_argument("--day", default="", help="UTC day in YYYY-MM-DD. Default: latest day in log.")
    p.add_argument("--json", action="store_true", help="Print summary JSON to stdout.")
    args = p.parse_args(argv)

    events_path = Path(str(args.event_log_path).strip())
    report_dir = Path(str(args.report_dir).strip())
    day = str(args.day or "").strip() or None
    md_path, json_path = generate_ops_diagnostic_report(events_path, report_dir, day=day)

    if args.json:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        print(json.dumps(data, ensure_ascii=False))
    else:
        print(f"Wrote: {md_path}")
        print(f"Wrote: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

