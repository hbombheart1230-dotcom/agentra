"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/trade_bundle_state.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def _safe_float_r4_impl(value, *, facade):
    if value in (None, ''):
        return None
    try:
        return float(value)
    except Exception:
        return None


def _first_positive_r4_impl(*values, facade):
    for value in values:
        num = facade._safe_float(value)
        if num is not None and num > 0:
            return float(num)
    return None


def _exit_monitor_reference_price_r4_impl(payload, execution_details, *, facade):
    monitor_context = payload.get('monitor_context') if isinstance(payload.get('monitor_context'), facade.Mapping) else {}
    quote_snapshot = execution_details.get('quote_snapshot') if isinstance(execution_details.get('quote_snapshot'), facade.Mapping) else {}
    return facade._first_positive(monitor_context.get('current_price'), monitor_context.get('price'), quote_snapshot.get('current_price'), quote_snapshot.get('best_bid'), quote_snapshot.get('best_ask'))


def _backfill_execution_fields_r4_impl(payload, execution_details, *, facade):
    out = dict(payload or {})
    details = dict(execution_details or {})
    for key in ('order_id', 'order_status', 'filled_qty', 'avg_price', 'filled_price'):
        if out.get(key) in (None, '') and details.get(key) not in (None, ''):
            out[key] = details.get(key)
    is_sell = str(out.get('action') or details.get('action') or '').strip().upper() == 'SELL'
    monitor_exit_price = facade._exit_monitor_reference_price(out, details) if is_sell else None
    broker_fill_price = facade._first_positive(details.get('filled_price'), details.get('broker_fill_price'))
    if out.get('price') in (None, ''):
        if broker_fill_price is not None:
            out['price'] = broker_fill_price
        elif is_sell and monitor_exit_price is not None:
            out['price'] = monitor_exit_price
            out.setdefault('price_basis', 'monitor_current_price_fallback')
        else:
            for key in ('avg_price', 'broker_buy_price'):
                if details.get(key) not in (None, ''):
                    out['price'] = details.get(key)
                    break
    elif is_sell and broker_fill_price is None and (monitor_exit_price is not None):
        existing_price = facade._safe_float(out.get('price'))
        avg_price = facade._safe_float(details.get('avg_price') if details.get('avg_price') not in (None, '') else out.get('avg_price'))
        if existing_price is not None and avg_price is not None and (abs(existing_price - avg_price) < 0.5) and (abs(existing_price - monitor_exit_price) >= 0.5):
            out['price'] = monitor_exit_price
            out.setdefault('price_basis', 'monitor_current_price_fallback')
    for key in ('broker_realized_pnl', 'broker_realized_pnl_pct', 'broker_fee', 'broker_tax', 'broker_day_truth_source', 'broker_day_match_mode', 'broker_day_authoritative'):
        if out.get(key) in (None, '') and details.get(key) not in (None, ''):
            out[key] = details.get(key)
    return out


def build_component_fingerprint_r4_impl(*, component, trade_id, run_id, lifecycle_status, story_type, model, story_input, compact_input, facade):
    story_hash = facade.payload_fingerprint(facade._normalize_story_input_for_fingerprint(story_input))
    compact_hash = facade.payload_fingerprint(dict(compact_input or {}))
    payload = {'component': str(component or ''), 'trade_id': str(trade_id or ''), 'run_id': str(run_id or ''), 'lifecycle_status': str(lifecycle_status or ''), 'story_type': str(story_type or ''), 'model': str(model or ''), 'story_input_sha256': story_hash, 'compact_input_sha256': compact_hash}
    return {'fingerprint': facade.payload_fingerprint(payload), 'source_inputs': {'story_input_sha256': story_hash, 'compact_input_sha256': compact_hash}, 'payload': payload}


def build_ai_trade_report_generation_component_r4_impl(*, fingerprint, trade_id, run_id, status, report_status, report_generation_reason, model, report_json_path, report_md_path, llm_response_path, source_inputs, updated_at, facade):
    return {'fingerprint': str(fingerprint or ''), 'component': 'ai_trade_report', 'status': str(status or 'skipped'), 'report_status': str(report_status or ''), 'skip_reason': 'fingerprint_match_existing_success' if str(report_generation_reason or '') == 'fingerprint_match_existing_success' else '', 'trade_id': str(trade_id or ''), 'run_id': str(run_id or ''), 'updated_at': str(updated_at or facade._utc_now_iso()), 'model': str(model or ''), 'report_json_path': str(report_json_path or ''), 'report_md_path': str(report_md_path or ''), 'llm_response_path': str(llm_response_path or ''), 'source_inputs': dict(source_inputs or {})}


def build_operator_brief_generation_component_r4_impl(*, trade_id, run_id, llm_brief_status, report_json_path, report_md_path, llm_response_path, brief_json_exists, brief_md_exists, brief_llm_exists, updated_at, facade):
    fingerprint_payload = {'component': 'operator_brief', 'trade_id': str(trade_id or ''), 'run_id': str(run_id or ''), 'brief_json_exists': bool(brief_json_exists), 'brief_md_exists': bool(brief_md_exists), 'brief_llm_exists': bool(brief_llm_exists), 'brief_llm_status': str(llm_brief_status or 'skipped')}
    return {'fingerprint': facade.payload_fingerprint(fingerprint_payload), 'component': 'operator_brief', 'status': str(llm_brief_status or 'skipped'), 'skip_reason': 'existing_artifact_state_reused' if brief_json_exists or brief_md_exists or brief_llm_exists else 'missing_brief_artifact', 'trade_id': str(trade_id or ''), 'run_id': str(run_id or ''), 'updated_at': str(updated_at or facade._utc_now_iso()), 'report_json_path': str(report_json_path or ''), 'report_md_path': str(report_md_path or ''), 'llm_response_path': str(llm_response_path or '')}


def build_generation_state_r4_impl(*, current_state, ai_trade_report_component, operator_brief_component, facade):
    state = dict(current_state or {})
    state['schema_version'] = str(state.get('schema_version') or 'report_generation_state.v1')
    components = dict(state.get('components') or {}) if isinstance(state.get('components'), facade.Mapping) else {}
    components['ai_trade_report'] = dict(ai_trade_report_component or {})
    components['operator_brief'] = dict(operator_brief_component or {})
    state['components'] = components
    return state


def _source_type_r4_impl(raw_source, source_path, *, facade):
    src = str(raw_source or '').strip().lower()
    path_text = str(source_path or '').strip()
    if src == 'canonical':
        return 'canonical'
    if src in {'normalized_trade_artifact', 'normalized_trade', 'direct_artifact', 'direct'}:
        return 'trade'
    if src in {'event_log'}:
        return 'events'
    if path_text:
        return 'trade'
    return 'missing'


def build_bundle_provenance_r4_impl(*, trade_id, run_id, day, lifecycle_status, recovery_metadata, strategy_anchor_run_id, evidence_source, agent_sources, section_provenance, artifacts, facade):
    section_map = dict(section_provenance or {})
    artifact_map = dict(artifacts or {})
    recovery = dict(recovery_metadata or {})
    return {'schema_version': 'trade_provenance.v1', 'trade_id': str(trade_id or ''), 'run_id': str(run_id or ''), 'day': str(day or ''), 'lifecycle_status': str(lifecycle_status or ''), 'trade_origin': str(recovery.get('trade_origin') or ''), 'lifecycle_completeness': str(recovery.get('lifecycle_completeness') or ''), 'evidence_recovery_used': bool(recovery.get('evidence_recovery_used')), 'recovery_missing_sections': list(recovery.get('recovery_missing_sections') or []), 'recovery_sources': list(recovery.get('recovery_sources') or []), 'entry_strategist_run_id': str(strategy_anchor_run_id or ''), 'strategy_anchor_run_id': str(strategy_anchor_run_id or ''), 'evidence_source': str(evidence_source or 'fallback'), 'agent_sources': dict(agent_sources or {}), 'section_provenance': section_map, 'read_precedence': ['normalized_trade_artifact', 'canonical_artifact', 'event_log', 'missing'], 'section_resolution': {str(key): {'source_type': facade._source_type((value or {}).get('source'), (value or {}).get('artifact_path')), 'source_path': str((value or {}).get('artifact_path') or ''), 'confidence': str((value or {}).get('confidence') or 'low')} for key, value in section_map.items()}, 'canonical_agent_artifact_paths': {key: str(value or '') for key, value in artifact_map.items() if str(key).startswith('canonical_') and str(key).endswith('_json')}}


def build_bundle_health_r4_impl(*, trade_id, run_id, day, lifecycle_status, recovery_metadata, diagnostics, report_generation, evidence_completeness_missing_sections, phase3_missing_sections, phase3_completeness_score, artifact_presence, ai_trade_report_llm_artifact, strategist_event_count, scanner_event_count, monitor_event_count, operator_brief_json_exists, facade):
    recovery = dict(recovery_metadata or {})
    diagnostics_obj = dict(diagnostics or {})
    llm_artifact = dict(ai_trade_report_llm_artifact or {})
    missing_sections = [str(x or '') for x in list(phase3_missing_sections or []) + [str(x or '') for x in list(evidence_completeness_missing_sections or []) if str(x or '').strip()] if str(x or '').strip()]
    return {'schema_version': 'trade_health.v1', 'trade_id': str(trade_id or ''), 'run_id': str(run_id or ''), 'day': str(day or ''), 'lifecycle_status': str(lifecycle_status or ''), 'trade_origin': str(recovery.get('trade_origin') or ''), 'lifecycle_completeness': str(recovery.get('lifecycle_completeness') or ''), 'evidence_recovery_used': bool(recovery.get('evidence_recovery_used')), 'recovery_missing_sections': list(recovery.get('recovery_missing_sections') or []), 'recovery_sources': list(recovery.get('recovery_sources') or []), 'ai_report_diagnostics': diagnostics_obj, 'report_generation': dict(report_generation or {}), 'deterministic_report_status': str(diagnostics_obj.get('deterministic_report_status') or 'skipped'), 'llm_brief_status': str(diagnostics_obj.get('llm_brief_status') or 'skipped'), 'ai_trade_report_status': str(diagnostics_obj.get('ai_trade_report_status') or 'skipped'), 'llm_trade_report_status': str(diagnostics_obj.get('ai_trade_report_status') or 'skipped'), 'report_generation_status': str(diagnostics_obj.get('report_status') or 'skipped'), 'operator_brief_status': str(diagnostics_obj.get('llm_brief_status') or 'skipped') if bool(operator_brief_json_exists) else 'missing', 'report_generation_reason': str(diagnostics_obj.get('report_generation_reason') or diagnostics_obj.get('report_reason_human') or ''), 'missing_sections': missing_sections, 'completeness_score': float(phase3_completeness_score or 0.0), 'artifact_presence': dict(artifact_presence or {}), 'llm_response_status': str(llm_artifact.get('status') or ''), 'llm_parse_mode': str(llm_artifact.get('parse_mode') or ''), 'llm_completeness_score': float(llm_artifact.get('completeness_score') or 0.0), 'llm_required_keys_missing': [str(x or '') for x in list(llm_artifact.get('required_keys_missing') or []) if str(x or '').strip()], 'evidence_counts': {'strategist_events': int(strategist_event_count or 0), 'scanner_events': int(scanner_event_count or 0), 'monitor_events': int(monitor_event_count or 0)}}


def finalize_bundle_health_r4_impl(health_payload, *, artifact_presence, diagnostics, facade):
    out = dict(health_payload or {})
    diagnostics_obj = dict(diagnostics or {})
    presence = dict(artifact_presence or {})
    out['artifact_presence'] = presence
    out['llm_trade_report_status'] = str(diagnostics_obj.get('ai_trade_report_status') or out.get('ai_trade_report_status') or 'skipped')
    out['report_generation_status'] = 'available' if bool(presence.get('ai_trade_report_json')) or bool(presence.get('ai_trade_report_md')) else str(diagnostics_obj.get('report_status') or 'skipped')
    out['operator_brief_status'] = str(diagnostics_obj.get('llm_brief_status') or 'skipped') if bool(presence.get('operator_brief_json')) else 'missing'
    out['llm_brief_status'] = str(out.get('operator_brief_status') or diagnostics_obj.get('llm_brief_status') or 'skipped')
    out['ai_trade_report_status'] = str(out.get('llm_trade_report_status') or diagnostics_obj.get('ai_trade_report_status') or 'skipped')
    return out


def build_trade_bundle_state_r4_impl(*, provenance_kwargs, health_kwargs, facade):
    provenance = facade.build_bundle_provenance(**dict(provenance_kwargs or {}))
    health = facade.build_bundle_health(**dict(health_kwargs or {}))
    return {'provenance': provenance, 'health': health}
