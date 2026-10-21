"""Dashboard presentation over existing GET payloads; never probes source files."""
from .fast08_observation_view import observed_bool, observed_number
from .fast08_detail_view import project_run_row, source_observation


def _count(value):
    number = observed_number(value)
    return number if number is not None and number >= 0 and number == int(number) else None


def project_traces(rows):
    """Count displayed records only; never extrapolate a broker/day total."""
    valid = isinstance(rows, (list, tuple))
    items = [project_run_row(row) for row in rows] if valid else []
    counts = dict.fromkeys(('EXECUTED', 'GUARDED', 'NO_ORDER', 'PENDING', 'FAILED', 'UNKNOWN', 'NO_DATA'), 0)
    for item in items:
        counts[item['execution']['state']] += 1
    return {'items': items, 'counts': counts, 'total': len(items),
            'state': 'OBSERVATIONS' if items else ('NO_DATA' if valid or rows is None else 'MALFORMED'),
            'malformed': sum(item['malformed'] for item in items)}


def project_dashboard(payload):
    raw = payload if isinstance(payload, dict) else {}
    summary = raw.get('operator_summary') if isinstance(raw.get('operator_summary'), dict) else {}
    recon = raw.get('reconciliation') if isinstance(raw.get('reconciliation'), dict) else {}
    system = str(summary.get('system_status') or '').strip().upper()
    if system in {'GREEN','OK','HEALTHY','SUCCESS'}:
        state,tone='SUCCESS','ok'
    elif system in {'RED','FAIL','FAILED','ERROR','CRITICAL'}:
        state,tone='FAILED','critical'
    elif system in {'GUARDED','BLOCKED','DENIED','YELLOW','WARN','WARNING','AMBER'}:
        state,tone='GUARDED','warn'
    elif system=='PENDING':
        state,tone='PENDING','warn'
    else:
        state,tone=('UNKNOWN' if system else 'NO_DATA'),'neutral'
    count=_count(summary.get('executions_total'))
    daily = raw.get('daily') if isinstance(raw.get('daily'), dict) else {}
    blocked = _count(summary.get('blocked_total'))
    if blocked is None:
        blocked = _count(daily.get('blocks'))
    traces = project_traces(raw.get('runs', raw.get('today_trades')))
    source_state = source_observation(summary)
    if source_state in {'STALE', 'ERROR'}:
        state, tone = source_state, ('critical' if source_state == 'ERROR' else 'warn')
    source='SOURCE_REFERENCED' if summary.get('path') else ('LOG_FALLBACK' if system=='LIVE' else 'UNKNOWN_SOURCE')
    numbers=[observed_number(recon.get(k)) for k in ('local_total','broker_total','matched_by_ord_no')]
    local,broker,matched=numbers
    pending=observed_bool(recon.get('pending'))
    if pending is True:
        rstate,rtone,sentence='PENDING','warn',str(recon.get('sentence') or 'Recorded reconciliation is pending.')
    elif any(n is None or n<0 for n in numbers):
        rstate,rtone,sentence='NO_DATA','neutral','Complete reconciliation counters were not captured.'
    elif pending is not False or matched>min(local,broker):
        rstate,rtone,sentence='UNKNOWN','neutral','Completion or count consistency is not established.'
    elif observed_bool(recon.get('broker_window_limited')) is True:
        rstate,rtone,sentence='PENDING','warn','Broker query window is limited; full alignment is not established.'
    elif max(local,broker)==0:
        observed=observed_bool(recon.get('observed')) is True
        rstate,rtone=('NO_EXECUTIONS' if observed else 'NO_DATA'),'neutral'
        sentence='No executions in the observed source.' if observed else 'Zero counters may be defaults; source presence was not independently recorded.'
    elif local==broker==matched:
        rstate,rtone,sentence='SUCCESS','ok','Recorded local and broker counters align.'
    elif matched>0:
        rstate,rtone,sentence='PENDING','warn','Partial reconciliation; inspect unmatched executions.'
    else:
        rstate,rtone,sentence='FAILED','critical','Recorded executions have no broker matches.'
    return {'traces':traces, 'source_state':source_state,
            'run_total':_count(summary.get('run_total')), 'blocked_total':blocked, 'approvals':_count(daily.get('approvals')),
            'system':{'state':state,'tone':tone},'executions':{'value':count,'source':source},
            'reconciliation':{'state':rstate,'tone':rtone,'sentence':sentence,'local':local,'broker':broker,
                              'matched':matched,'base':max(local or 0,broker or 0),'source':'OBSERVED' if recon.get('observed') is True else 'COUNTERS_ONLY'}}
