"""Operator summary trade decision field extraction from lifecycle/story payloads (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _extract_trade_decision_fields_r3_impl(row, reports_root, *, facade):
    trade_dir = facade._trade_dir_for_row(row, reports_root)
    if trade_dir is None:
        return {}
    summary_input = facade._read_json(trade_dir / "reports" / "ai_trade_summary_input.json")
    summary_report = facade._read_json(trade_dir / "reports" / "ai_trade_summary.json")
    full_report = facade._read_json(trade_dir / "reports" / "ai_trade_report.json")
    strategist_summary = facade._read_json(trade_dir / "reports" / "strategist_summary.json")
    exit_payload = facade._read_json(trade_dir / "exit.json")
    lifecycle_bundle = facade._read_json(trade_dir / "lifecycle_bundle.json")
    summary_input = facade._as_dict(summary_input)
    summary_report = facade._as_dict(summary_report)
    full_report = facade._as_dict(full_report)
    strategist_summary = facade._as_dict(strategist_summary)
    exit_payload = facade._as_dict(exit_payload)
    lifecycle_bundle = facade._as_dict(lifecycle_bundle)

    decision_flow = summary_input.get("decision_flow") if isinstance(summary_input.get("decision_flow"), dict) else {}
    if not decision_flow:
        decision_flow = summary_report.get("decision_flow") if isinstance(summary_report.get("decision_flow"), dict) else {}
    shared_facts = full_report.get("shared_facts") if isinstance(full_report.get("shared_facts"), dict) else {}
    if not shared_facts:
        shared_facts = summary_input.get("shared_facts") if isinstance(summary_input.get("shared_facts"), dict) else {}
    market_strategy = facade._as_dict(summary_input.get("market_and_strategy"))
    broker_alignment = facade._first_dict(
        summary_input.get("broker_alignment"),
        summary_report.get("broker_alignment"),
        full_report.get("broker_alignment"),
    )
    strategy_detail = facade._as_dict(strategist_summary.get("strategy_detail"))
    strategy_frame = facade._as_dict(strategist_summary.get("strategy_frame"))
    candidate_watch = facade._as_dict(strategy_detail.get("candidate_watch_policy"))
    entry_visibility = facade._as_dict(decision_flow.get("entry_execution_visibility"))
    if not candidate_watch:
        candidate_watch = facade._as_dict(entry_visibility.get("strategy_candidate_watch_proposal"))
    commander_entry = facade._as_dict(entry_visibility.get("commander_entry_control"))
    entry_observation = facade._as_dict(decision_flow.get("entry_observation"))
    scanner_chart_fit = facade._as_dict(decision_flow.get("scanner_chart_fit"))
    monitor_context = facade._as_dict(exit_payload.get("monitor_context"))
    full_monitor = facade._as_dict(full_report.get("monitor_snapshot"))
    summary_monitor = facade._as_dict(summary_input.get("monitor_snapshot"))
    quant_tactic_surface = facade._first_dict(
        summary_input.get("quant_tactic"),
        summary_report.get("quant_tactic"),
        full_report.get("quant_tactic"),
        full_report.get("quant_tactic_surface"),
    )
    recomputed_quant_tactic_surface = facade.build_quant_tactic_surface(full_report)
    if recomputed_quant_tactic_surface:
        quant_tactic_surface = recomputed_quant_tactic_surface
    entry_quant_decision = facade._first_dict(
        full_monitor.get("entry_quant_decision"),
        summary_monitor.get("entry_quant_decision"),
        monitor_context.get("entry_quant_decision"),
        facade._first_recursive_dict(summary_input, summary_report, full_report, exit_payload, lifecycle_bundle, key="entry_quant_decision"),
    )
    exit_quant_decision = facade._first_dict(
        full_monitor.get("exit_quant_decision"),
        summary_monitor.get("exit_quant_decision"),
        monitor_context.get("exit_quant_decision"),
        facade._first_recursive_dict(summary_input, summary_report, full_report, exit_payload, lifecycle_bundle, key="exit_quant_decision"),
    )
    quant_factor_snapshot = facade._first_dict(
        full_monitor.get("quant_factor_snapshot"),
        summary_monitor.get("quant_factor_snapshot"),
        monitor_context.get("quant_factor_snapshot"),
        facade._first_recursive_dict(summary_input, summary_report, full_report, exit_payload, lifecycle_bundle, key="quant_factor_snapshot"),
    )
    quant_factors = facade._as_dict(quant_factor_snapshot.get("factors"))
    tactic_suitability = facade._first_dict(
        facade._dig(full_report, "why_this_symbol_was_chosen", "tactic_suitability"),
        facade._dig(summary_input, "why_this_symbol_was_chosen", "tactic_suitability"),
        facade._dig(summary_report, "why_this_symbol_was_chosen", "tactic_suitability"),
        entry_quant_decision.get("tactic_suitability"),
        facade._first_recursive_dict(summary_input, summary_report, full_report, exit_payload, lifecycle_bundle, key="tactic_suitability"),
    )
    entry_focus = facade._as_dict(entry_visibility.get("monitor_focus_context"))
    entry_grouped = facade._as_dict(entry_visibility.get("entry_grouped_logic_trace"))
    if not entry_grouped:
        entry_grouped = facade._as_dict(entry_focus.get("entry_grouped_logic_trace"))
    if not entry_grouped and str(entry_focus.get("entry_triggered") or "").lower() not in {"true", "1"}:
        entry_grouped = facade._as_dict(monitor_context.get("entry_grouped_logic_trace"))
    if not entry_grouped and str(entry_focus.get("entry_triggered") or "").lower() not in {"true", "1"}:
        entry_grouped = facade._as_dict(facade._find_key_recursive(exit_payload, "entry_grouped_logic_trace"))
    human_detail = facade._as_dict(entry_grouped.get("human_chart_detail_observed"))
    if not human_detail:
        human_detail = facade._as_dict(entry_observation)

    out: Dict[str, Any] = {
        "trade_root_path": str(trade_dir),
        "report_path": str(trade_dir / "reports" / "ai_trade_report.json"),
    }
    entry_reason = facade._entry_reason_from_decision_flow(decision_flow, fallback=row.get("entry_reason"))
    exit_reason = str(
        decision_flow.get("exit_trigger")
        or decision_flow.get("exit_reason")
        or shared_facts.get("exit_reason")
        or row.get("exit_reason")
        or ""
    ).strip()
    if entry_reason:
        out["entry_reason"] = entry_reason
    if exit_reason:
        out["exit_reason"] = exit_reason
    if shared_facts:
        out["last_action"] = str(shared_facts.get("action") or row.get("last_action") or "")
        out["last_status"] = str(shared_facts.get("status") or row.get("last_status") or row.get("status") or "")
    if broker_alignment:
        alignment_status = facade._text_value(broker_alignment.get("status"))
        if alignment_status:
            out["broker_alignment_status"] = alignment_status
        for key in (
            "local_total",
            "broker_total",
            "missing_in_local_total",
            "missing_in_broker_total",
            "account_snapshot_error_count",
        ):
            value = broker_alignment.get(key)
            if facade._safe_int(value, default=-1) >= 0:
                out[f"broker_alignment_{key}"] = facade._safe_int(value)
        snapshot_status = facade._text_value(broker_alignment.get("account_snapshot_status"))
        if snapshot_status:
            out["broker_account_snapshot_status"] = snapshot_status
    for field in ("lifecycle_completeness", "trade_origin", "evidence_recovery_used"):
        if lifecycle_bundle.get(field) not in (None, ""):
            out[field] = lifecycle_bundle.get(field)

    final_playbook = facade._first_text(
        strategy_detail.get("final_playbook"),
        strategy_frame.get("playbook"),
        lifecycle_bundle.get("strategist_summary", {}).get("playbook") if isinstance(lifecycle_bundle.get("strategist_summary"), dict) else "",
        market_strategy.get("playbook"),
        row.get("playbook"),
    )
    if final_playbook:
        out["final_playbook"] = final_playbook
        out["playbook"] = final_playbook
    for key, value in {
        "pre_llm_playbook": strategy_detail.get("pre_llm_playbook"),
        "llm_requested_playbook": strategy_detail.get("llm_requested_playbook") or strategy_detail.get("requested_playbook"),
        "tactical_strategy": strategy_detail.get("tactical_strategy") or candidate_watch.get("tactical_strategy"),
        "risk_tone": candidate_watch.get("risk_tone") or market_strategy.get("risk_tone"),
        "trade_aggressiveness": candidate_watch.get("trade_aggressiveness"),
        "strategy_horizon": facade._first_text(
            facade._dig(lifecycle_bundle, "monitor_summary", "exit_vs_strategy_intent", "commander_horizon_policy", "strategy_horizon"),
            facade._dig(lifecycle_bundle, "monitor_summary", "exit_vs_strategy_intent", "strategy_horizon"),
            facade._find_key_recursive(exit_payload, "strategy_horizon"),
            facade._dig(lifecycle_bundle, "trade_lifecycle", "exit", "monitor_context", "strategy_horizon"),
        ),
        "market_regime": candidate_watch.get("market_regime"),
    }.items():
        text = facade._text_value(value)
        if text:
            out[key] = text
    if candidate_watch:
        out["candidate_watch_max_priority_rank"] = facade._safe_int(candidate_watch.get("max_priority_rank"))
        out["candidate_watch_max_runner_ups"] = facade._safe_int(candidate_watch.get("max_runner_ups"))
        cascade_bucket = facade._bool_bucket(candidate_watch.get("cascade_enabled"))
        if cascade_bucket:
            out["candidate_watch_cascade_enabled"] = cascade_bucket
    for key in ("candidate_watch_policy_effect", "candidate_watch_policy_clamp_reason", "mode", "decision"):
        text = facade._text_value(commander_entry.get(key))
        if text:
            out[f"commander_entry_{key}"] = text

    scanner_rank = facade._safe_int(decision_flow.get("scanner_rank") or decision_flow.get("selected_rank"), default=0)
    if scanner_rank > 0:
        out["scanner_rank"] = scanner_rank
        out["scanner_rank_bucket"] = facade._rank_bucket(scanner_rank)
    for key, value in {
        "scanner_selection_basis": decision_flow.get("selection_basis"),
        "scanner_rank_basis": decision_flow.get("scanner_rank_basis"),
        "scanner_selection_path": decision_flow.get("selection_path"),
        "scanner_chart_fit_authority": scanner_chart_fit.get("authority") or decision_flow.get("scanner_chart_fit_authority"),
    }.items():
        text = facade._text_value(value)
        if text:
            out[key] = text
    scanner_chart_score = scanner_chart_fit.get("score")
    if scanner_chart_score is None:
        scanner_chart_score = decision_flow.get("scanner_chart_fit_score")
    if facade._safe_float(scanner_chart_score) is not None:
        out["scanner_chart_fit_score"] = facade._safe_float(scanner_chart_score)
        out["scanner_chart_fit_score_bucket"] = facade._score_bucket(scanner_chart_score)

    for key, source in {
        "human_chart_entry_score": (
            entry_observation.get("human_chart_entry_score")
            or entry_grouped.get("human_chart_entry_score")
            or entry_focus.get("human_chart_entry_score")
        ),
        "human_chart_setup_quality": entry_grouped.get("human_chart_setup_quality") or entry_focus.get("human_chart_setup_quality"),
        "human_candle_quality_score": entry_observation.get("human_candle_quality_score") or entry_grouped.get("human_candle_quality_score"),
        "human_vwap_reference_quality_score": entry_observation.get("human_vwap_reference_quality_score") or entry_grouped.get("human_vwap_reference_quality_score"),
        "human_reward_room_score": entry_observation.get("human_reward_room_score") or entry_grouped.get("human_reward_room_score"),
        "human_multi_window_structure_score": entry_observation.get("human_multi_window_structure_score") or entry_grouped.get("human_multi_window_structure_score"),
        "entry_confidence_score": entry_observation.get("confidence_score") or facade._dig(monitor_context, "entry_condition_scores", "confidence_score"),
        "vwap_source": entry_observation.get("vwap_source") or human_detail.get("vwap_source"),
        "late_entry_risk": entry_grouped.get("late_entry_risk"),
    }.items():
        text = facade._text_value(source)
        if text:
            out[key] = source
    for key in (
        "human_chart_entry_score",
        "human_candle_quality_score",
        "human_vwap_reference_quality_score",
        "human_reward_room_score",
        "human_multi_window_structure_score",
        "entry_confidence_score",
    ):
        if facade._safe_float(out.get(key)) is not None:
            out[f"{key}_bucket"] = facade._score_bucket(out.get(key))
    reward_room_pct = human_detail.get("reward_room_pct") or entry_observation.get("reward_room_pct")
    if facade._safe_float(reward_room_pct) is not None:
        out["reward_room_pct"] = facade._safe_float(reward_room_pct)
        out["reward_room_pct_bucket"] = facade._pct_bucket(reward_room_pct)

    exit_triggered = facade._find_key_recursive(exit_payload, "exit_triggered")
    if isinstance(exit_triggered, bool):
        out["monitor_exit_triggered"] = "true" if exit_triggered else "false"
    cost_floor_blocked = facade._find_key_recursive(exit_payload, "cost_aware_profit_floor_blocked")
    cost_floor_met = facade._find_key_recursive(exit_payload, "cost_aware_profit_floor_met")
    if cost_floor_blocked is not None or cost_floor_met is not None:
        out["cost_floor_state"] = (
            "blocked" if bool(cost_floor_blocked) else "met" if bool(cost_floor_met) else "not_met"
        )
    peak_urgent = facade._find_key_recursive(exit_payload, "peak_drawdown_profit_protection_urgent")
    peak_armed = facade._find_key_recursive(exit_payload, "peak_drawdown_armed")
    if bool(peak_urgent):
        out["peak_drawdown_state"] = "urgent"
    elif bool(peak_armed):
        out["peak_drawdown_state"] = "armed"
    elif facade._safe_float(facade._find_key_recursive(exit_payload, "peak_drawdown")) is not None:
        out["peak_drawdown_state"] = "observed"
    time_blocked = facade._find_key_recursive(exit_payload, "time_limit_reassessment_blocked")
    time_reached = facade._find_key_recursive(exit_payload, "time_limit_reached")
    if time_blocked is not None or time_reached is not None:
        out["time_limit_reassessment_state"] = (
            "blocked" if bool(time_blocked) else "reached" if bool(time_reached) else "not_reached"
        )
    if facade._safe_float(facade._find_key_recursive(exit_payload, "vwap_distance")) is not None:
        out["vwap_breakdown_state"] = "observed"
    quant_tactic = facade._first_text(
        quant_tactic_surface.get("tactic_id"),
        entry_quant_decision.get("tactic_id"),
        exit_quant_decision.get("tactic_id"),
        quant_factor_snapshot.get("tactic_id"),
        out.get("tactical_strategy"),
    )
    if quant_tactic:
        out["quant_tactic_id"] = quant_tactic
        if not out.get("tactical_strategy"):
            out["tactical_strategy"] = quant_tactic
    tactic_source = facade._text_value(quant_tactic_surface.get("tactic_id_source"))
    if tactic_source:
        out["quant_tactic_id_source"] = tactic_source
    tactic_mismatches = quant_tactic_surface.get("tactic_id_mismatches")
    if isinstance(tactic_mismatches, list):
        out["quant_tactic_mismatch_count"] = len([row for row in tactic_mismatches if isinstance(row, dict)])
    elif entry_quant_decision.get("tactic_id") and exit_quant_decision.get("tactic_id"):
        out["quant_tactic_mismatch_count"] = int(
            str(entry_quant_decision.get("tactic_id")).strip() != str(exit_quant_decision.get("tactic_id")).strip()
        )
    exit_tactic_drifts = quant_tactic_surface.get("exit_tactic_drifts")
    if isinstance(exit_tactic_drifts, list):
        out["quant_exit_tactic_drift_count"] = len([row for row in exit_tactic_drifts if isinstance(row, dict)])
    for key, value in {
        "entry_quant_decision": entry_quant_decision.get("decision"),
        "exit_quant_decision": exit_quant_decision.get("decision"),
        "entry_quant_primary_blocker": facade._first_reason_bucket(entry_quant_decision.get("blockers")),
        "entry_quant_primary_warning": facade._first_reason_bucket(entry_quant_decision.get("warnings")),
        "exit_quant_primary_blocker": facade._first_reason_bucket(exit_quant_decision.get("blockers")),
        "exit_quant_primary_warning": facade._first_reason_bucket(exit_quant_decision.get("warnings")),
        "exit_quant_confirmation_state": facade._confirmation_bucket(exit_quant_decision.get("confirmation_pending")),
        "exit_quant_hold_window_state": facade._mismatch_bucket(exit_quant_decision.get("hold_window_mismatch")),
        "exit_quant_hard_exit": facade._bool_bucket(exit_quant_decision.get("hard_exit")),
        "tactic_suitability_tier": tactic_suitability.get("tier"),
        "entry_quant_cost_floor_state": facade._dig(entry_quant_decision, "cost_edge", "cost_floor_state") or quant_factors.get("cost_floor_state"),
    }.items():
        text = facade._text_value(value)
        if text:
            out[key] = text
    if facade._safe_float(tactic_suitability.get("score")) is not None:
        out["tactic_suitability_score"] = facade._safe_float(tactic_suitability.get("score"))
        out["tactic_suitability_score_bucket"] = facade._score_bucket(tactic_suitability.get("score"))
    if facade._safe_float(facade._dig(entry_quant_decision, "cost_edge", "cost_adjusted_edge_pct")) is not None:
        edge = facade._safe_float(facade._dig(entry_quant_decision, "cost_edge", "cost_adjusted_edge_pct"))
        out["entry_quant_cost_edge_pct"] = edge
        out["entry_quant_cost_edge_bucket"] = facade._pct_bucket(edge)
    if facade._safe_int(exit_quant_decision.get("actual_hold_sec"), 0) > 0:
        out["exit_quant_actual_hold_sec"] = facade._safe_int(exit_quant_decision.get("actual_hold_sec"), 0)
    return out
