"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/post_exit_shadow_recap.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def _render_daily_recap_markdown_r4_impl(recap, *, facade):
    summary = facade._as_dict(recap.get('summary'))
    lines = [f"# 매도 후 가격 추적 일괄 Recap ({recap.get('day')})", '', '- 기준: stage4 closeout review와 16:00 closeout에서 당일 매도 후 가격 추적을 일괄 갱신합니다.', '- 적용: 기존 ai_trade_report 본문은 수정하지 않고 recap과 ai_trade_summary 산출물만 갱신합니다.', f"- 총 대상: {summary.get('total', 0)}건", f"- 관측 완료: {summary.get('observed', 0)}건", f"- EOD 관측 완료: {summary.get('eod_observed', 0)}건", f"- 대기: {summary.get('pending', 0)}건", '', '| 거래 | 상태 | +5m | +15m | +30m | +60m | EOD | 최선 지점 | 최대 상승 |', '| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |']
    for trade in facade._as_list(recap.get('trades')):
        if not isinstance(trade, dict):
            continue
        checkpoints = facade._as_dict(trade.get('checkpoints'))
        returns = []
        for label in facade.CHECKPOINT_LABELS:
            row = facade._as_dict(checkpoints.get(label))
            returns.append(facade._pct(row.get('return_pct')) if row.get('status') == 'observed' else '-')
        lines.append(f"| {trade.get('label')} | {trade.get('price_observation_status')} | {returns[0]} | {returns[1]} | {returns[2]} | {returns[3]} | {returns[4]} | {trade.get('best_exit_offset') or '-'} | {facade._pct(trade.get('max_post_exit_upside_pct'))} |")
    return '\n'.join(lines) + '\n'
