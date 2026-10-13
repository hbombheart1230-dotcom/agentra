"""Entry/exit/monitor truth and data-source-quality projection.

Second Pass (P1.5) intra-function extraction from `libs/reporting/trade_read_model.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def read_truth_blocker_trace_data_source_quality(hold_duration_sec, _pick_with_source, exit_obj, shared_facts, bundle, report_data, entry_obj, monitor_art, scanner_art, strategist_art, commander_art, lifecycle, executor_art, entry_ts, exit_ts, _safe_float, report, artifacts, _clip, same_day_linkage, story_meta, evidence_provenance, entry_ts_source, exit_ts_source, hold_duration_source, td, lifecycle_path_used, report_path_used, canonical, *, facade):
    hold_duration_sec = max(0, hold_duration_sec)

    pnl_value, pnl_source = _pick_with_source(
        [
            ("lifecycle.exit.pnl", exit_obj.get("pnl")),
            ("ai_trade_report.shared_facts.pnl", shared_facts.get("pnl")),
        ],
        default="0.0",
    )
    pnl_pct_value, pnl_pct_source = _pick_with_source(
        [
            ("lifecycle.exit.pnl_pct", exit_obj.get("pnl_pct")),
            ("ai_trade_report.shared_facts.pnl_pct", shared_facts.get("pnl_pct")),
        ],
        default="0.0",
    )
    trade_id_value, trade_id_source = _pick_with_source(
        [
            ("lifecycle_bundle.trade_id", bundle.get("trade_id")),
            ("lifecycle_bundle.story_id", bundle.get("story_id")),
            ("ai_trade_report.report_data.trade_id", report_data.get("trade_id")),
        ],
        default="unknown",
    )
    symbol_value, symbol_source = _pick_with_source(
        [
            ("lifecycle_bundle.symbol", bundle.get("symbol")),
            ("ai_trade_report.report_data.symbol", report_data.get("symbol")),
        ],
        default="unknown",
    )

    primary_blocker = "unknown"
    primary_blocker_source = "default"
    if not entry_obj:
        primary_blocker, primary_blocker_source = _pick_with_source(
            [
                ("canonical.monitor.primary_reason_code", monitor_art.get("primary_reason_code")),
                ("canonical.monitor.dominant_blocker", monitor_art.get("dominant_blocker")),
                ("canonical.scanner.dominant_block_reason", scanner_art.get("dominant_block_reason")),
                ("ai_trade_report.report_data.missing_reason", report_data.get("missing_reason")),
            ],
            default="unknown",
        )

    playbook_value, playbook_source = _pick_with_source(
        [
            ("canonical.strategist.playbook", strategist_art.get("playbook")),
            ("lifecycle.entry.strategist_context.playbook", (entry_obj.get("strategist_context") if isinstance(entry_obj.get("strategist_context"), dict) else {}).get("playbook")),
            ("ai_trade_report.report_data.playbook", report_data.get("playbook")),
        ],
        default="unknown",
    )
    entry_reason_value, entry_reason_source = _pick_with_source(
        [
            ("lifecycle.entry.reason", entry_obj.get("reason")),
            ("lifecycle.entry.reason_human", entry_obj.get("reason_human")),
            ("canonical.monitor.decision_summary", monitor_art.get("decision_summary")),
            ("canonical.monitor.summary", monitor_art.get("summary")),
        ],
        default="unknown",
    )
    exit_reason_value, exit_reason_source = _pick_with_source(
        [
            ("lifecycle.exit.reason", exit_obj.get("reason")),
            ("lifecycle.exit.monitor_reason", exit_obj.get("monitor_reason")),
            ("lifecycle.exit.reason_human", exit_obj.get("reason_human")),
        ],
        default="unknown",
    )
    applied_policy_source_value, applied_policy_source_field = _pick_with_source(
        [
            ("canonical.commander.applied_policy_source", commander_art.get("applied_policy_source")),
            ("canonical.monitor.policy_source", monitor_art.get("policy_source")),
        ],
        default="unknown",
    )
    strategy_policy_source_value, strategy_policy_source_field = _pick_with_source(
        [
            ("canonical.strategist.policy_source", strategist_art.get("policy_source")),
        ],
        default="unknown",
    )
    execution_label_value, execution_label_source = _pick_with_source(
        [
            ("lifecycle.status", lifecycle.get("status")),
            ("canonical.executor.final_execution_status", executor_art.get("final_execution_status")),
            ("ai_trade_report.report_data.status", report_data.get("status")),
        ],
        default="unknown",
    )
    evidence_recovery_value = bool(bundle.get("evidence_recovery_used") or report_data.get("evidence_recovery_used"))
    evidence_recovery_source = (
        "lifecycle_bundle.evidence_recovery_used"
        if bundle.get("evidence_recovery_used") is not None
        else ("ai_trade_report.report_data.evidence_recovery_used" if report_data.get("evidence_recovery_used") is not None else "default")
    )

    facts = {
        "trade_id": trade_id_value,
        "symbol": symbol_value,
        "entry_ts": entry_ts,
        "exit_ts": exit_ts,
        "hold_duration_sec": hold_duration_sec,
        "pnl": _safe_float(pnl_value),
        "pnl_pct": _safe_float(pnl_pct_value),
        "playbook": playbook_value,
        "entry_reason": entry_reason_value,
        "exit_reason": exit_reason_value,
        "primary_blocker_if_no_buy": primary_blocker,
        "applied_policy_source": applied_policy_source_value,
        "strategy_policy_source": strategy_policy_source_value,
        "execution_label": execution_label_value,
        "data_source": "lifecycle_bundle" if bundle else ("ai_trade_report" if report else "unknown"),
        "evidence_recovery_used": evidence_recovery_value,
    }

    canonical_paths = {
        key: str(artifacts.get(key) or bundle.get(key) or "")
        for key in (
            "canonical_commander_json",
            "canonical_strategist_json",
            "canonical_scanner_json",
            "canonical_monitor_json",
            "canonical_supervisor_json",
            "canonical_executor_json",
        )
    }

    same_day_status = _clip(
        same_day_linkage.get("status")
        or story_meta.get("same_day_reporter_linkage_status")
        or "missing"
    )
    same_day_reason = _clip(
        same_day_linkage.get("reason")
        or story_meta.get("same_day_reporter_linkage_reason")
        or "Same-day reporter linkage was not captured."
    )
    same_day_analysis_path = str(same_day_linkage.get("analysis_path") or same_day_linkage.get("artifact_path") or "").strip()
    same_day_expected_path = str(
        same_day_linkage.get("expected_path")
        or same_day_linkage.get("fallback_expected_path")
        or story_meta.get("same_day_reporter_expected_path")
        or ""
    ).strip()
    same_day_file_found = bool(same_day_linkage.get("file_found"))
    if same_day_analysis_path and facade.Path(same_day_analysis_path).exists():
        same_day_file_found = True

    provenance = {
        "schema_version": "trade_read_model.v2",
        "data_source": facts["data_source"],
        "paths": {
            "trade_root_path": str(td),
            "lifecycle_bundle_json": str(lifecycle_path_used) if lifecycle_path_used.exists() else "",
            "ai_trade_report_json": str(report_path_used) if report_path_used.exists() else "",
        },
        "canonical_artifact_paths": canonical_paths,
        "evidence_provenance": evidence_provenance,
        "same_day_reporter_linkage": {
            "status": same_day_status,
            "reason": same_day_reason,
            "analysis_path": same_day_analysis_path,
            "expected_path": same_day_expected_path,
            "file_found": same_day_file_found,
        },
        "field_sources": {
            "trade_id": trade_id_source,
            "symbol": symbol_source,
            "entry_ts": entry_ts_source,
            "exit_ts": exit_ts_source,
            "hold_duration_sec": hold_duration_source,
            "pnl": pnl_source,
            "pnl_pct": pnl_pct_source,
            "entry_reason": entry_reason_source,
            "exit_reason": exit_reason_source,
            "playbook": playbook_source,
            "primary_blocker_if_no_buy": primary_blocker_source,
            "applied_policy_source": applied_policy_source_field,
            "strategy_policy_source": strategy_policy_source_field,
            "execution_label": execution_label_source,
            "data_source": "derived.presence_check",
            "evidence_recovery_used": evidence_recovery_source,
        },
    }

    stop_policy_trace = monitor_art.get("monitor_stop_policy_trace")
    stop_policy_trace = stop_policy_trace if isinstance(stop_policy_trace, dict) else {}
    blocker_trace = monitor_art.get("monitor_blocker_trace")
    blocker_trace = blocker_trace if isinstance(blocker_trace, dict) else {}
    watch_axes = monitor_art.get("watch_axes")
    if not isinstance(watch_axes, list):
        watch_axes = stop_policy_trace.get("watch_axes") if isinstance(stop_policy_trace.get("watch_axes"), list) else []
    thresholds_snapshot = (
        monitor_art.get("thresholds_snapshot")
        if isinstance(monitor_art.get("thresholds_snapshot"), dict)
        else {}
    )
    if not thresholds_snapshot:
        thresholds_snapshot = {
            "effective_stop_loss_pct": monitor_art.get("effective_stop_loss_pct"),
            "take_profit_pct": monitor_art.get("take_profit_pct"),
            "confirm_required": monitor_art.get("confirm_required"),
            "confirm_count": monitor_art.get("confirm_count"),
        }
        thresholds_snapshot = {k: v for k, v in thresholds_snapshot.items() if v is not None}
    monitor_exit_trigger = _clip(
        monitor_art.get("trigger_type")
        or monitor_art.get("active_exit_axis")
        or stop_policy_trace.get("active_exit_axis")
        or exit_obj.get("monitor_reason")
        or exit_obj.get("reason")
    )
    data_source_quality = {
        "has_lifecycle_bundle": bool(bundle),
        "has_ai_trade_report": bool(report),
        "has_canonical_artifacts": bool(canonical),
        "has_evidence_provenance": bool(evidence_provenance),
        "same_day_reporter_found": bool(same_day_file_found),
    }
    return (blocker_trace, data_source_quality, execution_label_value, facts, monitor_exit_trigger, playbook_value, provenance, same_day_reason, same_day_status, stop_policy_trace, strategy_policy_source_value, thresholds_snapshot, watch_axes)
