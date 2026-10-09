from __future__ import annotations

import logging
import re
from typing import Any, Dict, List

from .operator_parts.language import normalize_trade_report_language_impl
from .operator_parts.exact_phrases import resolve_exact_operator_phrase
from .operator_parts.context_patterns import resolve_market_selection_phrase
from .operator_parts.lifecycle_patterns import resolve_lifecycle_operator_phrase

from libs.reporting.trade_report_common import (
    dedupe_list as _dedupe_list,
    fmt_pct as _fmt_pct,
    report_clip as _clip,
)

# Preserve the historical logger identity used by the façade.
logger = logging.getLogger("libs.reporting.trade_report_ai")
_FORBIDDEN_CJK_OR_JP_RE = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")


def safe_fullmatch(pattern: str, text: str, *, flags: int = 0):
    try:
        return re.fullmatch(pattern, text, flags=flags)
    except re.error:
        logger.debug("trade_report_regex_invalid pattern=%r", pattern, exc_info=True)
        return None


def sanitize_forbidden_scripts_text(text: Any) -> str:
    raw = _clip(text, max_len=2000).strip()
    if not raw:
        return ""
    replacement_pairs = (
        ("生命周期", "생명주기"),
        ("缺失", "누락"),
        ("不足", "부족"),
        ("薄薄", "부족"),
        ("未完了", "미완료"),
        ("还未", "아직"),
        ("故事", "스토리"),
    )
    normalized = raw
    for src, dst in replacement_pairs:
        normalized = normalized.replace(src, dst)
    cleaned = _FORBIDDEN_CJK_OR_JP_RE.sub("", normalized)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    if cleaned:
        return cleaned
    return "데이터 부족으로 보수적으로 정리했습니다."



def operator_action_label(value: Any) -> str:
    raw = _clip(value, max_len=80).strip().lower()
    mapping = {
        "buy": "매수",
        "sell": "매도",
        "hold": "보유 유지",
        "wait": "진입 보류",
        "noop": "대기",
        "approve": "승인",
        "approved": "승인",
        "allowed": "허용",
        "yes": "허용",
        "no": "차단",
    }
    return mapping.get(raw, _clip(value, max_len=80) or "-")



def operator_axis_label(value: Any) -> str:
    raw = _clip(value, max_len=120).strip().lower()
    mapping = {
        "peak drawdown": "고점 대비 하락폭",
        "peak_drawdown": "고점 대비 하락폭",
        "hard stop": "고정 손절 기준",
        "hard_stop": "고정 손절 기준",
        "adaptive stop": "상황 대응형 손절 기준",
        "adaptive_stop": "상황 대응형 손절 기준",
        "take profit": "목표 수익 실현 기준",
        "take_profit": "목표 수익 실현 기준",
        "partial take profit": "1차 일부 익절",
        "partial_take_profit": "1차 일부 익절",
        "profit ladder": "구간별 분할 익절",
        "profit_ladder": "구간별 분할 익절",
        "risk/reward take profit": "손익비 익절",
        "risk_reward_take_profit": "손익비 익절",
        "vwap extension take profit": "VWAP 과확장 익절",
        "vwap_extension_take_profit": "VWAP 과확장 익절",
        "resistance take profit": "저항권 익절",
        "resistance_take_profit": "저항권 익절",
        "volume exhaustion take profit": "거래량 둔화 익절",
        "volume_exhaustion_take_profit": "거래량 둔화 익절",
        "opening gap profit take": "갭 추격 빠른 익절",
        "opening_gap_profit_take": "갭 추격 빠른 익절",
        "time-decay profit exit": "시간 경과 수익 보전",
        "time_decay_profit_exit": "시간 경과 수익 보전",
        "trailing stop": "추적 손절 기준",
        "trailing_stop": "추적 손절 기준",
        "vwap breakdown": "VWAP 이탈",
        "intraday low break": "장중 저점 이탈",
        "trend breakdown": "추세 훼손",
        "hold": "보유 유지",
        "wait": "진입 보류",
        "confirmed_exit_signal": "청산 확인 신호",
    }
    return mapping.get(raw, _clip(value, max_len=120) or "-")



def operator_filter_label(value: Any) -> str:
    raw = _clip(value, max_len=120).strip().lower()
    mapping = {
        "liquidity filter": "유동성 점검",
        "turnover filter": "회전율 점검",
        "sector/theme alignment": "섹터·테마 정렬 점검",
        "chart completeness filter": "차트 지표 충실도 점검",
        "sentiment gate": "시장 심리 점검",
        "risk gate": "리스크 점검",
        "price anomaly filter": "가격 이상치 점검",
        "spread/slippage filter": "호가 스프레드·슬리피지 점검",
    }
    return mapping.get(raw, _clip(value, max_len=120) or "-")



def operator_filter_status(value: Any) -> str:
    raw = _clip(value, max_len=40).strip().lower()
    mapping = {
        "pass": "통과",
        "fail": "미통과",
        "not_available": "확인 불가",
    }
    return mapping.get(raw, _clip(value, max_len=40) or "-")



def normalize_trade_report_language(text: Any) -> str:
    """Keep public identity and legacy call-time sanitize/clip monkeypatch seams."""
    return normalize_trade_report_language_impl(
        text, sanitize_forbidden_scripts_text=sanitize_forbidden_scripts_text, _clip=_clip,
    )


def exit_reason_label(value: Any) -> str:
    raw = _clip(value, max_len=220).strip()
    stripped = re.sub(r"^SELL was triggered because\s*", "", raw, flags=re.IGNORECASE).strip().rstrip(".")
    lowered = stripped.lower()
    if not raw:
        return ""
    if "peak_drawdown" in lowered:
        return "고점 대비 하락폭 기준으로 청산"
    if "hard_stop" in lowered:
        return "고정 손절 기준으로 청산"
    if "partial_take_profit" in lowered:
        return "1차 목표 수익 도달로 일부 익절"
    if "profit_ladder" in lowered:
        return "수익 구간별 분할 익절"
    if "risk_reward_take_profit" in lowered:
        return "손익비 목표 도달로 청산"
    if "vwap_extension_take_profit" in lowered:
        return "VWAP 과확장 구간에서 수익 실현"
    if "resistance_take_profit" in lowered:
        return "저항권 접근으로 수익 실현"
    if "volume_exhaustion_take_profit" in lowered:
        return "거래량/체결 강도 둔화로 수익 실현"
    if "opening_gap_profit_take" in lowered:
        return "장초반 갭 추격 구간 빠른 익절"
    if "time_decay_profit_exit" in lowered:
        return "수익권 시간 경과와 되돌림 기준으로 청산"
    if "take_profit" in lowered:
        return "목표 수익 실현으로 청산"
    if "trailing_stop" in lowered:
        return "추적 손절로 청산"
    if "vwap_breakdown" in lowered:
        return "VWAP 이탈로 청산"
    if (
        "exit_trigger_not_captured" in lowered
        or "monitor_exit_trigger_not_captured" in lowered
        or "sell 실행 및 잔여수량" in lowered
        or "청산 트리거 미확인" in lowered
        or "청산 이유는 기록되지" in lowered
        or "exit reasoning was not captured" in lowered
    ):
        return "모니터 청산 트리거 미확인"
    if "sell_execution_confirmed" in lowered or "full_sell_quantity_reconciled" in lowered:
        return "모니터 청산 트리거 미확인"
    if "intraday low break" in lowered or "intraday_low_break" in lowered:
        return "장중 저점 이탈 기준으로 청산"
    if "below_vwap_reclaim_not_ready" in lowered or "below vwap reclaim not ready" in lowered:
        return "VWAP 재회복 미완료 기준으로 청산"
    operatorized = operatorize_report_text(raw)
    if operatorized and operatorized != raw:
        return operatorized
    return stripped.replace("_", " ")



def operatorize_report_text(text: Any) -> str:
    cleaned = normalize_trade_report_language(text)
    if not cleaned:
        return ""
    lowered = cleaned.lower()
    cleaned = cleaned.replace(
        "pullback rebound above vwap with volume confirmation",
        "VWAP 위 되돌림 반등과 거래량 확인",
    )
    cleaned = cleaned.replace(
        "눌림목 rebound above vwap with volume confirmation",
        "VWAP 위 되돌림 반등과 거래량 확인",
    )
    cleaned = cleaned.replace(
        "pullback structure above vwap with volume confirmation",
        "VWAP 위 눌림목 구조와 거래량 확인",
    )
    cleaned = cleaned.replace(
        "눌림목 structure above vwap with volume confirmation",
        "VWAP 위 눌림목 구조와 거래량 확인",
    )
    cleaned = cleaned.replace(
        "breakout above recent high with vwap hold and volume confirmation",
        "VWAP 유지와 거래량 확인이 있는 최근 고점 돌파",
    )
    cleaned = re.sub(r"스캐너 1순위\s+([A-Z0-9]+)은", r"스캐너 상위 후보 \1은", cleaned)
    cleaned = cleaned.replace(" 이유로 막혔고", " 이유로 보류됐고")
    cleaned = cleaned.replace(" 사유로 막힌 뒤", " 사유로 보류된 뒤")
    lowered = cleaned.lower()
    exact_phrase = resolve_exact_operator_phrase(lowered)
    if exact_phrase is not None:
        return exact_phrase
    context_phrase = resolve_market_selection_phrase(
        cleaned, safe_fullmatch=safe_fullmatch, _clip=_clip, _fmt_pct=_fmt_pct,
        exit_reason_label=exit_reason_label, operator_axis_label=operator_axis_label,
    )
    if context_phrase is not None:
        return context_phrase
    lifecycle_phrase = resolve_lifecycle_operator_phrase(
        cleaned, safe_fullmatch=safe_fullmatch, _clip=_clip,
        operator_action_label=operator_action_label, operator_axis_label=operator_axis_label,
        operator_filter_label=operator_filter_label, operator_filter_status=operator_filter_status,
    )
    if lifecycle_phrase is not None:
        return lifecycle_phrase
    cleaned = cleaned.replace("Hard stop", "고정 손절 기준")
    cleaned = cleaned.replace("Adaptive stop", "상황 대응형 손절 기준")
    cleaned = cleaned.replace("Take profit", "목표 수익 실현 기준")
    cleaned = cleaned.replace("Partial take profit", "1차 일부 익절")
    cleaned = cleaned.replace("Profit ladder", "구간별 분할 익절")
    cleaned = cleaned.replace("Risk/reward take profit", "손익비 익절")
    cleaned = cleaned.replace("VWAP extension take profit", "VWAP 과확장 익절")
    cleaned = cleaned.replace("Resistance take profit", "저항권 익절")
    cleaned = cleaned.replace("Volume exhaustion take profit", "거래량 둔화 익절")
    cleaned = cleaned.replace("Opening gap profit take", "갭 추격 빠른 익절")
    cleaned = cleaned.replace("Time-decay profit exit", "시간 경과 수익 보전")
    cleaned = cleaned.replace("Trailing stop", "추적 손절 기준")
    cleaned = cleaned.replace("Peak drawdown", "고점 대비 하락폭")
    cleaned = cleaned.replace("VWAP breakdown", "VWAP 이탈")
    cleaned = cleaned.replace("Intraday low break", "장중 저점 이탈")
    cleaned = cleaned.replace("Trend breakdown", "추세 훼손")
    return normalize_trade_report_language(cleaned)



def preserve_legacy_trade_report_bullet(value: Any) -> str:
    cleaned = _clip(value, max_len=260)
    if not cleaned:
        return ""
    legacy_prefixes = (
        "Top candidates:",
        "Selection decision:",
        "Final decision basis:",
        "Tie-break rule:",
        "Runner-ups lost because:",
        "Monitor runs:",
        "Trigger type:",
    )
    if any(cleaned.startswith(prefix) for prefix in legacy_prefixes):
        return cleaned
    return ""



def operatorize_report_section(section: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(section or {})
    if "headline" in normalized:
        normalized["headline"] = operatorize_report_text(normalized.get("headline"))
    if "summary" in normalized:
        normalized["summary"] = operatorize_report_text(normalized.get("summary"))
    if isinstance(normalized.get("bullets"), list):
        normalized_bullets: List[str] = []
        for item in list(normalized.get("bullets") or []):
            preserved = preserve_legacy_trade_report_bullet(item)
            if preserved:
                normalized_bullets.append(preserved)
                continue
            operatorized = operatorize_report_text(item)
            if operatorized:
                normalized_bullets.append(operatorized)
        normalized["bullets"] = _dedupe_list(
            normalized_bullets,
            max_items=12,
            max_len=260,
        )
    if isinstance(normalized.get("watch_next"), list):
        normalized["watch_next"] = _dedupe_list(
            [operatorize_report_text(item) for item in list(normalized.get("watch_next") or []) if operatorize_report_text(item)],
            max_items=6,
            max_len=200,
        )
    if isinstance(normalized.get("thesis_invalidation"), list):
        normalized["thesis_invalidation"] = _dedupe_list(
            [operatorize_report_text(item) for item in list(normalized.get("thesis_invalidation") or []) if operatorize_report_text(item)],
            max_items=6,
            max_len=200,
        )
    return normalized


