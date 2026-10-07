from __future__ import annotations

from typing import Any, Dict, Mapping


def extract_entry_execution_visibility(story_input: Dict[str, Any], *, deps: Mapping[str, Any]) -> Dict[str, Any]:
    _as_dict = deps["as_dict"]
    _clip = deps["clip"]
    _compact_candidate_watch_proposal = deps["compact_candidate_watch_proposal"]
    _compact_commander_entry_control = deps["compact_commander_entry_control"]
    _compact_entry_candidate_cascade = deps["compact_entry_candidate_cascade"]
    _enrich_candidate_watch_proposal_from_entry_control = deps["enrich_candidate_watch_proposal_from_entry_control"]
    _entry_execution_visibility_summary = deps["entry_execution_visibility_summary"]
    _extract_strategy_detail_from_source = deps["extract_strategy_detail_from_source"]
    _first_dict_from = deps["first_dict_from"]
    canonical = _as_dict(story_input.get("canonical_agent_artifacts"))
    canonical_commander = _as_dict(canonical.get("commander"))
    canonical_commander_decision = _as_dict(canonical_commander.get("commander_decision"))
    canonical_monitor = _as_dict(canonical.get("monitor"))
    canonical_monitor_handoff = _as_dict(canonical_monitor.get("scanner_monitor_handoff"))
    canonical_strategist = _as_dict(canonical.get("strategist"))
    shared_facts = _as_dict(story_input.get("shared_facts"))
    shared_commander_route = _as_dict(shared_facts.get("commander_route"))
    monitor_reason = _as_dict(story_input.get("monitor_reason_human"))
    monitor_output = _as_dict(story_input.get("monitor_output"))
    story_handoff = _as_dict(story_input.get("scanner_monitor_handoff"))
    entry_summary = _as_dict(story_input.get("entry_summary"))
    entry_monitor = _as_dict(entry_summary.get("monitor_context"))
    entry_policy_ref = _as_dict(entry_monitor.get("policy_ref"))
    entry_applied_policy = _as_dict(entry_policy_ref.get("applied_policy"))
    strategy_detail = _extract_strategy_detail_from_source(
        _first_dict_from(
            story_input.get("strategist_output"),
            story_input.get("strategist"),
            canonical_strategist,
            story_input,
        )
    )
    raw_entry_control = _first_dict_from(
        _as_dict(entry_policy_ref.get("entry_control")),
        _as_dict(entry_applied_policy.get("commander_entry_control")),
        _as_dict(entry_applied_policy.get("entry_control")),
        story_input.get("commander_entry_control"),
        canonical_commander_decision.get("entry_control"),
        canonical_commander.get("entry_control"),
        canonical_commander.get("commander_entry_control"),
        _as_dict(canonical_commander.get("scanner_policy")).get("entry_control"),
        _as_dict(canonical_commander.get("monitor_policy")).get("entry_control"),
        _as_dict(story_input.get("commander_decision")).get("entry_control"),
        shared_commander_route.get("entry_control"),
    )
    raw_cascade = _first_dict_from(
        entry_monitor.get("entry_candidate_cascade"),
        _as_dict(entry_monitor.get("scanner_monitor_handoff")).get("entry_candidate_cascade"),
        story_input.get("monitor_entry_cascade"),
        story_input.get("entry_candidate_cascade"),
        story_handoff.get("entry_candidate_cascade"),
        monitor_reason.get("entry_candidate_cascade"),
        canonical_monitor.get("entry_candidate_cascade"),
        canonical_monitor_handoff.get("entry_candidate_cascade"),
        monitor_output.get("entry_candidate_cascade"),
        _as_dict(monitor_output.get("scanner_monitor_handoff")).get("entry_candidate_cascade"),
    )
    raw_focus_context = _first_dict_from(
        entry_monitor.get("monitor_focus_context"),
        story_input.get("monitor_focus_context"),
        monitor_reason.get("monitor_focus_context"),
        canonical_monitor.get("monitor_focus_context"),
        monitor_output.get("monitor_focus_context"),
    )
    raw_proposal = _first_dict_from(
        _as_dict(strategy_detail.get("candidate_watch_policy")),
        _as_dict(raw_entry_control.get("candidate_watch_policy_proposal")),
    )
    entry_control = _compact_commander_entry_control(raw_entry_control)
    proposal = _enrich_candidate_watch_proposal_from_entry_control(
        _compact_candidate_watch_proposal(raw_proposal),
        entry_control,
    )
    cascade = _compact_entry_candidate_cascade(raw_cascade)
    out: Dict[str, Any] = {}
    if proposal:
        out["strategy_candidate_watch_proposal"] = proposal
    if entry_control:
        out["commander_entry_control"] = entry_control
    if cascade:
        out["monitor_entry_candidate_cascade"] = cascade
    if raw_focus_context:
        out["monitor_focus_context"] = _as_dict(raw_focus_context)
    grouped_trace = _first_dict_from(
        entry_monitor.get("entry_grouped_logic_trace"),
        _as_dict(entry_monitor.get("threshold_snapshot")).get("entry_grouped_logic_trace"),
    )
    if grouped_trace:
        out["entry_grouped_logic_trace"] = _as_dict(grouped_trace)
    summary = _entry_execution_visibility_summary(
        proposal=proposal,
        entry_control=entry_control,
        cascade=cascade,
    )
    if summary:
        out["summary"] = _clip(summary, max_len=420)
    return out



def compact_strategist_report_context(story_input: Dict[str, Any], *, deps: Mapping[str, Any]) -> Dict[str, Any]:
    _as_dict = deps["as_dict"]
    _clip = deps["clip"]
    _compact_memory_application_trace = deps["compact_memory_application_trace"]
    _compact_memory_layer_decisions = deps["compact_memory_layer_decisions"]
    _compact_scalar_dict = deps["compact_scalar_dict"]
    _compact_strategy_detail_context = deps["compact_strategy_detail_context"]
    _compact_strategy_refresh_trace = deps["compact_strategy_refresh_trace"]
    _extract_strategist_report_context = deps["extract_strategist_report_context"]
    _listify = deps["listify"]
    context = _extract_strategist_report_context(story_input)
    if not context:
        return {}
    thesis = _as_dict(context.get("strategy_thesis"))
    memory = _as_dict(context.get("memory_usage_trace"))
    news = _as_dict(context.get("news_usage_trace"))
    scanner_handoff = _as_dict(context.get("scanner_handoff"))
    monitor_handoff = _as_dict(context.get("monitor_handoff"))
    boundary = _as_dict(context.get("responsibility_boundary"))
    permission = _as_dict(context.get("trade_permission_frame"))
    conflict = _as_dict(context.get("conflict_analysis"))
    delta = _as_dict(context.get("strategy_delta_trace"))
    strategy_detail = _compact_strategy_detail_context(context.get("strategy_detail"))
    refresh_trace = _compact_strategy_refresh_trace(context.get("strategy_refresh_trace"))
    return {
        "strategy_thesis": {
            "market_view": _clip(thesis.get("market_view"), max_len=220),
            "trade_style": _clip(thesis.get("trade_style"), max_len=180),
            "risk_tone": _clip(thesis.get("risk_tone"), max_len=60),
            "selected_playbook": _clip(thesis.get("selected_playbook"), max_len=60),
            "one_line": _clip(thesis.get("one_line"), max_len=240),
        },
        "strategy_delta_trace": {
            "changed": delta.get("changed"),
            "previous_playbook": _clip(delta.get("previous_playbook"), max_len=60),
            "current_playbook": _clip(delta.get("current_playbook"), max_len=60),
            "change_reason": _clip(delta.get("change_reason"), max_len=220),
        },
        "strategy_detail": strategy_detail,
        "strategy_refresh_trace": refresh_trace,
        "memory_usage_trace": {
            "schema_version": _clip(memory.get("schema_version"), max_len=80),
            "active_layers": _listify(memory.get("active_layers"), max_items=5, max_len=32),
            "priority_order": _listify(memory.get("priority_order"), max_items=6, max_len=32),
            "layer_decisions": _compact_memory_layer_decisions(memory.get("layer_decisions")),
            "applied_to_strategy": _compact_scalar_dict(memory.get("applied_to_strategy"), max_items=8, max_len=160),
            "scanner_application": _compact_memory_application_trace(memory.get("scanner_application")),
            "monitor_application": _compact_memory_application_trace(memory.get("monitor_application")),
            "human_summary": _clip(memory.get("human_summary"), max_len=320),
        },
        "news_usage_trace": {
            "schema_version": _clip(news.get("schema_version"), max_len=80),
            "query_targets": _listify(news.get("query_targets"), max_items=8, max_len=80),
            "market_headlines_used": _listify(news.get("market_headlines_used"), max_items=3, max_len=160),
            "candidate_headlines_used": _listify(news.get("candidate_headlines_used"), max_items=3, max_len=160),
            "market_effect": _clip(news.get("market_effect"), max_len=220),
            "playbook_effect": _clip(news.get("playbook_effect"), max_len=180),
            "scanner_guidance_effect": _clip(news.get("scanner_guidance_effect"), max_len=180),
            "monitor_policy_effect": _clip(news.get("monitor_policy_effect"), max_len=180),
            "ignored_or_low_signal_news": _listify(news.get("ignored_or_low_signal_news"), max_items=4, max_len=140),
            "confidence": _clip(news.get("confidence"), max_len=40),
            "source_event": _clip(news.get("source_event"), max_len=120),
            "human_summary": _clip(news.get("human_summary"), max_len=320),
        },
        "scanner_handoff": {
            "prefer_candidate_traits": _listify(scanner_handoff.get("prefer_candidate_traits"), max_items=6, max_len=80),
            "penalize_traits": _listify(scanner_handoff.get("penalize_traits"), max_items=6, max_len=80),
            "disqualifiers": _listify(scanner_handoff.get("disqualifiers"), max_items=5, max_len=80),
            "ranking_guidance": _clip(scanner_handoff.get("ranking_guidance"), max_len=260),
            "not_responsible_for": _listify(scanner_handoff.get("not_responsible_for"), max_items=5, max_len=80),
        },
        "monitor_handoff": {
            "entry_confirmation": _listify(monitor_handoff.get("entry_confirmation"), max_items=6, max_len=100),
            "hold_off_conditions": _listify(monitor_handoff.get("hold_off_conditions"), max_items=6, max_len=100),
            "entry_aggressiveness": _clip(monitor_handoff.get("entry_aggressiveness"), max_len=60),
            "policy_effect_summary": _clip(monitor_handoff.get("policy_effect_summary"), max_len=220),
        },
        "conflict_analysis": {
            "bullish_evidence": _listify(conflict.get("bullish_evidence"), max_items=5, max_len=120),
            "bearish_evidence": _listify(conflict.get("bearish_evidence"), max_items=5, max_len=120),
            "resolution": _clip(conflict.get("resolution"), max_len=240),
            "confidence": _clip(conflict.get("confidence"), max_len=40),
        },
        "trade_permission_frame": {
            "candidate_search_allowed": permission.get("candidate_search_allowed"),
            "entry_allowed_if": _listify(permission.get("entry_allowed_if"), max_items=6, max_len=100),
            "entry_blocked_if": _listify(permission.get("entry_blocked_if"), max_items=6, max_len=100),
            "permission_level": _clip(permission.get("permission_level"), max_len=60),
            "reason": _clip(permission.get("reason"), max_len=240),
        },
        "responsibility_boundary": {
            "strategist_owns": _listify(boundary.get("strategist_owns"), max_items=6, max_len=80),
            "scanner_owns": _listify(boundary.get("scanner_owns"), max_items=6, max_len=80),
            "monitor_owns": _listify(boundary.get("monitor_owns"), max_items=6, max_len=80),
            "executor_supervisor_owns": _listify(boundary.get("executor_supervisor_owns"), max_items=6, max_len=80),
            "not_responsible_for": _listify(boundary.get("not_responsible_for"), max_items=6, max_len=80),
        },
        "direct_consumption_rule": (
            "Use these strategist fields as the strategist rationale. Do not infer final symbol selection from strategist output."
        ),
    }


