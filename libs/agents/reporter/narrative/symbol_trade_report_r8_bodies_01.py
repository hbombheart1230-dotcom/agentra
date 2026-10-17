"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/symbol_trade_report.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def _clean_symbol_reason_r4_impl(value, *, axis, facade):
    text = str(value or '').strip()
    if not text:
        return ''
    lowered = text.lower()
    if axis == 'entry' and (lowered.startswith('entry reason was not captured') or lowered.startswith('entry evidence was not captured') or lowered.startswith('entry context was recovered')):
        return ''
    if axis == 'exit' and ('position is still open' in lowered or '포지션은 아직 열려' in text or '청산 근거가 누락' in text):
        return ''
    return facade._operator_reason_name(text)


def _actual_entry_reason_from_artifacts_r4_impl(*, report_path, report_entry_summary, bundle, feedback, facade):
    summary_input = facade._read_json(facade._summary_input_path_for_report(report_path))
    decision_flow = summary_input.get('decision_flow') if isinstance(summary_input.get('decision_flow'), dict) else {}
    for value in (decision_flow.get('monitor_fallback_reason'), decision_flow.get('actual_entry_reason'), decision_flow.get('entry_trigger'), facade._dict_at(bundle, 'lifecycle', 'entry', 'monitor_context').get('trigger_type'), facade._dict_at(bundle, 'lifecycle', 'entry', 'monitor_context').get('entry_reason'), facade._dict_at(bundle, 'entry', 'monitor_context').get('trigger_type'), facade._dict_at(bundle, 'entry', 'monitor_context').get('entry_reason'), feedback.get('entry_reason')):
        text = str(value or '').strip()
        if text:
            return text
    for source in (decision_flow.get('entry_confidence'), decision_flow.get('entry_reason'), report_entry_summary):
        text = str(source or '')
        for pattern in ('실제 트리거는\\s+(.+?)(?:였|이었|입니다|였습니다)', '실제 엔트리 경로는\\s+(.+?)(?:였|이었|입니다|였습니다)', '실제 엔트리는\\s+(.+?)(?:에서\\s+확정|로\\s+확정|으로\\s+확정)'):
            match = facade.re.search(pattern, text)
            if match:
                return match.group(1).strip(' .')
    return ''


def _collect_symbol_event_insights_r4_impl(events_path, symbol, *, facade):
    normalized_symbol = str(symbol or '').strip().upper()
    wait_reasons: facade.Counter[str] = facade.Counter()
    entry_reasons: facade.Counter[str] = facade.Counter()
    exit_reasons: facade.Counter[str] = facade.Counter()
    for row in facade._iter_jsonl(events_path):
        payload = row.get('payload') if isinstance(row.get('payload'), dict) else {}
        event = str(row.get('event') or '').strip()
        stage = str(row.get('stage') or '').strip()
        if stage == 'monitor' and event == 'entry_decision_detail':
            detail = payload.get('payload') if isinstance(payload.get('payload'), dict) else payload
            symbol_value = str(detail.get('symbol') or payload.get('symbol') or '').strip().upper()
            if symbol_value != normalized_symbol:
                continue
            decision = str(detail.get('decision') or '').strip().upper()
            reason = str(detail.get('reason') or '').strip()
            if decision == 'WAIT' and reason:
                wait_reasons[reason] += 1
            elif decision == 'BUY' and reason:
                clean_reason = facade._clean_symbol_reason(reason, axis='entry')
                if clean_reason:
                    entry_reasons[clean_reason] += 1
            continue
        if stage == 'monitor' and event in {'exit_decision_detail', 'state_transition'}:
            detail = payload.get('payload') if isinstance(payload.get('payload'), dict) else payload
            symbol_value = str(detail.get('symbol') or payload.get('symbol') or '').strip().upper()
            if symbol_value != normalized_symbol:
                continue
            reason = str(detail.get('final_reason') or detail.get('current_reason') or detail.get('triggered_rule') or '').strip()
            if reason:
                clean_reason = facade._clean_symbol_reason(reason, axis='exit')
                if clean_reason:
                    exit_reasons[clean_reason] += 1
    return {'recent_wait_reasons': [name for name, _count in wait_reasons.most_common(5)], 'recent_entry_reasons': [name for name, _count in entry_reasons.most_common(5)], 'recent_exit_reasons': [name for name, _count in exit_reasons.most_common(5)], 'common_monitor_failures': [name for name, _count in wait_reasons.most_common(5)], 'wait_reason_distribution': dict(wait_reasons)}


def build_symbol_trade_summary_r4_impl(events_path, reports_root, symbol, *, facade):
    normalized_symbol = str(symbol or '').strip().upper()
    history = facade._build_history_index(reports_root, normalized_symbol)
    insights = facade._collect_symbol_event_insights(events_path, normalized_symbol)
    recent_playbooks: List[str] = []
    for row in reversed(history):
        playbook = str(row.get('playbook') or '').strip()
        if playbook and playbook not in recent_playbooks:
            recent_playbooks.append(playbook)
        if len(recent_playbooks) >= 5:
            break
    history_entry_reasons = [facade._clean_symbol_reason(row.get('entry_reason'), axis='entry') for row in reversed(history) if facade._clean_symbol_reason(row.get('entry_reason'), axis='entry')]
    history_exit_reasons = [facade._clean_symbol_reason(row.get('exit_reason'), axis='exit') for row in reversed(history) if facade._clean_symbol_reason(row.get('exit_reason'), axis='exit')]
    recent_trade_headlines = [str(row.get('brief_headline') or row.get('report_headline') or '').strip() for row in reversed(history) if str(row.get('brief_headline') or row.get('report_headline') or '').strip()]
    recent_operator_viewpoints = [str(row.get('brief_executive_summary') or row.get('report_final_conclusion') or '').strip() for row in reversed(history) if str(row.get('brief_executive_summary') or row.get('report_final_conclusion') or '').strip()]
    entry_pattern_types = [facade._clean_symbol_pattern(row.get('entry_pattern_type'), axis='entry', fallback_reason=row.get('entry_reason')) for row in reversed(history) if facade._clean_symbol_pattern(row.get('entry_pattern_type'), axis='entry', fallback_reason=row.get('entry_reason'))]
    exit_pattern_types = [facade._clean_symbol_pattern(row.get('exit_pattern_type'), axis='exit', fallback_reason=row.get('exit_reason')) for row in reversed(history) if facade._clean_symbol_pattern(row.get('exit_pattern_type'), axis='exit', fallback_reason=row.get('exit_reason'))]
    improvement_tag_counter: facade.Counter[str] = facade.Counter()
    review_flag_counter: facade.Counter[str] = facade.Counter()
    for row in history:
        for tag in list(row.get('improvement_tags') or []):
            text = str(tag or '').strip()
            if text:
                improvement_tag_counter[text] += 1
        for flag in list(row.get('review_flags') or []):
            text = str(flag or '').strip()
            if text:
                review_flag_counter[text] += 1
    completed = [row for row in history if str(row.get('status') or '').strip().lower() == 'closed']
    returns = [value for value in (facade._safe_float(row.get('result_pct')) for row in completed) if value is not None]
    holds = [value for value in (facade._safe_float(row.get('hold_seconds')) for row in completed) if value is not None]
    win_count = sum((1 for value in returns if value > 0))
    loss_count = sum((1 for value in returns if value < 0))
    summary = {'trade_count': len(history), 'completed_trade_count': len(completed), 'win_count': win_count, 'loss_count': loss_count, 'avg_return_pct': round(sum(returns) / len(returns), 4) if returns else 0.0, 'avg_hold_seconds': round(sum(holds) / len(holds), 2) if holds else 0.0, 'recent_playbooks': recent_playbooks, 'recent_entry_reasons': list(insights.get('recent_entry_reasons') or history_entry_reasons[:5]), 'recent_exit_reasons': list(insights.get('recent_exit_reasons') or history_exit_reasons[:5]), 'recent_wait_reasons': list(insights.get('recent_wait_reasons') or []), 'wait_reason_distribution': dict(insights.get('wait_reason_distribution') or {}), 'recent_trade_headlines': facade._list_text(recent_trade_headlines, limit=5), 'recent_operator_viewpoints': facade._list_text(recent_operator_viewpoints, limit=5)}
    risk_notes: List[str] = []
    if summary['trade_count'] == 0:
        risk_notes.append('저장된 거래 이력이 아직 없어 전략 피드백 근거가 제한적입니다.')
    if summary['completed_trade_count'] > 0 and summary['avg_return_pct'] < 0:
        risk_notes.append('완료된 거래 기준 평균 수익률이 음수여서 동일한 접근의 재사용은 보수적으로 해석해야 합니다.')
    if len(summary['recent_wait_reasons']) >= 3:
        risk_notes.append('대기 사유가 반복적으로 누적되고 있어 진입 구조와 분봉 조건의 적합성을 점검할 필요가 있습니다.')
    payload = {'schema_version': 'symbol_trade_report.v1', 'symbol': normalized_symbol, 'summary': summary, 'pattern_insights': {'successful_entry_patterns': facade._pattern_rows(history, positive=True), 'failed_entry_patterns': facade._pattern_rows(history, positive=False), 'common_monitor_failures': list(insights.get('common_monitor_failures') or []), 'recent_entry_pattern_types': facade._list_text(entry_pattern_types, limit=5), 'recent_exit_pattern_types': facade._list_text(exit_pattern_types, limit=5), 'recent_improvement_tags': [name for name, _count in improvement_tag_counter.most_common(6)], 'recent_review_flags': [name for name, _count in review_flag_counter.most_common(6)], 'risk_notes': risk_notes}, 'history_index': history}
    return payload


def build_daily_trade_index_r4_impl(reports_root, day, *, facade):
    out: List[Dict[str, Any]] = []
    target_day = str(day or '').strip()
    for _path, obj in facade._iter_trade_lifecycles_for_day(reports_root, target_day):
        if str(obj.get('day') or '').strip() != target_day:
            continue
        summary = obj.get('summary') if isinstance(obj.get('summary'), dict) else {}
        entry = obj.get('entry') if isinstance(obj.get('entry'), dict) else {}
        exit_row = obj.get('exit') if isinstance(obj.get('exit'), dict) else {}
        out.append({'trade_id': str(obj.get('trade_id') or ''), 'symbol': str(obj.get('symbol') or ''), 'date': target_day, 'status': str(obj.get('status') or ''), 'entry_run_id': str(entry.get('run_id') or ''), 'exit_run_id': str(exit_row.get('run_id') or ''), 'entry_reason': facade._clean_symbol_reason(summary.get('entry_reason_human'), axis='entry'), 'exit_reason': facade._clean_symbol_reason(summary.get('exit_reason_human'), axis='exit')})
    carryover_index = facade._read_json(facade.resolve_trade_day_root(reports_root, target_day) / 'carryover_exit_index.json')
    for item in list(carryover_index.get('rows') or []):
        if not isinstance(item, dict):
            continue
        trade_id = str(item.get('trade_id') or '').strip()
        if trade_id and any((str(row.get('trade_id') or '') == trade_id for row in out)):
            continue
        out.append(dict(item))
    out.sort(key=lambda row: (str(row.get('symbol') or ''), str(row.get('trade_id') or '')))
    return out
