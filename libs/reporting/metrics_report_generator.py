from __future__ import annotations

import json
import os
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from libs.reporting.event_log_reader import iter_jsonl_events
from libs.reporting.report_metadata import (
    build_data_freshness,
    build_route_provenance,
)
from libs.reporting.metrics_report.event_extractors import (
    extract_api_id as _extract_api_id,
    extract_guard_reason as _extract_guard_reason,
    extract_intent_action as _extract_intent_action,
    extract_skill_error_tag as _extract_skill_error_tag,
    is_429_error_row as _is_429_error_row,
    looks_like_429 as _looks_like_429,
    to_non_negative_int as _to_non_negative_int,
)
from libs.reporting.metrics_report.aggregators import (
    build_event_rows as _build_event_rows,
    epoch_to_iso as _epoch_to_iso,
    empty_metrics_summary as _empty_metrics_summary,
    latency_summary as _latency_summary,
    numeric_summary as _numeric_summary,
    utc_now_iso as _utc_now_iso,
)
from libs.reporting.metrics_report.markdown import (
    render_empty_metrics_markdown as _render_empty_metrics_markdown,
    render_metrics_markdown as _render_metrics_markdown,
)
from libs.reporting.report_source_helpers import build_commander_route_summary
from libs.core.path_isolation import resolve_runtime_write_path
import sys as _metrics_sys
from libs.agents.reporter.read_models import metrics_projection as _metrics_projection


def _iter_events(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []

    def gen() -> Iterable[Dict[str, Any]]:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if isinstance(obj, dict):
                    yield obj

    return gen()


def generate_metrics_report(events_path: Path, out_dir: Path, day: str | None = None) -> Tuple[Path, Path]:
    """Generate daily metrics summary (MD + JSON) from events.jsonl."""
    out_dir = resolve_runtime_write_path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    source_rows = iter_jsonl_events(events_path, day=day) if day else _iter_events(events_path)
    rows = _build_event_rows(source_rows)

    if not rows:
        day = day or date.today().isoformat()
        md_path = out_dir / f"metrics_{day}.md"
        js_path = out_dir / f"metrics_{day}.json"
        empty = _empty_metrics_summary(day)
        md_path.write_text(_render_empty_metrics_markdown(day), encoding="utf-8")
        js_path.write_text(json.dumps(empty, ensure_ascii=False, indent=2), encoding="utf-8")
        return md_path, js_path

    day = day or sorted({str(r.get("_day")) for r in rows})[-1]
    day_rows = [r for r in rows if str(r.get("_day")) == day]

    metrics_acc = _metrics_projection.aggregate_day_metrics(
        day_rows=day_rows,
        facade=_metrics_sys.modules[__name__],
    )
    route_summary = build_commander_route_summary(
        reports_root=out_dir.parent,
        day=day,
        day_rows=day_rows,
    )
    generated_at = _utc_now_iso()
    summary = _metrics_projection.assemble_metrics_summary(
        route_summary=route_summary,
        day=day,
        generated_at=generated_at,
        day_rows=day_rows,
        **metrics_acc,
        facade=_metrics_sys.modules[__name__],
    )
    summary["data_freshness"] = build_data_freshness(
        generated_at=summary["generated_at"],
        source_run_count=summary["source_run_count"],
        latest_run_id=summary["latest_run_id"],
        latest_run_ts=summary["latest_run_ts"],
        stale=False,
    )
    summary["route_provenance"] = build_route_provenance(route_summary)

    md_text = _render_metrics_markdown(summary)

    md_path = out_dir / f"metrics_{day}.md"
    js_path = out_dir / f"metrics_{day}.json"
    md_path.write_text(md_text, encoding="utf-8")
    js_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return md_path, js_path


def main() -> None:
    events_path = Path(os.getenv("EVENT_LOG_PATH", "./data/events.jsonl"))
    out_dir = Path(os.getenv("REPORT_DIR", "./reports")) / "metrics"
    day = os.getenv("METRICS_DAY")
    result = Reporter().generate_metrics_report(
        event_log_path=events_path,
        report_dir=out_dir,
        day=day,
    )
    print(f"Wrote: {result.report_md_path}")
    print(f"Wrote: {result.report_json_path}")


if __name__ == "__main__":
    main()
