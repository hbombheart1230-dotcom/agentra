from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, TypedDict

from libs.contracts.agent_output_values import (
    _safe_float,
    _safe_int,
    _clip,
    _listify,
    _dict,
    _dict_list,
    _scanner_candidate_visibility_limit,
    _dedupe_text,
    _format_trace_number,
    _is_present,
)
from libs.runtime.dates import kst_day_str, to_kst
from libs.runtime.decision_observability import (
    build_entry_blocker_surface,
    build_commander_route_observability_surface,
    build_monitor_no_trade_surface,
    build_scanner_monitor_handoff_surface,
    build_strategist_policy_resolution_surface,
)
from libs.runtime.commander_memory_application_trace import (
    build_monitor_commander_memory_application_trace,
    build_scanner_commander_memory_application_trace,
)
from libs.runtime.strategist_explanation import build_strategist_explanation_fields
from libs.runtime.strategist_packet_visibility import build_strategist_memory_packet_visibility
import sys as _r3_sys
from libs.contracts.commander_output_context import (
    commander_route_runtime_facts,
)
from libs.contracts.commander_output_policy import (
    commander_decision_refresh_facts,
    commander_applied_policy_provenance,
)
from libs.contracts.commander_output_fields import (
    commander_artifact_route_fields,
    commander_artifact_decision_fields,
    commander_artifact_shadow_refresh_fields,
    commander_artifact_policy_fields,
    commander_artifact_observability_fields,
)
from libs.contracts.scanner_output_context import (
    scanner_row_feature_sources,
    scanner_applied_policy_evidence,
    scanner_policy_bias_evidence,
)
from libs.contracts.scanner_output_fields import (
    scanner_artifact_pool_ranking_fields,
    scanner_artifact_policy_compatibility_fields,
    scanner_artifact_bias_trace_fields,
    scanner_artifact_selection_trace_fields,
    scanner_artifact_policy_guard_fields,
    scanner_artifact_refs_preview_fields,
)
from libs.contracts.strategist_output_context import (
    strategist_market_news_inputs,
    strategist_decision_theme_policy_facts,
    strategist_plan_horizon_facts,
)
from libs.contracts.strategist_output_fields import (
    strategist_artifact_market_playbook_fields,
    strategist_artifact_context_frame_fields,
    strategist_artifact_theme_news_fallback_fields,
    strategist_artifact_commander_context_fields,
    strategist_artifact_horizon_guidance_fields,
)
from libs.contracts.strategist_output_plan_fields import (
    strategist_artifact_plan_policy_fields,
    strategist_artifact_trace_handoff_feedback_fields,
    strategist_artifact_llm_policy_bias_fields,
    strategist_artifact_refs_macro_fields,
)
from libs.contracts.monitor_output_context import (
    monitor_state_surface_sources,
    monitor_no_trade_policy_trace,
    monitor_entry_cascade_handoff,
    monitor_focus_context_projection,
)
from libs.contracts.monitor_output_decision import (
    monitor_decision_rule_evidence,
)
from libs.contracts.monitor_output_memory_bias import (
    monitor_memory_bias_application,
)
from libs.contracts.monitor_output_fields import (
    monitor_artifact_decision_fields,
    monitor_artifact_no_trade_fields,
    monitor_artifact_handoff_focus_fields,
)
from libs.contracts.monitor_output_policy_fields import (
    monitor_artifact_policy_memory_fields,
    monitor_artifact_signal_entry_fields,
)
from libs.contracts.monitor_output_exit_fields import (
    monitor_artifact_trace_evaluation_fields,
    monitor_artifact_price_exit_metric_fields,
    monitor_artifact_pnl_hold_exit_fields,
)


AGENT_OUTPUT_SCHEMA_VERSION = "agent_output.v1"
AGENT_VALIDATION_SCHEMA_VERSION = "agent_output_validation.v1"


class AgentOutput(TypedDict, total=False):
    schema_version: str
    agent: str
    run_id: str
    day: str
    ts: str
    phase: str
    symbol: str
    status: str
    evidence_refs: Dict[str, Any]
    source_refs: Dict[str, Any]
    validation: Dict[str, Any]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_strategist_trace_summary(
    *,
    strategist_output: Dict[str, Any],
    global_signal: Dict[str, Any],
    macro_overlay: Dict[str, Any],
    news_context: Dict[str, Any],
    themes: List[str],
    avoid_themes: List[str],
    market_regime: str,
    market_sentiment: str,
    playbook: str,
) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import strategist_projections as _parts
    return _parts._build_strategist_trace_summary(facade=_r3_sys.modules[__name__], strategist_output=strategist_output, global_signal=global_signal, macro_overlay=macro_overlay, news_context=news_context, themes=themes, avoid_themes=avoid_themes, market_regime=market_regime, market_sentiment=market_sentiment, playbook=playbook)

def _build_strategist_decision_frame(
    *,
    state: Dict[str, Any],
    strategist_output: Dict[str, Any],
    market_regime: str,
    market_sentiment: str,
    playbook: str,
    themes: List[str],
    avoid_themes: List[str],
) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import strategist_projections as _parts
    return _parts._build_strategist_decision_frame(facade=_r3_sys.modules[__name__], state=state, strategist_output=strategist_output, market_regime=market_regime, market_sentiment=market_sentiment, playbook=playbook, themes=themes, avoid_themes=avoid_themes)

def _build_strategist_news_evidence_ranked(
    *,
    state: Dict[str, Any],
    strategist_output: Dict[str, Any],
    news_context: Dict[str, Any],
    market_news_context: Dict[str, Any],
    candidate_news_context: Dict[str, Any],
) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import strategist_projections as _parts
    return _parts._build_strategist_news_evidence_ranked(facade=_r3_sys.modules[__name__], state=state, strategist_output=strategist_output, news_context=news_context, market_news_context=market_news_context, candidate_news_context=candidate_news_context)

def _build_global_sentiment_signal_payload(
    *,
    state: Dict[str, Any],
    global_signal: Dict[str, Any],
    macro_overlay: Dict[str, Any],
) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import strategist_projections as _parts
    return _parts._build_global_sentiment_signal_payload(facade=_r3_sys.modules[__name__], state=state, global_signal=global_signal, macro_overlay=macro_overlay)

def _build_scanner_trace_summary(
    *,
    symbol: str,
    selected_rank: int,
    universe_size: int,
    selected_score_total: float,
    margin_vs_second: float,
    selected_score_breakdown: Dict[str, Any],
    selected: Dict[str, Any],
    candidate_preview: List[Dict[str, Any]],
    selection_summary: str,
    scanner_bias_applied: bool = False,
    scanner_bias_summary: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import scanner_projections as _parts
    return _parts._build_scanner_trace_summary(facade=_r3_sys.modules[__name__], symbol=symbol, selected_rank=selected_rank, universe_size=universe_size, selected_score_total=selected_score_total, margin_vs_second=margin_vs_second, selected_score_breakdown=selected_score_breakdown, selected=selected, candidate_preview=candidate_preview, selection_summary=selection_summary, scanner_bias_applied=scanner_bias_applied, scanner_bias_summary=scanner_bias_summary)

def _build_scanner_candidate_ranking_table(
    *,
    state: Dict[str, Any],
    candidate_preview: List[Dict[str, Any]],
) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import scanner_projections as _parts
    return _parts._build_scanner_candidate_ranking_table(facade=_r3_sys.modules[__name__], state=state, candidate_preview=candidate_preview)

def _build_scanner_candidate_selection_reason(
    *,
    state: Dict[str, Any],
    selected_symbol: str,
    selected_rank: int,
    selected_score_total: float,
    margin_vs_second: float,
    critical_positive_factors: List[str],
    critical_negative_factors: List[str],
    selection_summary: str,
    runner_ups: List[Dict[str, Any]],
    selected: Dict[str, Any],
) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import scanner_projections as _parts
    return _parts._build_scanner_candidate_selection_reason(facade=_r3_sys.modules[__name__], state=state, selected_symbol=selected_symbol, selected_rank=selected_rank, selected_score_total=selected_score_total, margin_vs_second=margin_vs_second, critical_positive_factors=critical_positive_factors, critical_negative_factors=critical_negative_factors, selection_summary=selection_summary, runner_ups=runner_ups, selected=selected)

def _monitor_decision_summary(
    *,
    decision_phase: str,
    primary_reason_text: str,
    threshold_snapshot: Dict[str, Any],
    signal_snapshot: Dict[str, Any],
    missing_inputs: List[str],
) -> str:
    from libs.contracts.agent_output_parts import monitor_decision_summary as _owner
    return _owner.monitor_decision_summary(decision_phase=decision_phase, primary_reason_text=primary_reason_text, threshold_snapshot=threshold_snapshot, signal_snapshot=signal_snapshot, missing_inputs=missing_inputs, facade=_r3_sys.modules[__name__])


def _phase(state: Dict[str, Any]) -> str:
    from libs.contracts.agent_output_parts import artifact_metadata as _owner
    return _owner.phase(state, facade=_r3_sys.modules[__name__])


def _run_ts(state: Dict[str, Any]) -> str:
    for key in ("started_at", "ts", "tick_ts_iso", "now_iso"):
        value = str(state.get(key) or "").strip()
        if value:
            return value
    tick_epoch = _safe_int(state.get("tick_ts"), 0)
    if tick_epoch > 0:
        return datetime.fromtimestamp(tick_epoch, tz=timezone.utc).isoformat()
    return _utc_now_iso()


def _parse_day_from_timestamp(value: str) -> str:
    from libs.contracts.agent_output_parts import artifact_metadata as _owner
    return _owner.parse_day_from_timestamp(value, facade=_r3_sys.modules[__name__])


def _run_day(state: Dict[str, Any]) -> str:
    for key in ("day", "trade_day", "session_day", "runtime_day"):
        value = str(state.get(key) or "").strip()
        if len(value) == 10 and value[4:5] == "-" and value[7:8] == "-":
            return value
    for key in ("started_at", "ts", "tick_ts_iso", "now_iso"):
        resolved = _parse_day_from_timestamp(str(state.get(key) or "").strip())
        if resolved:
            return resolved
    tick_epoch = _safe_int(state.get("tick_ts"), 0)
    if tick_epoch > 0:
        return kst_day_str(datetime.fromtimestamp(tick_epoch, tz=timezone.utc))
    return kst_day_str(to_kst(datetime.now(timezone.utc)))


def _base_output(state: Dict[str, Any], *, agent: str, symbol: str = "", status: str = "ok") -> AgentOutput:
    return {
        "schema_version": AGENT_OUTPUT_SCHEMA_VERSION,
        "agent": str(agent or "").strip(),
        "run_id": str(state.get("run_id") or "").strip(),
        "day": _run_day(state),
        "ts": _run_ts(state),
        "phase": _phase(state),
        "symbol": str(symbol or "").strip(),
        "status": str(status or "ok").strip(),
    }


def _required_keys_for_agent(agent: str) -> List[str]:
    from libs.contracts.agent_output_parts import artifact_validation as _owner
    return _owner.required_keys_for_agent(agent, facade=_r3_sys.modules[__name__])


def _required_keys_for_artifact(obj: Dict[str, Any]) -> List[str]:
    from libs.contracts.agent_output_parts import artifact_validation as _owner
    return _owner.required_keys_for_artifact(obj, facade=_r3_sys.modules[__name__])


def validate_artifact(artifact: Dict[str, Any]) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import artifact_validation as _owner
    return _owner.validate_artifact(artifact, facade=_r3_sys.modules[__name__])


def build_strategist_output_artifact(state: Dict[str, Any]) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import artifact_build_strategist as _owner
    return _owner.build_strategist_output_artifact(state=state, facade=_r3_sys.modules[__name__])


def build_scanner_output_artifact(state: Dict[str, Any]) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import artifact_build_scanner as _owner
    return _owner.build_scanner_output_artifact(state=state, facade=_r3_sys.modules[__name__])


def build_monitor_output_artifact(state: Dict[str, Any]) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import artifact_build_monitor as _owner
    return _owner.build_monitor_output_artifact(state=state, facade=_r3_sys.modules[__name__])


def build_supervisor_output_artifact(
    state: Dict[str, Any],
    *,
    order: Dict[str, Any],
    allowed: bool,
    reason: str,
    details: Dict[str, Any] | None = None,
    strategy_policy_summary: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import artifact_build_supervisor_executor as _owner
    return _owner.build_supervisor_output_artifact(state=state, order=order, allowed=allowed, reason=reason, details=details, strategy_policy_summary=strategy_policy_summary, facade=_r3_sys.modules[__name__])


def build_executor_output_artifact(
    state: Dict[str, Any],
    *,
    execution: Dict[str, Any],
    order: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import artifact_build_supervisor_executor as _owner
    return _owner.build_executor_output_artifact(state=state, execution=execution, order=order, facade=_r3_sys.modules[__name__])


def _build_commander_shadow_artifact_summary(
    state: Dict[str, Any],
    *,
    mode: str,
    phase: str,
    path: str,
    status: str,
    reason: str = "",
) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import artifact_build_shadow as _owner
    return _owner.build_commander_shadow_artifact_summary(state=state, mode=mode, phase=phase, path=path, status=status, reason=reason, facade=_r3_sys.modules[__name__])


def build_commander_output_artifact(
    state: Dict[str, Any],
    *,
    mode: str,
    phase: str,
    path: str,
    status: str,
    reason: str = "",
) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import artifact_build_commander as _owner
    return _owner.build_commander_output_artifact(state=state, mode=mode, phase=phase, path=path, status=status, reason=reason, facade=_r3_sys.modules[__name__])


def _commander_shadow_has_open_order(state: Dict[str, Any]) -> Any:
    from libs.contracts.agent_output_parts import commander_shadow_checks as _owner
    return _owner.has_open_order(state, facade=_r3_sys.modules[__name__])


def _commander_shadow_actual_runtime(state: Dict[str, Any], *, path: str) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import commander_shadow_runtime as _commander_shadow_runtime_owner

    return _commander_shadow_runtime_owner.build_actual_runtime(state, path=path, facade=_r3_sys.modules[__name__])


def _commander_shadow_observations(state: Dict[str, Any], *, path: str) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import commander_shadow_runtime as _commander_shadow_runtime_owner

    return _commander_shadow_runtime_owner.build_observations(state, path=path, facade=_r3_sys.modules[__name__])


def _gate_pass(metrics: Dict[str, Any], passed_checks: List[str], failed_checks: List[str], key: str) -> Any:
    from libs.contracts.agent_output_parts import commander_shadow_checks as _owner
    return _owner.gate_pass(metrics, passed_checks, failed_checks, key, facade=_r3_sys.modules[__name__])


def _score_from_checks(*, passed_checks: List[str], failed_checks: List[str], fallback: Any) -> Any:
    from libs.contracts.agent_output_parts import commander_shadow_checks as _owner
    return _owner.score_from_checks(passed_checks=passed_checks, failed_checks=failed_checks, fallback=fallback, facade=_r3_sys.modules[__name__])


def _commander_shadow_monitor_gate_details(state: Dict[str, Any]) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import commander_shadow_evidence as _owner
    return _owner.build_monitor_gate_details(state, facade=_r3_sys.modules[__name__])


def _commander_shadow_context_delta_summary(state: Dict[str, Any], *, observations: Dict[str, Any]) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import commander_shadow_evidence as _owner
    return _owner.build_context_delta_summary(state, observations=observations, facade=_r3_sys.modules[__name__])


def _commander_shadow_no_trade_reason_code(
    state: Dict[str, Any],
    *,
    observations: Dict[str, Any],
    actual_runtime: Dict[str, Any],
    path: str,
) -> str:
    from libs.contracts.agent_output_parts.commander_shadow_advice import no_trade_reason_code
    return no_trade_reason_code(state, observations=observations, actual_runtime=actual_runtime, path=path, facade=_r3_sys.modules[__name__])


def _commander_shadow_strategist_recommendation(
    *,
    no_trade_reason_code: str,
    observations: Dict[str, Any],
) -> str:
    from libs.contracts.agent_output_parts.commander_shadow_advice import strategist_recommendation
    return strategist_recommendation(no_trade_reason_code=no_trade_reason_code, observations=observations)


def _commander_shadow_llm_call_advice(
    *,
    strategist_action_recommendation: str,
    observations: Dict[str, Any],
    state: Dict[str, Any],
) -> str:
    from libs.contracts.agent_output_parts import commander_shadow_advice_extended as _owner
    return _owner.llm_call_advice(
        strategist_action_recommendation=strategist_action_recommendation,
        observations=observations,
        state=state,
        facade=_r3_sys.modules[__name__],
    )


def _commander_shadow_suggested_action(
    *,
    strategist_action_recommendation: str,
    llm_call_advice: str,
    no_trade_reason_code: str,
) -> str:
    from libs.contracts.agent_output_parts import commander_shadow_advice_extended as _owner
    return _owner.suggested_action(
        strategist_action_recommendation=strategist_action_recommendation,
        llm_call_advice=llm_call_advice,
        no_trade_reason_code=no_trade_reason_code,
        facade=_r3_sys.modules[__name__],
    )


def _commander_shadow_next_action_recommendation(
    *,
    strategist_action_recommendation: str,
    llm_call_advice: str,
    no_trade_reason_code: str,
    actual_runtime: Dict[str, Any],
) -> str:
    from libs.contracts.agent_output_parts import commander_shadow_advice_extended as _owner
    return _owner.next_action_recommendation(
        strategist_action_recommendation=strategist_action_recommendation,
        llm_call_advice=llm_call_advice,
        no_trade_reason_code=no_trade_reason_code,
        actual_runtime=actual_runtime,
        facade=_r3_sys.modules[__name__],
    )


def _commander_shadow_reason_summary(
    *,
    no_trade_reason_code: str,
    observations: Dict[str, Any],
    actual_runtime: Dict[str, Any],
) -> str:
    from libs.contracts.agent_output_parts import commander_shadow_advice_extended as _owner
    return _owner.reason_summary(
        no_trade_reason_code=no_trade_reason_code,
        observations=observations,
        actual_runtime=actual_runtime,
        facade=_r3_sys.modules[__name__],
    )


def _commander_shadow_recommendation_gap(
    *,
    strategist_action_recommendation: str,
    llm_call_advice: str,
    actual_runtime: Dict[str, Any],
) -> str:
    from libs.contracts.agent_output_parts import commander_shadow_advice_extended as _owner
    return _owner.recommendation_gap(
        strategist_action_recommendation=strategist_action_recommendation,
        llm_call_advice=llm_call_advice,
        actual_runtime=actual_runtime,
        facade=_r3_sys.modules[__name__],
    )


def _commander_shadow_pre_strategist_snapshot(
    *,
    state: Dict[str, Any],
    observations: Dict[str, Any],
    context_delta_summary: Dict[str, Any],
    strategist_action_recommendation: str,
    llm_call_advice: str,
) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import commander_shadow_assessments as _owner
    return _owner.pre_strategist_snapshot(
        state=state,
        observations=observations,
        context_delta_summary=context_delta_summary,
        strategist_action_recommendation=strategist_action_recommendation,
        llm_call_advice=llm_call_advice,
        facade=_r3_sys.modules[__name__],
    )


def _commander_shadow_post_strategist_assessment(
    *,
    state: Dict[str, Any],
    actual_runtime: Dict[str, Any],
    context_delta_summary: Dict[str, Any],
    recommendation_gap: str,
) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import commander_shadow_assessments as _owner
    return _owner.post_strategist_assessment(
        state=state,
        actual_runtime=actual_runtime,
        context_delta_summary=context_delta_summary,
        recommendation_gap=recommendation_gap,
        facade=_r3_sys.modules[__name__],
    )


def _commander_shadow_post_monitor_assessment(
    *,
    actual_runtime: Dict[str, Any],
    monitor_gate_details: Dict[str, Any],
) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import commander_shadow_assessments as _owner
    return _owner.post_monitor_assessment(
        actual_runtime=actual_runtime,
        monitor_gate_details=monitor_gate_details,
        facade=_r3_sys.modules[__name__],
    )


def _commander_shadow_end_of_cycle_summary(
    *,
    no_trade_reason_code: str,
    reason_summary: str,
    actual_runtime: Dict[str, Any],
    next_action_recommendation: str,
    recommendation_gap: str,
) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import commander_shadow_cycle as _owner
    return _owner.end_of_cycle_summary(no_trade_reason_code=no_trade_reason_code, reason_summary=reason_summary, actual_runtime=actual_runtime, next_action_recommendation=next_action_recommendation, recommendation_gap=recommendation_gap, facade=_r3_sys.modules[__name__])


def build_commander_shadow_artifact(
    state: Dict[str, Any],
    *,
    mode: str,
    phase: str,
    path: str,
    status: str,
    reason: str = "",
) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import artifact_build_shadow as _owner
    return _owner.build_commander_shadow_artifact(state=state, mode=mode, phase=phase, path=path, status=status, reason=reason, facade=_r3_sys.modules[__name__])
