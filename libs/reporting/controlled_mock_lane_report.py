from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Mapping

from libs.reporting import controlled_lane_lookup_projection as _lookup_owner
from libs.reporting import controlled_lane_ledger_projection as _ledger_owner
from libs.reporting import controlled_lane_surface_build_projection as _build_owner
from libs.reporting import controlled_lane_surface_read_projection as _read_owner
from libs.reporting import controlled_lane_markdown_projection as _markdown_owner
from libs.reporting import controlled_lane_scalar_projection as _scalar_owner


LANE_LABELS = {
    "BTC_WOORI": "Q12 BTC-우리기술투자",
    "Q10_SEMICONDUCTOR": "Q10 반도체 선행시장",
    "Q10_INDEX": "Q10 한국지수 선행시장",
}


def _mapping(value: Any) -> dict[str, Any]:
    return _scalar_owner._mapping(value, facade=sys.modules[__name__])


def _text(value: Any) -> str:
    return str(value or "").strip()


def _first_mapping(*values: Any) -> dict[str, Any]:
    return _scalar_owner._first_mapping(*values, facade=sys.modules[__name__])


def _deep_first(value: Any, *keys: str) -> str:
    return _lookup_owner._deep_first(value, *keys, facade=sys.modules[__name__])


def _position_strategy(state: Mapping[str, Any], symbol: str) -> dict[str, Any]:
    return _lookup_owner._position_strategy(state, symbol, facade=sys.modules[__name__])


def _fixed_lane_strategy() -> dict[str, Any]:
    return {
        "controlled_mock_lane": True,
        "strategy_horizon": "intraday",
        "expected_hold_window": {"min_sec": 300, "target_sec": 1800, "max_sec": 14400},
        "llm_used": False,
        "horizon_revision_allowed": False,
    }


def _ledger_row(
    *, root: Path, day: str, symbol: str, order_id: str = "", run_id: str = ""
) -> dict[str, Any]:
    return _ledger_owner._ledger_row(root=root, day=day, symbol=symbol, order_id=order_id, run_id=run_id, facade=sys.modules[__name__])


def build_controlled_lane_report_surface(
    state: Mapping[str, Any], *, day: str = "", root: Path | str | None = None,
    prior_entry: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Recover controlled-lane entry evidence without same-symbol guessing."""
    return _build_owner.build_controlled_lane_report_surface(state, day=day, root=root, prior_entry=prior_entry, facade=sys.modules[__name__])


def controlled_lane_surface_from_report(report: Mapping[str, Any]) -> dict[str, Any]:
    return _read_owner.controlled_lane_surface_from_report(report, facade=sys.modules[__name__])


def attach_controlled_lane_report_surface(report: dict[str, Any], story_input: Mapping[str, Any]) -> dict[str, Any]:
    surface = _first_mapping(
        story_input.get("controlled_mock_lane"),
        _mapping(story_input.get("trade_lifecycle")).get("controlled_mock_lane"),
        _mapping(_mapping(story_input.get("trade_lifecycle")).get("entry")).get("controlled_mock_lane"),
        _mapping(story_input.get("lifecycle_bundle")).get("controlled_mock_lane"),
    )
    if surface:
        report["controlled_mock_lane"] = surface
        fact_payload = _mapping(report.get("fact_payload"))
        trade = _mapping(fact_payload.get("trade"))
        if trade:
            trade.setdefault("controlled_mock_lane", surface)
            fact_payload["trade"] = trade
            report["fact_payload"] = fact_payload
    return report


def apply_controlled_lane_story_surface(
    story_input: Mapping[str, Any], surface: Mapping[str, Any]
) -> dict[str, Any]:
    out = dict(story_input)
    lane = _mapping(surface)
    if not lane:
        return out
    symbol = _text(lane.get("symbol"))
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
    entry_summary = _mapping(out.get("entry_summary"))
    if entry_summary:
        entry_summary["reason_human"] = reason
        entry_summary["controlled_mock_lane"] = lane
        out["entry_summary"] = entry_summary
    lifecycle_summary = _mapping(out.get("lifecycle_summary"))
    if lifecycle_summary:
        lifecycle_summary["entry_reason_human"] = reason
        out["lifecycle_summary"] = lifecycle_summary
    scanner_evidence = _mapping(out.get("scanner_evidence"))
    if scanner_evidence:
        scanner_evidence["selection_authority"] = "deterministic_independent_lane"
        scanner_evidence["selected_rank"] = None
        scanner_evidence["independent_lane"] = lane
        out["scanner_evidence"] = scanner_evidence
    for lifecycle_key in ("trade_lifecycle", "lifecycle"):
        lifecycle = _mapping(out.get(lifecycle_key))
        if lifecycle:
            lifecycle["controlled_mock_lane"] = lane
            entry = _mapping(lifecycle.get("entry"))
            if entry:
                entry["reason_human"] = reason
                entry["controlled_mock_lane"] = lane
                lifecycle["entry"] = entry
            out[lifecycle_key] = lifecycle
    bundle = _mapping(out.get("lifecycle_bundle"))
    if bundle:
        bundle["controlled_mock_lane"] = lane
        bundle["scanner_reason_human"] = scanner_surface
        bundle["scanner_selection_trace"] = scanner_surface
        lifecycle = _mapping(bundle.get("lifecycle"))
        if lifecycle:
            lifecycle["controlled_mock_lane"] = lane
            entry = _mapping(lifecycle.get("entry"))
            if entry:
                entry["reason_human"] = reason
                entry["controlled_mock_lane"] = lane
                lifecycle["entry"] = entry
            bundle["lifecycle"] = lifecycle
        out["lifecycle_bundle"] = bundle
    return out


def render_controlled_lane_report_lines(report: Mapping[str, Any]) -> list[str]:
    return _markdown_owner.render_controlled_lane_report_lines(report, facade=sys.modules[__name__])


__all__ = ["apply_controlled_lane_story_surface", "attach_controlled_lane_report_surface", "build_controlled_lane_report_surface", "controlled_lane_surface_from_report", "render_controlled_lane_report_lines"]
