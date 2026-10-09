from __future__ import annotations

import re
from typing import Any, Optional


def resolve_market_selection_phrase(
    cleaned: str, *, safe_fullmatch: Any, _clip: Any, _fmt_pct: Any,
    exit_reason_label: Any, operator_axis_label: Any,
) -> Optional[str]:
    """Resolve market, policy, news and selection explanations."""
    m = safe_fullmatch(
        r"same-day closed trade reports show (\d+) trades with (\d+) wins,\s*(\d+) losses,\s*avg pnl pct\s*([0-9.+\-]+)\.?",
        cleaned,
        flags=re.IGNORECASE,
    )
    if m:
        trade_count = int(m.group(1))
        win_count = int(m.group(2))
        loss_count = int(m.group(3))
        avg_pnl_pct = _fmt_pct(str(m.group(4)).rstrip("."))
        return f"당일 closed trade {trade_count}건, 승/패 {win_count}/{loss_count}, 평균 손익률 {avg_pnl_pct}였습니다."
    
    m = safe_fullmatch(r"same-price cost-loss trades\s*(\d+)/(\d+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"동일가 왕복 후 비용 손실 거래가 {m.group(2)}건 중 {m.group(1)}건에서 확인됐습니다."
    
    m = safe_fullmatch(
        r"정규화된 청산 사유는\s+SELL was triggered because\s+(.+?)\.?입니다\.?",
        cleaned,
        flags=re.IGNORECASE,
    )
    if m:
        exit_label = exit_reason_label(m.group(1))
        if exit_label:
            return f"정규화된 청산 사유는 {exit_label}입니다."
    
    m = safe_fullmatch(r"SELL was triggered because\s+(.+?)\.?", cleaned, flags=re.IGNORECASE)
    if m:
        trigger_label = operator_axis_label(m.group(1))
        return f"{trigger_label} 기준으로 청산됐습니다."
    
    m = safe_fullmatch(r"Market regime:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"시장 상태는 {_clip(m.group(1), max_len=160)}입니다."
    m = safe_fullmatch(r"시장 regime:\s*([^,]+),\s*감성:\s*([^,]+),\s*플레이북:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"시장 상태는 {_clip(m.group(1), max_len=80)}이며, 시장 심리는 {_clip(m.group(2), max_len=80)}이고, 플레이북은 {_clip(m.group(3), max_len=120)}입니다."
    m = safe_fullmatch(r"Global sentiment score:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"글로벌 감성 점수는 {_clip(m.group(1), max_len=120)}입니다."
    m = safe_fullmatch(r"글로벌 감성 점수:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"글로벌 감성 점수는 {_clip(m.group(1), max_len=120)}입니다."
    m = safe_fullmatch(r"VIX:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"VIX 수준은 {_clip(m.group(1), max_len=120)}입니다."
    m = safe_fullmatch(r"VIX 수준:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"VIX 수준은 {_clip(m.group(1), max_len=120)}입니다."
    m = safe_fullmatch(r"News input:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"뉴스 입력 요약은 {_clip(m.group(1), max_len=240)}입니다."
    m = safe_fullmatch(r"News query targets:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"뉴스 조회 대상은 {_clip(m.group(1), max_len=220)}입니다."
    m = safe_fullmatch(
        r"적용 정책[:：]?\s*timeframe\s*([0-9]+)\s*분,\s*breakout lookback\s*([0-9]+),\s*volume ratio min\s*([0-9.]+)",
        cleaned,
        flags=re.IGNORECASE,
    )
    if m:
        return (
            f"적용 정책은 {int(m.group(1))}분봉, 돌파 확인 기준 봉 수 {int(m.group(2))}, "
            f"최소 거래량 비율 {float(m.group(3)):.2f}였습니다."
        )
    m = safe_fullmatch(r"Commander 의도[:：]?\s*([^,]+),\s*라우트[:：]?\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"Commander 의도는 {_clip(m.group(1), max_len=80)}이고, 선택된 라우트는 {_clip(m.group(2), max_len=120)}입니다."
    m = safe_fullmatch(r"정책 검증 상태[:：]?\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        status_text = _clip(m.group(1), max_len=200).replace("(", ", ").replace(")", "")
        return f"정책 검증 상태는 {status_text}입니다."
    m = safe_fullmatch(r"VWAP 확장 비율 조건[:：]?\s*([^,]+),\s*눌림목 비율[:：]?\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"VWAP 확장 허용 범위는 {_clip(m.group(1), max_len=80)}이고, 눌림목 비율 범위는 {_clip(m.group(2), max_len=80)}입니다."
    m = safe_fullmatch(r"Scanner linkage:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"스캐너 연결 근거는 {_clip(m.group(1), max_len=260)}입니다."
    m = safe_fullmatch(r"execution quote snapshot spread was\s*([0-9.]+)\s*bps", cleaned, flags=re.IGNORECASE)
    if m:
        return f"실행 시점 호가 스냅샷 기준 스프레드는 {float(m.group(1)):.1f}bps였습니다."
    m = safe_fullmatch(r"Key strategist inputs:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"전략가 핵심 입력은 {_clip(m.group(1), max_len=240)}입니다."
    m = safe_fullmatch(r"Market news titles:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"주요 시장 뉴스는 {_clip(m.group(1), max_len=240)}입니다."
    m = safe_fullmatch(r"Candidate news titles:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"후보 종목 관련 뉴스는 {_clip(m.group(1), max_len=240)}입니다."
    m = safe_fullmatch(r"테마:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"주요 테마는 {_clip(m.group(1), max_len=220)}입니다."
    m = safe_fullmatch(r"적용 테마:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"적용된 테마는 {_clip(m.group(1), max_len=220)}입니다."
    m = safe_fullmatch(r"뉴스 분석:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"뉴스 분석 범위는 {_clip(m.group(1), max_len=220)}입니다."
    m = safe_fullmatch(r"Universe scanned:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        value = _clip(m.group(1), max_len=80)
        if value == "not_captured":
            return "비교한 후보 수는 별도로 기록되지 않았습니다."
        return f"총 {value}개 후보를 비교했습니다."
    m = safe_fullmatch(r"Selected rank:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        value = _clip(m.group(1), max_len=80)
        if value == "not_captured":
            return "선정 순위 정보는 별도로 기록되지 않았습니다."
        return f"최종 선정 순위는 {value}입니다."
    m = safe_fullmatch(r"Selected because:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"선정 이유는 {_clip(m.group(1), max_len=220)}입니다."
    m = safe_fullmatch(r"Top candidates:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"상위 후보는 {_clip(m.group(1), max_len=240)}입니다."
    m = safe_fullmatch(r"Why not others:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"다른 후보가 밀린 이유는 {_clip(m.group(1), max_len=240)}입니다."
    m = safe_fullmatch(r"Selection decision:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"최종 선정 판단은 {_clip(m.group(1), max_len=220)}입니다."
    m = safe_fullmatch(r"Final decision basis:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"최종 결정 기준은 {_clip(m.group(1), max_len=220)}입니다."
    m = safe_fullmatch(r"Tie-break rule:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"동률 해소 기준은 {_clip(m.group(1), max_len=220)}입니다."
    m = safe_fullmatch(r"동률 해소 기준[:：]?\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"동률 해소 기준은 {_clip(m.group(1), max_len=220)}입니다."
    m = safe_fullmatch(r"Runner-ups lost because:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"차순위 후보가 밀린 이유는 {_clip(m.group(1), max_len=240)}입니다."
    m = safe_fullmatch(r"Selection sources:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"선정에 반영된 핵심 소스는 {_clip(m.group(1), max_len=220)}입니다."
    m = safe_fullmatch(r"Ranking basis:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"순위 산정 기준은 {_clip(m.group(1), max_len=220)}입니다."
    m = safe_fullmatch(r"Chart / feature coverage:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"차트 및 지표 충실도는 {_clip(m.group(1), max_len=120)}입니다."
    return None
