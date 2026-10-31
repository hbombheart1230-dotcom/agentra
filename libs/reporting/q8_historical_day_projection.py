"""q8_historical_review projections (moved verbatim from q8_historical_review).

Module globals and helpers are resolved on ``facade`` (the q8_historical_review module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable


def _iter_days(start: str, end: str) -> Iterable[str]:
    from datetime import date, timedelta

    current = date.fromisoformat(str(start)[:10])
    last = date.fromisoformat(str(end)[:10])
    while current <= last:
        yield current.isoformat()
        current += timedelta(days=1)


def _trade_id_from_path(path: Path) -> str:
    try:
        return path.parents[1].name
    except Exception:
        return ""


def _quant_shadow_candidate_root(reports_root: Path, *, facade: Any) -> Path:
    return facade.Path(reports_root).parent / "data" / "logs" / "quant_shadow_candidates"
