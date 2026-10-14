from __future__ import annotations

"""M21-1: Canonical commander runtime entry.

This module provides one stable entry for orchestration while preserving
existing runtime behavior.

Implementation note:
  - This file is the primary commander/orchestrator implementation.
  - `graphs/nodes/commander_node.py` is a thin graph wrapper.
  - `libs/agent/commander.py` is legacy compatibility scaffolding.
  - Commander only routes runtime flow; it does not select symbols or execute orders.

Modes:
  - graph_spine: run M17 graph spine (`run_trading_graph`)
  - decision_packet: run strategist decision + execution packet path
    (`decide_trade` -> `execute_from_packet`)
  - integrated_chain: run visible chain
    (`strategist_node -> scanner_node -> monitor_node -> decision_node -> execute_from_packet`)

Default mode is graph_spine for backward compatibility.
"""

import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

from graphs.trading_graph import run_trading_graph
from graphs.nodes.decide_trade import decide_trade
from graphs.nodes.execute_from_packet import execute_from_packet
from libs.contracts.agent_outputs import build_commander_shadow_artifact
from libs.runtime.commander_memory_policy import build_commander_memory_policy
from libs.runtime.decision_observability import build_commander_route_observability_surface
from libs.runtime.monitor_memory_bias import build_monitor_memory_bias, summarize_monitor_memory_bias
from libs.runtime.scanner_memory_bias import build_scanner_memory_bias, summarize_scanner_memory_bias
from libs.runtime.memory_packet_loader import load_commander_memory_packets
from libs.runtime.monitor_policy import (
    MonitorEntryPolicy,
    build_default_monitor_entry_policy,
    build_monitor_entry_policy_bundle,
    extract_monitor_entry_policy_mapping,
    normalize_monitor_entry_policy,
)
from libs.llm.model_catalog import resolve_execution_profile, resolve_model_profile
from libs.runtime.scanner_bias import normalize_scanner_bias_context, summarize_scanner_bias_context
from libs.runtime.scanner_policy import normalize_scanner_source_type
from libs.runtime.position_horizon_revision import (
    apply_strategist_horizon_revision,
    ensure_horizon_state,
    position_review_due,
)
from libs.runtime.stage3_horizon_lineage import record_stage3_assessment
from libs.runtime.strategy_horizon_feedback import (
    build_commander_horizon_policy,
    build_horizon_context,
)
from libs.runtime.canonical_artifacts import (
    write_commander_artifact,
    write_commander_shadow_artifact,
    write_llm_stage_skip_entry,
)
from libs.runtime.commander.integrated_chain_support import (
    emit_intraday_trade_report,
    load_integrated_chain_nodes,
    mark_strategist_executed,
    run_closeout_guard_fast_path,
    run_controlled_mock_lane_path,
    run_monitor_decision_path,
    run_monitor_only_fast_path,
    run_pre_entry_exit_sweep_if_needed,
)
from libs.runtime.commander.strategist_cycle import (
    run_post_scanner_refresh_cycle,
    resolve_strategist_cache_use,
    run_pre_scanner_strategist_cycle,
)
from libs.runtime.commander.strategist_cache_decision import (
    assess_cached_strategist_reuse_preference as _assess_cached_strategist_reuse_preference,
    should_use_cached_strategist_from_commander_skip as _should_use_cached_strategist_from_commander_skip,
    should_use_cached_strategist_when_flat as _should_use_cached_strategist_when_flat,
    strategist_cache_payload as _strategist_cache_payload,
)
from libs.runtime.commander.strategist_cache_store import (
    hydrate_strategist_output_cache as _hydrate_strategist_output_cache,
    normalize_strategist_output_contract as _normalize_strategist_output_contract,
    persist_strategist_output_cache as _persist_strategist_output_cache,
)
from libs.runtime.commander.strategist_fingerprint import (
    assess_cached_strategist_input_drift as _assess_cached_strategist_input_drift,
    assess_strategist_fingerprint_drift as _assess_strategist_fingerprint_drift,
    build_strategist_input_fingerprint as _build_strategist_input_fingerprint,
    compact_post_scanner_candidate_row as _compact_post_scanner_candidate_row,
    post_scanner_candidate_snapshot as _post_scanner_candidate_snapshot,
    post_scanner_selected_symbol as _post_scanner_selected_symbol,
)
from libs.runtime.commander.strategist_refresh_decision import (
    assess_pre_buy_strategist_refresh_need as _assess_pre_buy_strategist_refresh_need,
    force_selected_symbol_tactical_refresh_decision as _force_selected_symbol_tactical_refresh_decision,
)
from libs.runtime.commander.session_context import (
    build_integrated_chain_session_context,
    seed_shadow_prior_context,
)
from libs.runtime.commander.env_overrides import (
    apply_commander_temporary_runtime_defaults as _apply_commander_temporary_runtime_defaults,
    commander_default_bool as _commander_default_bool,
    commander_memory_usage_disabled as _commander_memory_usage_disabled,
    commander_post_scanner_refresh_enabled as _commander_post_scanner_refresh_enabled,
    commander_pre_entry_exit_sweep_enabled as _commander_pre_entry_exit_sweep_enabled,
    env_bool as _env_bool,
    restore_commander_temporary_runtime_env as _restore_commander_temporary_runtime_env,
)
from libs.runtime.commander.runtime_modes import (
    annotate_runtime_plan as _annotate_runtime_plan,
    normalize_transition as _normalize_transition,
    resolve_runtime_mode,
    resolve_runtime_phase,
)
from libs.runtime.commander.route_surface import (
    derive_commander_selected_route as _derive_commander_selected_route,
    normalize_reporter_integration_config as _normalize_reporter_integration_config,
    reporter_hook_requested as _reporter_hook_requested,
    resolve_commander_reporter_feedback_policy as _resolve_commander_reporter_feedback_policy,
)
from libs.runtime.commander.policy_readers import (
    commander_trade_report_enabled as _commander_trade_report_enabled,
    merge_nested_policy_dict as _merge_nested_policy_dict,
    resolve_commander_cooldown_policy as _resolve_commander_cooldown_policy,
    resolve_commander_route_toggle as _resolve_commander_route_toggle,
)
from libs.runtime.commander.output_frames import (
    build_commander_decision_frame as _build_commander_decision_frame_impl,
)
from libs.runtime.commander.policy_surface import (
    CANDIDATE_WATCH_DEFAULT_CASCADE_ALLOWED_REASONS as _CANDIDATE_WATCH_DEFAULT_CASCADE_ALLOWED_REASONS,
    CANDIDATE_WATCH_DEFAULT_CASCADE_BLOCKED_REASONS as _CANDIDATE_WATCH_DEFAULT_CASCADE_BLOCKED_REASONS,
    COMMANDER_OWNED_LLM_EXECUTION_POLICY_FIELDS as _COMMANDER_OWNED_LLM_EXECUTION_POLICY_FIELDS,
    COMMANDER_OWNED_LLM_POLICY_FIELDS as _COMMANDER_OWNED_LLM_POLICY_FIELDS,
    COMMANDER_OWNED_NUMERIC_POLICY_FIELDS as _COMMANDER_OWNED_NUMERIC_POLICY_FIELDS,
    COMMANDER_OWNED_POLICY_FIELDS as _COMMANDER_OWNED_POLICY_FIELDS,
    COMMANDER_OWNED_SCANNER_POLICY_FIELDS as _COMMANDER_OWNED_SCANNER_POLICY_FIELDS,
    COMMANDER_OWNED_UNIVERSE_POLICY_FIELDS as _COMMANDER_OWNED_UNIVERSE_POLICY_FIELDS,
    DEFAULT_BUY_CLOSEOUT_CUTOFF_MIN as _DEFAULT_BUY_CLOSEOUT_CUTOFF_MIN,
    ENTRY_CONTROL_DYNAMIC_BAND_BLOCKERS as _ENTRY_CONTROL_DYNAMIC_BAND_BLOCKERS,
    ENTRY_CONTROL_POOL_EXPAND_BLOCKERS as _ENTRY_CONTROL_POOL_EXPAND_BLOCKERS,
    OPEN_POSITION_STRATEGIST_REFRESH_COOLDOWN_SEC as _OPEN_POSITION_STRATEGIST_REFRESH_COOLDOWN_SEC,
    PRE_ENTRY_EXIT_SWEEP_TRANSIENT_KEYS as _PRE_ENTRY_EXIT_SWEEP_TRANSIENT_KEYS,
    RuntimeMode,
    RuntimePhase,
)
from libs.runtime.market_hours import MarketHours
from libs.runtime.resilience_state import ensure_runtime_resilience_state
import sys as _r3_sys
from libs.runtime.commander.carry_review_policy import (
    _build_stage4_carry_review_context_r3_impl,
    _force_stage4_carry_review_decision_r3_impl,
    _assess_position_carry_control_r3_impl,
    _derive_carry_state_r3_impl,
    _carry_state_rank_r3_impl,
    _carry_risk_bias_rank_r3_impl,
)
from libs.runtime.commander.fast_path_policy import (
    _should_use_monitor_only_fast_path_r3_impl,
    _should_use_session_closeout_fast_path_r3_impl,
)
from libs.runtime.commander.entry_control_policy import (
    _build_commander_entry_control_r3_impl,
)
from libs.runtime.commander.applied_policy import (
    _resolve_commander_applied_policy_r3_impl,
    _attach_commander_behavior_policy_r3_impl,
    _attach_commander_reporter_feedback_policy_r3_impl,
    _extract_commander_policy_vwap_ceiling_r3_impl,
    _dedupe_reason_list_r3_impl,
    _resolve_profit_protection_activation_ratio_r3_impl,
    _position_current_profit_ratio_r3_impl,
)
from libs.runtime.commander.candidate_watch_policy import (
    _extract_strategist_candidate_watch_policy_r3_impl,
    _normalize_candidate_watch_proposal_for_commander_r3_impl,
    _candidate_watch_rank_cap_r3_impl,
    _apply_candidate_watch_proposal_to_entry_control_r3_impl,
)
from libs.runtime.commander.position_projection import (
    _portfolio_open_position_count_r3_impl,
    _portfolio_open_position_symbols_r3_impl,
    _portfolio_open_position_row_r3_impl,
    _open_position_focus_sort_key_r3_impl,
    _select_open_position_focus_symbol_r3_impl,
    _closeout_unresolved_flatten_symbols_r3_impl,
    _resolve_position_age_seconds_r3_impl,
    _build_open_position_strategist_refresh_context_r3_impl,
    _compact_monitor_entry_state_for_refresh_r3_impl,
    _summarize_monitor_entry_policy_r3_impl,
    _monitor_entry_policy_delta_fields_r3_impl,
    _summarize_monitor_entry_policy_from_strategist_output_r3_impl,
)
from libs.runtime.commander.session_assessments import (
    _build_session_open_recovery_assessment_r3_impl,
    _build_intraday_performance_circuit_r3_impl,
    _derive_commander_market_regime_r3_impl,
    _build_shadow_assessment_summary_r3_impl,
    _ensure_market_context_clock_fields_r3_impl,
)
from libs.runtime.commander.event_projection import (
    _commander_decision_event_meta_r3_impl,
    _portfolio_guard_event_summary_r3_impl,
    _portfolio_preflight_event_summary_r3_impl,
    _portfolio_preflight_block_payload_r3_impl,
    _extract_portfolio_snapshot_health_r3_impl,
    _order_row_side_r3_impl,
    _pending_buy_cancel_intents_from_account_orders_r3_impl,
    _strategist_shadow_fingerprint_r3_impl,
    _shadow_float_r3_impl,
    _shadow_selected_score_r3_impl,
    _seed_commander_shadow_prior_context_r3_impl,
)
from libs.runtime.commander.policy_inputs_projection import (
    behavior_input_allow_legacy_rule_allow_legacy_strategy,
    commander_behavior_policy_inputs,
)
from libs.runtime.commander.policy_normalizers_projection import (
    behavior_norm_carry_risk_bias_carry_risk_reason,
)
from libs.runtime.commander.applied_policy_attach_projection import (
    attach_policy_commander_context_commander_memory_polic,
    attach_policy_commander_decision_commander_horizon_pol,
    attach_policy_monitor_policy,
    attach_policy_provenance,
)
from libs.runtime.commander.decision_context_projection import (
    decision_ctx_entry_capacity_available_market_regime,
    decision_policy_context,
)
from libs.runtime.commander.decision_context_projection_applied_policy_command import (
    applied_policy_command_context,
)
from libs.runtime.commander.decision_overlay_projection import (
    decision_overlay_applied_policy_commander_horizon_policy,
    decision_overlay_cached_output_for_state_decision_summary,
    decision_overlay_blocker_counts_monitor_last_states,
)
from libs.runtime.commander.decision_rules_projection import (
    decision_rules_adaptive_feedback_allowed_adaptive_polic,
    decision_rules_decision_summary_observations,
    decision_rules_current_monitor_entry_policy_summary_pri,
)
from libs.runtime.commander.open_position_inputs_projection import (
    open_pos_input_anomaly_found_last_exit_sweep_by_symbol,
    open_pos_input_candidate_loss_ratios_current_profit_rat,
    open_pos_input_anomaly_found_hold_repeat_count,
)
from libs.runtime.commander.open_position_assessment_projection import (
    open_pos_assess_carry_control,
    open_pos_assess_force_exit_review_pending_open_position,
    open_pos_assess_force_exit_review_pending_open_position_2,
)


def _is_trueish(v: Any) -> bool:
    return str(v or "").strip().lower() in ("1", "true", "yes", "y", "on")


def _coerce_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _resolve_risk_max_positions(state: Dict[str, Any] | None = None) -> int:
    obj = state if isinstance(state, dict) else {}
    for value in (
        ((obj.get("risk_context") or {}).get("max_positions") if isinstance(obj.get("risk_context"), dict) else None),
        ((obj.get("risk") or {}).get("max_positions") if isinstance(obj.get("risk"), dict) else None),
        os.getenv("RISK_MAX_POSITIONS"),
    ):
        try:
            if value not in (None, ""):
                return max(1, int(float(value)))
        except Exception:
            continue
    return 1


def _runtime_now_epoch(state: Dict[str, Any]) -> int:
    explicit_epoch = _coerce_int(state.get("now_epoch"), 0)
    if explicit_epoch > 0:
        return explicit_epoch
    raw_ts = str(state.get("ts") or "").strip()
    if raw_ts:
        try:
            stamped = raw_ts[:-1] + "+00:00" if raw_ts.endswith("Z") else raw_ts
            return int(datetime.fromisoformat(stamped).timestamp())
        except Exception:
            pass
    return int(time.time())


def _runtime_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def _mapping(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _build_intraday_performance_circuit(
    *,
    strategist_output: Dict[str, Any],
    memory_packets: Dict[str, Any],
    current_day: str = "",
) -> Dict[str, Any]:
    return _build_intraday_performance_circuit_r3_impl(strategist_output=strategist_output,
        memory_packets=memory_packets, current_day=current_day, facade=_r3_sys.modules[__name__])


def _runtime_clock_dt_kst(state: Dict[str, Any], *, market_hours: MarketHours | None = None) -> datetime:
    mh = market_hours or MarketHours()
    epoch = _coerce_int(state.get("tick_ts"), 0)
    if epoch <= 0:
        epoch = _coerce_int(state.get("now_epoch"), 0)
    if epoch <= 0:
        epoch = int(time.time())
    return datetime.fromtimestamp(epoch, tz=mh.tz)


def _runtime_clock_input_present(state: Dict[str, Any]) -> bool:
    return _coerce_int(state.get("tick_ts"), 0) > 0 or _coerce_int(state.get("now_epoch"), 0) > 0


def _runtime_day_string_kst(state: Dict[str, Any]) -> str:
    for key in ("day", "trading_day", "session_day", "trade_day"):
        raw = str(state.get(key) or "").strip()
        if not raw:
            continue
        if len(raw) == 8 and raw.isdigit():
            return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"
        return raw[:10]
    return _runtime_clock_dt_kst(state).strftime("%Y-%m-%d")


def _record_post_exit_recap_runtime_result(
    state: Dict[str, Any],
    *,
    day: str,
    trigger: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    runtime = _mapping(state.get("post_exit_shadow_recap_runtime"))
    triggers = _mapping(runtime.get("triggers"))
    day_triggers = _mapping(triggers.get(day))
    day_triggers[trigger] = dict(payload)
    triggers[day] = day_triggers
    runtime["triggers"] = triggers
    runtime["latest"] = {"day": day, "trigger": trigger, **dict(payload)}
    state["post_exit_shadow_recap_runtime"] = runtime
    persisted = state.get("persisted_state")
    if isinstance(persisted, dict):
        persisted["post_exit_shadow_recap_runtime"] = dict(runtime)
        state["persisted_state"] = persisted
    return state


def _maybe_run_post_exit_shadow_recap_runtime(
    state: Dict[str, Any],
    *,
    trigger: str,
) -> Dict[str, Any]:
    if os.getenv("PYTEST_CURRENT_TEST") and not _env_bool("POST_EXIT_SHADOW_RECAP_RUNTIME_IN_TESTS", False):
        return state
    if not _env_bool("POST_EXIT_SHADOW_RECAP_RUNTIME_ENABLED", True):
        return state

    day = _runtime_day_string_kst(state)
    trigger_key = str(trigger or "").strip() or "unknown"
    clock_kst = _runtime_clock_dt_kst(state)
    if trigger_key == "closeout_guard_after_sweep" and clock_kst.strftime("%H%M") >= "1600":
        trigger_key = "closeout_guard_after_sweep_1600_final"
    runtime = _mapping(state.get("post_exit_shadow_recap_runtime"))
    already = _mapping(_mapping(runtime.get("triggers")).get(day)).get(trigger_key)
    if already:
        return state

    reports_root = Path(str(os.getenv("REPORTS_ROOT") or "reports"))
    report_dir = Path(str(os.getenv("POST_EXIT_SHADOW_RECAP_REPORT_DIR") or "reports/dev/analysis/post_exit_shadow_recap"))
    state_path_raw = str(os.getenv("STATE_STORE_PATH") or os.getenv("MOCK_EXAM_STATE_PATH") or "data/state.json").strip()
    state_path = Path(state_path_raw) if state_path_raw else None
    try:
        from libs.reporting.post_exit_shadow_recap import generate_post_exit_shadow_recap

        out = generate_post_exit_shadow_recap(
            reports_root=reports_root,
            report_dir=report_dir,
            day=day,
            state_path=state_path,
        )
        summary = _mapping(out.get("summary"))
        return _record_post_exit_recap_runtime_result(
            state,
            day=day,
            trigger=trigger_key,
            payload={
                "ok": True,
                "source_trigger": str(trigger or ""),
                "generated_at": str(out.get("generated_at") or ""),
                "total": int(summary.get("total") or 0),
                "observed": int(summary.get("observed") or 0),
                "pending": int(summary.get("pending") or 0),
                "report_json_path": str(out.get("report_json_path") or ""),
                "report_md_path": str(out.get("report_md_path") or ""),
            },
        )
    except Exception as exc:
        return _record_post_exit_recap_runtime_result(
            state,
            day=day,
            trigger=trigger_key,
            payload={"ok": False, "source_trigger": str(trigger or ""), "error": str(exc)},
        )


def _ensure_market_context_clock_fields(
    state: Dict[str, Any],
    *,
    market_hours: MarketHours | None = None,
) -> Dict[str, Any]:
    return _ensure_market_context_clock_fields_r3_impl(state, market_hours=market_hours,
        facade=_r3_sys.modules[__name__])


def _derive_commander_market_regime(state: Dict[str, Any], *, shadow_assessment: Dict[str, Any]) -> tuple[str, bool]:
    return _derive_commander_market_regime_r3_impl(state, shadow_assessment=shadow_assessment,
        facade=_r3_sys.modules[__name__])


def _build_shadow_assessment_summary(
    state: Dict[str, Any],
    *,
    mode_value: str,
    phase_value: str,
    status_value: str,
    path_value: str,
    reason_text: str = "",
) -> Dict[str, Any]:
    return _build_shadow_assessment_summary_r3_impl(state, mode_value=mode_value,
        phase_value=phase_value, status_value=status_value, path_value=path_value,
        reason_text=reason_text, facade=_r3_sys.modules[__name__])


def _commander_decision_event_meta(state: Dict[str, Any]) -> Dict[str, Any]:
    return _commander_decision_event_meta_r3_impl(state, facade=_r3_sys.modules[__name__])


def _summarize_monitor_entry_policy(policy: Dict[str, Any]) -> Dict[str, Any]:
    return _summarize_monitor_entry_policy_r3_impl(policy, facade=_r3_sys.modules[__name__])


def _monitor_entry_policy_delta_fields(previous: Dict[str, Any], current: Dict[str, Any]) -> list[str]:
    return _monitor_entry_policy_delta_fields_r3_impl(previous, current,
        facade=_r3_sys.modules[__name__])


def _compact_monitor_entry_state_for_refresh(entry_state: Dict[str, Any]) -> Dict[str, Any]:
    return _compact_monitor_entry_state_for_refresh_r3_impl(entry_state,
        facade=_r3_sys.modules[__name__])


def _carry_state_rank(value: Any) -> int:
    return _carry_state_rank_r3_impl(value, facade=_r3_sys.modules[__name__])


def _carry_risk_bias_rank(value: Any) -> int:
    return _carry_risk_bias_rank_r3_impl(value, facade=_r3_sys.modules[__name__])


def _derive_carry_state(
    *,
    position_age_seconds: Any,
    hold_repeat_count: int,
    overnight_decision: Dict[str, Any] | None,
) -> str:
    return _derive_carry_state_r3_impl(position_age_seconds=position_age_seconds,
        hold_repeat_count=hold_repeat_count, overnight_decision=overnight_decision,
        facade=_r3_sys.modules[__name__])


def _closeout_unresolved_flatten_symbols(state: Dict[str, Any]) -> set[str]:
    return _closeout_unresolved_flatten_symbols_r3_impl(state, facade=_r3_sys.modules[__name__])


def _is_closeout_unresolved_flatten_symbol(state: Dict[str, Any], symbol: str) -> bool:
    normalized = str(symbol or "").strip().upper()
    return bool(normalized and normalized in _closeout_unresolved_flatten_symbols(state))


def _resolve_position_age_seconds(state: Dict[str, Any], row: Dict[str, Any], symbol: str) -> int | None:
    return _resolve_position_age_seconds_r3_impl(state, row, symbol,
        facade=_r3_sys.modules[__name__])


def _build_session_open_recovery_assessment(
    *,
    state: Dict[str, Any],
    carry_state: str,
    entry_state: Dict[str, Any],
    monitor_reason: str,
    active_exit_axis: str,
    effective_loss_ratio: float | None,
) -> Dict[str, Any]:
    return _build_session_open_recovery_assessment_r3_impl(state=state, carry_state=carry_state,
        entry_state=entry_state, monitor_reason=monitor_reason, active_exit_axis=active_exit_axis,
        effective_loss_ratio=effective_loss_ratio, facade=_r3_sys.modules[__name__])


def _assess_position_carry_control(
    *,
    state: Dict[str, Any],
    symbol: str,
    hold_repeat_count: int,
    position_age_seconds: Any,
    effective_loss_ratio: float | None,
    monitor_reason: str,
    active_exit_axis: str,
    entry_state: Dict[str, Any],
    overnight_decision: Dict[str, Any] | None,
) -> Dict[str, Any]:
    return _assess_position_carry_control_r3_impl(state=state, symbol=symbol,
        hold_repeat_count=hold_repeat_count, position_age_seconds=position_age_seconds,
        effective_loss_ratio=effective_loss_ratio, monitor_reason=monitor_reason,
        active_exit_axis=active_exit_axis, entry_state=entry_state,
        overnight_decision=overnight_decision, facade=_r3_sys.modules[__name__])


def _build_open_position_strategist_refresh_context(override_assessment: Dict[str, Any]) -> Dict[str, Any]:
    return _build_open_position_strategist_refresh_context_r3_impl(override_assessment,
        facade=_r3_sys.modules[__name__])


def _summarize_monitor_entry_policy_from_strategist_output(strategist_output: Dict[str, Any]) -> Dict[str, Any]:
    return _summarize_monitor_entry_policy_from_strategist_output_r3_impl(strategist_output,
        facade=_r3_sys.modules[__name__])


def _resolve_commander_applied_policy(state: Dict[str, Any]) -> Dict[str, Any]:
    return _resolve_commander_applied_policy_r3_impl(state, facade=_r3_sys.modules[__name__])


def _resolve_commander_behavior_policy(
    state: Dict[str, Any],
    *,
    selected_route: str = "",
    phase: str = "",
) -> Dict[str, Any]:
    applied_policy = state.get("applied_policy") if isinstance(state.get("applied_policy"), dict) else {}
    commander_override = (
        dict(state.get("commander_open_position_override") or {})
        if isinstance(state.get("commander_open_position_override"), dict)
        else {}
    )

    def _existing_value(*path: str) -> Any:
        cursor: Any = applied_policy
        for key in path:
            if not isinstance(cursor, dict):
                return None
            cursor = cursor.get(key)
        return cursor

    allow_legacy_rule, allow_legacy_strategy_v1, feedback_policy, memory_feedback_enabled, phase_text, reporter_ai_review_enabled, route, strict_mode, trade_report_enabled, trade_report_generate_on_open = behavior_input_allow_legacy_rule_allow_legacy_strategy(selected_route=selected_route, state=state, phase=phase, _existing_value=_existing_value, facade=_r3_sys.modules[__name__])
    if memory_feedback_enabled is None:
        memory_feedback_enabled = _env_bool(
            "USE_STRATEGY_MEMORY_FEEDBACK",
            _commander_default_bool("USE_STRATEGY_MEMORY_FEEDBACK", True),
        )
    performance_memory_enabled = _existing_value("strategist", "performance_memory", "enabled")
    if performance_memory_enabled is None:
        performance_memory_enabled = _env_bool(
            "USE_STRATEGY_PERFORMANCE_MEMORY",
            _commander_default_bool("USE_STRATEGY_PERFORMANCE_MEMORY", True),
        )
    strategy_memory_persist_enabled = _existing_value("strategist", "performance_memory", "persist_enabled")
    if strategy_memory_persist_enabled is None:
        strategy_memory_persist_enabled = _env_bool(
            "STRATEGY_MEMORY_PERSIST_ENABLED",
            _commander_default_bool("STRATEGY_MEMORY_PERSIST_ENABLED", True),
        )
    commander_memory_usage_disabled = _existing_value("commander", "memory_usage", "disabled")
    if commander_memory_usage_disabled is None:
        commander_memory_usage_disabled = _env_bool(
            "COMMANDER_MEMORY_USAGE_DISABLED",
            _commander_default_bool("COMMANDER_MEMORY_USAGE_DISABLED", False),
        )
    strategist_memory_usage_disabled = _existing_value("strategist", "memory_usage", "disabled")
    if strategist_memory_usage_disabled is None:
        strategist_memory_usage_disabled = _env_bool(
            "STRATEGIST_MEMORY_USAGE_DISABLED",
            _commander_default_bool("STRATEGIST_MEMORY_USAGE_DISABLED", False),
        )
    post_scanner_refresh_enabled = _existing_value("commander", "route", "post_scanner_refresh_enabled")
    if post_scanner_refresh_enabled is None:
        post_scanner_refresh_enabled = _env_bool(
            "COMMANDER_POST_SCANNER_REFRESH_ENABLED",
            _commander_default_bool("COMMANDER_POST_SCANNER_REFRESH_ENABLED", True),
        )
    pre_entry_exit_sweep_enabled = _existing_value("commander", "route", "pre_entry_exit_sweep_enabled")
    if pre_entry_exit_sweep_enabled is None:
        pre_entry_exit_sweep_enabled = True
    risk_max_positions = _resolve_risk_max_positions(state)
    memory_bias_observation_only = _env_bool(
        "MEMORY_BIAS_OBSERVATION_ONLY",
        _commander_default_bool("MEMORY_BIAS_OBSERVATION_ONLY", True),
    )
    block_buy_when_open_position, buy_closeout_cutoff_min, cached_strategist_when_flat, eod_flat_cutoff_min, exit_confirm_ticks, exit_policy_enabled, exit_policy_use_eod_flat, kiwoom_condition_limit, min_hold_seconds, monitor_only_when_holding, monitor_scoring_enabled, monitor_scoring_shadow_mode, monitor_scoring_threshold, position_sizing_enabled, position_sizing_risk_per_trade_ratio, post_exit_cooldown_sec, scanner_block_static_when_empty, scanner_include_change_rate, scanner_live_fetch, scanner_source_type, scanner_strict_only, sell_cooldown_sec, top_candidate_pool, universe_asset_type = commander_behavior_policy_inputs(_existing_value=_existing_value, risk_max_positions=risk_max_positions, facade=_r3_sys.modules[__name__])
    position_sizing_notional_ratio = _existing_value(
        "monitor",
        "entry",
        "position_sizing",
        "position_notional_ratio",
    )
    if position_sizing_notional_ratio is None:
        position_sizing_notional_ratio = 0.50
    position_sizing_max_qty = _existing_value("monitor", "entry", "position_sizing", "max_position_qty")
    if position_sizing_max_qty is None:
        position_sizing_max_qty = _coerce_int(os.getenv("MAX_ORDER_QTY") or os.getenv("MAX_QTY"), 10)
    position_sizing_max_notional = _existing_value("monitor", "entry", "position_sizing", "max_position_notional")
    if position_sizing_max_notional is None:
        position_sizing_max_notional = _runtime_float(
            os.getenv("MAX_ORDER_NOTIONAL") or os.getenv("MAX_NOTIONAL"),
            1_000_000.0,
        )
    carry_risk_bias, carry_risk_reason, carry_state, default_execution_profile, hold_repeat_count_max, override_reason, position_sizing_lot_size, position_sizing_min_qty, reporter_daily_execution_profile, reporter_daily_llm, reporter_intraday_execution_profile, reporter_intraday_llm, strategist_execution_profile, strategist_llm, strategy_memory_recent_runs = behavior_norm_carry_risk_bias_carry_risk_reason(_existing_value=_existing_value, commander_override=commander_override, facade=_r3_sys.modules[__name__])
    effective_loss_ratio_min = float(_runtime_float(commander_override.get("effective_loss_ratio_min"), 0.0))
    session_open_recovery = (
        dict(commander_override.get("session_open_recovery_assessment") or {})
        if isinstance(commander_override.get("session_open_recovery_assessment"), dict)
        else {}
    )
    market_context = state.get("market_context") if isinstance(state.get("market_context"), dict) else {}
    raw_minutes_to_close = market_context.get("minutes_to_close")
    minutes_to_close = None if raw_minutes_to_close in (None, "") else float(_runtime_float(raw_minutes_to_close, 0.0))
    carry_exit_policy_overrides: Dict[str, Any] = {}
    carry_policy_adjustments: list[str] = []
    if carry_risk_bias == "urgent_exit_review":
        carry_exit_policy_overrides = {
            "vwap_break_requires_profit": False,
            "hard_stop_pct": 0.015,
            "intraday_low_break_pct": 0.001,
            "trend_strength_floor": -0.10,
        }
        carry_policy_adjustments.append("carry_bias:urgent_exit_review->tighten_exit_policy")
        if str(session_open_recovery.get("recovery_state") or "").strip().lower() == "failed":
            carry_exit_policy_overrides["peak_drawdown_mode"] = "always_on"
            carry_policy_adjustments.append("session_open_recovery:failed->always_on_peak_drawdown")
    elif carry_risk_bias == "elevated" and carry_state in {"overnight_open", "multi_session_stale"}:
        carry_exit_policy_overrides = {
            "vwap_break_requires_profit": False,
            "intraday_low_break_pct": 0.0015,
            "trend_strength_floor": -0.12,
        }
        carry_policy_adjustments.append("carry_bias:elevated->narrow_exit_confirmation")
    elif (
        carry_risk_bias == "elevated"
        and carry_state == "same_session"
        and override_reason == "loss_threshold_exceeded"
        and hold_repeat_count_max >= 6
    ):
        carry_exit_policy_overrides = {
            "vwap_break_requires_profit": False,
            "intraday_low_break_pct": 0.0012,
            "trend_strength_floor": -0.11,
        }
        carry_policy_adjustments.append("carry_bias:elevated_same_session->tighten_loss_review")
        if effective_loss_ratio_min <= -0.01:
            carry_exit_policy_overrides["peak_drawdown_mode"] = "always_on"
            carry_policy_adjustments.append("same_session_loss_threshold->always_on_peak_drawdown")
        closeout_cutoff_min = max(15, _coerce_int(eod_flat_cutoff_min, 10))
        if minutes_to_close is not None and minutes_to_close <= float(closeout_cutoff_min):
            carry_exit_policy_overrides["use_eod_flat"] = True
            carry_exit_policy_overrides["eod_flat_cutoff_min"] = closeout_cutoff_min
            carry_policy_adjustments.append(
                f"same_session_loss_near_close->eod_flat_cutoff:{int(closeout_cutoff_min)}"
            )
    return {
        "execution": {
            "cooldowns": {
                "post_exit_sec": max(0, _coerce_int(post_exit_cooldown_sec, 180)),
                "sell_sec": max(0, _coerce_int(sell_cooldown_sec, 300)),
                "policy_source": "commander_applied_policy",
            },
        },
        "llm": {
            "execution_profile": {
                "profile_name": str(default_execution_profile.get("profile_name") or default_execution_profile.get("name") or "default_intraday"),
                "name": str(default_execution_profile.get("name") or "default_intraday"),
                "temperature": float(_runtime_float(default_execution_profile.get("temperature"), 0.2)),
                "max_tokens": max(256, _coerce_int(default_execution_profile.get("max_tokens"), 8192)),
                "timeout_sec": max(1, _coerce_int(default_execution_profile.get("timeout_sec"), 15)),
                    "retry": {
                        "max_attempts": max(0, _coerce_int((default_execution_profile.get("retry") or {}).get("max_attempts"), 2)),
                        "backoff_sec": max(0.0, float(_runtime_float((default_execution_profile.get("retry") or {}).get("backoff_sec"), 0.0))),
                    },
                    "retry_max": max(0, _coerce_int((default_execution_profile.get("retry") or {}).get("max_attempts"), 2)),
                    "retry_backoff_sec": max(0.0, float(_runtime_float((default_execution_profile.get("retry") or {}).get("backoff_sec"), 0.0))),
                    "policy_source": "commander_applied_policy",
                },
            "strategist": {
                "profile": str(strategist_llm.get("profile") or "balanced"),
                "primary": str(strategist_llm.get("primary") or ""),
                "fallback": str(strategist_llm.get("fallback") or ""),
                "execution_profile": {
                    "profile_name": str(strategist_execution_profile.get("profile_name") or strategist_execution_profile.get("name") or "balanced_reasoning"),
                    "name": str(strategist_execution_profile.get("name") or "balanced_reasoning"),
                    "temperature": float(_runtime_float(strategist_execution_profile.get("temperature"), 0.1)),
                    "max_tokens": max(256, _coerce_int(strategist_execution_profile.get("max_tokens"), 8192)),
                    "timeout_sec": max(1, _coerce_int(strategist_execution_profile.get("timeout_sec"), 15)),
                    "retry": {
                        "max_attempts": max(0, _coerce_int((strategist_execution_profile.get("retry") or {}).get("max_attempts"), 2)),
                        "backoff_sec": max(0.0, float(_runtime_float((strategist_execution_profile.get("retry") or {}).get("backoff_sec"), 0.0))),
                    },
                    "retry_max": max(0, _coerce_int(strategist_execution_profile.get("retry_max"), 2)),
                    "retry_backoff_sec": max(0.0, float(_runtime_float(strategist_execution_profile.get("retry_backoff_sec"), 0.0))),
                    "policy_source": "commander_applied_policy",
                },
                "policy_source": "commander_applied_policy",
            },
            "reporter": {
                "intraday": {
                    "profile": str(reporter_intraday_llm.get("profile") or "fast_free"),
                    "primary": str(reporter_intraday_llm.get("primary") or ""),
                    "fallback": str(reporter_intraday_llm.get("fallback") or ""),
                    "execution_profile": {
                        "profile_name": str(reporter_intraday_execution_profile.get("profile_name") or reporter_intraday_execution_profile.get("name") or "concise_review"),
                        "name": str(reporter_intraday_execution_profile.get("name") or "concise_review"),
                        "temperature": float(_runtime_float(reporter_intraday_execution_profile.get("temperature"), 0.2)),
                        "max_tokens": max(256, _coerce_int(reporter_intraday_execution_profile.get("max_tokens"), 8192)),
                        "timeout_sec": max(1, _coerce_int(reporter_intraday_execution_profile.get("timeout_sec"), 15)),
                        "retry": {
                            "max_attempts": max(0, _coerce_int((reporter_intraday_execution_profile.get("retry") or {}).get("max_attempts"), 2)),
                            "backoff_sec": max(0.0, float(_runtime_float((reporter_intraday_execution_profile.get("retry") or {}).get("backoff_sec"), 0.0))),
                        },
                        "retry_max": max(0, _coerce_int(reporter_intraday_execution_profile.get("retry_max"), 2)),
                        "retry_backoff_sec": max(0.0, float(_runtime_float(reporter_intraday_execution_profile.get("retry_backoff_sec"), 0.0))),
                        "policy_source": "commander_applied_policy",
                    },
                    "policy_source": "commander_applied_policy",
                },
                "daily": {
                    "profile": str(reporter_daily_llm.get("profile") or "strong_reasoning"),
                    "primary": str(reporter_daily_llm.get("primary") or ""),
                    "fallback": str(reporter_daily_llm.get("fallback") or ""),
                    "execution_profile": {
                        "profile_name": str(reporter_daily_execution_profile.get("profile_name") or reporter_daily_execution_profile.get("name") or "deep_review"),
                        "name": str(reporter_daily_execution_profile.get("name") or "deep_review"),
                        "temperature": float(_runtime_float(reporter_daily_execution_profile.get("temperature"), 0.2)),
                        "max_tokens": max(256, _coerce_int(reporter_daily_execution_profile.get("max_tokens"), 8192)),
                        "timeout_sec": max(1, _coerce_int(reporter_daily_execution_profile.get("timeout_sec"), 15)),
                        "retry": {
                            "max_attempts": max(0, _coerce_int((reporter_daily_execution_profile.get("retry") or {}).get("max_attempts"), 2)),
                            "backoff_sec": max(0.0, float(_runtime_float((reporter_daily_execution_profile.get("retry") or {}).get("backoff_sec"), 0.0))),
                        },
                        "retry_max": max(0, _coerce_int(reporter_daily_execution_profile.get("retry_max"), 2)),
                        "retry_backoff_sec": max(0.0, float(_runtime_float(reporter_daily_execution_profile.get("retry_backoff_sec"), 0.0))),
                        "policy_source": "commander_applied_policy",
                    },
                    "policy_source": "commander_applied_policy",
                },
            },
        },
        "reporter": {
            "ai_review": {
                "enabled": bool(reporter_ai_review_enabled),
                "policy_source": "commander_applied_policy",
            },
            "trade_report": {
                "enabled": bool(trade_report_enabled),
                "generate_on_open": bool(trade_report_generate_on_open),
                "policy_source": "commander_applied_policy",
            },
        },
        "strategist": {
            "runtime": {
                "strict_mode": bool(strict_mode),
                "allow_legacy_rule": bool(allow_legacy_rule),
                "allow_legacy_strategy_v1": bool(allow_legacy_strategy_v1),
                "policy_source": "commander_applied_policy",
            },
            "memory_feedback": {
                "enabled": bool(memory_feedback_enabled),
                "recent_runs": max(1, _coerce_int(strategy_memory_recent_runs, 12)),
                "policy_source": "commander_applied_policy",
            },
            "performance_memory": {
                "enabled": bool(performance_memory_enabled),
                "persist_enabled": bool(strategy_memory_persist_enabled),
                "policy_source": "commander_applied_policy",
            },
            "memory_usage": {
                "disabled": bool(strategist_memory_usage_disabled),
                "policy_source": "commander_applied_policy",
            },
            "reporter_feedback_mode": str(feedback_policy.get("reporter_feedback_mode") or "auto"),
            "reporter_feedback_mode_source": str(
                feedback_policy.get("reporter_feedback_mode_source") or "commander_applied_policy"
            ),
            "reporter_feedback_mode_reason": str(feedback_policy.get("reporter_feedback_mode_reason") or ""),
            "reporter_feedback_semantics": "advisory_only",
        },
        "commander": {
            "route": {
                "monitor_only_when_holding": bool(monitor_only_when_holding),
                "cached_strategist_when_flat": bool(cached_strategist_when_flat),
                "post_scanner_refresh_enabled": bool(post_scanner_refresh_enabled),
                "pre_entry_exit_sweep_enabled": bool(pre_entry_exit_sweep_enabled),
                "policy_source": "commander_applied_policy",
            },
            "memory_usage": {
                "disabled": bool(commander_memory_usage_disabled),
                "policy_source": "commander_applied_policy",
            },
        },
        "universe": {
            "asset_type": str(universe_asset_type or "all_tradable").strip().lower() or "all_tradable",
            "policy_source": "commander_applied_policy",
        },
        "scanner": {
            "memory_bias": {
                "observation_only": bool(memory_bias_observation_only),
                "policy_source": "commander_applied_policy",
            },
            "source": {
                "type": normalize_scanner_source_type(scanner_source_type),
                "policy_source": "commander_applied_policy",
            },
            "candidate": {
                "top_pool": max(1, _coerce_int(top_candidate_pool, 30)),
                "policy_source": "commander_applied_policy",
            },
            "kiwoom": {
                "condition_limit": max(0, _coerce_int(kiwoom_condition_limit, 200)),
                "strict_only": bool(scanner_strict_only),
                "live_fetch": bool(scanner_live_fetch),
                "include_change_rate": bool(scanner_include_change_rate),
                "policy_source": "commander_applied_policy",
            },
            "fallback": {
                "block_static_when_empty": bool(scanner_block_static_when_empty),
                "policy_source": "commander_applied_policy",
            },
        },
        "monitor": {
            "memory_bias": {
                "observation_only": bool(memory_bias_observation_only),
                "policy_source": "commander_applied_policy",
            },
            "hold": {
                "min_hold_seconds": max(0, _coerce_int(min_hold_seconds, 600)),
                "policy_source": "commander_applied_policy",
            },
            "exit": {
                "enabled": bool(exit_policy_enabled),
                "confirm_ticks": max(1, _coerce_int(exit_confirm_ticks, 2)),
                "eod_flat": {
                    "enabled": bool(exit_policy_use_eod_flat),
                    "cutoff_min": max(0, _coerce_int(eod_flat_cutoff_min, 10)),
                },
                "policy_overrides": dict(carry_exit_policy_overrides),
                "policy_adjustments": list(carry_policy_adjustments),
                "carry_state": carry_state,
                "carry_risk_bias": carry_risk_bias,
                "carry_risk_reason": carry_risk_reason,
                "policy_source": "commander_applied_policy",
            },
            "entry": {
                "block_buy_when_open_position": bool(block_buy_when_open_position),
                "multi_position": {
                    "enabled": bool(risk_max_positions > 1),
                    "max_positions": int(risk_max_positions),
                    "same_symbol_reentry_allowed": False,
                    "pending_buy_same_symbol_allowed": False,
                    "open_position_gate_mode": "max_positions",
                    "policy_source": "commander_applied_policy",
                },
                "buy_closeout_cutoff_min": max(
                    _coerce_int(eod_flat_cutoff_min, 10),
                    _coerce_int(buy_closeout_cutoff_min, _DEFAULT_BUY_CLOSEOUT_CUTOFF_MIN),
                ),
                "position_sizing": {
                    "enabled": bool(position_sizing_enabled),
                    "risk_per_trade_ratio": max(
                        0.0,
                        float(_runtime_float(position_sizing_risk_per_trade_ratio, 0.01)),
                    ),
                    "position_notional_ratio": max(
                        0.0,
                        float(_runtime_float(position_sizing_notional_ratio, 0.50)),
                    ),
                    "max_position_qty": max(1, _coerce_int(position_sizing_max_qty, 10)),
                    "max_position_notional": max(
                        0.0,
                        float(_runtime_float(position_sizing_max_notional, 0.0)),
                    ),
                    "min_position_qty": max(1, _coerce_int(position_sizing_min_qty, 1)),
                    "lot_size": max(1, _coerce_int(position_sizing_lot_size, 1)),
                    "policy_source": "commander_applied_policy",
                },
                "scoring": {
                    "enabled": bool(monitor_scoring_enabled),
                    "shadow_mode": bool(monitor_scoring_shadow_mode),
                    "threshold": max(0.0, float(_runtime_float(monitor_scoring_threshold, 3.0))),
                    "entry_threshold": max(0.0, float(_runtime_float(monitor_scoring_threshold, 3.0))),
                    "policy_source": "commander_applied_policy",
                },
            },
        },
        "policy_sources": {
            "commander_owned_fields": list(_COMMANDER_OWNED_POLICY_FIELDS),
            "commander_owned_universe_fields": list(_COMMANDER_OWNED_UNIVERSE_POLICY_FIELDS),
            "commander_owned_scanner_fields": list(_COMMANDER_OWNED_SCANNER_POLICY_FIELDS),
            "commander_owned_numeric_fields": list(_COMMANDER_OWNED_NUMERIC_POLICY_FIELDS),
            "commander_owned_llm_fields": list(_COMMANDER_OWNED_LLM_POLICY_FIELDS),
            "commander_owned_llm_execution_fields": list(_COMMANDER_OWNED_LLM_EXECUTION_POLICY_FIELDS),
        },
        "commander_applied_policy_summary": {
            "selected_route": route,
            "runtime_phase": phase_text,
            "reporter_ai_review_enabled": bool(reporter_ai_review_enabled),
            "trade_report_enabled": bool(trade_report_enabled),
            "trade_report_generate_on_open": bool(trade_report_generate_on_open),
            "strategist_strict_mode": bool(strict_mode),
            "allow_legacy_rule": bool(allow_legacy_rule),
            "allow_legacy_strategy_v1": bool(allow_legacy_strategy_v1),
            "strategy_memory_feedback_enabled": bool(memory_feedback_enabled),
            "strategy_performance_memory_enabled": bool(performance_memory_enabled),
            "strategy_memory_persist_enabled": bool(strategy_memory_persist_enabled),
            "commander_memory_usage_disabled": bool(commander_memory_usage_disabled),
            "strategist_memory_usage_disabled": bool(strategist_memory_usage_disabled),
            "memory_bias_observation_only": bool(memory_bias_observation_only),
            "post_scanner_refresh_enabled": bool(post_scanner_refresh_enabled),
            "pre_entry_exit_sweep_enabled": bool(pre_entry_exit_sweep_enabled),
            "monitor_only_when_holding": bool(monitor_only_when_holding),
            "cached_strategist_when_flat": bool(cached_strategist_when_flat),
            "exit_policy_enabled": bool(exit_policy_enabled),
            "exit_policy_use_eod_flat": bool(exit_policy_use_eod_flat),
            "carry_state": carry_state,
            "carry_risk_bias": carry_risk_bias,
            "carry_risk_reason": carry_risk_reason,
            "carry_exit_policy_overrides": dict(carry_exit_policy_overrides),
            "carry_policy_adjustments": list(carry_policy_adjustments),
            "block_buy_when_open_position": bool(block_buy_when_open_position),
            "multi_position_enabled": bool(risk_max_positions > 1),
            "max_positions": int(risk_max_positions),
            "same_symbol_reentry_allowed": False,
            "pending_buy_same_symbol_allowed": False,
            "open_position_gate_mode": "max_positions",
            "buy_closeout_cutoff_min": max(
                _coerce_int(eod_flat_cutoff_min, 10),
                _coerce_int(buy_closeout_cutoff_min, _DEFAULT_BUY_CLOSEOUT_CUTOFF_MIN),
            ),
            "monitor_scoring_enabled": bool(monitor_scoring_enabled),
            "monitor_scoring_shadow_mode": bool(monitor_scoring_shadow_mode),
            "position_sizing_enabled": bool(position_sizing_enabled),
            "position_sizing_risk_per_trade_ratio": max(
                0.0,
                float(_runtime_float(position_sizing_risk_per_trade_ratio, 0.01)),
            ),
            "position_sizing_position_notional_ratio": max(
                0.0,
                float(_runtime_float(position_sizing_notional_ratio, 0.50)),
            ),
            "position_sizing_max_position_qty": max(1, _coerce_int(position_sizing_max_qty, 10)),
            "position_sizing_max_position_notional": max(
                0.0,
                float(_runtime_float(position_sizing_max_notional, 0.0)),
            ),
            "reporter_feedback_mode": str(feedback_policy.get("reporter_feedback_mode") or "auto"),
            "universe_fields": {
                "asset_type": str(universe_asset_type or "all_tradable").strip().lower() or "all_tradable",
            },
            "scanner_fields": {
                "source_type": normalize_scanner_source_type(scanner_source_type),
                "strict_only": bool(scanner_strict_only),
                "block_static_when_empty": bool(scanner_block_static_when_empty),
                "live_fetch": bool(scanner_live_fetch),
                "include_change_rate": bool(scanner_include_change_rate),
            },
            "llm_profiles": {
                "strategist": {
                    "profile": str(strategist_llm.get("profile") or "balanced"),
                    "primary": str(strategist_llm.get("primary") or ""),
                    "fallback": str(strategist_llm.get("fallback") or ""),
                },
                "reporter_intraday": {
                    "profile": str(reporter_intraday_llm.get("profile") or "fast_free"),
                    "primary": str(reporter_intraday_llm.get("primary") or ""),
                    "fallback": str(reporter_intraday_llm.get("fallback") or ""),
                },
                "reporter_daily": {
                    "profile": str(reporter_daily_llm.get("profile") or "strong_reasoning"),
                    "primary": str(reporter_daily_llm.get("primary") or ""),
                    "fallback": str(reporter_daily_llm.get("fallback") or ""),
                },
            },
            "llm_execution_profiles": {
                "default": {
                    "profile_name": str(default_execution_profile.get("profile_name") or default_execution_profile.get("name") or "default_intraday"),
                    "temperature": float(_runtime_float(default_execution_profile.get("temperature"), 0.2)),
                    "max_tokens": max(256, _coerce_int(default_execution_profile.get("max_tokens"), 8192)),
                    "timeout_sec": max(1, _coerce_int(default_execution_profile.get("timeout_sec"), 15)),
                    "retry": {
                        "max_attempts": max(0, _coerce_int((default_execution_profile.get("retry") or {}).get("max_attempts"), 2)),
                        "backoff_sec": max(0.0, float(_runtime_float((default_execution_profile.get("retry") or {}).get("backoff_sec"), 0.0))),
                    },
                },
                "strategist": {
                    "profile_name": str(strategist_execution_profile.get("profile_name") or strategist_execution_profile.get("name") or "balanced_reasoning"),
                    "temperature": float(_runtime_float(strategist_execution_profile.get("temperature"), 0.1)),
                    "max_tokens": max(256, _coerce_int(strategist_execution_profile.get("max_tokens"), 8192)),
                    "timeout_sec": max(1, _coerce_int(strategist_execution_profile.get("timeout_sec"), 15)),
                    "retry": {
                        "max_attempts": max(0, _coerce_int((strategist_execution_profile.get("retry") or {}).get("max_attempts"), 2)),
                        "backoff_sec": max(0.0, float(_runtime_float((strategist_execution_profile.get("retry") or {}).get("backoff_sec"), 0.0))),
                    },
                },
                "reporter_intraday": {
                    "profile_name": str(reporter_intraday_execution_profile.get("profile_name") or reporter_intraday_execution_profile.get("name") or "concise_review"),
                    "temperature": float(_runtime_float(reporter_intraday_execution_profile.get("temperature"), 0.2)),
                    "max_tokens": max(256, _coerce_int(reporter_intraday_execution_profile.get("max_tokens"), 8192)),
                    "timeout_sec": max(1, _coerce_int(reporter_intraday_execution_profile.get("timeout_sec"), 15)),
                    "retry": {
                        "max_attempts": max(0, _coerce_int((reporter_intraday_execution_profile.get("retry") or {}).get("max_attempts"), 2)),
                        "backoff_sec": max(0.0, float(_runtime_float((reporter_intraday_execution_profile.get("retry") or {}).get("backoff_sec"), 0.0))),
                    },
                },
                "reporter_daily": {
                    "profile_name": str(reporter_daily_execution_profile.get("profile_name") or reporter_daily_execution_profile.get("name") or "deep_review"),
                    "temperature": float(_runtime_float(reporter_daily_execution_profile.get("temperature"), 0.2)),
                    "max_tokens": max(256, _coerce_int(reporter_daily_execution_profile.get("max_tokens"), 8192)),
                    "timeout_sec": max(1, _coerce_int(reporter_daily_execution_profile.get("timeout_sec"), 15)),
                    "retry": {
                        "max_attempts": max(0, _coerce_int((reporter_daily_execution_profile.get("retry") or {}).get("max_attempts"), 2)),
                        "backoff_sec": max(0.0, float(_runtime_float((reporter_daily_execution_profile.get("retry") or {}).get("backoff_sec"), 0.0))),
                    },
                },
            },
            "numeric_fields": {
                "post_exit_cooldown_sec": max(0, _coerce_int(post_exit_cooldown_sec, 180)),
                "sell_cooldown_sec": max(0, _coerce_int(sell_cooldown_sec, 300)),
                "min_hold_seconds": max(0, _coerce_int(min_hold_seconds, 600)),
                "exit_confirm_ticks": max(1, _coerce_int(exit_confirm_ticks, 2)),
                "eod_flat_cutoff_min": max(0, _coerce_int(eod_flat_cutoff_min, 10)),
                "buy_closeout_cutoff_min": max(
                    _coerce_int(eod_flat_cutoff_min, 10),
                    _coerce_int(buy_closeout_cutoff_min, _DEFAULT_BUY_CLOSEOUT_CUTOFF_MIN),
                ),
                "top_candidate_pool": max(1, _coerce_int(top_candidate_pool, 30)),
                "kiwoom_condition_limit": max(0, _coerce_int(kiwoom_condition_limit, 200)),
                "monitor_entry_scoring_threshold": max(0.0, float(_runtime_float(monitor_scoring_threshold, 3.0))),
                "position_sizing_enabled": bool(position_sizing_enabled),
                "position_sizing_risk_per_trade_ratio": max(
                    0.0,
                    float(_runtime_float(position_sizing_risk_per_trade_ratio, 0.01)),
                ),
                "position_sizing_position_notional_ratio": max(
                    0.0,
                    float(_runtime_float(position_sizing_notional_ratio, 0.50)),
                ),
                "position_sizing_max_position_qty": max(1, _coerce_int(position_sizing_max_qty, 10)),
                "position_sizing_max_position_notional": max(
                    0.0,
                    float(_runtime_float(position_sizing_max_notional, 0.0)),
                ),
                "strategy_memory_recent_runs": max(1, _coerce_int(strategy_memory_recent_runs, 12)),
            },
        },
    }


def _attach_commander_behavior_policy(
    state: Dict[str, Any],
    *,
    selected_route: str = "",
    phase: str = "",
) -> Dict[str, Any]:
    return _attach_commander_behavior_policy_r3_impl(state, selected_route=selected_route,
        phase=phase, facade=_r3_sys.modules[__name__])


def _attach_commander_reporter_feedback_policy(
    state: Dict[str, Any],
    *,
    selected_route: str = "",
    phase: str = "",
) -> Dict[str, Any]:
    return _attach_commander_reporter_feedback_policy_r3_impl(state, selected_route=selected_route,
        phase=phase, facade=_r3_sys.modules[__name__])


def _attach_commander_applied_policy(state: Dict[str, Any]) -> Dict[str, Any]:
    state = apply_strategist_horizon_revision(
        state,
        now_epoch=_runtime_now_epoch(state),
    )
    policy_meta = _resolve_commander_applied_policy(state)
    applied_policy = dict(policy_meta.get("applied_policy") or {})
    commander_decision = state.get("commander_decision") if isinstance(state.get("commander_decision"), dict) else {}
    commander_entry_control = (
        dict(commander_decision.get("entry_control") or {})
        if isinstance(commander_decision.get("entry_control"), dict)
        else {}
    )
    if commander_entry_control:
        applied_policy["commander_entry_control"] = dict(commander_entry_control)
        applied_policy["entry_control"] = dict(commander_entry_control)
    state["commander_applied_policy"] = dict(applied_policy)
    state["commander_applied_policy_meta"] = dict(policy_meta)
    state["monitor_entry_policy"] = dict(applied_policy)
    applied_policy_wrapper = dict(state.get("applied_policy") or {}) if isinstance(state.get("applied_policy"), dict) else {}
    strategist_policy = (
        dict(applied_policy_wrapper.get("strategist") or {})
        if isinstance(applied_policy_wrapper.get("strategist"), dict)
        else {}
    )
    merged_applied_policy = dict(applied_policy_wrapper)
    merged_applied_policy.update(applied_policy)
    if strategist_policy:
        merged_applied_policy["strategist"] = strategist_policy
    for section_name in ("execution", "llm", "reporter", "commander", "scanner", "monitor", "universe", "policy_sources"):
        section_value = applied_policy_wrapper.get(section_name)
        if isinstance(section_value, dict):
            merged_applied_policy[section_name] = dict(section_value)
    if applied_policy_wrapper.get("reporter_feedback_mode") not in (None, ""):
        merged_applied_policy["reporter_feedback_mode"] = applied_policy_wrapper.get("reporter_feedback_mode")
    if applied_policy_wrapper.get("reporter_feedback_mode_source") not in (None, ""):
        merged_applied_policy["reporter_feedback_mode_source"] = applied_policy_wrapper.get("reporter_feedback_mode_source")
    if applied_policy_wrapper.get("reporter_feedback_mode_reason") not in (None, ""):
        merged_applied_policy["reporter_feedback_mode_reason"] = applied_policy_wrapper.get("reporter_feedback_mode_reason")
    state["applied_policy"] = merged_applied_policy

    strategist_output = state.get("strategist_output") if isinstance(state.get("strategist_output"), dict) else {}
    if not strategist_output:
        return state

    commander_context, commander_memory_policy, memory_packets, scanner_policy, strategist_output, strategy_policy = attach_policy_commander_context_commander_memory_polic(strategist_output=strategist_output, facade=_r3_sys.modules[__name__])
    try:
        memory_packets = load_commander_memory_packets(state=state)
        commander_memory_policy = build_commander_memory_policy(
            session_bias=str(
                commander_decision.get("session_bias")
                or commander_context.get("session_bias")
                or state.get("session_bias")
                or state.get("runtime_phase")
                or "session"
            ),
            memory_packets=memory_packets,
            usage_disabled=_commander_memory_usage_disabled(state),
        )
    except Exception:
        memory_packets = (
            dict(commander_context.get("memory_packets") or {})
            if isinstance(commander_context.get("memory_packets"), dict)
            else dict(commander_decision.get("memory_packets") or {})
            if isinstance(commander_decision.get("memory_packets"), dict)
            else {}
        )
        commander_memory_policy = (
            dict(commander_context.get("commander_memory_policy") or {})
            if isinstance(commander_context.get("commander_memory_policy"), dict)
            else dict(commander_decision.get("commander_memory_policy") or {})
            if isinstance(commander_decision.get("commander_memory_policy"), dict)
            else {}
        )
    raw_scanner_bias_context = {}
    if isinstance(commander_context.get("scanner_bias"), dict):
        raw_scanner_bias_context = dict(commander_context.get("scanner_bias") or {})
    elif isinstance(scanner_policy.get("scanner_bias"), dict):
        raw_scanner_bias_context = dict(scanner_policy.get("scanner_bias") or {})
    elif isinstance(strategist_output.get("scanner_bias_context"), dict):
        raw_scanner_bias_context = dict(strategist_output.get("scanner_bias_context") or {})
    scanner_bias_context, scanner_bias_meta = normalize_scanner_bias_context(
        raw_scanner_bias_context or None,
        bias_source="commander_confirmed",
    )
    scanner_bias_summary = summarize_scanner_bias_context(scanner_bias_context)
    try:
        scanner_memory_bias = build_scanner_memory_bias(
            commander_memory_policy=commander_memory_policy,
            memory_packets=memory_packets,
        )
        scanner_memory_bias_summary = summarize_scanner_memory_bias(scanner_memory_bias)
        monitor_memory_bias = build_monitor_memory_bias(
            commander_memory_policy=commander_memory_policy,
            memory_packets=memory_packets,
        )
        monitor_memory_bias_summary = summarize_monitor_memory_bias(monitor_memory_bias)
    except Exception:
        scanner_memory_bias = (
            dict(commander_context.get("scanner_memory_bias") or {})
            if isinstance(commander_context.get("scanner_memory_bias"), dict)
            else dict(commander_decision.get("scanner_memory_bias") or {})
            if isinstance(commander_decision.get("scanner_memory_bias"), dict)
            else {}
        )
        scanner_memory_bias_summary = (
            dict(commander_context.get("scanner_memory_bias_summary") or {})
            if isinstance(commander_context.get("scanner_memory_bias_summary"), dict)
            else dict(commander_decision.get("scanner_memory_bias_summary") or {})
            if isinstance(commander_decision.get("scanner_memory_bias_summary"), dict)
            else {}
        )
        monitor_memory_bias = (
            dict(commander_context.get("monitor_memory_bias") or {})
            if isinstance(commander_context.get("monitor_memory_bias"), dict)
            else dict(commander_decision.get("monitor_memory_bias") or {})
            if isinstance(commander_decision.get("monitor_memory_bias"), dict)
            else {}
        )
        monitor_memory_bias_summary = (
            dict(commander_context.get("monitor_memory_bias_summary") or {})
            if isinstance(commander_context.get("monitor_memory_bias_summary"), dict)
            else dict(commander_decision.get("monitor_memory_bias_summary") or {})
            if isinstance(commander_decision.get("monitor_memory_bias_summary"), dict)
            else {}
        )
    commander_context.update(
        {
            "source": str(commander_context.get("source") or "commander_decision"),
            "market_regime": str(commander_decision.get("market_regime") or commander_context.get("market_regime") or ""),
            "market_regime_rail": str(
                commander_decision.get("market_regime_rail")
                or commander_context.get("market_regime_rail")
                or ""
            ),
            "market_regime_forced_by_rail": bool(
                commander_decision.get("market_regime_forced_by_rail")
                if commander_decision.get("market_regime_forced_by_rail") is not None
                else commander_context.get("market_regime_forced_by_rail")
            ),
            "session_bias": str(commander_decision.get("session_bias") or commander_context.get("session_bias") or ""),
            "risk_mode": str(commander_decision.get("risk_mode") or commander_context.get("risk_mode") or ""),
            "allowed_playbooks": list(commander_decision.get("allowed_playbooks") or commander_context.get("allowed_playbooks") or []),
            "banned_playbooks": list(commander_decision.get("banned_playbooks") or commander_context.get("banned_playbooks") or []),
            "scanner_mission": str(commander_decision.get("scanner_mission") or commander_context.get("scanner_mission") or ""),
            "monitor_mission": str(commander_decision.get("monitor_mission") or commander_context.get("monitor_mission") or ""),
            "llm_policy": str(commander_decision.get("llm_policy") or commander_context.get("llm_policy") or ""),
            "command_intent": str(commander_decision.get("command_intent") or commander_context.get("command_intent") or ""),
            "strategist_invocation": str(commander_decision.get("strategist_invocation") or commander_context.get("strategist_invocation") or ""),
            "flow_instruction": str(commander_decision.get("flow_instruction") or commander_context.get("flow_instruction") or ""),
            "no_trade_reason_code": str(commander_decision.get("no_trade_reason_code") or commander_context.get("no_trade_reason_code") or ""),
            "decision_summary": str(commander_decision.get("decision_summary") or commander_context.get("decision_summary") or ""),
            "strategist_refresh_requested": bool(
                commander_decision.get("strategist_refresh_requested")
                if commander_decision.get("strategist_refresh_requested") is not None
                else commander_context.get("strategist_refresh_requested")
            ),
            "strategist_refresh_reason": str(
                commander_decision.get("strategist_refresh_reason")
                or commander_context.get("strategist_refresh_reason")
                or ""
            ),
            "strategist_refresh_context": dict(
                commander_decision.get("strategist_refresh_context")
                or commander_context.get("strategist_refresh_context")
                or {}
            ),
            "carry_state": str(commander_decision.get("carry_state") or commander_context.get("carry_state") or ""),
            "carry_risk_bias": str(
                commander_decision.get("carry_risk_bias") or commander_context.get("carry_risk_bias") or ""
            ),
            "carry_risk_reason": str(
                commander_decision.get("carry_risk_reason") or commander_context.get("carry_risk_reason") or ""
            ),
            "session_open_recovery_assessment": dict(
                commander_decision.get("session_open_recovery_assessment")
                or commander_context.get("session_open_recovery_assessment")
                or {}
            ),
            "observations": dict(commander_decision.get("observations") or commander_context.get("observations") or {}),
            "source_priority": list(commander_decision.get("source_priority") or commander_context.get("source_priority") or []),
            "source_refs": dict(commander_decision.get("source_refs") or commander_context.get("source_refs") or {}),
            "shadow_used": bool(
                commander_decision.get("shadow_used")
                if commander_decision.get("shadow_used") is not None
                else commander_context.get("shadow_used")
            ),
            "strategist_fallback_used": bool(
                commander_decision.get("strategist_fallback_used")
                if commander_decision.get("strategist_fallback_used") is not None
                else commander_context.get("strategist_fallback_used")
            ),
            "memory_packets": dict(memory_packets),
            "commander_memory_policy": dict(commander_memory_policy),
            "applied_policy": dict(applied_policy),
            "policy_source": str(policy_meta.get("policy_source") or ""),
            "policy_validation_status": str(policy_meta.get("policy_validation_status") or ""),
            "policy_fallback_used": bool(policy_meta.get("policy_fallback_used")),
            "policy_fallback_reason": str(policy_meta.get("policy_fallback_reason") or ""),
            "policy_partial_normalized": bool(policy_meta.get("policy_partial_normalized")),
            "policy_default_filled_fields": list(policy_meta.get("policy_default_filled_fields") or []),
            "policy_validation_missing_fields": list(policy_meta.get("policy_validation_missing_fields") or []),
            "policy_validation_invalid_fields": list(policy_meta.get("policy_validation_invalid_fields") or []),
            "override_reason": str(policy_meta.get("override_reason") or ""),
            "applied_policy_source_chain": list(policy_meta.get("applied_policy_source_chain") or []),
            "monitor_entry_policy_summary": dict(policy_meta.get("monitor_entry_policy_summary") or {}),
            "entry_control": dict(commander_entry_control),
            "commander_entry_control": dict(commander_entry_control),
            "scanner_bias": scanner_bias_context.to_dict(),
            "scanner_bias_summary": dict(scanner_bias_summary),
            "scanner_memory_bias": dict(scanner_memory_bias),
            "scanner_memory_bias_summary": dict(scanner_memory_bias_summary),
            "monitor_memory_bias": dict(monitor_memory_bias),
            "monitor_memory_bias_summary": dict(monitor_memory_bias_summary),
        }
    )
    commander_decision, commander_horizon_policy, horizon_context = attach_policy_commander_decision_commander_horizon_pol(strategist_output=strategist_output, strategy_policy=strategy_policy, commander_context=commander_context, memory_packets=memory_packets, state=state, commander_decision=commander_decision, facade=_r3_sys.modules[__name__])
    commander_decision["commander_horizon_policy"] = dict(commander_horizon_policy)
    commander_decision["horizon_context"] = dict(horizon_context)
    state["commander_decision"] = commander_decision
    state["commander_horizon_policy"] = dict(commander_horizon_policy)
    merged_applied_policy = dict(state.get("applied_policy") or {}) if isinstance(state.get("applied_policy"), dict) else {}
    merged_applied_policy["horizon"] = dict(commander_horizon_policy)
    merged_applied_policy["commander_horizon_policy"] = dict(commander_horizon_policy)
    state["applied_policy"] = merged_applied_policy
    monitor_policy = attach_policy_monitor_policy(commander_context=commander_context, strategy_policy=strategy_policy, applied_policy=applied_policy, policy_meta=policy_meta, facade=_r3_sys.modules[__name__])[0]
    monitor_policy["monitor_memory_bias"] = dict(monitor_memory_bias)
    monitor_policy["monitor_memory_bias_summary"] = dict(monitor_memory_bias_summary)
    monitor_policy["commander_horizon_policy"] = dict(commander_horizon_policy)
    monitor_policy["horizon_policy"] = dict(commander_horizon_policy)
    if commander_entry_control:
        monitor_policy["entry_control"] = dict(commander_entry_control)
        monitor_policy["commander_entry_control"] = dict(commander_entry_control)
    strategy_policy["monitor_policy"] = monitor_policy
    strategy_policy["commander_horizon_policy"] = dict(commander_horizon_policy)
    if commander_entry_control:
        strategy_policy["entry_control"] = dict(commander_entry_control)
    scanner_policy["scanner_bias"] = scanner_bias_context.to_dict()
    scanner_policy["scanner_bias_summary"] = dict(scanner_bias_summary)
    scanner_policy["scanner_memory_bias"] = dict(scanner_memory_bias)
    scanner_policy["scanner_memory_bias_summary"] = dict(scanner_memory_bias_summary)
    provenance = attach_policy_provenance(commander_entry_control=commander_entry_control, scanner_policy=scanner_policy, strategy_policy=strategy_policy, policy_meta=policy_meta, scanner_bias_meta=scanner_bias_meta, facade=_r3_sys.modules[__name__])[0]

    strategist_output["strategy_policy"] = strategy_policy
    strategist_output["commander_context_ref"] = {
        **(
            dict(strategist_output.get("commander_context_ref") or {})
            if isinstance(strategist_output.get("commander_context_ref"), dict)
            else {}
        ),
        "source": str(commander_context.get("source") or ""),
        "market_regime": str(commander_context.get("market_regime") or ""),
        "market_regime_rail": str(commander_context.get("market_regime_rail") or ""),
        "market_regime_forced_by_rail": bool(commander_context.get("market_regime_forced_by_rail")),
        "session_bias": str(commander_context.get("session_bias") or ""),
        "risk_mode": str(commander_context.get("risk_mode") or ""),
        "command_intent": str(commander_context.get("command_intent") or ""),
        "strategist_invocation": str(commander_context.get("strategist_invocation") or ""),
        "llm_policy": str(commander_context.get("llm_policy") or ""),
        "no_trade_reason_code": str(commander_context.get("no_trade_reason_code") or ""),
        "strategist_refresh_requested": bool(commander_context.get("strategist_refresh_requested")),
        "strategist_refresh_reason": str(commander_context.get("strategist_refresh_reason") or ""),
        "strategist_refresh_context": dict(commander_context.get("strategist_refresh_context") or {}),
        "commander_horizon_policy": dict(commander_horizon_policy),
        "horizon_context": dict(horizon_context),
        "entry_control": dict(commander_entry_control),
        "carry_state": str(commander_context.get("carry_state") or ""),
        "carry_risk_bias": str(commander_context.get("carry_risk_bias") or ""),
        "carry_risk_reason": str(commander_context.get("carry_risk_reason") or ""),
        "session_open_recovery_assessment": dict(
            commander_context.get("session_open_recovery_assessment") or {}
        ),
        "decision_summary": str(commander_context.get("decision_summary") or ""),
        "source_priority": list(commander_context.get("source_priority") or []),
        "policy_source": str(policy_meta.get("policy_source") or ""),
        "policy_validation_status": str(policy_meta.get("policy_validation_status") or ""),
        "policy_fallback_used": bool(policy_meta.get("policy_fallback_used")),
        "override_reason": str(policy_meta.get("override_reason") or ""),
        "applied_policy_present": bool(applied_policy),
    }
    strategist_output["policy_provenance"] = dict(provenance)
    strategist_output["scanner_bias_context"] = scanner_bias_context.to_dict()
    strategist_output["scanner_bias_summary"] = dict(scanner_bias_summary)
    strategist_output["scanner_memory_bias"] = dict(scanner_memory_bias)
    strategist_output["scanner_memory_bias_summary"] = dict(scanner_memory_bias_summary)
    strategist_output["monitor_memory_bias"] = dict(monitor_memory_bias)
    strategist_output["monitor_memory_bias_summary"] = dict(monitor_memory_bias_summary)
    strategist_output["commander_horizon_policy"] = dict(commander_horizon_policy)
    strategist_output["horizon_context"] = dict(horizon_context)
    if commander_entry_control:
        strategist_output["commander_entry_control"] = dict(commander_entry_control)
    state["strategist_output"] = _normalize_strategist_output_contract(strategist_output)
    state["strategy_policy"] = dict(strategy_policy)
    state["scanner_bias_context"] = scanner_bias_context.to_dict()
    state["scanner_memory_bias"] = dict(scanner_memory_bias)
    state["monitor_memory_bias"] = dict(monitor_memory_bias)
    return state


def _extract_commander_policy_vwap_ceiling(applied_policy: Dict[str, Any]) -> float:
    return _extract_commander_policy_vwap_ceiling_r3_impl(applied_policy,
        facade=_r3_sys.modules[__name__])


def _clamp_int(value: Any, default: int, lo: int, hi: int) -> int:
    try:
        parsed = int(float(value))
    except Exception:
        parsed = int(default)
    return int(max(lo, min(hi, parsed)))


def _dedupe_reason_list(value: Any, defaults: tuple[str, ...]) -> list[str]:
    return _dedupe_reason_list_r3_impl(value, defaults, facade=_r3_sys.modules[__name__])


def _extract_strategist_candidate_watch_policy(strategist_output: Dict[str, Any] | None) -> Dict[str, Any]:
    return _extract_strategist_candidate_watch_policy_r3_impl(strategist_output,
        facade=_r3_sys.modules[__name__])


def _normalize_candidate_watch_proposal_for_commander(
    raw: Dict[str, Any] | None,
    *,
    playbook: str = "",
    tactical_strategy: str = "",
) -> Dict[str, Any]:
    return _normalize_candidate_watch_proposal_for_commander_r3_impl(raw, playbook=playbook,
        tactical_strategy=tactical_strategy, facade=_r3_sys.modules[__name__])


def _candidate_watch_rank_cap(
    *,
    proposal: Dict[str, Any],
    market_regime: str,
    market_regime_rail: str = "",
    risk_mode: str,
    stress_flags: list[Any],
    resilience: Dict[str, Any],
) -> int:
    return _candidate_watch_rank_cap_r3_impl(proposal=proposal, market_regime=market_regime,
        market_regime_rail=market_regime_rail, risk_mode=risk_mode, stress_flags=stress_flags,
        resilience=resilience, facade=_r3_sys.modules[__name__])


def _apply_candidate_watch_proposal_to_entry_control(
    base: Dict[str, Any],
    proposal: Dict[str, Any],
    *,
    rank_cap: int,
    force_disable_cascade: bool = False,
    clamp_reason: str = "",
) -> Dict[str, Any]:
    return _apply_candidate_watch_proposal_to_entry_control_r3_impl(base, proposal,
        rank_cap=rank_cap, force_disable_cascade=force_disable_cascade, clamp_reason=clamp_reason,
        facade=_r3_sys.modules[__name__])


def _build_commander_entry_control(
    *,
    market_regime: str,
    market_regime_rail: str = "",
    risk_mode: str,
    open_position_count: int,
    preflight: Dict[str, Any],
    stress_flags: list[Any],
    resilience: Dict[str, Any],
    monitor_feedback: Dict[str, Any],
    applied_policy: Dict[str, Any],
    max_positions: int = 1,
    strategist_output: Dict[str, Any] | None = None,
    performance_circuit: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return _build_commander_entry_control_r3_impl(market_regime=market_regime,
        market_regime_rail=market_regime_rail, risk_mode=risk_mode,
        open_position_count=open_position_count, preflight=preflight, stress_flags=stress_flags,
        resilience=resilience, monitor_feedback=monitor_feedback, applied_policy=applied_policy,
        max_positions=max_positions, strategist_output=strategist_output,
        performance_circuit=performance_circuit, facade=_r3_sys.modules[__name__])


def _build_commander_decision(
    state: Dict[str, Any],
    *,
    mode_value: str,
    phase_value: str,
    status_value: str,
    path_value: str,
    reason_text: str = "",
) -> Dict[str, Any]:
    entry_capacity_available, market_regime, market_regime_rail, max_positions, open_position_count, preflight, rail_risk_off, resilience, risk_mode, runtime_fast_path, session_bias, shadow_assessment, strategist_fallback_used, strategist_output, stress_flags = decision_ctx_entry_capacity_available_market_regime(state=state, mode_value=mode_value, phase_value=phase_value, status_value=status_value, path_value=path_value, reason_text=reason_text, facade=_r3_sys.modules[__name__])

    allowed_playbooks: list[str]
    allowed_playbooks, applied_policy_meta, banned_playbooks, command_intent, flow_instruction, llm_policy, monitor_mission, no_trade_reason_code, observations, reporter_feedback_policy, scanner_mission, shadow_reason_summary, shadow_used, source_priority, source_refs, strategist_cache_preference_context, strategist_cache_preference_reason, strategist_cache_preferred, strategist_invocation, strategist_refresh_context, strategist_refresh_reason, strategist_refresh_requested = decision_policy_context(risk_mode=risk_mode, session_bias=session_bias, path_value=path_value, phase_value=phase_value, runtime_fast_path=runtime_fast_path, shadow_assessment=shadow_assessment, open_position_count=open_position_count, entry_capacity_available=entry_capacity_available, state=state, market_regime=market_regime, strategist_fallback_used=strategist_fallback_used, facade=_r3_sys.modules[__name__])
    if not applied_policy_meta:
        strategist_policy_present = bool(
            (isinstance(strategist_output.get("monitor_entry_policy"), dict) and strategist_output.get("monitor_entry_policy"))
            or (isinstance(state.get("monitor_entry_policy"), dict) and state.get("monitor_entry_policy"))
            or (
                isinstance((strategist_output.get("strategy_policy") or {}).get("monitor_policy"), dict)
                and ((strategist_output.get("strategy_policy") or {}).get("monitor_policy") or {}).get("entry_policy")
            )
        )
        if strategist_policy_present:
            applied_policy_meta = _resolve_commander_applied_policy(state)
    applied_policy, command_intent, commander_applied_policy_summary, commander_behavior_policy, commander_carry_risk_bias, commander_carry_risk_reason, commander_carry_state, commander_override, commander_session_open_recovery, flow_instruction, llm_policy, monitor_mission, observations, open_position_refresh_context, scanner_mission, session_bias, source_priority, source_refs, strategist_invocation, strategist_refresh_context, strategist_refresh_reason, strategist_refresh_requested = applied_policy_command_context(applied_policy_meta=applied_policy_meta, state=state, strategist_refresh_reason=strategist_refresh_reason, strategist_refresh_context=strategist_refresh_context, open_position_count=open_position_count, observations=observations, source_refs=source_refs, source_priority=source_priority, phase_value=phase_value, strategist_refresh_requested=strategist_refresh_requested, flow_instruction=flow_instruction, command_intent=command_intent, llm_policy=llm_policy, monitor_mission=monitor_mission, scanner_mission=scanner_mission, session_bias=session_bias, strategist_invocation=strategist_invocation, facade=_r3_sys.modules[__name__])
    memory_packets = load_commander_memory_packets(state=state)
    applied_policy, commander_horizon_policy, commander_memory_policy, decision_summary, horizon_context, intraday_performance_circuit, monitor_memory_bias, monitor_memory_bias_summary, observations, open_position_refresh_context, policy_sources, scanner_memory_bias, scanner_memory_bias_summary, source_priority, source_refs, strategist_refresh_context = decision_overlay_applied_policy_commander_horizon_policy(session_bias=session_bias, memory_packets=memory_packets, state=state, strategist_output=strategist_output, market_regime=market_regime, market_regime_rail=market_regime_rail, rail_risk_off=rail_risk_off, risk_mode=risk_mode, strategist_refresh_requested=strategist_refresh_requested, strategist_refresh_reason=strategist_refresh_reason, commander_carry_state=commander_carry_state, commander_carry_risk_bias=commander_carry_risk_bias, phase_value=phase_value, strategist_refresh_context=strategist_refresh_context, open_position_refresh_context=open_position_refresh_context, observations=observations, applied_policy=applied_policy, source_refs=source_refs, source_priority=source_priority, commander_behavior_policy=commander_behavior_policy, allowed_playbooks=allowed_playbooks, shadow_reason_summary=shadow_reason_summary, reason_text=reason_text, commander_override=commander_override, facade=_r3_sys.modules[__name__])
    if strategist_refresh_requested:
        decision_summary = (
            f"{decision_summary} Commander requested fresh strategist context "
            f"before rebuilding the entry frame ({strategist_refresh_reason or 'strategy_refresh'})."
        )
        refresh_summary = str(open_position_refresh_context.get("refresh_summary") or "").strip()
        if refresh_summary:
            decision_summary = f"{decision_summary} {refresh_summary}"
    elif strategist_invocation == "SKIP" and strategist_cache_preferred:
        decision_summary = (
            f"{decision_summary} Commander preferred cached strategist context "
            f"for this cycle ({strategist_cache_preference_reason or 'context_reuse'})."
        )
    cached_output_for_state, decision_summary, generated_epoch_for_state, strategist_call_decision, strategist_call_reason, strategist_skip_reason = decision_overlay_cached_output_for_state_decision_summary(commander_carry_risk_bias=commander_carry_risk_bias, commander_carry_risk_reason=commander_carry_risk_reason, decision_summary=decision_summary, commander_carry_state=commander_carry_state, commander_memory_policy=commander_memory_policy, strategist_invocation=strategist_invocation, strategist_refresh_requested=strategist_refresh_requested, strategist_refresh_reason=strategist_refresh_reason, strategist_cache_preferred=strategist_cache_preferred, strategist_cache_preference_reason=strategist_cache_preference_reason, open_position_count=open_position_count, entry_capacity_available=entry_capacity_available, max_positions=max_positions, state=state, facade=_r3_sys.modules[__name__])
    now_epoch_for_state = _runtime_now_epoch(state)
    cache_age_sec_for_state = max(0, now_epoch_for_state - generated_epoch_for_state) if generated_epoch_for_state > 0 else 10**9
    reuse_sec_for_state = max(0, _coerce_int(os.getenv("COMMANDER_STRATEGIST_CACHE_REUSE_SEC", "600"), 600))
    blocker_counts, monitor_last_states, recent_monitor_issues, strategist_invocation_mode, strategy_selection_mode, strategy_state = decision_overlay_blocker_counts_monitor_last_states(cache_age_sec_for_state=cache_age_sec_for_state, reuse_sec_for_state=reuse_sec_for_state, cached_output_for_state=cached_output_for_state, strategist_refresh_requested=strategist_refresh_requested, state=state, open_position_count=open_position_count, entry_capacity_available=entry_capacity_available, facade=_r3_sys.modules[__name__])
    for issue in recent_monitor_issues:
        issue_str = str(issue).strip()
        if issue_str:
            blocker_counts[issue_str] = blocker_counts.get(issue_str, 0) + 1
            
    avg_distance = 0.0
    total_wait = 0
    near_ready_count = 0
    
    for sym, m_state in monitor_last_states.items():
        if not isinstance(m_state, dict): continue
        posture = str(m_state.get("posture") or "").upper()
        if posture in ("WAIT", "HOLD"):
            reason = str(m_state.get("reason") or "")
            if reason:
                blocker_counts[reason] = blocker_counts.get(reason, 0) + 1
                
            entry_state = m_state.get("entry_state") if isinstance(m_state.get("entry_state"), dict) else {}
            score = _runtime_float(entry_state.get("transition_readiness_score"), 0.0)
            if score > 0:
                avg_distance += score
                total_wait += 1
            if score >= 0.7:
                near_ready_count += 1
                
    adaptive_feedback_allowed, adaptive_policy, entry_control, monitor_feedback, policy_adjustment_trace = decision_rules_adaptive_feedback_allowed_adaptive_polic(blocker_counts=blocker_counts, total_wait=total_wait, avg_distance=avg_distance, near_ready_count=near_ready_count, state=state, market_regime=market_regime, market_regime_rail=market_regime_rail, risk_mode=risk_mode, open_position_count=open_position_count, preflight=preflight, stress_flags=stress_flags, resilience=resilience, applied_policy=applied_policy, max_positions=max_positions, strategist_output=strategist_output, intraday_performance_circuit=intraday_performance_circuit, facade=_r3_sys.modules[__name__])

    if monitor_feedback["dominant_blocker"] and monitor_feedback["failure_streak"] >= 3 and adaptive_feedback_allowed:
        adaptive_policy["entry_bias_adjustment"] += 0.02
        adaptive_policy["scan_aggressiveness"] += 0.05
        policy_adjustment_trace.append(f"failure_streak>={monitor_feedback['failure_streak']} for {monitor_feedback['dominant_blocker']} -> increased entry_bias_adjustment and scan_aggressiveness")
    elif monitor_feedback["dominant_blocker"] and monitor_feedback["failure_streak"] >= 3:
        policy_adjustment_trace.append(
            f"failure_streak>={monitor_feedback['failure_streak']} for {monitor_feedback['dominant_blocker']} "
            f"-> preserved entry scope because entry_control={entry_control.get('mode')}"
        )

    if monitor_feedback["near_ready_flag"] and adaptive_feedback_allowed:
        adaptive_policy["entry_bias_adjustment"] += 0.015
        adaptive_policy["reentry_penalty_adjustment"] -= 0.02
        policy_adjustment_trace.append("near_ready_flag=True -> increased entry_bias_adjustment, decreased reentry_penalty_adjustment")

    if monitor_feedback["failure_streak"] >= 5 and adaptive_feedback_allowed:
        adaptive_policy["diversification_adjustment"] += 0.03
        policy_adjustment_trace.append(f"failure_streak>={monitor_feedback['failure_streak']} -> increased diversification_adjustment")
    if adaptive_feedback_allowed:
        adaptive_policy["scan_aggressiveness"] = max(
            float(adaptive_policy["scan_aggressiveness"]),
            float(entry_control.get("scan_aggressiveness_floor") or 0.0),
        )
    decision_summary, observations, scanner_policy, source_priority, source_refs = decision_rules_decision_summary_observations(policy_adjustment_trace=policy_adjustment_trace, entry_control=entry_control, adaptive_policy=adaptive_policy, adaptive_feedback_allowed=adaptive_feedback_allowed, observations=observations, open_position_count=open_position_count, max_positions=max_positions, source_refs=source_refs, source_priority=source_priority, decision_summary=decision_summary, facade=_r3_sys.modules[__name__])
    shadow_runtime = _ensure_commander_shadow_runtime(state)
    current_monitor_entry_policy_summary, prior_monitor_entry_policy_summary, strategist_refresh_context, strategist_refresh_effective, strategist_refresh_evaluated, strategist_refresh_policy_delta_fields = decision_rules_current_monitor_entry_policy_summary_pri(shadow_runtime=shadow_runtime, applied_policy=applied_policy, applied_policy_meta=applied_policy_meta, strategist_refresh_requested=strategist_refresh_requested, open_position_refresh_context=open_position_refresh_context, strategist_invocation=strategist_invocation, commander_override=commander_override, commander_carry_state=commander_carry_state, commander_carry_risk_bias=commander_carry_risk_bias, commander_carry_risk_reason=commander_carry_risk_reason, commander_session_open_recovery=commander_session_open_recovery, strategist_refresh_context=strategist_refresh_context, facade=_r3_sys.modules[__name__])

    return {
        "market_regime": market_regime,
        "market_regime_rail": market_regime_rail,
        "market_regime_forced_by_rail": rail_risk_off,
        "session_bias": session_bias,
        "risk_mode": risk_mode,
        "allowed_playbooks": list(allowed_playbooks),
        "banned_playbooks": list(banned_playbooks),
        "scanner_mission": scanner_mission,
        "monitor_mission": monitor_mission,
        "llm_policy": llm_policy,
        "llm_invocation_policy": llm_policy,
        "scanner_policy": dict(scanner_policy),
        "monitor_feedback": dict(monitor_feedback),
        "adaptive_policy": dict(adaptive_policy),
        "entry_control": dict(entry_control),
        "policy_adjustment_trace": list(policy_adjustment_trace),
        "command_intent": command_intent,
        "strategist_invocation": strategist_invocation,
        "strategist_invocation_mode": strategist_invocation_mode,
        "strategy_selection_mode": strategy_selection_mode,
        "strategy_state": strategy_state,
        "strategist_call_decision": strategist_call_decision,
        "strategist_call_reason": strategist_call_reason,
        "strategist_skip_reason": strategist_skip_reason,
        "flow_instruction": flow_instruction,
        "no_trade_reason_code": no_trade_reason_code,
        "observations": observations,
        "source_priority": source_priority,
        "source_refs": source_refs,
        "strategist_fallback_used": bool(strategist_fallback_used),
        "shadow_used": shadow_used,
        "shadow_assessment_summary": shadow_reason_summary,
        "strategist_refresh_requested": strategist_refresh_requested,
        "strategist_refresh_reason": strategist_refresh_reason,
        "strategist_refresh_context": dict(strategist_refresh_context),
        "open_position_refresh_context": dict(open_position_refresh_context),
        "strategist_refresh_evaluated": strategist_refresh_evaluated,
        "strategist_refresh_effective": strategist_refresh_effective,
        "strategist_refresh_policy_delta_fields": list(strategist_refresh_policy_delta_fields),
        "strategist_refresh_policy_delta_count": int(len(strategist_refresh_policy_delta_fields)),
        "carry_state": commander_carry_state,
        "carry_risk_bias": commander_carry_risk_bias,
        "carry_risk_reason": commander_carry_risk_reason,
        "session_open_recovery_assessment": dict(commander_session_open_recovery),
        "memory_packets": dict(memory_packets),
        "commander_memory_policy": dict(commander_memory_policy),
        "scanner_memory_bias": dict(scanner_memory_bias),
        "scanner_memory_bias_summary": dict(scanner_memory_bias_summary),
        "monitor_memory_bias": dict(monitor_memory_bias),
        "monitor_memory_bias_summary": dict(monitor_memory_bias_summary),
        "intraday_performance_circuit": dict(intraday_performance_circuit),
        "commander_horizon_policy": dict(commander_horizon_policy),
        "horizon_context": dict(horizon_context),
        "prior_monitor_entry_policy_summary": dict(prior_monitor_entry_policy_summary),
        "current_monitor_entry_policy_summary": dict(current_monitor_entry_policy_summary),
        "strategist_cache_preferred": bool(strategist_invocation == "SKIP" and strategist_cache_preferred),
        "strategist_cache_preference_reason": strategist_cache_preference_reason,
        "strategist_cache_preference_context": strategist_cache_preference_context,
        "decision_summary": decision_summary,
        "applied_policy": applied_policy,
        "policy_source": str(applied_policy_meta.get("policy_source") or ""),
        "policy_validation_status": str(applied_policy_meta.get("policy_validation_status") or ""),
        "policy_fallback_used": bool(applied_policy_meta.get("policy_fallback_used")),
        "policy_fallback_reason": str(applied_policy_meta.get("policy_fallback_reason") or ""),
        "policy_partial_normalized": bool(applied_policy_meta.get("policy_partial_normalized")),
        "policy_default_filled_fields": list(applied_policy_meta.get("policy_default_filled_fields") or []),
        "policy_validation_missing_fields": list(applied_policy_meta.get("policy_validation_missing_fields") or []),
        "policy_validation_invalid_fields": list(applied_policy_meta.get("policy_validation_invalid_fields") or []),
        "override_triggered": bool(commander_override.get("override_triggered")),
        "override_reason": str(
            commander_override.get("override_reason")
            or applied_policy_meta.get("override_reason")
            or ""
        ),
        "override_action": str(commander_override.get("override_action") or ""),
        "position_refresh_due": bool(commander_override.get("position_refresh_due")),
        "position_refresh_trigger": str(commander_override.get("position_refresh_trigger") or ""),
        "force_exit_review_pending": bool(commander_override.get("force_exit_review_pending")),
        "open_position_risk_review_reason": str(commander_override.get("open_position_risk_review_reason") or ""),
        "override_context": dict(commander_override),
        "applied_policy_source_chain": list(applied_policy_meta.get("applied_policy_source_chain") or []),
        "commander_applied_policy_summary": dict(commander_applied_policy_summary),
        "policy_sources": dict(policy_sources),
        "strategist_runtime_policy_source": "commander_applied_policy",
        "llm_policy_source": "commander_applied_policy",
        "llm_execution_profile_source": "commander_applied_policy",
        "reporter_policy_source": "commander_applied_policy",
        "monitor_policy_source": "commander_applied_policy",
        "scanner_policy_source": "commander_applied_policy",
        "execution_policy_source": "commander_applied_policy",
        "reporter_feedback_mode": str(reporter_feedback_policy.get("reporter_feedback_mode") or "auto"),
        "reporter_feedback_mode_source": str(reporter_feedback_policy.get("reporter_feedback_mode_source") or "default_auto"),
        "reporter_feedback_mode_reason": str(reporter_feedback_policy.get("reporter_feedback_mode_reason") or ""),
        "reporter_feedback_semantics": "advisory_only",
    }


def _ensure_commander_shadow_runtime(state: Dict[str, Any]) -> Dict[str, Any]:
    runtime = state.get("commander_shadow_runtime") if isinstance(state.get("commander_shadow_runtime"), dict) else {}
    runtime = dict(runtime)
    runtime.setdefault("strategist_executed", None)
    runtime.setdefault("strategist_called", None)
    runtime.setdefault("llm_called_by_strategist", None)
    runtime.setdefault("used_cached_strategist", False)
    runtime.setdefault("market_changed", None)
    runtime.setdefault("repeated_same_context", None)
    runtime.setdefault("retry_count_estimate", None)
    runtime.setdefault("monitor_decision", "")
    runtime.setdefault("executor_action", "")
    runtime.setdefault("executor_status", "")
    runtime.setdefault("pre_buy_refresh_requested", False)
    runtime.setdefault("pre_buy_refresh_reason", "")
    runtime.setdefault("pre_buy_refresh_context", {})
    runtime.setdefault("post_scanner_refresh_requested", False)
    runtime.setdefault("post_scanner_refresh_reason", "")
    runtime.setdefault("post_scanner_refresh_context", {})
    runtime.setdefault("prior_context", {})
    state["commander_shadow_runtime"] = runtime
    return runtime


def _reset_commander_shadow_runtime(state: Dict[str, Any]) -> None:
    state["commander_shadow_runtime"] = {
        "strategist_executed": None,
        "strategist_called": None,
        "llm_called_by_strategist": None,
        "used_cached_strategist": False,
        "market_changed": None,
        "repeated_same_context": None,
        "retry_count_estimate": None,
        "monitor_decision": "",
        "executor_action": "",
        "executor_status": "",
        "pre_buy_refresh_requested": False,
        "pre_buy_refresh_reason": "",
        "pre_buy_refresh_context": {},
        "post_scanner_refresh_requested": False,
        "post_scanner_refresh_reason": "",
        "post_scanner_refresh_context": {},
        "prior_context": {},
    }


def _strategist_shadow_fingerprint(output: Dict[str, Any]) -> Dict[str, Any]:
    return _strategist_shadow_fingerprint_r3_impl(output, facade=_r3_sys.modules[__name__])


def _shadow_market_changed(previous_output: Dict[str, Any], current_output: Dict[str, Any]) -> Optional[bool]:
    previous = _strategist_shadow_fingerprint(previous_output)
    current = _strategist_shadow_fingerprint(current_output)
    if not any(v not in (None, "", (), []) for v in previous.values()):
        return None
    return previous != current


def _shadow_text(value: Any, *, max_len: int = 120) -> str:
    text = str(value or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max(0, max_len - 3)] + "..."


def _shadow_float(value: Any) -> Optional[float]:
    return _shadow_float_r3_impl(value, facade=_r3_sys.modules[__name__])


def _shadow_selected_symbol(state: Dict[str, Any]) -> str:
    selected = state.get("selected") if isinstance(state.get("selected"), dict) else {}
    monitor_output = state.get("monitor_output") if isinstance(state.get("monitor_output"), dict) else {}
    return _shadow_text(selected.get("symbol") or monitor_output.get("selected_symbol"), max_len=24)


def _shadow_selected_score(state: Dict[str, Any]) -> Optional[float]:
    return _shadow_selected_score_r3_impl(state, facade=_r3_sys.modules[__name__])


def _seed_commander_shadow_prior_context(state: Dict[str, Any], *, prior_cached_output: Dict[str, Any]) -> None:
    return _seed_commander_shadow_prior_context_r3_impl(state,
        prior_cached_output=prior_cached_output, facade=_r3_sys.modules[__name__])


def _set_degrade_mode(state: Dict[str, Any], *, reason: str) -> None:
    resilience = state.get("resilience")
    if not isinstance(resilience, dict):
        resilience = {}
        state["resilience"] = resilience
    resilience["degrade_mode"] = True
    if not str(resilience.get("degrade_reason") or "").strip():
        resilience["degrade_reason"] = str(reason or "")


def _apply_commander_cooldown_guard(state: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], Dict[str, Any]]:
    """M23-4: apply incident/cooldown policy before running node path."""
    resilience = state.get("resilience") if isinstance(state.get("resilience"), dict) else {}
    threshold, cooldown_sec = _resolve_commander_cooldown_policy(state)
    now_epoch = _runtime_now_epoch(state)

    incident_count = max(0, _coerce_int(resilience.get("incident_count"), 0))
    cooldown_until = max(0, _coerce_int(resilience.get("cooldown_until_epoch"), 0))

    if cooldown_until > now_epoch:
        state["runtime_status"] = "cooldown_wait"
        state["runtime_transition"] = "cooldown"
        _set_degrade_mode(state, reason="commander_cooldown_active")
        return False, state, {
            "reason": "cooldown_active",
            "incident_count": incident_count,
            "incident_threshold": threshold,
            "cooldown_sec": cooldown_sec,
            "cooldown_until_epoch": cooldown_until,
            "now_epoch": now_epoch,
        }

    if threshold > 0 and cooldown_sec > 0 and incident_count >= threshold:
        cooldown_until = now_epoch + cooldown_sec
        resilience["cooldown_until_epoch"] = cooldown_until
        state["resilience"] = resilience
        state["runtime_status"] = "cooldown_wait"
        state["runtime_transition"] = "cooldown"
        _set_degrade_mode(state, reason="incident_threshold_cooldown")
        return False, state, {
            "reason": "incident_threshold_cooldown",
            "incident_count": incident_count,
            "incident_threshold": threshold,
            "cooldown_sec": cooldown_sec,
            "cooldown_until_epoch": cooldown_until,
            "now_epoch": now_epoch,
        }

    return True, state, {
        "reason": "cooldown_not_active",
        "incident_count": incident_count,
        "incident_threshold": threshold,
        "cooldown_sec": cooldown_sec,
        "cooldown_until_epoch": cooldown_until,
        "now_epoch": now_epoch,
    }


def _register_commander_incident(state: Dict[str, Any], *, error_type: str) -> Dict[str, Any]:
    """M23-4: increment incident counter and optionally open commander cooldown."""
    resilience = state.get("resilience") if isinstance(state.get("resilience"), dict) else {}
    now_epoch = _runtime_now_epoch(state)
    threshold, cooldown_sec = _resolve_commander_cooldown_policy(state)

    incident_count = max(0, _coerce_int(resilience.get("incident_count"), 0)) + 1
    resilience["incident_count"] = incident_count
    resilience["last_error_type"] = str(error_type or "")

    cooldown_until = max(0, _coerce_int(resilience.get("cooldown_until_epoch"), 0))
    if threshold > 0 and cooldown_sec > 0 and incident_count >= threshold:
        cooldown_until = max(cooldown_until, now_epoch + cooldown_sec)
        resilience["cooldown_until_epoch"] = cooldown_until
        _set_degrade_mode(state, reason="incident_threshold_cooldown")

    state["resilience"] = resilience
    return {
        "incident_count": incident_count,
        "incident_threshold": threshold,
        "cooldown_sec": cooldown_sec,
        "cooldown_until_epoch": cooldown_until,
        "last_error_type": str(error_type or ""),
    }


def _apply_operator_resume_intervention(state: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """M23-6: explicit operator intervention to resume runtime from cooldown/degrade."""
    transition = _normalize_transition(state.get("runtime_control"))
    if transition != "resume":
        return state, {}

    resilience = state.get("resilience") if isinstance(state.get("resilience"), dict) else {}
    before = {
        "degrade_mode": bool(resilience.get("degrade_mode")),
        "degrade_reason": str(resilience.get("degrade_reason") or ""),
        "incident_count": _coerce_int(resilience.get("incident_count"), 0),
        "cooldown_until_epoch": _coerce_int(resilience.get("cooldown_until_epoch"), 0),
        "last_error_type": str(resilience.get("last_error_type") or ""),
    }
    now_epoch = _runtime_now_epoch(state)

    resilience["degrade_mode"] = False
    resilience["degrade_reason"] = ""
    resilience["incident_count"] = 0
    resilience["cooldown_until_epoch"] = 0
    resilience["last_error_type"] = ""
    state["resilience"] = resilience

    return state, {
        "type": "operator_resume",
        "at_epoch": now_epoch,
        "before": before,
        "after": {
            "degrade_mode": False,
            "degrade_reason": "",
            "incident_count": 0,
            "cooldown_until_epoch": 0,
            "last_error_type": "",
        },
    }


def _apply_runtime_transition(state: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Apply runtime control transition.

    Supported controls in `state["runtime_control"]`:
      - cancel: stop run immediately
      - pause: stop run immediately
      - retry: increment retry counter and continue run
    """
    transition = _normalize_transition(state.get("runtime_control"))
    if not transition:
        return True, state

    state["runtime_transition"] = transition

    if transition == "cancel":
        state["runtime_status"] = "cancelled"
        return False, state

    if transition == "pause":
        state["runtime_status"] = "paused"
        return False, state

    if transition == "resume":
        state["runtime_status"] = "resuming"
        return True, state

    # retry: mark status and continue the selected runtime path.
    state["runtime_status"] = "retrying"
    state["runtime_retry_count"] = _coerce_int(state.get("runtime_retry_count"), 0) + 1
    return True, state


def _import_event_logger():
    for mod in ("libs.event_logger", "libs.logging.event_logger", "libs.core.event_logger"):
        try:
            m = __import__(mod, fromlist=["EventLogger", "new_run_id"])
            return getattr(m, "EventLogger"), getattr(m, "new_run_id")
        except Exception:
            continue
    from libs.core.event_logger import EventLogger, new_run_id  # type: ignore
    return EventLogger, new_run_id


def _ensure_run_id(state: Dict[str, Any]) -> str:
    _EventLogger, new_run_id = _import_event_logger()
    rid = str(state.get("run_id") or new_run_id())
    state["run_id"] = rid
    return rid


def _make_event_logger(state: Dict[str, Any]) -> Any:
    injected = state.get("event_logger")
    if injected is not None and hasattr(injected, "log"):
        return injected
    from libs.core.event_logger import EventLogger, resolve_event_log_path

    return EventLogger(log_path=resolve_event_log_path())


def _log_commander_event(state: Dict[str, Any], event: str, payload: Dict[str, Any]) -> None:
    try:
        logger = _make_event_logger(state)
        run_id = _ensure_run_id(state)
        logger.log(run_id=run_id, stage="commander_router", event=event, payload=payload)
    except Exception:
        return


def _resolve_reporter_agent(state: Dict[str, Any]) -> Any:
    injected = state.get("reporter_agent") or state.get("reporter")
    if injected is not None:
        return injected
    from libs.agent.reporter import Reporter

    return Reporter()


def _invoke_reporter_hook(
    state: Dict[str, Any],
    *,
    hook_name: str,
    hook_fn: Callable[..., Dict[str, Any]],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    try:
        result = hook_fn(
            enabled=True,
            emit_reports=bool(config.get("emit_reports")),
            event_log_path=str(config.get("event_log_path") or "data/logs/events.jsonl"),
            reports_root=str(config.get("reports_root") or "reports"),
            day=str(config.get("day") or ""),
        )
    except TypeError:
        # Some hook placeholders intentionally accept a smaller surface.
        result = hook_fn(
            enabled=True,
            day=str(config.get("day") or ""),
            reports_root=str(config.get("reports_root") or "reports"),
        )
    except Exception as exc:
        return {
            "hook_name": hook_name,
            "enabled": True,
            "status": "failed",
            "executed": False,
            "reason": f"hook_exception:{type(exc).__name__}",
            "report_only": True,
            "execution_authority": False,
            "route_override_authority": False,
            "threshold_override_authority": False,
            "warnings": [str(exc)],
        }
    return dict(result or {})


def _maybe_run_reporter_hooks(
    state: Dict[str, Any],
    *,
    mode_value: str,
    phase_value: str,
) -> Dict[str, Any]:
    config = _normalize_reporter_integration_config(state)
    if not bool(config.get("enabled")):
        return state

    reporter = _resolve_reporter_agent(state)
    requested_hooks: list[tuple[str, Callable[..., Dict[str, Any]]]] = []
    if str(phase_value or "").strip() == "session":
        if _reporter_hook_requested(config, "intraday_summary", default=True):
            requested_hooks.append(("intraday_summary", reporter.maybe_generate_intraday_summary))
    elif str(phase_value or "").strip() == "closeout":
        if _reporter_hook_requested(config, "eod_reports", default=True):
            requested_hooks.append(("eod_reports", reporter.maybe_generate_eod_reports))
        if _reporter_hook_requested(config, "strategist_feedback", default=True):
            requested_hooks.append(("strategist_feedback", reporter.maybe_generate_strategist_feedback))

    if not requested_hooks:
        return state

    results: Dict[str, Any] = {}
    for hook_name, hook_fn in requested_hooks:
        hook_result = _invoke_reporter_hook(state, hook_name=hook_name, hook_fn=hook_fn, config=config)
        hook_result.setdefault("hook_name", hook_name)
        hook_result.setdefault("report_only", True)
        hook_result.setdefault("execution_authority", False)
        hook_result.setdefault("route_override_authority", False)
        hook_result.setdefault("threshold_override_authority", False)
        hook_result.setdefault("mode", str(mode_value or ""))
        hook_result.setdefault("phase", str(phase_value or ""))
        results[hook_name] = hook_result
        _log_commander_event(
            state,
            "reporter_hook",
            {
                "hook_name": hook_name,
                "mode": str(mode_value or ""),
                "phase": str(phase_value or ""),
                "status": str(hook_result.get("status") or ""),
                "executed": bool(hook_result.get("executed")),
                "report_only": True,
                "execution_authority": False,
                "route_override_authority": False,
                "threshold_override_authority": False,
            },
        )

    state["reporter_hook_results"] = results
    state["reporter_hook_summary"] = {
        "enabled": True,
        "mode": str(mode_value or ""),
        "phase": str(phase_value or ""),
        "requested_hooks": [name for name, _ in requested_hooks],
        "emit_reports": bool(config.get("emit_reports")),
        "report_only": True,
        "execution_authority": False,
        "route_override_authority": False,
        "threshold_override_authority": False,
    }
    return state


def _portfolio_guard_event_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    return _portfolio_guard_event_summary_r3_impl(state, facade=_r3_sys.modules[__name__])


def _portfolio_preflight_event_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    return _portfolio_preflight_event_summary_r3_impl(state, facade=_r3_sys.modules[__name__])


def _extract_portfolio_snapshot_health(state: Dict[str, Any]) -> Dict[str, Any]:
    return _extract_portfolio_snapshot_health_r3_impl(state, facade=_r3_sys.modules[__name__])


def _portfolio_preflight_block_payload(state: Dict[str, Any]) -> Dict[str, Any]:
    return _portfolio_preflight_block_payload_r3_impl(state, facade=_r3_sys.modules[__name__])


def _allow_closeout_after_portfolio_preflight_block(
    state: Dict[str, Any],
    payload: Dict[str, Any],
    *,
    phase: RuntimePhase,
) -> Tuple[bool, Dict[str, Any]]:
    if phase != "session":
        return False, {}
    if not _is_trueish(os.getenv("COMMANDER_CLOSEOUT_PREFLIGHT_FALLBACK_ENABLED", "true")):
        return False, {"reason": "closeout_preflight_fallback_disabled"}
    if str(payload.get("reason") or "") not in {
        "portfolio_snapshot_reader_error",
        "portfolio_snapshot_positions_mismatch_unresolved",
    }:
        return False, {"reason": "preflight_reason_not_closeout_fallback_eligible"}
    persisted_positions_count = _coerce_int(payload.get("persisted_positions_count"), 0)
    if persisted_positions_count <= 0:
        return False, {"reason": "no_persisted_position_for_closeout_fallback"}

    closeout_active, closeout_payload = _should_use_session_closeout_fast_path(state)
    if not closeout_active:
        return False, {
            "reason": "outside_session_closeout_window",
            "closeout_guard": dict(closeout_payload or {}),
        }
    return True, {
        "reason": "session_closeout_preflight_fallback",
        "original_preflight_reason": str(payload.get("reason") or ""),
        "persisted_positions_count": persisted_positions_count,
        "reader_positions_count": _coerce_int(payload.get("reader_positions_count"), 0),
        "positions_source": str(payload.get("positions_source") or ""),
        "reconciliation_status": str(payload.get("reconciliation_status") or ""),
        "closeout_guard": dict(closeout_payload or {}),
    }


def _apply_portfolio_preflight_guard(state: Dict[str, Any], *, phase: RuntimePhase) -> Tuple[bool, Dict[str, Any]]:
    payload = _portfolio_preflight_block_payload(state)
    if not payload:
        state["portfolio_preflight"] = {
            "applied": True,
            "blocked": False,
            "phase": phase,
        }
        return True, state

    allow_closeout, fallback_payload = _allow_closeout_after_portfolio_preflight_block(
        state,
        payload,
        phase=phase,
    )
    if allow_closeout:
        state["portfolio_preflight"] = {
            **payload,
            "applied": True,
            "blocked": False,
            "phase": phase,
            "degraded": True,
            "closeout_fallback": dict(fallback_payload),
        }
        state["portfolio_preflight_closeout_fallback"] = dict(fallback_payload)
        return True, state

    state["portfolio_preflight"] = {
        "applied": True,
        "blocked": True,
        "phase": phase,
        **payload,
    }
    state["runtime_status"] = "preflight_blocked"
    state["path"] = "portfolio_preflight_guard"
    state["decision"] = "reject"
    state["intents"] = []
    state["selected"] = None
    state["execution"] = {
        "allowed": False,
        "ok": False,
        "reason": payload.get("reason"),
        "order": {"action": "NOOP"},
        "payload": {
            "mode": "preflight_guard",
            "reason_human": payload.get("reason_human"),
        },
    }
    return False, state


def _graph_spine_portfolio_preflight_enabled(state: Dict[str, Any], *, phase: RuntimePhase) -> bool:
    if phase != "session":
        return False
    if _is_trueish(state.get("disable_graph_spine_portfolio_preflight")):
        return False
    if _is_trueish(state.get("enable_graph_spine_portfolio_preflight")):
        return True
    return _is_trueish(os.getenv("COMMANDER_GRAPH_SPINE_PORTFOLIO_PREFLIGHT_ENABLED", ""))


def _run_graph_spine_with_preflight(
    state: Dict[str, Any],
    *,
    graph_runner: Callable[[Dict[str, Any]], Dict[str, Any]],
) -> Dict[str, Any]:
    from graphs.nodes.build_portfolio_snapshot import build_portfolio_snapshot

    state = build_portfolio_snapshot(state)
    snaps = state.get("snapshots") if isinstance(state.get("snapshots"), dict) else {}
    state["snapshots"] = {**dict(snaps or {}), "portfolio": state.get("portfolio_snapshot")}
    should_continue, state = _apply_portfolio_preflight_guard(state, phase="session")
    if not should_continue:
        return state
    return graph_runner(state)


def _intent_from_monitor_state(state: Dict[str, Any]) -> Dict[str, Any]:
    intents = state.get("intents")
    if not isinstance(intents, list) or not intents:
        return {"action": "NOOP", "reason": "no_monitor_intent"}

    it0 = intents[0] if isinstance(intents[0], dict) else {}
    meta = dict(it0.get("meta") or {}) if isinstance(it0.get("meta"), dict) else {}
    side = str(it0.get("side") or "BUY").strip().upper()
    action = "BUY" if side == "BUY" else "SELL" if side == "SELL" else "NOOP"
    symbol = str(it0.get("symbol") or state.get("symbol") or state.get("selected_symbol") or "").strip().upper()
    qty = max(0, _coerce_int(it0.get("qty"), 0))

    market = state.get("market_snapshot") if isinstance(state.get("market_snapshot"), dict) else {}
    price = it0.get("price")
    controlled_lane = isinstance(meta.get("controlled_mock_lane"), dict)
    if price in (None, "") and not controlled_lane:
        entry_metrics = meta.get("entry_metrics") if isinstance(meta.get("entry_metrics"), dict) else {}
        entry_cost_filter = meta.get("entry_cost_filter") if isinstance(meta.get("entry_cost_filter"), dict) else {}
        sizing = meta.get("sizing") if isinstance(meta.get("sizing"), dict) else {}
        monitor_entry = state.get("monitor_entry") if isinstance(state.get("monitor_entry"), dict) else {}
        monitor_entry_metrics = (
            monitor_entry.get("metrics") if isinstance(monitor_entry.get("metrics"), dict) else {}
        )
        monitor_entry_cost_filter = (
            monitor_entry.get("entry_cost_filter")
            if isinstance(monitor_entry.get("entry_cost_filter"), dict)
            else {}
        )
        monitor_output = state.get("monitor_output") if isinstance(state.get("monitor_output"), dict) else {}
        for candidate in (
            meta.get("price"),
            meta.get("current_price"),
            meta.get("raw_price"),
            meta.get("quote_price"),
            meta.get("market_price"),
            entry_cost_filter.get("price"),
            entry_metrics.get("current_price"),
            entry_metrics.get("price"),
            sizing.get("price"),
            monitor_entry_cost_filter.get("price"),
            monitor_entry_metrics.get("current_price"),
            monitor_entry_metrics.get("price"),
            monitor_output.get("current_price"),
            monitor_output.get("price"),
            monitor_output.get("exit_raw_price"),
            market.get("price"),
        ):
            if candidate not in (None, "") and _runtime_float(candidate, 0.0) > 0.0:
                price = candidate
                break

    return {
        "action": action,
        "symbol": symbol,
        "qty": qty,
        "price": price,
        "order_type": "limit",
        "order_api_id": "ORDER_SUBMIT",
        "rationale": str(it0.get("thesis") or "monitor_intent"),
        "meta": meta,
    }


def _build_packet_from_state(state: Dict[str, Any], *, intent: Dict[str, Any]) -> Dict[str, Any]:
    risk = state.get("risk_context") if isinstance(state.get("risk_context"), dict) else {}
    exec_context = state.get("exec_context") if isinstance(state.get("exec_context"), dict) else {}
    packet = {
        "intent": dict(intent),
        "risk": dict(risk),
        "exec_context": dict(exec_context),
    }
    strategy_policy = state.get("strategy_policy") if isinstance(state.get("strategy_policy"), dict) else {}
    if strategy_policy:
        packet["strategy_policy"] = dict(strategy_policy)
    return packet


def _strategist_frame_blocked(state: Dict[str, Any]) -> bool:
    if bool(state.get("strategist_blocked")):
        return True
    strategist_output = state.get("strategist_output") if isinstance(state.get("strategist_output"), dict) else {}
    strategist_llm = state.get("strategist_llm") if isinstance(state.get("strategist_llm"), dict) else {}
    return bool(strategist_output.get("llm_frame_blocked")) or bool(strategist_llm.get("blocked"))


def _apply_strategist_block(state: Dict[str, Any], *, phase: str) -> Dict[str, Any]:
    reason = str(
        state.get("strategist_blocked_reason")
        or ((state.get("strategist_output") or {}).get("llm_frame_blocked_reason") if isinstance(state.get("strategist_output"), dict) else "")
        or ((state.get("strategist_llm") or {}).get("blocked_reason") if isinstance(state.get("strategist_llm"), dict) else "")
        or "strategist_llm_failed"
    )
    payload = {"path": "strategist_llm_blocked", "phase": phase, "reason": reason}
    _log_commander_event(state, "fast_path", payload)
    state["runtime_status"] = "blocked"
    state["path"] = f"{phase}_strategist_blocked"
    state["decision"] = "noop"
    state["decision_reason"] = reason
    return state


def _portfolio_open_position_count(state: Dict[str, Any]) -> int:
    return _portfolio_open_position_count_r3_impl(state, facade=_r3_sys.modules[__name__])


def _portfolio_open_position_symbols(state: Dict[str, Any]) -> list[str]:
    return _portfolio_open_position_symbols_r3_impl(state, facade=_r3_sys.modules[__name__])


def _portfolio_open_position_row(state: Dict[str, Any], symbol: str) -> Dict[str, Any]:
    return _portfolio_open_position_row_r3_impl(state, symbol, facade=_r3_sys.modules[__name__])


def _open_position_focus_sort_key(item: Dict[str, Any]) -> tuple[int, int, int, int, float, float, int, int, str]:
    return _open_position_focus_sort_key_r3_impl(item, facade=_r3_sys.modules[__name__])


def _select_open_position_focus_symbol(state: Dict[str, Any], fallback_symbols: list[str] | None = None) -> str:
    return _select_open_position_focus_symbol_r3_impl(state, fallback_symbols,
        facade=_r3_sys.modules[__name__])


def _normalize_order_symbol(value: Any) -> str:
    raw = str(value or "").strip().upper()
    if raw.startswith("A") and len(raw) == 7 and raw[1:].isdigit():
        raw = raw[1:]
    return raw if raw.isdigit() and len(raw) == 6 else ""


def _order_row_side(row: Dict[str, Any]) -> str:
    return _order_row_side_r3_impl(row, facade=_r3_sys.modules[__name__])


def _pending_buy_cancel_intents_from_account_orders(state: Dict[str, Any]) -> list[Dict[str, Any]]:
    return _pending_buy_cancel_intents_from_account_orders_r3_impl(state,
        facade=_r3_sys.modules[__name__])


def _hydrate_closeout_account_orders(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from graphs.nodes.skill_contracts import extract_account_orders_rows

        rows, meta = extract_account_orders_rows(state)
        if rows or bool(meta.get("present")):
            return state
    except Exception:
        return state

    try:
        from graphs.nodes.hydrate_skill_results_node import hydrate_skill_results_node
    except Exception:
        return state

    previous_auto = state.get("auto_skill_runner")
    previous_candidates = state.get("candidates")
    had_candidates = "candidates" in state
    state["auto_skill_runner"] = True
    state["candidates"] = []
    try:
        state = hydrate_skill_results_node(state)
    except Exception:
        return state
    finally:
        if previous_auto is None:
            state.pop("auto_skill_runner", None)
        else:
            state["auto_skill_runner"] = previous_auto
        if had_candidates:
            state["candidates"] = previous_candidates
        else:
            state.pop("candidates", None)
    return state


def _normalize_position_ratio(value: Any) -> float | None:
    if value in (None, ""):
        return None
    ratio = _runtime_float(value, 0.0)
    return float(ratio)


def _resolve_profit_protection_activation_ratio(state: Dict[str, Any]) -> float:
    return _resolve_profit_protection_activation_ratio_r3_impl(state,
        facade=_r3_sys.modules[__name__])


def _position_current_profit_ratio(
    *,
    raw_price_ratio: float | None,
    account_pnl_ratio: float | None,
    price_anomaly: bool,
) -> float | None:
    return _position_current_profit_ratio_r3_impl(raw_price_ratio=raw_price_ratio,
        account_pnl_ratio=account_pnl_ratio, price_anomaly=price_anomaly,
        facade=_r3_sys.modules[__name__])


def _assess_open_position_commander_override(state: Dict[str, Any]) -> Dict[str, Any]:
    anomaly_found, last_exit_sweep_by_symbol, max_hold_repeat, min_effective_loss_ratio, monitor_last_state, next_hold_counts, next_refresh_cooldowns, overnight_decisions, persisted, position_peak_price, position_strategy_context, prior_hold_counts, prior_refresh_cooldowns, profit_activation_ratio, reasons, repeated_hold_rows, risk_found, rows, rows_summary = open_pos_input_anomaly_found_last_exit_sweep_by_symbol(state=state, facade=_r3_sys.modules[__name__])
    now_epoch = _runtime_now_epoch(state)

    for row in rows:
        if not isinstance(row, dict):
            continue
        qty = max(0, _coerce_int(row.get("qty"), 0))
        if qty <= 0:
            continue
        symbol = str(row.get("symbol") or "").strip().upper()
        if not symbol:
            continue

        avg_price = _runtime_float(row.get("avg_price"), 0.0)
        current_price = _runtime_float(
            row.get("current_price")
            if row.get("current_price") not in (None, "")
            else row.get("price"),
            0.0,
        )
        unrealized_pnl = _runtime_float(row.get("unrealized_pnl"), 0.0)
        account_pnl_ratio = _normalize_position_ratio(row.get("account_pnl_ratio"))
        account_mark_price = 0.0
        price_anomaly = False
        price_anomaly_reason = ""
        if account_pnl_ratio is not None and avg_price > 0.0:
            account_mark_price = float(avg_price * (1.0 + float(account_pnl_ratio)))
            if current_price > 0.0 and account_mark_price > 0.0:
                mark_ratio = float(account_mark_price / current_price)
                if mark_ratio < 0.5:
                    price_anomaly = True
                    price_anomaly_reason = f"account_mark_below_reference_ratio:{mark_ratio:.4f}"
                elif mark_ratio > 1.5:
                    price_anomaly = True
                    price_anomaly_reason = f"account_mark_above_reference_ratio:{mark_ratio:.4f}"

        candidate_loss_ratios, current_profit_ratio, effective_loss_ratio, raw_loss_ratio, unrealized_loss_ratio = open_pos_input_candidate_loss_ratios_current_profit_rat(current_price=current_price, avg_price=avg_price, qty=qty, unrealized_pnl=unrealized_pnl, account_pnl_ratio=account_pnl_ratio, price_anomaly=price_anomaly, facade=_r3_sys.modules[__name__])
        peak_price = max(
            _runtime_float(row.get("peak_price"), 0.0),
            _runtime_float(row.get("high_water_mark"), 0.0),
            _runtime_float(position_peak_price.get(symbol), 0.0) if isinstance(position_peak_price, dict) else 0.0,
            current_price,
            avg_price,
        )
        anomaly_found, hold_repeat_count, horizon_review_due, horizon_revision_allowed, last_exit_sweep_epoch, max_hold_repeat, min_effective_loss_ratio, peak_profit_ratio, position_age_seconds, previous, previous_active_exit_axis, previous_entry_state, previous_posture, previous_reason, profit_giveback_ratio, profit_protection_priority, refresh_cooldown_until, risk_found, symbol_strategy_context = open_pos_input_anomaly_found_hold_repeat_count(peak_price=peak_price, avg_price=avg_price, current_profit_ratio=current_profit_ratio, profit_activation_ratio=profit_activation_ratio, symbol=symbol, last_exit_sweep_by_symbol=last_exit_sweep_by_symbol, monitor_last_state=monitor_last_state, prior_hold_counts=prior_hold_counts, next_hold_counts=next_hold_counts, max_hold_repeat=max_hold_repeat, prior_refresh_cooldowns=prior_refresh_cooldowns, now_epoch=now_epoch, next_refresh_cooldowns=next_refresh_cooldowns, effective_loss_ratio=effective_loss_ratio, min_effective_loss_ratio=min_effective_loss_ratio, price_anomaly=price_anomaly, reasons=reasons, price_anomaly_reason=price_anomaly_reason, repeated_hold_rows=repeated_hold_rows, state=state, row=row, position_strategy_context=position_strategy_context, anomaly_found=anomaly_found, risk_found=risk_found, facade=_r3_sys.modules[__name__])
        position_horizon_state = ensure_horizon_state(
            symbol_strategy_context
        )
        carry_control = open_pos_assess_carry_control(state=state, symbol=symbol, position_age_seconds=position_age_seconds, effective_loss_ratio=effective_loss_ratio, previous_reason=previous_reason, previous_active_exit_axis=previous_active_exit_axis, previous_entry_state=previous_entry_state, hold_repeat_count=hold_repeat_count, overnight_decisions=overnight_decisions, reasons=reasons, rows_summary=rows_summary, raw_loss_ratio=raw_loss_ratio, current_profit_ratio=current_profit_ratio, peak_profit_ratio=peak_profit_ratio, profit_giveback_ratio=profit_giveback_ratio, account_pnl_ratio=account_pnl_ratio, qty=qty, peak_price=peak_price, profit_protection_priority=profit_protection_priority, profit_activation_ratio=profit_activation_ratio, last_exit_sweep_epoch=last_exit_sweep_epoch, price_anomaly=price_anomaly, price_anomaly_reason=price_anomaly_reason, horizon_review_due=horizon_review_due, horizon_revision_allowed=horizon_revision_allowed, position_horizon_state=position_horizon_state, previous_posture=previous_posture, refresh_cooldown_until=refresh_cooldown_until, now_epoch=now_epoch, facade=_r3_sys.modules[__name__])[0]

    if next_hold_counts:
        persisted["commander_open_position_hold_repeat_by_symbol"] = dict(next_hold_counts)
    elif "commander_open_position_hold_repeat_by_symbol" in persisted:
        persisted.pop("commander_open_position_hold_repeat_by_symbol", None)

    closeout_unresolved_found = any(
        bool(row.get("closeout_unresolved_flatten_required")) for row in rows_summary if isinstance(row, dict)
    )
    horizon_review_found = any(
        bool(row.get("horizon_review_due")) for row in rows_summary if isinstance(row, dict)
    )
    force_exit_review_pending, open_position_risk_review_reason, override_action, override_reason, override_suppressed, override_suppressed_reason, override_triggered, position_refresh_due, position_refresh_trigger, refresh_cooldown_remaining_sec, refresh_cooldown_symbol, refresh_cooldown_until, strategist_refresh_context = open_pos_assess_force_exit_review_pending_open_position(closeout_unresolved_found=closeout_unresolved_found, anomaly_found=anomaly_found, risk_found=risk_found, horizon_review_found=horizon_review_found, max_hold_repeat=max_hold_repeat, facade=_r3_sys.modules[__name__])

    def _row_loss_value(item: Dict[str, Any]) -> float:
        value = item.get("effective_loss_ratio")
        return float(_runtime_float(value, 0.0)) if value not in (None, "") else 0.0

    def _row_refresh_cooldown_remaining(item: Dict[str, Any]) -> int:
        cooldown_until = max(0, _coerce_int(item.get("refresh_cooldown_until"), 0))
        return max(0, int(cooldown_until - now_epoch)) if cooldown_until > now_epoch else 0

    def _select_open_position_refresh_candidate(*, require_loss: bool) -> Dict[str, Any]:
        candidates = []
        for item in rows_summary:
            if not isinstance(item, dict):
                continue
            if not bool(item.get("horizon_revision_allowed", True)):
                continue
            if (
                _coerce_int(item.get("hold_repeat_count"), 0) < 3
                and not bool(item.get("horizon_review_due"))
            ):
                continue
            if require_loss and _row_loss_value(item) > -0.01:
                continue
            candidates.append(item)
        if not candidates:
            return {}
        return dict(
            sorted(
                candidates,
                key=lambda item: (
                    1 if _row_refresh_cooldown_remaining(item) > 0 else 0,
                    _row_loss_value(item) if require_loss else -_coerce_int(item.get("hold_repeat_count"), 0),
                    -_coerce_int(item.get("hold_repeat_count"), 0) if require_loss else _row_loss_value(item),
                    str(item.get("symbol") or ""),
                ),
            )[0]
        )

    if override_triggered:
        if closeout_unresolved_found:
            override_action = "force_exit_review"
            override_reason = "closeout_unresolved_flatten_required"
            force_exit_review_pending = True
            open_position_risk_review_reason = "closeout_unresolved_flatten_required"
            position_refresh_trigger = "closeout_unresolved_flatten_required"
        elif anomaly_found:
            override_action = "force_exit_review"
            override_reason = "price_pnl_anomaly"
        else:
            force_exit_review_pending, open_position_risk_review_reason, override_action, override_reason, override_suppressed, override_suppressed_reason, override_triggered, position_refresh_due, position_refresh_trigger, refresh_cooldown_remaining_sec, refresh_cooldown_symbol, refresh_cooldown_until, strategist_refresh_context = open_pos_assess_force_exit_review_pending_open_position_2(risk_found=risk_found, _select_open_position_refresh_candidate=_select_open_position_refresh_candidate, now_epoch=now_epoch, reasons=reasons, refresh_cooldown_remaining_sec=refresh_cooldown_remaining_sec, next_refresh_cooldowns=next_refresh_cooldowns, max_hold_repeat=max_hold_repeat, min_effective_loss_ratio=min_effective_loss_ratio, anomaly_found=anomaly_found, rows_summary=rows_summary, force_exit_review_pending=force_exit_review_pending, open_position_risk_review_reason=open_position_risk_review_reason, override_action=override_action, override_reason=override_reason, override_suppressed=override_suppressed, override_suppressed_reason=override_suppressed_reason, override_triggered=override_triggered, position_refresh_due=position_refresh_due, position_refresh_trigger=position_refresh_trigger, strategist_refresh_context=strategist_refresh_context, facade=_r3_sys.modules[__name__])

    if next_refresh_cooldowns:
        persisted["commander_open_position_refresh_cooldown_until_by_symbol"] = dict(next_refresh_cooldowns)
    elif "commander_open_position_refresh_cooldown_until_by_symbol" in persisted:
        persisted.pop("commander_open_position_refresh_cooldown_until_by_symbol", None)
    state["persisted_state"] = persisted
    carry_focus = (
        sorted(
            rows_summary,
            key=_open_position_focus_sort_key,
        )[0]
        if rows_summary
        else {}
    )

    return {
        "override_triggered": bool(override_triggered),
        "override_reason": str(override_reason),
        "override_action": str(override_action),
        "override_suppressed": bool(override_suppressed),
        "override_suppressed_reason": str(override_suppressed_reason),
        "reason_chain": list(reasons[:8]),
        "hold_repeat_count_max": int(max_hold_repeat),
        "effective_loss_ratio_min": min_effective_loss_ratio,
        "price_anomaly_flag": bool(anomaly_found),
        "closeout_unresolved_flatten_required": bool(closeout_unresolved_found),
        "refresh_cooldown_sec": int(_OPEN_POSITION_STRATEGIST_REFRESH_COOLDOWN_SEC),
        "refresh_cooldown_symbol": str(refresh_cooldown_symbol),
        "refresh_cooldown_until": int(refresh_cooldown_until) if refresh_cooldown_until > 0 else None,
        "refresh_cooldown_remaining_sec": int(refresh_cooldown_remaining_sec),
        "position_refresh_due": bool(position_refresh_due),
        "position_refresh_trigger": str(position_refresh_trigger),
        "force_exit_review_pending": bool(force_exit_review_pending),
        "open_position_risk_review_reason": str(open_position_risk_review_reason),
        "strategist_refresh_context": dict(strategist_refresh_context),
        "carry_state": str(carry_focus.get("carry_state") or ""),
        "carry_risk_bias": str(carry_focus.get("carry_risk_bias") or ""),
        "carry_risk_reason": str(carry_focus.get("carry_risk_reason") or ""),
        "session_open_recovery_assessment": dict(carry_focus.get("session_open_recovery_assessment") or {}),
        "policy_source": "commander_open_position_override",
        "positions": rows_summary,
    }


def _hydrate_monitor_symbol_features(state: Dict[str, Any]) -> Dict[str, Any]:
    held_symbols = _portfolio_open_position_symbols(state)
    if not held_symbols:
        state["monitor_feature_hydration"] = {
            "applied": False,
            "symbol_count": 0,
            "source": "none",
            "errors": [],
        }
        return state

    from graphs.nodes.skill_contracts import extract_market_quotes
    from libs.runtime.scanner_feature_hydration import hydrate_scanner_feature_map

    policy = state.get("policy") if isinstance(state.get("policy"), dict) else {}
    skill_quotes, _quote_meta = extract_market_quotes(state)
    feature_map, feature_source, feature_errors = hydrate_scanner_feature_map(
        state=state,
        candidates=[{"symbol": symbol} for symbol in held_symbols],
        skill_quotes=skill_quotes,
        policy=policy,
        refresh_existing=True,
    )
    state["monitor_feature_hydration"] = {
        "applied": True,
        "symbol_count": int(len(held_symbols)),
        "source": str(feature_source or "none"),
        "feature_symbol_count": int(len(feature_map)),
        "errors": list(feature_errors),
        "symbols": list(held_symbols),
    }
    return state


def _should_use_monitor_only_fast_path(state: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    return _should_use_monitor_only_fast_path_r3_impl(state, facade=_r3_sys.modules[__name__])


def _mark_pre_entry_exit_sweep_checked(state: Dict[str, Any], symbol: str) -> None:
    normalized = str(symbol or "").strip().upper()
    if not normalized:
        return
    persisted = state.get("persisted_state") if isinstance(state.get("persisted_state"), dict) else {}
    checked = (
        dict(persisted.get("commander_pre_entry_exit_sweep_last_checked_by_symbol") or {})
        if isinstance(persisted.get("commander_pre_entry_exit_sweep_last_checked_by_symbol"), dict)
        else {}
    )
    checked[normalized] = int(_runtime_now_epoch(state))
    persisted["commander_pre_entry_exit_sweep_last_checked_by_symbol"] = checked
    state["persisted_state"] = persisted


def _restore_pre_entry_exit_sweep_transients(
    state: Dict[str, Any],
    snapshot: Dict[str, Any],
    keys: tuple[str, ...],
) -> Dict[str, Any]:
    for key in keys:
        if key in snapshot:
            state[key] = snapshot[key]
        else:
            state.pop(key, None)
    return state


def _run_pre_entry_exit_sweep(
    state: Dict[str, Any],
    *,
    monitor_node_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
    decision_node_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
    execute_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
    emit_trade_report_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
    update_state_after_execution_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
    shadow_runtime: Dict[str, Any],
) -> Tuple[Dict[str, Any], bool]:
    if not _commander_pre_entry_exit_sweep_enabled(state):
        state["commander_pre_entry_exit_sweep"] = {"enabled": False, "reason": "disabled"}
        return state, False
    held_symbols = _portfolio_open_position_symbols(state)
    if not held_symbols:
        state["commander_pre_entry_exit_sweep"] = {"enabled": True, "reason": "no_open_position"}
        return state, False

    assessment = state.get("commander_open_position_override") if isinstance(state.get("commander_open_position_override"), dict) else {}
    if not isinstance(assessment.get("positions"), list) or not assessment.get("positions"):
        state["commander_open_position_override"] = dict(_assess_open_position_commander_override(state))
    focus_symbol = _select_open_position_focus_symbol(state, fallback_symbols=held_symbols)
    if not focus_symbol:
        state["commander_pre_entry_exit_sweep"] = {"enabled": True, "reason": "no_focus_symbol"}
        return state, False

    restore_keys = _PRE_ENTRY_EXIT_SWEEP_TRANSIENT_KEYS + ("runtime_fast_path", "commander_decision")
    restore_snapshot = {key: state[key] for key in restore_keys if key in state}
    sweep_payload = {
        "enabled": True,
        "reason": "pre_entry_open_position_exit_check",
        "focus_symbol": str(focus_symbol),
        "held_symbols": list(held_symbols),
        "open_position_count": int(len(held_symbols)),
        "max_positions": int(_resolve_risk_max_positions(state)),
        "result": "pending",
    }
    state["commander_pre_entry_exit_sweep"] = dict(sweep_payload)
    state["runtime_fast_path"] = dict(sweep_payload)
    state["commander_decision"] = _build_commander_decision(
        state,
        mode_value="integrated_chain",
        phase_value=str(state.get("runtime_phase") or "session"),
        status_value=str(state.get("runtime_status") or "planning"),
        path_value="integrated_chain_pre_entry_exit_sweep",
        reason_text="pre_entry_open_position_exit_check",
    )
    state["selected"] = {
        "symbol": focus_symbol,
        "_monitor_synthetic_selected": True,
        "_pre_entry_exit_sweep_selected": True,
    }
    state.pop("scanner_output", None)
    _log_commander_event(
        state,
        "pre_entry_exit_sweep",
        {"path": "integrated_chain_pre_entry_exit_sweep", **dict(sweep_payload)},
    )

    state = _hydrate_monitor_symbol_features(state)
    state = monitor_node_fn(state)
    monitor_output = state.get("monitor_output") if isinstance(state.get("monitor_output"), dict) else {}
    monitor_decision = str(monitor_output.get("intent_side") or "NOOP")
    shadow_runtime["pre_entry_exit_sweep_monitor_decision"] = monitor_decision
    state = decision_node_fn(state)
    decision = str(state.get("decision") or "").strip().lower()
    intent = _intent_from_monitor_state(state)
    action = str(intent.get("action") or "").strip().upper()
    forced_closeout_exit = bool(_is_closeout_unresolved_flatten_symbol(state, focus_symbol))
    if forced_closeout_exit and action != "SELL":
        position_row = _portfolio_open_position_row(state, focus_symbol)
        forced_qty = max(0, _coerce_int(position_row.get("qty"), 0))
        market_snapshot = state.get("market_snapshot") if isinstance(state.get("market_snapshot"), dict) else {}
        forced_price = (
            position_row.get("current_price")
            or position_row.get("price")
            or position_row.get("last_price")
            or market_snapshot.get("price")
        )
        if forced_qty > 0:
            intent = {
                "action": "SELL",
                "side": "SELL",
                "symbol": str(focus_symbol),
                "qty": forced_qty,
                "price": forced_price,
                "order_type": "market",
                "reason": "closeout_unresolved_flatten_required",
                "meta": {
                    "source": "commander_pre_entry_exit_sweep",
                    "forced_by": "closeout_unresolved_flatten_required",
                    "monitor_decision": monitor_decision,
                    "decision_before_override": decision,
                },
            }
            state["intents"] = [dict(intent)]
            state["decision"] = "approve"
            decision = "approve"
            action = "SELL"
            shadow_runtime["pre_entry_exit_sweep_forced_closeout_exit"] = True
            shadow_runtime["pre_entry_exit_sweep_forced_closeout_reason"] = "closeout_unresolved_flatten_required"
    _mark_pre_entry_exit_sweep_checked(state, focus_symbol)

    state["commander_pre_entry_exit_sweep"] = {
        **dict(sweep_payload),
        "monitor_decision": monitor_decision,
        "decision": str(decision or ""),
        "intent_action": action,
        "forced_closeout_exit": bool(forced_closeout_exit and action == "SELL"),
    }
    if decision == "approve" and action == "SELL":
        state["decision_packet"] = _build_packet_from_state(state, intent=intent)
        state = execute_fn(state)
        shadow_runtime["monitor_decision"] = monitor_decision
        shadow_runtime["executor_action"] = str(
            (((state.get("execution") or {}).get("order") or {}).get("action") or action or "")
        )
        shadow_runtime["executor_status"] = str(
            ((state.get("execution") or {}).get("reason") or ((state.get("execution") or {}).get("ok_source") or ""))
        )
        state = emit_trade_report_fn(state)
        state = update_state_after_execution_fn(state)
        state["commander_pre_entry_exit_sweep"] = {
            **dict(state.get("commander_pre_entry_exit_sweep") or {}),
            "result": "executed_exit",
        }
        state["path"] = "integrated_chain_pre_entry_exit_sweep"
        return state, True

    state["commander_pre_entry_exit_sweep"] = {
        **dict(state.get("commander_pre_entry_exit_sweep") or {}),
        "result": "no_exit_signal" if action in {"", "NOOP"} else "non_sell_intent_ignored",
    }
    state = _restore_pre_entry_exit_sweep_transients(state, restore_snapshot, restore_keys)
    return state, False


def _should_use_session_closeout_fast_path(state: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    return _should_use_session_closeout_fast_path_r3_impl(state, facade=_r3_sys.modules[__name__])


def _build_stage4_carry_review_context(
    state: Dict[str, Any],
    override_assessment: Dict[str, Any],
    *,
    review_reason: str,
) -> Dict[str, Any]:
    return _build_stage4_carry_review_context_r3_impl(state, override_assessment,
        review_reason=review_reason, facade=_r3_sys.modules[__name__])


def _force_stage4_carry_review_decision(
    state: Dict[str, Any],
    commander_decision: Dict[str, Any],
    *,
    review_reason: str,
) -> Dict[str, Any]:
    return _force_stage4_carry_review_decision_r3_impl(state, commander_decision,
        review_reason=review_reason, facade=_r3_sys.modules[__name__])


def _run_stage4_carry_review(
    state: Dict[str, Any],
    strategist_node: Callable[[Dict[str, Any]], Dict[str, Any]],
    *,
    review_reason: str,
    phase: str,
) -> Tuple[Dict[str, Any], bool]:
    if _portfolio_open_position_count(state) <= 0:
        write_llm_stage_skip_entry(state, call_kind="end_of_day_carry_review", reason="no_open_position")
        return state, False
    base_decision = state.get("commander_decision") if isinstance(state.get("commander_decision"), dict) else {}
    stage4_decision = _force_stage4_carry_review_decision(
        state,
        base_decision,
        review_reason=review_reason,
    )
    if not bool(stage4_decision.get("strategist_refresh_requested")):
        write_llm_stage_skip_entry(state, call_kind="end_of_day_carry_review", reason="no_rule_candidate")
        return state, False
    state["commander_decision"] = dict(stage4_decision)
    state = _attach_commander_reporter_feedback_policy(state, selected_route="full_cycle", phase=phase)
    state = _attach_commander_applied_policy(state)
    state = strategist_node(state)
    state = _attach_commander_applied_policy(state)
    state = _maybe_run_post_exit_shadow_recap_runtime(state, trigger="stage4_carry_review")
    return state, True


def _record_absent_later_stage_llm_reviews(state: Dict[str, Any]) -> None:
    try:
        if _portfolio_open_position_count(state) > 0:
            write_llm_stage_skip_entry(
                state,
                call_kind="stale_intraday_hold_review",
                reason="not_due_this_cycle",
            )
            phase = str(state.get("runtime_phase") or "").strip().lower()
            write_llm_stage_skip_entry(
                state,
                call_kind="end_of_day_carry_review",
                reason="not_closeout_window" if phase != "closeout" else "no_rule_candidate",
            )
        else:
            write_llm_stage_skip_entry(
                state,
                call_kind="stale_intraday_hold_review",
                reason="no_open_position",
            )
            write_llm_stage_skip_entry(
                state,
                call_kind="end_of_day_carry_review",
                reason="no_open_position",
            )
    except Exception:
        return


def _run_integrated_chain(
    state: Dict[str, Any],
    *,
    execute_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
) -> Dict[str, Any]:
    previous_env = _apply_commander_temporary_runtime_defaults(state)
    try:
        return _run_integrated_chain_impl(state, execute_fn=execute_fn)
    finally:
        _restore_commander_temporary_runtime_env(previous_env)


def _run_integrated_chain_impl(
    state: Dict[str, Any],
    *,
    execute_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
) -> Dict[str, Any]:
    """Run a visible end-to-end chain inside canonical runtime."""
    nodes = load_integrated_chain_nodes()
    build_portfolio_snapshot = nodes.build_portfolio_snapshot
    build_open_order_snapshot = nodes.build_open_order_snapshot
    build_execution_readiness = nodes.build_execution_readiness
    build_risk_context = nodes.build_risk_context
    strategist_node = nodes.strategist_node
    scanner_node = nodes.scanner_node
    monitor_node = nodes.monitor_node
    decision_node = nodes.decision_node
    update_state_after_execution = nodes.update_state_after_execution

    def _emit_intraday_trade_report(local_state: Dict[str, Any]) -> Dict[str, Any]:
        return emit_intraday_trade_report(
            local_state,
            reporter_node=nodes.reporter_node,
            trade_report_enabled_fn=_commander_trade_report_enabled,
        )

    shadow_runtime, prior_cache_payload, prior_cached_output = seed_shadow_prior_context(
        state,
        ensure_shadow_runtime_fn=_ensure_commander_shadow_runtime,
        strategist_cache_payload_fn=_strategist_cache_payload,
        seed_prior_context_fn=_seed_commander_shadow_prior_context,
    )

    state, should_continue = build_integrated_chain_session_context(
        state,
        build_portfolio_snapshot_fn=build_portfolio_snapshot,
        build_open_order_snapshot_fn=build_open_order_snapshot,
        build_execution_readiness_fn=build_execution_readiness,
        build_risk_context_fn=build_risk_context,
        apply_portfolio_preflight_guard_fn=_apply_portfolio_preflight_guard,
        build_commander_decision_fn=_build_commander_decision,
    )
    if not should_continue:
        return state

    use_closeout_guard, closeout_payload = _should_use_session_closeout_fast_path(state)
    if use_closeout_guard:
        state = run_closeout_guard_fast_path(
            state,
            shadow_runtime=shadow_runtime,
            closeout_payload=closeout_payload,
            strategist_node_fn=strategist_node,
            monitor_node_fn=monitor_node,
            decision_node_fn=decision_node,
            execute_fn=execute_fn,
            emit_trade_report_fn=_emit_intraday_trade_report,
            update_state_after_execution_fn=update_state_after_execution,
            hydrate_strategist_output_cache_fn=_hydrate_strategist_output_cache,
            attach_reporter_feedback_policy_fn=_attach_commander_reporter_feedback_policy,
            attach_applied_policy_fn=_attach_commander_applied_policy,
            build_commander_decision_fn=_build_commander_decision,
            hydrate_closeout_account_orders_fn=_hydrate_closeout_account_orders,
            pending_buy_cancel_intents_from_account_orders_fn=_pending_buy_cancel_intents_from_account_orders,
            build_packet_from_state_fn=_build_packet_from_state,
            log_commander_event_fn=_log_commander_event,
            record_absent_later_stage_llm_reviews_fn=_record_absent_later_stage_llm_reviews,
            portfolio_open_position_symbols_fn=_portfolio_open_position_symbols,
            select_open_position_focus_symbol_fn=_select_open_position_focus_symbol,
            run_stage4_carry_review_fn=_run_stage4_carry_review,
            strategist_frame_blocked_fn=_strategist_frame_blocked,
            apply_strategist_block_fn=_apply_strategist_block,
            hydrate_monitor_symbol_features_fn=_hydrate_monitor_symbol_features,
            intent_from_monitor_state_fn=_intent_from_monitor_state,
        )
        return _maybe_run_post_exit_shadow_recap_runtime(state, trigger="closeout_guard_after_sweep")

    use_monitor_only, fast_path_payload = _should_use_monitor_only_fast_path(state)
    if use_monitor_only:
        state = run_monitor_only_fast_path(
            state,
            shadow_runtime=shadow_runtime,
            fast_path_payload=fast_path_payload,
            monitor_node_fn=monitor_node,
            decision_node_fn=decision_node,
            execute_fn=execute_fn,
            emit_trade_report_fn=_emit_intraday_trade_report,
            update_state_after_execution_fn=update_state_after_execution,
            hydrate_strategist_output_cache_fn=_hydrate_strategist_output_cache,
            attach_reporter_feedback_policy_fn=_attach_commander_reporter_feedback_policy,
            attach_applied_policy_fn=_attach_commander_applied_policy,
            build_commander_decision_fn=_build_commander_decision,
            portfolio_open_position_symbols_fn=_portfolio_open_position_symbols,
            select_open_position_focus_symbol_fn=_select_open_position_focus_symbol,
            log_commander_event_fn=_log_commander_event,
            hydrate_monitor_symbol_features_fn=_hydrate_monitor_symbol_features,
            intent_from_monitor_state_fn=_intent_from_monitor_state,
            build_packet_from_state_fn=_build_packet_from_state,
        )
        monitor_execution = (
            state.get("execution") if isinstance(state.get("execution"), dict) else {}
        )
        monitor_action = str(
            ((monitor_execution.get("order") or {}).get("action") or "")
        ).strip().upper()
        if monitor_action in {"BUY", "SELL"}:
            return state
        state["intents"] = []
        state, controlled_executed = run_controlled_mock_lane_path(
            state,
            shadow_runtime=shadow_runtime,
            decision_node_fn=decision_node,
            execute_fn=execute_fn,
            emit_trade_report_fn=_emit_intraday_trade_report,
            update_state_after_execution_fn=update_state_after_execution,
            intent_from_monitor_state_fn=_intent_from_monitor_state,
            build_packet_from_state_fn=_build_packet_from_state,
        )
        return state

    state["commander_decision"] = _build_commander_decision(
        state,
        mode_value="integrated_chain",
        phase_value=str(state.get("runtime_phase") or "session"),
        status_value=str(state.get("runtime_status") or "planning"),
        path_value="integrated_chain_pre_strategist",
        reason_text=str(fast_path_payload.get("reason") or ""),
    )
    state, pre_entry_exit_executed = run_pre_entry_exit_sweep_if_needed(
        state,
        shadow_runtime=shadow_runtime,
        monitor_node_fn=monitor_node,
        decision_node_fn=decision_node,
        execute_fn=execute_fn,
        emit_trade_report_fn=_emit_intraday_trade_report,
        update_state_after_execution_fn=update_state_after_execution,
        portfolio_open_position_count_fn=_portfolio_open_position_count,
        attach_reporter_feedback_policy_fn=_attach_commander_reporter_feedback_policy,
        attach_applied_policy_fn=_attach_commander_applied_policy,
        run_pre_entry_exit_sweep_fn=_run_pre_entry_exit_sweep,
        record_absent_later_stage_llm_reviews_fn=_record_absent_later_stage_llm_reviews,
    )
    if pre_entry_exit_executed:
        return state

    state["intents"] = []
    state, controlled_executed = run_controlled_mock_lane_path(
        state,
        shadow_runtime=shadow_runtime,
        decision_node_fn=decision_node,
        execute_fn=execute_fn,
        emit_trade_report_fn=_emit_intraday_trade_report,
        update_state_after_execution_fn=update_state_after_execution,
        intent_from_monitor_state_fn=_intent_from_monitor_state,
        build_packet_from_state_fn=_build_packet_from_state,
    )
    if controlled_executed:
        state["path"] = "controlled_mock_lane_pre_strategist"
        return state

    reused_strategist_cache, cache_payload = resolve_strategist_cache_use(
        state,
        should_use_cached_from_commander_skip_fn=_should_use_cached_strategist_from_commander_skip,
        should_use_cached_when_flat_fn=_should_use_cached_strategist_when_flat,
    )
    state, reused_strategist_cache, strategist_blocked = run_pre_scanner_strategist_cycle(
        state,
        shadow_runtime=shadow_runtime,
        reused_strategist_cache=reused_strategist_cache,
        cache_payload=cache_payload,
        prior_cached_output=prior_cached_output if isinstance(prior_cached_output, dict) else {},
        hydrate_strategist_output_cache_fn=_hydrate_strategist_output_cache,
        log_commander_event_fn=_log_commander_event,
        attach_reporter_feedback_policy_fn=_attach_commander_reporter_feedback_policy,
        attach_applied_policy_fn=_attach_commander_applied_policy,
        strategist_node_fn=strategist_node,
        shadow_market_changed_fn=_shadow_market_changed,
        strategist_frame_blocked_fn=_strategist_frame_blocked,
        apply_strategist_block_fn=_apply_strategist_block,
        persist_strategist_output_cache_fn=_persist_strategist_output_cache,
    )
    if strategist_blocked:
        return state
    if reused_strategist_cache:
        state = _attach_commander_reporter_feedback_policy(state, selected_route="cached_strategist", phase="session")
    state = _attach_commander_applied_policy(state)
    state["commander_decision"] = _build_commander_decision(
        state,
        mode_value="integrated_chain",
        phase_value=str(state.get("runtime_phase") or "session"),
        status_value=str(state.get("runtime_status") or "planning"),
        path_value="integrated_chain_cached_frame" if reused_strategist_cache else "integrated_chain",
        reason_text=str((state.get("runtime_fast_path") or {}).get("reason") or ""),
    )
    state = scanner_node(state)
    post_scanner_selected_symbol = _post_scanner_selected_symbol(state)
    state, reused_strategist_cache, post_scanner_blocked = run_post_scanner_refresh_cycle(
        state,
        shadow_runtime=shadow_runtime,
        reused_strategist_cache=reused_strategist_cache,
        post_scanner_selected_symbol=post_scanner_selected_symbol,
        scanner_node_fn=scanner_node,
        strategist_node_fn=strategist_node,
        build_commander_decision_fn=_build_commander_decision,
        force_selected_symbol_tactical_refresh_decision_fn=_force_selected_symbol_tactical_refresh_decision,
        commander_post_scanner_refresh_enabled_fn=_commander_post_scanner_refresh_enabled,
        log_commander_event_fn=_log_commander_event,
        attach_reporter_feedback_policy_fn=_attach_commander_reporter_feedback_policy,
        attach_applied_policy_fn=_attach_commander_applied_policy,
        strategist_frame_blocked_fn=_strategist_frame_blocked,
        apply_strategist_block_fn=_apply_strategist_block,
        persist_strategist_output_cache_fn=_persist_strategist_output_cache,
        portfolio_open_position_count_fn=_portfolio_open_position_count,
        resolve_risk_max_positions_fn=_resolve_risk_max_positions,
    )
    if post_scanner_blocked:
        return state
    state = run_monitor_decision_path(
        state,
        shadow_runtime=shadow_runtime,
        hydrate_monitor_symbol_features_fn=_hydrate_monitor_symbol_features,
        monitor_node_fn=monitor_node,
        decision_node_fn=decision_node,
        execute_fn=execute_fn,
        emit_trade_report_fn=_emit_intraday_trade_report,
        update_state_after_execution_fn=update_state_after_execution,
        intent_from_monitor_state_fn=_intent_from_monitor_state,
        build_packet_from_state_fn=_build_packet_from_state,
    )

    _record_absent_later_stage_llm_reviews(state)
    state["path"] = "integrated_chain_cached_frame" if reused_strategist_cache else "integrated_chain"
    return state


def _run_preopen_phase(state: Dict[str, Any]) -> Dict[str, Any]:
    """Warm strategist context before session without entering selection/execution paths."""
    from graphs.nodes.build_portfolio_snapshot import build_portfolio_snapshot
    from graphs.nodes.build_risk_context import build_risk_context
    from graphs.nodes.strategist_node import strategist_node

    state = build_portfolio_snapshot(state)
    snaps = state.get("snapshots") if isinstance(state.get("snapshots"), dict) else {}
    state["snapshots"] = {**dict(snaps or {}), "portfolio": state.get("portfolio_snapshot")}
    should_continue, state = _apply_portfolio_preflight_guard(state, phase="preopen")
    if not should_continue:
        return state
    state = build_risk_context(state)
    if _portfolio_open_position_count(state) > 0:
        override_assessment = _assess_open_position_commander_override(state)
        state["commander_open_position_override"] = dict(override_assessment)
        refresh_context = (
            dict(override_assessment.get("strategist_refresh_context") or {})
            if isinstance(override_assessment.get("strategist_refresh_context"), dict)
            else {}
        )
        if refresh_context:
            state["commander_open_position_refresh_context"] = dict(refresh_context)
    state["commander_decision"] = _build_commander_decision(
        state,
        mode_value=str(state.get("runtime_mode") or "graph_spine"),
        phase_value="preopen",
        status_value=str(state.get("runtime_status") or "planning"),
        path_value=str(state.get("path") or "preopen_pending"),
        reason_text="",
    )
    state = _attach_commander_reporter_feedback_policy(state, selected_route="full_cycle", phase="preopen")
    state = _attach_commander_applied_policy(state)
    state = strategist_node(state)
    if _strategist_frame_blocked(state):
        return _apply_strategist_block(state, phase="preopen")
    state = _attach_commander_applied_policy(state)
    state["commander_decision"] = _build_commander_decision(
        state,
        mode_value=str(state.get("runtime_mode") or "graph_spine"),
        phase_value="preopen",
        status_value=str(state.get("runtime_status") or "planning"),
        path_value="preopen_strategist",
        reason_text="",
    )
    state = _persist_strategist_output_cache(state)
    state["path"] = "preopen_strategist"
    state["runtime_status"] = str(state.get("runtime_status") or "preopen_ready")
    return state


def _run_closeout_phase(state: Dict[str, Any]) -> Dict[str, Any]:
    """Run closeout carry review when positions remain; reporting remains script-driven."""
    from graphs.nodes.build_portfolio_snapshot import build_portfolio_snapshot
    from graphs.nodes.build_risk_context import build_risk_context
    from graphs.nodes.strategist_node import strategist_node

    state = _attach_commander_reporter_feedback_policy(state, selected_route="full_cycle", phase="closeout")
    state = build_portfolio_snapshot(state)
    snaps = state.get("snapshots") if isinstance(state.get("snapshots"), dict) else {}
    state["snapshots"] = {**dict(snaps or {}), "portfolio": state.get("portfolio_snapshot")}
    state = build_risk_context(state)
    state["commander_decision"] = _build_commander_decision(
        state,
        mode_value=str(state.get("runtime_mode") or "graph_spine"),
        phase_value="closeout",
        status_value=str(state.get("runtime_status") or "closeout_ready"),
        path_value=str(state.get("path") or "closeout_pending"),
        reason_text="",
    )
    if _portfolio_open_position_count(state) > 0:
        state, stage4_ran = _run_stage4_carry_review(
            state,
            strategist_node,
            review_reason="end_of_day_carry_review",
            phase="closeout",
        )
        if _strategist_frame_blocked(state):
            return _apply_strategist_block(state, phase="closeout")
        if stage4_ran:
            state["path"] = "closeout_stage4_carry_review"
            state["runtime_status"] = str(state.get("runtime_status") or "closeout_ready")
            return state
    _record_absent_later_stage_llm_reviews(state)
    state["path"] = "closeout_idle"
    state["runtime_status"] = str(state.get("runtime_status") or "closeout_ready")
    return state


def _run_commander_runtime_impl(
    state: Dict[str, Any],
    *,
    mode: Optional[RuntimeMode] = None,
    phase: Optional[RuntimePhase] = None,
    graph_runner: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    integrated_runner: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    preopen_runner: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    closeout_runner: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    decide: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    execute: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Run one canonical commander runtime step.

    Mode selection uses `resolve_runtime_mode(...)`.
    """
    state = ensure_runtime_resilience_state(state)
    _ensure_market_context_clock_fields(state)
    _reset_commander_shadow_runtime(state)

    def _build_commander_decision_frame(
        mode_value: str,
        phase_value: str,
        *,
        status_value: str,
        path_value: str,
        reason_text: str = "",
    ) -> Dict[str, Any]:
        return _build_commander_decision_frame_impl(
            state,
            mode_value,
            phase_value,
            status_value=status_value,
            path_value=path_value,
            reason_text=reason_text,
        )

    def _persist_commander(mode_value: str, phase_value: str, *, status_value: str, path_value: str, reason: str = "") -> None:
        state["commander_decision"] = _build_commander_decision(
            state,
            mode_value=mode_value,
            phase_value=phase_value,
            status_value=status_value,
            path_value=path_value,
            reason_text=reason,
        )
        state["commander_decision_frame"] = _build_commander_decision_frame(
            mode_value,
            phase_value,
            status_value=status_value,
            path_value=path_value,
            reason_text=reason,
        )
        try:
            write_commander_artifact(
                state,
                mode=str(mode_value or ""),
                phase=str(phase_value or ""),
                path=str(path_value or ""),
                status=str(status_value or "ok"),
                reason=str(reason or ""),
            )
        except Exception:
            pass
        try:
            # Shadow commander is observation-only: it records recommendations and
            # explanations beside the live flow, but never overrides runtime behavior.
            shadow_path = write_commander_shadow_artifact(
                state,
                mode=str(mode_value or ""),
                phase=str(phase_value or ""),
                path=str(path_value or ""),
                status=str(status_value or "ok"),
                reason=str(reason or ""),
            )
            shadow_payload = state.get("commander_shadow_runtime") if isinstance(state.get("commander_shadow_runtime"), dict) else {}
            _log_commander_event(
                state,
                "shadow_assessment",
                {
                    "path": str(path_value or ""),
                    "artifact_path": str(shadow_path or ""),
                    "shadow_only": True,
                    "monitor_decision": str(shadow_payload.get("monitor_decision") or ""),
                    "executor_action": str(shadow_payload.get("executor_action") or ""),
                    **_commander_decision_event_meta(state),
                },
            )
        except Exception:
            pass
    selected = resolve_runtime_mode(state, mode=mode)
    selected_phase = resolve_runtime_phase(state, phase=phase)
    state["runtime_phase"] = selected_phase
    state = _annotate_runtime_plan(state, selected, selected_phase)
    state["commander_decision"] = _build_commander_decision(
        state,
        mode_value=selected,
        phase_value=selected_phase,
        status_value=str(state.get("runtime_status") or "planning"),
        path_value=str(state.get("path") or "pending"),
        reason_text=str(state.get("runtime_transition") or ""),
    )
    _log_commander_event(
        state,
        "route",
        {
            "mode": selected,
            "phase": selected_phase,
            "agents": list(state.get("runtime_plan", {}).get("agents", [])),
            **_commander_decision_event_meta(state),
        },
    )
    _log_commander_event(
        state,
        "route_selected",
        {
            "mode": selected,
            "phase": selected_phase,
            "agents": list(state.get("runtime_plan", {}).get("agents", [])),
            **_commander_decision_event_meta(state),
        },
    )

    should_run, state = _apply_runtime_transition(state)
    if state.get("runtime_transition"):
        _log_commander_event(
            state,
            "transition",
            {
                "transition": state.get("runtime_transition"),
                "status": state.get("runtime_status"),
                "retry_count": state.get("runtime_retry_count"),
                **_commander_decision_event_meta(state),
            },
        )
    if not should_run:
        _log_commander_event(
            state,
            "end",
            {"mode": selected, "status": state.get("runtime_status", "stopped"), "path": None, **_commander_decision_event_meta(state)},
        )
        _persist_commander(selected, selected_phase, status_value=str(state.get("runtime_status", "stopped") or "stopped"), path_value="")
        return state

    state, intervention_payload = _apply_operator_resume_intervention(state)
    if intervention_payload:
        _log_commander_event(state, "intervention", intervention_payload)

    should_run, state, cooldown_payload = _apply_commander_cooldown_guard(state)
    if not should_run:
        _log_commander_event(
            state,
            "transition",
            {
                "transition": state.get("runtime_transition"),
                "status": state.get("runtime_status"),
                "reason": cooldown_payload.get("reason"),
                "cooldown_until_epoch": cooldown_payload.get("cooldown_until_epoch"),
                "incident_count": cooldown_payload.get("incident_count"),
                "incident_threshold": cooldown_payload.get("incident_threshold"),
                **_commander_decision_event_meta(state),
            },
        )
        _log_commander_event(state, "resilience", cooldown_payload)
        _log_commander_event(
            state,
            "end",
            {"mode": selected, "status": state.get("runtime_status", "stopped"), "path": None, **_commander_decision_event_meta(state)},
        )
        _persist_commander(
            selected,
            selected_phase,
            status_value=str(state.get("runtime_status", "stopped") or "stopped"),
            path_value=str(state.get("path") or ""),
            reason=str(cooldown_payload.get("reason") or state.get("runtime_status") or ""),
        )
        return state

    graph_runner = graph_runner or run_trading_graph
    decide = decide or decide_trade
    execute = execute or execute_from_packet
    integrated_runner = integrated_runner or (lambda s: _run_integrated_chain(s, execute_fn=execute))
    preopen_runner = preopen_runner or _run_preopen_phase
    closeout_runner = closeout_runner or _run_closeout_phase

    try:
        if selected_phase == "preopen":
            state = preopen_runner(state)
            _log_commander_event(
                state,
                "end",
                {
                    "mode": selected,
                    "phase": selected_phase,
                    "status": state.get("runtime_status", "preopen_ready"),
                    "path": state.get("path", "preopen_strategist"),
                    **_commander_decision_event_meta(state),
                    **_portfolio_guard_event_summary(state),
                    **_portfolio_preflight_event_summary(state),
                },
            )
            _persist_commander(selected, selected_phase, status_value=str(state.get("runtime_status", "preopen_ready") or "preopen_ready"), path_value=str(state.get("path", "preopen_strategist") or "preopen_strategist"))
            return state

        if selected_phase == "closeout":
            state = closeout_runner(state)
            _log_commander_event(
                state,
                "end",
                {
                    "mode": selected,
                    "phase": selected_phase,
                    "status": state.get("runtime_status", "closeout_ready"),
                    "path": state.get("path", "closeout_idle"),
                    **_commander_decision_event_meta(state),
                    **_portfolio_guard_event_summary(state),
                    **_portfolio_preflight_event_summary(state),
                },
            )
            _persist_commander(selected, selected_phase, status_value=str(state.get("runtime_status", "closeout_ready") or "closeout_ready"), path_value=str(state.get("path", "closeout_idle") or "closeout_idle"))
            state = _maybe_run_reporter_hooks(state, mode_value=selected, phase_value=selected_phase)
            return state

        if selected == "decision_packet":
            state = decide(state)
            state = execute(state)
            _log_commander_event(
                state,
                "end",
                {
                    "mode": selected,
                    "phase": selected_phase,
                    "status": state.get("runtime_status", "ok"),
                    "path": "decision_packet",
                    **_commander_decision_event_meta(state),
                    **_portfolio_guard_event_summary(state),
                    **_portfolio_preflight_event_summary(state),
                },
            )
            _persist_commander(selected, selected_phase, status_value=str(state.get("runtime_status", "ok") or "ok"), path_value="decision_packet")
            state = _maybe_run_reporter_hooks(state, mode_value=selected, phase_value=selected_phase)
            return state

        if selected == "integrated_chain":
            state = integrated_runner(state)
            _log_commander_event(
                state,
                "end",
                {
                    "mode": selected,
                    "phase": selected_phase,
                    "status": state.get("runtime_status", "ok"),
                    "path": state.get("path", "integrated_chain"),
                    **_commander_decision_event_meta(state),
                    **_portfolio_guard_event_summary(state),
                    **_portfolio_preflight_event_summary(state),
                },
            )
            _persist_commander(selected, selected_phase, status_value=str(state.get("runtime_status", "ok") or "ok"), path_value=str(state.get("path", "integrated_chain") or "integrated_chain"))
            state = _maybe_run_reporter_hooks(state, mode_value=selected, phase_value=selected_phase)
            return state

        if _graph_spine_portfolio_preflight_enabled(state, phase=selected_phase):
            state = _run_graph_spine_with_preflight(state, graph_runner=graph_runner)
        else:
            state = graph_runner(state)
        _log_commander_event(
            state,
            "end",
            {
                "mode": selected,
                "phase": selected_phase,
                "status": state.get("runtime_status", "ok"),
                "path": state.get("path", "graph_spine"),
                **_commander_decision_event_meta(state),
                **_portfolio_guard_event_summary(state),
                **_portfolio_preflight_event_summary(state),
            },
        )
        _persist_commander(selected, selected_phase, status_value=str(state.get("runtime_status", "ok") or "ok"), path_value=str(state.get("path", "graph_spine") or "graph_spine"))
        state = _maybe_run_reporter_hooks(state, mode_value=selected, phase_value=selected_phase)
        return state
    except Exception as e:
        incident_payload = _register_commander_incident(state, error_type=type(e).__name__)
        state["runtime_status"] = "error"
        _log_commander_event(
            state,
            "error",
            {
                "mode": selected,
                "phase": selected_phase,
                "error_type": type(e).__name__,
                "error": str(e),
                **incident_payload,
            },
        )
        _persist_commander(selected, selected_phase, status_value="error", path_value=str(state.get("path") or ""), reason=str(e))
        raise


def run_commander_runtime(
    state: Dict[str, Any],
    *,
    mode: Optional[RuntimeMode] = None,
    phase: Optional[RuntimePhase] = None,
    graph_runner: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    integrated_runner: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    preopen_runner: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    closeout_runner: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    decide: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    execute: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    previous_env = _apply_commander_temporary_runtime_defaults(state)
    try:
        return _run_commander_runtime_impl(
            state,
            mode=mode,
            phase=phase,
            graph_runner=graph_runner,
            integrated_runner=integrated_runner,
            preopen_runner=preopen_runner,
            closeout_runner=closeout_runner,
            decide=decide,
            execute=execute,
        )
    finally:
        _restore_commander_temporary_runtime_env(previous_env)
