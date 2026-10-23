"""Pure already-loaded UI projections; effectful calls remain in core."""
from __future__ import annotations

def project_run_inputs(all_rows, evidence_rows, *, facade):
    route_row = next((r for r in all_rows if str(r.get('stage') or '') == 'commander_router' and str(r.get('event') or '') == 'route'), {})
    end_row = next((r for r in reversed(all_rows) if str(r.get('stage') or '') == 'commander_router' and str(r.get('event') or '') == 'end'), {})
    strategist_summary = next((r.get('payload') for r in reversed(all_rows) if str(r.get('stage') or '') == 'strategist' and str(r.get('event') or '') == 'summary' and isinstance(r.get('payload'), dict)), {})
    strategist_llm = next((r.get('payload') for r in reversed(all_rows) if str(r.get('stage') or '') == 'strategist_llm' and str(r.get('event') or '') == 'result' and isinstance(r.get('payload'), dict)), {})
    scanner_summary = next((r.get('payload') for r in reversed(all_rows) if str(r.get('stage') or '') == 'scanner' and str(r.get('event') or '') == 'summary' and isinstance(r.get('payload'), dict)), {})
    monitor_summary = next((r.get('payload') for r in reversed(all_rows) if str(r.get('stage') or '') == 'monitor' and str(r.get('event') or '') == 'summary' and isinstance(r.get('payload'), dict)), {})
    verdict_payload = next((r.get('payload') for r in reversed(all_rows) if str(r.get('stage') or '') == 'execute_from_packet' and str(r.get('event') or '') == 'verdict' and isinstance(r.get('payload'), dict)), {})
    execution_payload = next((r.get('payload') for r in reversed(all_rows) if str(r.get('stage') or '') == 'execute_from_packet' and str(r.get('event') or '') == 'execution' and isinstance(r.get('payload'), dict)), {})
    portfolio_sync = facade._build_portfolio_sync_card(facade._extract_portfolio_guard_payload_from_run_rows(all_rows))
    strategic_frame = next(((r.get('payload') or {}).get('payload') for r in reversed(all_rows) if str(r.get('stage') or '') == 'decision_trace' and str(r.get('event') or '') == 'strategic_frame' and isinstance(r.get('payload'), dict) and (str((r.get('payload') or {}).get('agent') or '') == 'strategist')), {})
    candidate_selection = next(((r.get('payload') or {}).get('payload') for r in reversed(all_rows) if str(r.get('stage') or '') == 'decision_trace' and str(r.get('event') or '') == 'candidate_selection' and isinstance(r.get('payload'), dict) and (str((r.get('payload') or {}).get('agent') or '') == 'scanner')), {})
    entry_exit_decision = next(((r.get('payload') or {}).get('payload') for r in reversed(all_rows) if str(r.get('stage') or '') == 'decision_trace' and str(r.get('event') or '') == 'entry_exit_decision' and isinstance(r.get('payload'), dict) and (str((r.get('payload') or {}).get('agent') or '') == 'monitor')), {})
    selected_candidate = candidate_selection.get('selected_candidate') if isinstance(candidate_selection.get('selected_candidate'), dict) else {}
    feature_snapshot = selected_candidate.get('feature_snapshot') if isinstance(selected_candidate.get('feature_snapshot'), dict) else {}
    feature_coverage = facade._feature_coverage(feature_snapshot)
    quote_metrics = facade._quote_metrics_snapshot(feature_snapshot)
    strategist_evidence = facade._latest_evidence(evidence_rows, agent='strategist', stage='theme_selection')
    reporter_evidence = facade._latest_evidence(evidence_rows, agent='reporter', stage='post_run_analysis')
    first_dt = facade._to_datetime(all_rows[0].get('ts'))
    run_day = first_dt.strftime('%Y-%m-%d') if first_dt else ''
    return (route_row, end_row, strategist_summary, strategist_llm, scanner_summary, monitor_summary, verdict_payload, execution_payload, portfolio_sync, strategic_frame, candidate_selection, entry_exit_decision, feature_coverage, quote_metrics, strategist_evidence, run_day)
