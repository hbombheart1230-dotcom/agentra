"""Symbol trade report lifecycle iterators (moved verbatim from symbol_trade_report).

Helpers are resolved on ``facade`` (the symbol_trade_report module) at call time (and at iteration time inside the lazy generators); this module never imports it.
Read-only filesystem scans.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, Tuple


def _iter_trade_lifecycles(reports_root: Path, *, facade: Any) -> Iterable[Tuple[Path, Dict[str, Any]]]:
    trades_root = reports_root / "trades"
    if not trades_root.exists():
        return []

    def _gen() -> Iterable[Tuple[Path, Dict[str, Any]]]:
        seen_trade_ids: set[str] = set()
        for path in sorted(trades_root.rglob("lifecycle/trade_lifecycle.json")):
            obj = facade._read_json(path)
            if obj:
                trade_id = str(obj.get("trade_id") or "").strip()
                if trade_id:
                    seen_trade_ids.add(trade_id)
                yield path, obj

        for path in sorted(trades_root.rglob("lifecycle_bundle.json")):
            bundle = facade._read_json(path)
            if not bundle:
                continue
            trade_id = str(bundle.get("trade_id") or "").strip()
            if trade_id and trade_id in seen_trade_ids:
                continue
            normalized = facade._normalize_lifecycle_bundle(bundle)
            if normalized:
                if trade_id:
                    seen_trade_ids.add(trade_id)
                yield path, normalized

    return _gen()


def _iter_trade_lifecycles_for_day(reports_root: Path, day: str, *, facade: Any) -> Iterable[Tuple[Path, Dict[str, Any]]]:
    day_root = facade.resolve_trade_day_root(reports_root, str(day or "").strip())
    if not day_root.exists():
        return []

    def _gen() -> Iterable[Tuple[Path, Dict[str, Any]]]:
        seen_trade_ids: set[str] = set()
        for path in sorted(day_root.rglob("lifecycle/trade_lifecycle.json")):
            obj = facade._read_json(path)
            if obj:
                trade_id = str(obj.get("trade_id") or "").strip()
                if trade_id:
                    seen_trade_ids.add(trade_id)
                yield path, obj

        for path in sorted(day_root.rglob("lifecycle_bundle.json")):
            bundle = facade._read_json(path)
            if not bundle:
                continue
            trade_id = str(bundle.get("trade_id") or "").strip()
            if trade_id and trade_id in seen_trade_ids:
                continue
            normalized = facade._normalize_lifecycle_bundle(bundle)
            if normalized:
                if trade_id:
                    seen_trade_ids.add(trade_id)
                yield path, normalized

    return _gen()
