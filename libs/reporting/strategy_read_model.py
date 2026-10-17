from __future__ import annotations

"""Read-only strategist linkage helpers for Phase 5-2 reporting phases.

These helpers assemble additive views that connect strategist news context,
candidate hints, and the selected symbol without depending on UI modules.
They also provide compact strategist-facing feedback summaries derived from
trade story artifacts.
"""

from collections import Counter
from typing import Any, Dict, List

from libs.core.symbols import normalize_symbol
import sys as _r3_sys
from libs.agents.reporter.read_models.strategy_read_model_bodies_01 import (  # R-4 owner bodies (facade-injected)
    _list_text_r4_impl,
    _headline_text_r4_impl,
    _headline_matches_symbol_r4_impl,
    _collect_top_headlines_r4_impl,
    _rows_from_news_like_r4_impl,
    _candidate_hypotheses_r4_impl,
    _hypothesis_for_symbol_r4_impl,
    _collect_text_fragments_r4_impl,
    _entry_pattern_type_r4_impl,
    _entry_timing_quality_r4_impl,
    _entry_confirmation_quality_r4_impl,
    _exit_pattern_type_r4_impl,
    _exit_quality_r4_impl,
    _thesis_invalidation_code_r4_impl,
    _safe_float_r4_impl,
    _compact_recent_trade_ref_r4_impl,
    _improvement_tags_r4_impl,
    _review_flags_r4_impl,
)
from libs.agents.reporter.read_models.strategy_read_model_bodies_02 import (  # R-4 owner bodies (facade-injected)
    build_news_symbol_linkage_view_r4_impl,
    build_strategist_feedback_input_view_r4_impl,
    normalize_strategist_feedback_input_r4_impl,
    build_recent_strategist_feedback_window_r4_impl,
)


def _clip(value: Any, *, max_len: int = 220) -> str:
    text = str(value or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max(0, max_len - 3)] + "..."


def _list_text(values: Any, *, limit: int = 8, max_len: int = 120) -> List[str]:
    return _list_text_r4_impl(values, limit=limit, max_len=max_len, facade=_r3_sys.modules[__name__])


def _norm_symbol(value: Any) -> str:
    return normalize_symbol(value, allow_test_symbols=True).strip().upper()


def _headline_text(row: Any) -> str:
    return _headline_text_r4_impl(row, facade=_r3_sys.modules[__name__])


def _headline_matches_symbol(row: Any, symbol: str) -> bool:
    return _headline_matches_symbol_r4_impl(row, symbol, facade=_r3_sys.modules[__name__])


def _collect_top_headlines(rows: Any, *, limit: int = 3, symbol: str = "") -> List[str]:
    return _collect_top_headlines_r4_impl(rows, limit=limit, symbol=symbol, facade=_r3_sys.modules[__name__])


def _rows_from_news_like(value: Any) -> List[Dict[str, Any]]:
    return _rows_from_news_like_r4_impl(value, facade=_r3_sys.modules[__name__])


def _candidate_hints(summary: Dict[str, Any], parsed: Dict[str, Any]) -> List[str]:
    hints = summary.get("candidate_symbols_hint")
    if not isinstance(hints, list):
        hints = parsed.get("candidate_symbols_hint")
    return [symbol for symbol in (_norm_symbol(value) for value in list(hints or [])) if symbol][:8]


def _candidate_hypotheses(summary: Dict[str, Any], parsed: Dict[str, Any]) -> List[Dict[str, str]]:
    return _candidate_hypotheses_r4_impl(summary, parsed, facade=_r3_sys.modules[__name__])


def _hypothesis_for_symbol(hypotheses: List[Dict[str, str]], symbol: str) -> str:
    return _hypothesis_for_symbol_r4_impl(hypotheses, symbol, facade=_r3_sys.modules[__name__])


def _collect_text_fragments(*values: Any) -> str:
    return _collect_text_fragments_r4_impl(*values, facade=_r3_sys.modules[__name__])


def _contains_any(text: str, needles: List[str]) -> bool:
    haystack = str(text or "").lower()
    return any(str(needle or "").lower() in haystack for needle in needles if str(needle or "").strip())


def _entry_pattern_type(text: str) -> str:
    return _entry_pattern_type_r4_impl(text, facade=_r3_sys.modules[__name__])


def _entry_timing_quality(text: str) -> str:
    return _entry_timing_quality_r4_impl(text, facade=_r3_sys.modules[__name__])


def _entry_confirmation_quality(text: str, monitor_reason: Dict[str, Any]) -> str:
    return _entry_confirmation_quality_r4_impl(text, monitor_reason, facade=_r3_sys.modules[__name__])


def _exit_pattern_type(text: str) -> str:
    return _exit_pattern_type_r4_impl(text, facade=_r3_sys.modules[__name__])


def _exit_quality(text: str, exit_pattern_type: str) -> str:
    return _exit_quality_r4_impl(text, exit_pattern_type, facade=_r3_sys.modules[__name__])


def _thesis_invalidation_code(text: str, exit_pattern_type: str) -> str:
    return _thesis_invalidation_code_r4_impl(text, exit_pattern_type, facade=_r3_sys.modules[__name__])


def _append_unique(out: List[str], value: str) -> None:
    text = str(value or "").strip()
    if text and text not in out:
        out.append(text)


def _safe_float(value: Any) -> float | None:
    return _safe_float_r4_impl(value, facade=_r3_sys.modules[__name__])


def _normalize_counter_key(value: Any, *, unknown: str = "unknown") -> str:
    text = _clip(value, max_len=64)
    return text or unknown


def _ordered_counter_dict(counter: Counter[str]) -> Dict[str, int]:
    return {key: count for key, count in sorted(counter.items(), key=lambda row: (-row[1], row[0]))}


def _compact_recent_trade_ref(item: Dict[str, Any]) -> Dict[str, Any]:
    return _compact_recent_trade_ref_r4_impl(item, facade=_r3_sys.modules[__name__])


def _improvement_tags(text: str, thesis_invalidation_code: str, exit_pattern_type: str) -> List[str]:
    return _improvement_tags_r4_impl(text, thesis_invalidation_code, exit_pattern_type, facade=_r3_sys.modules[__name__])


def _review_flags(
    *,
    trade_status: str,
    final_action: str,
    exit_pattern_type: str,
    exit_quality: str,
    entry_confirmation_quality: str,
    improvement_tags: List[str],
) -> List[str]:
    return _review_flags_r4_impl(trade_status=trade_status, final_action=final_action, exit_pattern_type=exit_pattern_type, exit_quality=exit_quality, entry_confirmation_quality=entry_confirmation_quality, improvement_tags=improvement_tags, facade=_r3_sys.modules[__name__])


def build_news_symbol_linkage_view(
    *,
    strategist_summary: Dict[str, Any] | None = None,
    strategist_raw_input: Dict[str, Any] | None = None,
    strategist_parsed_output: Dict[str, Any] | None = None,
    selected_symbol: str = "",
    top_ranked_symbols: Any = None,
) -> Dict[str, Any]:
    return build_news_symbol_linkage_view_r4_impl(strategist_summary=strategist_summary, strategist_raw_input=strategist_raw_input, strategist_parsed_output=strategist_parsed_output, selected_symbol=selected_symbol, top_ranked_symbols=top_ranked_symbols, facade=_r3_sys.modules[__name__])


def build_strategist_feedback_input_view(story_input: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return build_strategist_feedback_input_view_r4_impl(story_input, facade=_r3_sys.modules[__name__])


def normalize_strategist_feedback_input(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return normalize_strategist_feedback_input_r4_impl(payload, facade=_r3_sys.modules[__name__])


def build_recent_strategist_feedback_window(
    items: List[Dict[str, Any]] | None = None,
    *,
    window_size: int = 10,
) -> Dict[str, Any]:
    return build_recent_strategist_feedback_window_r4_impl(items, window_size=window_size, facade=_r3_sys.modules[__name__])


__all__ = [
    "build_news_symbol_linkage_view",
    "build_strategist_feedback_input_view",
    "build_recent_strategist_feedback_window",
    "normalize_strategist_feedback_input",
]
