from __future__ import annotations

from typing import Any


def append_summary_closing(
    *,
    lines: Any, _authoritative_final_operator_summary: Any, _dedupe: Any, _ensure_sentence: Any,
    _extract_run_id: Any, _listify: Any, _policy_delta_lines: Any, _translate_text: Any,
    action: Any, carryover_exit: Any, final: Any, memory_app: Any,
    problems: Any, recommendations: Any, report: Any, reporter_eval: Any,
    result_label: Any, same_day: Any, status: Any, timeline: Any,
) -> None:
    """Append canonical Markdown section text in the original statement order."""
    lines.append("## ⚙️ 정책 및 메모리 영향")
    lines.append("")
    lines.extend(_policy_delta_lines(memory_app) if memory_app else ["* 정책/메모리 영향은 상세 리포트에서 확인 필요"])
    lines.append("")
    lines.append("👉 **진입/청산 정책 조합의 손익비 영향 확인 필요**")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🔁 패턴 분석 (당일)")
    lines.append("")
    lines.append(f"* {same_day}")
    lines.append("")
    lines.append("### 반복 패턴")
    lines.append("")
    pattern_lines = [
        line
        for line in _listify(reporter_eval.get("bullets"))
        if any(token in str(line).lower() for token in ("monitor", "fallback", "blocker", "closed trade", "차순위"))
    ]
    if pattern_lines:
        lines.extend(f"* {_translate_text(line).rstrip('.')}" for line in pattern_lines[:4])
    else:
        lines.append("* 반복 패턴은 추가 집계 필요")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## ⚠️ 주요 리스크")
    lines.append("")
    default_risks = (
        ["이월 승인 근거와 당일 청산 판단의 날짜 혼선 가능성", "장기/주말 이월 상태에서 청산 우선순위 검증 필요"]
        if carryover_exit
        else ["전략 vs 종목 톤 미스매치", "scanner → monitor 정합성 저하 가능성"]
    )
    risk_lines = _dedupe(problems + default_risks)
    lines.extend(f"* {item}" for item in risk_lines[:4])
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📌 보완 필요")
    lines.append("")
    lines.extend(f"* {item}" for item in recommendations[:4])
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📎 근거 출처")
    lines.append("")
    lines.append("* canonical agent artifacts 기반")
    lines.append("* commander / strategist / scanner / monitor / executor / supervisor 로그")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🧾 타임라인")
    lines.append("")
    lines.append(f"* 진입 run: {_extract_run_id(timeline, 'entry')}")
    lines.append(f"* 청산 run: {_extract_run_id(timeline, 'exit')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🔚 최종 판단")
    lines.append("")
    lines.append(f"* 상태: {status}")
    lines.append(f"* 액션: {action}")
    lines.append("")
    final_summary = _authoritative_final_operator_summary(
        report,
        action=action,
        fallback=(
            _ensure_sentence(_translate_text(final.get("summary")))
            if final.get("summary")
            else ""
        ),
    )
    if final_summary:
        lines.append(f"👉 **{final_summary}**")
        lines.append("")
    lines.append(f"👉 **{result_label} 원인은 단일 장애보다 진입/청산 구조와 정책 조합에서 우선 점검해야 합니다.**")
