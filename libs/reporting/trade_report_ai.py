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
    data = section if isinstance(section, dict) else {}
    out = {
        "summary": _clip(data.get("summary"), max_len=600) or _clip(default_summary, max_len=600),
        bullet_key: _listify(data.get(bullet_key), max_items=8, max_len=260),
    }
    for key in (
        "headline",
        "action",
        "confidence",
        "status",
        "grade",
        "current_action",
        "symbol",
        "story_type",
    ):
        value = _clip(data.get(key), max_len=120)
        if value:
            out[key] = value
    return out


def _actual_lifecycle_action(story_input: Dict[str, Any]) -> str:
    status_text = str(story_input.get("status") or "").strip().lower()
    exit_summary = story_input.get("exit_summary") if isinstance(story_input.get("exit_summary"), dict) else {}
    entry_summary = story_input.get("entry_summary") if isinstance(story_input.get("entry_summary"), dict) else {}
    operator_conclusion = story_input.get("operator_conclusion_human") if isinstance(story_input.get("operator_conclusion_human"), dict) else {}

    exit_action = _clip(exit_summary.get("action"), max_len=24).upper()
    entry_action = _clip(entry_summary.get("action"), max_len=24).upper()
    requested_action = _clip(story_input.get("action"), max_len=24).upper()
    conclusion_action = _clip(operator_conclusion.get("current_action"), max_len=24).upper()

    if exit_action in {"BUY", "SELL"}:
        return exit_action
    if status_text == "open":
        if conclusion_action in {"HOLD", "WAIT", "BUY"}:
            return conclusion_action
        return "HOLD"
    if requested_action in {"BUY", "SELL"}:
        return requested_action
    if conclusion_action in {"BUY", "SELL", "HOLD", "WAIT"}:
        return conclusion_action
    if entry_action in {"BUY", "SELL"}:
        return entry_action
    return "WAIT"


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
    text = str(value or "").strip()
    if not text:
        return False
    lowered = text.lower()
    exact_markers = {
        "same-day reporter analysis was not generated yet.",
        "a same-day reporter file exists, but this run was not linked to a run-specific evaluation yet.",
        "a same-day reporter analysis was linked to this run.",
        "당일 리포터 분석은 아직 생성되지 않았습니다.",
        "당일 리포터 파일은 있지만 이 run에 대한 개별 평가는 아직 연결되지 않았습니다.",
        "당일 리포터 분석이 이 run에 연결됐습니다.",
    }
    prefix_markers = (
        "reporter status:",
        "reporter reason:",
        "reporter grade:",
        "reporter summary:",
    )
    if lowered in {marker.lower() for marker in exact_markers}:
        return True
    return any(lowered.startswith(marker) for marker in prefix_markers)


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
    shared_seed = _build_shared_summary_seed(story_input)
    resolved = _as_dict(shared_seed.get("resolved_trade_facts"))
    data_source = _as_dict(resolved.get("data_source"))
    return {
        "action": _as_action(resolved.get("action")) or "unavailable",
        "status": _as_status(resolved.get("status")) or "unavailable",
        "holding_duration": _clip(resolved.get("holding_duration"), max_len=80) or "unavailable",
        "exit_reason": _clip(resolved.get("exit_reason"), max_len=280) or "unavailable",
        "pnl": resolved.get("pnl", "unavailable"),
        "pnl_pct": resolved.get("pnl_pct", "unavailable"),
        "broker_fee": resolved.get("broker_fee"),
        "broker_tax": resolved.get("broker_tax"),
        "pnl_truth_source": _clip(resolved.get("pnl_truth_source"), max_len=80) or "unavailable",
        "broker_fill_price": resolved.get("broker_fill_price"),
        "broker_buy_price": resolved.get("broker_buy_price"),
        "account_mark_price": resolved.get("account_mark_price"),
        "monitor_mark_price": resolved.get("monitor_mark_price"),
        "price_truth_source": _clip(resolved.get("price_truth_source"), max_len=40) or "unavailable",
        "monitor_price_source": _clip(resolved.get("monitor_price_source"), max_len=120) or "unavailable",
        "data_source": data_source,
        "monitor_decision": _as_dict(shared_seed.get("monitor_decision")),
    }


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
    raw = _clip(value, max_len=80).strip().lower()
    mapping = {
        "neutral": "중립",
        "bullish": "강세",
        "bearish": "약세",
        "pullback": "눌림목",
        "breakout": "돌파",
        "trend": "추세",
        "defensive": "방어적",
        "risk_off": "위험회피",
        "risk_on": "위험선호",
        "not_captured": "직접 캡처되지 않음",
        "unavailable": "확인 불가",
    }
    return mapping.get(raw, _clip(value, max_len=80))


def _theme_token_label(value: Any) -> str:
    raw = _clip(value, max_len=80).strip().lower()
    mapping = {
        "broad_market_leaders": "브로드마켓 리더",
        "semiconductor_leaders": "반도체 리더",
        "high_beta_leaders": "고베타 리더",
    }
    return mapping.get(raw, _clip(value, max_len=80))


def _theme_text(values: Any, *, max_items: int = 4) -> str:
    labels = [_theme_token_label(item) for item in _listify(values, max_items=max_items, max_len=80)]
    labels = [item for item in labels if item]
    if len(labels) == 2:
        return f"{labels[0]}와 {labels[1]}"
    if len(labels) >= 3:
        return ", ".join(labels[:-1]) + f", {labels[-1]}"
    return labels[0] if labels else "not_captured"


def _theme_linkage_label(values: Any) -> str:
    theme_values = [str(item or "").strip().lower() for item in _listify(values, max_items=4, max_len=80)]
    if "broad_market_leaders" in theme_values:
        return "시장 주도 대형주 우위"
    if "semiconductor_leaders" in theme_values:
        return "반도체 리더 우위"
    if "high_beta_leaders" in theme_values:
        return "고베타 리더 우위"
    themed = _theme_text(values, max_items=2)
    return f"{themed} 맥락" if themed and themed != "not_captured" else "시장 맥락"


def _risk_mode_label(value: Any) -> str:
    raw = _clip(value, max_len=80).strip().lower()
    mapping = {
        "balanced": "균형형",
        "conservative": "보수형",
        "aggressive": "공격형",
    }
    return mapping.get(raw, _clip(value, max_len=80))


def _strategy_constraint_label(value: Any) -> str:
    raw = _clip(value, max_len=80).strip().lower()
    mapping = {
        "defensive_assets": "방어 자산",
        "counter_trend_low_liquidity": "역추세 저유동성",
        "high_beta_leaders": "고베타 리더",
        "semiconductor_leaders": "반도체 리더",
        "broad_market_leaders": "브로드마켓 리더",
        "illiquid_microcap": "저유동성 소형주",
        "headline_only_momentum": "헤드라인 추격 모멘텀",
        "high_gap_speculative": "갭 급등 투기성 종목",
    }
    return mapping.get(raw, _clip(value, max_len=80))


def _strategy_constraint_text(values: Any, *, max_items: int = 4) -> str:
    labels = [_strategy_constraint_label(item) for item in _listify(values, max_items=max_items, max_len=80)]
    labels = [item for item in labels if item]
    if len(labels) >= 3:
        return ", ".join(labels[:-1]) + f", {labels[-1]}"
    if len(labels) == 2:
        return ", ".join(labels)
    return labels[0] if labels else ""


def _scanner_bias_label(value: Any) -> str:
    raw = _clip(value, max_len=80).strip().lower()
    mapping = {
        "prefer_shallow_pullback_candidates": "얕은 눌림목 후보 선호",
        "penalize_overextended": "과확장 후보 패널티",
        "prefer_reclaim_candidates": "재회복 후보 선호",
        "prefer_volume_confirmation": "거래량 확인 후보 선호",
    }
    return mapping.get(raw, _clip(value, max_len=80))


def _scanner_bias_text(summary: Any) -> str:
    data = summary if isinstance(summary, dict) else {}
    active_values = data.get("active_biases")
    if isinstance(active_values, str):
        raw = active_values.strip()
        if raw.startswith("[") and raw.endswith("]"):
            try:
                parsed = ast.literal_eval(raw)
                if isinstance(parsed, list):
                    active_values = parsed
            except Exception:
                pass
    active = [_scanner_bias_label(item) for item in _listify(active_values, max_items=6, max_len=80)]
    active = [item for item in active if item]
    strength = _clip(data.get("bias_strength"), max_len=24).strip().lower()
    strength_label = {"low": "낮음", "medium": "중간", "high": "높음"}.get(strength, _clip(strength, max_len=24))
    if active:
        joined = ", ".join(active)
        if strength_label:
            return f"{joined} (강도 {strength_label})"
        return joined
    raw_summary = _clip(data.get("summary"), max_len=220)
    return raw_summary


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
    data = section if isinstance(section, dict) else {}
    packet = data.get("korea_indices") if isinstance(data.get("korea_indices"), dict) else {}
    indices = packet.get("indices") if isinstance(packet.get("indices"), dict) else {}
    out: Dict[str, Dict[str, Any]] = {}
    for name in ("KOSPI", "KOSDAQ"):
        row = indices.get(name) if isinstance(indices.get(name), dict) else {}
        if row:
            out[name] = dict(row)
    if out:
        return out
    events = data.get("key_events") or data.get("key_events_hint")
    for row in _listify(events, max_items=8, max_len=260):
        text = str(row or "")
        match = re.search(
            r"kospi=([+-]?\d+(?:\.\d+)?)/prev=([+-]?\d+(?:\.\d+)?)/chg=([+-]?\d+(?:\.\d+)?)%.*?"
            r"kosdaq=([+-]?\d+(?:\.\d+)?)/prev=([+-]?\d+(?:\.\d+)?)/chg=([+-]?\d+(?:\.\d+)?)%",
            text,
            flags=re.IGNORECASE,
        )
        if not match:
            continue
        return {
            "KOSPI": {"current": float(match.group(1)), "previous_close": float(match.group(2)), "change_pct": float(match.group(3))},
            "KOSDAQ": {"current": float(match.group(4)), "previous_close": float(match.group(5)), "change_pct": float(match.group(6))},
        }
    return {}


def _format_korea_indices_sentence(indices: Dict[str, Dict[str, Any]]) -> str:
    parts: List[str] = []
    for name in ("KOSPI", "KOSDAQ"):
        row = indices.get(name) if isinstance(indices.get(name), dict) else {}
        if not row:
            continue
        current = _num_opt(row.get("current"))
        previous = _num_opt(row.get("previous_close"))
        change_pct = _num_opt(row.get("change_pct"))
        if current is None and previous is None and change_pct is None:
            continue
        bits = [name]
        if current is not None:
            bits.append(f"현재 {current:,.2f}")
        if previous is not None:
            bits.append(f"전일 {previous:,.2f}")
        if change_pct is not None:
            bits.append(f"등락률 {_format_pct_points(change_pct)}")
        parts.append(" ".join(bits))
    return "; ".join(parts)


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
    raw = _clip(value, max_len=80).strip().lower()
    mapping = {
        "top_value": "거래대금 상위",
        "top_volume": "거래량 상위",
        "sector_theme": "섹터·테마 정렬",
        "sentiment": "감성 반영",
        "news": "뉴스 반영",
    }
    return mapping.get(raw, _clip(value, max_len=80))


def _scanner_source_text(values: Any) -> str:
    labels = [_scanner_source_label(item) for item in _listify(values, max_items=4, max_len=80)]
    labels = [item for item in labels if item]
    if len(labels) == 2:
        return f"{labels[0]}와 {labels[1]}"
    if len(labels) >= 3:
        return ", ".join(labels[:-1]) + f", {labels[-1]}"
    return ", ".join(labels)


def _scanner_score_driver_label(value: Any) -> str:
    raw = _clip(value, max_len=80).strip().lower()
    mapping = {
        "trading_value": "거래대금",
        "momentum": "모멘텀",
        "trend": "추세",
        "ma_alignment": "이동평균 정렬",
        "adx_trend": "ADX 추세",
        "volume_surge": "거래량 스파이크",
        "intraday_strength": "장중 강도",
        "vwap_alignment": "VWAP 정렬",
        "theme_boost": "테마 가점",
        "sentiment": "감성",
        "cross_section_rank": "횡단면 순위",
        "entry_compatibility_bias": "진입 적합성",
        "rank_bonus": "순위 가점",
        "risk_penalty": "리스크 패널티",
        "repeat_symbol_penalty": "중복 종목 패널티",
        "scanner_bias": "스캐너 바이어스",
    }
    return mapping.get(raw, _clip(value, max_len=80))


def _scanner_chart_feature_label(value: Any) -> str:
    raw = _clip(value, max_len=80).strip().lower()
    mapping = {
        "engine_ma20_gap": "20일선 이격",
        "engine_ma60": "60일선",
        "engine_ma120": "120일선",
        "engine_adx14": "ADX14",
        "engine_trend_strength": "추세 강도",
        "engine_atr14": "ATR14",
        "engine_volume_spike20": "20봉 거래량 스파이크",
        "engine_volatility20": "20봉 변동성",
        "engine_vwap_distance": "VWAP 이격",
        "engine_sector_relative_strength": "섹터 상대강도",
        "engine_cross_section_rank": "횡단면 순위",
        "engine_regime": "레짐",
        "engine_signal_score": "신호 점수",
    }
    return mapping.get(raw, _clip(value, max_len=80))


def _scanner_ranked_candidates(scanner_reason: Dict[str, Any]) -> List[Dict[str, Any]]:
    for key in ("top_candidates", "ranked_candidates"):
        rows = [row for row in list(scanner_reason.get(key) or []) if isinstance(row, dict)]
        if rows:
            return rows[:5]
    trace = scanner_reason.get("scanner_selection_trace") if isinstance(scanner_reason.get("scanner_selection_trace"), dict) else {}
    return [row for row in list(trace.get("ranked_candidates") or []) if isinstance(row, dict)][:5]


def _scanner_selected_row(scanner_reason: Dict[str, Any]) -> Dict[str, Any]:
    selected_symbol = _clip(scanner_reason.get("selected_symbol"), max_len=24)
    ranked_rows = _scanner_ranked_candidates(scanner_reason)
    if selected_symbol:
        for row in ranked_rows:
            if _clip(row.get("symbol"), max_len=24) == selected_symbol:
                return dict(row)
    fallback_ctx = _scanner_monitor_fallback_context(scanner_reason)
    if fallback_ctx["used"] and selected_symbol:
        trace = scanner_reason.get("scanner_selection_trace") if isinstance(scanner_reason.get("scanner_selection_trace"), dict) else {}
        news = trace.get("news_scanner_contribution") if isinstance(trace.get("news_scanner_contribution"), dict) else {}
        row = {
            "symbol": selected_symbol,
            "rank": scanner_reason.get("selected_rank") or trace.get("selected_rank"),
            "score_total": scanner_reason.get("selected_score") or trace.get("selected_score") or news.get("selected_score_total"),
            "confidence": scanner_reason.get("confidence") or trace.get("confidence"),
            "risk_score": scanner_reason.get("risk_score") or trace.get("risk_score"),
        }
        return {key: value for key, value in row.items() if value not in (None, "")}
    return dict(ranked_rows[0]) if ranked_rows else {}


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
    driver_source = (
        scanner_reason.get("selected_symbol_score_drivers")
        if isinstance(scanner_reason.get("selected_symbol_score_drivers"), dict)
        else {}
    )
    if not driver_source:
        trace = scanner_reason.get("scanner_selection_trace") if isinstance(scanner_reason.get("scanner_selection_trace"), dict) else {}
        driver_source = trace.get("selected_symbol_score_drivers") if isinstance(trace.get("selected_symbol_score_drivers"), dict) else {}
    driver_rows: List[tuple[str, float]] = []
    for key, value in dict(driver_source or {}).items():
        numeric = _num_opt(value)
        if numeric is None or numeric <= 0:
            continue
        driver_rows.append((_scanner_score_driver_label(key), numeric))
    if not driver_rows:
        return ""
    driver_rows.sort(key=lambda item: item[1], reverse=True)
    top_rows = [f"{label} {value:.3f}" for label, value in driver_rows[:3]]
    return ", ".join(top_rows)


def _build_runner_up_comparison(
    row: Dict[str, Any],
    *,
    selected_symbol: str,
    selected_score: Optional[float],
    selected_risk: Optional[float],
) -> str:
    runner_symbol = _clip(row.get("symbol"), max_len=24)
    if not runner_symbol:
        return ""
    parts: List[str] = []
    runner_score = _num_opt(row.get("score_total"))
    runner_risk = _num_opt(row.get("risk_score"))
    if runner_score is not None and selected_score is not None:
        gap = selected_score - runner_score
        if gap >= 0:
            parts.append(
                f"종합 점수 {runner_score:.3f}로 {selected_symbol}({selected_score:.3f})보다 {gap:.3f} 낮았습니다"
            )
    if runner_risk is not None and selected_risk is not None and runner_risk > selected_risk:
        parts.append(
            f"리스크 점수 {runner_risk:.3f}로 {selected_symbol}({selected_risk:.3f})보다 높았습니다"
        )
    if not parts:
        why_text = _clip(row.get("why") or row.get("summary"), max_len=220)
        if why_text:
            parts.append(_operatorize_report_text(why_text))
    if not parts:
        return ""
    return f"{runner_symbol}은 " + ". ".join(parts) + "."


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
    raw = str(value or "").strip().lower()
    if not raw:
        return False
    noisy_tokens = (
        "cached_strategist",
        "policy_validation_status",
        "fallback_invalid",
        "strategist invocation",
        "headlines were considered",
        "market regime",
        "scanner selected ",
        "source mix:",
        "chart feature coverage",
        "trading value",
        "theme and sector alignment",
        "confidence:",
        "risk_score",
        "timeframe ",
        "breakout lookback",
        "volume lookback",
        "volume_ratio_min",
        "min_extended_from_vwap_pct",
        "max_extended_from_vwap_pct",
    )
    return any(token in raw for token in noisy_tokens)


def _scanner_check_name_label(value: Any) -> str:
    raw = _clip(value, max_len=80).strip().lower()
    mapping = {
        "liquidity filter": "유동성 점검",
        "유동성 필터": "유동성 점검",
        "turnover filter": "회전율 점검",
        "회전율 필터": "회전율 점검",
        "sector/theme alignment": "섹터·테마 정렬 점검",
        "섹터/테마 정렬": "섹터·테마 정렬 점검",
        "chart completeness filter": "차트 피처 충실도 점검",
        "차트 완전성 필터": "차트 피처 충실도 점검",
        "sentiment gate": "시장 심리 점검",
        "시장 심리 게이트": "시장 심리 점검",
        "risk gate": "리스크 점검",
        "리스크 게이트": "리스크 점검",
        "price anomaly filter": "가격 이상치 점검",
        "가격 이상치 필터": "가격 이상치 점검",
        "spread/slippage filter": "호가 스프레드·슬리피지 점검",
        "스프레드/슬리피지 필터": "호가 스프레드·슬리피지 점검",
    }
    return mapping.get(raw, _clip(value, max_len=80) or "스캐너 점검")


def _scanner_check_status_label(value: Any) -> str:
    raw = _clip(value, max_len=40).strip().upper()
    mapping = {
        "PASS": "통과",
        "FAIL": "미통과",
        "NOT_AVAILABLE": "확인 불가",
    }
    return mapping.get(raw, _clip(value, max_len=40) or "확인 불가")


def _build_scanner_filters_summary(filters_human: Dict[str, Any]) -> str:
    checks = [row for row in list(filters_human.get("checks") or []) if isinstance(row, dict)]
    feature_coverage = filters_human.get("feature_coverage") if isinstance(filters_human.get("feature_coverage"), dict) else {}
    if not checks:
        return _clip(filters_human.get("summary"), max_len=600) or "스캐너 후보 비교 근거는 저장된 범위 안에서 제한적으로 확인됩니다."
    pass_count = sum(1 for row in checks if str(row.get("status") or "").strip().upper() == "PASS")
    fail_count = sum(1 for row in checks if str(row.get("status") or "").strip().upper() == "FAIL")
    na_count = sum(1 for row in checks if str(row.get("status") or "").strip().upper() == "NOT_AVAILABLE")
    present = int(float(feature_coverage.get("present") or 0)) if _num_opt(feature_coverage.get("present")) is not None else 0
    total = int(float(feature_coverage.get("total") or 0)) if _num_opt(feature_coverage.get("total")) is not None else 0
    quality_raw = _clip(feature_coverage.get("quality"), max_len=40).strip().lower()
    quality = {
        "strong": "양호",
        "good": "양호",
        "moderate": "보통",
        "weak": "취약",
    }.get(quality_raw, _clip(feature_coverage.get("quality"), max_len=40) or "not_captured")

    summary = f"스캐너 후보 비교에서는 {len(checks)}개 체크 중 통과 {pass_count}개, 미통과 {fail_count}개, 확인 불가 {na_count}개였습니다."
    if present and total:
        summary += f" 차트 피처 커버리지는 {present}/{total}로 {quality} 수준이었습니다."
    return summary


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
    raw = _clip(value, max_len=220).strip()
    mapping = {
        "breakout_above_recent_high_with_vwap_structure_confirmation": "직전 고점 돌파와 VWAP 구조 확인",
        "breakout_confirmed": "돌파 확인",
        "pullback_rebound_confirmed": "눌림목 반등 확인",
        "reclaim_confirmed": "VWAP 재회복 확인",
        "breakout_vwap_hold": "돌파 후 VWAP 지지 확인",
    }
    if not raw:
        return ""
    if raw in mapping:
        return mapping[raw]
    return raw.replace("_", " ")


def _exit_reason_label(value: Any) -> str:
    return _exit_reason_label_impl(value)

def _decision_chain_label(value: Any) -> str:
    raw = _clip(value, max_len=80).strip().lower()
    mapping = {
        "confirmed_exit_signal": "청산 확인 신호",
        "peak_drawdown": "고점 대비 하락폭",
        "breakout_above_recent_high_with_vwap_structure_confirmation": "직전 고점 돌파와 VWAP 구조 확인",
        "hard_stop": "고정 손절",
        "partial_take_profit": "1차 일부 익절",
        "profit_ladder": "구간별 분할 익절",
        "risk_reward_take_profit": "손익비 익절",
        "vwap_extension_take_profit": "VWAP 과확장 익절",
        "resistance_take_profit": "저항권 익절",
        "volume_exhaustion_take_profit": "거래량 둔화 익절",
        "opening_gap_profit_take": "갭 추격 빠른 익절",
        "time_decay_profit_exit": "시간 경과 수익 보전",
        "vwap_breakdown": "VWAP 이탈",
        "breakout_path": "돌파 경로",
    }
    return mapping.get(raw, _clip(value, max_len=80))


def _humanize_duration_text(value: Any, *, fallback_seconds: Any = None) -> str:
    text = _clip(value, max_len=80).strip()
    lowered = text.lower()
    total_seconds: Optional[int] = None

    if text:
        if _safe_fullmatch(r"\d{1,2}:\d{2}:\d{2}", text):
            hours, minutes, seconds = [int(part) for part in text.split(":")]
            total_seconds = hours * 3600 + minutes * 60 + seconds
        elif _safe_fullmatch(r"\d{1,2}:\d{2}", text):
            minutes, seconds = [int(part) for part in text.split(":")]
            total_seconds = minutes * 60 + seconds
        else:
            hour_match = _safe_fullmatch(r"([0-9]+(?:\.[0-9]+)?)\s*h", lowered)
            minute_match = _safe_fullmatch(r"([0-9]+(?:\.[0-9]+)?)\s*m", lowered)
            second_match = _safe_fullmatch(r"([0-9]+(?:\.[0-9]+)?)\s*s", lowered)
            if hour_match:
                total_seconds = int(round(float(hour_match.group(1)) * 3600))
            elif minute_match:
                total_seconds = int(round(float(minute_match.group(1)) * 60))
            elif second_match:
                total_seconds = int(round(float(second_match.group(1))))

    if total_seconds is None and fallback_seconds not in (None, ""):
        try:
            total_seconds = int(round(float(fallback_seconds)))
        except Exception:
            total_seconds = None

    if total_seconds is None:
        return text

    hours, remainder = divmod(max(total_seconds, 0), 3600)
    minutes, seconds = divmod(remainder, 60)
    parts: List[str] = []
    if hours:
        parts.append(f"{hours}시간")
    if minutes:
        parts.append(f"{minutes}분")
    if seconds or not parts:
        parts.append(f"{seconds}초")
    return " ".join(parts)


def _holding_duration_label(value: Any) -> str:
    text = _humanize_duration_text(value)
    if not text:
        return ""
    return f"보유 시간은 {text}였습니다."


def _execution_mode_label(value: Any) -> str:
    raw = _clip(value, max_len=120).strip().lower()
    mapping = {
        "simulation trade report": "시뮬레이션 거래 리포트",
        "simulation": "시뮬레이션",
        "simulation (mock broker)": "시뮬레이션 (모의 브로커)",
        "real": "실거래",
        "live": "실거래",
    }
    return mapping.get(raw, _clip(value, max_len=120))


def _entry_path_label(value: Any) -> str:
    raw = _clip(value, max_len=80).strip().lower()
    mapping = {
        "breakout_path": "돌파 경로",
        "pullback_volume_path": "눌림목·거래량 경로",
        "reclaim_path": "재회복 경로",
    }
    return mapping.get(raw, _clip(value, max_len=80))


def _entry_gate_state_label(value: Any) -> str:
    if value is True:
        return "통과"
    if value is False:
        return "미통과"
    return "기록 없음"


def _entry_gate_name_label(value: str) -> str:
    mapping = {
        "reclaim": "VWAP 재회복",
        "extension": "과확장 점검",
        "confidence gate": "신뢰도 게이트",
    }
    return mapping.get(value, value)


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
    grouped_trace = _as_dict(monitor_reason.get("entry_grouped_logic_trace"))
    entry_scores = _as_dict(monitor_reason.get("entry_condition_scores"))
    has_entry_gate_snapshot = bool(
        grouped_trace
        or entry_scores
        or monitor_reason.get("entry_condition_path") not in (None, "")
    )
    if not has_entry_gate_snapshot:
        return False

    status_text = _clip(
        story_input.get("status")
        or story_input.get("lifecycle_status")
        or _as_dict(story_input.get("shared_facts")).get("status"),
        max_len=40,
    ).lower()
    action_text = _clip(
        story_input.get("action")
        or _as_dict(story_input.get("shared_facts")).get("action"),
        max_len=40,
    ).upper()
    posture = _clip(monitor_reason.get("posture"), max_len=40).upper()
    has_exit_axis = any(
        monitor_reason.get(key) not in (None, "", [], {})
        for key in (
            "active_exit_axis",
            "exit_triggered",
            "position_age_seconds",
            "trigger_type",
            "peak_drawdown",
            "current_drawdown",
            "effective_stop_loss_pct",
            "watch_axes",
        )
    )
    return bool(has_exit_axis and (status_text == "closed" or action_text == "SELL" or posture in {"SELL", "HOLD"}))


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
    text = str(value or "").strip()
    if not text:
        return noun_suffix
    tail = "입니다." if noun_suffix == "입니다." else noun_suffix
    last = text[-1]
    code = ord(last)
    if 0xAC00 <= code <= 0xD7A3:
        has_batchim = (code - 0xAC00) % 28 != 0
        if tail == "입니다.":
            return "이었습니다." if has_batchim else "였습니다."
    return tail


def _korean_euro_ro(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return "로"
    last = text[-1]
    code = ord(last)
    if 0xAC00 <= code <= 0xD7A3:
        jong = (code - 0xAC00) % 28
        if jong == 0 or jong == 8:
            return "로"
        return "으로"
    return "로"


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
    reason = _clip(exit_summary.get("reason_human"), max_len=600)
    reason_label = _exit_reason_label(reason)
    if status_text.lower() == "open":
        return reason_label or "현재 포지션은 아직 열려 있어 확정된 청산 체결은 기록되지 않았습니다."
    if reason or reason_label:
        price = _fmt_price(monitor_context.get("current_price"))
        avg_price = _fmt_price(monitor_context.get("average_price"))
        drawdown = _fmt_pct(monitor_context.get("current_drawdown"))
        axis = _operator_axis_label(_clip(monitor_context.get("active_exit_axis"), max_len=64))
        confirm_required = monitor_context.get("confirm_required")
        confirm_count = monitor_context.get("confirm_count")
        details: List[str] = []
        if axis:
            details.append(f"핵심 청산 축은 {axis}")
        if confirm_required is not None:
            details.append(f"확인 조건은 {int(confirm_count or 0)}/{int(confirm_required or 0)}")
        if price != "-" and avg_price != "-":
            details.append(f"현재가는 {price}, 평균가는 {avg_price}")
        if drawdown != "-":
            details.append(f"현재 손익 변동은 {drawdown}")
        if details:
            return f"{reason_label or reason}. 청산 당시 상황은 " + ", ".join(details) + "입니다."
        return reason_label or reason
    return "청산 판단 근거는 저장된 데이터 범위 안에서 충분히 확인되지 않았습니다."


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
    data = summary if isinstance(summary, dict) else {}
    strategist_ctx = data.get("strategist_context") if isinstance(data.get("strategist_context"), dict) else {}
    scanner_ctx = data.get("scanner_context") if isinstance(data.get("scanner_context"), dict) else {}
    monitor_ctx = data.get("monitor_context") if isinstance(data.get("monitor_context"), dict) else {}
    guard_ctx = data.get("guard_context") if isinstance(data.get("guard_context"), dict) else {}
    execution_ctx = data.get("execution_context") if isinstance(data.get("execution_context"), dict) else {}
    return {
        "run_id": _clip(data.get("run_id"), max_len=40),
        "ts": _clip(data.get("ts"), max_len=40),
        "action": _clip(data.get("action"), max_len=24),
        "reason_human": _clip(data.get("reason_human"), max_len=280),
        "strategist_context": {
            "market_regime": _clip(strategist_ctx.get("market_regime"), max_len=32),
            "market_sentiment": _clip(strategist_ctx.get("market_sentiment"), max_len=32),
            "playbook": _clip(strategist_ctx.get("playbook"), max_len=40),
            "themes": _listify(strategist_ctx.get("themes"), max_items=4, max_len=80),
            "global_sentiment_score": strategist_ctx.get("global_sentiment_score"),
            "vix_level": strategist_ctx.get("vix_level"),
            "headline_count": strategist_ctx.get("headline_count"),
            "news_query_targets": _listify(strategist_ctx.get("news_query_targets"), max_items=5, max_len=80),
            "stress_flags": _listify(strategist_ctx.get("stress_flags"), max_items=4, max_len=80),
        },
        "scanner_context": {
            "selected_symbol": _clip(scanner_ctx.get("selected_symbol"), max_len=24),
            "selected_rank": scanner_ctx.get("selected_rank"),
            "universe_size": scanner_ctx.get("universe_size"),
            "score_total": scanner_ctx.get("score_total"),
            "confidence": scanner_ctx.get("confidence"),
            "top_candidates": _compact_named_rows(scanner_ctx.get("top_candidates"), max_items=3),
            "selection_reason": _clip(scanner_ctx.get("selection_reason"), max_len=220),
        },
        "monitor_context": _compact_monitor_snapshot(monitor_ctx),
        "guard_context": {
            "status": _clip(guard_ctx.get("status") or guard_ctx.get("verdict"), max_len=32),
            "summary": _clip(guard_ctx.get("summary") or guard_ctx.get("reason"), max_len=220),
        },
        "execution_context": {
            "status": _clip(execution_ctx.get("status"), max_len=32),
            "summary": _clip(execution_ctx.get("summary") or execution_ctx.get("message"), max_len=220),
            "qty": execution_ctx.get("qty"),
            "price": execution_ctx.get("price"),
        },
    }


def _extract_policy_ref_context(story_input: Dict[str, Any], monitor_reason: Dict[str, Any]) -> Dict[str, Any]:
    candidates: List[Dict[str, Any]] = []
    if isinstance(monitor_reason.get("policy_ref"), dict):
        candidates.append(monitor_reason.get("policy_ref"))
    for key in ("entry_summary", "exit_summary"):
        block = story_input.get(key) if isinstance(story_input.get(key), dict) else {}
        monitor_ctx = block.get("monitor_context") if isinstance(block.get("monitor_context"), dict) else {}
        policy_ref = monitor_ctx.get("policy_ref") if isinstance(monitor_ctx.get("policy_ref"), dict) else {}
        if policy_ref:
            candidates.append(policy_ref)
    holding = story_input.get("holding_summary") if isinstance(story_input.get("holding_summary"), dict) else {}
    for row in list(holding.get("holding_events") or [])[:8]:
        if not isinstance(row, dict):
            continue
        monitor_ctx = row.get("monitor_context") if isinstance(row.get("monitor_context"), dict) else {}
        policy_ref = monitor_ctx.get("policy_ref") if isinstance(monitor_ctx.get("policy_ref"), dict) else {}
        if policy_ref:
            candidates.append(policy_ref)
    for policy_ref in candidates:
        symbol_constraints = policy_ref.get("symbol_constraints") if isinstance(policy_ref.get("symbol_constraints"), dict) else {}
        risk_mode = _clip(policy_ref.get("risk_mode"), max_len=40)
        selected_playbook = _clip(policy_ref.get("selected_playbook"), max_len=40)
        preferred_themes = _listify(symbol_constraints.get("preferred_themes"), max_items=6, max_len=80)
        avoid_themes = _listify(symbol_constraints.get("avoid_themes"), max_items=6, max_len=80)
        if risk_mode or selected_playbook or preferred_themes or avoid_themes:
            return {
                "risk_mode": risk_mode,
                "selected_playbook": selected_playbook,
                "preferred_themes": preferred_themes,
                "avoid_themes": avoid_themes,
            }
    return {}


def _extract_scanner_bias_summary(story_input: Dict[str, Any], scanner_reason: Dict[str, Any]) -> Dict[str, Any]:
    candidates: List[Dict[str, Any]] = []
    if isinstance(scanner_reason.get("scanner_bias_summary"), dict) and scanner_reason.get("scanner_bias_summary"):
        candidates.append(scanner_reason.get("scanner_bias_summary"))
    scanner_trace_summary = story_input.get("scanner_trace_summary") if isinstance(story_input.get("scanner_trace_summary"), dict) else {}
    if isinstance(scanner_trace_summary.get("scanner_bias_summary"), dict) and scanner_trace_summary.get("scanner_bias_summary"):
        candidates.append(scanner_trace_summary.get("scanner_bias_summary"))
    canonical_artifacts = story_input.get("canonical_agent_artifacts") if isinstance(story_input.get("canonical_agent_artifacts"), dict) else {}
    canonical_scanner = canonical_artifacts.get("scanner") if isinstance(canonical_artifacts.get("scanner"), dict) else {}
    if isinstance(canonical_scanner.get("scanner_bias_summary"), dict) and canonical_scanner.get("scanner_bias_summary"):
        candidates.append(canonical_scanner.get("scanner_bias_summary"))
    scanner_evidence = story_input.get("scanner_evidence") if isinstance(story_input.get("scanner_evidence"), dict) else {}
    for row in list(scanner_evidence.get("candidate_selection_reasons") or [])[:3]:
        if not isinstance(row, dict):
            continue
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
        if isinstance(payload.get("scanner_bias_summary"), dict) and payload.get("scanner_bias_summary"):
            candidates.append(payload.get("scanner_bias_summary"))
    for item in candidates:
        if item:
            return {
                "enabled": item.get("enabled"),
                "active_biases": _listify(item.get("active_biases"), max_items=6, max_len=80),
                "bias_strength": _clip(item.get("bias_strength"), max_len=24),
                "bias_source": _clip(item.get("bias_source"), max_len=80),
                "summary": _clip(item.get("summary"), max_len=220),
            }
    return {}


def _evidence_digest(evidence: Any, keys: List[str]) -> Dict[str, int]:
    data = evidence if isinstance(evidence, dict) else {}
    return {key: len(list(data.get(key) or [])) for key in keys}


def _extract_strategy_detail_from_source(source: Any) -> Dict[str, Any]:
    data = source if isinstance(source, dict) else {}
    if not data:
        return {}
    strategy_policy = _as_dict(data.get("strategy_policy"))
    market_policy = _as_dict(strategy_policy.get("market_policy"))
    scanner_policy = _as_dict(strategy_policy.get("scanner_policy"))
    direct_detail = _as_dict(data.get("strategy_detail"))

    def _pick_text(key: str, *, max_len: int = 80) -> str:
        return _first_nonempty_text(
            direct_detail.get(key),
            data.get(key),
            market_policy.get(key),
            max_len=max_len,
        )

    detail: Dict[str, Any] = {}
    for key in (
        "pre_llm_playbook",
        "llm_requested_playbook",
        "requested_playbook",
        "requested_playbook_source",
        "final_playbook",
        "tactical_strategy",
        "tactical_subtype",
    ):
        value = _pick_text(key)
        if value:
            detail[key] = value

    scores = (
        _as_dict(direct_detail.get("strategy_scores"))
        or _as_dict(data.get("strategy_scores"))
        or _as_dict(market_policy.get("strategy_scores"))
    )
    if scores:
        detail["strategy_scores"] = {
            str(key): value
            for key, value in list(scores.items())[:8]
            if str(key or "").strip()
        }

    rejected = (
        _as_dict(direct_detail.get("rejected_strategy_reasons"))
        or _as_dict(data.get("rejected_strategy_reasons"))
        or _as_dict(market_policy.get("rejected_strategy_reasons"))
    )
    if rejected:
        detail["rejected_strategy_reasons"] = _compact_scalar_dict(rejected, max_items=6, max_len=180)

    watch = (
        _as_dict(direct_detail.get("candidate_watch_policy"))
        or _as_dict(data.get("candidate_watch_policy"))
        or _as_dict(scanner_policy.get("candidate_watch_policy"))
    )
    if watch:
        detail["candidate_watch_policy"] = {
            "behavior_effect": _clip(watch.get("behavior_effect"), max_len=40),
            "source": _clip(watch.get("source"), max_len=80),
            "max_priority_rank": watch.get("max_priority_rank"),
            "max_runner_ups": watch.get("max_runner_ups"),
            "cascade_enabled": watch.get("cascade_enabled"),
            "tactical_strategy": _clip(watch.get("tactical_strategy"), max_len=80),
            "reason": _clip(watch.get("reason"), max_len=220),
            "cascade_allowed_reasons": _listify(watch.get("cascade_allowed_reasons"), max_items=6, max_len=80),
            "cascade_blocked_reasons": _listify(watch.get("cascade_blocked_reasons"), max_items=8, max_len=80),
        }

    return {key: value for key, value in detail.items() if value not in ("", None, [], {})}


def _compact_strategy_detail_context(value: Any) -> Dict[str, Any]:
    detail = _as_dict(value)
    if not detail:
        return {}
    out: Dict[str, Any] = {}
    for key, max_len in (
        ("pre_llm_playbook", 60),
        ("llm_requested_playbook", 60),
        ("requested_playbook", 60),
        ("requested_playbook_source", 60),
        ("final_playbook", 60),
        ("tactical_strategy", 80),
        ("tactical_subtype", 80),
    ):
        text = _clip(detail.get(key), max_len=max_len)
        if text:
            out[key] = text
    scores = _compact_scalar_dict(detail.get("strategy_scores"), max_items=8, max_len=80)
    if scores:
        out["strategy_scores"] = scores
    rejected = _compact_scalar_dict(detail.get("rejected_strategy_reasons"), max_items=6, max_len=180)
    if rejected:
        out["rejected_strategy_reasons"] = rejected
    watch = _as_dict(detail.get("candidate_watch_policy"))
    if watch:
        watch_out = {
            "behavior_effect": _clip(watch.get("behavior_effect"), max_len=40),
            "source": _clip(watch.get("source"), max_len=80),
            "max_priority_rank": watch.get("max_priority_rank"),
            "max_runner_ups": watch.get("max_runner_ups"),
            "cascade_enabled": watch.get("cascade_enabled"),
            "tactical_strategy": _clip(watch.get("tactical_strategy"), max_len=80),
            "reason": _clip(watch.get("reason"), max_len=220),
            "cascade_allowed_reasons": _listify(watch.get("cascade_allowed_reasons"), max_items=6, max_len=80),
            "cascade_blocked_reasons": _listify(watch.get("cascade_blocked_reasons"), max_items=8, max_len=80),
        }
        watch_out = {key: val for key, val in watch_out.items() if val not in ("", None, [], {})}
        if watch_out:
            out["candidate_watch_policy"] = watch_out
    return out


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
    out = dict(proposal or {})
    control = _as_dict(entry_control)
    nested = _as_dict(control.get("proposal")) or _as_dict(control.get("candidate_watch_policy_proposal"))
    if not out and nested:
        out = dict(nested)
    if not out:
        return {}
    if out.get("max_priority_rank") in (None, "") and control.get("proposed_max_priority_rank") not in (None, ""):
        out["max_priority_rank"] = control.get("proposed_max_priority_rank")
    if out.get("max_runner_ups") in (None, "") and control.get("proposed_max_runner_ups") not in (None, ""):
        out["max_runner_ups"] = control.get("proposed_max_runner_ups")
    if out.get("cascade_enabled") in (None, "") and nested.get("cascade_enabled") not in (None, ""):
        out["cascade_enabled"] = nested.get("cascade_enabled")
    for key in ("source", "behavior_effect", "tactical_strategy", "reason"):
        if out.get(key) in (None, "") and nested.get(key) not in (None, ""):
            out[key] = nested.get(key)
    for key in ("cascade_allowed_reasons", "cascade_blocked_reasons"):
        if out.get(key) in (None, "", []) and nested.get(key) not in (None, "", []):
            out[key] = nested.get(key)
    return _compact_candidate_watch_proposal(out)


def _compact_commander_entry_control(value: Any) -> Dict[str, Any]:
    data = _as_dict(value)
    if not data:
        return {}
    proposal = _compact_candidate_watch_proposal(data.get("candidate_watch_policy_proposal"))
    out = {
        "schema_version": _clip(data.get("schema_version"), max_len=80),
        "mode": _clip(data.get("mode"), max_len=80),
        "decision": _clip(data.get("decision"), max_len=100),
        "reason": _clip(data.get("reason"), max_len=220),
        "max_priority_rank": data.get("max_priority_rank"),
        "max_runner_ups": data.get("max_runner_ups"),
        "cascade_enabled": data.get("cascade_enabled"),
        "candidate_watch_policy_detected": data.get("candidate_watch_policy_detected"),
        "candidate_watch_policy_applied": data.get("candidate_watch_policy_applied"),
        "candidate_watch_policy_effect": _clip(data.get("candidate_watch_policy_effect"), max_len=80),
        "candidate_watch_policy_clamp_reason": _clip(
            data.get("candidate_watch_policy_clamp_reason"),
            max_len=220,
        ),
        "proposed_max_priority_rank": data.get("proposed_max_priority_rank") or proposal.get("max_priority_rank"),
        "proposed_max_runner_ups": data.get("proposed_max_runner_ups") or proposal.get("max_runner_ups"),
        "proposal": proposal,
        "cascade_allowed_reasons": _listify(data.get("cascade_allowed_reasons"), max_items=6, max_len=80),
        "cascade_blocked_reasons": _listify(data.get("cascade_blocked_reasons"), max_items=8, max_len=80),
    }
    return {key: value for key, value in out.items() if value not in ("", None, [], {})}


def _compact_entry_candidate_cascade(value: Any) -> Dict[str, Any]:
    data = _as_dict(value)
    if not data:
        return {}
    trace_rows: List[Dict[str, Any]] = []
    for row in list(data.get("fallback_trace") or [])[:6]:
        item = _as_dict(row)
        if not item:
            continue
        trace_rows.append(
            {
                "symbol": _clip(item.get("symbol"), max_len=24),
                "rank": item.get("rank"),
                "score_total": item.get("score_total"),
                "triggered": item.get("triggered"),
                "reason": _clip(item.get("reason"), max_len=120),
                "primary_failure_axis": _clip(item.get("primary_failure_axis"), max_len=80),
                "guard_blocked": item.get("guard_blocked"),
                "confidence_score": item.get("confidence_score"),
                "confidence_threshold": item.get("confidence_threshold"),
                "volume_ratio": item.get("volume_ratio"),
                "vwap_distance": item.get("vwap_distance"),
            }
        )
    trace_rows = [
        {key: value for key, value in row.items() if value not in ("", None, [], {})}
        for row in trace_rows
    ]
    out = {
        "attempted": data.get("attempted"),
        "eligible": data.get("eligible"),
        "cascade_enabled": data.get("cascade_enabled"),
        "reason": _clip(data.get("reason"), max_len=140),
        "blocked_reason": _clip(data.get("blocked_reason"), max_len=140),
        "top_pick_symbol": _clip(data.get("top_pick_symbol"), max_len=24),
        "top_pick_triggered": data.get("top_pick_triggered"),
        "top_pick_reason": _clip(data.get("top_pick_reason"), max_len=140),
        "top_pick_guard_blocked": data.get("top_pick_guard_blocked"),
        "max_priority_rank": data.get("max_priority_rank"),
        "max_runner_ups": data.get("max_runner_ups"),
        "control_source": _clip(data.get("control_source"), max_len=80),
        "control_mode": _clip(data.get("control_mode"), max_len=80),
        "runner_up_symbols": _listify(data.get("runner_up_symbols"), max_items=9, max_len=24),
        "fallback_used": data.get("fallback_used"),
        "fallback_from_symbol": _clip(data.get("fallback_from_symbol"), max_len=24),
        "fallback_to_symbol": _clip(data.get("fallback_to_symbol"), max_len=24),
        "fallback_to_rank": data.get("fallback_to_rank"),
        "final_selected_symbol": _clip(data.get("final_selected_symbol"), max_len=24),
        "final_selected_rank": data.get("final_selected_rank"),
        "fallback_trace": trace_rows,
        "cascade_allowed_reasons": _listify(data.get("cascade_allowed_reasons"), max_items=6, max_len=80),
        "cascade_blocked_reasons": _listify(data.get("cascade_blocked_reasons"), max_items=8, max_len=80),
    }
    return {key: value for key, value in out.items() if value not in ("", None, [], {})}


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
    parts: List[str] = []
    if proposal:
        parts.append(
            "strategy proposed "
            f"rank<={proposal.get('max_priority_rank', '-')}, runner_ups={proposal.get('max_runner_ups', '-')}"
        )
    if entry_control:
        parts.append(
            "commander applied "
            f"rank<={entry_control.get('max_priority_rank', '-')}, runner_ups={entry_control.get('max_runner_ups', '-')}"
        )
        clamp_reason = _clip(entry_control.get("candidate_watch_policy_clamp_reason"), max_len=120)
        if clamp_reason:
            parts.append(f"clamp={clamp_reason}")
    if cascade:
        attempted = "attempted" if bool(cascade.get("attempted")) else "not_attempted"
        fallback = cascade.get("fallback_to_symbol") if bool(cascade.get("fallback_used")) else ""
        if fallback:
            parts.append(f"monitor {attempted}, fallback_to={fallback}")
        else:
            blocked = _clip(cascade.get("blocked_reason"), max_len=120)
            suffix = f", blocked={blocked}" if blocked else ""
            parts.append(f"monitor {attempted}{suffix}")
    return "; ".join(part for part in parts if part)


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
    canonical = story_input.get("canonical_agent_artifacts") if isinstance(story_input.get("canonical_agent_artifacts"), dict) else {}
    carriers = [
        story_input.get("strategist_output"),
        story_input.get("strategist"),
        canonical.get("strategist"),
        story_input,
    ]
    fields = (
        "strategy_thesis",
        "strategy_delta_trace",
        "strategy_refresh_trace",
        "memory_usage_trace",
        "news_usage_trace",
        "scanner_handoff",
        "monitor_handoff",
        "conflict_analysis",
        "trade_permission_frame",
        "responsibility_boundary",
        "strategy_detail",
    )
    out: Dict[str, Any] = {}
    for carrier in carriers:
        source = carrier if isinstance(carrier, dict) else {}
        if not source:
            continue
        for field in fields:
            if field in out:
                continue
            value = source.get(field)
            if isinstance(value, dict) and value:
                out[field] = dict(value)
    if "strategy_detail" not in out:
        for carrier in carriers:
            detail = _extract_strategy_detail_from_source(carrier)
            if detail:
                out["strategy_detail"] = detail
                break
    return out


def _build_report_strategist_refresh_trace(story_input: Dict[str, Any]) -> Dict[str, Any]:
    canonical = story_input.get("canonical_agent_artifacts") if isinstance(story_input.get("canonical_agent_artifacts"), dict) else {}
    strategist_artifact = canonical.get("strategist") if isinstance(canonical.get("strategist"), dict) else {}
    commander_artifact = canonical.get("commander") if isinstance(canonical.get("commander"), dict) else {}
    strategist_output = (
        story_input.get("strategist_output")
        if isinstance(story_input.get("strategist_output"), dict)
        else strategist_artifact
    )
    if not isinstance(strategist_output, dict):
        strategist_output = {}
    commander_decision = (
        commander_artifact.get("commander_decision")
        if isinstance(commander_artifact.get("commander_decision"), dict)
        else story_input.get("commander_decision")
        if isinstance(story_input.get("commander_decision"), dict)
        else {}
    )
    if isinstance(strategist_artifact.get("strategy_refresh_trace"), dict) and strategist_artifact.get("strategy_refresh_trace"):
        return _compact_strategy_refresh_trace(strategist_artifact.get("strategy_refresh_trace"))
    if isinstance(strategist_output.get("strategy_refresh_trace"), dict) and strategist_output.get("strategy_refresh_trace"):
        return _compact_strategy_refresh_trace(strategist_output.get("strategy_refresh_trace"))
    trace = build_strategy_refresh_trace(
        strategist_output=dict(strategist_output),
        state={
            "commander_decision": dict(commander_decision or {}),
            "route_observability": dict(commander_artifact.get("route_observability") or {}),
        },
    )
    return _compact_strategy_refresh_trace(trace)


def _compact_strategy_refresh_trace(value: Any) -> Dict[str, Any]:
    trace = value if isinstance(value, dict) else {}
    stages: List[Dict[str, Any]] = []
    for row in list(trace.get("stages") or [])[:4]:
        if not isinstance(row, dict):
            continue
        quant_context = _as_dict(row.get("quant_context") or row.get("strategist_quant_context"))
        quant_market = _as_dict(quant_context.get("quant_market_context"))
        quant_scorecard = _as_dict(quant_market.get("scorecard"))
        quant_feedback = _as_dict(quant_scorecard.get("quant_memory_feedback"))
        compact_stage = {
            "stage": _clip(row.get("stage"), max_len=80),
            "label": _clip(row.get("label"), max_len=80),
            "summary": _clip(row.get("summary"), max_len=320),
            "requested": row.get("requested"),
            "evaluated": row.get("evaluated"),
            "effective": row.get("effective"),
            "reason": _clip(row.get("reason"), max_len=160),
            "selected_symbol": _clip(row.get("selected_symbol"), max_len=24),
            "policy_delta_count": row.get("policy_delta_count"),
            "policy_delta_fields": _listify(row.get("policy_delta_fields"), max_items=8, max_len=80),
        }
        if quant_context:
            compact_stage.update(
                {
                    "quant_context_call_kind": _clip(quant_context.get("call_kind"), max_len=80),
                    "quant_scorecard_available": quant_scorecard.get("available"),
                    "quant_feedback_tags": _listify(quant_feedback.get("feedback_tags"), max_items=8, max_len=80),
                    "selected_symbol_quant_snapshot_present": bool(quant_context.get("selected_symbol_quant_snapshot")),
                    "hold_quant_context_present": bool(quant_context.get("hold_quant_context")),
                    "carry_quant_context_present": bool(quant_context.get("carry_quant_context")),
                    "quant_behavior_effect": _clip(quant_context.get("behavior_effect"), max_len=80),
                }
            )
        stages.append(
            {key: val for key, val in compact_stage.items() if val not in ("", None, [], {})}
        )
    out = {
        "summary": _clip(trace.get("summary"), max_len=700),
        "bullets": _listify(trace.get("bullets"), max_items=8, max_len=220),
        "stages": stages,
        "refresh_requested": trace.get("refresh_requested"),
        "refresh_effective": trace.get("refresh_effective"),
        "policy_delta_count": trace.get("policy_delta_count"),
        "policy_delta_fields": _listify(trace.get("policy_delta_fields"), max_items=8, max_len=80),
        "source": _clip(trace.get("source"), max_len=120),
        "llm_interpretation": _compact_scalar_dict(trace.get("llm_interpretation"), max_items=4, max_len=240),
    }
    return {key: val for key, val in out.items() if val not in ("", None, [], {})}


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
    trace = value if isinstance(value, dict) else {}
    return {
        "captured": trace.get("captured"),
        "enabled": trace.get("enabled"),
        "applied": trace.get("applied"),
        "entry_applied": trace.get("entry_applied"),
        "hold_applied": trace.get("hold_applied"),
        "exit_applied": trace.get("exit_applied"),
        "not_applied_reason": _clip(trace.get("not_applied_reason"), max_len=120),
        "bias_source": _clip(trace.get("bias_source"), max_len=80),
        "active_layers": _listify(trace.get("active_layers"), max_items=5, max_len=32),
        "source_delta_keys": _listify(trace.get("source_delta_keys"), max_items=8, max_len=48),
        "entry_delta_keys": _listify(trace.get("entry_delta_keys"), max_items=8, max_len=48),
        "hold_delta_keys": _listify(trace.get("hold_delta_keys"), max_items=8, max_len=48),
        "exit_delta_keys": _listify(trace.get("exit_delta_keys"), max_items=8, max_len=48),
        "selected_symbol": _clip(trace.get("selected_symbol"), max_len=24),
        "selected_bias_adjustment": trace.get("selected_bias_adjustment"),
        "effective_policy_source": _clip(trace.get("effective_policy_source"), max_len=80),
        "reason": _listify(trace.get("reason"), max_items=5, max_len=80),
    }


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
    row = entry if isinstance(entry, dict) else {}
    source = str(row.get("source") or "fallback").strip().lower()
    path = str(row.get("artifact_path") or "").strip()
    confidence = str(row.get("confidence") or "").strip().lower()
    if confidence not in {"high", "medium", "low"}:
        if source == "canonical":
            confidence = "high"
        elif source in {"direct_artifact", "direct"}:
            confidence = "medium"
        else:
            confidence = "low"
    if confidence == "high":
        completeness = 1.0
    elif confidence == "medium":
        completeness = 0.75
    else:
        completeness = 0.5 if source != "fallback" else 0.35
    return {
        "source": source or "fallback",
        "evidence_source": source or "fallback",
        "artifact_path": path,
        "confidence": confidence,
        "completeness": completeness,
    }


def _report_section_provenance(story_input: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    source = story_input.get("section_provenance") if isinstance(story_input.get("section_provenance"), dict) else {}
    fallback = _normalize_provenance_entry({"source": "fallback", "artifact_path": "", "confidence": "low"})
    seeded = source.get("report_section_provenance_seeds") if isinstance(source.get("report_section_provenance_seeds"), dict) else {}

    def _pick(section_key: str, *legacy_keys: str) -> Dict[str, Any]:
        direct = source.get(section_key)
        if isinstance(direct, dict) and direct:
            return _normalize_provenance_entry(direct)
        seeded_entry = seeded.get(section_key)
        if isinstance(seeded_entry, dict) and seeded_entry:
            return _normalize_provenance_entry(seeded_entry)
        for legacy_key in legacy_keys:
            legacy = source.get(legacy_key)
            if isinstance(legacy, dict) and legacy:
                return _normalize_provenance_entry(legacy)
        return fallback

    return {
        "executive_summary": _pick("executive_summary", "operator_conclusion_human"),
        "market_context_at_entry": _pick("market_context_at_entry", "market_context_human"),
        "strategist_summary": _pick("strategist_summary", "market_context_at_entry", "market_context_human"),
        "strategist_refresh_trace": _pick("strategist_refresh_trace", "strategist_output", "commander"),
        "why_this_symbol_was_chosen": _pick("why_this_symbol_was_chosen", "scanner_reason_human"),
        "entry_decision": _pick("entry_decision", "why_this_symbol_was_chosen", "scanner_reason_human"),
        "holding_monitoring_story": _pick("holding_monitoring_story", "monitor_reason_human"),
        "exit_decision": _pick("exit_decision", "holding_monitoring_story", "monitor_reason_human"),
        "execution_quality": _pick("execution_quality", "execution_outcome_human"),
        "scanner_filters": _pick("scanner_filters", "filters_human"),
        "guard_approval_result": _pick("guard_approval_result", "guard_reason_human"),
        "reporter_evaluation": _pick("reporter_evaluation", "reporter_status_human"),
        "errors_weaknesses_improvement_points": _pick("errors_weaknesses_improvement_points", "reporter_evaluation", "reporter_status_human"),
        "full_timeline": _pick("full_timeline", "timeline"),
        "final_operator_conclusion": _pick("final_operator_conclusion", "operator_conclusion_human"),
    }


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
    out = dict(report or {})
    diagnostics = story_input.get("ai_report_diagnostics") if isinstance(story_input.get("ai_report_diagnostics"), dict) else {}
    llm_brief_status = _canonical_ai_report_status(diagnostics.get("llm_brief_status") or "skipped")
    out["deterministic_report_status"] = _canonical_ai_report_status(deterministic_report_status)
    out["llm_brief_status"] = llm_brief_status
    out["ai_trade_report_status"] = _canonical_ai_report_status(ai_trade_report_status)
    generation = out.get("generation") if isinstance(out.get("generation"), dict) else {}
    generation["deterministic_report_status"] = out["deterministic_report_status"]
    generation["llm_brief_status"] = out["llm_brief_status"]
    generation["ai_trade_report_status"] = out["ai_trade_report_status"]
    out["generation"] = generation
    if "fact_payload" not in out or "narrative" not in out:
        separated_trade_model = _resolve_separated_trade_model(story_input)
        runtime_mode = str(story_input.get("report_runtime_mode") or "").strip().lower()
        enable_separated_narrative = bool(story_input.get("enable_separated_narrative"))
        skip_separated_report_llm = bool(story_input.get("skip_separated_report_llm"))
        try:
            if enable_separated_narrative and not skip_separated_report_llm:
                from libs.reporting.fact_narrative_report import build_separated_report

                separated = build_separated_report(
                    trade_model=dict(separated_trade_model or {}),
                    model=str(generation.get("model") or "").strip() or None,
                    execution_profile=_resolve_intraday_report_execution_profile(
                        dict(separated_trade_model or {})
                    ),
                )
            else:
                skip_reason = (
                    f"{runtime_mode or 'runtime'}_skip_separated_report_llm"
                    if skip_separated_report_llm
                    else f"{runtime_mode or 'runtime'}_separated_narrative_disabled"
                )
                separated = _build_skipped_separated_report(
                    dict(separated_trade_model or {}),
                    reason=skip_reason,
                )
        except Exception:
            separated = {
                "fact_payload": {"trade": dict(separated_trade_model or {}), "daily": {}, "symbol": {}},
                "narrative": {
                    "summary": "",
                    "insight": "",
                    "recommendation": "",
                    "source": "llm",
                    "based_on": "fact_payload",
                    "status": "error",
                },
            }
        if isinstance(separated.get("fact_payload"), dict):
            out["fact_payload"] = dict(separated.get("fact_payload") or {})
        if isinstance(separated.get("narrative"), dict):
            out["narrative"] = dict(separated.get("narrative") or {})
    post_exit_shadow = _story_post_exit_shadow(story_input)
    if post_exit_shadow:
        out.setdefault("post_exit_shadow", dict(post_exit_shadow))
        fact_payload = out.get("fact_payload") if isinstance(out.get("fact_payload"), dict) else {}
        if fact_payload:
            fact_payload = dict(fact_payload)
            fact_payload.setdefault("post_exit_shadow", dict(post_exit_shadow))
            out["fact_payload"] = fact_payload
    return out


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
