from __future__ import annotations

from typing import Any, Dict, List


def _rank_scope_text_impl(row: Dict[str, Any]) -> str:
    if not row:
        return ""
    rank = row.get("max_priority_rank")
    runner_ups = row.get("max_runner_ups")
    if rank in (None, "") and runner_ups in (None, ""):
        return ""
    parts: List[str] = []
    if rank not in (None, ""):
        parts.append(f"rank<={rank}")
    if runner_ups not in (None, ""):
        parts.append(f"runner_ups={runner_ups}")
    return " / ".join(parts)

def _watch_scope_label_impl(row: Dict[str, Any]) -> str:
    if not row:
        return ""
    rank = row.get("max_priority_rank")
    runner_ups = row.get("max_runner_ups")
    parts: List[str] = []
    if rank not in (None, ""):
        parts.append(f"{rank}위까지")
    if runner_ups not in (None, ""):
        parts.append(f"차순위 {runner_ups}개")
    return " / ".join(parts)

def _candidate_watch_reason_label_impl(value: Any, *, _metadata_value) -> str:
    reason = _metadata_value(value)
    if not reason or reason == "-":
        return ""
    mapping = {
        "open_position_present": "보유 포지션 존재",
        "cascade_disabled_by_entry_control": "지휘관 설정으로 차순위 확인 비활성",
        "candidate_watch_disabled": "후보 감시 비활성",
        "entry_control_disabled": "지휘관 진입 제어 비활성",
    }
    return mapping.get(reason, reason)

def _story_type_label_impl(value: Any, *, _clip, _metadata_value) -> str:
    lowered = _clip(value, 80).lower()
    return {
        "simulation trade report": "시뮬레이션 거래 리포트",
        "simulation": "시뮬레이션 거래 리포트",
        "live trade report": "실거래 거래 리포트",
        "live": "실거래 거래 리포트",
    }.get(lowered, _metadata_value(value) or "-")

def _execution_mode_label_impl(value: Any, *, _clip, _metadata_value) -> str:
    lowered = _clip(value, 80).lower()
    return {
        "simulation (mock broker)": "시뮬레이션 (모의 브로커)",
        "real broker": "실브로커",
        "live": "실거래",
    }.get(lowered, _metadata_value(value) or "-")

def _action_label_impl(value: Any, *, _clip, _metadata_value) -> str:
    lowered = _clip(value, 40).upper()
    return {
        "BUY": "매수",
        "SELL": "매도",
        "HOLD": "보유 유지",
        "WAIT": "진입 보류",
    }.get(lowered, _metadata_value(value) or "-")

def _status_label_impl(value: Any, *, _clip, _metadata_value) -> str:
    lowered = _clip(value, 40).lower()
    return {
        "open": "열림",
        "closed": "종결",
        "ok": "정상",
    }.get(lowered, _metadata_value(value) or "-")

def _axis_label_impl(value: Any, *, _clip) -> str:
    raw = _clip(value, 120)
    if raw.lower().startswith("sell was triggered because "):
        raw = raw[len("SELL was triggered because ") :].strip().rstrip(".")
    lowered = raw.lower().replace("-", "_").replace(" ", "_")
    mapping = {
        "hard_stop": "고정 손절 기준",
        "stop_loss": "고정 손절 기준",
        "adaptive_stop": "상황 적응형 손절 기준",
        "take_profit": "목표 수익 실현 기준",
        "partial_take_profit": "1차 일부 익절",
        "profit_ladder": "구간별 분할 익절",
        "risk/reward_take_profit": "손익비 익절",
        "risk_reward_take_profit": "손익비 익절",
        "vwap_extension_take_profit": "VWAP 과확장 익절",
        "resistance_take_profit": "저항권 익절",
        "volume_exhaustion_take_profit": "거래량 둔화 익절",
        "opening_gap_profit_take": "갭 추격 빠른 익절",
        "time_decay_profit_exit": "시간 경과 수익 보전",
        "trailing_stop": "추적 손절 기준",
        "vwap_breakdown": "VWAP 이탈",
        "peak_drawdown": "고점 대비 하락폭 기준",
        "prior_low_break": "직전 저점 이탈",
        "intraday_low_break": "장중 저점 이탈 기준",
        "below_vwap_reclaim_not_ready": "VWAP 재회복 미완료",
        "exit_trigger_not_captured": "모니터 청산 트리거 미확인",
        "monitor_exit_trigger_not_captured": "모니터 청산 트리거 미확인",
        "sell_execution_confirmed": "모니터 청산 트리거 미확인",
        "full_sell_quantity_reconciled": "모니터 청산 트리거 미확인",
        "confirmed_exit_signal": "청산 확인 신호",
        "defensive_exit": "방어적 청산 신호",
        "trend_breakdown": "추세 붕괴 기준",
        "volatility_expansion": "변동성 확장 기준",
        "no_trigger_yet": "아직 청산 신호가 확인되지 않음",
    }
    return mapping.get(lowered, raw or "-")

def _risk_mode_label_impl(value: Any, *, _clip, _metadata_value) -> str:
    raw = _clip(value, 80).lower()
    return {
        "balanced": "균형형",
        "defensive": "방어형",
        "aggressive": "공격형",
        "normal": "보통",
    }.get(raw, _metadata_value(value) or "-")

def _theme_label_impl(value: Any, *, _clip, _metadata_value) -> str:
    raw = _clip(value, 120).lower()
    mapping = {
        "broad_market_leaders": "시장 대표주",
        "illiquid_microcap": "유동성 낮은 초소형주",
        "headline_only_momentum": "헤드라인 추격형 모멘텀",
        "high_gap_speculative": "갭 과열 투기형",
        "counter_trend_low_liquidity": "역추세 저유동성 종목",
        "defensive_assets": "방어 자산군",
    }
    return mapping.get(raw, _metadata_value(value) or "-")

def _policy_token_label_impl(value: Any, *, _clip, _metadata_value) -> str:
    raw = _clip(value, 120)
    lower = raw.lower()
    mapping = {
        "reclaim_gate_ok": "VWAP 재회복 확인",
        "extension_ok": "과열 이격 제한 통과",
        "confidence_ok": "신뢰도 기준 통과",
        "trend_regime=transition": "추세 전환 구간 확인",
        "structure_range_compression=moderate": "가격 압축이 중간 수준",
        "volume_ok": "거래량 확인",
        "breakout_ok": "돌파 확인",
        "pullback_ok": "눌림목 구조 확인",
        "failed_breakout=confirmed": "실패 돌파가 확인된 상태",
        "momentum_decay=strong": "모멘텀 둔화가 강한 상태",
        "vwap_reclaim_required": "VWAP 재회복 확인을 우선 조건으로 둠",
        "monitor_guidance:defensive_exit": "방어적 청산 안내 유지",
        "trade_aggressiveness:medium": "진입 강도는 중간 수준",
    }
    return mapping.get(lower, _metadata_value(value) or "-")

def _playbook_label_impl(value: Any, *, _clip, _metadata_value) -> str:
    raw = _clip(value, 80).lower()
    mapping = {
        "defensive": "방어형",
        "breakout": "돌파형",
        "pullback": "눌림목형",
        "reclaim": "재회복형",
        "leader": "주도주형",
        "balanced": "균형형",
        "normal": "정상",
        "neutral": "중립",
        "aggressive": "공격형",
    }
    return mapping.get(raw, _metadata_value(value) or "-")

def _monitor_guidance_label_impl(value: Any, *, _clip, _metadata_value) -> str:
    raw = _clip(value, 80).lower()
    mapping = {
        "defensive_exit": "방어적 청산 안내",
        "normal_exit": "일반 청산 안내",
        "hold_bias": "보유 우선 안내",
    }
    return mapping.get(raw, _metadata_value(value) or "-")

def _scanner_bias_label_impl(value: Any, *, _clip, _metadata_value) -> str:
    raw = _clip(value, 80).lower()
    mapping = {
        "leader": "주도주 우선",
        "balanced": "균형형",
        "defensive": "방어형",
    }
    return mapping.get(raw, _metadata_value(value) or "-")

def _policy_source_label_impl(value: Any, *, _clip, _metadata_value) -> str:
    raw = _clip(value, 80).lower()
    mapping = {
        "monitor_memory_bias_adjusted": "메모리 조정 반영 정책",
        "baseline_monitor_policy": "기본 모니터 정책",
    }
    return mapping.get(raw, _metadata_value(value) or "-")

def _failure_label_impl(value: Any, *, _clip, _playbook_label, _metadata_value) -> str:
    raw = _clip(value, 120)
    lower = raw.lower()
    if lower.startswith("playbook:"):
        return f"{_playbook_label(lower.split(':', 1)[1])} 전략 프레임 실패"
    return _metadata_value(value) or "-"

def _reporter_source_label_impl(source_reports: Dict[str, Any]) -> str:
    if source_reports.get("trade_reports"):
        return "same-day closed trade reports"
    if source_reports.get("reporter_analysis"):
        return "same-day reporter_analysis"
    if source_reports.get("metrics"):
        return "same-day metrics"
    if source_reports.get("trade_explain"):
        return "same-day trade explain"
    if source_reports.get("current_payload"):
        return "current payload"
    return "not_recorded"

def _humanize_reporter_source_label_impl(source_reports: Dict[str, Any], *, _reporter_source_label, _translate_text) -> str:
    raw = _reporter_source_label(source_reports)
    mapping = {
        "same-day closed trade reports": "당일 닫힌 거래 리포트",
        "same-day reporter_analysis": "당일 reporter_analysis",
        "same-day metrics": "당일 metrics",
        "same-day trade explain": "당일 trade explain",
        "current payload": "현재 payload",
        "not_recorded": "기록되지 않은 소스",
    }
    return mapping.get(raw, _translate_text(raw))
