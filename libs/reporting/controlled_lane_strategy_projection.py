"""controlled_mock_lane_report projections (moved verbatim from controlled_mock_lane_report).

Module globals and helpers are resolved on ``facade`` (the controlled_mock_lane_report module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any


def _fixed_lane_strategy() -> dict[str, Any]:
    return {
        "controlled_mock_lane": True,
        "strategy_horizon": "intraday",
        "expected_hold_window": {"min_sec": 300, "target_sec": 1800, "max_sec": 14400},
        "llm_used": False,
        "horizon_revision_allowed": False,
    }
