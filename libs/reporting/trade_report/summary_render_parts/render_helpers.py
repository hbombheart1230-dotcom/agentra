from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List


def pick_impl(*values: Any) -> Any:
    for value in values:
        if value not in (None, ""):
            return value
    return ""


def money_impl(value: Any, *, _num_opt: Any) -> str:
    num = _num_opt(value)
    if num is None:
        return "-"
    if abs(num) >= 100:
        return f"{num:,.0f}"
    return f"{num:,.2f}".rstrip("0").rstrip(".")


def compact_number_impl(value: Any, *, _metadata_value: Any, _num_opt: Any) -> str:
    num = _num_opt(value)
    if num is not None:
        rendered = f"{num:.6f}".rstrip("0").rstrip(".")
        return rendered or "0"
    text = str(value if value is not None else "").strip()
    return _metadata_value(text) or "-"


def compact_decimal_impl(value: Any, digits: int = 2, *, _metadata_value: Any, _num_opt: Any) -> str:
    num = _num_opt(value)
    if num is None:
        return _metadata_value(value) or "-"
    return f"{num:.{digits}f}"


def first_matching_line_impl(values: Iterable[Any], needles: Iterable[str], *, _translate_text: Any) -> str:
    lowered_needles = [needle.lower() for needle in needles]
    for raw in values:
        text = _translate_text(raw).strip()
        if not text:
            continue
        lowered = text.lower()
        if any(needle in lowered for needle in lowered_needles):
            return text.rstrip(".")
    return ""


def section_texts_impl(*sections: Dict[str, Any], _listify: Any) -> List[str]:
    texts: List[str] = []
    for section in sections:
        if not isinstance(section, dict):
            continue
        if section.get("summary"):
            texts.append(str(section.get("summary") or ""))
        texts.extend(str(item or "") for item in _listify(section.get("bullets")))
    return texts


def same_day_summary_impl(section: Dict[str, Any], *, _same_day_current_result: Any, _same_day_summary_from_texts: Any, _section_texts: Any, report: Any) -> str:
    return _same_day_summary_from_texts(
        _section_texts(section),
        fallback="당일 성과 집계는 리포터 평가 섹션에서 확인 필요",
        current_result=_same_day_current_result(report),
    )


def selected_score_impl(selection: Dict[str, Any], *, _as_dict: Any, _listify: Any, _num_opt: Any, _pick: Any, _selection_fallback_context: Any, report: Any) -> str:
    score = _pick(selection.get("score_total"), selection.get("selected_score"))
    trace = _as_dict(selection.get("scanner_selection_trace"))
    selected_symbol = str(_pick(selection.get("symbol"), report.get("symbol"), trace.get("monitor_selected_symbol"), trace.get("selected_symbol")) or "").strip()
    if score in (None, "") and _selection_fallback_context(selection, selected_symbol).get("used"):
        news = _as_dict(trace.get("news_scanner_contribution"))
        score = _pick(trace.get("selected_score"), news.get("selected_score_total"))
    if score in (None, ""):
        for row in _listify(trace.get("ranked_candidates")):
            row_obj = _as_dict(row)
            if str(row_obj.get("symbol") or "").strip() == selected_symbol:
                score = _pick(row_obj.get("score_total"), row_obj.get("score"))
                break
    num = _num_opt(score)
    return f"{num:.3f}" if num is not None else "-"


def selected_rank_impl(selection: Dict[str, Any], *, _as_dict: Any, _pick: Any) -> str:
    trace = _as_dict(selection.get("scanner_selection_trace"))
    rank = _pick(selection.get("selected_rank"), trace.get("selected_rank"), selection.get("scanner_rank"))
    return str(rank) if rank not in (None, "") else "-"


def extract_run_id_impl(timeline: Iterable[Any], event_name: str, *, _as_dict: Any, _pick: Any) -> str:
    for row in timeline:
        row_obj = _as_dict(row)
        event = str(_pick(row_obj.get("event"), row_obj.get("step")) or "").lower()
        if event_name not in event:
            continue
        direct = _pick(row_obj.get("run_id"), row_obj.get("id"))
        if direct:
            return str(direct)
        desc = str(_pick(row_obj.get("description"), row_obj.get("summary")) or "")
        match = re.search(r"\brun\s+([0-9a-f]{8,64})\b", desc, flags=re.IGNORECASE)
        if match:
            return match.group(1)
    return "-"


def policy_delta_lines_impl(memory_app: Dict[str, Any], *, _applied_label: Any, _as_dict: Any, _compact_number: Any, _listify: Any, _memory_layers_text: Any) -> List[str]:
    monitor = _as_dict(memory_app.get("monitor_memory_bias"))
    scanner = _as_dict(memory_app.get("scanner_memory_bias"))
    lines_out = [
        f"* 스캐너 메모리: {_applied_label(scanner.get('applied'))}",
        f"* 모니터 메모리: {_applied_label(monitor.get('applied'))}"
        + (f" ({_memory_layers_text(monitor.get('active_layers'))} 레벨)" if monitor.get("active_layers") else ""),
    ]
    deltas: List[str] = []
    for row in _listify(monitor.get("applied_deltas")) + _listify(monitor.get("exit_deltas")):
        row_obj = _as_dict(row)
        field = str(row_obj.get("field") or "").strip()
        if not field:
            continue
        before = row_obj.get("from")
        after = row_obj.get("to")
        deltas.append(f"* {field}: {_compact_number(before)} → {_compact_number(after)}")
    if deltas:
        lines_out.append("")
        lines_out.append("### 정책 변화")
        lines_out.extend(deltas[:4])
    return lines_out
