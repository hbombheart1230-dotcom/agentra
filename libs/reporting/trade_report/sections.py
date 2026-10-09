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
    commander_route = build_seed_commander_route(story_input, canonical_commander, canonical_commander_decision, deps=deps)
    scanner_reasoning = build_seed_scanner_reasoning(scanner_reason, scanner_selection_trace, deps=deps)
    monitor_reasoning = build_seed_monitor_reasoning(monitor_reason, monitor_blocker_trace, monitor_stop_policy_trace, deps=deps)
    enrich_seed_scanner_reasoning(scanner_reasoning, trade_model_scanner, deps=deps)
    enrich_seed_monitor_reasoning(monitor_reasoning, trade_read_model_context, deps=deps)
    strategist_context, strategist_evidence = build_seed_strategist_context_and_evidence(
        story_input, trade_read_model_context, market_context, strategist_evidence_trace,
        canonical_strategist, canonical_strategist_decision_frame, deps=deps,
    )
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
