from __future__ import annotations

import json
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



# Stable section exports: the implementation is single-owned by focused section_parts.
from .section_parts.market_context import (
    build_market_context_summary,
    build_market_context_bullets,
)

from .section_parts.strategist import (
    build_strategist_summary_section,
)

from .section_parts.scanner_selection import (
    build_market_scanner_linkage_bullet,
    build_scanner_choice_bullets,
    build_scanner_choice_summary,
    build_scanner_candidate_comparison_section,
)

from .section_parts.entry_decision import (
    build_entry_decision_summary,
    select_entry_decision_detail,
    resolve_entry_monitor_reason,
)

from .section_parts.entry_bullets import (
    build_entry_decision_bullets,
)

from .section_parts.lifecycle_bullets import (
    build_holding_story_bullets,
    build_exit_decision_bullets,
)

from .section_parts.reporter_evaluation import (
    build_reporter_evaluation_section,
    build_reporter_evaluation_from_feedback,
)

from .section_parts.execution_quality import (
    build_execution_quality_section,
)
