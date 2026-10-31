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
from libs.reporting import controlled_lane_text_projection as _ctext_owner
from libs.reporting import controlled_lane_strategy_projection as _cstrategy_owner
from libs.reporting import controlled_lane_attach_projection as _cattach_owner
from libs.reporting import controlled_lane_story_projection as _cstory_owner


LANE_LABELS = {
    "BTC_WOORI": "Q12 BTC-우리기술투자",
    "Q10_SEMICONDUCTOR": "Q10 반도체 선행시장",
    "Q10_INDEX": "Q10 한국지수 선행시장",
}


def _mapping(value: Any) -> dict[str, Any]:
    return _scalar_owner._mapping(value, facade=sys.modules[__name__])


def _text(value: Any) -> str:
    return _ctext_owner._text(value)


def _first_mapping(*values: Any) -> dict[str, Any]:
    return _scalar_owner._first_mapping(*values, facade=sys.modules[__name__])


def _deep_first(value: Any, *keys: str) -> str:
    return _lookup_owner._deep_first(value, *keys, facade=sys.modules[__name__])


def _position_strategy(state: Mapping[str, Any], symbol: str) -> dict[str, Any]:
    return _lookup_owner._position_strategy(state, symbol, facade=sys.modules[__name__])


def _fixed_lane_strategy() -> dict[str, Any]:
    return _cstrategy_owner._fixed_lane_strategy()


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
    return _cattach_owner.attach_controlled_lane_report_surface(report, story_input, facade=sys.modules[__name__])


def apply_controlled_lane_story_surface(
    story_input: Mapping[str, Any], surface: Mapping[str, Any]
) -> dict[str, Any]:
    return _cstory_owner.apply_controlled_lane_story_surface(story_input, surface, facade=sys.modules[__name__])


def render_controlled_lane_report_lines(report: Mapping[str, Any]) -> list[str]:
    return _markdown_owner.render_controlled_lane_report_lines(report, facade=sys.modules[__name__])


__all__ = ["apply_controlled_lane_story_surface", "attach_controlled_lane_report_surface", "build_controlled_lane_report_surface", "controlled_lane_surface_from_report", "render_controlled_lane_report_lines"]
