"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/reporter_analysis.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def _latest_day_r4_impl(path, *, facade):
    best: Optional[str] = None
    for row in facade._iter_jsonl(path):
        day = facade._utc_day(row.get('ts'))
        if not day:
            continue
        if best is None or day > best:
            best = day
    return best
