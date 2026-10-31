"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Iterable


def _iter_days(start: str, end: str, *, facade: Any) -> Iterable[str]:
    start_date = facade.date.fromisoformat(str(start)[:10])
    end_date = facade.date.fromisoformat(str(end)[:10])
    current = start_date
    while current <= end_date:
        yield current.isoformat()
        current += facade.timedelta(days=1)
