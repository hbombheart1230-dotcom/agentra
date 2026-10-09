from __future__ import annotations

from typing import Any, Callable, Dict, List


def append_monitor_entry_review_bullets(
    bullets: List[str], *,
    entry_evaluated: bool, entry_triggered: bool, entry_pattern: str,
    entry_signal_chain: List[str], entry_condition_path: str,
    entry_condition_paths_passed: List[str], entry_condition_scores: Dict[str, Any],
    entry_guard_blocked: bool, entry_guard_reason: str,
    entry_metrics: Dict[str, Any], entry_thresholds: Dict[str, Any],
    human_chart_detail_observed: Dict[str, Any], entry_check_summary: str,
    entry_blockers: List[str], entry_threshold_gaps: List[str],
    policy_adjustment_summary: str, effective_policy_deltas: List[Dict[str, Any]],
    policy_ref: Dict[str, Any], safe_float: Callable,
    safe_int: Callable, format_ratio_pct: Callable,
) -> None:
    """Append observed entry-scanner/monitor evidence with original field order."""
        if entry_evaluated:
            bullets.append(f"Entry triggered: {'yes' if entry_triggered else 'no'}")
            bullets.append(f"Entry pattern: {entry_pattern or 'not_captured'}")
            if entry_signal_chain:
                bullets.append("Entry signal chain: " + " -> ".join(entry_signal_chain[:6]))
            if entry_condition_path:
                bullets.append(f"Grouped entry path: {entry_condition_path}")
            if entry_condition_paths_passed:
                bullets.append("Grouped paths passed: " + ", ".join(entry_condition_paths_passed[:3]))
            if entry_condition_scores:
                bullets.append(
                    "Condition scores: "
                    + "; ".join(
                        [
                            f"{key}={safe_float(value, 0.0):.2f}"
                            for key, value in list(entry_condition_scores.items())[:6]
                            if value not in (None, "")
                        ]
                    )
                )
            if entry_guard_blocked or entry_guard_reason:
                bullets.append(
                    f"Entry guard blocked: {'yes' if entry_guard_blocked else 'no'} "
                    f"({entry_guard_reason or 'no guard reason captured'})"
                )
            if entry_metrics.get("timeframe_minutes") not in (None, ""):
                bullets.append(f"Entry timeframe: {safe_int(entry_metrics.get('timeframe_minutes'), 1)}m")
            if entry_metrics.get("recent_high") not in (None, ""):
                bullets.append(f"Recent high: {safe_float(entry_metrics.get('recent_high'), 0.0):.2f}")
            if entry_metrics.get("breakout_level") not in (None, ""):
                bullets.append(f"Breakout level: {safe_float(entry_metrics.get('breakout_level'), 0.0):.2f}")
            if entry_metrics.get("vwap") not in (None, ""):
                bullets.append(f"Entry VWAP: {safe_float(entry_metrics.get('vwap'), 0.0):.2f}")
            if entry_metrics.get("volume_ratio") not in (None, ""):
                bullets.append(
                    f"Volume ratio: {safe_float(entry_metrics.get('volume_ratio'), 0.0):.2f} "
                    f"(min {safe_float(entry_thresholds.get('volume_ratio_min'), 0.0):.2f})"
                )
            if entry_metrics.get("extended_from_vwap_pct") not in (None, ""):
                bullets.append(
                    f"Extended from VWAP: {format_ratio_pct(entry_metrics.get('extended_from_vwap_pct'))}% "
                    f"(max {format_ratio_pct(entry_thresholds.get('max_extended_from_vwap_pct'))}%)"
                )
            if entry_metrics.get("pullback_depth_pct") not in (None, ""):
                pullback_bullet = f"Pullback depth: {format_ratio_pct(entry_metrics.get('pullback_depth_pct'))}%"
                if entry_thresholds.get("pullback_min_pct") not in (None, ""):
                    pullback_bullet += f" (min {format_ratio_pct(entry_thresholds.get('pullback_min_pct'))}%)"
                if entry_thresholds.get("pullback_max_pct") not in (None, ""):
                    pullback_bullet += f" (max {format_ratio_pct(entry_thresholds.get('pullback_max_pct'))}%)"
                bullets.append(pullback_bullet)
            if any(
                entry_metrics.get(key) not in (None, "")
                for key in (
                    "human_candle_quality_score",
                    "human_vwap_reference_quality_score",
                    "human_reward_room_score",
                    "human_multi_window_structure_score",
                )
            ):
                bullets.append(
                    "Human chart setup quality: "
                    f"candle {safe_float(entry_metrics.get('human_candle_quality_score'), 0.0):.2f}, "
                    f"VWAP ref {safe_float(entry_metrics.get('human_vwap_reference_quality_score'), 0.0):.2f}, "
                    f"reward room {safe_float(entry_metrics.get('human_reward_room_score'), 0.0):.2f}, "
                    f"multi-window {safe_float(entry_metrics.get('human_multi_window_structure_score'), 0.0):.2f}"
                )
            if human_chart_detail_observed:
                candle_bits: List[str] = []
                if human_chart_detail_observed.get("close_location") not in (None, ""):
                    candle_bits.append(f"close location {safe_float(human_chart_detail_observed.get('close_location'), 0.0):.2f}")
                if human_chart_detail_observed.get("upper_wick_ratio") not in (None, ""):
                    candle_bits.append(f"upper wick {safe_float(human_chart_detail_observed.get('upper_wick_ratio'), 0.0):.2f}")
                if human_chart_detail_observed.get("lower_wick_ratio") not in (None, ""):
                    candle_bits.append(f"lower wick {safe_float(human_chart_detail_observed.get('lower_wick_ratio'), 0.0):.2f}")
                if human_chart_detail_observed.get("body_ratio") not in (None, ""):
                    candle_bits.append(f"body {safe_float(human_chart_detail_observed.get('body_ratio'), 0.0):.2f}")
                if candle_bits:
                    bullets.append("Entry candle shape: " + ", ".join(candle_bits))
                vwap_bits: List[str] = []
                if human_chart_detail_observed.get("vwap_source") not in (None, ""):
                    vwap_bits.append(f"source {human_chart_detail_observed.get('vwap_source')}")
                if human_chart_detail_observed.get("vwap_bar_count") not in (None, ""):
                    vwap_bits.append(f"bars {safe_int(human_chart_detail_observed.get('vwap_bar_count'), 0)}")
                if human_chart_detail_observed.get("explicit_vwap_count") not in (None, ""):
                    vwap_bits.append(f"explicit bars {safe_int(human_chart_detail_observed.get('explicit_vwap_count'), 0)}")
                if human_chart_detail_observed.get("explicit_vwap_ratio") not in (None, ""):
                    vwap_bits.append(f"explicit ratio {safe_float(human_chart_detail_observed.get('explicit_vwap_ratio'), 0.0):.2f}")
                if vwap_bits:
                    bullets.append("VWAP reference quality: " + ", ".join(vwap_bits))
                reward_bits: List[str] = []
                if human_chart_detail_observed.get("prior_resistance") not in (None, ""):
                    reward_bits.append(f"resistance {safe_float(human_chart_detail_observed.get('prior_resistance'), 0.0):.2f}")
                if human_chart_detail_observed.get("reward_room_pct") not in (None, ""):
                    reward_bits.append(f"room {format_ratio_pct(human_chart_detail_observed.get('reward_room_pct'))}%")
                if human_chart_detail_observed.get("breakout_extension_pct") not in (None, ""):
                    reward_bits.append(
                        f"breakout extension {format_ratio_pct(human_chart_detail_observed.get('breakout_extension_pct'))}%"
                    )
                if reward_bits:
                    bullets.append("Reward room context: " + ", ".join(reward_bits))
            if entry_check_summary:
                bullets.append(f"Entry check summary: {entry_check_summary}")
            if entry_blockers:
                bullets.append("Entry blockers: " + "; ".join(entry_blockers[:6]))
            if entry_threshold_gaps:
                bullets.append("Threshold gaps: " + "; ".join(entry_threshold_gaps[:3]))
            if policy_adjustment_summary:
                bullets.append(f"Policy adjustment summary: {policy_adjustment_summary}")
            if effective_policy_deltas:
                bullets.append(
                    "Effective policy deltas: "
                    + "; ".join(
                        [
                            f"{str((row or {}).get('field') or '')}: {(row or {}).get('from')} -> {(row or {}).get('to')}"
                            for row in effective_policy_deltas[:4]
                            if str((row or {}).get("field") or "").strip()
                        ]
                    )
                )
            if policy_ref:
                policy_bits: List[str] = []
                for key in ("monitor_mission", "flow_instruction", "risk_mode", "command_intent"):
                    value = str(policy_ref.get(key) or "").strip()
                    if value:
                        policy_bits.append(f"{key}={value}")
                if policy_bits:
                    bullets.append("Policy reference: " + ", ".join(policy_bits[:4]))
