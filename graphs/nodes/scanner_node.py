from __future__ import annotations

"""Canonical Scanner node for integrated runtime.

Role boundary:
- builds/reduces/ranks candidate pool (Kiwoom-first, strategist-guided)
- selects final Top-1 candidate for monitor stage within strategist frame
- does not create execution calls
"""

import os
import time
from collections import Counter
from functools import partial
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

from graphs.nodes.skill_contracts import (
    CONTRACT_VERSION as SKILL_CONTRACT_VERSION,
    account_order_is_pending,
    extract_account_orders_rows,
    extract_market_quotes,
    extract_minute_ohlcv_by_symbol,
    norm_symbol,
)
from libs.research.evidence_ledger import record_decision_bridge, record_raw_input
from libs.core.path_isolation import isolate_canonical_path_for_pytest
from libs.runtime.asset_universe_policy import apply_asset_universe_filter
from libs.runtime.canonical_artifacts import write_scanner_artifact
from libs.runtime.commander_memory_application_trace import build_scanner_commander_memory_application_trace
from libs.runtime.decision_trace import append_decision_trace
from libs.runtime.etf_deviation import extract_etf_deviation_signal
from libs.runtime.scanner_bias import normalize_scanner_bias_context, summarize_scanner_bias_context
from libs.runtime.scanner_memory_bias import (
    compute_scanner_memory_bias_adjustment,
    summarize_scanner_memory_bias,
)
from libs.runtime.scanner.candidate_selection import (
    build_kiwoom_candidates as _build_kiwoom_candidates_base,
    extract_strategist_candidates as _extract_strategist_candidates,
    normalize_scanner_source_policy as _normalize_scanner_source_policy,
    resolve_block_static_fallback as _resolve_block_static_fallback,
    resolve_candidate_limit as _resolve_candidate_limit,
    resolve_candidate_source as _resolve_candidate_source,
    resolve_condition_limit as _resolve_condition_limit,
    resolve_enable_theme_filter as _resolve_enable_theme_filter,
    resolve_include_change_rate as _resolve_include_change_rate,
    resolve_scan_aggressiveness as _resolve_scan_aggressiveness,
    resolve_scanner_candidates as _resolve_scanner_candidates_base,
    resolve_strict_kiwoom_only as _resolve_strict_kiwoom_only,
    resolve_top_candidate_pool as _resolve_top_candidate_pool,
)
from libs.runtime.scanner.theme_filter import (
    apply_avoid_theme_filter as _apply_avoid_theme_filter,
    apply_theme_filter as _apply_theme_filter,
    candidate_theme_match as _candidate_theme_match,
    extract_avoid_themes as _extract_avoid_themes,
    extract_selected_themes as _extract_selected_themes,
    extract_theme_symbol_index as _extract_theme_symbol_index,
    extract_themes as _extract_themes,
)
from libs.runtime.scanner.market_representative_guard import (
    apply_market_representative_guard as _apply_market_representative_guard,
    default_market_representative_guard_policy as _default_market_representative_guard_policy,
    market_representative_confirmation_sources as _market_representative_confirmation_sources,
    market_representative_top_value_dominance as _market_representative_top_value_dominance,
    resolve_market_representative_guard_policy as _resolve_market_representative_guard_policy,
)
from libs.runtime.scanner.practical_filters import (
    candidate_quote_metrics as _candidate_quote_metrics,
    filter_mock_broker_restricted_candidates as _filter_mock_broker_restricted_candidates,
    reduce_candidates_by_practical_filters as _reduce_candidates_by_practical_filters,
    resolve_exclude_halted as _resolve_exclude_halted,
    resolve_min_trading_value as _resolve_min_trading_value,
    resolve_min_volume as _resolve_min_volume,
)
from libs.runtime.scanner.candidate_risk import resolve_candidate_base_risk
from libs.runtime.scanner.output_snapshots import (
    compact_feature_snapshot as _compact_feature_snapshot,
    compact_selected_snapshot as _compact_selected_snapshot,
    feature_coverage_summary as _feature_coverage_summary,
    ranking_table_rows as _ranking_table_rows,
)
from libs.runtime.scanner.output_payloads import (
    build_candidate_ranking_table_payload as _build_candidate_ranking_table_payload,
    build_candidate_selection_reason_payload as _build_candidate_selection_reason_payload,
)
from libs.runtime.scanner.control_eligibility import build_full_strategist_control_eligibility
from libs.runtime.quant.suitability import score_candidate_tactic_suitability
from libs.runtime.intraday_monitor_signals import evaluate_intraday_entry_signal, resolve_intraday_entry_policy
from libs.runtime.feature_engine import build_feature_map
from libs.runtime.scanner_feature_hydration import hydrate_scanner_feature_map
from libs.runtime.scanner_policy import resolve_scanner_runtime_policy
from libs.strategies.contracts import coerce_strategist_output
from libs.reporting.symbol_read_model import build_symbol_read_model
import sys as _r3_sys
from libs.runtime.scanner.scoring_inputs import (
    _memory_bias_observation_only_r3_impl,
    _enforce_live_equity_symbols_r3_impl,
    _filter_live_equity_candidates_r3_impl,
    _get_scanner_weights_r3_impl,
    _stable_unit_hash_r3_impl,
    _resolve_scanner_score_weights_r3_impl,
    _normalize_priority_list_r3_impl,
    _resolve_compatibility_bias_context_r3_impl,
)
from libs.runtime.scanner.repeat_guard import (
    _resolve_scanner_repeat_guard_policy_r3_impl,
    _scanner_recent_selection_history_r3_impl,
    _scanner_recent_block_history_r3_impl,
    _repeat_symbol_penalty_r3_impl,
    _repeat_blocker_cooldown_penalty_r3_impl,
    _normalize_scanner_blocker_family_r3_impl,
    _candidate_blocker_families_r3_impl,
)
from libs.runtime.scanner.blocker_family_overlay import (
    _apply_blocker_family_concentration_overlay_r3_impl,
)
from libs.runtime.scanner.symbol_prior import (
    _compute_symbol_prior_adjustment_r3_impl,
)
from libs.runtime.scanner.evidence import (
    _extract_account_open_order_counts_r3_impl,
    _should_auto_hydrate_scanner_skills_r3_impl,
    _extract_feature_engine_map_r3_impl,
    _build_scanner_policy_trace_r3_impl,
)
from libs.runtime.scanner.feature_coverage import (
    _summarize_quote_metric_coverage_r3_impl,
    _should_refresh_scanner_features_r3_impl,
)
from libs.runtime.scanner.sentiment_inputs import (
    _get_global_sentiment_score_r3_impl,
    _get_news_sentiment_map_r3_impl,
    _get_global_sentiment_signal_r3_impl,
    _get_news_sentiment_signal_map_r3_impl,
)
from libs.runtime.scanner.guidance import (
    _extract_scanner_guidance_r3_impl,
    _apply_scanner_guidance_weights_r3_impl,
    _compute_structured_scanner_bias_r3_impl,
)
from libs.runtime.scanner.macro_focus import (
    _scanner_macro_focus_r3_impl,
)
from libs.runtime.scanner.compatibility import (
    _build_scanner_monitor_policy_input_r3_impl,
    _build_scanner_monitor_frame_r3_impl,
    _compute_entry_compatibility_signal_r3_impl,
    _extract_monitor_entry_block_reason_r3_impl,
    _merge_mock_compatibility_override_r3_impl,
)
from libs.runtime.scanner.macro_chart_fit import (
    _calc_reclaim_proximity_r3_impl,
    _calc_breakout_proximity_r3_impl,
    _scanner_chart_fit_from_entry_result_r3_impl,
    _compute_scanner_macro_chart_fit_r3_impl,
)
from libs.runtime.scanner.candidate_context_projection import (
    scan_context_candidates_policy,
    scan_context_commander_context_intrinsic_control_w,
)
from libs.runtime.scanner.score_feature_projection import (
    scan_feature_candidate_rank_score_candidate_universe,
    scan_feature_adx14_adx_component,
    scan_feature_avoid_theme_penalty_bias_result,
)
from libs.runtime.scanner.score_policy_projection import (
    scan_score_adj_risk_compatibility_bias,
    scan_score_adj_conf_adj_risk,
)
from libs.runtime.scanner.selection_evidence_projection import (
    scan_select_value_state_scanner_output,
    scan_select_value_state_scanner_skill,
    scan_select_commander_memory_application_trace_selec,
    scan_select_reasons_row_conf,
)
from libs.runtime.scanner.selection_evidence_projection_value_te_scanner import (
    scan_select_value_te_scanner_selection_reason,
    scan_select_candidate_selection_reason_payload,
)


def _clamp(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x


def _norm_symbol(v: Any) -> str:
    return norm_symbol(v)


def _to_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return float(default)


def _is_trueish(v: Any) -> bool:
    return str(v or "").strip().lower() in ("1", "true", "yes", "y", "on")


def _memory_bias_observation_only(state: Dict[str, Any] | None = None) -> bool:
    return _memory_bias_observation_only_r3_impl(state, facade=_r3_sys.modules[__name__])


def _to_int(v: Any, default: int) -> int:
    try:
        return int(float(v))
    except Exception:
        return int(default)


def _resolve_scanner_repeat_guard_policy(policy: Dict[str, Any]) -> Dict[str, Any]:
    return _resolve_scanner_repeat_guard_policy_r3_impl(policy, facade=_r3_sys.modules[__name__])


def _resolve_reports_root(state: Dict[str, Any]) -> Path:
    raw = str(state.get("reports_root") or os.getenv("REPORTS_ROOT", "reports")).strip() or "reports"
    return isolate_canonical_path_for_pytest(raw, canonical_path="reports", isolated_name="reports")


def _load_symbol_priors(state: Dict[str, Any], candidates: List[Any]) -> Dict[str, Dict[str, Any]]:
    reports_root = _resolve_reports_root(state)
    trades_root = reports_root / "trades"
    out: Dict[str, Dict[str, Any]] = {}
    if not trades_root.exists():
        return out
    for item in list(candidates or [])[:40]:
        symbol = _norm_symbol(item.get("symbol")) if isinstance(item, dict) else _norm_symbol(item)
        if not symbol or symbol in out:
            continue
        try:
            model = build_symbol_read_model(str(trades_root), symbol, persisted_only=True)
        except Exception:
            model = {}
        if isinstance(model, dict) and model:
            out[symbol] = model
    return out


def _compute_symbol_prior_adjustment(
    *,
    symbol_model: Dict[str, Any],
    playbook: str,
    current_day: str = "",
) -> Dict[str, Any]:
    return _compute_symbol_prior_adjustment_r3_impl(symbol_model=symbol_model, playbook=playbook,
        current_day=current_day, facade=_r3_sys.modules[__name__])


def _scanner_recent_selection_history(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    return _scanner_recent_selection_history_r3_impl(state, facade=_r3_sys.modules[__name__])


def _scanner_recent_block_history(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    return _scanner_recent_block_history_r3_impl(state, facade=_r3_sys.modules[__name__])


def _resolve_now_epoch(state: Dict[str, Any]) -> int:
    for key in ("now_epoch", "ts_epoch", "epoch"):
        value = _to_int(state.get(key), 0)
        if value > 0:
            return value
    return int(time.time())


def _repeat_symbol_penalty(
    state: Dict[str, Any],
    *,
    symbol: str,
    policy: Dict[str, Any],
) -> Dict[str, Any]:
    return _repeat_symbol_penalty_r3_impl(state, symbol=symbol, policy=policy,
        facade=_r3_sys.modules[__name__])


def _repeat_blocker_cooldown_penalty(
    state: Dict[str, Any],
    *,
    symbol: str,
    policy: Dict[str, Any],
) -> Dict[str, Any]:
    return _repeat_blocker_cooldown_penalty_r3_impl(state, symbol=symbol, policy=policy,
        facade=_r3_sys.modules[__name__])


def _remember_selected_symbol(state: Dict[str, Any], selected_symbol: str, *, now_epoch: int, policy: Dict[str, Any]) -> None:
    symbol = _norm_symbol(selected_symbol)
    if not symbol:
        return
    persisted = state.get("persisted_state") if isinstance(state.get("persisted_state"), dict) else {}
    state["persisted_state"] = persisted
    cfg = _resolve_scanner_repeat_guard_policy(policy)
    history = _scanner_recent_selection_history(state)
    history.append({"symbol": symbol, "epoch": int(now_epoch)})
    if cfg["lookback_sec"] > 0:
        cutoff = max(0, int(now_epoch) - int(cfg["lookback_sec"]) * 2)
        history = [row for row in history if _to_int(row.get("epoch"), 0) >= cutoff]
    if len(history) > cfg["history_limit"]:
        history = history[-cfg["history_limit"] :]
    persisted["recent_scanner_selected"] = history


def _make_event_logger(state: Dict[str, Any]) -> Any:
    injected = state.get("event_logger")
    if injected is not None and hasattr(injected, "log"):
        return injected
    from libs.core.event_logger import EventLogger, resolve_event_log_path

    return EventLogger(log_path=resolve_event_log_path())


def _emit_scanner_event(
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
            stage="scanner",
            event=name,
            event_name=f"scanner.{name}",
            payload=dict(payload or {}),
            level=level,
            agent="scanner",
            symbol=str(symbol or ""),
        )
    except Exception:
        return


def _candidate_visibility_limit(policy: Dict[str, Any]) -> int:
    entry_control = policy.get("entry_control") if isinstance(policy.get("entry_control"), dict) else {}
    raw = entry_control.get("max_priority_rank") or policy.get("max_priority_rank") or 10
    value = int(_to_float(raw) or 10)
    return int(min(10, max(1, value)))


def _log_scanner_summary(state: Dict[str, Any], payload: Dict[str, Any]) -> None:
    try:
        logger = _make_event_logger(state)
        run_id = str(state.get("run_id") or "scanner-node")
        logger.log(run_id=run_id, stage="scanner", event="summary", payload=dict(payload))
    except Exception:
        return


def _extract_skill_quotes(state: Dict[str, Any]) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Any]]:
    return extract_market_quotes(state)


def _extract_account_open_order_counts(state: Dict[str, Any]) -> Tuple[Dict[str, int], int, Dict[str, Any]]:
    return _extract_account_open_order_counts_r3_impl(state, facade=_r3_sys.modules[__name__])


def _is_live_equity_symbol(symbol: str) -> bool:
    sym = _norm_symbol(symbol)
    return bool(sym) and sym.isdigit() and len(sym) == 6


def _enforce_live_equity_symbols(state: Dict[str, Any], policy: Dict[str, Any]) -> bool:
    return _enforce_live_equity_symbols_r3_impl(state, policy, facade=_r3_sys.modules[__name__])


def _filter_live_equity_candidates(candidates: List[Any]) -> Tuple[List[Any], Dict[str, Any]]:
    return _filter_live_equity_candidates_r3_impl(candidates, facade=_r3_sys.modules[__name__])


def _should_auto_hydrate_scanner_skills(state: Dict[str, Any], candidates: List[Any]) -> bool:
    return _should_auto_hydrate_scanner_skills_r3_impl(state, candidates,
        facade=_r3_sys.modules[__name__])


def _maybe_hydrate_scanner_skill_results(state: Dict[str, Any], candidates: List[Any]) -> Dict[str, Any]:
    existing_quotes, _quote_meta = _extract_skill_quotes(state)
    existing_order_counts, existing_order_rows, _order_meta = _extract_account_open_order_counts(state)
    if existing_quotes or existing_order_counts or existing_order_rows > 0:
        return state
    if not _should_auto_hydrate_scanner_skills(state, candidates):
        return state

    try:
        from graphs.nodes.hydrate_skill_results_node import hydrate_skill_results_node
    except Exception:
        return state

    injected_auto = False
    previous_auto = state.get("auto_skill_runner")
    had_candidates_key = "candidates" in state
    previous_candidates = state.get("candidates")
    if (
        state.get("skill_runner") is None
        and not callable(state.get("skill_runner_factory"))
        and not _is_trueish(state.get("auto_skill_runner"))
    ):
        state["auto_skill_runner"] = True
        injected_auto = True
    # The hydration node resolves market.quote fan-out from `state["candidates"]`.
    # Scanner often works from a locally built Kiwoom candidate pool, so expose that
    # pool during hydration instead of silently hydrating an empty symbol list.
    state["candidates"] = list(candidates or [])
    try:
        return hydrate_skill_results_node(state)
    except Exception:
        return state
    finally:
        if had_candidates_key:
            state["candidates"] = previous_candidates
        else:
            state.pop("candidates", None)
        if injected_auto:
            if previous_auto is None:
                state.pop("auto_skill_runner", None)
            else:
                state["auto_skill_runner"] = previous_auto


def _get_global_sentiment_score(state: Dict[str, Any]) -> float:
    """Return global sentiment score in [-1, +1].

    Priority:
      1) state['global_sentiment_signal']['score'] (normalized signal)
      2) state['mock_global_sentiment'] (tests)
      3) state['global_sentiment']['score'] (precomputed)
      4) state['policy']['global_sentiment']['score'] (set by strategist)
      5) default 0.0
    """
    return _get_global_sentiment_score_r3_impl(state, facade=_r3_sys.modules[__name__])


def _get_news_sentiment_map(state: Dict[str, Any]) -> Dict[str, float]:
    """Return per-symbol news sentiment map in [-1, +1].

    Priority:
      1) state['news_sentiment_signal'][symbol]['score']
      2) state['news_sentiment'][symbol]
      3) state['mock_news_sentiment'][symbol]
    """
    return _get_news_sentiment_map_r3_impl(state, facade=_r3_sys.modules[__name__])


def _get_global_sentiment_signal(state: Dict[str, Any]) -> Dict[str, Any]:
    return _get_global_sentiment_signal_r3_impl(state, facade=_r3_sys.modules[__name__])


def _get_news_sentiment_signal_map(state: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return _get_news_sentiment_signal_map_r3_impl(state, facade=_r3_sys.modules[__name__])


def _get_scanner_weights(policy: Any) -> Dict[str, float]:
    """Scanner weighting policy for M18-4.

    Defaults are conservative (small influence), and should not change behavior
    when sentiments are missing (both default to 0.0).
    """
    return _get_scanner_weights_r3_impl(policy, facade=_r3_sys.modules[__name__])


def _stable_unit_hash(text: str) -> float:
    """Return a deterministic pseudo-random float in [0, 1).

    We avoid Python's built-in hash() because it is salted per-process.
    """
    return _stable_unit_hash_r3_impl(text, facade=_r3_sys.modules[__name__])


def _extract_feature_engine_map(state: Dict[str, Any]) -> Tuple[Dict[str, Dict[str, Any]], str, List[str]]:
    return _extract_feature_engine_map_r3_impl(state, facade=_r3_sys.modules[__name__])


def _normalize_scanner_blocker_family(value: Any) -> str:
    return _normalize_scanner_blocker_family_r3_impl(value, facade=_r3_sys.modules[__name__])


def _candidate_blocker_families(row: Mapping[str, Any]) -> List[str]:
    return _candidate_blocker_families_r3_impl(row, facade=_r3_sys.modules[__name__])


def _resolve_scanner_score_weights(policy: Dict[str, Any]) -> Dict[str, float]:
    return _resolve_scanner_score_weights_r3_impl(policy, facade=_r3_sys.modules[__name__])


def _extract_scanner_guidance(state: Dict[str, Any]) -> Dict[str, Any]:
    return _extract_scanner_guidance_r3_impl(state, facade=_r3_sys.modules[__name__])


_build_kiwoom_candidates = partial(
    _build_kiwoom_candidates_base,
    scanner_guidance_resolver=_extract_scanner_guidance,
)
_resolve_scanner_candidates = partial(
    _resolve_scanner_candidates_base,
    scanner_guidance_resolver=_extract_scanner_guidance,
)

def _build_scanner_policy_trace(
    *,
    commander_context: Dict[str, Any],
    strategist_plan: Dict[str, Any],
    policy_provenance: Dict[str, Any],
    playbook: str,
    scanner_priority: List[str],
    scanner_bias: str,
    scanner_bias_context: Dict[str, Any],
    scanner_memory_bias: Dict[str, Any],
) -> Dict[str, Any]:
    return _build_scanner_policy_trace_r3_impl(commander_context=commander_context,
        strategist_plan=strategist_plan, policy_provenance=policy_provenance, playbook=playbook,
        scanner_priority=scanner_priority, scanner_bias=scanner_bias,
        scanner_bias_context=scanner_bias_context, scanner_memory_bias=scanner_memory_bias,
        facade=_r3_sys.modules[__name__])


def _normalize_priority_list(values: Any) -> List[str]:
    return _normalize_priority_list_r3_impl(values, facade=_r3_sys.modules[__name__])


def _apply_scanner_guidance_weights(
    weights: Dict[str, float],
    *,
    playbook: str,
    scanner_bias: str,
    scanner_priority: List[str],
    trade_aggressiveness: str,
    risk_tone: str,
) -> Dict[str, float]:
    return _apply_scanner_guidance_weights_r3_impl(weights, playbook=playbook,
        scanner_bias=scanner_bias, scanner_priority=scanner_priority,
        trade_aggressiveness=trade_aggressiveness, risk_tone=risk_tone,
        facade=_r3_sys.modules[__name__])


def _scanner_bias_total_cap(bias_strength: str) -> float:
    return 0.04 if str(bias_strength or "").strip().lower() == "medium" else 0.02


def _compute_structured_scanner_bias(
    *,
    symbol: str,
    feature_row: Dict[str, Any],
    metrics: Dict[str, Any],
    bias_context: Dict[str, Any],
) -> Dict[str, Any]:
    return _compute_structured_scanner_bias_r3_impl(symbol=symbol, feature_row=feature_row,
        metrics=metrics, bias_context=bias_context, facade=_r3_sys.modules[__name__])


def _summarize_quote_metric_coverage(
    candidates: List[Any],
    *,
    skill_quotes: Dict[str, Dict[str, Any]],
    state: Dict[str, Any],
) -> Dict[str, Any]:
    return _summarize_quote_metric_coverage_r3_impl(candidates, skill_quotes=skill_quotes,
        state=state, facade=_r3_sys.modules[__name__])


def _should_refresh_scanner_features(
    *,
    state: Dict[str, Any],
    candidates: List[Any],
    quote_metric_coverage: Dict[str, Any],
) -> Tuple[bool, str]:
    return _should_refresh_scanner_features_r3_impl(state=state, candidates=candidates,
        quote_metric_coverage=quote_metric_coverage, facade=_r3_sys.modules[__name__])


def _build_scanner_monitor_policy_input(
    *,
    state: Dict[str, Any],
    commander_context: Dict[str, Any],
    monitor_policy: Dict[str, Any],
) -> Dict[str, Any]:
    return _build_scanner_monitor_policy_input_r3_impl(state=state,
        commander_context=commander_context, monitor_policy=monitor_policy,
        facade=_r3_sys.modules[__name__])


def _build_scanner_monitor_frame(
    *,
    playbook: str,
    monitor_guidance: str,
    risk_tone: str,
    trade_aggressiveness: str,
) -> Dict[str, Any]:
    return _build_scanner_monitor_frame_r3_impl(playbook=playbook,
        monitor_guidance=monitor_guidance, risk_tone=risk_tone,
        trade_aggressiveness=trade_aggressiveness, facade=_r3_sys.modules[__name__])


def _calc_reclaim_proximity(*, actual: float | None, minimum: float | None) -> float:
    return _calc_reclaim_proximity_r3_impl(actual=actual, minimum=minimum,
        facade=_r3_sys.modules[__name__])


def _calc_breakout_proximity(*, actual: float | None, minimum: float | None) -> float:
    return _calc_breakout_proximity_r3_impl(actual=actual, minimum=minimum,
        facade=_r3_sys.modules[__name__])


def _scanner_chart_fit_from_entry_result(result: Mapping[str, Any]) -> Dict[str, Any]:
    return _scanner_chart_fit_from_entry_result_r3_impl(result, facade=_r3_sys.modules[__name__])


def _scanner_macro_focus(
    *,
    playbook: str = "",
    scanner_priority: List[Any] | None = None,
    risk_tone: str = "",
    trade_aggressiveness: str = "",
) -> Dict[str, float]:
    return _scanner_macro_focus_r3_impl(playbook=playbook, scanner_priority=scanner_priority,
        risk_tone=risk_tone, trade_aggressiveness=trade_aggressiveness,
        facade=_r3_sys.modules[__name__])


def _compute_scanner_macro_chart_fit(
    *,
    feature_row: Mapping[str, Any],
    ma_alignment_component: float,
    trend_component: float,
    adx_component: float,
    momentum_component: float,
    volume_surge_component: float,
    vwap_alignment_component: float,
    cross_section_rank_component: float,
    volatility_penalty: float,
    gap_penalty: float,
    playbook: str = "",
    scanner_priority: List[Any] | None = None,
    risk_tone: str = "",
    trade_aggressiveness: str = "",
    bias_cap: float = 0.06,
) -> Dict[str, Any]:
    return _compute_scanner_macro_chart_fit_r3_impl(feature_row=feature_row,
        ma_alignment_component=ma_alignment_component, trend_component=trend_component,
        adx_component=adx_component, momentum_component=momentum_component,
        volume_surge_component=volume_surge_component,
        vwap_alignment_component=vwap_alignment_component,
        cross_section_rank_component=cross_section_rank_component,
        volatility_penalty=volatility_penalty, gap_penalty=gap_penalty, playbook=playbook,
        scanner_priority=scanner_priority, risk_tone=risk_tone,
        trade_aggressiveness=trade_aggressiveness, bias_cap=bias_cap,
        facade=_r3_sys.modules[__name__])


def _compute_entry_compatibility_signal(
    *,
    symbol: str,
    feature_row: Dict[str, Any],
    metrics: Dict[str, Any],
    candidate_rows: List[Dict[str, Any]],
    current_price: Any,
    policy: Any,
    bias_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return _compute_entry_compatibility_signal_r3_impl(symbol=symbol, feature_row=feature_row,
        metrics=metrics, candidate_rows=candidate_rows, current_price=current_price, policy=policy,
        bias_context=bias_context, facade=_r3_sys.modules[__name__])


def _resolve_canonical_day(state: Dict[str, Any]) -> str:
    for key in ("day", "trade_day", "session_day"):
        value = str(state.get(key) or "").strip()
        if value:
            return value
    now_epoch = _resolve_now_epoch(state)
    return datetime.fromtimestamp(now_epoch).strftime("%Y-%m-%d")


_ENTRY_COMPATIBILITY_BLOCK_REASONS = {
    "too_extended_from_vwap",
    "breakout_not_ready",
    "volume_insufficient",
    "volume_confirmation_missing",
    "below_vwap_reclaim_not_ready",
    "pullback_below_vwap_reclaim_not_ready",
    "pullback_not_mature",
    "minute_candle_missing",
    "human_chart_sanity_guard_blocked",
}


def _extract_monitor_entry_block_reason(payload: Dict[str, Any]) -> str:
    return _extract_monitor_entry_block_reason_r3_impl(payload, facade=_r3_sys.modules[__name__])


def _resolve_compatibility_bias_context(state: Dict[str, Any], *, limit: int = 20) -> Dict[str, Any]:
    return _resolve_compatibility_bias_context_r3_impl(state, limit=limit,
        facade=_r3_sys.modules[__name__])


def _norm01(x: float, lo: float, hi: float) -> float:
    if hi <= lo:
        return 0.0
    return _clamp((float(x) - float(lo)) / (float(hi) - float(lo)), 0.0, 1.0)


def _signed01(x: float, scale: float = 1.0) -> float:
    s = max(1e-9, float(scale))
    return _clamp(float(x) / s, -1.0, 1.0)


def _merge_mock_compatibility_override(
    base: Dict[str, Any],
    *,
    override: Any,
) -> Dict[str, Any]:
    return _merge_mock_compatibility_override_r3_impl(base, override=override,
        facade=_r3_sys.modules[__name__])


def _apply_blocker_family_concentration_overlay(
    rows: List[Dict[str, Any]],
    *,
    scan_aggressiveness: float,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    return _apply_blocker_family_concentration_overlay_r3_impl(rows,
        scan_aggressiveness=scan_aggressiveness, facade=_r3_sys.modules[__name__])


def scanner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    candidates, policy, pool_meta = scan_context_candidates_policy(state=state, facade=_r3_sys.modules[__name__])
    if _enforce_live_equity_symbols(state, policy):
        candidates, live_symbol_meta = _filter_live_equity_candidates(list(candidates or []))
        pool_meta = dict(pool_meta)
        pool_meta.update(dict(live_symbol_meta))
    full_strategist_control_eligibility = build_full_strategist_control_eligibility(pool_meta)
    state["scanner_source_universe_before_strategy_weighting"] = {
        "schema_version": "q9_scanner_source_universe.v1",
        "behavior_effect": "evaluation_only",
        "candidate_count": len(candidates),
        "rows": [
            {
                "rank": index,
                "symbol": _norm_symbol(item.get("symbol")) if isinstance(item, dict) else _norm_symbol(item),
                "sources": list(item.get("sources") or [])[:8] if isinstance(item, dict) else [],
                "source_scores": dict(item.get("source_scores") or {}) if isinstance(item, dict) else {},
                "source_observations": dict(item.get("source_observations") or {}) if isinstance(item, dict) else {},
                "rank_score": _to_float(item.get("rank_score")) if isinstance(item, dict) else 0.0,
                "universe_score": _to_float(item.get("universe_score")) if isinstance(item, dict) else 0.0,
                "why": str(item.get("why") or "") if isinstance(item, dict) else "",
            }
            for index, item in enumerate(list(candidates)[:50], start=1)
            if (
                _norm_symbol(item.get("symbol"))
                if isinstance(item, dict)
                else _norm_symbol(item)
            )
        ],
        "candidate_source": str(pool_meta.get("candidate_source") or ""),
        "scanner_candidate_source": str(pool_meta.get("scanner_candidate_source") or ""),
        "full_strategist_control_eligibility": dict(full_strategist_control_eligibility),
        "limitation": (
            "Captured before Scanner asset/practical filters and score overlays; source inclusion "
            "may still reflect the current Strategist-provided source policy."
        ),
    }
    run_id = str(state.get("run_id") or "").strip() or "scanner-unknown"

    mock: Optional[Mapping[str, Any]] = state.get("mock_scan_results")  # for tests
    mock_by_sym: Dict[str, Any] = {}
    if isinstance(mock, Mapping):
        for k, v in mock.items():
            mock_by_sym[_norm_symbol(k)] = v

    commander_context, intrinsic_control_w, monitor_guidance, playbook, policy_provenance, practical_w, risk_tone, scanner_bias, scanner_bias_context, scanner_guidance, scanner_memory_bias, scanner_policy_trace, scanner_priority, strategy_monitor_policy, trade_aggressiveness, w = scan_context_commander_context_intrinsic_control_w(policy=policy, state=state, facade=_r3_sys.modules[__name__])
    if isinstance(scanner_guidance.get("score_weights"), dict):
        for key, value in dict(scanner_guidance.get("score_weights") or {}).items():
            if key in practical_w and value not in (None, ""):
                practical_w[key] = _to_float(value)
    practical_w = _apply_scanner_guidance_weights(
        practical_w,
        playbook=playbook,
        scanner_bias=scanner_bias,
        scanner_priority=scanner_priority,
        trade_aggressiveness=trade_aggressiveness,
        risk_tone=risk_tone,
    )
    state = _maybe_hydrate_scanner_skill_results(state, list(candidates))
    skill_quotes, quote_meta = _extract_skill_quotes(state)
    skill_order_counts, skill_order_rows, order_meta = _extract_account_open_order_counts(state)
    quote_metric_coverage = _summarize_quote_metric_coverage(list(candidates), skill_quotes=skill_quotes, state=state)
    refresh_existing_features, feature_refresh_reason = _should_refresh_scanner_features(
        state=state,
        candidates=list(candidates),
        quote_metric_coverage=quote_metric_coverage,
    )
    feature_map, feature_source, feature_errors = hydrate_scanner_feature_map(
        state=state,
        candidates=list(candidates),
        skill_quotes=skill_quotes,
        policy=policy,
        refresh_existing=refresh_existing_features,
    )
    if not feature_map:
        feature_map, feature_source, feature_errors = _extract_feature_engine_map(state)
    minute_rows_by_symbol, minute_rows_meta = extract_minute_ohlcv_by_symbol(state)
    ohlcv_by_symbol = state.get("ohlcv_by_symbol") if isinstance(state.get("ohlcv_by_symbol"), dict) else {}
    compatibility_bias_context = _resolve_compatibility_bias_context(state)
    compatibility_policy_input = _build_scanner_monitor_policy_input(
        state=state,
        commander_context=commander_context,
        monitor_policy=strategy_monitor_policy,
    )
    compatibility_frame = _build_scanner_monitor_frame(
        playbook=playbook,
        monitor_guidance=monitor_guidance,
        risk_tone=risk_tone,
        trade_aggressiveness=trade_aggressiveness,
    )
    compatibility_policy = (
        resolve_intraday_entry_policy(compatibility_policy_input or None, frame=compatibility_frame or None)
        if compatibility_policy_input
        else None
    )
    state["scanner_quote_diagnostic"] = {
        **dict(quote_metric_coverage),
        "feature_refresh_forced": bool(refresh_existing_features),
        "feature_refresh_reason": str(feature_refresh_reason or ""),
        "feature_source": str(feature_source or ""),
        "minute_rows_source": str(minute_rows_meta.get("source") or "") if isinstance(minute_rows_meta, dict) else "",
    }
    gs = _get_global_sentiment_score(state)
    gs_signal = _get_global_sentiment_signal(state)
    news_by_sym = _get_news_sentiment_map(state)
    news_signal_by_sym = _get_news_sentiment_signal_map(state)
    try:
        raw_candidates = []
        for item in list(candidates)[:50]:
            if isinstance(item, dict):
                raw_candidates.append(
                    {
                        "symbol": _norm_symbol(item.get("symbol")),
                        "why": str(item.get("why") or ""),
                        "sources": list(item.get("sources") or [])[:5],
                        "rank_score": _to_float(item.get("rank_score") or 0.0),
                    }
                )
            else:
                raw_candidates.append({"symbol": _norm_symbol(item), "why": "raw_candidate"})
        record_raw_input(
            run_id=run_id,
            agent="scanner",
            stage="symbol_selection",
            raw_input={
                "candidate_pool_before_filter": int(len(candidates)),
                "candidates": raw_candidates,
                "candidate_source": str(pool_meta.get("candidate_source") or ""),
                "strategist_guidance": {
                    "themes": list(scanner_guidance.get("themes") or []),
                    "selected_themes": list(scanner_guidance.get("selected_themes") or []),
                    "avoid_themes": list(scanner_guidance.get("avoid_themes") or []),
                    "playbook": playbook,
                    "scanner_bias": scanner_bias,
                    "scanner_bias_context": dict(scanner_policy_trace.get("scanner_bias_context") or {}),
                    "scanner_priority": list(scanner_priority),
                    "scanner_source_policy": dict(scanner_guidance.get("scanner_source_policy") or {}),
                    "trade_aggressiveness": trade_aggressiveness,
                    "risk_tone": risk_tone,
                    "theme_source": str(scanner_guidance.get("theme_source") or ""),
                    "theme_source_status": str(scanner_guidance.get("theme_source_status") or ""),
                    "available_themes": list(scanner_guidance.get("available_themes") or [])[:8],
                    "theme_strategy": dict(scanner_guidance.get("theme_strategy") or {})
                    if isinstance(scanner_guidance.get("theme_strategy"), dict)
                    else {},
                    "theme_strength_packet_summary": {
                        "source": str((scanner_guidance.get("theme_strength_packet") or {}).get("source") or "")
                        if isinstance(scanner_guidance.get("theme_strength_packet"), dict)
                        else "",
                        "status": str((scanner_guidance.get("theme_strength_packet") or {}).get("status") or "")
                        if isinstance(scanner_guidance.get("theme_strength_packet"), dict)
                        else "",
                        "top_themes": list((scanner_guidance.get("theme_strength_packet") or {}).get("top_themes") or [])[:5]
                        if isinstance(scanner_guidance.get("theme_strength_packet"), dict)
                        else [],
                    },
                },
                "commander_context": scanner_policy_trace.get("commander_priority_ref"),
                "strategist_plan": scanner_policy_trace.get("strategist_constraints_ref"),
                "global_sentiment_score": float(gs),
                "feature_source": str(feature_source),
                "feature_symbol_count": int(len(feature_map)),
                "feature_errors": list(feature_errors),
                "quote_metric_coverage": dict(quote_metric_coverage),
                "feature_refresh_forced": bool(refresh_existing_features),
                "feature_refresh_reason": str(feature_refresh_reason or ""),
            },
            decision_link={"stage": "scanner_candidate_retrieval"},
        )
    except Exception:
        pass

    asset_filtered_candidates, asset_policy_meta = apply_asset_universe_filter(
        candidates,
        state=state,
        policy=policy,
        market_quotes=skill_quotes,
        allow_remote_lookup=True,
    )
    if int(asset_policy_meta.get("asset_policy_excluded_count") or 0) > 0:
        if not asset_filtered_candidates and not str((pool_meta or {}).get("fallback_reason") or "").strip():
            pool_meta = dict(pool_meta)
            pool_meta["fallback_reason"] = "asset_policy_filtered_all_candidates"
        _emit_scanner_event(
            state,
            name="asset_policy_exclusions",
            payload={
                "asset_universe_policy": str(asset_policy_meta.get("asset_universe_policy") or ""),
                "asset_universe_policy_source": str(asset_policy_meta.get("asset_universe_policy_source") or ""),
                "excluded_candidate_count": int(asset_policy_meta.get("asset_policy_excluded_count") or 0),
                "excluded_symbols": list(asset_policy_meta.get("asset_policy_excluded_symbols") or []),
                "exclusions": list(asset_policy_meta.get("asset_policy_exclusions") or []),
                "asset_detection_stats": dict(asset_policy_meta.get("asset_detection_stats") or {}),
                "unknown_asset_candidate_count": int(asset_policy_meta.get("unknown_asset_candidate_count") or 0),
                "total_candidates_before_filter": int(asset_policy_meta.get("total_candidates_before_filter") or 0),
                "total_candidates_after_filter": int(asset_policy_meta.get("total_candidates_after_filter") or 0),
            },
        )
    candidates = list(asset_filtered_candidates)
    pool_meta = dict(pool_meta)
    pool_meta.update(dict(asset_policy_meta))

    restricted_filtered_candidates, restricted_meta = _filter_mock_broker_restricted_candidates(
        candidates,
        state=state,
    )
    candidates = list(restricted_filtered_candidates)
    pool_meta.update(dict(restricted_meta))
    if int(restricted_meta.get("mock_broker_restricted_excluded_count") or 0) > 0:
        _emit_scanner_event(
            state,
            name="mock_broker_restricted_symbol_exclusions",
            payload={
                "excluded_candidate_count": int(restricted_meta.get("mock_broker_restricted_excluded_count") or 0),
                "excluded_symbols": list(restricted_meta.get("mock_broker_restricted_excluded_symbols") or []),
                "exclusions": list(restricted_meta.get("mock_broker_restricted_exclusions") or []),
                "candidate_pool_after_filter": int(restricted_meta.get("candidate_pool_after_mock_broker_restricted_filter") or 0),
            },
        )

    # Practical pool reduction before scoring.
    reduced_candidates, reduction_meta = _reduce_candidates_by_practical_filters(
        candidates,
        state=state,
        policy=policy,
        skill_quotes=skill_quotes,
    )
    candidates = list(reduced_candidates)
    pool_meta.update(dict(reduction_meta))
    state["scanner_candidate_pool"] = dict(pool_meta)
    practical_enabled = str(pool_meta.get("candidate_source") or "").strip().lower() == "kiwoom_market_data"
    if policy.get("enable_practical_scoring") is not None:
        practical_enabled = _is_trueish(policy.get("enable_practical_scoring"))
    practical_scale = 1.0 if practical_enabled else 0.0

    scan_results: List[Dict[str, Any]] = []
    symbol_priors = _load_symbol_priors(state, candidates)

    for item in candidates:
        candidate_meta: Dict[str, Any] = {}
        if isinstance(item, dict):
            symbol = _norm_symbol(item.get("symbol"))
            candidate_meta = dict(item)
        else:
            symbol = _norm_symbol(item)

        if not symbol:
            continue

        if symbol in mock_by_sym:
            row = dict(mock_by_sym[symbol])
            row.setdefault("symbol", symbol)
        else:
            base = _stable_unit_hash(symbol)
            # Simple deterministic defaults (placeholder)
            score = 1.0 - base  # higher is better
            confidence = max(0.0, min(1.0, 0.9 - base * 0.4))
            row = {
                "symbol": symbol,
                "score": float(score),
                "confidence": float(confidence),
                "features": {
                    "unit_hash": float(base),
                },
            }

        # ---- Practical scoring model (additive, deterministic) ----
        base_score = _to_float(row.get("score") or 0.0)
        base_conf = _to_float(row.get("confidence") or 0.55)
        row["raw_score"] = float(base_score)
        row["base_score"] = float(base_score)
        candidate_rank_score, candidate_universe_score, deviation_signal, etf_deviation_bias, etf_deviation_entry_score, etf_deviation_premium_score, etf_deviation_tradeable, feature_regime, feature_row, feature_signal, ma120_gap, ma20_gap, ma60_gap, metrics, news_s, news_sig, open_orders, order_penalty, quote, quote_price, quote_price_num, return20, source_scores, trend_strength = scan_feature_candidate_rank_score_candidate_universe(candidate_meta=candidate_meta, symbol=symbol, news_by_sym=news_by_sym, news_signal_by_sym=news_signal_by_sym, skill_quotes=skill_quotes, state=state, row=row, feature_map=feature_map, skill_order_counts=skill_order_counts, facade=_r3_sys.modules[__name__])
        adx14, adx_component, avoid_theme_symbols, base_risk, base_risk_result, cross_section_rank, cross_section_rank_component, gap_pct, intraday_strength_component, ma_alignment_component, momentum_component, momentum_raw, sentiment_component, theme_boost_component, theme_matched_symbols, trading_value_component, trend_component, trend_raw, volatility20, volatility_penalty, volume_spike20, volume_surge_component, vwap_alignment_component, vwap_distance = scan_feature_adx14_adx_component(feature_row=feature_row, candidate_meta=candidate_meta, row=row, metrics=metrics, source_scores=source_scores, return20=return20, ma20_gap=ma20_gap, ma120_gap=ma120_gap, ma60_gap=ma60_gap, trend_strength=trend_strength, feature_signal=feature_signal, pool_meta=pool_meta, symbol=symbol, news_s=news_s, gs=gs, facade=_r3_sys.modules[__name__])
        avoid_theme_penalty, bias_result, blocker_penalty_meta, candidate_rows, gap_penalty, intrinsic_control_positive, intrinsic_control_risk, legacy_adjust, memory_bias_result, open_order_penalty, positive_score, rank_bonus, raw_minute_rows, repeat_blocker_penalty, repeat_penalty_meta, repeat_symbol_penalty, risk_penalty_score, scanner_bias_adjustment, scanner_memory_bias_adjustment, scanner_memory_bias_observation_only, scanner_memory_bias_observed_adjustment = scan_feature_avoid_theme_penalty_bias_result(gap_pct=gap_pct, order_penalty=order_penalty, symbol=symbol, avoid_theme_symbols=avoid_theme_symbols, state=state, policy=policy, practical_scale=practical_scale, cross_section_rank_component=cross_section_rank_component, candidate_universe_score=candidate_universe_score, sentiment_component=sentiment_component, candidate_rank_score=candidate_rank_score, theme_boost_component=theme_boost_component, practical_w=practical_w, intraday_strength_component=intraday_strength_component, volume_surge_component=volume_surge_component, trend_component=trend_component, trading_value_component=trading_value_component, momentum_component=momentum_component, volatility_penalty=volatility_penalty, feature_signal=feature_signal, news_s=news_s, gs=gs, w=w, intrinsic_control_w=intrinsic_control_w, feature_row=feature_row, metrics=metrics, scanner_bias_context=scanner_bias_context, scanner_memory_bias=scanner_memory_bias, candidate_meta=candidate_meta, minute_rows_by_symbol=minute_rows_by_symbol, facade=_r3_sys.modules[__name__])
        if isinstance(raw_minute_rows, list) and raw_minute_rows:
            candidate_rows = list(raw_minute_rows)
        else:
            raw_ohlcv_rows = ohlcv_by_symbol.get(_norm_symbol(symbol)) if isinstance(ohlcv_by_symbol.get(_norm_symbol(symbol)), list) else []
            if raw_ohlcv_rows:
                candidate_rows = list(raw_ohlcv_rows)
        compatibility_result = _compute_entry_compatibility_signal(
            symbol=symbol,
            feature_row=feature_row,
            metrics=metrics,
            candidate_rows=candidate_rows,
            current_price=quote_price_num or feature_row.get("close_last"),
            policy=compatibility_policy,
            bias_context=compatibility_bias_context,
        )
        mock_row = mock_by_sym.get(symbol) if isinstance(mock_by_sym.get(symbol), Mapping) else {}
        mock_compatibility_override = mock_row.get("compatibility_override") if isinstance(mock_row.get("compatibility_override"), Mapping) else {}
        if not mock_compatibility_override and isinstance(mock_row, Mapping):
            top_level_override = {
                key: mock_row.get(key)
                for key in (
                    "entry_compatibility_score",
                    "compatibility_bias",
                    "expected_monitor_block_reason",
                    "dominant_block_reason",
                    "dominant_block_reason_ratio",
                    "bias_scale",
                    "soft_penalty",
                    "compatibility_score_pre_penalty",
                    "compatibility_score_post_penalty",
                )
                if mock_row.get(key) not in (None, "")
            }
            if top_level_override:
                mock_compatibility_override = top_level_override
        adj_risk, compatibility_bias, compatibility_result, feature_risk, macro_chart_fit, neg_global, neg_news, pre_adjust_score_total, scanner_intrinsic_control_score_total, scanner_macro_chart_fit_bias, score_total, symbol_prior_adjustment, symbol_prior_result = scan_score_adj_risk_compatibility_bias(compatibility_result=compatibility_result, mock_compatibility_override=mock_compatibility_override, feature_row=feature_row, ma_alignment_component=ma_alignment_component, trend_component=trend_component, adx_component=adx_component, momentum_component=momentum_component, volume_surge_component=volume_surge_component, vwap_alignment_component=vwap_alignment_component, cross_section_rank_component=cross_section_rank_component, volatility_penalty=volatility_penalty, gap_penalty=gap_penalty, playbook=playbook, scanner_priority=scanner_priority, risk_tone=risk_tone, trade_aggressiveness=trade_aggressiveness, state=state, symbol=symbol, symbol_priors=symbol_priors, etf_deviation_bias=etf_deviation_bias, scanner_memory_bias_adjustment=scanner_memory_bias_adjustment, repeat_blocker_penalty=repeat_blocker_penalty, repeat_symbol_penalty=repeat_symbol_penalty, rank_bonus=rank_bonus, intrinsic_control_risk=intrinsic_control_risk, legacy_adjust=legacy_adjust, base_score=base_score, intrinsic_control_positive=intrinsic_control_positive, scanner_bias_adjustment=scanner_bias_adjustment, risk_penalty_score=risk_penalty_score, positive_score=positive_score, news_s=news_s, gs=gs, w=w, feature_signal=feature_signal, feature_regime=feature_regime, open_order_penalty=open_order_penalty, practical_scale=practical_scale, base_risk=base_risk, facade=_r3_sys.modules[__name__])
        adj_conf, adj_risk, score_breakdown = scan_score_adj_conf_adj_risk(etf_deviation_tradeable=etf_deviation_tradeable, etf_deviation_premium_score=etf_deviation_premium_score, etf_deviation_entry_score=etf_deviation_entry_score, open_order_penalty=open_order_penalty, base_conf=base_conf, positive_score=positive_score, risk_penalty_score=risk_penalty_score, w=w, news_s=news_s, repeat_symbol_penalty=repeat_symbol_penalty, adj_risk=adj_risk, repeat_blocker_penalty=repeat_blocker_penalty, symbol_prior_result=symbol_prior_result, scanner_bias_adjustment=scanner_bias_adjustment, scanner_memory_bias_adjustment=scanner_memory_bias_adjustment, scanner_memory_bias_observed_adjustment=scanner_memory_bias_observed_adjustment, symbol_prior_adjustment=symbol_prior_adjustment, etf_deviation_bias=etf_deviation_bias, compatibility_bias=compatibility_bias, scanner_macro_chart_fit_bias=scanner_macro_chart_fit_bias, rank_bonus=rank_bonus, trading_value_component=trading_value_component, momentum_component=momentum_component, trend_component=trend_component, ma_alignment_component=ma_alignment_component, adx_component=adx_component, volume_surge_component=volume_surge_component, intraday_strength_component=intraday_strength_component, vwap_alignment_component=vwap_alignment_component, theme_boost_component=theme_boost_component, sentiment_component=sentiment_component, practical_scale=practical_scale, practical_w=practical_w, cross_section_rank_component=cross_section_rank_component, avoid_theme_penalty=avoid_theme_penalty, facade=_r3_sys.modules[__name__])

        row["score"] = float(score_total)
        row["score_total"] = float(score_total)
        row["score_breakdown"] = dict(score_breakdown)
        row["bias_adjustment"] = float(scanner_bias_adjustment)
        row["bias_adjustments"] = list(bias_result.get("bias_adjustments") or [])
        row["bias_summary"] = dict(bias_result.get("bias_summary") or {})
        row["memory_bias_adjustment"] = float(scanner_memory_bias_adjustment)
        row["memory_bias_observed_adjustment"] = float(scanner_memory_bias_observed_adjustment)
        row["memory_bias_observation_only"] = bool(scanner_memory_bias_observation_only)
        row["memory_bias_source_delta"] = float(memory_bias_result.get("source_delta") or 0.0)
        row["memory_bias_symbol_delta"] = float(memory_bias_result.get("symbol_delta") or 0.0)
        row["memory_bias_adjustments"] = list(memory_bias_result.get("adjustments") or [])
        row["memory_bias_summary"] = dict(memory_bias_result.get("summary") or {})
        row["symbol_prior_adjustment"] = float(symbol_prior_adjustment)
        row["symbol_prior_reasons"] = list(symbol_prior_result.get("reasons") or [])
        row["symbol_prior_summary"] = dict(symbol_prior_result.get("summary") or {})
        row["etf_deviation_pct"] = deviation_signal.get("etf_deviation_pct")
        row["etf_deviation_source"] = str(deviation_signal.get("etf_deviation_source") or "")
        row["etf_deviation_available"] = bool(deviation_signal.get("available"))
        row["etf_deviation_entry_score"] = float(etf_deviation_entry_score)
        row["etf_deviation_premium_score"] = float(etf_deviation_premium_score)
        row["etf_deviation_bias"] = float(etf_deviation_bias)
        row["entry_compatibility_score"] = float(compatibility_result.get("entry_compatibility_score") or 0.0)
        row["compatibility_bias"] = float(compatibility_bias)
        row["compatibility_components"] = dict(compatibility_result.get("compatibility_components") or {})
        row["scanner_chart_fit_score"] = float(_to_float(compatibility_result.get("scanner_chart_fit_score")))
        row["scanner_chart_fit_authority"] = str(compatibility_result.get("scanner_chart_fit_authority") or "")
        row["scanner_chart_fit_components"] = dict(compatibility_result.get("scanner_chart_fit_components") or {})
        row["scanner_chart_fit_penalty"] = float(_to_float(compatibility_result.get("scanner_chart_fit_penalty")))
        row["scanner_macro_chart_fit_score"] = float(
            _to_float(macro_chart_fit.get("scanner_macro_chart_fit_score"), 0.5)
        )
        row["scanner_macro_chart_fit_bias"] = float(scanner_macro_chart_fit_bias)
        row["scanner_macro_chart_fit_authority"] = str(
            macro_chart_fit.get("scanner_macro_chart_fit_authority") or ""
        )
        row["scanner_macro_chart_fit_components"] = dict(
            macro_chart_fit.get("scanner_macro_chart_fit_components") or {}
        )
        row["scanner_macro_chart_fit_focus"] = dict(
            macro_chart_fit.get("scanner_macro_chart_fit_focus") or {}
        )
        row["expected_monitor_block_reason"] = str(compatibility_result.get("expected_monitor_block_reason") or "")
        row["dominant_block_reason"] = str(compatibility_result.get("dominant_block_reason") or "")
        row["dominant_block_reason_ratio"] = float(_to_float(compatibility_result.get("dominant_block_reason_ratio")))
        row["bias_scale"] = float(_to_float(compatibility_result.get("bias_scale")))
        row["soft_penalty"] = float(_to_float(compatibility_result.get("soft_penalty")))
        row["compatibility_score_pre_penalty"] = float(_to_float(compatibility_result.get("compatibility_score_pre_penalty")))
        row["compatibility_score_post_penalty"] = float(_to_float(compatibility_result.get("compatibility_score_post_penalty")))
        row["compatibility_trace"] = dict(compatibility_result)
        row["pre_adjust_score_total"] = float(pre_adjust_score_total)
        row["post_adjust_score_total"] = float(score_total)
        row["scanner_intrinsic_control_score_total"] = float(
            scanner_intrinsic_control_score_total
        )
        row["risk_score"] = float(_clamp(adj_risk, 0.0, 1.0))
        row["base_risk_source"] = str(base_risk_result.get("source") or "")
        row["base_risk_components"] = dict(base_risk_result.get("components") or {})
        row["base_risk_missing_inputs"] = list(base_risk_result.get("missing_inputs") or [])
        row["confidence"] = float(adj_conf)
        row["why"] = str(candidate_meta.get("why") or row.get("why") or "")
        row["asset_class_detected"] = str(candidate_meta.get("asset_class_detected") or "")
        row["detection_source"] = str(candidate_meta.get("detection_source") or "")
        row["detection_field"] = str(candidate_meta.get("detection_field") or "")
        row["excluded_by_asset_policy"] = bool(candidate_meta.get("excluded_by_asset_policy"))
        row["exclusion_reason"] = str(candidate_meta.get("exclusion_reason") or "")
        row["source_observations"] = dict(candidate_meta.get("source_observations") or {})
        row["candidate"] = {
            "source_why": str(candidate_meta.get("why") or ""),
            "sources": list(candidate_meta.get("sources") or []),
            "rank_score": float(candidate_rank_score),
            "universe_score": float(candidate_universe_score),
            "source_scores": dict(candidate_meta.get("source_scores") or {}),
            "source_observations": dict(candidate_meta.get("source_observations") or {}),
            "source_count": int(candidate_meta.get("source_count") or len(list(candidate_meta.get("sources") or []))),
            "asset_class_detected": str(candidate_meta.get("asset_class_detected") or ""),
            "detection_source": str(candidate_meta.get("detection_source") or ""),
            "detection_field": str(candidate_meta.get("detection_field") or ""),
            "excluded_by_asset_policy": bool(candidate_meta.get("excluded_by_asset_policy")),
            "exclusion_reason": str(candidate_meta.get("exclusion_reason") or ""),
        }
        row.setdefault("features", {})
        if isinstance(row.get("features"), dict):
            row["features"].update(
                {
                    "skill_quote_price": quote_price_num,
                    "skill_open_orders": open_orders,
                    "skill_open_orders_pending_only": True,
                    "quote_best_bid": _to_float(metrics.get("best_bid")),
                    "quote_best_ask": _to_float(metrics.get("best_ask")),
                    "quote_spread_bps": metrics.get("spread_bps"),
                    "quote_payload_available": bool(metrics.get("quote_payload_available")),
                    "quote_source": str(metrics.get("quote_source") or ""),
                    "quote_evidence_status": str(
                        metrics.get("bid_ask_evidence_status") or ""
                    ),
                    "etf_deviation_pct": deviation_signal.get("etf_deviation_pct"),
                    "etf_deviation_source": str(deviation_signal.get("etf_deviation_source") or ""),
                    "etf_deviation_available": bool(deviation_signal.get("available")),
                    "etf_deviation_entry_score": float(etf_deviation_entry_score),
                    "etf_deviation_premium_score": float(etf_deviation_premium_score),
                    "asset_class_detected": str(
                        deviation_signal.get("asset_class_detected")
                        or candidate_meta.get("asset_class_detected")
                        or ""
                    ),
                    "engine_rsi14": feature_row.get("rsi14"),
                    "engine_close_last": feature_row.get("close_last"),
                    "engine_ma20_gap": feature_row.get("ma20_gap"),
                    "engine_ma60": feature_row.get("ma60"),
                    "engine_ma120": feature_row.get("ma120"),
                    "engine_adx14": feature_row.get("adx14"),
                    "engine_trend_strength": feature_row.get("trend_strength"),
                    "engine_atr14": feature_row.get("atr14"),
                    "engine_volume_spike20": feature_row.get("volume_spike20"),
                    "engine_volatility20": feature_row.get("volatility20"),
                    "engine_realized_volatility": feature_row.get("realized_volatility"),
                    "engine_vwap_distance": feature_row.get("vwap_distance"),
                    "engine_rolling_drawdown20": feature_row.get("rolling_drawdown20"),
                    "engine_sector_relative_strength": feature_row.get("sector_relative_strength"),
                    "engine_cross_section_rank": feature_row.get("cross_section_rank"),
                    "engine_regime": feature_row.get("regime"),
                    "engine_signal_score": feature_signal,
                    "intraday_change_pct": _to_float(metrics.get("change_pct")),
                    "quote_trading_value": _to_float(metrics.get("trading_value")),
                    "quote_volume": _to_float(metrics.get("volume")),
                    "entry_compatibility_score": compatibility_result.get("entry_compatibility_score"),
                    "compatibility_bias": compatibility_result.get("compatibility_bias"),
                    "compatibility_components": dict(compatibility_result.get("compatibility_components") or {}),
                    "scanner_chart_fit_score": compatibility_result.get("scanner_chart_fit_score"),
                    "scanner_chart_fit_authority": compatibility_result.get("scanner_chart_fit_authority"),
                    "scanner_chart_fit_components": dict(compatibility_result.get("scanner_chart_fit_components") or {}),
                    "scanner_macro_chart_fit_score": macro_chart_fit.get("scanner_macro_chart_fit_score"),
                    "scanner_macro_chart_fit_bias": scanner_macro_chart_fit_bias,
                    "scanner_macro_chart_fit_authority": macro_chart_fit.get("scanner_macro_chart_fit_authority"),
                    "scanner_macro_chart_fit_components": dict(
                        macro_chart_fit.get("scanner_macro_chart_fit_components") or {}
                    ),
                    "compatibility_source": compatibility_result.get("compatibility_source"),
                    "compat_vwap_distance_abs": compatibility_result.get("vwap_distance_abs"),
                    "compat_is_below_vwap": compatibility_result.get("is_below_vwap"),
                    "compat_reclaim_proximity": compatibility_result.get("reclaim_proximity"),
                    "compat_volume_ratio": compatibility_result.get("volume_ratio"),
                    "compat_breakout_gap_pct": compatibility_result.get("breakout_gap_pct"),
                }
            )
        row.setdefault("components", {})
        if isinstance(row.get("components"), dict):
            row["components"].update(
                {
                    "base_score": base_score,
                    "base_risk": base_risk,
                    "base_risk_source": str(base_risk_result.get("source") or ""),
                    "base_risk_components": dict(base_risk_result.get("components") or {}),
                    "base_risk_missing_inputs": list(base_risk_result.get("missing_inputs") or []),
                    "base_confidence": base_conf,
                    "news_sentiment": news_s,
                    "global_sentiment": gs,
                    "weight_news": w["weight_news"],
                    "weight_global": w["weight_global"],
                    "risk_news_penalty": w["risk_news_penalty"],
                    "risk_global_penalty": w["risk_global_penalty"],
                    "feature_signal": feature_signal,
                    "feature_regime": feature_regime,
                    "feature_score_weight": w["feature_score_weight"],
                    "feature_risk_penalty": w["feature_risk_penalty"],
                    "high_vol_risk_penalty": w["high_vol_risk_penalty"],
                    "practical_positive_score": float(positive_score),
                    "practical_risk_penalty_score": float(risk_penalty_score),
                    "skill_open_orders": open_orders,
                    "candidate_rank_score": candidate_rank_score,
                    "candidate_universe_score": candidate_universe_score,
                    "trading_value_component": trading_value_component,
                    "momentum_component": momentum_component,
                    "trend_component": trend_component,
                    "ma_alignment_component": ma_alignment_component,
                    "adx_component": adx_component,
                    "volume_surge_component": volume_surge_component,
                    "intraday_strength_component": intraday_strength_component,
                    "vwap_alignment_component": vwap_alignment_component,
                    "cross_section_rank_component": cross_section_rank_component,
                    "theme_boost_component": theme_boost_component,
                    "sentiment_component": sentiment_component,
                    "volatility_penalty_component": volatility_penalty,
                    "gap_penalty_component": gap_penalty,
                    "open_order_penalty_component": open_order_penalty,
                    "avoid_theme_penalty_component": avoid_theme_penalty,
                    "repeat_symbol_penalty_component": repeat_symbol_penalty,
                    "repeat_blocker_penalty_component": repeat_blocker_penalty,
                    "scanner_bias_adjustment": float(scanner_bias_adjustment),
                    "scanner_memory_bias_adjustment": float(scanner_memory_bias_adjustment),
                    "scanner_memory_bias_source_delta": float(memory_bias_result.get("source_delta") or 0.0),
                    "scanner_memory_bias_symbol_delta": float(memory_bias_result.get("symbol_delta") or 0.0),
                    "scanner_memory_bias_adjustments": list(memory_bias_result.get("adjustments") or []),
                    "entry_compatibility_score": compatibility_result.get("entry_compatibility_score"),
                    "entry_compatibility_bias": compatibility_result.get("compatibility_bias"),
                    "compatibility_components": dict(compatibility_result.get("compatibility_components") or {}),
                    "scanner_chart_fit_score": compatibility_result.get("scanner_chart_fit_score"),
                    "scanner_chart_fit_authority": compatibility_result.get("scanner_chart_fit_authority"),
                    "scanner_chart_fit_components": dict(compatibility_result.get("scanner_chart_fit_components") or {}),
                    "scanner_chart_fit_penalty": compatibility_result.get("scanner_chart_fit_penalty"),
                    "scanner_macro_chart_fit_score": macro_chart_fit.get("scanner_macro_chart_fit_score"),
                    "scanner_macro_chart_fit_bias": scanner_macro_chart_fit_bias,
                    "scanner_macro_chart_fit_authority": macro_chart_fit.get("scanner_macro_chart_fit_authority"),
                    "scanner_macro_chart_fit_components": dict(
                        macro_chart_fit.get("scanner_macro_chart_fit_components") or {}
                    ),
                    "scanner_macro_chart_fit_focus": dict(
                        macro_chart_fit.get("scanner_macro_chart_fit_focus") or {}
                    ),
                    "expected_monitor_block_reason": compatibility_result.get("expected_monitor_block_reason"),
                    "dominant_block_reason": compatibility_result.get("dominant_block_reason"),
                    "dominant_block_reason_ratio": compatibility_result.get("dominant_block_reason_ratio"),
                    "bias_scale": compatibility_result.get("bias_scale"),
                    "soft_penalty": compatibility_result.get("soft_penalty"),
                    "compatibility_score_pre_penalty": compatibility_result.get("compatibility_score_pre_penalty"),
                    "compatibility_score_post_penalty": compatibility_result.get("compatibility_score_post_penalty"),
                    "compatibility_source": compatibility_result.get("compatibility_source"),
                    "pre_adjust_score_total": float(pre_adjust_score_total),
                    "post_adjust_score_total": float(score_total),
                    "scanner_bias_signals": dict(bias_result.get("bias_signals") or {}),
                    "recent_selection_repeat_count": int(repeat_penalty_meta.get("repeat_count") or 0),
                    "recent_selection_streak_count": int(repeat_penalty_meta.get("streak_count") or 0),
                    "recent_trade_same_symbol": bool(repeat_penalty_meta.get("recent_trade_same_symbol")),
                    "recent_blocker_repeat_count": int(blocker_penalty_meta.get("repeat_count") or 0),
                    "recent_blocker_reason": str(blocker_penalty_meta.get("reason") or ""),
                    "news_sentiment_status": str(news_sig.get("status") or "fallback"),
                    "news_sentiment_source": str(news_sig.get("source") or ""),
                    "news_sentiment_reason": str(news_sig.get("reason") or ""),
                    "global_sentiment_status": str(gs_signal.get("status") or "fallback"),
                    "global_sentiment_source": str(gs_signal.get("source") or ""),
                    "global_sentiment_reason": str(gs_signal.get("reason") or ""),
                }
            )

        tactic_id = str(scanner_guidance.get("tactical_strategy") or "")
        row["tactical_strategy"] = tactic_id
        row["tactical_subtype"] = str(scanner_guidance.get("tactical_subtype") or "")
        row["playbook"] = playbook
        row["tactic_suitability"] = score_candidate_tactic_suitability(
            row,
            tactic_id=tactic_id,
            playbook=playbook,
        )

        scan_results.append(row)

    # Sort by score desc, then confidence desc, then risk asc
    scan_results_sorted = sorted(
        scan_results,
        key=lambda r: (
            float(r.get("score") or 0.0),
            float(r.get("confidence") or 0.0),
            -float(r.get("risk_score") or 0.0),
        ),
        reverse=True,
    )

    # ---- [NEW: Commander Policy Overlay] ----
    commander_decision = state.get("commander_decision") if isinstance(state.get("commander_decision"), dict) else {}
    commander_scanner_policy = commander_decision.get("scanner_policy") if isinstance(commander_decision.get("scanner_policy"), dict) else {}
    if not commander_scanner_policy:
        applied_policy = state.get("applied_policy") if isinstance(state.get("applied_policy"), dict) else {}
        applied_scanner_policy = applied_policy.get("scanner") if isinstance(applied_policy.get("scanner"), dict) else {}
        if applied_scanner_policy:
            commander_scanner_policy = dict(applied_scanner_policy)
    if not isinstance(commander_scanner_policy.get("market_representative_guard"), dict):
        source_type = str(((commander_scanner_policy.get("source") or {}).get("type") if isinstance(commander_scanner_policy.get("source"), dict) else "") or "").strip().lower()
        if source_type in ("", "kiwoom", "hybrid", "auto"):
            commander_scanner_policy = dict(commander_scanner_policy)
            commander_scanner_policy["market_representative_guard"] = _default_market_representative_guard_policy()
    enforce_blocker_family_veto = _is_trueish(
        commander_scanner_policy.get(
            "enforce_blocker_family_selection_veto",
            os.getenv("SCANNER_ENFORCE_BLOCKER_FAMILY_SELECTION_VETO", "false"),
        )
    )
    
    avoid_recent_symbol = _is_trueish(commander_scanner_policy.get("avoid_recent_symbol", False))
    recent_symbol_penalty = _to_float(commander_scanner_policy.get("recent_symbol_penalty", 0.0))
    diversification_bias = _to_float(commander_scanner_policy.get("diversification_bias", 0.0))
    entry_bias_cap = _to_float(commander_scanner_policy.get("entry_bias_cap", 0.0))
    allow_same_symbol_reentry = _is_trueish(commander_scanner_policy.get("allow_same_symbol_reentry", True))
    reentry_score_gap_threshold = _to_float(commander_scanner_policy.get("reentry_score_gap_threshold", 0.0))

    persisted = state.get("persisted_state") if isinstance(state.get("persisted_state"), dict) else {}
    last_trade_symbol = _norm_symbol(persisted.get("last_trade_symbol", ""))
    positions = state.get("portfolio_snapshot", {}).get("positions", [])
    if isinstance(positions, dict):
        open_position_count = sum(1 for v in positions.values() if isinstance(v, dict) and _to_float(v.get("qty")) > 0)
    elif isinstance(positions, list):
        open_position_count = sum(1 for v in positions if isinstance(v, dict) and _to_float(v.get("qty")) > 0)
    else:
        open_position_count = 0
    is_flat = open_position_count == 0

    ranking_before_policy = [{"symbol": r.get("symbol"), "score_total": r.get("score_total")} for r in scan_results_sorted]
    
    reentry_penalty_applied = False
    reentry_penalty_value = 0.0
    diversification_applied = False
    diversification_bonus_value = 0.0
    score_adjustment_trace = []
    market_representative_guard_meta = {
        "enabled": False,
        "applied": False,
        "policy": {},
        "symbol": "",
        "penalty": 0.0,
        "score_gap": 0.0,
        "top_value_dominance": False,
        "confirmation_sources": [],
        "before_top": [],
        "after_top": [],
        "skipped_reason": "",
        "reason": "",
    }

    if entry_bias_cap > 0.0:
        for r in scan_results_sorted:
            raw_bias = _to_float(r.get("compatibility_bias", 0.0))
            if raw_bias > entry_bias_cap:
                diff = raw_bias - entry_bias_cap
                r["compatibility_bias"] = entry_bias_cap
                r["score_total"] = _to_float(r.get("score_total", 0.0)) - diff
                r["score"] = r["score_total"]
                r["entry_bias_cap_applied"] = True
                r["raw_entry_compatibility_bias"] = raw_bias
                r["effective_entry_compatibility_bias"] = entry_bias_cap
                score_adjustment_trace.append(f"entry_bias_cap applied to {r.get('symbol')}: {raw_bias:.3f} -> {entry_bias_cap:.3f}")
        scan_results_sorted.sort(key=lambda r: (float(r.get("score_total") or 0.0), float(r.get("confidence") or 0.0), -float(r.get("risk_score") or 0.0)), reverse=True)

    if len(scan_results_sorted) > 0:
        top1 = scan_results_sorted[0]
        top1_sym = _norm_symbol(top1.get("symbol"))
        top1_score = _to_float(top1.get("score_total"))
        
        if len(scan_results_sorted) > 1:
            top2 = scan_results_sorted[1]
            top2_score = _to_float(top2.get("score_total"))
            score_gap = top1_score - top2_score
            
            if avoid_recent_symbol and is_flat and last_trade_symbol == top1_sym and allow_same_symbol_reentry:
                if score_gap <= reentry_score_gap_threshold:
                    top1["score_total"] = top1_score - recent_symbol_penalty
                    top1["score"] = top1["score_total"]
                    reentry_penalty_applied = True
                    reentry_penalty_value = recent_symbol_penalty
                    score_adjustment_trace.append(f"reentry_dampener applied to {top1_sym}: -{recent_symbol_penalty:.3f} (gap {score_gap:.3f} <= {reentry_score_gap_threshold:.3f})")
            elif diversification_bias > 0.0 and score_gap <= reentry_score_gap_threshold:
                if top2.get("symbol") != last_trade_symbol:
                    top2["score_total"] = top2_score + diversification_bias
                    top2["score"] = top2["score_total"]
                    diversification_applied = True
                    diversification_bonus_value = diversification_bias
                    score_adjustment_trace.append(f"diversification_bonus applied to {top2.get('symbol')}: +{diversification_bias:.3f}")

        scan_results_sorted.sort(key=lambda r: (float(r.get("score_total") or 0.0), float(r.get("confidence") or 0.0), -float(r.get("risk_score") or 0.0)), reverse=True)

    scan_results_sorted, market_representative_guard_meta = _apply_market_representative_guard(
        scan_results_sorted,
        raw_policy=commander_scanner_policy.get("market_representative_guard"),
    )
    if bool(market_representative_guard_meta.get("applied")):
        score_adjustment_trace.append(
            "market_representative_guard "
            f"{str(market_representative_guard_meta.get('symbol') or '')} "
            f"-{float(_to_float(market_representative_guard_meta.get('penalty'))):.3f}"
        )

    blocker_family_overlay_meta = {
        "applied": False,
        "family": "",
        "penalty": 0.0,
        "candidate_count": 0,
        "top3_symbols_before": [],
        "top3_symbols_after": [],
        "alternative_symbols": [],
        "selection_vetoed": False,
        "selection_veto_reason": "",
    }
    scan_results_sorted, blocker_family_overlay_meta = _apply_blocker_family_concentration_overlay(
        scan_results_sorted,
        scan_aggressiveness=float(_to_float(pool_meta.get("scan_aggressiveness"))),
    )
    if bool(blocker_family_overlay_meta.get("applied")):
        score_adjustment_trace.append(
            "blocker_family_concentration "
            f"{str(blocker_family_overlay_meta.get('family') or '')} "
            f"-{float(_to_float(blocker_family_overlay_meta.get('penalty'))):.3f}"
        )
    if bool(blocker_family_overlay_meta.get("selection_vetoed")):
        score_adjustment_trace.append(
            f"selection_veto:{str(blocker_family_overlay_meta.get('selection_veto_reason') or '')}"
        )
        if not enforce_blocker_family_veto:
            score_adjustment_trace.append("selection_veto_observed_not_enforced")

    ranking_after_policy = [{"symbol": r.get("symbol"), "score_total": r.get("score_total")} for r in scan_results_sorted]

    selected = scan_results_sorted[0] if scan_results_sorted else None
    selection_veto_enforced = bool(blocker_family_overlay_meta.get("selection_vetoed")) and bool(enforce_blocker_family_veto)
    if selection_veto_enforced:
        selected = None
    now_epoch = _resolve_now_epoch(state)
    if isinstance(selected, dict):
        _remember_selected_symbol(state, str(selected.get("symbol") or ""), now_epoch=now_epoch, policy=policy)
    state["scan_results"] = scan_results_sorted
    state["ranked_candidates"] = [
        {
            "symbol": str(r.get("symbol") or ""),
            "asset_class_detected": str(r.get("asset_class_detected") or ""),
            "detection_source": str(r.get("detection_source") or ""),
            "detection_field": str(r.get("detection_field") or ""),
            "score_total": float(r.get("score_total") if r.get("score_total") is not None else _to_float(r.get("score"))),
            "score_breakdown": dict(r.get("score_breakdown") or {}),
            "risk_score": float(_to_float(r.get("risk_score"))),
            "confidence": float(_to_float(r.get("confidence"))),
            "bias_adjustment": float(_to_float(r.get("bias_adjustment"))),
            "bias_adjustments": list(r.get("bias_adjustments") or []),
            "bias_summary": dict(r.get("bias_summary") or {}),
            "entry_compatibility_score": float(_to_float(r.get("entry_compatibility_score"))),
            "compatibility_bias": float(_to_float(r.get("compatibility_bias"))),
            "compatibility_components": dict(r.get("compatibility_components") or {}),
            "scanner_chart_fit_score": float(_to_float(r.get("scanner_chart_fit_score"))),
            "scanner_chart_fit_authority": str(r.get("scanner_chart_fit_authority") or ""),
            "scanner_chart_fit_components": dict(r.get("scanner_chart_fit_components") or {}),
            "scanner_macro_chart_fit_score": float(_to_float(r.get("scanner_macro_chart_fit_score"), 0.5)),
            "scanner_macro_chart_fit_bias": float(_to_float(r.get("scanner_macro_chart_fit_bias"))),
            "scanner_macro_chart_fit_authority": str(r.get("scanner_macro_chart_fit_authority") or ""),
            "scanner_macro_chart_fit_components": dict(r.get("scanner_macro_chart_fit_components") or {}),
            "expected_monitor_block_reason": str(r.get("expected_monitor_block_reason") or ""),
            "dominant_block_reason": str(r.get("dominant_block_reason") or ""),
            "dominant_block_reason_ratio": float(_to_float(r.get("dominant_block_reason_ratio"))),
            "blocker_families": list(_candidate_blocker_families(r)),
            "bias_scale": float(_to_float(r.get("bias_scale"))),
            "soft_penalty": float(_to_float(r.get("soft_penalty"))),
            "compatibility_score_pre_penalty": float(_to_float(r.get("compatibility_score_pre_penalty"))),
            "compatibility_score_post_penalty": float(_to_float(r.get("compatibility_score_post_penalty"))),
            "compatibility_trace": dict(r.get("compatibility_trace") or {}),
            "pre_adjust_score_total": float(_to_float(r.get("pre_adjust_score_total"))),
            "post_adjust_score_total": float(_to_float(r.get("post_adjust_score_total") or r.get("score_total") or r.get("score"))),
            "scanner_intrinsic_control_score_total": float(
                _to_float(r.get("scanner_intrinsic_control_score_total"))
            ),
            "market_representative_guard_applied": bool(r.get("market_representative_guard_applied")),
            "market_representative_guard_penalty": float(_to_float(r.get("market_representative_guard_penalty"))),
            "market_representative_guard_reason": str(r.get("market_representative_guard_reason") or ""),
            "market_representative_confirmation_sources": list(r.get("market_representative_confirmation_sources") or []),
        }
        for r in scan_results_sorted
        if isinstance(r, dict)
    ]
    candidate_visibility_limit = _candidate_visibility_limit(commander_scanner_policy)
    visible_ranked_candidates = list(state.get("ranked_candidates") or [])[:candidate_visibility_limit]
    state["selected"] = selected
    state["top_stock"] = str(selected.get("symbol") or "") if isinstance(selected, dict) else ""
    top_score = (
        float(selected.get("score_total"))
        if isinstance(selected, dict) and selected.get("score_total") is not None
        else (
            float(selected.get("score"))
            if isinstance(selected, dict) and selected.get("score") is not None
            else None
        )
    )
    state["scanner_output"] = scan_select_value_state_scanner_output(top_score=top_score, visible_ranked_candidates=visible_ranked_candidates, ranking_before_policy=ranking_before_policy, ranking_after_policy=ranking_after_policy, practical_w=practical_w, scanner_priority=scanner_priority, playbook=playbook, scanner_bias=scanner_bias, trade_aggressiveness=trade_aggressiveness, risk_tone=risk_tone, policy=policy, policy_provenance=policy_provenance, commander_scanner_policy=commander_scanner_policy, score_adjustment_trace=score_adjustment_trace, reentry_penalty_applied=reentry_penalty_applied, reentry_penalty_value=reentry_penalty_value, diversification_applied=diversification_applied, diversification_bonus_value=diversification_bonus_value, selection_veto_enforced=selection_veto_enforced, state=state, scan_results_sorted=scan_results_sorted, selected=selected, pool_meta=pool_meta, scanner_policy_trace=scanner_policy_trace, market_representative_guard_meta=market_representative_guard_meta, blocker_family_overlay_meta=blocker_family_overlay_meta, scanner_guidance=scanner_guidance, compatibility_bias_context=compatibility_bias_context, facade=_r3_sys.modules[__name__])

    # Provide a normalized risk snapshot for Decision Node.
    if isinstance(selected, dict):
        state["risk"] = {
            "risk_score": float(selected.get("risk_score") or 0.0),
            "confidence": float(selected.get("confidence") or 0.0),
        }
    else:
        state["risk"] = {"risk_score": 0.0, "confidence": 0.0}
    fallback_reasons: List[str] = list(quote_meta.get("errors") or []) + list(order_meta.get("errors") or [])
    state["scanner_skill"] = scan_select_value_state_scanner_skill(fallback_reasons=fallback_reasons, skill_quotes=skill_quotes, skill_order_counts=skill_order_counts, skill_order_rows=skill_order_rows, quote_meta=quote_meta, order_meta=order_meta, facade=_r3_sys.modules[__name__])
    state["scanner_feature"] = {
        "used": bool(feature_map),
        "source": feature_source,
        "symbol_count": len(feature_map),
        "refresh_existing": bool(refresh_existing_features),
        "refresh_reason": str(feature_refresh_reason or ""),
        "fallback": bool(feature_errors),
        "fallback_reasons": list(feature_errors),
        "error_count": len(feature_errors),
    }
    ranking_table = _ranking_table_rows(
        scan_results_sorted,
        max_rows=max(20, candidate_visibility_limit),
    )
    selected_snapshot = _compact_selected_snapshot(selected if isinstance(selected, dict) else None)
    selected_symbol = str((selected or {}).get("symbol") or "") if isinstance(selected, dict) else ""
    selected_rank = 0
    if selected_symbol:
        ranked_symbols = [str((row or {}).get("symbol") or "") for row in list(scan_results_sorted) if isinstance(row, dict)]
        if selected_symbol in ranked_symbols:
            selected_rank = int(ranked_symbols.index(selected_symbol) + 1)
    if isinstance(selected, dict) and selected_rank > 0:
        # 2026-09-04 Scanner rank plumbing fix: propagate the same canonical
        # rank that lands in scanner.json (via selected_rank above) onto the
        # state["selected"] candidate dict itself -- `selected` and
        # `state["selected"]` are the same object (state["selected"] =
        # selected was assigned earlier, by reference), so this mutation is
        # visible to every downstream reader of state["selected"], notably
        # libs/runtime/opening_rank1_controlled_probe.py::selected_rank(),
        # which checks a "scanner_rank" key with top priority. Purely
        # additive (new dict keys only); does not touch scoring, ranking,
        # or cascade logic.
        # 2026-09-05: direct assignment, not setdefault -- this value IS the
        # canonical truth freshly computed this cycle, so it must never be
        # shadowed by a stale/contaminated "scanner_rank" the candidate dict
        # happened to already carry (e.g. reused across cycles upstream).
        selected["scanner_rank"] = int(selected_rank)
        selected["scanner_rank_source"] = "canonical"
    selected_score_total = float(_to_float((selected or {}).get("score_total") or (selected or {}).get("score"))) if isinstance(selected, dict) else 0.0
    second_score_total = float(_to_float((scan_results_sorted[1] or {}).get("score_total") or (scan_results_sorted[1] or {}).get("score"))) if len(scan_results_sorted) > 1 and isinstance(scan_results_sorted[1], dict) else 0.0
    margin_vs_second = float(selected_score_total - second_score_total) if isinstance(selected, dict) else 0.0
    selected_score_breakdown = dict((selected or {}).get("score_breakdown") or {}) if isinstance(selected, dict) else {}
    critical_positive_factors = [f"{str(k)}:{float(_to_float(v)):.3f}" for k, v in selected_score_breakdown.items() if float(_to_float(v)) > 0][:4]
    critical_negative_factors = [f"{str(k)}:{float(_to_float(v)):.3f}" for k, v in selected_score_breakdown.items() if float(_to_float(v)) < 0][:4]
    selection_summary = str((selected or {}).get("why") or "").strip() if isinstance(selected, dict) else ""
    if bool(blocker_family_overlay_meta.get("selection_vetoed")):
        selection_summary = str(blocker_family_overlay_meta.get("selection_veto_reason") or "blocker_family_concentration_veto")
    scanner_bias_summary = dict(scanner_policy_trace.get("scanner_bias_summary") or {})
    scanner_memory_bias_summary = dict(scanner_policy_trace.get("scanner_memory_bias_summary") or {})
    candidate_bias_adjustments = [
        {
            "symbol": str(row.get("symbol") or ""),
            "bias_adjustment": float(_to_float(row.get("bias_adjustment"))),
            "bias_adjustments": list(row.get("bias_adjustments") or []),
        }
        for row in list(scan_results_sorted)[:candidate_visibility_limit]
        if isinstance(row, dict) and str(row.get("symbol") or "").strip()
    ]
    candidate_memory_bias_adjustments = [
        {
            "symbol": str(row.get("symbol") or ""),
            "memory_bias_adjustment": float(_to_float(row.get("memory_bias_adjustment"))),
            "memory_bias_observed_adjustment": float(_to_float(row.get("memory_bias_observed_adjustment"))),
            "memory_bias_observation_only": bool(row.get("memory_bias_observation_only")),
            "memory_bias_source_delta": float(_to_float(row.get("memory_bias_source_delta"))),
            "memory_bias_symbol_delta": float(_to_float(row.get("memory_bias_symbol_delta"))),
            "memory_bias_adjustments": list(row.get("memory_bias_adjustments") or []),
            "memory_bias_summary": dict(row.get("memory_bias_summary") or {}),
        }
        for row in list(scan_results_sorted)[:candidate_visibility_limit]
        if isinstance(row, dict) and str(row.get("symbol") or "").strip()
    ]
    candidate_symbol_prior_adjustments = [
        {
            "symbol": str(row.get("symbol") or ""),
            "symbol_prior_adjustment": float(_to_float(row.get("symbol_prior_adjustment"))),
            "symbol_prior_reasons": list(row.get("symbol_prior_reasons") or []),
            "symbol_prior_summary": dict(row.get("symbol_prior_summary") or {}),
        }
        for row in list(scan_results_sorted)[:candidate_visibility_limit]
        if isinstance(row, dict) and str(row.get("symbol") or "").strip()
    ]
    scanner_bias_applied = any(abs(float(_to_float(row.get("bias_adjustment")))) > 1e-9 for row in list(scan_results_sorted))
    scanner_memory_bias_applied = any(
        abs(float(_to_float(row.get("memory_bias_adjustment")))) > 1e-9 for row in list(scan_results_sorted)
    )
    commander_memory_application_trace, selection_reason_with_bias = scan_select_commander_memory_application_trace_selec(selected=selected, scanner_memory_bias=scanner_memory_bias, selected_symbol=selected_symbol, candidate_memory_bias_adjustments=candidate_memory_bias_adjustments, scanner_memory_bias_summary=scanner_memory_bias_summary, scanner_memory_bias_applied=scanner_memory_bias_applied, selection_summary=selection_summary, facade=_r3_sys.modules[__name__])
    if scanner_bias_applied:
        bias_text = str(scanner_bias_summary.get("summary") or "scanner_bias").strip() or "scanner_bias"
        selection_reason_with_bias = (
            f"{selection_summary} | bias: {bias_text}" if selection_summary else f"bias applied: {bias_text}"
        )
    if scanner_memory_bias_applied:
        memory_bias_text = "memory_bias=commander"
        selection_reason_with_bias = (
            f"{selection_reason_with_bias} | {memory_bias_text}"
            if selection_reason_with_bias
            else memory_bias_text
        )
    selected_compatibility_bias = float(_to_float((selected or {}).get("compatibility_bias"))) if isinstance(selected, dict) else 0.0
    selected_expected_block = str((selected or {}).get("expected_monitor_block_reason") or "") if isinstance(selected, dict) else ""
    if abs(selected_compatibility_bias) > 1e-9:
        compatibility_text = (
            f"compatibility_bias={selected_compatibility_bias:+.3f}"
            + (f", monitor_risk={selected_expected_block}" if selected_expected_block else "")
        )
        selection_reason_with_bias = (
            f"{selection_reason_with_bias} | {compatibility_text}"
            if selection_reason_with_bias
            else compatibility_text
        )
    if score_adjustment_trace:
        selection_reason_with_bias += f" | overlay: {', '.join(score_adjustment_trace)}"
    if bool(blocker_family_overlay_meta.get("selection_vetoed")):
        veto_text = (
            (
                "selection veto enforced due to blocker family concentration"
                if selection_veto_enforced
                else "selection veto observed but not enforced due to blocker family concentration"
            )
            + (
                f" ({str(blocker_family_overlay_meta.get('family') or '')})"
                if str(blocker_family_overlay_meta.get("family") or "").strip()
                else ""
            )
        )
        selection_reason_with_bias = (
            f"{selection_reason_with_bias} | {veto_text}"
            if selection_reason_with_bias
            else veto_text
        )
    runner_up_reasons: List[Dict[str, Any]] = []
    if len(scan_results_sorted) > 1 and isinstance(selected, dict):
        selected_score = float(_to_float(selected.get("score_total") or selected.get("score")))
        selected_confidence = float(_to_float(selected.get("confidence")))
        selected_risk = float(_to_float(selected.get("risk_score")))
        for row in list(scan_results_sorted[1:3]):
            if not isinstance(row, dict):
                continue
            reasons, row_conf, row_risk, row_score = scan_select_reasons_row_conf(row=row, selected_score=selected_score, selected_confidence=selected_confidence, selected_risk=selected_risk, runner_up_reasons=runner_up_reasons, facade=_r3_sys.modules[__name__])
    state["scanner_ranking_table"] = list(ranking_table)
    state["scanner_runner_up_reasons"] = list(runner_up_reasons)
    state["scanner_selection_reason"] = scan_select_value_te_scanner_selection_reason(selected_symbol=selected_symbol, selection_summary=selection_summary, selection_reason_with_bias=selection_reason_with_bias, selected_rank=selected_rank, selected_score_total=selected_score_total, margin_vs_second=margin_vs_second, critical_positive_factors=critical_positive_factors, critical_negative_factors=critical_negative_factors, selection_veto_enforced=selection_veto_enforced, scanner_bias_applied=scanner_bias_applied, scanner_bias_summary=scanner_bias_summary, scanner_memory_bias_applied=scanner_memory_bias_applied, scanner_memory_bias=scanner_memory_bias, scanner_memory_bias_summary=scanner_memory_bias_summary, commander_memory_application_trace=commander_memory_application_trace, candidate_bias_adjustments=candidate_bias_adjustments, candidate_memory_bias_adjustments=candidate_memory_bias_adjustments, candidate_symbol_prior_adjustments=candidate_symbol_prior_adjustments, playbook=playbook, selected=selected, scanner_policy_trace=scanner_policy_trace, market_representative_guard_meta=market_representative_guard_meta, blocker_family_overlay_meta=blocker_family_overlay_meta, compatibility_bias_context=compatibility_bias_context, facade=_r3_sys.modules[__name__])
    if isinstance(state.get("scanner_output"), dict):
        state["scanner_output"]["selection_summary"] = selection_summary
        state["scanner_output"]["selected_rank"] = int(selected_rank)
        state["scanner_output"]["selected_score_total"] = float(selected_score_total)
        state["scanner_output"]["margin_vs_second"] = float(margin_vs_second)
        state["scanner_output"]["critical_positive_factors"] = list(critical_positive_factors)
        state["scanner_output"]["critical_negative_factors"] = list(critical_negative_factors)
        state["scanner_output"]["rejected_candidates"] = list(runner_up_reasons)
        state["scanner_output"]["scanner_bias_applied"] = bool(scanner_bias_applied)
        state["scanner_output"]["scanner_bias_summary"] = dict(scanner_bias_summary)
        state["scanner_output"]["scanner_memory_bias_applied"] = bool(scanner_memory_bias_applied)
        state["scanner_output"]["scanner_memory_bias"] = dict(scanner_memory_bias)
        state["scanner_output"]["scanner_memory_bias_summary"] = dict(scanner_memory_bias_summary)
        state["scanner_output"]["commander_memory_application_trace"] = dict(commander_memory_application_trace)
        state["scanner_output"]["scanner_memory_application_trace"] = dict(commander_memory_application_trace)
        state["scanner_output"]["candidate_bias_adjustments"] = list(candidate_bias_adjustments)
        state["scanner_output"]["candidate_memory_bias_adjustments"] = list(candidate_memory_bias_adjustments)
        state["scanner_output"]["candidate_symbol_prior_adjustments"] = list(candidate_symbol_prior_adjustments)
        state["scanner_output"]["selection_reason_with_bias"] = selection_reason_with_bias
        state["scanner_output"]["entry_compatibility_score"] = float(_to_float((selected or {}).get("entry_compatibility_score"))) if isinstance(selected, dict) else 0.0
        state["scanner_output"]["compatibility_bias"] = float(_to_float((selected or {}).get("compatibility_bias"))) if isinstance(selected, dict) else 0.0
        state["scanner_output"]["compatibility_components"] = dict((selected or {}).get("compatibility_components") or {}) if isinstance(selected, dict) else {}
        state["scanner_output"]["scanner_chart_fit_score"] = float(_to_float((selected or {}).get("scanner_chart_fit_score"))) if isinstance(selected, dict) else 0.0
        state["scanner_output"]["scanner_chart_fit_authority"] = str((selected or {}).get("scanner_chart_fit_authority") or "") if isinstance(selected, dict) else ""
        state["scanner_output"]["scanner_chart_fit_components"] = dict((selected or {}).get("scanner_chart_fit_components") or {}) if isinstance(selected, dict) else {}
        state["scanner_output"]["scanner_macro_chart_fit_score"] = float(_to_float((selected or {}).get("scanner_macro_chart_fit_score"), 0.5)) if isinstance(selected, dict) else 0.5
        state["scanner_output"]["scanner_macro_chart_fit_bias"] = float(_to_float((selected or {}).get("scanner_macro_chart_fit_bias"))) if isinstance(selected, dict) else 0.0
        state["scanner_output"]["scanner_macro_chart_fit_authority"] = str((selected or {}).get("scanner_macro_chart_fit_authority") or "") if isinstance(selected, dict) else ""
        state["scanner_output"]["scanner_macro_chart_fit_components"] = dict((selected or {}).get("scanner_macro_chart_fit_components") or {}) if isinstance(selected, dict) else {}
        state["scanner_output"]["expected_monitor_block_reason"] = str((selected or {}).get("expected_monitor_block_reason") or "") if isinstance(selected, dict) else ""
        state["scanner_output"]["dominant_block_reason"] = str((selected or {}).get("dominant_block_reason") or compatibility_bias_context.get("dominant_block_reason") or "")
        state["scanner_output"]["dominant_block_reason_ratio"] = float(_to_float((selected or {}).get("dominant_block_reason_ratio") or compatibility_bias_context.get("dominant_block_reason_ratio")))
        state["scanner_output"]["market_representative_guard_enabled"] = bool(market_representative_guard_meta.get("enabled"))
        state["scanner_output"]["market_representative_guard_applied"] = bool(market_representative_guard_meta.get("applied"))
        state["scanner_output"]["market_representative_guard_policy"] = dict(market_representative_guard_meta.get("policy") or {})
        state["scanner_output"]["market_representative_guard_symbol"] = str(market_representative_guard_meta.get("symbol") or "")
        state["scanner_output"]["market_representative_guard_penalty"] = float(_to_float(market_representative_guard_meta.get("penalty")))
        state["scanner_output"]["market_representative_guard_score_gap"] = float(_to_float(market_representative_guard_meta.get("score_gap")))
        state["scanner_output"]["market_representative_guard_reason"] = str(
            market_representative_guard_meta.get("reason")
            or market_representative_guard_meta.get("skipped_reason")
            or ""
        )
        state["scanner_output"]["market_representative_guard_top_value_dominance"] = bool(market_representative_guard_meta.get("top_value_dominance"))
        state["scanner_output"]["market_representative_guard_confirmation_sources"] = list(market_representative_guard_meta.get("confirmation_sources") or [])
        state["scanner_output"]["market_representative_guard_before_top"] = list(market_representative_guard_meta.get("before_top") or [])
        state["scanner_output"]["market_representative_guard_after_top"] = list(market_representative_guard_meta.get("after_top") or [])
        state["scanner_output"]["blocker_family_concentration_applied"] = bool(blocker_family_overlay_meta.get("applied"))
        state["scanner_output"]["blocker_family_concentration_family"] = str(blocker_family_overlay_meta.get("family") or "")
        state["scanner_output"]["blocker_family_concentration_penalty"] = float(_to_float(blocker_family_overlay_meta.get("penalty")))
        state["scanner_output"]["blocker_family_concentration_top3_before"] = list(blocker_family_overlay_meta.get("top3_symbols_before") or [])
        state["scanner_output"]["blocker_family_concentration_top3_after"] = list(blocker_family_overlay_meta.get("top3_symbols_after") or [])
        state["scanner_output"]["blocker_family_concentration_alternative_symbols"] = list(blocker_family_overlay_meta.get("alternative_symbols") or [])
        state["scanner_output"]["selection_vetoed"] = bool(blocker_family_overlay_meta.get("selection_vetoed"))
        state["scanner_output"]["selection_veto_enforced"] = bool(selection_veto_enforced)
        state["scanner_output"]["selection_veto_reason"] = str(blocker_family_overlay_meta.get("selection_veto_reason") or "")
        state["scanner_output"]["bias_scale"] = float(_to_float((selected or {}).get("bias_scale") or compatibility_bias_context.get("bias_scale")))
        state["scanner_output"]["soft_penalty"] = float(_to_float((selected or {}).get("soft_penalty")))
        state["scanner_output"]["compatibility_score_pre_penalty"] = float(_to_float((selected or {}).get("compatibility_score_pre_penalty")))
        state["scanner_output"]["compatibility_score_post_penalty"] = float(_to_float((selected or {}).get("compatibility_score_post_penalty")))
        state["scanner_output"]["compatibility_trace"] = dict((selected or {}).get("compatibility_trace") or {}) if isinstance(selected, dict) else {}
        state["scanner_output"]["pre_adjust_score_total"] = float(_to_float((selected or {}).get("pre_adjust_score_total"))) if isinstance(selected, dict) else 0.0
        state["scanner_output"]["post_adjust_score_total"] = float(_to_float((selected or {}).get("post_adjust_score_total") or (selected or {}).get("score_total") or (selected or {}).get("score"))) if isinstance(selected, dict) else 0.0
        state["scanner_output"]["quote_data_diagnostic"] = dict(state.get("scanner_quote_diagnostic") or {})
        state["scanner_output"]["selected_asset_class_detected"] = str((selected or {}).get("asset_class_detected") or "") if isinstance(selected, dict) else ""
        state["scanner_output"]["selected_asset_detection_source"] = str((selected or {}).get("detection_source") or "") if isinstance(selected, dict) else ""
        state["scanner_output"]["selected_asset_detection_field"] = str((selected or {}).get("detection_field") or "") if isinstance(selected, dict) else ""
    state["scanner_margin_vs_second"] = float(margin_vs_second)
    _emit_scanner_event(
        state,
        name="candidate_pool_snapshot",
        payload={
            "candidate_source": str(pool_meta.get("candidate_source") or ""),
            "candidate_pool_before_filter": int(pool_meta.get("candidate_pool_before_filter") or 0),
            "candidate_pool_after_filter": int(pool_meta.get("candidate_pool_after_filter") or len(scan_results_sorted)),
            "asset_universe_policy": str(pool_meta.get("asset_universe_policy") or ""),
            "asset_universe_policy_source": str(pool_meta.get("asset_universe_policy_source") or ""),
            "excluded_candidate_count_by_asset_policy": int(pool_meta.get("asset_policy_excluded_count") or 0),
            "excluded_symbols_by_asset_policy": list(pool_meta.get("asset_policy_excluded_symbols") or []),
            "asset_detection_stats": dict(pool_meta.get("asset_detection_stats") or {}),
            "unknown_asset_candidate_count": int(pool_meta.get("unknown_asset_candidate_count") or 0),
            "total_candidates_before_filter": int(pool_meta.get("total_candidates_before_filter") or 0),
            "total_candidates_after_filter": int(pool_meta.get("total_candidates_after_filter") or 0),
            "theme_filter_applied": bool(pool_meta.get("theme_filter_applied")),
            "market_native_bypass_count": int(pool_meta.get("market_native_bypass_count") or 0),
            "market_native_bypass_symbols": list(pool_meta.get("market_native_bypass_symbols") or []),
            "avoid_filter_applied": bool(pool_meta.get("avoid_filter_applied")),
            "avoid_filter_reason": str(pool_meta.get("avoid_filter_reason") or ""),
            "avoid_filter_fallback_used": bool(pool_meta.get("avoid_filter_fallback_used")),
            "source_mix": dict(pool_meta.get("pool_source_mix") or {}),
            "scanner_source_policy": dict(pool_meta.get("scanner_source_policy") or {}),
            "candidate_symbols": [str((row or {}).get("symbol") or "") for row in list(scan_results_sorted or [])[:10] if isinstance(row, dict)],
            "fallback_reason": str(pool_meta.get("fallback_reason") or ""),
            "backfill_used": bool(pool_meta.get("backfill_used")),
            "backfill_count": int(pool_meta.get("backfill_count") or 0),
            "scan_aggressiveness": float(_to_float(pool_meta.get("scan_aggressiveness"))),
            "strict_mode_relaxed_by_scan_aggressiveness": bool(pool_meta.get("strict_mode_relaxed_by_scan_aggressiveness")),
            "aggressive_source_expansion_used": bool(pool_meta.get("aggressive_source_expansion_used")),
            "aggressive_source_expansion_sources": list(pool_meta.get("aggressive_source_expansion_sources") or []),
            "market_representative_guard_applied": bool(market_representative_guard_meta.get("applied")),
            "market_representative_guard_symbol": str(market_representative_guard_meta.get("symbol") or ""),
            "market_representative_guard_reason": str(
                market_representative_guard_meta.get("reason")
                or market_representative_guard_meta.get("skipped_reason")
                or ""
            ),
            "blocker_family_concentration_applied": bool(blocker_family_overlay_meta.get("applied")),
            "blocker_family_concentration_family": str(blocker_family_overlay_meta.get("family") or ""),
            "selection_vetoed": bool(blocker_family_overlay_meta.get("selection_vetoed")),
            "selection_veto_enforced": bool(selection_veto_enforced),
            "selection_veto_reason": str(blocker_family_overlay_meta.get("selection_veto_reason") or ""),
        },
    )
    candidate_ranking_table_payload = _build_candidate_ranking_table_payload(
        ranking_table,
        full_strategist_control_eligibility=full_strategist_control_eligibility,
    )
    state["scanner_candidate_ranking_table"] = dict(candidate_ranking_table_payload)
    state["scanner_output"]["scanner_intrinsic_control_top10"] = list(
        candidate_ranking_table_payload.get("scanner_intrinsic_control_top10") or []
    )
    state["scanner_output"]["scanner_intrinsic_control_top20"] = list(
        candidate_ranking_table_payload.get("scanner_intrinsic_control_top20") or []
    )
    state["scanner_output"]["pre_strategist_full_universe_snapshot"] = dict(
        candidate_ranking_table_payload.get("pre_strategist_full_universe_snapshot") or {}
    )
    _emit_scanner_event(
        state,
        name="candidate_ranking_table",
        payload=candidate_ranking_table_payload,
        symbol=str((selected or {}).get("symbol") or ""),
    )
    try:
        from libs.runtime.q9_decision_snapshots import capture_scanner_decision_snapshot

        state["q9_scanner_snapshot_result"] = capture_scanner_decision_snapshot(state)
    except Exception as exc:
        state["q9_scanner_snapshot_result"] = {
            "status": "error",
            "reason": f"{type(exc).__name__}: {exc}"[:300],
        }
    candidate_selection_reason_payload = scan_select_candidate_selection_reason_payload(selected_symbol=selected_symbol, selected_rank=selected_rank, selected_score_total=selected_score_total, margin_vs_second=margin_vs_second, critical_positive_factors=critical_positive_factors, critical_negative_factors=critical_negative_factors, selection_summary=selection_summary, scanner_policy_trace=scanner_policy_trace, playbook=playbook, compatibility_bias_context=compatibility_bias_context, market_representative_guard_meta=market_representative_guard_meta, blocker_family_overlay_meta=blocker_family_overlay_meta, selection_veto_enforced=selection_veto_enforced, scanner_bias_applied=scanner_bias_applied, scanner_memory_bias_applied=scanner_memory_bias_applied, scanner_memory_bias=scanner_memory_bias, commander_memory_application_trace=commander_memory_application_trace, candidate_bias_adjustments=candidate_bias_adjustments, candidate_memory_bias_adjustments=candidate_memory_bias_adjustments, candidate_symbol_prior_adjustments=candidate_symbol_prior_adjustments, selection_reason_with_bias=selection_reason_with_bias, runner_up_reasons=runner_up_reasons, selected=selected, facade=_r3_sys.modules[__name__])[0]
    state["scanner_candidate_selection_reason"] = dict(candidate_selection_reason_payload)
    _emit_scanner_event(
        state,
        name="candidate_selection_reason",
        payload=candidate_selection_reason_payload,
        symbol=str((selected or {}).get("symbol") or ""),
    )
    _emit_scanner_event(
        state,
        name="selection_output",
        payload={
            "selected_symbol": state.get("top_stock") or None,
            "scanner_selected_symbol": selected_symbol,
            "scanner_rank": int(selected_rank),
            "scanner_score_total": float(selected_score_total),
            "scanner_score_breakdown": dict((selected or {}).get("score_breakdown") or {}) if isinstance(selected, dict) else {},
            "scanner_top_candidates": ranking_table[:3],
            "candidate_count": int(len(scan_results_sorted)),
            "selected_asset_class_detected": str((selected or {}).get("asset_class_detected") or "") if isinstance(selected, dict) else "",
            "selected_asset_detection_source": str((selected or {}).get("detection_source") or "") if isinstance(selected, dict) else "",
            "ranking_top_n": ranking_table,
            "selected_candidate": selected_snapshot,
        },
        symbol=str((selected or {}).get("symbol") or ""),
    )

    _log_scanner_summary(
        state,
        {
            "candidate_source": str(pool_meta.get("candidate_source") or ""),
            "candidate_pool_before_filter": int(pool_meta.get("candidate_pool_before_filter") or 0),
            "candidate_pool_after_filter": int(pool_meta.get("candidate_pool_after_filter") or len(scan_results_sorted)),
            "asset_universe_policy": str(pool_meta.get("asset_universe_policy") or ""),
            "asset_universe_policy_source": str(pool_meta.get("asset_universe_policy_source") or ""),
            "excluded_candidate_count_by_asset_policy": int(pool_meta.get("asset_policy_excluded_count") or 0),
            "asset_detection_stats": dict(pool_meta.get("asset_detection_stats") or {}),
            "unknown_asset_candidate_count": int(pool_meta.get("unknown_asset_candidate_count") or 0),
            "total_candidates_before_filter": int(pool_meta.get("total_candidates_before_filter") or 0),
            "total_candidates_after_filter": int(pool_meta.get("total_candidates_after_filter") or 0),
            "theme_filter_applied": bool(pool_meta.get("theme_filter_applied")),
            "fallback_reason": str(pool_meta.get("fallback_reason") or ""),
            "blocked_static_fallback": bool(pool_meta.get("blocked_static_fallback")),
            "strict_kiwoom_only": bool(pool_meta.get("strict_kiwoom_only")),
            "backfill_used": bool(pool_meta.get("backfill_used")),
            "backfill_count": int(pool_meta.get("backfill_count") or 0),
            "scan_aggressiveness": float(_to_float(pool_meta.get("scan_aggressiveness"))),
            "strict_mode_relaxed_by_scan_aggressiveness": bool(pool_meta.get("strict_mode_relaxed_by_scan_aggressiveness")),
            "aggressive_source_expansion_used": bool(pool_meta.get("aggressive_source_expansion_used")),
            "aggressive_source_expansion_sources": list(pool_meta.get("aggressive_source_expansion_sources") or []),
            "top_stock": state.get("top_stock"),
            "top_score": top_score,
            "scanner_selected_symbol": selected_symbol,
            "scanner_rank": int(selected_rank),
            "scanner_score_total": float(selected_score_total),
            "scanner_score_breakdown": dict((selected or {}).get("score_breakdown") or {}) if isinstance(selected, dict) else {},
            "scanner_top_candidates": ranking_table[:3],
            "top_ranked_symbols": [str(x.get("symbol") or "") for x in visible_ranked_candidates],
            "strategist_scanner_priority": list(scanner_priority),
            "strategist_scanner_source_policy": dict(pool_meta.get("scanner_source_policy") or {}),
            "condition_search_status": str(pool_meta.get("condition_search_status") or ""),
            "condition_search_source": str(pool_meta.get("condition_search_source") or ""),
            "condition_search_reason": str(pool_meta.get("condition_search_reason") or ""),
            "strategist_playbook": playbook or "",
            "strategist_scanner_bias": scanner_bias or "",
            "strategist_avoid_themes": list(pool_meta.get("avoid_themes") or []),
            "strategist_trade_aggressiveness": trade_aggressiveness or "",
            "strategist_risk_tone": risk_tone or "",
            "recent_scanner_selected_count": int(len(_scanner_recent_selection_history(state))),
            "scanner_bias_applied": bool(scanner_bias_applied),
            "scanner_bias_summary": dict(scanner_bias_summary),
            "scanner_memory_bias_applied": bool(scanner_memory_bias_applied),
            "scanner_memory_bias_summary": dict(scanner_memory_bias_summary),
            "market_representative_guard_applied": bool(market_representative_guard_meta.get("applied")),
            "market_representative_guard_symbol": str(market_representative_guard_meta.get("symbol") or ""),
            "market_representative_guard_reason": str(
                market_representative_guard_meta.get("reason")
                or market_representative_guard_meta.get("skipped_reason")
                or ""
            ),
            "blocker_family_concentration_applied": bool(blocker_family_overlay_meta.get("applied")),
            "blocker_family_concentration_family": str(blocker_family_overlay_meta.get("family") or ""),
            "selection_vetoed": bool(blocker_family_overlay_meta.get("selection_vetoed")),
            "selection_veto_enforced": bool(selection_veto_enforced),
            "selection_veto_reason": str(blocker_family_overlay_meta.get("selection_veto_reason") or ""),
        },
    )

    top_candidates_summary: List[Dict[str, Any]] = []
    for row in list(state.get("ranked_candidates") or [])[:3]:
        if not isinstance(row, dict):
            continue
        top_candidates_summary.append(
            {
                "symbol": str(row.get("symbol") or ""),
                "score_total": float(_to_float(row.get("score_total"))),
                "risk_score": float(_to_float(row.get("risk_score"))),
            }
        )
    append_decision_trace(
        state,
        agent="scanner",
        event="candidate_selection",
        payload={
            "playbook": playbook or "",
            "scanner_priority": list(scanner_priority),
            "scanner_bias_applied": bool(scanner_bias_applied),
            "scanner_bias_summary": dict(scanner_bias_summary),
            "scanner_memory_bias_applied": bool(scanner_memory_bias_applied),
            "scanner_memory_bias": dict(scanner_memory_bias),
            "scanner_memory_bias_summary": dict(scanner_memory_bias_summary),
            "commander_memory_application_trace": dict(commander_memory_application_trace),
            "scanner_memory_application_trace": dict(commander_memory_application_trace),
            "candidate_bias_adjustments": list(candidate_bias_adjustments),
            "candidate_memory_bias_adjustments": list(candidate_memory_bias_adjustments),
            "selection_reason_with_bias": selection_reason_with_bias,
            "candidate_source": str(pool_meta.get("candidate_source") or ""),
            "asset_universe_policy": str(pool_meta.get("asset_universe_policy") or ""),
            "excluded_candidate_count_by_asset_policy": int(pool_meta.get("asset_policy_excluded_count") or 0),
            "asset_detection_stats": dict(pool_meta.get("asset_detection_stats") or {}),
            "unknown_asset_candidate_count": int(pool_meta.get("unknown_asset_candidate_count") or 0),
            "kiwoom_pool_source_mix": dict(pool_meta.get("pool_source_mix") or {}),
            "condition_search_status": str(pool_meta.get("condition_search_status") or ""),
            "condition_search_source": str(pool_meta.get("condition_search_source") or ""),
            "condition_search_reason": str(pool_meta.get("condition_search_reason") or ""),
            "scanner_source_policy": dict(pool_meta.get("scanner_source_policy") or {}),
            "candidate_pool_size": int(len(scan_results_sorted)),
            "recent_scanner_selected_count": int(len(_scanner_recent_selection_history(state))),
            "top_candidates": top_candidates_summary,
            "selected_symbol": state.get("top_stock") or None,
            "aggressive_source_expansion_used": bool(pool_meta.get("aggressive_source_expansion_used")),
            "aggressive_source_expansion_sources": list(pool_meta.get("aggressive_source_expansion_sources") or []),
            "market_representative_guard_applied": bool(market_representative_guard_meta.get("applied")),
            "market_representative_guard_symbol": str(market_representative_guard_meta.get("symbol") or ""),
            "market_representative_guard_reason": str(
                market_representative_guard_meta.get("reason")
                or market_representative_guard_meta.get("skipped_reason")
                or ""
            ),
            "blocker_family_concentration_applied": bool(blocker_family_overlay_meta.get("applied")),
            "blocker_family_concentration_family": str(blocker_family_overlay_meta.get("family") or ""),
            "selection_vetoed": bool(blocker_family_overlay_meta.get("selection_vetoed")),
            "selection_veto_enforced": bool(selection_veto_enforced),
            "selection_veto_reason": str(blocker_family_overlay_meta.get("selection_veto_reason") or ""),
            "score_breakdown_summary": (
                dict(selected.get("score_breakdown") or {})
                if isinstance(selected, dict)
                else {}
            ),
            "selected_candidate": _compact_selected_snapshot(selected if isinstance(selected, dict) else None),
        },
    )
    try:
        record_decision_bridge(
            run_id=run_id,
            agent="scanner",
            stage="decision_bridge",
            raw_input={
                "candidate_pool_size": int(len(scan_results_sorted)),
                "candidate_source": str(pool_meta.get("candidate_source") or ""),
                "theme_filter_applied": bool(pool_meta.get("theme_filter_applied")),
                "scanner_source_policy": dict(pool_meta.get("scanner_source_policy") or {}),
                "aggressive_source_expansion_used": bool(pool_meta.get("aggressive_source_expansion_used")),
                "aggressive_source_expansion_sources": list(pool_meta.get("aggressive_source_expansion_sources") or []),
            },
            parsed_output={
                "selected_symbol": state.get("top_stock") or None,
                "top_score": float(_to_float(top_score) if top_score is not None else 0.0),
                "ranked_candidates": visible_ranked_candidates,
                "selected_candidate": _compact_selected_snapshot(selected if isinstance(selected, dict) else None),
            },
            decision_link={
                "decision_chain": {
                    "theme": str((state.get("themes") or [""])[0] if isinstance(state.get("themes"), list) and state.get("themes") else ""),
                    "scanner_selected": state.get("top_stock") or None,
                }
            },
        )
    except Exception:
        pass
    try:
        write_scanner_artifact(state)
    except Exception:
        pass

    return state
