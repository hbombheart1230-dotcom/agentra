"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/entry_blocker_read_model.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def render_entry_blocker_summary_markdown_r4_impl(summary, *, facade):
    lines: List[str] = []
    lines.append(f"# Entry Blocker Summary ({facade._text(summary.get('date'))})")
    lines.append('')
    lines.append(f"- rows: {int(summary.get('row_count') or 0)}")
    if facade._text(summary.get('symbol_filter')):
        lines.append(f"- symbol: `{facade._text(summary.get('symbol_filter'))}`")
    if facade._text(summary.get('family_filter')):
        family = facade._text(summary.get('family_filter'))
        lines.append(f'- family: `{family}`')
        lines.append(f'- family explanation: {facade.explain_blocker_family(family)}')
    if int(summary.get('limit') or 0) > 0:
        lines.append(f"- limit: {int(summary.get('limit') or 0)}")
    lines.append('')
    lines.append('## Decision Frequency')
    for key, value in dict(summary.get('decision_frequency') or {}).items():
        lines.append(f'- `{key}`: {int(value)}')
    lines.append('')
    lines.append('## Blocker Families')
    for key, value in dict(summary.get('blocker_family_frequency') or {}).items():
        lines.append(f'- `{key}`: {int(value)}')
    lines.append('')
    lines.append('## Blocker Frequency')
    for key, value in dict(summary.get('blocker_frequency') or {}).items():
        lines.append(f'- `{key}`: {int(value)}')
    lines.append('')
    lines.append('## Family -> Raw Blocker Breakdown')
    for family, raw_counts in dict(summary.get('blocker_family_raw_breakdown') or {}).items():
        explanation = facade.explain_blocker_family(family)
        lines.append(f'- `{family}`: {explanation}')
        for raw, value in dict(raw_counts or {}).items():
            lines.append(f'  - `{raw}`: {int(value)} | {facade.explain_raw_blocker(raw)}')
    lines.append('')
    family_filter = facade._text(summary.get('family_filter'))
    if family_filter:
        focused_global = dict((summary.get('blocker_family_raw_breakdown') or {}).get(family_filter) or {})
        lines.append('## Focused Family Raw Blockers')
        for raw, value in focused_global.items():
            lines.append(f'- `{raw}`: {int(value)} | {facade.explain_raw_blocker(raw)}')
        lines.append('')
        lines.append('## Focused Family by Symbol')
        for symbol_value, payload in dict(summary.get('by_symbol') or {}).items():
            raw_counts = dict((payload.get('blocker_family_raw_breakdown') or {}).get(family_filter) or {})
            if not raw_counts:
                continue
            lines.append(f'- `{symbol_value}`: {raw_counts}')
        lines.append('')
        lines.append('## Focused Family by Time Bucket')
        for bucket, payload in dict(summary.get('by_time_bucket') or {}).items():
            raw_counts = dict((payload.get('blocker_family_raw_breakdown') or {}).get(family_filter) or {})
            if not raw_counts:
                continue
            lines.append(f'- `{bucket}`: {raw_counts}')
        lines.append('')
        lines.append('## Focused Family by Final Decision')
        for decision, payload in dict(summary.get('by_final_decision') or {}).items():
            raw_counts = dict((payload.get('blocker_family_raw_breakdown') or {}).get(family_filter) or {})
            if not raw_counts:
                continue
            lines.append(f'- `{decision}`: {raw_counts}')
        lines.append('')
    lines.append('## No-Trade Codes')
    for key, value in dict(summary.get('no_trade_code_frequency') or {}).items():
        lines.append(f'- `{key}`: {int(value)}')
    lines.append('')
    lines.append('## Scanner Quality Suspected')
    lines.append(f"- count: {int(summary.get('scanner_quality_suspected_count') or 0)}")
    if dict(summary.get('scanner_quality_reason_frequency') or {}):
        lines.append(f"- reasons: {dict(summary.get('scanner_quality_reason_frequency') or {})}")
    if dict(summary.get('scanner_quality_top_symbols') or {}):
        lines.append(f"- top_symbols: {dict(summary.get('scanner_quality_top_symbols') or {})}")
    lines.append('')
    lines.append('## Time Buckets')
    for bucket, payload in dict(summary.get('by_time_bucket') or {}).items():
        lines.append(f"- `{bucket}`: decisions={dict(payload.get('decision_frequency') or {})}, " + f"families={dict(payload.get('blocker_family_frequency') or {})}, " + f"blockers={dict(payload.get('blocker_frequency') or {})}")
        family_raw = dict(payload.get('blocker_family_raw_breakdown') or {})
        if family_raw:
            lines.append(f'  - family_raw_breakdown={family_raw}')
    if list(summary.get('symbol_sequence') or []):
        lines.append('')
        lines.append('## Symbol Sequence')
        for row in list(summary.get('symbol_sequence') or [])[:30]:
            family_explanations = dict(row.get('family_explanations') or {})
            raw_explanations = dict(row.get('raw_blocker_explanations') or {})
            lines.append('- ' + f"{facade._text(row.get('ts_kst'))} " + f"`{facade._text(row.get('run_id'))}` " + f"{facade._text(row.get('final_decision'))} " + f"reason=`{facade._text(row.get('no_trade_code'))}` " + f"families={list(row.get('blocker_families') or [])} " + f"blockers={list(row.get('primary_blockers') or [])}")
            if family_explanations:
                lines.append(f'  - family_explanations={family_explanations}')
            if raw_explanations:
                lines.append(f'  - raw_blocker_explanations={raw_explanations}')
            if facade._text(row.get('reclaim_evidence_explanation')):
                lines.append('  - reclaim=' + f"{facade._text(row.get('reclaim_evidence_explanation'))} " + f"distance={facade._text(row.get('reclaim_distance_to_ready'))} " + f"tuned={str(bool(row.get('reclaim_readiness_tuned'))).lower()} " + f"band={facade._text(row.get('reclaim_tuning_band_used'))}")
            if bool(row.get('scanner_quality_suspected')):
                lines.append('  - scanner_quality_suspected=' + f"true reason=`{facade._text(row.get('scanner_quality_reason'))}` " + f"explanation={facade._text(row.get('scanner_quality_reason_explanation'))}")
    return '\n'.join(lines).strip() + '\n'
