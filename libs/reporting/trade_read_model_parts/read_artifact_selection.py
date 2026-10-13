"""Artifact selection and precedence facts for the trade read model (inputs are already-loaded artifacts).

Second Pass (P1.5) intra-function extraction from `libs/reporting/trade_read_model.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def read_select_artifacts_bundle(report_payloads, _pick_with_source, *, facade):
    bundle = dict(report_payloads.get("lifecycle_data") or {})
    report = dict(report_payloads.get("report_data") or {})
    payload_paths = dict(report_payloads.get("paths") or {})
    lifecycle_path_used = facade.Path(str(payload_paths.get("lifecycle_path") or ""))
    report_path_used = facade.Path(str(payload_paths.get("report_path") or ""))

    lifecycle = bundle.get("lifecycle") if isinstance(bundle.get("lifecycle"), dict) else {}
    canonical = bundle.get("canonical_agent_artifacts") if isinstance(bundle.get("canonical_agent_artifacts"), dict) else {}
    artifacts = bundle.get("artifacts") if isinstance(bundle.get("artifacts"), dict) else {}
    evidence_provenance = bundle.get("evidence_provenance") if isinstance(bundle.get("evidence_provenance"), dict) else {}
    same_day_linkage = bundle.get("same_day_reporter_linkage") if isinstance(bundle.get("same_day_reporter_linkage"), dict) else {}
    story_meta = bundle.get("trade_story_input_meta") if isinstance(bundle.get("trade_story_input_meta"), dict) else {}
    market_context_human = bundle.get("market_context_human") if isinstance(bundle.get("market_context_human"), dict) else {}
    scanner_reason_human = bundle.get("scanner_reason_human") if isinstance(bundle.get("scanner_reason_human"), dict) else {}
    filters_human = bundle.get("filters_human") if isinstance(bundle.get("filters_human"), dict) else {}
    monitor_reason_human = bundle.get("monitor_reason_human") if isinstance(bundle.get("monitor_reason_human"), dict) else {}
    
    commander_art = canonical.get("commander") if isinstance(canonical.get("commander"), dict) else {}
    strategist_art = canonical.get("strategist") if isinstance(canonical.get("strategist"), dict) else {}
    scanner_art = canonical.get("scanner") if isinstance(canonical.get("scanner"), dict) else {}
    monitor_art = canonical.get("monitor") if isinstance(canonical.get("monitor"), dict) else {}
    executor_art = canonical.get("executor") if isinstance(canonical.get("executor"), dict) else {}

    report_data = report.get("report_data") if isinstance(report.get("report_data"), dict) else report
    shared_facts = report_data.get("shared_facts") if isinstance(report_data.get("shared_facts"), dict) else {}

    entry_obj = lifecycle.get("entry") if isinstance(lifecycle.get("entry"), dict) else {}
    holding_obj = lifecycle.get("holding") if isinstance(lifecycle.get("holding"), dict) else {}
    exit_obj = lifecycle.get("exit") if isinstance(lifecycle.get("exit"), dict) else {}

    entry_ts, entry_ts_source = _pick_with_source(
        [
            ("lifecycle.entry.timestamp", entry_obj.get("timestamp")),
            ("ai_trade_report.shared_facts.entry_time", shared_facts.get("entry_time")),
        ],
        default="unknown",
    )
    exit_ts, exit_ts_source = _pick_with_source(
        [
            ("lifecycle.exit.timestamp", exit_obj.get("timestamp")),
            ("ai_trade_report.shared_facts.exit_time", shared_facts.get("exit_time")),
        ],
        default="unknown",
    )

    hold_duration_sec = 0
    hold_duration_source = "default"
    if exit_obj.get("position_age_seconds") is not None:
        try:
            hold_duration_sec = int(float(exit_obj["position_age_seconds"]))
            hold_duration_source = "lifecycle.exit.position_age_seconds"
        except Exception:
            pass
    return (artifacts, bundle, canonical, commander_art, entry_obj, entry_ts, entry_ts_source, evidence_provenance, executor_art, exit_obj, exit_ts, exit_ts_source, filters_human, hold_duration_sec, hold_duration_source, holding_obj, lifecycle, lifecycle_path_used, market_context_human, monitor_art, monitor_reason_human, report, report_data, report_path_used, same_day_linkage, scanner_art, scanner_reason_human, shared_facts, story_meta, strategist_art)
