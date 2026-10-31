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
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from libs.reporting.event_log_reader import iter_jsonl_events


def _load_jsonl(path: Path) -> List[Dict[str, Any]]:
    return list(iter_jsonl_events(path))


def _is_incident_event(rec: Dict[str, Any]) -> bool:
    from scripts.diagnostics.commander_resilience_query_projection import _is_incident_event as owner
    return owner(rec,facade=_migration_sys.modules[__name__])


def _filtered_events(
    rows: List[Dict[str, Any]],
    *,
    run_id: str = "",
    only_incidents: bool = False,
    include_route: bool = False,
) -> List[Dict[str, Any]]:
    from scripts.diagnostics.commander_resilience_query_projection import _filtered_events as owner
    return owner(rows,run_id=run_id,only_incidents=only_incidents,include_route=include_route,facade=_migration_sys.modules[__name__])


def _summary(rows: List[Dict[str, Any]], *, total_matched: int) -> Dict[str, Any]:
    from scripts.diagnostics.commander_resilience_summary_projection import _summary as owner
    return owner(rows, total_matched=total_matched)


def _print_human(path: Path, rows: List[Dict[str, Any]], summary: Dict[str, Any]) -> None:
    from scripts.diagnostics.commander_resilience_render_projection import _print_human as owner
    return owner(path, rows, summary, facade=_migration_sys.modules[__name__])


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Query commander_router resilience events from EVENT_LOG_PATH JSONL.")
    p.add_argument("--path", default=os.getenv("EVENT_LOG_PATH", "./data/logs/events.jsonl"))
    p.add_argument("--run-id", default="", help="Filter by exact run_id.")
    p.add_argument("--limit", type=int, default=20, help="Show last N matched rows.")
    p.add_argument("--only-incidents", action="store_true", help="Only include cooldown/error incident events.")
    p.add_argument("--include-route", action="store_true", help="Include route events (excluded by default).")
    p.add_argument("--json", action="store_true", help="Print JSON object instead of human-readable lines.")
    args = p.parse_args(argv)

    path = Path(str(args.path).strip())
    if not path.exists():
        print(f"ERROR: event log path does not exist: {path}", file=sys.stderr)
        return 2

    rows = _load_jsonl(path)
    matched = _filtered_events(
        rows,
        run_id=str(args.run_id or "").strip(),
        only_incidents=bool(args.only_incidents),
        include_route=bool(args.include_route),
    )
    limit = max(1, int(args.limit))
    shown = matched[-limit:]
    summary = _summary(shown, total_matched=len(matched))

    if args.json:
        print(json.dumps({"summary": summary, "rows": shown}, ensure_ascii=False))
    else:
        _print_human(path, shown, summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
