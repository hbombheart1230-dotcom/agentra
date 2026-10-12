"""Behavior-preserving R3 implementation bodies moved from the public facade.

Each function keeps its original body except that every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module, no getattr fallback,
no entry-time capture), so late/use-time lookup and monkeypatching match the original
module-level resolution. Owner never imports the facade.
"""
from __future__ import annotations


def _extract_strategist_report_context_r3_impl(story_input, *, facade):
    canonical = story_input.get("canonical_agent_artifacts") if isinstance(story_input.get("canonical_agent_artifacts"), dict) else {}
    carriers = [
        story_input.get("strategist_output"),
        story_input.get("strategist"),
        canonical.get("strategist"),
        story_input,
    ]
    fields = (
        "strategy_thesis",
        "strategy_delta_trace",
        "strategy_refresh_trace",
        "memory_usage_trace",
        "news_usage_trace",
        "scanner_handoff",
        "monitor_handoff",
        "conflict_analysis",
        "trade_permission_frame",
        "responsibility_boundary",
        "strategy_detail",
    )
    out: Dict[str, Any] = {}
    for carrier in carriers:
        source = carrier if isinstance(carrier, dict) else {}
        if not source:
            continue
        for field in fields:
            if field in out:
                continue
            value = source.get(field)
            if isinstance(value, dict) and value:
                out[field] = dict(value)
    if "strategy_detail" not in out:
        for carrier in carriers:
            detail = facade._extract_strategy_detail_from_source(carrier)
            if detail:
                out["strategy_detail"] = detail
                break
    return out


def _build_report_strategist_refresh_trace_r3_impl(story_input, *, facade):
    canonical = story_input.get("canonical_agent_artifacts") if isinstance(story_input.get("canonical_agent_artifacts"), dict) else {}
    strategist_artifact = canonical.get("strategist") if isinstance(canonical.get("strategist"), dict) else {}
    commander_artifact = canonical.get("commander") if isinstance(canonical.get("commander"), dict) else {}
    strategist_output = (
        story_input.get("strategist_output")
        if isinstance(story_input.get("strategist_output"), dict)
        else strategist_artifact
    )
    if not isinstance(strategist_output, dict):
        strategist_output = {}
    commander_decision = (
        commander_artifact.get("commander_decision")
        if isinstance(commander_artifact.get("commander_decision"), dict)
        else story_input.get("commander_decision")
        if isinstance(story_input.get("commander_decision"), dict)
        else {}
    )
    if isinstance(strategist_artifact.get("strategy_refresh_trace"), dict) and strategist_artifact.get("strategy_refresh_trace"):
        return facade._compact_strategy_refresh_trace(strategist_artifact.get("strategy_refresh_trace"))
    if isinstance(strategist_output.get("strategy_refresh_trace"), dict) and strategist_output.get("strategy_refresh_trace"):
        return facade._compact_strategy_refresh_trace(strategist_output.get("strategy_refresh_trace"))
    trace = facade.build_strategy_refresh_trace(
        strategist_output=dict(strategist_output),
        state={
            "commander_decision": dict(commander_decision or {}),
            "route_observability": dict(commander_artifact.get("route_observability") or {}),
        },
    )
    return facade._compact_strategy_refresh_trace(trace)


def _compact_strategy_refresh_trace_r3_impl(value, *, facade):
    trace = value if isinstance(value, dict) else {}
    stages: List[Dict[str, Any]] = []
    for row in list(trace.get("stages") or [])[:4]:
        if not isinstance(row, dict):
            continue
        quant_context = facade._as_dict(row.get("quant_context") or row.get("strategist_quant_context"))
        quant_market = facade._as_dict(quant_context.get("quant_market_context"))
        quant_scorecard = facade._as_dict(quant_market.get("scorecard"))
        quant_feedback = facade._as_dict(quant_scorecard.get("quant_memory_feedback"))
        compact_stage = {
            "stage": facade._clip(row.get("stage"), max_len=80),
            "label": facade._clip(row.get("label"), max_len=80),
            "summary": facade._clip(row.get("summary"), max_len=320),
            "requested": row.get("requested"),
            "evaluated": row.get("evaluated"),
            "effective": row.get("effective"),
            "reason": facade._clip(row.get("reason"), max_len=160),
            "selected_symbol": facade._clip(row.get("selected_symbol"), max_len=24),
            "policy_delta_count": row.get("policy_delta_count"),
            "policy_delta_fields": facade._listify(row.get("policy_delta_fields"), max_items=8, max_len=80),
        }
        if quant_context:
            compact_stage.update(
                {
                    "quant_context_call_kind": facade._clip(quant_context.get("call_kind"), max_len=80),
                    "quant_scorecard_available": quant_scorecard.get("available"),
                    "quant_feedback_tags": facade._listify(quant_feedback.get("feedback_tags"), max_items=8, max_len=80),
                    "selected_symbol_quant_snapshot_present": bool(quant_context.get("selected_symbol_quant_snapshot")),
                    "hold_quant_context_present": bool(quant_context.get("hold_quant_context")),
                    "carry_quant_context_present": bool(quant_context.get("carry_quant_context")),
                    "quant_behavior_effect": facade._clip(quant_context.get("behavior_effect"), max_len=80),
                }
            )
        stages.append(
            {key: val for key, val in compact_stage.items() if val not in ("", None, [], {})}
        )
    out = {
        "summary": facade._clip(trace.get("summary"), max_len=700),
        "bullets": facade._listify(trace.get("bullets"), max_items=8, max_len=220),
        "stages": stages,
        "refresh_requested": trace.get("refresh_requested"),
        "refresh_effective": trace.get("refresh_effective"),
        "policy_delta_count": trace.get("policy_delta_count"),
        "policy_delta_fields": facade._listify(trace.get("policy_delta_fields"), max_items=8, max_len=80),
        "source": facade._clip(trace.get("source"), max_len=120),
        "llm_interpretation": facade._compact_scalar_dict(trace.get("llm_interpretation"), max_items=4, max_len=240),
    }
    return {key: val for key, val in out.items() if val not in ("", None, [], {})}


def _compact_memory_application_trace_r3_impl(value, *, facade):
    trace = value if isinstance(value, dict) else {}
    return {
        "captured": trace.get("captured"),
        "enabled": trace.get("enabled"),
        "applied": trace.get("applied"),
        "entry_applied": trace.get("entry_applied"),
        "hold_applied": trace.get("hold_applied"),
        "exit_applied": trace.get("exit_applied"),
        "not_applied_reason": facade._clip(trace.get("not_applied_reason"), max_len=120),
        "bias_source": facade._clip(trace.get("bias_source"), max_len=80),
        "active_layers": facade._listify(trace.get("active_layers"), max_items=5, max_len=32),
        "source_delta_keys": facade._listify(trace.get("source_delta_keys"), max_items=8, max_len=48),
        "entry_delta_keys": facade._listify(trace.get("entry_delta_keys"), max_items=8, max_len=48),
        "hold_delta_keys": facade._listify(trace.get("hold_delta_keys"), max_items=8, max_len=48),
        "exit_delta_keys": facade._listify(trace.get("exit_delta_keys"), max_items=8, max_len=48),
        "selected_symbol": facade._clip(trace.get("selected_symbol"), max_len=24),
        "selected_bias_adjustment": trace.get("selected_bias_adjustment"),
        "effective_policy_source": facade._clip(trace.get("effective_policy_source"), max_len=80),
        "reason": facade._listify(trace.get("reason"), max_items=5, max_len=80),
    }


def _normalize_provenance_entry_r3_impl(entry, *, facade):
    row = entry if isinstance(entry, dict) else {}
    source = str(row.get("source") or "fallback").strip().lower()
    path = str(row.get("artifact_path") or "").strip()
    confidence = str(row.get("confidence") or "").strip().lower()
    if confidence not in {"high", "medium", "low"}:
        if source == "canonical":
            confidence = "high"
        elif source in {"direct_artifact", "direct"}:
            confidence = "medium"
        else:
            confidence = "low"
    if confidence == "high":
        completeness = 1.0
    elif confidence == "medium":
        completeness = 0.75
    else:
        completeness = 0.5 if source != "fallback" else 0.35
    return {
        "source": source or "fallback",
        "evidence_source": source or "fallback",
        "artifact_path": path,
        "confidence": confidence,
        "completeness": completeness,
    }


def _report_section_provenance_r3_impl(story_input, *, facade):
    source = story_input.get("section_provenance") if isinstance(story_input.get("section_provenance"), dict) else {}
    fallback = facade._normalize_provenance_entry({"source": "fallback", "artifact_path": "", "confidence": "low"})
    seeded = source.get("report_section_provenance_seeds") if isinstance(source.get("report_section_provenance_seeds"), dict) else {}

    def _pick(section_key: str, *legacy_keys: str) -> Dict[str, Any]:
        direct = source.get(section_key)
        if isinstance(direct, dict) and direct:
            return facade._normalize_provenance_entry(direct)
        seeded_entry = seeded.get(section_key)
        if isinstance(seeded_entry, dict) and seeded_entry:
            return facade._normalize_provenance_entry(seeded_entry)
        for legacy_key in legacy_keys:
            legacy = source.get(legacy_key)
            if isinstance(legacy, dict) and legacy:
                return facade._normalize_provenance_entry(legacy)
        return fallback

    return {
        "executive_summary": _pick("executive_summary", "operator_conclusion_human"),
        "market_context_at_entry": _pick("market_context_at_entry", "market_context_human"),
        "strategist_summary": _pick("strategist_summary", "market_context_at_entry", "market_context_human"),
        "strategist_refresh_trace": _pick("strategist_refresh_trace", "strategist_output", "commander"),
        "why_this_symbol_was_chosen": _pick("why_this_symbol_was_chosen", "scanner_reason_human"),
        "entry_decision": _pick("entry_decision", "why_this_symbol_was_chosen", "scanner_reason_human"),
        "holding_monitoring_story": _pick("holding_monitoring_story", "monitor_reason_human"),
        "exit_decision": _pick("exit_decision", "holding_monitoring_story", "monitor_reason_human"),
        "execution_quality": _pick("execution_quality", "execution_outcome_human"),
        "scanner_filters": _pick("scanner_filters", "filters_human"),
        "guard_approval_result": _pick("guard_approval_result", "guard_reason_human"),
        "reporter_evaluation": _pick("reporter_evaluation", "reporter_status_human"),
        "errors_weaknesses_improvement_points": _pick("errors_weaknesses_improvement_points", "reporter_evaluation", "reporter_status_human"),
        "full_timeline": _pick("full_timeline", "timeline"),
        "final_operator_conclusion": _pick("final_operator_conclusion", "operator_conclusion_human"),
    }
