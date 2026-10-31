"""controlled_mock_lane_report projections (moved verbatim from controlled_mock_lane_report).

Module globals and helpers are resolved on ``facade`` (the controlled_mock_lane_report module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any


def _text(value: Any) -> str:
    return str(value or "").strip()
