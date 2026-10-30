from __future__ import annotations


def validate_trade_artifact_chain(reports_root, day, trade_id, *, facade):
    ctx = facade._resolve_trade_context(reports_root, day, trade_id)
    trade_paths, entry_payload, exit_payload = ctx['trade_paths'], ctx['entry_payload'], ctx['exit_payload']
    hold_payload, lifecycle_bundle, story_input = ctx['hold_payload'], ctx['lifecycle_bundle'], ctx['story_input']
    report, provenance, health = ctx['report'], ctx['provenance'], ctx['health']
    failures, warnings = [], []
    artifact_exists = {k: trade_paths[k].exists() for k in ('entry_json','hold_json','exit_json','lifecycle_bundle_json','ai_trade_report_input_json','ai_trade_report_json','ai_trade_report_md')}
    for key, exists in artifact_exists.items():
        if not exists: failures.append(f'missing_artifact:{key}')
    authoritative_status = str(provenance.get('lifecycle_status') or health.get('lifecycle_status') or lifecycle_bundle.get('trade_lifecycle_status') or lifecycle_bundle.get('status') or '').strip().lower()
    closed_trade = facade._is_closed_trade({**lifecycle_bundle, 'trade_lifecycle_status': authoritative_status or lifecycle_bundle.get('trade_lifecycle_status')}, exit_payload)
    entry_evidence = facade._has_substantive_entry_evidence(entry_payload)
    exit_evidence = facade._has_substantive_exit_evidence(exit_payload)
    linked_run_ids = [str(v or '').strip() for v in list(lifecycle_bundle.get('linked_run_ids') or []) if str(v or '').strip()]
    trace = story_input.get('scanner_selection_trace') if isinstance(story_input.get('scanner_selection_trace'), dict) else {}
    selected_rank = facade._safe_int(story_input.get('selected_rank'), facade._safe_int(trace.get('selected_rank')))
    candidate_count = facade._safe_int(story_input.get('candidate_count'), facade._safe_int(trace.get('candidate_count')))
    selected_symbol = str(story_input.get('selected_symbol') or trace.get('selected_symbol') or story_input.get('symbol') or '').strip()
    hold_duration = str(hold_payload.get('hold_duration') or lifecycle_bundle.get('hold_duration') or story_input.get('hold_duration') or '').strip()
    hold_duration_sec = hold_payload.get('hold_duration_sec')
    if hold_duration_sec in (None, ''): hold_duration_sec = lifecycle_bundle.get('hold_duration_sec')
    if hold_duration_sec in (None, ''): hold_duration_sec = story_input.get('hold_duration_sec')
    hold_duration_sec_int = facade._safe_int(hold_duration_sec, default=-1)
    story_status, story_action = str(story_input.get('status') or '').strip().lower(), str(story_input.get('action') or '').strip().upper()
    if closed_trade and not str(exit_payload.get('run_id') or '').strip(): failures.append('closed_trade_missing_exit_run_id')
    if closed_trade and not linked_run_ids: failures.append('closed_trade_missing_linked_run_ids')
    if closed_trade and entry_evidence and not str(entry_payload.get('run_id') or '').strip(): failures.append('closed_trade_missing_entry_run_id')
    if closed_trade and entry_evidence and not str(entry_payload.get('ts') or '').strip(): failures.append('closed_trade_missing_entry_ts')
    if closed_trade and not str(exit_payload.get('ts') or '').strip(): failures.append('closed_trade_missing_exit_ts')
    if closed_trade and entry_evidence:
        if hold_duration in {'','00:00:00','0초','0.0m','0m'}: failures.append('closed_trade_fake_or_missing_hold_duration')
        if hold_duration_sec_int == 0: failures.append('closed_trade_zero_hold_duration_sec')
    if closed_trade and selected_rank <= 0: failures.append('closed_trade_selected_rank_zero')
    if closed_trade and candidate_count <= 0: failures.append('closed_trade_candidate_count_zero')
    if authoritative_status and story_status and story_status != authoritative_status: failures.append('story_input_status_conflicts_with_authoritative_status')
    if authoritative_status == 'open' and not exit_evidence and story_action == 'SELL': failures.append('story_input_action_conflicts_with_open_trade')
    if selected_symbol and selected_symbol != str(story_input.get('symbol') or '').strip(): failures.append('selected_symbol_mismatch_story_symbol')
    generation = report.get('generation') if isinstance(report.get('generation'), dict) else {}
    if report and str(generation.get('status') or '').strip().lower() not in {'ok','partial','salvaged','repaired'}: failures.append('ai_trade_report_generation_status_bad')
    if report and facade._section_provenance_all_fallback(report): failures.append('ai_trade_report_all_section_provenance_fallback')
    linkage = lifecycle_bundle.get('same_day_reporter_linkage') if isinstance(lifecycle_bundle.get('same_day_reporter_linkage'), dict) else {}
    if linkage and str(linkage.get('status') or '').strip().lower() == 'missing' and (str(linkage.get('reporter_analysis_json_path') or '').strip() or str(linkage.get('reporter_analysis_md_path') or '').strip()): failures.append('reporter_linkage_missing_but_artifact_path_populated')
    trade_origin = str(provenance.get('trade_origin') or lifecycle_bundle.get('trade_origin') or '').strip()
    completeness = str(provenance.get('lifecycle_completeness') or lifecycle_bundle.get('lifecycle_completeness') or '').strip()
    if closed_trade and entry_evidence and trade_origin == 'recovered_partial': warnings.append('trade_origin_is_recovered_partial_even_with_entry_evidence')
    if closed_trade and not entry_evidence and completeness != 'partial': failures.append('thin_entry_evidence_not_marked_partial')
    return {'day':day,'trade_id':trade_id,'closed_trade':closed_trade,'authoritative_status':authoritative_status,'entry_run_id':str(entry_payload.get('run_id') or '').strip(),'exit_run_id':str(exit_payload.get('run_id') or '').strip(),'linked_run_ids':linked_run_ids,'selected_symbol':selected_symbol,'selected_rank':selected_rank,'candidate_count':candidate_count,'hold_duration':hold_duration,'hold_duration_sec':None if hold_duration_sec in (None,'') else hold_duration_sec_int,'trade_origin':trade_origin,'lifecycle_completeness':completeness,'artifact_exists':artifact_exists,'failures':failures,'warnings':warnings,'ok':len(failures)==0}
