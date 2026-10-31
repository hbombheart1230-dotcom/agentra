from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from libs.core.settings import load_env_file

from libs.reporting.event_log_reader import iter_jsonl_events


def _env_str(name: str, default: str) -> str:
    from scripts.diagnostics.notification_query_env_projection import _env_str as owner
    return owner(name,default,facade=sys.modules[__name__])


def _to_epoch(ts: Any) -> Optional[int]:
    from scripts.diagnostics.notification_query_time_projection import _to_epoch as owner
    return owner(ts,facade=sys.modules[__name__])


def _utc_day(ts: Any) -> str:
    from scripts.diagnostics.notification_query_time_projection import _utc_day as owner
    return owner(ts,facade=sys.modules[__name__])


def _iter_rows(path: Path) -> List[Dict[str, Any]]:
    return list(iter_jsonl_events(path))


def _build_parser() -> argparse.ArgumentParser:
    from scripts.diagnostics.notification_query_cli_projection import _build_parser as owner
    return owner(facade=sys.modules[__name__])
def main(argv: Optional[List[str]] = None) -> int:
    load_env_file(".env")
    args = _build_parser().parse_args(argv)

    event_log_path = Path(str(args.event_log_path))
    day_filter = str(args.day or "").strip()
    provider_filter = str(args.provider or "").strip().lower()
    only_escalated = bool(args.only_escalated)
    min_pg_alert_total = max(0, int(args.min_portfolio_guard_alert_total))

    rows = _iter_rows(event_log_path)
    filtered: List[Dict[str, Any]] = []
    for row in rows:
        if str(row.get("stage") or "") != "ops_batch_notify":
            continue
        if str(row.get("event") or "") != "result":
            continue
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
        day = str(payload.get("day") or _utc_day(row.get("ts")))
        if day_filter and day != day_filter:
            continue
        provider = str(payload.get("provider") or "").strip().lower()
        if provider_filter and provider != provider_filter:
            continue
        escalated = bool(payload.get("escalated"))
        if only_escalated and not escalated:
            continue
        pg_alert_total = int(payload.get("portfolio_guard_alert_total") or 0)
        if pg_alert_total < min_pg_alert_total:
            continue
        filtered.append(row)

    provider_total: Counter[str] = Counter()
    route_reason_total: Counter[str] = Counter()
    reason_total: Counter[str] = Counter()
    status_code_total: Counter[str] = Counter()
    ok_total = 0
    fail_total = 0
    sent_total = 0
    skipped_total = 0
    escalated_total = 0
    portfolio_guard_alert_total_sum = 0
    portfolio_guard_alert_nonzero_total = 0
    portfolio_guard_alert_max = 0
    for row in filtered:
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
        provider_total[str(payload.get("provider") or "unknown")] += 1
        route_reason_total[str(payload.get("route_reason") or "unknown")] += 1
        reason_total[str(payload.get("reason") or "unknown")] += 1
        status_code_total[str(int(payload.get("status_code") or 0))] += 1
        if bool(payload.get("escalated")):
            escalated_total += 1
        pg_alert_total = int(payload.get("portfolio_guard_alert_total") or 0)
        portfolio_guard_alert_total_sum += pg_alert_total
        if pg_alert_total > 0:
            portfolio_guard_alert_nonzero_total += 1
        if pg_alert_total > portfolio_guard_alert_max:
            portfolio_guard_alert_max = pg_alert_total
        if bool(payload.get("ok")):
            ok_total += 1
        else:
            fail_total += 1
        if bool(payload.get("sent")):
            sent_total += 1
        if bool(payload.get("skipped")):
            skipped_total += 1

    out = {
        "event_log_path": str(event_log_path),
        "day": day_filter or "",
        "total": int(len(filtered)),
        "ok_total": int(ok_total),
        "fail_total": int(fail_total),
        "sent_total": int(sent_total),
        "skipped_total": int(skipped_total),
        "escalated_total": int(escalated_total),
        "portfolio_guard_alert_total_sum": int(portfolio_guard_alert_total_sum),
        "portfolio_guard_alert_nonzero_total": int(portfolio_guard_alert_nonzero_total),
        "portfolio_guard_alert_max": int(portfolio_guard_alert_max),
        "provider_total": dict(provider_total),
        "route_reason_total": dict(route_reason_total),
        "reason_total": dict(reason_total),
        "status_code_total": dict(status_code_total),
    }
    if bool(args.json):
        print(json.dumps(out, ensure_ascii=False))
    else:
        print(
            f"total={out['total']} ok_total={out['ok_total']} fail_total={out['fail_total']} "
            f"sent_total={out['sent_total']} skipped_total={out['skipped_total']} "
            f"escalated_total={out['escalated_total']}"
        )
        print(f"provider_total={out['provider_total']}")
        print(f"route_reason_total={out['route_reason_total']}")
        print(f"reason_total={out['reason_total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
