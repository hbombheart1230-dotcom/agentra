from __future__ import annotations

from typing import Any, Dict, List


def _summary_problem_label_impl(value: Any, *, _summary_eval_sentence) -> str:
    raw = str(value or "").strip()
    mapping = {
        "monitor_only_path_ratio_high": "monitor_only 경로 비중 확인 필요",
        "peak_drawdown_exit_needs_review": "고점 대비 하락폭 청산 조건 점검 필요",
        "entered_lower_rank_after_top_candidate_block": "상위 후보 보류 후 차순위 진입 기대값 점검 필요",
        "scanner_chart_fit_low": "scanner chart-fit 낮은 후보 선택 여부 점검 필요",
        "pullback_condition_repeated": "눌림목 조건 반복 사용 여부 점검 필요",
        "entry_evidence_missing_for_recovered_partial_exit": "복구된 부분 청산이라 신규 진입 근거 별도 확인 필요",
        "carryover_exit_requires_separate_date_basis": "이월 포지션 청산이라 당일 신규 진입 평가와 분리 필요",
    }
    return mapping.get(raw, _summary_eval_sentence(raw))


def _summary_root_cause_label_impl(value: Any, *, _summary_eval_sentence) -> str:
    raw = str(value or "").strip()
    mapping = {
        "scanner_monitor_reassessment_after_top_rank_block": "스캐너 상위 후보 보류 후 모니터 재평가로 차순위 진입",
        "scanner_selected_candidate_had_weak_chart_fit": "선택 후보의 scanner chart-fit 점수가 낮았음",
        "entry_was_tightened_by_breakout_buffer": "메모리/정책이 breakout buffer를 강화함",
        "exit_was_tightened_by_peak_drawdown": "메모리/정책이 peak drawdown 청산을 강화함",
        "recovered_partial_exit_excludes_new_entry_assessment": "복구된 부분 청산이라 신규 진입 평가 제외",
        "carryover_position_excludes_same_day_scanner_selection_assessment": "이월 포지션이라 당일 스캐너 선정 평가 제외",
    }
    return mapping.get(raw, _summary_eval_sentence(raw))


def _summary_fact_text_impl(value: Any, *, _translate_text, re) -> str:
    text = _translate_text(value).strip()
    text = re.sub(r"\s+", " ", text)
    text = text.replace("입니다..", "입니다.")
    return text.rstrip(".")


def _summary_eval_sentence_impl(value: Any, *, _translate_text, re, _ensure_sentence) -> str:
    text = _translate_text(value).strip()
    if not text:
        return ""
    replacements = {
        "00번.symbol": "해당 종목",
        "root_cause_candidates": "원인 후보",
        "deterministic_findings": "결정론적 진단",
        "decision_flow": "의사결정 흐름",
        "truth_surface": "Truth Surface",
        "何か": "무엇인지",
        "如何": "어떤지",
        "により": "로 인해",
        "阈值": "기준",
        "況": "상황",
        "况": "상황",
        "inúmer": "국면",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    text = text.replace("monitor_only", "monitor-only")
    text = text.replace("cached_strategist", "cached strategist")
    text = re.sub(r"고점 대비 하락폭 기준[_-]?exit", "고점 대비 하락폭 청산", text)
    text = re.sub(r"스캐너 1순위\s+([A-Z0-9]+)", r"스캐너 상위 후보 \1", text)
    text = text.replace(" 이유로 막혀", " 이유로 보류되어")
    text = text.replace(" 이유로 막히면서", " 이유로 보류되면서")
    text = text.replace("으로 전환됨", "으로 전환됐습니다")
    text = text.replace("이유와cached", "이유와 cached")
    text = text.replace("이유는무엇인지", "이유는 무엇인지")
    text = text.replace("분포는어떤지", "분포는 어떤지")
    text = text.replace("어려움.", "어렵습니다.")
    text = text.replace("가능성입니다.", "가능성이 있습니다.")
    text = text.replace("부적절입니다.", "부적절합니다.")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\?입니다\.?$", "?", text)
    text = re.sub(r"함\.$", "합니다.", text)
    text = re.sub(r"었음\.$", "었습니다.", text)
    text = re.sub(r"있음\.$", "있습니다.", text)
    if text.endswith("수 있음"):
        text = text[: -len("수 있음")].rstrip() + " 수 있습니다."
    elif text.endswith("있음"):
        text = text[: -len("있음")].rstrip() + " 있습니다."
    elif text.endswith("확인"):
        text = text + "이 필요합니다."
    elif text.endswith("재검토"):
        text = text + "가 필요합니다."
    elif text.endswith("마련"):
        text = text + "이 필요합니다."
    elif text.endswith("가능성"):
        text = text + "이 있습니다."
    elif text.endswith("부적절"):
        text = text + "합니다."
    if text.endswith(("?", "!", "입니다.", "였습니다.", "합니다.", "됩니다.", "다.", ".")):
        return text
    return _ensure_sentence(text)


def _section_impl(title: str, content: List[str]) -> List[str]:
    if not content:
        return []
    lines = [f"## {title}", ""]
    lines.extend(content)
    lines.append("")
    return lines


def _strip_trailing_blanks_impl(lines: List[str]) -> List[str]:
    cleaned: List[str] = []
    prev_blank = False
    for line in lines:
        is_blank = not str(line).strip()
        if is_blank and prev_blank:
            continue
        cleaned.append(line)
        prev_blank = is_blank
    return cleaned


def _is_post_entry_gate_text_impl(value: Any, *, _translate_text) -> bool:
    text = _translate_text(value).strip().lower()
    return bool(
        text
        and (
            "사후 모니터 재평가" in text
            or "매수 후 보유·청산 구간" in text
            or "post-entry" in text
            or "post entry" in text
        )
    )


def _normalize_evaluation_hold_duration_impl(text: str, report: Dict[str, Any], *, _authoritative_holding_duration_label, re) -> str:
    duration = _authoritative_holding_duration_label(report)
    if not text or not duration:
        return text
    return re.sub(
        r"\b\d+(?:\.\d+)?\s*(?:초|분|시간|s|m|h)\s*(?=(?:동안\s*)?(?:보유|만에))",
        duration + " ",
        text,
        flags=re.IGNORECASE,
    )
