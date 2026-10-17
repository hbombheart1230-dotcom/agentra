"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/reporter_analysis.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def _to_markdown_r4_impl(out, *, facade):
    day = str(out.get('day') or '')
    trade_section = out.get('trade_decision_summaries') if isinstance(out.get('trade_decision_summaries'), dict) else {}
    flow = out.get('intent_flow_analysis') if isinstance(out.get('intent_flow_analysis'), dict) else {}
    eff = out.get('strategy_effectiveness') if isinstance(out.get('strategy_effectiveness'), dict) else {}
    over = out.get('overtrading_diagnostics') if isinstance(out.get('overtrading_diagnostics'), dict) else {}
    market = out.get('market_context') if isinstance(out.get('market_context'), dict) else {}
    incidents = out.get('incident_postmortem') if isinstance(out.get('incident_postmortem'), dict) else {}
    operator = out.get('daily_operator_report') if isinstance(out.get('daily_operator_report'), dict) else {}
    trade_summary = out.get('trade_summary') if isinstance(out.get('trade_summary'), dict) else {}
    decision_chains = out.get('decision_chains') if isinstance(out.get('decision_chains'), dict) else {}
    trace_summary = out.get('decision_trace_chain_summary') if isinstance(out.get('decision_trace_chain_summary'), dict) else {}
    strategist_eval = out.get('strategist_evaluation') if isinstance(out.get('strategist_evaluation'), dict) else {}
    scanner_eval = out.get('scanner_evaluation') if isinstance(out.get('scanner_evaluation'), dict) else {}
    monitor_eval = out.get('monitor_evaluation') if isinstance(out.get('monitor_evaluation'), dict) else {}
    supervisor_activity = out.get('supervisor_activity') if isinstance(out.get('supervisor_activity'), dict) else {}
    improvement = out.get('improvement_suggestions') if isinstance(out.get('improvement_suggestions'), list) else []
    report_focus_targets = out.get('report_focus_targets') if isinstance(out.get('report_focus_targets'), list) else []
    operator_view = out.get('operator_facing_summary') if isinstance(out.get('operator_facing_summary'), dict) else {}
    developer_view = out.get('developer_facing_summary') if isinstance(out.get('developer_facing_summary'), dict) else {}
    ai_review = out.get('ai_review') if isinstance(out.get('ai_review'), dict) else {}
    lines: List[str] = []
    lines.append(f'# Reporter Analysis ({day})')
    lines.append('')
    lines.append('## Daily Operator Report')
    lines.append('')
    lines.append(f"- system_health: **{operator_view.get('system_health') or 'UNKNOWN'}**")
    for txt in (operator_view.get('summary_lines') or [])[:4]:
        lines.append(f'- {txt}')
    lines.append(f"- recommended_actions: `{facade.json.dumps(operator_view.get('recommended_actions') or [], ensure_ascii=False)}`")
    lines.append('')
    lines.append(f'- market_context: `{facade.json.dumps(market, ensure_ascii=False)}`')
    lines.append(f"- trades_executed: **{facade._safe_int(operator.get('trades_executed'), 0)}**")
    lines.append(f"- trades_blocked: **{facade._safe_int(operator.get('trades_blocked'), 0)}**")
    lines.append(f"- major_decisions: `{facade.json.dumps(operator.get('major_decisions') or [], ensure_ascii=False)}`")
    lines.append(f"- anomalies: `{facade.json.dumps(operator.get('anomalies') or [], ensure_ascii=False)}`")
    lines.append('')
    lines.append('## Trade Decision Summaries')
    lines.append('')
    lines.append(f"- trade_summary_total: **{facade._safe_int(trade_section.get('trade_summary_total'), 0)}**")
    lines.append('| symbol | buy_reason | sell_reason | holding_duration_sec | exit_trigger |')
    lines.append('| --- | --- | --- | ---: | --- |')
    for row in (trade_section.get('trade_summaries') or [])[:40]:
        if not isinstance(row, dict):
            continue
        lines.append(f"| {row.get('symbol') or '-'} | {row.get('buy_reason') or '-'} | {row.get('sell_reason') or '-'} | {facade._safe_int(row.get('holding_duration_sec'), 0)} | {row.get('exit_trigger') or '-'} |")
    lines.append('')
    lines.append('## Trade Summary')
    lines.append('')
    lines.append(f"- trade_count: **{facade._safe_int(trade_summary.get('trade_count'), 0)}**")
    lines.append(f"- symbols_traded: `{facade.json.dumps(trade_summary.get('symbols_traded') or [], ensure_ascii=False)}`")
    lines.append('')
    lines.append('## Decision Chains')
    lines.append('')
    lines.append(f"- run_total: **{facade._safe_int(decision_chains.get('run_total'), 0)}**")
    lines.append(f"- rendered_run_total: **{facade._safe_int(decision_chains.get('rendered_run_total'), 0)}**")
    for chain in (decision_chains.get('chains') or [])[:10]:
        if not isinstance(chain, dict):
            continue
        lines.append(f"- run_id={chain.get('run_id')} symbol={chain.get('symbol') or '-'} action={chain.get('action') or '-'} supervisor={chain.get('supervisor_verdict') or '-'} execution={chain.get('execution_status') or '-'} buy_reason={chain.get('buy_reason') or '-'} sell_reason={chain.get('sell_reason') or '-'}")
    lines.append('')
    lines.append('## Decision Trace Chain Summary')
    lines.append('')
    lines.append(f"- run_total: **{facade._safe_int(trace_summary.get('run_total'), 0)}**")
    lines.append(f"- complete_chain_total: **{facade._safe_int(trace_summary.get('complete_chain_total'), 0)}**")
    for chain in (trace_summary.get('chains') or [])[:10]:
        if not isinstance(chain, dict):
            continue
        scanner = chain.get('scanner') if isinstance(chain.get('scanner'), dict) else {}
        monitor = chain.get('monitor') if isinstance(chain.get('monitor'), dict) else {}
        supervisor = chain.get('supervisor') if isinstance(chain.get('supervisor'), dict) else {}
        executor = chain.get('executor') if isinstance(chain.get('executor'), dict) else {}
        lines.append(f"- run_id={chain.get('run_id')} selected={scanner.get('selected_symbol') or '-'} monitor={monitor.get('monitor_reason') or '-'} supervisor={supervisor.get('verdict') or '-'} executor={executor.get('fill_status_summary') or '-'} complete={bool(chain.get('complete_chain'))}")
    lines.append('')
    lines.append('## Strategist Evaluation')
    lines.append('')
    lines.append(f"- themes_proposed: `{facade.json.dumps(strategist_eval.get('themes_proposed') or [], ensure_ascii=False)}`")
    lines.append(f"- actual_market_leaders_by_scanner: `{facade.json.dumps(strategist_eval.get('actual_market_leaders_by_scanner') or [], ensure_ascii=False)}`")
    lines.append(f"- theme_alignment_status: **{strategist_eval.get('theme_alignment_status') or 'unknown'}**")
    lines.append(f"- assessment: {strategist_eval.get('assessment') or '-'}")
    lines.append('')
    lines.append('## Scanner Evaluation')
    lines.append('')
    lines.append(f"- scanner_summary_total: **{facade._safe_int(scanner_eval.get('scanner_summary_total'), 0)}**")
    lines.append(f"- selected_symbol_top: `{facade.json.dumps(scanner_eval.get('selected_symbol_top') or {}, ensure_ascii=False)}`")
    lines.append(f"- no_candidate_total: **{facade._safe_int(scanner_eval.get('no_candidate_total'), 0)}**")
    if scanner_eval.get('avg_top_score') is not None:
        lines.append(f"- avg_top_score: **{facade._safe_float(scanner_eval.get('avg_top_score'), 0.0):.4f}**")
    lines.append(f"- selection_status: **{scanner_eval.get('selection_status') or 'unknown'}**")
    lines.append(f"- assessment: {scanner_eval.get('assessment') or '-'}")
    lines.append('')
    lines.append('## Monitor Evaluation')
    lines.append('')
    lines.append(f"- monitor_summary_total: **{facade._safe_int(monitor_eval.get('monitor_summary_total'), 0)}**")
    lines.append(f"- monitor_reason_top: `{facade.json.dumps(monitor_eval.get('monitor_reason_top') or {}, ensure_ascii=False)}`")
    lines.append(f"- rapid_buy_sell_cycles: **{facade._safe_int(monitor_eval.get('rapid_buy_sell_cycles'), 0)}**")
    lines.append(f"- monitor_status: **{monitor_eval.get('monitor_status') or 'unknown'}**")
    lines.append(f"- assessment: {monitor_eval.get('assessment') or '-'}")
    lines.append('')
    lines.append('## Supervisor Activity')
    lines.append('')
    lines.append(f"- verdict_total: **{facade._safe_int(supervisor_activity.get('verdict_total'), 0)}**")
    lines.append(f"- approved_total: **{facade._safe_int(supervisor_activity.get('approved_total'), 0)}**")
    lines.append(f"- blocked_total: **{facade._safe_int(supervisor_activity.get('blocked_total'), 0)}**")
    lines.append(f"- blocked_rate: **{facade._safe_float(supervisor_activity.get('blocked_rate'), 0.0):.2%}**")
    lines.append(f"- blocked_reason_top: `{facade.json.dumps(supervisor_activity.get('blocked_reason_top') or {}, ensure_ascii=False)}`")
    lines.append(f"- assessment: {supervisor_activity.get('assessment') or '-'}")
    lines.append('')
    lines.append('## Intent Flow Analysis')
    lines.append('')
    lines.append(f"- intents_created: **{facade._safe_int(flow.get('intents_created'), 0)}**")
    lines.append(f"- intents_blocked: **{facade._safe_int(flow.get('intents_blocked'), 0)}**")
    lines.append(f"- intents_approved: **{facade._safe_int(flow.get('intents_approved'), 0)}**")
    lines.append(f"- intents_executed: **{facade._safe_int(flow.get('intents_executed'), 0)}**")
    lines.append(f"- reason_top: `{facade.json.dumps(flow.get('reason_top') or {}, ensure_ascii=False)}`")
    lines.append('')
    lines.append('## Strategy Effectiveness')
    lines.append('')
    for text in eff.get('narrative') or []:
        lines.append(f'- {text}')
    lines.append('')
    lines.append('## Overtrading Diagnostics')
    lines.append('')
    lines.append(f"- rapid_buy_sell_cycles(<{facade._safe_int(over.get('rapid_threshold_sec'), 0)}s): **{facade._safe_int(over.get('rapid_buy_sell_cycles'), 0)}**")
    lines.append(f"- noise_exit_related_count: **{facade._safe_int(over.get('noise_exit_related_count'), 0)}**")
    lines.append(f"- frequent_guard_block_count: **{facade._safe_int(over.get('frequent_guard_block_count'), 0)}**")
    lines.append(f"- guard_block_rate: **{facade._safe_float(over.get('guard_block_rate'), 0.0):.2%}**")
    lines.append('')
    lines.append('## Incident / Post-Mortem Support')
    lines.append('')
    lines.append(f"- incident_total: **{facade._safe_int(incidents.get('incident_total'), 0)}**")
    for item in incidents.get('incidents') or []:
        if not isinstance(item, dict):
            continue
        lines.append(f"- [{item.get('severity')}] {item.get('type')}: {item.get('detail')}")
    lines.append('')
    lines.append('## Improvement Suggestions')
    lines.append('')
    lines.append(f'- report_focus_targets: `{facade.json.dumps(report_focus_targets, ensure_ascii=False)}`')
    for item in improvement[:8]:
        lines.append(f'- {item}')
    lines.append('')
    lines.append('## AI Review (Passive Optional Layer)')
    lines.append('')
    lines.append(f"- ai_review_status: **{ai_review.get('status') or 'disabled'}**")
    if ai_review.get('model'):
        lines.append(f"- ai_review_model: `{ai_review.get('model')}`")
    if ai_review.get('reason'):
        lines.append(f"- ai_review_reason: {ai_review.get('reason')}")
    if ai_review.get('fallback_enriched') is True:
        lines.append('- ai_review_fallback_enriched: true')
    lines.append(f"- ai_run_grade: **{out.get('ai_run_grade') or 'N/A'}**")
    if out.get('ai_summary'):
        lines.append(f"- ai_summary: {out.get('ai_summary')}")
    lines.append(f"- ai_findings: `{facade.json.dumps(out.get('ai_findings') or [], ensure_ascii=False)}`")
    lines.append(f"- ai_root_causes: `{facade.json.dumps(out.get('ai_root_causes') or [], ensure_ascii=False)}`")
    lines.append(f"- ai_improvement_suggestions: `{facade.json.dumps(out.get('ai_improvement_suggestions') or [], ensure_ascii=False)}`")
    lines.append(f"- ai_agent_evaluations: `{facade.json.dumps(out.get('ai_agent_evaluations') or {}, ensure_ascii=False)}`")
    ai_findings_detailed = out.get('ai_findings_detailed') if isinstance(out.get('ai_findings_detailed'), list) else []
    ai_root_causes_detailed = out.get('ai_root_causes_detailed') if isinstance(out.get('ai_root_causes_detailed'), list) else []
    ai_improvement_detailed = out.get('ai_improvement_suggestions_detailed') if isinstance(out.get('ai_improvement_suggestions_detailed'), list) else []
    if ai_findings_detailed:
        lines.append('- ai_findings_detailed:')
        for item in ai_findings_detailed[:6]:
            if not isinstance(item, dict):
                continue
            lines.append(f"  - text: {item.get('text')}")
            lines.append(f"    evidence_keys: `{facade.json.dumps(item.get('evidence_keys') or [], ensure_ascii=False)}`")
    if ai_root_causes_detailed:
        lines.append('- ai_root_causes_detailed:')
        for item in ai_root_causes_detailed[:6]:
            if not isinstance(item, dict):
                continue
            lines.append(f"  - text: {item.get('text')}")
            lines.append(f"    evidence_keys: `{facade.json.dumps(item.get('evidence_keys') or [], ensure_ascii=False)}`")
    if ai_improvement_detailed:
        lines.append('- ai_improvement_suggestions_detailed:')
        for item in ai_improvement_detailed[:6]:
            if not isinstance(item, dict):
                continue
            lines.append(f"  - text: {item.get('text')}")
            lines.append(f"    evidence_keys: `{facade.json.dumps(item.get('evidence_keys') or [], ensure_ascii=False)}`")
    lines.append('')
    lines.append('## Developer Summary')
    lines.append('')
    for txt in (developer_view.get('summary_lines') or [])[:8]:
        lines.append(f'- {txt}')
    lines.append(f"- blocked_reason_top: `{facade.json.dumps(developer_view.get('blocked_reason_top') or {}, ensure_ascii=False)}`")
    lines.append(f"- monitor_reason_top: `{facade.json.dumps(developer_view.get('monitor_reason_top') or {}, ensure_ascii=False)}`")
    lines.append('')
    lines.append('## Source Artifacts')
    lines.append('')
    refs = out.get('source_reports') if isinstance(out.get('source_reports'), dict) else {}
    for k, v in refs.items():
        lines.append(f'- {k}: `{v}`')
    lines.append('')
    return '\n'.join(lines)
