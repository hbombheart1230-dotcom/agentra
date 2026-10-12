"""Intraday entry-signal score components and caps (pure projections of features).

Second Pass (P1.5) intra-function extraction from `libs/runtime/intraday_monitor_signals.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def signal_score_chart_structure_features_legacy_decision(entry_condition_path, grouped_logic_trace, triggered, reason, pattern, candles, current_close, current_vwap, recent_high, breakout_ok, pullback_ok, vwap_reclaim_ok, volume_ok, confidence_gate_ok, volume_ratio, extension_ok, extended_from_vwap_pct, max_extended_from_vwap_pct, pullback_mature, etf_deviation_tradeable, etf_deviation_entry_score, scoring_settings, *, facade):
    grouped_logic_trace["triggered_path"] = entry_condition_path
    legacy_triggered = bool(triggered)
    legacy_decision = "BUY" if legacy_triggered else "WAIT"
    legacy_reason = str(reason or "")
    legacy_pattern = str(pattern or "")
    legacy_entry_condition_path = str(entry_condition_path or "")
    chart_structure_features = facade.build_chart_structure_features(
        candles,
        current_price=current_close,
        current_vwap=current_vwap,
        recent_high=recent_high,
        breakout_ok=breakout_ok,
        pullback_ok=pullback_ok,
        reclaim_ok=vwap_reclaim_ok,
        volume_ok=volume_ok,
        confidence_ok=confidence_gate_ok,
        volume_ratio=volume_ratio,
        too_extended=bool(not extension_ok and extended_from_vwap_pct > max_extended_from_vwap_pct),
    )
    score_breakdown = facade._build_monitor_score_breakdown(
        vwap_reclaim_ok=bool(vwap_reclaim_ok),
        breakout_ok=bool(breakout_ok),
        pullback_mature=bool(pullback_mature),
        volume_ok=bool(volume_ok),
        confidence_gate_ok=bool(confidence_gate_ok),
        chart_structure_features=chart_structure_features,
    )
    if etf_deviation_tradeable:
        score_breakdown["etf_deviation_discount"] = round(float(etf_deviation_entry_score), 4)
    scoring_entry_decision = "BUY" if sum(facade._to_float(v) for v in score_breakdown.values()) >= float(scoring_settings.get("entry_threshold") or 3.0) else "WAIT"
    return (chart_structure_features, legacy_decision, legacy_entry_condition_path, legacy_pattern, legacy_reason, legacy_triggered, score_breakdown)


def signal_score_chart_human_context_chart_structure_deci(vwap_reclaim_progress, volume_score, pullback_score, breakout_score, confidence_score, confidence_threshold, entry_quality_score, breakout_quality_score, pullback_quality_score, entry_quality_path, vwap_reclaim_ok, volume_ok, pullback_ok, breakout_ok, rebound_ok, reclaim_gate_ok, breakout_path_ok, pullback_volume_path_ok, extension_ok, rebound_progress, transition_readiness_score, reclaim_distance_to_ready, volume_distance_to_ready, breakout_distance_to_ready, score_breakdown, extended_from_vwap_pct, max_extended_from_vwap_pct, scoring_settings, chart_structure_features, out, legacy_triggered, legacy_reason, legacy_decision, legacy_entry_condition_path, candles, current_close, current_vwap, recent_high, breakout_level, volume_ratio, *, facade):
    signal_evidence = facade._build_monitor_signal_evidence(
        reclaim_score=vwap_reclaim_progress,
        volume_score=volume_score,
        pullback_score=pullback_score,
        breakout_score=breakout_score,
        confidence_score=confidence_score,
        confidence_threshold=confidence_threshold,
        entry_quality_score=entry_quality_score,
        breakout_quality_score=breakout_quality_score,
        pullback_quality_score=pullback_quality_score,
        entry_quality_path=entry_quality_path,
        reclaim_ok=vwap_reclaim_ok,
        volume_ok=volume_ok,
        pullback_ok=pullback_ok,
        breakout_ok=breakout_ok,
        rebound_ok=rebound_ok,
        reclaim_gate_ok=reclaim_gate_ok,
        breakout_path_ok=breakout_path_ok,
        pullback_volume_path_ok=pullback_volume_path_ok,
        extension_ok=extension_ok,
        too_extended=bool(not extension_ok and extended_from_vwap_pct > max_extended_from_vwap_pct),
        reclaim_strength=vwap_reclaim_progress,
        rebound_strength=rebound_progress,
        transition_readiness_score=transition_readiness_score,
        reclaim_distance_to_ready=reclaim_distance_to_ready,
        volume_distance_to_ready=volume_distance_to_ready,
        breakout_distance_to_ready=breakout_distance_to_ready,
        score_breakdown=score_breakdown,
        score_threshold=float(scoring_settings.get("entry_threshold") or 3.0),
    )
    policy_interpreter_trace = facade._build_monitor_policy_interpreter_trace(
        policy_interpretation=out.get("policy_interpretation"),
        signal_evidence=signal_evidence,
        chart_structure_features=chart_structure_features,
    )
    policy_alignment_summary = facade._build_monitor_policy_alignment_summary(
        policy_interpreter_trace=policy_interpreter_trace,
    )
    policy_aware_gating = facade._build_monitor_policy_aware_gating(
        policy_interpretation=out.get("policy_interpretation"),
        signal_evidence=signal_evidence,
        policy_interpreter_trace=policy_interpreter_trace,
        policy_alignment_summary=policy_alignment_summary,
        legacy_triggered=legacy_triggered,
        legacy_reason=legacy_reason,
    )
    chart_structure_decision_hint = facade._build_chart_structure_decision_hint(
        policy_interpretation=out.get("policy_interpretation"),
        signal_evidence=signal_evidence,
        chart_structure_features=chart_structure_features,
        legacy_triggered=legacy_triggered,
        legacy_decision=legacy_decision,
        legacy_reason=legacy_reason,
        legacy_entry_condition_path=legacy_entry_condition_path,
    )
    if bool(chart_structure_decision_hint.get("available")):
        policy_interpreter_trace["notes"] = facade._dedupe_non_empty(
            [
                *list(policy_interpreter_trace.get("notes") or []),
                "chart_structure_decision_hint_evaluated",
            ]
        )
    if bool(chart_structure_decision_hint.get("applied")):
        policy_alignment_summary["summary_notes"] = facade._dedupe_non_empty(
            [
                *list(policy_alignment_summary.get("summary_notes") or []),
                "chart_structure_decision_hint_applied",
            ]
        )
    chart_human_context = (
        dict(chart_structure_features.get("human_chart_context") or {})
        if isinstance(chart_structure_features.get("human_chart_context"), facade.Mapping)
        else {}
    )
    human_chart_detail_context = facade._build_human_chart_detail_context(
        candles,
        current_close=current_close,
        current_vwap=current_vwap,
        recent_high=recent_high,
        breakout_level=breakout_level,
        volume_ratio=volume_ratio,
    )
    return (chart_human_context, chart_structure_decision_hint, human_chart_detail_context, policy_alignment_summary, policy_aware_gating, policy_interpreter_trace, signal_evidence)
