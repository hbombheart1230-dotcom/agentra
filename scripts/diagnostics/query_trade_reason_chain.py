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
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional
from libs.reporting.event_log_reader import iter_jsonl_events
from libs.diagnostics.observations import broker_code_success


def _load_jsonl(path: Path) -> List[Dict[str, Any]]:
    return list(iter_jsonl_events(path))


def _broker_code_success(value: Any) -> Optional[bool]:
    return broker_code_success(value)


def _event_intent_id(payload: Dict[str, Any]) -> Optional[str]:
    from scripts.diagnostics.trade_reason_intent_projection import _event_intent_id as owner
    return owner(payload, facade=_migration_sys.modules[__name__])


def _build_rows(events: List[Dict[str, Any]], *, run_id_filter: str = "", action_filter: str = "", only_broker_success: bool = False) -> List[Dict[str, Any]]:
    from scripts.diagnostics.trade_reason_rows_projection import _build_rows as owner
    return owner(events, run_id_filter=run_id_filter, action_filter=action_filter, only_broker_success=only_broker_success, facade=_migration_sys.modules[__name__])
def _print_human(path: Path, rows: List[Dict[str, Any]]) -> None:
    print("=== Trade Reason Chain ===")
    print(f"path={path}")
    print(f"shown={len(rows)}")
    for r in rows:
        print(
            f"{r.get('ts')} run_id={r.get('run_id')} "
            f"action={r.get('action')} symbol={r.get('symbol')} qty={r.get('qty')} "
            f"order_type={r.get('order_type')} broker_code={r.get('broker_code')} "
            f"order_id={r.get('order_id')} strategy={r.get('decision_strategy')} "
            f"decision_rationale={r.get('decision_rationale')} "
            f"decision_reason={r.get('decision_reason')} "
            f"llm_model={r.get('llm_model')} llm_reason={r.get('llm_intent_reason')} "
            f"llm_rationale={r.get('llm_intent_rationale')}"
        )


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(
        description="Show run_id-level trade reasons (LLM -> decision -> execution) from EVENT_LOG_PATH JSONL."
    )
    p.add_argument("--path", default=os.getenv("EVENT_LOG_PATH", "./data/logs/events.jsonl"))
    p.add_argument("--run-id", default="", help="Filter by exact run_id.")
    p.add_argument("--action", default="", help="Filter by action BUY|SELL.")
    p.add_argument("--only-broker-success", action="store_true", help="Only include rows with broker_code==0.")
    p.add_argument("--limit", type=int, default=20, help="Show last N rows.")
    p.add_argument("--json", action="store_true", help="Print JSON array.")
    args = p.parse_args(argv)

    path = Path(str(args.path).strip())
    if not path.exists():
        print(f"ERROR: event log path does not exist: {path}", file=sys.stderr)
        return 2

    action_filter = str(args.action or "").strip().upper()
    if action_filter and action_filter not in ("BUY", "SELL"):
        print("ERROR: --action must be BUY or SELL", file=sys.stderr)
        return 3

    rows = _build_rows(
        _load_jsonl(path),
        run_id_filter=str(args.run_id or "").strip(),
        action_filter=action_filter,
        only_broker_success=bool(args.only_broker_success),
    )
    limit = max(1, int(args.limit))
    shown = rows[-limit:]

    if args.json:
        print(json.dumps(shown, ensure_ascii=False))
    else:
        _print_human(path, shown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
