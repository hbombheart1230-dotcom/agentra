from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, TypedDict

from libs.contracts.agent_output_values import (
    _safe_float,
    _safe_int,
    _clip,
    _listify,
    _dict,
    _dict_list,
    _scanner_candidate_visibility_limit,
    _dedupe_text,
    _format_trace_number,
    _is_present,
)
from libs.runtime.dates import kst_day_str, to_kst
from libs.runtime.decision_observability import (
    build_entry_blocker_surface,
    build_commander_route_observability_surface,
    build_monitor_no_trade_surface,
    build_scanner_monitor_handoff_surface,
    build_strategist_policy_resolution_surface,
)
from libs.runtime.commander_memory_application_trace import (
    build_monitor_commander_memory_application_trace,
    build_scanner_commander_memory_application_trace,
)
from libs.runtime.strategist_explanation import build_strategist_explanation_fields
from libs.runtime.strategist_packet_visibility import build_strategist_memory_packet_visibility
import sys as _r3_sys
from libs.contracts.commander_output_context import (
    commander_route_runtime_facts,
)
from libs.contracts.commander_output_policy import (
    commander_decision_refresh_facts,
    commander_applied_policy_provenance,
)
from libs.contracts.commander_output_fields import (
    commander_artifact_route_fields,
    commander_artifact_decision_fields,
    commander_artifact_shadow_refresh_fields,
    commander_artifact_policy_fields,
    commander_artifact_observability_fields,
)
from libs.contracts.scanner_output_context import (
    scanner_row_feature_sources,
    scanner_applied_policy_evidence,
    scanner_policy_bias_evidence,
)
from libs.contracts.scanner_output_fields import (
    scanner_artifact_pool_ranking_fields,
    scanner_artifact_policy_compatibility_fields,
    scanner_artifact_bias_trace_fields,
    scanner_artifact_selection_trace_fields,
    scanner_artifact_policy_guard_fields,
    scanner_artifact_refs_preview_fields,
)
from libs.contracts.strategist_output_context import (
    strategist_market_news_inputs,
    strategist_decision_theme_policy_facts,
    strategist_plan_horizon_facts,
)
from libs.contracts.strategist_output_fields import (
    strategist_artifact_market_playbook_fields,
    strategist_artifact_context_frame_fields,
    strategist_artifact_theme_news_fallback_fields,
    strategist_artifact_commander_context_fields,
    strategist_artifact_horizon_guidance_fields,
)
from libs.contracts.strategist_output_plan_fields import (
    strategist_artifact_plan_policy_fields,
    strategist_artifact_trace_handoff_feedback_fields,
    strategist_artifact_llm_policy_bias_fields,
    strategist_artifact_refs_macro_fields,
)
from libs.contracts.monitor_output_context import (
    monitor_state_surface_sources,
    monitor_no_trade_policy_trace,
    monitor_entry_cascade_handoff,
    monitor_focus_context_projection,
)
from libs.contracts.monitor_output_decision import (
    monitor_decision_rule_evidence,
)
from libs.contracts.monitor_output_memory_bias import (
    monitor_memory_bias_application,
)
from libs.contracts.monitor_output_fields import (
    monitor_artifact_decision_fields,
    monitor_artifact_no_trade_fields,
    monitor_artifact_handoff_focus_fields,
)
from libs.contracts.monitor_output_policy_fields import (
    monitor_artifact_policy_memory_fields,
    monitor_artifact_signal_entry_fields,
)
from libs.contracts.monitor_output_exit_fields import (
    monitor_artifact_trace_evaluation_fields,
    monitor_artifact_price_exit_metric_fields,
    monitor_artifact_pnl_hold_exit_fields,
)


AGENT_OUTPUT_SCHEMA_VERSION = "agent_output.v1"
AGENT_VALIDATION_SCHEMA_VERSION = "agent_output_validation.v1"


class AgentOutput(TypedDict, total=False):
    schema_version: str
    agent: str
    run_id: str
    day: str
    ts: str
    phase: str
    symbol: str
    status: str
    evidence_refs: Dict[str, Any]
    source_refs: Dict[str, Any]
    validation: Dict[str, Any]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_strategist_trace_summary(
    *,
    strategist_output: Dict[str, Any],
    global_signal: Dict[str, Any],
    macro_overlay: Dict[str, Any],
    news_context: Dict[str, Any],
    themes: List[str],
    avoid_themes: List[str],
    market_regime: str,
    market_sentiment: str,
    playbook: str,
) -> Dict[str, Any]:
    fear_index = _dict(global_signal.get("fear_index"))
    strategy_policy_summary = _dict(strategist_output.get("strategy_policy_summary"))
    market_policy = _dict(strategy_policy_summary.get("market_policy"))
    risk_tone = _clip(
        strategist_output.get("risk_tone") or market_policy.get("risk_tone"),
        max_len=40,
    )
    trade_aggressiveness = _clip(
        strategist_output.get("trade_aggressiveness") or market_policy.get("trade_aggressiveness"),
        max_len=40,
    )
    monitor_guidance = _clip(
        strategist_output.get("monitor_guidance") or market_policy.get("monitor_guidance"),
        max_len=80,
    )
    reason_chain = _listify(strategist_output.get("reason_chain"), limit=8, max_len=180)
    if not reason_chain:
        reason_chain = _listify(market_policy.get("reason_chain"), limit=8, max_len=180)
    news_targets = _listify(strategist_output.get("news_query_targets"), limit=8, max_len=80)
    stress_flags = _listify(macro_overlay.get("stress_flags"), limit=6, max_len=60)
    headline_count = _safe_int(
        news_context.get("headline_count")
        or strategist_output.get("news_total_headlines")
        or strategist_output.get("market_news_total_headlines")
    )
    query_count = _safe_int(
        strategist_output.get("market_news_query_count")
        or len(news_targets)
    )
    global_sentiment_score = strategist_output.get("global_sentiment_score")
    vix_level = (
        fear_index.get("level")
        if fear_index.get("level") not in (None, "")
        else global_signal.get("vix_level")
        if global_signal.get("vix_level") not in (None, "")
        else macro_overlay.get("vix_level")
    )
    missing_flags: List[str] = []
    if global_sentiment_score in (None, ""):
        missing_flags.append("global_sentiment_score_missing")
    if vix_level in (None, ""):
        missing_flags.append("vix_level_missing")
    if headline_count <= 0:
        missing_flags.append("news_headlines_missing")
    if not reason_chain:
        missing_flags.append("reason_chain_missing")
    summary = (
        f"Strategist used regime={market_regime or 'not_captured'}, sentiment={market_sentiment or 'not_captured'}, "
        f"playbook={playbook or 'not_captured'}, risk_tone={risk_tone or 'not_captured'}, "
        f"global_sentiment={_format_trace_number(global_sentiment_score, digits=3)}, "
        f"vix={_format_trace_number(vix_level, digits=2)}, headlines={headline_count}, targets={query_count}."
    )
    highlights = _dedupe_text(
        [
            f"Regime {market_regime or 'not_captured'} / playbook {playbook or 'not_captured'}",
            (
                "Themes: "
                + (", ".join(themes[:4]) if themes else "none")
                + (" | avoid: " + ", ".join(avoid_themes[:4]) if avoid_themes else "")
            ),
            (
                f"Sentiment { _format_trace_number(global_sentiment_score, digits=3) } / "
                f"VIX { _format_trace_number(vix_level, digits=2) } / "
                f"stress {', '.join(stress_flags) if stress_flags else 'none'}"
            ),
            f"News evidence: {headline_count} headlines across {query_count} targets",
            (
                "Risk tone: "
                + (risk_tone or "not_captured")
                + (f" / aggressiveness: {trade_aggressiveness}" if trade_aggressiveness else "")
            ),
        ],
        limit=6,
        max_len=220,
    )
    return {
        "summary": _clip(summary, max_len=320),
        "highlights": highlights,
        "reason_chain": reason_chain,
        "headline_count": headline_count,
        "news_query_count": query_count,
        "news_query_targets": news_targets,
        "global_sentiment_score": global_sentiment_score,
        "vix_level": vix_level,
        "stress_flags": stress_flags,
        "market_regime": market_regime,
        "market_sentiment": market_sentiment,
        "playbook": playbook,
        "risk_tone": risk_tone,
        "trade_aggressiveness": trade_aggressiveness,
        "monitor_guidance": monitor_guidance,
        "themes": list(themes),
        "avoid_themes": list(avoid_themes),
        "missing_flags": missing_flags,
    }


def _build_strategist_decision_frame(
    *,
    state: Dict[str, Any],
    strategist_output: Dict[str, Any],
    market_regime: str,
    market_sentiment: str,
    playbook: str,
    themes: List[str],
    avoid_themes: List[str],
) -> Dict[str, Any]:
    event_payload = _dict(state.get("strategist_decision_frame"))
    if event_payload:
        out = dict(event_payload)
        theme_packet = _dict(strategist_output.get("theme_strength_packet"))
        if theme_packet and not _dict(out.get("theme_strength_packet")):
            out["theme_strength_packet"] = theme_packet
        if not out.get("theme_source") and (theme_packet.get("source") or strategist_output.get("theme_source")):
            out["theme_source"] = _clip(strategist_output.get("theme_source") or theme_packet.get("source"), max_len=80)
        if not out.get("theme_source_status") and (theme_packet.get("status") or strategist_output.get("theme_source_status")):
            out["theme_source_status"] = _clip(
                strategist_output.get("theme_source_status") or theme_packet.get("status"),
                max_len=80,
            )
        if not out.get("theme_source_reason") and (theme_packet.get("reason") or strategist_output.get("theme_source_reason")):
            out["theme_source_reason"] = _clip(
                strategist_output.get("theme_source_reason") or theme_packet.get("reason"),
                max_len=160,
            )
        if not out.get("available_themes") and isinstance(strategist_output.get("available_themes"), list):
            out["available_themes"] = list(strategist_output.get("available_themes") or [])[:8]
        if not out.get("selected_themes") and isinstance(strategist_output.get("selected_themes"), list):
            out["selected_themes"] = _listify(strategist_output.get("selected_themes"), limit=5, max_len=80)
        if not out.get("theme_strategy") and isinstance(strategist_output.get("theme_strategy"), dict):
            out["theme_strategy"] = _dict(strategist_output.get("theme_strategy"))
        return out
    strategy_policy_summary = _dict(strategist_output.get("strategy_policy_summary"))
    strategy_memory = _dict(strategist_output.get("strategy_memory"))
    theme_packet = _dict(strategist_output.get("theme_strength_packet"))
    theme_strength = _dict(strategist_output.get("theme_strength")) or _dict(theme_packet.get("theme_scores"))
    reason_chain = _listify(
        strategist_output.get("reason_chain")
        or _dict(strategy_policy_summary.get("market_policy")).get("reason_chain"),
        limit=8,
        max_len=180,
    )
    return {
        "market_regime": market_regime,
        "market_sentiment": market_sentiment,
        "playbook": playbook,
        "themes": list(themes),
        "selected_themes": _listify(strategist_output.get("selected_themes"), limit=5, max_len=80),
        "avoid_themes": list(avoid_themes),
        "scanner_bias": _clip(strategist_output.get("scanner_bias"), max_len=80),
        "scanner_priority": _listify(strategist_output.get("scanner_priority"), limit=8, max_len=80),
        "trade_aggressiveness": _clip(strategist_output.get("trade_aggressiveness"), max_len=40),
        "risk_tone": _clip(strategist_output.get("risk_tone"), max_len=40),
        "monitor_guidance": _clip(strategist_output.get("monitor_guidance"), max_len=80),
        "report_focus": _listify(strategist_output.get("report_focus"), limit=8, max_len=80),
        "strategy_memory": strategy_memory,
        "reason_chain": reason_chain,
        "strategy_policy_summary": strategy_policy_summary,
        "theme_strength": theme_strength,
        "theme_strength_packet": theme_packet,
        "available_themes": list(strategist_output.get("available_themes") or [])[:8]
        if isinstance(strategist_output.get("available_themes"), list)
        else [],
        "theme_strategy": _dict(strategist_output.get("theme_strategy")),
        "theme_source": _clip(strategist_output.get("theme_source") or theme_packet.get("source"), max_len=80),
        "theme_source_status": _clip(
            strategist_output.get("theme_source_status") or theme_packet.get("status"),
            max_len=80,
        ),
        "theme_source_reason": _clip(
            strategist_output.get("theme_source_reason") or theme_packet.get("reason"),
            max_len=160,
        ),
    }


def _build_strategist_news_evidence_ranked(
    *,
    state: Dict[str, Any],
    strategist_output: Dict[str, Any],
    news_context: Dict[str, Any],
    market_news_context: Dict[str, Any],
    candidate_news_context: Dict[str, Any],
) -> Dict[str, Any]:
    event_payload = _dict(state.get("strategist_news_evidence_ranked"))
    if event_payload:
        return dict(event_payload)
    return {
        "news_query_targets": _listify(strategist_output.get("news_query_targets"), limit=12, max_len=80),
        "candidate_news_ranked": list(candidate_news_context.get("ranked_rows") or [])[:8],
        "market_news_ranked": list(market_news_context.get("ranked_rows") or [])[:8],
        "candidate_news_context": dict(candidate_news_context),
        "market_news_context": dict(market_news_context),
        "news_context": dict(news_context),
    }


def _build_global_sentiment_signal_payload(
    *,
    state: Dict[str, Any],
    global_signal: Dict[str, Any],
    macro_overlay: Dict[str, Any],
) -> Dict[str, Any]:
    event_payload = _dict(state.get("strategist_global_sentiment_breakdown"))
    if event_payload:
        return dict(event_payload)
    fear_index = _dict(global_signal.get("fear_index"))
    return {
        "score": global_signal.get("score"),
        "status": _clip(global_signal.get("status"), max_len=40),
        "source": _clip(global_signal.get("source"), max_len=80),
        "fear_index": {
            "level": fear_index.get("level"),
            "change_pct": fear_index.get("change_pct"),
            "level_pressure": fear_index.get("level_pressure"),
        },
        "index_moves": _dict(global_signal.get("index_moves")),
        "macro_moves": _dict(global_signal.get("macro_moves")),
        "stress_flags": _listify(macro_overlay.get("stress_flags"), limit=8, max_len=80),
    }


def _build_scanner_trace_summary(
    *,
    symbol: str,
    selected_rank: int,
    universe_size: int,
    selected_score_total: float,
    margin_vs_second: float,
    selected_score_breakdown: Dict[str, Any],
    selected: Dict[str, Any],
    candidate_preview: List[Dict[str, Any]],
    selection_summary: str,
    scanner_bias_applied: bool = False,
    scanner_bias_summary: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    selected_candidate = _dict(selected.get("candidate"))
    selected_sources = _listify(selected_candidate.get("sources"), limit=6, max_len=60)
    positive_factors = [f"{k}:{_safe_float(v, 0.0):.3f}" for k, v in selected_score_breakdown.items() if _safe_float(v, 0.0) > 0][:4]
    negative_factors = [f"{k}:{_safe_float(v, 0.0):.3f}" for k, v in selected_score_breakdown.items() if _safe_float(v, 0.0) < 0][:4]
    runner_ups = [
        {
            "symbol": str(row.get("symbol") or ""),
            "rank": _safe_int(row.get("rank")),
            "score_total": _safe_float(row.get("score_total")),
            "why": _clip(row.get("why"), max_len=160),
        }
        for row in candidate_preview[1:3]
        if isinstance(row, dict) and str(row.get("symbol") or "").strip()
    ]
    missing_flags: List[str] = []
    if not symbol:
        missing_flags.append("selected_symbol_missing")
    if universe_size <= 0:
        missing_flags.append("candidate_pool_missing")
    if not positive_factors and not negative_factors:
        missing_flags.append("score_breakdown_missing")
    bias_summary_dict = _dict(scanner_bias_summary)
    summary = (
        f"Scanner selected {symbol or 'not_captured'} rank #{selected_rank or 0}/{universe_size or 0} "
        f"with score={selected_score_total:.3f} and margin_vs_second={margin_vs_second:.3f}."
    )
    highlights = _dedupe_text(
        [
            f"Selected {symbol or 'not_captured'} rank #{selected_rank or 0} out of {universe_size or 0}",
            f"Score {selected_score_total:.3f} with margin {margin_vs_second:.3f} vs runner-up",
            f"Source mix: {', '.join(selected_sources) if selected_sources else 'not_captured'}",
            (
                "Positive factors: " + ", ".join(positive_factors)
                if positive_factors
                else "Positive factors were not captured"
            ),
            (
                "Negative factors: " + ", ".join(negative_factors)
                if negative_factors
                else "Negative factors were not captured"
            ),
            (
                "Bias: " + str(bias_summary_dict.get("summary") or "")
                if scanner_bias_applied and str(bias_summary_dict.get("summary") or "").strip()
                else ""
            ),
        ],
        limit=6,
        max_len=220,
    )
    return {
        "summary": _clip(selection_summary or summary, max_len=320),
        "highlights": highlights,
        "selected_symbol": symbol,
        "runner_up_symbol": str(runner_ups[0].get("symbol") or "") if runner_ups else "",
        "selected_rank": selected_rank,
        "universe_size": universe_size,
        "candidate_count": universe_size,
        "selected_score_total": selected_score_total,
        "margin_vs_second": margin_vs_second,
        "selected_sources": selected_sources,
        "critical_positive_factors": positive_factors,
        "critical_negative_factors": negative_factors,
        "top_candidates": candidate_preview[:3],
        "runner_ups": runner_ups,
        "scanner_bias_applied": bool(scanner_bias_applied),
        "scanner_bias_summary": bias_summary_dict,
        "missing_flags": missing_flags,
    }


def _build_scanner_candidate_ranking_table(
    *,
    state: Dict[str, Any],
    candidate_preview: List[Dict[str, Any]],
) -> Dict[str, Any]:
    event_payload = _dict(state.get("scanner_candidate_ranking_table"))
    if event_payload:
        rows = list(event_payload.get("rows") or [])
        return {
            "tie_break_rule": _clip(event_payload.get("tie_break_rule"), max_len=120),
            "rows": [dict(row) for row in rows if isinstance(row, dict)],
        }
    return {
        "tie_break_rule": "score_total desc -> confidence desc -> risk_score asc",
        "rows": [dict(row) for row in candidate_preview],
    }


def _build_scanner_candidate_selection_reason(
    *,
    state: Dict[str, Any],
    selected_symbol: str,
    selected_rank: int,
    selected_score_total: float,
    margin_vs_second: float,
    critical_positive_factors: List[str],
    critical_negative_factors: List[str],
    selection_summary: str,
    runner_ups: List[Dict[str, Any]],
    selected: Dict[str, Any],
) -> Dict[str, Any]:
    event_payload = _dict(state.get("scanner_candidate_selection_reason"))
    if event_payload:
        return dict(event_payload)
    selected_candidate = _dict(selected.get("candidate"))
    why_selected = _listify(selected.get("top_reasons"), limit=6, max_len=180)
    if not why_selected:
        why_selected = _dedupe_text(
            [
                f"highest total score ({selected_score_total:.3f})" if selected_score_total else "",
                f"confidence {_safe_float(selected.get('confidence')):.2f} and risk {_safe_float(selected.get('risk_score')):.2f}",
                f"source mix: {', '.join(_listify(selected_candidate.get('sources'), limit=4, max_len=40))}",
            ],
            limit=4,
            max_len=180,
        )
    return {
        "selected_symbol": selected_symbol,
        "selected_rank": selected_rank,
        "selected_score_total": selected_score_total,
        "margin_vs_second": margin_vs_second,
        "critical_positive_factors": list(critical_positive_factors),
        "critical_negative_factors": list(critical_negative_factors),
        "selection_summary": selection_summary,
        "why_selected": why_selected,
        "runner_ups_lost": list(runner_ups),
        "entry_compatibility_score": _safe_float(selected.get("entry_compatibility_score"), 0.0),
        "compatibility_bias": _safe_float(selected.get("compatibility_bias"), 0.0),
        "expected_monitor_block_reason": _clip(selected.get("expected_monitor_block_reason"), max_len=120),
        "compatibility_trace": _dict(selected.get("compatibility_trace")),
        "tie_break_rule": "score_total desc -> confidence desc -> risk_score asc",
        "final_decision_basis": "Scanner selected the highest-ranked candidate after strategist-guided weighting, source scoring, and risk penalties.",
    }


def _monitor_decision_summary(
    *,
    decision_phase: str,
    primary_reason_text: str,
    threshold_snapshot: Dict[str, Any],
    signal_snapshot: Dict[str, Any],
    missing_inputs: List[str],
) -> str:
    from libs.contracts.agent_output_parts import monitor_decision_summary as _owner
    return _owner.monitor_decision_summary(decision_phase=decision_phase, primary_reason_text=primary_reason_text, threshold_snapshot=threshold_snapshot, signal_snapshot=signal_snapshot, missing_inputs=missing_inputs, facade=_r3_sys.modules[__name__])


def _phase(state: Dict[str, Any]) -> str:
    from libs.contracts.agent_output_parts import artifact_metadata as _owner
    return _owner.phase(state, facade=_r3_sys.modules[__name__])


def _run_ts(state: Dict[str, Any]) -> str:
    for key in ("started_at", "ts", "tick_ts_iso", "now_iso"):
        value = str(state.get(key) or "").strip()
        if value:
            return value
    tick_epoch = _safe_int(state.get("tick_ts"), 0)
    if tick_epoch > 0:
        return datetime.fromtimestamp(tick_epoch, tz=timezone.utc).isoformat()
    return _utc_now_iso()


def _parse_day_from_timestamp(value: str) -> str:
    from libs.contracts.agent_output_parts import artifact_metadata as _owner
    return _owner.parse_day_from_timestamp(value, facade=_r3_sys.modules[__name__])


def _run_day(state: Dict[str, Any]) -> str:
    for key in ("day", "trade_day", "session_day", "runtime_day"):
        value = str(state.get(key) or "").strip()
        if len(value) == 10 and value[4:5] == "-" and value[7:8] == "-":
            return value
    for key in ("started_at", "ts", "tick_ts_iso", "now_iso"):
        resolved = _parse_day_from_timestamp(str(state.get(key) or "").strip())
        if resolved:
            return resolved
    tick_epoch = _safe_int(state.get("tick_ts"), 0)
    if tick_epoch > 0:
        return kst_day_str(datetime.fromtimestamp(tick_epoch, tz=timezone.utc))
    return kst_day_str(to_kst(datetime.now(timezone.utc)))


def _base_output(state: Dict[str, Any], *, agent: str, symbol: str = "", status: str = "ok") -> AgentOutput:
    return {
        "schema_version": AGENT_OUTPUT_SCHEMA_VERSION,
        "agent": str(agent or "").strip(),
        "run_id": str(state.get("run_id") or "").strip(),
        "day": _run_day(state),
        "ts": _run_ts(state),
        "phase": _phase(state),
        "symbol": str(symbol or "").strip(),
        "status": str(status or "ok").strip(),
    }


def _required_keys_for_agent(agent: str) -> List[str]:
    from libs.contracts.agent_output_parts import artifact_validation as _owner
    return _owner.required_keys_for_agent(agent, facade=_r3_sys.modules[__name__])


def _required_keys_for_artifact(obj: Dict[str, Any]) -> List[str]:
    from libs.contracts.agent_output_parts import artifact_validation as _owner
    return _owner.required_keys_for_artifact(obj, facade=_r3_sys.modules[__name__])


def validate_artifact(artifact: Dict[str, Any]) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import artifact_validation as _owner
    return _owner.validate_artifact(artifact, facade=_r3_sys.modules[__name__])


def build_strategist_output_artifact(state: Dict[str, Any]) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import artifact_build_strategist as _owner
    return _owner.build_strategist_output_artifact(state=state, facade=_r3_sys.modules[__name__])


def build_scanner_output_artifact(state: Dict[str, Any]) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import artifact_build_scanner as _owner
    return _owner.build_scanner_output_artifact(state=state, facade=_r3_sys.modules[__name__])


def build_monitor_output_artifact(state: Dict[str, Any]) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import artifact_build_monitor as _owner
    return _owner.build_monitor_output_artifact(state=state, facade=_r3_sys.modules[__name__])


def build_supervisor_output_artifact(
    state: Dict[str, Any],
    *,
    order: Dict[str, Any],
    allowed: bool,
    reason: str,
    details: Dict[str, Any] | None = None,
    strategy_policy_summary: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import artifact_build_supervisor_executor as _owner
    return _owner.build_supervisor_output_artifact(state=state, order=order, allowed=allowed, reason=reason, details=details, strategy_policy_summary=strategy_policy_summary, facade=_r3_sys.modules[__name__])


def build_executor_output_artifact(
    state: Dict[str, Any],
    *,
    execution: Dict[str, Any],
    order: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import artifact_build_supervisor_executor as _owner
    return _owner.build_executor_output_artifact(state=state, execution=execution, order=order, facade=_r3_sys.modules[__name__])


def _build_commander_shadow_artifact_summary(
    state: Dict[str, Any],
    *,
    mode: str,
    phase: str,
    path: str,
    status: str,
    reason: str = "",
) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import artifact_build_shadow as _owner
    return _owner.build_commander_shadow_artifact_summary(state=state, mode=mode, phase=phase, path=path, status=status, reason=reason, facade=_r3_sys.modules[__name__])


def build_commander_output_artifact(
    state: Dict[str, Any],
    *,
    mode: str,
    phase: str,
    path: str,
    status: str,
    reason: str = "",
) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import artifact_build_commander as _owner
    return _owner.build_commander_output_artifact(state=state, mode=mode, phase=phase, path=path, status=status, reason=reason, facade=_r3_sys.modules[__name__])


def _commander_shadow_has_open_order(state: Dict[str, Any]) -> Any:
    from libs.contracts.agent_output_parts import commander_shadow_checks as _owner
    return _owner.has_open_order(state, facade=_r3_sys.modules[__name__])


def _commander_shadow_actual_runtime(state: Dict[str, Any], *, path: str) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts.commander_shadow_runtime import build_actual_runtime

    return build_actual_runtime(state, path=path, facade=_r3_sys.modules[__name__])

def _commander_shadow_observations(state: Dict[str, Any], *, path: str) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts.commander_shadow_runtime import build_observations

    return build_observations(state, path=path, facade=_r3_sys.modules[__name__])

def _gate_pass(metrics: Dict[str, Any], passed_checks: List[str], failed_checks: List[str], key: str) -> Any:
    from libs.contracts.agent_output_parts import commander_shadow_checks as _owner
    return _owner.gate_pass(metrics, passed_checks, failed_checks, key, facade=_r3_sys.modules[__name__])


def _score_from_checks(*, passed_checks: List[str], failed_checks: List[str], fallback: Any) -> Any:
    from libs.contracts.agent_output_parts import commander_shadow_checks as _owner
    return _owner.score_from_checks(passed_checks=passed_checks, failed_checks=failed_checks, fallback=fallback, facade=_r3_sys.modules[__name__])


def _commander_shadow_monitor_gate_details(state: Dict[str, Any]) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import commander_shadow_evidence as _owner
    return _owner.build_monitor_gate_details(state, facade=_r3_sys.modules[__name__])


def _commander_shadow_context_delta_summary(state: Dict[str, Any], *, observations: Dict[str, Any]) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import commander_shadow_evidence as _owner
    return _owner.build_context_delta_summary(state, observations=observations, facade=_r3_sys.modules[__name__])


def _commander_shadow_no_trade_reason_code(
    state: Dict[str, Any],
    *,
    observations: Dict[str, Any],
    actual_runtime: Dict[str, Any],
    path: str,
) -> str:
    from libs.contracts.agent_output_parts.commander_shadow_advice import no_trade_reason_code
    return no_trade_reason_code(state, observations=observations, actual_runtime=actual_runtime, path=path, facade=_r3_sys.modules[__name__])


def _commander_shadow_strategist_recommendation(
    *,
    no_trade_reason_code: str,
    observations: Dict[str, Any],
) -> str:
    from libs.contracts.agent_output_parts.commander_shadow_advice import strategist_recommendation
    return strategist_recommendation(no_trade_reason_code=no_trade_reason_code, observations=observations)


def _commander_shadow_llm_call_advice(
    *,
    strategist_action_recommendation: str,
    observations: Dict[str, Any],
    state: Dict[str, Any],
) -> str:
    from libs.contracts.agent_output_parts import commander_shadow_advice_extended as _owner
    return _owner.llm_call_advice(
        strategist_action_recommendation=strategist_action_recommendation,
        observations=observations,
        state=state,
        facade=_r3_sys.modules[__name__],
    )


def _commander_shadow_suggested_action(
    *,
    strategist_action_recommendation: str,
    llm_call_advice: str,
    no_trade_reason_code: str,
) -> str:
    from libs.contracts.agent_output_parts import commander_shadow_advice_extended as _owner
    return _owner.suggested_action(
        strategist_action_recommendation=strategist_action_recommendation,
        llm_call_advice=llm_call_advice,
        no_trade_reason_code=no_trade_reason_code,
        facade=_r3_sys.modules[__name__],
    )


def _commander_shadow_next_action_recommendation(
    *,
    strategist_action_recommendation: str,
    llm_call_advice: str,
    no_trade_reason_code: str,
    actual_runtime: Dict[str, Any],
) -> str:
    from libs.contracts.agent_output_parts import commander_shadow_advice_extended as _owner
    return _owner.next_action_recommendation(
        strategist_action_recommendation=strategist_action_recommendation,
        llm_call_advice=llm_call_advice,
        no_trade_reason_code=no_trade_reason_code,
        actual_runtime=actual_runtime,
        facade=_r3_sys.modules[__name__],
    )


def _commander_shadow_reason_summary(
    *,
    no_trade_reason_code: str,
    observations: Dict[str, Any],
    actual_runtime: Dict[str, Any],
) -> str:
    from libs.contracts.agent_output_parts import commander_shadow_advice_extended as _owner
    return _owner.reason_summary(
        no_trade_reason_code=no_trade_reason_code,
        observations=observations,
        actual_runtime=actual_runtime,
        facade=_r3_sys.modules[__name__],
    )


def _commander_shadow_recommendation_gap(
    *,
    strategist_action_recommendation: str,
    llm_call_advice: str,
    actual_runtime: Dict[str, Any],
) -> str:
    from libs.contracts.agent_output_parts import commander_shadow_advice_extended as _owner
    return _owner.recommendation_gap(
        strategist_action_recommendation=strategist_action_recommendation,
        llm_call_advice=llm_call_advice,
        actual_runtime=actual_runtime,
        facade=_r3_sys.modules[__name__],
    )


def _commander_shadow_pre_strategist_snapshot(
    *,
    state: Dict[str, Any],
    observations: Dict[str, Any],
    context_delta_summary: Dict[str, Any],
    strategist_action_recommendation: str,
    llm_call_advice: str,
) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import commander_shadow_assessments as _owner
    return _owner.pre_strategist_snapshot(
        state=state,
        observations=observations,
        context_delta_summary=context_delta_summary,
        strategist_action_recommendation=strategist_action_recommendation,
        llm_call_advice=llm_call_advice,
        facade=_r3_sys.modules[__name__],
    )


def _commander_shadow_post_strategist_assessment(
    *,
    state: Dict[str, Any],
    actual_runtime: Dict[str, Any],
    context_delta_summary: Dict[str, Any],
    recommendation_gap: str,
) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import commander_shadow_assessments as _owner
    return _owner.post_strategist_assessment(
        state=state,
        actual_runtime=actual_runtime,
        context_delta_summary=context_delta_summary,
        recommendation_gap=recommendation_gap,
        facade=_r3_sys.modules[__name__],
    )


def _commander_shadow_post_monitor_assessment(
    *,
    actual_runtime: Dict[str, Any],
    monitor_gate_details: Dict[str, Any],
) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import commander_shadow_assessments as _owner
    return _owner.post_monitor_assessment(
        actual_runtime=actual_runtime,
        monitor_gate_details=monitor_gate_details,
        facade=_r3_sys.modules[__name__],
    )


def _commander_shadow_end_of_cycle_summary(
    *,
    no_trade_reason_code: str,
    reason_summary: str,
    actual_runtime: Dict[str, Any],
    next_action_recommendation: str,
    recommendation_gap: str,
) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import commander_shadow_cycle as _owner
    return _owner.end_of_cycle_summary(no_trade_reason_code=no_trade_reason_code, reason_summary=reason_summary, actual_runtime=actual_runtime, next_action_recommendation=next_action_recommendation, recommendation_gap=recommendation_gap, facade=_r3_sys.modules[__name__])


def build_commander_shadow_artifact(
    state: Dict[str, Any],
    *,
    mode: str,
    phase: str,
    path: str,
    status: str,
    reason: str = "",
) -> Dict[str, Any]:
    from libs.contracts.agent_output_parts import artifact_build_shadow as _owner
    return _owner.build_commander_shadow_artifact(state=state, mode=mode, phase=phase, path=path, status=status, reason=reason, facade=_r3_sys.modules[__name__])
