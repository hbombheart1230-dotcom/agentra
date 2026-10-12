"""Operator summary reason/pattern/signal-basis naming (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _operator_reason_name_r3_impl(value, *, facade):
    raw = str(value or "").strip()
    if not raw:
        return ""
    lowered = raw.lower().strip()
    if lowered in {"hold", "unknown", "none", "null", "-"}:
        return ""
    if lowered.startswith("entry evidence was not captured"):
        return ""
    if lowered.startswith("entry context was recovered"):
        return ""
    if "진입은 hold 조건에서 실행" in raw:
        return ""
    if "entry evidence was not captured" in lowered or "position context was inferred" in lowered:
        return ""
    if "position is still open" in lowered or "포지션은 아직 열려" in raw:
        return ""
    if "청산 근거가 누락" in raw:
        return ""
    if (
        "sell 실행 및 잔여수량" in lowered
        or "sell_execution_confirmed" in lowered
        or "full_sell_quantity_reconciled" in lowered
        or "exit_trigger_not_captured" in lowered
        or "monitor_exit_trigger_not_captured" in lowered
    ):
        return "모니터 청산 트리거 미확인"
    if lowered.startswith("진입 사유는 "):
        raw = raw[len("진입 사유는 ") :].strip()
        lowered = raw.lower().strip()
    if lowered.endswith("입니다"):
        raw = raw[:-3].strip()
        lowered = raw.lower().strip()
    scanner_match = facade.re.search(
        r"scanner selected\s+([0-9a-zA-Z]+)\s+as rank\s+#?\d+.*?because it led on\s+(.+?)(?:\.|$)",
        raw,
        flags=facade.re.IGNORECASE,
    )
    if scanner_match:
        basis = facade._operator_signal_basis_name(scanner_match.group(2))
        return f"스캐너 1순위 선정: {basis}" if basis else "스캐너 1순위 선정"
    if lowered.startswith("sell was triggered because "):
        lowered = lowered[len("sell was triggered because ") :].strip().rstrip(".")
        raw = lowered
    normalized = lowered.replace("-", "_").replace(" ", "_")
    mapping = {
        "breakout_above_recent_high": "직전 고점 돌파",
        "breakout_above_recent_high_with_vwap_structure_confirmation": "직전 고점 돌파 + VWAP 구조 확인",
        "breakout_above_recent_high_with_vwap_hold_and_volume_confirmation": "직전 고점 돌파 + VWAP 유지 + 거래량 확인",
        "pullback_structure_above_vwap_with_volume_confirmation": "VWAP 위 눌림목 + 거래량 확인",
        "pullback_rebound": "눌림목 반등",
        "pullback_rebound_above_vwap_with_confirmation": "눌림목 반등 + VWAP 확인",
        "pullback_rebound_above_vwap_with_volume_confirmation": "눌림목 반등 + VWAP + 거래량 확인",
        "pullback_reclaim_above_vwap_with_rebound_confirmation": "눌림목 VWAP 재회복 + 반등 확인",
        "pullback_reclaim_above_vwap_with_volume_confirmation": "눌림목 VWAP 재회복 + 거래량 확인",
        "hard_stop": "고정 손절 기준",
        "stop_loss": "고정 손절 기준",
        "take_profit": "목표 수익 실현 기준",
        "partial_take_profit": "1차 일부 익절",
        "profit_ladder": "구간별 분할 익절",
        "risk_reward_take_profit": "손익비 익절",
        "vwap_extension_take_profit": "VWAP 과확장 익절",
        "resistance_take_profit": "저항권 익절",
        "volume_exhaustion_take_profit": "거래량 둔화 익절",
        "opening_gap_profit_take": "갭 추격 빠른 익절",
        "time_decay_profit_exit": "시간 경과 수익 보전",
        "vwap_breakdown": "VWAP 이탈",
        "peak_drawdown": "고점 대비 하락폭 기준",
        "intraday_low_break": "장중 저점 이탈 기준",
        "prior_low_break": "직전 저점 이탈",
        "trend_breakdown": "추세 붕괴 기준",
        "trailing_stop": "추적 손절 기준",
        "eod_flat": "장마감 정리 기준",
        "exit_trigger_not_captured": "모니터 청산 트리거 미확인",
        "monitor_exit_trigger_not_captured": "모니터 청산 트리거 미확인",
        "sell_execution_confirmed": "모니터 청산 트리거 미확인",
        "full_sell_quantity_reconciled": "모니터 청산 트리거 미확인",
        "no_position": "",
        "no": "",
        "unknown": "미분류",
    }
    korean_text = raw.strip()
    if "VWAP 위 눌림목 구조와 거래량 확인" in korean_text:
        return "VWAP 위 눌림목 + 거래량 확인"
    if "직전 고점 돌파와 VWAP 구조 확인" in korean_text:
        return "직전 고점 돌파 + VWAP 구조 확인"
    if "VWAP 유지와 거래량 확인이 있는 최근 고점 돌파" in korean_text:
        return "직전 고점 돌파 + VWAP 유지 + 거래량 확인"
    if korean_text == "눌림목·거래량 경로":
        return "눌림목 + 거래량 경로"
    if korean_text == "돌파 경로":
        return "돌파 경로"
    if korean_text == "장중 저점 이탈":
        return "장중 저점 이탈 기준"
    if "pullback reclaim above vwap with rebound confirmation" in lowered:
        return "눌림목 VWAP 재회복 + 반등 확인"
    if "pullback structure above vwap with volume confirmation" in lowered:
        return "VWAP 위 눌림목 + 거래량 확인"
    if "pullback rebound above vwap with volume confirmation" in lowered:
        return "눌림목 반등 + VWAP + 거래량 확인"
    if "pullback rebound above vwap with confirmation" in lowered:
        return "눌림목 반등 + VWAP 확인"
    return mapping.get(normalized, raw)


def _operator_pattern_name_r3_impl(value, *, axis, fallback_reason, facade):
    raw = str(value or "").strip()
    lowered = raw.lower().strip()
    if lowered.startswith("entry context was recovered"):
        return ""
    if "진입은 hold 조건에서 실행" in raw:
        return ""
    if "entry evidence was not captured" in lowered or "position context was inferred" in lowered:
        return ""
    if "position is still open" in lowered or "포지션은 아직 열려" in raw:
        return ""
    if "청산 근거가 누락" in raw:
        return ""
    if (
        "sell 실행 및 잔여수량" in lowered
        or "sell_execution_confirmed" in lowered
        or "full_sell_quantity_reconciled" in lowered
        or "exit_trigger_not_captured" in lowered
        or "monitor_exit_trigger_not_captured" in lowered
    ):
        return "청산 트리거 미확인"
    if lowered in {"", "-", "no", "none", "unknown", "hold", "no_position", "no position"}:
        reason = facade._operator_reason_name(fallback_reason)
        if reason:
            return facade._operator_pattern_from_reason_name(reason, axis=axis)
        return ""
    normalized = lowered.replace("-", "_").replace(" ", "_")
    mapping = {
        "breakout": "돌파",
        "pullback": "눌림목",
        "reclaim": "VWAP 재회복",
        "continuation": "추세 지속",
        "hard_stop": "손절",
        "stop_loss": "손절",
        "peak_drawdown": "고점 대비 하락폭",
        "vwap_breakdown": "VWAP 이탈",
        "intraday_low_break": "장중 저점 이탈",
        "trend_breakdown": "추세 붕괴",
        "trailing_stop": "추적 손절",
        "take_profit": "익절",
        "eod_flat": "장마감 정리",
        "exit_trigger_not_captured": "청산 트리거 미확인",
        "monitor_exit_trigger_not_captured": "청산 트리거 미확인",
        "sell_execution_confirmed": "청산 트리거 미확인",
        "full_sell_quantity_reconciled": "청산 트리거 미확인",
    }
    return mapping.get(normalized, raw)


def _operator_pattern_from_reason_name_r3_impl(reason_name, *, axis, facade):
    text = str(reason_name or "").strip()
    if not text or text == "미분류":
        return ""
    if "고정 손절" in text:
        return "손절"
    if "장중 저점" in text:
        return "장중 저점 이탈"
    if "고점 대비" in text:
        return "고점 대비 하락폭"
    if "VWAP 이탈" in text:
        return "VWAP 이탈"
    if "목표 수익" in text or "익절" in text:
        return "익절"
    if "돌파" in text:
        return "돌파"
    if "눌림목" in text:
        return "눌림목"
    if axis == "entry" and text.startswith("스캐너 1순위 선정"):
        return ""
    return text


def _operator_signal_basis_name_r3_impl(value, *, facade):
    raw = str(value or "").strip().rstrip(".")
    if not raw:
        return ""
    pieces = [part.strip() for part in facade.re.split(r",|\band\b", raw) if part.strip()]
    mapping = {
        "turnover": "거래대금",
        "volume": "거래량",
        "turnover and volume": "거래대금/거래량",
        "trading value": "거래대금",
        "theme": "테마",
        "theme and sector alignment": "섹터·테마 정렬",
        "sector alignment": "섹터 정렬",
        "sentiment support": "감성 지원",
        "combined scanner ranking score": "스캐너 종합점수",
        "회전율/거래량": "회전율/거래량",
        "섹터·테마 정렬": "섹터·테마 정렬",
        "감성 지원": "감성 지원",
    }
    lowered = raw.lower()
    if lowered in mapping:
        return mapping[lowered]
    out: List[str] = []
    for piece in pieces:
        key = piece.lower()
        out.append(mapping.get(key, piece))
    return " + ".join(dict.fromkeys(out))


def _combined_pattern_key_r3_impl(row, *, facade):
    playbook = facade._first_text(row.get("final_playbook"), row.get("playbook"))
    tactical = facade._text_value(row.get("tactical_strategy"))
    rank = facade._text_value(row.get("scanner_rank_bucket"))
    entry = facade._operator_label_fallback(
        facade._operator_pattern_name(row.get("entry_pattern_type"), axis="entry", fallback_reason=row.get("entry_reason")),
        axis="entry",
    )
    exit_pattern = facade._operator_label_fallback(
        facade._operator_pattern_name(row.get("exit_pattern_type"), axis="exit", fallback_reason=row.get("exit_reason")),
        axis="exit",
    )
    parts = [part for part in (playbook, tactical, rank, entry, exit_pattern) if part]
    return " | ".join(parts)
