from __future__ import annotations

import logging
import re
from typing import Any, Dict, List

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
    cleaned = sanitize_forbidden_scripts_text(_clip(text, max_len=2000))
    if not cleaned:
        return ""

    def _normalize_metadata_value(value: str) -> str:
        raw = _clip(value, max_len=240).strip()
        lowered = raw.lower()
        if lowered in {"unknown", "not available", "not_available", "unavailable"}:
            return "확인되지 않음"
        if lowered in {"not captured", "not_captured"}:
            return "기록되지 않음"
        return raw

    def _replace_scanner_selection(match: re.Match[str]) -> str:
        symbol = _clip(match.group(1), max_len=24)
        rank = _clip(match.group(2), max_len=8)
        total = _clip(match.group(3), max_len=8)
        score = _clip(match.group(4), max_len=32)
        reason = _clip(match.group(5), max_len=220)
        return (
            f"스캐너는 {total}개 후보 중 {rank}위인 {symbol}을 총점 {score}로 선정했습니다. "
            f"선정 이유는 {reason}입니다."
        )

    def _replace_headlines(match: re.Match[str]) -> str:
        count = _clip(match.group(1), max_len=12)
        targets = _clip(match.group(2), max_len=12)
        detail = _clip(match.group(3), max_len=120)
        if detail:
            return f"관련 헤드라인 {count}건을 함께 반영했고 총 {targets}개 대상({detail})을 점검했습니다."
        return f"관련 헤드라인 {count}건을 함께 반영했고 총 {targets}개 대상을 점검했습니다."

    cleaned = re.sub(
        r"Scanner selected ([0-9A-Z]+) as rank #?(\d+) out of (\d+) candidates with score ([0-9.\-]+) because (.+?)(?:\.)?$",
        _replace_scanner_selection,
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"(\d+)\s+headlines were considered across (\d+)\s+targets(?:\s*\(([^)]*)\))?",
        _replace_headlines,
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"Scanner selected the highest-ranked candidate after (.+?)(?:\.)?$",
        lambda m: f"스캐너는 { _clip(m.group(1), max_len=220) }를 반영해 최상위 후보를 선정했습니다.",
        cleaned,
        flags=re.IGNORECASE,
    )

    def _replace_metadata_token(match: re.Match[str]) -> str:
        key = str(match.group(1) or "").strip().lower()
        value = _normalize_metadata_value(str(match.group(2) or ""))
        label_map = {
            "source": "데이터 출처",
            "path": "참조 경로",
            "model": "사용 모델",
            "status": "상태",
            "generated_at": "생성 시각",
        }
        return f"{label_map.get(key, key)}: {value}"

    cleaned = re.sub(
        r"\b(source|path|model|status|generated_at)\s*=\s*([^\s;,)\]]+)",
        _replace_metadata_token,
        cleaned,
        flags=re.IGNORECASE,
    )

    replacements = (
        ("Execution outcome summary was not captured.", "거래 생애주기 실행 요약은 기록되지 않았습니다."),
        ("Lifecycle conclusion was not captured.", "최종 생애주기 결론은 기록되지 않았습니다."),
        ("Entry reason was not captured.", "진입 이유는 기록되지 않았습니다."),
        ("Exit reason was not captured.", "청산 이유는 기록되지 않았습니다."),
        ("Reporter linkage was not captured.", "리포터 연계 정보는 기록되지 않았습니다."),
        ("Same-day reporter analysis was not generated yet.", "당일 리포터 분석은 아직 생성되지 않았습니다."),
        (
            "A same-day reporter file exists, but this run was not linked to a run-specific evaluation yet.",
            "당일 리포터 파일은 있지만 이 run에 대한 개별 평가는 아직 연결되지 않았습니다.",
        ),
        ("A same-day reporter analysis was linked to this run.", "당일 리포터 분석이 이 run에 연결됐습니다."),
        ("Interim summary:", "중간 요약:"),
        ("Reporter status:", "리포터 상태는"),
        ("Reporter reason:", "리포터 판단 사유는"),
        ("Reporter grade:", "리포터 등급은"),
        ("Reporter summary:", "리포터 요약은"),
        ("Monitor posture changes", "모니터 posture 변화"),
        ("Macro/news regime changes", "거시 환경 및 뉴스 레짐 변화"),
        ("Lifecycle status is closed", "생애주기 상태는 closed"),
        ("Lifecycle status is open", "생애주기 상태는 open"),
        ("Trailing stop", "추적 손절"),
        ("trailing stop", "추적 손절"),
        ("시장 시장 상태은", "시장 상태는"),
        ("시장 상태은", "시장 상태는"),
        ("Scanner selected", "스캐너는"),
        ("Market Sentiment", "시장 심리"),
        ("Market sentiment", "시장 심리"),
        ("Stress Flags", "스트레스 신호"),
        ("Stress flags", "스트레스 신호"),
        ("Scanner Rank", "스캐너 순위"),
        ("Scanner Ranking Basis", "스캐너 순위 산정 기준"),
        ("Tie Break Rule", "동률 해소 기준"),
        ("Tie-break rule", "동률 해소 기준"),
        ("Tie Break", "동률 해소"),
        ("Regime", "시장 상태"),
        ("playbook", "플레이북"),
        ("Playbook", "플레이북"),
        ("headlines were considered", "관련 헤드라인을 함께 반영했습니다"),
        ("Total Score", "총점"),
        ("strategist-guided weighting, source scoring, and risk penalties", "전략가 가중치, 소스 점수, 리스크 패널티"),
        ("it led on trading value, theme and sector alignment", "거래대금과 테마·섹터 정렬에서 앞섰기 때문"),
        ("breakout_above_recent_high_with_vwap_structure_confirmation", "직전 고점 돌파와 VWAP 구조 확인"),
        ("breakout_path", "돌파 경로"),
        ("pullback_volume_path", "눌림목·거래량 경로"),
        ("candidate signals", "후보 신호"),
        ("market /", "시장 /"),
        ("bearish", "약세"),
        ("bullish", "강세"),
        ("neutral", "중립"),
        ("pullback", "눌림목"),
        ("not captured", "기록되지 않음"),
        ("not available", "확인되지 않음"),
        ("unknown", "판단 정보 없음"),
    )
    for src, dst in replacements:
        cleaned = cleaned.replace(src, dst)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    return cleaned



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
    exact_mapping = {
        "the decision path was recorded, but the operator-facing summary is limited.": "의사결정 경로는 기록되었지만 운영자용 요약은 제한적으로만 남아 있습니다.",
        "current lifecycle status is closed. entry and exit are connected in one lifecycle story.": "이번 라이프사이클은 종결 상태이며, 진입과 청산이 하나의 거래 흐름으로 연결됐습니다.",
        "current lifecycle status is open. entry and exit are still unfolding within one lifecycle story.": "이번 라이프사이클은 아직 진행 중이며, 진입 이후 청산 판단이 이어지고 있습니다.",
        "supervisor approved the order because allowed.": "슈퍼바이저는 주문을 승인했고 가드 판단은 허용이었습니다.",
        "execution quality details were not captured.": "실행 품질 세부 내용은 별도로 기록되지 않았습니다.",
        "reporter linkage was not available yet.": "리포터 연계 결과는 아직 연결되지 않았습니다.",
        "reporter linkage status was recorded separately.": "리포터 연계 상태는 별도로 기록되어 있습니다.",
        "warnings and missing links were recorded for operator follow-up.": "운영자가 후속 확인해야 할 경고와 누락 링크가 함께 기록되었습니다.",
        "no explicit weaknesses were surfaced beyond the recorded trace.": "기록된 추적 정보 외에 추가 약점은 별도로 확인되지 않았습니다.",
        "ai trade report generation failed after retry attempts. review the saved llm response artifact for details.": "AI 거래 리포트 생성이 재시도 이후에도 완료되지 않았습니다. 저장된 LLM 응답 아티팩트를 함께 확인해 주세요.",
        "ai generation failed before a rendered market-context section was produced.": "시장 환경 요약은 생성 도중 중단되어, 저장된 근거를 기준으로 보수적으로 정리했습니다.",
        "ai generation failed before a rendered symbol-selection section was produced.": "종목 선정 설명은 생성 도중 중단되어, 저장된 선정 근거를 기준으로 보수적으로 정리했습니다.",
        "ai generation failed before a rendered entry-decision section was produced.": "진입 판단 설명은 생성 도중 중단되어, 저장된 진입 근거를 기준으로 보수적으로 정리했습니다.",
        "ai generation failed before a rendered holding-monitoring section was produced.": "보유 관리 설명은 생성 도중 중단되어, 저장된 모니터 기록을 기준으로 보수적으로 정리했습니다.",
        "ai generation failed before a rendered exit-decision section was produced.": "청산 판단 설명은 생성 도중 중단되어, 저장된 청산 근거를 기준으로 보수적으로 정리했습니다.",
        "ai generation failed before a rendered execution-quality section was produced.": "실행 품질 설명은 생성 도중 중단되어, 저장된 실행 기록을 기준으로 보수적으로 정리했습니다.",
        "ai generation failed and no rendered improvement section is available.": "AI 생성이 중단되어 개선 포인트는 저장된 경고와 오류 기록 중심으로 정리했습니다.",
        "ai generation failed. review lifecycle artifacts and the saved llm response artifact before taking action.": "AI 생성이 중단되었습니다. 다음 조치를 하기 전에 lifecycle 아티팩트와 저장된 LLM 응답을 함께 확인해 주세요.",
        "link same-day reporter analysis to this lifecycle for a complete quality review.": "동일 일자 리포터 분석이 아직 이 거래 생애주기에 연결되지 않았습니다.",
        "same-price round trips produced fee/tax drag; tighten follow-through evidence before repeating quick reversals.": "동일가 왕복 거래에서 수수료와 세금 손실이 반복돼, 짧은 반전 시도 전에는 후속 추세 확인을 더 엄격하게 봐야 합니다.",
        "same-day closed trades are loss-heavy; keep defensive entry posture until follow-through quality improves.": "당일 닫힌 거래 손익이 전반적으로 약해, 후속 추세 확인 품질이 개선될 때까지는 방어적인 진입 자세를 유지해야 합니다.",
        "selection": "선정 근거를 정리했습니다.",
        "entry": "진입 판단을 정리했습니다.",
        "filters": "스캐너 필터 점검 결과를 정리했습니다.",
        "guard": "승인 및 가드 판단 결과를 정리했습니다.",
        "execution": "실행 결과를 정리했습니다.",
        "reporter": "리포터 평가를 정리했습니다.",
        "none": "추가 보완 포인트는 제한적입니다.",
        "top value or trading-value input supported the selection": "거래대금 상위 신호가 선정 근거를 뒷받침했습니다.",
        "top volume or turnover input supported the selection": "회전율 신호는 존재했지만 최종 우위 근거로는 약했습니다.",
        "theme boost or sector source matched the strategist frame": "테마 가점과 섹터 소스가 전략가 프레임과 맞아떨어졌습니다.",
        "12/13 captured chart features": "13개 중 12개 차트 피처가 확보됐습니다.",
        "news/global sentiment contribution was 0.295": "뉴스와 글로벌 감성 기여 합산값은 0.295였습니다.",
        "risk score was 0.563 and supervisor allow=true": "리스크 점수는 0.563이었고 supervisor 허용 상태도 유지됐습니다.",
        "price anomaly check was not captured in this run": "이번 run에서는 가격 이상치 점검 결과가 저장되지 않았습니다.",
        "price anomaly check was 기록되지 않음 in this run": "이번 run에서는 가격 이상치 점검 결과가 저장되지 않았습니다.",
        "monitor price cross-check found no anomaly": "모니터 가격 교차검증에서 이상치가 확인되지 않았습니다.",
        "monitor price cross-check flagged an anomaly": "모니터 가격 교차검증에서 이상치가 감지되었습니다.",
        "spread or slippage diagnostics were not captured in this run": "이번 run에서는 호가 스프레드 또는 슬리피지 진단이 저장되지 않았습니다.",
        "spread or slippage diagnostics were 기록되지 않음 in this run": "이번 run에서는 호가 스프레드 또는 슬리피지 진단이 저장되지 않았습니다.",
        "holding-phase evidence is thin; preserve more monitor context between entry and exit.": "보유 구간 근거는 제한적이며 진입과 청산 사이 모니터 맥락이 충분하지 않습니다.",
        "같은 날 생성된 reporter 분석을 이 lifecycle에 연결해 전체 품질 평가를 완성해 주세요.": "동일 일자 리포터 분석이 아직 이 거래 생애주기에 연결되지 않았습니다.",
        "보유 단계 근거가 얇아 진입과 청산 사이의 모니터 맥락을 더 보존해야 합니다.": "보유 구간 근거는 제한적이며 진입과 청산 사이 모니터 맥락이 충분하지 않습니다.",
        "monitor trigger changes": "모니터 트리거 변화",
        "macro/news shifts": "거시 환경 및 뉴스 변화",
        "stop-loss breach": "손절 기준 이탈",
        "monitor and scanner divergence": "모니터와 스캐너 판단 발산",
        "negative macro regime shift": "거시 환경의 부정적 전환",
        "guard reason: allowed": "가드 판단 사유는 허용입니다.",
        "supervisor verdict: approve": "슈퍼바이저 최종 판단은 승인입니다.",
        "broad_market_leaders": "브로드마켓 리더",
        "top_value": "거래대금 상위",
        "top_volume": "거래량 상위",
        "sector_theme": "섹터·테마 정렬",
    }
    if lowered in exact_mapping:
        return exact_mapping[lowered]

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
    m = safe_fullmatch(r"Entry run:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        value = _clip(m.group(1), max_len=120)
        if value == "not_captured":
            return "진입 판단이 기록된 run 정보는 남아 있지 않습니다."
        return f"진입 판단이 기록된 run은 {value}입니다."
    m = safe_fullmatch(r"Entry time:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        value = _clip(m.group(1), max_len=120)
        if value == "not_captured":
            return "진입 시각은 별도로 기록되지 않았습니다."
        return f"진입 시각은 {value}입니다."
    m = safe_fullmatch(r"Entry action:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"진입 액션은 {operator_action_label(m.group(1))}입니다."
    m = safe_fullmatch(r"Entry reason:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        value = _clip(m.group(1), max_len=240)
        if value == "not_captured":
            return "진입 판단 사유는 별도로 기록되지 않았습니다."
        return f"진입 판단 근거는 {value}입니다."
    m = safe_fullmatch(r"보유 기간:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"보유 기간은 {_clip(m.group(1), max_len=140)}입니다."
    m = safe_fullmatch(r"모니터 실행:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"모니터 실행 기록은 {_clip(m.group(1), max_len=180)}입니다."
    m = safe_fullmatch(r"모니터 판단:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"모니터 판단 흐름은 {_clip(m.group(1), max_len=220)}입니다."
    m = safe_fullmatch(r"Monitor runs:\s*(\d+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"모니터는 총 {m.group(1)}회 실행되었습니다."
    m = safe_fullmatch(r"Posture:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"현재 포지션 판단은 {operator_action_label(m.group(1))}입니다."
    m = safe_fullmatch(r"Trigger type:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"감지된 핵심 신호는 {operator_axis_label(m.group(1))}입니다."
    m = safe_fullmatch(r"Position age:\s*(\d+)\s*seconds", cleaned, flags=re.IGNORECASE)
    if m:
        return f"포지션 보유 시간은 약 {m.group(1)}초입니다."
    m = safe_fullmatch(r"Effective stop:\s*([^(]+?)(?:\s*\((.+)\))?", cleaned, flags=re.IGNORECASE)
    if m:
        level = _clip(m.group(1), max_len=80)
        reason = operator_axis_label(m.group(2))
        if reason and reason != "-":
            return f"유효 손절 기준은 {level} 수준이며, 기준 축은 {reason}입니다."
        return f"유효 손절 기준은 {level} 수준입니다."
    m = safe_fullmatch(r"Take profit:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"목표 수익 실현 기준은 {_clip(m.group(1), max_len=80)} 수준입니다."
    m = safe_fullmatch(r"Active exit axis:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"현재 우선 감시 중인 청산 축은 {operator_axis_label(m.group(1))}입니다."
    m = safe_fullmatch(r"Exit confirmation:\s*(\d+)/(\d+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"청산 확인 조건은 {m.group(1)}/{m.group(2)} 단계로 기록되었습니다."
    m = safe_fullmatch(r"Watch axes:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        axes = ", ".join(operator_axis_label(part.strip()) for part in m.group(1).split(","))
        return f"주요 감시 축은 {axes}입니다."
    m = safe_fullmatch(r"Decision chain:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"판단 흐름은 {_clip(m.group(1), max_len=220)} 순서로 이어졌습니다."
    m = safe_fullmatch(r"Current price / avg / peak:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"현재가, 평균가, 고점 기준 값은 {_clip(m.group(1), max_len=200)}입니다."
    m = safe_fullmatch(r"Current drawdown / peak drawdown:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"현재 손익 변동과 고점 대비 하락폭은 {_clip(m.group(1), max_len=200)}입니다."
    m = safe_fullmatch(r"Price source:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"가격 기준 소스는 {_clip(m.group(1), max_len=140)}입니다."
    m = safe_fullmatch(r"Feature source:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"지표 기준 소스는 {_clip(m.group(1), max_len=140)}입니다."
    m = safe_fullmatch(r"Recent monitor update:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"최근 모니터 업데이트는 다음과 같습니다: {_clip(m.group(1), max_len=240)}"
    m = safe_fullmatch(r"Exit run:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        value = _clip(m.group(1), max_len=120)
        if value == "not_captured":
            return "청산 판단이 기록된 run 정보는 남아 있지 않습니다."
        return f"청산 판단이 기록된 run은 {value}입니다."
    m = safe_fullmatch(r"Exit time:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        value = _clip(m.group(1), max_len=120)
        if value == "not_captured":
            return "청산 시각은 별도로 기록되지 않았습니다."
        return f"청산 시각은 {value}입니다."
    m = safe_fullmatch(r"Exit action:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"청산 액션은 {operator_action_label(m.group(1))}입니다."
    m = safe_fullmatch(r"Exit reason:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        value = _clip(m.group(1), max_len=240)
        if value in {"position still open", "still open"}:
            return "현재 포지션은 아직 열려 있어 확정된 청산 사유는 없습니다."
        if value == "not_captured":
            return "청산 사유는 별도로 기록되지 않았습니다."
        return f"청산 사유는 {value}입니다."
    m = safe_fullmatch(r"Execution outcome:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"주문 실행 결과는 {_clip(m.group(1), max_len=180)}입니다."
    m = safe_fullmatch(r"Quantity:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"수량: {_clip(m.group(1), max_len=80)}"
    m = safe_fullmatch(r"수량:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"수량: {_clip(m.group(1), max_len=80)}"
    m = safe_fullmatch(r"Execution mode:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"실행 모드: {_clip(m.group(1), max_len=120)}"
    m = safe_fullmatch(r"Broker environment:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        value = _clip(m.group(1), max_len=120)
        if value == "not_captured":
            return "브로커 환경 정보는 별도로 기록되지 않았습니다."
        return f"브로커 환경은 {value}입니다."
    m = safe_fullmatch(r"Supervisor verdict:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"감독 승인 판단은 {operator_action_label(m.group(1))}입니다."
    m = safe_fullmatch(r"Supervisor allow:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"주문 허용 여부는 {operator_action_label(m.group(1))}입니다."
    m = safe_fullmatch(r"Guard reason:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"가드 판단 사유는 {_clip(m.group(1), max_len=200)}입니다."
    m = safe_fullmatch(r"Action reviewed:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"검토한 액션은 {operator_action_label(m.group(1))}입니다."
    m = safe_fullmatch(r"Symbol reviewed:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"검토한 종목은 {_clip(m.group(1), max_len=60)}입니다."
    m = safe_fullmatch(r"Approval mode:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        value = _clip(m.group(1), max_len=120)
        lowered_value = value.lower()
        if lowered_value == "not captured in the execution trace" or (
            "execution trace" in lowered_value and ("not captured" in lowered_value or "기록되지 않음" in value)
        ):
            return "승인 모드는 실행 추적에는 별도로 남아 있지 않습니다."
        return f"승인 모드는 {value}입니다."
    m = safe_fullmatch(r"Lifecycle status:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        status_token = _clip(m.group(1), max_len=80).strip().lower()
        status_label = {
            "closed": "종결",
            "open": "진행 중",
            "pending": "대기",
        }.get(status_token, _clip(m.group(1), max_len=80))
        return f"라이프사이클 상태 {status_label}"
    m = safe_fullmatch(r"Entry\s+([A-Z_]+)\s+was executed by run\s+([A-Za-z0-9_-]+)\.?", cleaned, flags=re.IGNORECASE)
    if m:
        return f"run {_clip(m.group(2), max_len=80)}에서 {operator_action_label(m.group(1))} 진입이 실행됐습니다."
    m = safe_fullmatch(r"Exit\s+([A-Z_]+)\s+was executed by run\s+([A-Za-z0-9_-]+)\.?", cleaned, flags=re.IGNORECASE)
    if m:
        return f"run {_clip(m.group(2), max_len=80)}에서 {operator_action_label(m.group(1))} 청산이 실행됐습니다."
    m = safe_fullmatch(r"슈퍼바이저 판단:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"감독 승인 판단은 {operator_action_label(m.group(1))}입니다."
    m = safe_fullmatch(r"슈퍼바이저 허용:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"주문 허용 여부는 {operator_action_label(m.group(1))}입니다."
    m = safe_fullmatch(r"가드 이유:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"가드 판단 사유는 {_clip(m.group(1), max_len=200)}입니다."
    m = safe_fullmatch(r"검토된 액션:\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"검토한 액션은 {operator_action_label(m.group(1))}입니다."
    m = safe_fullmatch(r"(.+?):\s*(PASS|FAIL|NOT_AVAILABLE)\s*-\s*(.+)", cleaned, flags=re.IGNORECASE)
    if m:
        return f"{operator_filter_label(m.group(1))}은 {operator_filter_status(m.group(2))}였습니다. 근거: {_clip(m.group(3), max_len=220)}"

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


