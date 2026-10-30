"""Controlled validation daily display status projection (moved verbatim from controlled_validation_daily).

Globals/helpers are resolved on ``facade`` (the controlled_validation_daily module) at call time; this module never imports it.
Pure function; the clock is read only through ``facade.datetime`` at call time.
"""
from __future__ import annotations

from typing import Any


def _display_evaluation_status(
    *, lane_id: str, day: str, status: str, reason: str, facade: Any
) -> tuple[str, str]:
    """Do not present expected post-window expiry as a delivery incident."""
    if lane_id != "BTC_WOORI" or status != "INPUT_DELAY" or reason != "q12_candidate_input_stale":
        return status, reason
    try:
        now = facade.datetime.now(facade.ZoneInfo("Asia/Seoul"))
        session_day = facade.datetime.strptime(day, "%Y-%m-%d").date()
    except ValueError:
        return status, reason
    if session_day < now.date() or (
        session_day == now.date() and now.time() > facade.time(9, 12)
    ):
        return "WINDOW_CLOSED", "q12_opening_candidate_window_closed"
    return status, reason
