"""Lifecycle commander/market-context evidence and scanner/filter reason enrichment projections.

Third Pass T2 (P1.5) intra-function extraction from `libs/reporting/live_execution_bundle_runner.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def lifecycle_commander_market_evidence(lifecycle_bundle, *, facade):
    existing_market_context = (
        lifecycle_bundle.get("market_context_human")
        if isinstance(lifecycle_bundle.get("market_context_human"), dict)
        else {}
    )
    existing_regime = str(existing_market_context.get("regime") or "").strip().lower()
    existing_playbook = str(existing_market_context.get("playbook") or "").strip().lower()
    existing_vix = existing_market_context.get("vix_level")
    if (
        not existing_market_context
        or existing_regime in {"", "not_captured"}
        or existing_playbook in {"", "not_captured"}
        or existing_vix in (None, "", "not_captured")
    ):
        lifecycle_bundle["market_context_human"] = facade.build_market_context_human(
            lifecycle_bundle.get("strategist") if isinstance(lifecycle_bundle.get("strategist"), dict) else {}
        )
    commander_evidence = facade.build_commander_evidence(
        lifecycle_bundle.get("commander") if isinstance(lifecycle_bundle.get("commander"), dict) else {}
    )
    return (commander_evidence, existing_market_context, existing_playbook, existing_regime, existing_vix)


def lifecycle_scanner_filter_enrichment(lifecycle_bundle, scanner_evidence, monitor_timeline, symbol, entry_run_id, anchor_run_id, strategist_input_artifact, *, facade):
    lifecycle_bundle["market_context_human"] = facade.build_market_context_human(
        lifecycle_bundle.get("strategist") if isinstance(lifecycle_bundle.get("strategist"), dict) else {}
    )
    lifecycle_bundle["scanner_reason_human"] = facade.build_scanner_reason_human(
        lifecycle_bundle.get("scanner") if isinstance(lifecycle_bundle.get("scanner"), dict) else {},
        lifecycle_bundle.get("strategist") if isinstance(lifecycle_bundle.get("strategist"), dict) else {},
    )
    lifecycle_bundle["scanner_reason_human"] = facade._enrich_scanner_reason_from_evidence(
        lifecycle_bundle.get("scanner_reason_human")
        if isinstance(lifecycle_bundle.get("scanner_reason_human"), dict)
        else {},
        scanner_evidence,
    )
    lifecycle_bundle["scanner_evidence"] = scanner_evidence if isinstance(scanner_evidence, dict) else {}
    lifecycle_bundle["monitor_evidence"] = monitor_timeline if isinstance(monitor_timeline, dict) else {}
    lifecycle_bundle["filters_human"] = facade.build_filters_human(
        lifecycle_bundle.get("scanner") if isinstance(lifecycle_bundle.get("scanner"), dict) else {},
        lifecycle_bundle.get("strategist") if isinstance(lifecycle_bundle.get("strategist"), dict) else {},
        lifecycle_bundle.get("supervisor") if isinstance(lifecycle_bundle.get("supervisor"), dict) else {},
    )
    lifecycle_bundle["filters_human"] = facade._enrich_filters_from_evidence(
        lifecycle_bundle.get("filters_human") if isinstance(lifecycle_bundle.get("filters_human"), dict) else {},
        scanner_evidence,
        selected_symbol=str(
            (
                lifecycle_bundle.get("scanner_reason_human")
                if isinstance(lifecycle_bundle.get("scanner_reason_human"), dict)
                else {}
            ).get("selected_symbol")
            or symbol
        ),
        monitor_evidence=monitor_timeline,
    )
    strategy_anchor_run_id = str(
        ((strategist_input_artifact.get("meta") or {}).get("source_run_id") or "")
        or entry_run_id
        or anchor_run_id
        or ""
    ).strip()
    return (strategy_anchor_run_id,)
