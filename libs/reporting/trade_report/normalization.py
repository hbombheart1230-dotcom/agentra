from __future__ import annotations

from typing import Any, Dict, Mapping


def normalize_trade_report_output(
    story_input: Dict[str, Any],
    report: Dict[str, Any],
    *,
    deps: Mapping[str, Any],
) -> Dict[str, Any]:
    """Normalize report output using façade-injected compatibility seams."""

    _build_shared_summary_seed = deps["build_shared_summary_seed"]
    _clip = deps["clip"]
    _actual_lifecycle_action = deps["actual_lifecycle_action"]
    _action_from_exit_reason = deps["action_from_exit_reason"]
    _lifecycle_summary_conflicts_with_status = deps["lifecycle_summary_conflicts_with_status"]
    _exit_reason_label = deps["exit_reason_label"]
    _compact_strategist_report_context = deps["compact_strategist_report_context"]
    _as_dict = deps["as_dict"]
    _build_report_strategist_refresh_trace = deps["build_report_strategist_refresh_trace"]
    _extract_entry_execution_visibility = deps["extract_entry_execution_visibility"]
    _story_post_exit_shadow = deps["story_post_exit_shadow"]
    _is_low_information_bullet = deps["is_low_information_bullet"]
    _report_section_provenance = deps["report_section_provenance"]
    _normalize_provenance_entry = deps["normalize_provenance_entry"]
    _operatorize_report_section = deps["operatorize_report_section"]
    _listify = deps["listify"]
    _is_open_position_placeholder_reason = deps["is_open_position_placeholder_reason"]
    build_trade_report_truth_surface = deps["build_trade_report_truth_surface"]
    build_trade_report_memory_surface = deps["build_trade_report_memory_surface"]
    build_trade_memory_application_surface = deps["build_trade_memory_application_surface"]
    _sanitize_report_language_fields = deps["sanitize_report_language_fields"]

    out = dict(report or {})
    shared_seed = _build_shared_summary_seed(story_input)
    action = _clip(shared_seed.get("lifecycle_action"), max_len=24) or _actual_lifecycle_action(story_input)
    symbol = _clip(shared_seed.get("symbol"), max_len=32) or _clip(out.get("symbol"), max_len=32) or "unknown"
    status_text = _clip(shared_seed.get("lifecycle_status"), max_len=32) or _clip(out.get("status"), max_len=32) or "closed"
    story_type = _clip(story_input.get("story_type"), max_len=40) or _clip(out.get("story_type"), max_len=40)
    execution_mode = _clip(story_input.get("execution_mode_label"), max_len=80) or _clip(out.get("execution_mode_label"), max_len=80)
    if status_text.lower() == "closed" and str(action or "").upper() == "BUY":
        resolved_trade_facts = (
            shared_seed.get("resolved_trade_facts")
            if isinstance(shared_seed.get("resolved_trade_facts"), dict)
            else {}
        )
        report_shared_facts = out.get("shared_facts") if isinstance(out.get("shared_facts"), dict) else {}
        report_exit_decision = out.get("exit_decision") if isinstance(out.get("exit_decision"), dict) else {}
        for candidate in (
            _action_from_exit_reason(resolved_trade_facts.get("exit_reason")),
            _action_from_exit_reason(report_shared_facts.get("exit_reason")),
            _action_from_exit_reason(report_exit_decision.get("summary")),
        ):
            if candidate in {"SELL", "EXIT"}:
                action = candidate
                break

    out["symbol"] = symbol
    out["action"] = action
    out["status"] = status_text
    if story_type:
        out["story_type"] = story_type
    if execution_mode:
        out["execution_mode_label"] = execution_mode

    executive = out.get("executive_summary") if isinstance(out.get("executive_summary"), dict) else {}
    executive_summary = dict(executive)
    executive_summary["action"] = action
    executive_summary["symbol"] = symbol
    if not str(executive_summary.get("headline") or "").strip():
        executive_summary["headline"] = f"{action} {symbol}"
    if status_text.lower() == "closed" and _lifecycle_summary_conflicts_with_status(
        executive_summary.get("summary"),
        status_text,
    ):
        exit_label = _exit_reason_label(shared_seed.get("exit_reason")) or "매도 실행 확인"
        executive_summary["summary"] = f"Trade {shared_seed.get('trade_id') or ''} for {symbol} is closed. Exit: {exit_label}"
        executive_summary["headline"] = f"{action} {symbol}"
    out["executive_summary"] = executive_summary
    out["report_generation"] = dict(out.get("generation") or {})
    strategist_output = _compact_strategist_report_context(story_input)
    if strategist_output:
        if not _as_dict(strategist_output.get("strategy_refresh_trace")):
            refresh_trace_for_output = _build_report_strategist_refresh_trace(story_input)
            if refresh_trace_for_output:
                strategist_output["strategy_refresh_trace"] = refresh_trace_for_output
        out["strategist_output"] = strategist_output
    entry_execution_visibility = _extract_entry_execution_visibility(story_input)
    if entry_execution_visibility:
        existing_visibility = out.get("entry_execution_visibility") if isinstance(out.get("entry_execution_visibility"), dict) else {}
        out["entry_execution_visibility"] = {**existing_visibility, **entry_execution_visibility}
        monitor_snapshot = out.get("monitor_snapshot") if isinstance(out.get("monitor_snapshot"), dict) else {}
        cascade = _as_dict(entry_execution_visibility.get("monitor_entry_candidate_cascade"))
        if monitor_snapshot and cascade and not _as_dict(monitor_snapshot.get("entry_candidate_cascade")):
            monitor_snapshot = dict(monitor_snapshot)
            monitor_snapshot["entry_candidate_cascade"] = cascade
            out["monitor_snapshot"] = monitor_snapshot
    post_exit_shadow = _story_post_exit_shadow(story_input)
    if post_exit_shadow:
        out["post_exit_shadow"] = dict(post_exit_shadow)
        fact_payload = out.get("fact_payload") if isinstance(out.get("fact_payload"), dict) else {}
        if fact_payload:
            fact_payload = dict(fact_payload)
            fact_payload.setdefault("post_exit_shadow", dict(post_exit_shadow))
            out["fact_payload"] = fact_payload
    refresh_trace = _build_report_strategist_refresh_trace(story_input)
    if refresh_trace:
        existing_refresh = out.get("strategist_refresh_trace") if isinstance(out.get("strategist_refresh_trace"), dict) else {}
        if not existing_refresh or _is_low_information_bullet(existing_refresh.get("summary")):
            out["strategist_refresh_trace"] = refresh_trace

    final_conclusion = out.get("final_operator_conclusion") if isinstance(out.get("final_operator_conclusion"), dict) else {}
    normalized_conclusion = dict(final_conclusion)
    if status_text.lower() == "closed" and _lifecycle_summary_conflicts_with_status(
        normalized_conclusion.get("summary"),
        status_text,
    ):
        normalized_conclusion["summary"] = executive_summary.get("summary") or (
            f"Trade {shared_seed.get('trade_id') or ''} for {symbol} is closed."
        )
    normalized_conclusion["current_action"] = "HOLD" if status_text.lower() == "open" and action == "BUY" else action
    out["final_operator_conclusion"] = normalized_conclusion
    if "section_provenance" not in out:
        out["section_provenance"] = _report_section_provenance(story_input)
    if "evidence_source" not in out:
        out["evidence_source"] = str(story_input.get("evidence_source") or "fallback")
    section_provenance = out.get("section_provenance") if isinstance(out.get("section_provenance"), dict) else {}
    for section_key in (
        "executive_summary",
        "market_context_at_entry",
        "strategist_summary",
        "strategist_refresh_trace",
        "why_this_symbol_was_chosen",
        "entry_decision",
        "holding_monitoring_story",
        "exit_decision",
        "execution_quality",
        "scanner_filters",
        "guard_approval_result",
        "reporter_evaluation",
        "errors_weaknesses_improvement_points",
        "final_operator_conclusion",
    ):
        section = out.get(section_key) if isinstance(out.get(section_key), dict) else {}
        source_entry = (
            _normalize_provenance_entry(section_provenance.get(section_key))
            if isinstance(section_provenance.get(section_key), dict)
            else _normalize_provenance_entry({})
        )
        section["evidence_source"] = str(source_entry.get("evidence_source") or "fallback")
        section["confidence"] = str(source_entry.get("confidence") or "low")
        section["completeness"] = float(source_entry.get("completeness") or 0.0)
        out[section_key] = _operatorize_report_section(section)
    strategist_context_for_theme = _as_dict(shared_seed.get("strategist_context"))
    market_section_for_theme = out.get("market_context_at_entry") if isinstance(out.get("market_context_at_entry"), dict) else {}
    for theme_key in (
        "risk_tone",
        "trade_aggressiveness",
        "monitor_guidance",
        "theme_strength_packet",
        "theme_source",
        "theme_source_status",
        "theme_source_reason",
        "theme_strength_top_themes",
        "theme_strength_scores",
    ):
        if strategist_context_for_theme.get(theme_key) not in (None, "", [], {}) and not market_section_for_theme.get(theme_key):
            market_section_for_theme[theme_key] = strategist_context_for_theme.get(theme_key)
    theme_status = _clip(market_section_for_theme.get("theme_source_status"), max_len=80)
    theme_source = _clip(market_section_for_theme.get("theme_source"), max_len=80)
    theme_reason = _clip(market_section_for_theme.get("theme_source_reason"), max_len=160)
    if theme_status or theme_source or theme_reason:
        theme_bullets = _listify(market_section_for_theme.get("bullets"), max_items=12, max_len=400)
        if not any("Kiwoom theme packet:" in str(row) or "키움 테마 packet:" in str(row) for row in theme_bullets):
            top_themes = ", ".join(
                _listify(market_section_for_theme.get("theme_strength_top_themes"), max_items=6, max_len=80)
            )
            theme_bullets.append(
                "키움 테마 packet: "
                f"source={theme_source or 'not_captured'}, "
                f"status={theme_status or 'not_captured'}, "
                f"reason={theme_reason or 'not_captured'}, "
                f"top_themes={top_themes or 'none'}"
            )
            market_section_for_theme["bullets"] = theme_bullets
        out["market_context_at_entry"] = market_section_for_theme
    if isinstance(out.get("market_context"), dict):
        out["market_context"] = dict(out.get("market_context_at_entry") or {})
    if isinstance(out.get("why_this_symbol"), dict):
        out["why_this_symbol"] = dict(out.get("why_this_symbol_was_chosen") or {})
    if isinstance(out.get("scanner_logic_and_filters"), dict):
        out["scanner_logic_and_filters"] = dict(out.get("scanner_filters") or {})
    if isinstance(out.get("monitor_trigger_reasoning"), dict):
        out["monitor_trigger_reasoning"] = dict(out.get("holding_monitoring_story") or {})
    if isinstance(out.get("execution_result"), dict):
        out["execution_result"] = dict(out.get("execution_quality") or {})
    if shared_seed.get("scanner_evidence_status") == "unavailable":
        scanner_section = out.get("why_this_symbol_was_chosen") if isinstance(out.get("why_this_symbol_was_chosen"), dict) else {}
        current_summary = _clip(scanner_section.get("summary"), max_len=600)
        if not current_summary or _is_low_information_bullet(current_summary):
            scanner_section["summary"] = "Scanner evidence unavailable for this trade. Selection confidence is constrained."
        out["why_this_symbol_was_chosen"] = scanner_section
    if shared_seed.get("strategist_evidence_status") == "unavailable":
        market_section = out.get("market_context_at_entry") if isinstance(out.get("market_context_at_entry"), dict) else {}
        current_summary = _clip(market_section.get("summary"), max_len=600)
        if not current_summary or _is_low_information_bullet(current_summary):
            market_section["summary"] = "Strategist evidence unavailable for this trade. Market-context detail is limited."
        out["market_context_at_entry"] = market_section
    resolved_trade_facts = dict(shared_seed.get("resolved_trade_facts") or {})
    resolved_data_source = dict((_as_dict(resolved_trade_facts).get("data_source")))
    resolved_exit_reason = _clip(shared_seed.get("exit_reason"), max_len=280) or "unavailable"
    report_shared_facts = out.get("shared_facts") if isinstance(out.get("shared_facts"), dict) else {}
    report_exit_decision = out.get("exit_decision") if isinstance(out.get("exit_decision"), dict) else {}
    if status_text.lower() == "closed" and (
        _is_open_position_placeholder_reason(resolved_exit_reason)
        or str(resolved_exit_reason or "").strip().lower() in {"", "unavailable"}
    ):
        for candidate in (
            _clip(report_shared_facts.get("exit_reason"), max_len=280),
            _clip(report_exit_decision.get("summary"), max_len=280),
            _clip(_as_dict(story_input.get("monitor_reason_human")).get("trigger_type"), max_len=280),
            _clip(_as_dict(story_input.get("monitor_reason_human")).get("active_exit_axis"), max_len=280),
            _clip(_as_dict(story_input.get("monitor_reason_human")).get("summary"), max_len=280),
        ):
            if candidate and not _is_open_position_placeholder_reason(candidate):
                resolved_exit_reason = candidate
                resolved_trade_facts["exit_reason"] = candidate
                resolved_data_source["exit_reason"] = "normalize_existing_report"
                resolved_trade_facts["data_source"] = dict(resolved_data_source)
                break

    out["shared_facts"] = {
        "symbol": symbol,
        "trade_id": _clip(shared_seed.get("trade_id"), max_len=120),
        "action": action,
        "status": status_text,
        "holding_duration": _clip(shared_seed.get("holding_duration"), max_len=80) or "unavailable",
        "exit_reason": resolved_exit_reason,
        "pnl": shared_seed.get("pnl", "unavailable"),
        "pnl_pct": shared_seed.get("pnl_pct", "unavailable"),
        "broker_fee": shared_seed.get("broker_fee"),
        "broker_tax": shared_seed.get("broker_tax"),
        "pnl_truth_source": _clip(shared_seed.get("pnl_truth_source"), max_len=80) or "unavailable",
        "broker_day_truth_source": _clip(shared_seed.get("broker_day_truth_source"), max_len=80) or "",
        "broker_day_match_mode": _clip(shared_seed.get("broker_day_match_mode"), max_len=40) or "",
        "broker_day_authoritative": bool(shared_seed.get("broker_day_authoritative")),
        "broker_day_row_count": shared_seed.get("broker_day_row_count"),
        "broker_truth_attempted": bool(shared_seed.get("broker_truth_attempted")),
        "broker_truth_error": _clip(shared_seed.get("broker_truth_error"), max_len=240) or "",
        "broker_day_truth_attempted": bool(shared_seed.get("broker_day_truth_attempted")),
        "broker_day_truth_error": _clip(shared_seed.get("broker_day_truth_error"), max_len=240) or "",
        "broker_fill_price": shared_seed.get("broker_fill_price"),
        "broker_buy_price": shared_seed.get("broker_buy_price"),
        "account_mark_price": shared_seed.get("account_mark_price"),
        "monitor_mark_price": shared_seed.get("monitor_mark_price"),
        "price_truth_source": _clip(shared_seed.get("price_truth_source"), max_len=40) or "unavailable",
        "monitor_price_source": _clip(shared_seed.get("monitor_price_source"), max_len=120) or "unavailable",
        "data_source": dict(resolved_data_source),
        "resolved_trade_facts": dict(resolved_trade_facts),
        "lifecycle_action": action,
        "lifecycle_status": status_text,
        "monitor_decision": dict(shared_seed.get("monitor_decision") or {}),
        "scanner_evidence_status": _clip(shared_seed.get("scanner_evidence_status"), max_len=24),
        "strategist_evidence_status": _clip(shared_seed.get("strategist_evidence_status"), max_len=24),
        "commander_route": dict(shared_seed.get("commander_route") or {}),
    }
    out["truth_surface"] = build_trade_report_truth_surface(out.get("shared_facts"))
    out["memory_surface"] = build_trade_report_memory_surface(story_input)
    out["memory_application_surface"] = build_trade_memory_application_surface(story_input)
    sanitized = _sanitize_report_language_fields(out)
    return dict(sanitized) if isinstance(sanitized, dict) else out


