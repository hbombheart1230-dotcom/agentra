from __future__ import annotations

from typing import Any, Dict, List


def _scanner_source_label_impl(value: Any, *, _clip) -> str:
    raw = _clip(value, max_len=80).strip().lower()
    mapping = {
        "top_value": "거래대금 상위",
        "top_volume": "거래량 상위",
        "sector_theme": "섹터·테마 정렬",
        "sentiment": "감성 반영",
        "news": "뉴스 반영",
    }
    return mapping.get(raw, _clip(value, max_len=80))

def _scanner_source_text_impl(values: Any, *, _scanner_source_label, _listify) -> str:
    labels = [_scanner_source_label(item) for item in _listify(values, max_items=4, max_len=80)]
    labels = [item for item in labels if item]
    if len(labels) == 2:
        return f"{labels[0]}와 {labels[1]}"
    if len(labels) >= 3:
        return ", ".join(labels[:-1]) + f", {labels[-1]}"
    return ", ".join(labels)

def _scanner_score_driver_label_impl(value: Any, *, _clip) -> str:
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

def _scanner_chart_feature_label_impl(value: Any, *, _clip) -> str:
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

def _scanner_check_name_label_impl(value: Any, *, _clip) -> str:
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

def _scanner_check_status_label_impl(value: Any, *, _clip) -> str:
    raw = _clip(value, max_len=40).strip().upper()
    mapping = {
        "PASS": "통과",
        "FAIL": "미통과",
        "NOT_AVAILABLE": "확인 불가",
    }
    return mapping.get(raw, _clip(value, max_len=40) or "확인 불가")

def _entry_reason_label_impl(value: Any, *, _clip) -> str:
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

def _decision_chain_label_impl(value: Any, *, _clip) -> str:
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

def _execution_mode_label_impl(value: Any, *, _clip) -> str:
    raw = _clip(value, max_len=120).strip().lower()
    mapping = {
        "simulation trade report": "시뮬레이션 거래 리포트",
        "simulation": "시뮬레이션",
        "simulation (mock broker)": "시뮬레이션 (모의 브로커)",
        "real": "실거래",
        "live": "실거래",
    }
    return mapping.get(raw, _clip(value, max_len=120))

def _entry_path_label_impl(value: Any, *, _clip) -> str:
    raw = _clip(value, max_len=80).strip().lower()
    mapping = {
        "breakout_path": "돌파 경로",
        "pullback_volume_path": "눌림목·거래량 경로",
        "reclaim_path": "재회복 경로",
    }
    return mapping.get(raw, _clip(value, max_len=80))

def _entry_gate_state_label_impl(value: Any) -> str:
    if value is True:
        return "통과"
    if value is False:
        return "미통과"
    return "기록 없음"

def _entry_gate_name_label_impl(value: str) -> str:
    mapping = {
        "reclaim": "VWAP 재회복",
        "extension": "과확장 점검",
        "confidence gate": "신뢰도 게이트",
    }
    return mapping.get(value, value)
