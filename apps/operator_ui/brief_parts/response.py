"""Pure already-loaded UI projections; effectful calls remain in core."""
from __future__ import annotations

def prepare_result(result, detail, fallback, attempts, *, facade):
    out = facade._sanitize_operator_brief_result(detail, result, fallback)
    headline = str(out.get('headline') or '').strip()
    fallback_headline = str(fallback.get('headline') or '').strip()
    expected_date = ''
    headline_date = ''
    started_at = str(detail.get('started_at') or '').strip()
    started_match = facade.re.search('\\d{4}-\\d{2}-\\d{2}', started_at)
    headline_match = facade.re.search('\\d{4}-\\d{2}-\\d{2}', headline)
    if started_match:
        expected_date = started_match.group(0)
    if headline_match:
        headline_date = headline_match.group(0)
    if not headline:
        out['headline'] = fallback_headline
    elif expected_date and headline_date and (headline_date != expected_date):
        out['headline'] = fallback_headline
    parsed_output = {
        'headline': str(out.get('headline') or ''),
        'commander_summary': str(out.get('commander_summary') or ''),
        'strategist_summary': str(out.get('strategist_summary') or ''),
        'scanner_summary': str(out.get('scanner_summary') or ''),
        'monitor_summary': str(out.get('monitor_summary') or ''),
        'supervisor_summary': str(out.get('supervisor_summary') or ''),
        'executor_summary': str(out.get('executor_summary') or ''),
        'reporter_summary': str(out.get('reporter_summary') or ''),
        'operator_takeaways': [str(x or '') for x in list(out.get('operator_takeaways') or []) if str(x or '').strip()],
        'executive_summary': str(out.get('executive_summary') or ''),
        'scanner_reason': str(out.get('scanner_reason') or ''),
        'entry_summary': str(out.get('entry_summary') or ''),
        'holding_summary': str(out.get('holding_summary') or ''),
        'exit_plan_summary': str(out.get('exit_plan_summary') or ''),
        'risk_summary': str(out.get('risk_summary') or ''),
        'next_checkpoints': [str(x or '') for x in list(out.get('next_checkpoints') or []) if str(x or '').strip()],
    }
    latency_ms = 0
    if attempts:
        latency_ms = sum((int(row.get('latency_ms') or 0) for row in attempts))
    return (out, parsed_output, latency_ms)

def primary_result(parsed_candidate, fallback, model, parse_meta, *, facade):
    return {
        'status': 'ok',
        'model': model,
        'headline': str(parsed_candidate.get('headline') or fallback.get('headline') or ''),
        'commander_summary': str(parsed_candidate.get('commander_summary') or fallback.get('commander_summary') or ''),
        'strategist_summary': str(parsed_candidate.get('strategist_summary') or fallback.get('strategist_summary') or ''),
        'scanner_summary': str(parsed_candidate.get('scanner_summary') or fallback.get('scanner_summary') or ''),
        'monitor_summary': str(parsed_candidate.get('monitor_summary') or fallback.get('monitor_summary') or ''),
        'supervisor_summary': str(parsed_candidate.get('supervisor_summary') or fallback.get('supervisor_summary') or ''),
        'executor_summary': str(parsed_candidate.get('executor_summary') or fallback.get('executor_summary') or ''),
        'reporter_summary': str(parsed_candidate.get('reporter_summary') or fallback.get('reporter_summary') or ''),
        'operator_takeaways': [str(x or '') for x in list(parsed_candidate.get('operator_takeaways') or [])[:5] if str(x or '').strip()] or list(fallback.get('operator_takeaways') or []),
        'executive_summary': str(parsed_candidate.get('executive_summary') or ''),
        'scanner_reason': str(parsed_candidate.get('scanner_reason') or ''),
        'entry_summary': str(parsed_candidate.get('entry_summary') or ''),
        'holding_summary': str(parsed_candidate.get('holding_summary') or ''),
        'exit_plan_summary': str(parsed_candidate.get('exit_plan_summary') or ''),
        'risk_summary': str(parsed_candidate.get('risk_summary') or ''),
        'next_checkpoints': [str(x or '') for x in list(parsed_candidate.get('next_checkpoints') or [])[:5] if str(x or '').strip()],
        **parse_meta,
        'used_fallback_sections': [],
    }

def repaired_result(repaired, fallback, model, repair_meta, *, facade):
    return {
        'status': 'repaired',
        'model': model,
        'headline': str(repaired.get('headline') or fallback.get('headline') or ''),
        'commander_summary': str(repaired.get('commander_summary') or fallback.get('commander_summary') or ''),
        'strategist_summary': str(repaired.get('strategist_summary') or fallback.get('strategist_summary') or ''),
        'scanner_summary': str(repaired.get('scanner_summary') or fallback.get('scanner_summary') or ''),
        'monitor_summary': str(repaired.get('monitor_summary') or fallback.get('monitor_summary') or ''),
        'supervisor_summary': str(repaired.get('supervisor_summary') or fallback.get('supervisor_summary') or ''),
        'executor_summary': str(repaired.get('executor_summary') or fallback.get('executor_summary') or ''),
        'reporter_summary': str(repaired.get('reporter_summary') or fallback.get('reporter_summary') or ''),
        'operator_takeaways': [str(x or '') for x in list(repaired.get('operator_takeaways') or [])[:5] if str(x or '').strip()] or list(fallback.get('operator_takeaways') or []),
        'executive_summary': str(repaired.get('executive_summary') or ''),
        'scanner_reason': str(repaired.get('scanner_reason') or ''),
        'entry_summary': str(repaired.get('entry_summary') or ''),
        'holding_summary': str(repaired.get('holding_summary') or ''),
        'exit_plan_summary': str(repaired.get('exit_plan_summary') or ''),
        'risk_summary': str(repaired.get('risk_summary') or ''),
        'next_checkpoints': [str(x or '') for x in list(repaired.get('next_checkpoints') or [])[:5] if str(x or '').strip()],
        'reason': 'llm_repair_pass',
        **repair_meta,
        'used_fallback_sections': [],
    }

def line_result(line_parsed, fallback, model, line_meta, *, facade):
    return {
        'status': 'salvaged',
        'model': model,
        'headline': str(line_parsed.get('headline') or fallback.get('headline') or ''),
        'commander_summary': str(line_parsed.get('commander_summary') or fallback.get('commander_summary') or ''),
        'strategist_summary': str(line_parsed.get('strategist_summary') or fallback.get('strategist_summary') or ''),
        'scanner_summary': str(line_parsed.get('scanner_summary') or fallback.get('scanner_summary') or ''),
        'monitor_summary': str(line_parsed.get('monitor_summary') or fallback.get('monitor_summary') or ''),
        'supervisor_summary': str(line_parsed.get('supervisor_summary') or fallback.get('supervisor_summary') or ''),
        'executor_summary': str(line_parsed.get('executor_summary') or fallback.get('executor_summary') or ''),
        'reporter_summary': str(line_parsed.get('reporter_summary') or fallback.get('reporter_summary') or ''),
        'operator_takeaways': [str(x or '') for x in list(line_parsed.get('operator_takeaways') or [])[:5] if str(x or '').strip()] or list(fallback.get('operator_takeaways') or []),
        'executive_summary': str(line_parsed.get('executive_summary') or ''),
        'scanner_reason': str(line_parsed.get('scanner_reason') or ''),
        'entry_summary': str(line_parsed.get('entry_summary') or ''),
        'holding_summary': str(line_parsed.get('holding_summary') or ''),
        'exit_plan_summary': str(line_parsed.get('exit_plan_summary') or ''),
        'risk_summary': str(line_parsed.get('risk_summary') or ''),
        'next_checkpoints': [str(x or '') for x in list(line_parsed.get('next_checkpoints') or [])[:5] if str(x or '').strip()],
        'reason': 'llm_line_repair_pass',
        'parse_mode': 'none',
        **line_meta,
        'used_fallback_sections': [],
    }
