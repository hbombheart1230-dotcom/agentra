from __future__ import annotations

from typing import Any, Dict, List, Mapping


def collect_render_diagnostics(
    truth_price: Any,
    truth_pnl: Any,
    shared: Any,
    carryover_exit: Any,
    recovered_partial_exit: Any,
    rank_num: Any,
    strategist: Any,
    selection: Any,
    entry: Any,
    exit_decision: Any,
    holding_duration_summary: Any,
    memory_app: Any,
    combined_texts: Any,
    cost_analysis: Any,
    cost_drag_pct: Any,
    selection_fallback_summary: Any,
    scanner_top_pick: Any,
    symbol: Any,
    entry_blob: Any,
    carryover_context: Any,
    actual_take_profit: Any,
    actual_peak_exit: Any,
    actual_hard_stop: Any,
    *, deps: Mapping[str, Any], compact_number: Any, first_matching_line: Any,
) -> tuple:
    """Render-only strengths, problems, causes and recommendations in original order."""
    _is_not_captured = deps["is_not_captured"]
    _fmt_pct = deps["fmt_pct"]
    _as_dict = deps["as_dict"]
    _listify = deps["listify"]
    _num_opt = deps["num_opt"]
    _dedupe = deps["dedupe"]
    _compact_number = compact_number
    _first_matching_line = first_matching_line
    positives = []
    broker_fill_present = truth_price.get("broker_fill_price") not in (None, "")
    realized_pnl_present = str(truth_pnl.get("value") or shared.get("pnl") or "").strip().lower() not in {
        "",
        "unavailable",
        "not_available",
        "none",
        "-",
    }
    if broker_fill_present and realized_pnl_present:
        positives.append("키움 체결가와 당일 실현손익 확보")
    elif broker_fill_present:
        positives.append("브로커 체결가 확보, 실현손익/비용은 확인 대기")
    if carryover_exit:
        positives.append("오버나이트/주말 이월 청산을 신규 선정 평가와 분리해 기록")
    elif recovered_partial_exit:
        positives.append("회수/partial 청산을 신규 진입 평가와 분리해 기록")
    elif rank_num is not None:
        positives.append(f"스캐너 순위 {int(rank_num)}위와 모니터 재평가 경로 기록")
    elif strategist or selection or entry or exit_decision:
        positives.append("전략 → 스캐너 → 모니터 판단 흐름 기록")
    if holding_duration_summary and not _is_not_captured(holding_duration_summary):
        positives.append(f"보유 시간 {holding_duration_summary}와 청산 트리거 기록")
    elif entry or exit_decision or memory_app:
        positives.append("진입/청산 근거 및 정책 추적 가능")
    if not positives:
        positives.append("핵심 거래 아티팩트가 보존됨")

    problems: List[str] = []
    monitor_line = _first_matching_line(combined_texts, ["monitor_only", "monitor-only", "monitor 단독"])
    if monitor_line:
        problems.append("당일 monitor_only 경로 비중 높음")
    if carryover_exit:
        problems.append("오늘 신규 진입이 아니라 전일/주말 이월 포지션으로 별도 해석 필요")
    if recovered_partial_exit:
        problems.append("당일 BUY 근거가 없어 신규 진입 품질 평가는 제외 필요")
    if cost_analysis.get("mock_cost_warning") and cost_drag_pct is not None:
        problems.append(f"모의투자 비용 드래그 {_fmt_pct(cost_drag_pct)} 별도 해석 필요")
    if selection_fallback_summary.get("used") or (rank_num is not None and rank_num > 1):
        if scanner_top_pick and scanner_top_pick != "-":
            problems.append(f"1순위 {scanner_top_pick} 보류 후 {symbol} {int(rank_num) if rank_num else '-'}위 재평가 진입")
        else:
            problems.append("1순위 탈락 후 차순위 재평가 진입 구조")
    if "pullback_not_mature" in entry_blob:
        problems.append("pullback 성숙도 부족으로 진입 보류 발생")
    if actual_peak_exit:
        problems.append("이번 청산이 peak_drawdown 축이라 confirm 조건 점검 필요")
    if not problems:
        problems.append("거래별 반복 패턴 판단을 위한 추가 표본 필요")

    monitor_memory = _as_dict(memory_app.get("monitor_memory_bias"))
    cause_lines: List[str] = []
    if carryover_exit:
        if carryover_context.get("estimated_entry_kst") and carryover_context.get("exit_kst"):
            cause_lines.append(
                f"{symbol}은 {carryover_context.get('estimated_entry_date_kst')} 보유분이 "
                f"{carryover_context.get('exit_date_kst')}에 청산된 이월 포지션입니다"
            )
        else:
            cause_lines.append(f"{symbol}은 오늘 신규 진입이 아니라 전일/주말 이월 보유분의 청산 결과입니다")
        if carryover_context.get("carry_risk_label"):
            cause_lines.append(f"런타임 상태는 {carryover_context.get('carry_state_label')} / {carryover_context.get('carry_risk_label')}로 기록됨")
    if recovered_partial_exit:
        cause_lines.append("보유/회수 포지션의 당일 SELL 결과이며, 신규 매수 선정·진입 판단과 같은 표본으로 보지 않습니다")
    for row in _listify(monitor_memory.get("applied_deltas")):
        row_obj = _as_dict(row)
        if str(row_obj.get("field") or "") == "breakout_buffer_pct" and (_num_opt(row_obj.get("delta")) or 0.0) > 0:
            cause_lines.append(
                "진입 정책은 breakout_buffer "
                f"{_compact_number(row_obj.get('from'))} → {_compact_number(row_obj.get('to'))}로 보수화됨"
            )
            break
    if actual_take_profit:
        cause_lines.append("청산은 목표 수익 실현 기준으로 실행됨")
    elif actual_peak_exit:
        cause_lines.append("청산은 peak_drawdown 축으로 실행됨")
    elif actual_hard_stop:
        cause_lines.append("청산은 고정 손절 기준으로 실행됨")
    if selection_fallback_summary.get("used") or (rank_num is not None and rank_num > 1):
        if scanner_top_pick and scanner_top_pick != "-":
            cause_lines.append(f"{scanner_top_pick} 보류 후 {symbol}에서 진입 조건이 충족됨")
        else:
            cause_lines.append("상위 후보 탈락 후 차순위 후보에서 진입이 성립됨")
    if cost_analysis.get("mock_cost_warning") and cost_drag_pct is not None:
        cause_lines.append(f"모의투자 수수료/세금이 손익률을 {_fmt_pct(cost_drag_pct)} 압박")
    if not cause_lines:
        cause_lines.append("진입/청산 구조의 반복성은 당일 패턴 섹션에서 추가 확인 필요")

    recommendations: List[str] = []
    if carryover_exit:
        recommendations.append("오버나이트 승인 시각/근거와 당일 청산 컨텍스트를 분리해 검증")
    if recovered_partial_exit:
        recommendations.append("회수/partial 청산은 완료 거래와 별도 집계해 승패와 평균 수익률을 확인")
    if cost_analysis.get("mock_cost_warning"):
        recommendations.append("모의투자 비용 기준과 실계좌 추정 비용 기준 분리 확인")
    if actual_peak_exit:
        recommendations.append("peak_drawdown activation/confirm 조건 점검")
    if "pullback_not_mature" in entry_blob:
        recommendations.append("pullback 조건 완화 또는 성숙도 판정 재검토")
    if selection_fallback_summary.get("used") or (rank_num is not None and rank_num > 1):
        recommendations.append("1순위 보류 사유와 차순위 진입 기대값 비교")
    if monitor_line:
        recommendations.append("monitor_only 비중이 높은 당일 route mix 점검")
    if (not holding_duration_summary or _is_not_captured(holding_duration_summary) or str(holding_duration_summary).strip() in {"0", "0s", "0초"}):
        recommendations.append("보유 구간 모니터 스냅샷 보강")
    if not recommendations:
        recommendations.append("동일 패턴 3건 이상 누적 후 정책 조정 여부 판단")
    recommendations = _dedupe([item for item in recommendations if item])[:4]

    return positives, problems, cause_lines, recommendations
