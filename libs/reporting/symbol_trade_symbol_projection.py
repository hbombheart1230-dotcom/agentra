"""symbol_trade_report collect_symbols_for_day (moved verbatim from symbol_trade_report).

Module globals and helpers are resolved on ``facade`` (the symbol_trade_report module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional


def collect_symbols_for_day(
    events_path: Path,
    reports_root: Path,
    day: str,
    trade_index: Optional[List[Dict[str, Any]]] = None,
    *,
    facade: Any,
) -> List[str]:
    target_day = str(day or "").strip()
    symbols: List[str] = []
    seen: set[str] = set()

    index_rows = trade_index if trade_index is not None else facade.build_daily_trade_index(reports_root, target_day)
    for row in index_rows:
        symbol = str(row.get("symbol") or "").strip().upper()
        if symbol and symbol not in seen:
            seen.add(symbol)
            symbols.append(symbol)

    for row in facade.iter_jsonl_events(events_path, day=target_day):
        ts_day = facade.datetime.fromtimestamp(facade._to_epoch(row.get("ts") or (row.get("payload") or {}).get("ts")), tz=facade.timezone.utc).strftime("%Y-%m-%d") if facade._to_epoch(row.get("ts") or (row.get("payload") or {}).get("ts")) > 0 else ""
        if ts_day != target_day:
            continue
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
        detail = payload.get("payload") if isinstance(payload.get("payload"), dict) else {}
        order = payload.get("order") if isinstance(payload.get("order"), dict) else {}
        for candidate in (
            detail.get("symbol"),
            payload.get("symbol"),
            order.get("symbol"),
            order.get("stk_cd"),
        ):
            symbol = str(candidate or "").strip().upper()
            if symbol and symbol not in seen:
                seen.add(symbol)
                symbols.append(symbol)
    return symbols
