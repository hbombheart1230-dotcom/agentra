"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/reporter_analysis.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def _to_epoch_r4_impl(ts, *, facade):
    if ts is None:
        return None
    if isinstance(ts, (int, float)):
        return int(ts)
    raw = str(ts).strip()
    if not raw:
        return None
    try:
        return int(float(raw))
    except Exception:
        pass
    s = raw[:-1] + '+00:00' if raw.endswith('Z') else raw
    try:
        dt = facade.datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=facade.timezone.utc)
        return int(dt.timestamp())
    except Exception:
        return None


def _top_chain_run_ids_r4_impl(trace_summary, agent_key, *, limit, facade):
    out: List[str] = []
    for chain in trace_summary.get('chains') or []:
        if not isinstance(chain, dict):
            continue
        agent_payload = chain.get(agent_key)
        if not isinstance(agent_payload, dict) or not agent_payload:
            continue
        run_id = str(chain.get('run_id') or '').strip()
        if run_id and run_id not in out:
            out.append(run_id)
        if len(out) >= max(1, int(limit)):
            break
    return out


def _make_evidence_ref_r4_impl(*, path, field, run_ids, summary, facade):
    return {'path': str(path or '').strip(), 'field': str(field or '').strip(), 'run_ids': [str(x or '').strip() for x in list(run_ids or []) if str(x or '').strip()], 'summary': str(summary or '').strip()}


def _decision_trace_agent_payload_r4_impl(row, *, facade):
    """Return (agent, payload) from `stage=decision_trace` rows.

    Expected event payload shape:
    {
      "agent": "strategist|scanner|monitor|supervisor|executor",
      "payload": {...}
    }
    """
    payload = row.get('payload') if isinstance(row.get('payload'), dict) else {}
    agent = str(payload.get('agent') or '').strip().lower()
    agent_payload = payload.get('payload') if isinstance(payload.get('payload'), dict) else {}
    return (agent, dict(agent_payload or {}))


def _execution_rows_by_run_r4_impl(executions, *, facade):
    out: Dict[str, List[Dict[str, Any]]] = {}
    for row in executions:
        run_id = str(row.get('run_id') or '').strip()
        if not run_id:
            continue
        out.setdefault(run_id, []).append(row)
    return out


def _build_trade_decision_summaries_r4_impl(trade_explain_obj, *, facade):
    executions = trade_explain_obj.get('executions') if isinstance(trade_explain_obj.get('executions'), list) else []
    sell_pairs = trade_explain_obj.get('sell_pairs') if isinstance(trade_explain_obj.get('sell_pairs'), list) else []
    by_run = facade._execution_rows_by_run([x for x in executions if isinstance(x, dict)])
    summaries: List[Dict[str, Any]] = []
    for pair in sell_pairs:
        if not isinstance(pair, dict):
            continue
        buy_runs = pair.get('matched_buy_run_ids') if isinstance(pair.get('matched_buy_run_ids'), list) else []
        buy_run_id = str(buy_runs[0] or '').strip() if buy_runs else ''
        buy_info = {}
        if buy_run_id and by_run.get(buy_run_id):
            for row in by_run[buy_run_id]:
                if str(row.get('action') or '').upper() == 'BUY':
                    buy_info = row
                    break
        sell_reason = facade._reason_text(pair.get('decision_reason') or pair.get('decision_rationale'))
        monitor_reason = facade._reason_text(pair.get('monitor_reason'))
        exit_trigger = facade._reason_text(pair.get('monitor_exit_reason') or pair.get('monitor_reason') or sell_reason)
        summaries.append({'symbol': facade._normalize_live_symbol(pair.get('symbol')), 'buy_run_id': buy_run_id, 'sell_run_id': str(pair.get('sell_run_id') or ''), 'buy_reason': facade._reason_text(buy_info.get('decision_reason') if isinstance(buy_info, dict) else '' or buy_info.get('decision_rationale') if isinstance(buy_info, dict) else ''), 'sell_reason': sell_reason, 'holding_duration_sec': facade._safe_int(pair.get('hold_duration_sec_avg'), 0), 'exit_trigger': exit_trigger, 'monitor_signals': {'monitor_reason': monitor_reason, 'monitor_exit_reason': facade._reason_text(pair.get('monitor_exit_reason')), 'signal_score': pair.get('signal_score'), 'rsi14': pair.get('rsi14'), 'volatility20': pair.get('volatility20')}, 'estimated_realized_pnl': facade._safe_float(pair.get('estimated_realized_pnl'), 0.0), 'buy_ts': buy_info.get('ts') if isinstance(buy_info, dict) else '', 'sell_ts': str(pair.get('sell_ts') or '')})
    return {'trade_summary_total': int(len(summaries)), 'trade_summaries': summaries}


def _build_strategy_effectiveness_r4_impl(*, day_rows, trade_explain_obj, facade):
    theme_counts: facade.Counter[str] = facade.Counter()
    scanner_top_counts: facade.Counter[str] = facade.Counter()
    strategy_counts: facade.Counter[str] = facade.Counter()
    exit_reason_counts: facade.Counter[str] = facade.Counter()
    report_focus_counts: facade.Counter[str] = facade.Counter()
    scanner_priority_counts: facade.Counter[str] = facade.Counter()
    for row in day_rows:
        stage = str(row.get('stage') or '').strip()
        event = str(row.get('event') or '').strip()
        payload = row.get('payload') if isinstance(row.get('payload'), dict) else {}
        if stage == 'strategist_llm' and event == 'result':
            for key in ('themes', 'top_themes'):
                v = payload.get(key)
                if isinstance(v, list):
                    for item in v:
                        t = str(item or '').strip().lower()
                        if t:
                            theme_counts[t] += 1
        if stage == 'strategist' and event == 'summary':
            v_themes = payload.get('themes')
            if isinstance(v_themes, list):
                for item in v_themes:
                    t = str(item or '').strip().lower()
                    if t:
                        theme_counts[t] += 1
            v_report_focus = payload.get('report_focus')
            if isinstance(v_report_focus, list):
                for item in v_report_focus:
                    f = str(item or '').strip()
                    if f:
                        report_focus_counts[f] += 1
            v_priority = payload.get('scanner_priority')
            if isinstance(v_priority, list):
                for item in v_priority:
                    p = str(item or '').strip().lower()
                    if p:
                        scanner_priority_counts[p] += 1
        if stage == 'scanner' and event == 'summary':
            top_stock = str(payload.get('top_stock') or '').strip().upper()
            if top_stock:
                scanner_top_counts[top_stock] += 1
        if stage == 'monitor' and event == 'summary':
            ex = str(payload.get('exit_reason') or '').strip().lower()
            if ex:
                exit_reason_counts[ex] += 1
    executions = trade_explain_obj.get('executions') if isinstance(trade_explain_obj.get('executions'), list) else []
    for row in executions:
        if not isinstance(row, dict):
            continue
        st = str(row.get('strategy') or '').strip()
        if st:
            strategy_counts[st] += 1
    top_theme = theme_counts.most_common(1)
    top_symbol = scanner_top_counts.most_common(1)
    top_exit = exit_reason_counts.most_common(1)
    strategy_line = f'Strategist favored {top_theme[0][0]} theme.' if top_theme else 'Strategist theme evidence was not captured in current event payload.'
    scanner_line = f'Scanner selected {top_symbol[0][0]} most frequently.' if top_symbol else 'Scanner top-stock evidence was not captured for this day.'
    monitor_line = f'Monitor exited mostly due to {top_exit[0][0]}.' if top_exit else 'Monitor exit trigger evidence was limited for this day.'
    focus_line = f'Reporter focus priority: {report_focus_counts.most_common(1)[0][0]}' if report_focus_counts else 'Reporter focus guidance was limited.'
    return {'theme_counts': dict(theme_counts.most_common(10)), 'scanner_top_stock_counts': dict(scanner_top_counts.most_common(10)), 'strategy_counts': dict(strategy_counts.most_common(10)), 'monitor_exit_reason_counts': dict(exit_reason_counts.most_common(10)), 'scanner_priority_counts': dict(scanner_priority_counts.most_common(10)), 'report_focus_counts': dict(report_focus_counts.most_common(10)), 'narrative': [strategy_line, scanner_line, monitor_line, focus_line]}


def _build_overtrading_diagnostics_r4_impl(*, trade_explain_obj, intent_flow, rapid_threshold_sec, facade):
    sell_pairs = trade_explain_obj.get('sell_pairs') if isinstance(trade_explain_obj.get('sell_pairs'), list) else []
    short_pairs = 0
    for p in sell_pairs:
        if not isinstance(p, dict):
            continue
        if facade._safe_int(p.get('hold_duration_sec_avg'), 0) < int(rapid_threshold_sec):
            short_pairs += 1
    reason_top = intent_flow.get('reason_top') if isinstance(intent_flow.get('reason_top'), dict) else {}
    noise_related = 0
    guard_related = 0
    for k, v in reason_top.items():
        key = str(k).lower()
        cnt = facade._safe_int(v, 0)
        if 'cooldown' in key or 'confirmation' in key or 'post_exit' in key:
            noise_related += cnt
        if 'guard' in key or 'allowlist' in key or 'notional' in key or ('risk' in key):
            guard_related += cnt
    created = facade._safe_int(intent_flow.get('intents_created'), 0)
    blocked = facade._safe_int(intent_flow.get('intents_blocked'), 0)
    blocked_rate = float(blocked) / float(created) if created > 0 else 0.0
    return {'rapid_buy_sell_cycles': int(short_pairs), 'rapid_threshold_sec': int(rapid_threshold_sec), 'noise_exit_related_count': int(noise_related), 'frequent_guard_block_count': int(guard_related), 'guard_block_rate': float(round(blocked_rate, 4))}


def _build_incident_postmortem_r4_impl(*, overtrading, intent_flow, day_rows, facade):
    incidents: List[Dict[str, Any]] = []
    if facade._safe_int(overtrading.get('rapid_buy_sell_cycles'), 0) > 0:
        incidents.append({'type': 'unexpected_rapid_exit', 'severity': 'YELLOW', 'detail': f"rapid_buy_sell_cycles={facade._safe_int(overtrading.get('rapid_buy_sell_cycles'), 0)}"})
    frequent_guard = facade._safe_int(overtrading.get('frequent_guard_block_count'), 0)
    if frequent_guard >= 3:
        incidents.append({'type': 'repeated_guard_blocks', 'severity': 'YELLOW', 'detail': f'guard_related_block_reasons={frequent_guard}'})
    if facade._safe_float(overtrading.get('guard_block_rate'), 0.0) >= 0.5 and facade._safe_int(intent_flow.get('intents_created'), 0) >= 5:
        incidents.append({'type': 'high_block_rate', 'severity': 'RED', 'detail': f"guard_block_rate={facade._safe_float(overtrading.get('guard_block_rate'), 0.0):.2%}"})
    execution_anomaly_total = 0
    for row in day_rows:
        stage = str(row.get('stage') or '').strip()
        event = str(row.get('event') or '').strip()
        payload = row.get('payload') if isinstance(row.get('payload'), dict) else {}
        if stage == 'execute_from_packet' and event == 'execution':
            if payload.get('ok') is False:
                execution_anomaly_total += 1
                continue
            px = payload.get('payload') if isinstance(payload.get('payload'), dict) else {}
            broker_code = str(px.get('broker_code') or '').strip()
            if broker_code and broker_code != '0':
                execution_anomaly_total += 1
                continue
        if stage == 'decision_trace' and event == 'result':
            agent, ap = facade._decision_trace_agent_payload(row)
            if agent != 'executor':
                continue
            if bool(ap.get('execution_attempted')) and str(ap.get('fill_status_summary') or '').strip().lower() in ('failed', 'rejected', 'error'):
                execution_anomaly_total += 1
    if execution_anomaly_total > 0:
        incidents.append({'type': 'execution_anomaly', 'severity': 'RED', 'detail': f'execution_anomaly_total={execution_anomaly_total}'})
    return {'incident_total': int(len(incidents)), 'incidents': incidents}


def _build_market_context_r4_impl(*, trade_explain_obj, day_rows, facade):
    global_scores: List[float] = []
    symbol_scores: List[float] = []
    for row in trade_explain_obj.get('executions') or []:
        if not isinstance(row, dict):
            continue
        gs = row.get('news_global_sentiment_score')
        ss = row.get('news_symbol_sentiment_score')
        if gs is not None:
            global_scores.append(facade._safe_float(gs, 0.0))
        if ss is not None:
            symbol_scores.append(facade._safe_float(ss, 0.0))
    providers: facade.Counter[str] = facade.Counter()
    models: facade.Counter[str] = facade.Counter()
    for row in day_rows:
        if str(row.get('stage') or '') != 'strategist_llm' or str(row.get('event') or '') != 'result':
            continue
        payload = row.get('payload') if isinstance(row.get('payload'), dict) else {}
        p = str(payload.get('provider') or '').strip()
        m = str(payload.get('model') or '').strip()
        if p:
            providers[p] += 1
        if m:
            models[m] += 1
    return {'global_sentiment_avg': float(round(sum(global_scores) / len(global_scores), 6)) if global_scores else None, 'symbol_sentiment_avg': float(round(sum(symbol_scores) / len(symbol_scores), 6)) if symbol_scores else None, 'llm_provider_top': dict(providers.most_common(3)), 'llm_model_top': dict(models.most_common(3))}


def _extract_report_focus_targets_r4_impl(day_rows, *, facade):
    out: List[str] = []
    seen = set()
    for row in day_rows:
        if str(row.get('stage') or '').strip() != 'strategist' or str(row.get('event') or '').strip() != 'summary':
            continue
        payload = row.get('payload') if isinstance(row.get('payload'), dict) else {}
        focus = payload.get('report_focus')
        if not isinstance(focus, list):
            continue
        for item in focus:
            s = str(item or '').strip().lower()
            if not s or s in seen:
                continue
            seen.add(s)
            out.append(s)
    return out[:12]
