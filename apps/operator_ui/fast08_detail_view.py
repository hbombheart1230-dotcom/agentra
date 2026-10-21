"""Detail-page provenance over supplied snapshots; never reads artifacts or executes."""
from .data_access_brief import saved_brief_observation as _saved_brief_observation
from .fast08_observation_view import execution_observation, has_observed_payload, safe_trace_link


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
        rows.append({'role':role,'source':source,'declared':declared})
    supervisor=data.get('supervisor') if isinstance(data.get('supervisor'),dict) else {}
    verdict=supervisor.get('verdict') if isinstance(supervisor.get('verdict'),dict) else {}
    executor=data.get('executor') if isinstance(data.get('executor'),dict) else {}
    execution=executor.get('execution') if isinstance(executor.get('execution'),dict) else {}
    commander=data.get('commander') if isinstance(data.get('commander'),dict) else {}
    sync=data.get('portfolio_sync') if isinstance(data.get('portfolio_sync'),dict) else {}
    return {'trace':str(data.get('run_id') or ''),'sources':rows,
            'execution':execution_observation(execution.get('action'),execution.get('status'),verdict.get('allowed'),verdict.get('reason')),
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
