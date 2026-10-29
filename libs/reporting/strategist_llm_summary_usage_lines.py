"""Strategist LLM summary memory/news usage markdown lines (moved verbatim; normal and clean variants stay separate).

Helpers are resolved on ``facade`` (the strategist_llm_summary module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, List


def memory_usage_lines(memory: Dict[str, Any], *, facade: Any) -> List[str]:
    if not bool(memory.get("available")):
        return ["- 메모리 사용 trace: -"]
    lines = [
        f"- 활성 레이어: {', '.join(str(x) for x in facade._as_list(memory.get('active_layers'))) or '-'}",
        f"- 우선순위: {' -> '.join(str(x) for x in facade._as_list(memory.get('priority_order'))) or '-'}",
        f"- 요약: {facade._text(memory.get('human_summary'))}",
    ]
    applied = facade._as_dict(memory.get("applied_to_strategy"))
    if applied:
        lines.append(f"- 전략 반영: playbook={facade._text(applied.get('playbook_effect'))}, risk={facade._text(applied.get('risk_posture_effect'))}")
        lines.append(
            f"- scanner/monitor 반영: scanner={facade._text(applied.get('scanner_guidance_effect'))}, "
            f"monitor={facade._text(applied.get('monitor_policy_effect'))}"
        )
    layer_decisions = facade._as_dict(memory.get("layer_decisions"))
    for layer in ("daily", "weekly", "monthly", "symbol"):
        row = facade._as_dict(layer_decisions.get(layer))
        if not row:
            continue
        summary = facade._as_dict(row.get("operator_summary"))
        metrics = []
        if summary.get("trade_count") is not None:
            metrics.append(f"trades={summary.get('trade_count')}")
        if summary.get("win_rate") is not None:
            metrics.append(f"win_rate={summary.get('win_rate')}")
        if summary.get("avg_return_pct") is not None:
            metrics.append(f"avg_return_pct={summary.get('avg_return_pct')}")
        metric_text = f" ({', '.join(metrics)})" if metrics else ""
        lines.append(
            f"- {layer}: used={row.get('used')} status={facade._text(row.get('status'), '')} "
            f"effect={facade._text(row.get('effect'), '')}{metric_text}"
        )
    return lines


def news_usage_lines(news: Dict[str, Any], *, facade: Any) -> List[str]:
    if not bool(news.get("available")):
        return ["- 뉴스 사용 trace: -"]
    query_targets = ", ".join(str(x) for x in facade._as_list(news.get("query_targets"))[:10]) or "-"
    return [
        f"- 검색/수집 타깃: {query_targets}",
        f"- 사용 요약: {facade._text(news.get('human_summary'))}",
        f"- 시장 효과: {facade._text(news.get('market_effect'))}",
        f"- 플레이북 효과: {facade._text(news.get('playbook_effect'))}",
        f"- 스캐너 반영: {facade._text(news.get('scanner_guidance_effect'))}",
        f"- 모니터 반영: {facade._text(news.get('monitor_policy_effect'))}",
        f"- 근거 헤드라인 수: market={news.get('market_headline_count')}, candidate={news.get('candidate_headline_count')}",
        f"- query reasoning: {facade._text(news.get('news_query_reasoning'))}",
    ]


def memory_usage_lines_clean(memory: Dict[str, Any], *, facade: Any) -> List[str]:
    if not bool(memory.get("available")):
        return ["- 메모리 사용 trace: -"]
    lines = [
        f"- 활성 레이어: {', '.join(str(x) for x in facade._as_list(memory.get('active_layers'))) or '-'}",
        f"- 우선순위: {' -> '.join(str(x) for x in facade._as_list(memory.get('priority_order'))) or '-'}",
        f"- 요약: {facade._text(memory.get('human_summary'))}",
    ]
    applied = facade._as_dict(memory.get("applied_to_strategy"))
    if applied:
        lines.append(f"- 전략 반영: playbook={facade._text(applied.get('playbook_effect'))}, risk={facade._text(applied.get('risk_posture_effect'))}")
        lines.append(
            f"- scanner/monitor 반영: scanner={facade._text(applied.get('scanner_guidance_effect'))}, "
            f"monitor={facade._text(applied.get('monitor_policy_effect'))}"
        )
    layer_decisions = facade._as_dict(memory.get("layer_decisions"))
    for layer in ("daily", "weekly", "monthly", "symbol"):
        row = facade._as_dict(layer_decisions.get(layer))
        if not row:
            continue
        summary = facade._as_dict(row.get("operator_summary"))
        metrics = []
        if summary.get("trade_count") is not None:
            metrics.append(f"trades={summary.get('trade_count')}")
        if summary.get("win_rate") is not None:
            metrics.append(f"win_rate={summary.get('win_rate')}")
        if summary.get("avg_return_pct") is not None:
            metrics.append(f"avg_return_pct={summary.get('avg_return_pct')}")
        metric_text = f" ({', '.join(metrics)})" if metrics else ""
        lines.append(
            f"- {layer}: used={row.get('used')} status={facade._text(row.get('status'), '')} "
            f"effect={facade._text(row.get('effect'), '')}{metric_text}"
        )
    return lines


def news_usage_lines_clean(news: Dict[str, Any], *, facade: Any) -> List[str]:
    if not bool(news.get("available")):
        return ["- 뉴스 사용 trace: -"]
    query_targets = ", ".join(str(x) for x in facade._as_list(news.get("query_targets"))[:10]) or "-"
    return [
        f"- 검색/수집 대상: {query_targets}",
        f"- 사용 요약: {facade._text(news.get('human_summary'))}",
        f"- 시장 효과: {facade._text(news.get('market_effect'))}",
        f"- 플레이북 효과: {facade._text(news.get('playbook_effect'))}",
        f"- 스캐너 반영: {facade._text(news.get('scanner_guidance_effect'))}",
        f"- 모니터 반영: {facade._text(news.get('monitor_policy_effect'))}",
        f"- 근거 헤드라인 수: market={news.get('market_headline_count')}, candidate={news.get('candidate_headline_count')}",
        f"- query reasoning: {facade._text(news.get('news_query_reasoning'))}",
    ]
