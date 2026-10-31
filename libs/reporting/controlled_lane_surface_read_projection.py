"""controlled_mock_lane_report projections (moved verbatim from controlled_mock_lane_report).

Module globals and helpers are resolved on ``facade`` (the controlled_mock_lane_report module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Mapping


def controlled_lane_surface_from_report(report: Mapping[str, Any], *, facade: Any) -> dict[str, Any]:
    fact_payload = facade._mapping(report.get("fact_payload"))
    trade = facade._mapping(fact_payload.get("trade"))
    lifecycle = facade._first_mapping(report.get("trade_lifecycle"), report.get("lifecycle"), trade.get("trade_lifecycle"), trade.get("lifecycle"))
    entry = facade._mapping(lifecycle.get("entry"))
    lifecycle_bundle = facade._first_mapping(report.get("lifecycle_bundle"), trade.get("lifecycle_bundle"))
    bundle_entry = facade._mapping(facade._mapping(lifecycle_bundle.get("lifecycle")).get("entry"))
    return facade._first_mapping(
        report.get("controlled_mock_lane"), trade.get("controlled_mock_lane"),
        lifecycle_bundle.get("controlled_mock_lane"), entry.get("controlled_mock_lane"),
        bundle_entry.get("controlled_mock_lane"),
    )
