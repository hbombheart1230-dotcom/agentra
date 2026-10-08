from __future__ import annotations

import html
import re
from typing import Any, Dict, List, Mapping

from libs.reporting.reasoning_trace import (
    build_reasoning_provenance,
    build_reasoning_trace_from_summaries,
    normalize_reasoning_provenance_aliases,
    normalize_reasoning_trace_aliases,
)
from libs.reporting.strategy_read_model import (
    build_news_symbol_linkage_view,
    build_strategist_feedback_input_view,
)
from libs.reporting.trade_read_model import normalize_trade_report_section
from libs.reporting.trade_report_ai import resolve_shared_trade_facts
from libs.reporting.trade_report_common import (
    clip_text as clip,
    format_exit_label,
    format_pct,
    format_ratio_pct,
    is_empty_placeholder as _is_empty_placeholder,
    list_text as _list_text,
    merge_missing_values as _merge_missing_values,
    safe_float,
    safe_int,
    utc_now_iso,
)
from libs.reporting.trade_scanner_fallback_anchor import (
    reanchor_scanner_selection_for_monitor_fallback,
)
from libs.reporting.trade_fallback_text import (
    EXECUTION_OUTCOME_NOT_CAPTURED,
    LIFECYCLE_CONCLUSION_NOT_CAPTURED,
    REPORTER_LINKAGE_NOT_CAPTURED,
    lifecycle_conclusion_summary_is_placeholder,
)
from libs.reporting.trade_execution_outcome_text import (
    build_execution_outcome_fallback_from_lifecycle,
    execution_outcome_summary_is_placeholder,
)
from libs.reporting.trade_reporter_status_text import normalize_reporter_status_human
from libs.reporting.trade_story_evidence import (
    derive_evidence_provenance as _derive_evidence_provenance_impl,
    has_substantive_exit_evidence as _has_substantive_exit_evidence_impl,
    set_or_replace_placeholder as _set_or_replace_placeholder_impl,
)
from libs.reporting.trade_story_pipeline_evidence_hydration import (
    enrich_scanner_reason_from_evidence as _enrich_scanner_reason_from_evidence_impl,
    enrich_filters_from_evidence as _enrich_filters_from_evidence_impl,
    hydrate_canonical_agent_artifacts as _hydrate_canonical_agent_artifacts_impl,
    resolve_selection_monitor_artifact as _resolve_selection_monitor_artifact_impl,
    safe_read_json_file as _safe_read_json_file_impl,
)
from libs.reporting.trade_story_pipeline_human_payloads import (
    build_scanner_reason_human as _build_scanner_reason_human_impl,
    build_monitor_reason_human as _build_monitor_reason_human_impl,
    build_market_context_human as _build_market_context_human_impl,
    build_execution_outcome_human as _build_execution_outcome_human_impl,
    build_monitor_blocker_trace as _build_monitor_blocker_trace_impl,
    build_monitor_stop_policy_trace as _build_monitor_stop_policy_trace_impl,
    normalize_stop_thresholds as _normalize_stop_thresholds_impl,
    resolve_adaptive_stop_loss_pct as _resolve_adaptive_stop_loss_pct_impl,
    resolve_strategist_adaptive_exit as _resolve_strategist_adaptive_exit_impl,
)
from libs.reporting.trade_story_pipeline_story_assembly import (
    build_trade_story_input as _build_trade_story_input_impl,
    build_report_section_seeds as _build_report_section_seeds_impl,
    build_lifecycle_bundle as _build_lifecycle_bundle_impl,
    build_timeline as _build_timeline_impl,
    collect_story_warnings as _collect_story_warnings_impl,
    compact_canonical_monitor as _compact_canonical_monitor_impl,
    normalize_trade_lifecycle_for_story_input as _normalize_trade_lifecycle_for_story_input_impl,
)
from libs.core.symbols import normalize_symbol
from libs.reporting.trade_story_pipeline_news import (
    _headline_text,
    _clean_news_fragment,
    _news_item_field,
    _news_sample_parts,
    _norm_symbol_text,
    _symbol_name_from_text,
    _sample_title_directly_matches_symbol,
    _format_symbol_news_headline,
    _collect_symbol_headlines_from_ranked_rows,
    _headline_matches_symbol,
    _collect_top_headlines,
    _title_prefixed_symbol,
    _list_text_for_symbol,
    _optional_float,
    _build_news_scanner_contribution_trace,
    _attach_news_scanner_contribution,
)
from libs.reporting.trade_story_pipeline_scanner import (
    _korea_indices_bullet,
    _top_numeric_drivers,
    _scanner_chart_fit_payload,
    _scanner_macro_chart_fit_payload,
    _candidate_sources_from_score_breakdown,
    _selection_basis_from_scores,
    _scanner_candidate_row_from_evidence,
    _build_scanner_selection_trace,
    _scanner_chart_fit_from_scanner_evidence,
    _scanner_macro_chart_fit_from_scanner_evidence,
    _normalized_feature_coverage_from_scanner_evidence,
)
from libs.reporting.trade_story_pipeline_provenance import (
    _source_confidence_label,
    _is_present,
    compute_evidence_completeness,
    _safe_path_text,
    _safe_ref_map,
    _resolve_commander_source_ref,
    _commander_reasoning_flag,
    _commander_reasoning_source_priority,
    build_commander_evidence,
    _section_source_entry,
    build_section_provenance,
    _section_seed_provenance_entry,
    build_report_section_provenance_seeds,
)


def _has_substantive_exit_evidence(exit_payload: Any) -> bool:
    return _has_substantive_exit_evidence_impl(exit_payload)


def _set_or_replace_placeholder(target: Dict[str, Any], key: str, value: Any) -> None:
    _set_or_replace_placeholder_impl(target, key, value)


def _derive_evidence_provenance(bundle_out: Dict[str, Any]) -> Dict[str, Any]:
    return _derive_evidence_provenance_impl(bundle_out)


def _safe_read_json_file(path_value: Any) -> Dict[str, Any]:
    return _safe_read_json_file_impl(path_value)


def _hydrate_canonical_agent_artifacts(
    bundle_out: Dict[str, Any],
    canonical_agent_artifacts: Dict[str, Any] | None,
) -> Dict[str, Any]:
    return _hydrate_canonical_agent_artifacts_impl(
        bundle_out,
        canonical_agent_artifacts,
        read_json_file=_safe_read_json_file,
    )


def _resolve_selection_monitor_artifact(
    bundle_out: Dict[str, Any],
    canonical_agent_artifacts: Dict[str, Any] | None,
) -> Dict[str, Any]:
    return _resolve_selection_monitor_artifact_impl(
        bundle_out,
        canonical_agent_artifacts,
        read_json_file=_safe_read_json_file,
    )


def _raw_strategist_evidence(bundle_out: Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(bundle_out.get("strategist_evidence"), dict):
        return dict(bundle_out.get("strategist_evidence") or {})
    evidence = bundle_out.get("evidence") if isinstance(bundle_out.get("evidence"), dict) else {}
    if isinstance(evidence.get("strategist"), dict):
        return dict(evidence.get("strategist") or {})
    return {}


def _strategist_trace_source(
    canonical_strategist: Dict[str, Any],
    raw_strategist_evidence: Dict[str, Any],
) -> Dict[str, Any]:
    source = dict(canonical_strategist or {})
    raw = raw_strategist_evidence if isinstance(raw_strategist_evidence, dict) else {}
    # Raw evidence carries the structured news rows. Prefer those over stale
    # flattened market_context headlines when rebuilding reports.
    if raw.get("news_evidence_ranked") is not None:
        source["news_evidence_ranked"] = raw.get("news_evidence_ranked")
    if raw.get("market_context_snapshots") is not None and source.get("market_context_snapshots") is None:
        source["market_context_snapshots"] = raw.get("market_context_snapshots")
    return source


def _build_strategist_evidence_trace(
    strategist: Dict[str, Any],
    *,
    selected_symbol: str = "",
    fallback_market_titles: Any = None,
    fallback_candidate_titles: Any = None,
) -> Dict[str, Any]:
    data = strategist if isinstance(strategist, dict) else {}
    news_ranked_raw = data.get("news_evidence_ranked")
    news_ranked = news_ranked_raw if isinstance(news_ranked_raw, dict) else {}
    if not news_ranked and isinstance(news_ranked_raw, list):
        for event in news_ranked_raw:
            payload = event.get("payload") if isinstance(event, dict) else {}
            if isinstance(payload, dict) and (
                payload.get("candidate_news_ranked") is not None
                or payload.get("market_news_ranked") is not None
            ):
                news_ranked = dict(payload)
                break
    global_signal = data.get("global_sentiment_signal") if isinstance(data.get("global_sentiment_signal"), dict) else {}
    fear_index = data.get("fear_index") if isinstance(data.get("fear_index"), dict) else {}
    if not fear_index and isinstance(global_signal.get("fear_index"), dict):
        fear_index = dict(global_signal.get("fear_index") or {})
    market_rows = list(news_ranked.get("market_news_ranked") or [])
    candidate_rows = list(news_ranked.get("candidate_news_ranked") or [])
    market_headlines = _collect_top_headlines(market_rows, limit=3)
    symbol_headlines = _collect_symbol_headlines_from_ranked_rows(
        candidate_rows,
        symbol=selected_symbol,
        limit=3,
    ) or _collect_top_headlines(candidate_rows, limit=3, symbol=selected_symbol)
    if not market_headlines:
        market_headlines = _list_text(fallback_market_titles, limit=3, max_len=180)
    if not symbol_headlines:
        symbol_headlines = _list_text_for_symbol(
            fallback_candidate_titles,
            symbol=selected_symbol,
            limit=3,
            max_len=180,
        )
    candidate_hints = _list_text(
        data.get("candidate_symbols_hint"),
        limit=8,
        max_len=24,
    )
    key_events = _list_text(
        data.get("key_events") if data.get("key_events") is not None else data.get("key_events_hint"),
        limit=6,
        max_len=180,
    )
    return {
        "candidate_hints": candidate_hints,
        "news_query_targets": _list_text(
            data.get("news_query_targets")
            if data.get("news_query_targets") is not None
            else news_ranked.get("news_query_targets"),
            limit=8,
            max_len=80,
        ),
        "market_headlines": market_headlines,
        "symbol_headlines": symbol_headlines,
        "global_sentiment_signal": dict(global_signal or {}),
        "korea_indices": dict(global_signal.get("korea_indices") or {}) if isinstance(global_signal.get("korea_indices"), dict) else {},
        "fear_index": dict(fear_index or {}),
        "key_events": key_events,
    }


def _normalize_stop_thresholds(thresholds: Dict[str, Any]) -> Dict[str, Any]:
    return _normalize_stop_thresholds_impl(thresholds)


def _resolve_strategist_adaptive_exit(monitor: Dict[str, Any]) -> Dict[str, Any]:
    return _resolve_strategist_adaptive_exit_impl(monitor)


def _resolve_adaptive_stop_loss_pct(monitor: Dict[str, Any], thresholds: Dict[str, Any]) -> Any:
    return _resolve_adaptive_stop_loss_pct_impl(monitor, thresholds)


def _build_monitor_stop_policy_trace(monitor: Dict[str, Any], thresholds: Dict[str, Any]) -> Dict[str, Any]:
    return _build_monitor_stop_policy_trace_impl(monitor, thresholds)


def _build_monitor_blocker_trace(monitor: Dict[str, Any]) -> Dict[str, Any]:
    return _build_monitor_blocker_trace_impl(monitor)


def _story_assembly_deps() -> Dict[str, Any]:
    return {
        "EXECUTION_OUTCOME_NOT_CAPTURED": EXECUTION_OUTCOME_NOT_CAPTURED,
        "LIFECYCLE_CONCLUSION_NOT_CAPTURED": LIFECYCLE_CONCLUSION_NOT_CAPTURED,
        "REPORTER_LINKAGE_NOT_CAPTURED": REPORTER_LINKAGE_NOT_CAPTURED,
        "_attach_news_scanner_contribution": _attach_news_scanner_contribution,
        "_build_monitor_blocker_trace": _build_monitor_blocker_trace,
        "_build_monitor_stop_policy_trace": _build_monitor_stop_policy_trace,
        "_build_scanner_selection_trace": _build_scanner_selection_trace,
        "_build_strategist_evidence_trace": _build_strategist_evidence_trace,
        "_commander_reasoning_flag": _commander_reasoning_flag,
        "_commander_reasoning_source_priority": _commander_reasoning_source_priority,
        "_compact_canonical_monitor": _compact_canonical_monitor,
        "_derive_evidence_provenance": _derive_evidence_provenance,
        "_has_substantive_exit_evidence": _has_substantive_exit_evidence,
        "_hydrate_canonical_agent_artifacts": _hydrate_canonical_agent_artifacts,
        "_is_empty_placeholder": _is_empty_placeholder,
        "_list_text": _list_text,
        "_raw_strategist_evidence": _raw_strategist_evidence,
        "_resolve_commander_source_ref": _resolve_commander_source_ref,
        "_resolve_selection_monitor_artifact": _resolve_selection_monitor_artifact,
        "_safe_ref_map": _safe_ref_map,
        "_set_or_replace_placeholder": _set_or_replace_placeholder,
        "_strategist_trace_source": _strategist_trace_source,
        "build_execution_outcome_fallback_from_lifecycle": build_execution_outcome_fallback_from_lifecycle,
        "build_news_symbol_linkage_view": build_news_symbol_linkage_view,
        "build_operator_conclusion_human": build_operator_conclusion_human,
        "build_reasoning_provenance": build_reasoning_provenance,
        "build_reasoning_trace_from_summaries": build_reasoning_trace_from_summaries,
        "build_report_section_provenance_seeds": build_report_section_provenance_seeds,
        "build_report_section_seeds": build_report_section_seeds,
        "build_section_provenance": build_section_provenance,
        "build_strategist_feedback_input_view": build_strategist_feedback_input_view,
        "compute_evidence_completeness": compute_evidence_completeness,
        "enrich_filters_from_evidence": enrich_filters_from_evidence,
        "enrich_scanner_reason_from_evidence": enrich_scanner_reason_from_evidence,
        "execution_outcome_summary_is_placeholder": execution_outcome_summary_is_placeholder,
        "lifecycle_conclusion_summary_is_placeholder": lifecycle_conclusion_summary_is_placeholder,
        "normalize_reasoning_provenance_aliases": normalize_reasoning_provenance_aliases,
        "normalize_reasoning_trace_aliases": normalize_reasoning_trace_aliases,
        "normalize_reporter_status_human": normalize_reporter_status_human,
        "normalize_trade_report_section": normalize_trade_report_section,
        "reanchor_scanner_selection_for_monitor_fallback": reanchor_scanner_selection_for_monitor_fallback,
        "resolve_shared_trade_facts": resolve_shared_trade_facts,
    }

def build_lifecycle_bundle(
    *,
    day: str,
    trade_id: str,
    run_id: str,
    symbol: str,
    lifecycle: Dict[str, Any],
    strategist_summary: Dict[str, Any],
    scanner_summary: Dict[str, Any],
    monitor_summary: Dict[str, Any],
    commander_summary: Dict[str, Any],
    story_input: Dict[str, Any],
    diagnostics: Dict[str, Any],
    canonical_refs: Dict[str, Any],
    llm_refs: Dict[str, Any],
    artifact_links: Dict[str, Any],
) -> Dict[str, Any]:
    return _build_lifecycle_bundle_impl(
        day=day, trade_id=trade_id, run_id=run_id, symbol=symbol,
        lifecycle=lifecycle, strategist_summary=strategist_summary,
        scanner_summary=scanner_summary, monitor_summary=monitor_summary,
        commander_summary=commander_summary, story_input=story_input,
        diagnostics=diagnostics, canonical_refs=canonical_refs,
        llm_refs=llm_refs, artifact_links=artifact_links,
        deps=_story_assembly_deps(),
    )

def build_report_section_seeds(
    *,
    market_context_human: Dict[str, Any],
    scanner_reason_human: Dict[str, Any],
    filters_human: Dict[str, Any],
    monitor_reason_human: Dict[str, Any] | None = None,
    execution_outcome_human: Dict[str, Any] | None = None,
    guard_reason_human: Dict[str, Any] | None = None,
    reporter_status_human: Dict[str, Any] | None = None,
    operator_conclusion_human: Dict[str, Any] | None = None,
) -> Dict[str, Dict[str, Any]]:
    return _build_report_section_seeds_impl(
        market_context_human=market_context_human,
        scanner_reason_human=scanner_reason_human,
        filters_human=filters_human,
        monitor_reason_human=monitor_reason_human,
        execution_outcome_human=execution_outcome_human,
        guard_reason_human=guard_reason_human,
        reporter_status_human=reporter_status_human,
        operator_conclusion_human=operator_conclusion_human,
        deps=_story_assembly_deps(),
    )

def slug(value: Any, *, max_len: int = 80) -> str:
    text = re.sub(r"[^a-zA-Z0-9_-]+", "_", str(value or "").strip()).strip("_")
    if not text:
        return "item"
    return text[: max_len]


def feature_coverage(selected_candidate: Dict[str, Any]) -> Dict[str, Any]:
    feature_snapshot = (
        selected_candidate.get("feature_snapshot") if isinstance(selected_candidate.get("feature_snapshot"), dict) else {}
    )
    keys = [
        "engine_ma20_gap",
        "engine_ma60",
        "engine_ma120",
        "engine_adx14",
        "engine_trend_strength",
        "engine_atr14",
        "engine_volume_spike20",
        "engine_volatility20",
        "engine_vwap_distance",
        "engine_sector_relative_strength",
        "engine_cross_section_rank",
        "engine_regime",
        "engine_signal_score",
    ]
    present: List[str] = []
    missing: List[str] = []
    for key in keys:
        if feature_snapshot.get(key) is None:
            missing.append(key)
        else:
            present.append(key)
    return {
        "present": len(present),
        "total": len(keys),
        "present_keys": present,
        "missing_keys": missing,
    }


def normalized_feature_coverage(scanner: Dict[str, Any], selected_candidate: Dict[str, Any]) -> Dict[str, Any]:
    reported = scanner.get("feature_coverage") if isinstance(scanner.get("feature_coverage"), dict) else {}
    computed = feature_coverage(selected_candidate)
    present = safe_int(reported.get("present"), computed.get("present"))
    total = safe_int(reported.get("total"), computed.get("total"))
    coverage_ratio = safe_float(
        reported.get("coverage_ratio"),
        (present / total) if total > 0 else 0.0,
    )
    quality = str(reported.get("quality") or "").strip().lower()
    if not quality:
        if total <= 0:
            quality = "missing"
        elif coverage_ratio >= 0.75:
            quality = "strong"
        elif coverage_ratio >= 0.5:
            quality = "partial"
        else:
            quality = "weak"
    reported_present_keys = [str(x or "") for x in list(reported.get("present_keys") or []) if str(x or "").strip()]
    reported_missing_keys = [str(x or "") for x in list(reported.get("missing_keys") or []) if str(x or "").strip()]
    computed_present = safe_int(computed.get("present"), 0)
    computed_total = safe_int(computed.get("total"), 0)
    reported_key_counts_match = bool(
        reported_present_keys
        and len(reported_present_keys) == present
        and len(reported_present_keys) + len(reported_missing_keys) == total
    )
    computed_key_counts_match = computed_present == present and computed_total == total
    computed_present_keys = [
        str(x or "") for x in list(computed.get("present_keys") or []) if str(x or "").strip()
    ]
    computed_missing_keys = [
        str(x or "") for x in list(computed.get("missing_keys") or []) if str(x or "").strip()
    ]
    present_keys = reported_present_keys if reported_key_counts_match else (computed_present_keys if computed_key_counts_match else [])
    missing_keys = reported_missing_keys if reported_key_counts_match else (computed_missing_keys if computed_key_counts_match else [])
    return {
        "present": present,
        "total": total,
        "coverage_ratio": coverage_ratio,
        "quality": quality,
        "present_keys": present_keys,
        "missing_keys": missing_keys,
    }


def confidence_label(value: Any) -> str:
    score = safe_float(value, -1.0)
    if score >= 0.85:
        return "high"
    if score >= 0.65:
        return "medium"
    if score >= 0.0:
        return "low"
    return "not_captured"


def execution_mode_label(executor: Dict[str, Any]) -> str:
    effective_mode = str(executor.get("effective_mode") or "").strip().lower()
    broker_env = str(executor.get("broker_env") or "").strip().lower()
    execution_mode = str(executor.get("execution_mode") or executor.get("mode") or "").strip().lower()
    kiwoom_mode = str(executor.get("kiwoom_mode") or "").strip().lower()
    if "mock" in effective_mode or broker_env == "mock" or kiwoom_mode == "mock":
        return "simulation (mock broker)"
    if broker_env == "real" or effective_mode == "real_broker_http":
        return "live broker"
    if execution_mode:
        return execution_mode
    return "decision only"


def classify_story_type(execution: Dict[str, Any], executor: Dict[str, Any]) -> str:
    effective_mode = str(executor.get("effective_mode") or "").strip().lower()
    broker_env = str(executor.get("broker_env") or "").strip().lower()
    kiwoom_mode = str(executor.get("kiwoom_mode") or "").strip().lower()
    execution_attempted = bool(executor.get("execution_attempted")) or bool(execution.get("action"))
    execution_ok = bool(executor.get("execution_ok"))
    if "mock" in effective_mode or broker_env == "mock" or kiwoom_mode == "mock":
        return "simulation"
    if not execution_attempted:
        return "decision_only"
    if execution_attempted and not execution_ok:
        return "failed_execution"
    return "live_trade"


def build_story_id(day: str, execution: Dict[str, Any]) -> str:
    run_id = slug(execution.get("run_id"), max_len=48)
    symbol = slug(execution.get("symbol"), max_len=24)
    action = slug(str(execution.get("action") or "").lower(), max_len=12)
    compact_day = str(day or "").replace("-", "")
    return slug(f"{compact_day}_{symbol}_{action}_{run_id}", max_len=96)


def build_story_contract(bundle_out: Dict[str, Any]) -> Dict[str, Any]:
    execution = bundle_out.get("execution") if isinstance(bundle_out.get("execution"), dict) else {}
    executor = bundle_out.get("executor") if isinstance(bundle_out.get("executor"), dict) else {}
    story_type = classify_story_type(execution, executor)
    mode_label = execution_mode_label(executor)
    story_anchor = (
        f"{execution.get('action') or 'WAIT'} {execution.get('symbol') or (bundle_out.get('scanner') or {}).get('top_stock') or '-'} "
        f"x{execution.get('qty') or 0} | run {bundle_out.get('run_id') or '-'}"
    )
    warnings: List[str] = []
    if story_type == "failed_execution":
        warnings.append("Execution was attempted but did not complete successfully.")
    if story_type == "simulation":
        warnings.append("This story reflects simulation mode, not a live broker fill.")
    return {
        "story_available": bool(execution.get("action") or execution.get("symbol") or (bundle_out.get("scanner") or {}).get("top_stock")),
        "story_type": story_type,
        "execution_mode_label": mode_label,
        "story_anchor": story_anchor,
        "warnings": warnings,
    }


def _human_payload_deps() -> Dict[str, Any]:
    return {
        "build_strategist_evidence_trace": _build_strategist_evidence_trace,
        "korea_indices_bullet": _korea_indices_bullet,
        "list_text": _list_text,
        "format_pct": format_pct,
        "safe_float": safe_float,
        "safe_int": safe_int,
        "build_news_scanner_contribution_trace": _build_news_scanner_contribution_trace,
        "build_scanner_selection_trace": _build_scanner_selection_trace,
        "scanner_chart_fit_payload": _scanner_chart_fit_payload,
        "scanner_macro_chart_fit_payload": _scanner_macro_chart_fit_payload,
        "clip": clip,
        "confidence_label": confidence_label,
        "normalized_feature_coverage": normalized_feature_coverage,
        "build_monitor_blocker_trace": _build_monitor_blocker_trace,
        "build_monitor_stop_policy_trace": _build_monitor_stop_policy_trace,
        "merge_missing_values": _merge_missing_values,
        "format_exit_label": format_exit_label,
        "format_ratio_pct": format_ratio_pct,
    }

def build_market_context_human(strategist: Dict[str, Any]) -> Dict[str, Any]:
    return _build_market_context_human_impl(strategist, deps=_human_payload_deps())

def build_scanner_reason_human(scanner: Dict[str, Any], strategist: Dict[str, Any]) -> Dict[str, Any]:
    return _build_scanner_reason_human_impl(scanner, strategist, deps=_human_payload_deps())

def _evidence_enrichment_deps() -> Dict[str, Any]:
    return {
        "normalized_feature_coverage_from_scanner_evidence": _normalized_feature_coverage_from_scanner_evidence,
        "scanner_candidate_row_from_evidence": _scanner_candidate_row_from_evidence,
        "scanner_chart_fit_from_scanner_evidence": _scanner_chart_fit_from_scanner_evidence,
        "scanner_macro_chart_fit_from_scanner_evidence": _scanner_macro_chart_fit_from_scanner_evidence,
        "selection_basis_from_scores": _selection_basis_from_scores,
        "top_numeric_drivers": _top_numeric_drivers,
    }

def enrich_scanner_reason_from_evidence(
    scanner_reason_human: Dict[str, Any],
    scanner_evidence: Dict[str, Any],
) -> Dict[str, Any]:
    return _enrich_scanner_reason_from_evidence_impl(scanner_reason_human, scanner_evidence, deps=_evidence_enrichment_deps())

def enrich_filters_from_evidence(
    filters_human: Dict[str, Any],
    scanner_evidence: Dict[str, Any],
    *,
    selected_symbol: str,
    monitor_evidence: Optional[Dict[str, Any]] = None,
    entry_execution_details: Optional[Dict[str, Any]] = None,
    exit_execution_details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return _enrich_filters_from_evidence_impl(
        filters_human,
        scanner_evidence,
        selected_symbol=selected_symbol,
        monitor_evidence=monitor_evidence,
        entry_execution_details=entry_execution_details,
        exit_execution_details=exit_execution_details,
        deps=_evidence_enrichment_deps(),
    )

def build_filters_human(scanner: Dict[str, Any], strategist: Dict[str, Any], supervisor: Dict[str, Any]) -> Dict[str, Any]:
    selected = scanner.get("selected_candidate") if isinstance(scanner.get("selected_candidate"), dict) else {}
    sources = [str(x or "") for x in list(selected.get("sources") or []) if str(x or "").strip()]
    score_breakdown = selected.get("score_breakdown") if isinstance(selected.get("score_breakdown"), dict) else {}
    components = selected.get("component_snapshot") if isinstance(selected.get("component_snapshot"), dict) else {}
    feature_snapshot = selected.get("feature_snapshot") if isinstance(selected.get("feature_snapshot"), dict) else {}
    coverage = normalized_feature_coverage(scanner, selected)
    checks: List[Dict[str, str]] = []

    def add_check(name: str, status: str, detail: str) -> None:
        checks.append({"name": name, "status": status, "detail": detail})

    liquidity_pass = "top_value" in sources or safe_float(components.get("trading_value_component"), 0.0) > 0
    turnover_pass = "top_volume" in sources or safe_float(score_breakdown.get("volume_surge"), 0.0) > 0
    theme_score = safe_float(score_breakdown.get("theme_boost"), 0.0)
    theme_pass = "sector_theme" in sources or theme_score > 0.0
    theme_detail = (
        f"selected candidate theme boost was {theme_score:+.3f} or sector_theme source matched"
        if theme_pass
        else f"selected candidate had no sector_theme source and theme boost was {theme_score:+.3f}"
    )
    if coverage["total"] <= 0:
        chart_status = "NOT_AVAILABLE"
    elif coverage["present"] >= 8:
        chart_status = "PASS"
    elif coverage["present"] >= 4:
        chart_status = "PARTIAL"
    else:
        chart_status = "FAIL"
    sentiment_gate = safe_float(components.get("sentiment_component"), 0.0) >= 0 or safe_float(
        strategist.get("global_sentiment_score"),
        0.0,
    ) > -0.35
    risk_gate = bool(supervisor.get("supervisor_allow")) and safe_float(selected.get("risk_score"), 0.0) <= 1.0
    spread_bps = selected.get("spread_bps")
    if spread_bps in (None, ""):
        spread_bps = feature_snapshot.get("quote_spread_bps")
    spread_bps = (safe_float(spread_bps, 0.0) if spread_bps not in (None, "") else None)
    spread_threshold_bps = 50.0
    spread_status = "NOT_AVAILABLE"
    spread_detail = "spread or slippage diagnostics were not captured in this run"
    if spread_bps is not None:
        spread_status = "PASS" if spread_bps <= spread_threshold_bps else "FAIL"
        spread_detail = f"scanner quote snapshot spread was {spread_bps:.1f} bps"

    add_check("liquidity filter", "PASS" if liquidity_pass else "FAIL", "top value or trading-value input supported the selection")
    add_check("turnover filter", "PASS" if turnover_pass else "FAIL", "top volume or turnover input supported the selection")
    add_check("sector/theme alignment", "PASS" if theme_pass else "FAIL", theme_detail)
    add_check("chart completeness filter", chart_status, f"{coverage['present']}/{coverage['total']} captured chart features")
    add_check("sentiment gate", "PASS" if sentiment_gate else "FAIL", f"news/global sentiment contribution was {safe_float(components.get('sentiment_component'), 0.0):.3f}")
    add_check("risk gate", "PASS" if risk_gate else "FAIL", f"risk score was {safe_float(selected.get('risk_score'), 0.0):.3f} and supervisor allow={bool(supervisor.get('supervisor_allow'))}")
    add_check("price anomaly filter", "NOT_AVAILABLE", "price anomaly check was not captured in this run")
    add_check("spread/slippage filter", spread_status, spread_detail)

    passed = sum(1 for row in checks if row["status"] == "PASS")
    bullets = [f"{row['name']}: {row['status']} - {row['detail']}" for row in checks]
    condition_status = str(scanner.get("condition_search_status") or "").strip()
    if condition_status:
        bullets.append(f"Condition search source: {condition_status} ({scanner.get('condition_search_reason') or 'no extra reason captured'})")
    coverage_quality = str(coverage.get("quality") or chart_status.lower()).strip().lower()
    return {
        "checks": checks,
        "summary": (
            f"Scanner and guard checks passed {passed} of {len(checks)} visible gates. "
            f"Chart completeness was {coverage_quality} with {coverage['present']}/{coverage['total']} captured features."
        ),
        "bullets": bullets,
    }


def build_monitor_reason_human(monitor: Dict[str, Any], execution: Dict[str, Any]) -> Dict[str, Any]:
    return _build_monitor_reason_human_impl(monitor, execution, deps=_human_payload_deps())

def build_guard_reason_human(supervisor: Dict[str, Any]) -> Dict[str, Any]:
    allow = bool(supervisor.get("supervisor_allow"))
    verdict = str(supervisor.get("verdict") or "").strip() or ("approve" if allow else "block")
    reason = str(supervisor.get("supervisor_reason") or supervisor.get("guard_reason") or "").strip() or "not captured"
    summary = (
        f"Supervisor approved the order because {reason}."
        if allow
        else f"Supervisor blocked the order because {reason}."
    )
    bullets = [
        f"Supervisor verdict: {verdict}",
        f"Supervisor allow: {'yes' if allow else 'no'}",
        f"Guard reason: {reason}",
        f"Action reviewed: {supervisor.get('action') or 'not_captured'}",
        f"Symbol reviewed: {supervisor.get('symbol') or 'not_captured'}",
        "Approval mode: not captured in the execution trace",
    ]
    return {"summary": summary, "bullets": bullets, "allow": allow, "verdict": verdict}


def build_execution_outcome_human(
    execution: Dict[str, Any],
    executor: Dict[str, Any],
    *,
    story_type: str,
    mode_label: str,
) -> Dict[str, Any]:
    return _build_execution_outcome_human_impl(
        execution,
        executor,
        story_type=story_type,
        mode_label=mode_label,
    )


def build_reporter_status_human(reporter: Dict[str, Any], reporter_day_obj: Dict[str, Any]) -> Dict[str, Any]:
    linked = bool(reporter.get("reporter_analysis_found"))
    day_file_found = bool(reporter.get("reporter_analysis_day_file_found"))
    ai_summary = str(reporter.get("reporter_analysis_summary") or reporter_day_obj.get("ai_summary") or "").strip()
    grade = str(reporter_day_obj.get("ai_run_grade") or "N/A").strip()
    if linked:
        status = "linked"
        reason = "당일 리포터 분석이 이 run에 연결됐습니다."
    elif day_file_found:
        status = "pending"
        reason = "당일 리포터 파일은 있지만 이 run에 대한 개별 평가는 아직 연결되지 않았습니다."
    else:
        status = "missing"
        reason = "당일 리포터 분석은 아직 생성되지 않았습니다."
    if status == "linked":
        summary = ai_summary or reason
    elif ai_summary:
        summary = f"{reason} 중간 요약: {ai_summary}"
    else:
        summary = reason
    bullets = [
        f"리포터 상태는 {status}입니다.",
        f"리포터 판단 사유는 {reason}입니다.",
        f"리포터 등급은 {grade}입니다.",
        f"리포터 요약은 {summary}입니다.",
    ]
    return normalize_reporter_status_human({
        "status": status,
        "reason": reason,
        "grade": grade,
        "summary": summary,
        "bullets": bullets,
    })


def build_operator_conclusion_human(
    *,
    execution: Dict[str, Any],
    scanner_reason_human: Dict[str, Any],
    filters_human: Dict[str, Any],
    monitor_reason_human: Dict[str, Any],
    execution_outcome_human: Dict[str, Any],
    reporter_status_human: Dict[str, Any],
) -> Dict[str, Any]:
    action = str(execution.get("action") or "").upper() or "WAIT"
    outcome_text = str(execution_outcome_human.get("summary") or "").upper()
    outcome_ko = str(execution_outcome_human.get("summary") or "")
    if action != "SELL" and ("SELL" in outcome_text or "매도" in outcome_ko):
        action = "SELL"
    elif action not in {"BUY", "SELL"} and ("BUY" in outcome_text or "매수" in outcome_ko):
        action = "BUY"
    watch_next: List[str] = []
    invalidation: List[str] = [
        "거시 환경이 부정적으로 전환되는지 확인해야 합니다.",
        "테마나 섹터 강도가 약해지는지 확인해야 합니다.",
        "스캐너와 모니터 판단이 다시 어긋나는지 확인해야 합니다.",
    ]
    if action == "BUY":
        summary_prefix = "현재 판단은 진입 유지입니다."
        watch_next.append("보유 포지션의 손절과 익절 기준이 유지되는지 확인해야 합니다.")
        watch_next.append("선택된 테마와 종목의 상대 강도가 유지되는지 확인해야 합니다.")
    elif action == "SELL":
        summary_prefix = "현재 판단은 청산 완료입니다."
        watch_next.append("이번 청산이 방어적으로 타당했는지, 과도한 노이즈 청산은 아니었는지 복기해야 합니다.")
        watch_next.append("재진입은 쿨다운 이후 새 스캐너 확인이 있을 때만 검토해야 합니다.")
    elif action == "HOLD":
        summary_prefix = "현재 판단은 보유 유지입니다."
        watch_next.append("보유 근거가 약해지는지와 모니터 경고 축 변화를 계속 확인해야 합니다.")
    else:
        summary_prefix = "현재 판단은 관망입니다."
        watch_next.append("새로운 스캐너 순위와 모니터 확인이 나올 때까지 관망해야 합니다.")
    if reporter_status_human.get("status") != "linked":
        watch_next.append("동일 일자 리포터 분석 연계가 가능해지면 후속 확인이 필요합니다.")
    if "FAIL" in " ".join(row.get("status") or "" for row in list(filters_human.get("checks") or [])):
        watch_next.append("실패했거나 비어 있던 필터를 다시 확인하기 전에는 다음 사이클을 공격적으로 해석하면 안 됩니다.")
    summary = (
        f"{summary_prefix} "
        f"{execution_outcome_human.get('summary') or scanner_reason_human.get('summary') or monitor_reason_human.get('summary')}"
    )
    return {
        "current_action": action,
        "summary": summary,
        "watch_next": watch_next[:6],
        "thesis_invalidation": invalidation[:6],
    }


def build_timeline(
    *,
    commander: Dict[str, Any],
    market_context_human: Dict[str, Any],
    scanner_reason_human: Dict[str, Any],
    monitor_reason_human: Dict[str, Any],
    guard_reason_human: Dict[str, Any],
    execution_outcome_human: Dict[str, Any],
    reporter_status_human: Dict[str, Any],
    execution: Dict[str, Any],
) -> List[Dict[str, Any]]:
    return _build_timeline_impl(
        commander=commander,
        market_context_human=market_context_human,
        scanner_reason_human=scanner_reason_human,
        monitor_reason_human=monitor_reason_human,
        guard_reason_human=guard_reason_human,
        execution_outcome_human=execution_outcome_human,
        reporter_status_human=reporter_status_human,
        execution=execution,
    )


def collect_story_warnings(
    *,
    story_contract: Dict[str, Any],
    market_context_human: Dict[str, Any],
    filters_human: Dict[str, Any],
    reporter_status_human: Dict[str, Any],
    execution_outcome_human: Dict[str, Any],
) -> List[str]:
    return _collect_story_warnings_impl(
        story_contract=story_contract,
        market_context_human=market_context_human,
        filters_human=filters_human,
        reporter_status_human=reporter_status_human,
        execution_outcome_human=execution_outcome_human,
    )


def _normalize_trade_lifecycle_for_story_input(
    bundle_out: Dict[str, Any],
    *,
    trade_lifecycle: Dict[str, Any] | None = None,
    existing_story_input: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return _normalize_trade_lifecycle_for_story_input_impl(
        bundle_out,
        trade_lifecycle=trade_lifecycle,
        existing_story_input=existing_story_input,
    )


def build_trade_story_input_from_bundle(
    bundle_out: Dict[str, Any],
    *,
    trade_lifecycle: Dict[str, Any] | None = None,
    existing_story_input: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    normalized_lifecycle = _normalize_trade_lifecycle_for_story_input(
        bundle_out,
        trade_lifecycle=trade_lifecycle,
        existing_story_input=existing_story_input,
    )
    story_input = build_trade_story_input(
        bundle_out,
        trade_lifecycle=normalized_lifecycle if normalized_lifecycle else trade_lifecycle,
    )
    existing = existing_story_input if isinstance(existing_story_input, dict) else {}
    for key in (
        "report_runtime_mode",
        "skip_separated_report_llm",
        "entry_strategist_run_id",
        "strategy_anchor_run_id",
    ):
        if key not in story_input and key in existing:
            story_input[key] = existing.get(key)
    for key in ("trade_id", "day", "run_id"):
        if story_input.get(key) in (None, "", [], {}) and existing.get(key) not in (None, "", [], {}):
            story_input[key] = existing.get(key)
    return story_input


def _compact_canonical_monitor(canonical_monitor: Dict[str, Any] | None) -> Dict[str, Any]:
    return _compact_canonical_monitor_impl(canonical_monitor)


def build_trade_story_input(
    bundle_out: Dict[str, Any],
    *,
    trade_lifecycle: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return _build_trade_story_input_impl(bundle_out, trade_lifecycle=trade_lifecycle, deps=_story_assembly_deps())

def render_bundle_markdown(out: Dict[str, Any]) -> str:
    story_contract = out.get("story_contract") if isinstance(out.get("story_contract"), dict) else {}
    lines: List[str] = []
    lines.append(f"# Aggregated Execution Bundle ({out.get('run_id')})")
    lines.append("")
    lines.append(f"- day: **{out.get('day')}**")
    lines.append(f"- story_anchor: **{story_contract.get('story_anchor') or '-'}**")
    lines.append(f"- story_type: **{story_contract.get('story_type') or '-'}**")
    lines.append(f"- execution_mode: **{story_contract.get('execution_mode_label') or '-'}**")
    lines.append("")
    sections = [
        ("Market Context", out.get("market_context_human")),
        ("Why This Symbol", out.get("scanner_reason_human")),
        ("Filters / Gates", out.get("filters_human")),
        ("Monitor / Trigger Reasoning", out.get("monitor_reason_human")),
        ("Guard / Approval", out.get("guard_reason_human")),
        ("Execution Outcome", out.get("execution_outcome_human")),
        ("Reporter Status", out.get("reporter_status_human")),
        ("Operator Conclusion", out.get("operator_conclusion_human")),
    ]
    for title, section in sections:
        data = section if isinstance(section, dict) else {}
        lines.append(f"## {title}")
        lines.append("")
        if data.get("summary"):
            lines.append(str(data.get("summary")))
            lines.append("")
        for bullet in list(data.get("bullets") or [])[:8]:
            lines.append(f"- {bullet}")
        lines.append("")
    lines.append("## Timeline")
    lines.append("")
    for row in list(out.get("timeline") or [])[:10]:
        if not isinstance(row, dict):
            continue
        lines.append(f"- {row.get('step')}: {row.get('summary') or '-'}")
    lines.append("")
    lines.append("## Artifacts")
    lines.append("")
    for key, value in dict(out.get("artifacts") or {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    return "\n".join(lines)


def render_summary_markdown(out: Dict[str, Any]) -> str:
    bundles = out.get("bundles") if isinstance(out.get("bundles"), list) else []
    lines: List[str] = []
    lines.append(f"# Live Execution Bundles ({out.get('day')})")
    lines.append("")
    lines.append(f"- bundle_count: **{out.get('bundle_count')}**")
    lines.append(f"- canonical_trades_root: `{out.get('canonical_trades_root')}`")
    lines.append("")
    if not bundles:
        lines.append("No executed BUY/SELL runs were found for the selected day.")
        lines.append("")
        return "\n".join(lines)
    lines.append("## Bundles")
    lines.append("")
    for row in bundles:
        lines.append(
            f"- `{row.get('run_id')}` {row.get('action')} {row.get('symbol')} x{row.get('qty')} "
            f"story=`{row.get('story_type')}` report=`{row.get('trade_report_json_path')}`"
        )
    lines.append("")
    return "\n".join(lines)
