from pathlib import Path
import inspect

from libs.reporting.trade_story_human_parts.monitor_diagnostics import (
    build_monitor_watch_axes, build_monitor_entry_threshold_gaps,
)


def _float(value, default=0.0):
    return float(value) if value not in (None, "") else default


def test_human_monitor_watch_axes_preserve_configured_stop_priority():
    result = build_monitor_watch_axes(
        {"watch_axes": ["Existing"]}, {},
        {"hard_stop_pct": -0.01, "take_profit_pct": 0.02,
         "trailing_stop_pct": -0.015, "profit_ladder_levels_pct": [0.03]},
        _float,
    )
    assert result[0] == "Existing"
    assert "Hard stop" in result
    assert "Take profit" in result
    assert "Profit ladder" in result
    assert "Trailing stop" in result
    assert result.count("Hard stop") == 1


def test_human_monitor_threshold_gaps_are_observations_not_trade_decisions():
    result = build_monitor_entry_threshold_gaps(
        {"volume_ratio": 0.5, "extended_from_vwap_pct": 0.03,
         "pullback_depth_pct": 0.001},
        {"volume_ratio_min": 1.2, "max_extended_from_vwap_pct": 0.02,
         "pullback_min_pct": 0.005},
        _float, lambda value: f"{_float(value) * 100:.2f}",
    )
    assert len(result) == 3
    assert "volume ratio" in result[0]
    assert "VWAP extension" in result[1]
    assert "pullback depth" in result[2]


def test_monitor_diagnostics_is_bounded():
    path = Path(inspect.getsourcefile(build_monitor_watch_axes))
    assert len(path.read_text(encoding="utf-8").splitlines()) <= 350
