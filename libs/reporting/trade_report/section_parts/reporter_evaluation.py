from __future__ import annotations

import json
from typing import Any, Dict, Mapping

def build_reporter_evaluation_section(
    shared_seed: Dict[str, Any],
    scanner_reason: Dict[str, Any],
    monitor_reason: Dict[str, Any],
    execution_outcome: Dict[str, Any],
    reporter_status: Dict[str, Any],
    reporter_feedback_packet: Dict[str, Any] | None = None,
    *,
    deps: Mapping[str, Any],
) -> Dict[str, Any]:
    _build_reporter_evaluation_from_feedback = deps["build_reporter_evaluation_from_feedback"]
    _clip = deps["clip"]
    _dedupe_list = deps["dedupe_list"]
    _humanize_duration_text = deps["humanize_duration_text"]
    _korean_euro_ro = deps["korean_euro_ro"]
    _num_opt = deps["num_opt"]
    _operator_axis_label = deps["operator_axis_label"]
    _scanner_ranked_candidates = deps["scanner_ranked_candidates"]
    _scanner_selected_row = deps["scanner_selected_row"]
    reporter_feedback = dict(reporter_feedback_packet or {})
    reporter_feedback_available = bool(reporter_feedback.get("available")) or bool(reporter_feedback.get("consumed"))
    reporter_status_value = _clip(reporter_status.get("status"), max_len=40).lower()
    if reporter_feedback_available and reporter_status_value in {"", "missing", "pending", "auto_ignored", "source_unavailable", "not_captured", "unknown"}:
        return _build_reporter_evaluation_from_feedback(reporter_feedback)

    status = _clip(reporter_status.get("status"), max_len=40) or "missing"
    grade = _clip(reporter_status.get("grade"), max_len=16) or "N/A"
    symbol = _clip(scanner_reason.get("selected_symbol") or shared_seed.get("symbol"), max_len=24) or "선정 종목"
    selected_rank = scanner_reason.get("selected_rank")
    selected_score = _num_opt(scanner_reason.get("selected_score"))
    confidence = _num_opt(scanner_reason.get("confidence"))
    ranked_rows = _scanner_ranked_candidates(scanner_reason)
    selected_row = _scanner_selected_row(scanner_reason)
    selected_risk = _num_opt(selected_row.get("risk_score"))
    hold_seconds = int(monitor_reason.get("position_age_seconds") or 0)
    hold_duration = _humanize_duration_text(shared_seed.get("holding_duration"), fallback_seconds=hold_seconds)
    trigger_type = _operator_axis_label(
        _clip(monitor_reason.get("trigger_type"), max_len=80)
        or _clip(shared_seed.get("exit_reason"), max_len=120)
    )
    exit_reason = _clip(shared_seed.get("exit_reason"), max_len=220)
    execution_summary = _clip(execution_outcome.get("summary"), max_len=300)
    same_day_status = _clip(reporter_status.get("same_day_linkage_status"), max_len=40)
    same_day_reason = _clip(reporter_status.get("same_day_linkage_reason"), max_len=220)
    reporter_summary = _clip(reporter_status.get("summary"), max_len=300)
    reporter_summary_lower = reporter_summary.lower()
    if "overtrading" in reporter_summary_lower or "rapid exit pressure" in reporter_summary_lower:
        reporter_summary = "동일 일자 리포터도 과매매 또는 빠른 청산 압력을 시사했습니다."
    same_day_status_label = {
        "linked_run": "동일 실행 기록 직접 연계",
        "linked_trade": "동일 거래 직접 연계",
        "linked_day": "당일 묶음 연계",
        "missing": "미연계",
    }.get(same_day_status, same_day_status)

    is_short_hold = hold_seconds > 0 and hold_seconds <= 120
    peak_drawdown_exit = "peak_drawdown" in str(monitor_reason.get("trigger_type") or "").lower() or "peak_drawdown" in exit_reason.lower()
    execution_recorded = "recorded" in execution_summary.lower() or "approved" in execution_summary.lower()

    summary_parts: List[str] = []
    if is_short_hold and peak_drawdown_exit:
        summary_parts.append("이번 거래는 종목 선정 자체보다 진입 타이밍 부담이 더 크게 드러났습니다.")
    elif peak_drawdown_exit:
        summary_parts.append("이번 거래는 보유 이후 되밀림 관리가 더 크게 작동한 케이스로 보입니다.")
    else:
        summary_parts.append("이번 거래는 저장된 근거상 scanner, entry, hold, exit 축을 함께 봐야 합니다.")
    if selected_rank == 1 and selected_score is not None:
        scanner_bits = [f"스캐너는 {symbol}을 {selected_rank}위"]
        if selected_score is not None:
            scanner_bits.append(f"종합 점수 {selected_score:.3f}")
        if confidence is not None:
            scanner_bits.append(f"신뢰도 {confidence:.2f}")
        if selected_risk is not None:
            scanner_bits.append(f"리스크 {selected_risk:.3f}")
        summary_parts.append(", ".join(scanner_bits) + "로 올렸고 선정 자체는 크게 흔들리지 않았습니다.")
    if hold_duration and peak_drawdown_exit:
        summary_parts.append(f"다만 진입 후 약 {hold_duration} 만에 {trigger_type} 축 청산이 발생해 추가 상승 지속성이 약했습니다.")
    elif hold_duration:
        summary_parts.append(f"보유 시간은 약 {hold_duration}로 짧아 hold 단계 해석은 제한적입니다.")
    if execution_recorded:
        summary_parts.append("실행 기록상 주문 자체 문제는 보이지 않았습니다.")
    elif execution_summary:
        summary_parts.append("실행 기록은 남아 있지만 주문 품질은 추가 확인이 필요합니다.")

    bullets: List[str] = []
    if selected_rank not in (None, "") and selected_score is not None:
        scanner_line = f"종목 선정 평가는 {symbol} {selected_rank}위, 종합 점수 {selected_score:.3f}"
        if confidence is not None:
            scanner_line += f", 신뢰도 {confidence:.2f}"
        if selected_risk is not None:
            scanner_line += f", 리스크 {selected_risk:.3f}"
        scanner_line += "로 종목 선택 자체는 비교적 정상으로 보입니다."
        bullets.append(scanner_line)
    if is_short_hold and peak_drawdown_exit:
        bullets.append(
            f"진입 평가는 진입 후 약 {hold_duration or f'{hold_seconds}초'} 만에 {trigger_type} 청산이 나와, 종목 선정보다 진입 위치 부담이 더 컸던 것으로 읽힙니다."
        )
    elif hold_duration:
        bullets.append(f"진입·보유 평가는 보유 시간이 {hold_duration}로 짧아 추가 사례 비교가 필요합니다.")
    if hold_duration:
        bullets.append(f"보유 평가는 보유 시간이 {hold_duration}에 그쳐 중간 악화 흐름을 두껍게 읽기에는 정보가 부족합니다.")
    if trigger_type:
        bullets.append(f"청산 평가는 청산 축이 {trigger_type}{_korean_euro_ro(trigger_type)} 명확해 청산 규칙 자체는 규칙대로 작동한 것으로 보입니다.")
    if execution_recorded:
        bullets.append("실행 평가는 주문 승인 및 기록이 남아 있어 실행 누락보다는 전략/타이밍 해석 이슈 쪽에 가깝습니다.")
    elif execution_summary:
        bullets.append(f"실행 평가는 {execution_summary}")
    if same_day_status:
        linkage_line = f"당일 리포터 연계 상태는 {same_day_status_label}였습니다."
        bullets.append(linkage_line)
    if reporter_summary:
        bullets.append(reporter_summary)

    return {
        "summary": " ".join(summary_parts).strip(),
        "status": status,
        "grade": grade,
        "bullets": _dedupe_list(bullets, max_items=8, max_len=260),
    }



def build_reporter_evaluation_from_feedback(reporter_feedback_packet: Dict[str, Any] | None, *, deps: Mapping[str, Any]) -> Dict[str, Any]:
    _as_dict = deps["as_dict"]
    _clip = deps["clip"]
    _dedupe_list = deps["dedupe_list"]
    _fmt_pct = deps["fmt_pct"]
    _listify = deps["listify"]
    _num_opt = deps["num_opt"]
    _operatorize_report_text = deps["operatorize_report_text"]
    normalize_reporter_text = deps["normalize_reporter_text"]
    packet = dict(reporter_feedback_packet or {})
    confidence = _clip(packet.get("confidence"), max_len=16).lower()
    confidence_label = {
        "high": "높음",
        "medium": "중간",
        "low": "낮음",
    }.get(confidence, "확인되지 않음")
    grade = {
        "high": "A",
        "medium": "B",
        "low": "C",
    }.get(confidence, "N/A")
    source_reports = _as_dict(packet.get("source_reports"))
    trade_summary = _as_dict(packet.get("trade_report_analysis"))
    insight_summary = normalize_reporter_text(_operatorize_report_text(_clip(packet.get("insight_summary"), max_len=600)))
    recommendations = [
        normalize_reporter_text(_operatorize_report_text(item))
        for item in _listify(packet.get("recommendation"), max_items=4, max_len=220)
        if str(item or "").strip()
    ]
    normalized_recommendations: List[str] = []
    for raw_item, rendered in zip(_listify(packet.get("recommendation"), max_items=4, max_len=220), recommendations):
        if raw_item == "Same-price round trips produced fee/tax drag; tighten follow-through evidence before repeating quick reversals.":
            normalized_recommendations.append("동일가 왕복 거래에서 수수료와 세금 손실이 반복돼, 짧은 반전 재진입 전에는 후속 추세 확인을 더 엄격하게 봐야 합니다.")
            continue
        if rendered:
            normalized_recommendations.append(rendered)
            continue
    recommendations = normalized_recommendations
    dominant_patterns = [
        _as_dict(item)
        for item in list(packet.get("dominant_patterns") or [])[:4]
        if isinstance(item, dict)
    ]
    source_labels: List[str] = []
    if source_reports.get("metrics"):
        source_labels.append("당일 metrics")
    if source_reports.get("reporter_analysis"):
        source_labels.append("당일 reporter 분석")
    if source_reports.get("trade_reports"):
        source_labels.append("당일 닫힌 거래 리포트")
    if not source_labels:
        source_labels.append("당일 피드백 패킷")

    closed_trade_count = int(trade_summary.get("closed_trade_count") or 0)
    win_count = int(trade_summary.get("win_count") or 0)
    loss_count = int(trade_summary.get("loss_count") or 0)
    flat_count = int(trade_summary.get("flat_count") or 0)
    unknown_pnl_count = int(trade_summary.get("unknown_pnl_count") or 0)
    if closed_trade_count > 0 and unknown_pnl_count <= 0:
        inferred_unknown = closed_trade_count - win_count - loss_count - flat_count
        if inferred_unknown > 0:
            unknown_pnl_count = inferred_unknown
    pnl_pct_sample_count = int(trade_summary.get("pnl_pct_sample_count") or 0)
    avg_pnl_pct = _num_opt(trade_summary.get("avg_pnl_pct"))

    summary_parts: List[str] = [
        f"당일 reporter feedback은 {', '.join(source_labels)} 기준으로 생성됐습니다."
    ]
    if closed_trade_count > 0:
        trade_bits = [f"당일 closed trade {closed_trade_count}건"]
        trade_bits.append(f"승/패 {win_count}/{loss_count}")
        if flat_count > 0:
            trade_bits.append(f"보합 {flat_count}건")
        if unknown_pnl_count > 0:
            trade_bits.append(f"손익 미확정 {unknown_pnl_count}건")
        if avg_pnl_pct is not None and pnl_pct_sample_count > 0:
            avg_label = "확인분 평균 손익률" if unknown_pnl_count > 0 else "평균 손익률"
            trade_bits.append(f"{avg_label} {_fmt_pct(avg_pnl_pct)}")
        summary_parts.append(", ".join(trade_bits) + "였습니다.")
    if insight_summary:
        summary_parts.append(insight_summary)

    bullets: List[str] = []
    bullets.append(f"피드백 생성 소스는 {', '.join(source_labels)}입니다.")
    if closed_trade_count > 0:
        trade_line = f"당일 closed trade 집계는 {closed_trade_count}건, 승패 {win_count}/{loss_count}"
        if flat_count > 0:
            trade_line += f", 보합 {flat_count}건"
        if unknown_pnl_count > 0:
            trade_line += f", 손익 미확정 {unknown_pnl_count}건"
        if avg_pnl_pct is not None and pnl_pct_sample_count > 0:
            avg_label = "확인분 평균 손익률" if unknown_pnl_count > 0 else "평균 손익률"
            trade_line += f", {avg_label} {_fmt_pct(avg_pnl_pct)}"
        trade_line += "입니다."
        bullets.append(trade_line)
    for row in dominant_patterns:
        detail = normalize_reporter_text(_operatorize_report_text(_clip(row.get("detail"), max_len=180)))
        name = normalize_reporter_text(_operatorize_report_text(_clip(row.get("name"), max_len=40)))
        if detail:
            bullets.append(f"주요 패턴: {detail}")
        elif name:
            bullets.append(f"주요 패턴: {name}")
    for item in recommendations:
        bullets.append(f"권고: {item}")

    return {
        "summary": " ".join(part for part in summary_parts if str(part or "").strip()).strip(),
        "status": "ok",
        "grade": grade,
        "bullets": _dedupe_list(bullets, max_items=8, max_len=260),
    }



