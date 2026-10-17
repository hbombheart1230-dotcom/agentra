"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/entry_blocker_read_model.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def _to_float_r4_impl(value, *, facade):
    try:
        out = float(value)
    except Exception:
        return None
    if out != out:
        return None
    return out


def _list_text_r4_impl(values, *, limit, facade):
    out: List[str] = []
    seen: set[str] = set()
    for value in list(values or []):
        text = facade._text(value)
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
        if len(out) >= int(limit):
            break
    return out


def _normalize_blocker_family_r4_impl(value, *, facade):
    text = facade._text(value).lower()
    if not text:
        return ''
    if text in {'buy_blocked_open_position', 'open_position_blocked'}:
        return 'open_position_guard'
    if text.startswith('entry_guard_cooldown') or 'cooldown' in text:
        return 'cooldown_guard'
    if text in {'pullback_not_mature', 'pullback_mature', 'pullback_ok', 'pullback_structure_ok', 'pullback_volume_path_ok', 'pullback_below_vwap_reclaim_not_ready'} or 'pullback' in text:
        return 'pullback_timing'
    if text in {'below_vwap_reclaim_not_ready', 'vwap_reclaim_ok', 'reclaim_gate_ok', 'vwap_hold_ok'} or 'reclaim' in text or 'vwap' in text:
        return 'reclaim_readiness'
    if text in {'volume_confirmation_missing', 'volume_ok'} or 'volume' in text:
        return 'volume_confirmation'
    if text in {'breakout_not_ready', 'breakout_ok', 'breakout_path_ok', 'wait_for_confirmation'} or 'breakout' in text or 'confirmation' in text:
        return 'breakout_confirmation'
    if text in {'rebound_ok'} or 'rebound' in text:
        return 'rebound_confirmation'
    if text in {'structure_hh_hl', 'chart_structure_guard'} or 'structure' in text:
        return 'structure_confirmation'
    if text in {'confidence_gate_ok'} or 'confidence' in text:
        return 'confidence_gate'
    if 'extend' in text or 'overextended' in text:
        return 'overextension_guard'
    if text.startswith('risk_') or text == 'risk_blocked':
        return 'risk_guard'
    if text == 'unknown':
        return 'unknown'
    return 'other'


def explain_raw_blocker_r4_impl(value, *, facade):
    text = facade._text(value)
    key = text.lower()
    if not key:
        return ''
    if key.startswith('entry_guard_cooldown'):
        return '엔트리 가드 쿨다운으로 잠시 재진입 대기'
    if key in facade._RAW_BLOCKER_EXPLANATIONS:
        return facade._RAW_BLOCKER_EXPLANATIONS[key]
    return f'{text} 관련 확인/차단 조건'


def _build_blocker_families_r4_impl(primary_blockers, *, no_trade_code, limit, facade):
    out: List[str] = []
    seen: set[str] = set()
    values = list(primary_blockers or [])
    if no_trade_code not in (None, ''):
        values = [no_trade_code] + values
    for value in values:
        family = facade._normalize_blocker_family(value)
        if not family or family in seen:
            continue
        seen.add(family)
        out.append(family)
        if len(out) >= int(limit):
            break
    return out


def _build_family_raw_breakdown_r4_impl(primary_blockers, *, no_trade_code, limit_per_family, facade):
    breakdown: Dict[str, List[str]] = {}
    values = facade._list_text(([no_trade_code] if no_trade_code not in (None, '') else []) + list(primary_blockers or []), limit=20)
    for raw in values:
        family = facade._normalize_blocker_family(raw)
        if not family:
            continue
        breakdown.setdefault(family, [])
        if raw not in breakdown[family]:
            breakdown[family].append(raw)
            if len(breakdown[family]) > int(limit_per_family):
                breakdown[family] = breakdown[family][:int(limit_per_family)]
    return breakdown


def _infer_scanner_quality_suspected_r4_impl(*, no_trade_code, primary_blockers, scanner_selected_summary, scanner_score_total, facade):
    reasons: List[str] = []
    raw = {facade._text(item) for item in list(primary_blockers or []) if facade._text(item)}
    if facade._text(no_trade_code):
        raw.add(facade._text(no_trade_code))
    selected_confidence = facade._to_float(scanner_selected_summary.get('confidence'))
    selected_score = facade._to_float(scanner_selected_summary.get('score_total'))
    effective_score = selected_score if selected_score is not None else scanner_score_total
    if 'too_extended_from_vwap' in raw:
        reasons.append('selected_candidate_extended')
    if 'volume_confirmation_missing' in raw and effective_score is not None and (effective_score < 0.8):
        reasons.append('volume_confirmation_missing_low_score')
    if selected_confidence is not None and selected_confidence < 0.72:
        reasons.append('low_candidate_confidence')
    return (bool(reasons), reasons[0] if reasons else '', reasons)


def _scanner_quality_reason_explanation_r4_impl(value, *, facade):
    key = facade._text(value)
    mapping = {'selected_candidate_extended': '선정 종목이 이미 VWAP 대비 과열/이격 상태로 보임', 'volume_confirmation_missing_low_score': '거래량 확인 부족과 낮은 scanner 점수가 함께 나타남', 'low_candidate_confidence': 'selected candidate confidence가 낮은 편'}
    return mapping.get(key, '')


def _parse_ts_r4_impl(value, *, facade):
    text = facade._text(value)
    if not text:
        return None
    try:
        return facade.datetime.fromisoformat(text)
    except Exception:
        return None


def classify_entry_time_bucket_r4_impl(value, *, facade):
    dt = facade._parse_ts(value)
    if dt is None:
        return 'unknown'
    dt_kst = dt.astimezone(facade.KST)
    minutes = dt_kst.hour * 60 + dt_kst.minute
    if minutes < 10 * 60 + 30:
        return 'open_window'
    if minutes < 14 * 60 + 30:
        return 'mid_session'
    return 'late_session'


def _resolve_structure_state_r4_impl(monitor, blocker_surface, *, facade):
    state = facade._text(blocker_surface.get('structure_hh_hl'))
    if state:
        return state
    chart_features = monitor.get('entry_chart_structure_features')
    if isinstance(chart_features, facade.Mapping):
        structure = chart_features.get('structure')
        if isinstance(structure, facade.Mapping):
            state = facade._text(structure.get('structure_hh_hl'))
            if state:
                return state
        state = facade._text(chart_features.get('structure_hh_hl'))
        if state:
            return state
    return ''


def _resolve_threshold_actual_r4_impl(threshold_snapshot, field, *, facade):
    margins = threshold_snapshot.get('entry_threshold_margins')
    if isinstance(margins, facade.Mapping):
        row = margins.get(field)
        if isinstance(row, facade.Mapping) and row.get('actual') not in (None, ''):
            return row.get('actual')
    return threshold_snapshot.get(field)


def build_entry_blocker_row_r4_impl(run_id, *, monitor, scanner, facade):
    scanner_row = dict(scanner or {}) if isinstance(scanner, facade.Mapping) else {}
    blocker_surface = dict(monitor.get('entry_blocker_surface') or {}) if isinstance(monitor.get('entry_blocker_surface'), facade.Mapping) else {}
    no_trade_surface = dict(monitor.get('no_trade_surface') or {}) if isinstance(monitor.get('no_trade_surface'), facade.Mapping) else {}
    threshold_snapshot = dict(monitor.get('threshold_snapshot') or {}) if isinstance(monitor.get('threshold_snapshot'), facade.Mapping) else {}
    scanner_selected = dict(scanner_row.get('selected_candidate') or {}) if isinstance(scanner_row.get('selected_candidate'), facade.Mapping) else {}
    scanner_pool = dict(scanner_row.get('candidate_pool_snapshot') or {}) if isinstance(scanner_row.get('candidate_pool_snapshot'), facade.Mapping) else {}
    ts = facade._text(monitor.get('ts'))
    dt = facade._parse_ts(ts)
    ts_kst = dt.astimezone(facade.KST).isoformat() if dt is not None else ''
    decision_raw = facade._text(monitor.get('decision') or monitor.get('decision_action') or 'NOOP').upper()
    if decision_raw == 'BUY':
        final_decision = 'BUY'
    elif decision_raw == 'SELL':
        final_decision = 'SELL'
    else:
        final_decision = 'WAIT'
    no_trade_code = facade._text(blocker_surface.get('no_trade_code') or monitor.get('no_trade_reason_code') or no_trade_surface.get('no_trade_reason_code'))
    dominant_blocker = facade._text(blocker_surface.get('dominant_blocker') or monitor.get('dominant_blocker') or no_trade_surface.get('dominant_blocker') or no_trade_code)
    primary_blockers = facade._list_text(blocker_surface.get('primary_blockers') or monitor.get('entry_blockers') or [dominant_blocker, no_trade_code])
    raw_entry_blockers = facade._list_text(blocker_surface.get('raw_entry_blockers') or monitor.get('entry_blockers'))
    confidence_score = blocker_surface.get('confidence_score')
    if confidence_score in (None, ''):
        confidence_score = (monitor.get('evidence_snapshot') or {}).get('confidence_score') if isinstance(monitor.get('evidence_snapshot'), facade.Mapping) else None
    if confidence_score in (None, '') and isinstance(monitor.get('entry_condition_scores'), facade.Mapping):
        confidence_score = monitor.get('entry_condition_scores', {}).get('confidence_score')
    confidence_threshold = blocker_surface.get('confidence_threshold')
    if confidence_threshold in (None, '') and isinstance(monitor.get('evidence_snapshot'), facade.Mapping):
        confidence_threshold = monitor.get('evidence_snapshot', {}).get('confidence_threshold')
    if confidence_threshold in (None, '') and isinstance(monitor.get('entry_condition_scores'), facade.Mapping):
        confidence_threshold = monitor.get('entry_condition_scores', {}).get('confidence_threshold')
    symbol = facade._text(monitor.get('symbol') or monitor.get('scanner_selected_symbol') or scanner_selected.get('symbol'))
    volume_ratio = blocker_surface.get('volume_ratio')
    if volume_ratio in (None, ''):
        volume_ratio = facade._resolve_threshold_actual(threshold_snapshot, 'entry_volume_ratio')
    pullback_depth_pct = blocker_surface.get('pullback_depth_pct')
    if pullback_depth_pct in (None, ''):
        pullback_depth_pct = facade._resolve_threshold_actual(threshold_snapshot, 'entry_pullback_depth_pct')
    previous_close = blocker_surface.get('previous_close', monitor.get('previous_close'))
    if previous_close in (None, ''):
        previous_close = threshold_snapshot.get('entry_previous_close')
    session_open = blocker_surface.get('session_open', monitor.get('session_open'))
    if session_open in (None, ''):
        session_open = threshold_snapshot.get('entry_session_open')
    open_gap_pct = blocker_surface.get('open_gap_pct', monitor.get('open_gap_pct'))
    if open_gap_pct in (None, ''):
        open_gap_pct = threshold_snapshot.get('entry_open_gap_pct')
    prev_close_distance_pct = blocker_surface.get('prev_close_distance_pct', monitor.get('prev_close_distance_pct'))
    if prev_close_distance_pct in (None, ''):
        prev_close_distance_pct = threshold_snapshot.get('entry_prev_close_distance_pct')
    minutes_since_session_open = blocker_surface.get('minutes_since_session_open', monitor.get('minutes_since_session_open'))
    if minutes_since_session_open in (None, ''):
        minutes_since_session_open = threshold_snapshot.get('entry_minutes_since_session_open')
    selected_summary = {'symbol': facade._text(scanner_selected.get('symbol') or symbol), 'why': facade._text(scanner_selected.get('why')), 'asset_class_detected': facade._text(scanner_selected.get('asset_class_detected')), 'detection_source': facade._text(scanner_selected.get('detection_source')), 'score_total': scanner_selected.get('score_total', monitor.get('scanner_score_total')), 'confidence': scanner_selected.get('confidence'), 'sources': facade._list_text(scanner_selected.get('sources'), limit=6)}
    blocker_families = facade._build_blocker_families(primary_blockers, no_trade_code=no_trade_code)
    blocker_family_raw_breakdown = facade._build_family_raw_breakdown(primary_blockers, no_trade_code=no_trade_code)
    scanner_score_total = facade._to_float(monitor.get('scanner_score_total'))
    scanner_quality_suspected, scanner_quality_reason, scanner_quality_reasons = facade._infer_scanner_quality_suspected(no_trade_code=no_trade_code, primary_blockers=primary_blockers, scanner_selected_summary=selected_summary, scanner_score_total=scanner_score_total)
    blocker_family_explanations = {family: facade.explain_blocker_family(family) for family in blocker_families if facade.explain_blocker_family(family)}
    raw_blocker_explanations = {raw: facade.explain_raw_blocker(raw) for raw in facade._list_text(([no_trade_code] if no_trade_code else []) + primary_blockers, limit=12) if facade.explain_raw_blocker(raw)}
    return {'run_id': facade._text(run_id), 'ts': ts, 'ts_kst': ts_kst, 'time_bucket': facade.classify_entry_time_bucket(ts), 'symbol': symbol, 'final_decision': final_decision, 'decision_raw': decision_raw, 'primary_blockers': primary_blockers, 'blocker_families': blocker_families, 'blocker_family_raw_breakdown': blocker_family_raw_breakdown, 'blocker_family_explanations': blocker_family_explanations, 'raw_entry_blockers': raw_entry_blockers, 'raw_blocker_explanations': raw_blocker_explanations, 'dominant_blocker': dominant_blocker, 'no_trade_code': no_trade_code, 'entry_style': facade._text(blocker_surface.get('entry_style') or ((monitor.get('evidence_snapshot') or {}).get('entry_style') if isinstance(monitor.get('evidence_snapshot'), facade.Mapping) else '')), 'confidence_score': facade._to_float(confidence_score), 'confidence_threshold': facade._to_float(confidence_threshold), 'pullback_depth_pct': facade._to_float(pullback_depth_pct), 'rebound_ok': blocker_surface.get('rebound_ok'), 'rebound_progress': facade._to_float(blocker_surface.get('rebound_progress')), 'pullback_ok': blocker_surface.get('pullback_ok'), 'pullback_not_mature': bool(blocker_surface.get('pullback_not_mature') or no_trade_code == 'pullback_not_mature'), 'volume_ok': blocker_surface.get('volume_ok'), 'volume_ratio': facade._to_float(volume_ratio), 'volume_confirmation_missing': bool(blocker_surface.get('volume_confirmation_missing') or no_trade_code == 'volume_confirmation_missing'), 'previous_close': facade._to_float(previous_close), 'session_open': facade._to_float(session_open), 'open_gap_pct': facade._to_float(open_gap_pct), 'prev_close_distance_pct': facade._to_float(prev_close_distance_pct), 'minutes_since_session_open': facade._to_float(minutes_since_session_open), 'opening_gap_chase_observed': bool(blocker_surface.get('opening_gap_chase_observed') or monitor.get('opening_gap_chase_observed') or threshold_snapshot.get('entry_opening_gap_chase_observed')), 'opening_gap_context_observation_only': bool(blocker_surface.get('opening_gap_context_observation_only') or monitor.get('opening_gap_context_observation_only') or threshold_snapshot.get('entry_opening_gap_context_observation_only')), 'structure_hh_hl': facade._resolve_structure_state(monitor, blocker_surface), 'below_vwap_reclaim_not_ready': bool(blocker_surface.get('below_vwap_reclaim_not_ready') or no_trade_code == 'below_vwap_reclaim_not_ready'), 'reclaim_gate_ok': blocker_surface.get('reclaim_gate_ok'), 'vwap_hold_ok': blocker_surface.get('vwap_hold_ok'), 'vwap_reclaim_ok': blocker_surface.get('vwap_reclaim_ok'), 'reclaim_distance_to_ready': blocker_surface.get('reclaim_distance_to_ready'), 'reclaim_readiness_tuned': bool(blocker_surface.get('reclaim_readiness_tuned')), 'reclaim_tuning_version': facade._text(blocker_surface.get('reclaim_tuning_version')), 'reclaim_tuning_scope': facade._text(blocker_surface.get('reclaim_tuning_scope')), 'reclaim_tuning_band_used': facade._text(blocker_surface.get('reclaim_tuning_band_used')), 'entry_tuning_flags': facade._list_text(blocker_surface.get('entry_tuning_flags'), limit=6), 'reclaim_evidence_explanation': facade._text(blocker_surface.get('reclaim_evidence_explanation')), 'open_position_blocked': bool(blocker_surface.get('open_position_blocked') or monitor.get('buy_blocked_open_position')), 'cooldown_blocked': bool(blocker_surface.get('cooldown_blocked') or monitor.get('buy_blocked_post_exit_cooldown')), 'cooldown_remaining_sec': facade._to_int(blocker_surface.get('post_exit_cooldown_remaining_sec') or monitor.get('post_exit_cooldown_remaining_sec')), 'scanner_rank': facade._to_int(monitor.get('scanner_rank')), 'scanner_score_total': scanner_score_total, 'scanner_selected_summary': selected_summary, 'scanner_candidate_count_after_filter': facade._to_int(scanner_pool.get('total_candidates_after_filter') or scanner_row.get('candidate_pool_after_filter')), 'unknown_asset_candidate_count': facade._to_int(scanner_pool.get('unknown_asset_candidate_count') or scanner_row.get('unknown_asset_candidate_count')), 'scanner_quality_suspected': scanner_quality_suspected, 'scanner_quality_reason': scanner_quality_reason, 'scanner_quality_reasons': scanner_quality_reasons, 'scanner_quality_reason_explanation': facade._scanner_quality_reason_explanation(scanner_quality_reason)}


def build_symbol_entry_blocker_sequence_r4_impl(rows, *, symbol, facade):
    target = facade._text(symbol).upper()
    out: List[Dict[str, Any]] = []
    for row in rows:
        if facade._text(row.get('symbol')).upper() != target:
            continue
        out.append({'run_id': facade._text(row.get('run_id')), 'ts_kst': facade._text(row.get('ts_kst')), 'final_decision': facade._text(row.get('final_decision')), 'no_trade_code': facade._text(row.get('no_trade_code')), 'primary_blockers': facade._list_text(row.get('primary_blockers')), 'blocker_families': facade._list_text(row.get('blocker_families')), 'family_explanations': dict(row.get('blocker_family_explanations') or {}), 'raw_blocker_explanations': dict(row.get('raw_blocker_explanations') or {}), 'scanner_quality_suspected': bool(row.get('scanner_quality_suspected')), 'scanner_quality_reason': facade._text(row.get('scanner_quality_reason')), 'scanner_quality_reason_explanation': facade._text(row.get('scanner_quality_reason_explanation')), 'scanner_selected_summary': dict(row.get('scanner_selected_summary') or {})})
    out.sort(key=lambda row: (facade._text(row.get('ts_kst')), facade._text(row.get('run_id'))))
    return out


def _counter_to_dict_r4_impl(counter, *, facade):
    if isinstance(counter, facade.Mapping):
        items = counter.items()
    else:
        items = list(counter or [])
    return {str(key): int(value) for key, value in items}


def summarize_entry_blocker_rows_r4_impl(rows, *, symbol, family, facade):
    blocker_frequency: facade.Counter[str] = facade.Counter()
    blocker_family_frequency: facade.Counter[str] = facade.Counter()
    blocker_family_raw_breakdown: Dict[str, facade.Counter[str]] = facade.defaultdict(facade.Counter)
    no_trade_frequency: facade.Counter[str] = facade.Counter()
    decision_frequency: facade.Counter[str] = facade.Counter()
    by_symbol_counts: Dict[str, facade.Counter[str]] = facade.defaultdict(facade.Counter)
    by_time_bucket: Dict[str, Dict[str, Any]] = facade.defaultdict(lambda: {'blockers': facade.Counter(), 'blocker_families': facade.Counter(), 'family_raw_breakdown': facade.defaultdict(facade.Counter), 'no_trade_codes': facade.Counter(), 'decisions': facade.Counter()})
    by_decision: Dict[str, Dict[str, Any]] = facade.defaultdict(lambda: {'blockers': facade.Counter(), 'blocker_families': facade.Counter(), 'family_raw_breakdown': facade.defaultdict(facade.Counter), 'no_trade_codes': facade.Counter(), 'symbols': facade.Counter()})
    by_symbol_family_raw_breakdown: Dict[str, Dict[str, facade.Counter[str]]] = facade.defaultdict(lambda: facade.defaultdict(facade.Counter))
    scanner_quality_reason_frequency: facade.Counter[str] = facade.Counter()
    scanner_quality_top_symbols: facade.Counter[str] = facade.Counter()
    scanner_quality_suspected_count = 0
    for row in rows:
        final_decision = facade._text(row.get('final_decision') or 'WAIT') or 'WAIT'
        decision_frequency[final_decision] += 1
        symbol_value = facade._text(row.get('symbol') or 'UNKNOWN') or 'UNKNOWN'
        bucket = facade._text(row.get('time_bucket') or 'unknown') or 'unknown'
        no_trade_code = facade._text(row.get('no_trade_code'))
        primary_blockers = facade._list_text(row.get('primary_blockers'))
        blocker_families = facade._list_text(row.get('blocker_families')) or facade._build_blocker_families(primary_blockers, no_trade_code=no_trade_code)
        family_raw_breakdown = dict(row.get('blocker_family_raw_breakdown') or {}) if isinstance(row.get('blocker_family_raw_breakdown'), facade.Mapping) else facade._build_family_raw_breakdown(primary_blockers, no_trade_code=no_trade_code)
        scanner_quality_suspected = bool(row.get('scanner_quality_suspected'))
        scanner_quality_reason = facade._text(row.get('scanner_quality_reason'))
        by_time_bucket[bucket]['decisions'][final_decision] += 1
        by_decision[final_decision]['symbols'][symbol_value] += 1
        if no_trade_code:
            by_decision[final_decision]['no_trade_codes'][no_trade_code] += 1
        for blocker in primary_blockers:
            by_decision[final_decision]['blockers'][blocker] += 1
        for family_name in blocker_families:
            by_decision[final_decision]['blocker_families'][family_name] += 1
        for family_name, raw_values in family_raw_breakdown.items():
            for raw in facade._list_text(raw_values, limit=20):
                by_decision[final_decision]['family_raw_breakdown'][family_name][raw] += 1
        if scanner_quality_suspected:
            scanner_quality_suspected_count += 1
            scanner_quality_top_symbols[symbol_value] += 1
            if scanner_quality_reason:
                scanner_quality_reason_frequency[scanner_quality_reason] += 1
        if final_decision != 'WAIT':
            continue
        if no_trade_code:
            no_trade_frequency[no_trade_code] += 1
            by_symbol_counts[symbol_value][no_trade_code] += 1
            by_time_bucket[bucket]['no_trade_codes'][no_trade_code] += 1
        for blocker in primary_blockers:
            blocker_frequency[blocker] += 1
            by_time_bucket[bucket]['blockers'][blocker] += 1
        for family_name in blocker_families:
            blocker_family_frequency[family_name] += 1
            by_time_bucket[bucket]['blocker_families'][family_name] += 1
        for family_name, raw_values in family_raw_breakdown.items():
            for raw in facade._list_text(raw_values, limit=20):
                blocker_family_raw_breakdown[family_name][raw] += 1
                by_time_bucket[bucket]['family_raw_breakdown'][family_name][raw] += 1
                by_symbol_family_raw_breakdown[symbol_value][family_name][raw] += 1
    symbol_summary = {}
    for symbol_value, no_trade_counter in by_symbol_counts.items():
        symbol_rows = [row for row in rows if facade._text(row.get('symbol')) == symbol_value and facade._text(row.get('final_decision') or 'WAIT') == 'WAIT']
        symbol_summary[symbol_value] = {'run_count': len(symbol_rows), 'decision_frequency': facade._counter_to_dict(facade.Counter((facade._text(row.get('final_decision') or 'WAIT') or 'WAIT' for row in symbol_rows))), 'no_trade_code_frequency': facade._counter_to_dict(no_trade_counter), 'top_blocker_families': facade._counter_to_dict(facade.Counter((family for row in symbol_rows for family_name in facade._list_text(row.get('blocker_families')) or facade._build_blocker_families(row.get('primary_blockers'), no_trade_code=row.get('no_trade_code')) for family in [family_name])).most_common(8)), 'blocker_family_raw_breakdown': facade._nested_counter_to_dict(by_symbol_family_raw_breakdown[symbol_value]), 'top_blockers': facade._counter_to_dict(facade.Counter((blocker for row in symbol_rows for blocker in facade._list_text(row.get('primary_blockers')))).most_common(8)), 'scanner_quality_suspected_count': int(sum((1 for row in symbol_rows if bool(row.get('scanner_quality_suspected')))))}
    return {'row_count': len(rows), 'symbol_filter': facade._text(symbol).upper(), 'family_filter': facade._text(family), 'blocker_family_frequency': facade._counter_to_dict(facade.Counter(dict(blocker_family_frequency.most_common(12)))), 'blocker_family_raw_breakdown': facade._nested_counter_to_dict(blocker_family_raw_breakdown), 'blocker_frequency': facade._counter_to_dict(facade.Counter(dict(blocker_frequency.most_common(16)))), 'no_trade_code_frequency': facade._counter_to_dict(facade.Counter(dict(no_trade_frequency.most_common(16)))), 'decision_frequency': facade._counter_to_dict(decision_frequency), 'scanner_quality_suspected_count': int(scanner_quality_suspected_count), 'scanner_quality_reason_frequency': facade._counter_to_dict(facade.Counter(dict(scanner_quality_reason_frequency.most_common(8)))), 'scanner_quality_top_symbols': facade._counter_to_dict(facade.Counter(dict(scanner_quality_top_symbols.most_common(8)))), 'by_symbol': symbol_summary, 'by_time_bucket': {bucket: {'decision_frequency': facade._counter_to_dict(payload['decisions']), 'blocker_family_frequency': facade._counter_to_dict(facade.Counter(dict(payload['blocker_families'].most_common(8)))), 'blocker_family_raw_breakdown': facade._nested_counter_to_dict(payload['family_raw_breakdown']), 'blocker_frequency': facade._counter_to_dict(facade.Counter(dict(payload['blockers'].most_common(12)))), 'no_trade_code_frequency': facade._counter_to_dict(facade.Counter(dict(payload['no_trade_codes'].most_common(12))))} for bucket, payload in by_time_bucket.items()}, 'by_final_decision': {decision: {'blocker_family_frequency': facade._counter_to_dict(facade.Counter(dict(payload['blocker_families'].most_common(8)))), 'blocker_family_raw_breakdown': facade._nested_counter_to_dict(payload['family_raw_breakdown']), 'blocker_frequency': facade._counter_to_dict(facade.Counter(dict(payload['blockers'].most_common(12)))), 'no_trade_code_frequency': facade._counter_to_dict(facade.Counter(dict(payload['no_trade_codes'].most_common(12)))), 'top_symbols': facade._counter_to_dict(facade.Counter(dict(payload['symbols'].most_common(8))))} for decision, payload in by_decision.items()}, 'symbol_sequence': facade.build_symbol_entry_blocker_sequence(rows, symbol=symbol) if symbol else []}
