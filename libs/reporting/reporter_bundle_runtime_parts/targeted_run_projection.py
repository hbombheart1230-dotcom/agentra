"""Targeted-run row projection: target run-id expansion and merged day event/evidence rows (read-only over copied rows).

Third Pass T2 (P1.5) intra-function extraction from `libs/reporting/live_execution_bundle_runner.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def targeted_day_rows(day_event_rows, targeted_run_ids, all_day_event_rows, target_ctx, day_evidence_rows, *, facade):
    if True:
        targeted_run_ids = facade._expand_targeted_run_ids_with_cached_strategist_sources(
            event_rows=day_event_rows,
            targeted_run_ids=targeted_run_ids,
        )
        target_monitor_rows = facade._target_symbol_monitor_rows(
            all_day_event_rows,
            symbol=str(target_ctx.get("target_symbol") or ""),
        )
        day_event_rows = facade._merge_rows_by_identity(
            facade._filter_rows_by_run_ids(day_event_rows, targeted_run_ids),
            target_monitor_rows,
        )
        day_evidence_rows = facade._filter_rows_by_run_ids(day_evidence_rows, targeted_run_ids)
    return (day_event_rows, day_evidence_rows)
