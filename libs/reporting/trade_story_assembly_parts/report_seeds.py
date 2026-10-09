from __future__ import annotations

from typing import Any, Dict, List, Mapping

from libs.reporting.trade_report_common import clip_text as clip, utc_now_iso
from libs.reporting.trade_reporter_status_text import normalize_reporter_status_human


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
    deps: Mapping[str, Any],
) -> Dict[str, Dict[str, Any]]:
    _list_text = deps["_list_text"]
    normalize_trade_report_section = deps["normalize_trade_report_section"]
    report_like = {
        "market_context_at_entry": dict(market_context_human or {}),
        "why_this_symbol_was_chosen": dict(scanner_reason_human or {}),
        "scanner_filters": dict(filters_human or {}),
        "holding_monitoring_story": dict(monitor_reason_human or {}),
        "exit_decision": dict(execution_outcome_human or {}),
        "execution_quality": dict(execution_outcome_human or {}),
        "guard_approval_result": dict(guard_reason_human or {}),
        "reporter_evaluation": dict(reporter_status_human or {}),
        "final_operator_conclusion": dict(operator_conclusion_human or {}),
    }
    return {
        "market_context_at_entry": normalize_trade_report_section(
            report_like,
            "market_context_at_entry",
            str((market_context_human or {}).get("summary") or ""),
            trim_text=clip,
            clean_str_list=_list_text,
        ),
        "strategist_summary": normalize_trade_report_section(
            report_like,
            "strategist_summary",
            str((market_context_human or {}).get("summary") or ""),
            trim_text=clip,
            clean_str_list=_list_text,
        ),
        "why_this_symbol_was_chosen": normalize_trade_report_section(
            report_like,
            "why_this_symbol_was_chosen",
            str((scanner_reason_human or {}).get("summary") or ""),
            trim_text=clip,
            clean_str_list=_list_text,
        ),
        "entry_decision": normalize_trade_report_section(
            report_like,
            "entry_decision",
            str((scanner_reason_human or {}).get("summary") or ""),
            trim_text=clip,
            clean_str_list=_list_text,
        ),
        "holding_monitoring_story": normalize_trade_report_section(
            report_like,
            "holding_monitoring_story",
            str((monitor_reason_human or {}).get("summary") or ""),
            trim_text=clip,
            clean_str_list=_list_text,
        ),
        "exit_decision": normalize_trade_report_section(
            report_like,
            "exit_decision",
            str((execution_outcome_human or {}).get("summary") or ""),
            trim_text=clip,
            clean_str_list=_list_text,
        ),
        "scanner_filters": normalize_trade_report_section(
            report_like,
            "scanner_filters",
            str((filters_human or {}).get("summary") or ""),
            trim_text=clip,
            clean_str_list=_list_text,
        ),
        "execution_quality": normalize_trade_report_section(
            report_like,
            "execution_quality",
            str((execution_outcome_human or {}).get("summary") or ""),
            trim_text=clip,
            clean_str_list=_list_text,
        ),
        "guard_approval_result": normalize_trade_report_section(
            report_like,
            "guard_approval_result",
            str((guard_reason_human or {}).get("summary") or ""),
            trim_text=clip,
            clean_str_list=_list_text,
        ),
        "reporter_evaluation": normalize_trade_report_section(
            report_like,
            "reporter_evaluation",
            str((reporter_status_human or {}).get("summary") or ""),
            trim_text=clip,
            clean_str_list=_list_text,
        ),
        "final_operator_conclusion": normalize_trade_report_section(
            report_like,
            "final_operator_conclusion",
            str((operator_conclusion_human or {}).get("summary") or ""),
            trim_text=clip,
            clean_str_list=_list_text,
        ),
    }



