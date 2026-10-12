from __future__ import annotations

import ast
import html
import json
import logging
import os
import re
import threading
import time
from typing import Any, Dict, List, Optional

from libs.reporting.trade_report.ai_facade_parts.duration_language import (
    _humanize_duration_text_impl,
    _holding_duration_label_impl,
    _korean_predicate_impl,
    _korean_euro_ro_impl,
)
from libs.reporting.trade_report.ai_facade_parts.market_labels import (
    _market_token_label_impl,
    _theme_token_label_impl,
    _theme_text_impl,
    _theme_linkage_label_impl,
    _risk_mode_label_impl,
    _strategy_constraint_label_impl,
    _strategy_constraint_text_impl,
    _scanner_bias_label_impl,
    _scanner_bias_text_impl,
)
from libs.reporting.trade_report.ai_facade_parts.scanner_labels import (
    _scanner_source_label_impl,
    _scanner_source_text_impl,
    _scanner_score_driver_label_impl,
    _scanner_chart_feature_label_impl,
    _scanner_check_name_label_impl,
    _scanner_check_status_label_impl,
    _entry_reason_label_impl,
    _decision_chain_label_impl,
    _execution_mode_label_impl,
    _entry_path_label_impl,
    _entry_gate_state_label_impl,
    _entry_gate_name_label_impl,
)
from libs.reporting.trade_report.ai_facade_parts.text_helpers import (
    _is_low_information_bullet_impl,
    _count_hangul_impl,
    _count_latin_impl,
    _first_nonempty_text_impl,
    _has_evidence_payload_impl,
    _as_action_impl,
)
from libs.llm.json_response import parse_llm_json_response, required_key_metadata
from libs.llm.model_catalog import build_execution_profile_observability, resolve_policy_llm_execution_slot, resolve_policy_llm_slot
from libs.llm.model_names import normalize_openrouter_model_name
from libs.llm.llm_router import LLMRouter
from libs.reporting.llm_artifacts import build_llm_response_artifact, classify_llm_exception, make_attempt
from libs.reporting.trade_price_truth import resolve_trade_price_truth
from libs.reporting.execution_truth_surface import build_execution_truth_bullets
from libs.reporting.trade_memory_application_surface import build_trade_memory_application_surface
from libs.reporting.trade_memory_surface import build_trade_report_memory_surface
from libs.reporting.report_truth_surface import build_trade_report_truth_surface
from libs.reporting.trade_execution_outcome_text import execution_outcome_summary_is_placeholder
from libs.reporting.trade_reporter_status_text import normalize_reporter_text
from libs.reporting.trade_report_common import (
    compact_named_rows as _compact_named_rows,
    compact_scalar_dict as _compact_scalar_dict,
    dedupe_list as _dedupe_list,
    fmt_pct as _fmt_pct,
    fmt_price as _fmt_price,
    listify as _listify,
    report_clip as _clip,
    utc_now_iso as _utc_now_iso,
)
from libs.reporting.trade_report_ai_shared_facts import (
    resolve_trade_facts_with_precedence as _resolve_trade_facts_with_precedence_impl,
)
from libs.reporting.trade_report_ai_compact_input import (
    compact_section_seed_for_llm as _compact_section_seed_for_llm_impl,
    compact_story_input_for_llm as _compact_story_input_for_llm_impl,
    sparse_story_input_for_llm as _sparse_story_input_for_llm_impl,
)
from libs.reporting.trade_report_ai_compact_helpers import (
    compact_event_row as _compact_event_row_impl,
    compact_monitor_snapshot as _compact_monitor_snapshot_impl,
    compact_timeline_rows as _compact_timeline_rows_impl,
    tail_list as _tail_list_impl,
)
from libs.reporting.trade_report_ai_merge_policy import (
    is_scanner_execution_mismatch_text as _is_scanner_execution_mismatch_text_impl,
    is_scanner_selection_label_line as _is_scanner_selection_label_line_impl,
    merge_bullets_with_fallback as _merge_bullets_with_fallback_impl,
    merge_section_with_fallback as _merge_section_with_fallback_impl,
    prefer_fallback_summary as _prefer_fallback_summary_impl,
    prefer_fallback_text as _prefer_fallback_text_impl,
    trade_report_priority_bullet_prefixes as _trade_report_priority_bullet_prefixes_impl,
)
from libs.reporting.trade_report_ai_prompting import (
    build_concise_trade_report_messages as _build_concise_trade_report_messages_impl,
    build_messages as _build_messages_impl,
    build_repair_messages as _build_repair_messages_impl,
    prompt_story_input_for_llm as _prompt_story_input_for_llm_impl,
    trade_report_output_template as _trade_report_output_template_impl,
)
from libs.reporting.trade_report_ai_deterministic import (
    append_news_scanner_choice_details as _append_news_scanner_choice_details_impl,
    attach_backward_compatible_aliases as _attach_backward_compatible_aliases_impl,
    build_monitor_snapshot as _build_monitor_snapshot_impl,
    build_shared_facts as _build_shared_facts_impl,
    build_deterministic_trade_report as _build_deterministic_trade_report_impl,
    enrich_market_context_for_fallback as _enrich_market_context_for_fallback_impl,
    enrich_scanner_reason_for_fallback as _enrich_scanner_reason_for_fallback_impl,
    fallback_section_seeds as _fallback_section_seeds_impl,
    fallback_report as _fallback_report_impl,
    failure_report as _failure_report_impl,
    merge_trade_report_candidate as _merge_trade_report_candidate_impl,
)
from libs.reporting.trade_report_ai_llm import run_trade_report_llm_attempts as _run_trade_report_llm_attempts_impl
from libs.reporting.trade_report.normalization import normalize_trade_report_output as _normalize_trade_report_output_impl
from libs.reporting.trade_report.context import (
    compact_strategist_report_context as _compact_strategist_report_context_impl,
    extract_entry_execution_visibility as _extract_entry_execution_visibility_impl,
)
from libs.reporting.trade_report.sections import (
    select_entry_decision_detail as _select_entry_decision_detail_impl,
    resolve_entry_monitor_reason as _resolve_entry_monitor_reason_impl,
    build_reporter_evaluation_section as _build_reporter_evaluation_section_impl,
    build_reporter_evaluation_from_feedback as _build_reporter_evaluation_from_feedback_impl,
    build_holding_story_bullets as _build_holding_story_bullets_impl,
    build_exit_decision_bullets as _build_exit_decision_bullets_impl,
    build_execution_quality_section as _build_execution_quality_section_impl,
    build_entry_decision_summary as _build_entry_decision_summary_impl,
    build_entry_decision_bullets as _build_entry_decision_bullets_impl,
    build_market_context_bullets as _build_market_context_bullets_impl,
    build_market_context_summary as _build_market_context_summary_impl,
    build_market_scanner_linkage_bullet as _build_market_scanner_linkage_bullet_impl,
    build_scanner_candidate_comparison_section as _build_scanner_candidate_comparison_section_impl,
    build_scanner_choice_bullets as _build_scanner_choice_bullets_impl,
    build_scanner_choice_summary as _build_scanner_choice_summary_impl,
    build_shared_summary_seed as _build_shared_summary_seed_impl,
    build_strategist_summary_section as _build_strategist_summary_section_impl,
)
from libs.reporting.trade_report.operator_text import (
    exit_reason_label as _exit_reason_label_impl,
    normalize_trade_report_language as _normalize_trade_report_language_impl,
    operator_action_label as _operator_action_label_impl,
    operator_axis_label as _operator_axis_label_impl,
    operator_filter_label as _operator_filter_label_impl,
    operator_filter_status as _operator_filter_status_impl,
    operatorize_report_section as _operatorize_report_section_impl,
    operatorize_report_text as _operatorize_report_text_impl,
    preserve_legacy_trade_report_bullet as _preserve_legacy_trade_report_bullet_impl,
    safe_fullmatch as _safe_fullmatch_impl,
    sanitize_forbidden_scripts_text as _sanitize_forbidden_scripts_text_impl,
)
from libs.reporting.trade_report.service import (
    build_ai_trade_report_service as _build_ai_trade_report_service_impl,
    build_trade_summary_report_service as _build_trade_summary_report_service_impl,
)
from libs.reporting.trade_report_ai_summary_adapter import (
    AI_TRADE_SUMMARY_EVALUATION_KEYS,
    build_trade_summary_evaluation_messages as _build_trade_summary_evaluation_messages_impl,
    deterministic_trade_summary_report as _deterministic_trade_summary_report_impl,
    normalize_trade_summary_evaluation as _normalize_trade_summary_evaluation_impl,
    trade_summary_evaluation_template as _trade_summary_evaluation_template_impl,
    trade_summary_parse_meta as _trade_summary_parse_meta_impl,
)
from libs.reporting.truth_source_labels import (
    monitor_price_source_label,
    pnl_truth_source_label,
    price_truth_source_label,
    truth_availability_line,
)
from libs.runtime.strategist_explanation import build_strategy_refresh_trace
import sys as _r3_sys
from libs.reporting.trade_report.ai_facade_r3_parts.bodies_01 import (
    _normalize_section_r3_impl,
    _actual_lifecycle_action_r3_impl,
    _reporter_summary_is_placeholder_r3_impl,
    resolve_shared_trade_facts_r3_impl,
    _extract_korea_indices_snapshot_r3_impl,
    _format_korea_indices_sentence_r3_impl,
    _scanner_selected_row_r3_impl,
    _build_scanner_driver_summary_r3_impl,
    _build_runner_up_comparison_r3_impl,
)
from libs.reporting.trade_report.ai_facade_r3_parts.bodies_02 import (
    _has_noisy_trade_report_text_r3_impl,
    _build_scanner_filters_summary_r3_impl,
    _looks_like_post_entry_monitor_snapshot_r3_impl,
    _build_exit_decision_summary_r3_impl,
    _compact_entry_or_exit_summary_r3_impl,
    _extract_policy_ref_context_r3_impl,
    _extract_scanner_bias_summary_r3_impl,
)
from libs.reporting.trade_report.ai_facade_r3_parts.bodies_03 import (
    _extract_strategy_detail_from_source_r3_impl,
    _compact_strategy_detail_context_r3_impl,
    _enrich_candidate_watch_proposal_from_entry_control_r3_impl,
    _compact_commander_entry_control_r3_impl,
    _compact_entry_candidate_cascade_r3_impl,
    _entry_execution_visibility_summary_r3_impl,
)
from libs.reporting.trade_report.ai_facade_r3_parts.bodies_04 import (
    _extract_strategist_report_context_r3_impl,
    _build_report_strategist_refresh_trace_r3_impl,
    _compact_strategy_refresh_trace_r3_impl,
    _compact_memory_application_trace_r3_impl,
    _normalize_provenance_entry_r3_impl,
    _report_section_provenance_r3_impl,
)
from libs.reporting.trade_report.ai_facade_r3_parts.bodies_05 import (
    _attach_report_status_matrix_r3_impl,
)

logger = logging.getLogger(__name__)


def _safe_fullmatch(pattern: str, text: str, *, flags: int = 0):
    return _safe_fullmatch_impl(pattern, text, flags=flags)

def _resolve_intraday_report_model(source: Dict[str, Any] | None, *, explicit_model: Optional[str] = None) -> str:
    resolved = resolve_policy_llm_slot(source if isinstance(source, dict) else {}, "reporter", "intraday", default_profile="fast_free")
    return normalize_openrouter_model_name(
        str(explicit_model or "").strip()
        or str(resolved.get("primary") or "").strip()
        or "minimax/minimax-m2.5"
    )


def _resolve_intraday_report_execution_profile(source: Dict[str, Any] | None) -> Dict[str, Any]:
    return resolve_policy_llm_execution_slot(
        source if isinstance(source, dict) else {},
        "reporter",
        "intraday",
        default_profile="concise_review",
        defaults={
            "profile_name": "concise_review",
            "name": "concise_review",
            "temperature": 0.2,
            "max_tokens": 3072,
            "timeout_sec": 15,
            "retry": {"max_attempts": 1, "backoff_sec": 0.0},
            "retry_max": 1,
            "retry_backoff_sec": 0.0,
        },
    )


def _router_chat_with_hard_timeout(
    router: LLMRouter,
    role: str,
    messages: List[Dict[str, Any]],
    *,
    policy: Optional[Dict[str, Any]] = None,
    hard_timeout_sec: Optional[float] = None,
) -> str:
    if hard_timeout_sec in (None, "", 0):
        return router.chat(role, messages, policy=policy)
    timeout_value = max(0.1, float(hard_timeout_sec or 0.0))
    result: Dict[str, Any] = {}
    failure: Dict[str, Exception] = {}
    done = threading.Event()

    def _run() -> None:
        try:
            result["value"] = router.chat(role, messages, policy=policy)
        except Exception as exc:
            failure["exc"] = exc
        finally:
            done.set()

    worker = threading.Thread(target=_run, name="trade-report-chat", daemon=True)
    worker.start()
    if not done.wait(timeout_value):
        raise TimeoutError(f"trade_report_ai hard timeout after {timeout_value:.1f}s")
    if "exc" in failure:
        raise failure["exc"]
    return str(result.get("value") or "")


def _is_low_information_bullet(value: Any) -> bool:
    return _is_low_information_bullet_impl(value, _safe_fullmatch=_safe_fullmatch)


def _count_hangul(text: Any) -> int:
    return _count_hangul_impl(text)


def _count_latin(text: Any) -> int:
    return _count_latin_impl(text)


def _count_forbidden_cjk_or_japanese(text: Any) -> int:
    raw = str(text or "")
    # Korean-only policy for human-readable sentences.
    return len(re.findall(r"[\u3040-\u30ff\u4e00-\u9fff]", raw))


AI_TRADE_REPORT_REQUIRED_KEYS = [
    "executive_summary",
    "market_context_at_entry",
    "why_this_symbol_was_chosen",
    "entry_decision",
    "holding_monitoring_story",
    "exit_decision",
    "execution_quality",
    "scanner_filters",
    "guard_approval_result",
    "reporter_evaluation",
    "errors_weaknesses_improvement_points",
    "final_operator_conclusion",
]

AI_TRADE_REPORT_KOREAN_RULES = (
    "사람이 읽는 모든 값은 반드시 한국어로 작성해야 합니다. "
    "All human-readable sentences must be Korean. "
    "Do not use Japanese or Chinese sentences. "
    "Allowed unchanged tokens: symbol code, ISO timestamp, BUY/SELL/HOLD/WAIT, VIX, "
    "top_value/top_volume/sector_theme, not_captured."
)



def _sanitize_forbidden_scripts_text(text: Any) -> str:
    return _sanitize_forbidden_scripts_text_impl(text)

def _sanitize_report_language_fields(value: Any) -> Any:
    if isinstance(value, str):
        return _sanitize_forbidden_scripts_text(value)
    if isinstance(value, list):
        return [_sanitize_report_language_fields(item) for item in value]
    if isinstance(value, dict):
        return {key: _sanitize_report_language_fields(item) for key, item in value.items()}
    return value


def _env_bool(name: str, default: bool = True) -> bool:
    raw = str(os.getenv(name, "1" if default else "0")).strip().lower()
    return raw in {"1", "true", "yes", "on"}


def _normalize_section(section: Any, *, default_summary: str = "", bullet_key: str = "bullets") -> Dict[str, Any]:
    return _normalize_section_r3_impl(section, default_summary=default_summary,
        bullet_key=bullet_key, facade=_r3_sys.modules[__name__])


def _actual_lifecycle_action(story_input: Dict[str, Any]) -> str:
    return _actual_lifecycle_action_r3_impl(story_input, facade=_r3_sys.modules[__name__])


def _first_nonempty_text(*values: Any, max_len: int = 240) -> str:
    return _first_nonempty_text_impl(*values, max_len=max_len, _clip=_clip)


def _has_evidence_payload(value: Any) -> bool:
    return _has_evidence_payload_impl(value)


def _as_dict(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _as_action(value: Any) -> str:
    return _as_action_impl(value, _clip=_clip)


def _as_status(value: Any) -> str:
    text = _clip(value, max_len=32).lower()
    if text == "opened":
        return "open"
    if text == "closed_out":
        return "closed"
    return text


def _action_from_exit_reason(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""
    if "sell" in text or "매도" in text or "청산" in text:
        return "SELL"
    return ""


def _is_open_position_placeholder_reason(value: Any) -> bool:
    text = str(value or "").strip().lower()
    if not text:
        return False
    markers = (
        "no_position",
        "no position",
        "position is still open",
        "monitor is watching for exit",
        "still open",
        "포지션이 아직",
    )
    return any(token in text for token in markers)


def _is_hold_placeholder_exit_reason(value: Any) -> bool:
    text = str(value or "").strip()
    if not text:
        return False
    normalized = re.sub(r"^sell\s+was\s+triggered\s+because\s*", "", text, flags=re.IGNORECASE)
    normalized = normalized.strip().strip(".").strip().lower()
    return normalized in {"hold", "hold_position", "holding", "보유", "보유 유지"} or "because hold" in text.lower()


def _lifecycle_summary_conflicts_with_status(value: Any, status: Any) -> bool:
    text = str(value or "").strip().lower()
    status_text = str(status or "").strip().lower()
    if not text or not status_text:
        return False
    if status_text == "closed" and (" is partial" in text or "status is partial" in text):
        return True
    if status_text == "partial" and (" is closed" in text or "status is closed" in text):
        return True
    return False


def _story_post_exit_shadow(story_input: Dict[str, Any]) -> Dict[str, Any]:
    for candidate in (
        _as_dict(story_input.get("post_exit_shadow")),
        _as_dict(_as_dict(story_input.get("lifecycle_bundle")).get("post_exit_shadow")),
        _as_dict(_as_dict(story_input.get("trade_lifecycle")).get("post_exit_shadow")),
        _as_dict(_as_dict(_as_dict(story_input.get("trade_lifecycle")).get("exit")).get("post_exit_shadow")),
        _as_dict(_as_dict(_as_dict(story_input.get("lifecycle_bundle")).get("exit")).get("post_exit_shadow")),
    ):
        if candidate:
            return candidate
    return {}


def _reporter_summary_is_placeholder(value: Any) -> bool:
    return _reporter_summary_is_placeholder_r3_impl(value, facade=_r3_sys.modules[__name__])


def _resolve_trade_facts_with_precedence(story_input: Dict[str, Any]) -> Dict[str, Any]:
    return _resolve_trade_facts_with_precedence_impl(
        story_input,
        load_trade_read_model_hint=_load_trade_read_model_hint,
        humanize_duration_text=_humanize_duration_text,
        actual_lifecycle_action=_actual_lifecycle_action,
    )

def _build_shared_summary_seed(story_input: Dict[str, Any]) -> Dict[str, Any]:
    return _build_shared_summary_seed_impl(
        story_input,
        deps={
            "as_dict": _as_dict,
            "load_trade_read_model_hint": _load_trade_read_model_hint,
            "resolve_trade_facts_with_precedence": _resolve_trade_facts_with_precedence,
            "resolve_trade_price_truth": resolve_trade_price_truth,
            "clip": _clip,
            "as_action": _as_action,
            "as_status": _as_status,
            "has_evidence_payload": _has_evidence_payload,
            "first_nonempty_text": _first_nonempty_text,
            "listify": _listify,
            "compact_commander_entry_control": _compact_commander_entry_control,
            "first_dict_from": _first_dict_from,
            "compact_scalar_dict": _compact_scalar_dict,
            "extract_entry_execution_visibility": _extract_entry_execution_visibility,
        },
    )

def resolve_shared_trade_facts(story_input: Dict[str, Any]) -> Dict[str, Any]:
    return resolve_shared_trade_facts_r3_impl(story_input, facade=_r3_sys.modules[__name__])


def _normalize_trade_report_output(story_input: Dict[str, Any], report: Dict[str, Any]) -> Dict[str, Any]:
    return _normalize_trade_report_output_impl(
        story_input,
        report,
        deps={
            "build_shared_summary_seed": _build_shared_summary_seed,
            "clip": _clip,
            "actual_lifecycle_action": _actual_lifecycle_action,
            "action_from_exit_reason": _action_from_exit_reason,
            "lifecycle_summary_conflicts_with_status": _lifecycle_summary_conflicts_with_status,
            "exit_reason_label": _exit_reason_label,
            "compact_strategist_report_context": _compact_strategist_report_context,
            "as_dict": _as_dict,
            "build_report_strategist_refresh_trace": _build_report_strategist_refresh_trace,
            "extract_entry_execution_visibility": _extract_entry_execution_visibility,
            "story_post_exit_shadow": _story_post_exit_shadow,
            "is_low_information_bullet": _is_low_information_bullet,
            "report_section_provenance": _report_section_provenance,
            "normalize_provenance_entry": _normalize_provenance_entry,
            "operatorize_report_section": _operatorize_report_section,
            "listify": _listify,
            "is_open_position_placeholder_reason": _is_open_position_placeholder_reason,
            "build_trade_report_truth_surface": build_trade_report_truth_surface,
            "build_trade_report_memory_surface": build_trade_report_memory_surface,
            "build_trade_memory_application_surface": build_trade_memory_application_surface,
            "sanitize_report_language_fields": _sanitize_report_language_fields,
        },
    )

def _tail_list(values: Any, *, max_items: int = 6, max_len: int = 220) -> List[str]:
    return _tail_list_impl(values, max_items=max_items, max_len=max_len)


def _compact_event_row(row: Any) -> Dict[str, Any]:
    return _compact_event_row_impl(row)


def _compact_timeline_rows(values: Any, *, head: int = 3, tail: int = 9) -> List[Dict[str, Any]]:
    return _compact_timeline_rows_impl(values, head=head, tail=tail)


def _compact_monitor_snapshot(section: Any) -> Dict[str, Any]:
    return _compact_monitor_snapshot_impl(
        section,
        compact_entry_candidate_cascade=_compact_entry_candidate_cascade,
    )

def _is_market_context_noise_bullet(value: Any) -> bool:
    text = _clip(value, max_len=260).strip()
    if not text:
        return True
    lowered = text.lower()
    if lowered.startswith("news input:"):
        return True
    if lowered.startswith("news query targets:"):
        return True
    if "headlines were considered across" in lowered:
        return True
    if text.startswith("뉴스 입력 요약은"):
        return True
    if text.startswith("뉴스 조회 대상은"):
        return True
    if "관련 헤드라인" in text and "반영" in text:
        return True
    return False


def _sanitize_market_context_summary(value: Any) -> str:
    text = _clip(value, max_len=600).strip()
    if not text:
        return ""
    cleaned = re.sub(
        r"[^.]*\b\d+\s*headlines were considered across \d+\s*targets[^.]*\.?\s*",
        " ",
        text,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"[^.]*관련 헤드라인\s*\d+건[^.]*\.?\s*",
        " ",
        cleaned,
    )
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip(" .")
    return cleaned or text


def _num_opt(value: Any) -> Optional[float]:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except Exception:
        return None


def _clean_news_title(value: Any, *, max_len: int = 220) -> str:
    text = html.unescape(_clip(value, max_len=max_len).strip())
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip(" .;")
    return text


def _market_token_label(value: Any) -> str:
    return _market_token_label_impl(value, _clip=_clip)

def _theme_token_label(value: Any) -> str:
    return _theme_token_label_impl(value, _clip=_clip)

def _theme_text(values: Any, *, max_items: int = 4) -> str:
    return _theme_text_impl(values, max_items=max_items, _theme_token_label=_theme_token_label, _listify=_listify)

def _theme_linkage_label(values: Any) -> str:
    return _theme_linkage_label_impl(values, _listify=_listify, _theme_text=_theme_text)

def _risk_mode_label(value: Any) -> str:
    return _risk_mode_label_impl(value, _clip=_clip)

def _strategy_constraint_label(value: Any) -> str:
    return _strategy_constraint_label_impl(value, _clip=_clip)

def _strategy_constraint_text(values: Any, *, max_items: int = 4) -> str:
    return _strategy_constraint_text_impl(values, max_items=max_items, _strategy_constraint_label=_strategy_constraint_label, _listify=_listify)

def _scanner_bias_label(value: Any) -> str:
    return _scanner_bias_label_impl(value, _clip=_clip)

def _scanner_bias_text(summary: Any) -> str:
    return _scanner_bias_text_impl(summary, ast=ast, _scanner_bias_label=_scanner_bias_label, _listify=_listify, _clip=_clip)

def _extract_us_indices_snapshot(events: Any) -> Dict[str, float]:
    for row in _listify(events, max_items=8, max_len=220):
        match = re.search(
            r"sp500=([+-]?\d+(?:\.\d+)?)%\s+nasdaq=([+-]?\d+(?:\.\d+)?)%\s+dow=([+-]?\d+(?:\.\d+)?)%",
            str(row),
            flags=re.IGNORECASE,
        )
        if not match:
            continue
        return {
            "sp500": float(match.group(1)),
            "nasdaq": float(match.group(2)),
            "dow": float(match.group(3)),
        }
    return {}


def _extract_korea_indices_snapshot(section: Any) -> Dict[str, Dict[str, Any]]:
    return _extract_korea_indices_snapshot_r3_impl(section, facade=_r3_sys.modules[__name__])


def _format_korea_indices_sentence(indices: Dict[str, Dict[str, Any]]) -> str:
    return _format_korea_indices_sentence_r3_impl(indices, facade=_r3_sys.modules[__name__])


def _format_pct_points(value: Any) -> str:
    number = _num_opt(value)
    if number is None:
        return "-"
    return f"{number:+.2f}%"


def _select_symbol_headline(headlines: Any, symbol: str = "") -> str:
    cleaned_rows = [_clean_news_title(row) for row in _listify(headlines, max_items=20, max_len=240)]
    cleaned_rows = [row for row in cleaned_rows if row]
    if not cleaned_rows:
        return ""
    symbol_token = str(symbol or "").strip()
    if symbol_token:
        for row in cleaned_rows:
            if row.startswith(f"{symbol_token}:"):
                return row
    return cleaned_rows[0]


def _join_headlines(headlines: Any, *, max_items: int = 2, max_len: int = 180) -> str:
    cleaned = [_clean_news_title(row, max_len=max_len) for row in _listify(headlines, max_items=max_items, max_len=max_len)]
    cleaned = [row for row in cleaned if row]
    return "; ".join(cleaned)


def _section_builder_deps() -> Dict[str, Any]:
    return {
        "clip": _clip,
        "extract_korea_indices_snapshot": _extract_korea_indices_snapshot,
        "extract_us_indices_snapshot": _extract_us_indices_snapshot,
        "format_korea_indices_sentence": _format_korea_indices_sentence,
        "format_pct_points": _format_pct_points,
        "market_token_label": _market_token_label,
        "num_opt": _num_opt,
        "theme_text": _theme_text,
        "dedupe_list": _dedupe_list,
        "join_headlines": _join_headlines,
        "listify": _listify,
        "select_symbol_headline": _select_symbol_headline,
        "risk_mode_label": _risk_mode_label,
        "scanner_bias_text": _scanner_bias_text,
        "scanner_source_text": _scanner_source_text,
        "strategy_constraint_text": _strategy_constraint_text,
        "theme_linkage_label": _theme_linkage_label,
        "build_runner_up_comparison": _build_runner_up_comparison,
        "build_scanner_driver_summary": _build_scanner_driver_summary,
        "fmt_num": _fmt_num,
        "scanner_basis_text": _scanner_basis_text,
        "scanner_chart_feature_coverage": _scanner_chart_feature_coverage,
        "scanner_chart_feature_label": _scanner_chart_feature_label,
        "scanner_monitor_fallback_context": _scanner_monitor_fallback_context,
        "scanner_ranked_candidates": _scanner_ranked_candidates,
        "scanner_selected_row": _scanner_selected_row,
        "build_scanner_choice_bullets": _build_scanner_choice_bullets,
        "build_scanner_choice_summary": _build_scanner_choice_summary,
        "build_scanner_choice_bullets": _build_scanner_choice_bullets,
        "build_scanner_choice_summary": _build_scanner_choice_summary,
        "entry_gate_score_relation": _entry_gate_score_relation,
        "entry_path_label": _entry_path_label,
        "entry_reason_label": _entry_reason_label,
        "operator_action_label": _operator_action_label,
        "as_dict": _as_dict,
        "compact_entry_gate_snapshot": _compact_entry_gate_snapshot,
        "entry_gate_signature": _entry_gate_signature,
        "entry_snapshot_as_post_entry_observation": _entry_snapshot_as_post_entry_observation,
        "looks_like_post_entry_monitor_snapshot": _looks_like_post_entry_monitor_snapshot,
        "select_entry_decision_detail": _select_entry_decision_detail,
        "entry_gate_bits": _entry_gate_bits,
        "korean_predicate": _korean_predicate,
        "decision_chain_label": _decision_chain_label,
        "fmt_pct": _fmt_pct,
        "fmt_price": _fmt_price,
        "is_low_information_bullet": _is_low_information_bullet,
        "operator_axis_label": _operator_axis_label,
        "build_reporter_evaluation_from_feedback": _build_reporter_evaluation_from_feedback,
        "humanize_duration_text": _humanize_duration_text,
        "korean_euro_ro": _korean_euro_ro,
        "operatorize_report_text": _operatorize_report_text,
        "execution_mode_label": _execution_mode_label,
        "exit_reason_label": _exit_reason_label,
        "normalize_reporter_text": normalize_reporter_text,
        "build_execution_truth_bullets": build_execution_truth_bullets,
    }

def _build_market_context_summary(section: Any, *, scanner_reason: Dict[str, Any] | None = None) -> str:
    return _build_market_context_summary_impl(section, scanner_reason=scanner_reason, deps=_section_builder_deps())

def _build_market_context_bullets(section: Any, *, scanner_reason: Dict[str, Any] | None = None) -> List[str]:
    return _build_market_context_bullets_impl(section, scanner_reason=scanner_reason, deps=_section_builder_deps())

def _build_strategist_summary_section(
    market_context: Dict[str, Any],
    scanner_reason: Dict[str, Any],
) -> Dict[str, Any]:
    return _build_strategist_summary_section_impl(market_context, scanner_reason, deps=_section_builder_deps())

def _build_market_scanner_linkage_bullet(section: Any, scanner_reason: Dict[str, Any] | None = None) -> str:
    return _build_market_scanner_linkage_bullet_impl(section, scanner_reason, deps=_section_builder_deps())

def _fmt_num(value: Any, *, digits: int = 3) -> str:
    try:
        return f"{float(value):.{digits}f}"
    except Exception:
        return "-"


def _scanner_basis_text(scanner_reason: Dict[str, Any]) -> str:
    def _basis_label(value: Any) -> str:
        raw = _clip(value, max_len=120).strip()
        mapping = {
            "trading value": "거래대금",
            "theme and sector alignment": "섹터·테마 정렬",
            "sentiment support": "감성 지원",
            "top value": "거래대금 상위",
            "top volume": "거래량 상위",
            "momentum": "모멘텀",
            "trend": "추세",
            "confidence": "신뢰도",
        }
        return mapping.get(raw.lower(), raw)

    basis = scanner_reason.get("ranking_basis")
    if isinstance(basis, list):
        return ", ".join(_basis_label(item) for item in _listify(basis, max_items=4, max_len=80) if _basis_label(item))
    return _basis_label(_clip(basis, max_len=220))


def _scanner_source_label(value: Any) -> str:
    return _scanner_source_label_impl(value, _clip=_clip)

def _scanner_source_text(values: Any) -> str:
    return _scanner_source_text_impl(values, _scanner_source_label=_scanner_source_label, _listify=_listify)

def _scanner_score_driver_label(value: Any) -> str:
    return _scanner_score_driver_label_impl(value, _clip=_clip)

def _scanner_chart_feature_label(value: Any) -> str:
    return _scanner_chart_feature_label_impl(value, _clip=_clip)

def _scanner_ranked_candidates(scanner_reason: Dict[str, Any]) -> List[Dict[str, Any]]:
    for key in ("top_candidates", "ranked_candidates"):
        rows = [row for row in list(scanner_reason.get(key) or []) if isinstance(row, dict)]
        if rows:
            return rows[:5]
    trace = scanner_reason.get("scanner_selection_trace") if isinstance(scanner_reason.get("scanner_selection_trace"), dict) else {}
    return [row for row in list(trace.get("ranked_candidates") or []) if isinstance(row, dict)][:5]


def _scanner_selected_row(scanner_reason: Dict[str, Any]) -> Dict[str, Any]:
    return _scanner_selected_row_r3_impl(scanner_reason, facade=_r3_sys.modules[__name__])


def _scanner_monitor_fallback_context(scanner_reason: Dict[str, Any]) -> Dict[str, Any]:
    trace = scanner_reason.get("scanner_selection_trace") if isinstance(scanner_reason.get("scanner_selection_trace"), dict) else {}
    return {
        "used": bool(scanner_reason.get("monitor_fallback_used") or trace.get("monitor_fallback_used")),
        "scanner_top_pick_symbol": _clip(
            scanner_reason.get("scanner_top_pick_symbol") or trace.get("scanner_top_pick_symbol"),
            max_len=24,
        ),
        "reason": _operatorize_report_text(
            scanner_reason.get("monitor_fallback_reason") or trace.get("monitor_fallback_reason")
        ),
        "trigger_reason": _operatorize_report_text(
            scanner_reason.get("monitor_trigger_reason") or trace.get("monitor_trigger_reason")
        ),
    }


def _scanner_chart_feature_coverage(scanner_reason: Dict[str, Any]) -> Dict[str, Any]:
    trace = scanner_reason.get("scanner_selection_trace") if isinstance(scanner_reason.get("scanner_selection_trace"), dict) else {}
    row = trace.get("chart_feature_coverage") if isinstance(trace.get("chart_feature_coverage"), dict) else {}
    out = dict(row)
    present = int(float(out.get("present") or 0)) if _num_opt(out.get("present")) is not None else 0
    total = int(float(out.get("total") or 0)) if _num_opt(out.get("total")) is not None else 0
    present_keys = [str(x or "") for x in list(out.get("present_keys") or []) if str(x or "").strip()]
    missing_keys = [str(x or "") for x in list(out.get("missing_keys") or []) if str(x or "").strip()]
    if (present_keys or missing_keys) and not (
        present_keys
        and len(present_keys) == present
        and len(present_keys) + len(missing_keys) == total
    ):
        out["present_keys"] = []
        out["missing_keys"] = []
    return out


def _build_scanner_driver_summary(scanner_reason: Dict[str, Any]) -> str:
    return _build_scanner_driver_summary_r3_impl(scanner_reason, facade=_r3_sys.modules[__name__])


def _build_runner_up_comparison(
    row: Dict[str, Any],
    *,
    selected_symbol: str,
    selected_score: Optional[float],
    selected_risk: Optional[float],
) -> str:
    return _build_runner_up_comparison_r3_impl(row, selected_symbol=selected_symbol,
        selected_score=selected_score, selected_risk=selected_risk,
        facade=_r3_sys.modules[__name__])


def _build_scanner_choice_bullets(
    scanner_reason: Dict[str, Any],
    market_context: Dict[str, Any],
) -> List[str]:
    return _build_scanner_choice_bullets_impl(scanner_reason, market_context, deps=_section_builder_deps())

def _build_scanner_choice_summary(scanner_reason: Dict[str, Any], market_context: Dict[str, Any]) -> str:
    return _build_scanner_choice_summary_impl(scanner_reason, market_context, deps=_section_builder_deps())

def _build_scanner_candidate_comparison_section(
    scanner_reason: Dict[str, Any],
    market_context: Dict[str, Any],
) -> Dict[str, Any]:
    return _build_scanner_candidate_comparison_section_impl(scanner_reason, market_context, deps=_section_builder_deps())

def _has_noisy_trade_report_text(value: Any) -> bool:
    return _has_noisy_trade_report_text_r3_impl(value, facade=_r3_sys.modules[__name__])


def _scanner_check_name_label(value: Any) -> str:
    return _scanner_check_name_label_impl(value, _clip=_clip)

def _scanner_check_status_label(value: Any) -> str:
    return _scanner_check_status_label_impl(value, _clip=_clip)

def _build_scanner_filters_summary(filters_human: Dict[str, Any]) -> str:
    return _build_scanner_filters_summary_r3_impl(filters_human, facade=_r3_sys.modules[__name__])


def _build_scanner_filters_bullets(filters_human: Dict[str, Any]) -> List[str]:
    checks = [row for row in list(filters_human.get("checks") or []) if isinstance(row, dict)]
    if not checks:
        return _listify(filters_human.get("bullets"), max_items=10, max_len=260)
    bullets: List[str] = []
    for row in checks[:8]:
        label = _scanner_check_name_label(row.get("name"))
        status = _scanner_check_status_label(row.get("status"))
        detail = _operatorize_report_text(row.get("detail"))
        if detail:
            bullets.append(f"{label}은 {status}였습니다. 근거: {detail}")
        else:
            bullets.append(f"{label}은 {status}였습니다.")
    return _dedupe_list(bullets, max_items=10, max_len=260)


def _build_entry_decision_summary(
    entry_summary: Dict[str, Any],
    scanner_reason: Dict[str, Any],
    market_context: Dict[str, Any],
    monitor_reason: Dict[str, Any],
    action: str,
) -> str:
    return _build_entry_decision_summary_impl(entry_summary, scanner_reason, market_context, monitor_reason, action, deps=_section_builder_deps())

def _entry_reason_label(value: Any) -> str:
    return _entry_reason_label_impl(value, _clip=_clip)

def _exit_reason_label(value: Any) -> str:
    return _exit_reason_label_impl(value)

def _decision_chain_label(value: Any) -> str:
    return _decision_chain_label_impl(value, _clip=_clip)

def _humanize_duration_text(value: Any, *, fallback_seconds: Any = None) -> str:
    return _humanize_duration_text_impl(
        value, fallback_seconds=fallback_seconds, _clip=_clip, _safe_fullmatch=_safe_fullmatch
    )

def _holding_duration_label(value: Any) -> str:
    return _holding_duration_label_impl(value, _humanize_duration_text=_humanize_duration_text)

def _execution_mode_label(value: Any) -> str:
    return _execution_mode_label_impl(value, _clip=_clip)

def _entry_path_label(value: Any) -> str:
    return _entry_path_label_impl(value, _clip=_clip)

def _entry_gate_state_label(value: Any) -> str:
    return _entry_gate_state_label_impl(value)

def _entry_gate_name_label(value: str) -> str:
    return _entry_gate_name_label_impl(value)

def _entry_gate_score_relation(score: float, threshold: float) -> str:
    if abs(float(score) - float(threshold)) <= 1e-6:
        return "동일했습니다"
    return "상회했습니다" if float(score) > float(threshold) else "하회했습니다"


def _entry_gate_bits(grouped_trace: Dict[str, Any], entry_scores: Dict[str, Any] | None = None) -> List[str]:
    scores = entry_scores if isinstance(entry_scores, dict) else {}
    gate_bits: List[str] = []
    if "reclaim_gate_ok" in grouped_trace:
        gate_bits.append(f"{_entry_gate_name_label('reclaim')} {_entry_gate_state_label(grouped_trace.get('reclaim_gate_ok'))}")
    if "extension_ok" in grouped_trace:
        gate_bits.append(f"{_entry_gate_name_label('extension')} {_entry_gate_state_label(grouped_trace.get('extension_ok'))}")
    if "confidence_gate_ok" in grouped_trace:
        gate_bits.append(f"{_entry_gate_name_label('confidence gate')} {_entry_gate_state_label(grouped_trace.get('confidence_gate_ok'))}")
    elif "confidence_gate_ok" in scores:
        gate_bits.append(f"{_entry_gate_name_label('confidence gate')} {_entry_gate_state_label(scores.get('confidence_gate_ok'))}")
    return gate_bits


def _entry_gate_signature(source: Dict[str, Any]) -> tuple[Any, ...]:
    grouped_trace = _as_dict(source.get("entry_grouped_logic_trace"))
    entry_scores = _as_dict(source.get("entry_condition_scores"))
    return (
        grouped_trace.get("reclaim_gate_ok"),
        grouped_trace.get("extension_ok"),
        grouped_trace.get("confidence_gate_ok", entry_scores.get("confidence_gate_ok")),
        grouped_trace.get("triggered_path") or source.get("entry_condition_path"),
        entry_scores.get("confidence_score"),
        entry_scores.get("confidence_threshold"),
    )


def _compact_entry_gate_snapshot(source: Dict[str, Any]) -> Dict[str, Any]:
    grouped_trace = _as_dict(source.get("entry_grouped_logic_trace"))
    entry_scores = _as_dict(source.get("entry_condition_scores"))
    out: Dict[str, Any] = {}
    if grouped_trace:
        out["entry_grouped_logic_trace"] = grouped_trace
    if entry_scores:
        out["entry_condition_scores"] = entry_scores
    if source.get("entry_condition_path") not in (None, ""):
        out["entry_condition_path"] = source.get("entry_condition_path")
    if source.get("entry_reason") not in (None, ""):
        out["entry_reason"] = source.get("entry_reason")
    return out


def _looks_like_post_entry_monitor_snapshot(story_input: Dict[str, Any], monitor_reason: Dict[str, Any]) -> bool:
    return _looks_like_post_entry_monitor_snapshot_r3_impl(story_input, monitor_reason,
        facade=_r3_sys.modules[__name__])


def _entry_snapshot_as_post_entry_observation(monitor_reason: Dict[str, Any]) -> Dict[str, Any]:
    resolved = dict(monitor_reason or {})
    post_entry_snapshot = _compact_entry_gate_snapshot(monitor_reason)
    for key in (
        "entry_grouped_logic_trace",
        "entry_condition_scores",
        "entry_condition_path",
        "entry_condition_paths_passed",
        "entry_reason",
        "entry_thresholds",
    ):
        resolved.pop(key, None)
    if post_entry_snapshot:
        resolved["post_entry_gate_observation"] = post_entry_snapshot
        resolved["entry_gate_snapshot_source"] = "post_entry_monitor_snapshot_only"
    return resolved


def _select_entry_decision_detail(story_input: Dict[str, Any], entry_summary: Dict[str, Any]) -> Dict[str, Any]:
    return _select_entry_decision_detail_impl(story_input, entry_summary, deps=_section_builder_deps())

def _resolve_entry_monitor_reason(
    story_input: Dict[str, Any],
    monitor_reason: Dict[str, Any],
    entry_summary: Dict[str, Any],
) -> Dict[str, Any]:
    return _resolve_entry_monitor_reason_impl(story_input, monitor_reason, entry_summary, deps=_section_builder_deps())

def _korean_predicate(value: str, *, noun_suffix: str = "입니다.") -> str:
    return _korean_predicate_impl(value, noun_suffix=noun_suffix)

def _korean_euro_ro(value: Any) -> str:
    return _korean_euro_ro_impl(value)

def _build_entry_decision_bullets(
    entry_summary: Dict[str, Any],
    scanner_reason: Dict[str, Any],
    market_context: Dict[str, Any],
    monitor_reason: Dict[str, Any],
    action: str,
) -> List[str]:
    return _build_entry_decision_bullets_impl(entry_summary, scanner_reason, market_context, monitor_reason, action, deps=_section_builder_deps())

def _build_holding_story_summary(hold_count: int, monitor_reason: Dict[str, Any], status_text: str) -> str:
    posture = _operator_action_label(_clip(monitor_reason.get("posture"), max_len=32) or "WAIT")
    trigger = _operator_axis_label(_clip(monitor_reason.get("trigger_type"), max_len=48) or "not_captured")
    axis = _operator_axis_label(_clip(monitor_reason.get("active_exit_axis"), max_len=64) or trigger)
    confirm_required = monitor_reason.get("confirm_required")
    confirm_count = monitor_reason.get("confirm_count")
    exit_triggered = bool(monitor_reason.get("exit_triggered"))
    if hold_count > 0:
        base = f"보유 구간에서는 모니터가 총 {hold_count}회 실행되었고, 마지막 포지션 판단은 {posture}였습니다. 핵심 감시 축은 {axis}{_korean_euro_ro(axis)} 유지됐습니다."
    else:
        base = "이번 lifecycle의 보유 구간 기록은 제한적이어서, 저장된 모니터 근거를 중심으로 보수적으로 정리했습니다."
    if confirm_required is not None:
        base += f" 청산 확인 조건은 {int(confirm_count or 0)}/{int(confirm_required or 0)} 단계로 기록되었습니다."
    if status_text.lower() == "open" and not exit_triggered:
        base += " 아직 확정된 매도 신호는 확인되지 않았습니다."
    return base


def _build_holding_story_bullets(holding_summary: Dict[str, Any], monitor_reason: Dict[str, Any]) -> List[str]:
    return _build_holding_story_bullets_impl(holding_summary, monitor_reason, deps=_section_builder_deps())

def _build_reporter_evaluation_section(
    shared_seed: Dict[str, Any],
    scanner_reason: Dict[str, Any],
    monitor_reason: Dict[str, Any],
    execution_outcome: Dict[str, Any],
    reporter_status: Dict[str, Any],
    reporter_feedback_packet: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return _build_reporter_evaluation_section_impl(shared_seed, scanner_reason, monitor_reason, execution_outcome, reporter_status, reporter_feedback_packet, deps=_section_builder_deps())

def _build_reporter_evaluation_from_feedback(reporter_feedback_packet: Dict[str, Any] | None) -> Dict[str, Any]:
    return _build_reporter_evaluation_from_feedback_impl(reporter_feedback_packet, deps=_section_builder_deps())

def _build_execution_quality_section(
    story_input: Dict[str, Any],
    execution_outcome: Dict[str, Any],
    lifecycle_summary: Dict[str, Any],
) -> Dict[str, Any]:
    return _build_execution_quality_section_impl(story_input, execution_outcome, lifecycle_summary, deps=_section_builder_deps())

def _build_exit_decision_summary(
    exit_summary: Dict[str, Any],
    monitor_context: Dict[str, Any],
    *,
    status_text: str,
) -> str:
    return _build_exit_decision_summary_r3_impl(exit_summary, monitor_context,
        status_text=status_text, facade=_r3_sys.modules[__name__])


def _build_exit_decision_bullets(
    exit_summary: Dict[str, Any],
    monitor_context: Dict[str, Any],
    *,
    status_text: str,
) -> List[str]:
    return _build_exit_decision_bullets_impl(exit_summary, monitor_context, status_text=status_text, deps=_section_builder_deps())

def _compact_holding_summary(holding: Any) -> Dict[str, Any]:
    data = holding if isinstance(holding, dict) else {}
    posture_rows = data.get("posture_history") if isinstance(data.get("posture_history"), list) else []
    recent_posture = [_compact_event_row(row) for row in posture_rows[-4:] if isinstance(row, dict)]
    recent_posture = [row for row in recent_posture if row]
    return {
        "run_count": len(list(data.get("run_ids") or [])),
        "recent_run_ids": [str(x or "") for x in list(data.get("run_ids") or [])[-6:] if str(x or "").strip()],
        "holding_event_count": len(list(data.get("holding_events") or [])),
        "recent_posture_history": recent_posture,
        "recent_monitor_updates": _tail_list(data.get("monitor_updates"), max_items=6, max_len=200),
    }


def _compact_entry_or_exit_summary(summary: Any) -> Dict[str, Any]:
    return _compact_entry_or_exit_summary_r3_impl(summary, facade=_r3_sys.modules[__name__])


def _extract_policy_ref_context(story_input: Dict[str, Any], monitor_reason: Dict[str, Any]) -> Dict[str, Any]:
    return _extract_policy_ref_context_r3_impl(story_input, monitor_reason,
        facade=_r3_sys.modules[__name__])


def _extract_scanner_bias_summary(story_input: Dict[str, Any], scanner_reason: Dict[str, Any]) -> Dict[str, Any]:
    return _extract_scanner_bias_summary_r3_impl(story_input, scanner_reason,
        facade=_r3_sys.modules[__name__])


def _evidence_digest(evidence: Any, keys: List[str]) -> Dict[str, int]:
    data = evidence if isinstance(evidence, dict) else {}
    return {key: len(list(data.get(key) or [])) for key in keys}


def _extract_strategy_detail_from_source(source: Any) -> Dict[str, Any]:
    return _extract_strategy_detail_from_source_r3_impl(source, facade=_r3_sys.modules[__name__])


def _compact_strategy_detail_context(value: Any) -> Dict[str, Any]:
    return _compact_strategy_detail_context_r3_impl(value, facade=_r3_sys.modules[__name__])


def _compact_candidate_watch_proposal(value: Any) -> Dict[str, Any]:
    data = _as_dict(value)
    if not data:
        return {}
    out = {
        "source": _clip(data.get("source"), max_len=80),
        "behavior_effect": _clip(data.get("behavior_effect"), max_len=48),
        "tactical_strategy": _clip(data.get("tactical_strategy"), max_len=80),
        "tactical_subtype": _clip(data.get("tactical_subtype"), max_len=80),
        "max_priority_rank": data.get("max_priority_rank"),
        "max_runner_ups": data.get("max_runner_ups"),
        "cascade_enabled": data.get("cascade_enabled"),
        "reason": _clip(data.get("reason"), max_len=220),
        "cascade_allowed_reasons": _listify(data.get("cascade_allowed_reasons"), max_items=6, max_len=80),
        "cascade_blocked_reasons": _listify(data.get("cascade_blocked_reasons"), max_items=8, max_len=80),
    }
    return {key: value for key, value in out.items() if value not in ("", None, [], {})}


def _enrich_candidate_watch_proposal_from_entry_control(
    proposal: Dict[str, Any],
    entry_control: Dict[str, Any],
) -> Dict[str, Any]:
    return _enrich_candidate_watch_proposal_from_entry_control_r3_impl(proposal, entry_control,
        facade=_r3_sys.modules[__name__])


def _compact_commander_entry_control(value: Any) -> Dict[str, Any]:
    return _compact_commander_entry_control_r3_impl(value, facade=_r3_sys.modules[__name__])


def _compact_entry_candidate_cascade(value: Any) -> Dict[str, Any]:
    return _compact_entry_candidate_cascade_r3_impl(value, facade=_r3_sys.modules[__name__])


def _first_dict_from(*values: Any) -> Dict[str, Any]:
    for value in values:
        data = _as_dict(value)
        if data:
            return data
    return {}


def _entry_execution_visibility_summary(
    *,
    proposal: Dict[str, Any],
    entry_control: Dict[str, Any],
    cascade: Dict[str, Any],
) -> str:
    return _entry_execution_visibility_summary_r3_impl(proposal=proposal,
        entry_control=entry_control, cascade=cascade, facade=_r3_sys.modules[__name__])


def _context_builder_deps() -> Dict[str, Any]:
    return {
        "as_dict": _as_dict,
        "clip": _clip,
        "compact_candidate_watch_proposal": _compact_candidate_watch_proposal,
        "compact_commander_entry_control": _compact_commander_entry_control,
        "compact_entry_candidate_cascade": _compact_entry_candidate_cascade,
        "enrich_candidate_watch_proposal_from_entry_control": _enrich_candidate_watch_proposal_from_entry_control,
        "entry_execution_visibility_summary": _entry_execution_visibility_summary,
        "extract_strategy_detail_from_source": _extract_strategy_detail_from_source,
        "first_dict_from": _first_dict_from,
        "compact_memory_application_trace": _compact_memory_application_trace,
        "compact_memory_layer_decisions": _compact_memory_layer_decisions,
        "compact_scalar_dict": _compact_scalar_dict,
        "compact_strategy_detail_context": _compact_strategy_detail_context,
        "compact_strategy_refresh_trace": _compact_strategy_refresh_trace,
        "extract_strategist_report_context": _extract_strategist_report_context,
        "listify": _listify,
    }

def _extract_entry_execution_visibility(story_input: Dict[str, Any]) -> Dict[str, Any]:
    return _extract_entry_execution_visibility_impl(story_input, deps=_context_builder_deps())

def _extract_strategist_report_context(story_input: Dict[str, Any]) -> Dict[str, Any]:
    return _extract_strategist_report_context_r3_impl(story_input, facade=_r3_sys.modules[__name__])


def _build_report_strategist_refresh_trace(story_input: Dict[str, Any]) -> Dict[str, Any]:
    return _build_report_strategist_refresh_trace_r3_impl(story_input,
        facade=_r3_sys.modules[__name__])


def _compact_strategy_refresh_trace(value: Any) -> Dict[str, Any]:
    return _compact_strategy_refresh_trace_r3_impl(value, facade=_r3_sys.modules[__name__])


def _compact_memory_layer_decisions(value: Any) -> Dict[str, Any]:
    decisions = value if isinstance(value, dict) else {}
    out: Dict[str, Any] = {}
    for layer, row in list(decisions.items())[:6]:
        if not isinstance(row, dict):
            continue
        out[str(layer)] = {
            "status": _clip(row.get("status"), max_len=32),
            "active": row.get("active"),
            "visible": row.get("visible"),
            "used": row.get("used"),
            "gate_reason": _clip(row.get("gate_reason"), max_len=80),
            "effect": _clip(row.get("effect"), max_len=140),
            "reason": _clip(row.get("reason"), max_len=220),
            "confidence": row.get("confidence"),
            "application_targets": _listify(row.get("application_targets"), max_items=5, max_len=60),
        }
    return out


def _compact_memory_application_trace(value: Any) -> Dict[str, Any]:
    return _compact_memory_application_trace_r3_impl(value, facade=_r3_sys.modules[__name__])


def _compact_strategist_report_context(story_input: Dict[str, Any]) -> Dict[str, Any]:
    return _compact_strategist_report_context_impl(story_input, deps=_context_builder_deps())

def _compact_story_input_for_llm(story_input: Dict[str, Any]) -> Dict[str, Any]:
    return _compact_story_input_for_llm_impl(
        story_input,
        deps={
            "build_shared_summary_seed": _build_shared_summary_seed,
            "extract_policy_ref_context": _extract_policy_ref_context,
            "extract_scanner_bias_summary": _extract_scanner_bias_summary,
            "as_dict": _as_dict,
            "clip": _clip,
            "listify": _listify,
            "compact_scalar_dict": _compact_scalar_dict,
            "reporter_summary_is_placeholder": _reporter_summary_is_placeholder,
            "compact_strategist_report_context": _compact_strategist_report_context,
            "build_report_strategist_refresh_trace": _build_report_strategist_refresh_trace,
            "compact_entry_or_exit_summary": _compact_entry_or_exit_summary,
            "compact_holding_summary": _compact_holding_summary,
            "compact_named_rows": _compact_named_rows,
            "compact_monitor_snapshot": _compact_monitor_snapshot,
            "compact_entry_candidate_cascade": _compact_entry_candidate_cascade,
            "compact_timeline_rows": _compact_timeline_rows,
            "evidence_digest": _evidence_digest,
            "execution_outcome_summary_is_placeholder": execution_outcome_summary_is_placeholder,
        },
    )

def build_ai_trade_report_compact_input(story_input: Dict[str, Any]) -> Dict[str, Any]:
    return _sparse_story_input_for_llm(story_input)


def _compact_section_seed_for_llm(value: Any) -> Dict[str, Any]:
    return _compact_section_seed_for_llm_impl(value)


def _sparse_story_input_for_llm(story_input: Dict[str, Any]) -> Dict[str, Any]:
    return _sparse_story_input_for_llm_impl(
        story_input,
        compact_story_input_for_llm=_compact_story_input_for_llm,
        reporter_summary_is_placeholder=_reporter_summary_is_placeholder,
        compact_timeline_rows=_compact_timeline_rows,
    )

def _normalize_provenance_entry(entry: Any) -> Dict[str, Any]:
    return _normalize_provenance_entry_r3_impl(entry, facade=_r3_sys.modules[__name__])


def _report_section_provenance(story_input: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    return _report_section_provenance_r3_impl(story_input, facade=_r3_sys.modules[__name__])


def _contains_hangul(value: Any) -> bool:
    # Avoid a regex here: this file has previously been damaged by mojibake,
    # and a corrupted Hangul character class can break report generation before
    # the LLM call is even attempted.
    return any("\uac00" <= ch <= "\ud7a3" for ch in str(value or ""))


def _operator_action_label(value: Any) -> str:
    return _operator_action_label_impl(value)

def _operator_axis_label(value: Any) -> str:
    return _operator_axis_label_impl(value)

def _operator_filter_label(value: Any) -> str:
    return _operator_filter_label_impl(value)

def _operator_filter_status(value: Any) -> str:
    return _operator_filter_status_impl(value)

def _normalize_trade_report_language(text: Any) -> str:
    return _normalize_trade_report_language_impl(text)

def _operatorize_report_text(text: Any) -> str:
    return _operatorize_report_text_impl(text)

def _preserve_legacy_trade_report_bullet(value: Any) -> str:
    return _preserve_legacy_trade_report_bullet_impl(value)

def _operatorize_report_section(section: Dict[str, Any]) -> Dict[str, Any]:
    return _operatorize_report_section_impl(section)

def _prefer_fallback_text(ai_text: Any, fallback_text: Any) -> str:
    return _prefer_fallback_text_impl(ai_text, fallback_text)


def _is_scanner_execution_mismatch_text(value: Any) -> bool:
    return _is_scanner_execution_mismatch_text_impl(value)


def _is_scanner_selection_label_line(value: Any) -> bool:
    return _is_scanner_selection_label_line_impl(value)


def _prefer_fallback_summary(section_key: str, ai_text: Any, fallback_text: Any) -> str:
    return _prefer_fallback_summary_impl(
        section_key,
        ai_text,
        fallback_text,
        contains_hangul=_contains_hangul,
        has_noisy_trade_report_text=_has_noisy_trade_report_text,
    )


def _trade_report_priority_bullet_prefixes(section_key: str) -> List[str]:
    return _trade_report_priority_bullet_prefixes_impl(section_key)


def _merge_bullets_with_fallback(section_key: str, ai_bullets: List[str], fallback_bullets: List[str]) -> List[str]:
    return _merge_bullets_with_fallback_impl(
        section_key,
        ai_bullets,
        fallback_bullets,
        is_market_context_noise_bullet=_is_market_context_noise_bullet,
    )


def _merge_section_with_fallback(ai_section: Any, fallback_section: Dict[str, Any], *, section_key: str = "") -> Dict[str, Any]:
    return _merge_section_with_fallback_impl(
        ai_section,
        fallback_section,
        section_key=section_key,
        contains_hangul=_contains_hangul,
        has_noisy_trade_report_text=_has_noisy_trade_report_text,
        is_low_information_bullet=_is_low_information_bullet,
        is_market_context_noise_bullet=_is_market_context_noise_bullet,
    )

def _trade_report_parse_meta(raw: Any, parsed: Dict[str, Any] | None) -> Dict[str, Any]:
    result = parse_llm_json_response(raw)
    candidate = parsed if isinstance(parsed, dict) else {}
    key_meta = required_key_metadata(candidate, AI_TRADE_REPORT_REQUIRED_KEYS)
    parse_mode = "none"
    if bool(result.get("is_full")):
        parse_mode = "full"
    elif bool(result.get("is_partial")):
        parse_mode = "partial"
    return {
        "parse_mode": parse_mode,
        **key_meta,
        "trailing_text": str(result.get("trailing_text") or ""),
        "raw_nonempty": bool(result.get("raw_nonempty")),
        "parse_error": str(result.get("error") or ""),
    }


def _build_report_shared_facts(
    *,
    shared_seed: Dict[str, Any],
    action: str,
    symbol: str,
    trade_id: str,
    status_text: str,
) -> Dict[str, Any]:
    return _build_shared_facts_impl(
        shared_seed=shared_seed,
        action=action,
        symbol=symbol,
        trade_id=trade_id,
        status_text=status_text,
        clip=_clip,
        as_dict=_as_dict,
    )


def _attach_backward_compatible_aliases(report: Dict[str, Any]) -> Dict[str, Any]:
    return _attach_backward_compatible_aliases_impl(report)


def _build_report_monitor_snapshot(
    *,
    monitor_reason: Dict[str, Any],
    story_input: Dict[str, Any],
    action: str,
    entry_execution_visibility: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return _build_monitor_snapshot_impl(
        monitor_reason=monitor_reason,
        story_input=story_input,
        action=action,
        clip=_clip,
        listify=_listify,
        as_dict=_as_dict,
        entry_execution_visibility=entry_execution_visibility,
        compact_entry_candidate_cascade=_compact_entry_candidate_cascade,
    )


def _enrich_market_context_for_fallback(
    *,
    market_context: Dict[str, Any],
    strategist_context: Dict[str, Any],
    policy_ref_context: Dict[str, Any],
    scanner_bias_summary: Dict[str, Any],
) -> Dict[str, Any]:
    return _enrich_market_context_for_fallback_impl(
        market_context=market_context,
        strategist_context=strategist_context,
        policy_ref_context=policy_ref_context,
        scanner_bias_summary=scanner_bias_summary,
    )


def _enrich_scanner_reason_for_fallback(
    *,
    scanner_reason: Dict[str, Any],
    shared_scanner_reasoning: Dict[str, Any],
    shared_selection_trace: Dict[str, Any],
) -> Dict[str, Any]:
    return _enrich_scanner_reason_for_fallback_impl(
        scanner_reason=scanner_reason,
        shared_scanner_reasoning=shared_scanner_reasoning,
        shared_selection_trace=shared_selection_trace,
    )


def _fallback_section_seeds(shared_seed: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return _fallback_section_seeds_impl(shared_seed, as_dict=_as_dict)


def _append_news_scanner_choice_details(
    why_symbol_bullets: List[str],
    news_scanner_contribution: Dict[str, Any],
) -> List[str]:
    return _append_news_scanner_choice_details_impl(
        why_symbol_bullets,
        news_scanner_contribution,
        listify=_listify,
    )


def _merge_trade_report_candidate(
    story_input: Dict[str, Any],
    candidate: Dict[str, Any],
    *,
    status: str,
    mode: str,
    model: str,
    reason: str,
) -> Dict[str, Any]:
    return _merge_trade_report_candidate_impl(
        story_input,
        candidate,
        status=status,
        mode=mode,
        model=model,
        reason=reason,
        fallback_report=_fallback_report,
        normalize_section=_normalize_section,
        merge_section_with_fallback=_merge_section_with_fallback,
        prefer_fallback_text=_prefer_fallback_text,
        listify=_listify,
        clip=_clip,
        normalize_trade_report_output=_normalize_trade_report_output,
    )


def _fallback_report(
    story_input: Dict[str, Any],
    *,
    status: str,
    mode: str,
    model: str,
    reason: str,
) -> Dict[str, Any]:
    return _fallback_report_impl(
        story_input,
        status=status,
        mode=mode,
        model=model,
        reason=reason,
        deps={
            "build_shared_summary_seed": _build_shared_summary_seed,
            "build_trade_report_memory_surface": build_trade_report_memory_surface,
            "as_dict": _as_dict,
            "extract_policy_ref_context": _extract_policy_ref_context,
            "extract_scanner_bias_summary": _extract_scanner_bias_summary,
            "enrich_market_context_for_fallback": _enrich_market_context_for_fallback,
            "fallback_section_seeds": _fallback_section_seeds,
            "enrich_scanner_reason_for_fallback": _enrich_scanner_reason_for_fallback,
            "clip": _clip,
            "build_report_monitor_snapshot": _build_report_monitor_snapshot,
            "resolve_entry_monitor_reason": _resolve_entry_monitor_reason,
            "listify": _listify,
            "scanner_chart_feature_coverage": _scanner_chart_feature_coverage,
            "build_scanner_choice_bullets": _build_scanner_choice_bullets,
            "append_news_scanner_choice_details": _append_news_scanner_choice_details,
            "lifecycle_summary_conflicts_with_status": _lifecycle_summary_conflicts_with_status,
            "build_scanner_choice_summary": _build_scanner_choice_summary,
            "build_market_context_summary": _build_market_context_summary,
            "build_market_context_bullets": _build_market_context_bullets,
            "build_market_scanner_linkage_bullet": _build_market_scanner_linkage_bullet,
            "build_strategist_summary_section": _build_strategist_summary_section,
            "build_entry_decision_summary": _build_entry_decision_summary,
            "build_entry_decision_bullets": _build_entry_decision_bullets,
            "build_holding_story_summary": _build_holding_story_summary,
            "build_holding_story_bullets": _build_holding_story_bullets,
            "build_exit_decision_summary": _build_exit_decision_summary,
            "build_exit_decision_bullets": _build_exit_decision_bullets,
            "build_execution_quality_section": _build_execution_quality_section,
            "build_scanner_filters_summary": _build_scanner_filters_summary,
            "build_scanner_filters_bullets": _build_scanner_filters_bullets,
            "build_reporter_evaluation_section": _build_reporter_evaluation_section,
            "holding_duration_label": _holding_duration_label,
            "exit_reason_label": _exit_reason_label,
            "is_low_information_bullet": _is_low_information_bullet,
            "reporter_summary_is_placeholder": _reporter_summary_is_placeholder,
            "scanner_basis_text": _scanner_basis_text,
            "build_report_shared_facts": _build_report_shared_facts,
            "attach_backward_compatible_aliases": _attach_backward_compatible_aliases,
            "build_report_strategist_refresh_trace": _build_report_strategist_refresh_trace,
            "compact_strategist_report_context": _compact_strategist_report_context,
            "compact_scalar_dict": _compact_scalar_dict,
            "story_post_exit_shadow": _story_post_exit_shadow,
            "utc_now_iso": _utc_now_iso,
            "build_trade_report_truth_surface": build_trade_report_truth_surface,
            "build_trade_memory_application_surface": build_trade_memory_application_surface,
            "execution_outcome_summary_is_placeholder": execution_outcome_summary_is_placeholder,
        },
    )

def _failure_report(
    story_input: Dict[str, Any],
    *,
    status: str,
    mode: str,
    model: str,
    reason: str,
    error: str = "",
) -> Dict[str, Any]:
    return _failure_report_impl(
        story_input,
        status=status,
        mode=mode,
        model=model,
        reason=reason,
        error=error,
        build_shared_summary_seed=_build_shared_summary_seed,
        clip=_clip,
        actual_lifecycle_action=_actual_lifecycle_action,
        as_dict=_as_dict,
        utc_now_iso=_utc_now_iso,
        build_report_strategist_refresh_trace=_build_report_strategist_refresh_trace,
        listify=_listify,
        build_monitor_snapshot_fn=_build_report_monitor_snapshot,
        normalize_trade_report_output=_normalize_trade_report_output,
    )


def build_separated_ai_trade_report(trade_dir: str, *, model: Optional[str] = None) -> Dict[str, Any]:
    """Phase 6-1 Task 4 Compatibility Wrapper."""
    from libs.reporting.trade_read_model import build_trade_read_model
    from libs.reporting.fact_narrative_report import build_separated_report
    from libs.agent.reporter import run_reporter_agent

    try:
        trade_model = build_trade_read_model(str(trade_dir))
    except Exception:
        trade_model = {}
    chosen_model = _resolve_intraday_report_model(trade_model, explicit_model=model)
    execution_profile = _resolve_intraday_report_execution_profile(
        trade_model if isinstance(trade_model, dict) else {}
    )
    agent_out = run_reporter_agent(
        str(trade_dir),
        policy={
            "model": chosen_model,
            "execution_profile": execution_profile,
        },
    )
    agent_status = str(agent_out.get("status") or "").strip().lower()
    narrative_obj = agent_out.get("narrative") if isinstance(agent_out.get("narrative"), dict) else {}
    narrative_reason = str(narrative_obj.get("reason") or "").strip().lower()
    degraded_for_contract = (
        agent_status == "degraded"
        and (
            narrative_reason.startswith("trade_read_model_")
            or not isinstance(agent_out.get("facts"), dict)
            or not isinstance(agent_out.get("provenance"), dict)
        )
    )
    if degraded_for_contract:
        return build_separated_report(
            trade_model=trade_model,
            model=chosen_model,
            execution_profile=execution_profile,
        )

    facts = agent_out.get("facts") if isinstance(agent_out.get("facts"), dict) else {}
    provenance = agent_out.get("provenance") if isinstance(agent_out.get("provenance"), dict) else {}
    context = agent_out.get("context") if isinstance(agent_out.get("context"), dict) else {}
    narrative = narrative_obj
    trade_fact_payload: Dict[str, Any] = dict(facts)
    trade_fact_payload.setdefault("facts", dict(facts))
    trade_fact_payload.setdefault("provenance", dict(provenance))
    trade_fact_payload.setdefault("context", dict(context))
    return {
        "fact_payload": {
            "trade": trade_fact_payload,
            "daily": {},
            "symbol": {},
        },
        "narrative": dict(narrative),
        "reporter_agent": {
            "status": str(agent_out.get("status") or ""),
            "metadata": dict(agent_out.get("metadata") or {}),
        },
    }


def _build_skipped_separated_report(trade_model: Dict[str, Any], *, reason: str) -> Dict[str, Any]:
    from libs.reporting.fact_narrative_report import build_fact_payload

    return {
        "fact_payload": build_fact_payload(trade_model=trade_model),
        "narrative": {
            "summary": "",
            "insight": "",
            "recommendation": "",
            "source": "llm",
            "based_on": "fact_payload",
            "status": "skipped",
            "reason": reason,
            "llm_call_skipped": True,
        },
    }


def _resolve_separated_trade_model(story_input: Dict[str, Any]) -> Dict[str, Any]:
    trade_model = _load_trade_read_model_hint(story_input)
    if isinstance(trade_model, dict) and trade_model:
        return trade_model
    return dict((story_input if isinstance(story_input, dict) else {}) or {})


def _load_trade_read_model_hint(story_input: Dict[str, Any]) -> Dict[str, Any]:
    from pathlib import Path
    from libs.reporting.trade_read_model import build_trade_read_model

    story_input_obj = story_input if isinstance(story_input, dict) else {}
    artifacts = story_input_obj.get("artifacts") if isinstance(story_input_obj.get("artifacts"), dict) else {}
    artifact_root = Path(str(artifacts.get("ai_trade_report_input_json") or ""))
    trade_root: Path | None = artifact_root.parent if artifact_root.name == "ai_trade_report_input.json" else None
    try:
        if trade_root is not None and trade_root.exists():
            trade_model = build_trade_read_model(str(trade_root))
            return trade_model if isinstance(trade_model, dict) else {}
    except Exception:
        pass
    return {}


def _trade_report_output_template() -> Dict[str, Any]:
    return _trade_report_output_template_impl()


def _trade_report_language_meta(candidate: Dict[str, Any]) -> Dict[str, Any]:
    sample_fields: List[str] = []

    def _collect(section: Any) -> None:
        if isinstance(section, dict):
            for key, value in section.items():
                if key in {"headline", "summary", "description"} and str(value or "").strip():
                    sample_fields.append(str(value or "").strip())
                elif key in {"bullets", "watch_next", "thesis_invalidation"} and isinstance(value, list):
                    for row in value:
                        if str(row or "").strip():
                            sample_fields.append(str(row or "").strip())
                elif key == "full_timeline" and isinstance(value, list):
                    for row in value:
                        if isinstance(row, dict) and str(row.get("description") or "").strip():
                            sample_fields.append(str(row.get("description") or "").strip())
                elif isinstance(value, dict):
                    _collect(value)

    _collect(candidate)
    hangul_total = sum(_count_hangul(item) for item in sample_fields)
    latin_total = sum(_count_latin(item) for item in sample_fields)
    forbidden_cjk_total = sum(_count_forbidden_cjk_or_japanese(item) for item in sample_fields)
    english_like = [
        item
        for item in sample_fields
        if _count_hangul(item) == 0 and _count_latin(item) >= 8
    ]
    requires_korean_repair = bool(
        sample_fields
        and len(english_like) >= 6
        and (hangul_total == 0 or hangul_total < max(20, latin_total * 0.2))
    )
    if forbidden_cjk_total > 0:
        requires_korean_repair = True
    return {
        "language_sample_count": len(sample_fields),
        "language_hangul_chars": hangul_total,
        "language_latin_chars": latin_total,
        "language_english_like_count": len(english_like),
        "language_forbidden_cjk_chars": forbidden_cjk_total,
        "requires_korean_repair": requires_korean_repair,
    }


def _build_concise_trade_report_messages(
    compact_input: Dict[str, Any],
    contract: Dict[str, Any],
    *,
    partial_note: str = "",
    previous_response_text: str = "",
    repair: bool = False,
    enforce_korean: bool = False,
) -> List[Dict[str, str]]:
    return _build_concise_trade_report_messages_impl(
        compact_input,
        contract,
        korean_rules=AI_TRADE_REPORT_KOREAN_RULES,
        compact_section_seed_for_llm=_compact_section_seed_for_llm,
        partial_note=partial_note,
        previous_response_text=previous_response_text,
        repair=repair,
        enforce_korean=enforce_korean,
    )


def _prompt_story_input_for_llm(compact_input: Dict[str, Any]) -> Dict[str, Any]:
    return _prompt_story_input_for_llm_impl(
        compact_input,
        compact_section_seed_for_llm=_compact_section_seed_for_llm,
    )


def _build_repair_messages(
    story_input: Dict[str, Any],
    raw_response: Any,
    *,
    sparse: bool = False,
    enforce_korean: bool = False,
) -> List[Dict[str, str]]:
    return _build_repair_messages_impl(
        story_input,
        raw_response,
        sparse_story_input_for_llm=_sparse_story_input_for_llm,
        compact_section_seed_for_llm=_compact_section_seed_for_llm,
        korean_rules=AI_TRADE_REPORT_KOREAN_RULES,
        sparse=sparse,
        enforce_korean=enforce_korean,
    )


def _build_messages(story_input: Dict[str, Any]) -> List[Dict[str, str]]:
    return _build_messages_impl(
        story_input,
        sparse_story_input_for_llm=_sparse_story_input_for_llm,
        compact_section_seed_for_llm=_compact_section_seed_for_llm,
        korean_rules=AI_TRADE_REPORT_KOREAN_RULES,
    )


def _canonical_ai_report_status(value: Any) -> str:
    raw = str(value or "").strip().lower()
    if raw in {"ok", "partial", "salvaged", "error", "skipped"}:
        return raw
    if raw in {"repaired"}:
        return "ok"
    if raw in {"disabled", "fallback", "unavailable", "dry_run"}:
        return "skipped"
    return "error"


def _attach_report_status_matrix(
    report: Dict[str, Any],
    story_input: Dict[str, Any],
    *,
    ai_trade_report_status: Any,
    deterministic_report_status: Any = "ok",
) -> Dict[str, Any]:
    return _attach_report_status_matrix_r3_impl(report, story_input,
        ai_trade_report_status=ai_trade_report_status,
        deterministic_report_status=deterministic_report_status, facade=_r3_sys.modules[__name__])


def build_deterministic_trade_report(story_input: Dict[str, Any]) -> Dict[str, Any]:
    return _build_deterministic_trade_report_impl(
        story_input,
        fallback_report=_fallback_report,
        attach_report_status_matrix=_attach_report_status_matrix,
    )


def build_ai_trade_report(
    story_input: Dict[str, Any],
    *,
    enabled: Optional[bool] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    retry_max_override: Optional[int] = None,
    timeout_sec_override: Optional[float] = None,
    hard_timeout_sec_override: Optional[float] = None,
    local_debug_no_llm: bool = False,
) -> Dict[str, Any]:
    return _build_ai_trade_report_service_impl(
        story_input,
        enabled=enabled,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        retry_max_override=retry_max_override,
        timeout_sec_override=timeout_sec_override,
        hard_timeout_sec_override=hard_timeout_sec_override,
        local_debug_no_llm=local_debug_no_llm,
        deps={
            "resolve_intraday_report_model": _resolve_intraday_report_model,
            "resolve_intraday_report_execution_profile": _resolve_intraday_report_execution_profile,
            "failure_report": _failure_report,
            "attach_report_status_matrix": _attach_report_status_matrix,
            "fallback_report": _fallback_report,
            "llm_router_cls": LLMRouter,
            "build_messages": _build_messages,
            "router_chat_with_hard_timeout": _router_chat_with_hard_timeout,
            "trade_report_parse_meta": _trade_report_parse_meta,
            "trade_report_language_meta": _trade_report_language_meta,
            "build_repair_messages": _build_repair_messages,
            "merge_trade_report_candidate": _merge_trade_report_candidate,
            "required_keys": tuple(AI_TRADE_REPORT_REQUIRED_KEYS),
        },
    )

def render_trade_report_markdown(report: Dict[str, Any]) -> str:
    from libs.reporting.trade_report_markdown_clean import render_trade_report_markdown_clean

    return render_trade_report_markdown_clean(report)


def build_trade_summary_input(report: Dict[str, Any]) -> Dict[str, Any]:
    from libs.reporting.trade_report_markdown_clean import build_trade_summary_input_clean

    return build_trade_summary_input_clean(report)


def _trade_summary_evaluation_template() -> Dict[str, Any]:
    return _trade_summary_evaluation_template_impl()


def _normalize_trade_summary_evaluation(value: Any) -> Dict[str, Any]:
    return _normalize_trade_summary_evaluation_impl(value, clip=_clip, listify=_listify)


def _trade_summary_parse_meta(raw_response: Any, candidate: Dict[str, Any]) -> Dict[str, Any]:
    return _trade_summary_parse_meta_impl(raw_response, candidate)


def _build_trade_summary_evaluation_messages(
    summary_input: Dict[str, Any],
    *,
    previous_response_text: str = "",
    repair: bool = False,
) -> List[Dict[str, str]]:
    return _build_trade_summary_evaluation_messages_impl(
        summary_input,
        korean_rules=AI_TRADE_REPORT_KOREAN_RULES,
        previous_response_text=previous_response_text,
        repair=repair,
    )


def _deterministic_trade_summary_report(
    summary_input: Dict[str, Any],
    *,
    status: str,
    mode: str,
    model: str,
    reason: str,
    evaluation: Dict[str, Any] | None = None,
    llm_response_artifact: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return _deterministic_trade_summary_report_impl(
        summary_input,
        status=status,
        mode=mode,
        model=model,
        reason=reason,
        evaluation=evaluation,
        llm_response_artifact=llm_response_artifact,
        as_dict=_as_dict,
        normalize_evaluation=_normalize_trade_summary_evaluation,
    )


def build_trade_summary_report(
    summary_input: Dict[str, Any],
    *,
    enabled: bool = False,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    retry_max_override: Optional[int] = None,
    timeout_sec_override: Optional[float] = None,
    hard_timeout_sec_override: Optional[float] = None,
    local_debug_no_llm: bool = False,
) -> Dict[str, Any]:
    return _build_trade_summary_report_service_impl(
        summary_input,
        enabled=enabled,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        retry_max_override=retry_max_override,
        timeout_sec_override=timeout_sec_override,
        hard_timeout_sec_override=hard_timeout_sec_override,
        local_debug_no_llm=local_debug_no_llm,
        deps={
            "as_dict": _as_dict,
            "resolve_intraday_report_model": _resolve_intraday_report_model,
            "deterministic_trade_summary_report": _deterministic_trade_summary_report,
            "llm_router_cls": LLMRouter,
            "build_trade_summary_evaluation_messages": _build_trade_summary_evaluation_messages,
            "router_chat_with_hard_timeout": _router_chat_with_hard_timeout,
            "trade_summary_parse_meta": _trade_summary_parse_meta,
            "normalize_trade_summary_evaluation": _normalize_trade_summary_evaluation,
            "required_keys": tuple(AI_TRADE_SUMMARY_EVALUATION_KEYS),
        },
    )

def render_trade_summary_markdown(report: Dict[str, Any]) -> str:
    from libs.reporting.trade_report_markdown_clean import render_trade_summary_markdown_clean

    return render_trade_summary_markdown_clean(report)


def render_trade_summary_markdown_with_evaluation(
    report: Dict[str, Any],
    summary_report: Dict[str, Any],
) -> str:
    from libs.reporting.trade_report_markdown_clean import render_trade_summary_markdown_with_evaluation_clean

    return render_trade_summary_markdown_with_evaluation_clean(report, summary_report)
