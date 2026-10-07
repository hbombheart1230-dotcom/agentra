from __future__ import annotations

from typing import Any, Dict, Mapping


def build_shared_summary_seed(
    story_input: Dict[str, Any],
    *,
    deps: Mapping[str, Any],
) -> Dict[str, Any]:
    """Assemble the shared deterministic report seed behind the compatibility façade."""

    _as_dict = deps["as_dict"]
    _load_trade_read_model_hint = deps["load_trade_read_model_hint"]
    _resolve_trade_facts_with_precedence = deps["resolve_trade_facts_with_precedence"]
    resolve_trade_price_truth = deps["resolve_trade_price_truth"]
    _clip = deps["clip"]
    _as_action = deps["as_action"]
    _as_status = deps["as_status"]
    _has_evidence_payload = deps["has_evidence_payload"]
    _first_nonempty_text = deps["first_nonempty_text"]
    _listify = deps["listify"]
    _compact_commander_entry_control = deps["compact_commander_entry_control"]
    _first_dict_from = deps["first_dict_from"]
    _compact_scalar_dict = deps["compact_scalar_dict"]
    _extract_entry_execution_visibility = deps["extract_entry_execution_visibility"]

    entry_summary = _as_dict(story_input.get("entry_summary"))
    exit_summary = _as_dict(story_input.get("exit_summary"))
    scanner_reason = _as_dict(story_input.get("scanner_reason_human"))
    market_context = _as_dict(story_input.get("market_context_human"))
    monitor_reason = _as_dict(story_input.get("monitor_reason_human"))
    strategist_evidence_trace = _as_dict(story_input.get("strategist_evidence_trace"))
    scanner_selection_trace = _as_dict(story_input.get("scanner_selection_trace"))
    monitor_stop_policy_trace = _as_dict(story_input.get("monitor_stop_policy_trace"))
    monitor_blocker_trace = _as_dict(story_input.get("monitor_blocker_trace"))
    canonical = _as_dict(story_input.get("canonical_agent_artifacts"))
    canonical_commander = _as_dict(canonical.get("commander"))
    canonical_commander_decision = _as_dict(canonical_commander.get("commander_decision"))
    canonical_strategist = _as_dict(canonical.get("strategist"))
    canonical_strategist_decision_frame = _as_dict(canonical_strategist.get("decision_frame"))
    trade_read_model = _load_trade_read_model_hint(story_input)
    trade_read_model_facts = trade_read_model.get("facts") if isinstance(trade_read_model.get("facts"), dict) else {}
    trade_read_model_provenance = trade_read_model.get("provenance") if isinstance(trade_read_model.get("provenance"), dict) else {}
    trade_read_model_field_sources = (
        trade_read_model_provenance.get("field_sources")
        if isinstance(trade_read_model_provenance.get("field_sources"), dict)
        else {}
    )
    trade_read_model_context = trade_read_model.get("context") if isinstance(trade_read_model.get("context"), dict) else {}
    trade_model_report_section_seeds = (
        trade_read_model_context.get("report_section_seeds")
        if isinstance(trade_read_model_context.get("report_section_seeds"), dict)
        else {}
    )
    resolved_facts = _resolve_trade_facts_with_precedence(story_input)
    price_truth = resolve_trade_price_truth(story_input)
    trade_model_hold_duration_sec = trade_read_model_facts.get("hold_duration_sec")
    if resolved_facts.get("holding_duration") in (None, "", "unavailable") and trade_model_hold_duration_sec not in (None, ""):
        try:
            hold_seconds = int(float(trade_model_hold_duration_sec))
            if hold_seconds > 0:
                resolved_facts["holding_duration"] = str(hold_seconds)
                (resolved_facts.get("data_source") if isinstance(resolved_facts.get("data_source"), dict) else {}).update({"holding_duration": "trade_read_model"})
        except Exception:
            pass
    if resolved_facts.get("exit_reason") in (
        None,
        "",
        "unavailable",
        "exit_trigger_not_captured",
    ) and str(trade_read_model_facts.get("exit_reason") or "").strip():
        resolved_facts["exit_reason"] = _clip(trade_read_model_facts.get("exit_reason"), max_len=280)
        (resolved_facts.get("data_source") if isinstance(resolved_facts.get("data_source"), dict) else {}).update({"exit_reason": "trade_read_model"})
    read_model_pnl_source = str(trade_read_model_field_sources.get("pnl") or "").strip()
    if (
        read_model_pnl_source != "default"
        and resolved_facts.get("pnl") in (None, "", "unavailable")
        and trade_read_model_facts.get("pnl") not in (None, "")
    ):
        resolved_facts["pnl"] = trade_read_model_facts.get("pnl")
        (resolved_facts.get("data_source") if isinstance(resolved_facts.get("data_source"), dict) else {}).update({"pnl": "trade_read_model"})
    read_model_pnl_pct_source = str(trade_read_model_field_sources.get("pnl_pct") or "").strip()
    if (
        read_model_pnl_pct_source != "default"
        and resolved_facts.get("pnl_pct") in (None, "", "unavailable")
        and trade_read_model_facts.get("pnl_pct") not in (None, "")
    ):
        resolved_facts["pnl_pct"] = trade_read_model_facts.get("pnl_pct")
        (resolved_facts.get("data_source") if isinstance(resolved_facts.get("data_source"), dict) else {}).update({"pnl_pct": "trade_read_model"})
    lifecycle_action = _as_action(resolved_facts.get("action")) or "WAIT"
    status_text = _as_status(resolved_facts.get("status")) or "unavailable"
    trade_model_scanner = trade_read_model_context.get("scanner") if isinstance(trade_read_model_context.get("scanner"), dict) else {}
    scanner_evidence_status = (
        "available"
        if (
            _has_evidence_payload(story_input.get("scanner_evidence"))
            or bool(_first_nonempty_text(scanner_reason.get("selected_symbol"), scanner_reason.get("summary"), max_len=200))
            or bool(_listify(scanner_reason.get("bullets"), max_items=1, max_len=120))
            or bool(_first_nonempty_text(trade_model_scanner.get("summary"), max_len=200))
            or bool(_listify(trade_model_scanner.get("top_candidates"), max_items=1, max_len=120))
        )
        else "unavailable"
    )
    strategist_evidence_status = (
        "available"
        if (
            _has_evidence_payload(story_input.get("strategist_evidence"))
            or bool(_first_nonempty_text(market_context.get("summary"), market_context.get("regime"), max_len=200))
            or bool(_listify(market_context.get("bullets"), max_items=1, max_len=120))
        )
        else "unavailable"
    )
    commander_route = {
        "selected_route": _first_nonempty_text(
            canonical_commander.get("selected_route"),
            canonical_commander.get("final_runtime_path"),
            max_len=120,
        ),
        "reason": _first_nonempty_text(
            canonical_commander.get("route_reason_text"),
            canonical_commander.get("final_reason"),
            max_len=260,
        ),
        "command_intent": _first_nonempty_text(
            canonical_commander_decision.get("command_intent"),
            canonical_commander.get("command_intent"),
            max_len=40,
        ),
        "strategist_invocation": _first_nonempty_text(
            canonical_commander_decision.get("strategist_invocation"),
            canonical_commander.get("strategist_invocation"),
            max_len=40,
        ),
        "llm_policy": _first_nonempty_text(
            canonical_commander_decision.get("llm_policy"),
            canonical_commander.get("llm_invocation_policy"),
            max_len=40,
        ),
        "strategist_cache_used": canonical_commander.get("strategist_cache_used"),
        "strategist_called": canonical_commander.get("strategist_called"),
        "cooldown_applied": canonical_commander.get("cooldown_applied"),
        "applied_policy": _as_dict(canonical_commander.get("applied_policy")),
        "policy_source": _first_nonempty_text(
            canonical_commander.get("policy_source"),
            canonical_commander_decision.get("policy_source"),
            max_len=80,
        ),
        "policy_validation_status": _first_nonempty_text(
            canonical_commander.get("policy_validation_status"),
            canonical_commander_decision.get("policy_validation_status"),
            max_len=80,
        ),
        "policy_fallback_used": canonical_commander.get("policy_fallback_used")
        if canonical_commander.get("policy_fallback_used") is not None
        else canonical_commander_decision.get("policy_fallback_used"),
        "policy_fallback_reason": _first_nonempty_text(
            canonical_commander.get("policy_fallback_reason"),
            canonical_commander_decision.get("policy_fallback_reason"),
            max_len=220,
        ),
        "policy_partial_normalized": canonical_commander.get("policy_partial_normalized")
        if canonical_commander.get("policy_partial_normalized") is not None
        else canonical_commander_decision.get("policy_partial_normalized"),
        "policy_default_filled_fields": _listify(
            canonical_commander.get("policy_default_filled_fields")
            or canonical_commander_decision.get("policy_default_filled_fields"),
            max_items=12,
            max_len=80,
        ),
        "policy_validation_missing_fields": _listify(
            canonical_commander.get("policy_validation_missing_fields")
            or canonical_commander_decision.get("policy_validation_missing_fields"),
            max_items=12,
            max_len=80,
        ),
        "policy_validation_invalid_fields": _listify(
            canonical_commander.get("policy_validation_invalid_fields")
            or canonical_commander_decision.get("policy_validation_invalid_fields"),
            max_items=12,
            max_len=80,
        ),
        "override_reason": _first_nonempty_text(
            canonical_commander.get("override_reason"),
            canonical_commander_decision.get("override_reason"),
            max_len=160,
        ),
        "applied_policy_source_chain": _listify(
            canonical_commander.get("applied_policy_source_chain")
            or canonical_commander_decision.get("applied_policy_source_chain"),
            max_items=6,
            max_len=80,
        ),
        "entry_control": _compact_commander_entry_control(
            _first_dict_from(
                canonical_commander_decision.get("entry_control"),
                canonical_commander.get("entry_control"),
                canonical_commander.get("commander_entry_control"),
                _as_dict(canonical_commander.get("scanner_policy")).get("entry_control"),
                _as_dict(canonical_commander.get("monitor_policy")).get("entry_control"),
                _as_dict(story_input.get("commander_decision")).get("entry_control"),
                story_input.get("commander_entry_control"),
            )
        ),
    }
    scanner_reasoning = {
        "playbook": _first_nonempty_text(scanner_reason.get("playbook"), max_len=80),
        "policy_source": _first_nonempty_text(scanner_reason.get("policy_source"), max_len=80),
        "applied_policy_present": bool(scanner_reason.get("applied_policy_present")),
        "monitor_entry_policy_summary": _compact_scalar_dict(
            scanner_reason.get("monitor_entry_policy_summary"),
            max_items=8,
            max_len=120,
        ),
        "scanner_bias_applied": bool(scanner_reason.get("scanner_bias_applied")),
        "scanner_bias_summary": _compact_scalar_dict(
            scanner_reason.get("scanner_bias_summary"),
            max_items=8,
            max_len=120,
        ),
        "candidate_bias_adjustments": [
            {
                "symbol": _clip((row or {}).get("symbol"), max_len=24),
                "bias_adjustment": (row or {}).get("bias_adjustment"),
                "bias_adjustments": _listify(
                    [
                        str((item or {}).get("reason") or "")
                        for item in list((row or {}).get("bias_adjustments") or [])
                        if isinstance(item, dict)
                    ],
                    max_items=4,
                    max_len=120,
                ),
            }
            for row in list(scanner_reason.get("candidate_bias_adjustments") or [])[:5]
            if isinstance(row, dict)
        ],
        "selection_reason_with_bias": _first_nonempty_text(
            scanner_reason.get("selection_reason_with_bias"),
            scanner_reason.get("selection_basis"),
            scanner_reason.get("summary"),
            max_len=320,
        ),
        "selection_trace": {
            "ranked_candidates": [
                {
                    "rank": (row or {}).get("rank"),
                    "symbol": _clip((row or {}).get("symbol"), max_len=24),
                    "score_total": (row or {}).get("score_total"),
                    "risk_score": (row or {}).get("risk_score"),
                    "confidence": (row or {}).get("confidence"),
                }
                for row in list(scanner_selection_trace.get("ranked_candidates") or [])[:5]
                if isinstance(row, dict)
            ],
            "selected_symbol": _first_nonempty_text(
                scanner_selection_trace.get("selected_symbol"),
                scanner_reason.get("selected_symbol"),
                max_len=24,
            ),
            "selected_rank": scanner_selection_trace.get("selected_rank") or scanner_reason.get("selected_rank"),
            "selection_reason": _first_nonempty_text(
                scanner_selection_trace.get("selection_reason"),
                scanner_reason.get("selection_reason"),
                scanner_reason.get("selection_basis"),
                max_len=280,
            ),
            "selected_symbol_score_drivers": _compact_scalar_dict(
                scanner_selection_trace.get("selected_symbol_score_drivers")
                or scanner_reason.get("selected_symbol_score_drivers"),
                max_items=6,
                max_len=120,
            ),
        },
    }
    monitor_policy_ref = _as_dict(monitor_reason.get("policy_ref"))
    monitor_reasoning = {
        "entry_check_summary": _first_nonempty_text(monitor_reason.get("entry_check_summary"), max_len=240),
        "entry_blockers": _listify(monitor_reason.get("entry_blockers"), max_items=6, max_len=120),
        "threshold_shortfalls": _listify(
            monitor_blocker_trace.get("threshold_shortfalls") or monitor_reason.get("threshold_shortfalls"),
            max_items=4,
            max_len=160,
        ),
        "policy_ref": _compact_scalar_dict(monitor_policy_ref, max_items=8, max_len=120),
        "thresholds_guards_used": _compact_scalar_dict(monitor_reason.get("thresholds_guards_used"), max_items=8, max_len=120),
        "received_policy": _compact_scalar_dict(monitor_reason.get("received_policy"), max_items=12, max_len=120),
        "received_policy_source": _first_nonempty_text(monitor_reason.get("received_policy_source"), max_len=80),
        "effective_policy": _compact_scalar_dict(
            monitor_reason.get("effective_policy")
            if isinstance(monitor_reason.get("effective_policy"), dict)
            else (
                monitor_reason.get("applied_policy")
                if isinstance(monitor_reason.get("applied_policy"), dict)
                else monitor_policy_ref.get("effective_policy")
            ),
            max_items=12,
            max_len=120,
        ),
        "effective_policy_source": _first_nonempty_text(
            monitor_reason.get("effective_policy_source"),
            monitor_policy_ref.get("effective_policy_source"),
            max_len=80,
        ),
        "effective_policy_source_chain": _listify(
            monitor_reason.get("effective_policy_source_chain")
            or monitor_policy_ref.get("effective_policy_source_chain"),
            max_items=6,
            max_len=80,
        ),
        "policy_adjustments": _compact_scalar_dict(
            monitor_reason.get("policy_adjustments")
            if isinstance(monitor_reason.get("policy_adjustments"), dict)
            else monitor_policy_ref.get("policy_adjustments"),
            max_items=8,
            max_len=120,
        ),
        "policy_adjustment_summary": _first_nonempty_text(
            monitor_reason.get("policy_adjustment_summary"),
            monitor_policy_ref.get("policy_adjustment_summary"),
            max_len=220,
        ),
        "policy_adjustment_reasoning": _first_nonempty_text(
            monitor_reason.get("policy_adjustment_reasoning"),
            monitor_policy_ref.get("policy_adjustment_reasoning"),
            max_len=260,
        ),
        "effective_policy_deltas": [
            {
                "field": _clip((row or {}).get("field"), max_len=80),
                "from": (row or {}).get("from"),
                "to": (row or {}).get("to"),
            }
            for row in list(
                monitor_reason.get("effective_policy_deltas")
                or monitor_policy_ref.get("effective_policy_deltas")
                or []
            )[:8]
            if isinstance(row, dict)
        ],
        "applied_policy": _compact_scalar_dict(
            monitor_reason.get("applied_policy")
            if isinstance(monitor_reason.get("applied_policy"), dict)
            else monitor_policy_ref.get("applied_policy"),
            max_items=12,
            max_len=120,
        ),
        "policy_source": _first_nonempty_text(
            monitor_reason.get("policy_source"),
            monitor_policy_ref.get("policy_source"),
            max_len=80,
        ),
        "policy_validation_status": _first_nonempty_text(
            monitor_reason.get("policy_validation_status"),
            monitor_policy_ref.get("policy_validation_status"),
            max_len=80,
        ),
        "policy_fallback_used": monitor_reason.get("policy_fallback_used")
        if monitor_reason.get("policy_fallback_used") is not None
        else monitor_policy_ref.get("policy_fallback_used"),
        "policy_fallback_reason": _first_nonempty_text(
            monitor_reason.get("policy_fallback_reason"),
            monitor_policy_ref.get("policy_fallback_reason"),
            max_len=220,
        ),
        "policy_partial_normalized": monitor_reason.get("policy_partial_normalized")
        if monitor_reason.get("policy_partial_normalized") is not None
        else monitor_policy_ref.get("policy_partial_normalized"),
        "policy_default_filled_fields": _listify(
            monitor_reason.get("policy_default_filled_fields")
            or monitor_policy_ref.get("policy_default_filled_fields"),
            max_items=12,
            max_len=80,
        ),
        "policy_validation_missing_fields": _listify(
            monitor_reason.get("policy_validation_missing_fields")
            or monitor_policy_ref.get("policy_validation_missing_fields"),
            max_items=12,
            max_len=80,
        ),
        "policy_validation_invalid_fields": _listify(
            monitor_reason.get("policy_validation_invalid_fields")
            or monitor_policy_ref.get("policy_validation_invalid_fields"),
            max_items=12,
            max_len=80,
        ),
        "override_reason": _first_nonempty_text(
            monitor_reason.get("override_reason"),
            monitor_policy_ref.get("override_reason"),
            max_len=160,
        ),
        "applied_policy_source_chain": _listify(
            monitor_reason.get("applied_policy_source_chain")
            or monitor_policy_ref.get("applied_policy_source_chain"),
            max_items=6,
            max_len=80,
        ),
        "hard_stop_pct": monitor_reason.get("hard_stop_pct") or monitor_stop_policy_trace.get("hard_stop_pct"),
        "adaptive_stop_loss_pct": monitor_reason.get("adaptive_stop_loss_pct")
        or monitor_stop_policy_trace.get("adaptive_stop_loss_pct"),
        "effective_stop_loss_pct": monitor_reason.get("effective_stop_loss_pct")
        or monitor_stop_policy_trace.get("effective_stop_loss_pct"),
        "trailing_stop_pct": monitor_reason.get("trailing_stop_pct") or monitor_stop_policy_trace.get("trailing_stop_pct"),
        "take_profit_pct": monitor_reason.get("take_profit_pct") or monitor_stop_policy_trace.get("take_profit_pct"),
        "monitor_stop_policy_trace": {
            "hard_stop_pct": monitor_stop_policy_trace.get("hard_stop_pct") or monitor_reason.get("hard_stop_pct"),
            "adaptive_stop_loss_pct": monitor_stop_policy_trace.get("adaptive_stop_loss_pct")
            or monitor_reason.get("adaptive_stop_loss_pct"),
            "effective_stop_loss_pct": monitor_stop_policy_trace.get("effective_stop_loss_pct")
            or monitor_reason.get("effective_stop_loss_pct"),
            "trailing_stop_pct": monitor_stop_policy_trace.get("trailing_stop_pct") or monitor_reason.get("trailing_stop_pct"),
            "take_profit_pct": monitor_stop_policy_trace.get("take_profit_pct") or monitor_reason.get("take_profit_pct"),
            "strategist_baseline_stop_loss_pct": monitor_stop_policy_trace.get("strategist_baseline_stop_loss_pct")
            or monitor_reason.get("strategist_baseline_stop_loss_pct"),
            "strategist_baseline_take_profit_pct": monitor_stop_policy_trace.get("strategist_baseline_take_profit_pct")
            or monitor_reason.get("strategist_baseline_take_profit_pct"),
            "strategist_baseline_trailing_stop_pct": monitor_stop_policy_trace.get("strategist_baseline_trailing_stop_pct")
            or monitor_reason.get("strategist_baseline_trailing_stop_pct"),
        },
        "monitor_blocker_trace": {
            "entry_check_summary": _first_nonempty_text(
                monitor_blocker_trace.get("entry_check_summary"),
                monitor_reason.get("entry_check_summary"),
                max_len=240,
            ),
            "entry_blockers": _listify(
                monitor_blocker_trace.get("entry_blockers") or monitor_reason.get("entry_blockers"),
                max_items=6,
                max_len=120,
            ),
            "threshold_shortfalls": _listify(
                monitor_blocker_trace.get("threshold_shortfalls") or monitor_reason.get("threshold_shortfalls"),
                max_items=4,
                max_len=160,
            ),
        },
    }
    if not scanner_reasoning.get("selection_reason_with_bias") and str(trade_model_scanner.get("summary") or "").strip():
        scanner_reasoning["selection_reason_with_bias"] = _clip(trade_model_scanner.get("summary"), max_len=320)
    selection_trace = scanner_reasoning.get("selection_trace") if isinstance(scanner_reasoning.get("selection_trace"), dict) else {}
    if not selection_trace.get("ranked_candidates") and isinstance(trade_model_scanner.get("top_candidates"), list):
        selection_trace["ranked_candidates"] = [
            {
                "symbol": _clip((row or {}).get("symbol"), max_len=24),
                "score_total": (row or {}).get("score_total"),
                "rank": (row or {}).get("rank"),
            }
            for row in list(trade_model_scanner.get("top_candidates") or [])[:5]
            if isinstance(row, dict)
        ]
    if not selection_trace.get("selected_symbol"):
        first_ranked = ((selection_trace.get("ranked_candidates") or [None])[0] or {}) if isinstance(selection_trace.get("ranked_candidates"), list) else {}
        if isinstance(first_ranked, dict) and str(first_ranked.get("symbol") or "").strip():
            selection_trace["selected_symbol"] = _clip(first_ranked.get("symbol"), max_len=24)
    if not selection_trace.get("selected_rank"):
        first_ranked = ((selection_trace.get("ranked_candidates") or [None])[0] or {}) if isinstance(selection_trace.get("ranked_candidates"), list) else {}
        if isinstance(first_ranked, dict) and first_ranked.get("rank") not in (None, ""):
            selection_trace["selected_rank"] = first_ranked.get("rank")
    if not selection_trace.get("selected_symbol_score_drivers") and isinstance(trade_model_scanner.get("score_drivers"), dict):
        selection_trace["selected_symbol_score_drivers"] = _compact_scalar_dict(
            trade_model_scanner.get("score_drivers"), max_items=6, max_len=120
        )
    scanner_reasoning["selection_trace"] = selection_trace

    trade_model_monitor = trade_read_model_context.get("monitor") if isinstance(trade_read_model_context.get("monitor"), dict) else {}
    if not monitor_reasoning.get("entry_check_summary") and str(trade_model_monitor.get("entry_reason") or "").strip():
        monitor_reasoning["entry_check_summary"] = _clip(trade_model_monitor.get("entry_reason"), max_len=240)
    if not monitor_reasoning.get("threshold_shortfalls") and isinstance(trade_model_monitor.get("blocker_trace"), dict):
        monitor_reasoning["threshold_shortfalls"] = _listify(
            (trade_model_monitor.get("blocker_trace") or {}).get("threshold_shortfalls"), max_items=4, max_len=160
        )
    existing_monitor_stop_trace = (
        monitor_reasoning.get("monitor_stop_policy_trace")
        if isinstance(monitor_reasoning.get("monitor_stop_policy_trace"), dict)
        else {}
    )
    if not any(value not in (None, "", [], {}) for value in existing_monitor_stop_trace.values()) and isinstance(trade_model_monitor.get("stop_policy_trace"), dict):
        monitor_reasoning["monitor_stop_policy_trace"] = _compact_scalar_dict(
            trade_model_monitor.get("stop_policy_trace"), max_items=8, max_len=120
        )
    trade_model_strategist = trade_read_model_context.get("strategist") if isinstance(trade_read_model_context.get("strategist"), dict) else {}
    canonical_trace_summary = (
        _as_dict(story_input.get("strategist_trace_summary"))
        or _as_dict(story_input.get("trace_summary"))
        or _as_dict(canonical_strategist.get("trace_summary"))
        or _as_dict(canonical_strategist.get("strategist_trace_summary"))
    )
    theme_strength_packet = (
        _as_dict(market_context.get("theme_strength_packet"))
        or _as_dict(trade_model_strategist.get("theme_strength_packet"))
        or _as_dict(canonical_strategist.get("theme_strength_packet"))
        or _as_dict(canonical_strategist_decision_frame.get("theme_strength_packet"))
    )
    theme_strength_scores = (
        _as_dict(market_context.get("theme_strength_scores"))
        or _as_dict(trade_model_strategist.get("theme_strength_scores"))
        or _as_dict(canonical_strategist.get("theme_strength"))
        or _as_dict(theme_strength_packet.get("theme_scores"))
    )
    strategist_context = {
        "playbook": _first_nonempty_text(
            market_context.get("playbook"),
            market_context.get("selected_playbook"),
            trade_model_strategist.get("playbook"),
            max_len=80,
        ),
        "selected_playbook": _first_nonempty_text(
            market_context.get("selected_playbook"),
            market_context.get("playbook"),
            trade_model_strategist.get("playbook"),
            max_len=80,
        ),
        "policy_source": _first_nonempty_text(
            market_context.get("policy_source"),
            trade_model_strategist.get("policy_source"),
            max_len=80,
        ),
        "risk_tone": _first_nonempty_text(
            market_context.get("risk_tone"),
            trade_model_strategist.get("risk_tone"),
            canonical_trace_summary.get("risk_tone"),
            canonical_strategist.get("risk_tone"),
            canonical_strategist_decision_frame.get("risk_tone"),
            max_len=40,
        ),
        "trade_aggressiveness": _first_nonempty_text(
            market_context.get("trade_aggressiveness"),
            trade_model_strategist.get("trade_aggressiveness"),
            canonical_trace_summary.get("trade_aggressiveness"),
            canonical_strategist.get("trade_aggressiveness"),
            canonical_strategist_decision_frame.get("trade_aggressiveness"),
            max_len=40,
        ),
        "monitor_guidance": _first_nonempty_text(
            market_context.get("monitor_guidance"),
            trade_model_strategist.get("monitor_guidance"),
            canonical_trace_summary.get("monitor_guidance"),
            canonical_strategist.get("monitor_guidance"),
            canonical_strategist_decision_frame.get("monitor_guidance"),
            max_len=80,
        ),
        "themes": _listify(
            market_context.get("themes")
            or market_context.get("preferred_themes")
            or trade_model_strategist.get("themes"),
            max_items=6,
            max_len=48,
        ),
        "preferred_themes": _listify(
            market_context.get("preferred_themes")
            or market_context.get("themes")
            or trade_model_strategist.get("themes"),
            max_items=6,
            max_len=48,
        ),
        "market_context_summary": _first_nonempty_text(
            market_context.get("summary"),
            trade_model_strategist.get("market_context_summary"),
            max_len=320,
        ),
        "theme_strength_packet": theme_strength_packet,
        "theme_source": _first_nonempty_text(
            market_context.get("theme_source"),
            trade_model_strategist.get("theme_source"),
            canonical_strategist.get("theme_source"),
            canonical_strategist_decision_frame.get("theme_source"),
            theme_strength_packet.get("source"),
            max_len=80,
        ),
        "theme_source_status": _first_nonempty_text(
            market_context.get("theme_source_status"),
            trade_model_strategist.get("theme_source_status"),
            canonical_strategist.get("theme_source_status"),
            canonical_strategist_decision_frame.get("theme_source_status"),
            theme_strength_packet.get("status"),
            max_len=80,
        ),
        "theme_source_reason": _first_nonempty_text(
            market_context.get("theme_source_reason"),
            trade_model_strategist.get("theme_source_reason"),
            canonical_strategist.get("theme_source_reason"),
            canonical_strategist_decision_frame.get("theme_source_reason"),
            theme_strength_packet.get("reason"),
            max_len=160,
        ),
        "theme_strength_top_themes": _listify(
            market_context.get("theme_strength_top_themes") or theme_strength_packet.get("top_themes"),
            max_items=6,
            max_len=80,
        ),
        "theme_strength_scores": theme_strength_scores,
    }

    strategist_evidence = {
        "candidate_hints": _listify(
            strategist_evidence_trace.get("candidate_hints")
            or market_context.get("candidate_hints")
            or story_input.get("strategist_candidate_hints"),
            max_items=8,
            max_len=24,
        ),
        "news_query_targets": _listify(
            strategist_evidence_trace.get("news_query_targets")
            or market_context.get("news_query_targets"),
            max_items=8,
            max_len=80,
        ),
        "market_headlines": _listify(
            strategist_evidence_trace.get("market_headlines")
            or market_context.get("market_headlines")
            or story_input.get("strategist_market_headlines"),
            max_items=3,
            max_len=180,
        ),
        "symbol_headlines": _listify(
            strategist_evidence_trace.get("symbol_headlines")
            or market_context.get("symbol_headlines")
            or story_input.get("strategist_symbol_headlines"),
            max_items=3,
            max_len=180,
        ),
        "global_sentiment_signal": _compact_scalar_dict(
            strategist_evidence_trace.get("global_sentiment_signal") or market_context.get("global_sentiment_signal"),
            max_items=8,
            max_len=120,
        ),
        "fear_index": _compact_scalar_dict(
            strategist_evidence_trace.get("fear_index") or market_context.get("fear_index"),
            max_items=8,
            max_len=120,
        ),
        "key_events": _listify(
            strategist_evidence_trace.get("key_events")
            or market_context.get("key_events")
            or market_context.get("key_events_hint"),
            max_items=6,
            max_len=180,
        ),
    }
    entry_execution_visibility = _extract_entry_execution_visibility(story_input)
    return {
        "symbol": _clip(story_input.get("symbol"), max_len=32) or "unknown",
        "trade_id": _clip(story_input.get("trade_id") or story_input.get("story_id"), max_len=120),
        "lifecycle_action": lifecycle_action,
        "lifecycle_status": status_text,
        "entry_exists": bool(_has_evidence_payload(entry_summary)),
        "exit_exists": bool(_has_evidence_payload(exit_summary)),
        "holding_duration": _clip(resolved_facts.get("holding_duration"), max_len=80) or "unavailable",
        "exit_reason": _clip(resolved_facts.get("exit_reason"), max_len=280) or "unavailable",
        "pnl": resolved_facts.get("pnl"),
        "pnl_pct": resolved_facts.get("pnl_pct"),
        "broker_fee": resolved_facts.get("broker_fee"),
        "broker_tax": resolved_facts.get("broker_tax"),
        "pnl_truth_source": _clip(resolved_facts.get("pnl_truth_source"), max_len=80) or "unavailable",
        "broker_day_truth_source": _clip(resolved_facts.get("broker_day_truth_source"), max_len=80) or "",
        "broker_day_match_mode": _clip(resolved_facts.get("broker_day_match_mode"), max_len=40) or "",
        "broker_day_authoritative": bool(resolved_facts.get("broker_day_authoritative")),
        "broker_day_row_count": resolved_facts.get("broker_day_row_count"),
        "broker_truth_attempted": bool(resolved_facts.get("broker_truth_attempted")),
        "broker_truth_error": _clip(resolved_facts.get("broker_truth_error"), max_len=240) or "",
        "broker_day_truth_attempted": bool(resolved_facts.get("broker_day_truth_attempted")),
        "broker_day_truth_error": _clip(resolved_facts.get("broker_day_truth_error"), max_len=240) or "",
        "broker_fill_price": price_truth.get("broker_fill_price"),
        "broker_buy_price": price_truth.get("broker_buy_price"),
        "account_mark_price": price_truth.get("account_mark_price"),
        "monitor_mark_price": price_truth.get("monitor_mark_price"),
        "price_truth_source": _clip(price_truth.get("price_truth_source"), max_len=40) or "unavailable",
        "monitor_price_source": _clip(price_truth.get("monitor_price_source"), max_len=120) or "unavailable",
        "monitor_decision": dict(resolved_facts.get("monitor_decision") or {}),
        "resolved_trade_facts": {
            "action": lifecycle_action,
            "status": status_text,
            "holding_duration": _clip(resolved_facts.get("holding_duration"), max_len=80) or "unavailable",
            "exit_reason": _clip(resolved_facts.get("exit_reason"), max_len=280) or "unavailable",
            "pnl": resolved_facts.get("pnl", "unavailable"),
            "pnl_pct": resolved_facts.get("pnl_pct", "unavailable"),
            "broker_fee": resolved_facts.get("broker_fee"),
            "broker_tax": resolved_facts.get("broker_tax"),
            "pnl_truth_source": _clip(resolved_facts.get("pnl_truth_source"), max_len=80) or "unavailable",
            "broker_day_truth_source": _clip(resolved_facts.get("broker_day_truth_source"), max_len=80) or "",
            "broker_day_match_mode": _clip(resolved_facts.get("broker_day_match_mode"), max_len=40) or "",
            "broker_day_authoritative": bool(resolved_facts.get("broker_day_authoritative")),
            "broker_day_row_count": resolved_facts.get("broker_day_row_count"),
            "broker_truth_attempted": bool(resolved_facts.get("broker_truth_attempted")),
            "broker_truth_error": _clip(resolved_facts.get("broker_truth_error"), max_len=240) or "",
            "broker_day_truth_attempted": bool(resolved_facts.get("broker_day_truth_attempted")),
            "broker_day_truth_error": _clip(resolved_facts.get("broker_day_truth_error"), max_len=240) or "",
            "broker_fill_price": price_truth.get("broker_fill_price"),
            "broker_buy_price": price_truth.get("broker_buy_price"),
            "account_mark_price": price_truth.get("account_mark_price"),
            "monitor_mark_price": price_truth.get("monitor_mark_price"),
            "price_truth_source": _clip(price_truth.get("price_truth_source"), max_len=40) or "unavailable",
            "monitor_price_source": _clip(price_truth.get("monitor_price_source"), max_len=120) or "unavailable",
            "data_source": dict(resolved_facts.get("data_source") or {}),
        },
        "scanner_evidence_status": scanner_evidence_status,
        "strategist_evidence_status": strategist_evidence_status,
        "commander_route": commander_route,
        "strategist_evidence": strategist_evidence,
        "strategist_context": strategist_context,
        "entry_execution_visibility": entry_execution_visibility,
        "report_section_seeds": {
            "market_context_at_entry": _as_dict(trade_model_report_section_seeds.get("market_context_at_entry")),
            "strategist_summary": _as_dict(trade_model_report_section_seeds.get("strategist_summary")),
            "why_this_symbol_was_chosen": _as_dict(trade_model_report_section_seeds.get("why_this_symbol_was_chosen")),
            "entry_decision": _as_dict(trade_model_report_section_seeds.get("entry_decision")),
            "holding_monitoring_story": _as_dict(trade_model_report_section_seeds.get("holding_monitoring_story")),
            "exit_decision": _as_dict(trade_model_report_section_seeds.get("exit_decision")),
            "scanner_filters": _as_dict(trade_model_report_section_seeds.get("scanner_filters")),
            "execution_quality": _as_dict(trade_model_report_section_seeds.get("execution_quality")),
            "guard_approval_result": _as_dict(trade_model_report_section_seeds.get("guard_approval_result")),
            "reporter_evaluation": _as_dict(trade_model_report_section_seeds.get("reporter_evaluation")),
            "final_operator_conclusion": _as_dict(trade_model_report_section_seeds.get("final_operator_conclusion")),
        },
        "scanner_reasoning": scanner_reasoning,
        "monitor_reasoning": monitor_reasoning,
    }

# Responsibility-specific market/scanner section builders extracted from trade_report_ai.py.


def build_market_context_summary(section: Any, *, scanner_reason: Dict[str, Any] | None = None, deps: Mapping[str, Any]) -> str:
    _clip = deps["clip"]
    _extract_korea_indices_snapshot = deps["extract_korea_indices_snapshot"]
    _extract_us_indices_snapshot = deps["extract_us_indices_snapshot"]
    _format_korea_indices_sentence = deps["format_korea_indices_sentence"]
    _format_pct_points = deps["format_pct_points"]
    _market_token_label = deps["market_token_label"]
    _num_opt = deps["num_opt"]
    _theme_text = deps["theme_text"]
    market = section if isinstance(section, dict) else {}
    scanner = scanner_reason if isinstance(scanner_reason, dict) else {}
    regime = _market_token_label(market.get("regime")) or ""
    market_sentiment = _market_token_label(market.get("market_sentiment")) or ""
    selected_playbook = _market_token_label(market.get("selected_playbook")) or _clip(market.get("selected_playbook"), max_len=40)
    playbook = _market_token_label(market.get("playbook")) or selected_playbook or "not_captured"
    themes = _theme_text(market.get("themes") or market.get("preferred_themes"), max_items=3)
    sentiment = _num_opt(market.get("global_sentiment_score"))
    fear_index = market.get("fear_index") if isinstance(market.get("fear_index"), dict) else {}
    vix_level = _num_opt(market.get("vix_level"))
    if vix_level is None:
        vix_level = _num_opt(fear_index.get("level"))
    headline_count = int(float(market.get("headline_count") or 0)) if _num_opt(market.get("headline_count")) is not None else 0
    query_count = int(float(market.get("news_query_count") or 0)) if _num_opt(market.get("news_query_count")) is not None else 0
    us_indices = _extract_us_indices_snapshot(market.get("key_events") or market.get("key_events_hint"))
    korea_indices_text = _format_korea_indices_sentence(_extract_korea_indices_snapshot(market))
    selected_symbol = _clip(scanner.get("selected_symbol"), max_len=24)

    regime_missing = regime in {"", "not_captured", "unknown", "직접 캡처되지 않음"}
    sentiment_missing = market_sentiment in {"", "not_captured", "unknown", "직접 캡처되지 않음"}
    playbook_known = playbook not in {"", "not_captured", "unknown", "직접 캡처되지 않음"}
    themes_known = themes not in {"", "not_captured", "unknown", "직접 캡처되지 않음"}

    if regime_missing and sentiment_missing and (playbook_known or themes_known):
        frame_bits: List[str] = []
        if playbook_known:
            frame_bits.append(f"플레이북 {playbook}")
        if themes_known:
            frame_bits.append(f"핵심 테마 {themes}")
        frame_text = ", ".join(frame_bits) if frame_bits else "핵심 프레임 미확인"
        sentences: List[str] = [
            f"시장 상태/심리 직접 캡처는 제한적이지만, {frame_text} 기준으로 정리했습니다."
        ]
    else:
        regime_text = regime or "not_captured"
        sentences = [
            f"시장 상태 {regime_text} 기준에서 플레이북 {playbook}로 운용했습니다."
        ]

    metric_bits: List[str] = []
    if sentiment is not None:
        metric_bits.append(f"글로벌 감성 {sentiment:.3f}")
    if vix_level is not None:
        metric_bits.append(f"VIX {vix_level:.2f}")
    if metric_bits:
        sentences.append(", ".join(metric_bits) + " 입력은 시장 안정성 점검에 반영되었습니다.")
    if us_indices:
        sentences.append(
            f"미국 지수는 S&P500 {_format_pct_points(us_indices.get('sp500'))}, "
            f"Nasdaq {_format_pct_points(us_indices.get('nasdaq'))}, Dow {_format_pct_points(us_indices.get('dow'))}였습니다."
        )
    if korea_indices_text:
        sentences.append(f"국내 지수는 {korea_indices_text} 기준으로 반영했습니다.")
    if headline_count or query_count:
        sentences.append(
            f"뉴스 입력 {headline_count}건과 조회 대상 {query_count}개를 함께 반영했습니다."
        )
    if themes_known:
        theme_sentence = f"핵심 테마는 {themes}로 정리됐습니다."
        if selected_symbol:
            theme_sentence = f"핵심 테마 {themes} 기준에서 {selected_symbol}이 스캐너 연결 종목으로 확인됐습니다."
        sentences.append(theme_sentence)
    return " ".join(sentences[:5]).strip()



def build_market_context_bullets(section: Any, *, scanner_reason: Dict[str, Any] | None = None, deps: Mapping[str, Any]) -> List[str]:
    _clip = deps["clip"]
    _dedupe_list = deps["dedupe_list"]
    _extract_korea_indices_snapshot = deps["extract_korea_indices_snapshot"]
    _extract_us_indices_snapshot = deps["extract_us_indices_snapshot"]
    _format_korea_indices_sentence = deps["format_korea_indices_sentence"]
    _format_pct_points = deps["format_pct_points"]
    _join_headlines = deps["join_headlines"]
    _listify = deps["listify"]
    _market_token_label = deps["market_token_label"]
    _num_opt = deps["num_opt"]
    _select_symbol_headline = deps["select_symbol_headline"]
    _theme_text = deps["theme_text"]
    data = section if isinstance(section, dict) else {}
    scanner = scanner_reason if isinstance(scanner_reason, dict) else {}
    regime = _market_token_label(data.get("regime")) or ""
    market_sentiment = _market_token_label(data.get("market_sentiment")) or ""
    selected_playbook = _market_token_label(data.get("selected_playbook")) or _clip(data.get("selected_playbook"), max_len=40)
    playbook = _market_token_label(data.get("playbook")) or selected_playbook or "not_captured"
    themes = _theme_text(data.get("themes") or data.get("preferred_themes"), max_items=4)
    sentiment = _num_opt(data.get("global_sentiment_score"))
    fear_index = data.get("fear_index") if isinstance(data.get("fear_index"), dict) else {}
    vix_level = _num_opt(data.get("vix_level"))
    if vix_level is None:
        vix_level = _num_opt(fear_index.get("level"))
    vix_change = _num_opt(fear_index.get("change_pct"))
    headline_count = int(float(data.get("headline_count") or 0)) if _num_opt(data.get("headline_count")) is not None else 0
    query_count = int(float(data.get("news_query_count") or 0)) if _num_opt(data.get("news_query_count")) is not None else 0
    us_indices = _extract_us_indices_snapshot(data.get("key_events") or data.get("key_events_hint"))
    korea_indices_text = _format_korea_indices_sentence(_extract_korea_indices_snapshot(data))
    market_titles = _join_headlines(data.get("market_news_titles") or data.get("market_headlines"), max_items=2, max_len=180)
    symbol_title = _select_symbol_headline(
        data.get("symbol_news_titles")
        or data.get("symbol_headlines")
        or data.get("strategist_symbol_headlines")
        or data.get("candidate_news_titles"),
        _clip(scanner.get("selected_symbol"), max_len=24),
    )
    targets = ", ".join(_listify(data.get("news_query_targets"), max_items=7, max_len=40))
    theme_source = _clip(data.get("theme_source"), max_len=80)
    theme_status = _clip(data.get("theme_source_status"), max_len=80)
    theme_reason = _clip(data.get("theme_source_reason"), max_len=160)
    theme_top = ", ".join(_listify(data.get("theme_strength_top_themes"), max_items=6, max_len=80))

    bullets: List[str] = []
    regime_missing = regime in {"", "not_captured", "unknown", "직접 캡처되지 않음"}
    sentiment_missing = market_sentiment in {"", "not_captured", "unknown", "직접 캡처되지 않음"}
    themes_known = themes not in {"", "not_captured", "unknown", "직접 캡처되지 않음"}
    if regime_missing and sentiment_missing and (playbook != "not_captured" or themes_known):
        bullets.append(
            f"시장 상태/심리 직접 캡처는 제한적이며, 플레이북 {playbook}, 핵심 테마 {themes if themes_known else 'not_captured'} 기준으로 해석했습니다."
        )
    else:
        bullets.append(
            f"시장 상태는 {regime or 'not_captured'}, 시장 심리는 {market_sentiment or 'not_captured'}, 플레이북은 {playbook}, 핵심 테마는 {themes} 기준입니다."
        )
    if sentiment is not None or vix_level is not None:
        metric = []
        if sentiment is not None:
            metric.append(f"글로벌 감성 {sentiment:.3f}")
        if vix_level is not None:
            change_text = f", 변화율 {_format_pct_points(vix_change)}" if vix_change is not None else ""
            metric.append(f"VIX {vix_level:.2f}{change_text}")
        bullets.append("변동성/심리 입력은 " + ", ".join(metric) + "입니다.")
    if us_indices:
        bullets.append(
            f"미국 지수는 S&P500 {_format_pct_points(us_indices.get('sp500'))}, "
            f"Nasdaq {_format_pct_points(us_indices.get('nasdaq'))}, Dow {_format_pct_points(us_indices.get('dow'))}였습니다."
        )
    if korea_indices_text:
        bullets.append(f"국내 지수는 {korea_indices_text}입니다.")
    if headline_count or query_count or targets:
        bullets.append(
            f"뉴스 입력은 {headline_count}건 헤드라인, 조회 대상은 {query_count}개"
            + (f" ({targets})" if targets else "")
            + "를 반영했습니다."
        )
    if market_titles:
        bullets.append(f"주요 시장 뉴스는 {market_titles}입니다.")
    if symbol_title:
        bullets.append(f"대표 종목/섹터 뉴스는 {symbol_title}입니다.")
    if theme_source or theme_status or theme_reason:
        bullets.append(
            "키움 테마 packet은 "
            f"source={theme_source or 'not_captured'}, "
            f"status={theme_status or 'not_captured'}, "
            f"reason={theme_reason or 'not_captured'}, "
            f"top_themes={theme_top or 'none'} 상태였습니다."
        )
    return _dedupe_list(bullets, max_items=10, max_len=260)



def build_strategist_summary_section(market_context: Dict[str, Any], scanner_reason: Dict[str, Any], *, deps: Mapping[str, Any]) -> Dict[str, Any]:
    _clip = deps["clip"]
    _core_value_opt = deps["core_value_opt"]
    _dedupe_list = deps["dedupe_list"]
    _extract_korea_indices_snapshot = deps["extract_korea_indices_snapshot"]
    _extract_us_indices_snapshot = deps["extract_us_indices_snapshot"]
    _format_korea_indices_sentence = deps["format_korea_indices_sentence"]
    _format_pct_points = deps["format_pct_points"]
    _join_headlines = deps["join_headlines"]
    _listify = deps["listify"]
    _market_token_label = deps["market_token_label"]
    _num_opt = deps["num_opt"]
    _risk_mode_label = deps["risk_mode_label"]
    _scanner_bias_text = deps["scanner_bias_text"]
    _scanner_source_text = deps["scanner_source_text"]
    _select_symbol_headline = deps["select_symbol_headline"]
    _strategy_constraint_text = deps["strategy_constraint_text"]
    _theme_linkage_label = deps["theme_linkage_label"]
    _theme_text = deps["theme_text"]
    regime = _market_token_label(market_context.get("regime")) or ""
    market_sentiment = _market_token_label(market_context.get("market_sentiment")) or ""
    selected_playbook = _market_token_label(market_context.get("selected_playbook")) or _clip(market_context.get("selected_playbook"), max_len=40)
    playbook = _market_token_label(market_context.get("playbook")) or selected_playbook or "not_captured"
    themes = _theme_text(market_context.get("themes") or market_context.get("preferred_themes"), max_items=3)
    risk_mode = _risk_mode_label(market_context.get("risk_mode"))
    preferred_themes = _strategy_constraint_text(market_context.get("preferred_themes"), max_items=4)
    avoid_themes = _strategy_constraint_text(market_context.get("avoid_themes"), max_items=4)
    scanner_bias = _scanner_bias_text(market_context.get("scanner_bias_summary"))
    sentiment = _num_opt(market_context.get("global_sentiment_score"))
    fear_index = market_context.get("fear_index") if isinstance(market_context.get("fear_index"), dict) else {}
    vix_level = _num_opt(market_context.get("vix_level"))
    if vix_level is None:
        vix_level = _num_opt(fear_index.get("level"))
    headline_count = int(float(market_context.get("headline_count") or 0)) if _num_opt(market_context.get("headline_count")) is not None else 0
    query_count = int(float(market_context.get("news_query_count") or 0)) if _num_opt(market_context.get("news_query_count")) is not None else 0
    query_targets = ", ".join(_listify(market_context.get("news_query_targets"), max_items=7, max_len=32))
    stress_flags = _listify(market_context.get("stress_flags"), max_items=4, max_len=48)
    candidate_hints = _listify(market_context.get("candidate_hints"), max_items=4, max_len=48)
    selected_symbol = _clip(scanner_reason.get("selected_symbol"), max_len=24)
    selected_rank = scanner_reason.get("selected_rank")
    selected_score = _num_opt(scanner_reason.get("selected_score"))
    selected_sources = _scanner_source_text(scanner_reason.get("selected_sources"))
    scanner_bias_applied = bool(scanner_reason.get("scanner_bias_applied"))
    contribution = scanner_reason.get("news_scanner_contribution") if isinstance(scanner_reason.get("news_scanner_contribution"), dict) else {}
    core = contribution.get("core_score_contributions") if isinstance(contribution.get("core_score_contributions"), dict) else {}
    sentiment_inputs = contribution.get("sentiment_inputs") if isinstance(contribution.get("sentiment_inputs"), dict) else {}

    def _core_value_opt(key: str) -> Optional[float]:
        row = core.get(key)
        if isinstance(row, dict):
            return _num_opt(row.get("value"))
        return _num_opt(row)

    sentiment_contrib = _core_value_opt("sentiment")
    if sentiment_contrib is None:
        sentiment_contrib = _num_opt(sentiment_inputs.get("weighted_sentiment_score_contribution"))
    theme_boost = _core_value_opt("theme_boost")
    market_titles = _join_headlines(market_context.get("market_news_titles") or market_context.get("market_headlines"), max_items=1, max_len=110)
    symbol_title = _select_symbol_headline(
        market_context.get("symbol_news_titles")
        or market_context.get("symbol_headlines")
        or market_context.get("strategist_symbol_headlines")
        or market_context.get("candidate_news_titles"),
        selected_symbol,
    )
    theme_linkage = _theme_linkage_label(market_context.get("themes") or market_context.get("preferred_themes"))
    theme_source = _clip(market_context.get("theme_source"), max_len=80)
    theme_status = _clip(market_context.get("theme_source_status"), max_len=80)
    theme_reason = _clip(market_context.get("theme_source_reason"), max_len=160)
    theme_top = ", ".join(_listify(market_context.get("theme_strength_top_themes"), max_items=6, max_len=80))

    regime_missing = regime in {"", "not_captured", "unknown", "직접 캡처되지 않음"}
    sentiment_missing = market_sentiment in {"", "not_captured", "unknown", "직접 캡처되지 않음"}
    themes_known = themes not in {"", "not_captured", "unknown", "직접 캡처되지 않음"}

    if regime_missing and sentiment_missing:
        frame_bits: List[str] = []
        if playbook not in {"", "not_captured", "unknown", "직접 캡처되지 않음"}:
            frame_bits.append(f"플레이북 {playbook}")
        if themes_known:
            frame_bits.append(f"핵심 테마 {themes}")
        frame_text = ", ".join(frame_bits) if frame_bits else "핵심 프레임 미확인"
        summary_parts = [f"전략가는 시장 상태 직접 캡처가 제한적이어서 {frame_text} 중심으로 정리했습니다."]
    else:
        summary_parts = [f"전략가는 시장을 {regime or 'not_captured'}, 시장 심리를 {market_sentiment or 'not_captured'}으로 해석했고 {playbook} 플레이북과 {themes} 프레임을 유지했습니다."]
    if not stress_flags:
        summary_parts.append("뚜렷한 스트레스 신호는 확인되지 않았습니다.")
    if selected_symbol:
        scanner_sentence = f"스캐너 연결 종목은 {selected_symbol}입니다."
        if selected_rank not in (None, "") and selected_score is not None:
            scanner_sentence = f"스캐너 연결 종목은 {selected_symbol}이며 순위 {selected_rank}, 점수 {selected_score:.3f}입니다."
        summary_parts.append(scanner_sentence)
    summary = " ".join(summary_parts)

    bullets: List[str] = []
    input_bits: List[str] = []
    if sentiment is not None:
        input_bits.append(f"글로벌 감성 {sentiment:.3f}")
    if vix_level is not None:
        input_bits.append(f"VIX {vix_level:.2f}")
    if headline_count or query_count:
        input_bits.append(f"뉴스 {headline_count}건/{query_count}대상")
    us_indices = _extract_us_indices_snapshot(market_context.get("key_events") or market_context.get("key_events_hint"))
    if us_indices:
        input_bits.append(
            f"미국 지수 S&P500 {_format_pct_points(us_indices.get('sp500'))}, Nasdaq {_format_pct_points(us_indices.get('nasdaq'))}, Dow {_format_pct_points(us_indices.get('dow'))}"
        )
    if input_bits:
        bullets.append("핵심 입력은 " + ", ".join(input_bits) + "입니다.")
    korea_indices_text = _format_korea_indices_sentence(_extract_korea_indices_snapshot(market_context))
    if korea_indices_text:
        bullets.append("전략가는 국내 지수 " + korea_indices_text + "를 시장 상태 입력으로 사용했습니다.")

    if regime_missing and sentiment_missing:
        interpretation_bits = [f"플레이북 {playbook}"]
        if themes_known:
            interpretation_bits.append(f"핵심 테마 {themes}")
        interpretation_bits.append("스트레스 신호 없음" if not stress_flags else "스트레스 신호 " + ", ".join(stress_flags))
        bullets.append("전략 해석은 " + ", ".join(interpretation_bits) + " 기준이었습니다.")
    else:
        interpretation_bits = [f"시장 상태 {regime}", f"시장 심리 {market_sentiment}", f"플레이북 {playbook}", f"핵심 테마 {themes}"]
        if stress_flags:
            interpretation_bits.append("스트레스 신호 " + ", ".join(stress_flags))
        else:
            interpretation_bits.append("스트레스 신호 없음")
        bullets.append("전략 해석은 " + ", ".join(interpretation_bits) + " 기준이었습니다.")

    if query_targets:
        bullets.append(f"전략가가 관찰한 대상은 다음과 같았습니다: {query_targets}.")
    if risk_mode or selected_playbook:
        if risk_mode and selected_playbook:
            bullets.append(f"전략가 운용 기준은 리스크 모드 {risk_mode}이었고, 선택 플레이북은 {selected_playbook}이었습니다.")
        elif risk_mode:
            bullets.append(f"전략가 운용 기준은 리스크 모드 {risk_mode}였습니다.")
        else:
            bullets.append(f"전략가 운용 기준에서 선택 플레이북은 {selected_playbook}이었습니다.")
    if preferred_themes or avoid_themes:
        theme_pref_bits: List[str] = []
        if preferred_themes:
            theme_pref_bits.append(f"선호 테마 {preferred_themes}")
        if avoid_themes:
            theme_pref_bits.append(f"회피 테마 {avoid_themes}")
        bullets.append("전략가 선호/회피 기준은 " + ", ".join(theme_pref_bits) + "이었습니다.")
    if theme_source or theme_status or theme_reason:
        bullets.append(
            "전략가 테마 강도 입력은 "
            f"source={theme_source or 'not_captured'}, "
            f"status={theme_status or 'not_captured'}, "
            f"reason={theme_reason or 'not_captured'}, "
            f"top_themes={theme_top or 'none'} 기준이었습니다."
        )
    if scanner_bias:
        bullets.append(f"스캐너 바이어스는 {scanner_bias} 기준이었습니다.")
    if candidate_hints:
        bullets.append("전략가 후보 힌트는 " + ", ".join(candidate_hints) + "였습니다.")
    if market_titles or symbol_title:
        if market_titles and symbol_title and selected_symbol:
            linkage_line = f"뉴스 연결 해석은 시장 뉴스로 {theme_linkage} 맥락을 확인했고, 종목 뉴스로 {selected_symbol} 선정 근거를 보강했습니다."
        elif market_titles:
            linkage_line = f"뉴스 연결 해석은 시장 뉴스로 {theme_linkage} 맥락을 확인했습니다."
        elif symbol_title and selected_symbol:
            linkage_line = f"뉴스 연결 해석은 종목 뉴스로 {selected_symbol} 선정 근거를 보강했습니다."
        else:
            linkage_line = "뉴스 연결 해석은 headline evidence로 확인됐습니다."
        if selected_sources:
            linkage_line += f". 선정 소스는 {selected_sources}였습니다."
        evidence_parts: List[str] = []
        if market_titles:
            evidence_parts.append(f"시장: {market_titles}")
        if symbol_title:
            evidence_parts.append(f"종목: {symbol_title}")
        if evidence_parts:
            linkage_line += " 참조 headline: " + " / ".join(evidence_parts)
        bullets.append(linkage_line)
        if selected_sources:
            bullets.append(f"이 해석은 {selected_sources} 축으로 연결했습니다.")
    contribution_bits: List[str] = []
    if sentiment_contrib is not None:
        contribution_bits.append(f"감성 기여 {sentiment_contrib:+.3f}")
    if theme_boost is not None:
        contribution_bits.append(f"테마 가점 {theme_boost:+.3f}")
    if selected_sources:
        contribution_bits.append(f"선정 소스 {selected_sources}")
    if scanner_bias_applied:
        contribution_bits.append("바이어스 적용")
    if contribution_bits:
        bullets.append("스캐너 반영은 " + ", ".join(contribution_bits) + " 기준으로 정리됐습니다.")
    if selected_symbol:
        symbol_bits = [selected_symbol]
        if selected_rank not in (None, ""):
            symbol_bits.append(f"{selected_rank}위")
        if selected_score is not None:
            symbol_bits.append(f"점수 {selected_score:.3f}")
        bullets.append("종목 연결은 " + ", ".join(symbol_bits) + "로 확인됩니다.")
    return {
        "summary": summary,
        "bullets": _dedupe_list(bullets, max_items=12, max_len=260),
    }



def build_market_scanner_linkage_bullet(section: Any, scanner_reason: Dict[str, Any] | None = None, *, deps: Mapping[str, Any]) -> str:
    _clip = deps["clip"]
    _core_value_opt = deps["core_value_opt"]
    _listify = deps["listify"]
    _num_opt = deps["num_opt"]
    market = section if isinstance(section, dict) else {}
    scanner = scanner_reason if isinstance(scanner_reason, dict) else {}
    symbol = _clip(scanner.get("selected_symbol"), max_len=24)
    if not symbol:
        return ""
    playbook = _clip(market.get("playbook"), max_len=40) or "not_captured"
    source_text = ", ".join(_listify(scanner.get("selected_sources"), max_items=4, max_len=80))
    contribution = scanner.get("news_scanner_contribution") if isinstance(scanner.get("news_scanner_contribution"), dict) else {}
    core = contribution.get("core_score_contributions") if isinstance(contribution.get("core_score_contributions"), dict) else {}
    sentiment_inputs = contribution.get("sentiment_inputs") if isinstance(contribution.get("sentiment_inputs"), dict) else {}

    def _core_value_opt(key: str) -> Optional[float]:
        row = core.get(key)
        if isinstance(row, dict):
            return _num_opt(row.get("value"))
        return _num_opt(row)

    score_value = _num_opt(scanner.get("selected_score"))
    sentiment_contrib = _core_value_opt("sentiment")
    if sentiment_contrib is None:
        sentiment_contrib = _num_opt(sentiment_inputs.get("weighted_sentiment_score_contribution"))
    theme_boost = _core_value_opt("theme_boost")
    global_sentiment_value = _num_opt(sentiment_inputs.get("global_sentiment_score"))
    if global_sentiment_value is None:
        global_sentiment_value = _num_opt(market.get("global_sentiment_score"))
    vix_value = _num_opt(market.get("vix_level"))

    metric_bits: List[str] = []
    if score_value is not None:
        metric_bits.append(f"종합 점수 {score_value:.3f}")
    if sentiment_contrib is not None:
        metric_bits.append(f"감성 기여 {sentiment_contrib:+.3f}")
    if theme_boost is not None:
        metric_bits.append(f"테마 가점 {theme_boost:+.3f}")
    if global_sentiment_value is not None:
        metric_bits.append(f"글로벌 감성 {global_sentiment_value:.3f}")
    if vix_value is not None:
        metric_bits.append(f"VIX {vix_value:.2f}")

    parts: List[str] = [f"종목 {symbol}을 {playbook} 플레이북 기준으로 선정했고"]
    if metric_bits:
        parts.append(", ".join(metric_bits))
    if source_text:
        parts.append(f"선정 소스 {source_text}")
    return "Scanner linkage: " + ", ".join(parts)



def build_scanner_choice_bullets(scanner_reason: Dict[str, Any], market_context: Dict[str, Any], *, deps: Mapping[str, Any]) -> List[str]:
    _build_runner_up_comparison = deps["build_runner_up_comparison"]
    _build_scanner_driver_summary = deps["build_scanner_driver_summary"]
    _clip = deps["clip"]
    _dedupe_list = deps["dedupe_list"]
    _fmt_num = deps["fmt_num"]
    _listify = deps["listify"]
    _market_token_label = deps["market_token_label"]
    _num_opt = deps["num_opt"]
    _scanner_basis_text = deps["scanner_basis_text"]
    _scanner_chart_feature_coverage = deps["scanner_chart_feature_coverage"]
    _scanner_chart_feature_label = deps["scanner_chart_feature_label"]
    _scanner_monitor_fallback_context = deps["scanner_monitor_fallback_context"]
    _scanner_ranked_candidates = deps["scanner_ranked_candidates"]
    _scanner_selected_row = deps["scanner_selected_row"]
    _scanner_source_text = deps["scanner_source_text"]
    symbol = _clip(scanner_reason.get("selected_symbol"), max_len=24) or "선정 종목"
    rank = scanner_reason.get("selected_rank")
    universe = scanner_reason.get("universe_size")
    score_value = _num_opt(scanner_reason.get("selected_score"))
    confidence_value = _num_opt(scanner_reason.get("confidence"))
    ranked_rows = _scanner_ranked_candidates(scanner_reason)
    selected_row = _scanner_selected_row(scanner_reason)
    selected_risk = _num_opt(selected_row.get("risk_score"))
    fallback_ctx = _scanner_monitor_fallback_context(scanner_reason)
    basis = _scanner_basis_text(scanner_reason)
    source_text = _scanner_source_text(scanner_reason.get("selected_sources"))
    playbook = _market_token_label(market_context.get("playbook")) or _clip(market_context.get("playbook"), max_len=32)
    driver_summary = _build_scanner_driver_summary(scanner_reason)
    coverage = _scanner_chart_feature_coverage(scanner_reason)

    bullets: List[str] = []
    if fallback_ctx["used"] and fallback_ctx["scanner_top_pick_symbol"]:
        rank_text = f"{rank}위" if rank not in (None, "") else "후보"
        fallback_line = (
            f"스캐너 상위 후보 {fallback_ctx['scanner_top_pick_symbol']}은 모니터 단계에서 보류됐고 "
            f"{symbol}은 차순위 재평가 {rank_text}로 실제 진입 종목이 됐습니다."
        )
        if fallback_ctx["reason"]:
            fallback_line = (
                f"스캐너 상위 후보 {fallback_ctx['scanner_top_pick_symbol']}은 {fallback_ctx['reason']} 이유로 보류됐고 "
                f"{symbol}은 차순위 재평가 {rank_text}로 실제 진입 종목이 됐습니다."
            )
        bullets.append(fallback_line)
        if fallback_ctx["trigger_reason"]:
            bullets.append(f"실제 진입은 {fallback_ctx['trigger_reason']} 조건에서 확정됐습니다.")
    if universe not in (None, "") and rank not in (None, ""):
        bullets.append(f"총 {int(universe)}개 후보를 비교했고 {symbol}이 {rank}위로 선정됐습니다.")
    elif rank not in (None, ""):
        bullets.append(f"{symbol}의 최종 선정 순위는 {rank}위였습니다.")
    if score_value is not None:
        metric_bits = [f"종합 점수 {score_value:.3f}"]
        if confidence_value is not None:
            metric_bits.append(f"신뢰도 {confidence_value:.2f}")
        if selected_risk is not None:
            metric_bits.append(f"리스크 {selected_risk:.3f}")
        bullets.append(", ".join(metric_bits) + "로 집계됐습니다.")
    if basis:
        bullets.append(f"주요 선정 기준은 {basis} 축이었습니다.")
    if source_text:
        bullets.append(f"선정에는 {source_text}이 반영됐습니다.")
    if driver_summary:
        bullets.append(f"주요 점수 기여는 {driver_summary}였습니다.")
    if playbook:
        bullets.append(f"전략가 플레이북 {playbook}과 정렬된 후보였습니다.")
    if ranked_rows:
        ranked_text = " / ".join(
            f"#{int(float(row.get('rank') or idx + 1))} {_clip(row.get('symbol'), max_len=24)}({_fmt_num(row.get('score_total'))})"
            for idx, row in enumerate(ranked_rows[:3])
            if _clip(row.get("symbol"), max_len=24)
        )
        if ranked_text:
            bullets.append(f"상위 후보는 {ranked_text} 순이었습니다.")
    if coverage:
        present = int(float(coverage.get("present") or 0)) if _num_opt(coverage.get("present")) is not None else 0
        total = int(float(coverage.get("total") or 0)) if _num_opt(coverage.get("total")) is not None else 0
        missing = [
            _scanner_chart_feature_label(item)
            for item in _listify(coverage.get("missing_keys"), max_items=4, max_len=80)
            if _scanner_chart_feature_label(item)
        ]
        coverage_text = f"차트 피처 커버리지는 {present}/{total}였습니다." if present and total else ""
        if coverage_text and missing:
            coverage_text += f" 누락된 항목은 {', '.join(missing)}이었습니다."
        elif missing:
            coverage_text = f"누락된 차트 피처는 {', '.join(missing)}였습니다."
        if coverage_text:
            bullets.append(coverage_text)
    for row in list(scanner_reason.get("runner_ups") or [])[:2]:
        if isinstance(row, dict):
            rendered = _build_runner_up_comparison(
                row,
                selected_symbol=symbol,
                selected_score=score_value,
                selected_risk=selected_risk,
            )
            if rendered:
                bullets.append(rendered)
    return _dedupe_list(bullets, max_items=10, max_len=260)



def build_scanner_choice_summary(scanner_reason: Dict[str, Any], market_context: Dict[str, Any], *, deps: Mapping[str, Any]) -> str:
    _build_runner_up_comparison = deps["build_runner_up_comparison"]
    _build_scanner_driver_summary = deps["build_scanner_driver_summary"]
    _clip = deps["clip"]
    _market_token_label = deps["market_token_label"]
    _num_opt = deps["num_opt"]
    _scanner_basis_text = deps["scanner_basis_text"]
    _scanner_monitor_fallback_context = deps["scanner_monitor_fallback_context"]
    _scanner_ranked_candidates = deps["scanner_ranked_candidates"]
    _scanner_selected_row = deps["scanner_selected_row"]
    _scanner_source_text = deps["scanner_source_text"]
    symbol = _clip(scanner_reason.get("selected_symbol"), max_len=24) or "선정 종목"
    rank = scanner_reason.get("selected_rank")
    universe = scanner_reason.get("universe_size")
    score_value = _num_opt(scanner_reason.get("selected_score"))
    basis = _scanner_basis_text(scanner_reason)
    sources = _scanner_source_text(scanner_reason.get("selected_sources"))
    playbook = _market_token_label(market_context.get("playbook")) or _clip(market_context.get("playbook"), max_len=32)
    confidence_value = _num_opt(scanner_reason.get("confidence"))
    ranked_rows = _scanner_ranked_candidates(scanner_reason)
    selected_row = _scanner_selected_row(scanner_reason)
    selected_risk = _num_opt(selected_row.get("risk_score"))
    fallback_ctx = _scanner_monitor_fallback_context(scanner_reason)
    driver_summary = _build_scanner_driver_summary(scanner_reason)
    comparison_bits: List[str] = []
    for row in list(scanner_reason.get("runner_ups") or [])[:2]:
        if not isinstance(row, dict):
            continue
        rendered = _build_runner_up_comparison(
            row,
            selected_symbol=symbol,
            selected_score=score_value,
            selected_risk=selected_risk,
        )
        if rendered:
            comparison_bits.append(rendered.rstrip("."))

    if fallback_ctx["used"] and fallback_ctx["scanner_top_pick_symbol"]:
        rank_text = f"{rank}위" if rank not in (None, "") else "후보"
        summary = (
            f"스캐너 상위 후보 {fallback_ctx['scanner_top_pick_symbol']}이 모니터 단계에서 보류된 뒤 "
            f"{symbol}이 차순위 재평가 {rank_text}로 실제 진입 종목에 선택됐습니다"
        )
        if fallback_ctx["reason"]:
            summary = (
                f"스캐너 상위 후보 {fallback_ctx['scanner_top_pick_symbol']}이 {fallback_ctx['reason']} 이유로 보류된 뒤 "
                f"{symbol}이 차순위 재평가 {rank_text}로 실제 진입 종목에 선택됐습니다"
            )
    elif universe not in (None, "") and rank == 1:
        summary = f"{symbol}은 총 {int(universe)}개 후보 중 1위로 선정됐습니다"
    elif rank == 1:
        summary = f"{symbol}은 스캐너 후보 중 최종 1순위였습니다"
    else:
        summary = f"{symbol}이 스캐너 후보로 선정됐습니다"
    if universe not in (None, "") and rank not in (None, ""):
        if not (rank == 1 and summary.endswith("선정됐습니다")):
            summary += f". 총 {int(universe)}개 후보 중 {rank}위였습니다"
    elif rank not in (None, ""):
        summary += f". 선정 순위는 {rank}위였습니다"
    elif universe not in (None, ""):
        summary += f". 비교한 후보는 총 {int(universe)}개였습니다"
    if score_value is not None:
        if fallback_ctx["used"]:
            summary += f". 실제 진입 후보의 종합 점수는 {score_value:.3f}였습니다"
        elif rank == 1:
            summary += f". 종합 점수는 {score_value:.3f}로 가장 높았습니다"
        else:
            summary += f". 종합 점수는 {score_value:.3f}였습니다"
    if basis:
        summary += f". 강했던 축은 {basis} 축이었습니다"
    details: List[str] = []
    if sources:
        details.append(f"선정에는 {sources}이 반영됐습니다")
    if driver_summary:
        details.append(f"핵심 점수 기여는 {driver_summary}였습니다")
    if confidence_value is not None:
        details.append(f"신뢰도는 {confidence_value:.2f} 수준이었습니다")
    if selected_risk is not None:
        details.append(f"리스크는 {selected_risk:.3f} 수준이었습니다")
    if playbook:
        details.append(f"전략가 플레이북 {playbook}과도 정렬됐습니다")
    if details:
        summary += ". " + ". ".join(details) + "."
    if comparison_bits:
        summary += " " + ". ".join(comparison_bits) + "."
    return summary



def build_scanner_candidate_comparison_section(scanner_reason: Dict[str, Any], market_context: Dict[str, Any], *, deps: Mapping[str, Any]) -> Dict[str, Any]:
    _build_scanner_choice_bullets = deps["build_scanner_choice_bullets"]
    _build_scanner_choice_summary = deps["build_scanner_choice_summary"]
    _clip = deps["clip"]
    _dedupe_list = deps["dedupe_list"]
    _num_opt = deps["num_opt"]
    _scanner_ranked_candidates = deps["scanner_ranked_candidates"]
    ranked_rows = _scanner_ranked_candidates(scanner_reason)
    runner_ups = [row for row in list(scanner_reason.get("runner_ups") or []) if isinstance(row, dict)]
    runner_ups_lost = [row for row in list(scanner_reason.get("runner_ups_lost") or []) if isinstance(row, dict)]
    symbol = _clip(scanner_reason.get("selected_symbol"), max_len=24) or "?? ?? ???"
    universe = scanner_reason.get("universe_size")
    if not ranked_rows and universe in (None, "", 0):
        if runner_ups or runner_ups_lost:
            bullets: List[str] = []
            for row in runner_ups[:2]:
                comp_symbol = _clip(row.get("symbol"), max_len=24)
                comp_rank = _clip(row.get("rank"), max_len=8) or "?"
                comp_score = _num_opt(row.get("score_total"))
                comp_why = _clip(row.get("why"), max_len=160)
                if not comp_symbol:
                    continue
                detail = f"{comp_symbol}? rank {comp_rank}"
                if comp_score is not None:
                    detail += f", score {comp_score:.3f}"
                if comp_why:
                    detail += f", ?? ??? {comp_why}"
                bullets.append(detail + "???.")
            for row in runner_ups_lost[:2]:
                lost_symbol = _clip(row.get("symbol"), max_len=24)
                lost_reason = _clip(row.get("summary") or row.get("reason"), max_len=160)
                if lost_symbol and lost_reason:
                    bullets.append(f"{lost_symbol} ?? ??? {lost_reason}???.")
                elif lost_symbol:
                    bullets.append(f"{lost_symbol}? runner-up ????? ?? ????? ?????.")
            return {
                "summary": f"{symbol} ???? runner-up ?? ??? ??? ????.",
                "bullets": _dedupe_list(bullets, max_items=12, max_len=260),
            }
        return {
            "summary": "??? ?? ??? ?? ?? ?? ?? ??? ??????.",
            "bullets": [
                f"?? ??? {symbol}?? ????? ranked candidate / runner-up trace? ?? ?? ??? ??????.",
            ],
        }

    summary = _build_scanner_choice_summary(scanner_reason, market_context)
    bullets = _build_scanner_choice_bullets(scanner_reason, market_context)
    if universe not in (None, "") and ranked_rows:
        try:
            universe_count = int(float(universe))
        except Exception:
            universe_count = 0
        bullets = [f"??? ???? ?? ?? {universe_count}?????."] + list(bullets)
    return {
        "summary": summary,
        "bullets": _dedupe_list(bullets, max_items=12, max_len=260),
    }

