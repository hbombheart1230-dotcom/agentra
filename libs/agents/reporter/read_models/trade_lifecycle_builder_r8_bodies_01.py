"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/trade_lifecycle_builder.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def _build_lifecycle_from_seed_r4_impl(*, trade_id, symbol, day, execution_mode_label_text, story_type, facade):
    return {'trade_id': trade_id, 'symbol': symbol, 'day': day, 'status': 'open', 'execution_mode_label': execution_mode_label_text, 'story_type': story_type, 'entry': {}, 'holding': {'run_ids': [], 'holding_events': [], 'posture_history': [], 'monitor_updates': [], 'noteworthy_changes': []}, 'exit': {}, 'run_ids_all': [], 'summary': {}, 'reporter': {}, 'timeline': [], 'warnings': []}
