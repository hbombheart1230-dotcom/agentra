"""Monitor observation views; policy/effects remain at the facade."""
from __future__ import annotations

from typing import Any, Dict, List


def annotate_entry_policy_fields(effective_policy_trace, entry_info, entry_policy_contract, monitor_memory_bias, monitor_memory_bias_observation_only, monitor_memory_bias_observed_entry_result, monitor_memory_bias_result, monitor_memory_bias_summary, *, facade):
    entry_info["received_policy"] = dict(effective_policy_trace.get("received_policy") or {})
    entry_info["received_policy_source"] = str(effective_policy_trace.get("received_policy_source") or "")
    entry_info["policy_contract"] = dict(entry_policy_contract)
    entry_info["effective_policy"] = dict(effective_policy_trace.get("effective_policy") or {})
    entry_info["effective_policy_source"] = str(effective_policy_trace.get("effective_policy_source") or "")
    entry_info["effective_policy_source_chain"] = list(effective_policy_trace.get("effective_policy_source_chain") or [])
    entry_info["policy_adjustments"] = dict(effective_policy_trace.get("policy_adjustments") or {})
    entry_info["policy_adjustment_summary"] = str(effective_policy_trace.get("policy_adjustment_summary") or "")
    entry_info["policy_adjustment_reasoning"] = str(effective_policy_trace.get("policy_adjustment_reasoning") or "")
    entry_info["effective_policy_deltas"] = list(effective_policy_trace.get("effective_policy_deltas") or [])
    entry_info["monitor_memory_bias_applied"] = bool(monitor_memory_bias_result.get("applied"))
    entry_info["monitor_memory_bias_observation_only"] = bool(monitor_memory_bias_observation_only)
    entry_info["monitor_memory_bias"] = dict(monitor_memory_bias)
    entry_info["monitor_memory_bias_summary"] = dict(monitor_memory_bias_summary)
    entry_info["monitor_memory_bias_deltas"] = list(monitor_memory_bias_result.get("deltas") or [])
    entry_info["monitor_memory_bias_observed_deltas"] = list(
        monitor_memory_bias_observed_entry_result.get("deltas") or []
    )
    entry_memory_application_trace = facade.build_monitor_commander_memory_application_trace(
        monitor_memory_bias=monitor_memory_bias,
        entry_result=monitor_memory_bias_result,
        hold_result={"applied": False, "deltas": []},
        exit_result={"applied": False, "deltas": []},
        monitor_memory_bias_summary=monitor_memory_bias_summary,
        effective_policy_source=str(effective_policy_trace.get("effective_policy_source") or ""),
        effective_policy_source_chain=list(effective_policy_trace.get("effective_policy_source_chain") or []),
    )
    entry_info["commander_memory_application_trace"] = dict(entry_memory_application_trace)
    entry_info["monitor_memory_application_trace"] = dict(entry_memory_application_trace)
    return None


def annotate_entry_minute_metrics(entry_info, entry_row_source, entry_rows, minute_fetch_meta, minute_ohlcv_meta, *, facade):
    entry_metrics = entry_info.get("metrics") if isinstance(entry_info.get("metrics"), dict) else {}
    entry_metrics["minute_source_present"] = bool(entry_rows)
    entry_metrics["minute_source_used"] = entry_row_source or ""
    latest_candle_ts = None
    if entry_rows and isinstance(entry_rows[-1], dict):
        latest_candle_ts = entry_rows[-1].get("ts")
    entry_metrics["latest_candle_ts"] = latest_candle_ts
    entry_metrics["minute_snapshot_age_minutes"] = minute_fetch_meta.get("minute_snapshot_age_minutes")
    entry_metrics["minute_snapshot_was_stale"] = bool(minute_fetch_meta.get("minute_snapshot_was_stale"))
    entry_metrics["minute_refetch_attempted"] = bool(minute_fetch_meta.get("minute_refetch_attempted"))
    entry_metrics["minute_refetch_succeeded"] = bool(minute_fetch_meta.get("minute_refetch_succeeded"))
    entry_metrics["minute_refetch_reason"] = str(minute_fetch_meta.get("minute_refetch_reason") or "")
    entry_metrics["minute_refetch_trigger_reason"] = str(minute_fetch_meta.get("minute_refetch_trigger_reason") or "")
    entry_metrics["minute_refetch_failure_reason"] = str(minute_fetch_meta.get("minute_refetch_failure_reason") or "")
    entry_metrics["minute_refetch_failure_detail"] = str(minute_fetch_meta.get("minute_refetch_failure_detail") or "")
    entry_metrics["minute_refetch_runner_source"] = str(minute_fetch_meta.get("minute_refetch_runner_source") or "")
    entry_metrics["minute_refetch_produced_fresh_snapshot"] = bool(
        minute_fetch_meta.get("minute_refetch_produced_fresh_snapshot")
    )
    entry_metrics["minute_cache_fallback_used"] = bool(minute_fetch_meta.get("minute_cache_fallback_used"))
    entry_metrics["minute_cache_fallback_source"] = str(minute_fetch_meta.get("minute_cache_fallback_source") or "")
    entry_info["metrics"] = entry_metrics
    entry_info["minute_source_meta"] = dict(minute_ohlcv_meta or {})
    entry_info["minute_fetch_meta"] = minute_fetch_meta
    return None


def build_monitor_policy_trace(
    *,
    commander_context: Dict[str, Any],
    monitor_policy: Dict[str, Any],
    strategist_plan: Dict[str, Any],
    policy_provenance: Dict[str, Any],
    entry_info: Dict[str, Any],
    exit_info: Dict[str, Any],
    current_reason: str,
    facade,
) -> Dict[str, Any]:
    consumed_fields: List[str] = []
    for key in (
        "monitor_mission",
        "flow_instruction",
        "command_intent",
        "risk_mode",
        "no_trade_reason_code",
        "llm_policy",
        "source_priority",
        "entry_control",
        "commander_entry_control",
    ):
        value = commander_context.get(key)
        if value not in (None, "", [], {}):
            consumed_fields.append(key)
    commander_context_consumed = bool(consumed_fields)

    strategy_fields: List[str] = []
    for key in ("selected_playbook", "entry_plan", "exit_plan", "symbol_constraints", "strategy_summary"):
        value = strategist_plan.get(key)
        if value not in (None, "", [], {}):
            strategy_fields.append(key)

    flow_instruction = str(commander_context.get("flow_instruction") or "").strip()
    no_trade_reason_code = str(commander_context.get("no_trade_reason_code") or "").strip()
    monitor_mission = str(commander_context.get("monitor_mission") or "").strip()
    entry_plan = dict(strategist_plan.get("entry_plan") or {})
    exit_plan = dict(strategist_plan.get("exit_plan") or {})

    def _policy_meta_value(key: str, default: Any = "") -> Any:
        commander_value = commander_context.get(key)
        if commander_value not in (None, "", [], {}):
            return commander_value
        monitor_value = monitor_policy.get(key)
        if monitor_value not in (None, "", [], {}):
            return monitor_value
        return default

    entry_blockers = list(
        dict.fromkeys(
            [
                no_trade_reason_code,
                str(entry_info.get("guard_reason") or "").strip(),
                str(entry_info.get("reason") or "").strip(),
                *[str(x or "").strip() for x in list(entry_info.get("failed_checks") or []) if str(x or "").strip()],
            ]
        )
    )
    entry_blockers = [item for item in entry_blockers if item][:8]

    summary_parts: List[str] = []
    if monitor_mission:
        summary_parts.append(f"mission={monitor_mission}")
    if flow_instruction:
        summary_parts.append(f"flow={flow_instruction}")
    if str(strategist_plan.get("selected_playbook") or "").strip():
        summary_parts.append(f"playbook={str(strategist_plan.get('selected_playbook') or '').strip()}")
    if current_reason:
        summary_parts.append(f"reason={current_reason}")

    return {
        "commander_context_consumed": commander_context_consumed,
        "consumed_fields": consumed_fields + strategy_fields,
        "flow_instruction_applied": bool(flow_instruction),
        "no_trade_reason_applied": bool(no_trade_reason_code),
        "shadow_used": bool(
            commander_context.get("shadow_used")
            if commander_context.get("shadow_used") is not None
            else policy_provenance.get("shadow_used")
        ),
        "strategist_fallback_used": bool(
            commander_context.get("strategist_fallback_used")
            if commander_context.get("strategist_fallback_used") is not None
            else policy_provenance.get("strategist_fallback_used")
        ),
        "policy_ref": {
            "monitor_mission": monitor_mission,
            "flow_instruction": flow_instruction,
            "command_intent": str(commander_context.get("command_intent") or ""),
            "risk_mode": str(commander_context.get("risk_mode") or ""),
            "no_trade_reason_code": no_trade_reason_code,
            "llm_policy": str(commander_context.get("llm_policy") or ""),
            "source_priority": list(commander_context.get("source_priority") or []),
            "entry_control": dict(commander_context.get("entry_control") or {})
            if isinstance(commander_context.get("entry_control"), dict)
            else {},
            "applied_policy": dict(commander_context.get("applied_policy") or {})
            if isinstance(commander_context.get("applied_policy"), dict)
            else dict(monitor_policy.get("applied_policy") or {})
            if isinstance(monitor_policy.get("applied_policy"), dict)
            else {},
            "policy_source": str(_policy_meta_value("policy_source", "")),
            "policy_validation_status": str(_policy_meta_value("policy_validation_status", "")),
            "policy_fallback_used": bool(_policy_meta_value("policy_fallback_used", False)),
            "policy_fallback_reason": str(_policy_meta_value("policy_fallback_reason", "")),
            "policy_partial_normalized": bool(_policy_meta_value("policy_partial_normalized", False)),
            "policy_default_filled_fields": list(_policy_meta_value("policy_default_filled_fields", [])),
            "policy_validation_missing_fields": list(_policy_meta_value("policy_validation_missing_fields", [])),
            "policy_validation_invalid_fields": list(_policy_meta_value("policy_validation_invalid_fields", [])),
            "override_reason": str(_policy_meta_value("override_reason", "")),
            "applied_policy_source_chain": list(_policy_meta_value("applied_policy_source_chain", [])),
            "selected_playbook": str(strategist_plan.get("selected_playbook") or ""),
            "entry_plan": entry_plan,
            "exit_plan": exit_plan,
            "symbol_constraints": dict(strategist_plan.get("symbol_constraints") or {}),
            "strategy_summary": str(strategist_plan.get("strategy_summary") or ""),
        },
        "entry_check_summary": " | ".join(summary_parts) if summary_parts else str(current_reason or entry_info.get("reason") or ""),
        "entry_blockers": entry_blockers,
        "timing_assessment": {
            "entry_pattern": str(entry_info.get("pattern") or ""),
            "entry_reason": str(entry_info.get("reason") or ""),
            "entry_plan": entry_plan,
            "monitor_mission": monitor_mission,
            "strategy_summary": str(strategist_plan.get("strategy_summary") or ""),
        },
        "exit_trigger_basis": {
            "exit_reason": str(exit_info.get("reason") or ""),
            "active_exit_axis": str(exit_info.get("active_exit_axis") or ""),
            "final_exit_thresholds": dict(exit_info.get("final_exit_thresholds") or {}),
            "exit_threshold_source": str(exit_info.get("exit_threshold_source") or ""),
            "hold_block_reason": str(exit_info.get("hold_block_reason") or ""),
            "hold_limit_sec": exit_info.get("hold_limit_sec"),
            "max_hold_reached": bool(exit_info.get("max_hold_reached")),
            "time_stop_reached": bool(exit_info.get("time_stop_reached")),
            "time_limit_reached": bool(exit_info.get("time_limit_reached")),
            "time_limit_reason": str(exit_info.get("time_limit_reason") or ""),
            "time_limit_reassessment_required": bool(exit_info.get("time_limit_reassessment_required")),
            "time_limit_reassessment_blocked": bool(exit_info.get("time_limit_reassessment_blocked")),
            "time_limit_reassessment_blocked_reason": str(
                exit_info.get("time_limit_reassessment_blocked_reason") or ""
            ),
            "max_runup_pct": exit_info.get("max_runup_pct"),
            "peak_drawdown_from_peak": exit_info.get("peak_drawdown_from_peak"),
            "peak_drawdown_armed": bool(exit_info.get("peak_drawdown_armed")),
            "peak_drawdown_mode": str(exit_info.get("peak_drawdown_mode") or ""),
            "peak_drawdown_blocked": bool(exit_info.get("peak_drawdown_blocked")),
            "peak_drawdown_block_reason": str(exit_info.get("peak_drawdown_block_reason") or ""),
            "peak_drawdown_profit_floor_required_pct": exit_info.get("peak_drawdown_profit_floor_required_pct"),
            "peak_drawdown_profit_floor_met": bool(exit_info.get("peak_drawdown_profit_floor_met")),
            "final_peak_drawdown_ratio": exit_info.get("final_peak_drawdown_ratio"),
            "peak_drawdown_source": str(exit_info.get("peak_drawdown_source") or ""),
            "exit_trigger_metric_name": str(exit_info.get("exit_trigger_metric_name") or ""),
            "exit_trigger_metric_value": exit_info.get("exit_trigger_metric_value"),
            "exit_trigger_metric_source": str(exit_info.get("exit_trigger_metric_source") or ""),
            "gross_pnl_ratio": exit_info.get("gross_pnl_ratio"),
            "technical_pnl_ratio": exit_info.get("technical_pnl_ratio"),
            "stop_pnl_ratio": exit_info.get("stop_pnl_ratio"),
            "stop_pnl_ratio_source": str(exit_info.get("stop_pnl_ratio_source") or ""),
            "hard_stop_pnl_ratio": exit_info.get("hard_stop_pnl_ratio"),
            "hard_stop_pnl_ratio_source": str(exit_info.get("hard_stop_pnl_ratio_source") or ""),
            "cost_drag_pressure": bool(exit_info.get("cost_drag_pressure")),
            "cost_drag_pressure_pct": exit_info.get("cost_drag_pressure_pct"),
            "cost_drag_pressure_reason": str(exit_info.get("cost_drag_pressure_reason") or ""),
            "stop_loss_cost_drag_blocked": bool(exit_info.get("stop_loss_cost_drag_blocked")),
            "stop_loss_cost_drag_blocked_reason": str(exit_info.get("stop_loss_cost_drag_blocked_reason") or ""),
            "cost_aware_profit_floor_enabled": bool(exit_info.get("cost_aware_profit_floor_enabled")),
            "cost_aware_profit_floor_pct": exit_info.get("cost_aware_profit_floor_pct"),
            "cost_aware_profit_floor_met": bool(exit_info.get("cost_aware_profit_floor_met")),
            "cost_aware_profit_floor_gap_pct": exit_info.get("cost_aware_profit_floor_gap_pct"),
            "cost_aware_profit_floor_blocked": bool(exit_info.get("cost_aware_profit_floor_blocked")),
            "protective_exit_floor_blocked": bool(exit_info.get("protective_exit_floor_blocked")),
            "protective_exit_floor_blocked_reason": str(exit_info.get("protective_exit_floor_blocked_reason") or ""),
            "protective_exit_hard_invalidation": bool(exit_info.get("protective_exit_hard_invalidation")),
            "protective_exit_hard_invalidation_reason": str(
                exit_info.get("protective_exit_hard_invalidation_reason") or ""
            ),
            "exit_plan": exit_plan,
            "monitor_mission": monitor_mission,
        },
    }


def build_monitor_effective_policy_trace(
    *,
    received_policy: Dict[str, Any],
    effective_policy: Dict[str, Any],
    frame: Dict[str, Any],
    received_policy_source: str,
    facade,
) -> Dict[str, Any]:
    adjustment_inputs = facade.monitor_policy_adjustment_inputs(frame)
    deltas = facade.summarize_monitor_policy_deltas(received_policy, effective_policy)
    changed_fields = [str((row or {}).get("field") or "") for row in deltas if str((row or {}).get("field") or "").strip()]
    applied_rules = [str(x or "").strip() for x in list(effective_policy.get("adjustments") or []) if str(x or "").strip()]
    frame_labels = [
        str(adjustment_inputs.get("playbook") or "").strip(),
        str(adjustment_inputs.get("monitor_guidance") or "").strip(),
        str(adjustment_inputs.get("risk_tone") or "").strip(),
        str(adjustment_inputs.get("trade_aggressiveness") or "").strip(),
    ]
    frame_labels = [x for x in frame_labels if x]
    if deltas:
        if frame_labels:
            summary = f"{' + '.join(frame_labels)} adjusted {', '.join(changed_fields[:4])}"
        else:
            summary = f"strategy frame adjusted {', '.join(changed_fields[:4])}"
        reasoning = (
            f"Monitor used an effective policy derived from the commander-confirmed baseline after "
            f"strategy-frame adjustment. Changed fields: {', '.join(changed_fields[:6])}."
        )
        effective_policy_source = "monitor_frame_adjusted"
        effective_policy_source_chain = [
            str(received_policy_source or "monitor_received_policy"),
            "strategy_frame_adjustment",
            "monitor_effective_policy",
        ]
    else:
        summary = "Monitor used the received policy without strategy-frame threshold changes."
        reasoning = "Monitor used the received baseline policy directly because strategy-frame adjustments did not change threshold fields."
        effective_policy_source = "monitor_received_policy"
        effective_policy_source_chain = [
            str(received_policy_source or "monitor_received_policy"),
            "monitor_effective_policy",
        ]
    return {
        "received_policy": dict(received_policy),
        "effective_policy": dict(effective_policy),
        "received_policy_source": str(received_policy_source or ""),
        "effective_policy_source": effective_policy_source,
        "effective_policy_source_chain": [str(x) for x in effective_policy_source_chain if str(x or "").strip()],
        "policy_adjustments": {
            "inputs": adjustment_inputs,
            "applied_rules": applied_rules,
            "changed_fields": changed_fields,
        },
        "policy_adjustment_summary": summary,
        "policy_adjustment_reasoning": reasoning,
        "effective_policy_deltas": deltas,
    }


def build_entry_effective_policy_trace(entry_applied_policy, entry_policy_origin, entry_received_policy, monitor_memory_bias_result, strategy_frame, *, facade):
    effective_policy_trace = facade._build_monitor_effective_policy_trace(
        received_policy=entry_received_policy,
        effective_policy=entry_applied_policy,
        frame=strategy_frame,
        received_policy_source=entry_policy_origin,
    )
    if bool(monitor_memory_bias_result.get("applied")):
        source_chain = list(effective_policy_trace.get("effective_policy_source_chain") or [])
        effective_policy_trace["effective_policy_source_chain"] = (
            [source_chain[0], "commander_memory_bias", *source_chain[1:]]
            if source_chain
            else ["commander_memory_bias", "monitor_effective_policy"]
        )
        effective_policy_trace["effective_policy_source"] = "monitor_memory_bias_adjusted"
        policy_adjustment_summary = str(effective_policy_trace.get("policy_adjustment_summary") or "").strip()
        effective_policy_trace["policy_adjustment_summary"] = (
            f"{policy_adjustment_summary} | memory_bias=commander"
            if policy_adjustment_summary
            else "commander memory bias adjusted entry policy"
        )
        policy_adjustment_reasoning = str(effective_policy_trace.get("policy_adjustment_reasoning") or "").strip()
        prefix = "Commander-approved memory bias adjusted the entry baseline before strategy-frame normalization."
        effective_policy_trace["policy_adjustment_reasoning"] = (
            f"{prefix} {policy_adjustment_reasoning}".strip()
        )
    return effective_policy_trace
