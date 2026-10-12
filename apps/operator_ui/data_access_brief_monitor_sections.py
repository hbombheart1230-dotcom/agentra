"""Operator brief monitor/position/exit/watch/guard/entry detail sections.

Second Pass (P1.5) intra-function extraction from `apps/operator_ui/data_access_core.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def brief_monitor_canonical_active_exit_axis_canonical_ave(canonical_monitor_snapshot, monitor_summary, monitor_trace, *, facade):
    canonical_average_price = str(canonical_monitor_snapshot.get("average_price") or "").strip()
    canonical_peak_price = str(canonical_monitor_snapshot.get("peak_price") or "").strip()
    canonical_current_drawdown = str(canonical_monitor_snapshot.get("current_drawdown") or "").strip()
    canonical_peak_drawdown = str(canonical_monitor_snapshot.get("peak_drawdown") or "").strip()
    canonical_vwap_distance = str(canonical_monitor_snapshot.get("vwap_distance") or "").strip()
    canonical_stop_loss = str(canonical_monitor_snapshot.get("stop_loss") or "").strip()
    canonical_effective_stop = str(canonical_monitor_snapshot.get("effective_stop") or "").strip()
    canonical_effective_stop_reason = str(canonical_monitor_snapshot.get("effective_stop_reason") or "").strip()
    canonical_take_profit = str(canonical_monitor_snapshot.get("take_profit") or "").strip()
    canonical_price_source = str(canonical_monitor_snapshot.get("price_source") or "").strip()
    canonical_feature_source = str(canonical_monitor_snapshot.get("feature_source") or "").strip()
    canonical_price_source_policy = str(canonical_monitor_snapshot.get("price_source_policy") or "").strip()
    canonical_active_exit_axis = str(canonical_monitor_snapshot.get("active_exit_axis") or "").strip()
    canonical_watch_axes = [str(x or "") for x in list(canonical_monitor_snapshot.get("watch_axes") or []) if str(x or "").strip()]
    canonical_hold_reasons = [str(x or "") for x in list(canonical_monitor_snapshot.get("hold_reasons") or []) if str(x or "").strip()]
    canonical_exit_triggers = [str(x or "") for x in list(canonical_monitor_snapshot.get("exit_triggers") or []) if str(x or "").strip()]

    entry_evaluated = bool(
        canonical_monitor_snapshot.get("entry_evaluated")
        or monitor_summary.get("entry_evaluated")
        or monitor_trace.get("entry_evaluated")
    )
    entry_triggered = bool(
        canonical_monitor_snapshot.get("entry_triggered")
        or monitor_summary.get("entry_triggered")
        or monitor_trace.get("entry_triggered")
    )
    entry_reason_code = str(
        canonical_monitor_snapshot.get("entry_reason")
        or monitor_summary.get("entry_reason")
        or monitor_trace.get("entry_reason")
        or ""
    ).strip()
    entry_pattern = str(
        canonical_monitor_snapshot.get("entry_pattern")
        or monitor_summary.get("entry_pattern")
        or monitor_trace.get("entry_pattern")
        or ""
    ).strip()
    entry_metrics = (
        canonical_monitor_snapshot.get("entry_metrics")
        if isinstance(canonical_monitor_snapshot.get("entry_metrics"), dict)
        else (
            monitor_summary.get("entry_metrics")
            if isinstance(monitor_summary.get("entry_metrics"), dict)
            else (
                monitor_trace.get("entry_metrics")
                if isinstance(monitor_trace.get("entry_metrics"), dict)
                else {}
            )
        )
    )
    entry_guard_reason = str(
        canonical_monitor_snapshot.get("entry_guard_reason")
        or monitor_summary.get("entry_guard_reason")
        or monitor_trace.get("entry_guard_reason")
        or ""
    ).strip()
    entry_signal_chain = [
        str(x or "")
        for x in list(
            canonical_monitor_snapshot.get("entry_signal_chain")
            or monitor_summary.get("entry_signal_chain")
            or monitor_trace.get("entry_signal_chain")
            or []
        )
        if str(x or "").strip()
    ]

    hold_reasons: facade.List[str] = []
    return (canonical_active_exit_axis, canonical_average_price, canonical_current_drawdown, canonical_effective_stop, canonical_effective_stop_reason, canonical_exit_triggers, canonical_feature_source, canonical_hold_reasons, canonical_peak_drawdown, canonical_peak_price, canonical_price_source, canonical_price_source_policy, canonical_stop_loss, canonical_take_profit, canonical_vwap_distance, canonical_watch_axes, entry_evaluated, entry_guard_reason, entry_metrics, entry_pattern, entry_reason_code, entry_signal_chain, entry_triggered, hold_reasons)


def brief_monitor_decision_reason_execution_quality(prefer_runtime_reporter, reporter, canonical_trade, execution_action, monitor_reason, exit_reason, final_action, selected_rank, universe_size, feature_coverage, selected_symbol, take_profit_text, stop_loss_text, vix_level, detected_themes, trade_report, scanner_summary, *, facade):
    reporter_found = bool(reporter.get("found")) if prefer_runtime_reporter else (
        bool(reporter.get("found")) or str(canonical_trade.get("reporter_status") or "").strip().lower() == "linked"
    )
    reporter_reason_key = str(reporter.get("reason") or "").strip()
    if reporter_found:
        reporter_status = "linked"
        reporter_reason = "same-day reporter analysis is linked to this run"
    elif reporter_reason_key == "same_day_report_missing":
        reporter_status = "pending"
        reporter_reason = "same-day reporter analysis file is not generated yet"
    elif reporter_reason_key == "run_not_linked_in_same_day_report":
        reporter_status = "pending"
        reporter_reason = "same-day reporter analysis exists, but this run_id is not linked yet"
    else:
        reporter_status = "missing"
        reporter_reason = "reporter linkage is unavailable for this run"

    run_grade = str((reporter.get("ai_run_grade") if prefer_runtime_reporter else "") or canonical_trade.get("reporter_grade") or reporter.get("ai_run_grade") or "").strip()
    ai_summary = str((reporter.get("ai_summary") if prefer_runtime_reporter else "") or canonical_trade.get("reporter_summary") or reporter.get("ai_summary") or "").strip()
    strategy_alignment = "strategy frame and scanner trace were captured"
    execution_quality = "execution log present" if execution_action in {"BUY", "SELL"} else "no executed order in this run"
    monitor_consistency = f"monitor={monitor_reason or '-'} / exit={exit_reason or '-'}"
    if reporter_found:
        trade_quality = f"grade {run_grade}" if run_grade else "grade not provided"
        key_finding = ai_summary or "reporter summary exists but key finding text is empty"
    else:
        trade_quality = "post-trade quality grade is pending"
        key_finding = ai_summary or reporter_reason

    canonical_report_summary = str(canonical_trade.get("report_summary") or "")
    generic_lifecycle_summary = canonical_report_summary.lower().startswith("current lifecycle status is")
    if canonical_report_summary and not (final_action == "SELL" and generic_lifecycle_summary):
        decision_reason = str(canonical_trade.get("report_summary"))
    elif final_action == "BUY":
        decision_reason = (
            f"scanner rank #{selected_rank or 1} out of {max(universe_size, 1)} with strong selection factors, "
            f"chart coverage {feature_coverage.get('present')}/{feature_coverage.get('total')}, and approved execution."
        )
    elif final_action == "SELL":
        decision_reason = (
            f"monitor/supervisor flow triggered SELL for {selected_symbol or '-'} "
            f"after exit condition review ({exit_reason or monitor_reason or 'triggered'})."
        )
    elif final_action == "HOLD":
        decision_reason = (
            f"scanner rank #{selected_rank or 1} candidate is retained with chart coverage "
            f"{feature_coverage.get('present')}/{feature_coverage.get('total')}, and no active exit trigger yet."
        )
    else:
        decision_reason = (
            f"no executable BUY/SELL action yet; waiting for entry confirmation while monitoring {selected_symbol or 'candidate'}."
        )

    watch_next: facade.List[str] = []
    if take_profit_text != "-":
        watch_next.append(f"take-profit proximity ({take_profit_text})")
    if stop_loss_text != "-":
        watch_next.append(f"stop-loss proximity ({stop_loss_text})")
    if vix_level is not None:
        watch_next.append(f"volatility trend (VIX {facade._format_float(vix_level, 2)})")
    if detected_themes:
        watch_next.append(f"theme strength drift ({', '.join(detected_themes[:2])})")
    if not watch_next:
        watch_next = ["entry/exit trigger activation", "volatility expansion", "sector weakness"]

    thesis_invalidation = [
        "stop-loss breach or abnormal drawdown",
        "scanner and monitor signal divergence",
        "negative macro/news regime shift",
    ]

    report_available = bool(trade_report.get("report_available"))
    report_diag = (
        trade_report.get("ai_report_diagnostics")
        if isinstance(trade_report.get("ai_report_diagnostics"), dict)
        else {}
    )
    report_status = str(
        report_diag.get("report_status")
        or trade_report.get("report_status")
        or ("available" if report_available else "skipped")
    ).strip().lower()
    report_reason = str(
        report_diag.get("report_reason_human")
        or trade_report.get("report_reason_human")
        or facade._report_reason_human(trade_report.get("report_reason_code"))
    ).strip()
    report_next_step = str(
        report_diag.get("next_expected_step")
        or trade_report.get("report_next_expected_step")
        or facade._report_next_step(trade_report.get("report_reason_code"))
    ).strip()
    report_model = str(
        report_diag.get("llm_model_used")
        or trade_report.get("report_generation_model")
        or "-"
    ).strip()
    report_trade_id = str(trade_report.get("trade_id") or "")
    report_lifecycle_status = str(trade_report.get("lifecycle_status") or "")
    report_lifecycle_summary = str(trade_report.get("lifecycle_summary") or "")
    report_story_type = str(trade_report.get("story_type_label") or trade_report.get("story_type") or "No linked report")
    report_mode = str(trade_report.get("execution_mode_label") or "-")
    report_summary = str(trade_report.get("report_summary") or "")
    report_link = str(trade_report.get("report_link") or "")
    focus_symbol = selected_symbol or facade._clean_brief_text(scanner_summary.get("top_stock") or "") or "-"
    return (decision_reason, execution_quality, focus_symbol, key_finding, monitor_consistency, report_available, report_lifecycle_status, report_lifecycle_summary, report_link, report_mode, report_model, report_next_step, report_reason, report_status, report_story_type, report_summary, report_trade_id, reporter_reason, reporter_status, run_grade, strategy_alignment, thesis_invalidation, trade_quality, watch_next)


def brief_monitor_execution_status_label_next_expected_ste(verdict, execution, canonical_trade, thresholds, stop_loss, stop_loss_text, canonical_monitor_snapshot, effective_stop_text, take_profit, take_profit_text, canonical_effective_stop_reason, effective_stop_reason, watch_next, final_action, selected_symbol, active_exit_axis, playbook, global_score, vix_level, strategist_summary, selection_reasons, selected_why, *, facade):
    supervisor_allowed = bool(verdict.get("allowed"))
    execution_status_label = str(
        execution.get("fill_status_summary")
        or execution.get("status")
        or canonical_trade.get("execution_mode_label")
        or "not captured"
    ).strip()
    stop_policy_trace = dict(canonical_trade.get("monitor_stop_policy_trace") or {}) if isinstance(canonical_trade.get("monitor_stop_policy_trace"), dict) else {}
    hard_stop_source = stop_policy_trace.get("hard_stop_pct")
    if hard_stop_source in (None, ""):
        hard_stop_source = thresholds.get("hard_stop_pct")
    if hard_stop_source in (None, ""):
        hard_stop_source = stop_loss
    hard_stop_brief = (
        facade._format_percent(hard_stop_source, 2)
        if hard_stop_source not in (None, "")
        else canonical_monitor_snapshot.get("stop_loss")
        or stop_loss_text
    )
    effective_stop_brief = canonical_monitor_snapshot.get("effective_stop") or effective_stop_text
    take_profit_source = stop_policy_trace.get("take_profit_pct")
    if take_profit_source in (None, ""):
        take_profit_source = take_profit
    take_profit_brief = canonical_monitor_snapshot.get("take_profit") or (facade._format_percent(take_profit_source, 2) if take_profit_source not in (None, "") else take_profit_text)
    effective_stop_reason_brief = (
        canonical_effective_stop_reason
        or (facade._friendly_exit_reason(effective_stop_reason or "stop_loss") if effective_stop_brief != "-" else "")
    )
    stop_policy_summary: facade.List[str] = []
    if hard_stop_brief and str(hard_stop_brief).strip() not in {"", "-"}:
        stop_policy_summary.append(f"Hard fail-safe stop {hard_stop_brief}")
    strategist_baseline_stop = stop_policy_trace.get("strategist_baseline_stop_loss_pct")
    if strategist_baseline_stop not in (None, ""):
        stop_policy_summary.append(
            f"Strategist baseline adaptive stop {facade._format_percent(strategist_baseline_stop, 2)}"
        )
    if effective_stop_brief and str(effective_stop_brief).strip() not in {"", "-"}:
        stop_policy_summary.append(f"Effective stop {effective_stop_brief} ({effective_stop_reason_brief or 'active stop'})")
    if take_profit_brief and str(take_profit_brief).strip() not in {"", "-"}:
        stop_policy_summary.append(f"Take profit {take_profit_brief}")
    strategist_baseline_take_profit = stop_policy_trace.get("strategist_baseline_take_profit_pct")
    if strategist_baseline_take_profit not in (None, ""):
        stop_policy_summary.append(
            f"Strategist baseline take profit {facade._format_percent(strategist_baseline_take_profit, 2)}"
        )
    trailing_stop_brief = stop_policy_trace.get("trailing_stop_pct")
    if trailing_stop_brief in (None, ""):
        trailing_stop_brief = thresholds.get("trailing_stop_pct")
    if trailing_stop_brief not in (None, ""):
        stop_policy_summary.append(f"Trailing stop {facade._format_percent(trailing_stop_brief, 2)}")
    strategist_baseline_trailing = stop_policy_trace.get("strategist_baseline_trailing_stop_pct")
    if strategist_baseline_trailing not in (None, ""):
        stop_policy_summary.append(
            f"Strategist baseline trailing stop {facade._format_percent(strategist_baseline_trailing, 2)}"
        )

    next_expected_step = ""
    if watch_next:
        next_expected_step = str(watch_next[0] or "").strip()
    elif final_action == "WAIT":
        next_expected_step = f"Wait for clearer entry confirmation on {selected_symbol or 'the current focus symbol'}."
    elif final_action in {"BUY", "HOLD"}:
        next_expected_step = f"Keep monitoring {selected_symbol or 'the position'} against {active_exit_axis or 'the active exit axis'}."
    elif final_action == "SELL":
        next_expected_step = "Review the closed trade and wait for the next qualified setup."

    strategist_evidence_summary_bits = [
        f"{playbook} playbook" if playbook else "",
        f"regime {strategist_summary.get('market_regime')}" if strategist_summary.get("market_regime") else "",
        f"global sentiment {facade._format_float(global_score, 2)}" if global_score is not None else "",
        f"VIX {facade._format_float(vix_level, 2)}" if vix_level is not None else "",
    ]
    strategist_evidence_summary = ", ".join([bit for bit in strategist_evidence_summary_bits if bit]) or "Strategist evidence was captured for this run."
    selection_reason_text = (
        selection_reasons[0]
        if selection_reasons
        else str(canonical_trade.get("selection_summary") or selected_why or "Selection rationale was not explicitly persisted.")
    )
    return (execution_status_label, next_expected_step, selection_reason_text, stop_policy_summary, strategist_evidence_summary, supervisor_allowed)
