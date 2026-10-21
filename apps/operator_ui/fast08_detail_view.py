"""Detail-page provenance over supplied snapshots; never reads artifacts or executes."""
from .data_access_brief import saved_brief_observation as _saved_brief_observation
from urllib.parse import quote
from .fast08_observation_view import execution_observation, has_observed_payload, observed_number, safe_trace_link



def source_observation(payload):
    """Describe only supplied source flags; paths never establish freshness."""
    data = payload if isinstance(payload, dict) else {}
    if data.get('reader_error') or data.get('source_error'):
        return 'ERROR'
    if data.get('stale') is True or data.get('source_status') == 'stale':
        return 'STALE'
    if data.get('found') is False or not has_observed_payload(data):
        return 'MISSING'
    if data.get('source') == 'fallback' or data.get('source_status') == 'fallback':
        return 'FALLBACK'
    return 'UNKNOWN'


def recorded_execution(action, status, allowed=None, reason=''):
    """Recorded fill is distinct from generic success or permission to execute."""
    view = execution_observation(action, status, allowed, reason)
    raw = view['raw_status']
    if view['state'] == 'SUCCESS':
        # A generic ok/completed is not a fill receipt, even if allowed=True.
        if raw in {'filled', 'executed'}:
            view.update(state='EXECUTED', tone='neutral')
        else:
            view.update(state='UNKNOWN', tone='neutral')
    elif view['state'] == 'NO_ORDER' and raw in {'filled', 'executed', 'partially_filled'}:
        view.update(state='UNKNOWN', tone='neutral')
    return view


def run_trace_link(run_id):
    if isinstance(run_id, bool) or not isinstance(run_id, (str, int)):
        return ''
    value = str(run_id)
    if not value.strip() or value in {'.', '..'} or '/' in value or '\\' in value:
        return ''
    return safe_trace_link('/runs/' + quote(value, safe=''))


def project_run_row(raw):
    """Normalize one list/trade row without changing source values or authority."""
    row = raw if isinstance(raw, dict) else {}
    execution = recorded_execution(row.get('execution_action', row.get('action')),
        row.get('execution_status', row.get('status')), row.get('supervisor_allowed'), row.get('guard_reason'))
    coverage = observed_number(row.get('feature_coverage_ratio'))
    if coverage is not None and not 0 <= coverage <= 1:
        coverage = None
    flags = row.get('macro_stress_flags')
    flags = flags if isinstance(flags, (list, tuple)) else []
    return {'coverage': coverage, 'flags': flags, 'row': row, 'execution': execution, 'source': source_observation(row),
            'run_link': run_trace_link(row.get('run_id')), 'artifact': artifact_observation(row),
            'brief_link': safe_trace_link(row.get('operator_brief_link')) if row.get('operator_brief_available') is True else '',
            'malformed': not isinstance(raw, dict)}


def artifact_observation(raw):
    data=raw if isinstance(raw,dict) else {}
    link = safe_trace_link(data.get('report_link'))
    available = data.get('report_available') is True and bool(link) and data.get('found') is not False
    state = 'OBSERVED' if available else ('UNKNOWN' if data.get('report_available') is True else 'NO_DATA')
    return {'state': state, 'tone': 'neutral', 'link': link if available else '',
            'label': 'Linked artifact observed' if available else (
                'UNKNOWN — linked artifact not confirmed' if state == 'UNKNOWN' else 'NO_DATA — no linked AI artifact')}


def saved_brief_observation(payload, *, sections=None):
    """Retain status diagnostics, but distinguish saved content from metadata."""
    raw = payload if isinstance(payload, dict) else {}
    saved = raw.get('sections') if isinstance(raw.get('sections'), dict) else {}
    derived = sections if isinstance(sections, dict) else {}
    result = _saved_brief_observation(raw, sections=sections)
    if has_observed_payload(saved):
        source = 'saved_artifact'
    elif has_observed_payload(derived):
        source = 'derived_view'
    else:
        source = 'unknown' if raw else 'missing'
    result['source_class'] = source
    if result['state'] in {'SAVED', 'DERIVED', 'NO_DATA'}:
        result['state'] = {'saved_artifact': 'SAVED', 'derived_view': 'DERIVED',
                           'unknown': 'NO_DATA', 'missing': 'NO_DATA'}[source]
    return result



def project_run(detail):
    data=detail if isinstance(detail,dict) else {}
    provenance=data.get('artifact_provenance') if isinstance(data.get('artifact_provenance'),dict) else {}
    rows=[]
    for role in ('commander','strategist','scanner','monitor','supervisor','executor','reporter'):
        payload=data.get(role)
        declared=str(provenance.get(role) or '')
        source=declared if declared in {'canonical','normalized_trade_artifact','event_log','direct_artifact','fallback'} else 'UNKNOWN'
        if not has_observed_payload(payload) or isinstance(payload,dict) and payload.get('found') is False:
            source='MISSING'
        rows.append({'role':role,'source':source,'declared':declared,'health':source_observation(payload)})
    supervisor=data.get('supervisor') if isinstance(data.get('supervisor'),dict) else {}
    verdict=supervisor.get('verdict') if isinstance(supervisor.get('verdict'),dict) else {}
    executor=data.get('executor') if isinstance(data.get('executor'),dict) else {}
    execution=executor.get('execution') if isinstance(executor.get('execution'),dict) else {}
    commander=data.get('commander') if isinstance(data.get('commander'),dict) else {}
    sync=data.get('portfolio_sync') if isinstance(data.get('portfolio_sync'),dict) else {}
    return {'trace':str(data.get('run_id') or ''),'sources':rows,'run_link':run_trace_link(data.get('run_id')),
            'source_status':source_observation(sync),
            'execution':recorded_execution(execution.get('action'),execution.get('status'),verdict.get('allowed'),verdict.get('reason')),
            'decision_intent':commander.get('command_intent') if commander.get('command_intent') is not None and commander.get('command_intent') != '' else commander.get('path'),
            'reader_source':sync.get('positions_source_label'),
            'reader_error':str(sync.get('reader_error') or ''),'artifact':artifact_observation(data.get('trade_report')),
            'notice':'Decision, guard and executor records are separate observations; an intent is not a fill.'}


def project_trade(report):
    data=report if isinstance(report,dict) else {}
    artifact=artifact_observation(data)
    return {'trace':str(data.get('run_id') or ''),'sources':[{'role':'AI report','source':'linked_artifact' if artifact['state']=='OBSERVED' else 'MISSING','declared':''}],
            'artifact':artifact,'execution':None,'reader_error':'',
            'notice':'Saved report narrative is not an approval or execution receipt.'}
