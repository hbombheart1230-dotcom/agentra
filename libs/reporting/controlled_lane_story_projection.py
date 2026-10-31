"""controlled_mock_lane_report projections (moved verbatim from controlled_mock_lane_report).

Module globals and helpers are resolved on ``facade`` (the controlled_mock_lane_report module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Mapping


def apply_controlled_lane_story_surface(
    story_input: Mapping[str, Any], surface: Mapping[str, Any],
    *,
    facade: Any,
) -> dict[str, Any]:
    out = dict(story_input)
    lane = facade._mapping(surface)
    if not lane:
        return out
    symbol = facade._text(lane.get("symbol"))
    reason = (
        f"{lane.get('lane_label') or lane.get('lane_id')} 독립 결정 레인이 {symbol}을 선택했습니다. "
        "메인 Scanner 순위는 이 거래에 적용되지 않습니다."
    )
    scanner_surface = {
        "summary": reason,
        "comparison": "This trade did not use the main Scanner ranking authority.",
        "bullets": [
            f"Independent lane: {lane.get('lane_id')}",
            "Scanner rank: not applicable",
            f"Signal ID: {lane.get('signal_id') or 'not_captured'}",
        ],
        "selected_symbol": symbol,
        "selected_rank": None,
        "universe_size": None,
        "selection_authority": "deterministic_independent_lane",
    }
    out["controlled_mock_lane"] = lane
    out["scanner_reason_human"] = scanner_surface
    out["scanner_selection_trace"] = dict(scanner_surface)
    entry_summary = facade._mapping(out.get("entry_summary"))
    if entry_summary:
        entry_summary["reason_human"] = reason
        entry_summary["controlled_mock_lane"] = lane
        out["entry_summary"] = entry_summary
    lifecycle_summary = facade._mapping(out.get("lifecycle_summary"))
    if lifecycle_summary:
        lifecycle_summary["entry_reason_human"] = reason
        out["lifecycle_summary"] = lifecycle_summary
    scanner_evidence = facade._mapping(out.get("scanner_evidence"))
    if scanner_evidence:
        scanner_evidence["selection_authority"] = "deterministic_independent_lane"
        scanner_evidence["selected_rank"] = None
        scanner_evidence["independent_lane"] = lane
        out["scanner_evidence"] = scanner_evidence
    for lifecycle_key in ("trade_lifecycle", "lifecycle"):
        lifecycle = facade._mapping(out.get(lifecycle_key))
        if lifecycle:
            lifecycle["controlled_mock_lane"] = lane
            entry = facade._mapping(lifecycle.get("entry"))
            if entry:
                entry["reason_human"] = reason
                entry["controlled_mock_lane"] = lane
                lifecycle["entry"] = entry
            out[lifecycle_key] = lifecycle
    bundle = facade._mapping(out.get("lifecycle_bundle"))
    if bundle:
        bundle["controlled_mock_lane"] = lane
        bundle["scanner_reason_human"] = scanner_surface
        bundle["scanner_selection_trace"] = scanner_surface
        lifecycle = facade._mapping(bundle.get("lifecycle"))
        if lifecycle:
            lifecycle["controlled_mock_lane"] = lane
            entry = facade._mapping(lifecycle.get("entry"))
            if entry:
                entry["reason_human"] = reason
                entry["controlled_mock_lane"] = lane
                lifecycle["entry"] = entry
            bundle["lifecycle"] = lifecycle
        out["lifecycle_bundle"] = bundle
    return out
