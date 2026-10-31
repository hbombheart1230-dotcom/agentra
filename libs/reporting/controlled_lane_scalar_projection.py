"""controlled_mock_lane_report projections (moved verbatim from controlled_mock_lane_report).

Module globals and helpers are resolved on ``facade`` (the controlled_mock_lane_report module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any


def _mapping(value: Any, *, facade: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, facade.Mapping) else {}



def _first_mapping(*values: Any, facade: Any) -> dict[str, Any]:
    for value in values:
        row = facade._mapping(value)
        if row:
            return row
    return {}
