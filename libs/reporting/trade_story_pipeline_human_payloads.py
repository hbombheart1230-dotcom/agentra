from __future__ import annotations

from .trade_story_human_parts.monitor_context import prepare_monitor_review_context
from .trade_story_human_parts.monitor_traces import (
    resolve_strategist_adaptive_exit_impl, build_monitor_stop_policy_trace_impl,
    build_monitor_blocker_trace_impl,
)

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
    return resolve_strategist_adaptive_exit_impl(monitor)


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
    return build_monitor_stop_policy_trace_impl(
        monitor, thresholds, normalize_stop_thresholds=normalize_stop_thresholds,
        resolve_strategist_adaptive_exit=resolve_strategist_adaptive_exit,
        resolve_adaptive_stop_loss_pct=resolve_adaptive_stop_loss_pct,
    )


def build_monitor_blocker_trace(monitor: Dict[str, Any]) -> Dict[str, Any]:
    return build_monitor_blocker_trace_impl(
        monitor, clip=clip, _list_text=_list_text, safe_float=safe_float,
        format_ratio_pct=format_ratio_pct,
    )


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
    (
        action, active_exit_axis, average_price, confirm_count, confirm_required,
        current_drawdown, current_price, decision_reason_chain, effective_policy, effective_policy_deltas,
        entry_blockers, entry_check_summary, entry_condition_path, entry_condition_paths_passed, entry_condition_scores,
        entry_evaluated, entry_grouped_logic_trace, entry_guard_blocked, entry_guard_reason, entry_metrics,
        entry_pattern, entry_reason, entry_signal_chain, entry_threshold_gaps, entry_thresholds,
        entry_triggered, eod_carry_action, eod_carry_anomaly, eod_carry_anomaly_reason, eod_carry_approved,
        eod_carry_blockers, eod_carry_evaluated, eod_carry_positive_signals, eod_carry_reason, exit_pending_confirmation,
        exit_reason, feature_source, guard_blocked, guard_reason, hold_limit_sec,
        hold_without_confirmed_exit, human_chart_detail_observed, minutes_to_close, monitor_blocker_trace, monitor_execution_mismatch,
        monitor_reason, monitor_stop_policy_trace, peak_drawdown, peak_price, policy_adjustment_summary,
        policy_ref, price_source, price_source_policy, received_policy, thresholds,
        thresholds_guards_used, time_limit_reached, time_limit_reason, time_limit_reassessment_blocked, time_limit_reassessment_blocked_reason,
        time_limit_reassessment_required, timing_assessment, trigger_type, vwap_distance, watch_axes,
    ) = prepare_monitor_review_context(
        monitor, execution, deps=deps,
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


