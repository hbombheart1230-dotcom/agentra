"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/trade_bundle_assembly.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def resolve_lifecycle_bundle_sources_r4_impl(*, reports_root, day, anchor_bundle, anchor_run_id, entry_run_id, exit_run_id, facade):
    agents = ('commander', 'strategist', 'scanner', 'monitor', 'supervisor', 'executor')
    artifacts = dict((anchor_bundle.get('artifacts') if isinstance(anchor_bundle.get('artifacts'), dict) else {}) or {})
    canonical_agent_artifacts = dict((anchor_bundle.get('canonical_agent_artifacts') if isinstance(anchor_bundle.get('canonical_agent_artifacts'), dict) else {}) or {})
    evidence_provenance = dict((anchor_bundle.get('evidence_provenance') if isinstance(anchor_bundle.get('evidence_provenance'), dict) else {}) or {})
    resolved_agents: Dict[str, Dict[str, Any]] = {agent: dict(anchor_bundle.get(agent) or {}) if isinstance(anchor_bundle.get(agent), dict) else {} for agent in agents}
    run_cache: Dict[str, Dict[str, Any]] = {}

    def _load_sources(run_id: str) -> Dict[str, Any]:
        rid = str(run_id or '').strip()
        if not rid:
            return {}
        if rid not in run_cache:
            run_cache[rid] = facade.load_run_canonical_artifacts(reports_root=reports_root, run_id=rid, day_hint=day)
        return run_cache[rid]
    for agent in agents:
        canonical_key = f'canonical_{agent}_json'
        for rid in facade.preferred_run_ids_for_agent(agent, anchor_run_id=anchor_run_id, entry_run_id=entry_run_id, exit_run_id=exit_run_id):
            sources = _load_sources(rid)
            paths = dict(sources.get('paths') or {}) if isinstance(sources.get('paths'), dict) else {}
            payloads = dict(sources.get('artifacts') or {}) if isinstance(sources.get('artifacts'), dict) else {}
            if not str(artifacts.get(canonical_key) or '').strip():
                resolved_path = str(paths.get(agent) or '').strip()
                if resolved_path:
                    artifacts[canonical_key] = resolved_path
            if not (isinstance(canonical_agent_artifacts.get(agent), dict) and bool(canonical_agent_artifacts.get(agent))):
                resolved_payload = payloads.get(agent)
                if isinstance(resolved_payload, dict) and bool(resolved_payload):
                    canonical_agent_artifacts[agent] = dict(resolved_payload)
            if not resolved_agents.get(agent):
                if isinstance(canonical_agent_artifacts.get(agent), dict) and bool(canonical_agent_artifacts.get(agent)):
                    resolved_agents[agent] = dict(canonical_agent_artifacts.get(agent) or {})
            if resolved_agents.get(agent) and str(artifacts.get(canonical_key) or '').strip():
                break
        if not str(evidence_provenance.get(agent) or '').strip():
            if str(artifacts.get(canonical_key) or '').strip() or (isinstance(canonical_agent_artifacts.get(agent), dict) and bool(canonical_agent_artifacts.get(agent))):
                evidence_provenance[agent] = 'canonical'
            elif resolved_agents.get(agent):
                evidence_provenance[agent] = 'direct_artifact'
    return {'artifacts': artifacts, 'canonical_agent_artifacts': canonical_agent_artifacts, 'evidence_provenance': evidence_provenance, 'agents': resolved_agents}


def hydrate_live_run_bundle_context_r4_impl(*, reports_root, day, run_id, execution_row, trace_out, reporter_obj, trade_obj, trace_json_path, trace_md_path, trade_json_path, trade_md_path, reporter_json_path, reporter_md_path, operator_summary_json_path, operator_summary_md_path, bundle_ts, facade):
    execution_payload = dict(execution_row.get('payload') or {}) if isinstance(execution_row, facade.Mapping) and isinstance(execution_row.get('payload'), dict) else dict(execution_row or {}) if isinstance(execution_row, facade.Mapping) else {}
    canonical_sources = facade.load_run_canonical_artifacts(reports_root=reports_root, run_id=run_id, day_hint=day)
    commander_preferred = facade._prefer_canonical_payload(canonical_sources, 'commander', dict((trace_out or {}).get('commander') or {}), fallback_source='direct_artifact')
    strategist_preferred = facade._prefer_canonical_payload(canonical_sources, 'strategist', dict((trace_out or {}).get('strategist') or {}), fallback_source='direct_artifact')
    scanner_preferred = facade._prefer_canonical_payload(canonical_sources, 'scanner', dict((trace_out or {}).get('scanner') or {}), fallback_source='direct_artifact')
    monitor_preferred = facade._prefer_canonical_payload(canonical_sources, 'monitor', dict((trace_out or {}).get('monitor') or {}), fallback_source='direct_artifact')
    supervisor_preferred = facade._prefer_canonical_payload(canonical_sources, 'supervisor', dict((trace_out or {}).get('supervisor') or {}), fallback_source='direct_artifact')
    executor_preferred = facade._prefer_canonical_payload(canonical_sources, 'executor', dict((trace_out or {}).get('executor') or {}), fallback_source='direct_artifact')
    merged_execution = facade.build_execution_snapshot(candidates=[execution_payload, dict(executor_preferred.get('payload') or {})], run_id=run_id, ts=str((execution_row or {}).get('ts') or '') if isinstance(execution_row, facade.Mapping) else '')
    bundle_build = facade.build_live_run_bundle(day=day, run_id=run_id, merged_execution=merged_execution, commander_payload=commander_preferred.get('payload') or {}, strategist_payload=strategist_preferred.get('payload') or {}, scanner_payload=scanner_preferred.get('payload') or {}, monitor_payload=monitor_preferred.get('payload') or {}, supervisor_payload=supervisor_preferred.get('payload') or {}, executor_payload=executor_preferred.get('payload') or {}, reporter_trace_payload=dict((trace_out or {}).get('reporter') or {}), reporter_obj=reporter_obj, trade_obj=trade_obj, trace_json_path=trace_json_path, trace_md_path=trace_md_path, trade_json_path=trade_json_path, trade_md_path=trade_md_path, reporter_json_path=reporter_json_path, reporter_md_path=reporter_md_path, operator_summary_json_path=operator_summary_json_path, operator_summary_md_path=operator_summary_md_path, commander_path=str(commander_preferred.get('path') or ''), strategist_path=str(strategist_preferred.get('path') or ''), scanner_path=str(scanner_preferred.get('path') or ''), monitor_path=str(monitor_preferred.get('path') or ''), supervisor_path=str(supervisor_preferred.get('path') or ''), executor_path=str(executor_preferred.get('path') or ''), canonical_sources=canonical_sources)
    bundle_out = dict(bundle_build.get('bundle_out') or {})
    bundle_out['ts'] = str(bundle_ts or '')
    bundle_out['evidence_provenance'] = {'commander': str(commander_preferred.get('source') or ''), 'strategist': str(strategist_preferred.get('source') or ''), 'scanner': str(scanner_preferred.get('source') or ''), 'monitor': str(monitor_preferred.get('source') or ''), 'supervisor': str(supervisor_preferred.get('source') or ''), 'executor': str(executor_preferred.get('source') or ''), 'reporter': 'direct_artifact'}
    return {'bundle_out': bundle_out, 'story_contract': dict(bundle_build.get('story_contract') or {}), 'story_id': str(bundle_build.get('story_id') or ''), 'story_type': str(bundle_build.get('story_type') or 'unknown'), 'canonical_sources': dict(canonical_sources or {})}


def derive_trade_recovery_metadata_r4_impl(*, lifecycle, evidence_completeness, section_provenance, has_substantive_entry_evidence_fn, facade):
    lifecycle_obj = dict(lifecycle or {})
    status = str(lifecycle_obj.get('status') or '').strip().lower()
    entry = lifecycle_obj.get('entry') if isinstance(lifecycle_obj.get('entry'), dict) else {}
    exit_ctx = lifecycle_obj.get('exit') if isinstance(lifecycle_obj.get('exit'), dict) else {}
    entry_present = bool(entry)
    exit_present = bool(exit_ctx)
    missing_sections = {str(x or '') for x in list((evidence_completeness or {}).get('missing_sections') or []) if str(x or '').strip()}
    provenance_sources = {str((value or {}).get('source') or '').strip().lower() for value in dict(section_provenance or {}).values() if isinstance(value, dict)}
    scanner_context = entry.get('scanner_context') if isinstance(entry.get('scanner_context'), dict) else {}
    strategist_context = entry.get('strategist_context') if isinstance(entry.get('strategist_context'), dict) else {}
    inferred_entry = bool(entry.get('inferred_entry'))
    entry_evidence_complete = bool(has_substantive_entry_evidence_fn(entry))
    scanner_selected_symbol = str(scanner_context.get('selected_symbol') or '').strip()
    scanner_summary = str(scanner_context.get('summary') or '').strip().lower()
    strategist_summary = str(strategist_context.get('market_context_summary') or '').strip()
    lifecycle_recovered = status == 'partial' or not entry_present or (status not in {'open'} and (not exit_present)) or (status not in {'open'} and (not entry_evidence_complete))
    recovery_sources = {src for src in provenance_sources if src in {'event_log', 'fallback', 'normalized_trade_artifact'}}
    if lifecycle_recovered:
        recovery_sources.add('partial_lifecycle')
    if not entry_present:
        missing_sections.add('entry')
        recovery_sources.add('entry_missing')
    if status not in {'open'} and (not exit_present):
        missing_sections.add('exit')
        recovery_sources.add('exit_missing')
    if inferred_entry:
        missing_sections.add('entry_evidence')
        recovery_sources.add('inferred_entry')
    if entry_present and (not entry_evidence_complete):
        missing_sections.add('entry_evidence')
        recovery_sources.add('entry_evidence_thin')
    if entry_present and (not scanner_selected_symbol or not scanner_summary or 'not captured' in scanner_summary or ('did not record' in scanner_summary)):
        missing_sections.add('scanner_context')
        recovery_sources.add('scanner_context_missing')
    if entry_present and (not strategist_summary):
        missing_sections.add('strategist_context')
        recovery_sources.add('strategist_context_missing')
    evidence_recovery_used = bool(lifecycle_recovered or missing_sections or recovery_sources)
    return {'trade_origin': 'recovered_partial' if lifecycle_recovered else 'normal_lifecycle', 'lifecycle_completeness': 'partial' if evidence_recovery_used else 'complete', 'evidence_recovery_used': bool(evidence_recovery_used), 'recovery_missing_sections': sorted(missing_sections), 'recovery_sources': sorted(recovery_sources)}
