"""controlled_mock_lane_report projections (moved verbatim from controlled_mock_lane_report).

Module globals and helpers are resolved on ``facade`` (the controlled_mock_lane_report module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Mapping


def _deep_first(value: Any, *keys: str, facade: Any) -> str:
    if isinstance(value, facade.Mapping):
        for key in keys:
            if facade._text(value.get(key)):
                return facade._text(value.get(key))
        for child in value.values():
            found = facade._deep_first(child, *keys)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = facade._deep_first(child, *keys)
            if found:
                return found
    return ""



def _position_strategy(state: Mapping[str, Any], symbol: str, *, facade: Any) -> dict[str, Any]:
    persisted = facade._mapping(state.get("persisted_state"))
    contexts = facade._mapping(persisted.get("position_strategy_context"))
    row = facade._mapping(contexts.get(symbol))
    return facade._mapping(row.get("output"))
