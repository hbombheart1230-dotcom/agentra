"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/agent_pipeline_trace.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def _build_markdown_r4_impl(out, *, facade):
    commander = out.get('commander') if isinstance(out.get('commander'), dict) else {}
    strategist = out.get('strategist') if isinstance(out.get('strategist'), dict) else {}
    news_symbol_linkage = out.get('news_symbol_linkage') if isinstance(out.get('news_symbol_linkage'), dict) else {}
    scanner = out.get('scanner') if isinstance(out.get('scanner'), dict) else {}
    monitor = out.get('monitor') if isinstance(out.get('monitor'), dict) else {}
    supervisor = out.get('supervisor') if isinstance(out.get('supervisor'), dict) else {}
    executor = out.get('executor') if isinstance(out.get('executor'), dict) else {}
    reporter = out.get('reporter') if isinstance(out.get('reporter'), dict) else {}
    reasoning_trace = out.get('reasoning_trace') if isinstance(out.get('reasoning_trace'), dict) else {}
    reasoning_provenance = out.get('reasoning_provenance') if isinstance(out.get('reasoning_provenance'), dict) else {}
    lines: List[str] = []
    lines.append(f"# Agent Pipeline Trace ({out.get('run_id')})")
    lines.append('')
    lines.append(f"- day: **{out.get('day')}**")
    lines.append(f"- event_log_path: `{out.get('event_log_path')}`")
    lines.append(f"- evidence_log_path: `{out.get('evidence_log_path')}`")
    lines.append('')
    lines.append('## Commander')
    lines.append(f"- mode: **{commander.get('mode')}**")
    lines.append(f"- agents: `{facade.json.dumps(commander.get('agents') or [], ensure_ascii=False)}`")
    lines.append(f"- route_ts: `{commander.get('route_ts')}`")
    lines.append(f"- end_status: **{commander.get('end_status')}**")
    lines.append('')
    lines.append('## Strategist')
    lines.append(f"- news_source: **{strategist.get('news_source')}** headlines={facade._safe_int(strategist.get('news_total_headlines'), 0)} symbols={facade._safe_int(strategist.get('news_symbol_count'), 0)}")
    if strategist.get('news_query_targets'):
        lines.append(f"- news_query_targets: `{facade.json.dumps(strategist.get('news_query_targets') or [], ensure_ascii=False)}`")
    if strategist.get('news_query_reasoning'):
        lines.append(f"- news_query_reasoning: {strategist.get('news_query_reasoning')}")
    lines.append(f"- global_sentiment: score={facade._safe_float(strategist.get('global_sentiment_score'), 0.0):.4f} status={strategist.get('global_sentiment_status')} source={strategist.get('global_sentiment_source')}")
    if strategist.get('global_index_moves'):
        lines.append(f"- global_index_moves: `{facade.json.dumps(strategist.get('global_index_moves') or {}, ensure_ascii=False)}`")
    if strategist.get('fear_index'):
        lines.append(f"- fear_index: `{facade.json.dumps(strategist.get('fear_index') or {}, ensure_ascii=False)}`")
    if strategist.get('macro_stress_overlay'):
        overlay = strategist.get('macro_stress_overlay') or {}
        lines.append(f"- macro_stress: active={bool(overlay.get('active'))} flags=`{facade.json.dumps(overlay.get('stress_flags') or [], ensure_ascii=False)}` reason=`{overlay.get('reason')}`")
    lines.append(f"- llm: provider={strategist.get('llm_provider')} model={strategist.get('llm_model')} ok={strategist.get('llm_ok')} latency_ms={strategist.get('llm_latency_ms')}")
    lines.append(f"- llm_prompt_captured: **{bool(strategist.get('llm_prompt'))}**")
    lines.append(f"- llm_response_captured: **{bool(strategist.get('llm_response'))}**")
    lines.append(f"- themes: `{facade.json.dumps(strategist.get('themes') or [], ensure_ascii=False)}`")
    lines.append(f"- playbook: **{strategist.get('playbook')}**")
    if strategist.get('scanner_source_policy'):
        lines.append(f"- scanner_source_policy: `{facade.json.dumps(strategist.get('scanner_source_policy') or {}, ensure_ascii=False)}`")
    if strategist.get('news_sample_titles'):
        lines.append(f"- news_sample_titles: `{facade.json.dumps(strategist.get('news_sample_titles') or [], ensure_ascii=False)}`")
    directives = strategist.get('strategy_adjustment_directives') if isinstance(strategist.get('strategy_adjustment_directives'), dict) else {}
    directives_summary = facade._format_strategist_directives_summary(directives)
    if directives:
        lines.append(f'- strategy_adjustment_directives: `{facade.json.dumps(directives, ensure_ascii=False)}`')
    if directives_summary:
        lines.append(f'- strategy_adjustment_summary: {directives_summary}')
    if strategist.get('memory_packet_visibility'):
        lines.append(f"- memory_packet_visibility: `{facade.json.dumps(strategist.get('memory_packet_visibility') or {}, ensure_ascii=False)}`")
    lines.append('')
    lines.append('## News -> Symbol Linkage')
    lines.append(f"- linkage_strength: **{news_symbol_linkage.get('linkage_strength') or 'unknown'}**")
    if news_symbol_linkage.get('summary'):
        lines.append(f"- summary: {news_symbol_linkage.get('summary')}")
    if news_symbol_linkage.get('candidate_symbols_hint'):
        lines.append(f"- candidate_symbols_hint: `{facade.json.dumps(news_symbol_linkage.get('candidate_symbols_hint') or [], ensure_ascii=False)}`")
    if news_symbol_linkage.get('news_query_targets'):
        lines.append(f"- linkage_news_query_targets: `{facade.json.dumps(news_symbol_linkage.get('news_query_targets') or [], ensure_ascii=False)}`")
    if news_symbol_linkage.get('selected_symbol'):
        lines.append(f"- selected_symbol_linkage: symbol={news_symbol_linkage.get('selected_symbol')} in_candidate_hints={bool(news_symbol_linkage.get('selected_symbol_in_candidate_hints'))}")
    if news_symbol_linkage.get('runner_up_symbol'):
        lines.append(f"- runner_up_symbol_linkage: symbol={news_symbol_linkage.get('runner_up_symbol')} in_candidate_hints={bool(news_symbol_linkage.get('runner_up_symbol_in_candidate_hints'))}")
    if news_symbol_linkage.get('selected_symbol_headlines'):
        lines.append(f"- selected_symbol_headlines: `{facade.json.dumps(news_symbol_linkage.get('selected_symbol_headlines') or [], ensure_ascii=False)}`")
    if news_symbol_linkage.get('runner_up_symbol_headlines'):
        lines.append(f"- runner_up_symbol_headlines: `{facade.json.dumps(news_symbol_linkage.get('runner_up_symbol_headlines') or [], ensure_ascii=False)}`")
    comparison = news_symbol_linkage.get('selected_vs_runner_up') if isinstance(news_symbol_linkage.get('selected_vs_runner_up'), dict) else {}
    if comparison.get('comparison_summary'):
        lines.append(f"- selected_vs_runner_up: {comparison.get('comparison_summary')}")
    if news_symbol_linkage.get('market_headlines'):
        lines.append(f"- linkage_market_headlines: `{facade.json.dumps(news_symbol_linkage.get('market_headlines') or [], ensure_ascii=False)}`")
    lines.append('')
    lines.append('## Scanner')
    lines.append(f"- candidate_source: **{scanner.get('candidate_source')}**")
    lines.append(f"- pool: before={facade._safe_int(scanner.get('candidate_pool_before_filter'), 0)} after={facade._safe_int(scanner.get('candidate_pool_after_filter'), 0)}")
    lines.append(f"- kiwoom_source_mix: `{facade.json.dumps(scanner.get('kiwoom_source_mix') or {}, ensure_ascii=False)}`")
    if scanner.get('condition_search_status') or scanner.get('condition_search_reason'):
        lines.append(f"- condition_search: status={scanner.get('condition_search_status')} source={scanner.get('condition_search_source')} reason={scanner.get('condition_search_reason')}")
    if scanner.get('scanner_source_policy'):
        lines.append(f"- scanner_source_policy: `{facade.json.dumps(scanner.get('scanner_source_policy') or {}, ensure_ascii=False)}`")
    lines.append(f"- top_stock: **{scanner.get('top_stock')}** top_score={scanner.get('top_score')}")
    lines.append(f"- top_ranked_symbols: `{facade.json.dumps(scanner.get('top_ranked_symbols') or [], ensure_ascii=False)}`")
    lines.append(f"- score_breakdown_summary: `{facade.json.dumps(scanner.get('score_breakdown_summary') or {}, ensure_ascii=False)}`")
    if scanner.get('selected_candidate'):
        lines.append(f"- selected_candidate: `{facade.json.dumps(scanner.get('selected_candidate') or {}, ensure_ascii=False)}`")
    lines.append('')
    lines.append('## Monitor')
    lines.append(f"- selected_symbol: **{monitor.get('selected_symbol')}**")
    lines.append(f"- entry_reason={monitor.get('entry_reason')} exit_reason={monitor.get('exit_reason')} monitor_reason={monitor.get('monitor_reason')}")
    lines.append(f"- position_age_seconds={monitor.get('position_age_seconds')} min_hold_blocked={monitor.get('min_hold_blocked')} sell_cooldown_blocked={monitor.get('sell_cooldown_blocked')}")
    lines.append(f"- thresholds: `{facade.json.dumps(monitor.get('thresholds') or {}, ensure_ascii=False)}` min_hold={facade._safe_int(monitor.get('min_hold_sec'), 0)} sell_cooldown={facade._safe_int(monitor.get('sell_cooldown_sec'), 0)} confirm_ticks={facade._safe_int(monitor.get('exit_confirm_ticks'), 0)}")
    if monitor.get('strategy_frame_adjustments'):
        lines.append(f"- strategy_frame_adjustments: `{facade.json.dumps(monitor.get('strategy_frame_adjustments') or [], ensure_ascii=False)}`")
    lines.append('')
    if reasoning_trace:
        lines.append('## Reasoning Trace')
        for key in ('commander_summary', 'strategist_summary', 'scanner_summary', 'monitor_summary'):
            row = reasoning_trace.get(key) if isinstance(reasoning_trace.get(key), dict) else {}
            if row:
                lines.append(f"- {key}: {row.get('summary') or '-'}")
        if reasoning_provenance:
            lines.append(f"- provenance: shadow_used={reasoning_provenance.get('shadow_used')} strategist_fallback_used={reasoning_provenance.get('strategist_fallback_used')}")
        lines.append('')
    lines.append('## Supervisor')
    lines.append(f"- verdict={supervisor.get('verdict')} allow={supervisor.get('supervisor_allow')} reason={supervisor.get('supervisor_reason') or supervisor.get('guard_reason')}")
    lines.append('')
    lines.append('## Executor')
    lines.append(f"- execution_attempted={executor.get('execution_attempted')} ok={executor.get('execution_ok')} broker_code={executor.get('broker_code')}")
    lines.append(f"- execution_mode={executor.get('execution_mode')} kiwoom_mode={executor.get('kiwoom_mode')} broker_env={executor.get('broker_env')} effective_mode={executor.get('effective_mode')}")
    lines.append(f"- api_id={executor.get('order_api_id')} url={executor.get('order_url')} action={executor.get('order_action')} symbol={executor.get('order_symbol')} qty={executor.get('order_qty')}")
    lines.append('')
    lines.append('## Reporter')
    lines.append(f"- in_run_trace_available: **{reporter.get('in_run_trace_available')}**")
    lines.append(f"- reporter_analysis_day_file_found: **{reporter.get('reporter_analysis_day_file_found')}**")
    lines.append(f"- reporter_analysis_found: **{reporter.get('reporter_analysis_found')}**")
    lines.append(f"- reporter_analysis_path: `{reporter.get('reporter_analysis_path')}`")
    lines.append('')
    lines.append('## Next Command')
    lines.append(f"- `python scripts/run_agent_pipeline_trace_report.py --run-id {out.get('run_id')} --json`")
    lines.append(f"- `python scripts/query_trade_reason_chain.py --run-id {out.get('run_id')} --only-broker-success`")
    return '\n'.join(lines)
