from pathlib import Path
import inspect
from libs.reporting.trade_story_human_parts.monitor_policy_bullets import append_monitor_policy_observation_bullets

def _float(x, default=0.0):
    return float(x) if x not in (None, "") else default

def test_stop_profit_policy_display_preserves_order_and_append_contract():
    bullets = ["earlier"]
    append_monitor_policy_observation_bullets(
        bullets, {"hard_stop_pct": -0.01, "trailing_stop_pct": -0.005,
                  "take_profit_pct": 0.02, "partial_take_profit_pct": 0.015,
                  "profit_ladder_levels_pct": [0.03]},
        safe_float=_float, safe_int=lambda x, default=0: int(x) if x else default,
        format_ratio_pct=lambda x: f"{_float(x)*100:.1f}",
    )
    assert bullets[0] == "earlier"
    assert [x.split(":")[0] for x in bullets[1:]] == [
        "Hard fail-safe stop", "Trailing stop", "Take profit target",
        "Partial take profit", "Profit ladder levels",
    ]

def test_absent_policy_values_do_not_produce_bullets():
    bullets = []
    append_monitor_policy_observation_bullets(
        bullets, {}, safe_float=_float, safe_int=int, format_ratio_pct=str)
    assert bullets == []

def test_new_owner_avoids_oversized_module():
    p = Path(inspect.getsourcefile(append_monitor_policy_observation_bullets))
    assert len(p.read_text(encoding="utf-8").splitlines()) <= 350
