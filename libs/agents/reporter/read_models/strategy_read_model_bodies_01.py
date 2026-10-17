"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/strategy_read_model.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def _list_text_r4_impl(values, *, limit, max_len, facade):
    if not isinstance(values, list):
        return []
    out: List[str] = []
    for value in values:
        text = facade._clip(value, max_len=max_len)
        if not text or text in out:
            continue
        out.append(text)
        if len(out) >= max(1, int(limit)):
            break
    return out


def _headline_text_r4_impl(row, *, facade):
    item = row if isinstance(row, dict) else {}
    for key in ('title', 'headline', 'summary', 'description', 'text', 'news_title'):
        text = facade._clip(item.get(key), max_len=180)
        if text:
            return text
    return ''


def _headline_matches_symbol_r4_impl(row, symbol, *, facade):
    item = row if isinstance(row, dict) else {}
    target = facade._norm_symbol(symbol)
    if not target:
        return False
    for candidate in (item.get('symbol'), item.get('code'), item.get('ticker'), item.get('query_target'), item.get('query'), item.get('news_query_target')):
        if facade._norm_symbol(candidate) == target:
            return True
    for key in ('symbols', 'tickers', 'related_symbols'):
        values = item.get(key)
        if not isinstance(values, list):
            continue
        for candidate in values:
            if facade._norm_symbol(candidate) == target:
                return True
    joined = ' '.join([str(item.get('title') or ''), str(item.get('headline') or ''), str(item.get('summary') or ''), str(item.get('description') or ''), str(item.get('query_target') or '')]).upper()
    return bool(target and target in joined)


def _collect_top_headlines_r4_impl(rows, *, limit, symbol, facade):
    if not isinstance(rows, list):
        return []
    filtered: List[str] = []
    fallback: List[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        text = facade._headline_text(row)
        if not text:
            continue
        if text not in fallback:
            fallback.append(text)
        if symbol and facade._headline_matches_symbol(row, symbol) and (text not in filtered):
            filtered.append(text)
    picked = filtered or fallback
    return picked[:max(1, int(limit))]


def _rows_from_news_like_r4_impl(value, *, facade):
    if isinstance(value, list):
        return [dict(row) for row in value if isinstance(row, dict)]
    if not isinstance(value, dict):
        return []
    ranked_rows = value.get('ranked_rows')
    if isinstance(ranked_rows, list):
        return [dict(row) for row in ranked_rows if isinstance(row, dict)]
    out: List[Dict[str, Any]] = []
    for key, row in value.items():
        if not isinstance(row, dict):
            continue
        symbol = facade._norm_symbol(row.get('symbol') or key)
        titles: List[Any] = []
        for bucket in ('sample', 'titles', 'headlines'):
            values = row.get(bucket)
            if isinstance(values, list):
                titles.extend(values)
        for title in titles[:3]:
            text = facade._clip(title, max_len=180)
            if text:
                out.append({'symbol': symbol, 'title': text})
    return out


def _candidate_hypotheses_r4_impl(summary, parsed, *, facade):
    raw = summary.get('candidate_hypotheses')
    if not isinstance(raw, list):
        raw = parsed.get('candidate_hypotheses')
    out: List[Dict[str, str]] = []
    if not isinstance(raw, list):
        return out
    for item in raw:
        if not isinstance(item, dict):
            continue
        symbol = facade._norm_symbol(item.get('symbol'))
        hypothesis = facade._clip(item.get('hypothesis') or item.get('summary') or item.get('reason'), max_len=240)
        source = facade._clip(item.get('source'), max_len=80)
        if not symbol and (not hypothesis):
            continue
        out.append({'symbol': symbol, 'hypothesis': hypothesis, 'source': source})
    return out


def _hypothesis_for_symbol_r4_impl(hypotheses, symbol, *, facade):
    target = facade._norm_symbol(symbol)
    for item in hypotheses:
        if facade._norm_symbol(item.get('symbol')) == target and str(item.get('hypothesis') or '').strip():
            return str(item.get('hypothesis') or '').strip()
    return ''


def _collect_text_fragments_r4_impl(*values, facade):
    parts: List[str] = []
    for value in values:
        if isinstance(value, list):
            for item in value:
                text = facade._clip(item, max_len=240)
                if text:
                    parts.append(text)
            continue
        if isinstance(value, dict):
            for item in value.values():
                text = facade._clip(item, max_len=240)
                if text:
                    parts.append(text)
            continue
        text = facade._clip(value, max_len=240)
        if text:
            parts.append(text)
    return ' | '.join(parts).lower()


def _entry_pattern_type_r4_impl(text, *, facade):
    if facade._contains_any(text, ['breakout']):
        return 'breakout'
    if facade._contains_any(text, ['pullback']):
        return 'pullback'
    if facade._contains_any(text, ['reclaim']):
        return 'reclaim'
    if facade._contains_any(text, ['continuation']):
        return 'continuation'
    return 'unknown'


def _entry_timing_quality_r4_impl(text, *, facade):
    if facade._contains_any(text, ['late entry', 'late chase', 'entered late', 'too late', 'late']):
        return 'late'
    if facade._contains_any(text, ['early entry', 'entered early', 'too early', 'early']):
        return 'early'
    if facade._contains_any(text, ['mid entry', 'mid-cycle', 'middle of move', 'mid']):
        return 'mid'
    return 'unknown'


def _entry_confirmation_quality_r4_impl(text, monitor_reason, *, facade):
    scores = monitor_reason.get('entry_condition_scores') if isinstance(monitor_reason.get('entry_condition_scores'), dict) else {}
    if scores:
        try:
            confidence = float(scores.get('confidence_score'))
        except Exception:
            confidence = None
        try:
            threshold = float(scores.get('confidence_threshold'))
        except Exception:
            threshold = None
        try:
            breakout_score = float(scores.get('breakout_score'))
        except Exception:
            breakout_score = None
        try:
            volume_score = float(scores.get('volume_score'))
        except Exception:
            volume_score = None
        if confidence is not None and threshold is not None and (confidence >= threshold):
            if (breakout_score is not None and breakout_score >= 1.0) and (volume_score is not None and volume_score >= 1.0):
                return 'strong'
            return 'moderate'
        if any((value is not None for value in (confidence, breakout_score, volume_score))):
            return 'weak'
    if facade._contains_any(text, ['strong confirmation', 'fully confirmed', 'high confidence']):
        return 'strong'
    if facade._contains_any(text, ['confirmed', 'confirmation', 'vwap hold', 'volume confirmation']):
        return 'moderate'
    if facade._contains_any(text, ['not confirmed', 'weak confirmation', 'insufficient confirmation']):
        return 'weak'
    return 'unknown'


def _exit_pattern_type_r4_impl(text, *, facade):
    if facade._contains_any(text, ['vwap_breakdown', 'vwap breakdown', 'vwap loss']):
        return 'vwap_breakdown'
    if facade._contains_any(text, ['trend_breakdown', 'trend breakdown', 'trend loss']):
        return 'trend_breakdown'
    if facade._contains_any(text, ['peak_drawdown', 'peak drawdown']):
        return 'peak_drawdown'
    if facade._contains_any(text, ['hard_stop', 'hard stop', 'stop loss', 'stop-loss']):
        return 'hard_stop'
    if facade._contains_any(text, ['trailing_stop', 'trailing stop']):
        return 'trailing_stop'
    if facade._contains_any(text, ['take_profit', 'take profit']):
        return 'take_profit'
    return 'unknown'


def _exit_quality_r4_impl(text, exit_pattern_type, *, facade):
    if facade._contains_any(text, ['forced', 'forced exit', 'forced liquidation']):
        return 'forced'
    if exit_pattern_type == 'hard_stop':
        return 'protective'
    if exit_pattern_type in {'vwap_breakdown', 'trend_breakdown', 'peak_drawdown'}:
        return 'reactive'
    if exit_pattern_type in {'trailing_stop', 'take_profit'}:
        return 'disciplined'
    return 'unknown'


def _thesis_invalidation_code_r4_impl(text, exit_pattern_type, *, facade):
    if facade._contains_any(text, ['weak follow-through', 'weak follow through']):
        return 'weak_follow_through'
    if facade._contains_any(text, ['failed breakout', 'breakout failed']):
        return 'failed_breakout'
    if exit_pattern_type == 'vwap_breakdown' or facade._contains_any(text, ['vwap loss', 'lost vwap']):
        return 'vwap_loss'
    if exit_pattern_type == 'trend_breakdown' or facade._contains_any(text, ['trend loss', 'lost trend']):
        return 'trend_loss'
    if exit_pattern_type == 'hard_stop':
        return 'stop_loss'
    return 'unknown'


def _safe_float_r4_impl(value, *, facade):
    try:
        if value in (None, ''):
            return None
        return float(value)
    except Exception:
        return None


def _compact_recent_trade_ref_r4_impl(item, *, facade):
    return {'trade_id': str(item.get('trade_id') or ''), 'story_id': str(item.get('story_id') or ''), 'run_id': str(item.get('run_id') or ''), 'symbol': facade._norm_symbol(item.get('selected_symbol') or item.get('symbol') or ''), 'playbook': facade._clip(item.get('playbook'), max_len=48), 'trade_status': facade._clip(item.get('trade_status'), max_len=24) or 'unknown', 'final_action': facade._clip(item.get('final_action'), max_len=24) or 'unknown', 'entry_pattern_type': facade._clip(item.get('entry_pattern_type'), max_len=32) or 'unknown', 'exit_pattern_type': facade._clip(item.get('exit_pattern_type'), max_len=32) or 'unknown', 'thesis_invalidation_code': facade._clip(item.get('thesis_invalidation_code'), max_len=48) or 'unknown', 'result_pct': facade._safe_float(item.get('result_pct'))}


def _improvement_tags_r4_impl(text, thesis_invalidation_code, exit_pattern_type, *, facade):
    tags: List[str] = []
    if facade._contains_any(text, ['late entry', 'entered late', 'too late', 'late']):
        facade._append_unique(tags, 'late_entry')
    if facade._contains_any(text, ['weak follow-through', 'weak follow through']):
        facade._append_unique(tags, 'weak_follow_through')
    if facade._contains_any(text, ['insufficient confirmation', 'weak confirmation', 'volume confirmation missing', 'reclaim_not_confirmed']):
        facade._append_unique(tags, 'insufficient_confirmation')
    if thesis_invalidation_code == 'failed_breakout':
        facade._append_unique(tags, 'failed_breakout')
    if thesis_invalidation_code == 'vwap_loss':
        facade._append_unique(tags, 'vwap_loss')
    if thesis_invalidation_code == 'trend_loss':
        facade._append_unique(tags, 'trend_loss')
    if thesis_invalidation_code == 'stop_loss' or exit_pattern_type == 'hard_stop':
        facade._append_unique(tags, 'stop_loss')
    return tags


def _review_flags_r4_impl(*, trade_status, final_action, exit_pattern_type, exit_quality, entry_confirmation_quality, improvement_tags, facade):
    flags: List[str] = []
    if exit_pattern_type == 'take_profit':
        facade._append_unique(flags, 'high_quality_trade')
    if final_action == 'SELL' and exit_quality in {'disciplined', 'protective'} and (exit_pattern_type in {'hard_stop', 'trailing_stop', 'vwap_breakdown', 'trend_breakdown'}):
        facade._append_unique(flags, 'small_loss_disciplined_exit')
    if trade_status == 'closed' and final_action == 'SELL' and (exit_pattern_type == 'unknown'):
        facade._append_unique(flags, 'needs_human_review')
    if entry_confirmation_quality == 'unknown' and (not improvement_tags) and (exit_pattern_type == 'unknown'):
        facade._append_unique(flags, 'needs_human_review')
    return flags
