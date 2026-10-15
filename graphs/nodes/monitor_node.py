from __future__ import annotations

"""Canonical Monitor node for integrated runtime.

Role boundary:
- monitors selected stock / active position state
- emits entry/exit intents only
- never re-ranks symbol universe and never executes orders
"""

import os
import time
from functools import partial
from pathlib import Path
from typing import Any, Dict, List

from graphs.nodes.skill_contracts import (
    CONTRACT_VERSION as SKILL_CONTRACT_VERSION,
    extract_market_quotes,
    extract_minute_ohlcv_by_symbol,
    extract_order_status,
)
from libs.core.symbols import normalize_symbol
from libs.research.evidence_ledger import record_decision_bridge, record_raw_input
from libs.runtime.canonical_artifacts import write_monitor_artifact
from libs.runtime.decision_trace import append_decision_trace
from libs.runtime.decision_observability import (
    build_entry_blocker_surface,
    build_monitor_no_trade_surface,
    build_scanner_monitor_handoff_surface,
)
from libs.runtime.etf_deviation import extract_etf_deviation_signal
from libs.runtime.monitor_candidate_cascade import build_entry_candidate_cascade_plan
from libs.runtime.monitor_runner_up_quality import evaluate_runner_up_entry_quality
from libs.runtime.commander_memory_application_trace import build_monitor_commander_memory_application_trace
from libs.runtime.monitor_entry_blockers import evaluate_entry_guard
from libs.runtime.opening_rank1_controlled_probe import (
    evaluate_opening_rank1_controlled_probe,
    load_probe_submissions,
    load_rank_observations,
    record_probe_evaluation,
    record_rank1_observation,
    record_probe_submission,
    session_clock as _opening_probe_session_clock,
)
from libs.runtime.opening_rank1_probe_authority import resolve_opening_rank1_probe_authority
from libs.runtime.monitor_entry_quality import (
    classify_vwap_reclaim_pullback_candidate as _classify_vwap_reclaim_pullback_candidate,
    evaluate_entry_quality_gate as _evaluate_entry_quality_gate,
)
from libs.runtime.monitor_entry_cost_filter import (
    evaluate_entry_cost_filter as _evaluate_entry_cost_filter,
    resolve_entry_cost_filter_config as _resolve_entry_cost_filter_config,
)
from libs.runtime.monitor_directional_edge import (
    apply_horizon_directional_edge as _apply_horizon_directional_edge,
)
from libs.runtime.monitor_entry_controls import (
    features_pending_order_count as _features_pending_order_count,
    pending_buy_symbols_from_account_orders as _pending_buy_symbols_from_account_orders,
    pending_order_symbols_from_account_orders as _pending_order_symbols_from_account_orders,
    resolve_block_buy_when_open_position as _resolve_block_buy_when_open_position,
    resolve_entry_closeout_window_guard as _resolve_entry_closeout_window_guard,
    resolve_max_positions as _resolve_max_positions,
)
from libs.runtime.monitor_entry_policy_context import (
    build_monitor_effective_policy_trace as _build_monitor_effective_policy_trace,
    resolve_commander_entry_control_for_monitor as _resolve_commander_entry_control_for_monitor,
    resolve_entry_candidate_cascade_config as _resolve_entry_candidate_cascade_config,
    resolve_monitor_entry_scoring_config as _resolve_monitor_entry_scoring_config,
    resolve_monitor_memory_bias_payload as _resolve_monitor_memory_bias_payload,
)
from libs.runtime.monitor_entry_sizing import (
    build_sizing_risk_context as _build_sizing_risk_context,
    derive_position_sizing_stop_context as _derive_position_sizing_stop_context,
    position_by_symbol as _position_by_symbol,
    resolve_cash as _resolve_cash,
    resolve_position_sizing_config as _resolve_position_sizing_config,
)
from libs.runtime.monitor_entry_state import (
    build_monitor_entry_state_snapshot as _build_monitor_entry_state_snapshot,
    build_monitor_entry_transition_trace as _build_monitor_entry_transition_trace,
    load_previous_monitor_state as _load_previous_monitor_state,
    monitor_posture_for_cycle as _monitor_posture_for_cycle,
    save_current_monitor_state as _save_current_monitor_state,
)
from libs.runtime.quant.decision import build_entry_quant_decision, build_exit_quant_decision
from libs.runtime.quant.enforcement import build_entry_quant_enforcement
from libs.runtime.quant.factors import build_factor_snapshot_from_monitor_entry
from libs.runtime.quant.market_rail_translation import evaluate_market_rail_translation
from libs.runtime.quant.risk_off_defensive_policy import evaluate_risk_off_defensive_observe_policy
from libs.runtime.quant.shadow_candidates import save_quant_shadow_candidates_for_state
from libs.runtime.intraday_monitor_signals import (
    evaluate_intraday_entry_signal,
    resolve_intraday_entry_policy,
)
from libs.runtime.monitor_exit.hold_controls import (
    resolve_exit_confirm_ticks as _resolve_exit_confirm_ticks,
    resolve_min_hold_sec as _resolve_min_hold_sec,
    resolve_post_exit_cooldown_sec as _resolve_post_exit_cooldown_sec,
    resolve_sell_cooldown_sec as _resolve_sell_cooldown_sec,
    resolve_use_exit_policy as _resolve_use_exit_policy,
)
from libs.runtime.monitor_exit.observability import build_monitor_exit_payload
from libs.runtime.monitor_exit.overnight_carry import (
    evaluate_overnight_carry_decision,
    persist_eod_carry_decisions_for_open_positions,
    persist_overnight_decision,
)
from libs.runtime.monitor_exit.order_lifecycle import derive_order_lifecycle as _derive_order_lifecycle
from libs.runtime.monitor_exit.policy_config import resolve_exit_policy_config as _resolve_exit_policy_config
from libs.runtime.monitor_exit.post_exit_shadow import (
    active_post_exit_shadow_watches as _active_post_exit_shadow_watches,
    refresh_post_exit_shadow_watchlist_minute_rows as _refresh_post_exit_shadow_watchlist_minute_rows,
)
from libs.runtime.monitor_exit.position_tracking import (
    ensure_position_peak_price_map as _ensure_position_peak_price_map,
    position_hold_seconds as _position_hold_seconds,
)
from libs.runtime.monitor_exit.price_resolution import (
    resolve_price as _resolve_price,
    resolve_price_with_source as _resolve_price_with_source,
)
from libs.runtime.monitor_exit.preview import preview_exit_decision_for_symbol
from libs.runtime.monitor_exit.reasons import (
    friendly_exit_axis as _friendly_exit_axis,
    is_emergency_exit_reason as _is_emergency_exit_reason,
    is_hard_exit_reason as _is_hard_exit_reason,
    monitor_watch_axes as _monitor_watch_axes,
)
from libs.runtime.monitor_exit.selection import select_exit_symbol
from libs.runtime.monitor_exit.selected_snapshot import (
    monitor_selected_snapshot_for_symbol as _monitor_selected_snapshot_for_symbol,
)
from libs.runtime.monitor_memory_bias import (
    apply_monitor_memory_bias_to_exit_policy,
    apply_monitor_memory_bias_to_hold_controls,
    apply_monitor_memory_bias_to_entry_policy,
    summarize_monitor_memory_bias,
)
from libs.runtime.same_symbol_loss_reentry import evaluate_same_symbol_loss_reentry
from libs.runtime.monitor_minute_ohlcv import (
    _ensure_monitor_minute_ohlcv_for_symbol,
    _extract_monitor_minute_rows,
    _fresh_monitor_skill_runner,
    _is_trueish,
    _latest_row_ts,
    _minute_snapshot_age_minutes,
    _minute_snapshot_stale_reason,
    _monitor_skill_output_to_record,
    _recover_monitor_minute_rows_from_history,
    _recover_monitor_minute_rows_from_persisted_cache,
    _remember_monitor_minute_rows_in_persisted_cache,
    _resolve_monitor_skill_runner,
    _run_monitor_minute_skill,
)
from libs.runtime.monitor_policy import (
    MonitorEntryPolicy,
    build_monitor_entry_policy_contract,
)
from libs.runtime.monitor_strategy_frame import (
    build_monitor_policy_trace as _build_monitor_policy_trace,
    extract_monitor_strategy_frame as _extract_monitor_strategy_frame,
    position_strategy_frame_for_symbol as _position_strategy_frame_for_symbol,
    apply_exit_policy_strategy_frame as _apply_exit_policy_strategy_frame,
    apply_monitor_strategy_frame as _apply_monitor_strategy_frame,
    harmonize_exit_policy_with_monitor_guards as _harmonize_exit_policy_with_monitor_guards,
)
from libs.runtime.position_sizing import evaluate_position_size
from libs.runtime.strategy_horizon_feedback import build_exit_vs_strategy_intent
import sys as _r3_sys
from libs.runtime.monitor.entry_carry_guard import (
    _entry_forced_block_reason_for_open_carry_r3_impl,
    _memory_bias_observation_only_r3_impl,
)
from libs.runtime.monitor.entry_cycle_context import (
    entry_cycle_all_pos_map_monitor_policy,
    entry_cycle_buy_blocked_closeout_window_buy_blocked,
)
from libs.runtime.monitor.entry_cascade_projection import (
    entry_cascade_entry_candidate_cascade_entry_cascade_co,
    entry_cascade_buy_blocked_closeout_window_buy_blocked,
    entry_cascade_entry_cooldown_map_runner_entry,
    entry_cascade_buy_blocked_closeout_window_buy_blocked_2,
    entry_cascade_intent,
)
from libs.runtime.monitor.exit_frame_projection import (
    exit_frame_exit_bias_result_exit_info,
    exit_frame_confirm_ticks_effective_exit_policy_base,
    exit_frame_avg_price_decision,
)
from libs.runtime.monitor.exit_decision_projection import (
    exit_decision_confirm_count_confirm_key,
    exit_decision_exit_info_exit_vs_strategy_intent,
    exit_decision_intents,
)
from libs.runtime.monitor.cycle_output_projection import (
    cycle_output_value_state_monitor,
    cycle_output_monitor_entry_exit_reason_quant_entry_de,
)
from libs.runtime.monitor.cycle_output_projection_value_state_monitor import (
    cycle_output_value_state_monitor_output,
)
from libs.runtime.monitor.cycle_posture_projection import (
    cycle_posture_entry_applied_policy_entry_metrics,
    cycle_posture_threshold_snapshot,
    cycle_posture_value_te_monitor_state_transition,
    cycle_posture_buy_skipped_reason_entry_event_metrics,
)
from libs.runtime.monitor.cycle_detail_projection import (
    cycle_detail_entry_candidate_symbol_entry_cost_filter,
    cycle_detail_entry_decision_detail,
    cycle_detail_scoring_event_payload,
)
from libs.runtime.monitor.cycle_detail_projection_exit_decision_detail import (
    cycle_detail_exit_decision_detail,
    cycle_detail_blocked_rules_reason_chain,
    cycle_detail_value_state_monitor_evaluation,
    cycle_detail_value_ate_monitor_action_decision,
)
from libs.runtime.monitor.entry_context import (
    entry_context_buy_blocked_post_exit_cooldown_closeout,
)
from libs.runtime.monitor.entry_evidence import (
    entry_evidence_entry_features_entry_row_source,
)
from libs.runtime.monitor.entry_quality_projection import (
    entry_quality_qty_sizing_info,
    entry_quality_quant_entry_decision_quant_entry_enforce,
)
from libs.runtime.monitor.entry_guard_evidence import (
    entry_guard_market_rail_translation_market_regime_fo,
    entry_guard_base_entry_guard_blocked_base_entry_guar,
)
from libs.runtime.monitor.entry_candidate_policy import (
    resolve_entry_memory_bias_policy,
    build_entry_effective_policy_trace,
)
from libs.runtime.monitor.entry_candidate_annotation import (
    annotate_entry_policy_fields,
    annotate_entry_minute_metrics,
)
from libs.runtime.monitor.entry_candidate_guards import (
    apply_market_rail_translation_to_quant_decision,
    resolve_entry_intent_cooldown,
    apply_entry_guard_overrides,
)
from libs.runtime.monitor.entry_candidate_probe import (
    resolve_opening_probe_context,
)
from libs.runtime.monitor.entry_cascade_selection import (
    build_entry_cascade_plan_for_selection,
    resolve_entry_order_price,
    annotate_entry_intent_meta,
)
from libs.runtime.monitor_exit.exit_policy_bias import (
    apply_exit_policy_memory_bias,
)
from libs.runtime.monitor_exit.exit_cycle_guards import (
    load_exit_cycle_maps,
    resolve_exit_cooldown_and_lock,
    evaluate_exit_sell_guards,
    commit_exit_signal_lock,
    build_overnight_carry_decision_payload,
)
from libs.runtime.monitor.scanner_monitor_handoff_projection import (
    build_scanner_monitor_handoff_for_cycle,
)
from libs.runtime.monitor.entry_focus_output_projection import (
    build_entry_focus_monitor_output,
)
from libs.runtime.monitor.policy_output_projection import (
    build_policy_monitor_output,
)
from libs.runtime.monitor.cycle_event_payloads import (
    build_monitor_raw_input_snapshot,
    build_state_transition_event_payload,
    build_cycle_summary_event_payload,
    build_decision_bridge_raw_input,
)
from libs.runtime.monitor.cycle_log_trace_payloads import (
    build_monitor_summary_log_payload,
    build_entry_exit_decision_trace_payload,
)

_preview_exit_decision_for_symbol = partial(
    preview_exit_decision_for_symbol,
    selected_snapshot_resolver=_monitor_selected_snapshot_for_symbol,
)
_persist_overnight_decision = persist_overnight_decision
_evaluate_overnight_carry_decision = evaluate_overnight_carry_decision
_persist_eod_carry_decisions_for_open_positions = partial(
    persist_eod_carry_decisions_for_open_positions,
    preview_resolver=_preview_exit_decision_for_symbol,
    hold_seconds_resolver=_position_hold_seconds,
)
_select_exit_symbol = partial(
    select_exit_symbol,
    preview_resolver=_preview_exit_decision_for_symbol,
)


def _to_int(v: Any) -> int:
    try:
        return int(float(v))
    except Exception:
        return 0


def _memory_bias_observation_only(state: Dict[str, Any] | None = None) -> bool:
    return _memory_bias_observation_only_r3_impl(state, facade=_r3_sys.modules[__name__])


def _to_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return float(default)


def _optional_float(v: Any) -> float | None:
    if v in (None, ""):
        return None
    try:
        return float(v)
    except Exception:
        return None


def _clamp(x: float, lo: float, hi: float) -> float:
    return float(max(lo, min(hi, x)))


def _resolve_now_epoch(state: Dict[str, Any]) -> int:
    tick_ts = state.get("tick_ts")
    try:
        if tick_ts is not None:
            return int(float(tick_ts))
    except Exception:
        pass
    return int(time.time())


def _entry_forced_block_reason_for_open_carry(
    state: Dict[str, Any],
    all_pos_map: Dict[str, Any],
    *,
    now_epoch: int,
) -> str:
    return _entry_forced_block_reason_for_open_carry_r3_impl(state, all_pos_map,
        now_epoch=now_epoch, facade=_r3_sys.modules[__name__])


def _norm_symbol(v: Any) -> str:
    return normalize_symbol(v)


def _clear_symbol_confirm_keys(confirm_map: Dict[str, Any], symbol: str) -> None:
    prefix = f"{_norm_symbol(symbol)}:"
    for key in list(confirm_map.keys()):
        if str(key).startswith(prefix):
            confirm_map.pop(key, None)


def _make_event_logger(state: Dict[str, Any]) -> Any:
    injected = state.get("event_logger")
    if injected is not None and hasattr(injected, "log"):
        return injected
    from libs.core.event_logger import EventLogger, resolve_event_log_path

    return EventLogger(log_path=resolve_event_log_path())


def _emit_monitor_event(
    state: Dict[str, Any],
    *,
    name: str,
    payload: Dict[str, Any],
    level: str = "info",
    symbol: str = "",
) -> None:
    try:
        logger = _make_event_logger(state)
        from libs.core.event_logger import log_state_event

        log_state_event(
            logger,
            state,
            stage="monitor",
            event=name,
            event_name=f"monitor.{name}",
            payload=dict(payload or {}),
            level=level,
            agent="monitor",
            symbol=str(symbol or ""),
        )
    except Exception:
        return


def _log_monitor_summary(state: Dict[str, Any], payload: Dict[str, Any]) -> None:
    try:
        logger = _make_event_logger(state)
        run_id = str(state.get("run_id") or "monitor-node")
        logger.log(run_id=run_id, stage="monitor", event="summary", payload=dict(payload))
    except Exception:
        return


def _evaluate_monitor_entry_candidate(
    *,
    state: Dict[str, Any],
    selected: Dict[str, Any],
    plan: Dict[str, Any],
    policy: Dict[str, Any],
    monitor_policy: Dict[str, Any],
    strategy_monitor_policy: Dict[str, Any],
    strategy_frame: Dict[str, Any],
    commander_context: Dict[str, Any],
    entry_policy_contract: Dict[str, Any],
    entry_policy_input: Dict[str, Any],
    entry_policy_origin: str,
    all_pos_map: Dict[str, Any],
    open_position_count: int,
    block_buy_open_position: bool,
    post_exit_cooldown_sec: int,
    entry_cooldown_map: Dict[str, Any],
    now_epoch_for_entry: int,
    prefer_fresh_minute_runner: bool = False,
    allow_opening_rank1_controlled_probe: bool = False,
) -> Dict[str, Any]:
    buy_blocked_post_exit_cooldown, closeout_window_guard, held_symbols, last_trade_epoch, last_trade_side, last_trade_symbol, max_positions, pending_buy_symbols, position_sizing_policy, post_exit_cooldown_remaining_sec, post_exit_cooldown_scope, post_exit_cooldown_symbol_match, qty, selected_already_held, selected_features, selected_pending_buy, sizing_info, symbol, use_position_sizing = entry_context_buy_blocked_post_exit_cooldown_closeout(selected=selected, state=state, policy=policy, all_pos_map=all_pos_map, facade=_r3_sys.modules[__name__])
    if (
        open_position_count <= 0
        and post_exit_cooldown_sec > 0
        and last_trade_side == "SELL"
        and last_trade_epoch > 0
        and post_exit_cooldown_symbol_match
    ):
        elapsed = max(0, int(now_epoch_for_entry - last_trade_epoch))
        remaining = max(0, int(post_exit_cooldown_sec - elapsed))
        if remaining > 0:
            buy_blocked_post_exit_cooldown = True
            post_exit_cooldown_remaining_sec = remaining

    commander_entry_control, entry_policy, entry_policy_input, entry_received_policy, monitor_memory_bias, monitor_memory_bias_observation_only, monitor_memory_bias_observed_entry_result, monitor_memory_bias_result, monitor_memory_bias_summary = resolve_entry_memory_bias_policy(commander_context=commander_context, entry_policy_input=entry_policy_input, monitor_policy=monitor_policy, state=state, strategy_frame=strategy_frame, strategy_monitor_policy=strategy_monitor_policy, facade=_r3_sys.modules[__name__])
    state = _ensure_monitor_minute_ohlcv_for_symbol(
        state,
        symbol=symbol,
        timeframe_minutes=int(entry_policy.timeframe_minutes or 1),
        now_epoch=now_epoch_for_entry,
        prefer_fresh_runner=prefer_fresh_minute_runner,
    )
    entry_features, entry_row_source, entry_rows, entry_scoring_policy, minute_fetch_meta, minute_ohlcv_meta, quote_for_entry = entry_evidence_entry_features_entry_row_source(state=state, policy=policy, symbol=symbol, selected=selected, selected_features=selected_features, facade=_r3_sys.modules[__name__])
    selected["features"] = entry_features
    entry_info = evaluate_intraday_entry_signal(
        entry_rows,
        current_price=selected.get("price") if isinstance(selected, dict) else None,
        features=entry_features,
        policy=entry_policy,
        scoring=entry_scoring_policy,
        frame=strategy_frame,
        policy_contract=entry_policy_contract,
    )
    entry_info["closeout_window_guard"] = dict(closeout_window_guard)
    entry_info["minutes_to_close"] = closeout_window_guard.get("minutes_to_close")
    entry_info["eod_flat_cutoff_min"] = int(closeout_window_guard.get("cutoff_min") or 0)
    entry_info["buy_closeout_cutoff_min"] = int(closeout_window_guard.get("buy_cutoff_min") or 0)
    entry_info["closeout_window_active"] = bool(closeout_window_guard.get("active"))
    entry_info["symbol"] = symbol
    entry_info["selected_symbol"] = symbol
    entry_info["max_positions"] = int(max_positions)
    entry_info["multi_position_capacity_remaining"] = max(0, int(max_positions) - int(open_position_count))
    entry_info["held_symbols"] = sorted(held_symbols)
    entry_info["pending_buy_symbols"] = sorted(pending_buy_symbols)
    entry_info["selected_symbol_already_held"] = bool(selected_already_held)
    entry_info["selected_symbol_pending_buy"] = bool(selected_pending_buy)
    entry_info["post_exit_cooldown_scope"] = str(post_exit_cooldown_scope)
    entry_info["post_exit_cooldown_last_trade_symbol"] = str(last_trade_symbol)
    entry_info["post_exit_cooldown_symbol_match"] = bool(post_exit_cooldown_symbol_match)
    if commander_entry_control:
        entry_info["commander_entry_control"] = dict(commander_entry_control)
    entry_info["applied_policy"] = dict(entry_info.get("applied_policy") or entry_info.get("thresholds") or entry_policy.to_dict())
    entry_applied_policy = dict(entry_info.get("applied_policy") or {})
    effective_policy_trace = build_entry_effective_policy_trace(entry_applied_policy=entry_applied_policy, entry_policy_origin=entry_policy_origin, entry_received_policy=entry_received_policy, monitor_memory_bias_result=monitor_memory_bias_result, strategy_frame=strategy_frame, facade=_r3_sys.modules[__name__])
    annotate_entry_policy_fields(effective_policy_trace=effective_policy_trace, entry_info=entry_info, entry_policy_contract=entry_policy_contract, monitor_memory_bias=monitor_memory_bias, monitor_memory_bias_observation_only=monitor_memory_bias_observation_only, monitor_memory_bias_observed_entry_result=monitor_memory_bias_observed_entry_result, monitor_memory_bias_result=monitor_memory_bias_result, monitor_memory_bias_summary=monitor_memory_bias_summary, facade=_r3_sys.modules[__name__])
    annotate_entry_minute_metrics(entry_info=entry_info, entry_row_source=entry_row_source, entry_rows=entry_rows, minute_fetch_meta=minute_fetch_meta, minute_ohlcv_meta=minute_ohlcv_meta)
    if use_position_sizing:
        qty, sizing_info = entry_quality_qty_sizing_info(state=state, symbol=symbol, selected=selected, position_sizing_policy=position_sizing_policy, policy=policy, entry_info=entry_info, facade=_r3_sys.modules[__name__])
    entry_cost_filter_config = _resolve_entry_cost_filter_config(
        state=state,
        policy=policy,
        monitor_policy=monitor_policy,
        strategy_monitor_policy=strategy_monitor_policy,
        entry_policy_input=entry_policy_input,
        commander_entry_control=commander_entry_control,
    )
    _apply_horizon_directional_edge(
        state=state,
        selected=selected,
        entry_info=entry_info,
        strategy_frame=strategy_frame,
    )
    entry_cost_filter = _evaluate_entry_cost_filter(
        entry_info=entry_info,
        selected=selected,
        qty=int(qty),
        config=entry_cost_filter_config,
    )
    entry_info["entry_cost_filter"] = dict(entry_cost_filter)
    entry_info["cost_adjusted_edge_ok"] = bool(entry_cost_filter.get("cost_adjusted_edge_ok"))
    entry_info["cost_adjusted_edge_pct"] = entry_cost_filter.get("cost_adjusted_edge_pct")
    entry_info["cost_drag_pct"] = entry_cost_filter.get("cost_drag_pct")
    entry_quality_gate = _evaluate_entry_quality_gate(
        selected=selected,
        entry_info=entry_info,
        entry_cost_filter=entry_cost_filter,
    )
    entry_info["entry_quality_gate"] = dict(entry_quality_gate)
    entry_info["entry_lane"] = "strict"
    entry_info["scoring_mode"] = str(entry_info.get("scoring_mode") or "disabled")
    quant_entry_decision, quant_entry_enforcement, quant_entry_factor_snapshot, tactic_id_for_quant_entry = entry_quality_quant_entry_decision_quant_entry_enforce(plan=plan, strategy_frame=strategy_frame, entry_info=entry_info, selected=selected, state=state, facade=_r3_sys.modules[__name__])
    entry_info["quant_factor_snapshot"] = dict(quant_entry_factor_snapshot)
    entry_info["entry_quant_decision"] = dict(quant_entry_decision)
    entry_info["quant_entry_enforcement"] = dict(quant_entry_enforcement)
    market_rail_translation, market_regime_for_entry, market_regime_rail_for_entry = entry_guard_market_rail_translation_market_regime_fo(state=state, strategy_frame=strategy_frame, commander_context=commander_context, entry_info=entry_info, quant_entry_decision=quant_entry_decision, quant_entry_factor_snapshot=quant_entry_factor_snapshot, facade=_r3_sys.modules[__name__])
    entry_info["market_rail_translation"] = dict(market_rail_translation)
    apply_market_rail_translation_to_quant_decision(market_rail_translation=market_rail_translation, quant_entry_decision=quant_entry_decision)
    quant_entry_enforcement = build_entry_quant_enforcement(quant_entry_decision)
    entry_info["entry_quant_decision"] = dict(quant_entry_decision)
    entry_info["quant_entry_enforcement"] = dict(quant_entry_enforcement)
    risk_off_defensive_policy = evaluate_risk_off_defensive_observe_policy(
        tactic_id=tactic_id_for_quant_entry,
        market_regime=market_regime_for_entry,
        market_regime_rail=market_regime_rail_for_entry,
        entry_info=entry_info,
        commander_context=commander_context,
    )
    entry_info["risk_off_defensive_observe_policy"] = dict(risk_off_defensive_policy)
    entry_intent_cooldown_sec = max(0, _to_int((entry_info.get("thresholds") or {}).get("intent_cooldown_sec")))
    cooldown_until = resolve_entry_intent_cooldown(all_pos_map=all_pos_map, entry_cooldown_map=entry_cooldown_map, entry_info=entry_info, entry_intent_cooldown_sec=entry_intent_cooldown_sec, now_epoch_for_entry=now_epoch_for_entry, symbol=symbol, facade=_r3_sys.modules[__name__])

    max_positions_reached = bool(open_position_count >= max_positions)
    same_symbol_loss_reentry_control = evaluate_same_symbol_loss_reentry(
        state,
        symbol=symbol,
        now_epoch=int(now_epoch_for_entry),
    )
    entry_info["same_symbol_loss_reentry_control"] = dict(
        same_symbol_loss_reentry_control
    )
    base_entry_guard_blocked, base_entry_guard_reason, buy_blocked_closeout_window, buy_blocked_open_position, buy_blocked_pending_buy, buy_blocked_same_symbol, entry_guard_blocked, entry_guard_reason, entry_info, original_wait_reason = entry_guard_base_entry_guard_blocked_base_entry_guar(state=state, all_pos_map=all_pos_map, now_epoch_for_entry=now_epoch_for_entry, same_symbol_loss_reentry_control=same_symbol_loss_reentry_control, entry_info=entry_info, entry_quality_gate=entry_quality_gate, entry_cost_filter=entry_cost_filter, selected_already_held=selected_already_held, selected_pending_buy=selected_pending_buy, max_positions_reached=max_positions_reached, buy_blocked_post_exit_cooldown=buy_blocked_post_exit_cooldown, entry_intent_cooldown_sec=entry_intent_cooldown_sec, cooldown_until=cooldown_until, closeout_window_guard=closeout_window_guard, facade=_r3_sys.modules[__name__])
    entry_info["legacy_fallback_used"] = False
    entry_info["decision"] = "WAIT"
    entry_info["cascade_candidate"] = str(plan.get("cascade_candidate") or "")
    entry_guard_blocked, entry_guard_reason, qty = apply_entry_guard_overrides(entry_guard_blocked=entry_guard_blocked, entry_guard_reason=entry_guard_reason, entry_info=entry_info, market_rail_translation=market_rail_translation, qty=qty, quant_entry_enforcement=quant_entry_enforcement, risk_off_defensive_policy=risk_off_defensive_policy, sizing_info=sizing_info, facade=_r3_sys.modules[__name__])

    probe_day, _probe_minutes = _opening_probe_session_clock(now_epoch_for_entry)
    prior_probe_rows = load_probe_submissions(probe_day)
    prior_rank_observations = load_rank_observations(probe_day)
    observation_price, opening_probe_selection_authority, probe_selected, same_symbol_reentry_detected = resolve_opening_probe_context(_probe_minutes=_probe_minutes, allow_opening_rank1_controlled_probe=allow_opening_rank1_controlled_probe, entry_rows=entry_rows, last_trade_epoch=last_trade_epoch, last_trade_side=last_trade_side, last_trade_symbol=last_trade_symbol, now_epoch_for_entry=now_epoch_for_entry, probe_day=probe_day, quote_for_entry=quote_for_entry, selected=selected, state=state, symbol=symbol, facade=_r3_sys.modules[__name__])
    opening_rank1_controlled_probe = evaluate_opening_rank1_controlled_probe(
        selected=probe_selected,
        entry_info=entry_info,
        original_wait_reason=original_wait_reason,
        base_entry_guard_blocked=base_entry_guard_blocked,
        base_entry_guard_reason=base_entry_guard_reason,
        entry_quality_gate=entry_quality_gate,
        entry_cost_filter=entry_cost_filter,
        quant_entry_enforcement=quant_entry_enforcement,
        risk_off_policy=risk_off_defensive_policy,
        selection_authority=opening_probe_selection_authority,
        now_epoch=now_epoch_for_entry,
        normal_qty=qty,
        prior_probe_count=len(prior_probe_rows),
        is_top_pick=bool(allow_opening_rank1_controlled_probe),
        same_symbol_reentry_detected=same_symbol_reentry_detected,
        broker_mode=str(os.getenv("KIWOOM_MODE") or ""),
        prior_rank_observations=prior_rank_observations,
        recent_minute_rows=entry_rows,
        strategy_horizon=str(strategy_frame.get("strategy_horizon") or ""),
    )
    if (
        bool(allow_opening_rank1_controlled_probe)
        and int(opening_rank1_controlled_probe.get("scanner_rank") or 0) == 1
        and bool(opening_probe_selection_authority.get("evidence_available"))
        and bool(opening_probe_selection_authority.get("aligned"))
        and 0 <= _probe_minutes <= 20
    ):
        opening_rank1_controlled_probe["rank_observation"] = record_rank1_observation(
            day=probe_day,
            symbol=symbol,
            observed_epoch=now_epoch_for_entry,
            run_id=str(state.get("run_id") or ""),
            **observation_price,
        )
    if bool(opening_rank1_controlled_probe.get("applied")):
        reservation = record_probe_submission(
            opening_rank1_controlled_probe,
            run_id=str(state.get("run_id") or ""),
            recorded_at=str(state.get("ts") or now_epoch_for_entry),
        )
        opening_rank1_controlled_probe["reservation"] = dict(reservation)
        if bool(reservation.get("recorded")):
            qty = int(opening_rank1_controlled_probe.get("probe_qty") or 0)
            entry_guard_blocked = False
            entry_guard_reason = ""
            entry_info["triggered"] = True
            entry_info["guard_blocked"] = False
            entry_info["guard_reason"] = ""
            entry_info["reason"] = "opening_rank1_controlled_probe"
            entry_info["entry_lane"] = "opening_rank1_controlled_probe"
            sizing_info["qty"] = int(qty)
            sizing_info["opening_rank1_controlled_probe_applied"] = True
        else:
            opening_rank1_controlled_probe["applied"] = False
            opening_rank1_controlled_probe["reason"] = str(
                reservation.get("reason") or "probe_reservation_failed"
            )
    if bool(allow_opening_rank1_controlled_probe) and 0 <= _probe_minutes <= 20:
        opening_rank1_controlled_probe["evaluation_record"] = record_probe_evaluation(
            opening_rank1_controlled_probe,
            run_id=str(state.get("run_id") or ""),
            recorded_at=str(state.get("ts") or now_epoch_for_entry),
        )
    entry_info["opening_rank1_controlled_probe"] = dict(opening_rank1_controlled_probe)
    state["opening_rank1_controlled_probe"] = dict(opening_rank1_controlled_probe)

    if symbol and qty > 0 and not entry_guard_blocked and bool(entry_info.get("triggered")):
        entry_info["intent_submitted"] = True
        if entry_intent_cooldown_sec > 0:
            entry_cooldown_map[symbol] = int(now_epoch_for_entry + entry_intent_cooldown_sec)
            entry_info["intent_cooldown_until"] = int(now_epoch_for_entry + entry_intent_cooldown_sec)
        entry_info["decision"] = "BUY"
    else:
        entry_info["intent_submitted"] = False

    return {
        "state": state,
        "selected": selected,
        "symbol": symbol,
        "qty": int(qty),
        "sizing_info": sizing_info,
        "entry_info": entry_info,
        "entry_guard_blocked": bool(entry_guard_blocked),
        "entry_guard_reason": str(entry_guard_reason),
        "buy_blocked_open_position": bool(buy_blocked_open_position),
        "buy_blocked_same_symbol": bool(buy_blocked_same_symbol),
        "buy_blocked_pending_buy": bool(buy_blocked_pending_buy),
        "max_positions_reached": bool(max_positions_reached),
        "buy_blocked_post_exit_cooldown": bool(buy_blocked_post_exit_cooldown),
        "buy_blocked_closeout_window": bool(buy_blocked_closeout_window),
        "post_exit_cooldown_remaining_sec": int(post_exit_cooldown_remaining_sec),
        "entry_received_policy": entry_received_policy,
        "entry_applied_policy": entry_applied_policy,
        "effective_policy_trace": effective_policy_trace,
        "entry_cooldown_map": entry_cooldown_map,
        "entry_signal_detected": bool(entry_info.get("triggered")),
    }


def monitor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    all_pos_map, monitor_policy, plan, policy, run_id, selected, strategist_output, strategy_monitor_policy = entry_cycle_all_pos_map_monitor_policy(state=state, facade=_r3_sys.modules[__name__])
    _ensure_position_peak_price_map(state, all_pos_map)
    open_position_count = sum(1 for row in all_pos_map.values() if max(0, _to_int((row or {}).get("qty"))) > 0)
    max_positions = _resolve_max_positions(state, policy)
    held_symbols_for_entry = {
        _norm_symbol(sym)
        for sym, row in all_pos_map.items()
        if _norm_symbol(sym) and max(0, _to_int((row or {}).get("qty"))) > 0
    }
    pending_buy_symbols_for_entry = _pending_buy_symbols_from_account_orders(state)
    block_buy_open_position = _resolve_block_buy_when_open_position(state, policy, monitor_policy)
    post_exit_cooldown_sec = _resolve_post_exit_cooldown_sec(state, policy, monitor_policy)
    strategy_frame = _extract_monitor_strategy_frame(state)
    commander_context = (
        dict(strategy_frame.get("commander_context") or {})
        if isinstance(strategy_frame.get("commander_context"), dict)
        else {}
    )
    commander_entry_control = _resolve_commander_entry_control_for_monitor(
        commander_context=commander_context,
        strategy_monitor_policy=strategy_monitor_policy,
        state=state,
    )
    if commander_entry_control:
        commander_context["entry_control"] = dict(commander_entry_control)
        commander_context["commander_entry_control"] = dict(commander_entry_control)
        strategy_frame["commander_context"] = commander_context
    buy_blocked_closeout_window, buy_blocked_open_position, buy_blocked_pending_buy, buy_blocked_post_exit_cooldown, buy_blocked_same_symbol, entry_applied_policy, entry_guard_blocked, entry_guard_reason, entry_info, entry_policy_contract, entry_policy_input, entry_policy_origin, entry_received_policy, exit_bias_result, hold_bias_result, max_positions_reached, monitor_memory_bias, monitor_memory_bias_observation_only, monitor_memory_bias_summary, policy_provenance, post_exit_cooldown_remaining_sec, strategist_plan = entry_cycle_buy_blocked_closeout_window_buy_blocked(strategy_monitor_policy=strategy_monitor_policy, commander_context=commander_context, state=state, strategy_frame=strategy_frame, strategist_output=strategist_output, commander_entry_control=commander_entry_control, open_position_count=open_position_count, max_positions=max_positions, facade=_r3_sys.modules[__name__])
    entry_symbol = _norm_symbol(selected.get("symbol")) if isinstance(selected, dict) and selected.get("symbol") else ""
    entry_cooldown_map = state.get("_monitor_entry_cooldown_until")
    if not isinstance(entry_cooldown_map, dict):
        entry_cooldown_map = {}
    now_epoch_for_entry = _resolve_now_epoch(state)
    state = _refresh_post_exit_shadow_watchlist_minute_rows(
        state,
        now_epoch=now_epoch_for_entry,
    )
    try:
        record_raw_input(
            run_id=run_id,
            agent="monitor",
            stage="entry_exit_decision",
            raw_input=build_monitor_raw_input_snapshot(all_pos_map=all_pos_map, commander_context=commander_context, commander_entry_control=commander_entry_control, monitor_policy=monitor_policy, open_position_count=open_position_count, selected=selected, strategist_output=strategist_output, strategist_plan=strategist_plan, facade=_r3_sys.modules[__name__]),
            decision_link={"stage": "monitor_input_snapshot"},
        )
    except Exception:
        pass

    entry_candidate_cascade, entry_cascade_config, entry_cascade_max_runner_ups, intents, scanner_selected_snapshot, sizing_info = entry_cascade_entry_candidate_cascade_entry_cascade_co(selected=selected, commander_entry_control=commander_entry_control, open_position_count=open_position_count, max_positions=max_positions, held_symbols_for_entry=held_symbols_for_entry, pending_buy_symbols_for_entry=pending_buy_symbols_for_entry, facade=_r3_sys.modules[__name__])
    if isinstance(selected, dict) and selected.get("symbol"):
        buy_blocked_closeout_window, buy_blocked_open_position, buy_blocked_pending_buy, buy_blocked_post_exit_cooldown, buy_blocked_same_symbol, entry_applied_policy, entry_cooldown_map, entry_guard_blocked, entry_guard_reason, entry_info, entry_received_policy, max_positions_reached, post_exit_cooldown_remaining_sec, qty, selected, sizing_info, state, symbol = entry_cascade_buy_blocked_closeout_window_buy_blocked(state=state, plan=plan, policy=policy, monitor_policy=monitor_policy, strategy_monitor_policy=strategy_monitor_policy, strategy_frame=strategy_frame, commander_context=commander_context, entry_policy_contract=entry_policy_contract, entry_policy_input=entry_policy_input, entry_policy_origin=entry_policy_origin, all_pos_map=all_pos_map, open_position_count=open_position_count, block_buy_open_position=block_buy_open_position, post_exit_cooldown_sec=post_exit_cooldown_sec, entry_cooldown_map=entry_cooldown_map, now_epoch_for_entry=now_epoch_for_entry, selected=selected, sizing_info=sizing_info, entry_info=entry_info, entry_candidate_cascade=entry_candidate_cascade, facade=_r3_sys.modules[__name__])

        cascade_plan = build_entry_cascade_plan_for_selection(entry_candidate_cascade=entry_candidate_cascade, entry_cascade_config=entry_cascade_config, entry_cascade_max_runner_ups=entry_cascade_max_runner_ups, entry_guard_blocked=entry_guard_blocked, entry_guard_reason=entry_guard_reason, entry_info=entry_info, held_symbols_for_entry=held_symbols_for_entry, max_positions=max_positions, open_position_count=open_position_count, pending_buy_symbols_for_entry=pending_buy_symbols_for_entry, state=state, symbol=symbol, facade=_r3_sys.modules[__name__])
        fallback_trace = list(entry_candidate_cascade.get("fallback_trace") or [])
        if bool(cascade_plan.get("attempted")):
            for runner_row in list(cascade_plan.get("runner_rows") or []):
                if not isinstance(runner_row, dict):
                    continue
                runner_symbol = _norm_symbol(runner_row.get("symbol"))
                if not runner_symbol:
                    continue
                entry_cooldown_map, runner_entry, runner_metrics, runner_result, runner_scores, runner_selected, state = entry_cascade_entry_cooldown_map_runner_entry(state=state, runner_symbol=runner_symbol, runner_row=runner_row, plan=plan, policy=policy, monitor_policy=monitor_policy, strategy_monitor_policy=strategy_monitor_policy, strategy_frame=strategy_frame, commander_context=commander_context, entry_policy_contract=entry_policy_contract, entry_policy_input=entry_policy_input, entry_policy_origin=entry_policy_origin, all_pos_map=all_pos_map, open_position_count=open_position_count, block_buy_open_position=block_buy_open_position, post_exit_cooldown_sec=post_exit_cooldown_sec, entry_cooldown_map=entry_cooldown_map, now_epoch_for_entry=now_epoch_for_entry, fallback_trace=fallback_trace, facade=_r3_sys.modules[__name__])
                if not bool(runner_entry.get("intent_submitted")):
                    continue
                runner_quality = evaluate_runner_up_entry_quality(
                    runner_row=runner_row,
                    runner_entry=runner_entry,
                    runner_guard_blocked=bool(runner_result.get("entry_guard_blocked")),
                )
                if fallback_trace and isinstance(fallback_trace[-1], dict):
                    fallback_trace[-1]["runner_up_quality_gate"] = dict(runner_quality)
                if not bool(runner_quality.get("passed")):
                    runner_entry["intent_submitted"] = False
                    runner_entry["triggered"] = False
                    runner_entry["reason"] = str(runner_quality.get("reason") or "runner_up_quality_gate_failed")
                    runner_entry["runner_up_quality_gate"] = dict(runner_quality)
                    if fallback_trace and isinstance(fallback_trace[-1], dict):
                        fallback_trace[-1]["triggered"] = False
                        fallback_trace[-1]["reason"] = str(runner_entry.get("reason") or "")
                        fallback_trace[-1]["runner_up_quality_blocked"] = True
                    continue
                runner_rank = int(_to_int(runner_row.get("rank") or runner_row.get("priority_rank")))
                runner_subtype = _classify_vwap_reclaim_pullback_candidate(
                    candidate_row=dict(runner_row),
                    selected_rank=runner_rank,
                    fallback_used=True,
                    entry_info=runner_entry,
                )
                if fallback_trace and isinstance(fallback_trace[-1], dict):
                    fallback_trace[-1]["pullback_evidence_profile"] = dict(runner_subtype)
                if not bool(runner_subtype.get("fallback_qualified")):
                    runner_entry["intent_submitted"] = False
                    runner_entry["triggered"] = False
                    runner_entry["reason"] = str(
                        runner_subtype.get("fallback_rejection_reason")
                        or "weak_fallback_pullback"
                    )
                    runner_entry["pullback_evidence_profile"] = dict(runner_subtype)
                    runner_entry["weak_fallback_blocked"] = True
                    if fallback_trace and isinstance(fallback_trace[-1], dict):
                        fallback_trace[-1]["triggered"] = False
                        fallback_trace[-1]["reason"] = str(runner_entry.get("reason") or "")
                        fallback_trace[-1]["weak_fallback_blocked"] = True
                    continue
                buy_blocked_closeout_window, buy_blocked_open_position, buy_blocked_pending_buy, buy_blocked_post_exit_cooldown, buy_blocked_same_symbol, entry_applied_policy, entry_guard_blocked, entry_info, entry_received_policy, max_positions_reached, post_exit_cooldown_remaining_sec, qty, selected, sizing_info, symbol = entry_cascade_buy_blocked_closeout_window_buy_blocked_2(entry_candidate_cascade=entry_candidate_cascade, runner_symbol=runner_symbol, runner_row=runner_row, runner_subtype=runner_subtype, symbol=symbol, runner_selected=runner_selected, runner_result=runner_result, sizing_info=sizing_info, runner_entry=runner_entry, facade=_r3_sys.modules[__name__])
                entry_info["fallback_from_symbol"] = entry_candidate_cascade.get("fallback_from_symbol")
                entry_info["fallback_to_symbol"] = runner_symbol
                entry_info["pullback_evidence_profile"] = dict(runner_subtype)
                break
        entry_candidate_cascade["fallback_trace"] = fallback_trace
        entry_candidate_cascade["final_selected_symbol"] = symbol
        entry_candidate_cascade["final_selected_rank"] = (
            entry_candidate_cascade.get("fallback_to_rank")
            or selected.get("rank")
            or selected.get("priority_rank")
            or selected.get("scanner_rank")
        )

        if symbol and qty > 0 and not entry_guard_blocked and bool(entry_info.get("intent_submitted")):
            order_price, order_price_source = resolve_entry_order_price(entry_info=entry_info, selected=selected, sizing_info=sizing_info, facade=_r3_sys.modules[__name__])
            intent = entry_cascade_intent(symbol=symbol, qty=qty, order_price=order_price, order_price_source=order_price_source, entry_candidate_cascade=entry_candidate_cascade, selected=selected, entry_info=entry_info, plan=plan, facade=_r3_sys.modules[__name__])[0]
            annotate_entry_intent_meta(entry_info=entry_info, intent=intent, post_exit_cooldown_sec=post_exit_cooldown_sec, sizing_info=sizing_info)
            intents = [intent]
        else:
            intents = []
    if bool(intents) and open_position_count >= max_positions:
        intents = []
        buy_blocked_open_position = True
        entry_info["guard_blocked"] = True
        entry_info["guard_reason"] = "max_positions_reached"
        entry_info["max_positions_reached"] = True
        entry_info["decision"] = "WAIT"
    state["_monitor_entry_cooldown_until"] = entry_cooldown_map
    if isinstance(selected, dict) and selected.get("symbol"):
        state["selected"] = dict(selected)
    if isinstance(scanner_selected_snapshot, dict) and scanner_selected_snapshot:
        state["scanner_selected_snapshot"] = dict(scanner_selected_snapshot)
    state["monitor_entry_cascade"] = dict(entry_candidate_cascade)

    # Optional M29-2 exit policy (default disabled for backward compatibility).
    exit_bias_result, exit_info, exit_policy_base, hold_bias_result, selected_snapshot, selected_symbol, use_exit_policy = exit_frame_exit_bias_result_exit_info(state=state, policy=policy, selected=selected, facade=_r3_sys.modules[__name__])
    has_open_position_for_exit = any(
        max(0, _to_int((row or {}).get("qty"))) > 0
        for row in list(all_pos_map.values())
    )
    if use_exit_policy and (selected_symbol or has_open_position_for_exit):
        pos_map = all_pos_map
        preliminary_exit_symbol = _select_exit_symbol(
            selected_symbol,
            pos_map,
            state=state,
            selected=selected_snapshot,
            policy=policy,
            exit_policy_base=exit_policy_base,
        )
        exit_strategy_frame = _position_strategy_frame_for_symbol(
            state,
            preliminary_exit_symbol,
            strategy_frame,
        )
        min_hold_sec = _resolve_min_hold_sec(state, monitor_policy)
        sell_cooldown_sec = _resolve_sell_cooldown_sec(state, monitor_policy)
        confirm_ticks = _resolve_exit_confirm_ticks(state, monitor_policy)
        frame_applied = _apply_monitor_strategy_frame(
            min_hold_sec=min_hold_sec,
            sell_cooldown_sec=sell_cooldown_sec,
            confirm_ticks=confirm_ticks,
            frame=exit_strategy_frame,
        )
        min_hold_sec = int(frame_applied.get("min_hold_sec") or min_hold_sec)
        sell_cooldown_sec = int(frame_applied.get("sell_cooldown_sec") or sell_cooldown_sec)
        confirm_ticks = int(frame_applied.get("confirm_ticks") or confirm_ticks)
        hold_bias_result = apply_monitor_memory_bias_to_hold_controls(
            min_hold_sec=min_hold_sec,
            sell_cooldown_sec=sell_cooldown_sec,
            confirm_ticks=confirm_ticks,
            monitor_memory_bias=monitor_memory_bias,
        )
        confirm_ticks, effective_exit_policy_base, exit_policy_guard_adjustments, hold_bias_observed_result, hold_bias_result, min_hold_sec, sell_cooldown_sec = exit_frame_confirm_ticks_effective_exit_policy_base(hold_bias_result=hold_bias_result, monitor_memory_bias_observation_only=monitor_memory_bias_observation_only, min_hold_sec=min_hold_sec, sell_cooldown_sec=sell_cooldown_sec, confirm_ticks=confirm_ticks, exit_policy_base=exit_policy_base, facade=_r3_sys.modules[__name__])
        effective_exit_policy_base, exit_bias_observed_result, exit_bias_result = apply_exit_policy_memory_bias(effective_exit_policy_base=effective_exit_policy_base, exit_policy_guard_adjustments=exit_policy_guard_adjustments, frame_applied=frame_applied, hold_bias_result=hold_bias_result, monitor_memory_bias=monitor_memory_bias, monitor_memory_bias_observation_only=monitor_memory_bias_observation_only, pos_map=pos_map, selected_snapshot=selected_snapshot, selected_symbol=selected_symbol, state=state, facade=_r3_sys.modules[__name__])
        now_epoch = _resolve_now_epoch(state)
        eod_carry_sweep = _persist_eod_carry_decisions_for_open_positions(
            state=state,
            pos_map=pos_map,
            selected=selected_snapshot,
            exit_policy_base=effective_exit_policy_base,
            frame=frame_applied,
            now_epoch=now_epoch,
        )
        avg_price, decision, eod_carry, features, hold_sec, intents, price, qty, selected_pending_order_for_exit, symbol = exit_frame_avg_price_decision(selected_symbol=selected_symbol, pos_map=pos_map, state=state, selected_snapshot=selected_snapshot, policy=policy, effective_exit_policy_base=effective_exit_policy_base, preliminary_exit_symbol=preliminary_exit_symbol, exit_policy_guard_adjustments=exit_policy_guard_adjustments, intents=intents, frame_applied=frame_applied, facade=_r3_sys.modules[__name__])
        if bool(eod_carry.get("approved")):
            decision["triggered"] = False
            decision["reason"] = "carry_overnight_approved"
        if qty > 0 and bool(eod_carry.get("evaluated")):
            _persist_overnight_decision(
                state,
                symbol=symbol,
                decision=build_overnight_carry_decision_payload(eod_carry=eod_carry, now_epoch=now_epoch, symbol=symbol),
            )
        elif qty <= 0:
            _persist_overnight_decision(state, symbol=symbol, clear=True)
        confirm_map, cooldown_map, pending_exit_lock, prev_qty_map = load_exit_cycle_maps(state=state)

        cooldown_until, lock_until = resolve_exit_cooldown_and_lock(cooldown_map=cooldown_map, now_epoch=now_epoch, pending_exit_lock=pending_exit_lock, prev_qty_map=prev_qty_map, qty=qty, sell_cooldown_sec=sell_cooldown_sec, symbol=symbol, facade=_r3_sys.modules[__name__])

        confirm_count, confirm_key, decision_thresholds, effective_confirm_ticks, emergency_exit, eod_flat_exit, exit_signal_detected, hard_exit, hold_block_reason, min_hold_blocked, monitor_reason, peak_drawdown_confirm_ticks, sell_cooldown_blocked, sell_guard_blocked, sell_guard_reason = exit_decision_confirm_count_confirm_key(symbol=symbol, decision=decision, confirm_ticks=confirm_ticks, facade=_r3_sys.modules[__name__])

        confirm_count, hold_block_reason, min_hold_blocked, monitor_reason, sell_cooldown_blocked, sell_guard_blocked, sell_guard_reason = evaluate_exit_sell_guards(confirm_count=confirm_count, confirm_key=confirm_key, confirm_map=confirm_map, cooldown_until=cooldown_until, decision=decision, effective_confirm_ticks=effective_confirm_ticks, emergency_exit=emergency_exit, entry_info=entry_info, eod_carry=eod_carry, eod_flat_exit=eod_flat_exit, exit_signal_detected=exit_signal_detected, hard_exit=hard_exit, hold_block_reason=hold_block_reason, hold_sec=hold_sec, lock_until=lock_until, min_hold_blocked=min_hold_blocked, min_hold_sec=min_hold_sec, monitor_reason=monitor_reason, now_epoch=now_epoch, qty=qty, selected_pending_order_for_exit=selected_pending_order_for_exit, sell_cooldown_blocked=sell_cooldown_blocked, sell_cooldown_sec=sell_cooldown_sec, sell_guard_blocked=sell_guard_blocked, sell_guard_reason=sell_guard_reason, state=state, symbol=symbol, facade=_r3_sys.modules[__name__])

        confirm_count, cooldown_until, lock_until, monitor_reason = commit_exit_signal_lock(confirm_count=confirm_count, confirm_map=confirm_map, cooldown_map=cooldown_map, cooldown_until=cooldown_until, effective_confirm_ticks=effective_confirm_ticks, emergency_exit=emergency_exit, exit_signal_detected=exit_signal_detected, hard_exit=hard_exit, lock_until=lock_until, monitor_reason=monitor_reason, now_epoch=now_epoch, pending_exit_lock=pending_exit_lock, qty=qty, sell_cooldown_sec=sell_cooldown_sec, sell_guard_blocked=sell_guard_blocked, symbol=symbol, facade=_r3_sys.modules[__name__])

        state["_monitor_exit_confirm"] = confirm_map
        state["_monitor_sell_cooldown_until"] = cooldown_map
        state["_monitor_pending_exit_lock"] = pending_exit_lock
        state["_monitor_prev_position_qty"] = prev_qty_map

        exit_info, exit_vs_strategy_intent = exit_decision_exit_info_exit_vs_strategy_intent(decision=decision, features=features, entry_info=entry_info, frame_applied=frame_applied, eod_carry=eod_carry, eod_carry_sweep=eod_carry_sweep, effective_exit_policy_base=effective_exit_policy_base, decision_thresholds=decision_thresholds, symbol=symbol, selected_symbol=selected_symbol, qty=qty, price=price, avg_price=avg_price, hold_sec=hold_sec, exit_signal_detected=exit_signal_detected, sell_guard_blocked=sell_guard_blocked, sell_guard_reason=sell_guard_reason, min_hold_sec=min_hold_sec, sell_cooldown_sec=sell_cooldown_sec, effective_confirm_ticks=effective_confirm_ticks, confirm_count=confirm_count, peak_drawdown_confirm_ticks=peak_drawdown_confirm_ticks, min_hold_blocked=min_hold_blocked, sell_cooldown_blocked=sell_cooldown_blocked, hold_block_reason=hold_block_reason, cooldown_until=cooldown_until, lock_until=lock_until, now_epoch=now_epoch, monitor_reason=monitor_reason, emergency_exit=emergency_exit, hard_exit=hard_exit, exit_policy_guard_adjustments=exit_policy_guard_adjustments, monitor_memory_bias_observation_only=monitor_memory_bias_observation_only, hold_bias_result=hold_bias_result, hold_bias_observed_result=hold_bias_observed_result, exit_bias_result=exit_bias_result, exit_bias_observed_result=exit_bias_observed_result, state=state, facade=_r3_sys.modules[__name__])
        exit_info["exit_vs_strategy_intent"] = dict(exit_vs_strategy_intent)
        if bool(exit_signal_detected) and not bool(sell_guard_blocked) and qty > 0:
            exit_order_qty = max(1, min(int(qty), _to_int(decision.get("exit_qty") or qty)))
            exit_info["exit_qty"] = int(exit_order_qty)
            intents = exit_decision_intents(symbol=symbol, exit_order_qty=exit_order_qty, price=price, qty=qty, avg_price=avg_price, hold_sec=hold_sec, exit_signal_detected=exit_signal_detected, confirm_count=confirm_count, min_hold_blocked=min_hold_blocked, sell_cooldown_blocked=sell_cooldown_blocked, emergency_exit=emergency_exit, exit_policy_guard_adjustments=exit_policy_guard_adjustments, exit_vs_strategy_intent=exit_vs_strategy_intent, decision=decision, monitor_reason=monitor_reason, plan=plan, frame_applied=frame_applied, facade=_r3_sys.modules[__name__])[0]

    commander_memory_application_trace = build_monitor_commander_memory_application_trace(
        monitor_memory_bias=monitor_memory_bias,
        entry_result={
            "applied": bool(entry_info.get("monitor_memory_bias_applied")),
            "deltas": list(entry_info.get("monitor_memory_bias_deltas") or []),
        },
        hold_result=hold_bias_result,
        exit_result=exit_bias_result,
        monitor_memory_bias_summary=monitor_memory_bias_summary,
        effective_policy_source=str(entry_info.get("effective_policy_source") or ""),
        effective_policy_source_chain=list(entry_info.get("effective_policy_source_chain") or []),
    )
    entry_info["commander_memory_application_trace"] = dict(commander_memory_application_trace)
    entry_info["monitor_memory_application_trace"] = dict(commander_memory_application_trace)
    exit_info["commander_memory_application_trace"] = dict(commander_memory_application_trace)
    exit_info["monitor_memory_application_trace"] = dict(commander_memory_application_trace)

    order_status, order_status_meta = extract_order_status(state)
    order_lifecycle = _derive_order_lifecycle(order_status)
    fallback_reasons = list(order_status_meta.get("errors") or [])

    state["intents"] = intents
    state["monitor"] = cycle_output_value_state_monitor(order_status=order_status, fallback_reasons=fallback_reasons, order_lifecycle=order_lifecycle, intents=intents, open_position_count=open_position_count, max_positions=max_positions, block_buy_open_position=block_buy_open_position, buy_blocked_open_position=buy_blocked_open_position, buy_blocked_same_symbol=buy_blocked_same_symbol, buy_blocked_pending_buy=buy_blocked_pending_buy, max_positions_reached=max_positions_reached, buy_blocked_closeout_window=buy_blocked_closeout_window, post_exit_cooldown_sec=post_exit_cooldown_sec, buy_blocked_post_exit_cooldown=buy_blocked_post_exit_cooldown, post_exit_cooldown_remaining_sec=post_exit_cooldown_remaining_sec, entry_applied_policy=entry_applied_policy, commander_memory_application_trace=commander_memory_application_trace, entry_candidate_cascade=entry_candidate_cascade, selected=selected, exit_info=exit_info, entry_info=entry_info, entry_received_policy=entry_received_policy, entry_policy_origin=entry_policy_origin, entry_policy_contract=entry_policy_contract, order_status_meta=order_status_meta, sizing_info=sizing_info, state=state, facade=_r3_sys.modules[__name__])
    monitor_entry_exit_reason, quant_entry_decision, quant_entry_enforcement, quant_entry_factor_snapshot, quant_exit_decision = cycle_output_monitor_entry_exit_reason_quant_entry_de(buy_blocked_post_exit_cooldown=buy_blocked_post_exit_cooldown, buy_blocked_closeout_window=buy_blocked_closeout_window, exit_info=exit_info, buy_blocked_pending_buy=buy_blocked_pending_buy, buy_blocked_same_symbol=buy_blocked_same_symbol, max_positions_reached=max_positions_reached, buy_blocked_open_position=buy_blocked_open_position, entry_info=entry_info, strategist_output=strategist_output, strategist_plan=strategist_plan, selected=selected, state=state, facade=_r3_sys.modules[__name__])
    entry_info["quant_factor_snapshot"] = dict(quant_entry_factor_snapshot)
    entry_info["entry_quant_decision"] = dict(quant_entry_decision)
    entry_info["quant_entry_enforcement"] = dict(quant_entry_enforcement)
    exit_info["exit_quant_decision"] = dict(quant_exit_decision)
    state["monitor_output"] = cycle_output_value_state_monitor_output(monitor_entry_exit_reason=monitor_entry_exit_reason, intents=intents, entry_candidate_cascade=entry_candidate_cascade, quant_entry_factor_snapshot=quant_entry_factor_snapshot, quant_entry_decision=quant_entry_decision, quant_entry_enforcement=quant_entry_enforcement, quant_exit_decision=quant_exit_decision, selected=selected, entry_info=entry_info, exit_info=exit_info, facade=_r3_sys.modules[__name__])
    state["monitor_entry"] = dict(entry_info)
    state["monitor_exit"] = exit_info
    state["monitor_sizing"] = sizing_info
    monitor_symbol = str(exit_info.get("symbol") or (selected.get("symbol") if isinstance(selected, dict) else "") or "")
    current_posture = _monitor_posture_for_cycle(
        open_position_count=open_position_count,
        intents=intents,
        exit_info=exit_info,
        buy_blocked_open_position=buy_blocked_open_position,
        buy_blocked_post_exit_cooldown=buy_blocked_post_exit_cooldown,
    )
    current_reason = str(exit_info.get("monitor_reason") or exit_info.get("reason") or (state.get("monitor_output") or {}).get("entry_exit_reason") or "").strip()
    previous_monitor_state = _load_previous_monitor_state(state, monitor_symbol) if monitor_symbol else {}
    previous_posture = str(previous_monitor_state.get("posture") or "").strip()
    previous_reason = str(previous_monitor_state.get("reason") or "").strip()
    entry_transition_trace = _build_monitor_entry_transition_trace(previous_monitor_state, entry_info)
    entry_info.update(dict(entry_transition_trace))
    entry_info["entry_transition_trace"] = dict(entry_transition_trace)
    state_changed = bool(previous_posture != current_posture or previous_reason != current_reason)
    if monitor_symbol:
        _save_current_monitor_state(
            state,
            monitor_symbol,
            posture=current_posture,
            reason=current_reason,
            active_exit_axis=str(exit_info.get("active_exit_axis") or ""),
            entry_state=_build_monitor_entry_state_snapshot(entry_info),
        )
    if isinstance(state.get("monitor"), dict):
        state["monitor"]["entry_transition_trace"] = dict(entry_transition_trace)
        state["monitor"]["entry_became_ready_this_cycle"] = bool(entry_transition_trace.get("became_ready_this_cycle"))
        state["monitor"]["entry_last_blocking_axis"] = str(entry_transition_trace.get("last_blocking_axis") or "")
        state["monitor"]["entry_transition_readiness_score"] = entry_transition_trace.get("transition_readiness_score")
    if isinstance(state.get("monitor_output"), dict):
        state["monitor_output"]["entry_transition_trace"] = dict(entry_transition_trace)
        state["monitor_output"]["entry_became_ready_this_cycle"] = bool(entry_transition_trace.get("became_ready_this_cycle"))
        state["monitor_output"]["entry_last_blocking_axis"] = str(entry_transition_trace.get("last_blocking_axis") or "")
        state["monitor_output"]["entry_transition_readiness_score"] = entry_transition_trace.get("transition_readiness_score")

    entry_applied_policy, entry_metrics, entry_thresholds, monitor_policy_trace, policy_ref, thresholds = cycle_posture_entry_applied_policy_entry_metrics(exit_info=exit_info, entry_info=entry_info, entry_applied_policy=entry_applied_policy, commander_context=commander_context, strategy_monitor_policy=strategy_monitor_policy, strategist_plan=strategist_plan, policy_provenance=policy_provenance, current_reason=current_reason, entry_received_policy=entry_received_policy, entry_policy_origin=entry_policy_origin, commander_memory_application_trace=commander_memory_application_trace, facade=_r3_sys.modules[__name__])
    monitor_policy_trace["policy_ref"] = policy_ref
    threshold_snapshot = cycle_posture_threshold_snapshot(exit_info=exit_info, entry_applied_policy=entry_applied_policy, thresholds=thresholds, entry_metrics=entry_metrics, entry_received_policy=entry_received_policy, entry_policy_origin=entry_policy_origin, entry_policy_contract=entry_policy_contract, entry_thresholds=entry_thresholds, entry_info=entry_info, facade=_r3_sys.modules[__name__])[0]
    state["monitor_posture"] = current_posture
    state["monitor_threshold_snapshot"] = dict(threshold_snapshot)
    if isinstance(state.get("monitor"), dict):
        state["monitor"]["threshold_snapshot"] = dict(threshold_snapshot)
        state["monitor"]["exit_stop_loss_pct"] = threshold_snapshot.get("stop_loss_pct")
        state["monitor"]["exit_effective_stop_loss_pct"] = threshold_snapshot.get("effective_stop_loss_pct")
        state["monitor"]["position_entry_risk_applied"] = bool(exit_info.get("position_entry_risk_applied"))
        state["monitor"]["position_entry_stop_loss_pct"] = exit_info.get("position_entry_stop_loss_pct")
        state["monitor"]["position_entry_stop_loss_source"] = str(exit_info.get("position_entry_stop_loss_source") or "")
        state["monitor"]["position_entry_invalidation_price"] = exit_info.get("position_entry_invalidation_price")
        state["monitor"]["position_entry_raw_structure_stop_loss_pct"] = exit_info.get(
            "position_entry_raw_structure_stop_loss_pct"
        )
        state["monitor"]["position_entry_min_structure_stop_loss_pct"] = exit_info.get(
            "position_entry_min_structure_stop_loss_pct"
        )
    state["monitor_state_transition"] = cycle_posture_value_te_monitor_state_transition(previous_posture=previous_posture, current_posture=current_posture, previous_reason=previous_reason, current_reason=current_reason, state_changed=state_changed, entry_transition_trace=entry_transition_trace, exit_info=exit_info, entry_info=entry_info, previous_monitor_state=previous_monitor_state, facade=_r3_sys.modules[__name__])
    _emit_monitor_event(
        state,
        name="threshold_snapshot",
        payload=threshold_snapshot,
        symbol=monitor_symbol,
    )
    _emit_monitor_event(
        state,
        name="state_transition",
        payload=build_state_transition_event_payload(current_posture=current_posture, current_reason=current_reason, entry_info=entry_info, entry_transition_trace=entry_transition_trace, exit_info=exit_info, previous_monitor_state=previous_monitor_state, previous_posture=previous_posture, previous_reason=previous_reason, state_changed=state_changed),
        symbol=monitor_symbol,
    )
    buy_submitted = any(str((intent or {}).get("side") or "").strip().upper() == "BUY" for intent in list(intents or []))
    buy_skipped_reason, entry_event_metrics, final_entry_decision, monitor_no_trade_surface = cycle_posture_buy_skipped_reason_entry_event_metrics(buy_submitted=buy_submitted, entry_info=entry_info, state=state, facade=_r3_sys.modules[__name__])
    scanner_monitor_handoff = build_scanner_monitor_handoff_for_cycle(entry_candidate_cascade=entry_candidate_cascade, entry_info=entry_info, final_entry_decision=final_entry_decision, monitor_no_trade_surface=monitor_no_trade_surface, scanner_selected_snapshot=scanner_selected_snapshot, selected=selected, state=state, facade=_r3_sys.modules[__name__])
    state["monitor_no_trade_surface"] = dict(monitor_no_trade_surface)
    state["scanner_monitor_handoff"] = dict(scanner_monitor_handoff)
    entry_blocker_surface = build_entry_blocker_surface(
        entry_info,
        final_decision=final_entry_decision,
        no_trade_surface=monitor_no_trade_surface,
        entry_blockers=list(monitor_policy_trace.get("entry_blockers") or []),
        buy_blocked_open_position=bool(buy_blocked_open_position),
        buy_blocked_closeout_window=bool(buy_blocked_closeout_window),
        buy_blocked_post_exit_cooldown=bool(buy_blocked_post_exit_cooldown),
        post_exit_cooldown_remaining_sec=post_exit_cooldown_remaining_sec,
        open_position_count=open_position_count,
        minutes_to_close=entry_info.get("minutes_to_close"),
        eod_flat_cutoff_min=entry_info.get("eod_flat_cutoff_min"),
    )
    state["monitor_entry_blocker_surface"] = dict(entry_blocker_surface)
    entry_candidate_symbol, entry_cost_filter_snapshot, entry_final_symbol, monitor_focus_context, monitor_focus_mode, monitor_output_symbol, position_focus_symbol, scanner_selected_symbol = cycle_detail_entry_candidate_symbol_entry_cost_filter(scanner_monitor_handoff=scanner_monitor_handoff, scanner_selected_snapshot=scanner_selected_snapshot, entry_info=entry_info, selected=selected, entry_candidate_cascade=entry_candidate_cascade, exit_info=exit_info, monitor_symbol=monitor_symbol, final_entry_decision=final_entry_decision, open_position_count=open_position_count, max_positions=max_positions, held_symbols_for_entry=held_symbols_for_entry, pending_buy_symbols_for_entry=pending_buy_symbols_for_entry, buy_submitted=buy_submitted, facade=_r3_sys.modules[__name__])
    state["monitor_focus_context"] = dict(monitor_focus_context)
    if isinstance(state.get("monitor"), dict):
        state["monitor"]["monitor_focus_context"] = dict(monitor_focus_context)
        state["monitor"]["entry_candidate_symbol"] = entry_candidate_symbol
        state["monitor"]["entry_final_symbol"] = entry_final_symbol
        state["monitor"]["position_focus_symbol"] = position_focus_symbol
        state["monitor"]["monitor_focus_mode"] = monitor_focus_mode
    if isinstance(state.get("monitor_output"), dict):
        state["monitor_output"].update(build_entry_focus_monitor_output(entry_blocker_surface=entry_blocker_surface, entry_candidate_symbol=entry_candidate_symbol, entry_cost_filter_snapshot=entry_cost_filter_snapshot, entry_final_symbol=entry_final_symbol, entry_info=entry_info, final_entry_decision=final_entry_decision, monitor_focus_context=monitor_focus_context, monitor_focus_mode=monitor_focus_mode, monitor_output_symbol=monitor_output_symbol, position_focus_symbol=position_focus_symbol, scanner_selected_symbol=scanner_selected_symbol))
    _emit_monitor_event(
        state,
        name="entry_blocker_surface",
        payload=entry_blocker_surface,
        level="info",
        symbol=monitor_symbol or entry_symbol,
    )
    entry_decision_detail = cycle_detail_entry_decision_detail(final_entry_decision=final_entry_decision, buy_skipped_reason=buy_skipped_reason, entry_event_metrics=entry_event_metrics, scanner_selected_symbol=scanner_selected_symbol, entry_candidate_symbol=entry_candidate_symbol, entry_final_symbol=entry_final_symbol, position_focus_symbol=position_focus_symbol, monitor_output_symbol=monitor_output_symbol, monitor_focus_mode=monitor_focus_mode, buy_submitted=buy_submitted, entry_applied_policy=entry_applied_policy, monitor_no_trade_surface=monitor_no_trade_surface, scanner_monitor_handoff=scanner_monitor_handoff, entry_candidate_cascade=entry_candidate_cascade, entry_blocker_surface=entry_blocker_surface, quant_entry_factor_snapshot=quant_entry_factor_snapshot, quant_entry_decision=quant_entry_decision, quant_entry_enforcement=quant_entry_enforcement, monitor_focus_context=monitor_focus_context, entry_policy_contract=entry_policy_contract, entry_info=entry_info, monitor_policy_trace=monitor_policy_trace, facade=_r3_sys.modules[__name__])[0]
    state["monitor_entry_decision_detail"] = dict(entry_decision_detail)
    _emit_monitor_event(
        state,
        name="entry_decision_detail",
        payload=entry_decision_detail,
        level="info",
        symbol=monitor_symbol or entry_symbol,
    )
    scoring_event_payload = cycle_detail_scoring_event_payload(final_entry_decision=final_entry_decision, monitor_no_trade_surface=monitor_no_trade_surface, scanner_monitor_handoff=scanner_monitor_handoff, entry_blocker_surface=entry_blocker_surface, monitor_symbol=monitor_symbol, entry_symbol=entry_symbol, entry_info=entry_info, state=state, facade=_r3_sys.modules[__name__])[0]
    if not bool(entry_info.get("hard_filter_passed")):
        _emit_monitor_event(
            state,
            name="hard_filter_failed",
            payload=dict(scoring_event_payload),
            level="info",
            symbol=monitor_symbol or entry_symbol,
        )
    _emit_monitor_event(
        state,
        name="score_computed",
        payload=dict(scoring_event_payload),
        level="info",
        symbol=monitor_symbol or entry_symbol,
    )
    _emit_monitor_event(
        state,
        name="entry_decision",
        payload=dict(scoring_event_payload),
        level="info",
        symbol=monitor_symbol or entry_symbol,
    )
    sell_submitted = any(str((intent or {}).get("side") or "").strip().upper() == "SELL" for intent in list(intents or []))
    exit_decision_detail = cycle_detail_exit_decision_detail(sell_submitted=sell_submitted, exit_info=exit_info, current_reason=current_reason, quant_exit_decision=quant_exit_decision, monitor_policy_trace=monitor_policy_trace, facade=_r3_sys.modules[__name__])[0]
    state["monitor_exit_decision_detail"] = dict(exit_decision_detail)
    _emit_monitor_event(
        state,
        name="exit_decision_detail",
        payload=exit_decision_detail,
        level="warning" if bool(exit_info.get("triggered")) else "info",
        symbol=monitor_symbol,
    )
    blocked_rules, reason_chain, triggered_rules = cycle_detail_blocked_rules_reason_chain(exit_info=exit_info, entry_info=entry_info, state=state, facade=_r3_sys.modules[__name__])
    if isinstance(state.get("monitor_output"), dict):
        state["monitor_output"].update(build_policy_monitor_output(commander_memory_application_trace=commander_memory_application_trace, entry_applied_policy=entry_applied_policy, entry_info=entry_info, entry_policy_contract=entry_policy_contract, entry_policy_origin=entry_policy_origin, entry_received_policy=entry_received_policy, exit_info=exit_info, monitor_no_trade_surface=monitor_no_trade_surface, monitor_policy_trace=monitor_policy_trace, scanner_monitor_handoff=scanner_monitor_handoff))
    state["monitor_evaluation"] = cycle_detail_value_state_monitor_evaluation(current_posture=current_posture, triggered_rules=triggered_rules, monitor_no_trade_surface=monitor_no_trade_surface, scanner_monitor_handoff=scanner_monitor_handoff, entry_info=entry_info, entry_received_policy=entry_received_policy, entry_policy_contract=entry_policy_contract, entry_applied_policy=entry_applied_policy, blocked_rules=blocked_rules, monitor_policy_trace=monitor_policy_trace, exit_info=exit_info, facade=_r3_sys.modules[__name__])
    state["monitor_action_decision"] = cycle_detail_value_ate_monitor_action_decision(reason_chain=reason_chain, triggered_rules=triggered_rules, entry_applied_policy=entry_applied_policy, monitor_no_trade_surface=monitor_no_trade_surface, scanner_monitor_handoff=scanner_monitor_handoff, current_reason=current_reason, entry_received_policy=entry_received_policy, entry_policy_contract=entry_policy_contract, entry_info=entry_info, blocked_rules=blocked_rules, monitor_policy_trace=monitor_policy_trace, exit_info=exit_info, state=state, facade=_r3_sys.modules[__name__])
    _emit_monitor_event(
        state,
        name="cycle_summary",
        payload=build_cycle_summary_event_payload(buy_blocked_closeout_window=buy_blocked_closeout_window, buy_blocked_open_position=buy_blocked_open_position, buy_blocked_post_exit_cooldown=buy_blocked_post_exit_cooldown, current_posture=current_posture, current_reason=current_reason, entry_blocker_surface=entry_blocker_surface, entry_info=entry_info, exit_info=exit_info, intents=intents, monitor_symbol=monitor_symbol, open_position_count=open_position_count, selected=selected, state=state),
        symbol=monitor_symbol,
    )
    _log_monitor_summary(
        state,
        build_monitor_summary_log_payload(block_buy_open_position=block_buy_open_position, buy_blocked_closeout_window=buy_blocked_closeout_window, buy_blocked_open_position=buy_blocked_open_position, buy_blocked_post_exit_cooldown=buy_blocked_post_exit_cooldown, entry_blocker_surface=entry_blocker_surface, entry_info=entry_info, exit_info=exit_info, fallback_reasons=fallback_reasons, final_entry_decision=final_entry_decision, intents=intents, monitor_no_trade_surface=monitor_no_trade_surface, open_position_count=open_position_count, post_exit_cooldown_remaining_sec=post_exit_cooldown_remaining_sec, post_exit_cooldown_sec=post_exit_cooldown_sec, scanner_monitor_handoff=scanner_monitor_handoff, selected=selected, sizing_info=sizing_info),
    )
    append_decision_trace(
        state,
        agent="monitor",
        event="entry_exit_decision",
        payload=build_entry_exit_decision_trace_payload(entry_applied_policy=entry_applied_policy, entry_info=entry_info, entry_policy_origin=entry_policy_origin, entry_received_policy=entry_received_policy, exit_info=exit_info, monitor_policy_trace=monitor_policy_trace, selected=selected, state=state),
    )
    try:
        record_decision_bridge(
            run_id=run_id,
            agent="monitor",
            stage="decision_bridge",
            raw_input=build_decision_bridge_raw_input(intents=intents, monitor_policy=monitor_policy, selected=selected, facade=_r3_sys.modules[__name__]),
            parsed_output={
                "entry_reason": str((state.get("monitor_output") or {}).get("entry_exit_reason") or ""),
                "exit_reason": str(exit_info.get("reason") or ""),
                "monitor_reason": str(exit_info.get("monitor_reason") or ""),
                "position_age_seconds": exit_info.get("position_age_seconds"),
                "peak_drawdown": exit_info.get("peak_drawdown"),
                "peak_price": exit_info.get("peak_price"),
                "vwap_distance": exit_info.get("vwap_distance"),
                "price_source": str(exit_info.get("price_source") or ""),
                "feature_source": str(exit_info.get("feature_source") or ""),
                "exit_signal_detected": bool(exit_info.get("exit_signal_detected")),
                "min_hold_blocked": bool(exit_info.get("min_hold_blocked")),
                "sell_cooldown_blocked": bool(exit_info.get("sell_cooldown_blocked")),
                "sell_guard_reason": str(exit_info.get("sell_guard_reason") or ""),
                "exit_policy_guard_adjustments": list(exit_info.get("exit_policy_guard_adjustments") or []),
                "post_exit_cooldown_sec": int(post_exit_cooldown_sec),
                "buy_blocked_closeout_window": bool(buy_blocked_closeout_window),
                "buy_blocked_post_exit_cooldown": bool(buy_blocked_post_exit_cooldown),
                "post_exit_cooldown_remaining_sec": int(post_exit_cooldown_remaining_sec),
                "minutes_to_close": entry_info.get("minutes_to_close"),
                "eod_flat_cutoff_min": int(entry_info.get("eod_flat_cutoff_min") or 0),
                "buy_closeout_cutoff_min": int(entry_info.get("buy_closeout_cutoff_min") or 0),
                "closeout_window_active": bool(entry_info.get("closeout_window_active")),
                "entry_evaluated": bool(entry_info.get("evaluated")),
                "entry_triggered": bool(entry_info.get("triggered")),
                "entry_pattern": str(entry_info.get("pattern") or ""),
                "entry_reason": str(entry_info.get("reason") or ""),
                "entry_signal_chain": list(entry_info.get("signal_chain") or []),
                "entry_condition_path": str(entry_info.get("entry_condition_path") or ""),
                "entry_condition_paths_passed": list(entry_info.get("entry_condition_paths_passed") or []),
                "entry_condition_scores": dict(entry_info.get("condition_scores") or {}),
                "entry_grouped_logic_trace": dict(entry_info.get("grouped_logic_trace") or {}),
                "entry_metrics": dict(entry_info.get("metrics") or {}),
                "entry_thresholds": dict(entry_info.get("thresholds") or {}),
                "entry_passed_checks": list(entry_info.get("passed_checks") or []),
                "entry_failed_checks": list(entry_info.get("failed_checks") or []),
                "entry_primary_failure_axis": str(entry_info.get("primary_failure_axis") or ""),
                "entry_threshold_margins": dict(entry_info.get("threshold_margins") or {}),
                "entry_transition_trace": dict(entry_info.get("entry_transition_trace") or {}),
                "entry_guard_blocked": bool(entry_info.get("guard_blocked")),
                "entry_guard_reason": str(entry_info.get("guard_reason") or ""),
            },
            decision_link={
                "decision_chain": {
                    "theme": str((state.get("themes") or [""])[0] if isinstance(state.get("themes"), list) and state.get("themes") else ""),
                    "scanner_selected": state.get("top_stock") or (
                        str(selected.get("symbol") or "") if isinstance(selected, dict) else ""
                    ),
                    "entry_reason": str((state.get("monitor_output") or {}).get("entry_exit_reason") or ""),
                    "exit_reason": str(exit_info.get("reason") or ""),
                }
            },
        )
    except Exception:
        pass
    try:
        shadow_result = save_quant_shadow_candidates_for_state(state, trigger="monitor_cycle")
        state["quant_shadow_candidates"] = dict(shadow_result)
        if isinstance(state.get("monitor_output"), dict):
            state["monitor_output"]["quant_shadow_candidates"] = dict(shadow_result)
    except Exception as exc:
        state["quant_shadow_candidates"] = {"status": "error", "error": str(exc)}
        if isinstance(state.get("monitor_output"), dict):
            state["monitor_output"]["quant_shadow_candidates"] = dict(state["quant_shadow_candidates"])
    try:
        write_monitor_artifact(state)
    except Exception:
        pass
    return state
