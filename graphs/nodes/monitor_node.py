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
    entry_cascade_intent_intents,
)
from libs.runtime.monitor.exit_frame_projection import (
    exit_frame_exit_bias_result_exit_info,
    exit_frame_confirm_ticks_effective_exit_policy_base,
    exit_frame_avg_price_decision,
)
from libs.runtime.monitor.exit_decision_projection import (
    exit_decision_confirm_count_confirm_map,
    exit_decision_exit_info_exit_vs_strategy_intent,
    exit_decision_intents,
    exit_decision_commander_memory_application_trace_fallb,
)
from libs.runtime.monitor.cycle_output_projection import (
    cycle_output_value_state_monitor,
    cycle_output_monitor_entry_exit_reason_quant_entry_de,
)
from libs.runtime.monitor.cycle_output_projection_value_state_monitor import (
    cycle_output_value_state_monitor_output,
)
from libs.runtime.monitor.cycle_posture_projection import (
    cycle_posture_entry_applied_policy_monitor_policy_trac,
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
    entry_evidence_effective_policy_trace_entry_applied_pol,
    entry_evidence_effect_free_block_500,
    entry_evidence_effect_free_block_518,
)
from libs.runtime.monitor.entry_quality_projection import (
    entry_quality_qty_sizing_info,
    entry_quality_entry_cost_filter_entry_quality_gate,
)
from libs.runtime.monitor.entry_guard_evidence import (
    entry_guard_base_entry_guard_blocked_base_entry_guar,
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

    monitor_memory_bias = _resolve_monitor_memory_bias_payload(
        strategy_monitor_policy=strategy_monitor_policy,
        commander_context=commander_context,
        state=state,
    )
    monitor_memory_bias_summary = summarize_monitor_memory_bias(monitor_memory_bias)
    entry_received_policy = MonitorEntryPolicy.from_mapping(entry_policy_input or monitor_policy).to_dict()
    commander_entry_control = (
        dict(commander_context.get("commander_entry_control") or commander_context.get("entry_control") or {})
        if isinstance(commander_context, dict)
        else {}
    )
    if commander_entry_control:
        entry_policy_input = dict(entry_policy_input or monitor_policy or {})
        entry_policy_input["commander_entry_control"] = dict(commander_entry_control)
        entry_policy_input["entry_control"] = dict(commander_entry_control)
    monitor_memory_bias_result = apply_monitor_memory_bias_to_entry_policy(
        entry_policy=entry_policy_input or monitor_policy,
        monitor_memory_bias=monitor_memory_bias,
    )
    monitor_memory_bias_observation_only = _memory_bias_observation_only(state)
    monitor_memory_bias_observed_entry_result = dict(monitor_memory_bias_result)
    if monitor_memory_bias_observation_only:
        monitor_memory_bias_result = {
            "policy": MonitorEntryPolicy.from_mapping(entry_policy_input or monitor_policy).to_dict(),
            "applied": False,
            "deltas": [],
            "observation_only": True,
            "observed_deltas": list(monitor_memory_bias_observed_entry_result.get("deltas") or []),
        }
    entry_policy_input = dict(monitor_memory_bias_result.get("policy") or {})
    if commander_entry_control:
        entry_policy_input["commander_entry_control"] = dict(commander_entry_control)
        entry_policy_input["entry_control"] = dict(commander_entry_control)
    entry_policy = resolve_intraday_entry_policy(entry_policy_input or monitor_policy, frame=strategy_frame)
    state = _ensure_monitor_minute_ohlcv_for_symbol(
        state,
        symbol=symbol,
        timeframe_minutes=int(entry_policy.timeframe_minutes or 1),
        now_epoch=now_epoch_for_entry,
        prefer_fresh_runner=prefer_fresh_minute_runner,
    )
    effective_policy_trace, entry_applied_policy, entry_info, entry_row_source, entry_rows, minute_fetch_meta, minute_ohlcv_meta, quote_for_entry = entry_evidence_effective_policy_trace_entry_applied_pol(state=state, policy=policy, symbol=symbol, selected=selected, selected_features=selected_features, entry_policy=entry_policy, strategy_frame=strategy_frame, entry_policy_contract=entry_policy_contract, closeout_window_guard=closeout_window_guard, max_positions=max_positions, open_position_count=open_position_count, held_symbols=held_symbols, pending_buy_symbols=pending_buy_symbols, selected_already_held=selected_already_held, selected_pending_buy=selected_pending_buy, post_exit_cooldown_scope=post_exit_cooldown_scope, last_trade_symbol=last_trade_symbol, post_exit_cooldown_symbol_match=post_exit_cooldown_symbol_match, commander_entry_control=commander_entry_control, entry_received_policy=entry_received_policy, entry_policy_origin=entry_policy_origin, facade=_r3_sys.modules[__name__])
    if bool(monitor_memory_bias_result.get("applied")):
        entry_evidence_effect_free_block_500(effective_policy_trace=effective_policy_trace, facade=_r3_sys.modules[__name__])
    entry_evidence_effect_free_block_518(entry_info=entry_info, effective_policy_trace=effective_policy_trace, entry_policy_contract=entry_policy_contract, monitor_memory_bias_result=monitor_memory_bias_result, monitor_memory_bias_observation_only=monitor_memory_bias_observation_only, monitor_memory_bias=monitor_memory_bias, monitor_memory_bias_summary=monitor_memory_bias_summary, monitor_memory_bias_observed_entry_result=monitor_memory_bias_observed_entry_result, entry_rows=entry_rows, entry_row_source=entry_row_source, minute_fetch_meta=minute_fetch_meta, minute_ohlcv_meta=minute_ohlcv_meta, facade=_r3_sys.modules[__name__])
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
    entry_cost_filter, entry_quality_gate, market_rail_translation, market_regime_for_entry, market_regime_rail_for_entry, quant_entry_decision, quant_entry_enforcement, tactic_id_for_quant_entry = entry_quality_entry_cost_filter_entry_quality_gate(entry_info=entry_info, selected=selected, entry_cost_filter_config=entry_cost_filter_config, qty=qty, plan=plan, strategy_frame=strategy_frame, state=state, commander_context=commander_context, facade=_r3_sys.modules[__name__])
    if isinstance(quant_entry_decision, dict):
        quant_entry_decision["market_rail_translation"] = dict(market_rail_translation)
        if bool(market_rail_translation.get("applied")):
            warnings = list(quant_entry_decision.get("warnings") or [])
            if "market_rail_translation_probe" not in warnings:
                warnings.append("market_rail_translation_probe")
            positives = list(quant_entry_decision.get("positive_reasons") or [])
            if "supportive_market_rail_probe_allowed" not in positives:
                positives.append("supportive_market_rail_probe_allowed")
            quant_entry_decision["warnings"] = warnings[:10]
            quant_entry_decision["positive_reasons"] = positives[:10]
            quant_entry_decision["decision"] = "entry_probe_allowed"
            quant_entry_decision["commander_override_required"] = False
            quant_entry_decision["override_reason_required_for"] = []
    base_entry_guard_blocked, base_entry_guard_reason, buy_blocked_closeout_window, buy_blocked_open_position, buy_blocked_pending_buy, buy_blocked_same_symbol, entry_guard_blocked, entry_guard_reason, entry_info, entry_intent_cooldown_sec, max_positions_reached, original_wait_reason, quant_entry_enforcement, risk_off_defensive_policy = entry_guard_base_entry_guard_blocked_base_entry_guar(quant_entry_decision=quant_entry_decision, entry_info=entry_info, tactic_id_for_quant_entry=tactic_id_for_quant_entry, market_regime_for_entry=market_regime_for_entry, market_regime_rail_for_entry=market_regime_rail_for_entry, commander_context=commander_context, symbol=symbol, entry_cooldown_map=entry_cooldown_map, now_epoch_for_entry=now_epoch_for_entry, all_pos_map=all_pos_map, open_position_count=open_position_count, max_positions=max_positions, state=state, entry_quality_gate=entry_quality_gate, entry_cost_filter=entry_cost_filter, selected_already_held=selected_already_held, selected_pending_buy=selected_pending_buy, buy_blocked_post_exit_cooldown=buy_blocked_post_exit_cooldown, closeout_window_guard=closeout_window_guard, plan=plan, facade=_r3_sys.modules[__name__])
    if bool(market_rail_translation.get("applied")):
        if (
            entry_guard_blocked
            and entry_guard_reason in {"cost_adjusted_edge_not_ready", "entry_quality_gate_blocked"}
        ):
            entry_guard_blocked = False
            entry_guard_reason = ""
            entry_info["guard_blocked"] = False
            entry_info["guard_reason"] = ""
            entry_info["market_rail_translation_unblocked_guard"] = True
        entry_info["triggered"] = True
        entry_info["market_rail_translation_probe"] = True
        probe_max_qty = max(1, _to_int(market_rail_translation.get("probe_max_qty") or 1))
        if qty > 0:
            qty = max(1, min(int(qty), int(probe_max_qty)))
            sizing_info["qty"] = int(qty)
            sizing_info["market_rail_translation_probe_max_qty"] = int(probe_max_qty)
            sizing_info["market_rail_translation_applied"] = True
    if (
        bool(quant_entry_enforcement.get("blocked"))
        and not entry_guard_blocked
        and bool(entry_info.get("triggered"))
    ):
        entry_guard_blocked = True
        entry_guard_reason = str(quant_entry_enforcement.get("reason") or "quant_entry_block")
        entry_info["guard_blocked"] = True
        entry_info["guard_reason"] = entry_guard_reason
        entry_info["reason"] = entry_guard_reason
    if bool(risk_off_defensive_policy.get("blocked")) and not entry_guard_blocked:
        entry_guard_blocked = True
        entry_guard_reason = str(risk_off_defensive_policy.get("reason") or "risk_off_defensive_observe_no_entry")
        failed_checks = list(entry_info.get("failed_checks") or [])
        if entry_guard_reason not in failed_checks:
            failed_checks.append(entry_guard_reason)
        entry_info["failed_checks"] = failed_checks
        entry_info["guard_blocked"] = True
        entry_info["guard_reason"] = entry_guard_reason
        entry_info["reason"] = entry_guard_reason
        entry_info["primary_failure_axis"] = "risk_off_defensive_observe_policy"

    probe_day, _probe_minutes = _opening_probe_session_clock(now_epoch_for_entry)
    prior_probe_rows = load_probe_submissions(probe_day)
    prior_rank_observations = load_rank_observations(probe_day)
    last_trade_day = (
        _opening_probe_session_clock(last_trade_epoch)[0]
        if last_trade_epoch > 0
        else ""
    )
    same_symbol_reentry_detected = bool(
        last_trade_side == "SELL"
        and last_trade_symbol == symbol
        and last_trade_day == probe_day
    )
    opening_probe_selection_authority = resolve_opening_rank1_probe_authority(
        state=state,
        selected=selected,
    )
    observation_price = {"observed_price": None, "price_source": "unavailable"}
    probe_selected = selected
    if bool(allow_opening_rank1_controlled_probe) and 0 <= _probe_minutes <= 20:
        from libs.runtime.opening_rank1_observation_price import resolve_observation_price

        observation_price = resolve_observation_price(
            selected=selected,
            quote=quote_for_entry,
            rows=entry_rows,
            now_epoch=now_epoch_for_entry,
        )
        observed_price = _to_float(observation_price.get("observed_price"))
        if observed_price > 0.0 and _to_float(selected.get("price")) <= 0.0:
            probe_selected = dict(selected)
            probe_selected["price"] = float(observed_price)
            probe_selected["_monitor_price_source"] = str(
                observation_price.get("price_source") or "opening_rank1_observation"
            )
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
    buy_blocked_closeout_window, buy_blocked_open_position, buy_blocked_pending_buy, buy_blocked_post_exit_cooldown, buy_blocked_same_symbol, commander_context, commander_entry_control, entry_applied_policy, entry_guard_blocked, entry_guard_reason, entry_info, entry_policy_contract, entry_policy_input, entry_policy_origin, max_positions_reached, monitor_memory_bias, monitor_memory_bias_observation_only, monitor_memory_bias_summary, policy_provenance, post_exit_cooldown_remaining_sec, strategist_plan, strategy_frame = entry_cycle_buy_blocked_closeout_window_buy_blocked(state=state, strategy_monitor_policy=strategy_monitor_policy, strategist_output=strategist_output, open_position_count=open_position_count, max_positions=max_positions, facade=_r3_sys.modules[__name__])
    entry_received_policy: Dict[str, Any] = {}
    effective_policy_trace: Dict[str, Any] = {}
    hold_bias_result: Dict[str, Any] = {"controls": {}, "applied": False, "deltas": []}
    exit_bias_result: Dict[str, Any] = {"policy": {}, "applied": False, "deltas": []}
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
            raw_input={
                "selected_symbol": (
                    str(selected.get("symbol") or "")
                    if isinstance(selected, dict)
                    else ""
                ),
                "selected_snapshot": (
                    {
                        "symbol": str(selected.get("symbol") or ""),
                        "score": selected.get("score"),
                        "risk_score": selected.get("risk_score"),
                        "confidence": selected.get("confidence"),
                        "price_source": str(selected.get("_monitor_price_source") or ""),
                        "feature_source": str(selected.get("_monitor_feature_source") or ""),
                    }
                    if isinstance(selected, dict)
                    else {}
                ),
                "open_position_count": int(open_position_count),
                "positions": {
                    str(k): {"qty": _to_int((v or {}).get("qty")), "avg_price": (v or {}).get("avg_price")}
                    for k, v in list(all_pos_map.items())[:20]
                },
                "monitor_policy": dict(monitor_policy),
                "strategist_guidance": {
                    "playbook": str(strategist_output.get("playbook") or ""),
                    "monitor_guidance": str(strategist_output.get("monitor_guidance") or ""),
                    "risk_tone": str(strategist_output.get("risk_tone") or ""),
                    "trade_aggressiveness": str(strategist_output.get("trade_aggressiveness") or ""),
                },
                "commander_context": {
                    "monitor_mission": str(commander_context.get("monitor_mission") or ""),
                    "flow_instruction": str(commander_context.get("flow_instruction") or ""),
                    "command_intent": str(commander_context.get("command_intent") or ""),
                    "risk_mode": str(commander_context.get("risk_mode") or ""),
                    "no_trade_reason_code": str(commander_context.get("no_trade_reason_code") or ""),
                    "llm_policy": str(commander_context.get("llm_policy") or ""),
                    "source_priority": list(commander_context.get("source_priority") or []),
                    "entry_control": dict(commander_entry_control),
                },
                "strategist_plan": {
                    "selected_playbook": str(strategist_plan.get("selected_playbook") or ""),
                    "entry_plan": dict(strategist_plan.get("entry_plan") or {}),
                    "exit_plan": dict(strategist_plan.get("exit_plan") or {}),
                    "symbol_constraints": dict(strategist_plan.get("symbol_constraints") or {}),
                    "strategy_summary": str(strategist_plan.get("strategy_summary") or ""),
                },
            },
            decision_link={"stage": "monitor_input_snapshot"},
        )
    except Exception:
        pass

    entry_candidate_cascade, entry_cascade_config, entry_cascade_max_runner_ups, intents, scanner_selected_snapshot, sizing_info = entry_cascade_entry_candidate_cascade_entry_cascade_co(selected=selected, commander_entry_control=commander_entry_control, open_position_count=open_position_count, max_positions=max_positions, held_symbols_for_entry=held_symbols_for_entry, pending_buy_symbols_for_entry=pending_buy_symbols_for_entry, facade=_r3_sys.modules[__name__])
    if isinstance(selected, dict) and selected.get("symbol"):
        buy_blocked_closeout_window, buy_blocked_open_position, buy_blocked_pending_buy, buy_blocked_post_exit_cooldown, buy_blocked_same_symbol, entry_applied_policy, entry_cooldown_map, entry_guard_blocked, entry_guard_reason, entry_info, entry_received_policy, max_positions_reached, post_exit_cooldown_remaining_sec, qty, selected, sizing_info, state, symbol = entry_cascade_buy_blocked_closeout_window_buy_blocked(state=state, plan=plan, policy=policy, monitor_policy=monitor_policy, strategy_monitor_policy=strategy_monitor_policy, strategy_frame=strategy_frame, commander_context=commander_context, entry_policy_contract=entry_policy_contract, entry_policy_input=entry_policy_input, entry_policy_origin=entry_policy_origin, all_pos_map=all_pos_map, open_position_count=open_position_count, block_buy_open_position=block_buy_open_position, post_exit_cooldown_sec=post_exit_cooldown_sec, entry_cooldown_map=entry_cooldown_map, now_epoch_for_entry=now_epoch_for_entry, selected=selected, sizing_info=sizing_info, entry_info=entry_info, entry_candidate_cascade=entry_candidate_cascade, facade=_r3_sys.modules[__name__])

        cascade_plan = build_entry_candidate_cascade_plan(
            selected_symbol=symbol,
            ranked_candidates=[row for row in list(state.get("ranked_candidates") or []) if isinstance(row, dict)],
            scanner_output=state.get("scanner_output") if isinstance(state.get("scanner_output"), dict) else {},
            open_position_count=open_position_count,
            max_positions=max_positions,
            entry_guard_blocked=entry_guard_blocked,
            entry_guard_reason=entry_guard_reason,
            entry_triggered=bool(entry_info.get("triggered")),
            entry_reason=str(entry_info.get("reason") or ""),
            max_runner_ups=int(entry_cascade_max_runner_ups),
            cascade_enabled=bool(entry_cascade_config.get("cascade_enabled", True)),
            cascade_allowed_reasons=list(entry_cascade_config.get("cascade_allowed_reasons") or []),
            cascade_blocked_reasons=list(entry_cascade_config.get("cascade_blocked_reasons") or []),
            hard_block_override_enabled=bool(entry_cascade_config.get("hard_block_override_enabled")),
            hard_block_override_reason=str(entry_cascade_config.get("hard_block_override_reason") or ""),
            excluded_symbols=sorted(held_symbols_for_entry | pending_buy_symbols_for_entry),
        )
        entry_candidate_cascade.update(dict(cascade_plan))
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
            entry_metrics_for_order = (
                dict(entry_info.get("metrics") or {})
                if isinstance(entry_info.get("metrics"), dict)
                else {}
            )
            entry_cost_filter_for_order = (
                dict(entry_info.get("entry_cost_filter") or {})
                if isinstance(entry_info.get("entry_cost_filter"), dict)
                else {}
            )
            order_price_source = ""
            order_price = 0.0
            for source_name, candidate in (
                ("entry_cost_filter.price", entry_cost_filter_for_order.get("price")),
                ("selected.price", selected.get("price")),
                ("entry.metrics.current_price", entry_metrics_for_order.get("current_price")),
                ("entry.metrics.price", entry_metrics_for_order.get("price")),
                ("sizing.price", sizing_info.get("price")),
            ):
                candidate_price = _to_float(candidate)
                if candidate_price > 0.0:
                    order_price = float(candidate_price)
                    order_price_source = source_name
                    break
            intent, intents = entry_cascade_intent_intents(symbol=symbol, qty=qty, order_price=order_price, order_price_source=order_price_source, entry_candidate_cascade=entry_candidate_cascade, selected=selected, entry_info=entry_info, plan=plan, sizing_info=sizing_info, post_exit_cooldown_sec=post_exit_cooldown_sec, facade=_r3_sys.modules[__name__])
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
        exit_policy_strategy = _apply_exit_policy_strategy_frame(
            state=state,
            exit_policy_base=effective_exit_policy_base,
            selected=selected_snapshot,
            position=pos_map.get(selected_symbol, {}) if selected_symbol else {},
            frame=frame_applied,
        )
        effective_exit_policy_base = dict(exit_policy_strategy.get("policy") or effective_exit_policy_base)
        effective_exit_policy_base["policy_source"] = str(
            effective_exit_policy_base.get("policy_source")
            or effective_exit_policy_base.get("effective_policy_source")
            or "monitor_effective_exit_policy"
        )
        effective_exit_policy_base["effective_policy_source"] = str(
            effective_exit_policy_base.get("effective_policy_source")
            or effective_exit_policy_base.get("policy_source")
            or "monitor_effective_exit_policy"
        )
        exit_policy_guard_adjustments.extend(list(exit_policy_strategy.get("adjustments") or []))
        exit_bias_result = apply_monitor_memory_bias_to_exit_policy(
            exit_policy=effective_exit_policy_base,
            monitor_memory_bias=monitor_memory_bias,
        )
        exit_bias_observed_result = dict(exit_bias_result)
        if monitor_memory_bias_observation_only:
            exit_bias_result = {
                "policy": dict(effective_exit_policy_base),
                "applied": False,
                "deltas": [],
                "observation_only": True,
                "observed_deltas": list(exit_bias_observed_result.get("deltas") or []),
            }
        effective_exit_policy_base = dict(exit_bias_result.get("policy") or effective_exit_policy_base)
        if bool(hold_bias_result.get("applied")):
            for row in list(hold_bias_result.get("deltas") or [])[:6]:
                exit_policy_guard_adjustments.append(
                    f"commander_memory_bias_hold:{str((row or {}).get('field') or '')}:{(row or {}).get('from')}->{(row or {}).get('to')}"
                )
        if bool(exit_bias_result.get("applied")):
            for row in list(exit_bias_result.get("deltas") or [])[:6]:
                exit_policy_guard_adjustments.append(
                    f"commander_memory_bias_exit:{str((row or {}).get('field') or '')}:{(row or {}).get('from')}->{(row or {}).get('to')}"
                )
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
        if qty > 0 and bool(eod_carry.get("evaluated")):
            _persist_overnight_decision(
                state,
                symbol=symbol,
                decision={
                    "approved": bool(eod_carry.get("approved")),
                    "action": str(eod_carry.get("action") or ""),
                    "reason": str(eod_carry.get("reason") or ""),
                    "minutes_to_close": eod_carry.get("minutes_to_close"),
                    "cutoff_min": eod_carry.get("cutoff_min"),
                    "positive_signals": list(eod_carry.get("positive_signals") or []),
                    "blockers": list(eod_carry.get("blockers") or []),
                    "carry_calendar": dict(eod_carry.get("carry_calendar") or {}),
                    "weekend_carry": bool(eod_carry.get("weekend_carry")),
                    "allow_weekend_carry": bool(eod_carry.get("allow_weekend_carry")),
                    "holding_gap_days": eod_carry.get("holding_gap_days"),
                    "decided_at_epoch": int(now_epoch),
                    "symbol": str(symbol or ""),
                },
            )
        elif qty <= 0:
            _persist_overnight_decision(state, symbol=symbol, clear=True)
        confirm_count, confirm_map, cooldown_map, cooldown_until, decision_thresholds, effective_confirm_ticks, emergency_exit, exit_signal_detected, hard_exit, hold_block_reason, lock_until, min_hold_blocked, monitor_reason, peak_drawdown_confirm_ticks, pending_exit_lock, prev_qty_map, sell_cooldown_blocked, sell_guard_blocked, sell_guard_reason = exit_decision_confirm_count_confirm_map(state=state, symbol=symbol, qty=qty, sell_cooldown_sec=sell_cooldown_sec, now_epoch=now_epoch, decision=decision, confirm_ticks=confirm_ticks, selected_pending_order_for_exit=selected_pending_order_for_exit, eod_carry=eod_carry, entry_info=entry_info, min_hold_sec=min_hold_sec, hold_sec=hold_sec, facade=_r3_sys.modules[__name__])

        if not sell_guard_blocked and exit_signal_detected:
            if not emergency_exit and not hard_exit and confirm_count <= 0:
                confirm_count = max(1, int(effective_confirm_ticks))
            _clear_symbol_confirm_keys(confirm_map, symbol)
            lock_sec = max(30, int(sell_cooldown_sec))
            pending_exit_lock[symbol] = int(now_epoch + lock_sec)
            lock_until = int(now_epoch + lock_sec)
            if sell_cooldown_sec > 0:
                cooldown_until = int(now_epoch + sell_cooldown_sec)
                cooldown_map[symbol] = int(cooldown_until)
            if emergency_exit:
                monitor_reason = "emergency_exit_signal"
            elif monitor_reason not in ("confirmed_exit_signal", "emergency_exit_signal"):
                monitor_reason = "confirmed_exit_signal"

        if qty <= 0:
            pending_exit_lock.pop(symbol, None)
            lock_until = 0

        state["_monitor_exit_confirm"] = confirm_map
        state["_monitor_sell_cooldown_until"] = cooldown_map
        state["_monitor_pending_exit_lock"] = pending_exit_lock
        state["_monitor_prev_position_qty"] = prev_qty_map

        exit_info, exit_vs_strategy_intent = exit_decision_exit_info_exit_vs_strategy_intent(decision=decision, features=features, entry_info=entry_info, frame_applied=frame_applied, eod_carry=eod_carry, eod_carry_sweep=eod_carry_sweep, effective_exit_policy_base=effective_exit_policy_base, decision_thresholds=decision_thresholds, symbol=symbol, selected_symbol=selected_symbol, qty=qty, price=price, avg_price=avg_price, hold_sec=hold_sec, exit_signal_detected=exit_signal_detected, sell_guard_blocked=sell_guard_blocked, sell_guard_reason=sell_guard_reason, min_hold_sec=min_hold_sec, sell_cooldown_sec=sell_cooldown_sec, effective_confirm_ticks=effective_confirm_ticks, confirm_count=confirm_count, peak_drawdown_confirm_ticks=peak_drawdown_confirm_ticks, min_hold_blocked=min_hold_blocked, sell_cooldown_blocked=sell_cooldown_blocked, hold_block_reason=hold_block_reason, cooldown_until=cooldown_until, lock_until=lock_until, now_epoch=now_epoch, monitor_reason=monitor_reason, emergency_exit=emergency_exit, hard_exit=hard_exit, exit_policy_guard_adjustments=exit_policy_guard_adjustments, monitor_memory_bias_observation_only=monitor_memory_bias_observation_only, hold_bias_result=hold_bias_result, hold_bias_observed_result=hold_bias_observed_result, exit_bias_result=exit_bias_result, exit_bias_observed_result=exit_bias_observed_result, state=state, facade=_r3_sys.modules[__name__])
        if bool(exit_signal_detected) and not bool(sell_guard_blocked) and qty > 0:
            intents = exit_decision_intents(qty=qty, decision=decision, exit_info=exit_info, symbol=symbol, price=price, avg_price=avg_price, hold_sec=hold_sec, exit_signal_detected=exit_signal_detected, confirm_count=confirm_count, min_hold_blocked=min_hold_blocked, sell_cooldown_blocked=sell_cooldown_blocked, emergency_exit=emergency_exit, exit_policy_guard_adjustments=exit_policy_guard_adjustments, exit_vs_strategy_intent=exit_vs_strategy_intent, monitor_reason=monitor_reason, plan=plan, frame_applied=frame_applied, facade=_r3_sys.modules[__name__])[0]

    commander_memory_application_trace, fallback_reasons, order_lifecycle, order_status, order_status_meta = exit_decision_commander_memory_application_trace_fallb(monitor_memory_bias=monitor_memory_bias, hold_bias_result=hold_bias_result, exit_bias_result=exit_bias_result, monitor_memory_bias_summary=monitor_memory_bias_summary, entry_info=entry_info, exit_info=exit_info, state=state, facade=_r3_sys.modules[__name__])

    state["intents"] = intents
    state["monitor"] = cycle_output_value_state_monitor(order_status=order_status, fallback_reasons=fallback_reasons, order_lifecycle=order_lifecycle, intents=intents, open_position_count=open_position_count, max_positions=max_positions, block_buy_open_position=block_buy_open_position, buy_blocked_open_position=buy_blocked_open_position, buy_blocked_same_symbol=buy_blocked_same_symbol, buy_blocked_pending_buy=buy_blocked_pending_buy, max_positions_reached=max_positions_reached, buy_blocked_closeout_window=buy_blocked_closeout_window, post_exit_cooldown_sec=post_exit_cooldown_sec, buy_blocked_post_exit_cooldown=buy_blocked_post_exit_cooldown, post_exit_cooldown_remaining_sec=post_exit_cooldown_remaining_sec, entry_applied_policy=entry_applied_policy, commander_memory_application_trace=commander_memory_application_trace, entry_candidate_cascade=entry_candidate_cascade, selected=selected, exit_info=exit_info, entry_info=entry_info, entry_received_policy=entry_received_policy, entry_policy_origin=entry_policy_origin, entry_policy_contract=entry_policy_contract, order_status_meta=order_status_meta, sizing_info=sizing_info, state=state, facade=_r3_sys.modules[__name__])
    monitor_entry_exit_reason, quant_entry_decision, quant_entry_enforcement, quant_entry_factor_snapshot, quant_exit_decision = cycle_output_monitor_entry_exit_reason_quant_entry_de(buy_blocked_post_exit_cooldown=buy_blocked_post_exit_cooldown, buy_blocked_closeout_window=buy_blocked_closeout_window, exit_info=exit_info, buy_blocked_pending_buy=buy_blocked_pending_buy, buy_blocked_same_symbol=buy_blocked_same_symbol, max_positions_reached=max_positions_reached, buy_blocked_open_position=buy_blocked_open_position, entry_info=entry_info, strategist_output=strategist_output, strategist_plan=strategist_plan, selected=selected, state=state, facade=_r3_sys.modules[__name__])
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

    entry_applied_policy, monitor_policy_trace, threshold_snapshot = cycle_posture_entry_applied_policy_monitor_policy_trac(exit_info=exit_info, entry_info=entry_info, entry_applied_policy=entry_applied_policy, commander_context=commander_context, strategy_monitor_policy=strategy_monitor_policy, strategist_plan=strategist_plan, policy_provenance=policy_provenance, current_reason=current_reason, entry_received_policy=entry_received_policy, entry_policy_origin=entry_policy_origin, commander_memory_application_trace=commander_memory_application_trace, entry_policy_contract=entry_policy_contract, facade=_r3_sys.modules[__name__])
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
        payload={
            "previous_posture": previous_posture,
            "current_posture": current_posture,
            "previous_reason": previous_reason,
            "current_reason": current_reason,
            "state_changed": bool(state_changed),
            "trigger_delta": {
                "previous_active_exit_axis": str(previous_monitor_state.get("active_exit_axis") or ""),
                "current_active_exit_axis": str(exit_info.get("active_exit_axis") or ""),
                "exit_triggered": bool(exit_info.get("triggered")),
                "entry_triggered": bool(entry_info.get("triggered")),
                "entry_pattern": str(entry_info.get("pattern") or ""),
                "became_ready_this_cycle": bool(entry_transition_trace.get("became_ready_this_cycle")),
                "last_blocking_axis": str(entry_transition_trace.get("last_blocking_axis") or ""),
                "transition_readiness_score": entry_transition_trace.get("transition_readiness_score"),
            },
        },
        symbol=monitor_symbol,
    )
    buy_submitted = any(str((intent or {}).get("side") or "").strip().upper() == "BUY" for intent in list(intents or []))
    buy_skipped_reason, entry_event_metrics, final_entry_decision, monitor_no_trade_surface = cycle_posture_buy_skipped_reason_entry_event_metrics(buy_submitted=buy_submitted, entry_info=entry_info, state=state, facade=_r3_sys.modules[__name__])
    scanner_monitor_handoff = build_scanner_monitor_handoff_surface(
        selected=scanner_selected_snapshot if isinstance(scanner_selected_snapshot, dict) else {},
        ranked_candidates=[row for row in list(state.get("ranked_candidates") or []) if isinstance(row, dict)],
        scanner_output=state.get("scanner_output") if isinstance(state.get("scanner_output"), dict) else {},
        final_decision=final_entry_decision,
        no_trade_surface=monitor_no_trade_surface,
        entry_info=entry_info,
    )
    scanner_monitor_handoff["monitor_selected_symbol"] = str((selected or {}).get("symbol") or "")
    scanner_monitor_handoff["entry_candidate_cascade"] = dict(entry_candidate_cascade)
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
        state["monitor_output"]["entry_blocker_surface"] = dict(entry_blocker_surface)
        state["monitor_output"]["monitor_focus_context"] = dict(monitor_focus_context)
        state["monitor_output"]["scanner_selected_symbol"] = scanner_selected_symbol
        state["monitor_output"]["entry_candidate_symbol"] = entry_candidate_symbol
        state["monitor_output"]["entry_final_symbol"] = entry_final_symbol
        state["monitor_output"]["position_focus_symbol"] = position_focus_symbol
        state["monitor_output"]["monitor_output_symbol"] = monitor_output_symbol
        state["monitor_output"]["monitor_focus_mode"] = monitor_focus_mode
        state["monitor_output"]["entry_candidate_decision"] = final_entry_decision
        state["monitor_output"]["entry_candidate_reason"] = str(
            entry_info.get("guard_reason") or entry_info.get("reason") or "entry_wait"
        )
        state["monitor_output"]["entry_candidate_primary_failure_axis"] = str(
            entry_info.get("primary_failure_axis") or ""
        )
        state["monitor_output"]["entry_candidate_cost_adjusted_edge_ok"] = bool(
            entry_info.get("cost_adjusted_edge_ok")
        )
        state["monitor_output"]["entry_candidate_cost_adjusted_edge_pct"] = entry_info.get("cost_adjusted_edge_pct")
        state["monitor_output"]["entry_candidate_cost_drag_pct"] = entry_info.get("cost_drag_pct")
        state["monitor_output"]["entry_candidate_cost_filter"] = dict(entry_cost_filter_snapshot)
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
        state["monitor_output"]["policy_ref"] = dict(monitor_policy_trace.get("policy_ref") or {})
        state["monitor_output"]["entry_check_summary"] = str(monitor_policy_trace.get("entry_check_summary") or "")
        state["monitor_output"]["entry_blockers"] = list(monitor_policy_trace.get("entry_blockers") or [])
        state["monitor_output"]["timing_assessment"] = dict(monitor_policy_trace.get("timing_assessment") or {})
        state["monitor_output"]["exit_trigger_basis"] = dict(monitor_policy_trace.get("exit_trigger_basis") or {})
        state["monitor_output"]["exit_vs_strategy_intent"] = dict(exit_info.get("exit_vs_strategy_intent") or {})
        state["monitor_output"]["final_exit_thresholds"] = dict(exit_info.get("final_exit_thresholds") or {})
        state["monitor_output"]["exit_threshold_source"] = str(exit_info.get("exit_threshold_source") or "")
        state["monitor_output"]["hold_block_reason"] = str(exit_info.get("hold_block_reason") or "")
        state["monitor_output"]["max_runup_pct"] = exit_info.get("max_runup_pct")
        state["monitor_output"]["peak_drawdown_from_peak"] = exit_info.get("peak_drawdown_from_peak")
        state["monitor_output"]["peak_drawdown_armed"] = bool(exit_info.get("peak_drawdown_armed"))
        state["monitor_output"]["peak_drawdown_mode"] = str(exit_info.get("peak_drawdown_mode") or "")
        state["monitor_output"]["peak_drawdown_blocked"] = bool(exit_info.get("peak_drawdown_blocked"))
        state["monitor_output"]["peak_drawdown_block_reason"] = str(exit_info.get("peak_drawdown_block_reason") or "")
        state["monitor_output"]["peak_drawdown_profit_floor_required_pct"] = exit_info.get(
            "peak_drawdown_profit_floor_required_pct"
        )
        state["monitor_output"]["peak_drawdown_profit_floor_met"] = bool(exit_info.get("peak_drawdown_profit_floor_met"))
        state["monitor_output"]["final_peak_drawdown_ratio"] = exit_info.get("final_peak_drawdown_ratio")
        state["monitor_output"]["peak_drawdown_source"] = str(exit_info.get("peak_drawdown_source") or "")
        state["monitor_output"]["exit_trigger_metric_name"] = str(exit_info.get("exit_trigger_metric_name") or "")
        state["monitor_output"]["exit_trigger_metric_value"] = exit_info.get("exit_trigger_metric_value")
        state["monitor_output"]["exit_trigger_metric_source"] = str(exit_info.get("exit_trigger_metric_source") or "")
        state["monitor_output"]["exit_gross_pnl_ratio"] = exit_info.get("gross_pnl_ratio")
        state["monitor_output"]["exit_technical_pnl_ratio"] = exit_info.get("technical_pnl_ratio")
        state["monitor_output"]["exit_stop_pnl_ratio"] = exit_info.get("stop_pnl_ratio")
        state["monitor_output"]["exit_stop_pnl_ratio_source"] = str(exit_info.get("stop_pnl_ratio_source") or "")
        state["monitor_output"]["exit_hard_stop_pnl_ratio"] = exit_info.get("hard_stop_pnl_ratio")
        state["monitor_output"]["exit_hard_stop_pnl_ratio_source"] = str(
            exit_info.get("hard_stop_pnl_ratio_source") or ""
        )
        state["monitor_output"]["exit_cost_drag_pressure"] = bool(exit_info.get("cost_drag_pressure"))
        state["monitor_output"]["exit_cost_drag_pressure_pct"] = exit_info.get("cost_drag_pressure_pct")
        state["monitor_output"]["exit_cost_drag_pressure_reason"] = str(exit_info.get("cost_drag_pressure_reason") or "")
        state["monitor_output"]["exit_stop_loss_cost_drag_blocked"] = bool(
            exit_info.get("stop_loss_cost_drag_blocked")
        )
        state["monitor_output"]["exit_stop_loss_cost_drag_blocked_reason"] = str(
            exit_info.get("stop_loss_cost_drag_blocked_reason") or ""
        )
        state["monitor_output"]["risk_reward_take_profit_target_pct"] = exit_info.get("risk_reward_take_profit_target_pct")
        state["monitor_output"]["risk_reward_take_profit_rung"] = exit_info.get("risk_reward_take_profit_rung")
        state["monitor_output"]["resistance_price"] = exit_info.get("resistance_price")
        state["monitor_output"]["resistance_price_source"] = str(exit_info.get("resistance_price_source") or "")
        state["monitor_output"]["resistance_distance_pct"] = exit_info.get("resistance_distance_pct")
        state["monitor_output"]["profit_time_stop_peak_giveback_pct"] = exit_info.get("profit_time_stop_peak_giveback_pct")
        state["monitor_output"]["partial_exit"] = bool(exit_info.get("partial_exit"))
        state["monitor_output"]["exit_qty"] = exit_info.get("exit_qty")
        state["monitor_output"]["exit_qty_fraction"] = exit_info.get("exit_qty_fraction")
        state["monitor_output"]["profit_ladder_level_pct"] = exit_info.get("profit_ladder_level_pct")
        state["monitor_output"]["profit_ladder_level_index"] = exit_info.get("profit_ladder_level_index")
        state["monitor_output"]["volume_ratio"] = exit_info.get("volume_ratio")
        state["monitor_output"]["execution_strength"] = exit_info.get("execution_strength")
        state["monitor_output"]["trade_strength"] = exit_info.get("trade_strength")
        state["monitor_output"]["opening_gap_chase_observed"] = bool(exit_info.get("opening_gap_chase_observed"))
        state["monitor_output"]["open_gap_pct"] = exit_info.get("open_gap_pct")
        state["monitor_output"]["prev_close_distance_pct"] = exit_info.get("prev_close_distance_pct")
        state["monitor_output"]["position_entry_risk_applied"] = bool(exit_info.get("position_entry_risk_applied"))
        state["monitor_output"]["position_entry_stop_loss_pct"] = exit_info.get("position_entry_stop_loss_pct")
        state["monitor_output"]["position_entry_stop_loss_source"] = str(exit_info.get("position_entry_stop_loss_source") or "")
        state["monitor_output"]["position_entry_invalidation_price"] = exit_info.get("position_entry_invalidation_price")
        state["monitor_output"]["position_entry_raw_structure_stop_loss_pct"] = exit_info.get(
            "position_entry_raw_structure_stop_loss_pct"
        )
        state["monitor_output"]["position_entry_min_structure_stop_loss_pct"] = exit_info.get(
            "position_entry_min_structure_stop_loss_pct"
        )
        state["monitor_output"]["received_policy"] = dict(entry_info.get("received_policy") or entry_received_policy or {})
        state["monitor_output"]["received_policy_source"] = str(entry_info.get("received_policy_source") or entry_policy_origin or "")
        state["monitor_output"]["policy_contract"] = dict(entry_info.get("policy_contract") or entry_policy_contract or {})
        state["monitor_output"]["effective_policy"] = dict(entry_info.get("effective_policy") or entry_applied_policy)
        state["monitor_output"]["effective_policy_source"] = str(entry_info.get("effective_policy_source") or "")
        state["monitor_output"]["effective_policy_source_chain"] = list(entry_info.get("effective_policy_source_chain") or [])
        state["monitor_output"]["policy_adjustments"] = dict(entry_info.get("policy_adjustments") or {})
        state["monitor_output"]["policy_adjustment_summary"] = str(entry_info.get("policy_adjustment_summary") or "")
        state["monitor_output"]["policy_adjustment_reasoning"] = str(entry_info.get("policy_adjustment_reasoning") or "")
        state["monitor_output"]["effective_policy_deltas"] = list(entry_info.get("effective_policy_deltas") or [])
        state["monitor_output"]["monitor_memory_bias_applied"] = bool(entry_info.get("monitor_memory_bias_applied"))
        state["monitor_output"]["monitor_memory_bias_observation_only"] = bool(entry_info.get("monitor_memory_bias_observation_only"))
        state["monitor_output"]["monitor_memory_bias"] = dict(entry_info.get("monitor_memory_bias") or {})
        state["monitor_output"]["monitor_memory_bias_summary"] = dict(entry_info.get("monitor_memory_bias_summary") or {})
        state["monitor_output"]["monitor_memory_bias_deltas"] = list(entry_info.get("monitor_memory_bias_deltas") or [])
        state["monitor_output"]["monitor_memory_bias_observed_deltas"] = list(entry_info.get("monitor_memory_bias_observed_deltas") or [])
        state["monitor_output"]["monitor_memory_bias_hold_applied"] = bool(exit_info.get("monitor_memory_bias_hold_applied"))
        state["monitor_output"]["monitor_memory_bias_hold_deltas"] = list(exit_info.get("monitor_memory_bias_hold_deltas") or [])
        state["monitor_output"]["monitor_memory_bias_exit_applied"] = bool(exit_info.get("monitor_memory_bias_exit_applied"))
        state["monitor_output"]["monitor_memory_bias_exit_deltas"] = list(exit_info.get("monitor_memory_bias_exit_deltas") or [])
        state["monitor_output"]["commander_memory_application_trace"] = dict(commander_memory_application_trace)
        state["monitor_output"]["monitor_memory_application_trace"] = dict(commander_memory_application_trace)
        state["monitor_output"]["applied_policy"] = dict(entry_applied_policy)
        state["monitor_output"]["policy_source"] = str((monitor_policy_trace.get("policy_ref") or {}).get("policy_source") or "")
        state["monitor_output"]["policy_validation_status"] = str((monitor_policy_trace.get("policy_ref") or {}).get("policy_validation_status") or "")
        state["monitor_output"]["policy_fallback_used"] = bool((monitor_policy_trace.get("policy_ref") or {}).get("policy_fallback_used"))
        state["monitor_output"]["policy_fallback_reason"] = str((monitor_policy_trace.get("policy_ref") or {}).get("policy_fallback_reason") or "")
        state["monitor_output"]["policy_partial_normalized"] = bool((monitor_policy_trace.get("policy_ref") or {}).get("policy_partial_normalized"))
        state["monitor_output"]["policy_default_filled_fields"] = list((monitor_policy_trace.get("policy_ref") or {}).get("policy_default_filled_fields") or [])
        state["monitor_output"]["policy_validation_missing_fields"] = list((monitor_policy_trace.get("policy_ref") or {}).get("policy_validation_missing_fields") or [])
        state["monitor_output"]["policy_validation_invalid_fields"] = list((monitor_policy_trace.get("policy_ref") or {}).get("policy_validation_invalid_fields") or [])
        state["monitor_output"]["override_reason"] = str((monitor_policy_trace.get("policy_ref") or {}).get("override_reason") or "")
        state["monitor_output"]["applied_policy_source_chain"] = list((monitor_policy_trace.get("policy_ref") or {}).get("applied_policy_source_chain") or [])
        state["monitor_output"]["commander_context_consumed"] = bool(monitor_policy_trace.get("commander_context_consumed"))
        state["monitor_output"]["consumed_fields"] = list(monitor_policy_trace.get("consumed_fields") or [])
        state["monitor_output"]["shadow_used"] = bool(monitor_policy_trace.get("shadow_used"))
        state["monitor_output"]["strategist_fallback_used"] = bool(monitor_policy_trace.get("strategist_fallback_used"))
        state["monitor_output"]["hard_filter_passed"] = bool(entry_info.get("hard_filter_passed"))
        state["monitor_output"]["hard_filter_fail_reasons"] = list(entry_info.get("hard_filter_fail_reasons") or [])
        state["monitor_output"]["total_score"] = entry_info.get("total_score")
        state["monitor_output"]["score_breakdown"] = dict(entry_info.get("score_breakdown") or {})
        state["monitor_output"]["policy_interpretation"] = dict(entry_info.get("policy_interpretation") or {})
        state["monitor_output"]["signal_evidence"] = dict(entry_info.get("signal_evidence") or {})
        state["monitor_output"]["chart_structure_features"] = dict(entry_info.get("chart_structure_features") or {})
        state["monitor_output"]["policy_interpreter_trace"] = dict(entry_info.get("policy_interpreter_trace") or {})
        state["monitor_output"]["policy_alignment_summary"] = dict(entry_info.get("policy_alignment_summary") or {})
        state["monitor_output"]["policy_aware_gating"] = dict(entry_info.get("policy_aware_gating") or {})
        state["monitor_output"]["chart_structure_decision_hint"] = dict(entry_info.get("chart_structure_decision_hint") or {})
        state["monitor_output"]["no_trade_surface"] = dict(monitor_no_trade_surface)
        state["monitor_output"]["scanner_monitor_handoff"] = dict(scanner_monitor_handoff)
        state["monitor_output"]["entry_threshold"] = entry_info.get("entry_threshold")
        state["monitor_output"]["score_passed"] = bool(entry_info.get("score_passed"))
        state["monitor_output"]["scoring_mode"] = str(entry_info.get("scoring_mode") or "disabled")
        state["monitor_output"]["legacy_entry_decision"] = str(entry_info.get("legacy_entry_decision") or "WAIT")
        state["monitor_output"]["scoring_entry_decision"] = str(entry_info.get("scoring_entry_decision") or "WAIT")
    state["monitor_evaluation"] = cycle_detail_value_state_monitor_evaluation(current_posture=current_posture, triggered_rules=triggered_rules, monitor_no_trade_surface=monitor_no_trade_surface, scanner_monitor_handoff=scanner_monitor_handoff, entry_info=entry_info, entry_received_policy=entry_received_policy, entry_policy_contract=entry_policy_contract, entry_applied_policy=entry_applied_policy, blocked_rules=blocked_rules, monitor_policy_trace=monitor_policy_trace, exit_info=exit_info, facade=_r3_sys.modules[__name__])
    state["monitor_action_decision"] = cycle_detail_value_ate_monitor_action_decision(reason_chain=reason_chain, triggered_rules=triggered_rules, entry_applied_policy=entry_applied_policy, monitor_no_trade_surface=monitor_no_trade_surface, scanner_monitor_handoff=scanner_monitor_handoff, current_reason=current_reason, entry_received_policy=entry_received_policy, entry_policy_contract=entry_policy_contract, entry_info=entry_info, blocked_rules=blocked_rules, monitor_policy_trace=monitor_policy_trace, exit_info=exit_info, state=state, facade=_r3_sys.modules[__name__])
    _emit_monitor_event(
        state,
        name="cycle_summary",
        payload={
            "selected_symbol": str((selected.get("symbol") if isinstance(selected, dict) else "") or ""),
            "monitor_symbol": monitor_symbol,
            "posture": current_posture,
            "monitor_reason": current_reason,
            "open_position_count": int(open_position_count),
            "has_intent": bool(intents),
            "intent_side": str((state.get("monitor_output") or {}).get("intent_side") or "NOOP"),
            "active_exit_axis": str(exit_info.get("active_exit_axis") or ""),
            "price_source": str(exit_info.get("price_source") or ""),
            "peak_update": (
                dict(state["peak_update_events"][-1])
                if isinstance(state.get("peak_update_events"), list)
                and state.get("peak_update_events")
                else {}
            ),
            "feature_source": str(exit_info.get("feature_source") or ""),
            "entry_evaluated": bool(entry_info.get("evaluated")),
            "entry_triggered": bool(entry_info.get("triggered")),
            "entry_pattern": str(entry_info.get("pattern") or ""),
            "buy_blocked_open_position": bool(buy_blocked_open_position),
            "buy_blocked_closeout_window": bool(buy_blocked_closeout_window),
            "buy_blocked_post_exit_cooldown": bool(buy_blocked_post_exit_cooldown),
            "minutes_to_close": entry_info.get("minutes_to_close"),
            "eod_flat_cutoff_min": int(entry_info.get("eod_flat_cutoff_min") or 0),
            "buy_closeout_cutoff_min": int(entry_info.get("buy_closeout_cutoff_min") or 0),
            "closeout_window_active": bool(entry_info.get("closeout_window_active")),
            "entry_blocker_surface": dict(entry_blocker_surface),
        },
        symbol=monitor_symbol,
    )
    _log_monitor_summary(
        state,
        {
            "has_intent": bool(intents),
            "intent_count": len(intents),
            "selected_symbol": (selected.get("symbol") if isinstance(selected, dict) else None),
            "order_status_fallback": bool(fallback_reasons),
            "exit_policy_enabled": bool(exit_info.get("enabled")),
            "exit_evaluated": bool(exit_info.get("evaluated")),
            "exit_triggered": bool(exit_info.get("triggered")),
            "exit_reason": str(exit_info.get("reason") or ""),
            "monitor_reason": str(exit_info.get("monitor_reason") or ""),
            "position_age_seconds": exit_info.get("position_age_seconds"),
            "peak_drawdown": exit_info.get("peak_drawdown"),
            "peak_price": exit_info.get("peak_price"),
            "vwap_distance": exit_info.get("vwap_distance"),
            "price_source": str(exit_info.get("price_source") or ""),
            "feature_source": str(exit_info.get("feature_source") or ""),
            "min_hold_sec": int(exit_info.get("min_hold_sec") or 0),
            "sell_cooldown_sec": int(exit_info.get("sell_cooldown_sec") or 0),
            "exit_confirm_ticks": int(exit_info.get("exit_confirm_ticks") or 0),
            "exit_confirm_count": int(exit_info.get("exit_confirm_count") or 0),
            "min_hold_blocked": bool(exit_info.get("min_hold_blocked")),
            "sell_cooldown_blocked": bool(exit_info.get("sell_cooldown_blocked")),
            "sell_guard_reason": str(exit_info.get("sell_guard_reason") or ""),
            "exit_policy_guard_adjustments": list(exit_info.get("exit_policy_guard_adjustments") or []),
            "exit_symbol_fallback": bool(exit_info.get("exit_symbol_fallback")),
            "exit_vs_strategy_intent": dict(exit_info.get("exit_vs_strategy_intent") or {}),
            "playbook": str(exit_info.get("playbook") or ""),
            "monitor_guidance": str(exit_info.get("monitor_guidance") or ""),
            "risk_tone": str(exit_info.get("risk_tone") or ""),
            "trade_aggressiveness": str(exit_info.get("trade_aggressiveness") or ""),
            "position_sizing_enabled": bool(sizing_info.get("enabled")),
            "position_sizing_evaluated": bool(sizing_info.get("evaluated")),
            "position_sizing_qty": int(sizing_info.get("qty") or 0),
            "position_sizing_reason": str(sizing_info.get("reason") or ""),
            "position_sizing_stop_loss_pct": (sizing_info.get("inputs") or {}).get("stop_loss_pct")
            if isinstance(sizing_info.get("inputs"), dict)
            else None,
            "position_sizing_stop_loss_source": str(
                ((sizing_info.get("inputs") or {}).get("stop_loss_source") if isinstance(sizing_info.get("inputs"), dict) else "")
                or ""
            ),
            "position_sizing_invalidation_price": (sizing_info.get("inputs") or {}).get("invalidation_price")
            if isinstance(sizing_info.get("inputs"), dict)
            else None,
            "open_position_count": int(open_position_count),
            "block_buy_when_open_position": bool(block_buy_open_position),
            "buy_blocked_open_position": bool(buy_blocked_open_position),
            "buy_blocked_closeout_window": bool(buy_blocked_closeout_window),
            "post_exit_cooldown_sec": int(post_exit_cooldown_sec),
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
            "entry_guard_blocked": bool(entry_info.get("guard_blocked")),
            "entry_guard_reason": str(entry_info.get("guard_reason") or ""),
            "entry_metrics": dict(entry_info.get("metrics") or {}),
            "entry_thresholds": dict(entry_info.get("thresholds") or {}),
            "entry_lane": str(entry_info.get("entry_lane") or "strict"),
            "entry_cost_filter": dict(entry_info.get("entry_cost_filter") or {}),
            "cost_adjusted_edge_ok": bool(entry_info.get("cost_adjusted_edge_ok")),
            "cost_adjusted_edge_pct": entry_info.get("cost_adjusted_edge_pct"),
            "cost_drag_pct": entry_info.get("cost_drag_pct"),
            "decision_outcome": str(monitor_no_trade_surface.get("decision_outcome") or final_entry_decision),
            "pre_intent_decision": str(monitor_no_trade_surface.get("pre_intent_decision") or ""),
            "no_trade_stage": str(monitor_no_trade_surface.get("no_trade_stage") or ""),
            "no_trade_reason_code": str(monitor_no_trade_surface.get("no_trade_reason_code") or ""),
            "no_trade_reason_summary": str(monitor_no_trade_surface.get("no_trade_reason_summary") or ""),
            "dominant_blocker": str(monitor_no_trade_surface.get("dominant_blocker") or ""),
            "blocker_family": str(monitor_no_trade_surface.get("blocker_family") or ""),
            "blocker_metrics": dict(monitor_no_trade_surface.get("blocker_metrics") or {}),
            "distance_to_ready": dict(monitor_no_trade_surface.get("distance_to_ready") or {}),
            "near_ready_flag": bool(monitor_no_trade_surface.get("near_ready_flag")),
            "required_checks_failed": list(monitor_no_trade_surface.get("required_checks_failed") or []),
            "preferred_checks_failed": list(monitor_no_trade_surface.get("preferred_checks_failed") or []),
            "relaxable_checks_failed": list(monitor_no_trade_surface.get("relaxable_checks_failed") or []),
            "evidence_snapshot": dict(monitor_no_trade_surface.get("evidence_snapshot") or {}),
            "scanner_monitor_handoff": dict(scanner_monitor_handoff),
            "entry_blocker_surface": dict(entry_blocker_surface),
        },
    )
    append_decision_trace(
        state,
        agent="monitor",
        event="entry_exit_decision",
        payload={
            "selected_symbol": str((selected.get("symbol") if isinstance(selected, dict) else "") or ""),
            "entry_reason": str((state.get("monitor_output") or {}).get("entry_exit_reason") or ""),
            "exit_reason": str(exit_info.get("reason") or ""),
            "thresholds": dict(exit_info.get("thresholds") or {}),
            "position_age_seconds": exit_info.get("position_age_seconds"),
            "peak_drawdown": exit_info.get("peak_drawdown"),
            "peak_price": exit_info.get("peak_price"),
            "vwap_distance": exit_info.get("vwap_distance"),
            "price_source": str(exit_info.get("price_source") or ""),
            "price_source_policy": str(exit_info.get("price_source_policy") or ""),
            "feature_source": str(exit_info.get("feature_source") or ""),
            "min_hold_sec": int(exit_info.get("min_hold_sec") or 0),
            "sell_cooldown_sec": int(exit_info.get("sell_cooldown_sec") or 0),
            "exit_confirm_ticks": int(exit_info.get("exit_confirm_ticks") or 0),
            "min_hold_blocked": bool(exit_info.get("min_hold_blocked")),
            "sell_cooldown_blocked": bool(exit_info.get("sell_cooldown_blocked")),
            "monitor_reason": str(exit_info.get("monitor_reason") or ""),
            "exit_symbol_fallback": bool(exit_info.get("exit_symbol_fallback")),
            "playbook": str(exit_info.get("playbook") or ""),
            "monitor_guidance": str(exit_info.get("monitor_guidance") or ""),
            "risk_tone": str(exit_info.get("risk_tone") or ""),
            "trade_aggressiveness": str(exit_info.get("trade_aggressiveness") or ""),
            "strategy_horizon": str(exit_info.get("strategy_horizon") or ""),
            "source_strategy_horizon": str(exit_info.get("source_strategy_horizon") or ""),
            "horizon_behavior_translation": dict(exit_info.get("horizon_behavior_translation") or {}),
            "position_strategy_context_applied": bool(exit_info.get("position_strategy_context_applied")),
            "position_strategy_context_symbol": str(exit_info.get("position_strategy_context_symbol") or ""),
            "position_strategy_context_source": str(exit_info.get("position_strategy_context_source") or ""),
            "strategy_frame_adjustments": list(exit_info.get("strategy_frame_adjustments") or []),
            "exit_policy_guard_adjustments": list(exit_info.get("exit_policy_guard_adjustments") or []),
            "entry_evaluated": bool(entry_info.get("evaluated")),
            "entry_triggered": bool(entry_info.get("triggered")),
            "entry_pattern": str(entry_info.get("pattern") or ""),
            "entry_signal_chain": list(entry_info.get("signal_chain") or []),
            "entry_condition_path": str(entry_info.get("entry_condition_path") or ""),
            "entry_condition_paths_passed": list(entry_info.get("entry_condition_paths_passed") or []),
            "entry_condition_scores": dict(entry_info.get("condition_scores") or {}),
            "entry_grouped_logic_trace": dict(entry_info.get("grouped_logic_trace") or {}),
            "entry_metrics": dict(entry_info.get("metrics") or {}),
            "entry_thresholds": dict(entry_info.get("thresholds") or {}),
            "received_policy": dict(entry_info.get("received_policy") or entry_received_policy or {}),
            "received_policy_source": str(entry_info.get("received_policy_source") or entry_policy_origin or ""),
            "effective_policy": dict(entry_info.get("effective_policy") or entry_applied_policy),
            "effective_policy_source": str(entry_info.get("effective_policy_source") or ""),
            "effective_policy_source_chain": list(entry_info.get("effective_policy_source_chain") or []),
            "policy_adjustments": dict(entry_info.get("policy_adjustments") or {}),
            "policy_adjustment_summary": str(entry_info.get("policy_adjustment_summary") or ""),
            "policy_adjustment_reasoning": str(entry_info.get("policy_adjustment_reasoning") or ""),
            "effective_policy_deltas": list(entry_info.get("effective_policy_deltas") or []),
            "applied_policy": dict(entry_applied_policy),
            "policy_source": str((monitor_policy_trace.get("policy_ref") or {}).get("policy_source") or ""),
            "policy_validation_status": str((monitor_policy_trace.get("policy_ref") or {}).get("policy_validation_status") or ""),
            "policy_fallback_used": bool((monitor_policy_trace.get("policy_ref") or {}).get("policy_fallback_used")),
            "policy_fallback_reason": str((monitor_policy_trace.get("policy_ref") or {}).get("policy_fallback_reason") or ""),
            "policy_partial_normalized": bool((monitor_policy_trace.get("policy_ref") or {}).get("policy_partial_normalized")),
            "policy_default_filled_fields": list((monitor_policy_trace.get("policy_ref") or {}).get("policy_default_filled_fields") or []),
            "policy_validation_missing_fields": list((monitor_policy_trace.get("policy_ref") or {}).get("policy_validation_missing_fields") or []),
            "policy_validation_invalid_fields": list((monitor_policy_trace.get("policy_ref") or {}).get("policy_validation_invalid_fields") or []),
            "override_reason": str((monitor_policy_trace.get("policy_ref") or {}).get("override_reason") or ""),
            "applied_policy_source_chain": list((monitor_policy_trace.get("policy_ref") or {}).get("applied_policy_source_chain") or []),
            "entry_passed_checks": list(entry_info.get("passed_checks") or []),
            "entry_failed_checks": list(entry_info.get("failed_checks") or []),
            "entry_primary_failure_axis": str(entry_info.get("primary_failure_axis") or ""),
            "entry_threshold_margins": dict(entry_info.get("threshold_margins") or {}),
            "entry_transition_trace": dict(entry_info.get("entry_transition_trace") or {}),
            "entry_guard_blocked": bool(entry_info.get("guard_blocked")),
            "entry_guard_reason": str(entry_info.get("guard_reason") or ""),
        },
    )
    try:
        record_decision_bridge(
            run_id=run_id,
            agent="monitor",
            stage="decision_bridge",
            raw_input={
                "selected_symbol": (
                    str(selected.get("symbol") or "")
                    if isinstance(selected, dict)
                    else ""
                ),
                "monitor_policy": dict(monitor_policy),
                "intents_preview": [
                    {
                        "symbol": str(x.get("symbol") or ""),
                        "side": str(x.get("side") or ""),
                        "qty": _to_int(x.get("qty")),
                    }
                    for x in list(intents)[:3]
                    if isinstance(x, dict)
                ],
            },
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
