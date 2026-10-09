from __future__ import annotations

from typing import Any, Dict, List


def _operatorize_strategist_output_text_impl(value: Any, *, _metadata_value) -> str:
    text = _metadata_value(value)
    if not text:
        return ""
    replacements = (
        ("defensive frame", "방어형 전략 프레임"),
        ("pullback frame", "눌림목 전략 프레임"),
        ("breakout frame", "돌파 전략 프레임"),
        (" with ", " / "),
        ("normal risk tone", "정상 위험 톤"),
        ("balanced risk tone", "균형 위험 톤"),
        ("conservative risk tone", "보수적 위험 톤"),
        ("monitor guidance is defensive_exit", "모니터 가이드는 defensive_exit"),
        ("neutral regime with neutral sentiment", "중립 체제와 중립 감정"),
        ("neutral regime / neutral sentiment", "중립 체제와 중립 감정"),
        ("Active memory layers: none", "활성 메모리 레이어 없음"),
        ("Active memory layers:", "활성 메모리 레이어:"),
        ("unused visible layers:", "미사용 표시 레이어:"),
        ("layer inactive", "레이어 비활성"),
        ("insufficient_trade_count", "거래 수 부족"),
        ("no_symbol", "종목 없음"),
        (
            "News was used for market/theme context and scanner guidance; it was not used as final symbol selection.",
            "뉴스는 시장/테마 맥락과 스캐너 가이드에 사용됐고, 최종 종목 선정 근거로는 사용되지 않았습니다.",
        ),
        (
            "Rank candidates by strategist frame fit, tape confirmation, and risk policy alignment.",
            "전략 프레임 적합도, 장중 확인, 리스크 정책 정합성 기준으로 후보를 정렬했습니다.",
        ),
        ("Entry is conditional on monitor gate confirmation.", "진입은 모니터 게이트 확인 조건부입니다."),
        (
            "Strategist permits only the strategy frame; scanner, monitor, supervisor, and executor still own downstream gates.",
            "전략가는 전략 프레임만 허용하며, 스캐너/모니터/슈퍼바이저/집행기가 후속 게이트를 소유합니다.",
        ),
        ("final_symbol_selection", "최종 종목 선택"),
        ("final_candidate_rank", "최종 후보 순위"),
        ("playbook=defensive", "playbook=방어형"),
        ("playbook=pullback", "playbook=눌림목"),
        ("playbook=breakout", "playbook=돌파"),
        ("risk=normal", "risk=정상"),
        ("status=ok", "status=정상"),
        ("liquidity", "유동성"),
        ("risk_penalty", "리스크 패널티"),
        ("low_volatility", "저변동성"),
        ("illiquid_microcap", "저유동성 소형주"),
        ("headline_only_momentum", "헤드라인 단독 모멘텀"),
        ("high_gap_speculative", "갭 급등 투기성"),
        ("VWAP reclaim", "VWAP 회복"),
        ("rebound confirmation", "리바운드 확인"),
        ("too_extended_from_vwap", "VWAP 대비 과확장"),
        ("breakout_without_volume", "거래량 없는 돌파"),
        ("risk_policy_block", "리스크 정책 차단"),
    )
    out = text
    for src, dst in replacements:
        out = out.replace(src, dst)
    return out

def _strategy_output_text_impl(value: Any, *, max_len: int = 240, _operatorize_strategist_output_text, _clip) -> str:
    text = _operatorize_strategist_output_text(value)
    if not text or text == "-":
        return ""
    return _clip(text, max_len)

def _strategy_output_list_text_impl(values: Any, *, limit: int = 4, sep: str = ", ", _listify, _strategy_output_text) -> str:
    items: List[str] = []
    for raw in _listify(values):
        text = _strategy_output_text(raw, max_len=120)
        if not text or text in items:
            continue
        items.append(text)
        if len(items) >= max(1, int(limit)):
            break
    return sep.join(items)
