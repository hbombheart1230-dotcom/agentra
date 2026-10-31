"""post_exit_shadow_recap projections (moved verbatim from post_exit_shadow_recap).

Module globals and helpers are resolved on ``facade`` (the post_exit_shadow_recap module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping


def _rows_reach_epoch(rows: Iterable[Mapping[str, Any]], target_epoch: float | None, *, facade: Any) -> bool:
    if target_epoch is None:
        return False
    return any((facade._epoch_seconds(row.get("ts")) or 0.0) >= float(target_epoch) for row in rows if isinstance(row, Mapping))


def _rows_reach_regular_close(rows: Iterable[Mapping[str, Any]], *, facade: Any) -> bool:
    return any(
        facade._row_kst_hhmmss(row) >= "153000"
        for row in rows
        if isinstance(row, Mapping) and facade._row_kst_hhmmss(row)
    )
