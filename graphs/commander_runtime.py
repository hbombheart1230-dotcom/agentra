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

    route = str(selected_route or _derive_commander_selected_route(state) or "").strip().lower() or "unknown"
    phase_text = str(phase or state.get("runtime_phase") or "session").strip().lower() or "session"
    feedback_policy = _resolve_commander_reporter_feedback_policy(
        state,
        selected_route=route,
        phase=phase_text,
    )
    reporter_ai_review_enabled = _existing_value("reporter", "ai_review", "enabled")
    if reporter_ai_review_enabled is None:
        reporter_ai_review_enabled = False
    trade_report_enabled = _existing_value("reporter", "trade_report", "enabled")
    if trade_report_enabled is None:
        trade_report_enabled = True
    trade_report_generate_on_open = _existing_value("reporter", "trade_report", "generate_on_open")
    if trade_report_generate_on_open is None:
        trade_report_generate_on_open = False
    strict_mode = _existing_value("strategist", "runtime", "strict_mode")
    if strict_mode is None:
        strict_mode = True
    allow_legacy_rule = _existing_value("strategist", "runtime", "allow_legacy_rule")
    if allow_legacy_rule is None:
        allow_legacy_rule = False
    allow_legacy_strategy_v1 = _existing_value("strategist", "runtime", "allow_legacy_strategy_v1")
    if allow_legacy_strategy_v1 is None:
        allow_legacy_strategy_v1 = False
    memory_feedback_enabled = _existing_value("strategist", "memory_feedback", "enabled")
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
    monitor_only_when_holding = _existing_value("commander", "route", "monitor_only_when_holding")
    if monitor_only_when_holding is None:
        monitor_only_when_holding = True
    cached_strategist_when_flat = _existing_value("commander", "route", "cached_strategist_when_flat")
    if cached_strategist_when_flat is None:
        cached_strategist_when_flat = False
    exit_policy_enabled = _existing_value("monitor", "exit", "enabled")
    if exit_policy_enabled is None:
        exit_policy_enabled = True
    exit_policy_use_eod_flat = _existing_value("monitor", "exit", "eod_flat", "enabled")
    if exit_policy_use_eod_flat is None:
        exit_policy_use_eod_flat = True
    block_buy_when_open_position = _existing_value("monitor", "entry", "block_buy_when_open_position")
    if block_buy_when_open_position is None:
        block_buy_when_open_position = risk_max_positions <= 1
    monitor_scoring_enabled = _existing_value("monitor", "entry", "scoring", "enabled")
    if monitor_scoring_enabled is None:
        monitor_scoring_enabled = False
    monitor_scoring_shadow_mode = _existing_value("monitor", "entry", "scoring", "shadow_mode")
    if monitor_scoring_shadow_mode is None:
        monitor_scoring_shadow_mode = True
    post_exit_cooldown_sec = _existing_value("execution", "cooldowns", "post_exit_sec")
    if post_exit_cooldown_sec is None:
        post_exit_cooldown_sec = 180
    sell_cooldown_sec = _existing_value("execution", "cooldowns", "sell_sec")
    if sell_cooldown_sec is None:
        sell_cooldown_sec = 300
    min_hold_seconds = _existing_value("monitor", "hold", "min_hold_seconds")
    if min_hold_seconds is None:
        min_hold_seconds = 600
    exit_confirm_ticks = _existing_value("monitor", "exit", "confirm_ticks")
    if exit_confirm_ticks is None:
        exit_confirm_ticks = 2
    eod_flat_cutoff_min = _existing_value("monitor", "exit", "eod_flat", "cutoff_min")
    if eod_flat_cutoff_min is None:
        eod_flat_cutoff_min = 10
    buy_closeout_cutoff_min = _existing_value("monitor", "entry", "buy_closeout_cutoff_min")
    if buy_closeout_cutoff_min is None:
        buy_closeout_cutoff_min = max(
            _DEFAULT_BUY_CLOSEOUT_CUTOFF_MIN,
            _coerce_int(eod_flat_cutoff_min, 10),
        )
    top_candidate_pool = _existing_value("scanner", "candidate", "top_pool")
    if top_candidate_pool is None:
        top_candidate_pool = 30
    kiwoom_condition_limit = _existing_value("scanner", "kiwoom", "condition_limit")
    if kiwoom_condition_limit is None:
        kiwoom_condition_limit = 200
    scanner_source_type = _existing_value("scanner", "source", "type")
    if scanner_source_type in (None, ""):
        scanner_source_type = "kiwoom"
    scanner_strict_only = _existing_value("scanner", "kiwoom", "strict_only")
    if scanner_strict_only is None:
        scanner_strict_only = True
    scanner_strict_only = _is_trueish(scanner_strict_only)
    scanner_block_static_when_empty = _existing_value("scanner", "fallback", "block_static_when_empty")
    if scanner_block_static_when_empty is None:
        scanner_block_static_when_empty = True
    scanner_block_static_when_empty = _is_trueish(scanner_block_static_when_empty)
    scanner_live_fetch = _existing_value("scanner", "kiwoom", "live_fetch")
    if scanner_live_fetch is None:
        scanner_live_fetch = True
    scanner_live_fetch = _is_trueish(scanner_live_fetch)
    scanner_include_change_rate = _existing_value("scanner", "kiwoom", "include_change_rate")
    if scanner_include_change_rate is None:
        scanner_include_change_rate = True
    scanner_include_change_rate = _is_trueish(scanner_include_change_rate)
    universe_asset_type = _existing_value("universe", "asset_type")
    if universe_asset_type in (None, ""):
        universe_asset_type = "all_tradable"
    monitor_scoring_threshold = _existing_value("monitor", "entry", "scoring", "threshold")
    if monitor_scoring_threshold is None:
        monitor_scoring_threshold = 3
    position_sizing_enabled = _existing_value("monitor", "entry", "position_sizing", "enabled")
    if position_sizing_enabled is None:
        position_sizing_enabled = True
    position_sizing_risk_per_trade_ratio = _existing_value(
        "monitor",
        "entry",
        "position_sizing",
        "risk_per_trade_ratio",
    )
    if position_sizing_risk_per_trade_ratio is None:
        position_sizing_risk_per_trade_ratio = 0.01
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
    position_sizing_min_qty = _existing_value("monitor", "entry", "position_sizing", "min_position_qty")
    if position_sizing_min_qty is None:
        position_sizing_min_qty = 1
    position_sizing_lot_size = _existing_value("monitor", "entry", "position_sizing", "lot_size")
    if position_sizing_lot_size is None:
        position_sizing_lot_size = 1
    strategy_memory_recent_runs = _existing_value("strategist", "memory_feedback", "recent_runs")
    if strategy_memory_recent_runs is None:
        strategy_memory_recent_runs = 12
    strategist_llm_profile = str(_existing_value("llm", "strategist", "profile") or "balanced").strip().lower() or "balanced"
    reporter_intraday_profile = str(_existing_value("llm", "reporter", "intraday", "profile") or "fast_free").strip().lower() or "fast_free"
    reporter_daily_profile = str(_existing_value("llm", "reporter", "daily", "profile") or "strong_reasoning").strip().lower() or "strong_reasoning"
    strategist_llm = resolve_model_profile(strategist_llm_profile, default_profile="balanced")
    reporter_intraday_llm = resolve_model_profile(reporter_intraday_profile, default_profile="fast_free")
    reporter_daily_llm = resolve_model_profile(reporter_daily_profile, default_profile="strong_reasoning")
    default_execution_profile_name = (
        str(
            _existing_value("llm", "execution_profile", "profile_name")
            or _existing_value("llm", "execution_profile", "name")
            or "default_intraday"
        ).strip().lower()
        or "default_intraday"
    )
    default_execution_profile = resolve_execution_profile(
        default_execution_profile_name,
        default_profile="default_intraday",
        defaults={
            "profile_name": "default_intraday",
            "name": "default_intraday",
            "temperature": 0.2,
            "max_tokens": 8192,
            "timeout_sec": 15,
            "retry": {"max_attempts": 2, "backoff_sec": 0.0},
            "retry_max": 2,
            "retry_backoff_sec": 0.0,
        },
    )
    strategist_execution_profile_name = (
        str(_existing_value("llm", "strategist", "execution_profile", "name") or "balanced_reasoning").strip().lower()
        or "balanced_reasoning"
    )
    reporter_intraday_execution_profile_name = (
        str(_existing_value("llm", "reporter", "intraday", "execution_profile", "name") or "concise_review").strip().lower()
        or "concise_review"
    )
    reporter_daily_execution_profile_name = (
        str(_existing_value("llm", "reporter", "daily", "execution_profile", "name") or "deep_review").strip().lower()
        or "deep_review"
    )
    strategist_execution_profile = resolve_execution_profile(
        strategist_execution_profile_name,
        default_profile="balanced_reasoning",
        defaults={
            "profile_name": "balanced_reasoning",
            "name": "balanced_reasoning",
            "temperature": 0.1,
            "max_tokens": 8192,
            "timeout_sec": 15,
            "retry": {
                "max_attempts": int(((default_execution_profile.get("retry") or {}).get("max_attempts") or 2)),
                "backoff_sec": float(((default_execution_profile.get("retry") or {}).get("backoff_sec") or 0.0)),
            },
            "retry_max": 2,
            "retry_backoff_sec": float(((default_execution_profile.get("retry") or {}).get("backoff_sec") or 0.0)),
        },
    )
    reporter_intraday_execution_profile = resolve_execution_profile(
        reporter_intraday_execution_profile_name,
        default_profile="concise_review",
        defaults={
            "profile_name": "concise_review",
            "name": "concise_review",
            "temperature": 0.2,
            "max_tokens": 8192,
            "timeout_sec": max(1, _coerce_int(default_execution_profile.get("timeout_sec"), 15)),
            "retry": {
                "max_attempts": int(((default_execution_profile.get("retry") or {}).get("max_attempts") or 2)),
                "backoff_sec": float(((default_execution_profile.get("retry") or {}).get("backoff_sec") or 0.0)),
            },
            "retry_max": int(((default_execution_profile.get("retry") or {}).get("max_attempts") or 2)),
            "retry_backoff_sec": float(((default_execution_profile.get("retry") or {}).get("backoff_sec") or 0.0)),
        },
    )
    reporter_daily_execution_profile = resolve_execution_profile(
        reporter_daily_execution_profile_name,
        default_profile="deep_review",
        defaults={
            "profile_name": "deep_review",
            "name": "deep_review",
            "temperature": 0.2,
            "max_tokens": 8192,
            "timeout_sec": max(1, _coerce_int(default_execution_profile.get("timeout_sec"), 15)),
            "retry": {
                "max_attempts": int(((default_execution_profile.get("retry") or {}).get("max_attempts") or 2)),
                "backoff_sec": float(((default_execution_profile.get("retry") or {}).get("backoff_sec") or 0.0)),
            },
            "retry_max": int(((default_execution_profile.get("retry") or {}).get("max_attempts") or 2)),
            "retry_backoff_sec": float(((default_execution_profile.get("retry") or {}).get("backoff_sec") or 0.0)),
        },
    )
    carry_state = str(commander_override.get("carry_state") or "").strip().lower()
    carry_risk_bias = str(commander_override.get("carry_risk_bias") or "").strip().lower()
    carry_risk_reason = str(commander_override.get("carry_risk_reason") or "")
    override_reason = str(commander_override.get("override_reason") or "").strip().lower()
    hold_repeat_count_max = max(0, _coerce_int(commander_override.get("hold_repeat_count_max"), 0))
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

    strategist_output = dict(strategist_output)
    strategy_policy = (
        dict(strategist_output.get("strategy_policy") or {})
        if isinstance(strategist_output.get("strategy_policy"), dict)
        else {}
    )
    scanner_policy = (
        dict(strategy_policy.get("scanner_policy") or {})
        if isinstance(strategy_policy.get("scanner_policy"), dict)
        else {}
    )
    commander_context = (
        dict(strategy_policy.get("commander_context") or {})
        if isinstance(strategy_policy.get("commander_context"), dict)
        else {}
    )
    memory_packets = {}
    commander_memory_policy = {}
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
    horizon_proposal = {}
    if isinstance(strategist_output.get("strategist_horizon_proposal"), dict):
        horizon_proposal = dict(strategist_output.get("strategist_horizon_proposal") or {})
    elif isinstance(strategist_output.get("strategy_horizon_feedback"), dict):
        horizon_proposal = dict(strategist_output.get("strategy_horizon_feedback") or {})
    elif isinstance((strategy_policy.get("monitor_policy") or {}).get("strategy_horizon_feedback"), dict):
        horizon_proposal = dict((strategy_policy.get("monitor_policy") or {}).get("strategy_horizon_feedback") or {})
    commander_horizon_policy = build_commander_horizon_policy(
        horizon_proposal,
        commander_context=commander_context,
        memory_packets=memory_packets,
        runtime_phase=str(state.get("runtime_phase") or commander_context.get("session_bias") or ""),
        live_validation_mode=True,
        source="commander_applied_policy",
    )
    horizon_context = build_horizon_context(commander_horizon_policy)
    strategist_refresh_context = (
        dict(commander_context.get("strategist_refresh_context") or {})
        if isinstance(commander_context.get("strategist_refresh_context"), dict)
        else {}
    )
    strategist_refresh_context["commander_horizon_policy"] = dict(commander_horizon_policy)
    strategist_refresh_context["horizon_context"] = dict(horizon_context)
    commander_context["strategist_refresh_context"] = strategist_refresh_context
    open_position_refresh_context = (
        dict(commander_context.get("open_position_refresh_context") or {})
        if isinstance(commander_context.get("open_position_refresh_context"), dict)
        else {}
    )
    if open_position_refresh_context:
        open_position_refresh_context["commander_horizon_policy"] = dict(commander_horizon_policy)
        open_position_refresh_context["horizon_context"] = dict(horizon_context)
        commander_context["open_position_refresh_context"] = open_position_refresh_context
    commander_context["commander_horizon_policy"] = dict(commander_horizon_policy)
    commander_context["horizon_context"] = dict(horizon_context)
    commander_decision = dict(commander_decision)
    commander_decision["commander_horizon_policy"] = dict(commander_horizon_policy)
    commander_decision["horizon_context"] = dict(horizon_context)
    state["commander_decision"] = commander_decision
    state["commander_horizon_policy"] = dict(commander_horizon_policy)
    merged_applied_policy = dict(state.get("applied_policy") or {}) if isinstance(state.get("applied_policy"), dict) else {}
    merged_applied_policy["horizon"] = dict(commander_horizon_policy)
    merged_applied_policy["commander_horizon_policy"] = dict(commander_horizon_policy)
    state["applied_policy"] = merged_applied_policy
    strategy_policy["commander_context"] = commander_context

    monitor_policy = (
        dict(strategy_policy.get("monitor_policy") or {})
        if isinstance(strategy_policy.get("monitor_policy"), dict)
        else {}
    )
    monitor_policy["applied_policy"] = dict(applied_policy)
    monitor_policy["policy_source"] = str(policy_meta.get("policy_source") or "")
    monitor_policy["policy_validation_status"] = str(policy_meta.get("policy_validation_status") or "")
    monitor_policy["policy_fallback_used"] = bool(policy_meta.get("policy_fallback_used"))
    monitor_policy["policy_fallback_reason"] = str(policy_meta.get("policy_fallback_reason") or "")
    monitor_policy["policy_partial_normalized"] = bool(policy_meta.get("policy_partial_normalized"))
    monitor_policy["policy_default_filled_fields"] = list(policy_meta.get("policy_default_filled_fields") or [])
    monitor_policy["policy_validation_missing_fields"] = list(policy_meta.get("policy_validation_missing_fields") or [])
    monitor_policy["policy_validation_invalid_fields"] = list(policy_meta.get("policy_validation_invalid_fields") or [])
    monitor_policy["override_reason"] = str(policy_meta.get("override_reason") or "")
    monitor_policy["applied_policy_source_chain"] = list(policy_meta.get("applied_policy_source_chain") or [])
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
    if commander_entry_control:
        scanner_policy["entry_control"] = dict(commander_entry_control)
        scanner_policy["max_priority_rank"] = int(
            commander_entry_control.get("max_priority_rank")
            if commander_entry_control.get("max_priority_rank") not in (None, "")
            else 10
        )
        scanner_policy["max_runner_ups"] = int(
            commander_entry_control.get("max_runner_ups")
            if commander_entry_control.get("max_runner_ups") not in (None, "")
            else 9
        )
    strategy_policy["scanner_policy"] = scanner_policy

    provenance = (
        dict(strategy_policy.get("provenance") or {})
        if isinstance(strategy_policy.get("provenance"), dict)
        else {}
    )
    provenance["applied_policy_source"] = str(policy_meta.get("policy_source") or "")
    provenance["policy_validation_status"] = str(policy_meta.get("policy_validation_status") or "")
    provenance["policy_fallback_used"] = bool(policy_meta.get("policy_fallback_used"))
    provenance["policy_fallback_reason"] = str(policy_meta.get("policy_fallback_reason") or "")
    provenance["policy_partial_normalized"] = bool(policy_meta.get("policy_partial_normalized"))
    provenance["policy_default_filled_fields"] = list(policy_meta.get("policy_default_filled_fields") or [])
    provenance["policy_validation_missing_fields"] = list(policy_meta.get("policy_validation_missing_fields") or [])
    provenance["policy_validation_invalid_fields"] = list(policy_meta.get("policy_validation_invalid_fields") or [])
    provenance["override_reason"] = str(policy_meta.get("override_reason") or "")
    provenance["applied_policy_source_chain"] = list(policy_meta.get("applied_policy_source_chain") or [])
    provenance["scanner_bias_source"] = str(scanner_bias_meta.get("bias_source") or "")
    strategy_policy["provenance"] = provenance

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
    portfolio_snapshot = state.get("portfolio_snapshot") if isinstance(state.get("portfolio_snapshot"), dict) else {}
    preflight = state.get("portfolio_preflight") if isinstance(state.get("portfolio_preflight"), dict) else {}
    runtime_fast_path = state.get("runtime_fast_path") if isinstance(state.get("runtime_fast_path"), dict) else {}
    strategist_output = state.get("strategist_output") if isinstance(state.get("strategist_output"), dict) else {}
    resilience = state.get("runtime_resilience_state") if isinstance(state.get("runtime_resilience_state"), dict) else {}
    shadow_assessment = _build_shadow_assessment_summary(
        state,
        mode_value=mode_value,
        phase_value=phase_value,
        status_value=status_value,
        path_value=path_value,
        reason_text=reason_text,
    )
    positions = [row for row in list(portfolio_snapshot.get("positions") or []) if isinstance(row, dict)]
    open_position_count = len(positions)
    max_positions = _resolve_risk_max_positions(state)
    entry_capacity_available = open_position_count < max_positions
    market_regime, strategist_fallback_used = _derive_commander_market_regime(state, shadow_assessment=shadow_assessment)
    strategist_rail_raw = strategist_output.get("market_regime_rail")
    strategist_rail_shadow = (
        strategist_output.get("market_regime_rail_shadow")
        if isinstance(strategist_output.get("market_regime_rail_shadow"), dict)
        else {}
    )
    strategist_input_quality = (
        strategist_output.get("strategist_input_quality")
        if isinstance(strategist_output.get("strategist_input_quality"), dict)
        else {}
    )
    input_quality_rail = (
        strategist_input_quality.get("market_regime_rail")
        if isinstance(strategist_input_quality.get("market_regime_rail"), dict)
        else {}
    )
    risk_off_policy = (
        strategist_output.get("risk_off_exception_policy")
        if isinstance(strategist_output.get("risk_off_exception_policy"), dict)
        else {}
    )
    if isinstance(strategist_rail_raw, dict):
        market_regime_rail = str(
            strategist_rail_raw.get("market_regime_rail")
            or strategist_rail_raw.get("rail_id")
            or strategist_rail_raw.get("rail")
            or ""
        )
    else:
        market_regime_rail = str(strategist_rail_raw or "")
    market_regime_rail = str(
        market_regime_rail
        or strategist_rail_shadow.get("market_regime_rail")
        or strategist_rail_shadow.get("rail_id")
        or input_quality_rail.get("market_regime_rail")
        or input_quality_rail.get("rail_id")
        or risk_off_policy.get("market_regime_rail")
        or state.get("market_regime_rail")
        or ""
    ).strip()
    rail_l = market_regime_rail.lower()
    rail_risk_off = bool("risk_off" in rail_l or "gap_down" in rail_l or "breadth_collapse" in rail_l)
    if rail_risk_off and market_regime != "risk_off":
        market_regime = "risk_off"
    macro_stress_overlay = (
        strategist_output.get("macro_stress_overlay")
        if isinstance(strategist_output.get("macro_stress_overlay"), dict)
        else {}
    )
    raw_stress_flags = list(macro_stress_overlay.get("stress_flags") or [])
    macro_stress_active = bool(macro_stress_overlay.get("active"))
    stress_flags = raw_stress_flags if macro_stress_active else []
    if str(phase_value or "").strip() == "preopen":
        session_bias = "preopen_context"
    elif str(phase_value or "").strip() == "closeout":
        session_bias = "closeout_control"
    elif open_position_count > 0 and not entry_capacity_available:
        session_bias = "position_management"
    elif open_position_count > 0 and entry_capacity_available:
        session_bias = "multi_position_selection"
    elif "cached" in str(path_value or ""):
        session_bias = "context_reuse"
    else:
        session_bias = "active_selection"

    runtime_status_blocked = str(status_value or "").strip().lower() in {"blocked", "preflight_blocked"}
    hard_runtime_blocked = bool(preflight.get("blocked")) or (
        bool(runtime_status_blocked) and not bool(entry_capacity_available)
    )
    if hard_runtime_blocked:
        risk_mode = "blocked"
    elif market_regime == "risk_off" or rail_risk_off or bool(stress_flags) or str(resilience.get("degrade_mode") or "").strip():
        risk_mode = "defensive"
    elif market_regime == "risk_on":
        risk_mode = "offensive"
    else:
        risk_mode = "balanced"

    allowed_playbooks: list[str]
    if risk_mode == "blocked":
        allowed_playbooks = []
    elif risk_mode == "defensive":
        allowed_playbooks = ["defensive", "pullback"]
    elif risk_mode == "offensive":
        allowed_playbooks = ["breakout", "pullback"]
    else:
        allowed_playbooks = ["pullback", "defensive", "breakout"]
    all_playbooks = ["breakout", "pullback", "reversal", "defensive"]
    banned_playbooks = [x for x in all_playbooks if x not in allowed_playbooks]

    if risk_mode == "defensive":
        scanner_mission = "Prioritize liquid leaders and defensive candidates with resilient participation."
        monitor_mission = "Require cleaner confirmation and protect downside quickly."
    elif risk_mode == "offensive":
        scanner_mission = "Prioritize liquid momentum leaders with strong participation and clean continuation."
        monitor_mission = "Confirm intraday continuation promptly while respecting risk rails."
    elif session_bias == "position_management":
        scanner_mission = "Keep candidate refresh narrow while existing exposure is being managed."
        monitor_mission = "Focus on hold versus exit confirmation for open positions first."
    elif session_bias == "multi_position_selection":
        scanner_mission = "Continue candidate selection while existing exposure is monitored, avoiding held symbols."
        monitor_mission = "Evaluate fresh entries only when position capacity remains and duplicate-symbol guards pass."
    else:
        scanner_mission = "Prioritize balanced liquid leaders with clear scanner fit and manageable risk."
        monitor_mission = "Wait for confirmation and avoid low-quality chase entries."

    if "cached" in str(path_value or "") or str(runtime_fast_path.get("reason") or "").strip() == "flat_position_cached_strategist":
        llm_policy = "prefer_cached_context"
    elif session_bias == "position_management":
        llm_policy = "allow_if_context_changed"
    elif str(phase_value or "").strip() == "preopen":
        llm_policy = "allow_context_refresh"
    else:
        llm_policy = "allow"

    shadow_used = bool(shadow_assessment)
    shadow_no_trade_reason_code = str(shadow_assessment.get("no_trade_reason_code") or "").strip()
    shadow_reason_summary = str(shadow_assessment.get("reason_summary") or "").strip()
    command_intent = str(shadow_assessment.get("decision") or "OBSERVE_ONLY").strip() if shadow_used else "OBSERVE_ONLY"
    strategist_invocation = str(shadow_assessment.get("strategist_action_recommendation") or "").strip() if shadow_used else ""
    llm_policy = str(shadow_assessment.get("llm_call_advice") or llm_policy).strip()
    flow_instruction = str(shadow_assessment.get("suggested_action") or "").strip()
    no_trade_reason_code = shadow_no_trade_reason_code
    if not strategist_invocation:
        strategist_invocation = "SKIP" if open_position_count > 0 and not entry_capacity_available else "RUN"
    if not flow_instruction:
        flow_instruction = "HOLD_OBSERVE" if open_position_count > 0 and not entry_capacity_available else "NO_ACTION"
    if not no_trade_reason_code:
        no_trade_reason_code = "MAX_POSITIONS_REACHED" if open_position_count > 0 and not entry_capacity_available else "NONE"
    observations = dict(shadow_assessment.get("observations") or {}) if isinstance(shadow_assessment.get("observations"), dict) else {}
    refresh_assessment = _assess_pre_buy_strategist_refresh_need(state, commander_market_regime=market_regime)
    strategist_refresh_requested = bool(refresh_assessment.get("requested"))
    strategist_refresh_reason = str(refresh_assessment.get("refresh_signal") or refresh_assessment.get("reason") or "").strip()
    strategist_refresh_context = {
        k: v
        for k, v in dict(refresh_assessment).items()
        if k not in {"requested"}
    }
    cache_reuse_assessment = _assess_cached_strategist_reuse_preference(state)
    strategist_cache_preferred = bool(cache_reuse_assessment.get("preferred"))
    strategist_cache_preference_reason = str(cache_reuse_assessment.get("reason") or "").strip()
    strategist_cache_preference_context = {
        k: v
        for k, v in dict(cache_reuse_assessment).items()
        if k not in {"preferred"}
    }
    if strategist_refresh_requested:
        strategist_invocation = "RUN_REFRESH"
        llm_policy = "allow_context_refresh"
        flow_instruction = "REFRESH_STRATEGY_FRAME"
        observations = {
            **observations,
            "strategist_refresh_requested": True,
            "strategist_refresh_reason": strategist_refresh_reason,
        }
    elif strategist_invocation == "RUN" and strategist_cache_preferred:
        strategist_invocation = "SKIP"
        llm_policy = "prefer_cached_context"
        flow_instruction = "REUSE_STRATEGY_FRAME"
        observations = {
            **observations,
            "strategist_cache_preferred": True,
            "strategist_cache_preference_reason": strategist_cache_preference_reason,
        }
    source_priority = ["shadow_commander", "runtime_observation", "strategist_fallback"]
    if strategist_refresh_requested:
        source_priority = ["commander_refresh_heuristic", *source_priority]
    elif strategist_invocation == "SKIP" and strategist_cache_preferred:
        source_priority = ["commander_cache_reuse", *source_priority]
    source_refs = {
        "shadow_event": "commander_router.shadow_assessment",
        "runtime_fast_path_reason": str(runtime_fast_path.get("reason") or ""),
        "runtime_path": str(path_value or ""),
        "strategist_fallback_fields": ["market_regime"] if strategist_fallback_used else [],
    }
    if strategist_refresh_requested:
        source_refs["strategist_refresh_reason"] = strategist_refresh_reason
        source_refs["strategist_refresh_scope"] = "strategy_frame_refresh"
    elif strategist_invocation == "SKIP" and strategist_cache_preferred:
        source_refs["strategist_cache_preference_reason"] = strategist_cache_preference_reason
        source_refs["strategist_cache_preference_scope"] = "cached_strategy_frame_reuse"
    applied_policy_meta = (
        dict(state.get("commander_applied_policy_meta") or {})
        if isinstance(state.get("commander_applied_policy_meta"), dict)
        else {}
    )
    reporter_feedback_policy = (
        dict(state.get("commander_reporter_feedback_policy") or {})
        if isinstance(state.get("commander_reporter_feedback_policy"), dict)
        else {}
    )
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
    applied_policy = dict(applied_policy_meta.get("applied_policy") or {})
    commander_behavior_policy = (
        dict(state.get("commander_behavior_policy") or {})
        if isinstance(state.get("commander_behavior_policy"), dict)
        else {}
    )
    commander_override = (
        dict(state.get("commander_open_position_override") or {})
        if isinstance(state.get("commander_open_position_override"), dict)
        else {}
    )
    open_position_refresh_context = (
        dict(state.get("commander_open_position_refresh_context") or {})
        if isinstance(state.get("commander_open_position_refresh_context"), dict)
        else dict(commander_override.get("strategist_refresh_context") or {})
        if isinstance(commander_override.get("strategist_refresh_context"), dict)
        else {}
    )
    commander_carry_state = str(
        commander_override.get("carry_state")
        or open_position_refresh_context.get("carry_state")
        or ""
    )
    commander_carry_risk_bias = str(
        commander_override.get("carry_risk_bias")
        or open_position_refresh_context.get("carry_risk_bias")
        or ""
    )
    commander_carry_risk_reason = str(
        commander_override.get("carry_risk_reason")
        or open_position_refresh_context.get("carry_risk_reason")
        or ""
    )
    commander_session_open_recovery = (
        dict(
            commander_override.get("session_open_recovery_assessment")
            or open_position_refresh_context.get("session_open_recovery_assessment")
            or {}
        )
        if isinstance(commander_override.get("session_open_recovery_assessment"), dict)
        or isinstance(open_position_refresh_context.get("session_open_recovery_assessment"), dict)
        else {}
    )
    if str(commander_override.get("override_action") or "").strip().lower() == "strategist_refresh":
        strategist_refresh_requested = True
        strategist_refresh_reason = strategist_refresh_reason or str(
            commander_override.get("override_reason") or "repeated_hold_monitor_only"
        )
        strategist_refresh_context = {
            **strategist_refresh_context,
            **open_position_refresh_context,
        }
    if open_position_count > 0 and (commander_carry_state or commander_carry_risk_bias):
        observations = {
            **observations,
            "carry_state": commander_carry_state,
            "carry_risk_bias": commander_carry_risk_bias,
            "carry_risk_reason": commander_carry_risk_reason,
            "session_open_recovery_assessment": dict(commander_session_open_recovery),
        }
        source_priority = ["commander_carry_control", *[x for x in source_priority if x != "commander_carry_control"]]
        source_refs = {
            **source_refs,
            "carry_state": commander_carry_state,
            "carry_risk_bias": commander_carry_risk_bias,
        }
        if commander_carry_risk_reason:
            source_refs["carry_risk_reason"] = commander_carry_risk_reason
    if (
        str(phase_value or "").strip().lower() == "preopen"
        and open_position_count > 0
        and commander_carry_risk_bias in {"elevated", "urgent_exit_review"}
    ):
        strategist_refresh_requested = True
        strategist_refresh_reason = "preopen_carry_risk_review"
        strategist_refresh_context = {
            **dict(strategist_refresh_context or {}),
            **dict(open_position_refresh_context or {}),
            "refresh_scope": str(
                (open_position_refresh_context or {}).get("refresh_scope")
                or "preopen_open_position_review"
            ),
            "refresh_signal": "preopen_carry_risk_review",
            "carry_state": commander_carry_state,
            "carry_risk_bias": commander_carry_risk_bias,
            "carry_risk_reason": commander_carry_risk_reason,
            "session_open_recovery_assessment": dict(commander_session_open_recovery),
        }
        observations = {
            **observations,
            "strategist_refresh_requested": True,
            "strategist_refresh_reason": "preopen_carry_risk_review",
        }
        llm_policy = "allow_context_refresh"
        strategist_invocation = "RUN_REFRESH"
        command_intent = "MANAGE_OPEN_RISK"
        flow_instruction = "REVIEW_CARRY_POSITIONS_BEFORE_NEW_ENTRIES"
        source_priority = ["commander_preopen_carry_review", *[x for x in source_priority if x != "commander_preopen_carry_review"]]
        source_refs = {
            **source_refs,
            "strategist_refresh_reason": "preopen_carry_risk_review",
            "strategist_refresh_scope": "preopen_open_position_review",
        }
    if commander_carry_risk_bias == "urgent_exit_review":
        session_bias = "position_management"
        command_intent = "MANAGE_OPEN_RISK"
        scanner_mission = "Deprioritize new candidate exploration while carried-position risk is under urgent exit review."
        monitor_mission = "Prioritize carried-position exit review and failed session-open recovery before new entries."
        if str(flow_instruction or "").strip() in {
            "",
            "HOLD_OBSERVE",
            "NO_ACTION",
            "REUSE_STRATEGY_FRAME",
            "allow_current_flow",
            "RUN_STRATEGIST_REFRESH",
        }:
            flow_instruction = "REDUCE_CARRY_RISK_FIRST"
        if not strategist_refresh_requested:
            llm_policy = "allow_context_refresh"
    elif commander_carry_risk_bias == "elevated":
        session_bias = "position_management"
        scanner_mission = "Keep new candidate exploration narrow while carried exposure is being revalidated."
        monitor_mission = "Prioritize carried-position confirmation and recovery quality before new entries."
        if not strategist_refresh_requested and str(flow_instruction or "").strip() in {
            "",
            "HOLD_OBSERVE",
            "NO_ACTION",
            "allow_current_flow",
        }:
            flow_instruction = "PRIORITIZE_CARRY_REVIEW"
    if str(phase_value or "").strip().lower() == "preopen" and commander_carry_risk_bias in {"elevated", "urgent_exit_review"}:
        scanner_mission = "Review carried positions first and keep preopen candidate expansion narrow until carry risk is revalidated."
        monitor_mission = "Prepare session-open carry-risk response for held positions before allowing new entry exploration."
    commander_applied_policy_summary = dict(state.get("commander_applied_policy_summary") or {})
    memory_packets = load_commander_memory_packets(state=state)
    commander_memory_policy = build_commander_memory_policy(
        session_bias=session_bias,
        memory_packets=memory_packets,
        usage_disabled=_commander_memory_usage_disabled(state),
    )
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
    intraday_performance_circuit = _build_intraday_performance_circuit(
        strategist_output=strategist_output,
        memory_packets=memory_packets,
        current_day=str(state.get("day") or state.get("trading_day") or state.get("session_day") or ""),
    )
    horizon_proposal = {}
    if isinstance(strategist_output.get("strategist_horizon_proposal"), dict):
        horizon_proposal = dict(strategist_output.get("strategist_horizon_proposal") or {})
    elif isinstance(strategist_output.get("strategy_horizon_feedback"), dict):
        horizon_proposal = dict(strategist_output.get("strategy_horizon_feedback") or {})
    commander_horizon_policy = build_commander_horizon_policy(
        horizon_proposal,
        commander_context={
            "runtime_phase": str(phase_value or ""),
            "market_regime": market_regime,
            "market_regime_rail": market_regime_rail,
            "market_regime_forced_by_rail": rail_risk_off,
            "session_bias": session_bias,
            "risk_mode": risk_mode,
            "strategist_refresh_requested": strategist_refresh_requested,
            "strategist_refresh_reason": strategist_refresh_reason,
            "carry_state": commander_carry_state,
            "carry_risk_bias": commander_carry_risk_bias,
            "commander_memory_policy": dict(commander_memory_policy),
        },
        memory_packets=memory_packets,
        runtime_phase=str(phase_value or ""),
        live_validation_mode=True,
        source="commander_decision",
    )
    horizon_context = build_horizon_context(commander_horizon_policy)
    strategist_refresh_context = {
        **dict(strategist_refresh_context or {}),
        "commander_horizon_policy": dict(commander_horizon_policy),
        "horizon_context": dict(horizon_context),
    }
    if open_position_refresh_context:
        open_position_refresh_context = {
            **dict(open_position_refresh_context or {}),
            "commander_horizon_policy": dict(commander_horizon_policy),
            "horizon_context": dict(horizon_context),
        }
    observations = {
        **observations,
        "horizon_owner": "commander",
        "commander_horizon": str(commander_horizon_policy.get("strategy_horizon") or ""),
        "source_strategy_horizon": str(commander_horizon_policy.get("source_strategy_horizon") or ""),
    }
    applied_policy = dict(applied_policy)
    applied_policy["horizon"] = dict(commander_horizon_policy)
    applied_policy["commander_horizon_policy"] = dict(commander_horizon_policy)
    if list(commander_memory_policy.get("active_layers") or []):
        observations = {
            **observations,
            "memory_active_layers": list(commander_memory_policy.get("active_layers") or []),
            "memory_priority_order": list(commander_memory_policy.get("priority_order") or []),
            "symbol_memory_override_enabled": bool(commander_memory_policy.get("symbol_memory_override_enabled")),
            "scanner_memory_bias_enabled": bool(scanner_memory_bias.get("enabled")),
            "monitor_memory_bias_enabled": bool(monitor_memory_bias.get("enabled")),
        }
        source_priority = [*list(source_priority or []), *([] if "commander_memory_policy" in list(source_priority or []) else ["commander_memory_policy"])]
        source_refs = {
            **source_refs,
            "memory_active_layers": list(commander_memory_policy.get("active_layers") or []),
            "scanner_memory_bias_enabled": bool(scanner_memory_bias.get("enabled")),
            "monitor_memory_bias_enabled": bool(monitor_memory_bias.get("enabled")),
        }
    policy_sources = (
        dict(applied_policy.get("policy_sources") or {})
        if isinstance(applied_policy.get("policy_sources"), dict)
        else dict(commander_behavior_policy.get("policy_sources") or {})
        if isinstance(commander_behavior_policy.get("policy_sources"), dict)
        else {}
    )

    decision_summary = (
        f"Commander set regime={market_regime}, session_bias={session_bias}, risk_mode={risk_mode}; "
        f"allowed_playbooks={', '.join(allowed_playbooks) if allowed_playbooks else 'none'}."
    )
    if shadow_reason_summary:
        decision_summary = shadow_reason_summary
    if reason_text:
        decision_summary = f"{decision_summary} Runtime note: {str(reason_text).strip()[:180]}"
    if bool(commander_override.get("override_triggered")):
        decision_summary = (
            f"{decision_summary} Commander override requested "
            f"{str(commander_override.get('override_action') or 'force_exit_review')} "
            f"because {str(commander_override.get('override_reason') or 'open_position_risk')}."
        )
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
    if commander_carry_risk_bias:
        decision_summary = (
            f"{decision_summary} Carry control classified state={commander_carry_state or 'unknown'} "
            f"with bias={commander_carry_risk_bias}."
        )
        if commander_carry_risk_reason:
            decision_summary = f"{decision_summary} Carry reason: {commander_carry_risk_reason}."
    if list(commander_memory_policy.get("active_layers") or []):
        decision_summary = (
            f"{decision_summary} Commander memory policy active layers="
            f"{', '.join(list(commander_memory_policy.get('active_layers') or []))}."
        )
        
    strategist_call_decision = strategist_invocation
    strategist_call_reason = strategist_refresh_reason if strategist_refresh_requested else ("normal_cycle" if strategist_invocation == "RUN" else "")
    strategist_skip_reason = (
        strategist_cache_preference_reason
        if strategist_cache_preferred
        else (
            ("open_positions_present" if max_positions <= 1 else "max_positions_reached")
            if open_position_count > 0 and not entry_capacity_available
            else ""
        )
    )

    # Task 2: Explicit Strategy Decision Rules
    cache_payload_for_state = _strategist_cache_payload(state)
    cached_output_for_state = cache_payload_for_state.get("output") if isinstance(cache_payload_for_state.get("output"), dict) else {}
    generated_epoch_for_state = max(0, _coerce_int(cache_payload_for_state.get("generated_epoch"), 0))
    now_epoch_for_state = _runtime_now_epoch(state)
    cache_age_sec_for_state = max(0, now_epoch_for_state - generated_epoch_for_state) if generated_epoch_for_state > 0 else 10**9
    reuse_sec_for_state = max(0, _coerce_int(os.getenv("COMMANDER_STRATEGIST_CACHE_REUSE_SEC", "600"), 600))
    is_cache_stale = cache_age_sec_for_state > reuse_sec_for_state

    if not cached_output_for_state:
        strategy_state = "INVALID"
    elif strategist_refresh_requested:
        strategy_state = "REBUILD_REQUIRED"
    elif is_cache_stale:
        strategy_state = "STALE"
    else:
        strategy_state = "ACTIVE"

    if _is_trueish(state.get("force_refresh_strategist")):
        strategy_selection_mode = "force_fresh"
    elif strategist_refresh_requested:
        strategy_selection_mode = "prefer_fresh"
    else:
        strategy_selection_mode = "prefer_cache"

    if open_position_count > 0 and not entry_capacity_available:
        strategist_invocation_mode = "SKIP_MONITOR_ONLY"
    elif not cached_output_for_state:
        strategist_invocation_mode = "RUN"
    elif strategist_refresh_requested and is_cache_stale:
        strategist_invocation_mode = "RUN_REFRESH"
    elif strategist_refresh_requested and not is_cache_stale:
        strategist_invocation_mode = "SKIP_USE_CACHE"
    elif open_position_count == 0 and is_cache_stale:
        strategist_invocation_mode = "RUN"
    else:
        strategist_invocation_mode = "SKIP_USE_CACHE"

    # Task 4: Monitor feedback and adaptive policy
    persisted = state.get("persisted_state") if isinstance(state.get("persisted_state"), dict) else {}
    monitor_last_states = persisted.get("monitor_last_state_by_symbol") if isinstance(persisted.get("monitor_last_state_by_symbol"), dict) else {}
    
    recent_feedback = state.get("recent_strategy_feedback") if isinstance(state.get("recent_strategy_feedback"), dict) else {}
    recent_monitor_issues = list(recent_feedback.get("recent_monitor_issues") or [])
    
    blocker_counts = {}
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
                
    dominant_blocker = ""
    blocker_count = 0
    if blocker_counts:
        dominant_blocker = max(blocker_counts, key=blocker_counts.get)
        blocker_count = blocker_counts[dominant_blocker]
        
    avg_distance_to_ready = avg_distance / total_wait if total_wait > 0 else 0.0
    near_ready_flag = near_ready_count > 0
    failure_streak = blocker_count
    
    injected_feedback = state.get("mock_monitor_feedback")
    if isinstance(injected_feedback, dict):
        dominant_blocker = injected_feedback.get("dominant_blocker", dominant_blocker)
        blocker_count = injected_feedback.get("blocker_count", blocker_count)
        failure_streak = injected_feedback.get("failure_streak", failure_streak)
        near_ready_flag = injected_feedback.get("near_ready_flag", near_ready_flag)
        avg_distance_to_ready = injected_feedback.get("avg_distance_to_ready", avg_distance_to_ready)

    monitor_feedback = {
        "dominant_blocker": str(dominant_blocker),
        "blocker_count": int(blocker_count),
        "failure_streak": int(failure_streak),
        "near_ready_flag": bool(near_ready_flag),
        "avg_distance_to_ready": float(avg_distance_to_ready),
    }
    entry_control = _build_commander_entry_control(
        market_regime=market_regime,
        market_regime_rail=market_regime_rail,
        risk_mode=risk_mode,
        open_position_count=open_position_count,
        preflight=preflight,
        stress_flags=stress_flags,
        resilience=resilience,
        monitor_feedback=monitor_feedback,
        applied_policy=applied_policy,
        max_positions=max_positions,
        strategist_output=strategist_output,
        performance_circuit=intraday_performance_circuit,
    )

    adaptive_policy = {
        "entry_bias_adjustment": 0.0,
        "diversification_adjustment": 0.0,
        "reentry_penalty_adjustment": 0.0,
        "scan_aggressiveness": 0.0,
    }
    policy_adjustment_trace = []
    adaptive_feedback_allowed = str(entry_control.get("mode") or "") not in {
        "blocked_no_entry_expansion",
        "position_management_no_entry_expansion",
        "preserve_defensive_no_trade_ok",
        "preserve_guardrail_no_trade_ok",
        "risk_off_no_entry_expansion",
    }

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
    if str(entry_control.get("mode") or "") != "baseline":
        policy_adjustment_trace.append(
            f"entry_control={entry_control.get('mode')} -> {entry_control.get('reason')}"
        )

    scanner_policy = {
        "avoid_recent_symbol": False,
        "recent_symbol_penalty": round(max(0.0, 0.05 + adaptive_policy["reentry_penalty_adjustment"]), 6),
        "diversification_bias": round(
            max(0.0, (0.02 if adaptive_feedback_allowed else 0.0) + adaptive_policy["diversification_adjustment"]),
            6,
        ),
        "entry_bias_cap": round(max(0.0, 0.0 + adaptive_policy["entry_bias_adjustment"]), 6),
        "scan_aggressiveness": round(max(0.0, adaptive_policy["scan_aggressiveness"]), 6),
        "allow_same_symbol_reentry": True,
        "reentry_score_gap_threshold": 0.03,
        "market_representative_guard": {
            "enabled": True,
            "symbols": ["005930", "000660"],
            "penalty": 0.04,
            "max_penalty": 0.12,
            "near_tie_gap": 0.06,
            "top_value_dominance_min": 0.55,
            "weak_confirmation_max": 1,
            "strong_confirmation_min": 2,
            "bypass_when_strong_confirmation": True,
            "apply_when_top_value_only": True,
            "policy_source": "commander_default",
        },
        "max_priority_rank": int(entry_control.get("max_priority_rank") if entry_control.get("max_priority_rank") not in (None, "") else 10),
        "max_runner_ups": int(entry_control.get("max_runner_ups") if entry_control.get("max_runner_ups") not in (None, "") else 9),
        "entry_control": dict(entry_control),
    }
    observations = {
        **observations,
        "entry_control_mode": str(entry_control.get("mode") or ""),
        "entry_control_decision": str(entry_control.get("decision") or ""),
        "entry_control_reason": str(entry_control.get("reason") or ""),
        "entry_control_max_priority_rank": int(entry_control.get("max_priority_rank") if entry_control.get("max_priority_rank") not in (None, "") else 10),
        "entry_control_dynamic_band": bool(entry_control.get("allow_dynamic_entry_band")),
        "open_position_count": int(open_position_count),
        "max_positions": int(max_positions),
        "multi_position_capacity_remaining": max(0, int(max_positions) - int(open_position_count)),
    }
    source_refs = {
        **source_refs,
        "entry_control": {
            "source": "commander_decision.monitor_feedback",
            "dominant_blocker": str(entry_control.get("dominant_blocker") or ""),
            "failure_streak": int(entry_control.get("failure_streak") or 0),
            "market_supportive": bool(entry_control.get("market_supportive")),
            "mode": str(entry_control.get("mode") or ""),
        },
    }
    if "commander_entry_control" not in list(source_priority or []):
        source_priority = [*list(source_priority or []), "commander_entry_control"]
    if str(entry_control.get("mode") or "") not in {"", "baseline"}:
        decision_summary = (
            f"{decision_summary} Entry control {entry_control.get('mode')} "
            f"because {entry_control.get('reason')}."
        )
    shadow_runtime = _ensure_commander_shadow_runtime(state)
    prior_context = dict(shadow_runtime.get("prior_context") or {}) if isinstance(shadow_runtime.get("prior_context"), dict) else {}
    prior_monitor_entry_policy_summary = (
        dict(prior_context.get("monitor_entry_policy_summary") or {})
        if isinstance(prior_context.get("monitor_entry_policy_summary"), dict)
        else {}
    )
    current_monitor_entry_policy_summary = dict(
        applied_policy_meta.get("monitor_entry_policy_summary")
        or _summarize_monitor_entry_policy(applied_policy)
        or {}
    )
    if (
        strategist_refresh_requested
        and open_position_refresh_context
        and not current_monitor_entry_policy_summary
        and prior_monitor_entry_policy_summary
    ):
        current_monitor_entry_policy_summary = dict(prior_monitor_entry_policy_summary)
    strategist_refresh_evaluated = bool(
        str(commander_override.get("override_action") or "").strip().lower() == "strategist_refresh"
        or strategist_invocation == "RUN_REFRESH"
    )
    strategist_refresh_policy_delta_fields = (
        _monitor_entry_policy_delta_fields(
            prior_monitor_entry_policy_summary,
            current_monitor_entry_policy_summary,
        )
        if strategist_refresh_evaluated
        else []
    )
    if strategist_refresh_requested:
        strategist_refresh_context = {
            **dict(strategist_refresh_context or {}),
            "prior_monitor_entry_policy_summary": dict(prior_monitor_entry_policy_summary),
            "current_monitor_entry_policy_summary": dict(current_monitor_entry_policy_summary),
            "carry_state": commander_carry_state,
            "carry_risk_bias": commander_carry_risk_bias,
            "carry_risk_reason": commander_carry_risk_reason,
            "session_open_recovery_assessment": dict(commander_session_open_recovery),
        }
    strategist_refresh_effective = bool(
        strategist_refresh_evaluated and bool(strategist_refresh_policy_delta_fields)
    )

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
    snapshot = state.get("portfolio_snapshot") if isinstance(state.get("portfolio_snapshot"), dict) else {}
    positions = snapshot.get("positions")
    if isinstance(positions, dict):
        rows = list(positions.values())
    elif isinstance(positions, list):
        rows = positions
    else:
        rows = []

    persisted = state.get("persisted_state") if isinstance(state.get("persisted_state"), dict) else {}
    monitor_last_state = (
        persisted.get("monitor_last_state_by_symbol")
        if isinstance(persisted.get("monitor_last_state_by_symbol"), dict)
        else {}
    )
    prior_hold_counts = (
        persisted.get("commander_open_position_hold_repeat_by_symbol")
        if isinstance(persisted.get("commander_open_position_hold_repeat_by_symbol"), dict)
        else {}
    )
    prior_refresh_cooldowns = (
        persisted.get("commander_open_position_refresh_cooldown_until_by_symbol")
        if isinstance(persisted.get("commander_open_position_refresh_cooldown_until_by_symbol"), dict)
        else {}
    )
    overnight_decisions = (
        persisted.get("overnight_decision_by_symbol")
        if isinstance(persisted.get("overnight_decision_by_symbol"), dict)
        else {}
    )
    position_peak_price = (
        persisted.get("position_peak_price")
        if isinstance(persisted.get("position_peak_price"), dict)
        else {}
    )
    position_strategy_context = (
        persisted.get("position_strategy_context")
        if isinstance(persisted.get("position_strategy_context"), dict)
        else {}
    )
    last_exit_sweep_by_symbol = (
        persisted.get("commander_pre_entry_exit_sweep_last_checked_by_symbol")
        if isinstance(persisted.get("commander_pre_entry_exit_sweep_last_checked_by_symbol"), dict)
        else {}
    )
    profit_activation_ratio = _resolve_profit_protection_activation_ratio(state)

    next_hold_counts: Dict[str, int] = {}
    next_refresh_cooldowns: Dict[str, int] = {}
    reasons: list[str] = []
    rows_summary: list[Dict[str, Any]] = []
    repeated_hold_rows: list[Dict[str, Any]] = []
    anomaly_found = False
    risk_found = False
    max_hold_repeat = 0
    min_effective_loss_ratio: float | None = None
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

        raw_loss_ratio = (
            float((current_price / avg_price) - 1.0)
            if current_price > 0.0 and avg_price > 0.0
            else None
        )
        unrealized_loss_ratio = (
            float(unrealized_pnl / float(avg_price * qty))
            if avg_price > 0.0 and qty > 0
            else None
        )
        candidate_loss_ratios = [x for x in (raw_loss_ratio, unrealized_loss_ratio) if x is not None]
        if account_pnl_ratio is not None and not price_anomaly:
            candidate_loss_ratios.append(float(account_pnl_ratio))
        effective_loss_ratio = min(candidate_loss_ratios) if candidate_loss_ratios else None
        current_profit_ratio = _position_current_profit_ratio(
            raw_price_ratio=raw_loss_ratio,
            account_pnl_ratio=account_pnl_ratio,
            price_anomaly=price_anomaly,
        )
        peak_price = max(
            _runtime_float(row.get("peak_price"), 0.0),
            _runtime_float(row.get("high_water_mark"), 0.0),
            _runtime_float(position_peak_price.get(symbol), 0.0) if isinstance(position_peak_price, dict) else 0.0,
            current_price,
            avg_price,
        )
        peak_profit_ratio = float((peak_price / avg_price) - 1.0) if peak_price > 0.0 and avg_price > 0.0 else None
        profit_giveback_ratio = (
            max(0.0, float(peak_profit_ratio) - float(current_profit_ratio))
            if peak_profit_ratio is not None and current_profit_ratio is not None
            else 0.0
        )
        profit_protection_priority = 0
        if peak_profit_ratio is not None and peak_profit_ratio >= profit_activation_ratio:
            profit_protection_priority = 2
        elif current_profit_ratio is not None and current_profit_ratio >= profit_activation_ratio:
            profit_protection_priority = 2
        elif current_profit_ratio is not None and current_profit_ratio >= (profit_activation_ratio * 0.75):
            profit_protection_priority = 1
        last_exit_sweep_epoch = max(0, _coerce_int(last_exit_sweep_by_symbol.get(symbol), 0))

        previous = monitor_last_state.get(symbol) if isinstance(monitor_last_state, dict) else {}
        previous_posture = str((previous or {}).get("posture") or "").strip().lower()
        previous_reason = str((previous or {}).get("reason") or "")
        previous_active_exit_axis = str((previous or {}).get("active_exit_axis") or "")
        previous_entry_state = dict((previous or {}).get("entry_state") or {})
        hold_repeat_count = max(0, _coerce_int(prior_hold_counts.get(symbol), 0))
        if previous_posture == "hold":
            hold_repeat_count += 1
        else:
            hold_repeat_count = 0
        next_hold_counts[symbol] = int(hold_repeat_count)
        max_hold_repeat = max(max_hold_repeat, int(hold_repeat_count))
        refresh_cooldown_until = max(0, _coerce_int(prior_refresh_cooldowns.get(symbol), 0))
        if refresh_cooldown_until > now_epoch:
            next_refresh_cooldowns[symbol] = int(refresh_cooldown_until)

        if effective_loss_ratio is not None:
            min_effective_loss_ratio = (
                float(effective_loss_ratio)
                if min_effective_loss_ratio is None
                else min(float(min_effective_loss_ratio), float(effective_loss_ratio))
            )

        if price_anomaly:
            anomaly_found = True
            reasons.append(f"{symbol}:price_anomaly:{price_anomaly_reason}")
        if effective_loss_ratio is not None and effective_loss_ratio <= -0.01:
            risk_found = True
            reasons.append(f"{symbol}:loss_threshold:{effective_loss_ratio:.4f}")
        if hold_repeat_count >= 3:
            reasons.append(f"{symbol}:hold_repeat:{hold_repeat_count}")
            repeated_hold_rows.append(
                {
                    "symbol": symbol,
                    "hold_repeat_count": int(hold_repeat_count),
                    "refresh_cooldown_until": int(refresh_cooldown_until) if refresh_cooldown_until > 0 else 0,
                    "refresh_cooldown_remaining_sec": max(0, int(refresh_cooldown_until - now_epoch))
                    if refresh_cooldown_until > now_epoch
                    else 0,
                }
            )
        position_age_seconds = _resolve_position_age_seconds(state, row, symbol)
        symbol_strategy_context = (
            position_strategy_context.get(symbol)
            if isinstance(position_strategy_context, dict)
            else {}
        )
        symbol_strategy_context = (
            symbol_strategy_context if isinstance(symbol_strategy_context, dict) else {}
        )
        horizon_revision_allowed = bool(
            symbol_strategy_context.get("horizon_revision_allowed", True)
        )
        horizon_review_due = horizon_revision_allowed and position_review_due(
            symbol_strategy_context,
            position_age_seconds=position_age_seconds,
            now_epoch=now_epoch,
        )
        position_horizon_state = ensure_horizon_state(
            symbol_strategy_context
        )
        carry_control = _assess_position_carry_control(
            state=state,
            symbol=symbol,
            hold_repeat_count=int(hold_repeat_count),
            position_age_seconds=position_age_seconds,
            effective_loss_ratio=effective_loss_ratio,
            monitor_reason=previous_reason,
            active_exit_axis=previous_active_exit_axis,
            entry_state=previous_entry_state,
            overnight_decision=overnight_decisions.get(symbol) if isinstance(overnight_decisions, dict) else {},
        )
        if str(carry_control.get("carry_risk_bias") or "") != "normal":
            reasons.append(
                f"{symbol}:carry_bias:{str(carry_control.get('carry_risk_bias') or '')}:{str(carry_control.get('carry_risk_reason') or '')}"
            )
        if bool(carry_control.get("closeout_unresolved_flatten_required")):
            reasons.append(f"{symbol}:closeout_unresolved_flatten_required")

        rows_summary.append(
            {
                "symbol": symbol,
                "qty": int(qty),
                "effective_loss_ratio": effective_loss_ratio,
                "raw_loss_ratio": raw_loss_ratio,
                "current_profit_ratio": current_profit_ratio,
                "peak_price": peak_price if peak_price > 0.0 else None,
                "peak_profit_ratio": peak_profit_ratio,
                "profit_giveback_ratio": profit_giveback_ratio,
                "profit_protection_priority": int(profit_protection_priority),
                "profit_protection_activation_ratio": float(profit_activation_ratio),
                "last_exit_sweep_epoch": int(last_exit_sweep_epoch),
                "account_pnl_ratio": account_pnl_ratio,
                "price_anomaly": bool(price_anomaly),
                "price_anomaly_reason": str(price_anomaly_reason),
                "hold_repeat_count": int(hold_repeat_count),
                "posture": str(previous_posture or ""),
                "reason": str(previous_reason or ""),
                "active_exit_axis": str(previous_active_exit_axis or ""),
                "entry_state": _compact_monitor_entry_state_for_refresh(previous_entry_state),
                "position_age_seconds": position_age_seconds,
                "horizon_review_due": bool(horizon_review_due),
                "horizon_revision_allowed": bool(horizon_revision_allowed),
                "position_horizon_state": dict(position_horizon_state),
                "refresh_cooldown_until": int(refresh_cooldown_until) if refresh_cooldown_until > 0 else None,
                "refresh_cooldown_remaining_sec": max(0, int(refresh_cooldown_until - now_epoch))
                if refresh_cooldown_until > now_epoch
                else 0,
                "carry_state": str(carry_control.get("carry_state") or ""),
                "carry_risk_bias": str(carry_control.get("carry_risk_bias") or ""),
                "carry_risk_reason": str(carry_control.get("carry_risk_reason") or ""),
                "overnight_carry_approved": bool(carry_control.get("overnight_carry_approved")),
                "overnight_carry_reason": str(carry_control.get("overnight_carry_reason") or ""),
                "closeout_unresolved_flatten_required": bool(
                    carry_control.get("closeout_unresolved_flatten_required")
                ),
                "session_open_recovery_assessment": dict(carry_control.get("session_open_recovery_assessment") or {}),
            }
        )

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
    override_triggered = bool(
        closeout_unresolved_found
        or anomaly_found
        or risk_found
        or max_hold_repeat >= 3
        or horizon_review_found
    )
    override_action = ""
    override_reason = ""
    override_suppressed = False
    override_suppressed_reason = ""
    refresh_cooldown_symbol = ""
    refresh_cooldown_until = 0
    refresh_cooldown_remaining_sec = 0
    position_refresh_due = False
    position_refresh_trigger = ""
    force_exit_review_pending = False
    open_position_risk_review_reason = ""
    strategist_refresh_context: Dict[str, Any] = {}

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
            selected_row = (
                _select_open_position_refresh_candidate(require_loss=True)
                if risk_found
                else _select_open_position_refresh_candidate(require_loss=False)
            )
            refresh_cooldown_symbol = str(selected_row.get("symbol") or "")
            refresh_cooldown_until = max(0, _coerce_int(selected_row.get("refresh_cooldown_until"), 0))
            refresh_trigger = (
                "loss_threshold_exceeded"
                if risk_found
                else "horizon_review_due"
                if bool(selected_row.get("horizon_review_due"))
                else "repeated_hold_monitor_only"
            )
            if selected_row and refresh_cooldown_until > now_epoch:
                refresh_cooldown_remaining_sec = max(0, int(refresh_cooldown_until - now_epoch))
                override_suppressed = True
                override_suppressed_reason = (
                    "loss_threshold_refresh_cooldown"
                    if risk_found
                    else "repeated_hold_monitor_only_refresh_cooldown"
                )
                reasons.append(
                    f"{refresh_cooldown_symbol}:refresh_cooldown_active:{refresh_cooldown_remaining_sec}"
                )
                if risk_found:
                    override_action = "force_exit_review"
                    override_reason = "loss_threshold_exceeded"
                    force_exit_review_pending = True
                    open_position_risk_review_reason = "loss_threshold_exceeded"
                    position_refresh_trigger = str(refresh_trigger)
                else:
                    override_triggered = False
            elif selected_row:
                override_action = "strategist_refresh"
                override_reason = str(refresh_trigger)
                position_refresh_due = True
                position_refresh_trigger = str(refresh_trigger)
                force_exit_review_pending = bool(risk_found)
                open_position_risk_review_reason = "loss_threshold_exceeded" if risk_found else ""
                refresh_cooldown_until = int(now_epoch + _OPEN_POSITION_STRATEGIST_REFRESH_COOLDOWN_SEC)
                refresh_cooldown_remaining_sec = int(_OPEN_POSITION_STRATEGIST_REFRESH_COOLDOWN_SEC)
                if refresh_cooldown_symbol:
                    next_refresh_cooldowns[refresh_cooldown_symbol] = int(refresh_cooldown_until)
                strategist_refresh_context = _build_open_position_strategist_refresh_context(
                    {
                        "refresh_cooldown_symbol": refresh_cooldown_symbol,
                        "hold_repeat_count_max": max_hold_repeat,
                        "effective_loss_ratio_min": min_effective_loss_ratio,
                        "price_anomaly_flag": anomaly_found,
                        "refresh_trigger": str(refresh_trigger),
                        "refresh_cadence_sec": int(_OPEN_POSITION_STRATEGIST_REFRESH_COOLDOWN_SEC),
                        "force_exit_review_pending": bool(force_exit_review_pending),
                        "open_position_risk_review_reason": str(open_position_risk_review_reason),
                        "reason_chain": list(reasons),
                        "positions": rows_summary,
                    }
                )
            elif risk_found:
                override_action = "force_exit_review"
                override_reason = "loss_threshold_exceeded"
                force_exit_review_pending = True
                open_position_risk_review_reason = "loss_threshold_exceeded"

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
