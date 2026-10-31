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
from scripts.diagnostics import strategist_event_query_projection as event_projection


def _to_float(value: Any, default: float = 0.0) -> float:
    return event_projection._to_float(value, default)


def _infer_call_kind(payload: Dict[str, Any]) -> str:
    return event_projection._infer_call_kind(payload)


def _load_jsonl(path: Path) -> List[Dict[str, Any]]:
    return list(iter_jsonl_events(path))


def _filtered_events(
    rows: List[Dict[str, Any]],
    *,
    run_id: str = "",
    day: str = "",
    only_failures: bool = False,
    only_nonzero_news: bool = False,
) -> List[Dict[str, Any]]:
    return event_projection._filtered_events(rows, run_id=run_id, day=day, only_failures=only_failures, only_nonzero_news=only_nonzero_news, facade=sys.modules[__name__])


def _print_human(path: Path, rows: List[Dict[str, Any]]) -> None:
    from scripts.diagnostics.strategist_query_render_projection import _print_human as owner
    return owner(path, rows, facade=_migration_sys.modules[__name__])


def _print_summary(rows: List[Dict[str, Any]]) -> None:
    from scripts.diagnostics.strategist_query_render_projection import _print_summary as owner
    return owner(rows, facade=_migration_sys.modules[__name__])


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Query strategist_llm result events from EVENT_LOG_PATH JSONL.")
    p.add_argument("--path", default=os.getenv("EVENT_LOG_PATH", "./data/logs/events.jsonl"))
    p.add_argument("--run-id", default="", help="Filter by exact run_id.")
    p.add_argument("--day", default="", help="Filter by day prefix in ts/ts_kst, e.g. 2026-03-19.")
    p.add_argument("--limit", type=int, default=20, help="Show last N matched rows.")
    p.add_argument("--only-failures", action="store_true", help="Only include rows where payload.ok is false.")
    p.add_argument(
        "--only-nonzero-news",
        action="store_true",
        help="Only include rows where payload.context_symbol_sentiment_score is non-zero.",
    )
    p.add_argument("--summary", action="store_true", help="Print compact summary counters before rows.")
    p.add_argument("--json", action="store_true", help="Print JSON array instead of human-readable lines.")
    args = p.parse_args(argv)

    path = Path(str(args.path).strip())
    if not path.exists():
        print(f"ERROR: event log path does not exist: {path}", file=sys.stderr)
        return 2

    rows = _load_jsonl(path)
    matched = _filtered_events(
        rows,
        run_id=str(args.run_id or "").strip(),
        day=str(args.day or "").strip(),
        only_failures=bool(args.only_failures),
        only_nonzero_news=bool(args.only_nonzero_news),
    )
    limit = max(1, int(args.limit))
    shown = matched[-limit:]

    if args.json:
        print(json.dumps(shown, ensure_ascii=False))
    else:
        if args.summary:
            _print_summary(matched)
        _print_human(path, shown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
