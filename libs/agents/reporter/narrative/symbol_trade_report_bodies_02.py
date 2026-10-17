"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/symbol_trade_report.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def build_symbol_memory_payload_r4_impl(payload, *, facade):
    normalized_symbol = str(payload.get('symbol') or '').strip().upper()
    summary = payload.get('summary') if isinstance(payload.get('summary'), dict) else {}
    pattern_insights = payload.get('pattern_insights') if isinstance(payload.get('pattern_insights'), dict) else {}
    history = payload.get('history_index') if isinstance(payload.get('history_index'), list) else []
    trade_count = facade._safe_int(summary.get('trade_count'))
    completed_trade_count = facade._safe_int(summary.get('completed_trade_count'))
    win_count = facade._safe_int(summary.get('win_count'))
    avg_return_pct = facade._safe_float(summary.get('avg_return_pct')) or 0.0
    avg_hold_seconds = facade._safe_float(summary.get('avg_hold_seconds')) or 0.0
    repeated_blockers = facade._list_text(pattern_insights.get('common_monitor_failures'), limit=5)
    playbook_stats = facade._derive_playbook_stats(history)
    latest_trade = dict(history[-1]) if history else {}
    dominant_wait_reason = ''
    wait_distribution = summary.get('wait_reason_distribution') if isinstance(summary.get('wait_reason_distribution'), dict) else {}
    if wait_distribution:
        dominant_wait_reason = str(max(wait_distribution.items(), key=lambda item: float(item[1] or 0))[0])
    memory = {'schema_version': 'symbol_memory.v1', 'symbol': normalized_symbol, 'window_label': 'rolling_recent', 'trade_stats': {'trade_count': trade_count, 'completed_trade_count': completed_trade_count, 'win_rate': round(facade._ratio(float(win_count), float(completed_trade_count)), 4), 'avg_return_pct': round(avg_return_pct, 4), 'avg_hold_seconds': round(avg_hold_seconds, 2)}, 'playbook_stats': playbook_stats, 'pattern_stats': {'successful_entry_patterns': list(pattern_insights.get('successful_entry_patterns') or []), 'failed_entry_patterns': list(pattern_insights.get('failed_entry_patterns') or []), 'common_monitor_failures': repeated_blockers, 'recent_entry_pattern_types': list(pattern_insights.get('recent_entry_pattern_types') or []), 'recent_exit_pattern_types': list(pattern_insights.get('recent_exit_pattern_types') or [])}, 'execution_risk': {'spread_bps_p50': None, 'spread_bps_p90': None, 'slippage_bps_p50': None, 'execution_risk_level': 'not_available'}, 'monitor_patterns': {'repeated_blockers': repeated_blockers, 'dominant_wait_reason': dominant_wait_reason, 'dominant_exit_failure_axis': facade._derive_dominant_exit_failure_axis(history), 'hold_refresh_count': 0, 'hold_refresh_effective_count': 0, 'hold_refresh_effective_rate': 0.0}, 'bias_recommendation': facade._derive_bias_recommendation(avg_return_pct=avg_return_pct, playbook_stats=playbook_stats, repeated_blockers=repeated_blockers), 'latest_snapshot': {'last_trade_id': str(latest_trade.get('trade_id') or ''), 'last_trade_date': str(latest_trade.get('date') or ''), 'last_status': str(latest_trade.get('last_status') or latest_trade.get('status') or '')}}
    return memory


def _render_symbol_trade_markdown_r4_impl(payload, *, facade):
    symbol = str(payload.get('symbol') or '')
    summary = payload.get('summary') if isinstance(payload.get('summary'), dict) else {}
    insights = payload.get('pattern_insights') if isinstance(payload.get('pattern_insights'), dict) else {}
    history = payload.get('history_index') if isinstance(payload.get('history_index'), list) else []
    lines = [f'# 심볼 거래 리포트 ({symbol})', '', '## 요약', '', f"- 누적 거래 수: **{facade._safe_int(summary.get('trade_count'))}**", f"- 완료 거래 수: **{facade._safe_int(summary.get('completed_trade_count'))}**", f"- 승리/손실: **{facade._safe_int(summary.get('win_count'))} / {facade._safe_int(summary.get('loss_count'))}**", f"- 평균 수익률: **{float(summary.get('avg_return_pct') or 0.0):.2f}%**", f"- 평균 보유 시간: **{float(summary.get('avg_hold_seconds') or 0.0):.0f}초**", '', '## 최근 관찰 포인트', '', f"- 최근 playbook: {', '.join(summary.get('recent_playbooks') or []) or '없음'}", f"- 최근 진입 사유: {', '.join(summary.get('recent_entry_reasons') or []) or '없음'}", f"- 최근 청산 사유: {', '.join(summary.get('recent_exit_reasons') or []) or '없음'}", f"- 최근 WAIT 사유: {', '.join(summary.get('recent_wait_reasons') or []) or '없음'}", f"- recent trade headlines: {', '.join(summary.get('recent_trade_headlines') or []) or 'none'}", f"- recent operator viewpoints: {', '.join(summary.get('recent_operator_viewpoints') or []) or 'none'}", '', '## 패턴 인사이트', '', f"- 성과가 좋았던 진입 패턴: {', '.join(insights.get('successful_entry_patterns') or []) or '없음'}", f"- 성과가 약했던 진입 패턴: {', '.join(insights.get('failed_entry_patterns') or []) or '없음'}", f"- 자주 반복된 모니터 실패 축: {', '.join(insights.get('common_monitor_failures') or []) or '없음'}", f"- recent entry pattern types: {', '.join(insights.get('recent_entry_pattern_types') or []) or 'none'}", f"- recent exit pattern types: {', '.join(insights.get('recent_exit_pattern_types') or []) or 'none'}", f"- recent improvement tags: {', '.join(insights.get('recent_improvement_tags') or []) or 'none'}", f"- recent review flags: {', '.join(insights.get('recent_review_flags') or []) or 'none'}"]
    risk_notes = list(insights.get('risk_notes') or [])
    if risk_notes:
        lines.extend(['', '## 리스크 메모', ''])
        for note in risk_notes:
            lines.append(f'- {note}')
    lines.extend(['', '## 거래 이력', ''])
    if not history:
        lines.append('- 저장된 거래 이력이 없습니다.')
    else:
        for row in history[-20:]:
            result_pct = facade._safe_float(row.get('result_pct'))
            result_text = f'{result_pct:.2f}%' if result_pct is not None else '미기록'
            lines.append(f"- {row.get('date')}: {row.get('trade_id')} / 상태 {row.get('status')} / 진입 {row.get('entry_reason') or '미기록'} / 청산 {row.get('exit_reason') or '미기록'} / 결과 {result_text}")
    lines.append('')
    return '\n'.join(lines)
