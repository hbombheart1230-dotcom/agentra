"""Operator visibility summary snapshot, separated brief and bundle projections (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def build_operator_summary_snapshot_from_payload_r3_impl(payload, *, facade):
    executive = payload.get("executive_summary") if isinstance(payload.get("executive_summary"), dict) else {}
    system_health = payload.get("system_health_status") if isinstance(payload.get("system_health_status"), dict) else {}
    trading_activity = (
        payload.get("trading_activity_summary")
        if isinstance(payload.get("trading_activity_summary"), dict)
        else {}
    )
    top_issues = payload.get("top_issues") if isinstance(payload.get("top_issues"), list) else []
    recommended_actions = (
        payload.get("recommended_operator_actions")
        if isinstance(payload.get("recommended_operator_actions"), list)
        else []
    )
    route_summary = payload.get("route_summary") if isinstance(payload.get("route_summary"), dict) else {}
    data_freshness = facade.build_data_freshness(
        generated_at=str(payload.get("generated_at") or ""),
        source_run_count=payload.get("source_run_count"),
        latest_run_id=str(payload.get("latest_run_id") or ""),
        latest_run_ts=str(payload.get("latest_run_ts") or ""),
        stale=False,
    )
    return {
        "available": True,
        "generated_at": str(payload.get("generated_at") or ""),
        "source_run_count": payload.get("source_run_count"),
        "latest_run_id": str(payload.get("latest_run_id") or ""),
        "latest_run_ts": str(payload.get("latest_run_ts") or ""),
        "data_freshness": data_freshness,
        "executive_summary": {
            "system_status": str(executive.get("system_status") or ""),
            "summary_lines": [str(x or "") for x in list(executive.get("summary_lines") or []) if str(x or "").strip()][:5],
        },
        "system_health_status": {
            "system_health_level": str(system_health.get("system_health_level") or ""),
            "reasoning": [str(x or "") for x in list(system_health.get("reasoning") or []) if str(x or "").strip()][:5],
            "recommended_action": [str(x or "") for x in list(system_health.get("recommended_action") or []) if str(x or "").strip()][:3],
        },
        "trading_activity_summary": {
            "run_total": trading_activity.get("run_total"),
            "decision_action_counts": dict(trading_activity.get("decision_action_counts") or {}),
            "strategy_counts": dict(trading_activity.get("strategy_counts") or {}),
            "executions_total": trading_activity.get("executions_total"),
            "executions_ok_total": trading_activity.get("executions_ok_total"),
            "executions_fail_total": trading_activity.get("executions_fail_total"),
            "blocked_total": trading_activity.get("blocked_total"),
        },
        "route_summary": {
            "route_source": str(route_summary.get("route_source") or ""),
            "route_source_run_count": int(route_summary.get("route_source_run_count") or 0),
            "route_source_missing_count": int(route_summary.get("route_source_missing_count") or 0),
            "route_source_breakdown": dict(route_summary.get("route_source_breakdown") or {}),
            "route_selected_total": dict(route_summary.get("route_selected_total") or {}),
            "strategy_generation_mode_total": dict(route_summary.get("strategy_generation_mode_total") or {}),
        },
        "route_provenance": facade.build_route_provenance(route_summary),
        "top_issues": [
            {
                "code": str((issue or {}).get("code") or ""),
                "severity": str((issue or {}).get("severity") or ""),
                "detail": str((issue or {}).get("detail") or ""),
            }
            for issue in top_issues[:5]
            if isinstance(issue, dict)
        ],
        "recommended_operator_actions": [str(x or "") for x in recommended_actions[:5] if str(x or "").strip()],
        "narrative_axis_policy": dict(payload.get("narrative_axis_policy") or facade.narrative_axis_policy()),
    }


def build_separated_operator_brief_r3_impl(trade_dir, symbol, trades_root, *, model, facade):
    """Phase 6-1 Task 4: Fact/Narrative separated operator brief."""
    from libs.reporting.trade_read_model import build_trade_read_model
    from libs.reporting.symbol_read_model import build_symbol_read_model
    from libs.reporting.fact_narrative_report import build_separated_report

    try:
        trade_model = build_trade_read_model(str(trade_dir))
    except Exception:
        trade_model = {}
    try:
        symbol_model = build_symbol_read_model(str(trades_root), str(symbol))
    except Exception:
        symbol_model = {}
    trade_scope = trade_model if facade._operator_brief_trade_model_is_valid(trade_model) else {}
    llm_scope = trade_scope if trade_scope else symbol_model
    chosen_model = facade.normalize_openrouter_model_name(
        str(model or "").strip()
        or str(facade.resolve_policy_llm_slot(llm_scope if isinstance(llm_scope, dict) else {}, "reporter", "intraday", default_profile="fast_free").get("primary") or "").strip()
        or "minimax/minimax-m2.5"
    )
    execution_profile = facade.resolve_policy_llm_execution_slot(
        llm_scope if isinstance(llm_scope, dict) else {},
        "reporter",
        "intraday",
        default_profile="concise_review",
        defaults={
            "profile_name": "concise_review",
            "name": "concise_review",
            "temperature": 0.2,
            "max_tokens": 8192,
            "timeout_sec": 15,
            "retry": {"max_attempts": 2, "backoff_sec": 0.0},
            "retry_max": 2,
            "retry_backoff_sec": 0.0,
        },
    )
    return build_separated_report(
        trade_model=trade_model,
        symbol_model=symbol_model,
        model=chosen_model,
        execution_profile=execution_profile,
    )


def generate_operator_visibility_bundle_r3_impl(*, events_path, report_root, day, facade):
    summary_md, summary_js = facade.generate_operator_daily_summary(
        events_path,
        report_root / "operator_summary",
        day=day,
        metrics_report_dir=report_root / "metrics",
        m30_post_golive_dir=report_root / "milestones" / "m30_post_golive",
        m30_golive_dir=report_root / "milestones" / "m30_golive",
        m31_slo_incident_dir=report_root / "m31_slo_incident",
    )
    summary_obj = facade._read_json(summary_js)
    target_day = str(summary_obj.get("day") or day or "")

    manual_dir = report_root / "dev" / "manual"
    decision_md, decision_obj = facade.generate_decision_story_report(
        events_path,
        manual_dir / "decision_story",
        day=target_day or day,
    )
    run_cards_md, run_cards_obj = facade.generate_run_card_report(
        events_path,
        manual_dir / "run_cards",
        day=target_day or day,
    )

    return {
        "day": target_day or (day or ""),
        "operator_summary_md": str(summary_md),
        "operator_summary_json": str(summary_js),
        "decision_story_md": str(decision_md),
        "decision_story_total": int(decision_obj.get("story_total") or 0),
        "run_cards_md": str(run_cards_md),
        "run_card_total": int(run_cards_obj.get("card_total") or 0),
    }


def _run_context_default_r3_impl(run_id, *, facade):
    return {
        "run_id": run_id,
        "first_epoch": 0,
        "last_epoch": 0,
        "symbol": "",
        "action": "",
        "qty": 0,
        "execution_status": "UNKNOWN",
        "guard_status": "none",
        "guard_reason": "",
        "guard_reason_human": "none",
        "key_reason": "",
        "key_reason_raw": "",
        "technical_evidence": "",
        "sentiment_evidence": "",
        "policy_evidence": "",
        "news_status": {"symbol_sentiment_status": "", "global_sentiment_status": ""},
        "invalidation": {},
        "operator_intervention": [],
        "final_outcome": "",
        "risk_flags": [],
        "llm": {},
        "decision": {},
        "monitor_entry": {},
        "scanner_selection": {},
        "strategist_policy_resolution": {},
        "commander_route": {},
        "verdict": {},
        "execution": {},
        "strategy_frame": {},
    }


def _build_report_freshness_r3_impl(day_rows, *, facade):
    latest_run_id = ""
    latest_epoch = 0
    run_ids: set[str] = set()
    for row in day_rows:
        run_id = str(row.get("run_id") or "").strip()
        if run_id:
            run_ids.add(run_id)
        epoch = int(row.get("_epoch") or 0)
        if epoch <= 0:
            continue
        if epoch >= latest_epoch:
            latest_epoch = epoch
            latest_run_id = run_id
    return {
        "generated_at": facade._utc_now_iso(),
        "source_run_count": int(len(run_ids)),
        "latest_run_id": latest_run_id,
        "latest_run_ts": facade._epoch_to_iso(latest_epoch),
    }


def _canonical_report_root_r3_impl(report_dir, *, facade):
    if report_dir.name == "operator_summary":
        return report_dir.parent
    if report_dir.name == "daily" and report_dir.parent.name == "operator_summary":
        return report_dir.parent.parent
    if report_dir.parent.name == "daily" and report_dir.parent.parent.name == "operator_summary":
        return report_dir.parent.parent.parent
    if report_dir.name in {"daily", "metrics"}:
        return report_dir.parent
    if report_dir.name in {"run_cards", "decision_story"}:
        parent = report_dir.parent
        if parent.name == "manual" and parent.parent.name == "dev":
            return parent.parent.parent
    if report_dir.name == "trade_explain":
        parent = report_dir.parent
        if parent.name == "analysis" and parent.parent.name == "dev":
            return parent.parent.parent
    return report_dir


def _apply_commander_route_overlay_r3_impl(stories, route_summary, *, facade):
    by_run = route_summary.get("by_run") if isinstance(route_summary.get("by_run"), dict) else {}
    if not by_run:
        return stories
    for story in stories:
        run_id = str(story.get("run_id") or "").strip()
        if not run_id:
            continue
        route_row = by_run.get(run_id)
        if not isinstance(route_row, dict):
            continue
        existing = story.get("commander_route") if isinstance(story.get("commander_route"), dict) else {}
        merged = {**dict(existing), **dict(route_row)}
        story["commander_route"] = merged
    return stories


def _merge_scanner_handoff_with_selection_r3_impl(handoff, selection, *, facade):
    handoff_row = handoff if isinstance(handoff, dict) else {}
    selection_row = selection if isinstance(selection, dict) else {}
    if not handoff_row and not selection_row:
        return {}
    merged = dict(selection_row)
    merged.update(dict(handoff_row))
    return merged


def _is_trade_story_r3_impl(story, *, facade):
    action = str(story.get("action") or "").strip().upper()
    status = str(story.get("execution_status") or "").strip().upper()
    guard_status = str(story.get("guard_status") or "").strip().lower()
    no_trade = story.get("no_trade_surface") if isinstance(story.get("no_trade_surface"), dict) else {}
    if action in ("BUY", "SELL"):
        return True
    if status in ("EXECUTED", "EXECUTED_OK", "EXECUTED_FAIL", "BLOCKED", "INTENT_ONLY"):
        return True
    if guard_status == "intervened":
        return True
    if str(no_trade.get("no_trade_stage") or "").strip() in {"guard_block", "pre_intent_wait", "pre_intent_noop"}:
        return True
    return False


def _iter_day_rows_with_epoch_r3_impl(events_path, day, *, facade):
    """Streams one day's rows with _epoch/_day attached, without ever
    materializing the day into a list -- backs the day-scoped calls in
    generate_decision_story_report/generate_run_card_report. Relies on
    iter_jsonl_events's own per-day disk cache, so multiple calls for the
    same (events_path, day) within one report -- one per consumer -- only
    pay the full-file scan once; the rest stream the much smaller day cache.
    """
    for raw in facade.iter_jsonl_events(events_path, day=day):
        ts = raw.get("ts") or (raw.get("payload") or {}).get("ts")
        yield {**raw, "_epoch": facade._to_epoch(ts), "_day": facade._utc_day(ts)}
