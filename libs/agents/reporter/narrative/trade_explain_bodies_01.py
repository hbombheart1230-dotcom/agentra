"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/trade_explain.py``.

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


def _extract_news_items_r4_impl(news, llm_ctx, *, facade):
    out: List[str] = []
    for key in ('headlines', 'items', 'news_items'):
        src = news.get(key)
        if src is None:
            src = llm_ctx.get(key)
        if isinstance(src, list):
            for it in src:
                if isinstance(it, str):
                    s = it.strip()
                    if s:
                        out.append(s)
                elif isinstance(it, dict):
                    title = str(it.get('title') or it.get('headline') or '').strip()
                    if title:
                        out.append(title)
    uniq: List[str] = []
    seen = set()
    for s in out:
        if s in seen:
            continue
        seen.add(s)
        uniq.append(s)
    return uniq


def _extract_decision_context_r4_impl(payload, *, facade):
    packet = payload.get('decision_packet') if isinstance(payload.get('decision_packet'), dict) else {}
    trace = payload.get('trace') if isinstance(payload.get('trace'), dict) else {}
    intent = packet.get('intent') if isinstance(packet.get('intent'), dict) else {}
    why = packet.get('why') if isinstance(packet.get('why'), dict) else {}
    llm_ctx = trace.get('llm_context') if isinstance(trace.get('llm_context'), dict) else {}
    technical = why.get('technical') if isinstance(why.get('technical'), dict) else {}
    if not technical:
        technical = llm_ctx.get('technical') if isinstance(llm_ctx.get('technical'), dict) else {}
    news = why.get('news') if isinstance(why.get('news'), dict) else {}
    if not news:
        news = llm_ctx.get('news') if isinstance(llm_ctx.get('news'), dict) else {}
    policy = why.get('policy') if isinstance(why.get('policy'), dict) else {}
    if not policy:
        policy = llm_ctx.get('decision_policy') if isinstance(llm_ctx.get('decision_policy'), dict) else {}
    decision_rationale = str(trace.get('rationale') or intent.get('rationale') or '').strip()
    decision_reason = str(intent.get('reason') or '').strip()
    return {'strategy': str(trace.get('strategy') or '').strip(), 'decision_rationale': decision_rationale, 'decision_reason': decision_reason, 'intent_action': str(intent.get('action') or '').strip().upper(), 'intent_symbol': facade._normalize_live_symbol(intent.get('symbol')), 'intent_qty': facade._safe_int(intent.get('qty'), 0), 'technical': technical if isinstance(technical, dict) else {}, 'news': news if isinstance(news, dict) else {}, 'policy': policy if isinstance(policy, dict) else {}, 'news_items': facade._extract_news_items(news if isinstance(news, dict) else {}, llm_ctx)}


def _run_context_default_r4_impl(run_id, *, facade):
    return {'run_id': run_id, 'strategist_llm': {}, 'strategist_policy_resolution': {}, 'decision': {}, 'scanner': {}, 'monitor': {}, 'monitor_entry': {}, 'commander_route': {}, 'verdict': {}, 'execution': {}, 'first_epoch': 0, 'last_epoch': 0}


def _build_run_contexts_r4_impl(rows, *, facade):
    by_run: Dict[str, Dict[str, Any]] = {}
    stage_counts: facade.Counter = facade.Counter()
    for row in rows:
        stage = str(row.get('stage') or '').strip()
        stage_counts[stage] += 1
        run_id = str(row.get('run_id') or '').strip()
        if not run_id:
            continue
        ctx = by_run.setdefault(run_id, facade._run_context_default(run_id))
        epoch = facade._to_epoch(row.get('ts')) or 0
        if ctx['first_epoch'] <= 0 or epoch < int(ctx['first_epoch']):
            ctx['first_epoch'] = epoch
        if epoch > int(ctx['last_epoch']):
            ctx['last_epoch'] = epoch
        event = str(row.get('event') or '').strip()
        payload = row.get('payload') if isinstance(row.get('payload'), dict) else {}
        if stage == 'strategist_llm' and event == 'result':
            ctx['strategist_llm'] = dict(payload)
        elif stage == 'strategist' and event == 'policy_resolution':
            ctx['strategist_policy_resolution'] = dict(payload)
        elif stage == 'decision' and event == 'trace':
            ctx['decision'] = facade._extract_decision_context(payload)
        elif stage == 'scanner' and event == 'summary':
            ctx['scanner'] = dict(payload)
        elif stage == 'scanner' and event == 'candidate_selection_reason':
            scanner = ctx.get('scanner') if isinstance(ctx.get('scanner'), dict) else {}
            ctx['scanner'] = {**dict(scanner), **dict(payload)}
        elif stage == 'monitor' and event == 'summary':
            ctx['monitor'] = dict(payload)
        elif stage == 'monitor' and event == 'entry_decision_detail':
            ctx['monitor_entry'] = dict(payload)
        elif stage == 'execute_from_packet' and event == 'verdict':
            ctx['verdict'] = dict(payload)
        elif stage == 'execute_from_packet' and event == 'execution':
            ctx['execution'] = dict(payload)
        elif stage == 'commander_router' and event in {'route_selected', 'end'}:
            existing = ctx.get('commander_route') if isinstance(ctx.get('commander_route'), dict) else {}
            merged = {**dict(existing), **dict(payload)}
            route_obs = payload.get('route_observability') if isinstance(payload.get('route_observability'), dict) else {}
            if route_obs:
                merged.update(dict(route_obs))
            ctx['commander_route'] = merged
    return (by_run, stage_counts)


def _apply_commander_route_overlay_r4_impl(by_run, route_summary, *, facade):
    route_by_run = route_summary.get('by_run') if isinstance(route_summary.get('by_run'), dict) else {}
    if not route_by_run:
        return by_run
    for run_id, route_row in route_by_run.items():
        if not isinstance(route_row, dict):
            continue
        ctx = by_run.setdefault(run_id, facade._run_context_default(run_id))
        existing = ctx.get('commander_route') if isinstance(ctx.get('commander_route'), dict) else {}
        ctx['commander_route'] = {**dict(existing), **dict(route_row)}
    return by_run


def _build_execution_rows_r4_impl(rows, by_run, *, facade):
    out: List[Dict[str, Any]] = []
    for row in rows:
        stage = str(row.get('stage') or '').strip()
        event = str(row.get('event') or '').strip()
        if stage != 'execute_from_packet' or event != 'execution':
            continue
        run_id = str(row.get('run_id') or '').strip()
        payload = row.get('payload') if isinstance(row.get('payload'), dict) else {}
        order = payload.get('order') if isinstance(payload.get('order'), dict) else {}
        action = str(order.get('action') or '').strip().upper()
        if action not in ('BUY', 'SELL'):
            continue
        symbol = facade._normalize_live_symbol(order.get('symbol') or order.get('stk_cd'))
        qty = facade._safe_int(order.get('qty'), 0)
        if not symbol or qty <= 0:
            continue
        price = facade._safe_float(order.get('price'), 0.0)
        ts = str(row.get('ts') or '')
        epoch = facade._to_epoch(ts) or 0
        ctx = by_run.get(run_id) if isinstance(by_run.get(run_id), dict) else {}
        decision = ctx.get('decision') if isinstance(ctx.get('decision'), dict) else {}
        scanner = ctx.get('scanner') if isinstance(ctx.get('scanner'), dict) else {}
        monitor = ctx.get('monitor') if isinstance(ctx.get('monitor'), dict) else {}
        monitor_entry = ctx.get('monitor_entry') if isinstance(ctx.get('monitor_entry'), dict) else {}
        verdict = ctx.get('verdict') if isinstance(ctx.get('verdict'), dict) else {}
        strategist_llm = ctx.get('strategist_llm') if isinstance(ctx.get('strategist_llm'), dict) else {}
        strategist_policy_resolution = ctx.get('strategist_policy_resolution') if isinstance(ctx.get('strategist_policy_resolution'), dict) else {}
        commander_route = ctx.get('commander_route') if isinstance(ctx.get('commander_route'), dict) else {}
        news = decision.get('news') if isinstance(decision.get('news'), dict) else {}
        tech = decision.get('technical') if isinstance(decision.get('technical'), dict) else {}
        narrative = facade.build_narrative_explanation(action=action, decision_rationale=decision.get('decision_rationale'), decision_reason=decision.get('decision_reason'), key_reason=decision.get('decision_reason'), entry_reason=monitor.get('monitor_reason') if action == 'BUY' else '', dominant_blocker=((monitor_entry.get('no_trade_surface') if isinstance(monitor_entry.get('no_trade_surface'), dict) else {}) or {}).get('dominant_blocker'), exit_reason=monitor.get('exit_reason') if action == 'SELL' else '', exit_monitor_reason=monitor.get('monitor_reason') if action == 'SELL' else '')
        out.append({'ts': ts, 'epoch': int(epoch), 'run_id': run_id, 'symbol': symbol, 'action': action, 'qty': int(qty), 'price': float(price), 'order_type': str(order.get('order_type') or '').strip().lower(), 'broker_code': str((payload.get('payload') or {}).get('broker_code') if isinstance(payload.get('payload'), dict) else ''), 'broker_message': str((payload.get('payload') or {}).get('broker_message') if isinstance(payload.get('payload'), dict) else ''), 'strategy': str(decision.get('strategy') or ''), 'decision_rationale': str(decision.get('decision_rationale') or ''), 'decision_reason': str(decision.get('decision_reason') or ''), 'scanner_source': str(scanner.get('candidate_source') or ''), 'scanner_top_stock': facade._normalize_live_symbol(scanner.get('top_stock')), 'scanner_top_score': scanner.get('top_score'), 'scanner_top_ranked_symbols': [sym for sym in (facade._normalize_live_symbol(x) for x in list(scanner.get('top_ranked_symbols') or [])) if sym], 'scanner_vs_monitor_alignment': str(((monitor_entry.get('scanner_monitor_handoff') if isinstance(monitor_entry.get('scanner_monitor_handoff'), dict) else {}) or {}).get('scanner_vs_monitor_alignment') or ''), 'monitor_exit_reason': str(monitor.get('exit_reason') or ''), 'monitor_reason': str(monitor.get('monitor_reason') or ''), 'monitor_dominant_blocker': str(((monitor_entry.get('no_trade_surface') if isinstance(monitor_entry.get('no_trade_surface'), dict) else {}) or {}).get('dominant_blocker') or ''), 'monitor_price_source': str(monitor.get('price_source') or ''), 'monitor_price_source_policy': str(monitor.get('price_source_policy') or ''), 'monitor_feature_source': str(monitor.get('feature_source') or ''), 'guard_allowed': verdict.get('allowed'), 'guard_reason': str(verdict.get('reason') or ''), 'llm_provider': str(strategist_llm.get('provider') or ''), 'llm_model': str(strategist_llm.get('model') or ''), 'llm_ok': strategist_llm.get('ok'), 'strategist_mode': str(commander_route.get('strategy_generation_mode') or strategist_policy_resolution.get('strategy_generation_mode') or ''), 'strategist_fallback_used': bool(strategist_policy_resolution.get('fallback_used')), 'route_selected': str(commander_route.get('route_selected') or ''), 'route_source': str(commander_route.get('route_source') or 'unavailable'), 'decision_axis': str(narrative.get('decision_axis') or 'unknown'), 'primary_explanation': str(narrative.get('primary_explanation') or '-'), 'entry_narrative': str(narrative.get('entry_narrative') or '-'), 'exit_narrative': str(narrative.get('exit_narrative') or '-'), 'why_not_buy_summary': str(narrative.get('why_not_buy_summary') or '-'), 'why_exit_summary': str(narrative.get('why_exit_summary') or '-'), 'narrative_order': list(narrative.get('narrative_order') or []), 'narrative_order_text': str(narrative.get('narrative_order_text') or '-'), 'narrative_consistency_flag': bool(narrative.get('narrative_consistency_flag')), 'entry_context_blocker': str(narrative.get('entry_context_blocker') or '-'), 'news_symbol_sentiment_score': news.get('symbol_sentiment_score'), 'news_global_sentiment_score': news.get('global_sentiment_score'), 'news_symbol_status': str(news.get('symbol_sentiment_status') or ''), 'news_global_status': str(news.get('global_sentiment_status') or ''), 'news_symbol_source': str(news.get('symbol_sentiment_source') or ''), 'news_global_source': str(news.get('global_sentiment_source') or ''), 'news_items': list(decision.get('news_items') or []), 'signal_score': tech.get('signal_score'), 'rsi14': tech.get('rsi14'), 'ma20_gap': tech.get('ma20_gap'), 'volatility20': tech.get('volatility20'), 'composite_score': tech.get('composite_score')})
    out.sort(key=lambda x: int(x.get('epoch') or 0))
    return out


def _build_sell_pairs_fifo_r4_impl(executions, *, facade):
    open_lots: Dict[str, List[Dict[str, Any]]] = facade.defaultdict(list)
    pairs: List[Dict[str, Any]] = []
    for row in executions:
        action = str(row.get('action') or '').upper()
        symbol = str(row.get('symbol') or '')
        qty = max(0, facade._safe_int(row.get('qty'), 0))
        price = facade._safe_float(row.get('price'), 0.0)
        if not symbol or qty <= 0:
            continue
        if action == 'BUY':
            open_lots[symbol].append({'qty': qty, 'price': price, 'epoch': facade._safe_int(row.get('epoch'), 0), 'run_id': str(row.get('run_id') or '')})
            continue
        if action != 'SELL':
            continue
        remain = qty
        matched_qty = 0
        realized_est = 0.0
        total_entry = 0.0
        weighted_hold = 0.0
        matched_buy_runs: List[str] = []
        while remain > 0 and open_lots.get(symbol):
            lot = open_lots[symbol][0]
            lot_qty = max(0, facade._safe_int(lot.get('qty'), 0))
            if lot_qty <= 0:
                open_lots[symbol].pop(0)
                continue
            take = min(remain, lot_qty)
            entry_px = facade._safe_float(lot.get('price'), 0.0)
            sell_px = facade._safe_float(row.get('price'), 0.0)
            realized_est += (sell_px - entry_px) * float(take)
            total_entry += entry_px * float(take)
            matched_qty += int(take)
            hold_sec = max(0, facade._safe_int(row.get('epoch'), 0) - facade._safe_int(lot.get('epoch'), 0))
            weighted_hold += float(hold_sec * take)
            buy_run_id = str(lot.get('run_id') or '')
            if buy_run_id:
                matched_buy_runs.append(buy_run_id)
            remain -= int(take)
            lot['qty'] = lot_qty - int(take)
            if facade._safe_int(lot.get('qty'), 0) <= 0:
                open_lots[symbol].pop(0)
        avg_entry = total_entry / float(matched_qty) if matched_qty > 0 else 0.0
        avg_hold_sec = weighted_hold / float(matched_qty) if matched_qty > 0 else 0.0
        narrative = facade.build_narrative_explanation(action='SELL', decision_rationale=row.get('decision_rationale'), decision_reason=row.get('decision_reason'), key_reason=row.get('decision_reason') or row.get('monitor_exit_reason'), exit_reason=row.get('monitor_exit_reason'), exit_monitor_reason=row.get('monitor_reason'), dominant_blocker=row.get('monitor_dominant_blocker'))
        pairs.append({'sell_run_id': str(row.get('run_id') or ''), 'sell_ts': str(row.get('ts') or ''), 'symbol': symbol, 'sell_qty': int(qty), 'matched_qty': int(matched_qty), 'unmatched_qty': int(max(0, remain)), 'sell_price': facade._safe_float(row.get('price'), 0.0), 'avg_entry_price': float(round(avg_entry, 4)), 'hold_duration_sec_avg': int(round(avg_hold_sec)), 'estimated_realized_pnl': float(round(realized_est, 4)), 'decision_rationale': str(row.get('decision_rationale') or ''), 'decision_reason': str(row.get('decision_reason') or ''), 'strategy': str(row.get('strategy') or ''), 'monitor_exit_reason': str(row.get('monitor_exit_reason') or ''), 'monitor_reason': str(row.get('monitor_reason') or ''), 'monitor_price_source': str(row.get('monitor_price_source') or ''), 'monitor_price_source_policy': str(row.get('monitor_price_source_policy') or ''), 'monitor_feature_source': str(row.get('monitor_feature_source') or ''), 'scanner_source': str(row.get('scanner_source') or ''), 'scanner_top_stock': str(row.get('scanner_top_stock') or ''), 'scanner_top_score': row.get('scanner_top_score'), 'scanner_top_ranked_symbols': list(row.get('scanner_top_ranked_symbols') or []), 'route_selected': str(row.get('route_selected') or ''), 'route_source': str(row.get('route_source') or 'unavailable'), 'strategist_mode': str(row.get('strategist_mode') or ''), 'decision_axis': str(narrative.get('decision_axis') or 'unknown'), 'primary_explanation': str(narrative.get('primary_explanation') or '-'), 'entry_narrative': str(narrative.get('entry_narrative') or '-'), 'exit_narrative': str(narrative.get('exit_narrative') or '-'), 'why_not_buy_summary': str(narrative.get('why_not_buy_summary') or '-'), 'why_exit_summary': str(narrative.get('why_exit_summary') or '-'), 'narrative_order': list(narrative.get('narrative_order') or []), 'narrative_order_text': str(narrative.get('narrative_order_text') or '-'), 'narrative_consistency_flag': bool(narrative.get('narrative_consistency_flag')), 'entry_context_blocker': str(narrative.get('entry_context_blocker') or '-'), 'news_symbol_sentiment_score': row.get('news_symbol_sentiment_score'), 'news_global_sentiment_score': row.get('news_global_sentiment_score'), 'news_symbol_status': str(row.get('news_symbol_status') or ''), 'news_global_status': str(row.get('news_global_status') or ''), 'signal_score': row.get('signal_score'), 'rsi14': row.get('rsi14'), 'ma20_gap': row.get('ma20_gap'), 'volatility20': row.get('volatility20'), 'composite_score': row.get('composite_score'), 'matched_buy_run_ids': matched_buy_runs})
    return pairs
