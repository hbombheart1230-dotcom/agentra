from __future__ import annotations

import re
from typing import Any


def normalize_trade_report_language_impl(text: Any, *, sanitize_forbidden_scripts_text: Any, _clip: Any) -> str:
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
