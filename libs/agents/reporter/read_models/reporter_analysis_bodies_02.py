"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/reporter_analysis.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def _build_decision_chains_r4_impl(day_rows, *, limit, facade):
    by_run: Dict[str, Dict[str, Any]] = {}
    ordered = sorted(day_rows, key=lambda r: facade._to_epoch(r.get('ts') or (r.get('payload') or {}).get('ts')) or 0)
    for row in ordered:
        run_id = str(row.get('run_id') or '').strip()
        if not run_id:
            continue
        chain = by_run.setdefault(run_id, {'run_id': run_id, 'symbol': '', 'action': '', 'buy_reason': '', 'sell_reason': '', 'monitor_reason': '', 'execution_status': 'UNKNOWN', 'supervisor_verdict': 'UNKNOWN', 'guard_reason': '', 'strategist_frame': {}, 'scanner_selection': {}, 'monitor_decision': {}, 'events': []})
        stage = str(row.get('stage') or '').strip()
        event = str(row.get('event') or '').strip()
        payload = row.get('payload') if isinstance(row.get('payload'), dict) else {}
        chain['events'].append(f'{stage}:{event}')
        if stage == 'decision' and event == 'trace':
            packet = payload.get('decision_packet') if isinstance(payload.get('decision_packet'), dict) else {}
            intent = packet.get('intent') if isinstance(packet.get('intent'), dict) else {}
            action = str(intent.get('action') or '').strip().upper()
            symbol = facade._normalize_live_symbol(intent.get('symbol'))
            reason = facade._reason_text(intent.get('reason') or intent.get('rationale'))
            if action:
                chain['action'] = action
            if symbol:
                chain['symbol'] = symbol
            if action == 'BUY' and reason:
                chain['buy_reason'] = reason
            if action == 'SELL' and reason:
                chain['sell_reason'] = reason
        elif stage == 'monitor' and event == 'summary':
            mr = facade._reason_text(payload.get('monitor_reason') or payload.get('exit_reason'))
            if mr:
                chain['monitor_reason'] = mr
        elif stage == 'execute_from_packet' and event == 'verdict':
            allowed = payload.get('allowed')
            if allowed is True:
                chain['supervisor_verdict'] = 'APPROVED'
            elif allowed is False:
                chain['supervisor_verdict'] = 'BLOCKED'
                chain['guard_reason'] = facade._reason_text(payload.get('reason'))
                chain['execution_status'] = 'BLOCKED'
        elif stage == 'execute_from_packet' and event == 'execution':
            ex_payload = payload.get('payload') if isinstance(payload.get('payload'), dict) else {}
            order = payload.get('order') if isinstance(payload.get('order'), dict) else {}
            symbol = facade._normalize_live_symbol(order.get('symbol'))
            action = str(order.get('action') or '').strip().upper()
            if symbol:
                chain['symbol'] = symbol
            if action:
                chain['action'] = action
            broker_code = str(ex_payload.get('broker_code') or '').strip()
            if broker_code == '0':
                chain['execution_status'] = 'EXECUTED_OK'
            elif broker_code:
                chain['execution_status'] = 'EXECUTED_FAIL'
            else:
                chain['execution_status'] = 'EXECUTED'
        elif stage == 'decision_trace':
            agent, ap = facade._decision_trace_agent_payload(row)
            if agent == 'strategist':
                chain['strategist_frame'] = {'market_regime': str(ap.get('market_regime') or ''), 'themes': list(ap.get('themes') or []), 'playbook': str(ap.get('playbook') or ''), 'scanner_bias': str(ap.get('scanner_bias') or ''), 'risk_tone': str(ap.get('risk_tone') or ''), 'monitor_guidance': str(ap.get('monitor_guidance') or '')}
            elif agent == 'scanner':
                chain['scanner_selection'] = {'candidate_pool_size': facade._safe_int(ap.get('candidate_pool_size'), 0), 'selected_symbol': facade._normalize_live_symbol(ap.get('selected_symbol')), 'top_candidates': [sym for sym in (facade._normalize_live_symbol(x) for x in list(ap.get('top_candidates') or [])[:3]) if sym]}
                if not chain.get('symbol'):
                    sel = facade._normalize_live_symbol(ap.get('selected_symbol'))
                    if sel:
                        chain['symbol'] = sel
            elif agent == 'monitor':
                chain['monitor_decision'] = {'entry_reason': facade._reason_text(ap.get('entry_reason')), 'exit_reason': facade._reason_text(ap.get('exit_reason')), 'monitor_reason': facade._reason_text(ap.get('monitor_reason')), 'min_hold_blocked': bool(ap.get('min_hold_blocked')), 'sell_cooldown_blocked': bool(ap.get('sell_cooldown_blocked'))}
                mr = facade._reason_text(ap.get('monitor_reason'))
                if mr != 'unspecified':
                    chain['monitor_reason'] = mr
            elif agent == 'supervisor':
                verdict = str(ap.get('verdict') or '').strip().upper()
                if verdict:
                    chain['supervisor_verdict'] = verdict
                gr = facade._reason_text(ap.get('guard_reason'))
                if gr != 'unspecified':
                    chain['guard_reason'] = gr
                if verdict in ('REJECT', 'BLOCKED'):
                    chain['execution_status'] = 'BLOCKED'
            elif agent == 'executor':
                fs = str(ap.get('fill_status_summary') or '').strip().upper()
                if fs:
                    chain['execution_status'] = fs
    chains = list(by_run.values())
    for c in chains:
        if not c.get('buy_reason') and str(c.get('action') or '').upper() == 'BUY':
            c['buy_reason'] = 'unspecified'
        if not c.get('sell_reason') and str(c.get('action') or '').upper() == 'SELL':
            c['sell_reason'] = 'unspecified'
        c['events'] = list(c.get('events') or [])[:24]
    chains = chains[:max(1, int(limit))]
    return {'run_total': int(len(by_run)), 'rendered_run_total': int(len(chains)), 'chains': chains}


def _build_decision_trace_chain_summary_r4_impl(day_rows, *, limit, facade):
    by_run: Dict[str, Dict[str, Any]] = {}
    for row in sorted(day_rows, key=lambda r: facade._to_epoch(r.get('ts') or (r.get('payload') or {}).get('ts')) or 0):
        if str(row.get('stage') or '').strip() != 'decision_trace':
            continue
        run_id = str(row.get('run_id') or '').strip()
        if not run_id:
            continue
        agent, ap = facade._decision_trace_agent_payload(row)
        if not agent:
            continue
        chain = by_run.setdefault(run_id, {'run_id': run_id, 'strategist': {}, 'scanner': {}, 'monitor': {}, 'supervisor': {}, 'executor': {}, 'agent_sequence': []})
        chain['agent_sequence'].append(agent)
        if agent == 'strategist':
            chain['strategist'] = {'market_regime': str(ap.get('market_regime') or ''), 'themes': list(ap.get('themes') or [])[:5], 'playbook': str(ap.get('playbook') or ''), 'scanner_bias': str(ap.get('scanner_bias') or ''), 'risk_tone': str(ap.get('risk_tone') or ''), 'monitor_guidance': str(ap.get('monitor_guidance') or '')}
        elif agent == 'scanner':
            chain['scanner'] = {'candidate_pool_size': facade._safe_int(ap.get('candidate_pool_size'), 0), 'selected_symbol': facade._normalize_live_symbol(ap.get('selected_symbol')), 'top_candidates': [sym for sym in (facade._normalize_live_symbol(x) for x in list(ap.get('top_candidates') or [])[:3]) if sym], 'score_breakdown_summary': dict(ap.get('score_breakdown_summary') or {})}
        elif agent == 'monitor':
            chain['monitor'] = {'entry_reason': facade._reason_text(ap.get('entry_reason')), 'exit_reason': facade._reason_text(ap.get('exit_reason')), 'monitor_reason': facade._reason_text(ap.get('monitor_reason')), 'min_hold_blocked': bool(ap.get('min_hold_blocked')), 'sell_cooldown_blocked': bool(ap.get('sell_cooldown_blocked'))}
        elif agent == 'supervisor':
            chain['supervisor'] = {'verdict': str(ap.get('verdict') or ''), 'guard_reason': facade._reason_text(ap.get('guard_reason'))}
        elif agent == 'executor':
            chain['executor'] = {'execution_attempted': bool(ap.get('execution_attempted')), 'fill_status_summary': str(ap.get('fill_status_summary') or ''), 'order_result': dict(ap.get('order_result') or {})}
    chains = list(by_run.values())
    complete_total = 0
    for chain in chains:
        seq = list(chain.get('agent_sequence') or [])
        chain['agent_sequence'] = seq[:16]
        complete = bool(chain.get('strategist')) and bool(chain.get('scanner')) and bool(chain.get('monitor')) and bool(chain.get('supervisor')) and bool(chain.get('executor'))
        if complete:
            complete_total += 1
        chain['complete_chain'] = bool(complete)
    chains = chains[:max(1, int(limit))]
    return {'run_total': int(len(by_run)), 'rendered_run_total': int(len(chains)), 'complete_chain_total': int(complete_total), 'chains': chains}


def _build_trade_summary_section_r4_impl(*, trade_decision, decision_chains, facade):
    trade_rows = trade_decision.get('trade_summaries') if isinstance(trade_decision.get('trade_summaries'), list) else []
    symbols = sorted({sym for sym in (facade._normalize_live_symbol((r or {}).get('symbol')) for r in trade_rows if isinstance(r, dict)) if sym})
    hold_rows: List[Dict[str, Any]] = []
    for row in trade_rows:
        if not isinstance(row, dict):
            continue
        symbol = facade._normalize_live_symbol(row.get('symbol'))
        if not symbol:
            continue
        hold_rows.append({'symbol': symbol, 'holding_duration_sec': facade._safe_int(row.get('holding_duration_sec'), 0), 'buy_reason': facade._reason_text(row.get('buy_reason')), 'sell_reason': facade._reason_text(row.get('sell_reason'))})
    return {'trade_count': int(facade._safe_int(trade_decision.get('trade_summary_total'), 0)), 'symbols_traded': symbols, 'symbol_hold_durations': hold_rows, 'decision_chain_run_total': int(facade._safe_int(decision_chains.get('run_total'), 0))}


def _build_ai_evidence_catalog_r4_impl(out, *, facade):
    strategist_eval = out.get('strategist_evaluation') if isinstance(out.get('strategist_evaluation'), dict) else {}
    scanner_eval = out.get('scanner_evaluation') if isinstance(out.get('scanner_evaluation'), dict) else {}
    monitor_eval = out.get('monitor_evaluation') if isinstance(out.get('monitor_evaluation'), dict) else {}
    supervisor_activity = out.get('supervisor_activity') if isinstance(out.get('supervisor_activity'), dict) else {}
    overtrading = out.get('overtrading_diagnostics') if isinstance(out.get('overtrading_diagnostics'), dict) else {}
    incidents = out.get('incident_postmortem') if isinstance(out.get('incident_postmortem'), dict) else {}
    trade_summary = out.get('trade_summary') if isinstance(out.get('trade_summary'), dict) else {}
    trace_summary = out.get('decision_trace_chain_summary') if isinstance(out.get('decision_trace_chain_summary'), dict) else {}
    source_reports = out.get('source_reports') if isinstance(out.get('source_reports'), dict) else {}
    report_json_path = str(out.get('report_json_path') or '').strip()
    return {'strategist_theme_alignment': {'summary': str(strategist_eval.get('assessment') or 'Strategist theme alignment assessment'), 'evidence_refs': [facade._make_evidence_ref(path=report_json_path, field='strategist_evaluation.theme_alignment_status', run_ids=facade._top_chain_run_ids(trace_summary, 'strategist'), summary=str(strategist_eval.get('theme_alignment_status') or '')), facade._make_evidence_ref(path=source_reports.get('decision_story_md'), field='decision_story', run_ids=facade._top_chain_run_ids(trace_summary, 'strategist'), summary='per-run strategist to scanner narrative')]}, 'scanner_selection_fit': {'summary': str(scanner_eval.get('assessment') or 'Scanner selection fit assessment'), 'evidence_refs': [facade._make_evidence_ref(path=report_json_path, field='scanner_evaluation.selected_symbol_top', run_ids=facade._top_chain_run_ids(trace_summary, 'scanner'), summary=facade.json.dumps(scanner_eval.get('selected_symbol_top') or {}, ensure_ascii=False)), facade._make_evidence_ref(path=source_reports.get('run_cards_md'), field='run_cards', run_ids=facade._top_chain_run_ids(trace_summary, 'scanner'), summary='top stock and guard status snapshots')]}, 'monitor_exit_quality': {'summary': str(monitor_eval.get('assessment') or 'Monitor exit quality assessment'), 'evidence_refs': [facade._make_evidence_ref(path=report_json_path, field='monitor_evaluation.monitor_reason_top', run_ids=facade._top_chain_run_ids(trace_summary, 'monitor'), summary=facade.json.dumps(monitor_eval.get('monitor_reason_top') or {}, ensure_ascii=False)), facade._make_evidence_ref(path=source_reports.get('trade_explain_json'), field='trade_explain.trade_summaries', run_ids=facade._top_chain_run_ids(trace_summary, 'monitor'), summary='buy/sell reasons and holding durations')]}, 'overtrading_risk': {'summary': f"rapid_cycles={facade._safe_int(overtrading.get('rapid_buy_sell_cycles'), 0)} guard_block_rate={facade._safe_float(overtrading.get('guard_block_rate'), 0.0):.2%}", 'evidence_refs': [facade._make_evidence_ref(path=report_json_path, field='overtrading_diagnostics', run_ids=facade._top_chain_run_ids(trace_summary, 'monitor'), summary='rapid buy/sell, noise exits, guard block rate')]}, 'supervisor_guard_activity': {'summary': str(supervisor_activity.get('assessment') or 'Supervisor guard activity assessment'), 'evidence_refs': [facade._make_evidence_ref(path=report_json_path, field='supervisor_activity.blocked_reason_top', run_ids=facade._top_chain_run_ids(trace_summary, 'supervisor'), summary=facade.json.dumps(supervisor_activity.get('blocked_reason_top') or {}, ensure_ascii=False)), facade._make_evidence_ref(path=source_reports.get('operator_summary_json'), field='trading_activity_summary', summary='blocked/approved/executed counts')]}, 'incident_summary': {'summary': f"incident_total={facade._safe_int(incidents.get('incident_total'), 0)}", 'evidence_refs': [facade._make_evidence_ref(path=report_json_path, field='incident_postmortem.incidents', summary='unexpected exits, anomalies, guard patterns')]}, 'trade_summary': {'summary': f"trade_count={facade._safe_int(trade_summary.get('trade_count'), 0)} symbols={','.join(list(trade_summary.get('symbols_traded') or [])[:4])}", 'evidence_refs': [facade._make_evidence_ref(path=source_reports.get('trade_explain_json'), field='trade_explain.trade_summaries', summary='trade level buy/sell reasons and hold durations'), facade._make_evidence_ref(path=report_json_path, field='trade_summary', summary='aggregated traded symbols and hold samples')]}, 'decision_trace_quality': {'summary': f"complete_chain_total={facade._safe_int(trace_summary.get('complete_chain_total'), 0)} run_total={facade._safe_int(trace_summary.get('run_total'), 0)}", 'evidence_refs': [facade._make_evidence_ref(path=report_json_path, field='decision_trace_chain_summary', run_ids=facade._top_chain_run_ids(trace_summary, 'executor'), summary='cross-agent chain completeness')]}}


def _infer_ai_evidence_keys_r4_impl(text, catalog, *, facade):
    lower = str(text or '').strip().lower()
    if not lower:
        return []
    rules = [('strategist_theme_alignment', ('strategist', 'theme', 'playbook', 'regime')), ('scanner_selection_fit', ('scanner', 'candidate', 'selection', 'rank', 'top stock')), ('monitor_exit_quality', ('monitor', 'exit', 'hold', 'stop', 'take profit')), ('overtrading_risk', ('overtrading', 'rapid', 'noise', 'cycle')), ('supervisor_guard_activity', ('supervisor', 'guard', 'block', 'approval')), ('incident_summary', ('incident', 'anomal', 'error')), ('trade_summary', ('trade', 'holding', 'pnl')), ('decision_trace_quality', ('trace', 'chain', 'complete'))]
    out: List[str] = []
    for key, patterns in rules:
        if key not in catalog:
            continue
        if any((pattern in lower for pattern in patterns)):
            out.append(key)
    return out[:4]


def _hydrate_ai_evidence_details_r4_impl(texts, link_items, catalog, *, facade):
    links = link_items if isinstance(link_items, list) else []
    details: List[Dict[str, Any]] = []
    for idx, raw_text in enumerate(texts):
        text = str(raw_text or '').strip()
        if not text:
            continue
        item = links[idx] if idx < len(links) and isinstance(links[idx], dict) else {}
        evidence_keys: List[str] = []
        for key in list(item.get('evidence_keys') or []):
            normalized = str(key or '').strip()
            if normalized and normalized in catalog and (normalized not in evidence_keys):
                evidence_keys.append(normalized)
        if not evidence_keys:
            evidence_keys = facade._infer_ai_evidence_keys(text, catalog)
        evidence_refs: List[Dict[str, Any]] = []
        for key in evidence_keys:
            entry = catalog.get(key) if isinstance(catalog.get(key), dict) else {}
            for ref in list(entry.get('evidence_refs') or []):
                if isinstance(ref, dict):
                    evidence_refs.append(dict(ref))
            if len(evidence_refs) >= 8:
                break
        details.append({'text': text, 'evidence_keys': evidence_keys, 'evidence_refs': evidence_refs[:8]})
    return details


def _first_nonempty_str_r4_impl(*values, facade):
    for value in values:
        s = str(value or '').strip()
        if s:
            return s
    return ''


def _ensure_min_ai_review_payload_r4_impl(*, out, ai_review, facade):
    findings = list(ai_review.get('ai_findings') or [])
    root_causes = list(ai_review.get('ai_root_causes') or [])
    improvements = list(ai_review.get('ai_improvement_suggestions') or [])
    evidence_links = ai_review.get('ai_evidence_links') if isinstance(ai_review.get('ai_evidence_links'), dict) else {}
    finding_links = list(evidence_links.get('findings') or [])
    root_links = list(evidence_links.get('root_causes') or [])
    improvement_links = list(evidence_links.get('improvements') or [])
    catalog = out.get('ai_evidence_catalog') if isinstance(out.get('ai_evidence_catalog'), dict) else {}
    strategist_eval = out.get('strategist_evaluation') if isinstance(out.get('strategist_evaluation'), dict) else {}
    scanner_eval = out.get('scanner_evaluation') if isinstance(out.get('scanner_evaluation'), dict) else {}
    monitor_eval = out.get('monitor_evaluation') if isinstance(out.get('monitor_evaluation'), dict) else {}
    supervisor_activity = out.get('supervisor_activity') if isinstance(out.get('supervisor_activity'), dict) else {}
    overtrading = out.get('overtrading_diagnostics') if isinstance(out.get('overtrading_diagnostics'), dict) else {}
    improvement_suggestions = out.get('improvement_suggestions') if isinstance(out.get('improvement_suggestions'), list) else []
    fallback_used = False

    def _append_with_link(target: List[str], link_target: List[Dict[str, Any]], text: str, evidence_keys: List[str]) -> None:
        cleaned = str(text or '').strip()
        if not cleaned:
            return
        if cleaned not in target:
            target.append(cleaned)
            link_target.append({'text': cleaned, 'evidence_keys': list(evidence_keys or [])[:3]})
    if not findings:
        fallback_used = True
        if str(scanner_eval.get('selection_status') or '') == 'needs_review':
            _append_with_link(findings, finding_links, 'Scanner selection fit needs review under the observed market context.', ['scanner_selection_fit'])
        if str(monitor_eval.get('monitor_status') or '') == 'overtrading_risk' or facade._safe_int(overtrading.get('rapid_buy_sell_cycles'), 0) > 0:
            _append_with_link(findings, finding_links, 'Monitor behavior showed overtrading or rapid exit pressure in this run window.', ['monitor_exit_quality', 'overtrading_risk'])
        if not findings and facade._safe_float(supervisor_activity.get('blocked_rate'), 0.0) >= 0.4:
            _append_with_link(findings, finding_links, 'Supervisor blocked a material share of intents, indicating upstream intent quality friction.', ['supervisor_guard_activity'])
        if not findings:
            _append_with_link(findings, finding_links, 'Deterministic evidence is available for strategist, scanner, and monitor evaluation and should guide the next run review.', ['decision_trace_quality', 'trade_summary'])
    if not root_causes:
        fallback_used = True
        if str(monitor_eval.get('monitor_status') or '') == 'overtrading_risk' or facade._safe_int(overtrading.get('rapid_buy_sell_cycles'), 0) > 0:
            _append_with_link(root_causes, root_links, 'Exit handling and monitor confirmation logic remained the dominant source of instability.', ['monitor_exit_quality', 'overtrading_risk'])
        if not root_causes and str(scanner_eval.get('selection_status') or '') == 'needs_review':
            _append_with_link(root_causes, root_links, 'Scanner candidate ranking relied on weak fit signals relative to the observed market regime.', ['scanner_selection_fit'])
        if not root_causes and str(strategist_eval.get('theme_alignment_status') or '') in ('partial', 'insufficient_data'):
            _append_with_link(root_causes, root_links, 'Strategist framing only partially aligned with the leaders observed by scanner and execution traces.', ['strategist_theme_alignment'])
        if not root_causes:
            _append_with_link(root_causes, root_links, 'No single dominant cause was isolated; scanner fit and monitor exit quality should be reviewed together.', ['scanner_selection_fit', 'monitor_exit_quality'])
    if not improvements:
        fallback_used = True
        if improvement_suggestions:
            top_suggestion = str(improvement_suggestions[0] or '').strip()
            evidence_keys = facade._infer_ai_evidence_keys(top_suggestion, catalog)
            _append_with_link(improvements, improvement_links, top_suggestion, evidence_keys or ['monitor_exit_quality'])
        if not improvements and str(monitor_eval.get('monitor_status') or '') == 'overtrading_risk':
            _append_with_link(improvements, improvement_links, 'Tighten non-emergency monitor behavior by increasing confirmation strictness or widening patience around noise.', ['monitor_exit_quality', 'overtrading_risk'])
        if not improvements and str(scanner_eval.get('selection_status') or '') == 'needs_review':
            _append_with_link(improvements, improvement_links, 'Refine scanner pool reduction and ranking so candidate fit is less dependent on weak liquidity-only signals.', ['scanner_selection_fit'])
        if not improvements:
            _append_with_link(improvements, improvement_links, 'Keep using evidence-linked post-run review and convert the top weakness into an explicit next-run checklist item.', ['decision_trace_quality', 'incident_summary'])
    agent_evaluations = ai_review.get('ai_agent_evaluations') if isinstance(ai_review.get('ai_agent_evaluations'), dict) else {}
    if fallback_used and (not agent_evaluations):
        agent_evaluations = {'strategist': 'needs_improvement' if str(strategist_eval.get('theme_alignment_status') or '') in ('partial', 'insufficient_data') else 'good', 'scanner': 'needs_improvement' if str(scanner_eval.get('selection_status') or '') == 'needs_review' else 'good', 'monitor': 'needs_improvement' if str(monitor_eval.get('monitor_status') or '') == 'overtrading_risk' else 'good', 'supervisor': 'needs_improvement' if facade._safe_float(supervisor_activity.get('blocked_rate'), 0.0) >= 0.4 else 'good', 'executor': 'good'}
    ai_summary = str(ai_review.get('ai_summary') or '').strip()
    if fallback_used and (not ai_summary):
        ai_summary = facade._first_nonempty_str(findings[0] if findings else '', root_causes[0] if root_causes else '', 'Deterministic post-run evidence was used to build a minimal AI review summary.')
    reason = str(ai_review.get('reason') or '').strip()
    if fallback_used:
        reason = facade._first_nonempty_str(reason, 'empty_ai_lists_repaired_from_deterministic_evidence')
    return {**dict(ai_review), 'reason': reason, 'ai_summary': ai_summary, 'ai_findings': findings[:12], 'ai_root_causes': root_causes[:10], 'ai_improvement_suggestions': improvements[:10], 'ai_agent_evaluations': dict(agent_evaluations), 'ai_evidence_links': {'findings': finding_links[:12], 'root_causes': root_links[:10], 'improvements': improvement_links[:10]}, 'fallback_enriched': bool(fallback_used)}


def _build_strategy_frame_summary_r4_impl(day_rows, *, facade):
    theme_counts: facade.Counter[str] = facade.Counter()
    playbook_counts: facade.Counter[str] = facade.Counter()
    risk_tone_counts: facade.Counter[str] = facade.Counter()
    monitor_guidance_counts: facade.Counter[str] = facade.Counter()
    report_focus_counts: facade.Counter[str] = facade.Counter()

    def _consume(payload: Dict[str, Any]) -> None:
        for theme in list(payload.get('themes') or []):
            text = str(theme or '').strip().lower()
            if text:
                theme_counts[text] += 1
        playbook = str(payload.get('playbook') or '').strip().lower()
        if playbook:
            playbook_counts[playbook] += 1
        risk_tone = str(payload.get('risk_tone') or '').strip().lower()
        if risk_tone:
            risk_tone_counts[risk_tone] += 1
        monitor_guidance = str(payload.get('monitor_guidance') or '').strip().lower()
        if monitor_guidance:
            monitor_guidance_counts[monitor_guidance] += 1
        for focus in list(payload.get('report_focus') or []):
            text = str(focus or '').strip()
            if text:
                report_focus_counts[text] += 1
    for row in day_rows:
        stage = str(row.get('stage') or '').strip()
        event = str(row.get('event') or '').strip()
        payload = row.get('payload') if isinstance(row.get('payload'), dict) else {}
        if stage == 'strategist' and event == 'summary':
            _consume(payload)
            continue
        if stage == 'decision_trace' and event == 'strategic_frame':
            agent, agent_payload = facade._decision_trace_agent_payload(row)
            if agent == 'strategist':
                _consume(agent_payload)
    return {'theme_top': dict(theme_counts.most_common(8)), 'playbook_top': dict(playbook_counts.most_common(6)), 'risk_tone_top': dict(risk_tone_counts.most_common(6)), 'monitor_guidance_top': dict(monitor_guidance_counts.most_common(6)), 'report_focus_top': dict(report_focus_counts.most_common(8))}
