from __future__ import annotations

"""Canonical Strategist node for integrated runtime.

Role boundary:
- owns strategic framing (themes/sectors, sentiment context, candidate hints)
- prepares strategist outputs for scanner/monitor handoff
- does not execute orders
"""

import os
import json
import ast
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from libs.core.evidence_identity import stable_evidence_id
from libs.core.path_isolation import isolate_canonical_path_for_pytest
from libs.ai.strategist_config import (
    strategist_llm_requested,
    strategist_llm_strict,
    strategist_runtime_settings,
)
from libs.data_quality.signal_contract import SIGNAL_STATUS_FALLBACK, make_signal
from libs.llm.model_names import normalize_openrouter_model_name
from libs.llm.llm_router import LLMRouter
from libs.market.global_sentiment import compute_global_sentiment_signal
from libs.news.news_pipeline import collect_news_items, score_news_sentiment_signal
from libs.performance.strategy_memory import load_strategy_memory_hint
from libs.research.evidence_ledger import (
    record_decision_bridge,
    record_llm_prompt,
    record_llm_response,
    record_raw_input,
)
from libs.research.strategy_feedback_builder import build_recent_strategy_feedback
from libs.runtime.decision_trace import append_decision_trace
from libs.runtime.decision_observability import build_strategist_policy_resolution_surface
from libs.runtime.strategist_packet_visibility import (
    build_strategist_memory_packet_visibility,
    summarize_read_model_facts,
)
from libs.runtime.strategist.llm.stage_contracts import build_stage_specific_contract
from libs.runtime.monitor_policy import (
    MonitorEntryPolicy,
    build_monitor_entry_policy_bundle,
    build_default_monitor_entry_policy,
    normalize_monitor_entry_policy,
)
from libs.runtime.scanner_bias import normalize_scanner_bias_context, summarize_scanner_bias_context
from libs.runtime.canonical_artifacts import (
    strategist_llm_stage_descriptor,
    write_llm_artifact_bundle,
    write_llm_stage_manifest_entry,
    write_strategist_artifact,
)
from libs.runtime.regime import classify_regime_v2
from libs.runtime.strategist_explanation import build_strategist_explanation_fields
from libs.runtime.strategist_feedback_trace import build_feedback_application_trace
from libs.runtime.strategy_horizon_feedback import (
    build_commander_horizon_policy,
    build_horizon_context,
    build_strategy_horizon_feedback,
)
from libs.strategies.candidates.fallback_pool import resolve_fallback_symbols
from libs.strategies.contracts import StrategistOutput, coerce_strategist_output
from libs.strategies.candidates.market_rank import MarketRankCandidateGenerator
from libs.strategies.candidates.market_rank import TopPicksCandidateGenerator
from libs.strategies.universe_builder import build_candidate_universe
from libs.reporting.trade_read_model import build_trade_read_model
from libs.reporting.reporter_feedback import build_strategist_feedback_packet
from libs.reporting.symbol_read_model import build_symbol_read_model
from libs.runtime.commander_memory_policy import build_commander_memory_policy
from libs.runtime.memory_packet_loader import load_commander_memory_packets
from libs.runtime.monitor_memory_bias import build_monitor_memory_bias, summarize_monitor_memory_bias
from libs.runtime.scanner_memory_bias import build_scanner_memory_bias, summarize_scanner_memory_bias
from libs.runtime.quant.contracts import TACTIC_IDS, TACTICAL_SUBTYPES
from libs.runtime.quant.tactics import (
    TACTIC_DEFAULT_RUNNER_UP_RANK,
    canonical_tactic_key,
    default_tactic_for_playbook,
    normalize_playbook as normalize_tactic_playbook,
    normalize_tactic_id,
    normalize_tactical_subtype as normalize_quant_tactical_subtype,
)
from libs.runtime.quant.context import build_strategist_quant_context
from libs.runtime.news_event_intelligence import (
    build_news_event_intelligence,
    compact_news_event_intelligence_for_llm,
)
from libs.runtime.strategist_input_quality import build_strategist_input_quality_context
from libs.read.kiwoom_theme_reader import build_theme_strength_packet
import sys as _r3_sys
from libs.runtime.strategist.context.memory import (
    _strategy_memory_usage_disabled_r3_impl,
    _neutralize_ambiguous_playbook_memory_r3_impl,
    _symbol_memory_model_has_signal_r3_impl,
    _compact_recent_strategy_feedback_for_llm_r3_impl,
    _compact_reporter_feedback_for_llm_r3_impl,
    _compact_strategy_memory_for_llm_r3_impl,
    _hide_stage1_symbol_memory_r3_impl,
    _pick_playbook_r3_impl,
)
from libs.runtime.strategist.context.common_values import (
    _env_int_r3_impl,
    _nested_mapping_value_r3_impl,
    _attach_quant_context_to_strategy_refresh_trace_r3_impl,
    _append_unique_text_r3_impl,
    _signal_score_r3_impl,
)
from libs.runtime.strategist.llm.response_contract_parsing import (
    _extract_contract_from_prose_r3_impl,
    _extract_json_object_r3_impl,
    _classify_llm_parse_failure_r3_impl,
)
from libs.runtime.strategist.llm.text_fragment_helpers import (
    _strip_fenced_block_r3_impl,
    _parse_text_list_fragment_r3_impl,
)
from libs.runtime.strategist.context.value_helpers import (
    _clamp_r3_impl,
    _to_float_r3_impl,
    _to_int_r3_impl,
    _round_optional_r3_impl,
    _unit_score_r3_impl,
    _is_trueish_r3_impl,
)
from libs.runtime.strategist.context.market_inputs import (
    _resolve_top_n_candidates_r3_impl,
    _candidates_from_state_r3_impl,
    _extract_market_context_inputs_r3_impl,
    _market_structure_label_r3_impl,
    _compose_regime_score_r3_impl,
    _scanner_priority_r3_impl,
    _scanner_bias_r3_impl,
    _build_scanner_bias_context_seed_r3_impl,
    _macro_stress_overlay_r3_impl,
    _apply_macro_stress_to_monitor_frame_r3_impl,
    _build_market_regime_summary_r3_impl,
)
from libs.runtime.strategist.context.market_key_events import (
    _key_events_r3_impl,
)
from libs.runtime.strategist.llm.stage_reviews import (
    _stage_text_list_r3_impl,
    _stage_bool_r3_impl,
    _stage_float_r3_impl,
    _normalize_stage2_selected_symbol_review_r3_impl,
    _normalize_stage3_hold_review_r3_impl,
    _normalize_stage4_carry_review_r3_impl,
)
from libs.runtime.strategist.llm.override_normalization import (
    _derive_stage_specific_common_overrides_r3_impl,
    _normalize_llm_overrides_r3_impl,
)
from libs.runtime.strategist.llm.adjustment_directives import (
    _infer_policy_adjustment_direction_r3_impl,
    _normalize_policy_adjustment_surface_r3_impl,
    _clean_directive_reason_r3_impl,
    _normalize_strategy_adjustment_directives_r3_impl,
    _normalize_rejected_strategy_reasons_r3_impl,
    _sanitize_reason_list_r3_impl,
)
from libs.runtime.strategist.llm.candidate_watch_overrides import (
    _normalize_candidate_watch_policy_r3_impl,
    _extract_ai_overrides_r3_impl,
    _merge_override_text_list_r3_impl,
)
from libs.runtime.strategist.policy.monitor_entry_policy import (
    _summarize_monitor_entry_policy_for_adjustment_r3_impl,
    _monitor_entry_policy_adjustment_delta_fields_r3_impl,
    _focus_axes_from_strings_r3_impl,
    _compact_monitor_entry_policy_baseline_for_llm_r3_impl,
    _monitor_policy_r3_impl,
    _strategy_policy_score_weights_r3_impl,
    _strategy_policy_entry_policy_r3_impl,
    _build_strategy_policy_r3_impl,
)
from libs.runtime.strategist.policy.monitor_entry_policy_seed import (
    _build_strategist_monitor_entry_policy_seed_r3_impl,
    _build_monitor_entry_policy_rationale_r3_impl,
    _build_strategy_policy_provenance_r3_impl,
)
from libs.runtime.strategist.context.commander_refresh_context import (
    _build_llm_commander_refresh_context_r3_impl,
    _compact_top_metric_map_r3_impl,
    _compact_performance_summary_map_r3_impl,
    _compact_pattern_performance_for_llm_r3_impl,
    _compact_scalar_mapping_for_llm_r3_impl,
    _compact_pattern_rows_for_llm_r3_impl,
    _compact_trade_read_model_for_llm_r3_impl,
)
from libs.runtime.strategist.context.symbol_read_models import (
    _compact_symbol_read_model_for_llm_r3_impl,
    _compact_read_model_facts_for_llm_r3_impl,
    _compact_candidate_context_for_refresh_r3_impl,
    _slim_refresh_context_for_llm_r3_impl,
)
from libs.runtime.strategist.context.news_compaction import (
    _compact_news_sample_for_llm_r3_impl,
    _compact_global_signal_for_llm_r3_impl,
    _news_signal_label_r3_impl,
    _news_item_title_for_llm_r3_impl,
    _compact_news_signal_summary_for_llm_r3_impl,
    _selected_symbol_news_signal_for_llm_r3_impl,
    _merge_news_collection_symbols_r3_impl,
    _build_market_news_query_targets_r3_impl,
)
from libs.runtime.strategist.context.news_context import (
    _build_market_news_query_reasoning_r3_impl,
    _news_context_summary_r3_impl,
    _merge_news_contexts_r3_impl,
    _sample_news_for_evidence_r3_impl,
    _rank_news_evidence_rows_r3_impl,
    _global_sentiment_breakdown_payload_r3_impl,
    _merge_news_samples_r3_impl,
)
from libs.runtime.strategist.output.strategy_scores_and_summary import (
    _operator_summary_for_llm_r3_impl,
    _deterministic_strategy_scores_r3_impl,
    _normalize_strategy_scores_r3_impl,
)
from libs.runtime.strategist.output.commander_context_and_plan import (
    _build_commander_context_summary_r3_impl,
    _build_strategist_plan_r3_impl,
    _augment_strategy_fields_r3_impl,
)
from libs.runtime.strategist.output.strategic_answers import (
    _build_strategic_answers_r3_impl,
)
from libs.runtime.strategist.context.theme_compaction import (
    _compact_theme_strength_for_llm_r3_impl,
    _theme_packet_summary_for_llm_r3_impl,
    _extract_themes_r3_impl,
    _theme_to_news_queries_r3_impl,
    _theme_news_query_terms_r3_impl,
    _theme_component_symbols_for_news_r3_impl,
    _extract_theme_symbol_index_r3_impl,
    _merge_theme_symbol_map_r3_impl,
)
from libs.runtime.strategist.context.theme_packet import (
    _merge_theme_packet_into_state_r3_impl,
    _extract_theme_names_from_any_r3_impl,
    _theme_packet_available_themes_r3_impl,
    _resolve_selected_themes_from_api_r3_impl,
    _build_theme_strategy_surface_r3_impl,
)
from libs.runtime.strategist.context.theme_strength import (
    _theme_strength_map_r3_impl,
    _avoid_themes_r3_impl,
)
from libs.runtime.strategist.policy.exit_and_defaults import (
    _default_policy_r3_impl,
    _exit_policy_r3_impl,
)
from libs.runtime.strategist.policy.scanner_policy import (
    _scanner_source_policy_r3_impl,
)
from libs.runtime.strategist.context.node_context_projection import (
    strat_ctx_candidates_universe_candidates,
    strat_ctx_news_collection_policy_news_collection_s,
    strat_ctx_avoid_themes_exit_policy,
    strat_ctx_fallback_theme_hints_pre_llm_commander_c,
)
from libs.runtime.strategist.policy.node_policy_projection import (
    strat_policy_exit_policy_monitor_entry_policy,
    strat_policy_candidate_watch_policy_rejected_strategy,
    strat_policy_commander_context_policy_adjustment,
    strat_policy_commander_context_commander_horizon_poli,
)
from libs.runtime.strategist.output.node_output_projection import (
    strat_output_value_state_scanner_guidance,
    strat_output_performance_summary_strategist_output,
    strat_output_value_state_strategist_llm,
)
from libs.runtime.strategist.output.node_trace_projection import (
    strat_trace_ranked_candidate_news_ranked_market_news,
    strat_trace_decision_frame_payload,
)
from libs.runtime.strategist.policy.global_risk_adjustment import (
    adjust_policy_for_global_sentiment,
)
from libs.runtime.strategist.context.news_signal_fallbacks import (
    news_exception_fallback_signals,
    news_disabled_signals,
    summarize_news_contexts,
)
from libs.runtime.strategist.context.candidate_rerank import (
    rerank_candidates_by_news_and_global,
)
from libs.runtime.strategist.context.theme_candidate_projection import (
    project_theme_candidate_inputs,
)
from libs.runtime.strategist.context.regime_scoring import (
    score_market_regime_and_sentiment,
)
from libs.runtime.strategist.context.llm_input_payload import (
    assemble_frame_llm_payload,
    build_theme_selection_raw_input,
)
from libs.runtime.strategist.policy.llm_override_application import (
    apply_ai_overrides_to_frame,
)
from libs.runtime.strategist.policy.strategy_policy_annotation import (
    annotate_strategy_policy_market_scanner,
    attach_horizon_to_commander_context,
    attach_horizon_to_monitor_policy_and_plan,
)
from libs.runtime.strategist.output.strategist_output_core_fields import (
    fill_strategist_output_core,
)
from libs.runtime.strategist.output.strategist_output_stage_reviews import (
    fill_strategist_output_stage_reviews,
)
from libs.runtime.strategist.output.strategist_output_policy_commander_fields import (
    fill_strategist_output_policy_and_commander,
)
from libs.runtime.strategist.output.strategist_output_explanations import (
    fill_strategist_output_explanations,
)
from libs.runtime.strategist.output.node_event_payloads import (
    build_market_context_snapshot_payload,
    build_news_evidence_ranked_payload,
    build_strategist_summary_log_payload,
    build_strategic_frame_trace_payload,
    build_strategist_decision_bridge_output,
)


def _is_trueish(v: Any) -> bool:
    return _is_trueish_r3_impl(v, facade=_r3_sys.modules[__name__])


def _env_bool(name: str, default: bool = False) -> bool:
    raw = str(os.getenv(name, "1" if default else "0") or "").strip().lower()
    if not raw:
        return bool(default)
    return raw in ("1", "true", "yes", "y", "on")


def _strategy_memory_usage_disabled(policy_or_payload: Any | None = None) -> bool:
    return _strategy_memory_usage_disabled_r3_impl(policy_or_payload,
        facade=_r3_sys.modules[__name__])


def _to_int(v: Any, default: int) -> int:
    return _to_int_r3_impl(v, default, facade=_r3_sys.modules[__name__])


def _env_int(key: str) -> int | None:
    return _env_int_r3_impl(key, facade=_r3_sys.modules[__name__])


def _nested_mapping_value(mapping: Any, *path: str) -> Any:
    return _nested_mapping_value_r3_impl(mapping, *path, facade=_r3_sys.modules[__name__])


def _neutralize_ambiguous_playbook_memory(memory: Dict[str, Any]) -> Dict[str, Any]:
    return _neutralize_ambiguous_playbook_memory_r3_impl(memory, facade=_r3_sys.modules[__name__])


def _load_recent_strategy_feedback(state: Dict[str, Any], policy: Dict[str, Any]) -> Dict[str, Any]:
    applied_policy = state.get("applied_policy") if isinstance(state.get("applied_policy"), dict) else {}
    strategist_policy = applied_policy.get("strategist") if isinstance(applied_policy.get("strategist"), dict) else {}
    memory_feedback_policy = (
        strategist_policy.get("memory_feedback")
        if isinstance(strategist_policy.get("memory_feedback"), dict)
        else {}
    )
    if isinstance(memory_feedback_policy, dict) and memory_feedback_policy.get("enabled") is not None:
        enabled_raw = memory_feedback_policy.get("enabled")
        policy_source = str(memory_feedback_policy.get("policy_source") or "commander_applied_policy")
    elif strategist_policy.get("memory_feedback_enabled") is not None:
        enabled_raw = strategist_policy.get("memory_feedback_enabled")
        policy_source = "strategist_policy_fallback"
    elif policy.get("use_strategy_memory_feedback") is not None:
        enabled_raw = policy.get("use_strategy_memory_feedback")
        policy_source = "policy_fallback"
    else:
        enabled_raw = True
        policy_source = "default_true"
    enabled = _is_trueish(enabled_raw)
    if not enabled:
        return {
            "feedback_window_size": 0,
            "recent_theme_performance": {},
            "recent_playbook_performance": {},
            "recent_monitor_issues": [],
            "recent_scanner_issues": [],
            "recent_guard_patterns": [],
            "recent_overtrading_patterns": [],
            "recent_reporter_summary": [],
            "top_recent_strengths": [],
            "top_recent_weaknesses": [],
            "suggested_report_focus": [],
            "advisory_only": True,
            "status": "disabled",
            "policy_source": str(policy_source),
        }
    raw_window = _nested_mapping_value(memory_feedback_policy, "recent_runs")
    if raw_window is not None:
        policy_source = str(memory_feedback_policy.get("policy_source") or "commander_applied_policy")
    elif strategist_policy.get("memory_feedback_recent_runs") is not None:
        raw_window = strategist_policy.get("memory_feedback_recent_runs")
        policy_source = "strategist_policy_fallback"
    elif policy.get("strategy_memory_recent_runs") is not None:
        raw_window = policy.get("strategy_memory_recent_runs")
        policy_source = "policy_fallback"
    else:
        raw_window = 12
    last_n_runs = max(1, _to_int(raw_window, 12))
    feedback = build_recent_strategy_feedback(
        last_n_runs,
        as_of_day=_resolve_state_day(state),
    )
    feedback.setdefault(
        "status",
        "ok" if int(feedback.get("feedback_window_size") or 0) > 0 else "empty",
    )
    feedback["requested_window_size"] = int(last_n_runs)
    feedback["policy_source"] = str(policy_source)
    return feedback


def _iso_day_from_value(value: Any) -> str:
    text = str(value or "").strip()
    if len(text) >= 10 and text[4:5] == "-" and text[7:8] == "-":
        return text[:10]
    try:
        epoch = int(float(value))
    except Exception:
        epoch = 0
    if epoch > 0:
        return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("%Y-%m-%d")
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _resolve_state_day(state: Dict[str, Any]) -> str:
    for key in ("started_at", "ts", "now_iso", "tick_ts"):
        if state.get(key) not in (None, ""):
            return _iso_day_from_value(state.get(key))
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _load_strategy_memory_advisory(state: Dict[str, Any], policy: Dict[str, Any]) -> Dict[str, Any]:
    enabled_raw = (
        policy.get("use_strategy_performance_memory")
        if policy.get("use_strategy_performance_memory") is not None
        else os.getenv("USE_STRATEGY_PERFORMANCE_MEMORY", "true")
    )
    enabled = _is_trueish(enabled_raw)
    if not enabled:
        return {
            "schema_version": "strategy_memory.v1",
            "status": "disabled",
            "best_playbooks": [],
            "worst_playbooks": [],
            "market_condition_bias": {},
            "recent_failures": [],
            "recent_success_patterns": [],
            "playbook_performance_snapshot": {},
            "pattern_performance_snapshot": {},
            "advisory_only": True,
        }

    auto_build_raw = (
        policy.get("strategy_performance_auto_build")
        if policy.get("strategy_performance_auto_build") is not None
        else os.getenv("STRATEGY_PERFORMANCE_AUTO_BUILD", "false")
    )
    auto_build = _is_trueish(auto_build_raw)
    reports_root = isolate_canonical_path_for_pytest(str(state.get("reports_root") or os.getenv("REPORTS_ROOT", "reports")).strip() or "reports", canonical_path="reports", isolated_name="reports")
    day = str(
        policy.get("strategy_performance_day")
        or state.get("day")
        or _resolve_state_day(state)
    ).strip()
    try:
        memory = load_strategy_memory_hint(
            reports_root=reports_root,
            day=day,
            auto_build=bool(auto_build),
        )
    except Exception as exc:
        return {
            "schema_version": "strategy_memory.v1",
            "status": "error",
            "error": str(exc),
            "day": str(day),
            "best_playbooks": [],
            "worst_playbooks": [],
            "market_condition_bias": {},
            "recent_failures": [],
            "recent_success_patterns": [],
            "playbook_performance_snapshot": {},
            "pattern_performance_snapshot": {},
            "advisory_only": True,
        }
    if not isinstance(memory, dict):
        return {
            "schema_version": "strategy_memory.v1",
            "status": "empty",
            "day": str(day),
            "best_playbooks": [],
            "worst_playbooks": [],
            "market_condition_bias": {},
            "recent_failures": [],
            "recent_success_patterns": [],
            "playbook_performance_snapshot": {},
            "pattern_performance_snapshot": {},
            "advisory_only": True,
        }
    out = dict(memory)
    out.setdefault("schema_version", "strategy_memory.v1")
    out.setdefault("day", str(day))
    out.setdefault("status", "ok" if out.get("best_playbooks") or out.get("worst_playbooks") else "empty")
    out.setdefault("best_playbooks", [])
    out.setdefault("worst_playbooks", [])
    out.setdefault("market_condition_bias", {})
    out.setdefault("recent_failures", [])
    out.setdefault("recent_success_patterns", [])
    out.setdefault("playbook_performance_snapshot", {})
    out.setdefault("pattern_performance_snapshot", {})
    out.setdefault("advisory_only", True)
    out = _neutralize_ambiguous_playbook_memory(out)
    age_days = _to_int(out.get("age_days"), 0)
    if age_days > 7:
        # Preserve the artifact for audit, but do not let old daily evidence
        # become the current directional authority after a no-trade stretch.
        out["status"] = "stale"
        out["directional_bias_usable"] = False
        out["best_playbooks"] = []
        out["worst_playbooks"] = []
        out["recent_failures"] = []
        out["recent_success_patterns"] = []
    else:
        out["directional_bias_usable"] = True
    return out


def _resolve_top_n_candidates(policy: Dict[str, Any]) -> int:
    return _resolve_top_n_candidates_r3_impl(policy, facade=_r3_sys.modules[__name__])


def _strip_fenced_block(text: str) -> str:
    return _strip_fenced_block_r3_impl(text, facade=_r3_sys.modules[__name__])


def _parse_text_list_fragment(raw: Any) -> List[str]:
    return _parse_text_list_fragment_r3_impl(raw, facade=_r3_sys.modules[__name__])


def _extract_contract_from_prose(text: str) -> Dict[str, Any]:
    return _extract_contract_from_prose_r3_impl(text, facade=_r3_sys.modules[__name__])


def _extract_json_object(text: str) -> Dict[str, Any]:
    return _extract_json_object_r3_impl(text, facade=_r3_sys.modules[__name__])


def _classify_llm_parse_failure(raw: Any) -> str:
    return _classify_llm_parse_failure_r3_impl(raw, facade=_r3_sys.modules[__name__])


def _resolve_strategist_frame_llm_enabled(policy: Dict[str, Any]) -> bool:
    if os.getenv("PYTEST_CURRENT_TEST") and policy.get("strategist_frame_use_llm") is None:
        raw_env = str(os.getenv("STRATEGIST_FRAME_USE_LLM", "") or "").strip()
        provider = str((strategist_runtime_settings(policy) or {}).get("provider") or "").strip().lower()
        if not raw_env and provider not in ("openai", "http", "api"):
            return False
    return strategist_llm_requested(policy)


def _resolve_strategist_frame_llm_strict_enabled(policy: Dict[str, Any]) -> bool:
    return strategist_llm_strict(policy)


def _stage_text_list(raw: Any, *, limit: int = 8, upper: bool = False) -> List[str]:
    return _stage_text_list_r3_impl(raw, limit=limit, upper=upper, facade=_r3_sys.modules[__name__])


def _stage_bool(raw: Any, default: bool = False) -> bool:
    return _stage_bool_r3_impl(raw, default, facade=_r3_sys.modules[__name__])


def _stage_float(raw: Any, default: float | None = None) -> float | None:
    return _stage_float_r3_impl(raw, default, facade=_r3_sys.modules[__name__])


def _normalize_stage2_selected_symbol_review(raw: Dict[str, Any]) -> Dict[str, Any]:
    return _normalize_stage2_selected_symbol_review_r3_impl(raw, facade=_r3_sys.modules[__name__])


def _normalize_stage3_hold_review(raw: Dict[str, Any]) -> Dict[str, Any]:
    return _normalize_stage3_hold_review_r3_impl(raw, facade=_r3_sys.modules[__name__])


def _normalize_stage4_carry_review(raw: Dict[str, Any]) -> Dict[str, Any]:
    return _normalize_stage4_carry_review_r3_impl(raw, facade=_r3_sys.modules[__name__])


def _derive_stage_specific_common_overrides(out: Dict[str, Any]) -> None:
    return _derive_stage_specific_common_overrides_r3_impl(out, facade=_r3_sys.modules[__name__])


def _stage_specific_role_boundary(call_kind: str) -> str:
    if call_kind == "selected_symbol_tactical_refresh":
        return (
            "You may recommend how to watch the Scanner-selected symbol and runner-ups, "
            "but you do not approve orders. Monitor calculates the final entry signal and Commander owns hard risk gates. "
        )
    if call_kind == "stale_intraday_hold_review":
        return (
            "You review an already-held intraday position for hold, tighter exit handling, or exit pressure, "
            "but you do not place or approve sell orders. Monitor and Commander retain hard exit authority. "
        )
    if call_kind == "end_of_day_carry_review":
        return (
            "You review held positions near the close for flatten/carry risk, "
            "but you do not bypass deterministic closeout, broker truth, weekend, or risk controls. "
        )
    return "Do not select final stock and do not produce order instructions. "


def _stage_specific_task_requirement(call_kind: str) -> str:
    if call_kind == "selected_symbol_tactical_refresh":
        return (
            "Your role is to compare Scanner rank #1 with compressed runner-ups, use selected_symbol_memory only as bounded symbol-specific evidence when memory is enabled, "
            "and output selected_symbol_decision, target_symbol, target_rank, runner_up_order, monitor_instruction, entry_policy_delta, memory_usage, market_regime_rail, news_quality, risk_off_exception_conditions, news_event_intelligence_usage, commander_actionability, confidence, and reason. "
        )
    if call_kind == "stale_intraday_hold_review":
        return (
            "Your role is to review whether the held position thesis is still intact, whether exit pressure is rising, and whether the current operating horizon should be maintained, shortened, or extended for this symbol. "
            "Do not blindly preserve the entry horizon. Stage 3 may revise only same-session horizons; overnight carry remains a Stage 4 decision. "
            "Output hold_review_decision, horizon_action, current_horizon, proposed_horizon, revised_hold_window, exit_pressure, thesis_status, evidence_confidence, data_quality, monitor_adjustment, priority_exit_triggers, next_check_minutes, and reason. "
        )
    if call_kind == "end_of_day_carry_review":
        return (
            "Your role is to review each held position near session close for carry risk versus same-day flattening. "
            "Output carry_review, portfolio_level_decision, and risk_note. "
        )
    return (
        "Your role is to choose exactly ONE playbook, provide a short rationale, produce a realistic and bounded monitor_entry_policy, propose tactical strategy detail, propose candidate_watch_policy, and produce explicit strategy_adjustment_directives that indicate what should change, what should be maintained, and why. "
    )


def _stage_specific_user_requirement(call_kind: str) -> str:
    if call_kind == "selected_symbol_tactical_refresh":
        return (
            "Decision requirements: return the Stage 2 selected-symbol tactical refresh contract only. "
            "Compare rank #1 and runner-ups in one call, decide whether to watch rank #1, avoid rank #1, tighten rank #1 gates, cascade to runner-ups, or no-trade. "
            "Always include market_regime_rail, news_quality, and risk_off_exception_conditions so Commander and reports can audit whether market/news context changed the recommendation. "
            "If news_event_intelligence exists, include news_event_intelligence_usage as observation-only evidence usage; it must not imply direct BUY/SELL or gate bypass. "
            "Do not output a direct BUY/SELL. "
        )
    if call_kind == "stale_intraday_hold_review":
        return (
            "Decision requirements: return the Stage 3 stale intraday hold review contract only. "
            "Decide hold, tighten_exit, exit_now, or wait_until_next_check using the held position thesis, net PnL, VWAP, drawdown, time decay, and market context. "
            "Explicitly decide whether the active same-session horizon should be maintained, shortened, or extended. Do not authorize overnight carry in Stage 3. "
            "Keep the reason tied to the held symbol under review and do not attribute unrelated candidate or market theme labels to that position. "
            "Do not output a direct SELL order. "
        )
    if call_kind == "end_of_day_carry_review":
        return (
            "Decision requirements: return the Stage 4 end-of-day carry review contract only. "
            "For each held position decide carry_overnight, flatten_today, or reduce_or_flatten, then provide a portfolio-level carry decision. "
            "Do not bypass hard closeout, weekend, broker-truth, or risk controls. "
        )
    return (
        "Decision requirements: choose exactly ONE playbook, provide a short but concrete rationale, produce tactical_strategy, strategy_scores, rejected_strategy_reasons, candidate_watch_policy, a realistic and bounded monitor_entry_policy, and strategy_adjustment_directives that clearly state whether to maintain, tighten, relax, rebalance, deprioritize, prefer, or switch, which fields, axes, or playbooks are affected, and why this action is justified by deterministic evidence. "
    )


def _stage_specific_llm_contract(call_kind: str, base_contract: Dict[str, Any]) -> Dict[str, Any]:
    return build_stage_specific_contract(call_kind, base_contract)


def _normalize_llm_overrides(raw: Dict[str, Any]) -> Dict[str, Any]:
    return _normalize_llm_overrides_r3_impl(raw, facade=_r3_sys.modules[__name__])


_POLICY_ADJUSTMENT_COMPARE_FIELDS = (
    "timeframe_minutes",
    "breakout_lookback",
    "volume_lookback",
    "volume_ratio_min",
    "min_extended_from_vwap_pct",
    "max_extended_from_vwap_pct",
    "pullback_min_pct",
    "pullback_max_pct",
    "reclaim_tolerance_pct",
    "breakout_buffer_pct",
    "intent_cooldown_sec",
    "require_vwap_reclaim",
    "require_rebound",
)


def _summarize_monitor_entry_policy_for_adjustment(policy: Dict[str, Any]) -> Dict[str, Any]:
    return _summarize_monitor_entry_policy_for_adjustment_r3_impl(policy,
        facade=_r3_sys.modules[__name__])


def _monitor_entry_policy_adjustment_delta_fields(
    baseline_summary: Dict[str, Any],
    current_summary: Dict[str, Any],
) -> List[str]:
    return _monitor_entry_policy_adjustment_delta_fields_r3_impl(baseline_summary, current_summary,
        facade=_r3_sys.modules[__name__])


def _infer_policy_adjustment_direction(
    baseline_summary: Dict[str, Any],
    current_summary: Dict[str, Any],
) -> str:
    return _infer_policy_adjustment_direction_r3_impl(baseline_summary, current_summary,
        facade=_r3_sys.modules[__name__])


def _symbol_memory_model_has_signal(model: Dict[str, Any]) -> bool:
    return _symbol_memory_model_has_signal_r3_impl(model, facade=_r3_sys.modules[__name__])


def _build_symbol_refresh_memory_excerpt(
    selected_symbol: str,
    read_model_facts: Dict[str, Any] | None = None,
    reports_root: str | Path | None = None,
) -> Dict[str, Any]:
    symbol = str(selected_symbol or "").strip().upper()
    facts = dict(read_model_facts or {}) if isinstance(read_model_facts, dict) else {}
    symbol_patterns = facts.get("symbol_patterns") if isinstance(facts.get("symbol_patterns"), dict) else {}
    model = dict(symbol_patterns.get(symbol) or {}) if isinstance(symbol_patterns.get(symbol), dict) else {}
    if not symbol:
        return {}
    if not _symbol_memory_model_has_signal(model):
        root = Path(str(reports_root or "").strip()) if str(reports_root or "").strip() else None
        if root is not None:
            trades_root = root / "trades" if root.name.lower() != "trades" else root
            try:
                persisted_model = build_symbol_read_model(str(trades_root), symbol, persisted_only=True)
            except TypeError:
                persisted_model = build_symbol_read_model(str(trades_root), symbol)
            if isinstance(persisted_model, dict) and _symbol_memory_model_has_signal(persisted_model):
                model = dict(persisted_model)
    if not _symbol_memory_model_has_signal(model):
        return {}

    repeated_failure_pattern = []
    for item in list(model.get("repeated_failure_pattern") or [])[:3]:
        if not isinstance(item, dict):
            continue
        repeated_failure_pattern.append(
            {
                "type": str(item.get("type") or "").strip(),
                "value": str(item.get("value") or "").strip(),
                "count": int(item.get("count") or 0),
            }
        )

    recent_success_pattern = []
    for item in list(model.get("recent_success_pattern") or [])[:2]:
        if not isinstance(item, dict):
            continue
        recent_success_pattern.append(
            {
                "playbook": str(item.get("playbook") or "").strip(),
                "entry_reason": str(item.get("entry_reason") or "").strip(),
                "exit_reason": str(item.get("exit_reason") or "").strip(),
                "count": int(item.get("count") or 0),
            }
        )

    data_quality = model.get("data_quality") if isinstance(model.get("data_quality"), dict) else {}
    return {
        "symbol": symbol,
        "trade_count": int(model.get("trade_count") or 0),
        "closed_trade_count": int(model.get("closed_trade_count") or 0),
        "win_rate": _round_optional(model.get("win_rate"), 4),
        "avg_pnl_pct": _round_optional(model.get("avg_pnl_pct"), 4),
        "avg_hold_duration_sec": _round_optional(model.get("avg_hold_duration_sec"), 2),
        "dominant_playbook": str(model.get("dominant_playbook") or ""),
        "dominant_monitor_blocker": str(model.get("dominant_monitor_blocker") or ""),
        "dominant_exit_reason": str(model.get("dominant_exit_reason") or ""),
        "repeated_failure_pattern": repeated_failure_pattern,
        "recent_success_pattern": recent_success_pattern,
        "data_quality": {
            "data_source": str(data_quality.get("data_source") or ""),
            "unknown_fields_ratio": _round_optional(data_quality.get("unknown_fields_ratio"), 4),
        },
    }



def _build_llm_commander_refresh_context(
    commander_context: Dict[str, Any],
    read_model_facts: Dict[str, Any] | None = None,
    reports_root: str | Path | None = None,
) -> Dict[str, Any]:
    return _build_llm_commander_refresh_context_r3_impl(commander_context, read_model_facts,
        reports_root, facade=_r3_sys.modules[__name__])


def _normalize_policy_adjustment_surface(
    *,
    raw_adjustment: Any,
    baseline_summary: Dict[str, Any],
    current_summary: Dict[str, Any],
    refresh_requested: bool,
    recent_strategy_feedback: Dict[str, Any],
) -> Dict[str, Any]:
    return _normalize_policy_adjustment_surface_r3_impl(raw_adjustment=raw_adjustment,
        baseline_summary=baseline_summary, current_summary=current_summary,
        refresh_requested=refresh_requested, recent_strategy_feedback=recent_strategy_feedback,
        facade=_r3_sys.modules[__name__])


_PLAYBOOK_ACTIONS = {"maintain", "prefer", "deprioritize", "switch"}
_ENTRY_POLICY_ACTIONS = {"maintain", "tighten", "relax", "rebalance"}
_MONITOR_FOCUS_ACTIONS = {"maintain", "increase_focus", "decrease_focus", "shift_focus"}
_SELECTED_SYMBOL_BIAS_ACTIONS = {"none", "prefer_pullback", "avoid_breakout", "prefer_reclaim", "avoid_extension"}
_REFRESH_ACTIONS = {"none", "refresh_for_holding", "refresh_for_repeated_hold", "refresh_for_exit_axis_mismatch"}
_MONITOR_FOCUS_AXES = {"reclaim", "pullback", "volume", "breakout", "extension", "exit_axis"}
_GENERIC_DIRECTIVE_TOKENS = ("slightly", "carefully", "appropriately", "in general")


def _clean_directive_reason(value: Any, *, default: str) -> str:
    return _clean_directive_reason_r3_impl(value, default=default, facade=_r3_sys.modules[__name__])


def _focus_axes_from_strings(*values: Any) -> List[str]:
    return _focus_axes_from_strings_r3_impl(*values, facade=_r3_sys.modules[__name__])


def _normalize_strategy_adjustment_directives(
    *,
    raw_directives: Any,
    playbook: str,
    policy_adjustment: Dict[str, Any],
    commander_context: Dict[str, Any],
    strategy_memory: Dict[str, Any],
    selected_symbol_memory: Dict[str, Any],
) -> Dict[str, Any]:
    return _normalize_strategy_adjustment_directives_r3_impl(raw_directives=raw_directives,
        playbook=playbook, policy_adjustment=policy_adjustment, commander_context=commander_context,
        strategy_memory=strategy_memory, selected_symbol_memory=selected_symbol_memory,
        facade=_r3_sys.modules[__name__])


def _build_strategist_llm_messages(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    memory_usage_disabled = _strategy_memory_usage_disabled(payload)
    call_kind = _resolve_strategist_llm_call_kind(payload)
    stage_instruction = (
        "This is Stage 2 selected-symbol tactical refresh. Keep the Stage 1 market frame unless the selected symbol and runner-up evidence clearly contradict it. Use selected_symbol_memory only for symbol-specific bias, policy delta, and monitor handoff. "
        if call_kind == "selected_symbol_tactical_refresh"
        else "This is Stage 3 stale intraday hold review. Focus on whether the open position still deserves HOLD, needs tighter exit handling, or needs an immediate exit review. Review only the held symbol from commander_refresh_context/current_position; do not borrow Stage 1 selected themes, runner-up themes, or unrelated candidate themes unless explicit held-symbol evidence says they apply. If held-symbol theme evidence is missing, say it is unavailable instead of naming a theme. "
        if call_kind == "stale_intraday_hold_review"
        else "This is Stage 4 end-of-day carry review. Focus on whether the position can be carried overnight or should be closed before session end, using carry risk and session context. "
        if call_kind == "end_of_day_carry_review"
        else "This is Stage 1 market strategy frame. Do not choose a final stock here; set market, theme, playbook, scanner, and monitor guidance only. Symbol-level memory is intentionally excluded at this stage. "
    )
    memory_system_instruction = (
        "Memory packets are temporarily disabled by Commander policy. "
        "Treat read_model_facts, recent_strategy_feedback, reporter_feedback_packet, strategy_memory, selected_symbol_memory, memory_packets, and commander_memory_policy as audit-only surfaces. "
        "Do not use memory fields to adjust playbook, selected themes, monitor_entry_policy, scanner guidance, monitor focus, or selected_symbol_bias_action. "
        "strategy_adjustment_directives must be based on current market, scanner, monitor, refresh, and risk evidence only. "
        if memory_usage_disabled
        else (
            "You MUST use the provided deterministic memory packets as primary constraints: read_model_facts, recent_strategy_feedback, reporter_feedback_packet, strategy_memory, selected_symbol_memory, memory_packets, commander_memory_policy. "
            "You MUST convert those inputs into explicit strategy adjustment directives. "
            "When recent_strategy_feedback is stale, empty, disabled, or performance_metric_usable=false, exclude it from performance inference and use strategy_memory plus memory_packets as the performance authority. "
            "For Stage 1, use broad daily/weekly/monthly performance memory only and do not infer symbol-specific bias unless a selected-symbol refresh is requested. "
        )
        if call_kind == "market_strategy_frame"
        else (
            "You MUST use the provided deterministic memory packets as primary constraints: read_model_facts, recent_strategy_feedback, reporter_feedback_packet, strategy_memory, selected_symbol_memory, memory_packets, commander_memory_policy. "
            "You MUST convert those inputs into explicit strategy adjustment directives. "
            "When recent_strategy_feedback is stale, empty, disabled, or performance_metric_usable=false, exclude it from performance inference and use strategy_memory plus memory_packets as the performance authority. "
        )
    )
    memory_user_instruction = (
        "Memory usage is temporarily disabled. Do not use any memory packet as a reason to change strategy, thresholds, themes, or symbol bias; mention memory only as disabled/audit-only if needed. "
        if memory_usage_disabled
        else (
            "The memory packets are not optional background. They are the main basis for strategic adjustment. "
            "Input packets: read_model_facts, recent_strategy_feedback, reporter_feedback_packet, strategy_memory, selected_symbol_memory, memory_packets, commander_memory_policy. "
            "Treat recent_strategy_feedback as qualitative-only and exclude it when stale or marked performance_metric_usable=false. "
        )
    )
    memory_sensitive_directives = (
        "Do not ignore repeated patterns across memory packets. "
        "If a playbook is consistently underperforming in the recent memory, you must deprioritize or switch it. "
        + (
            "Do not use selected_symbol_bias_action as a symbol-memory decision during Stage 1. "
            if call_kind == "market_strategy_frame"
            else "If a selected symbol shows repeated structural mismatch, you must reflect that in selected_symbol_bias_action. "
        )
        if not memory_usage_disabled
        else (
            "Ignore memory-derived performance, win-rate, loss, pattern, and symbol-history fields when choosing playbook, thresholds, themes, monitor focus, or symbol bias. "
        )
    )
    memory_user_directives = (
        "Do not ignore repeated patterns across memory packets. "
        "If symbol-level memory contradicts broad market memory, keep broad playbook stable but express symbol-specific bias separately. "
        if not memory_usage_disabled
        else (
            "Memory performance and symbol-history fields are hidden; do not reference weekly, monthly, symbol, win-rate, or loss memory as a reason. "
        )
    )
    system = (
        "You are the Strategist agent for an automated trading system. "
        "You must output a strategic frame only. "
        f"{_stage_specific_role_boundary(call_kind)}"
        f"{stage_instruction}"
        f"{memory_system_instruction}"
        "Do not merely summarize, restate, or lightly reference the inputs. "
        f"{_stage_specific_task_requirement(call_kind)}"
        "Return exactly one minified JSON object only. "
        "Do not add analysis, markdown, bullet points, or any text before or after the JSON. "
        "The first character must be { and the last character must be }. "
        "If deterministic evidence shows repeated NOOP-like blockage, you must decide whether entry conditions should be relaxed, tightened, or rebalanced. "
        "If deterministic evidence shows repeated false entries, stop-outs, or drawdown-heavy outcomes, you must tighten or rebalance policy. "
        "Use quant_context when present as deterministic observation-only evidence: it does not execute behavior by itself, but it should inform tactic fit, scorecard-aware caution, selected-symbol review, hold review, and carry review. "
        "Use market_regime_rail, news_quality, and risk_off_exception_policy as explicit evaluation inputs. "
        "You MUST echo the applicable market_regime_rail, summarize news_quality, and list risk_off_exception_conditions in the JSON output when the contract contains those fields. "
        "Use news_event_intelligence only as observation-only watchlist evidence; it may inform themes to watch, but it must not override Scanner, Monitor, Commander, cost, or risk gates. "
        "In risk-off rails, do not relax entry policy unless risk_off_exception_policy.allowed_exception_conditions are explicitly satisfied by scanner, monitor, cost, volume, and fresh symbol-news evidence. "
        "Use memory_packets.*.operator_summary.tactic_lane_guidance when present as deterministic Q8 feedback: if vwap_reclaim_pullback is overused and weak, do not default to it; explicitly compare breakout or volume_breakout when shadow breakout-ready evidence exists; keep cost-edge guard promoted when shadow readiness recommends it. "
        "Use selected_symbol_news_signal and candidate_news_signal_summary when present: negative selected-symbol news must block relaxation unless chart/volume evidence is exceptional; positive selected-symbol news may support relaxation only when monitor and cost evidence are also ready. "
        f"{memory_sensitive_directives}"
        "If evidence is mixed or weak, explicitly maintain conservative baseline. "
        "strategy_adjustment_directives must be actionable, specific, and bounded. "
        "Do not output generic advice. "
        "Do not output passive observations without a concrete action. "
        "Every directive must include an action, a target or focus, and a short reason. "
        "When commander refresh context exists, separate the 1st/base frame, 2nd/post-scanner refresh, and final application result in strategy_refresh_trace. "
        "If confidence is low, default to conservative baseline. "
        "Do not hallucinate confidence. "
        "Infer confidence only from consistency and sufficiency of deterministic evidence. "
        "All human-readable sentences must be in Korean. "
        "Return JSON only."
    )
    base_contract = {
        "market_regime_rail": "risk_off_breadth_collapse|global_risk_off_pressure|risk_on_supportive|neutral_mixed|macro_packet_unavailable",
        "news_quality": {
            "status": "ok|partial|weak",
            "headline_count": 0,
            "candidate_headline_count": 0,
            "market_headline_count": 0,
            "issues": ["string"],
            "usage_rule": "string",
        },
        "risk_off_exception_conditions": ["string"],
        "news_event_intelligence_usage": {
            "status": "used|ignored|insufficient",
            "used_event_ids": ["news_event_001"],
            "theme_watchlist": ["space_aerospace"],
            "symbol_watchlist": ["005930"],
            "reason": "string",
            "observation_only": True,
        },
        "playbook": "breakout|pullback|reversal|defensive",
        "tactical_strategy": (
            "opening_gap_momentum|opening_range_breakout|vwap_reclaim_pullback|"
            "volume_breakout|reversal_reclaim|cost_aware_scalp|defensive_observe"
        ),
        "tactical_subtype": (
            "theme_confirmed_pullback|market_representative_pullback|liquidity_confirmed_pullback|"
            "vwap_reclaim_setup|weak_fallback_pullback|none"
        ),
        "strategy_scores": {
            "opening_gap_momentum": 0.0,
            "opening_range_breakout": 0.0,
            "vwap_reclaim_pullback": 0.0,
            "volume_breakout": 0.0,
            "reversal_reclaim": 0.0,
            "cost_aware_scalp": 0.0,
            "defensive_observe": 0.0,
        },
        "rejected_strategy_reasons": {
            "strategy_name": "short reason why this tactical strategy was not selected"
        },
        "candidate_watch_policy": {
            "max_priority_rank": 5,
            "max_runner_ups": 4,
            "cascade_enabled": True,
            "cascade_allowed_reasons": [
                "too_extended_from_vwap",
                "breakout_not_ready",
                "volume_insufficient",
                "volume_confirmation_missing",
                "below_vwap_reclaim_not_ready",
                "pullback_below_vwap_reclaim_not_ready",
                "pullback_not_mature",
            ],
            "cascade_blocked_reasons": [
                "cost_filter_failed",
                "risk_policy_block",
                "closeout_window",
                "open_position_present",
                "daily_loss_limit",
                "broker_truth_mismatch",
                "data_quality_guard",
            ],
            "reason": "string",
        },
        "selected_themes": ["string from available_themes only when available"],
        "theme_strategy": {
            "selection_mode": "kiwoom_api_constrained|fallback",
            "selected_themes": [
                {
                    "theme": "string",
                    "playbook_overlay": "momentum|pullback|reversal|defensive|fallback",
                    "scanner_directive": "string",
                    "reason": "string",
                }
            ],
            "fallback_reason": "string",
        },
        "rationale": "string",
        "monitor_entry_policy": {
            "enabled": True,
            "timeframe_minutes": 1,
            "breakout_lookback": 5,
            "volume_lookback": 5,
            "volume_ratio_min": 0.68,
            "min_extended_from_vwap_pct": -0.02,
            "max_extended_from_vwap_pct": 0.13,
            "pullback_min_pct": 0.008,
            "pullback_max_pct": 0.07,
            "reclaim_tolerance_pct": 0.0015,
            "breakout_buffer_pct": 0.0,
            "intent_cooldown_sec": 60,
            "require_vwap_reclaim": True,
            "require_rebound": True,
        },
        "strategy_adjustment_directives": {
            "playbook_action": {
                "action": "maintain|prefer|deprioritize|switch",
                "target": "string|null",
                "reason": "string",
            },
            "entry_policy_action": {
                "action": "maintain|tighten|relax|rebalance",
                "target_fields": ["string"],
                "reason": "string",
            },
            "monitor_focus_action": {
                "action": "maintain|increase_focus|decrease_focus|shift_focus",
                "target_axes": ["reclaim", "pullback", "volume", "breakout", "extension", "exit_axis"],
                "reason": "string",
            },
            "selected_symbol_bias_action": {
                "action": "none|prefer_pullback|avoid_breakout|prefer_reclaim|avoid_extension",
                "reason": "string",
            },
            "refresh_action": {
                "action": "none|refresh_for_holding|refresh_for_repeated_hold|refresh_for_exit_axis_mismatch",
                "reason": "string",
            },
        },
        "strategy_refresh_trace": {
            "summary": "string",
            "bullets": ["string"],
            "stages": [
                {
                    "stage": "initial_frame|post_scanner_refresh|final_application",
                    "label": "string",
                    "summary": "string",
                    "requested": True,
                    "effective": False,
                    "reason": "string",
                }
            ],
        },
        "strategy_horizon_feedback": {
            "strategy_horizon": "one_of:scalp,intraday,overnight_probe,1_2day_swing",
            "expected_hold_window": {"min_sec": 300, "target_sec": 1800, "max_sec": 14400},
            "exit_guidance": {
                "profit_take_style": "trail_after_first_push",
                "allow_early_exit": True,
                "early_exit_allowed_reasons": ["hard_stop", "liquidity_collapse", "market_regime_flip"],
                "avoid_early_exit_reasons": ["small_noise_pullback", "minor_profit_without_momentum_loss"],
            },
            "invalidation_conditions": ["string"],
            "monitor_handoff": {
                "hold_bias": "neutral|neutral_to_patient|defensive",
                "preferred_exit": "string",
                "do_not_force_hold": True,
            },
        },
    }
    contract = _stage_specific_llm_contract(call_kind, base_contract)
    user = (
        (
            "Use the provided market context and candidate hints. "
            if memory_usage_disabled
            else "Use the provided market context, candidate hints, and deterministic memory packets. "
        )
        + f"{memory_user_instruction}"
        f"{_stage_specific_user_requirement(call_kind)}"
        "Prefer changing strategy only when deterministic evidence supports it. "
        "Prefer maintaining current baseline when evidence is weak or mixed. "
        "Do not overreact to a single trade. "
        f"{memory_user_directives}"
        "Do not produce narrative summary in place of directives. "
        "Do not collapse strategist refresh into one generic summary; strategy_refresh_trace must distinguish 1st/base frame, 2nd/post-scanner refresh, and final application. "
        "For strategy_horizon_feedback.strategy_horizon, choose exactly one enum value: scalp, intraday, overnight_probe, or 1_2day_swing. Never return the pipe-delimited placeholder. "
        "If available_themes is non-empty, selected_themes must be chosen only from available_themes.theme. "
        "If available_themes is empty, selected_themes must stay empty; fallback_theme_hints are context only and must not be treated as tradable Kiwoom themes. "
        "Do not invent tradable theme names outside Kiwoom available_themes; abstract labels may appear only in rationale or fallback_reason. "
        "Scanner directives must describe how to rank symbols inside selected Kiwoom theme components, not name a final stock. "
        "candidate_watch_policy is a proposal only; Commander owns final executable entry_control and may clamp the proposed watch depth. "
        "Avoid vague terms such as slightly, carefully, appropriately, or in general. "
        "Use explicit, bounded, implementable language. "
        "If repeated failure is concentrated in one axis, reflect that axis in monitor_focus_action. "
        "Reply with JSON only. No prose.\n"
        "JSON contract:\n"
        f"{json.dumps(contract, ensure_ascii=False)}\n\n"
        "Input:\n"
        f"{json.dumps(payload, ensure_ascii=False)}"
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _compact_news_sample_for_llm(sample: Any, *, max_symbols: int = 6, max_titles: int = 2, max_title_len: int = 160) -> Dict[str, Any]:
    return _compact_news_sample_for_llm_r3_impl(sample, max_symbols=max_symbols,
        max_titles=max_titles, max_title_len=max_title_len, facade=_r3_sys.modules[__name__])


def _round_optional(value: Any, digits: int = 4) -> Any:
    return _round_optional_r3_impl(value, digits, facade=_r3_sys.modules[__name__])


def _compact_global_signal_for_llm(signal: Any) -> Dict[str, Any]:
    return _compact_global_signal_for_llm_r3_impl(signal, facade=_r3_sys.modules[__name__])


def _compact_top_metric_map(raw: Any, *, max_items: int = 4) -> Dict[str, Any]:
    return _compact_top_metric_map_r3_impl(raw, max_items=max_items,
        facade=_r3_sys.modules[__name__])


def _compact_performance_summary_map(raw: Any, *, max_items: int = 3) -> Dict[str, Any]:
    return _compact_performance_summary_map_r3_impl(raw, max_items=max_items,
        facade=_r3_sys.modules[__name__])


def _compact_recent_strategy_feedback_for_llm(feedback: Any) -> Dict[str, Any]:
    return _compact_recent_strategy_feedback_for_llm_r3_impl(feedback,
        facade=_r3_sys.modules[__name__])


def _load_reporter_feedback_packet(state: Dict[str, Any], policy: Dict[str, Any]) -> Dict[str, Any]:
    def _load_source_packet() -> Dict[str, Any]:
        src = state.get("strategist_feedback_packet")
        if not isinstance(src, dict):
            src = state.get("reporter_feedback_packet")
        if isinstance(src, dict) and src:
            return dict(src)

        reports_root = isolate_canonical_path_for_pytest(str(state.get("reports_root") or os.getenv("REPORTS_ROOT", "reports")).strip() or "reports", canonical_path="reports", isolated_name="reports")
        day = str(policy.get("reporter_feedback_day") or state.get("day") or _resolve_state_day(state)).strip()
        try:
            packet = build_strategist_feedback_packet(
                mode="strategist_feedback",
                payload={"day": day},
                reports_root=reports_root,
                day=day,
            )
        except Exception:
            return {}
        return dict(packet or {})

    def _normalize_mode(value: Any) -> str:
        mode = str(value or "").strip().lower()
        return mode if mode in {"auto", "enabled", "disabled"} else "auto"

    def _empty_feedback_packet(
        *,
        mode: str,
        mode_source: str,
        status: str,
        gate_reason: str,
        source_status: str = "",
        source_available: bool = False,
        feedback_id: str = "",
        source_day: str = "",
    ) -> Dict[str, Any]:
        return {
            "available": False,
            "status": str(status or "disabled"),
            "advisory_only": True,
            "feedback_mode": "deterministic",
            "confidence": "none",
            "insight_summary": "",
            "dominant_patterns": [],
            "blocker_analysis": [],
            "route_analysis": {},
            "recommendation": [],
            "reporter_feedback_mode": str(mode or "auto"),
            "reporter_feedback_mode_source": str(mode_source or "default_auto"),
            "consumed": False,
            "feedback_gate_reason": str(gate_reason or ""),
            "source_status": str(source_status or ""),
            "source_available": bool(source_available),
            "feedback_id": str(feedback_id or ""),
            "source_day": str(source_day or ""),
            "data_freshness": {},
        }

    def _resolve_mode() -> Tuple[str, str]:
        applied_policy = state.get("applied_policy")
        applied_policy = applied_policy if isinstance(applied_policy, dict) else {}
        applied_policy_strategist = applied_policy.get("strategist")
        applied_policy_strategist = applied_policy_strategist if isinstance(applied_policy_strategist, dict) else {}
        strategist_runtime_input = state.get("strategist_runtime_input")
        strategist_runtime_input = strategist_runtime_input if isinstance(strategist_runtime_input, dict) else {}

        candidates = [
            (
                applied_policy_strategist.get("reporter_feedback_mode"),
                str(applied_policy_strategist.get("reporter_feedback_mode_source") or "commander_applied_policy"),
                "commander_applied_policy",
            ),
            (
                applied_policy.get("reporter_feedback_mode"),
                str(applied_policy.get("reporter_feedback_mode_source") or "applied_policy_fallback"),
                "applied_policy_fallback",
            ),
            (
                state.get("reporter_feedback_mode"),
                str(state.get("reporter_feedback_mode_source") or "state_fallback"),
                "state_fallback",
            ),
            (
                strategist_runtime_input.get("reporter_feedback_mode"),
                "legacy_fallback",
                "legacy_fallback",
            ),
            (
                policy.get("reporter_feedback_mode"),
                "legacy_fallback",
                "legacy_fallback",
            ),
        ]
        for raw_value, source_hint, default_source in candidates:
            if raw_value not in (None, ""):
                return _normalize_mode(raw_value), str(source_hint or default_source)
        return "auto", "default_auto"

    feedback_mode, feedback_mode_source = _resolve_mode()
    if feedback_mode == "disabled":
        return _empty_feedback_packet(
            mode=feedback_mode,
            mode_source=feedback_mode_source,
            status="disabled",
            gate_reason="mode_disabled",
        )

    src = _load_source_packet()
    if not src:
        return _empty_feedback_packet(
            mode=feedback_mode,
            mode_source=feedback_mode_source,
            status="missing",
            gate_reason="no_packet",
        )

    out = dict(src)
    out["available"] = bool(src.get("available"))
    out["status"] = str(src.get("status") or "ok")
    out["advisory_only"] = True
    out["feedback_mode"] = str(src.get("feedback_mode") or "deterministic")
    out["confidence"] = str(src.get("confidence") or "none")
    out["insight_summary"] = str(src.get("insight_summary") or "")
    out["dominant_patterns"] = list(src.get("dominant_patterns") or [])
    out["blocker_analysis"] = list(src.get("blocker_analysis") or [])
    out["route_analysis"] = dict(src.get("route_analysis") or {})
    out["recommendation"] = [str(x or "") for x in list(src.get("recommendation") or []) if str(x or "").strip()][:4]
    out["data_freshness"] = dict(src.get("data_freshness") or {})
    out["reporter_feedback_mode"] = feedback_mode
    out["reporter_feedback_mode_source"] = feedback_mode_source
    out["source_status"] = str(src.get("status") or "ok")
    out["source_available"] = bool(src.get("available"))
    out["consumed"] = False
    out["feedback_gate_reason"] = ""

    if feedback_mode == "enabled":
        if bool(out.get("available")):
            out["consumed"] = True
            out["feedback_gate_reason"] = "mode_enabled"
            return out
        return _empty_feedback_packet(
            mode=feedback_mode,
            mode_source=feedback_mode_source,
            status="unavailable",
            gate_reason="source_unavailable",
            source_status=str(src.get("status") or "unavailable"),
            source_available=bool(src.get("available")),
            feedback_id=str(out.get("feedback_id") or ""),
            source_day=str(src.get("source_day") or ""),
        )

    freshness = out.get("data_freshness") if isinstance(out.get("data_freshness"), dict) else {}
    freshness_status = str(freshness.get("freshness_status") or "").strip().lower()
    stale = bool(freshness.get("stale")) or freshness_status == "stale"
    confidence_raw = src.get("confidence")
    confidence_text = str(confidence_raw or "none").strip().lower()
    confidence_numeric = _round_optional(confidence_raw, 4) if confidence_raw not in (None, "") else None
    confidence_ok = confidence_text in {"medium", "high"} or (
        isinstance(confidence_numeric, (int, float)) and float(confidence_numeric) >= 0.5
    )
    route_analysis = out.get("route_analysis") if isinstance(out.get("route_analysis"), dict) else {}
    route_selected_total = dict(route_analysis.get("route_selected_total") or {})
    relevant = bool(
        str(out.get("insight_summary") or "").strip()
        or list(out.get("dominant_patterns") or [])
        or list(out.get("blocker_analysis") or [])
        or list(out.get("recommendation") or [])
        or route_selected_total
        or route_analysis
    )
    if not bool(out.get("available")):
        return _empty_feedback_packet(
            mode=feedback_mode,
            mode_source=feedback_mode_source,
            status="auto_ignored",
            gate_reason="source_unavailable",
            source_status=str(src.get("status") or "unavailable"),
            source_available=False,
            feedback_id=str(out.get("feedback_id") or ""),
            source_day=str(src.get("source_day") or ""),
        )
    if stale:
        return _empty_feedback_packet(
            mode=feedback_mode,
            mode_source=feedback_mode_source,
            status="auto_ignored",
            gate_reason="stale",
            source_status=str(src.get("status") or "ok"),
            source_available=True,
            feedback_id=str(out.get("feedback_id") or ""),
            source_day=str(src.get("source_day") or ""),
        )
    if not confidence_ok:
        return _empty_feedback_packet(
            mode=feedback_mode,
            mode_source=feedback_mode_source,
            status="auto_ignored",
            gate_reason="low_confidence",
            source_status=str(src.get("status") or "ok"),
            source_available=True,
            feedback_id=str(out.get("feedback_id") or ""),
            source_day=str(src.get("source_day") or ""),
        )
    if not relevant:
        return _empty_feedback_packet(
            mode=feedback_mode,
            mode_source=feedback_mode_source,
            status="auto_ignored",
            gate_reason="not_relevant",
            source_status=str(src.get("status") or "ok"),
            source_available=True,
            feedback_id=str(out.get("feedback_id") or ""),
            source_day=str(src.get("source_day") or ""),
        )
    out["consumed"] = True
    out["feedback_gate_reason"] = "auto_accepted"
    return out


def _compact_reporter_feedback_for_llm(packet: Any) -> Dict[str, Any]:
    return _compact_reporter_feedback_for_llm_r3_impl(packet, facade=_r3_sys.modules[__name__])


def _compact_strategy_memory_for_llm(memory: Any) -> Dict[str, Any]:
    return _compact_strategy_memory_for_llm_r3_impl(memory, facade=_r3_sys.modules[__name__])


def _compact_pattern_performance_for_llm(snapshot: Any) -> Dict[str, Any]:
    return _compact_pattern_performance_for_llm_r3_impl(snapshot, facade=_r3_sys.modules[__name__])


def _news_signal_label(score: Any) -> str:
    return _news_signal_label_r3_impl(score, facade=_r3_sys.modules[__name__])


def _news_item_title_for_llm(row: Any, *, max_len: int = 120) -> str:
    return _news_item_title_for_llm_r3_impl(row, max_len=max_len, facade=_r3_sys.modules[__name__])


def _compact_news_signal_summary_for_llm(
    *,
    signal_map: Any,
    sample: Any,
    symbols: List[str],
    limit: int = 6,
) -> List[Dict[str, Any]]:
    return _compact_news_signal_summary_for_llm_r3_impl(signal_map=signal_map, sample=sample,
        symbols=symbols, limit=limit, facade=_r3_sys.modules[__name__])


def _selected_symbol_news_signal_for_llm(
    rows: List[Dict[str, Any]],
    selected_symbol: Any,
) -> Dict[str, Any]:
    return _selected_symbol_news_signal_for_llm_r3_impl(rows, selected_symbol,
        facade=_r3_sys.modules[__name__])


def _clip_text_for_llm(raw: Any, *, max_len: int = 180) -> str:
    text = str(raw or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max(0, max_len - 1)].rstrip() + "..."


def _compact_scalar_mapping_for_llm(src: Any, *, allowed_keys: List[str], max_text_len: int = 160) -> Dict[str, Any]:
    return _compact_scalar_mapping_for_llm_r3_impl(src, allowed_keys=allowed_keys,
        max_text_len=max_text_len, facade=_r3_sys.modules[__name__])


def _compact_pattern_rows_for_llm(rows: Any, *, limit: int = 3) -> List[Dict[str, Any]]:
    return _compact_pattern_rows_for_llm_r3_impl(rows, limit=limit,
        facade=_r3_sys.modules[__name__])


def _operator_summary_for_llm(summary: Any) -> Dict[str, Any]:
    return _operator_summary_for_llm_r3_impl(summary, facade=_r3_sys.modules[__name__])


def _compact_trade_read_model_for_llm(row: Any) -> Dict[str, Any]:
    return _compact_trade_read_model_for_llm_r3_impl(row, facade=_r3_sys.modules[__name__])


def _compact_symbol_read_model_for_llm(row: Any) -> Dict[str, Any]:
    return _compact_symbol_read_model_for_llm_r3_impl(row, facade=_r3_sys.modules[__name__])


def _compact_read_model_facts_for_llm(facts: Any) -> Dict[str, Any]:
    return _compact_read_model_facts_for_llm_r3_impl(facts, facade=_r3_sys.modules[__name__])


def _load_deterministic_read_models(state: Dict[str, Any], candidates: List[str]) -> Dict[str, Any]:
    """Phase 6-2: Gather strictly deterministic read models for Strategist context."""
    reports_root = isolate_canonical_path_for_pytest(str(state.get("reports_root") or os.getenv("REPORTS_ROOT", "reports")).strip() or "reports", canonical_path="reports", isolated_name="reports")
    trades_root = reports_root / "trades"
    
    recent_trades = []
    if trades_root.exists() and trades_root.is_dir():
        # Find recent trade directories (limit to 5 without using env vars)
        trade_dirs = sorted([d for d in trades_root.iterdir() if d.is_dir()], key=lambda x: x.stat().st_mtime, reverse=True)[:5]
        for td in trade_dirs:
            try:
                trm = build_trade_read_model(str(td))
                if trm and trm.get("trade_id"):
                    recent_trades.append(trm)
            except Exception:
                pass
                
    symbol_patterns = {}
    persisted_symbol_models_only = not _env_bool("STRATEGIST_READ_MODEL_FULL_SCAN", False)
    for sym in list(candidates or [])[:5]:
        try:
            symbol_patterns[str(sym)] = build_symbol_read_model(
                str(trades_root),
                str(sym),
                persisted_only=persisted_symbol_models_only,
            )
        except Exception:
            pass
            
    return {
        "recent_trades": recent_trades,
        "daily_summary": {},  # Placeholder for daily_summary_read_model
        "symbol_patterns": symbol_patterns
    }


def _resolve_strategist_llm_call_kind(payload: Dict[str, Any]) -> str:
    compact = payload if isinstance(payload, dict) else {}
    context = compact.get("commander_refresh_context") if isinstance(compact.get("commander_refresh_context"), dict) else {}
    if bool(context.get("requested")):
        scope = str(context.get("refresh_scope") or "").strip().lower()
        reason = str(context.get("reason") or "").strip().lower()
        carry_state = str(context.get("carry_state") or "").strip().lower()
        if (
            "closeout" in scope
            or "closeout" in reason
            or "end_of_day" in scope
            or "end_of_day" in reason
            or "eod" in scope
            or "eod" in reason
            or "overnight_review" in scope
            or "overnight_review" in reason
            or "overnight" in reason
            or reason in {"end_of_day_carry_review", "session_closeout_carry_review"}
        ):
            return "end_of_day_carry_review"
        if (
            "open_position" in scope
            or "hold" in scope
            or "position" in scope
            or "hold" in reason
            or "loss_threshold" in reason
            or "preopen_carry" in reason
            or carry_state
        ):
            return "stale_intraday_hold_review"
        return "selected_symbol_tactical_refresh"
    explicit = str(compact.get("resolved_call_kind") or compact.get("call_kind") or "").strip().lower()
    if explicit in {
        "selected_symbol_tactical_refresh",
        "stale_intraday_hold_review",
        "end_of_day_carry_review",
        "market_strategy_frame",
    }:
        return explicit
    return "market_strategy_frame"


def _hide_stage1_symbol_memory(compact: Dict[str, Any]) -> None:
    return _hide_stage1_symbol_memory_r3_impl(compact, facade=_r3_sys.modules[__name__])


def _compact_monitor_entry_policy_baseline_for_llm(policy: Any) -> Dict[str, Any]:
    return _compact_monitor_entry_policy_baseline_for_llm_r3_impl(policy,
        facade=_r3_sys.modules[__name__])


def _compact_theme_strength_for_llm(raw: Any, *, limit: int = 6) -> Dict[str, Any]:
    return _compact_theme_strength_for_llm_r3_impl(raw, limit=limit,
        facade=_r3_sys.modules[__name__])


def _theme_packet_summary_for_llm(packet: Any) -> Dict[str, Any]:
    return _theme_packet_summary_for_llm_r3_impl(packet, facade=_r3_sys.modules[__name__])


def _compact_candidate_context_for_refresh(row: Any) -> Dict[str, Any]:
    return _compact_candidate_context_for_refresh_r3_impl(row, facade=_r3_sys.modules[__name__])


def _slim_refresh_context_for_llm(context: Any) -> Dict[str, Any]:
    return _slim_refresh_context_for_llm_r3_impl(context, facade=_r3_sys.modules[__name__])


def _apply_strategist_llm_token_budget(compact: Dict[str, Any], *, memory_usage_disabled: bool) -> Dict[str, Any]:
    from libs.runtime.strategist.context.token_budget import apply_frame_token_budget
    return apply_frame_token_budget(compact, memory_usage_disabled=memory_usage_disabled, facade=_r3_sys.modules[__name__])


def _build_compact_strategist_llm_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    compact = dict(payload or {})
    memory_usage_disabled = _strategy_memory_usage_disabled(compact)
    compact["global_sentiment_signal"] = _compact_global_signal_for_llm(compact.get("global_sentiment_signal"))
    news_ctx = compact.get("news_context") if isinstance(compact.get("news_context"), dict) else {}
    compact["news_context"] = {
        "signal_total": int(news_ctx.get("signal_total") or 0),
        "avg_score": _round_optional(news_ctx.get("avg_score"), 4),
        "headline_count": int(news_ctx.get("headline_count") or 0),
        "candidate_signal_total": int(news_ctx.get("candidate_signal_total") or 0),
        "market_signal_total": int(news_ctx.get("market_signal_total") or 0),
    }
    market_ctx = compact.get("market_context_inputs") if isinstance(compact.get("market_context_inputs"), dict) else {}
    compact["market_context_inputs"] = {
        "index_trend": _round_optional(market_ctx.get("index_trend"), 4),
        "realized_volatility": _round_optional(market_ctx.get("realized_volatility"), 4),
        "market_breadth": _round_optional(market_ctx.get("market_breadth"), 4),
        "macro_risk": _round_optional(market_ctx.get("macro_risk"), 4),
    }
    compact["recent_strategy_feedback"] = _compact_recent_strategy_feedback_for_llm(compact.get("recent_strategy_feedback"))
    compact["reporter_feedback_packet"] = _compact_reporter_feedback_for_llm(compact.get("reporter_feedback_packet"))
    compact["strategy_memory"] = _compact_strategy_memory_for_llm(compact.get("strategy_memory"))
    compact["macro_stress_overlay_hint"] = {
        "active": bool(((compact.get("macro_stress_overlay_hint") or {}).get("active"))),
        "stress_flags": [str(x or "") for x in list(((compact.get("macro_stress_overlay_hint") or {}).get("stress_flags") or [])[:4])],
        "reason": str(((compact.get("macro_stress_overlay_hint") or {}).get("reason") or "")),
    }
    compact["market_news_sample"] = _compact_news_sample_for_llm(compact.get("market_news_sample"), max_symbols=4, max_titles=1, max_title_len=120)
    compact["candidate_news_sample"] = _compact_news_sample_for_llm(compact.get("candidate_news_sample"), max_symbols=4, max_titles=1, max_title_len=120)
    compact["news_event_intelligence"] = compact_news_event_intelligence_for_llm(
        compact.get("news_event_intelligence")
    )
    compact["candidate_symbols_hint"] = list(compact.get("candidate_symbols_hint") or [])[:5]
    compact["key_events_hint"] = [str(x or "") for x in list(compact.get("key_events_hint") or [])[:4]]
    compact["themes_hint"] = [str(x or "") for x in list(compact.get("themes_hint") or [])[:4]]
    compact["fallback_theme_hints"] = [
        str(x or "") for x in list(compact.get("fallback_theme_hints") or [])[:4] if str(x or "").strip()
    ]
    compact["available_themes"] = [
        {
            "theme": str((row or {}).get("theme") or ""),
            "theme_code": str((row or {}).get("theme_code") or ""),
            "score": _round_optional((row or {}).get("score"), 4),
            "component_count": int((row or {}).get("component_count") or 0),
            "component_symbols": [str(x or "") for x in list((row or {}).get("component_symbols") or [])[:6]],
        }
        for row in list(compact.get("available_themes") or [])[:8]
        if isinstance(row, dict)
    ]
    compact["selected_themes_hint"] = [
        str(x or "") for x in list(compact.get("selected_themes_hint") or [])[:5] if str(x or "").strip()
    ]
    news_collection_policy = compact.get("news_collection_policy") if isinstance(compact.get("news_collection_policy"), dict) else {}
    compact["news_collection_policy"] = {
        "provider": str(news_collection_policy.get("provider") or ""),
        "market_query_targets": [str(x or "") for x in list(news_collection_policy.get("market_query_targets") or [])[:8]],
        "candidate_symbols_requested": [
            str(x or "") for x in list(news_collection_policy.get("candidate_symbols_requested") or [])[:8]
        ],
        "theme_component_symbols_requested": [
            str(x or "") for x in list(news_collection_policy.get("theme_component_symbols_requested") or [])[:8]
        ],
        "collection_symbols": [str(x or "") for x in list(news_collection_policy.get("collection_symbols") or [])[:12]],
        "post_scanner_requery": bool(news_collection_policy.get("post_scanner_requery")),
        "reuse_policy": str(news_collection_policy.get("reuse_policy") or ""),
    }
    compact["news_query_targets"] = [str(x or "") for x in list(compact.get("news_query_targets") or [])[:8]]
    commander_refresh_context = compact.get("commander_refresh_context") if isinstance(compact.get("commander_refresh_context"), dict) else {}
    selected_symbol_was_rank1_raw = commander_refresh_context.get("selected_symbol_was_rank1")
    selected_symbol_was_rank1 = (
        bool(selected_symbol_was_rank1_raw)
        if selected_symbol_was_rank1_raw is not None
        else int(commander_refresh_context.get("selected_rank") or 0) == 1
    )
    actual_selected_candidate = (
        commander_refresh_context.get("actual_selected_candidate")
        if isinstance(commander_refresh_context.get("actual_selected_candidate"), dict)
        else commander_refresh_context.get("scanner_primary_candidate")
        if isinstance(commander_refresh_context.get("scanner_primary_candidate"), dict)
        else {}
    )
    selected_news_symbol = (
        commander_refresh_context.get("selected_symbol")
        or actual_selected_candidate.get("symbol")
        or (compact.get("candidate_symbols_hint") or [""])[0]
    )
    candidate_news_signal_summary = _compact_news_signal_summary_for_llm(
        signal_map=compact.get("news_sentiment_signal"),
        sample=compact.get("candidate_news_sample"),
        symbols=[str(x or "") for x in list(compact.get("candidate_symbols_hint") or [])],
        limit=6,
    )
    compact["candidate_news_signal_summary"] = candidate_news_signal_summary
    compact["selected_symbol_news_signal"] = _selected_symbol_news_signal_for_llm(
        candidate_news_signal_summary,
        selected_news_symbol,
    )
    compact["market_news_signal_summary"] = _compact_news_signal_summary_for_llm(
        signal_map=compact.get("market_news_sentiment_signal"),
        sample=compact.get("market_news_sample"),
        symbols=[str(x or "") for x in list((compact.get("market_news_sample") or {}).keys())],
        limit=4,
    )
    compact.pop("news_sentiment_signal", None)
    compact.pop("market_news_sentiment_signal", None)
    compact["commander_refresh_context"] = {
        "requested": bool(commander_refresh_context.get("requested")),
        "reason": str(commander_refresh_context.get("reason") or ""),
        "refresh_scope": str(commander_refresh_context.get("refresh_scope") or ""),
        "selected_symbol": str(commander_refresh_context.get("selected_symbol") or ""),
        "hold_repeat_count_max": int(commander_refresh_context.get("hold_repeat_count_max") or 0),
        "selected_hold_repeat_count": int(commander_refresh_context.get("selected_hold_repeat_count") or 0),
        "monitor_reason": str(commander_refresh_context.get("monitor_reason") or ""),
        "active_exit_axis": str(commander_refresh_context.get("active_exit_axis") or ""),
        "refresh_summary": str(commander_refresh_context.get("refresh_summary") or "")[:220],
        "selected_rank": int(commander_refresh_context.get("selected_rank") or 0),
        "selected_score": _round_optional(commander_refresh_context.get("selected_score"), 4),
        "scanner_primary_candidate": dict(commander_refresh_context.get("scanner_primary_candidate") or {}),
        "actual_selected_candidate": dict(actual_selected_candidate),
        "scanner_rank1_candidate": dict(commander_refresh_context.get("scanner_rank1_candidate") or {}),
        "scanner_runner_ups": [
            dict(row)
            for row in list(commander_refresh_context.get("scanner_runner_ups") or [])[:4]
            if isinstance(row, dict)
        ],
        "scanner_top_candidates": [
            dict(row)
            for row in list(commander_refresh_context.get("scanner_top_candidates") or [])[:5]
            if isinstance(row, dict)
        ],
        "selected_symbol_was_rank1": bool(selected_symbol_was_rank1),
        "stage2_context_quality": str(commander_refresh_context.get("stage2_context_quality") or ""),
        "stage2_context_quality_reasons": [
            str(reason or "")
            for reason in list(commander_refresh_context.get("stage2_context_quality_reasons") or [])[:6]
            if str(reason or "").strip()
        ],
        "entry_state": dict(commander_refresh_context.get("entry_state") or {}),
        "position_horizon_state": dict(commander_refresh_context.get("position_horizon_state") or {}),
        "carry_state": str(commander_refresh_context.get("carry_state") or ""),
        "carry_risk_bias": str(commander_refresh_context.get("carry_risk_bias") or ""),
        "carry_risk_reason": str(commander_refresh_context.get("carry_risk_reason") or "")[:220],
        "session_open_recovery_assessment": dict(
            commander_refresh_context.get("session_open_recovery_assessment") or {}
        ),
        "prior_monitor_entry_policy_summary": dict(commander_refresh_context.get("prior_monitor_entry_policy_summary") or {}),
        "current_monitor_entry_policy_summary": dict(commander_refresh_context.get("current_monitor_entry_policy_summary") or {}),
        "commander_horizon_policy": {
            "owner": str((commander_refresh_context.get("commander_horizon_policy") or {}).get("owner") or "commander")
            if isinstance(commander_refresh_context.get("commander_horizon_policy"), dict)
            else "",
            "strategy_horizon": str(
                (commander_refresh_context.get("commander_horizon_policy") or {}).get("strategy_horizon") or ""
            )
            if isinstance(commander_refresh_context.get("commander_horizon_policy"), dict)
            else "",
            "source_strategy_horizon": str(
                (commander_refresh_context.get("commander_horizon_policy") or {}).get("source_strategy_horizon") or ""
            )
            if isinstance(commander_refresh_context.get("commander_horizon_policy"), dict)
            else "",
            "observability_only": bool(
                (commander_refresh_context.get("commander_horizon_policy") or {}).get("observability_only", True)
            )
            if isinstance(commander_refresh_context.get("commander_horizon_policy"), dict)
            else True,
            "do_not_force_hold": bool(
                (commander_refresh_context.get("commander_horizon_policy") or {}).get("do_not_force_hold", True)
            )
            if isinstance(commander_refresh_context.get("commander_horizon_policy"), dict)
            else True,
            "decision_reason": str(
                (commander_refresh_context.get("commander_horizon_policy") or {}).get("decision_reason") or ""
            )
            if isinstance(commander_refresh_context.get("commander_horizon_policy"), dict)
            else "",
        },
        "requires_policy_delta": bool(commander_refresh_context.get("requires_policy_delta")),
        "selected_symbol_memory": dict(commander_refresh_context.get("selected_symbol_memory") or {}),
    }
    if not compact["commander_refresh_context"].get("position_horizon_state"):
        compact["commander_refresh_context"].pop("position_horizon_state", None)
    compact["strategy_refresh_trace_input"] = {
        "initial_frame": {
            "market_regime": str(compact.get("market_regime_hint") or ""),
            "market_sentiment": str(compact.get("market_sentiment_hint") or ""),
            "playbook": str(compact.get("playbook_hint") or ""),
            "candidate_symbols": list(compact.get("candidate_symbols_hint") or [])[:5],
        },
        "post_scanner_refresh": {
            "requested": bool(commander_refresh_context.get("requested")),
            "reason": str(commander_refresh_context.get("reason") or ""),
            "scope": str(commander_refresh_context.get("refresh_scope") or ""),
            "selected_symbol": str(commander_refresh_context.get("selected_symbol") or ""),
            "selected_rank": int(commander_refresh_context.get("selected_rank") or 0),
            "selected_score": _round_optional(commander_refresh_context.get("selected_score"), 4),
            "scanner_rank1_symbol": str(
                (commander_refresh_context.get("scanner_rank1_candidate") or {}).get("symbol") or ""
            )
            if isinstance(commander_refresh_context.get("scanner_rank1_candidate"), dict)
            else "",
            "actual_selected_rank": int(
                (commander_refresh_context.get("actual_selected_candidate") or {}).get("rank")
                or commander_refresh_context.get("selected_rank")
                or 0
            )
            if isinstance(commander_refresh_context.get("actual_selected_candidate"), dict)
            else int(commander_refresh_context.get("selected_rank") or 0),
            "selected_symbol_was_rank1": bool(selected_symbol_was_rank1),
            "stage2_context_quality": str(commander_refresh_context.get("stage2_context_quality") or ""),
            "runner_up_count": len(list(commander_refresh_context.get("scanner_runner_ups") or [])),
            "monitor_reason": str(commander_refresh_context.get("monitor_reason") or ""),
            "refresh_summary": str(commander_refresh_context.get("refresh_summary") or "")[:220],
        },
        "final_application": {
            "requires_policy_delta": bool(commander_refresh_context.get("requires_policy_delta")),
            "prior_monitor_entry_policy_summary": dict(commander_refresh_context.get("prior_monitor_entry_policy_summary") or {}),
            "current_monitor_entry_policy_summary": dict(commander_refresh_context.get("current_monitor_entry_policy_summary") or {}),
        },
    }
    memory_packets = compact.get("memory_packets") if isinstance(compact.get("memory_packets"), dict) else {}
    daily_packet = dict(memory_packets.get("daily_strategy_memory") or {})
    weekly_packet = dict(memory_packets.get("weekly_strategy_memory") or {})
    monthly_packet = dict(memory_packets.get("monthly_strategy_memory") or {})
    symbol_packet = dict(memory_packets.get("symbol_memory_packet") or {})
    compact["memory_packets"] = {
        "daily_strategy_memory": {
            "status": str(daily_packet.get("status") or ""),
            "best_playbooks": [str(x or "") for x in list(daily_packet.get("best_playbooks") or [])[:3] if str(x or "").strip()],
            "worst_playbooks": [str(x or "") for x in list(daily_packet.get("worst_playbooks") or [])[:3] if str(x or "").strip()],
            "pattern_performance_snapshot": _compact_pattern_performance_for_llm(
                daily_packet.get("pattern_performance_snapshot")
            ),
            "operator_summary": _operator_summary_for_llm(daily_packet.get("operator_summary")),
        },
        "weekly_strategy_memory": {
            "status": str(weekly_packet.get("status") or ""),
            "pattern_performance_snapshot": _compact_pattern_performance_for_llm(
                weekly_packet.get("pattern_performance_snapshot")
            ),
            "operator_summary": _operator_summary_for_llm(weekly_packet.get("operator_summary")),
        },
        "monthly_strategy_memory": {
            "status": str(monthly_packet.get("status") or ""),
            "pattern_performance_snapshot": _compact_pattern_performance_for_llm(
                monthly_packet.get("pattern_performance_snapshot")
            ),
            "operator_summary": _operator_summary_for_llm(monthly_packet.get("operator_summary")),
        },
        "symbol_memory_packet": {
            "status": str(symbol_packet.get("status") or ""),
            "symbol": str(symbol_packet.get("symbol") or ""),
            "trade_count": int(symbol_packet.get("trade_count") or 0),
            "override_eligible": bool(symbol_packet.get("override_eligible")),
            "operator_summary": _operator_summary_for_llm(symbol_packet.get("operator_summary")),
        },
    }
    commander_memory_policy = compact.get("commander_memory_policy") if isinstance(compact.get("commander_memory_policy"), dict) else {}
    compact["commander_memory_policy"] = {
        "application_mode": str(commander_memory_policy.get("application_mode") or ""),
        "active_layers": [str(x or "") for x in list(commander_memory_policy.get("active_layers") or [])[:4] if str(x or "").strip()],
        "priority_order": [str(x or "") for x in list(commander_memory_policy.get("priority_order") or [])[:4] if str(x or "").strip()],
        "symbol_memory_override_enabled": bool(commander_memory_policy.get("symbol_memory_override_enabled")),
        "scanner_bias_enabled": bool(commander_memory_policy.get("scanner_bias_enabled")),
        "monitor_bias_enabled": bool(commander_memory_policy.get("monitor_bias_enabled")),
    }
    scanner_memory_bias = compact.get("scanner_memory_bias") if isinstance(compact.get("scanner_memory_bias"), dict) else {}
    compact["scanner_memory_bias"] = {
        "enabled": bool(scanner_memory_bias.get("enabled")),
        "active_layers": [str(x or "") for x in list(scanner_memory_bias.get("active_layers") or [])[:4] if str(x or "").strip()],
        "source_weight_delta": dict(scanner_memory_bias.get("source_weight_delta") or {}),
        "symbol_adjustment_count": len(dict(scanner_memory_bias.get("symbol_adjustments") or {})),
    }
    monitor_memory_bias = compact.get("monitor_memory_bias") if isinstance(compact.get("monitor_memory_bias"), dict) else {}
    compact["monitor_memory_bias"] = {
        "enabled": bool(monitor_memory_bias.get("enabled")),
        "active_layers": [str(x or "") for x in list(monitor_memory_bias.get("active_layers") or [])[:4] if str(x or "").strip()],
        "entry_policy_delta": dict(monitor_memory_bias.get("entry_policy_delta") or {}),
        "risk_posture": str(monitor_memory_bias.get("risk_posture") or ""),
    }
    compact["read_model_facts"] = _compact_read_model_facts_for_llm(payload.get("read_model_facts", {}))
    if memory_usage_disabled:
        disabled_stub = {
            "status": "disabled",
            "visible_to_llm": False,
            "reason": "commander_memory_usage_disabled",
        }
        compact["recent_strategy_feedback"] = dict(disabled_stub)
        compact["reporter_feedback_packet"] = dict(disabled_stub)
        compact["strategy_memory"] = dict(disabled_stub)
        compact["read_model_facts"] = {
            **disabled_stub,
            "recent_trade_count": 0,
            "symbol_pattern_count": 0,
        }
        compact["memory_packets"] = {
            "daily_strategy_memory": dict(disabled_stub),
            "weekly_strategy_memory": dict(disabled_stub),
            "monthly_strategy_memory": dict(disabled_stub),
            "symbol_memory_packet": dict(disabled_stub),
        }
        compact["scanner_memory_bias"] = {"enabled": False, "visible_to_llm": False}
        compact["monitor_memory_bias"] = {"enabled": False, "visible_to_llm": False}
        if isinstance(compact.get("commander_refresh_context"), dict):
            compact["commander_refresh_context"]["selected_symbol_memory"] = {}
        compact["memory_disabled_notice"] = (
            "Memory-derived trade history and performance fields are hidden from the strategist LLM; "
            "use only current market, scanner, monitor, refresh, and risk evidence."
        )
    compact["resolved_call_kind"] = _resolve_strategist_llm_call_kind(compact)
    quant_context = build_strategist_quant_context(
        compact,
        call_kind=str(compact["resolved_call_kind"]),
        memory_usage_disabled=memory_usage_disabled,
    )
    quant_scorecard = (
        ((quant_context.get("quant_market_context") or {}).get("scorecard") or {})
        if isinstance(quant_context.get("quant_market_context"), dict)
        else {}
    )
    if not (
        compact["resolved_call_kind"] == "market_strategy_frame"
        and str(quant_scorecard.get("reason") or "") == "reports_root_not_explicit"
    ):
        compact["quant_context"] = dict(quant_context)
    compact = _apply_strategist_llm_token_budget(compact, memory_usage_disabled=memory_usage_disabled)
    compact["resolved_call_kind"] = _resolve_strategist_llm_call_kind(compact)
    if not memory_usage_disabled and compact["resolved_call_kind"] == "market_strategy_frame":
        _hide_stage1_symbol_memory(compact)
    return compact


def _quant_trace_stage_for_call_kind(call_kind: Any) -> str:
    text = str(call_kind or "").strip()
    if text == "selected_symbol_tactical_refresh":
        return "post_scanner_refresh"
    if text == "market_strategy_frame":
        return "initial_frame"
    if text == "stale_intraday_hold_review":
        return "stale_intraday_hold_review"
    if text == "end_of_day_carry_review":
        return "end_of_day_carry_review"
    return text or "quant_context"


def _quant_trace_label_for_stage(stage: str) -> str:
    if stage == "initial_frame":
        return "Quant context - initial frame"
    if stage == "post_scanner_refresh":
        return "Quant context - selected symbol refresh"
    if stage == "stale_intraday_hold_review":
        return "Quant context - stale intraday hold review"
    if stage == "end_of_day_carry_review":
        return "Quant context - end of day carry review"
    return "Quant context"


def _attach_quant_context_to_strategy_refresh_trace(
    trace: Any,
    quant_context: Any,
) -> Dict[str, Any]:
    return _attach_quant_context_to_strategy_refresh_trace_r3_impl(trace, quant_context,
        facade=_r3_sys.modules[__name__])


def _build_strategist_llm_repair_messages(payload: Dict[str, Any], raw_response: Any) -> List[Dict[str, str]]:
    compact_payload = _build_compact_strategist_llm_payload(payload)
    call_kind = _resolve_strategist_llm_call_kind(compact_payload)
    system = (
        "You repair strategist outputs for an automated trading system. "
        "Return exactly one minified JSON object only, matching the required contract exactly. "
        "Do not add commentary, markdown, analysis, or explanations. "
        "If the previous draft contained prose, ignore it and generate a fresh JSON object."
    )
    base_contract = {
        "market_regime": "risk_on|neutral|risk_off",
        "market_regime_rail": "risk_off_breadth_collapse|global_risk_off_pressure|risk_on_supportive|neutral_mixed|macro_packet_unavailable",
        "news_quality": {
            "status": "ok|partial|weak",
            "headline_count": 0,
            "candidate_headline_count": 0,
            "market_headline_count": 0,
            "issues": ["string"],
            "usage_rule": "string",
        },
        "risk_off_exception_conditions": ["string"],
        "news_event_intelligence_usage": {
            "status": "used|ignored|insufficient",
            "used_event_ids": ["news_event_001"],
            "theme_watchlist": ["space_aerospace"],
            "symbol_watchlist": ["005930"],
            "reason": "string",
            "observation_only": True,
        },
        "market_sentiment": "bullish|neutral|bearish",
        "key_events": ["string"],
        "themes": ["string"],
        "selected_themes": ["string from available_themes only when available"],
        "theme_strategy": {
            "selection_mode": "kiwoom_api_constrained|fallback",
            "selected_themes": [
                {
                    "theme": "string",
                    "playbook_overlay": "momentum|pullback|reversal|defensive|fallback",
                    "scanner_directive": "string",
                    "reason": "string",
                }
            ],
            "fallback_reason": "string",
        },
        "avoid_themes": ["string"],
        "playbook": "breakout|pullback|reversal|defensive",
        "scanner_bias": "large_cap|leader|momentum|value",
        "scanner_priority": ["trading_value", "trend_strength", "volume_surge", "leader_quality"],
        "trade_aggressiveness": "low|medium|high",
        "risk_tone": "conservative|normal|aggressive",
        "monitor_guidance": "hold_through_noise|defensive_exit|quick_take_profit",
        "market_regime_summary": "string",
        "policy_rationale": "string",
        "confidence": 0.0,
        "policy_source": "strategist",
        "policy_adjustment": {
            "adjustment_required": True,
            "baseline_retained": False,
            "baseline_retained_reason": "string",
            "adjustment_direction": "tighten|relax|mixed|none",
            "dominant_failure_pattern": "string",
            "addressed_failure_patterns": ["string"],
            "delta_fields": ["volume_ratio_min"],
            "hold_refresh_considered": True,
        },
        "strategy_refresh_trace": {
            "summary": "string",
            "bullets": ["string"],
            "stages": [
                {
                    "stage": "initial_frame|post_scanner_refresh|final_application",
                    "label": "string",
                    "summary": "string",
                    "requested": True,
                    "effective": False,
                    "reason": "string",
                }
            ],
        },
        "monitor_entry_policy": {
            "timeframe_minutes": 1,
            "breakout_lookback": 5,
            "volume_lookback": 5,
            "volume_ratio_min": 0.68,
            "min_extended_from_vwap_pct": -0.02,
            "max_extended_from_vwap_pct": 0.13,
            "pullback_min_pct": 0.008,
            "pullback_max_pct": 0.07,
            "reclaim_tolerance_pct": 0.0015,
            "breakout_buffer_pct": 0.0,
            "intent_cooldown_sec": 60,
            "require_vwap_reclaim": True,
            "require_rebound": True,
        },
        "report_focus": ["theme_accuracy", "exit_quality", "overtrading"],
    }
    contract = _stage_specific_llm_contract(call_kind, base_contract)
    raw = str(raw_response or "").strip()
    user = (
        "Fix or regenerate the strategist response as valid JSON.\n"
        "JSON contract:\n"
        f"{json.dumps(contract, ensure_ascii=False)}\n\n"
        "Compact input:\n"
        f"{json.dumps(compact_payload, ensure_ascii=False)}\n\n"
        "If Compact input contains available_themes, selected_themes must use only those theme names.\n"
        f"Previous attempt failure reason: {_classify_llm_parse_failure(raw)}\n"
        "Return only the repaired JSON object."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _messages_to_prompt_text(messages: List[Dict[str, str]]) -> str:
    rows: List[str] = []
    for m in messages:
        role = str(m.get("role") or "").strip().lower() or "unknown"
        content = str(m.get("content") or "")
        rows.append(f"[{role}]\n{content}")
    return "\n\n".join(rows).strip()


def _run_strategist_frame_llm(
    *,
    state: Dict[str, Any],
    policy: Dict[str, Any],
    payload: Dict[str, Any],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    run_id = str(state.get("run_id") or "").strip() or "strategist-unknown"
    runtime = strategist_runtime_settings(policy)
    explicit_llm_request = (
        policy.get("strategist_frame_use_llm") is not None
        or bool(str(os.getenv("STRATEGIST_FRAME_USE_LLM", "") or "").strip())
    )
    if not bool(runtime.get("requested")):
        return {}, {"enabled": False, "status": "disabled", "reason": "strategist_frame_llm_disabled"}

    if _env_bool("DRY_RUN", False):
        return {}, {"enabled": True, "status": "dry_run", "reason": "dry_run"}

    if not bool(runtime.get("uses_ai")) and not bool(explicit_llm_request):
        return {}, {"enabled": True, "status": "disabled", "reason": "strategist_provider_not_ai"}

    # Phase 5-4 / 6-1 LLM Policy Enforcement
    primary_model = normalize_openrouter_model_name(str(runtime.get("model") or ""))
    fallback_model = normalize_openrouter_model_name(str(runtime.get("fallback_model") or ""))
    max_retries = max(1, _to_int(runtime.get("retry_max"), 2))
    temperature = float(runtime.get("temperature") or 0.1)
    max_tokens = max(256, int(runtime.get("max_tokens") or 8192))
    timeout_sec = max(1.0, float(runtime.get("timeout_sec") or 15.0))
    retry_backoff_sec = max(0.0, float(runtime.get("retry_backoff_sec") or 0.0))

    router = LLMRouter.from_env()
    if router.client is None:
        return {}, {"enabled": True, "status": "unavailable", "reason": "llm_client_unavailable"}

    route_policy: Dict[str, Any] = {
        "temperature": float(temperature),
        "max_tokens": int(max_tokens),
        "timeout_sec": float(timeout_sec),
    }
    if _env_bool("STRATEGIST_FRAME_LLM_JSON_RESPONSE_FORMAT", True):
        route_policy["response_format"] = {"type": "json_object"}
        
    compact_payload = _build_compact_strategist_llm_payload(payload)
    quant_context_for_trace = (
        dict(compact_payload.get("quant_context") or {})
        if isinstance(compact_payload.get("quant_context"), dict)
        else {}
    )
    refresh_context = (
        compact_payload.get("commander_refresh_context")
        if isinstance(compact_payload.get("commander_refresh_context"), dict)
        else {}
    )
    if bool(refresh_context.get("requested")):
        refresh_token_cap = max(1024, int(_env_int("STRATEGIST_REFRESH_MAX_TOKENS") or 2048))
        if max_tokens > refresh_token_cap:
            max_tokens = int(refresh_token_cap)
            route_policy["max_tokens"] = int(max_tokens)
            effective_config = dict(runtime.get("llm_execution_effective_config") or {})
            effective_config["max_tokens"] = int(max_tokens)
            effective_config["refresh_token_cap_applied"] = True
            runtime["llm_execution_effective_config"] = effective_config

    llm_call_trace = {
        "primary_attempted": True,
        "primary_failed": False,
        "fallback_used": False,
        "final_model": primary_model,
        "final_provider": "strategist_router",
        "final_status": "pending",
        "llm_profile": str(runtime.get("llm_profile") or ""),
        "llm_policy_source": str(runtime.get("llm_policy_source") or ""),
        "llm_execution_profile": str(runtime.get("llm_execution_profile_name") or ((runtime.get("llm_execution_profile") or {}).get("name") or "")),
        "llm_execution_profile_name": str(runtime.get("llm_execution_profile_name") or ((runtime.get("llm_execution_profile") or {}).get("name") or "")),
        "llm_execution_profile_source": str(runtime.get("llm_execution_profile_source") or ((runtime.get("llm_execution_profile") or {}).get("policy_source") or "")),
        "llm_execution_effective_config": dict(
            runtime.get("llm_execution_effective_config")
            or {
                "temperature": float(temperature),
                "max_tokens": int(max_tokens),
                "timeout_sec": float(timeout_sec),
                "retry": {
                    "max_attempts": int(max_retries),
                    "backoff_sec": float(retry_backoff_sec),
                },
            }
        ),
    }

    def _persist_llm_artifacts(
        *,
        stage: str,
        prompt_value: Any,
        response_value: Any,
        status: str,
        reason: str = "",
        attempts_count: int = 1,
        repair: bool = False,
        active_model: str = "",
    ) -> Dict[str, Any]:
        try:
            call_kind = _resolve_strategist_llm_call_kind(compact_payload)
            stage_descriptor = strategist_llm_stage_descriptor(call_kind)
            stage_component = str(stage_descriptor.get("component") or "strategist_stage1_market_frame")
            stage_index = int(stage_descriptor.get("stage_index") or 1)
            stage_name = str(stage_descriptor.get("stage_name") or call_kind)
            prompt_payload = {
                "stage": str(stage or "theme_selection"),
                "stage_index": int(stage_index),
                "stage_name": stage_name,
                "call_kind": call_kind,
                "stage_component": stage_component,
                "provider": "strategist_router",
                "model": active_model,
                "payload": dict(compact_payload),
                "messages": [], # omitted for brevity in loop
                "prompt_text": str(prompt_value or ""),
                "temperature": float(temperature),
                "max_tokens": int(max_tokens),
                "timeout_sec": float(timeout_sec),
                "retry_max": int(max_retries),
                "retry_backoff_sec": float(retry_backoff_sec),
                "llm_execution_profile_name": str(runtime.get("llm_execution_profile_name") or ""),
                "llm_execution_profile_source": str(runtime.get("llm_execution_profile_source") or ""),
                "llm_execution_effective_config": dict(runtime.get("llm_execution_effective_config") or {}),
            }
            response_payload = {
                "stage": str(stage or "theme_selection"),
                "stage_index": int(stage_index),
                "stage_name": stage_name,
                "call_kind": call_kind,
                "stage_component": stage_component,
                "provider": "strategist_router",
                "model": active_model,
                "status": str(status or ""),
                "reason": str(reason or ""),
                "repair_used": bool(repair),
                "attempts": int(attempts_count),
                "llm_execution_profile_name": str(runtime.get("llm_execution_profile_name") or ""),
                "llm_execution_profile_source": str(runtime.get("llm_execution_profile_source") or ""),
                "llm_execution_effective_config": dict(runtime.get("llm_execution_effective_config") or {}),
                "response_text": str(response_value or ""),
            }
            meta_payload = {
                "component": "strategist",
                "llm_status": str(status or ""),
                "status": str(status or ""),
                "reason": str(reason or ""),
                "model": active_model,
                "attempts": int(attempts_count),
                "repair_used": bool(repair),
                "stage": str(stage or "theme_selection"),
                "stage_index": int(stage_index),
                "stage_name": stage_name,
                "call_kind": call_kind,
                "stage_component": stage_component,
                "llm_execution_profile_name": str(runtime.get("llm_execution_profile_name") or ""),
                "llm_execution_profile_source": str(runtime.get("llm_execution_profile_source") or ""),
                "llm_execution_effective_config": dict(runtime.get("llm_execution_effective_config") or {}),
            }
            legacy_refs = write_llm_artifact_bundle(
                state,
                artifact_name="strategist",
                prompt_payload=prompt_payload,
                response_payload=response_payload,
                meta_payload=meta_payload,
            )
            stage_refs = write_llm_artifact_bundle(
                state,
                artifact_name=stage_component,
                prompt_payload={**dict(prompt_payload), "artifact_role": "stage_specific"},
                response_payload={**dict(response_payload), "artifact_role": "stage_specific"},
                meta_payload={
                    **dict(meta_payload),
                    "component": stage_component,
                    "legacy_component": "strategist",
                    "artifact_role": "stage_specific",
                },
            )
            manifest_refs = write_llm_stage_manifest_entry(
                state,
                {
                    "stage_index": int(stage_index),
                    "stage_name": stage_name,
                    "call_kind": call_kind,
                    "component": stage_component,
                    "status": str(status or ""),
                    "reason": str(reason or ""),
                    "model": active_model,
                    "prompt_ref": str(stage_refs.get("prompt_ref") or ""),
                    "response_ref": str(stage_refs.get("response_ref") or ""),
                    "meta_ref": str(stage_refs.get("meta_ref") or ""),
                    "legacy_prompt_ref": str(legacy_refs.get("prompt_ref") or ""),
                    "legacy_response_ref": str(legacy_refs.get("response_ref") or ""),
                    "legacy_meta_ref": str(legacy_refs.get("meta_ref") or ""),
                    "strategist_summary_md_ref": str(legacy_refs.get("strategist_summary_md_ref") or ""),
                    "strategist_summary_json_ref": str(legacy_refs.get("strategist_summary_json_ref") or ""),
                },
            )
            return {
                **dict(legacy_refs),
                "llm_stage_component": stage_component,
                "llm_stage_index": int(stage_index),
                "llm_stage_name": stage_name,
                "llm_call_kind": call_kind,
                "stage_prompt_ref": str(stage_refs.get("prompt_ref") or ""),
                "stage_response_ref": str(stage_refs.get("response_ref") or ""),
                "stage_meta_ref": str(stage_refs.get("meta_ref") or ""),
                "llm_stage_manifest_ref": str(manifest_refs.get("llm_stage_manifest_ref") or ""),
            }
        except Exception:
            return {}

    attempts = 0
    repair_used = False
    current_model = primary_model
    last_reason = ""
    last_error_type = ""
    last_raw = ""
    
    while attempts < max_retries + 1:
        attempts += 1
        
        if attempts > 1 and attempts == max_retries + 1 and fallback_model:
            current_model = fallback_model
            llm_call_trace["primary_failed"] = True
            llm_call_trace["fallback_used"] = True
            
        route_policy["model"] = current_model
        llm_call_trace["final_model"] = current_model
        
        if repair_used and last_raw:
            route_policy["temperature"] = 0.0
            route_policy["max_tokens"] = min(max(384, int(max_tokens)), 768)
            messages = _build_strategist_llm_repair_messages(compact_payload, last_raw)
            stage_name = "theme_selection_repair"
        else:
            messages = _build_strategist_llm_messages(compact_payload)
            stage_name = "theme_selection"
            
        prompt_text = _messages_to_prompt_text(messages)
        llm_call_trace["prompt_chars"] = int(len(prompt_text))
        llm_call_trace["compact_payload_chars"] = int(
            len(json.dumps(compact_payload, ensure_ascii=False, separators=(",", ":")))
        )
        
        try:
            record_llm_prompt(
                run_id=run_id,
                agent="strategist",
                stage=stage_name,
                raw_input=dict(compact_payload),
                llm_prompt=prompt_text,
                decision_link={
                    "model": current_model,
                    "provider": "strategist_router",
                    "temperature": float(route_policy.get("temperature", 0.1)),
                    "max_tokens": int(route_policy.get("max_tokens", 320)),
                    "repair": repair_used,
                },
            )
        except Exception:
            pass

        t0 = time.perf_counter()
        try:
            raw = router.chat("strategist", messages, policy=route_policy)
            latency_ms = int((time.perf_counter() - t0) * 1000)
            
            obj = _extract_json_object(raw)
            if isinstance(obj, dict) and obj:
                overrides = _normalize_llm_overrides(obj)
                if overrides:
                    llm_call_trace["final_status"] = "ok"
                    llm_artifacts = _persist_llm_artifacts(
                        stage=stage_name, prompt_value=prompt_text, response_value=raw,
                        status="ok", attempts_count=attempts, repair=repair_used, active_model=current_model
                    )
                    try:
                        record_llm_response(
                            run_id=run_id, agent="strategist", stage=stage_name,
                            llm_response=str(raw or ""), parsed_output=dict(overrides),
                            decision_link={"status": "ok", "model": current_model, "attempts": attempts, "repair": repair_used},
                        )
                    except Exception:
                        pass
                    return overrides, {
                        "enabled": True, "status": "ok", "latency_ms": latency_ms,
                        "model": current_model, "attempts": attempts, "repair_used": repair_used,
                        "recovery_method": "" if str(raw or "").strip().startswith("{") else "prose_contract",
                        "llm_call_trace": dict(llm_call_trace),
                        "llm_execution_profile_name": str(runtime.get("llm_execution_profile_name") or ""),
                        "llm_execution_profile_source": str(runtime.get("llm_execution_profile_source") or ""),
                        "llm_execution_effective_config": dict(runtime.get("llm_execution_effective_config") or {}),
                        "prompt_ref": str(llm_artifacts.get("prompt_ref") or ""),
                        "response_ref": str(llm_artifacts.get("response_ref") or ""),
                        "prompt_hash": str(llm_artifacts.get("prompt_hash") or ""),
                        "response_hash": str(llm_artifacts.get("response_hash") or ""),
                        "llm_stage_component": str(llm_artifacts.get("llm_stage_component") or ""),
                        "llm_stage_index": int(llm_artifacts.get("llm_stage_index") or 0),
                        "llm_stage_name": str(llm_artifacts.get("llm_stage_name") or ""),
                        "llm_call_kind": str(llm_artifacts.get("llm_call_kind") or ""),
                        "stage_prompt_ref": str(llm_artifacts.get("stage_prompt_ref") or ""),
                        "stage_response_ref": str(llm_artifacts.get("stage_response_ref") or ""),
                        "stage_meta_ref": str(llm_artifacts.get("stage_meta_ref") or ""),
                        "llm_stage_manifest_ref": str(llm_artifacts.get("llm_stage_manifest_ref") or ""),
                        "quant_context": dict(quant_context_for_trace),
                    }
                    
            last_raw = raw
            last_reason = _classify_llm_parse_failure(raw)
            last_error_type = "ParseError"
            repair_used = True
            
            _persist_llm_artifacts(stage=stage_name, prompt_value=prompt_text, response_value=raw, status="parse_error", reason=last_reason, attempts_count=attempts, repair=repair_used, active_model=current_model)
            try:
                record_llm_response(run_id=run_id, agent="strategist", stage=stage_name, llm_response=str(raw or ""), parsed_output={}, decision_link={"status": "parse_error", "repair": repair_used})
            except Exception:
                pass
                
        except Exception as e:
            latency_ms = int((time.perf_counter() - t0) * 1000)
            last_error_type = type(e).__name__
            last_reason = str(e)
            _persist_llm_artifacts(stage=stage_name, prompt_value=prompt_text, response_value=f"ERROR:{last_error_type}:{last_reason}", status="error", reason=last_reason, attempts_count=attempts, repair=repair_used, active_model=current_model)
            try:
                record_llm_response(run_id=run_id, agent="strategist", stage=stage_name, llm_response=f"ERROR:{last_error_type}:{last_reason}", parsed_output={}, decision_link={"status": "error", "repair": repair_used})
            except Exception:
                pass

    llm_call_trace["final_status"] = "error" if last_error_type != "ParseError" else "parse_error"
    if fallback_model and not llm_call_trace["fallback_used"]:
        llm_call_trace["primary_failed"] = True
        
    return {}, {
        "enabled": True,
        "status": llm_call_trace["final_status"],
        "reason": last_reason,
        "error_type": last_error_type,
        "latency_ms": latency_ms,
        "model": current_model,
        "attempts": attempts,
        "repair_used": repair_used,
        "llm_call_trace": dict(llm_call_trace),
        "llm_execution_profile_name": str(runtime.get("llm_execution_profile_name") or ""),
        "llm_execution_profile_source": str(runtime.get("llm_execution_profile_source") or ""),
        "llm_execution_effective_config": dict(runtime.get("llm_execution_effective_config") or {}),
        "quant_context": dict(quant_context_for_trace),
    }

def _extract_themes(state: Dict[str, Any], policy: Dict[str, Any]) -> List[str]:
    return _extract_themes_r3_impl(state, policy, facade=_r3_sys.modules[__name__])


def _append_unique_text(out: List[str], seen: set[str], raw: Any) -> None:
    return _append_unique_text_r3_impl(out, seen, raw, facade=_r3_sys.modules[__name__])


def _theme_to_news_queries(theme: Any) -> List[str]:
    return _theme_to_news_queries_r3_impl(theme, facade=_r3_sys.modules[__name__])


def _theme_news_query_terms(theme_hints: List[str], *, limit: int = 8) -> List[str]:
    return _theme_news_query_terms_r3_impl(theme_hints, limit=limit,
        facade=_r3_sys.modules[__name__])


def _theme_component_symbols_for_news(
    *,
    state: Dict[str, Any],
    available_themes: List[Dict[str, Any]],
    theme_hints: List[str],
    limit: int,
) -> List[str]:
    return _theme_component_symbols_for_news_r3_impl(state=state, available_themes=available_themes,
        theme_hints=theme_hints, limit=limit, facade=_r3_sys.modules[__name__])


def _merge_news_collection_symbols(*, base_symbols: List[str], theme_symbols: List[str], limit: int) -> List[str]:
    return _merge_news_collection_symbols_r3_impl(base_symbols=base_symbols,
        theme_symbols=theme_symbols, limit=limit, facade=_r3_sys.modules[__name__])


def _build_market_news_query_targets(
    *,
    state: Dict[str, Any],
    policy: Dict[str, Any],
    global_signal: Dict[str, Any],
    market_context_inputs: Dict[str, float],
    theme_hints: List[str],
) -> List[str]:
    return _build_market_news_query_targets_r3_impl(state=state, policy=policy,
        global_signal=global_signal, market_context_inputs=market_context_inputs,
        theme_hints=theme_hints, facade=_r3_sys.modules[__name__])



def _build_market_news_query_reasoning(
    *,
    state: Dict[str, Any],
    policy: Dict[str, Any],
    global_signal: Dict[str, Any],
    market_context_inputs: Dict[str, float],
    theme_hints: List[str],
) -> str:
    return _build_market_news_query_reasoning_r3_impl(state=state, policy=policy,
        global_signal=global_signal, market_context_inputs=market_context_inputs,
        theme_hints=theme_hints, facade=_r3_sys.modules[__name__])



def _default_policy(user_policy: Dict[str, Any] | None) -> Dict[str, Any]:
    return _default_policy_r3_impl(user_policy, facade=_r3_sys.modules[__name__])


def _candidates_from_state(state: Dict[str, Any], k: int) -> List[Dict[str, str]]:
    # Highest priority: explicit candidates provided
    return _candidates_from_state_r3_impl(state, k, facade=_r3_sys.modules[__name__])


def _signal_score(sig: Any) -> float:
    return _signal_score_r3_impl(sig, facade=_r3_sys.modules[__name__])


def _to_float(v: Any, default: float = 0.0) -> float:
    return _to_float_r3_impl(v, default, facade=_r3_sys.modules[__name__])


def _clamp(x: float, lo: float, hi: float) -> float:
    return _clamp_r3_impl(x, lo, hi, facade=_r3_sys.modules[__name__])


def _risk_regime_label(score: float) -> str:
    if score >= 0.20:
        return "risk_on"
    if score <= -0.20:
        return "risk_off"
    return "neutral"


def _market_sentiment_label(score: float) -> str:
    if score >= 0.15:
        return "bullish"
    if score <= -0.15:
        return "bearish"
    return "neutral"


def _extract_market_context_inputs(state: Dict[str, Any]) -> Dict[str, float]:
    return _extract_market_context_inputs_r3_impl(state, facade=_r3_sys.modules[__name__])


def _market_structure_label(
    *,
    state: Dict[str, Any],
    global_score: float,
    market_context_inputs: Dict[str, float],
) -> Tuple[str, Dict[str, Any]]:
    return _market_structure_label_r3_impl(state=state, global_score=global_score,
        market_context_inputs=market_context_inputs, facade=_r3_sys.modules[__name__])


def _extract_theme_symbol_index(state: Dict[str, Any], policy: Dict[str, Any]) -> Dict[str, set[str]]:
    return _extract_theme_symbol_index_r3_impl(state, policy, facade=_r3_sys.modules[__name__])


def _merge_theme_symbol_map(
    existing: Any,
    *,
    themes: List[str],
    candidate_symbols: List[str],
    protect_existing_themes: bool = False,
) -> Dict[str, List[str]]:
    return _merge_theme_symbol_map_r3_impl(existing, themes=themes,
        candidate_symbols=candidate_symbols, protect_existing_themes=protect_existing_themes,
        facade=_r3_sys.modules[__name__])


def _theme_packet_symbol_map_is_authoritative(packet: Dict[str, Any]) -> bool:
    if not isinstance(packet, dict):
        return False
    return str(packet.get("status") or "").strip().lower() == "ok" and not bool(packet.get("fallback_used"))


def _merge_theme_packet_into_state(state: Dict[str, Any], packet: Dict[str, Any]) -> None:
    return _merge_theme_packet_into_state_r3_impl(state, packet, facade=_r3_sys.modules[__name__])


def _extract_theme_names_from_any(raw: Any, *, limit: int = 8) -> List[str]:
    return _extract_theme_names_from_any_r3_impl(raw, limit=limit, facade=_r3_sys.modules[__name__])


def _theme_packet_available_themes(packet: Dict[str, Any], *, limit: int = 8) -> List[Dict[str, Any]]:
    return _theme_packet_available_themes_r3_impl(packet, limit=limit,
        facade=_r3_sys.modules[__name__])


def _resolve_selected_themes_from_api(
    *,
    available_themes: List[Dict[str, Any]],
    themes: List[str],
    raw_selected: Any,
    limit: int = 5,
) -> List[str]:
    return _resolve_selected_themes_from_api_r3_impl(available_themes=available_themes,
        themes=themes, raw_selected=raw_selected, limit=limit, facade=_r3_sys.modules[__name__])


def _build_theme_strategy_surface(
    *,
    available_themes: List[Dict[str, Any]],
    selected_themes: List[str],
    playbook: str,
    theme_strength_packet: Dict[str, Any],
    raw_theme_strategy: Any,
) -> Dict[str, Any]:
    return _build_theme_strategy_surface_r3_impl(available_themes=available_themes,
        selected_themes=selected_themes, playbook=playbook,
        theme_strength_packet=theme_strength_packet, raw_theme_strategy=raw_theme_strategy,
        facade=_r3_sys.modules[__name__])


def _news_context_summary(
    news_signal_map: Dict[str, Dict[str, Any]],
    news_items_by_symbol: Dict[str, List[Any]],
) -> Dict[str, Any]:
    return _news_context_summary_r3_impl(news_signal_map, news_items_by_symbol,
        facade=_r3_sys.modules[__name__])


def _merge_news_contexts(candidate_ctx: Dict[str, Any], market_ctx: Dict[str, Any]) -> Dict[str, Any]:
    return _merge_news_contexts_r3_impl(candidate_ctx, market_ctx, facade=_r3_sys.modules[__name__])


def _theme_strength_map(
    *,
    themes: List[str],
    candidates: List[Dict[str, Any]],
    theme_scores: Dict[str, Any],
    theme_index: Dict[str, set[str]],
) -> Dict[str, float]:
    return _theme_strength_map_r3_impl(themes=themes, candidates=candidates,
        theme_scores=theme_scores, theme_index=theme_index, facade=_r3_sys.modules[__name__])


def _compose_regime_score(
    *,
    global_score: float,
    news_score: float,
    market_context_inputs: Dict[str, float],
) -> float:
    return _compose_regime_score_r3_impl(global_score=global_score, news_score=news_score,
        market_context_inputs=market_context_inputs, facade=_r3_sys.modules[__name__])


def _pick_playbook(*, market_structure: str, market_regime: str, market_sentiment: str) -> str:
    return _pick_playbook_r3_impl(market_structure=market_structure, market_regime=market_regime,
        market_sentiment=market_sentiment, facade=_r3_sys.modules[__name__])


def _scanner_priority(playbook: str, market_regime: str) -> List[str]:
    return _scanner_priority_r3_impl(playbook, market_regime, facade=_r3_sys.modules[__name__])


def _scanner_bias(*, playbook: str, market_regime: str) -> str:
    return _scanner_bias_r3_impl(playbook=playbook, market_regime=market_regime,
        facade=_r3_sys.modules[__name__])


def _build_scanner_bias_context_seed(
    *,
    playbook: str,
    scanner_bias: str,
    monitor_entry_policy: Dict[str, Any],
) -> Dict[str, Any]:
    return _build_scanner_bias_context_seed_r3_impl(playbook=playbook, scanner_bias=scanner_bias,
        monitor_entry_policy=monitor_entry_policy, facade=_r3_sys.modules[__name__])


def _avoid_themes(*, market_sentiment: str, playbook: str) -> List[str]:
    return _avoid_themes_r3_impl(market_sentiment=market_sentiment, playbook=playbook,
        facade=_r3_sys.modules[__name__])


def _trade_aggressiveness(*, market_regime: str, market_structure: str) -> str:
    if market_regime == "risk_off" or str(market_structure).startswith("high_volatility"):
        return "low"
    if market_regime == "risk_on" and str(market_structure).startswith("trend"):
        return "high"
    return "medium"


def _risk_tone(aggressiveness: str) -> str:
    if aggressiveness == "low":
        return "conservative"
    if aggressiveness == "high":
        return "aggressive"
    return "normal"


def _monitor_guidance(*, market_regime: str, playbook: str) -> str:
    if market_regime == "risk_off" or playbook == "defensive":
        return "defensive_exit"
    if playbook == "breakout":
        return "hold_through_noise"
    return "quick_take_profit"


_TACTICAL_STRATEGIES = TACTIC_IDS
_TACTICAL_SUBTYPES = TACTICAL_SUBTYPES

_TACTICAL_STRATEGY_BY_PLAYBOOK = {
    "breakout": "opening_range_breakout",
    "pullback": "vwap_reclaim_pullback",
    "reversal": "reversal_reclaim",
    "defensive": "defensive_observe",
}

_CANDIDATE_WATCH_DEFAULT_RANK = {
    **dict(TACTIC_DEFAULT_RUNNER_UP_RANK),
}

_CANDIDATE_WATCH_CASCADE_ALLOWED_REASONS = (
    "too_extended_from_vwap",
    "breakout_not_ready",
    "volume_insufficient",
    "volume_confirmation_missing",
    "below_vwap_reclaim_not_ready",
    "pullback_below_vwap_reclaim_not_ready",
    "pullback_not_mature",
)

_CANDIDATE_WATCH_CASCADE_BLOCKED_REASONS = (
    "cost_filter_failed",
    "risk_policy_block",
    "closeout_window",
    "open_position_present",
    "daily_loss_limit",
    "broker_truth_mismatch",
    "data_quality_guard",
    "buy_blocked_post_exit_cooldown",
    "buy_blocked_closeout_window",
)


def _norm_playbook(value: Any, *, default: str = "") -> str:
    return normalize_tactic_playbook(value, default=default)


def _default_tactical_strategy(playbook: str) -> str:
    return default_tactic_for_playbook(playbook)


def _normalize_tactical_strategy(value: Any, *, playbook: str) -> str:
    return normalize_tactic_id(value, playbook=playbook)


def _normalize_tactical_subtype(value: Any, *, tactical_strategy: str) -> str:
    return normalize_quant_tactical_subtype(value, tactic_id=tactical_strategy)


def _unit_score(value: Any, default: float = 0.0) -> float:
    return _unit_score_r3_impl(value, default, facade=_r3_sys.modules[__name__])


def _deterministic_strategy_scores(
    *,
    playbook: str,
    market_regime: str,
    market_sentiment: str,
    market_structure: str,
    market_context_inputs: Dict[str, Any],
) -> Dict[str, float]:
    return _deterministic_strategy_scores_r3_impl(playbook=playbook, market_regime=market_regime,
        market_sentiment=market_sentiment, market_structure=market_structure,
        market_context_inputs=market_context_inputs, facade=_r3_sys.modules[__name__])


def _normalize_strategy_scores(
    raw: Any,
    *,
    playbook: str,
    market_regime: str,
    market_sentiment: str,
    market_structure: str,
    market_context_inputs: Dict[str, Any],
) -> Dict[str, float]:
    return _normalize_strategy_scores_r3_impl(raw, playbook=playbook, market_regime=market_regime,
        market_sentiment=market_sentiment, market_structure=market_structure,
        market_context_inputs=market_context_inputs, facade=_r3_sys.modules[__name__])


def _normalize_rejected_strategy_reasons(
    raw: Any,
    *,
    tactical_strategy: str,
    strategy_scores: Dict[str, float],
) -> Dict[str, str]:
    return _normalize_rejected_strategy_reasons_r3_impl(raw, tactical_strategy=tactical_strategy,
        strategy_scores=strategy_scores, facade=_r3_sys.modules[__name__])


def _sanitize_reason_list(raw: Any, defaults: Tuple[str, ...]) -> List[str]:
    return _sanitize_reason_list_r3_impl(raw, defaults, facade=_r3_sys.modules[__name__])


def _normalize_candidate_watch_policy(
    raw: Any,
    *,
    tactical_strategy: str,
    playbook: str,
    market_regime: str,
    risk_tone: str,
    trade_aggressiveness: str,
) -> Dict[str, Any]:
    return _normalize_candidate_watch_policy_r3_impl(raw, tactical_strategy=tactical_strategy,
        playbook=playbook, market_regime=market_regime, risk_tone=risk_tone,
        trade_aggressiveness=trade_aggressiveness, facade=_r3_sys.modules[__name__])


def _macro_stress_overlay(global_signal: Dict[str, Any]) -> Dict[str, Any]:
    return _macro_stress_overlay_r3_impl(global_signal, facade=_r3_sys.modules[__name__])


def _apply_macro_stress_to_monitor_frame(
    *,
    global_signal: Dict[str, Any],
    monitor_guidance: str,
    risk_tone: str,
    trade_aggressiveness: str,
    exit_policy: Dict[str, Any],
    report_focus: List[str],
) -> Tuple[str, str, str, Dict[str, Any], List[str], Dict[str, Any]]:
    return _apply_macro_stress_to_monitor_frame_r3_impl(global_signal=global_signal,
        monitor_guidance=monitor_guidance, risk_tone=risk_tone,
        trade_aggressiveness=trade_aggressiveness, exit_policy=exit_policy,
        report_focus=report_focus, facade=_r3_sys.modules[__name__])


def _condition_search_source_enabled() -> bool:
    return _env_bool("KIWOOM_CANDIDATE_ENABLE_CONDITION_SEARCH", False)


def _monitor_policy(
    *,
    state: Dict[str, Any] | None = None,
    policy: Dict[str, Any] | None = None,
    monitor_guidance: str,
    trade_aggressiveness: str,
    risk_tone: str,
) -> Dict[str, Any]:
    return _monitor_policy_r3_impl(state=state, policy=policy, monitor_guidance=monitor_guidance,
        trade_aggressiveness=trade_aggressiveness, risk_tone=risk_tone,
        facade=_r3_sys.modules[__name__])


def _exit_policy(
    *,
    playbook: str,
    monitor_guidance: str,
    trade_aggressiveness: str,
    risk_tone: str,
) -> Dict[str, Any]:
    return _exit_policy_r3_impl(playbook=playbook, monitor_guidance=monitor_guidance,
        trade_aggressiveness=trade_aggressiveness, risk_tone=risk_tone,
        facade=_r3_sys.modules[__name__])


def _scanner_source_policy(
    *,
    playbook: str,
    risk_tone: str,
    trade_aggressiveness: str,
    market_regime: str,
    themes: List[str],
    fear_index: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return _scanner_source_policy_r3_impl(playbook=playbook, risk_tone=risk_tone,
        trade_aggressiveness=trade_aggressiveness, market_regime=market_regime, themes=themes,
        fear_index=fear_index, facade=_r3_sys.modules[__name__])


def _strategy_policy_score_weights() -> Dict[str, float]:
    return _strategy_policy_score_weights_r3_impl(facade=_r3_sys.modules[__name__])


def _strategy_policy_entry_policy() -> Dict[str, Any]:
    return _strategy_policy_entry_policy_r3_impl(facade=_r3_sys.modules[__name__])


def _build_strategy_policy(
    *,
    market_regime: str,
    market_sentiment: str,
    playbook: str,
    trade_aggressiveness: str,
    risk_tone: str,
    monitor_guidance: str,
    global_signal: Dict[str, Any],
    market_context_inputs: Dict[str, float],
    themes: List[str],
    avoid_themes: List[str],
    theme_strength: Dict[str, Any],
    scanner_priority: List[str],
    scanner_source_policy: Dict[str, Any],
    scanner_bias_context: Dict[str, Any],
    monitor_entry_policy: Dict[str, Any],
    monitor_policy: Dict[str, Any],
    exit_policy: Dict[str, Any],
    macro_stress_overlay: Dict[str, Any],
    news_ctx: Dict[str, Any],
) -> Dict[str, Any]:
    return _build_strategy_policy_r3_impl(market_regime=market_regime,
        market_sentiment=market_sentiment, playbook=playbook,
        trade_aggressiveness=trade_aggressiveness, risk_tone=risk_tone,
        monitor_guidance=monitor_guidance, global_signal=global_signal,
        market_context_inputs=market_context_inputs, themes=themes, avoid_themes=avoid_themes,
        theme_strength=theme_strength, scanner_priority=scanner_priority,
        scanner_source_policy=scanner_source_policy, scanner_bias_context=scanner_bias_context,
        monitor_entry_policy=monitor_entry_policy, monitor_policy=monitor_policy,
        exit_policy=exit_policy, macro_stress_overlay=macro_stress_overlay, news_ctx=news_ctx,
        facade=_r3_sys.modules[__name__])


def _build_commander_context_summary(
    *,
    state: Dict[str, Any],
    commander_decision: Dict[str, Any],
    runtime_phase: str,
    market_regime: str,
    playbook: str,
) -> Dict[str, Any]:
    return _build_commander_context_summary_r3_impl(state=state,
        commander_decision=commander_decision, runtime_phase=runtime_phase,
        market_regime=market_regime, playbook=playbook, facade=_r3_sys.modules[__name__])


def _build_strategist_plan(
    *,
    commander_context: Dict[str, Any],
    playbook: str,
    candidate_symbols: List[str],
    themes: List[str],
    avoid_themes: List[str],
    scanner_priority: List[str],
    monitor_guidance: str,
    trade_aggressiveness: str,
    risk_tone: str,
    news_query_reasoning: str,
    monitor_policy: Dict[str, Any],
    exit_policy: Dict[str, Any],
) -> Dict[str, Any]:
    return _build_strategist_plan_r3_impl(commander_context=commander_context, playbook=playbook,
        candidate_symbols=candidate_symbols, themes=themes, avoid_themes=avoid_themes,
        scanner_priority=scanner_priority, monitor_guidance=monitor_guidance,
        trade_aggressiveness=trade_aggressiveness, risk_tone=risk_tone,
        news_query_reasoning=news_query_reasoning, monitor_policy=monitor_policy,
        exit_policy=exit_policy, facade=_r3_sys.modules[__name__])


def _build_market_regime_summary(
    *,
    market_regime: str,
    market_sentiment: str,
    market_structure: str,
    playbook: str,
    global_signal: Dict[str, Any],
) -> str:
    return _build_market_regime_summary_r3_impl(market_regime=market_regime,
        market_sentiment=market_sentiment, market_structure=market_structure, playbook=playbook,
        global_signal=global_signal, facade=_r3_sys.modules[__name__])


def _build_strategist_monitor_entry_policy_seed(
    *,
    playbook: str,
    market_regime: str,
    monitor_guidance: str,
    risk_tone: str,
    trade_aggressiveness: str,
) -> Dict[str, Any]:
    return _build_strategist_monitor_entry_policy_seed_r3_impl(playbook=playbook,
        market_regime=market_regime, monitor_guidance=monitor_guidance, risk_tone=risk_tone,
        trade_aggressiveness=trade_aggressiveness, facade=_r3_sys.modules[__name__])


def _build_monitor_entry_policy_rationale(
    *,
    playbook: str,
    market_regime: str,
    market_sentiment: str,
    monitor_guidance: str,
    risk_tone: str,
    trade_aggressiveness: str,
    validation_meta: Dict[str, Any],
) -> str:
    return _build_monitor_entry_policy_rationale_r3_impl(playbook=playbook,
        market_regime=market_regime, market_sentiment=market_sentiment,
        monitor_guidance=monitor_guidance, risk_tone=risk_tone,
        trade_aggressiveness=trade_aggressiveness, validation_meta=validation_meta,
        facade=_r3_sys.modules[__name__])


def _build_strategy_policy_provenance(*, commander_context: Dict[str, Any]) -> Dict[str, Any]:
    return _build_strategy_policy_provenance_r3_impl(commander_context=commander_context,
        facade=_r3_sys.modules[__name__])


def _report_focus(*, playbook: str, themes: List[str]) -> List[str]:
    if playbook == "defensive":
        return ["theme_accuracy", "exit_quality", "overtrading", "guard_blocks"]
    if playbook == "breakout":
        return ["theme_accuracy", "scanner_fit", "exit_quality", "overtrading"]
    return ["theme_accuracy", "scanner_fit", "exit_quality", "overtrading"]


def _augment_strategy_fields(
    *,
    themes: List[str],
    avoid_themes: List[str],
    scanner_priority: List[str],
    report_focus: List[str],
    market_context_inputs: Dict[str, float],
    news_ctx: Dict[str, Any],
) -> Tuple[List[str], List[str], List[str], List[str]]:
    return _augment_strategy_fields_r3_impl(themes=themes, avoid_themes=avoid_themes,
        scanner_priority=scanner_priority, report_focus=report_focus,
        market_context_inputs=market_context_inputs, news_ctx=news_ctx,
        facade=_r3_sys.modules[__name__])


def _key_events(
    *,
    state: Dict[str, Any],
    global_signal: Dict[str, Any],
    news_signal_map: Dict[str, Dict[str, Any]],
    market_regime: str,
    playbook: str,
    market_context_inputs: Dict[str, float],
    news_ctx: Dict[str, Any],
    theme_strength: Dict[str, float],
) -> List[str]:
    return _key_events_r3_impl(state=state, global_signal=global_signal,
        news_signal_map=news_signal_map, market_regime=market_regime, playbook=playbook,
        market_context_inputs=market_context_inputs, news_ctx=news_ctx,
        theme_strength=theme_strength, facade=_r3_sys.modules[__name__])


def _extract_ai_overrides(state: Dict[str, Any], policy: Dict[str, Any]) -> Dict[str, Any]:
    # External LLM strategists can inject this shape without breaking node contract.
    return _extract_ai_overrides_r3_impl(state, policy, facade=_r3_sys.modules[__name__])


def _merge_override_text_list(base: List[str], override_values: Any, *, limit: int = 8) -> List[str]:
    return _merge_override_text_list_r3_impl(base, override_values, limit=limit,
        facade=_r3_sys.modules[__name__])


def _build_strategic_answers(
    *,
    commander_context: Dict[str, Any],
    market_regime: str,
    market_sentiment: str,
    key_events: List[str],
    themes: List[str],
    avoid_themes: List[str],
    playbook: str,
    scanner_bias: str,
    scanner_priority: List[str],
    trade_aggressiveness: str,
    risk_tone: str,
    monitor_guidance: str,
    report_focus: List[str],
    recent_strategy_feedback: Dict[str, Any],
    strategy_memory: Dict[str, Any],
    read_model_facts: Dict[str, Any],
    reports_root: str | Path | None = None,
) -> Dict[str, Any]:
    return _build_strategic_answers_r3_impl(commander_context=commander_context,
        market_regime=market_regime, market_sentiment=market_sentiment, key_events=key_events,
        themes=themes, avoid_themes=avoid_themes, playbook=playbook, scanner_bias=scanner_bias,
        scanner_priority=scanner_priority, trade_aggressiveness=trade_aggressiveness,
        risk_tone=risk_tone, monitor_guidance=monitor_guidance, report_focus=report_focus,
        recent_strategy_feedback=recent_strategy_feedback, strategy_memory=strategy_memory,
        read_model_facts=read_model_facts, reports_root=reports_root,
        facade=_r3_sys.modules[__name__])


def _make_event_logger(state: Dict[str, Any]) -> Any:
    injected = state.get("event_logger")
    if injected is not None and hasattr(injected, "log"):
        return injected
    from libs.core.event_logger import EventLogger, resolve_event_log_path

    return EventLogger(log_path=resolve_event_log_path())


def _emit_strategist_event(
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
            stage="strategist",
            event=name,
            event_name=f"strategist.{name}",
            payload=dict(payload or {}),
            level=level,
            agent="strategist",
            symbol=str(symbol or ""),
        )
    except Exception:
        return


def _log_strategist_summary(state: Dict[str, Any], payload: Dict[str, Any]) -> None:
    try:
        logger = _make_event_logger(state)
        run_id = str(state.get("run_id") or "strategist-node")
        logger.log(run_id=run_id, stage="strategist", event="summary", payload=dict(payload))
    except Exception:
        return


def _log_strategist_llm_result(state: Dict[str, Any], payload: Dict[str, Any]) -> None:
    try:
        logger = _make_event_logger(state)
        run_id = str(state.get("run_id") or "strategist-node")
        logger.log(run_id=run_id, stage="strategist_llm", event="result", payload=dict(payload))
    except Exception:
        return


def _sample_news_for_evidence(
    news_items_by_symbol: Dict[str, List[Any]],
    *,
    max_symbols: int = 8,
    max_items_per_symbol: int = 3,
) -> Dict[str, Any]:
    return _sample_news_for_evidence_r3_impl(news_items_by_symbol, max_symbols=max_symbols,
        max_items_per_symbol=max_items_per_symbol, facade=_r3_sys.modules[__name__])


def _rank_news_evidence_rows(
    items_by_target: Dict[str, List[Any]],
    signal_map: Dict[str, Dict[str, Any]],
    *,
    used_targets: List[str],
    scope: str,
    max_rows: int = 10,
) -> List[Dict[str, Any]]:
    return _rank_news_evidence_rows_r3_impl(items_by_target, signal_map, used_targets=used_targets,
        scope=scope, max_rows=max_rows, facade=_r3_sys.modules[__name__])


def _global_sentiment_breakdown_payload(global_signal: Dict[str, Any]) -> Dict[str, Any]:
    return _global_sentiment_breakdown_payload_r3_impl(global_signal,
        facade=_r3_sys.modules[__name__])


def _merge_news_samples(*samples: Dict[str, Any], limit: int = 12) -> Dict[str, Any]:
    return _merge_news_samples_r3_impl(*samples, limit=limit, facade=_r3_sys.modules[__name__])


def strategist_node(state: Dict[str, Any]) -> Dict[str, Any]:
    policy = _default_policy(state.get("policy"))
    k = _resolve_top_n_candidates(policy)
    policy["candidate_k"] = int(k)

    # 1) candidates (injected or generated)
    candidates, universe_candidates = strat_ctx_candidates_universe_candidates(state=state, k=k, policy=policy, facade=_r3_sys.modules[__name__])

    if not candidates:
        source = str(policy.get("candidate_source") or "top_picks")
        if source == "market_rank":
            gen = MarketRankCandidateGenerator()
            # tolerate signature differences
            try:
                symbols = gen.generate(state=state, policy=policy, k=k)
            except TypeError:
                try:
                    symbols = gen.generate(state=state, k=k)
                except TypeError:
                    symbols = gen.generate(state=state)
            candidates = [{"symbol": str(s), "why": "market_rank"} for s in symbols[:k]]
        else:
            # top_picks (M18-2): generator signature is generate(state)
            gen = TopPicksCandidateGenerator(
                rank_mode=str(policy.get("candidate_rank_mode") or "value"),
                rank_topn=int(policy.get("candidate_rank_topn") or 30),
                topk=int(policy.get("candidate_topk") or k),
            )
            symbols = gen.generate(state=state)
            candidates = [{"symbol": str(s), "why": "top_picks"} for s in symbols[:k]]

    # Absolute fallback:
    # - source is configurable (`fallback_candidate_symbols`, `FALLBACK_CANDIDATE_SYMBOLS`)
    # - static default remains as last-resort compatibility path
    if not candidates:
        fallback, fallback_source = resolve_fallback_symbols(state=state, policy=policy, limit=k)
        fallback_why = "fallback_static" if fallback_source == "static_default" else "fallback_configured"
        candidates = [{"symbol": s, "why": fallback_why, "fallback_source": fallback_source} for s in fallback]
        state["strategist_fallback_source"] = fallback_source

    state["universe_candidates"] = universe_candidates
    symbols = [c["symbol"] for c in candidates]

    # 2) Global sentiment (score + data-quality signal)
    now = int(time.time())
    global_enabled = bool(policy.get("use_global_sentiment", True)) or state.get("mock_global_sentiment") is not None
    if global_enabled:
        try:
            global_signal = dict(compute_global_sentiment_signal(state=state, policy=policy))
        except Exception:
            global_signal = make_signal(
                score=0.0,
                status=SIGNAL_STATUS_FALLBACK,
                source="strategist_node",
                reason="global_sentiment_exception",
                ts=now,
            )
    else:
        global_signal = make_signal(
            score=0.0,
            status=SIGNAL_STATUS_FALLBACK,
            source="global_policy",
            reason="global_sentiment_disabled",
            ts=now,
        )
    gs = _signal_score(global_signal)
    policy["global_sentiment"] = float(gs)
    # Keep canonical state-level score and signal shape for downstream nodes.
    state["global_sentiment"] = {"score": float(gs)}
    state["global_sentiment_signal"] = dict(global_signal)
    market_context_inputs = _extract_market_context_inputs(state)
    theme_strength_packet = build_theme_strength_packet(state=state, policy=policy)
    state["theme_strength_packet"] = dict(theme_strength_packet)
    _merge_theme_packet_into_state(state, theme_strength_packet)
    available_themes = _theme_packet_available_themes(theme_strength_packet)
    state["available_themes"] = list(available_themes)
    theme_hints = _extract_themes(state, policy)
    news_query_targets = _build_market_news_query_targets(
        state=state,
        policy=policy,
        global_signal=global_signal,
        market_context_inputs=market_context_inputs,
        theme_hints=theme_hints,
    )
    news_query_reasoning = _build_market_news_query_reasoning(
        state=state,
        policy=policy,
        global_signal=global_signal,
        market_context_inputs=market_context_inputs,
        theme_hints=theme_hints,
    )
    state["news_query_targets"] = list(news_query_targets)
    state["news_query_reasoning"] = news_query_reasoning
    theme_news_symbol_limit = _to_int(
        policy.get("theme_news_symbol_limit")
        if policy.get("theme_news_symbol_limit") is not None
        else os.getenv("STRATEGIST_NEWS_THEME_COMPONENT_SYMBOL_LIMIT", "12"),
        12,
    )
    news_collection_limit = _to_int(
        policy.get("news_collection_symbol_limit")
        if policy.get("news_collection_symbol_limit") is not None
        else os.getenv("STRATEGIST_NEWS_COLLECTION_SYMBOL_LIMIT", "20"),
        20,
    )
    news_collection_policy, news_collection_symbols, theme_news_symbols = strat_ctx_news_collection_policy_news_collection_s(state=state, theme_news_symbol_limit=theme_news_symbol_limit, available_themes=available_themes, theme_hints=theme_hints, symbols=symbols, news_collection_limit=news_collection_limit, news_query_targets=news_query_targets, policy=policy, facade=_r3_sys.modules[__name__])
    state["news_collection_policy"] = dict(news_collection_policy)
    state["news_collection_symbols"] = list(news_collection_symbols)
    state["news_theme_component_symbols"] = list(theme_news_symbols)

    # policy adjustment based on global sentiment
    # - risk-off: max_risk decreases, min_confidence increases
    # - risk-on : max_risk increases, min_confidence decreases
    adjust_policy_for_global_sentiment(gs=gs, policy=policy)

    # 3) News analysis (score + data-quality signal)
    news_items_by_symbol = {s: [] for s in news_collection_symbols}
    news_signal_map: Dict[str, Dict[str, Any]] = {}
    market_news_items_by_target = {q: [] for q in news_query_targets}
    market_news_signal_map: Dict[str, Dict[str, Any]] = {}

    if bool(policy.get("use_news_analysis", False)) or state.get("mock_news_sentiment") is not None:
        # mock_news_sentiment path is handled inside score_news_sentiment_signal.
        if bool(policy.get("use_news_analysis", False)) or state.get("mock_news_items") is not None:
            if news_collection_symbols:
                news_items_by_symbol = collect_news_items(news_collection_symbols, state=state, policy=policy)
            if news_query_targets:
                market_news_items_by_target = collect_news_items(news_query_targets, state=state, policy=policy)
        try:
            if news_collection_symbols:
                news_signal_map = score_news_sentiment_signal(
                    news_items_by_symbol,
                    state=state,
                    policy=policy,
                    symbols=news_collection_symbols,
                )
            else:
                news_signal_map = {}
            if news_query_targets:
                market_news_signal_map = score_news_sentiment_signal(
                    market_news_items_by_target,
                    state=state,
                    policy=policy,
                    symbols=news_query_targets,
                )
            else:
                market_news_signal_map = {}
        except Exception:
            market_news_signal_map, news_signal_map = news_exception_fallback_signals(news_collection_symbols=news_collection_symbols, news_query_targets=news_query_targets, now=now, facade=_r3_sys.modules[__name__])
    else:
        market_news_signal_map, news_signal_map = news_disabled_signals(news_collection_symbols=news_collection_symbols, news_query_targets=news_query_targets, now=now, facade=_r3_sys.modules[__name__])

    candidate_news_ctx, market_news_ctx, news_avg_score, news_ctx, news_sent = summarize_news_contexts(market_news_items_by_target=market_news_items_by_target, market_news_signal_map=market_news_signal_map, news_collection_symbols=news_collection_symbols, news_items_by_symbol=news_items_by_symbol, news_signal_map=news_signal_map, facade=_r3_sys.modules[__name__])

    state["policy"] = policy
    state["candidates"] = candidates
    # store per-symbol news items (dict)
    state["news_items"] = news_items_by_symbol
    state["news_sentiment"] = news_sent
    state["news_sentiment_signal"] = news_signal_map
    state["candidate_news_items"] = dict(news_items_by_symbol)
    state["candidate_news_context"] = dict(candidate_news_ctx)
    state["market_news_items"] = dict(market_news_items_by_target)
    state["market_news_sentiment"] = {q: _signal_score(market_news_signal_map.get(q)) for q in news_query_targets}
    state["market_news_sentiment_signal"] = dict(market_news_signal_map)
    state["market_news_context"] = dict(market_news_ctx)

    # 4) Candidate rerank (M18-5): apply weights and negative-news filter, then risk-off count reduction
    candidates = rerank_candidates_by_news_and_global(candidates=candidates, gs=gs, k=k, news_sent=news_sent, policy=policy)

    state["candidates"] = candidates
    candidate_symbols, theme_strength, themes = project_theme_candidate_inputs(candidates=candidates, policy=policy, state=state, theme_hints=theme_hints, facade=_r3_sys.modules[__name__])

    state["themes"] = themes
    state["candidate_symbols"] = list(candidate_symbols)
    state["theme_map"] = _merge_theme_symbol_map(
        state.get("theme_map"),
        themes=list(themes),
        candidate_symbols=list(candidate_symbols),
        protect_existing_themes=_theme_packet_symbol_map_is_authoritative(theme_strength_packet),
    )
    state["sector_map"] = _merge_theme_symbol_map(
        state.get("sector_map"),
        themes=list(themes),
        candidate_symbols=list(candidate_symbols),
        protect_existing_themes=_theme_packet_symbol_map_is_authoritative(theme_strength_packet),
    )

    market_regime, market_sentiment, regime_score, sentiment_score = score_market_regime_and_sentiment(gs=gs, market_context_inputs=market_context_inputs, news_avg_score=news_avg_score, news_ctx=news_ctx, facade=_r3_sys.modules[__name__])
    avoid_themes, exit_policy, market_structure, monitor_guidance, monitor_policy, playbook, pre_llm_market_regime, pre_llm_market_sentiment, pre_llm_market_structure, pre_llm_monitor_guidance, pre_llm_playbook, pre_llm_risk_tone, pre_llm_trade_aggressiveness, regime_factors, risk_tone, scanner_bias, scanner_priority, trade_aggressiveness = strat_ctx_avoid_themes_exit_policy(state=state, gs=gs, market_context_inputs=market_context_inputs, market_regime=market_regime, market_sentiment=market_sentiment, policy=policy, facade=_r3_sys.modules[__name__])
    macro_stress_overlay = _macro_stress_overlay(global_signal)
    report_focus = _report_focus(playbook=playbook, themes=themes)
    themes, avoid_themes, scanner_priority, report_focus = _augment_strategy_fields(
        themes=themes,
        avoid_themes=avoid_themes,
        scanner_priority=scanner_priority,
        report_focus=report_focus,
        market_context_inputs=market_context_inputs,
        news_ctx=news_ctx,
    )
    key_events = _key_events(
        state=state,
        global_signal=global_signal,
        news_signal_map=news_signal_map,
        market_regime=market_regime,
        playbook=playbook,
        market_context_inputs=market_context_inputs,
        news_ctx=news_ctx,
        theme_strength=theme_strength,
    )
    recent_strategy_feedback = _load_recent_strategy_feedback(state, policy)
    reporter_feedback_packet = _load_reporter_feedback_packet(state, policy)
    strategy_memory_advisory = _load_strategy_memory_advisory(state, policy)
    report_focus = _merge_override_text_list(
        report_focus,
        recent_strategy_feedback.get("suggested_report_focus"),
        limit=8,
    )
    reports_root = isolate_canonical_path_for_pytest(str(state.get("reports_root") or os.getenv("REPORTS_ROOT", "reports")).strip() or "reports", canonical_path="reports", isolated_name="reports")
    read_model_facts = _load_deterministic_read_models(state, candidate_symbols)
    read_model_facts_summary = summarize_read_model_facts(read_model_facts)
    
    state["recent_strategy_feedback"] = dict(recent_strategy_feedback)
    state["reporter_feedback_packet"] = dict(reporter_feedback_packet)
    state["strategy_memory"] = dict(strategy_memory_advisory)
    state["read_model_facts_summary"] = dict(read_model_facts_summary)
    fallback_theme_hints, pre_llm_commander_context, selected_themes_hint = strat_ctx_fallback_theme_hints_pre_llm_commander_c(state=state, market_regime=market_regime, playbook=playbook, available_themes=available_themes, themes=themes, facade=_r3_sys.modules[__name__])

    llm_payload, news_event_intelligence, strategist_input_quality = assemble_frame_llm_payload(available_themes=available_themes, candidate_symbols=candidate_symbols, fallback_theme_hints=fallback_theme_hints, global_signal=global_signal, key_events=key_events, macro_stress_overlay=macro_stress_overlay, market_context_inputs=market_context_inputs, market_news_items_by_target=market_news_items_by_target, market_news_signal_map=market_news_signal_map, market_regime=market_regime, market_sentiment=market_sentiment, market_structure=market_structure, news_collection_policy=news_collection_policy, news_ctx=news_ctx, news_items_by_symbol=news_items_by_symbol, news_query_targets=news_query_targets, news_signal_map=news_signal_map, playbook=playbook, pre_llm_commander_context=pre_llm_commander_context, read_model_facts=read_model_facts, recent_strategy_feedback=recent_strategy_feedback, reporter_feedback_packet=reporter_feedback_packet, reports_root=reports_root, selected_themes_hint=selected_themes_hint, strategy_memory_advisory=strategy_memory_advisory, theme_strength=theme_strength, theme_strength_packet=theme_strength_packet, themes=themes, facade=_r3_sys.modules[__name__])
    candidate_news_sample = _sample_news_for_evidence(news_items_by_symbol)
    market_news_sample = _sample_news_for_evidence(market_news_items_by_target)
    try:
        record_raw_input(
            run_id=str(state.get("run_id") or "strategist-unknown"),
            agent="strategist",
            stage="theme_selection",
            raw_input=build_theme_selection_raw_input(available_themes=available_themes, candidate_news_sample=candidate_news_sample, candidate_symbols=candidate_symbols, global_signal=global_signal, llm_payload=llm_payload, market_context_inputs=market_context_inputs, market_news_sample=market_news_sample, market_regime=market_regime, market_sentiment=market_sentiment, market_structure=market_structure, news_collection_policy=news_collection_policy, news_event_intelligence=news_event_intelligence, news_query_reasoning=news_query_reasoning, news_query_targets=news_query_targets, recent_strategy_feedback=recent_strategy_feedback, reporter_feedback_packet=reporter_feedback_packet, strategy_memory_advisory=strategy_memory_advisory, theme_strength_packet=theme_strength_packet, facade=_r3_sys.modules[__name__]),
            decision_link={"stage": "strategist_input_collection"},
        )
    except Exception:
        pass
    llm_overrides, llm_meta = _run_strategist_frame_llm(state=state, policy=policy, payload=llm_payload)
    manual_overrides = _extract_ai_overrides(state, policy)
    ai_overrides = {**dict(llm_overrides or {}), **dict(manual_overrides or {})}
    llm_requested_playbook = _norm_playbook((llm_overrides or {}).get("playbook"))
    requested_playbook = _norm_playbook(ai_overrides.get("playbook"))
    requested_playbook_source = (
        "manual_override"
        if _norm_playbook((manual_overrides or {}).get("playbook"))
        else "llm"
        if llm_requested_playbook
        else "deterministic"
    )
    llm_required = _resolve_strategist_frame_llm_enabled(policy)
    llm_strict = _resolve_strategist_frame_llm_strict_enabled(policy)
    strategist_llm_blocked = bool(llm_required and llm_strict and str(llm_meta.get("status") or "") != "ok")
    strategist_llm_block_reason = ""
    if strategist_llm_blocked:
        strategist_llm_block_reason = (
            "strategist_llm_required"
            if str(llm_meta.get("status") or "") in {"disabled", "dry_run", "unavailable"}
            else "strategist_llm_failed"
        )

    if llm_required:
        llm_payload_log: Dict[str, Any] = {
            "call_kind": "strategic_frame",
            "provider": "openrouter",
            "model": str(llm_meta.get("model") or ""),
            "ok": str(llm_meta.get("status") or "") == "ok",
            "status": str(llm_meta.get("status") or ""),
            "latency_ms": int(llm_meta.get("latency_ms") or 0),
            "attempts": int(llm_meta.get("attempts") or 1),
            "repair_used": bool(llm_meta.get("repair_used")),
            "prompt_version": str(os.getenv("STRATEGIST_FRAME_LLM_PROMPT_VERSION", "m31-strategic-frame-v1") or "m31-strategic-frame-v1"),
            "schema_version": "strategist_output.v1",
            "llm_execution_profile_name": str(llm_meta.get("llm_execution_profile_name") or ""),
            "llm_execution_profile_source": str(llm_meta.get("llm_execution_profile_source") or ""),
            "llm_execution_effective_config": dict(llm_meta.get("llm_execution_effective_config") or {}),
            "themes": list((llm_overrides or {}).get("themes") or [])[:5],
            "avoid_themes": list((llm_overrides or {}).get("avoid_themes") or [])[:5],
            "playbook": str((llm_overrides or {}).get("playbook") or ""),
            "scanner_bias": str((llm_overrides or {}).get("scanner_bias") or ""),
            "risk_tone": str((llm_overrides or {}).get("risk_tone") or ""),
            "monitor_guidance": str((llm_overrides or {}).get("monitor_guidance") or ""),
            "candidate_hint_count": len(list(candidate_symbols)),
        }
        if llm_meta.get("reason"):
            llm_payload_log["error"] = str(llm_meta.get("reason"))
        if llm_meta.get("error_type"):
            llm_payload_log["error_type"] = str(llm_meta.get("error_type"))
        if llm_meta.get("recovery_method"):
            llm_payload_log["recovery_method"] = str(llm_meta.get("recovery_method"))
        if strategist_llm_blocked:
            llm_payload_log["blocked"] = True
            llm_payload_log["blocked_reason"] = strategist_llm_block_reason
        _log_strategist_llm_result(state, llm_payload_log)

    # Optional AI overrides are additive and bounded to keep deterministic fallback.
    avoid_themes, key_events, market_regime, market_regime_summary, market_sentiment, monitor_guidance, playbook, raw_theme_strategy, report_focus, risk_tone, scanner_bias, scanner_priority, selected_themes, themes, trade_aggressiveness = apply_ai_overrides_to_frame(ai_overrides=ai_overrides, available_themes=available_themes, avoid_themes=avoid_themes, global_signal=global_signal, key_events=key_events, market_regime=market_regime, market_sentiment=market_sentiment, market_structure=market_structure, monitor_guidance=monitor_guidance, playbook=playbook, report_focus=report_focus, risk_tone=risk_tone, scanner_bias=scanner_bias, scanner_priority=scanner_priority, themes=themes, trade_aggressiveness=trade_aggressiveness, facade=_r3_sys.modules[__name__])
    exit_policy, monitor_entry_policy, monitor_entry_policy_validation, monitor_policy, policy_confidence, policy_source, scanner_bias_context, scanner_bias_context_validation = strat_policy_exit_policy_monitor_entry_policy(ai_overrides=ai_overrides, monitor_policy=monitor_policy, state=state, policy=policy, monitor_guidance=monitor_guidance, trade_aggressiveness=trade_aggressiveness, risk_tone=risk_tone, playbook=playbook, market_regime=market_regime, scanner_bias=scanner_bias, exit_policy=exit_policy, facade=_r3_sys.modules[__name__])
    monitor_guidance, risk_tone, trade_aggressiveness, exit_policy, report_focus, macro_stress_overlay = _apply_macro_stress_to_monitor_frame(
        global_signal=global_signal,
        monitor_guidance=monitor_guidance,
        risk_tone=risk_tone,
        trade_aggressiveness=trade_aggressiveness,
        exit_policy=exit_policy,
        report_focus=report_focus,
    )
    monitor_policy = _monitor_policy(
        state=state,
        policy=policy,
        monitor_guidance=monitor_guidance,
        trade_aggressiveness=trade_aggressiveness,
        risk_tone=risk_tone,
    )
    scanner_source_policy = _scanner_source_policy(
        playbook=playbook,
        risk_tone=risk_tone,
        trade_aggressiveness=trade_aggressiveness,
        market_regime=market_regime,
        themes=list(themes),
        fear_index=global_signal.get("fear_index") if isinstance(global_signal.get("fear_index"), dict) else {},
    )
    candidate_watch_policy, rejected_strategy_reasons, strategy_scores, tactical_strategy, tactical_subtype = strat_policy_candidate_watch_policy_rejected_strategy(playbook=playbook, ai_overrides=ai_overrides, market_regime=market_regime, market_sentiment=market_sentiment, market_structure=market_structure, market_context_inputs=market_context_inputs, risk_tone=risk_tone, trade_aggressiveness=trade_aggressiveness, facade=_r3_sys.modules[__name__])

    if isinstance(ai_overrides.get("themes"), list) and list(ai_overrides.get("themes") or []):
        # Keep runtime theme/sector maps aligned with the final strategist frame
        # only when AI/manual overrides actually replace themes. Unconditionally
        # syncing broad fallback themes makes scanner sector-theme sourcing too
        # aggressive in deterministic baseline paths.
        state["theme_map"] = _merge_theme_symbol_map(
            state.get("theme_map"),
            themes=list(themes),
            candidate_symbols=list(state.get("candidate_symbols") or []),
            protect_existing_themes=_theme_packet_symbol_map_is_authoritative(theme_strength_packet),
        )
        state["sector_map"] = _merge_theme_symbol_map(
            state.get("sector_map"),
            themes=list(themes),
            candidate_symbols=list(state.get("candidate_symbols") or []),
            protect_existing_themes=_theme_packet_symbol_map_is_authoritative(theme_strength_packet),
        )

    theme_strategy = _build_theme_strategy_surface(
        available_themes=list(available_themes),
        selected_themes=list(selected_themes),
        playbook=playbook,
        theme_strength_packet=dict(theme_strength_packet),
        raw_theme_strategy=raw_theme_strategy,
    )
    state["selected_themes"] = list(selected_themes)
    state["theme_strategy"] = dict(theme_strategy)

    commander_context, policy_adjustment, policy_rationale, strategic_answers, strategist_plan, strategy_adjustment_directives = strat_policy_commander_context_policy_adjustment(state=state, market_regime=market_regime, playbook=playbook, market_sentiment=market_sentiment, key_events=key_events, themes=themes, avoid_themes=avoid_themes, scanner_bias=scanner_bias, scanner_priority=scanner_priority, trade_aggressiveness=trade_aggressiveness, risk_tone=risk_tone, monitor_guidance=monitor_guidance, report_focus=report_focus, recent_strategy_feedback=recent_strategy_feedback, strategy_memory_advisory=strategy_memory_advisory, reports_root=reports_root, read_model_facts=read_model_facts, news_query_reasoning=news_query_reasoning, monitor_policy=monitor_policy, exit_policy=exit_policy, ai_overrides=ai_overrides, monitor_entry_policy_validation=monitor_entry_policy_validation, monitor_entry_policy=monitor_entry_policy, facade=_r3_sys.modules[__name__])
    if bool(policy_adjustment.get("adjustment_required")) and not list(policy_adjustment.get("delta_fields") or []):
        monitor_entry_policy_validation = dict(monitor_entry_policy_validation or {})
        validation_issues = [
            str(x)
            for x in list(monitor_entry_policy_validation.get("issues") or [])
            if str(x or "").strip()
        ]
        if "adjustment_required_but_no_policy_delta" not in validation_issues:
            validation_issues.append("adjustment_required_but_no_policy_delta")
        monitor_entry_policy_validation["issues"] = list(validation_issues)
    policy_provenance = _build_strategy_policy_provenance(commander_context=commander_context)
    strategy_policy = _build_strategy_policy(
        market_regime=market_regime,
        market_sentiment=market_sentiment,
        playbook=playbook,
        trade_aggressiveness=trade_aggressiveness,
        risk_tone=risk_tone,
        monitor_guidance=monitor_guidance,
        global_signal=global_signal,
        market_context_inputs=market_context_inputs,
        themes=list(themes),
        avoid_themes=list(avoid_themes),
        theme_strength=dict(theme_strength),
        scanner_priority=list(scanner_priority),
        scanner_source_policy=dict(scanner_source_policy),
        scanner_bias_context=dict(scanner_bias_context),
        monitor_entry_policy=dict(monitor_entry_policy),
        monitor_policy=dict(monitor_policy),
        exit_policy=dict(exit_policy),
        macro_stress_overlay=dict(macro_stress_overlay),
        news_ctx=dict(news_ctx),
    )
    strategy_policy["commander_context"] = dict(commander_context)
    strategy_policy["strategist_plan"] = dict(strategist_plan)
    strategy_policy["provenance"] = dict(policy_provenance)
    annotate_strategy_policy_market_scanner(candidate_watch_policy=candidate_watch_policy, llm_requested_playbook=llm_requested_playbook, playbook=playbook, pre_llm_playbook=pre_llm_playbook, rejected_strategy_reasons=rejected_strategy_reasons, requested_playbook=requested_playbook, requested_playbook_source=requested_playbook_source, strategy_policy=strategy_policy, strategy_scores=strategy_scores, tactical_strategy=tactical_strategy, tactical_subtype=tactical_subtype)
    commander_context, commander_horizon_policy, horizon_context, strategist_horizon_proposal, strategist_refresh_context, strategy_horizon_feedback = strat_policy_commander_context_commander_horizon_poli(ai_overrides=ai_overrides, playbook=playbook, monitor_guidance=monitor_guidance, trade_aggressiveness=trade_aggressiveness, risk_tone=risk_tone, policy_source=policy_source, commander_context=commander_context, state=state, facade=_r3_sys.modules[__name__])
    attach_horizon_to_commander_context(commander_context=commander_context, commander_horizon_policy=commander_horizon_policy, horizon_context=horizon_context, strategic_answers=strategic_answers, strategist_refresh_context=strategist_refresh_context, strategy_policy=strategy_policy)
    attach_horizon_to_monitor_policy_and_plan(commander_horizon_policy=commander_horizon_policy, strategist_horizon_proposal=strategist_horizon_proposal, strategist_plan=strategist_plan, strategy_horizon_feedback=strategy_horizon_feedback, strategy_policy=strategy_policy)

    state["market_regime"] = market_regime
    state["market_sentiment"] = market_sentiment
    state["market_structure"] = market_structure
    state["market_context_inputs"] = dict(market_context_inputs)
    state["regime_factors"] = dict(regime_factors)
    state["theme_strength"] = dict(theme_strength)
    state["key_events"] = list(key_events)
    state["news_event_intelligence"] = dict(news_event_intelligence)
    state["avoid_themes"] = list(avoid_themes)
    state["playbook"] = playbook
    state["scanner_bias"] = scanner_bias
    state["scanner_bias_context"] = dict(scanner_bias_context)
    state["scanner_priority"] = list(scanner_priority)
    state["trade_aggressiveness"] = trade_aggressiveness
    state["risk_tone"] = risk_tone
    state["monitor_guidance"] = monitor_guidance
    state["macro_stress_overlay"] = dict(macro_stress_overlay)
    state["monitor_entry_policy"] = dict(monitor_entry_policy)
    state["monitor_policy"] = dict(monitor_policy)
    state["strategist_exit_policy"] = dict(exit_policy)
    state["strategy_policy"] = dict(strategy_policy)
    state["strategist_plan"] = dict(strategist_plan)
    state["commander_horizon_policy"] = dict(commander_horizon_policy)
    state["report_focus"] = list(report_focus)
    state["scanner_guidance"] = strat_output_value_state_scanner_guidance(playbook=playbook, scanner_bias=scanner_bias, trade_aggressiveness=trade_aggressiveness, risk_tone=risk_tone, themes=themes, selected_themes=selected_themes, avoid_themes=avoid_themes, scanner_bias_context=scanner_bias_context, scanner_priority=scanner_priority, scanner_source_policy=scanner_source_policy, theme_strength_packet=theme_strength_packet, available_themes=available_themes, theme_strategy=theme_strategy, facade=_r3_sys.modules[__name__])
    strategist_feedback = _compact_recent_strategy_feedback_for_llm(recent_strategy_feedback)
    compact_reporter_feedback = _compact_reporter_feedback_for_llm(reporter_feedback_packet)
    performance_summary, strategist_output = strat_output_performance_summary_strategist_output(recent_strategy_feedback=recent_strategy_feedback, strategist_feedback=strategist_feedback, market_regime=market_regime, market_sentiment=market_sentiment, playbook=playbook, trade_aggressiveness=trade_aggressiveness, key_events=key_events, themes=themes, avoid_themes=avoid_themes, scanner_bias=scanner_bias, scanner_bias_context=scanner_bias_context, scanner_priority=scanner_priority, scanner_source_policy=scanner_source_policy, risk_tone=risk_tone, monitor_guidance=monitor_guidance, strategy_policy=strategy_policy, report_focus=report_focus, strategic_answers=strategic_answers, state=state, facade=_r3_sys.modules[__name__])
    fill_strategist_output_core(ai_overrides=ai_overrides, available_themes=available_themes, candidate_news_ctx=candidate_news_ctx, candidate_watch_policy=candidate_watch_policy, commander_horizon_policy=commander_horizon_policy, compact_reporter_feedback=compact_reporter_feedback, exit_policy=exit_policy, global_signal=global_signal, horizon_context=horizon_context, llm_requested_playbook=llm_requested_playbook, macro_stress_overlay=macro_stress_overlay, market_context_inputs=market_context_inputs, market_news_ctx=market_news_ctx, market_regime_summary=market_regime_summary, market_structure=market_structure, monitor_entry_policy=monitor_entry_policy, monitor_policy=monitor_policy, news_collection_policy=news_collection_policy, news_ctx=news_ctx, news_event_intelligence=news_event_intelligence, news_query_reasoning=news_query_reasoning, news_query_targets=news_query_targets, performance_summary=performance_summary, playbook=playbook, policy_adjustment=policy_adjustment, policy_provenance=policy_provenance, policy_rationale=policy_rationale, pre_llm_market_regime=pre_llm_market_regime, pre_llm_market_sentiment=pre_llm_market_sentiment, pre_llm_market_structure=pre_llm_market_structure, pre_llm_monitor_guidance=pre_llm_monitor_guidance, pre_llm_playbook=pre_llm_playbook, pre_llm_risk_tone=pre_llm_risk_tone, pre_llm_trade_aggressiveness=pre_llm_trade_aggressiveness, recent_strategy_feedback=recent_strategy_feedback, regime_score=regime_score, rejected_strategy_reasons=rejected_strategy_reasons, reporter_feedback_packet=reporter_feedback_packet, requested_playbook=requested_playbook, requested_playbook_source=requested_playbook_source, scanner_bias_context=scanner_bias_context, scanner_bias_context_validation=scanner_bias_context_validation, selected_themes=selected_themes, sentiment_score=sentiment_score, strategist_feedback=strategist_feedback, strategist_horizon_proposal=strategist_horizon_proposal, strategist_input_quality=strategist_input_quality, strategist_output=strategist_output, strategist_plan=strategist_plan, strategy_adjustment_directives=strategy_adjustment_directives, strategy_horizon_feedback=strategy_horizon_feedback, strategy_memory_advisory=strategy_memory_advisory, strategy_scores=strategy_scores, tactical_strategy=tactical_strategy, tactical_subtype=tactical_subtype, theme_hints=theme_hints, theme_strategy=theme_strategy, theme_strength=theme_strength, theme_strength_packet=theme_strength_packet, themes=themes, facade=_r3_sys.modules[__name__])
    fill_strategist_output_stage_reviews(ai_overrides=ai_overrides, strategist_output=strategist_output)
    fill_strategist_output_policy_and_commander(commander_context=commander_context, commander_horizon_policy=commander_horizon_policy, horizon_context=horizon_context, llm_meta=llm_meta, llm_overrides=llm_overrides, llm_required=llm_required, llm_strict=llm_strict, monitor_entry_policy_validation=monitor_entry_policy_validation, policy_confidence=policy_confidence, policy_source=policy_source, read_model_facts_summary=read_model_facts_summary, state=state, strategic_answers=strategic_answers, strategist_llm_block_reason=strategist_llm_block_reason, strategist_llm_blocked=strategist_llm_blocked, strategist_output=strategist_output)
    fill_strategist_output_explanations(ai_overrides=ai_overrides, state=state, strategist_output=strategist_output, facade=_r3_sys.modules[__name__])
    state["strategist_output"] = strategist_output
    state["strategist_blocked"] = bool(strategist_llm_blocked)
    state["strategist_blocked_reason"] = str(strategist_llm_block_reason or "")
    state["strategist_llm"] = strat_output_value_state_strategist_llm(llm_overrides=llm_overrides, strategist_llm_blocked=strategist_llm_blocked, strategist_llm_block_reason=strategist_llm_block_reason, llm_meta=llm_meta, state=state, facade=_r3_sys.modules[__name__])
    strategist_policy_resolution = build_strategist_policy_resolution_surface(
        strategist_output=strategist_output,
        strategist_llm=state.get("strategist_llm"),
        commander_context=commander_context,
    )
    strategist_output["policy_resolution"] = dict(strategist_policy_resolution)
    state["strategist_output"] = strategist_output
    state["strategist_policy_resolution"] = dict(strategist_policy_resolution)
    ranked_candidate_news, ranked_market_news, reason_chain = strat_trace_ranked_candidate_news_ranked_market_news(market_news_items_by_target=market_news_items_by_target, market_news_signal_map=market_news_signal_map, news_query_targets=news_query_targets, news_items_by_symbol=news_items_by_symbol, news_signal_map=news_signal_map, state=state, market_regime=market_regime, playbook=playbook, themes=themes, avoid_themes=avoid_themes, monitor_guidance=monitor_guidance, news_query_reasoning=news_query_reasoning, macro_stress_overlay=macro_stress_overlay, facade=_r3_sys.modules[__name__])

    _emit_strategist_event(
        state,
        name="market_context_snapshot",
        payload=build_market_context_snapshot_payload(global_signal=global_signal, macro_stress_overlay=macro_stress_overlay, market_context_inputs=market_context_inputs, market_structure=market_structure, regime_factors=regime_factors, state=state, facade=_r3_sys.modules[__name__]),
    )
    global_sentiment_breakdown_payload = _global_sentiment_breakdown_payload(global_signal)
    state["strategist_global_sentiment_breakdown"] = dict(global_sentiment_breakdown_payload)
    _emit_strategist_event(
        state,
        name="global_sentiment_breakdown",
        payload=global_sentiment_breakdown_payload,
    )
    news_evidence_ranked_payload = build_news_evidence_ranked_payload(candidate_news_ctx=candidate_news_ctx, market_news_ctx=market_news_ctx, news_ctx=news_ctx, news_query_targets=news_query_targets, ranked_candidate_news=ranked_candidate_news, ranked_market_news=ranked_market_news)
    state["strategist_news_evidence_ranked"] = dict(news_evidence_ranked_payload)
    state["strategist_candidate_symbols_hint"] = list(state.get("candidate_symbols") or [])[:10]
    strategist_output["feedback_application_trace"] = build_feedback_application_trace(
        feedback_packet=reporter_feedback_packet,
        strategist_output=strategist_output,
    )
    strategist_explanation_fields = build_strategist_explanation_fields(
        strategist_output=strategist_output,
        state=state,
        news_evidence_ranked=news_evidence_ranked_payload,
    )
    strategist_output.update(strategist_explanation_fields)
    if isinstance(llm_meta.get("quant_context"), dict) and llm_meta.get("quant_context"):
        strategist_output["quant_context"] = dict(llm_meta.get("quant_context") or {})
        strategist_output["strategy_refresh_trace"] = _attach_quant_context_to_strategy_refresh_trace(
            strategist_output.get("strategy_refresh_trace"),
            llm_meta.get("quant_context"),
        )
    state["strategist_output"] = strategist_output
    _emit_strategist_event(
        state,
        name="news_evidence_ranked",
        payload=news_evidence_ranked_payload,
    )
    decision_frame_payload = strat_trace_decision_frame_payload(market_regime=market_regime, market_sentiment=market_sentiment, playbook=playbook, scanner_bias=scanner_bias, trade_aggressiveness=trade_aggressiveness, risk_tone=risk_tone, monitor_guidance=monitor_guidance, reason_chain=reason_chain, themes=themes, avoid_themes=avoid_themes, scanner_priority=scanner_priority, scanner_source_policy=scanner_source_policy, report_focus=report_focus, commander_horizon_policy=commander_horizon_policy, horizon_context=horizon_context, reporter_feedback_packet=reporter_feedback_packet, strategist_output=strategist_output, strategy_memory_advisory=strategy_memory_advisory, strategy_policy=strategy_policy, theme_strength_packet=theme_strength_packet, facade=_r3_sys.modules[__name__])[0]
    state["strategist_decision_frame"] = dict(decision_frame_payload)
    _emit_strategist_event(
        state,
        name="decision_frame",
        payload=decision_frame_payload,
    )
    if llm_required:
        _emit_strategist_event(
            state,
            name="llm_response_saved",
            payload={
                "status": str(llm_meta.get("status") or "disabled"),
                "model": str(llm_meta.get("model") or ""),
                "attempts": int(llm_meta.get("attempts") or 1),
                "repair_used": bool(llm_meta.get("repair_used")),
                "blocked": bool(strategist_llm_blocked),
                "blocked_reason": str(strategist_llm_block_reason or ""),
                "llm_response_artifact": {
                    "component": "strategist",
                    "evidence_log_path": str(Path(os.getenv("EVIDENCE_LEDGER_PATH", "data/evidence_ledger/events.jsonl"))),
                    "prompt_stage": "theme_selection",
                    "response_stage": "theme_selection_repair" if bool(llm_meta.get("repair_used")) else "theme_selection",
                    "prompt_ref": str(llm_meta.get("prompt_ref") or ""),
                    "response_ref": str(llm_meta.get("response_ref") or ""),
                    "prompt_hash": str(llm_meta.get("prompt_hash") or ""),
                    "response_hash": str(llm_meta.get("response_hash") or ""),
                },
            },
            level="warning" if strategist_llm_blocked else "info",
        )
    _emit_strategist_event(
        state,
        name="policy_resolution",
        payload=dict(strategist_policy_resolution),
        level="warning" if bool(strategist_policy_resolution.get("fallback_used")) else "info",
    )
    _log_strategist_summary(
        state,
        build_strategist_summary_log_payload(avoid_themes=avoid_themes, llm_meta=llm_meta, llm_overrides=llm_overrides, macro_stress_overlay=macro_stress_overlay, market_regime=market_regime, market_sentiment=market_sentiment, monitor_guidance=monitor_guidance, news_query_reasoning=news_query_reasoning, news_query_targets=news_query_targets, playbook=playbook, recent_strategy_feedback=recent_strategy_feedback, regime_score=regime_score, report_focus=report_focus, reporter_feedback_packet=reporter_feedback_packet, risk_tone=risk_tone, scanner_bias=scanner_bias, scanner_priority=scanner_priority, scanner_source_policy=scanner_source_policy, sentiment_score=sentiment_score, state=state, strategist_llm_block_reason=strategist_llm_block_reason, strategist_llm_blocked=strategist_llm_blocked, strategist_output=strategist_output, strategist_policy_resolution=strategist_policy_resolution, strategy_memory_advisory=strategy_memory_advisory, themes=themes, trade_aggressiveness=trade_aggressiveness),
    )
    append_decision_trace(
        state,
        agent="strategist",
        event="strategic_frame",
        payload=build_strategic_frame_trace_payload(avoid_themes=avoid_themes, key_events=key_events, llm_meta=llm_meta, llm_overrides=llm_overrides, macro_stress_overlay=macro_stress_overlay, market_regime=market_regime, market_sentiment=market_sentiment, monitor_guidance=monitor_guidance, news_query_reasoning=news_query_reasoning, news_query_targets=news_query_targets, playbook=playbook, recent_strategy_feedback=recent_strategy_feedback, regime_score=regime_score, report_focus=report_focus, reporter_feedback_packet=reporter_feedback_packet, risk_tone=risk_tone, scanner_bias=scanner_bias, scanner_priority=scanner_priority, scanner_source_policy=scanner_source_policy, sentiment_score=sentiment_score, strategist_output=strategist_output, strategy_memory_advisory=strategy_memory_advisory, themes=themes, trade_aggressiveness=trade_aggressiveness),
    )
    try:
        record_decision_bridge(
            run_id=str(state.get("run_id") or "strategist-unknown"),
            agent="strategist",
            stage="decision_bridge",
            parsed_output=build_strategist_decision_bridge_output(avoid_themes=avoid_themes, macro_stress_overlay=macro_stress_overlay, market_regime=market_regime, market_sentiment=market_sentiment, monitor_guidance=monitor_guidance, news_query_reasoning=news_query_reasoning, news_query_targets=news_query_targets, playbook=playbook, recent_strategy_feedback=recent_strategy_feedback, report_focus=report_focus, reporter_feedback_packet=reporter_feedback_packet, risk_tone=risk_tone, scanner_bias=scanner_bias, scanner_priority=scanner_priority, scanner_source_policy=scanner_source_policy, state=state, strategist_output=strategist_output, strategy_memory_advisory=strategy_memory_advisory, themes=themes, trade_aggressiveness=trade_aggressiveness),
            decision_link={
                "decision_chain": {
                    "theme": (list(themes)[0] if list(themes) else ""),
                    "candidate_symbols": list(state.get("candidate_symbols") or []),
                }
            },
        )
    except Exception:
        pass
    try:
        write_strategist_artifact(state)
    except Exception:
        pass
    return state
