from pathlib import Path
import inspect

from libs.reporting.trade_story_human_parts.monitor_entry_review import (
    append_monitor_entry_review_bullets,
)

def _inputs(**override):
    result=dict(
        entry_evaluated=False, entry_triggered=False, entry_pattern="",
        entry_signal_chain=[], entry_condition_path="", entry_condition_paths_passed=[],
        entry_condition_scores={}, entry_guard_blocked=False, entry_guard_reason="",
        entry_metrics={}, entry_thresholds={}, human_chart_detail_observed={},
        entry_check_summary="", entry_blockers=[], entry_threshold_gaps=[],
        policy_adjustment_summary="", effective_policy_deltas=[], policy_ref={},
        safe_float=lambda value, default=0.0: float(value) if value not in (None, "") else default,
        safe_int=lambda value, default=0: int(value) if value not in (None, "") else default,
        format_ratio_pct=lambda value: str(float(value)*100) if value not in (None, "") else "0",
    )
    result.update(override)
    return result


def test_not_evaluated_generates_no_entry_review_text():
    bullets=[]
    append_monitor_entry_review_bullets(bullets, **_inputs())
    assert bullets == []


def test_entry_signal_and_price_evidence_keep_original_order():
    bullets=[]
    append_monitor_entry_review_bullets(
        bullets, **_inputs(entry_evaluated=True, entry_triggered=True,
                          entry_pattern="breakout", entry_signal_chain=["rank", "volume"],
                          entry_condition_path="open", entry_condition_paths_passed=["open"],
                          entry_metrics={"volume_ratio": 1.5, "vwap": 100.0},
                          entry_thresholds={"volume_ratio_min": 1.2}),
    )
    assert bullets[0] == "Entry triggered: yes"
    assert bullets[1] == "Entry pattern: breakout"
    assert bullets[2] == "Entry signal chain: rank -> volume"
    assert bullets.index("Entry VWAP: 100.00") < bullets.index("Volume ratio: 1.50 (min 1.20)")


def test_small_entry_review_owner():
    p=Path(inspect.getsourcefile(append_monitor_entry_review_bullets))
    assert len(p.read_text(encoding="utf-8").splitlines()) <= 350
