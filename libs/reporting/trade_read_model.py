from __future__ import annotations

"""Read-only reporting/trade artifact helpers for Phase 5-2.

This module is the stable non-UI surface for loading and normalizing
trade report / operator brief artifacts. UI modules may still wrap these
helpers, but the parsing and normalization ownership lives here.
"""

from pathlib import Path
import re
from typing import Any, Callable, Dict, List, Optional

from libs.reporting.strategy_read_model import (
    build_recent_strategist_feedback_window,
    normalize_strategist_feedback_input,
)
import sys as _r3_sys
from libs.reporting.trade_read_model_parts.read_artifact_selection import (
    selected_trade_artifacts,
)
from libs.reporting.trade_read_model_parts.read_truth_projection import (
    read_truth_blocker_trace_data_source_quality,
)
from libs.reporting.trade_read_model_parts.read_display_context import (
    read_display_context,
)
from libs.agents.reporter.read_models.read_model_bodies_01 import (  # R-4 owner bodies (facade-injected)
    _section_value_quality_r4_impl,
    prefer_richer_trade_report_section_r4_impl,
    normalize_trade_report_section_r4_impl,
    normalize_trade_report_detail_sections_r4_impl,
    normalize_trade_report_detail_meta_r4_impl,
    collect_strategist_feedback_inputs_r4_impl,
    build_trade_report_recent_feedback_pack_r4_impl,
    load_trade_report_recent_feedback_pack_r4_impl,
    load_time_bucketed_trade_report_recent_feedback_pack_r4_impl,
    build_linked_trade_report_card_r4_impl,
    build_unlinked_trade_report_card_r4_impl,
    normalize_operator_brief_detail_payload_r4_impl,
    build_operator_brief_detail_view_r4_impl,
    extract_labeled_bullet_r4_impl,
    extract_labeled_int_r4_impl,
    parse_canonical_filter_bullets_r4_impl,
    normalize_canonical_monitor_snapshot_r4_impl,
    brief_headline_text_r4_impl,
    brief_headline_matches_symbol_r4_impl,
)
from libs.agents.reporter.read_models.read_model_bodies_02 import (  # R-4 owner bodies (facade-injected)
    brief_collect_top_headlines_r4_impl,
    brief_top_numeric_drivers_r4_impl,
)


def _pick_first_existing(*paths: Path) -> Path:
    for path in paths:
        if isinstance(path, Path) and path.exists():
            return path
    return Path()


def trade_report_artifact_payload(trade_report: Dict[str, Any], key: str) -> Dict[str, Any]:
    payload = trade_report.get(key) if isinstance(trade_report, dict) else {}
    return payload if isinstance(payload, dict) else {}


def _section_value_quality(value: Any) -> int:
    return _section_value_quality_r4_impl(value, facade=_r3_sys.modules[__name__])


def prefer_richer_trade_report_section(*sections: Any) -> Dict[str, Any]:
    return prefer_richer_trade_report_section_r4_impl(*sections, facade=_r3_sys.modules[__name__])


def trade_report_section_summary(section: Dict[str, Any], fallback: str = "") -> str:
    if not isinstance(section, dict):
        return str(fallback or "")
    return str(section.get("summary") or fallback or "")


def trade_report_section_bullets(section: Dict[str, Any], *, limit: int = 6) -> List[str]:
    if not isinstance(section, dict):
        return []
    return [str(x or "") for x in list(section.get("bullets") or [])[:limit] if str(x or "").strip()]


def normalize_trade_report_section(
    report: Dict[str, Any],
    key: str,
    fallback_summary: str = "",
    *,
    trim_text: Callable[..., str],
    clean_str_list: Callable[..., List[str]],
) -> Dict[str, Any]:
    return normalize_trade_report_section_r4_impl(report, key, fallback_summary, trim_text=trim_text, clean_str_list=clean_str_list, facade=_r3_sys.modules[__name__])


def normalize_trade_report_detail_sections(
    report: Dict[str, Any],
    *,
    fallback_summaries: Dict[str, str],
    trim_text: Callable[..., str],
    clean_str_list: Callable[..., List[str]],
) -> Dict[str, Any]:
    return normalize_trade_report_detail_sections_r4_impl(report, fallback_summaries=fallback_summaries, trim_text=trim_text, clean_str_list=clean_str_list, facade=_r3_sys.modules[__name__])


def normalize_trade_report_detail_meta(
    report: Dict[str, Any],
    *,
    operator_conclusion_human: Dict[str, Any],
    action: str,
    trim_text: Callable[..., str],
    clean_str_list: Callable[..., List[str]],
) -> Dict[str, Any]:
    return normalize_trade_report_detail_meta_r4_impl(report, operator_conclusion_human=operator_conclusion_human, action=action, trim_text=trim_text, clean_str_list=clean_str_list, facade=_r3_sys.modules[__name__])


def build_trade_report_detail_view(
    meta: Dict[str, Any],
    payloads: Dict[str, Any],
    *,
    trim_text: Callable[..., str],
    clean_str_list: Callable[..., List[str]],
    normalize_symbol: Callable[..., str],
    story_type_label: Callable[[Any], str],
    story_type_badge_class: Callable[[Any], str],
    normalize_ai_report_diagnostics: Callable[..., Dict[str, Any]],
) -> Dict[str, Any]:
    report = payloads.get("report_data") if isinstance(payloads.get("report_data"), dict) else {}
    bundle = payloads.get("bundle_data") if isinstance(payloads.get("bundle_data"), dict) else {}
    lifecycle = payloads.get("lifecycle_data") if isinstance(payloads.get("lifecycle_data"), dict) else {}
    market_context_human = bundle.get("market_context_human") if isinstance(bundle.get("market_context_human"), dict) else {}
    scanner_reason_human = bundle.get("scanner_reason_human") if isinstance(bundle.get("scanner_reason_human"), dict) else {}
    filters_human = bundle.get("filters_human") if isinstance(bundle.get("filters_human"), dict) else {}
    monitor_reason_human = bundle.get("monitor_reason_human") if isinstance(bundle.get("monitor_reason_human"), dict) else {}
    monitor_reason_human = bundle.get("monitor_reason_human") if isinstance(bundle.get("monitor_reason_human"), dict) else {}
    guard_reason_human = bundle.get("guard_reason_human") if isinstance(bundle.get("guard_reason_human"), dict) else {}
    execution_outcome_human = bundle.get("execution_outcome_human") if isinstance(bundle.get("execution_outcome_human"), dict) else {}
    reporter_status_human = bundle.get("reporter_status_human") if isinstance(bundle.get("reporter_status_human"), dict) else {}
    operator_conclusion_human = bundle.get("operator_conclusion_human") if isinstance(bundle.get("operator_conclusion_human"), dict) else {}

    lifecycle_entry = lifecycle.get("entry") if isinstance(lifecycle.get("entry"), dict) else {}
    lifecycle_holding = lifecycle.get("holding") if isinstance(lifecycle.get("holding"), dict) else {}
    lifecycle_exit = lifecycle.get("exit") if isinstance(lifecycle.get("exit"), dict) else {}
    lifecycle_summary_obj = lifecycle.get("summary") if isinstance(lifecycle.get("summary"), dict) else {}
    lifecycle_reporter = lifecycle.get("reporter") if isinstance(lifecycle.get("reporter"), dict) else {}

    sections = normalize_trade_report_detail_sections(
        report,
        fallback_summaries={
            "executive_summary": lifecycle_summary_obj.get("lifecycle_summary_human") or operator_conclusion_human.get("summary") or execution_outcome_human.get("summary") or "",
            "market_context_at_entry": (lifecycle_entry.get("strategist_context") or {}).get("market_context_summary") if isinstance(lifecycle_entry.get("strategist_context"), dict) else market_context_human.get("summary") or "",
            "why_this_symbol_was_chosen": lifecycle_entry.get("reason_human") or scanner_reason_human.get("summary") or "",
            "scanner_filters": filters_human.get("summary") or "",
            "entry_decision": lifecycle_entry.get("reason_human") or scanner_reason_human.get("summary") or "",
            "holding_monitoring_story": monitor_reason_human.get("summary")
            or (
                f"Holding phase captured {len(list(lifecycle_holding.get('run_ids') or []))} runs."
                if list(lifecycle_holding.get("run_ids") or [])
                else ""
            ),
            "exit_decision": lifecycle_exit.get("reason_human")
            or (
                "Position is still open; no closing SELL execution has been captured yet."
                if str(lifecycle.get("status") or "").lower() == "open"
                else ""
            ),
            "execution_quality": execution_outcome_human.get("summary") or "",
            "guard_approval_result": guard_reason_human.get("summary") or "",
            "reporter_evaluation": reporter_status_human.get("summary") or "",
            "errors_weaknesses_improvement_points": "No explicit weaknesses were captured beyond standard warnings.",
        },
        trim_text=trim_text,
        clean_str_list=clean_str_list,
    )
    executive = sections.get("executive_summary") if isinstance(sections.get("executive_summary"), dict) else {}
    market_context = sections.get("market_context") if isinstance(sections.get("market_context"), dict) else {}
    why_symbol = sections.get("why_this_symbol") if isinstance(sections.get("why_this_symbol"), dict) else {}
    scanner_filters = sections.get("scanner_filters") if isinstance(sections.get("scanner_filters"), dict) else {}
    entry_decision = sections.get("entry_decision") if isinstance(sections.get("entry_decision"), dict) else {}
    holding_story = sections.get("holding_monitoring_story") if isinstance(sections.get("holding_monitoring_story"), dict) else {}
    exit_decision = sections.get("exit_decision") if isinstance(sections.get("exit_decision"), dict) else {}
    execution_quality = sections.get("execution_quality") if isinstance(sections.get("execution_quality"), dict) else {}
    guard_result = sections.get("guard_approval_result") if isinstance(sections.get("guard_approval_result"), dict) else {}
    reporter_eval = sections.get("reporter_evaluation") if isinstance(sections.get("reporter_evaluation"), dict) else {}
    weak_points = sections.get("errors_weaknesses_improvement_points") if isinstance(sections.get("errors_weaknesses_improvement_points"), dict) else {}
    timeline = [
        row
        for row in list(report.get("full_timeline") or report.get("timeline") or lifecycle.get("timeline") or bundle.get("timeline") or [])
        if isinstance(row, dict)
    ][:24]
    report_exists = bool(payloads.get("report_exists"))
    action = trim_text(report.get("action"), max_len=32) or trim_text(meta.get("action"), max_len=32) or "WAIT"
    detail_meta = normalize_trade_report_detail_meta(
        report,
        operator_conclusion_human=operator_conclusion_human,
        action=action,
        trim_text=trim_text,
        clean_str_list=clean_str_list,
    )
    generation = detail_meta.get("generation") if isinstance(detail_meta.get("generation"), dict) else {}
    diagnostics = normalize_ai_report_diagnostics(
        report.get("ai_report_diagnostics")
        if isinstance(report.get("ai_report_diagnostics"), dict)
        else bundle.get("ai_report_diagnostics")
        if isinstance(bundle.get("ai_report_diagnostics"), dict)
        else lifecycle.get("ai_report_diagnostics")
        if isinstance(lifecycle.get("ai_report_diagnostics"), dict)
        else {},
        report_exists=report_exists,
        lifecycle_status=meta.get("lifecycle_status") or lifecycle.get("status"),
        story_type=meta.get("story_type") or report.get("story_type"),
        model_hint=generation.get("model"),
        generation=generation,
    )
    symbol = normalize_symbol(
        report.get("symbol") or meta.get("symbol") or "",
        allow_test_symbols=True,
    )
    reporter_status = trim_text(reporter_eval.get("status"), max_len=48) or trim_text(reporter_status_human.get("status"), max_len=48) or "-"
    reporter_grade = trim_text(reporter_eval.get("grade"), max_len=24) or trim_text(reporter_status_human.get("grade"), max_len=24) or "-"
    review_focus = sections.get("review_focus") if isinstance(sections.get("review_focus"), dict) else {}
    strategist_feedback_input = normalize_strategist_feedback_input(
        bundle.get("strategist_feedback_input")
        if isinstance(bundle.get("strategist_feedback_input"), dict)
        else lifecycle.get("strategist_feedback_input")
        if isinstance(lifecycle.get("strategist_feedback_input"), dict)
        else report.get("strategist_feedback_input")
        if isinstance(report.get("strategist_feedback_input"), dict)
        else {}
    )
    recent_feedback_items = (
        payloads.get("recent_feedback_items")
        if payloads.get("recent_feedback_items") is not None
        else meta.get("recent_feedback_items")
    )
    recent_feedback_window_size = (
        payloads.get("recent_feedback_window_size")
        if payloads.get("recent_feedback_window_size") not in (None, "")
        else meta.get("recent_feedback_window_size")
    )
    strategist_feedback_recent_window = build_trade_report_recent_feedback_view(
        recent_feedback_items,
        window_size=int(recent_feedback_window_size or 10),
    )

    return {
        "found": True,
        "trade_id": str(meta.get("trade_id") or meta.get("story_id") or ""),
        "story_id": str(meta.get("story_id") or ""),
        "run_id": str(meta.get("run_id") or ""),
        "run_link": f"/runs/{meta.get('run_id')}" if str(meta.get("run_id") or "").strip() else "",
        "symbol": symbol,
        "action": action,
        "status": str(meta.get("lifecycle_status") or report.get("status") or lifecycle.get("status") or ""),
        "lifecycle_summary": str(meta.get("lifecycle_summary") or lifecycle_summary_obj.get("lifecycle_summary_human") or ""),
        "story_type": str(meta.get("story_type") or report.get("story_type") or ""),
        "story_type_label": str(meta.get("story_type_label") or story_type_label(report.get("story_type"))),
        "story_type_badge_class": str(meta.get("story_type_badge_class") or story_type_badge_class(report.get("story_type"))),
        "execution_mode_label": str(meta.get("execution_mode_label") or report.get("execution_mode_label") or "not captured"),
        "report_available": bool(diagnostics.get("report_status") == "available" and report_exists),
        "report_summary": str(meta.get("report_summary") or executive.get("summary") or ""),
        "reporter_status_human": str(meta.get("reporter_status_human") or reporter_eval.get("summary") or ""),
        "ai_report_diagnostics": diagnostics,
        "executive_summary": executive,
        "market_context": market_context,
        "why_this_symbol": why_symbol,
        "entry_decision": entry_decision,
        "holding_monitoring_story": holding_story,
        "exit_decision": exit_decision,
        "scanner_logic_and_filters": scanner_filters,
        "monitor_trigger_reasoning": holding_story,
        "guard_approval_result": guard_result,
        "execution_result": execution_quality,
        "execution_quality": execution_quality,
        "review_focus": review_focus,
        "strategist_feedback_input": strategist_feedback_input,
        "strategist_feedback_recent_window": strategist_feedback_recent_window,
        "reporter_evaluation": {
            **reporter_eval,
            "status": reporter_status,
            "grade": reporter_grade or trim_text(lifecycle_reporter.get("grade"), max_len=24) or "-",
        },
        "errors_weaknesses_improvement_points": weak_points,
        "timeline": timeline,
        "full_timeline": timeline,
        "trade_lifecycle": lifecycle if isinstance(lifecycle, dict) else {},
        "final_operator_conclusion": detail_meta.get("final_operator_conclusion") if isinstance(detail_meta.get("final_operator_conclusion"), dict) else {},
        "generation": generation,
        "paths": {
            "trade_report_json": str(meta.get("trade_report_json_path") or ""),
            "trade_report_md": str(meta.get("trade_report_md_path") or ""),
            "trade_story_input": str(meta.get("trade_story_input_path") or ""),
            "ai_trade_report_json": str(meta.get("ai_trade_report_json_path") or meta.get("trade_report_json_path") or ""),
            "ai_trade_report_md": str(meta.get("ai_trade_report_md_path") or meta.get("trade_report_md_path") or ""),
            "ai_trade_report_input": str(meta.get("ai_trade_report_input_path") or meta.get("trade_story_input_path") or ""),
            "trade_lifecycle": str(meta.get("trade_lifecycle_json_path") or ""),
            "aggregated_execution_bundle": str(meta.get("aggregated_bundle_path") or ""),
            "strategist_llm_response": str(meta.get("strategist_llm_response_path") or ""),
            "ai_trade_report_llm_response": str(meta.get("ai_trade_report_llm_response_path") or ""),
            "brief_llm_response": str(meta.get("brief_llm_response_path") or ""),
        },
        "raw_report": report if isinstance(report, dict) else {},
    }


def collect_strategist_feedback_inputs(items: Any) -> List[Dict[str, Any]]:
    return collect_strategist_feedback_inputs_r4_impl(items, facade=_r3_sys.modules[__name__])


def build_recent_trade_feedback_summary_input(
    items: Any,
    *,
    window_size: int = 10,
) -> Dict[str, Any]:
    return build_recent_strategist_feedback_window(
        collect_strategist_feedback_inputs(items),
        window_size=window_size,
    )


def build_trade_report_recent_feedback_view(
    items: Any,
    *,
    window_size: int = 10,
) -> Dict[str, Any]:
    return build_recent_trade_feedback_summary_input(items, window_size=window_size)


def build_trade_report_recent_feedback_pack(
    items: Any,
    *,
    window_size: int = 10,
) -> Dict[str, Any]:
    return build_trade_report_recent_feedback_pack_r4_impl(items, window_size=window_size, facade=_r3_sys.modules[__name__])


def load_trade_report_recent_feedback_pack(
    meta: Dict[str, Any] | None = None,
    payloads: Dict[str, Any] | None = None,
    *,
    default_window_size: int = 10,
) -> Dict[str, Any]:
    return load_trade_report_recent_feedback_pack_r4_impl(meta, payloads, default_window_size=default_window_size, facade=_r3_sys.modules[__name__])


def load_time_bucketed_trade_report_recent_feedback_pack(
    meta: Dict[str, Any] | None = None,
    payloads: Dict[str, Any] | None = None,
    *,
    default_window_size: int = 10,
) -> Dict[str, Any]:
    """Future-facing time-bucketed contract candidate for non-UI consumers.

    This helper does not replace the existing recent-window contract.
    It wraps the existing recent-window pack in a parallel bucketed surface so
    future runtime or reporting consumers can depend on a common bucket shape
    without changing current behavior.

    Current buckets intentionally stay minimal:
    - overall_recent: existing recent-window pack reuse path
    - daily_recent: optional shell fed by meta/payload inputs if available
    - symbol_recent: optional shell fed by meta/payload inputs if available
    """
    return load_time_bucketed_trade_report_recent_feedback_pack_r4_impl(meta, payloads, default_window_size=default_window_size, facade=_r3_sys.modules[__name__])


def load_reporter_snippet_for_run(
    reports_root: Path,
    run_id: str,
    run_day: str,
    *,
    read_json: Callable[[Path], Dict[str, Any]],
) -> Dict[str, Any]:
    path = reports_root / "dev" / "analysis" / "reporter_analysis" / f"reporter_analysis_{run_day}.json"
    report = read_json(path)
    if not report:
        return {
            "report_path": str(path),
            "found": False,
            "ai_summary": "",
            "ai_run_grade": "",
            "reason": "same_day_report_missing",
        }
    chains = ((report.get("decision_trace_chain_summary") or {}).get("chains") or []) if isinstance(report.get("decision_trace_chain_summary"), dict) else []
    chain = next((c for c in chains if isinstance(c, dict) and str(c.get("run_id") or "").strip() == str(run_id or "").strip()), {})
    if not chain:
        return {
            "report_path": str(path),
            "found": False,
            "ai_summary": "",
            "ai_run_grade": str(report.get("ai_run_grade") or ""),
            "reason": "run_not_linked_in_same_day_report",
        }
    return {
        "report_path": str(path),
        "found": True,
        "ai_summary": str(report.get("ai_summary") or ""),
        "ai_run_grade": str(report.get("ai_run_grade") or ""),
        "chain": chain,
    }


def build_linked_trade_report_card(
    trade_report_meta: Dict[str, Any],
    report_payloads: Dict[str, Any],
    *,
    primary_symbol: str,
    execution_action: str,
    normalize_ai_report_diagnostics: Callable[..., Dict[str, Any]],
) -> Dict[str, Any]:
    return build_linked_trade_report_card_r4_impl(trade_report_meta, report_payloads, primary_symbol=primary_symbol, execution_action=execution_action, normalize_ai_report_diagnostics=normalize_ai_report_diagnostics, facade=_r3_sys.modules[__name__])


def build_unlinked_trade_report_card(
    *,
    execution_action: str,
    monitor_reason_text: str,
    symbol: str,
    normalize_ai_report_diagnostics: Callable[..., Dict[str, Any]],
    report_reason_human: Callable[[str], str],
    report_next_step: Callable[[str], str],
) -> Dict[str, Any]:
    return build_unlinked_trade_report_card_r4_impl(execution_action=execution_action, monitor_reason_text=monitor_reason_text, symbol=symbol, normalize_ai_report_diagnostics=normalize_ai_report_diagnostics, report_reason_human=report_reason_human, report_next_step=report_next_step, facade=_r3_sys.modules[__name__])


def load_trade_report_detail_payloads(
    trade_report_meta: Dict[str, Any],
    *,
    read_json: Callable[[Path], Dict[str, Any]],
) -> Dict[str, Any]:
    report_path = Path(str(trade_report_meta.get("trade_report_json_path") or ""))
    bundle_path = Path(str(trade_report_meta.get("aggregated_bundle_path") or ""))
    lifecycle_path = Path(str(trade_report_meta.get("trade_lifecycle_json_path") or ""))
    report_md_path = Path(str(trade_report_meta.get("trade_report_md_path") or ""))

    report_data = read_json(report_path) if report_path.exists() else {}
    bundle_data = read_json(bundle_path) if bundle_path.exists() else {}
    lifecycle_data = read_json(lifecycle_path) if lifecycle_path.exists() else {}

    return {
        "report_data": report_data if isinstance(report_data, dict) else {},
        "bundle_data": bundle_data if isinstance(bundle_data, dict) else {},
        "lifecycle_data": lifecycle_data if isinstance(lifecycle_data, dict) else {},
        "report_exists": bool(report_path.exists() or report_md_path.exists()),
        "paths": {
            "report_json_path": str(report_path) if report_path.exists() else "",
            "report_md_path": str(report_md_path) if report_md_path.exists() else "",
            "bundle_path": str(bundle_path) if bundle_path.exists() else "",
            "lifecycle_path": str(lifecycle_path) if lifecycle_path.exists() else "",
        },
    }


def load_operator_brief_detail_payloads(
    trade_report_meta: Dict[str, Any],
    *,
    read_json: Callable[[Path], Dict[str, Any]],
    allow_saved_brief: bool,
) -> Dict[str, Any]:
    json_path = Path(str(trade_report_meta.get("operator_brief_json_path") or ""))
    md_path = Path(str(trade_report_meta.get("operator_brief_md_path") or ""))
    brief_data: Dict[str, Any] = {}
    if allow_saved_brief and json_path.exists():
        brief_data = read_json(json_path)
        if not isinstance(brief_data, dict):
            brief_data = {}
    return {
        "brief_data": brief_data,
        "paths": {
            "operator_brief_json": str(json_path) if json_path.exists() else "",
            "operator_brief_md": str(md_path) if md_path.exists() else "",
        },
    }


def normalize_operator_brief_detail_payload(
    brief: Dict[str, Any],
    *,
    clean_str_list: Callable[..., List[str]],
) -> Dict[str, Any]:
    return normalize_operator_brief_detail_payload_r4_impl(brief, clean_str_list=clean_str_list, facade=_r3_sys.modules[__name__])


def build_operator_brief_detail_view(
    meta: Dict[str, Any],
    brief: Dict[str, Any],
    *,
    json_path: str,
    md_path: str,
    normalize_symbol: Callable[..., str],
    clean_str_list: Callable[..., List[str]],
) -> Dict[str, Any]:
    return build_operator_brief_detail_view_r4_impl(meta, brief, json_path=json_path, md_path=md_path, normalize_symbol=normalize_symbol, clean_str_list=clean_str_list, facade=_r3_sys.modules[__name__])


def extract_labeled_bullet(bullets: List[str], labels: List[str]) -> str:
    return extract_labeled_bullet_r4_impl(bullets, labels, facade=_r3_sys.modules[__name__])


def extract_labeled_int(bullets: List[str], labels: List[str]) -> Optional[int]:
    return extract_labeled_int_r4_impl(bullets, labels, facade=_r3_sys.modules[__name__])


def parse_canonical_filter_bullets(bullets: List[str]) -> List[Dict[str, str]]:
    return parse_canonical_filter_bullets_r4_impl(bullets, facade=_r3_sys.modules[__name__])


def normalize_canonical_monitor_snapshot(
    snapshot: Dict[str, Any],
    story_monitor: Dict[str, Any] | None = None,
    *,
    format_duration: Callable[[Any], str],
    format_percent: Callable[[Any, int], str],
    format_float: Callable[[Any, int], str],
    friendly_exit_reason: Callable[[Any], str],
) -> Dict[str, Any]:
    return normalize_canonical_monitor_snapshot_r4_impl(snapshot, story_monitor, format_duration=format_duration, format_percent=format_percent, format_float=format_float, friendly_exit_reason=friendly_exit_reason, facade=_r3_sys.modules[__name__])


def brief_headline_text(row: Any, *, trim_text: Callable[..., str]) -> str:
    return brief_headline_text_r4_impl(row, trim_text=trim_text, facade=_r3_sys.modules[__name__])


def brief_norm_symbol_text(value: Any, *, normalize_symbol: Callable[..., str]) -> str:
    return normalize_symbol(value, allow_test_symbols=True).strip().upper()


def brief_headline_matches_symbol(
    row: Any,
    symbol: str,
    *,
    normalize_symbol: Callable[..., str],
) -> bool:
    return brief_headline_matches_symbol_r4_impl(row, symbol, normalize_symbol=normalize_symbol, facade=_r3_sys.modules[__name__])


def brief_collect_top_headlines(
    rows: Any,
    *,
    limit: int = 3,
    symbol: str = "",
    trim_text: Callable[..., str],
    normalize_symbol: Callable[..., str],
) -> List[str]:
    return brief_collect_top_headlines_r4_impl(rows, limit=limit, symbol=symbol, trim_text=trim_text, normalize_symbol=normalize_symbol, facade=_r3_sys.modules[__name__])


def brief_top_numeric_drivers(values: Any, *, limit: int = 4) -> Dict[str, float]:
    return brief_top_numeric_drivers_r4_impl(values, limit=limit, facade=_r3_sys.modules[__name__])


def load_trade_report_payloads(
    trade_report_meta: Dict[str, Any],
    *,
    read_json: Callable[[Path], Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    trade_root_path = Path(str(trade_report_meta.get("trade_root_path") or ""))
    normalized_story_input = trade_root_path / "ai_trade_report_input.json"
    normalized_lifecycle = trade_root_path / "lifecycle_bundle.json"
    normalized_report_json = trade_root_path / "reports" / "ai_trade_report.json"
    legacy_story_input = trade_root_path / "ai_trade_report" / "ai_trade_report_input.json"
    legacy_lifecycle = trade_root_path / "lifecycle" / "trade_lifecycle.json"
    legacy_report_json = trade_root_path / "ai_trade_report" / "ai_trade_report.json"

    story_input_meta_path = Path(str(trade_report_meta.get("trade_story_input_path") or ""))
    lifecycle_meta_path = Path(str(trade_report_meta.get("trade_lifecycle_json_path") or ""))
    report_meta_path = Path(str(trade_report_meta.get("trade_report_json_path") or ""))
    aggregated_bundle_path = Path(str(trade_report_meta.get("aggregated_bundle_path") or ""))

    story_input_path = _pick_first_existing(normalized_story_input, legacy_story_input, story_input_meta_path)
    lifecycle_path = _pick_first_existing(normalized_lifecycle, legacy_lifecycle, lifecycle_meta_path)
    report_json_path = _pick_first_existing(normalized_report_json, legacy_report_json, report_meta_path)

    story_input_data = read_json(story_input_path) if story_input_path.exists() else {}
    lifecycle_data = read_json(lifecycle_path) if lifecycle_path.exists() else {}
    report_data = read_json(report_json_path) if report_json_path.exists() else {}

    bundle_data = read_json(aggregated_bundle_path) if aggregated_bundle_path.exists() else {}
    if not bundle_data and normalized_lifecycle.exists():
        bundle_data = read_json(normalized_lifecycle)
    if not bundle_data and legacy_lifecycle.exists():
        bundle_data = read_json(legacy_lifecycle)
    canonical_fallback = (
        bundle_data.get("canonical_agent_artifacts")
        if isinstance(bundle_data.get("canonical_agent_artifacts"), dict)
        else {}
    )

    story_source = (
        "normalized_trade_artifact"
        if story_input_path == normalized_story_input and story_input_path.exists()
        else ("direct_artifact" if story_input_path.exists() else "missing")
    )
    lifecycle_source = (
        "normalized_trade_artifact"
        if lifecycle_path == normalized_lifecycle and lifecycle_path.exists()
        else ("direct_artifact" if lifecycle_path.exists() else "missing")
    )
    report_source = (
        "normalized_trade_artifact"
        if report_json_path == normalized_report_json and report_json_path.exists()
        else ("direct_artifact" if report_json_path.exists() else "missing")
    )

    return {
        "story_input_data": story_input_data if isinstance(story_input_data, dict) else {},
        "lifecycle_data": lifecycle_data if isinstance(lifecycle_data, dict) else {},
        "report_data": report_data if isinstance(report_data, dict) else {},
        "payload_sources": {
            "story_input": story_source,
            "lifecycle": lifecycle_source,
            "report": report_source,
            "canonical_fallback": "canonical_artifact" if canonical_fallback else "missing",
        },
        "paths": {
            "story_input_path": str(story_input_path) if story_input_path.exists() else "",
            "lifecycle_path": str(lifecycle_path) if lifecycle_path.exists() else "",
            "report_path": str(report_json_path) if report_json_path.exists() else "",
            "aggregated_bundle_path": str(aggregated_bundle_path) if aggregated_bundle_path.exists() else "",
        },
    }

def build_trade_read_model(trade_dir: str) -> Dict[str, Any]:
    """Phase 6-1 Task 1: Build a deterministic read model for a single trade lifecycle."""
    import json
    from datetime import datetime

    def _safe_float(v: Any, default: float = 0.0) -> float:
        try:
            return float(v)
        except Exception:
            return float(default)

    def _clip(s: Any, max_len: int = 255) -> str:
        text = str(s or "").strip()
        if not text or text.lower() in ("none", "null", "unavailable", "nan"):
            return "unknown"
        return text[:max_len]

    def _is_meaningful(v: Any) -> bool:
        text = str(v or "").strip().lower()
        return bool(text and text not in {"unknown", "none", "null", "unavailable", "nan"})

    def _pick_with_source(candidates: List[tuple[str, Any]], *, default: str = "unknown") -> tuple[str, str]:
        for source_key, raw in candidates:
            clipped = _clip(raw)
            if _is_meaningful(clipped):
                return clipped, source_key
        return str(default), "default"

    def _read_json(path: Path) -> Dict[str, Any]:
        try:
            if path.exists():
                payload = json.loads(path.read_text(encoding="utf-8"))
                return payload if isinstance(payload, dict) else {}
        except Exception:
            pass
        return {}

    def _trim_text(value: Any, max_len: int = 255) -> str:
        return str(value or "").strip()[:max_len]

    def _clean_str_list(value: Any, *, limit: int = 6, max_len: int = 220) -> List[str]:
        out: List[str] = []
        if not isinstance(value, list):
            return out
        for item in value[:limit]:
            text = str(item or "").strip()
            if not text:
                continue
            out.append(text[:max_len])
        return out

    td = Path(str(trade_dir))
    trade_report_meta = {
        "trade_root_path": str(td),
        "trade_story_input_path": "",
        "trade_lifecycle_json_path": "",
        "trade_report_json_path": "",
        "aggregated_bundle_path": "",
    }
    report_payloads = load_trade_report_payloads(trade_report_meta, read_json=_read_json)
    artifacts, bundle, canonical, commander_art, entry_obj, entry_ts, entry_ts_source, evidence_provenance, executor_art, exit_obj, exit_ts, exit_ts_source, filters_human, hold_duration_sec, hold_duration_source, holding_obj, lifecycle, lifecycle_path_used, market_context_human, monitor_art, monitor_reason_human, report, report_data, report_path_used, same_day_linkage, scanner_art, scanner_reason_human, shared_facts, story_meta, strategist_art = selected_trade_artifacts(report_payloads=report_payloads, _pick_with_source=_pick_with_source, facade=_r3_sys.modules[__name__])
    if hold_duration_sec <= 0 and entry_ts != "unknown" and exit_ts != "unknown":
        try:
            e1 = entry_ts.replace("Z", "+00:00")
            e2 = exit_ts.replace("Z", "+00:00")
            dt1 = datetime.fromisoformat(e1)
            dt2 = datetime.fromisoformat(e2)
            hold_duration_sec = int((dt2 - dt1).total_seconds())
            hold_duration_source = "derived.timestamp_diff"
        except Exception:
            pass
    blocker_trace, data_source_quality, execution_label_value, facts, monitor_exit_trigger, playbook_value, provenance, same_day_reason, same_day_status, stop_policy_trace, strategy_policy_source_value, thresholds_snapshot, watch_axes = read_truth_blocker_trace_data_source_quality(hold_duration_sec=hold_duration_sec, _pick_with_source=_pick_with_source, exit_obj=exit_obj, shared_facts=shared_facts, bundle=bundle, report_data=report_data, entry_obj=entry_obj, monitor_art=monitor_art, scanner_art=scanner_art, strategist_art=strategist_art, commander_art=commander_art, lifecycle=lifecycle, executor_art=executor_art, entry_ts=entry_ts, exit_ts=exit_ts, _safe_float=_safe_float, report=report, artifacts=artifacts, _clip=_clip, same_day_linkage=same_day_linkage, story_meta=story_meta, evidence_provenance=evidence_provenance, entry_ts_source=entry_ts_source, exit_ts_source=exit_ts_source, hold_duration_source=hold_duration_source, td=td, lifecycle_path_used=lifecycle_path_used, report_path_used=report_path_used, canonical=canonical, facade=_r3_sys.modules[__name__])
    context = read_display_context(report_data=report_data, _trim_text=_trim_text, _clean_str_list=_clean_str_list, entry_obj=entry_obj, scanner_reason_human=scanner_reason_human, monitor_reason_human=monitor_reason_human, filters_human=filters_human, market_context_human=market_context_human, bundle=bundle, lifecycle=lifecycle, holding_obj=holding_obj, monitor_exit_trigger=monitor_exit_trigger, thresholds_snapshot=thresholds_snapshot, stop_policy_trace=stop_policy_trace, blocker_trace=blocker_trace, same_day_status=same_day_status, same_day_reason=same_day_reason, data_source_quality=data_source_quality, _clip=_clip, playbook_value=playbook_value, strategy_policy_source_value=strategy_policy_source_value, execution_label_value=execution_label_value, watch_axes=watch_axes, scanner_art=scanner_art, executor_art=executor_art, monitor_art=monitor_art, facade=_r3_sys.modules[__name__])[0]

    return {
        **facts,
        "facts": dict(facts),
        "provenance": provenance,
        "context": context,
    }


__all__ = [
    "trade_report_artifact_payload",
    "prefer_richer_trade_report_section",
    "trade_report_section_summary",
    "trade_report_section_bullets",
    "normalize_trade_report_section",
    "normalize_trade_report_detail_sections",
    "extract_strategy_memory_record",
    "normalize_trade_report_detail_meta",
    "build_trade_report_detail_view",
    "collect_strategist_feedback_inputs",
    "build_recent_trade_feedback_summary_input",
    "build_trade_report_recent_feedback_view",
    "build_trade_report_recent_feedback_pack",
    "load_trade_report_recent_feedback_pack",
    "load_time_bucketed_trade_report_recent_feedback_pack",
    "load_reporter_snippet_for_run",
    "build_linked_trade_report_card",
    "build_unlinked_trade_report_card",
    "load_trade_report_detail_payloads",
    "load_operator_brief_detail_payloads",
    "normalize_operator_brief_detail_payload",
    "build_operator_brief_detail_view",
    "extract_labeled_bullet",
    "extract_labeled_int",
    "parse_canonical_filter_bullets",
    "normalize_canonical_monitor_snapshot",
    "brief_headline_text",
    "brief_norm_symbol_text",
    "brief_headline_matches_symbol",
    "brief_collect_top_headlines",
    "brief_top_numeric_drivers",
    "load_trade_report_payloads",
    "build_trade_read_model",
]
