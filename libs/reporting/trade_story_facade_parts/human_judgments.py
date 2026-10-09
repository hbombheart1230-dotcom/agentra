from __future__ import annotations

from typing import Any, Dict, List


def build_guard_reason_human_impl(supervisor: Dict[str, Any]) -> Dict[str, Any]:
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


def build_reporter_status_human_impl(reporter: Dict[str, Any], reporter_day_obj: Dict[str, Any], *, normalize_reporter_status_human) -> Dict[str, Any]:
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


def build_operator_conclusion_human_impl(
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
