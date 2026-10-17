"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/reporter_analysis.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def _build_strategist_evaluation_r4_impl(day_rows, *, facade):
    theme_counts: facade.Counter[str] = facade.Counter()
    leader_symbol_counts: facade.Counter[str] = facade.Counter()
    theme_filter_applied_total = 0
    scanner_summary_total = 0
    for row in day_rows:
        stage = str(row.get('stage') or '').strip()
        event = str(row.get('event') or '').strip()
        payload = row.get('payload') if isinstance(row.get('payload'), dict) else {}
        if stage == 'strategist' and event == 'summary':
            for t in payload.get('themes') or []:
                s = str(t or '').strip().lower()
                if s:
                    theme_counts[s] += 1
        if stage == 'strategist_llm' and event == 'result':
            for key in ('themes', 'top_themes'):
                vals = payload.get(key)
                if isinstance(vals, list):
                    for t in vals:
                        s = str(t or '').strip().lower()
                        if s:
                            theme_counts[s] += 1
        if stage == 'scanner' and event == 'summary':
            scanner_summary_total += 1
            if bool(payload.get('theme_filter_applied')):
                theme_filter_applied_total += 1
            top = facade._normalize_live_symbol(payload.get('top_stock'))
            if top:
                leader_symbol_counts[top] += 1
    themes = [k for k, _ in theme_counts.most_common(8)]
    leaders = [k for k, _ in leader_symbol_counts.most_common(8)]
    if not themes or scanner_summary_total <= 0:
        alignment = 'insufficient_data'
    elif theme_filter_applied_total > 0:
        alignment = 'aligned'
    else:
        alignment = 'partial'
    return {'themes_proposed': themes, 'actual_market_leaders_by_scanner': leaders, 'theme_filter_applied_total': int(theme_filter_applied_total), 'scanner_summary_total': int(scanner_summary_total), 'theme_alignment_status': alignment, 'assessment': 'Strategist themes were reflected in scanner filtering.' if alignment == 'aligned' else 'Theme guidance existed but scanner theme-filter evidence was limited.' if alignment == 'partial' else 'Insufficient strategist/scanner evidence to evaluate theme correctness.'}


def _build_scanner_evaluation_r4_impl(day_rows, *, facade):
    top_score_values: List[float] = []
    candidate_pool_values: List[int] = []
    top_stock_counts: facade.Counter[str] = facade.Counter()
    no_candidate_total = 0
    source_counts: facade.Counter[str] = facade.Counter()
    for row in day_rows:
        if str(row.get('stage') or '').strip() != 'scanner' or str(row.get('event') or '').strip() != 'summary':
            continue
        payload = row.get('payload') if isinstance(row.get('payload'), dict) else {}
        source = str(payload.get('candidate_source') or '').strip().lower()
        if source:
            source_counts[source] += 1
        top = facade._normalize_live_symbol(payload.get('top_stock'))
        if top:
            top_stock_counts[top] += 1
        else:
            no_candidate_total += 1
        top_score = payload.get('top_score')
        if top_score is not None:
            top_score_values.append(facade._safe_float(top_score, 0.0))
        pool = payload.get('candidate_pool_after_filter')
        if pool is not None:
            candidate_pool_values.append(facade._safe_int(pool, 0))
    total = int(sum(source_counts.values()) + no_candidate_total)
    avg_top_score = sum(top_score_values) / len(top_score_values) if top_score_values else None
    avg_pool = sum(candidate_pool_values) / len(candidate_pool_values) if candidate_pool_values else None
    status = 'insufficient_data'
    if total > 0:
        status = 'appropriate' if no_candidate_total / max(1, total) <= 0.4 else 'needs_review'
    return {'scanner_summary_total': int(total), 'candidate_source_top': dict(source_counts.most_common(5)), 'selected_symbol_top': dict(top_stock_counts.most_common(10)), 'no_candidate_total': int(no_candidate_total), 'avg_top_score': float(round(avg_top_score, 6)) if avg_top_score is not None else None, 'avg_candidate_pool_after_filter': float(round(avg_pool, 3)) if avg_pool is not None else None, 'selection_status': status, 'assessment': 'Scanner selected symbols consistently with sufficient candidate pool.' if status == 'appropriate' else 'Scanner produced too many empty selections; candidate sourcing/filtering should be tuned.' if status == 'needs_review' else 'Insufficient scanner summary events.'}


def _build_monitor_evaluation_r4_impl(*, day_rows, overtrading, facade):
    monitor_total = 0
    min_hold_blocked = 0
    sell_cooldown_blocked = 0
    confirm_pending = 0
    confirmed_exit = 0
    monitor_reason_counts: facade.Counter[str] = facade.Counter()
    for row in day_rows:
        if str(row.get('stage') or '').strip() != 'monitor' or str(row.get('event') or '').strip() != 'summary':
            continue
        monitor_total += 1
        payload = row.get('payload') if isinstance(row.get('payload'), dict) else {}
        if bool(payload.get('min_hold_blocked')):
            min_hold_blocked += 1
        if bool(payload.get('sell_cooldown_blocked')):
            sell_cooldown_blocked += 1
        reason = str(payload.get('monitor_reason') or '').strip().lower()
        if reason:
            monitor_reason_counts[reason] += 1
            if reason == 'exit_signal_pending_confirmation':
                confirm_pending += 1
            if reason in ('confirmed_exit_signal', 'emergency_exit_signal'):
                confirmed_exit += 1
    rapid_cycles = facade._safe_int(overtrading.get('rapid_buy_sell_cycles'), 0)
    status = 'stable'
    if rapid_cycles > 0:
        status = 'overtrading_risk'
    elif monitor_total <= 0:
        status = 'insufficient_data'
    return {'monitor_summary_total': int(monitor_total), 'monitor_reason_top': dict(monitor_reason_counts.most_common(12)), 'min_hold_blocked_total': int(min_hold_blocked), 'sell_cooldown_blocked_total': int(sell_cooldown_blocked), 'exit_signal_pending_confirmation_total': int(confirm_pending), 'confirmed_exit_total': int(confirmed_exit), 'rapid_buy_sell_cycles': int(rapid_cycles), 'monitor_status': status, 'assessment': 'Monitor shows overtrading risk; tighten exit confirmation or thresholds.' if status == 'overtrading_risk' else 'Monitor flow is stable under current guards.' if status == 'stable' else 'Insufficient monitor summary events.'}


def _build_supervisor_activity_r4_impl(day_rows, *, intent_flow, facade):
    verdict_total = 0
    blocked_total = 0
    approved_total = 0
    reason_counts: facade.Counter[str] = facade.Counter()
    for row in day_rows:
        stage = str(row.get('stage') or '').strip()
        event = str(row.get('event') or '').strip()
        payload = row.get('payload') if isinstance(row.get('payload'), dict) else {}
        if stage == 'execute_from_packet' and event == 'verdict':
            verdict_total += 1
            if payload.get('allowed') is True:
                approved_total += 1
            elif payload.get('allowed') is False:
                blocked_total += 1
                reason_counts[facade._reason_text(payload.get('reason'))] += 1
            continue
        if stage == 'decision_trace' and event == 'verdict':
            agent, ap = facade._decision_trace_agent_payload(row)
            if agent != 'supervisor':
                continue
            verdict_total += 1
            verdict = str(ap.get('verdict') or '').strip().upper()
            if verdict in ('APPROVE', 'APPROVED', 'ALLOW'):
                approved_total += 1
            elif verdict in ('REJECT', 'BLOCKED', 'DENY'):
                blocked_total += 1
                reason_counts[facade._reason_text(ap.get('guard_reason'))] += 1
    if blocked_total <= 0:
        blocked_total = facade._safe_int(intent_flow.get('intents_blocked'), blocked_total)
    if approved_total <= 0:
        approved_total = facade._safe_int(intent_flow.get('intents_approved'), approved_total)
    block_rate = float(blocked_total / max(1, blocked_total + approved_total))
    return {'verdict_total': int(verdict_total), 'approved_total': int(approved_total), 'blocked_total': int(blocked_total), 'blocked_rate': float(round(block_rate, 6)), 'blocked_reason_top': dict(reason_counts.most_common(12)), 'assessment': 'Supervisor blocks are elevated; review guard thresholds.' if block_rate >= 0.4 else 'Supervisor activity within normal range.'}


def _build_report_views_r4_impl(*, day, trade_summary, monitor_eval, scanner_eval, supervisor_activity, incidents, improvement_suggestions, facade):
    incident_total = facade._safe_int(incidents.get('incident_total'), 0)
    blocked_rate = facade._safe_float(supervisor_activity.get('blocked_rate'), 0.0)
    monitor_status = str(monitor_eval.get('monitor_status') or 'unknown')
    scanner_status = str(scanner_eval.get('selection_status') or 'unknown')
    health = 'GREEN'
    if incident_total > 0 or monitor_status == 'overtrading_risk':
        health = 'YELLOW'
    if blocked_rate >= 0.5:
        health = 'RED'
    operator_lines: List[str] = [f'{day}: health={health}', f"trade_count={facade._safe_int(trade_summary.get('trade_count'), 0)} symbols={len(trade_summary.get('symbols_traded') or [])}", f'monitor_status={monitor_status} scanner_status={scanner_status} supervisor_blocked_rate={blocked_rate:.2%}']
    if incident_total > 0:
        operator_lines.append(f'incident_total={incident_total}')
    if improvement_suggestions:
        operator_lines.append(f'next_action={improvement_suggestions[0]}')
    developer_lines: List[str] = [f"decision_chain_run_total={facade._safe_int(trade_summary.get('decision_chain_run_total'), 0)}", f"blocked_total={facade._safe_int(supervisor_activity.get('blocked_total'), 0)} approved_total={facade._safe_int(supervisor_activity.get('approved_total'), 0)}", f"monitor_confirmed_exit_total={facade._safe_int(monitor_eval.get('confirmed_exit_total'), 0)}", f"scanner_no_candidate_total={facade._safe_int(scanner_eval.get('no_candidate_total'), 0)}"]
    return {'operator_facing_summary': {'system_health': health, 'summary_lines': operator_lines[:4], 'recommended_actions': improvement_suggestions[:3]}, 'developer_facing_summary': {'summary_lines': developer_lines, 'blocked_reason_top': dict(supervisor_activity.get('blocked_reason_top') or {}), 'monitor_reason_top': dict(monitor_eval.get('monitor_reason_top') or {})}}


def _build_improvement_suggestions_r4_impl(*, strategist_eval, scanner_eval, monitor_eval, supervisor_activity, incidents, report_focus_targets, facade):
    focus = {str(x or '').strip().lower() for x in list(report_focus_targets or [])}
    wants_theme = bool(focus & {'theme_accuracy', 'theme', 'themes'})
    wants_scanner = bool(focus & {'scanner_fit', 'scanner', 'selection'})
    wants_exit = bool(focus & {'exit_quality', 'exit', 'overtrading'})
    wants_guard = bool(focus & {'guard_blocks', 'supervisor', 'risk_guard'})
    no_focus = len(focus) == 0
    suggestions: List[str] = []
    if (no_focus or wants_theme) and str(strategist_eval.get('theme_alignment_status') or '') in ('partial', 'insufficient_data'):
        suggestions.append('Improve strategist-to-market alignment evidence: add stronger theme mapping and leader validation inputs.')
    if (no_focus or wants_scanner) and str(scanner_eval.get('selection_status') or '') == 'needs_review':
        suggestions.append('Tune scanner candidate pool reduction (Commander candidate pool baseline / MIN_TRADING_VALUE / MIN_VOLUME) to reduce empty selections.')
    if (no_focus or wants_exit) and str(monitor_eval.get('monitor_status') or '') == 'overtrading_risk':
        suggestions.append('Reduce monitor flip risk by increasing confirmation strictness or widening non-emergency exit thresholds.')
    if (no_focus or wants_guard) and facade._safe_float(supervisor_activity.get('blocked_rate'), 0.0) >= 0.4:
        suggestions.append('High supervisor block rate: recalibrate strategy aggressiveness and guard limits for better intent quality.')
    if facade._safe_int(incidents.get('incident_total'), 0) > 0:
        suggestions.append('Run incident postmortem and convert top anomaly into explicit preopen/checklist gate before next session.')
    if not suggestions:
        suggestions.append('No critical gaps detected; keep current baseline and continue daily report-driven calibration.')
    return suggestions[:8]
