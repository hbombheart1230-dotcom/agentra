from __future__ import annotations

from typing import Any


def append_summary_market_news(
    *,
    lines: Any, _build_strategy_horizon_lines: Any, _compact_decimal: Any, _is_not_captured: Any,
    _korea_index_lines: Any, _listify: Any, _metadata_value: Any, _theme_label: Any,
    _translated_metadata: Any, carryover_context: Any, carryover_exit: Any, entry_watch_lines: Any,
    market: Any, market_news: Any, market_summary: Any, monitor_guide: Any,
    playbook: Any, recovered_partial_exit: Any, report: Any, risk_tone: Any,
    selection: Any, symbol: Any, symbol_news: Any,
) -> None:
    """Append canonical Markdown section text in the original statement order."""
    lines.append("## 🧠 전략 및 시장 맥락")
    lines.append("")
    lines.append("### 시장 상태")
    lines.append("")
    lines.append(f"* {market_summary}")
    for korea_line in _korea_index_lines(market):
        lines.append(f"* 국내 지수: {korea_line}")
    if market.get("vix_level") not in (None, ""):
        lines.append(f"* VIX: {_compact_decimal(market.get('vix_level'))}")
    if market.get("market_sentiment"):
        lines.append(f"* 시장 심리: {_metadata_value(market.get('market_sentiment'))}")
    if carryover_exit:
        lines.append(
            f"* 날짜 주의: 위 시장/지수는 {carryover_context.get('exit_date_kst') or '청산일'} 청산 시점 컨텍스트입니다. "
            f"오버나이트 승인 판단은 {carryover_context.get('estimated_entry_date_kst') or '이전 거래일'} 기준과 분리해 봅니다."
        )
    lines.append("")
    lines.append("### 전략가 출력 요약")
    lines.append("")
    lines.append(f"* 플레이북: **{playbook or '-'}**")
    lines.append(f"* 리스크 톤: {risk_tone or '-'}")
    themes = [_theme_label(x) for x in _listify(market.get("themes") or market.get("preferred_themes")) if not _is_not_captured(x)]
    if themes:
        lines.append(f"* 핵심 테마: {', '.join(themes[:4])}")
    theme_source = _metadata_value(market.get("theme_source"))
    theme_status = _metadata_value(market.get("theme_source_status"))
    if theme_source and theme_source != "-":
        source_text = theme_source
        if theme_status and theme_status != "-":
            source_text += f" / {theme_status}"
        lines.append(f"* 테마 출처: {source_text}")
    if monitor_guide:
        lines.append(f"* 모니터 가이드: {monitor_guide}")
    strategy_horizon_lines = _build_strategy_horizon_lines(report, compact=True)
    if strategy_horizon_lines:
        lines.append("")
        lines.append("### 전략 보유 기간")
        lines.append("")
        lines.extend(strategy_horizon_lines)
    if entry_watch_lines and not carryover_exit:
        lines.append(f"* 후보 감시: {entry_watch_lines[0]}")
        if len(entry_watch_lines) > 1:
            lines.append(f"* 후보 선택: {entry_watch_lines[-1]}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📰 뉴스 및 컨텍스트")
    lines.append("")
    lines.append("### 시장 뉴스")
    lines.append("")
    if market_news:
        lines.extend(f"* {item}" for item in market_news)
    else:
        lines.append("* 표본 없음")
        lines.append("* 원천 위치: ai_trade_report_input.json의 market_context_at_entry.market_news_titles")
    lines.append("")
    lines.append(f"### 종목 뉴스 ({symbol})")
    lines.append("")
    if symbol_news:
        lines.extend(f"* {item}" for item in symbol_news)
    else:
        lines.append("* 표본 없음")
        lines.append(f"* 원천 위치: ai_trade_report_input.json의 market_context_at_entry.candidate_news_titles 중 {symbol} 항목")
    lines.append("")
    lines.append("👉 해석:")
    lines.append("")
    if carryover_exit:
        lines.append("* 종목은 오버나이트/주말 이월 포지션 청산 흐름")
        lines.append(f"* 전략은 {playbook or '-'} → **당일 신규 선정이 아니라 보유 포지션 청산 품질 중심으로 확인 필요**")
    elif recovered_partial_exit:
        lines.append("* 종목은 보유/회수 포지션 청산 흐름")
        lines.append(f"* 전략은 {playbook or '-'} → **신규 선정 평가가 아니라 청산 결과 중심으로 확인 필요**")
    else:
        lines.append(f"* 종목은 {_translated_metadata(selection.get('basis') or '후보 점수 우위')} 흐름")
        lines.append(f"* 전략은 {playbook or '-'} → **전략/종목 톤 정합성 점검 필요**")
    lines.append("")
    lines.append("---")
    lines.append("")
