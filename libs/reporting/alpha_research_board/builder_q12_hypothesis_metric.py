"""``_q12_hypothesis_metric`` moved verbatim from builder.py.

Helpers are resolved on ``facade`` (the source module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Mapping


def _q12_hypothesis_metric(
    payload: Mapping[str, Any],
    *,
    phase: str,
    path_value: str = "FAST_BUY_ALL_PASS",
    entry_method: str = "09:05",
    horizon: str = "+30m",
    facade: Any,
) -> dict[str, Any]:
    for raw in payload.get("rows") or []:
        row = facade.mapping(raw)
        if (
            row.get("evidence_phase") == phase
            and row.get("axis") == "hypothesis_path"
            and row.get("value") == path_value
            and row.get("entry_method") == entry_method
            and row.get("horizon") == horizon
        ):
            return facade.metric_snapshot(row.get("metrics"))
    return facade.metric_snapshot({})
