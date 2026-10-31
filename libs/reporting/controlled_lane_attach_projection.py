"""controlled_mock_lane_report projections (moved verbatim from controlled_mock_lane_report).

Module globals and helpers are resolved on ``facade`` (the controlled_mock_lane_report module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Mapping


def attach_controlled_lane_report_surface(report: dict[str, Any], story_input: Mapping[str, Any], *, facade: Any) -> dict[str, Any]:
    surface = facade._first_mapping(
        story_input.get("controlled_mock_lane"),
        facade._mapping(story_input.get("trade_lifecycle")).get("controlled_mock_lane"),
        facade._mapping(facade._mapping(story_input.get("trade_lifecycle")).get("entry")).get("controlled_mock_lane"),
        facade._mapping(story_input.get("lifecycle_bundle")).get("controlled_mock_lane"),
    )
    if surface:
        report["controlled_mock_lane"] = surface
        fact_payload = facade._mapping(report.get("fact_payload"))
        trade = facade._mapping(fact_payload.get("trade"))
        if trade:
            trade.setdefault("controlled_mock_lane", surface)
            fact_payload["trade"] = trade
            report["fact_payload"] = fact_payload
    return report
