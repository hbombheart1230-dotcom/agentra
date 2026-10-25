"""Operator UI recent-run list read model, run activity meta and portfolio-guard extraction (pure projections over loaded rows).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def load_recent_runs_r3_impl(config, *, limit, mismatch_only, activity_view, facade):
    rows = list(facade._iter_jsonl(config.event_log_path))
    route_rows = [row for row in rows if str(row.get("stage") or "") == "commander_router" and str(row.get("event") or "") == "route"]
    route_rows = sorted(route_rows, key=lambda row: facade._to_epoch(row.get("ts")) or 0, reverse=True)
    latest_day = facade._latest_event_day(config.event_log_path)
    if activity_view == "trades" and latest_day:
        day_filtered = [row for row in route_rows if facade._event_day(row.get("ts")) == latest_day]
        if day_filtered:
            route_rows = day_filtered
    target_run_ids = {str(row.get("run_id") or "").strip() for row in route_rows if str(row.get("run_id") or "").strip()}
    grouped: Dict[str, List[Dict[str, Any]]] = {rid: [] for rid in target_run_ids}
    report_index = facade._trade_report_index(config)
    reports_by_run = report_index.get("by_run_id") or {}
    for row in rows:
        rid = str(row.get("run_id") or "").strip()
        if rid in grouped:
            grouped[rid].append(row)

    out: List[Dict[str, Any]] = []
    for route in route_rows:
        rid = str(route.get("run_id") or "").strip()
        run_rows = grouped.get(rid) or []
        strategist_summary = next(
            (r.get("payload") for r in reversed(run_rows) if str(r.get("stage") or "") == "strategist" and str(r.get("event") or "") == "summary" and isinstance(r.get("payload"), dict)),
            {},
        )
        scanner_summary = next(
            (r.get("payload") for r in reversed(run_rows) if str(r.get("stage") or "") == "scanner" and str(r.get("event") or "") == "summary" and isinstance(r.get("payload"), dict)),
            {},
        )
        monitor_summary = next(
            (r.get("payload") for r in reversed(run_rows) if str(r.get("stage") or "") == "monitor" and str(r.get("event") or "") == "summary" and isinstance(r.get("payload"), dict)),
            {},
        )
        monitor_trace = next(
            (
                (r.get("payload") or {}).get("payload")
                for r in reversed(run_rows)
                if str(r.get("stage") or "") == "decision_trace"
                and str(r.get("event") or "") == "entry_exit_decision"
                and isinstance(r.get("payload"), dict)
                and str((r.get("payload") or {}).get("agent") or "") == "monitor"
            ),
            {},
        )
        strategic_frame = next(
            (
                (r.get("payload") or {}).get("payload")
                for r in reversed(run_rows)
                if str(r.get("stage") or "") == "decision_trace"
                and str(r.get("event") or "") == "strategic_frame"
                and isinstance(r.get("payload"), dict)
                and str((r.get("payload") or {}).get("agent") or "") == "strategist"
            ),
            {},
        )
        candidate_selection = next(
            (
                (r.get("payload") or {}).get("payload")
                for r in reversed(run_rows)
                if str(r.get("stage") or "") == "decision_trace"
                and str(r.get("event") or "") == "candidate_selection"
                and isinstance(r.get("payload"), dict)
                and str((r.get("payload") or {}).get("agent") or "") == "scanner"
            ),
            {},
        )
        verdict_payload = next(
            (r.get("payload") for r in reversed(run_rows) if str(r.get("stage") or "") == "execute_from_packet" and str(r.get("event") or "") == "verdict" and isinstance(r.get("payload"), dict)),
            {},
        )
        fast_path_payload = next(
            (r.get("payload") for r in reversed(run_rows) if str(r.get("stage") or "") == "commander_router" and str(r.get("event") or "") == "fast_path" and isinstance(r.get("payload"), dict)),
            {},
        )
        runtime_end_payload = next(
            (r.get("payload") for r in reversed(run_rows) if str(r.get("stage") or "") == "commander_router" and str(r.get("event") or "") == "end" and isinstance(r.get("payload"), dict)),
            {},
        )
        execution_payload = next(
            (r.get("payload") for r in reversed(run_rows) if str(r.get("stage") or "") == "execute_from_packet" and str(r.get("event") or "") == "execution" and isinstance(r.get("payload"), dict)),
            {},
        )
        execution = facade._normalize_execution_payload(execution_payload if isinstance(execution_payload, dict) else {})
        portfolio_sync = facade._build_portfolio_sync_card(facade._extract_portfolio_guard_payload_from_run_rows(run_rows))
        monitor_row = facade._monitor_row_summary(
            monitor_summary if isinstance(monitor_summary, dict) else {},
            monitor_trace if isinstance(monitor_trace, dict) else {},
        )
        selected_candidate = candidate_selection.get("selected_candidate") if isinstance(candidate_selection.get("selected_candidate"), dict) else {}
        feature_snapshot = selected_candidate.get("feature_snapshot") if isinstance(selected_candidate.get("feature_snapshot"), dict) else {}
        feature_coverage = facade._feature_coverage(feature_snapshot)
        macro_stress_overlay = strategic_frame.get("macro_stress_overlay") if isinstance(strategic_frame.get("macro_stress_overlay"), dict) else {}
        runtime_path = str(runtime_end_payload.get("path") or fast_path_payload.get("path") or "")
        report_meta = reports_by_run.get(rid) if isinstance(reports_by_run.get(rid), dict) else {}
        if report_meta:
            report_diag = (
                report_meta.get("ai_report_diagnostics")
                if isinstance(report_meta.get("ai_report_diagnostics"), dict)
                else {}
            )
        else:
            execution_action = str(execution.get("action") or "").upper()
            monitor_reason_text = str(monitor_summary.get("monitor_reason") or "").strip().lower()
            if execution_action in {"BUY", "SELL"}:
                report_diag = facade._normalize_ai_report_diagnostics(
                    {
                        "report_status": "failed",
                        "report_reason_code": "missing_report_linkage",
                        "report_reason_human": facade._report_reason_human("missing_report_linkage"),
                        "next_expected_step": facade._report_next_step("missing_report_linkage"),
                        "generation_attempted": False,
                        "story_input_available": False,
                        "report_output_available": False,
                    },
                    report_exists=False,
                    lifecycle_status="",
                    story_type="",
                )
            elif "hold" in monitor_reason_text:
                report_diag = facade._normalize_ai_report_diagnostics(
                    {
                        "report_status": "skipped",
                        "report_reason_code": "hold_only_run",
                        "report_reason_human": facade._report_reason_human("hold_only_run"),
                        "next_expected_step": facade._report_next_step("hold_only_run"),
                    },
                    report_exists=False,
                    lifecycle_status="",
                    story_type="decision_only",
                )
            else:
                report_diag = facade._normalize_ai_report_diagnostics(
                    {
                        "report_status": "skipped",
                        "report_reason_code": "decision_only_run",
                        "report_reason_human": facade._report_reason_human("decision_only_run"),
                        "next_expected_step": facade._report_next_step("decision_only_run"),
                    },
                    report_exists=False,
                    lifecycle_status="",
                    story_type="decision_only",
                )
        row = {
                "run_id": rid,
                "run_id_short": facade._short_run_id(rid),
                "ts": facade._iso_to_display(route.get("ts")),
                "mode": str((route.get("payload") or {}).get("mode") or ""),
                "phase": str((route.get("payload") or {}).get("phase") or ""),
                "runtime_path": runtime_path,
                "strategist_playbook": str(strategist_summary.get("playbook") or ""),
                "strategist_risk_tone": facade._strategist_risk_tone(strategist_summary),
                "scanner_top_stock": str(scanner_summary.get("top_stock") or ""),
                "scanner_top_score": facade._safe_float(scanner_summary.get("top_score"), 0.0),
                "monitor_reason": str(monitor_summary.get("monitor_reason") or ""),
                "exit_reason": str(monitor_summary.get("exit_reason") or ""),
                "active_exit_axis": str(monitor_row.get("active_exit_axis") or "-"),
                "effective_stop": str(monitor_row.get("effective_stop") or "-"),
                "peak_drawdown": str(monitor_row.get("peak_drawdown") or "-"),
                "watch_axes": list(monitor_row.get("watch_axes") or []),
                "supervisor_allowed": verdict_payload.get("allowed"),
                "guard_reason": str(verdict_payload.get("reason") or ""),
                "execution_status": str(execution.get("status") or ""),
                "execution_action": str(execution.get("action") or ""),
                "symbol": facade.normalize_symbol(execution.get("symbol") or scanner_summary.get("top_stock") or "", allow_test_symbols=True),
                "macro_stress_active": bool(macro_stress_overlay.get("active")),
                "macro_stress_flags": list(macro_stress_overlay.get("stress_flags") or [])[:3],
                "feature_coverage_quality": str(feature_coverage.get("quality") or "missing"),
                "feature_coverage_ratio": facade._safe_float(feature_coverage.get("coverage_ratio"), 0.0),
                "report_available": bool(report_meta.get("report_available")),
                "report_status": str(report_meta.get("report_status") or report_diag.get("report_status") or "skipped"),
                "report_status_label": str(report_meta.get("report_status_label") or report_diag.get("report_status_label") or facade._report_status_label("skipped")),
                "report_status_badge_class": str(report_meta.get("report_status_badge_class") or report_diag.get("report_status_badge_class") or facade._report_status_badge_class("skipped")),
                "report_reason_human": str(report_meta.get("report_reason_human") or report_diag.get("report_reason_human") or ""),
                "report_next_expected_step": str(report_meta.get("report_next_expected_step") or report_diag.get("next_expected_step") or ""),
                "report_generation_model": str(report_meta.get("report_generation_model") or report_diag.get("llm_model_used") or ""),
                "trade_id": str(report_meta.get("trade_id") or ""),
                "story_id": str(report_meta.get("story_id") or ""),
                "story_type": str(report_meta.get("story_type") or ""),
                "story_type_label": str(report_meta.get("story_type_label") or "No linked report"),
                "story_type_badge_class": str(report_meta.get("story_type_badge_class") or "status-badge"),
                "lifecycle_status": str(report_meta.get("lifecycle_status") or ""),
                "lifecycle_summary": str(report_meta.get("lifecycle_summary") or ""),
                "execution_mode_label": str(report_meta.get("execution_mode_label") or "-"),
                "report_summary": str(report_meta.get("report_summary") or "No linked trade report for this run."),
                "reporter_status_human": str(report_meta.get("reporter_status_human") or ""),
                "report_link": str(report_meta.get("report_link") or ""),
                "operator_brief_available": bool(report_meta.get("operator_brief_available")),
                "operator_brief_link": str(report_meta.get("operator_brief_link") or ""),
                "portfolio_sync": portfolio_sync,
                "portfolio_sync_status": str(portfolio_sync.get("status") or "unavailable"),
                "portfolio_sync_label": str(portfolio_sync.get("status_label") or "Sync status unavailable"),
                "portfolio_sync_badge_class": str(portfolio_sync.get("badge_class") or "status-badge"),
                "portfolio_sync_sentence": str(portfolio_sync.get("sentence") or ""),
            }
        row.update(
            facade._run_activity_meta(
                runtime_path,
                execution,
                verdict_payload.get("reason") if isinstance(verdict_payload, dict) else "",
                monitor_summary.get("monitor_reason") if isinstance(monitor_summary, dict) else "",
            )
        )
        if mismatch_only and row["portfolio_sync_status"] not in {"mismatch", "reader_error"}:
            continue
        if activity_view == "trades" and row.get("activity_kind") != "trade":
            continue
        if activity_view == "monitoring" and row.get("activity_kind") != "monitoring":
            continue
        out.append(row)
        if activity_view != "trades" and len(out) >= max(1, int(limit)):
            break
    return out


def _extract_portfolio_guard_payload_from_run_rows_r3_impl(run_rows, *, facade):
    if not isinstance(run_rows, list) or not run_rows:
        return {}
    execution_payload = next(
        (
            r.get("payload")
            for r in reversed(run_rows)
            if str(r.get("stage") or "") == "execute_from_packet"
            and str(r.get("event") or "") == "execution"
            and isinstance(r.get("payload"), dict)
        ),
        {},
    )
    if isinstance(execution_payload, dict) and isinstance(execution_payload.get("portfolio_guard"), dict):
        return dict(execution_payload.get("portfolio_guard") or {})

    verdict_payload = next(
        (
            r.get("payload")
            for r in reversed(run_rows)
            if str(r.get("stage") or "") == "execute_from_packet"
            and str(r.get("event") or "") == "verdict"
            and isinstance(r.get("payload"), dict)
        ),
        {},
    )
    if isinstance(verdict_payload, dict) and isinstance(verdict_payload.get("portfolio_guard"), dict):
        return dict(verdict_payload.get("portfolio_guard") or {})

    portfolio_guard_block_payload = next(
        (
            r.get("payload")
            for r in reversed(run_rows)
            if str(r.get("stage") or "") == "execute_from_packet"
            and str(r.get("event") or "") == "portfolio_guard_block"
            and isinstance(r.get("payload"), dict)
        ),
        {},
    )
    if isinstance(portfolio_guard_block_payload, dict):
        if isinstance(portfolio_guard_block_payload.get("portfolio_guard"), dict):
            return dict(portfolio_guard_block_payload.get("portfolio_guard") or {})
        return dict(portfolio_guard_block_payload)
    return {}


def _run_activity_meta_r3_impl(runtime_path, execution, guard_reason, monitor_reason, *, facade):
    path = str(runtime_path or "").strip().lower()
    action = str((execution or {}).get("action") or "").strip().upper()
    status = str((execution or {}).get("status") or "").strip()
    guard = str(guard_reason or "").strip().lower()
    monitor = str(monitor_reason or "").strip().lower()
    if action in {"BUY", "SELL"} and status:
        return {
            "activity_kind": "trade",
            "activity_label": "Trade",
            "activity_badge_class": "status-badge status-badge--ok",
        }
    if path == "integrated_chain_monitor_only" and (guard == "noop_intent_skipped" or "hold" in monitor):
        return {
            "activity_kind": "monitoring",
            "activity_label": "Monitoring",
            "activity_badge_class": "status-badge",
        }
    return {
        "activity_kind": "analysis",
        "activity_label": "Analysis",
        "activity_badge_class": "chip",
    }
