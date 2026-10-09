from __future__ import annotations

from typing import Any, Dict, List, Mapping

from libs.reporting.trade_execution_outcome_text import build_execution_outcome_human_payload
from libs.reporting.trade_report_common import (
    clip_text as clip,
    format_ratio_pct,
    list_text as _list_text,
    safe_float,
)


from .trade_story_human_parts.market_context import build_market_context_human
from .trade_story_human_parts.scanner_reason import build_scanner_reason_human
from .trade_story_human_parts.monitor_policy_bullets import append_monitor_policy_observation_bullets
from .trade_story_human_parts.monitor_entry_review import append_monitor_entry_review_bullets
from .trade_story_human_parts.monitor_diagnostics import (
    build_monitor_watch_axes, build_monitor_entry_threshold_gaps,
)

def normalize_stop_thresholds(thresholds: Dict[str, Any]) -> Dict[str, Any]:
    data = thresholds if isinstance(thresholds, dict) else {}
    nested = data.get("thresholds") if isinstance(data.get("thresholds"), dict) else {}
    return nested or data


def resolve_strategist_adaptive_exit(monitor: Dict[str, Any]) -> Dict[str, Any]:
    data = monitor if isinstance(monitor, dict) else {}
    for candidate in (
        ((data.get("policy_ref") or {}).get("exit_plan") or {}).get("adaptive_exit"),
        (((data.get("decision_trace") or {}).get("policy_ref") or {}).get("exit_plan") or {}).get("adaptive_exit"),
        (((data.get("timing_assessment") or {}).get("entry_plan") or {}).get("adaptive_exit")),
    ):
        if isinstance(candidate, dict) and candidate:
            return candidate
    return {}


def resolve_adaptive_stop_loss_pct(monitor: Dict[str, Any], thresholds: Dict[str, Any]) -> Any:
    thresholds = normalize_stop_thresholds(thresholds)
    adaptive_exit = monitor.get("adaptive_exit") if isinstance(monitor.get("adaptive_exit"), dict) else {}
    if adaptive_exit.get("stop_loss_pct") not in (None, ""):
        return adaptive_exit.get("stop_loss_pct")
    if thresholds.get("adaptive_stop_loss_pct") not in (None, ""):
        return thresholds.get("adaptive_stop_loss_pct")
    threshold_snapshot = monitor.get("threshold_snapshot") if isinstance(monitor.get("threshold_snapshot"), dict) else {}
    if threshold_snapshot.get("adaptive_stop_loss_pct") not in (None, ""):
        return threshold_snapshot.get("adaptive_stop_loss_pct")
    return None


def build_monitor_stop_policy_trace(monitor: Dict[str, Any], thresholds: Dict[str, Any]) -> Dict[str, Any]:
    thresholds = normalize_stop_thresholds(thresholds)
    strategist_adaptive_exit = resolve_strategist_adaptive_exit(monitor)
    adaptive_stop_loss_pct = resolve_adaptive_stop_loss_pct(monitor, thresholds)
    hard_stop_pct = (
        thresholds.get("hard_stop_pct")
        if thresholds.get("hard_stop_pct") not in (None, "")
        else monitor.get("hard_stop_pct")
    )
    effective_stop_loss_pct = (
        thresholds.get("effective_stop_loss_pct")
        if thresholds.get("effective_stop_loss_pct") not in (None, "")
        else adaptive_stop_loss_pct
        if adaptive_stop_loss_pct not in (None, "")
        else hard_stop_pct
    )
    return {
        "hard_stop_pct": hard_stop_pct,
        "adaptive_stop_loss_pct": adaptive_stop_loss_pct,
        "effective_stop_loss_pct": effective_stop_loss_pct,
        "trailing_stop_pct": thresholds.get("trailing_stop_pct"),
        "take_profit_pct": thresholds.get("take_profit_pct"),
        "partial_take_profit_pct": thresholds.get("partial_take_profit_pct"),
        "partial_take_profit_fraction": thresholds.get("partial_take_profit_fraction"),
        "profit_ladder_levels_pct": thresholds.get("profit_ladder_levels_pct"),
        "profit_ladder_fraction": thresholds.get("profit_ladder_fraction"),
        "risk_reward_take_profit_r": thresholds.get("risk_reward_take_profit_r"),
        "risk_reward_take_profit_rungs": thresholds.get("risk_reward_take_profit_rungs"),
        "risk_reward_take_profit_fraction": thresholds.get("risk_reward_take_profit_fraction"),
        "risk_reward_take_profit_min_pct": thresholds.get("risk_reward_take_profit_min_pct"),
        "vwap_extension_take_profit_pct": thresholds.get("vwap_extension_take_profit_pct"),
        "vwap_extension_take_profit_min_pct": thresholds.get("vwap_extension_take_profit_min_pct"),
        "resistance_take_profit_near_pct": thresholds.get("resistance_take_profit_near_pct"),
        "resistance_take_profit_min_pct": thresholds.get("resistance_take_profit_min_pct"),
        "profit_time_stop_sec": thresholds.get("profit_time_stop_sec"),
        "profit_time_stop_min_pct": thresholds.get("profit_time_stop_min_pct"),
        "profit_time_stop_peak_giveback_pct": thresholds.get("profit_time_stop_peak_giveback_pct"),
        "volume_exhaustion_take_profit_min_pct": thresholds.get("volume_exhaustion_take_profit_min_pct"),
        "volume_exhaustion_volume_ratio_max": thresholds.get("volume_exhaustion_volume_ratio_max"),
        "volume_exhaustion_strength_max": thresholds.get("volume_exhaustion_strength_max"),
        "opening_gap_profit_take_min_pct": thresholds.get("opening_gap_profit_take_min_pct"),
        "opening_gap_profit_take_window_sec": thresholds.get("opening_gap_profit_take_window_sec"),
        "opening_gap_profit_take_fraction": thresholds.get("opening_gap_profit_take_fraction"),
        "cost_aware_profit_floor_enabled": thresholds.get("cost_aware_profit_floor_enabled"),
        "round_trip_cost_floor_pct": thresholds.get("round_trip_cost_floor_pct"),
        "min_net_profit_buffer_pct": thresholds.get("min_net_profit_buffer_pct"),
        "cost_aware_profit_floor_pct": thresholds.get("cost_aware_profit_floor_pct"),
        "strategist_baseline_stop_loss_pct": strategist_adaptive_exit.get("stop_loss_pct"),
        "strategist_baseline_take_profit_pct": strategist_adaptive_exit.get("take_profit_pct"),
        "strategist_baseline_trailing_stop_pct": strategist_adaptive_exit.get("trailing_stop_pct"),
    }


def build_monitor_blocker_trace(monitor: Dict[str, Any]) -> Dict[str, Any]:
    data = monitor if isinstance(monitor, dict) else {}
    entry_metrics = data.get("entry_metrics") if isinstance(data.get("entry_metrics"), dict) else {}
    entry_thresholds = data.get("entry_thresholds") if isinstance(data.get("entry_thresholds"), dict) else {}
    timing_assessment = data.get("timing_assessment") if isinstance(data.get("timing_assessment"), dict) else {}
    policy_ref = data.get("policy_ref") if isinstance(data.get("policy_ref"), dict) else {}
    threshold_shortfalls: List[str] = []
    if entry_metrics.get("volume_ratio") not in (None, "") and entry_thresholds.get("volume_ratio_min") not in (None, ""):
        volume_ratio = safe_float(entry_metrics.get("volume_ratio"), 0.0)
        volume_ratio_min = safe_float(entry_thresholds.get("volume_ratio_min"), 0.0)
        if volume_ratio < volume_ratio_min:
            threshold_shortfalls.append(f"volume ratio {volume_ratio:.2f} below min {volume_ratio_min:.2f}")
    if entry_metrics.get("extended_from_vwap_pct") not in (None, "") and entry_thresholds.get("max_extended_from_vwap_pct") not in (None, ""):
        extended = safe_float(entry_metrics.get("extended_from_vwap_pct"), 0.0)
        extended_max = safe_float(entry_thresholds.get("max_extended_from_vwap_pct"), 0.0)
        if extended > extended_max:
            threshold_shortfalls.append(
                f"VWAP extension {format_ratio_pct(extended)}% above max {format_ratio_pct(extended_max)}%"
            )
    if entry_metrics.get("pullback_depth_pct") not in (None, "") and entry_thresholds.get("pullback_min_pct") not in (None, ""):
        pullback_depth = safe_float(entry_metrics.get("pullback_depth_pct"), 0.0)
        pullback_min = safe_float(entry_thresholds.get("pullback_min_pct"), 0.0)
        if pullback_depth < pullback_min:
            threshold_shortfalls.append(
                f"pullback depth {format_ratio_pct(pullback_depth)}% below min {format_ratio_pct(pullback_min)}%"
            )
    return {
        "entry_check_summary": clip(data.get("entry_check_summary"), max_len=260),
        "entry_blockers": _list_text(data.get("entry_blockers"), limit=8, max_len=120),
        "threshold_shortfalls": threshold_shortfalls[:4],
        "timing_assessment": dict(timing_assessment or {}),
        "policy_ref": dict(policy_ref or {}),
        "entry_condition_path": clip(data.get("entry_condition_path"), max_len=80),
        "entry_condition_paths_passed": _list_text(data.get("entry_condition_paths_passed"), limit=4, max_len=80),
        "condition_scores": dict(data.get("condition_scores") or {}),
        "grouped_logic_trace": dict(data.get("grouped_logic_trace") or {}),
    }


def build_execution_outcome_human(
    execution: Dict[str, Any],
    executor: Dict[str, Any],
    *,
    story_type: str,
    mode_label: str,
) -> Dict[str, Any]:
    return build_execution_outcome_human_payload(
        execution,
        executor,
        story_type=story_type,
        mode_label=mode_label,
    )

# P1.5.2 R2-C: market / scanner / monitor human payload owners.


def build_monitor_reason_human(monitor: Dict[str, Any], execution: Dict[str, Any], *, deps: Mapping[str, Any]) -> Dict[str, Any]:
    _build_monitor_blocker_trace = deps["build_monitor_blocker_trace"]
    _build_monitor_stop_policy_trace = deps["build_monitor_stop_policy_trace"]
    _list_text = deps["list_text"]
    _merge_missing_values = deps["merge_missing_values"]
    format_exit_label = deps["format_exit_label"]
    format_ratio_pct = deps["format_ratio_pct"]
    safe_float = deps["safe_float"]
    safe_int = deps["safe_int"]
    action = str(execution.get("action") or "").upper()
    decision_trace = monitor.get("decision_trace") if isinstance(monitor.get("decision_trace"), dict) else {}
    thresholds = monitor.get("thresholds") if isinstance(monitor.get("thresholds"), dict) else {}
    thresholds_guards_used = (
        decision_trace.get("thresholds_guards_used")
        if isinstance(decision_trace.get("thresholds_guards_used"), dict)
        else (
            monitor.get("thresholds_guards_used")
            if isinstance(monitor.get("thresholds_guards_used"), dict)
            else {}
        )
    )
    threshold_snapshot = (
        monitor.get("threshold_snapshot")
        if isinstance(monitor.get("threshold_snapshot"), dict)
        else {}
    )
    thresholds = _merge_missing_values(
        thresholds,
        thresholds_guards_used.get("thresholds") if isinstance(thresholds_guards_used.get("thresholds"), dict) else {},
    )
    for key in (
        "stop_loss_pct",
        "effective_stop_loss_pct",
        "effective_stop_reason",
        "take_profit_pct",
        "peak_drawdown_exit_pct",
        "trailing_stop_pct",
        "vwap_breakdown_pct",
        "intraday_low_break_pct",
        "trend_strength_floor",
    ):
        if thresholds.get(key) in (None, "", [], {}):
            thresholds[key] = monitor.get(key)
    trigger_details = monitor.get("trigger_details") if isinstance(monitor.get("trigger_details"), dict) else {}
    decision_reason_chain = [str(x or "") for x in list(monitor.get("decision_reason_chain") or []) if str(x or "").strip()]
    timing_assessment = decision_trace.get("timing_assessment") if isinstance(decision_trace.get("timing_assessment"), dict) else {}
    policy_ref = decision_trace.get("policy_ref") if isinstance(decision_trace.get("policy_ref"), dict) else {}
    received_policy = (
        monitor.get("received_policy")
        if isinstance(monitor.get("received_policy"), dict)
        else (
            threshold_snapshot.get("received_policy")
            if isinstance(threshold_snapshot.get("received_policy"), dict)
            else (
                policy_ref.get("received_policy")
                if isinstance(policy_ref.get("received_policy"), dict)
                else {}
            )
        )
    )
    effective_policy = (
        monitor.get("effective_policy")
        if isinstance(monitor.get("effective_policy"), dict)
        else (
            threshold_snapshot.get("effective_policy")
            if isinstance(threshold_snapshot.get("effective_policy"), dict)
            else (
                policy_ref.get("effective_policy")
                if isinstance(policy_ref.get("effective_policy"), dict)
                else {}
            )
        )
    )
    policy_adjustment_summary = str(
        monitor.get("policy_adjustment_summary")
        or threshold_snapshot.get("policy_adjustment_summary")
        or policy_ref.get("policy_adjustment_summary")
        or ""
    ).strip()
    effective_policy_deltas = [
        dict(row)
        for row in list(
            monitor.get("effective_policy_deltas")
            or threshold_snapshot.get("effective_policy_deltas")
            or policy_ref.get("effective_policy_deltas")
            or []
        )[:8]
        if isinstance(row, dict)
    ]
    entry_check_summary = str(decision_trace.get("entry_check_summary") or "").strip()
    entry_blockers = [str(x or "") for x in list(decision_trace.get("entry_blockers") or []) if str(x or "").strip()]
    entry_reason = str(
        timing_assessment.get("entry_reason")
        or monitor.get("entry_reason")
        or ""
    ).strip()
    entry_pattern = str(
        timing_assessment.get("entry_pattern")
        or monitor.get("entry_pattern")
        or ""
    ).strip()
    entry_signal_chain = [str(x or "") for x in list(monitor.get("entry_signal_chain") or []) if str(x or "").strip()]
    entry_condition_path = str(monitor.get("entry_condition_path") or "").strip()
    entry_condition_paths_passed = [str(x or "") for x in list(monitor.get("entry_condition_paths_passed") or []) if str(x or "").strip()]
    entry_condition_scores = monitor.get("entry_condition_scores") if isinstance(monitor.get("entry_condition_scores"), dict) else {}
    entry_grouped_logic_trace = monitor.get("entry_grouped_logic_trace") if isinstance(monitor.get("entry_grouped_logic_trace"), dict) else {}
    entry_metrics = monitor.get("entry_metrics") if isinstance(monitor.get("entry_metrics"), dict) else {}
    human_chart_detail_observed = (
        entry_metrics.get("human_chart_detail_observed")
        if isinstance(entry_metrics.get("human_chart_detail_observed"), dict)
        else {}
    )
    human_chart_detail_context = (
        monitor.get("human_chart_detail_context")
        if isinstance(monitor.get("human_chart_detail_context"), dict)
        else {}
    )
    if not human_chart_detail_observed and isinstance(human_chart_detail_context.get("observed"), dict):
        human_chart_detail_observed = dict(human_chart_detail_context.get("observed") or {})
    entry_thresholds = (
        monitor.get("entry_thresholds")
        if isinstance(monitor.get("entry_thresholds"), dict)
        else {}
    )
    if not entry_thresholds and isinstance(effective_policy, dict):
        entry_thresholds = dict(effective_policy or {})
    if not entry_thresholds and isinstance(monitor.get("applied_policy"), dict):
        entry_thresholds = dict(monitor.get("applied_policy") or {})
    if not entry_thresholds and isinstance(threshold_snapshot.get("entry_thresholds"), dict):
        entry_thresholds = dict(threshold_snapshot.get("entry_thresholds") or {})
    if not entry_thresholds and isinstance(threshold_snapshot.get("applied_policy"), dict):
        entry_thresholds = dict(threshold_snapshot.get("applied_policy") or {})
    entry_guard_blocked = bool(monitor.get("entry_guard_blocked"))
    entry_guard_reason = str(monitor.get("entry_guard_reason") or "").strip()
    entry_evaluated = bool(monitor.get("entry_evaluated"))
    entry_triggered = bool(monitor.get("entry_triggered"))
    exit_reason = str(monitor.get("exit_reason") or "").strip()
    monitor_reason = str(monitor.get("monitor_reason") or monitor.get("evaluation_summary") or "").strip()
    price_source = str(monitor.get("price_source") or "").strip()
    price_source_policy = str(monitor.get("price_source_policy") or "").strip()
    feature_source = str(monitor.get("feature_source") or "").strip()
    current_price = monitor.get("current_price")
    if current_price in (None, ""):
        current_price = monitor.get("price")
    average_price = monitor.get("average_price")
    if average_price in (None, ""):
        average_price = monitor.get("avg_price")
    peak_price = monitor.get("peak_price")
    peak_drawdown = monitor.get("peak_drawdown")
    current_drawdown = monitor.get("current_drawdown")
    vwap_distance = monitor.get("vwap_distance")
    hold_limit_sec = monitor.get("hold_limit_sec")
    if hold_limit_sec in (None, ""):
        hold_limit_sec = (
            thresholds.get("time_stop_sec")
            if safe_int(thresholds.get("time_stop_sec"), 0) > 0
            else thresholds.get("max_hold_sec")
        )
    time_limit_reached = bool(monitor.get("time_limit_reached"))
    time_limit_reason = str(monitor.get("time_limit_reason") or "").strip()
    time_limit_reassessment_required = bool(monitor.get("time_limit_reassessment_required"))
    time_limit_reassessment_blocked = bool(monitor.get("time_limit_reassessment_blocked"))
    time_limit_reassessment_blocked_reason = str(
        monitor.get("time_limit_reassessment_blocked_reason") or ""
    ).strip()
    if current_drawdown in (None, "") and current_price not in (None, "") and peak_price not in (None, ""):
        current_drawdown = (safe_float(current_price, 0.0) / max(safe_float(peak_price, 1.0), 1e-9)) - 1.0
    if current_drawdown in (None, "") and peak_drawdown not in (None, ""):
        current_drawdown = peak_drawdown

    watch_axes = build_monitor_watch_axes(monitor, trigger_details, thresholds, safe_float)
    trigger_type = str(monitor.get("trigger_type") or "").strip()
    if not trigger_type:
        trigger_type = exit_reason if action == "SELL" else entry_reason or monitor_reason
    if not trigger_type and decision_reason_chain:
        trigger_type = decision_reason_chain[-1]
    active_exit_axis = str(monitor.get("active_exit_axis") or trigger_details.get("active_exit_axis") or "").strip()
    if str(monitor_reason or "").strip().lower() in {"hold", "hold_position", "eod_carry_approved"} and not bool(monitor.get("exit_triggered")):
        active_exit_axis = "Hold"
    elif not active_exit_axis:
        active_exit_axis = format_exit_label(trigger_type)
    confirm_required = safe_int(
        thresholds_guards_used.get("exit_confirm_ticks"),
        safe_int(thresholds_guards_used.get("exit_confirm_required"), safe_int(monitor.get("exit_confirm_required"), 0)),
    )
    confirm_count = safe_int(
        thresholds_guards_used.get("exit_confirm_count"),
        safe_int(monitor.get("exit_confirm_count"), 0),
    )
    guard_blocked = bool(trigger_details.get("sell_guard_blocked") or monitor.get("guard_blocked") or monitor.get("sell_guard_blocked"))
    guard_reason = str(trigger_details.get("sell_guard_reason") or monitor.get("guard_reason") or monitor.get("sell_guard_reason") or "").strip()
    exit_pending_confirmation = (
        guard_reason.startswith("exit_confirmation_pending:")
        or exit_reason.startswith("exit_confirmation_pending:")
        or monitor_reason == "exit_signal_pending_confirmation"
    )
    hold_without_confirmed_exit = bool(
        action == "SELL"
        and not bool(monitor.get("exit_triggered"))
        and str(trigger_type or monitor_reason or "").strip().lower() in {"hold", "hold_position"}
    )
    monitor_execution_mismatch = bool(
        action == "SELL"
        and not bool(monitor.get("exit_triggered"))
        and (exit_pending_confirmation or hold_without_confirmed_exit)
    )
    eod_carry_evaluated = bool(monitor.get("eod_carry_evaluated"))
    eod_carry_approved = bool(monitor.get("eod_carry_approved"))
    eod_carry_action = str(monitor.get("eod_carry_action") or "").strip()
    eod_carry_reason = str(monitor.get("eod_carry_reason") or "").strip()
    eod_carry_positive_signals = _list_text(monitor.get("eod_carry_positive_signals"), limit=6, max_len=120)
    eod_carry_blockers = _list_text(monitor.get("eod_carry_blockers"), limit=6, max_len=120)
    eod_carry_anomaly = bool(monitor.get("eod_carry_anomaly"))
    eod_carry_anomaly_reason = str(monitor.get("eod_carry_anomaly_reason") or "").strip()
    minutes_to_close = monitor.get("minutes_to_close")
    entry_threshold_gaps = build_monitor_entry_threshold_gaps(
        entry_metrics, entry_thresholds, safe_float, format_ratio_pct,
    )
    monitor_stop_policy_trace = _build_monitor_stop_policy_trace(monitor, thresholds)
    monitor_blocker_trace = _build_monitor_blocker_trace(
        {
            "entry_check_summary": entry_check_summary,
            "entry_blockers": entry_blockers,
            "entry_metrics": entry_metrics,
            "entry_thresholds": entry_thresholds,
            "timing_assessment": timing_assessment,
            "policy_ref": policy_ref,
            "entry_condition_path": entry_condition_path,
            "entry_condition_paths_passed": entry_condition_paths_passed,
            "condition_scores": entry_condition_scores,
            "grouped_logic_trace": entry_grouped_logic_trace,
        }
    )
    if eod_carry_approved and action not in ("BUY", "SELL"):
        summary = (
            f"Monitor kept the position into the close because overnight carry was approved "
            f"{safe_float(minutes_to_close, 0.0):.1f} minutes before the close."
        )
    elif action == "BUY":
        summary = f"BUY was triggered because {entry_reason or monitor_reason or 'the intraday entry condition passed'}."
        if entry_pattern:
            summary += f" Pattern: {entry_pattern}."
        if entry_condition_path:
            summary += f" Path: {entry_condition_path.replace('_', ' ')}."
    elif action == "SELL":
        if monitor_execution_mismatch:
            pending_label = (
                guard_reason
                or exit_reason
                or monitor_reason
                or (
                    "monitor posture was hold without a confirmed exit trigger"
                    if hold_without_confirmed_exit
                    else "exit confirmation was pending"
                )
            )
            summary = (
                "Executor recorded SELL, but the monitor had not confirmed the exit yet "
                f"({pending_label}). This is a monitor/executor mismatch, not a confirmed exit trigger."
            )
        elif eod_carry_evaluated and not eod_carry_approved and str(trigger_type or "").strip().lower() in ("eod_flat", "carry_overnight_approved"):
            summary = (
                f"SELL was triggered to flatten before the close because overnight carry was not approved "
                f"({eod_carry_reason or 'carry conditions were not met'})."
            )
        else:
            summary = f"SELL was triggered because {trigger_type or monitor_reason or 'the exit condition passed'}."
    elif eod_carry_anomaly:
        summary = (
            f"Monitor kept the position without a valid end-of-day carry decision because "
            f"{eod_carry_anomaly_reason or 'the carry evaluation context was incomplete'}."
        )
    elif entry_evaluated and not entry_triggered:
        summary = f"Monitor stayed on WAIT because {entry_check_summary or entry_reason or monitor_reason or 'the intraday entry signal was not confirmed'}."
        if entry_threshold_gaps:
            summary += " Threshold gaps: " + "; ".join(entry_threshold_gaps[:3]) + "."
    else:
        summary = f"Monitor posture was {action or 'WAIT'} with trigger {trigger_type or 'not_captured'}."
    bullets = [
        f"Posture: {action or 'WAIT'}",
        (
            f"Trigger type: {trigger_type or 'not_captured'} (pending, not confirmed)"
            if monitor_execution_mismatch
            else f"Trigger type: {trigger_type or 'not_captured'}"
        ),
        f"Monitor reason: {monitor_reason or trigger_type or 'not_captured'}",
        f"Position age: {safe_int(monitor.get('position_age_seconds'), 0)} seconds",
        f"Hold time limit: {safe_int(hold_limit_sec, 0)} seconds" if safe_int(hold_limit_sec, 0) > 0 else "Hold time limit: not configured",
        f"Stop loss: {format_ratio_pct(thresholds.get('stop_loss_pct'))}%",
        f"Effective stop: {format_ratio_pct(thresholds.get('effective_stop_loss_pct'))}%",
        f"Effective stop reason: {str(thresholds.get('effective_stop_reason') or 'not_captured')}",
        f"Take profit: {format_ratio_pct(thresholds.get('take_profit_pct'))}%",
        f"Active exit axis: {active_exit_axis or 'not_captured'}",
        f"Exit confirmation: {confirm_count}/{confirm_required}" if confirm_required > 0 else "Exit confirmation: not required",
        f"Min hold blocked: {'yes' if monitor.get('min_hold_blocked') else 'no'}",
        f"Sell cooldown blocked: {'yes' if monitor.get('sell_cooldown_blocked') else 'no'}",
        f"Exit triggered: {'yes' if monitor.get('exit_triggered') else 'no'}",
    ]
    if time_limit_reassessment_required:
        bullets.append(
            "Time-limit reassessment: "
            f"{'blocked by profit floor' if time_limit_reassessment_blocked else 'allowed'} "
            f"({time_limit_reassessment_blocked_reason or time_limit_reason or 'time limit reached'})"
        )
    append_monitor_policy_observation_bullets(
        bullets, monitor_stop_policy_trace, safe_float=safe_float,
        safe_int=safe_int, format_ratio_pct=format_ratio_pct,
    )
    append_monitor_entry_review_bullets(
        bullets,
        entry_evaluated=entry_evaluated,
        entry_triggered=entry_triggered,
        entry_pattern=entry_pattern,
        entry_signal_chain=entry_signal_chain,
        entry_condition_path=entry_condition_path,
        entry_condition_paths_passed=entry_condition_paths_passed,
        entry_condition_scores=entry_condition_scores,
        entry_guard_blocked=entry_guard_blocked,
        entry_guard_reason=entry_guard_reason,
        entry_metrics=entry_metrics,
        entry_thresholds=entry_thresholds,
        human_chart_detail_observed=human_chart_detail_observed,
        entry_check_summary=entry_check_summary,
        entry_blockers=entry_blockers,
        entry_threshold_gaps=entry_threshold_gaps,
        policy_adjustment_summary=policy_adjustment_summary,
        effective_policy_deltas=effective_policy_deltas,
        policy_ref=policy_ref,
        safe_float=safe_float,
        safe_int=safe_int,
        format_ratio_pct=format_ratio_pct,
    )
    if eod_carry_evaluated:
        bullets.append(
            f"EOD carry decision: {'approved' if eod_carry_approved else 'flatten before close'} "
            f"({eod_carry_reason or 'not_captured'})"
        )
        if minutes_to_close not in (None, ""):
            bullets.append(f"Minutes to close at decision: {safe_float(minutes_to_close, 0.0):.1f}")
        if eod_carry_positive_signals:
            bullets.append("Carry positives: " + "; ".join(eod_carry_positive_signals[:4]))
        if eod_carry_blockers:
            bullets.append("Carry blockers: " + "; ".join(eod_carry_blockers[:4]))
    if eod_carry_anomaly:
        bullets.append(
            f"EOD carry anomaly: yes ({eod_carry_anomaly_reason or 'carry evaluation context missing'})"
        )
    if watch_axes:
        bullets.append("Watch axes: " + ", ".join(watch_axes[:8]))
    if decision_reason_chain:
        bullets.append("Decision chain: " + " -> ".join(decision_reason_chain[:5]))
    entry_quant_decision = monitor.get("entry_quant_decision") if isinstance(monitor.get("entry_quant_decision"), dict) else {}
    exit_quant_decision = monitor.get("exit_quant_decision") if isinstance(monitor.get("exit_quant_decision"), dict) else {}
    quant_factor_snapshot = monitor.get("quant_factor_snapshot") if isinstance(monitor.get("quant_factor_snapshot"), dict) else {}
    if entry_quant_decision:
        blockers = [str(x or "") for x in list(entry_quant_decision.get("blockers") or []) if str(x or "").strip()]
        warnings = [str(x or "") for x in list(entry_quant_decision.get("warnings") or []) if str(x or "").strip()]
        bullets.append(
            "Entry quant decision: "
            f"{entry_quant_decision.get('decision') or 'not_captured'} "
            f"(blockers: {', '.join(blockers[:4]) or 'none'}; warnings: {', '.join(warnings[:4]) or 'none'})"
        )
    if exit_quant_decision:
        blockers = [str(x or "") for x in list(exit_quant_decision.get("blockers") or []) if str(x or "").strip()]
        warnings = [str(x or "") for x in list(exit_quant_decision.get("warnings") or []) if str(x or "").strip()]
        bullets.append(
            "Exit quant decision: "
            f"{exit_quant_decision.get('decision') or 'not_captured'} "
            f"(blockers: {', '.join(blockers[:4]) or 'none'}; warnings: {', '.join(warnings[:4]) or 'none'})"
        )
    if guard_blocked or guard_reason:
        bullets.append(f"Guard blocked: {'yes' if guard_blocked else 'no'} ({guard_reason or 'no guard reason captured'})")
    if monitor_execution_mismatch:
        mismatch_label = (
            "SELL recorded while monitor posture was hold"
            if hold_without_confirmed_exit
            else "SELL recorded while monitor exit confirmation was pending"
        )
        bullets.append(f"Monitor/executor mismatch: yes ({mismatch_label})")
    if current_price not in (None, ""):
        bullets.append(f"Current price: {safe_float(current_price, 0.0):.2f}")
    if average_price not in (None, ""):
        bullets.append(f"Average price: {safe_float(average_price, 0.0):.2f}")
    if peak_price not in (None, ""):
        bullets.append(f"Peak price: {safe_float(peak_price, 0.0):.2f}")
    if current_drawdown not in (None, ""):
        bullets.append(f"Current drawdown: {format_ratio_pct(current_drawdown)}%")
    if peak_drawdown not in (None, ""):
        bullets.append(f"Peak drawdown: {format_ratio_pct(peak_drawdown)}%")
    if vwap_distance not in (None, ""):
        bullets.append(f"VWAP distance: {format_ratio_pct(vwap_distance)}%")
    if price_source:
        bullets.append(f"Price source: {price_source}")
    if feature_source:
        bullets.append(f"Feature source: {feature_source}")
    if price_source_policy:
        bullets.append(f"Price source policy: {price_source_policy}")
    return {
        "posture": action or "WAIT",
        "trigger_type": trigger_type,
        "summary": summary,
        "bullets": bullets,
        "position_age_seconds": safe_int(monitor.get("position_age_seconds"), 0),
        "hold_limit_sec": safe_int(hold_limit_sec, 0),
        "time_limit_reached": time_limit_reached,
        "time_limit_reason": time_limit_reason,
        "time_limit_reassessment_required": time_limit_reassessment_required,
        "time_limit_reassessment_blocked": time_limit_reassessment_blocked,
        "time_limit_reassessment_blocked_reason": time_limit_reassessment_blocked_reason,
        "stop_loss_pct": thresholds.get("stop_loss_pct"),
        "hard_stop_pct": monitor_stop_policy_trace.get("hard_stop_pct"),
        "adaptive_stop_loss_pct": monitor_stop_policy_trace.get("adaptive_stop_loss_pct"),
        "effective_stop_loss_pct": monitor_stop_policy_trace.get("effective_stop_loss_pct"),
        "effective_stop_reason": str(thresholds.get("effective_stop_reason") or "").strip(),
        "take_profit_pct": monitor_stop_policy_trace.get("take_profit_pct"),
        "trailing_stop_pct": monitor_stop_policy_trace.get("trailing_stop_pct"),
        "exit_triggered": bool(monitor.get("exit_triggered")),
        "entry_evaluated": entry_evaluated,
        "entry_triggered": entry_triggered,
        "entry_reason": entry_reason,
        "entry_pattern": entry_pattern,
        "entry_signal_chain": entry_signal_chain[:8],
        "entry_condition_path": entry_condition_path,
        "entry_condition_paths_passed": entry_condition_paths_passed[:4],
        "entry_condition_scores": dict(entry_condition_scores),
        "entry_grouped_logic_trace": dict(entry_grouped_logic_trace),
        "entry_metrics": dict(entry_metrics),
        "human_chart_detail_observed": dict(human_chart_detail_observed),
        "entry_thresholds": dict(entry_thresholds),
        "entry_check_summary": entry_check_summary,
        "entry_blockers": entry_blockers[:8],
        "threshold_shortfalls": entry_threshold_gaps[:4],
        "policy_ref": dict(policy_ref),
        "received_policy": dict(received_policy),
        "effective_policy": dict(effective_policy),
        "policy_adjustment_summary": policy_adjustment_summary,
        "effective_policy_deltas": effective_policy_deltas,
        "monitor_stop_policy_trace": monitor_stop_policy_trace,
        "monitor_blocker_trace": monitor_blocker_trace,
        "timing_assessment": dict(timing_assessment),
        "thresholds_guards_used": dict(thresholds_guards_used),
        "quant_factor_snapshot": dict(quant_factor_snapshot),
        "entry_quant_decision": dict(entry_quant_decision),
        "exit_quant_decision": dict(exit_quant_decision),
        "entry_guard_blocked": entry_guard_blocked,
        "entry_guard_reason": entry_guard_reason,
        "current_price": current_price,
        "average_price": average_price,
        "peak_price": peak_price,
        "current_drawdown": current_drawdown,
        "peak_drawdown": peak_drawdown,
        "vwap_distance": vwap_distance,
        "active_exit_axis": active_exit_axis,
        "watch_axes": watch_axes[:8],
        "confirm_required": confirm_required,
        "confirm_count": confirm_count,
        "guard_blocked": guard_blocked,
        "guard_reason": guard_reason,
        "pending_confirmation": exit_pending_confirmation,
        "monitor_execution_mismatch": monitor_execution_mismatch,
        "eod_carry_evaluated": eod_carry_evaluated,
        "eod_carry_approved": eod_carry_approved,
        "eod_carry_action": eod_carry_action,
        "eod_carry_reason": eod_carry_reason,
        "eod_carry_positive_signals": eod_carry_positive_signals,
        "eod_carry_blockers": eod_carry_blockers,
        "eod_carry_anomaly": eod_carry_anomaly,
        "eod_carry_anomaly_reason": eod_carry_anomaly_reason,
        "decision_reason_chain": decision_reason_chain[:6],
        "price_source": price_source,
        "feature_source": feature_source,
        "price_source_policy": price_source_policy,
    }


