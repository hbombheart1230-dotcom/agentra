"""Strategist output artifact market/news inputs, decision/theme/policy and plan/horizon facts.

T3.5 (P1.5 Third Pass): contiguous statement runs / dict item ranges of `libs/contracts/agent_outputs.py::build_strategist_output_artifact` moved verbatim into
contract-owned projection stages. Locals enter as explicit parameters and leave as the returned record or dict; value
helpers are imported from `libs.contracts.agent_output_values`; remaining module globals of the public facade are
resolved at use time as `facade.NAME`. Final artifact assembly and `validate_artifact` stay in the public builder.
"""
from __future__ import annotations

from typing import Any, NamedTuple

from libs.contracts.agent_output_values import (
    _clip,
    _dict,
    _dict_list,
    _listify,
    _safe_float,
    _safe_int,
)


class StrategistMarketNewsInputs(NamedTuple):
    """Result of `strategist_market_news_inputs` (positional order is the pre-T3.5 tuple order)."""

    avoid_themes: Any
    candidate_news_context: Any
    decision_status: Any
    evidence_log_path: Any
    fear_index: Any
    global_signal: Any
    macro_overlay: Any
    market_news_context: Any
    market_regime: Any
    market_sentiment: Any
    negative_factors: Any
    news_context: Any
    playbook: Any
    positive_factors: Any
    selected: Any
    selected_score_total: Any
    strategist_llm: Any
    strategist_output: Any
    strategy_policy: Any
    summary: Any
    themes: Any

class StrategistDecisionThemePolicyFacts(NamedTuple):
    """Result of `strategist_decision_theme_policy_facts` (positional order is the pre-T3.5 tuple order)."""

    commander_context: Any
    confidence: Any
    decision_frame: Any
    global_sentiment_signal: Any
    market_regime_summary: Any
    memory_packet_visibility: Any
    monitor_entry_policy: Any
    news_collection_policy: Any
    news_evidence_ranked: Any
    policy_fallback_reason: Any
    policy_provenance: Any
    policy_rationale: Any
    policy_source: Any
    policy_validation_issues: Any
    policy_validation_status: Any
    strategist_plan: Any
    strategy_detail: Any
    theme_source: Any
    theme_source_fallback_used: Any
    theme_source_reason: Any
    theme_source_status: Any
    theme_strength: Any
    theme_strength_packet: Any
    trace_summary: Any

class StrategistPlanHorizonFacts(NamedTuple):
    """Result of `strategist_plan_horizon_facts` (positional order is the pre-T3.5 tuple order)."""

    candidate_hypotheses: Any
    candidate_symbols_hint: Any
    commander_horizon_policy: Any
    entry_plan: Any
    exit_plan: Any
    explanation_fields: Any
    fallback_reason: Any
    fallback_used: Any
    horizon_context: Any
    news_evidence_missing: Any
    policy_resolution: Any
    selected_playbook: Any
    strategist_horizon_proposal: Any
    strategy_horizon_feedback: Any
    strategy_summary: Any
    strategy_thesis_text: Any
    symbol_plan: Any

def strategist_market_news_inputs(state, *, facade):
    strategist_output = _dict(state.get("strategist_output"))
    strategist_llm = _dict(state.get("strategist_llm"))
    strategy_policy = _dict(strategist_output.get("strategy_policy"))
    macro_overlay = _dict(strategist_output.get("macro_stress_overlay"))
    news_context = _dict(strategist_output.get("news_context"))
    global_signal = _dict(state.get("global_signal"))
    fear_index = _dict(global_signal.get("fear_index"))
    evidence_log_path = str(facade.Path("data/evidence_ledger/events.jsonl"))
    themes = _listify(strategist_output.get("themes"), limit=6)
    avoid_themes = _listify(strategist_output.get("avoid_themes"), limit=6)
    market_news_context = _dict(strategist_output.get("market_news_context"))
    candidate_news_context = _dict(strategist_output.get("candidate_news_context"))
    playbook = _clip(strategist_output.get("playbook"), max_len=80)
    market_regime = _clip(strategist_output.get("market_regime"), max_len=80)
    market_sentiment = _clip(strategist_output.get("market_sentiment"), max_len=80)
    selected = _dict(state.get("selected"))
    selected_score_total = _safe_float(selected.get("score_total") if selected.get("score_total") is not None else selected.get("score"), 0.0)
    score_breakdown = _dict(selected.get("score_breakdown"))
    positive_factors = [f"{k}:{_safe_float(v, 0.0):.3f}" for k, v in score_breakdown.items() if _safe_float(v, 0.0) > 0][:4]
    negative_factors = [f"{k}:{_safe_float(v, 0.0):.3f}" for k, v in score_breakdown.items() if _safe_float(v, 0.0) < 0][:4]
    decision_status = "blocked" if bool(state.get("strategist_blocked")) else "ready"
    summary = (
        f"Regime {market_regime or 'not_captured'} with playbook {playbook or 'not_captured'}; "
        f"themes {', '.join(themes) if themes else 'none'}."
    )
    return StrategistMarketNewsInputs(avoid_themes, candidate_news_context, decision_status, evidence_log_path, fear_index, global_signal, macro_overlay, market_news_context, market_regime, market_sentiment, negative_factors, news_context, playbook, positive_factors, selected, selected_score_total, strategist_llm, strategist_output, strategy_policy, summary, themes)


def strategist_decision_theme_policy_facts(strategist_output, global_signal, macro_overlay, news_context, themes, avoid_themes, market_regime, market_sentiment, playbook, state, market_news_context, candidate_news_context, strategy_policy, *, facade):
    trace_summary = facade._build_strategist_trace_summary(
        strategist_output=strategist_output,
        global_signal=global_signal,
        macro_overlay=macro_overlay,
        news_context=news_context,
        themes=themes,
        avoid_themes=avoid_themes,
        market_regime=market_regime,
        market_sentiment=market_sentiment,
        playbook=playbook,
    )
    memory_packet_visibility = facade.build_strategist_memory_packet_visibility(
        state=state,
        strategist_output=strategist_output,
    )
    decision_frame = facade._build_strategist_decision_frame(
        state=state,
        strategist_output=strategist_output,
        market_regime=market_regime,
        market_sentiment=market_sentiment,
        playbook=playbook,
        themes=themes,
        avoid_themes=avoid_themes,
    )
    theme_strength_packet = _dict(strategist_output.get("theme_strength_packet")) or _dict(
        decision_frame.get("theme_strength_packet")
    )
    theme_strength = _dict(strategist_output.get("theme_strength")) or _dict(
        theme_strength_packet.get("theme_scores")
    )
    theme_source = _clip(strategist_output.get("theme_source") or theme_strength_packet.get("source"), max_len=80)
    theme_source_status = _clip(
        strategist_output.get("theme_source_status") or theme_strength_packet.get("status"),
        max_len=80,
    )
    theme_source_reason = _clip(
        strategist_output.get("theme_source_reason") or theme_strength_packet.get("reason"),
        max_len=160,
    )
    theme_source_fallback_used = bool(
        strategist_output.get("theme_source_fallback_used")
        if strategist_output.get("theme_source_fallback_used") is not None
        else theme_strength_packet.get("fallback_used")
    )
    news_evidence_ranked = facade._build_strategist_news_evidence_ranked(
        state=state,
        strategist_output=strategist_output,
        news_context=news_context,
        market_news_context=market_news_context,
        candidate_news_context=candidate_news_context,
    )
    news_collection_policy = _dict(strategist_output.get("news_collection_policy")) or _dict(
        state.get("news_collection_policy")
    )
    global_sentiment_signal = facade._build_global_sentiment_signal_payload(
        state=state,
        global_signal=global_signal,
        macro_overlay=macro_overlay,
    )
    commander_context = _dict(strategy_policy.get("commander_context"))
    if not commander_context:
        commander_context = _dict(state.get("commander_decision"))
    strategist_plan = _dict(strategy_policy.get("strategist_plan"))
    market_policy = _dict(strategy_policy.get("market_policy"))
    scanner_policy = _dict(strategy_policy.get("scanner_policy"))
    strategy_scores = _dict(strategist_output.get("strategy_scores")) or _dict(market_policy.get("strategy_scores"))
    rejected_strategy_reasons = _dict(strategist_output.get("rejected_strategy_reasons")) or _dict(
        market_policy.get("rejected_strategy_reasons")
    )
    candidate_watch_policy = _dict(strategist_output.get("candidate_watch_policy")) or _dict(
        scanner_policy.get("candidate_watch_policy")
    )
    strategy_detail = {
        "pre_llm_playbook": _clip(strategist_output.get("pre_llm_playbook"), max_len=80),
        "llm_requested_playbook": _clip(strategist_output.get("llm_requested_playbook"), max_len=80),
        "requested_playbook": _clip(strategist_output.get("requested_playbook"), max_len=80),
        "requested_playbook_source": _clip(strategist_output.get("requested_playbook_source"), max_len=80),
        "final_playbook": _clip(strategist_output.get("final_playbook") or strategist_output.get("playbook"), max_len=80),
        "tactical_strategy": _clip(
            strategist_output.get("tactical_strategy") or market_policy.get("tactical_strategy"),
            max_len=120,
        ),
        "tactical_subtype": _clip(
            strategist_output.get("tactical_subtype") or market_policy.get("tactical_subtype"),
            max_len=120,
        ),
        "strategy_scores": dict(strategy_scores),
        "rejected_strategy_reasons": dict(rejected_strategy_reasons),
        "candidate_watch_policy": dict(candidate_watch_policy),
    }
    policy_provenance = _dict(strategy_policy.get("provenance"))
    monitor_entry_policy = _dict(strategist_output.get("monitor_entry_policy"))
    policy_rationale = _clip(strategist_output.get("policy_rationale"), max_len=320)
    policy_validation_status = _clip(strategist_output.get("policy_validation_status"), max_len=80)
    policy_source = _clip(strategist_output.get("policy_source"), max_len=80)
    policy_fallback_reason = _clip(strategist_output.get("policy_fallback_reason"), max_len=220)
    policy_validation_issues = _listify(strategist_output.get("policy_validation_issues"), limit=8, max_len=120)
    market_regime_summary = _clip(strategist_output.get("market_regime_summary"), max_len=220)
    confidence = strategist_output.get("confidence")
    return StrategistDecisionThemePolicyFacts(commander_context, confidence, decision_frame, global_sentiment_signal, market_regime_summary, memory_packet_visibility, monitor_entry_policy, news_collection_policy, news_evidence_ranked, policy_fallback_reason, policy_provenance, policy_rationale, policy_source, policy_validation_issues, policy_validation_status, strategist_plan, strategy_detail, theme_source, theme_source_fallback_used, theme_source_reason, theme_source_status, theme_strength, theme_strength_packet, trace_summary)


def strategist_plan_horizon_facts(playbook, strategist_output, strategist_plan, strategy_policy, summary, state, news_evidence_ranked, news_context, strategist_llm, commander_context, *, facade):
    selected_playbook = _clip(
        strategist_output.get("selected_playbook")
        or strategist_plan.get("selected_playbook")
        or playbook,
        max_len=80,
    )
    candidate_hypotheses = _dict_list(
        strategist_output.get("candidate_hypotheses")
        if strategist_output.get("candidate_hypotheses") is not None
        else strategist_plan.get("candidate_hypotheses"),
        limit=8,
    )
    symbol_plan = _dict(
        strategist_output.get("symbol_plan")
        if strategist_output.get("symbol_plan") is not None
        else strategist_output.get("symbol_constraints")
    )
    if not symbol_plan:
        symbol_plan = _dict(
            strategist_plan.get("symbol_plan")
            if strategist_plan.get("symbol_plan") is not None
            else strategist_plan.get("symbol_constraints")
        )
    entry_plan = _dict(strategist_output.get("entry_plan"))
    if not entry_plan:
        entry_plan = _dict(strategist_plan.get("entry_plan"))
    exit_plan = _dict(strategist_output.get("exit_plan"))
    if not exit_plan:
        exit_plan = _dict(strategist_plan.get("exit_plan"))
    strategy_horizon_feedback = _dict(strategist_output.get("strategy_horizon_feedback"))
    if not strategy_horizon_feedback:
        strategy_horizon_feedback = _dict(_dict(strategy_policy.get("monitor_policy")).get("strategy_horizon_feedback"))
    strategist_horizon_proposal = _dict(strategist_output.get("strategist_horizon_proposal")) or dict(strategy_horizon_feedback)
    commander_horizon_policy = (
        _dict(strategist_output.get("commander_horizon_policy"))
        or _dict(_dict(strategy_policy.get("monitor_policy")).get("commander_horizon_policy"))
        or _dict(strategy_policy.get("commander_horizon_policy"))
    )
    horizon_context = _dict(strategist_output.get("horizon_context")) or _dict(
        _dict(strategy_policy.get("monitor_policy")).get("horizon_context")
    )
    strategy_summary = _clip(
        strategist_output.get("strategy_summary")
        or strategist_plan.get("strategy_summary")
        or summary,
        max_len=320,
    )
    candidate_symbols_hint = _listify(
        state.get("strategist_candidate_symbols_hint")
        if state.get("strategist_candidate_symbols_hint") is not None
        else state.get("candidate_symbols"),
        limit=10,
        max_len=24,
    )
    news_evidence_missing = not bool(
        list(news_evidence_ranked.get("candidate_news_ranked") or [])
        or list(news_evidence_ranked.get("market_news_ranked") or [])
        or _safe_int(news_context.get("headline_count") or news_context.get("total_headlines"))
    )
    llm_status = str(strategist_llm.get("status") or "").strip().lower()
    fallback_used = bool(strategist_llm.get("blocked")) or llm_status in {"fallback", "error", "blocked"}
    fallback_reason = _clip(
        strategist_llm.get("blocked_reason")
        or strategist_output.get("llm_frame_status")
        or strategist_llm.get("status"),
        max_len=180,
    )
    policy_resolution = facade.build_strategist_policy_resolution_surface(
        strategist_output=strategist_output,
        strategist_llm=strategist_llm,
        commander_context=commander_context,
    )
    explanation_fields = facade.build_strategist_explanation_fields(
        strategist_output={
            **dict(strategist_output),
            "news_evidence_ranked": news_evidence_ranked,
        },
        state=state,
        news_evidence_ranked=news_evidence_ranked,
    )
    strategy_thesis_text = _clip(
        strategist_output.get("news_query_reasoning")
        or strategist_output.get("monitor_guidance")
        or summary,
        max_len=500,
    )
    return StrategistPlanHorizonFacts(candidate_hypotheses, candidate_symbols_hint, commander_horizon_policy, entry_plan, exit_plan, explanation_fields, fallback_reason, fallback_used, horizon_context, news_evidence_missing, policy_resolution, selected_playbook, strategist_horizon_proposal, strategy_horizon_feedback, strategy_summary, strategy_thesis_text, symbol_plan)
