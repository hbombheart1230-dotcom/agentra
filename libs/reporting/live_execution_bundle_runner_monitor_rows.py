"""``_target_symbol_monitor_rows`` moved verbatim from live_execution_bundle_runner.py as ``target_symbol_monitor_rows``.

Helpers are resolved on ``facade`` (the runner module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, List


def target_symbol_monitor_rows(
    rows: List[Dict[str, Any]] | None,
    *,
    symbol: str,
    facade: Any,
) -> List[Dict[str, Any]]:
    sym = facade.normalize_symbol(symbol or "", allow_test_symbols=True)
    if not sym:
        return []
    out: List[Dict[str, Any]] = []
    for row in list(rows or []):
        if facade._event_row_symbol(row) != sym:
            continue
        name = facade._event_row_name(row)
        if not name.startswith("monitor."):
            continue
        out.append(row)
    return out
