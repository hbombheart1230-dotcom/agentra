"""``_find_existing_trade_id_for_run_ids`` moved verbatim from live_execution_bundle_runner.py as ``find_existing_trade_id_for_run_ids``.

Helpers are resolved on ``facade`` (the runner module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, List, Tuple


def find_existing_trade_id_for_run_ids(
    *,
    reports_root: Path,
    day: str,
    symbol: str,
    run_ids: Iterable[str],
    facade: Any,
) -> str:
    day_root = facade.Path(reports_root) / "trades" / str(day or "").strip()
    if not day_root.exists():
        return ""
    requested = {str(item or "").strip() for item in list(run_ids or []) if str(item or "").strip()}
    if not requested:
        return ""
    symbol_norm = facade.normalize_symbol(symbol or "", allow_test_symbols=True) or ""
    matches: List[Tuple[int, str]] = []
    for trade_dir in facade.iter_trade_dirs(day_root):
        trade_id = str(trade_dir.name or "").strip()
        if symbol_norm and f"_{symbol_norm}_" not in trade_id:
            continue
        existing_run_ids = set(facade._existing_trade_run_ids(trade_dir))
        if not existing_run_ids.intersection(requested):
            continue
        matches.append((facade._trade_id_sequence(trade_id), trade_id))
    if not matches:
        return ""
    matches.sort(key=lambda item: (item[0], item[1]))
    return str(matches[0][1] or "")
