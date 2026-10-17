"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/trade_explain.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def _latest_day_r4_impl(path, *, facade):
    best: Optional[str] = None
    for row in facade._iter_jsonl(path):
        d = facade._utc_day(row.get('ts'))
        if not d:
            continue
        if best is None or d > best:
            best = d
    return best


def _canonical_report_root_r4_impl(report_dir, *, facade):
    for candidate in (report_dir, *report_dir.parents):
        if candidate.name == 'reports':
            return candidate
    if report_dir.name in {'trade_explain', 'daily', 'metrics', 'run_cards', 'decision_story', 'operator_summary'}:
        return report_dir.parent
    return report_dir


def _to_markdown_r4_impl(*, day, event_log_path, route_summary, freshness, data_freshness, route_provenance, output_path_policy, execution_summary, agent_activity, sell_pairs, executions, report_inventory, no_trade_summary, data_gaps, facade):
    lines: List[str] = []
    lines.append(f'# Trade Explain Report ({day})')
    lines.append('')
    lines.append(f'- event_log_path: `{event_log_path}`')
    lines.append(f'- narrative_policy: exit-first for SELL/EXIT, entry-first for BUY/WAIT/NO_TRADE')
    lines.append('')
    lines += facade.render_data_freshness_markdown(data_freshness)
    lines += ['', '## Output Path Policy', '', f"- official_report_dir: `{output_path_policy.get('official_report_dir') or ''}`", f"- requested_report_dir: `{output_path_policy.get('requested_report_dir') or ''}`", f"- path_status: `{output_path_policy.get('path_status') or 'unknown'}`", f"- note: {output_path_policy.get('deprecated_note') or 'requested path is canonical'}", '', '## Route Provenance', '', f"- route_source: `{route_provenance.get('route_source') or 'unavailable'}`", f"- route_source_run_count: **{int(route_provenance.get('route_source_run_count') or 0)}**", f"- route_source_missing_count: **{int(route_provenance.get('route_source_missing_count') or 0)}**", f"- route_source_breakdown: `{route_provenance.get('route_source_breakdown') or {}}`", '']
    lines.append('## Executive Summary')
    lines.append('')
    lines.append(f"- executions_total: **{int(execution_summary.get('executions_total') or 0)}**")
    lines.append(f"- sell_pairs_total: **{int(execution_summary.get('sell_pairs_total') or 0)}**")
    lines.append(f"- symbols_executed: `{execution_summary.get('symbols_executed') or []}`")
    lines.append(f"- action_counts: `{execution_summary.get('action_counts') or {}}`")
    lines.append(f"- symbol_side_counts: `{execution_summary.get('symbol_side_counts') or {}}`")
    lines.append(f"- short_holds_lt_120s: **{int(execution_summary.get('short_holds_lt_120s') or 0)}**")
    lines.append('')
    lines.append('## Route Summary')
    lines.append('')
    lines.append(f"- route_source: `{route_summary.get('route_source') or 'unavailable'}`")
    lines.append(f"- route_source_run_count: **{int(route_summary.get('route_source_run_count') or 0)}**")
    lines.append(f"- route_source_missing_count: **{int(route_summary.get('route_source_missing_count') or 0)}**")
    lines.append(f"- route_source_breakdown: `{route_summary.get('route_source_breakdown') or {}}`")
    lines.append(f"- route_selected_total: `{route_summary.get('route_selected_total') or {}}`")
    lines.append(f"- strategy_generation_mode_total: `{route_summary.get('strategy_generation_mode_total') or {}}`")
    lines.append('')
    lines.append('## Agent Activity Snapshot')
    lines.append('')
    stage_counts = agent_activity.get('stage_counts') if isinstance(agent_activity.get('stage_counts'), dict) else {}
    for stage, cnt in stage_counts.items():
        lines.append(f'- `{stage}`: {int(cnt)}')
    lines.append('')
    lines.append('## Report Inventory')
    lines.append('')
    if report_inventory:
        for path in report_inventory:
            lines.append(f'- `{path}`')
    else:
        lines.append('- none')
    lines.append('')
    lines.append('## No-Trade Summary')
    lines.append('')
    lines.append(f"- no_trade_runs_total: **{int(no_trade_summary.get('no_trade_runs_total') or 0)}**")
    lines.append(f"- near_ready_runs_total: **{int(no_trade_summary.get('near_ready_runs_total') or 0)}**")
    lines.append(f"- strategist_fallback_total: **{int(no_trade_summary.get('strategist_fallback_total') or 0)}**")
    lines.append(f"- route_selected_total: `{no_trade_summary.get('route_selected_total') or {}}`")
    lines.append(f"- scanner_monitor_mismatch_total: **{int(no_trade_summary.get('scanner_monitor_mismatch_total') or 0)}**")
    lines.append(f"- dominant_blocker_topN: `{no_trade_summary.get('dominant_blocker_topN') or []}`")
    lines.append('')
    lines.append('## Execution Timeline (Latest)')
    lines.append('')
    if not executions:
        lines.append('No execution rows found.')
    else:
        lines.append('| ts | run_id | symbol | action | qty | price | strategy | reason |')
        lines.append('| --- | --- | --- | --- | ---: | ---: | --- | --- |')
        for row in executions:
            lines.append('| {ts} | `{run_id}` | {symbol} | {action} | {qty} | {price} | {strategy} | {reason} |'.format(ts=str(row.get('ts') or ''), run_id=str(row.get('run_id') or ''), symbol=str(row.get('symbol') or ''), action=str(row.get('action') or ''), qty=int(facade._safe_int(row.get('qty'), 0)), price=round(facade._safe_float(row.get('price'), 0.0), 4), strategy=str(row.get('strategy') or '-'), reason=str(row.get('primary_explanation') or '-')))
    lines.append('')
    lines.append('## Sell Pair Analysis (FIFO, Latest)')
    lines.append('')
    if not sell_pairs:
        lines.append('No SELL pairs found.')
    else:
        for pair in sell_pairs:
            lines.append(f"### SELL `{pair.get('sell_run_id')}` / {pair.get('symbol')}")
            lines.append(f"- sell_ts: {pair.get('sell_ts')}")
            lines.append(f"- qty: sell={int(pair.get('sell_qty') or 0)}, matched={int(pair.get('matched_qty') or 0)}, unmatched={int(pair.get('unmatched_qty') or 0)}")
            lines.append(f"- hold_duration_sec_avg: **{int(pair.get('hold_duration_sec_avg') or 0)}** / estimated_realized_pnl: **{round(facade._safe_float(pair.get('estimated_realized_pnl'), 0.0), 4)}**")
            lines.append(f"- entry_vs_exit_price: entry_avg={round(facade._safe_float(pair.get('avg_entry_price'), 0.0), 4)}, exit={round(facade._safe_float(pair.get('sell_price'), 0.0), 4)}")
            lines.append(f"- decision_axis: {pair.get('decision_axis') or '-'}")
            lines.append(f"- primary_explanation: {pair.get('primary_explanation') or '-'}")
            lines.append(f"- narrative_order: {pair.get('narrative_order_text') or '-'}")
            lines.append(f"- narrative_consistency_flag: {bool(pair.get('narrative_consistency_flag'))}")
            lines.append(f"- strategy: {pair.get('strategy') or '-'}")
            lines.append(f"- sell_reason: {pair.get('decision_rationale') or pair.get('decision_reason') or '-'}")
            lines.append(f"- entry_narrative: {pair.get('entry_narrative') or '-'}")
            lines.append(f"- exit_narrative: {pair.get('exit_narrative') or '-'}")
            lines.append(f"- entry_context_blocker: {pair.get('entry_context_blocker') or '-'}")
            lines.append(f"- scanner_context: source={pair.get('scanner_source') or '-'}, top_stock={pair.get('scanner_top_stock') or '-'}, top_score={pair.get('scanner_top_score')}")
            lines.append(f"- commander_route: route={pair.get('route_selected') or '-'}, source={pair.get('route_source') or 'unavailable'}, strategist_mode={pair.get('strategist_mode') or '-'}")
            lines.append(f"- sentiment_context: symbol={pair.get('news_symbol_sentiment_score')}, global={pair.get('news_global_sentiment_score')}, status=({pair.get('news_symbol_status') or '-'}, {pair.get('news_global_status') or '-'})")
            lines.append(f"- technical_context: signal_score={pair.get('signal_score')}, rsi14={pair.get('rsi14')}, ma20_gap={pair.get('ma20_gap')}, volatility20={pair.get('volatility20')}, composite={pair.get('composite_score')}")
            lines.append(f"- monitor_context: exit_reason={pair.get('monitor_exit_reason') or '-'}, monitor_reason={pair.get('monitor_reason') or '-'}, price_source={pair.get('monitor_price_source') or '-'}, feature_source={pair.get('monitor_feature_source') or '-'}")
            if pair.get('monitor_price_source_policy'):
                lines.append(f"- monitor_price_policy: {pair.get('monitor_price_source_policy')}")
            lines.append(f"- matched_buy_runs: `{pair.get('matched_buy_run_ids') or []}`")
            lines.append('')
    lines.append('## Data Gaps')
    lines.append('')
    for k, v in data_gaps.items():
        lines.append(f'- {k}: {v}')
    return '\n'.join(lines).rstrip() + '\n'
