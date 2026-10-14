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
    if missing_inputs:
        missing = ",".join([_clip(item, max_len=24) for item in list(missing_inputs)[:3] if _clip(item, max_len=24)])
        return _clip(f"Decision: insufficient data ({missing or 'unavailable'})", max_len=120)
    phase = str(decision_phase or "").strip().lower()
    reason = _clip(primary_reason_text, max_len=64) or "unavailable"
    if phase == "entry":
        entry_signal = _clip(_dict(signal_snapshot).get("entry_pattern"), max_len=42) or reason
        entry_thresholds = _dict(_dict(threshold_snapshot).get("entry_thresholds"))
        threshold_text = (
            _clip(entry_thresholds.get("max_extended_from_vwap_pct"), max_len=24)
            or _clip(entry_thresholds.get("volume_ratio_min"), max_len=24)
            or "thresholds"
        )
        return _clip(f"Entry: {entry_signal} met with {threshold_text} -> BUY", max_len=120)
    if phase == "exit":
        trigger = _clip(_dict(signal_snapshot).get("exit_triggered_rule"), max_len=48) or reason
        return _clip(f"Exit: {trigger}", max_len=120)
    if phase == "hold":
        return "Hold: conditions stable, no exit trigger"
    return _clip(f"No action: {reason}", max_len=120)


def _phase(state: Dict[str, Any]) -> str:
    return str(state.get("runtime_phase") or state.get("phase") or "").strip()


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
    text = str(value or "").strip()
    if not text:
        return ""
    if len(text) == 10 and text[4:5] == "-" and text[7:8] == "-":
        return text
    normalized = text.replace("Z", "+00:00") if text.endswith("Z") else text
    try:
        return kst_day_str(datetime.fromisoformat(normalized))
    except Exception:
        if len(text) >= 10 and text[4:5] == "-" and text[7:8] == "-":
            return text[:10]
    return ""


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
    base = ["schema_version", "agent", "run_id", "day", "ts", "phase", "status"]
    specific: Dict[str, List[str]] = {
        "strategist": [
            "market_regime",
            "market_context_summary",
            "news_evidence_summary",
            "sentiment_evidence_summary",
            "volatility_context",
            "strategy_thesis",
            "playbook",
            "market_context",
            "news_context",
            "strategy_frame",
            "policy_selected",
            "llm_trace",
            "decision_summary",
            "llm_metadata_summary",
            "source_refs",
        ],
        "scanner": [
            "candidate_pool_snapshot",
            "filter_funnel",
            "universe_size",
            "candidate_list_summary",
            "ranking_table",
            "selected_symbol",
            "selected_rank",
            "selection_reason",
            "selection_reason_detail",
            "rejection_summary",
            "filter_feature_summary",
            "evidence_refs",
        ],
        "monitor": [
            "position_snapshot",
            "monitor_evaluation",
            "monitor_action_decision",
            "thresholds_guards_used",
            "threshold_snapshot",
            "signal_snapshot",
            "market_snapshot_refs",
            "evaluation_summary",
            "decision",
            "decision_phase",
            "decision_action",
            "decision_status",
            "decision_summary",
            "primary_reason_code",
            "primary_reason_text",
            "secondary_reason_codes",
            "intent_emitted",
            "evidence_quality",
            "missing_inputs",
            "generated_at",
            "decision_reason_chain",
            "trigger_details",
            "evidence_refs",
        ],
        "supervisor": [
            "invoked_agents",
            "command",
            "decision",
            "approval_result",
            "reason",
            "blocked_allowed_details",
        ],
        "executor": [
            "action",
            "order_request_summary",
            "execution_enabled",
            "approval_mode",
            "broker_result",
            "final_execution_status",
            "failure_reason",
        ],
        "commander": [
            "mode",
            "phase",
            "path",
            "runtime_mode",
            "runtime_phase",
            "selected_route",
            "route_reason_codes",
            "route_reason_text",
            "open_position_count",
            "open_position_symbols",
            "strategist_cache_used",
            "strategist_blocked",
            "cooldown_applied",
            "incident_state",
            "portfolio_preflight_result",
            "generated_at",
            "session_type",
            "market_clock_phase",
            "portfolio_state_summary",
            "market_regime_summary",
            "goal",
            "agent_invocation_plan",
            "decision_checkpoints",
            "final_runtime_path",
            "final_reason",
            "handoff_instruction",
            "invoked_agents",
            "command",
            "decision",
            "approval_result",
            "reason",
            "blocked_allowed_details",
        ],
    }
    out = list(base)
    out.extend(list(specific.get(str(agent or "").strip().lower(), [])))
    return out


def _required_keys_for_artifact(obj: Dict[str, Any]) -> List[str]:
    artifact = dict(obj or {}) if isinstance(obj, dict) else {}
    agent = str(artifact.get("agent") or "").strip().lower()
    mode = str(artifact.get("mode") or "").strip().lower()
    if agent == "commander" and (mode == "shadow" or bool(artifact.get("shadow_only"))):
        base = ["schema_version", "agent", "run_id", "day", "ts", "phase", "status"]
        specific = [
            "mode",
            "decision",
            "strategist_action_recommendation",
            "llm_call_advice",
            "suggested_action",
            "next_action_recommendation",
            "no_trade_reason_code",
            "reason_summary",
            "observations",
            "actual_runtime",
            "monitor_gate_details",
            "context_delta_summary",
            "pre_strategist_shadow_snapshot",
            "post_strategist_assessment",
            "post_monitor_assessment",
            "end_of_cycle_summary",
            "shadow_only",
            "generated_at",
        ]
        return base + specific
    return _required_keys_for_agent(agent)


def validate_artifact(artifact: Dict[str, Any]) -> Dict[str, Any]:
    obj = dict(artifact or {}) if isinstance(artifact, dict) else {}
    expected = _required_keys_for_artifact(obj)
    present: List[str] = []
    missing: List[str] = []
    for key in expected:
        if _is_present(obj.get(key)):
            present.append(key)
        else:
            missing.append(key)
    completeness = float(len(present)) / float(len(expected)) if expected else 1.0
    if not missing:
        status = "ok"
    elif not present:
        status = "invalid"
    else:
        status = "partial"
    return {
        "schema_version": AGENT_VALIDATION_SCHEMA_VERSION,
        "status": status,
        "required_keys_expected": expected,
        "required_keys_present": present,
        "required_keys_missing": missing,
        "completeness_score": completeness,
    }


def build_strategist_output_artifact(state: Dict[str, Any]) -> Dict[str, Any]:
    avoid_themes, candidate_news_context, decision_status, evidence_log_path, fear_index, global_signal, macro_overlay, market_news_context, market_regime, market_sentiment, negative_factors, news_context, playbook, positive_factors, selected, selected_score_total, strategist_llm, strategist_output, strategy_policy, summary, themes = strategist_market_news_inputs(state=state, facade=_r3_sys.modules[__name__])
    artifact = _base_output(state, agent="strategist", status="blocked" if bool(state.get("strategist_blocked")) else "ok")
    commander_context, confidence, decision_frame, global_sentiment_signal, market_regime_summary, memory_packet_visibility, monitor_entry_policy, news_collection_policy, news_evidence_ranked, policy_fallback_reason, policy_provenance, policy_rationale, policy_source, policy_validation_issues, policy_validation_status, strategist_plan, strategy_detail, theme_source, theme_source_fallback_used, theme_source_reason, theme_source_status, theme_strength, theme_strength_packet, trace_summary = strategist_decision_theme_policy_facts(strategist_output=strategist_output, global_signal=global_signal, macro_overlay=macro_overlay, news_context=news_context, themes=themes, avoid_themes=avoid_themes, market_regime=market_regime, market_sentiment=market_sentiment, playbook=playbook, state=state, market_news_context=market_news_context, candidate_news_context=candidate_news_context, strategy_policy=strategy_policy, facade=_r3_sys.modules[__name__])
    candidate_hypotheses, candidate_symbols_hint, commander_horizon_policy, entry_plan, exit_plan, explanation_fields, fallback_reason, fallback_used, horizon_context, news_evidence_missing, policy_resolution, selected_playbook, strategist_horizon_proposal, strategy_horizon_feedback, strategy_summary, strategy_thesis_text, symbol_plan = strategist_plan_horizon_facts(playbook=playbook, strategist_output=strategist_output, strategist_plan=strategist_plan, strategy_policy=strategy_policy, summary=summary, state=state, news_evidence_ranked=news_evidence_ranked, news_context=news_context, strategist_llm=strategist_llm, commander_context=commander_context, facade=_r3_sys.modules[__name__])
    artifact.update(
        {
            **strategist_artifact_market_playbook_fields(explanation_fields=explanation_fields, fear_index=fear_index, macro_overlay=macro_overlay, market_regime=market_regime, market_sentiment=market_sentiment, news_context=news_context, playbook=playbook, strategist_output=strategist_output, strategy_detail=strategy_detail, strategy_thesis_text=strategy_thesis_text, summary=summary),
            **strategist_artifact_context_frame_fields(avoid_themes=avoid_themes, candidate_news_context=candidate_news_context, decision_frame=decision_frame, decision_status=decision_status, macro_overlay=macro_overlay, market_news_context=market_news_context, market_regime=market_regime, market_sentiment=market_sentiment, negative_factors=negative_factors, news_collection_policy=news_collection_policy, news_context=news_context, playbook=playbook, positive_factors=positive_factors, selected=selected, selected_score_total=selected_score_total, state=state, strategist_llm=strategist_llm, strategist_output=strategist_output, summary=summary, theme_source=theme_source, theme_source_reason=theme_source_reason, theme_source_status=theme_source_status, theme_strength=theme_strength, theme_strength_packet=theme_strength_packet, themes=themes),
            **strategist_artifact_theme_news_fallback_fields(candidate_symbols_hint=candidate_symbols_hint, fallback_reason=fallback_reason, fallback_used=fallback_used, fear_index=fear_index, global_sentiment_signal=global_sentiment_signal, macro_overlay=macro_overlay, news_collection_policy=news_collection_policy, news_evidence_missing=news_evidence_missing, news_evidence_ranked=news_evidence_ranked, strategist_output=strategist_output, theme_source=theme_source, theme_source_fallback_used=theme_source_fallback_used, theme_source_reason=theme_source_reason, theme_source_status=theme_source_status, theme_strength=theme_strength, theme_strength_packet=theme_strength_packet),
            **strategist_artifact_commander_context_fields(commander_context=commander_context, strategist_output=strategist_output),
            **strategist_artifact_horizon_guidance_fields(commander_horizon_policy=commander_horizon_policy, horizon_context=horizon_context, selected_playbook=selected_playbook, strategist_horizon_proposal=strategist_horizon_proposal, strategist_output=strategist_output, strategy_horizon_feedback=strategy_horizon_feedback),
            **strategist_artifact_plan_policy_fields(candidate_hypotheses=candidate_hypotheses, entry_plan=entry_plan, exit_plan=exit_plan, market_regime_summary=market_regime_summary, monitor_entry_policy=monitor_entry_policy, policy_fallback_reason=policy_fallback_reason, policy_provenance=policy_provenance, policy_rationale=policy_rationale, policy_resolution=policy_resolution, policy_source=policy_source, policy_validation_issues=policy_validation_issues, policy_validation_status=policy_validation_status, strategist_output=strategist_output, strategy_summary=strategy_summary, symbol_plan=symbol_plan),
            **strategist_artifact_trace_handoff_feedback_fields(explanation_fields=explanation_fields, policy_resolution=policy_resolution, strategist_output=strategist_output),
            **strategist_artifact_llm_policy_bias_fields(confidence=confidence, policy_resolution=policy_resolution, strategist_output=strategist_output),
            **strategist_artifact_refs_macro_fields(avoid_themes=avoid_themes, candidate_news_context=candidate_news_context, evidence_log_path=evidence_log_path, fear_index=fear_index, global_signal=global_signal, macro_overlay=macro_overlay, market_news_context=market_news_context, memory_packet_visibility=memory_packet_visibility, news_context=news_context, strategist_llm=strategist_llm, strategist_output=strategist_output, summary=summary, themes=themes, trace_summary=trace_summary),
        }
    )
    artifact["validation"] = validate_artifact(artifact)
    return artifact


def build_scanner_output_artifact(state: Dict[str, Any]) -> Dict[str, Any]:
    scanner_output = _dict(state.get("scanner_output"))
    selected = _dict(state.get("selected"))
    selected_candidate = _dict(selected.get("candidate"))
    selected_features = _dict(selected.get("features"))
    ranked = [row for row in list(state.get("ranked_candidates") or []) if isinstance(row, dict)]
    candidate_visibility_limit = _scanner_candidate_visibility_limit(scanner_output)
    visible_ranked = ranked[:candidate_visibility_limit]
    top_ranked_symbols = [str(row.get("symbol") or "") for row in visible_ranked if str(row.get("symbol") or "").strip()]
    pool_meta = _dict(state.get("scanner_candidate_pool"))
    candidate_preview: List[Dict[str, Any]] = []
    for rank, row in enumerate(visible_ranked, start=1):
        compact_features, row_breakdown, row_sources = scanner_row_feature_sources(row=row, candidate_preview=candidate_preview, rank=rank)
    applied_policy_present, critical_negative_factors, critical_positive_factors, margin_vs_second, monitor_entry_policy_summary, playbook, policy_provenance_ref, policy_source, selected_rank, selected_score_breakdown, selected_score_total, selection_summary, symbol = scanner_applied_policy_evidence(selected=selected, scanner_output=scanner_output, top_ranked_symbols=top_ranked_symbols, ranked=ranked, state=state)
    rejection_rows = [row for row in list(state.get("scanner_runner_up_reasons") or []) if isinstance(row, dict)]
    bias_scale, candidate_bias_adjustments, candidate_memory_bias_adjustments, candidate_ranking_table, candidate_selection_reason, commander_memory_application_trace, compatibility_bias, compatibility_components, compatibility_score_post_penalty, compatibility_score_pre_penalty, compatibility_trace, dominant_block_reason, dominant_block_reason_ratio, entry_compatibility_score, expected_monitor_block_reason, pre_adjust_score_total, scanner_bias_applied, scanner_bias_summary, scanner_memory_bias, scanner_memory_bias_applied, scanner_memory_bias_summary, selection_reason_detail, selection_reason_with_bias, soft_penalty = scanner_policy_bias_evidence(symbol=symbol, selected_rank=selected_rank, selected_score_total=selected_score_total, margin_vs_second=margin_vs_second, critical_positive_factors=critical_positive_factors, critical_negative_factors=critical_negative_factors, selection_summary=selection_summary, state=state, candidate_preview=candidate_preview, rejection_rows=rejection_rows, selected=selected, scanner_output=scanner_output, policy_provenance_ref=policy_provenance_ref, candidate_visibility_limit=candidate_visibility_limit, selected_candidate=selected_candidate, facade=_r3_sys.modules[__name__])
    post_adjust_score_total = _safe_float(
        scanner_output.get("post_adjust_score_total")
        if scanner_output.get("post_adjust_score_total") not in (None, "")
        else candidate_selection_reason.get("post_adjust_score_total"),
        selected_score_total,
    )
    quote_data_diagnostic = _dict(scanner_output.get("quote_data_diagnostic") or state.get("scanner_quote_diagnostic"))
    runner_up_symbol = ""
    ranking_rows = [row for row in list(candidate_ranking_table.get("rows") or []) if isinstance(row, dict)]
    if len(ranking_rows) > 1:
        runner_up_symbol = str(ranking_rows[1].get("symbol") or "").strip()
    score_breakdown_by_symbol = {
        str(row.get("symbol") or "").strip(): _dict(row.get("score_breakdown"))
        for row in ranking_rows
        if str(row.get("symbol") or "").strip()
    }
    confidence_by_symbol = {
        str(row.get("symbol") or "").strip(): row.get("confidence")
        for row in ranking_rows
        if str(row.get("symbol") or "").strip()
    }
    risk_score_by_symbol = {
        str(row.get("symbol") or "").strip(): row.get("risk_score")
        for row in ranking_rows
        if str(row.get("symbol") or "").strip()
    }
    fallback_reason = _clip(
        pool_meta.get("fallback_reason")
        or scanner_output.get("fallback_reason")
        or ("backfill_used" if bool(pool_meta.get("backfill_used")) else ""),
        max_len=180,
    )
    fallback_used = bool(fallback_reason)
    trace_summary = _build_scanner_trace_summary(
        symbol=symbol,
        selected_rank=selected_rank,
        universe_size=_safe_int(scanner_output.get("candidate_pool_size") or scanner_output.get("candidate_count")) or _safe_int(pool_meta.get("candidate_pool_after_filter") or len(ranked)),
        selected_score_total=selected_score_total,
        margin_vs_second=margin_vs_second,
        selected_score_breakdown=selected_score_breakdown,
        selected=selected,
        candidate_preview=candidate_preview,
        selection_summary=selection_summary,
        scanner_bias_applied=scanner_bias_applied,
        scanner_bias_summary=scanner_bias_summary,
    )
    artifact = _base_output(state, agent="scanner", symbol=symbol)
    artifact.update(
        {
            **scanner_artifact_pool_ranking_fields(candidate_preview=candidate_preview, candidate_ranking_table=candidate_ranking_table, candidate_selection_reason=candidate_selection_reason, pool_meta=pool_meta, ranked=ranked, scanner_output=scanner_output, selected_rank=selected_rank, selected_score_breakdown=selected_score_breakdown, selected_score_total=selected_score_total, symbol=symbol),
            **scanner_artifact_policy_compatibility_fields(applied_policy_present=applied_policy_present, bias_scale=bias_scale, compatibility_bias=compatibility_bias, compatibility_components=compatibility_components, compatibility_score_post_penalty=compatibility_score_post_penalty, compatibility_score_pre_penalty=compatibility_score_pre_penalty, dominant_block_reason=dominant_block_reason, dominant_block_reason_ratio=dominant_block_reason_ratio, entry_compatibility_score=entry_compatibility_score, expected_monitor_block_reason=expected_monitor_block_reason, monitor_entry_policy_summary=monitor_entry_policy_summary, playbook=playbook, policy_source=policy_source, runner_up_symbol=runner_up_symbol, soft_penalty=soft_penalty),
            **scanner_artifact_bias_trace_fields(candidate_bias_adjustments=candidate_bias_adjustments, candidate_memory_bias_adjustments=candidate_memory_bias_adjustments, commander_memory_application_trace=commander_memory_application_trace, compatibility_trace=compatibility_trace, post_adjust_score_total=post_adjust_score_total, pre_adjust_score_total=pre_adjust_score_total, scanner_bias_applied=scanner_bias_applied, scanner_bias_summary=scanner_bias_summary, scanner_memory_bias=scanner_memory_bias, scanner_memory_bias_applied=scanner_memory_bias_applied, scanner_memory_bias_summary=scanner_memory_bias_summary, scanner_output=scanner_output),
            **scanner_artifact_selection_trace_fields(confidence_by_symbol=confidence_by_symbol, fallback_reason=fallback_reason, fallback_used=fallback_used, quote_data_diagnostic=quote_data_diagnostic, ranking_rows=ranking_rows, rejection_rows=rejection_rows, risk_score_by_symbol=risk_score_by_symbol, scanner_output=scanner_output, score_breakdown_by_symbol=score_breakdown_by_symbol, selection_reason_detail=selection_reason_detail, selection_reason_with_bias=selection_reason_with_bias, selection_summary=selection_summary, state=state, trace_summary=trace_summary),
            **scanner_artifact_policy_guard_fields(scanner_output=scanner_output),
            **scanner_artifact_refs_preview_fields(candidate_preview=candidate_preview, scanner_output=scanner_output, selected=selected, selected_candidate=selected_candidate, selected_features=selected_features, symbol=symbol, top_ranked_symbols=top_ranked_symbols),
        }
    )
    artifact["validation"] = validate_artifact(artifact)
    return artifact


def build_monitor_output_artifact(state: Dict[str, Any]) -> Dict[str, Any]:
    entry_detail, entry_info, exit_detail, exit_info, monitor, monitor_focus_state, monitor_output, scanner_selected_snapshot, selected, trace_sources, transition = monitor_state_surface_sources(state=state)

    def _first_trace_dict(key: str) -> Dict[str, Any]:
        for source in trace_sources:
            value = source.get(key)
            if isinstance(value, dict) and value:
                return dict(value)
        return {}

    def _first_trace_list(key: str) -> List[Any]:
        for source in trace_sources:
            value = source.get(key)
            if isinstance(value, list) and value:
                return list(value)
        return []

    def _first_trace_text(key: str) -> str:
        for source in trace_sources:
            value = source.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ""

    def _first_trace_bool(key: str) -> Any:
        for source in trace_sources:
            value = source.get(key)
            if isinstance(value, bool):
                return value
        return None

    def _first_trace_value(key: str) -> Any:
        for source in trace_sources:
            if key not in source:
                continue
            value = source.get(key)
            if value not in (None, "", [], {}):
                return value
        return None

    exit_vs_strategy_intent, monitor_no_trade_surface, policy_trace = monitor_no_trade_policy_trace(_first_trace_dict=_first_trace_dict, _first_trace_text=_first_trace_text, _first_trace_list=_first_trace_list, _first_trace_bool=_first_trace_bool)
    if not monitor_no_trade_surface:
        commander_decision = _dict(state.get("commander_decision"))
        monitor_no_trade_surface = build_monitor_no_trade_surface(
            entry_info,
            final_decision=str(monitor_output.get("intent_side") or "NOOP").strip().upper() or "WAIT",
            buy_submitted=str(monitor_output.get("intent_side") or "").strip().upper() == "BUY",
            guard_blocked=bool(entry_info.get("guard_blocked")),
            guard_reason=entry_info.get("guard_reason"),
            commander_no_trade_reason_code=commander_decision.get("no_trade_reason_code"),
        )
    entry_blocker_surface, entry_candidate_cascade, first_intent, intent_side, intents, monitor_focus_context, open_position_count, scanner_monitor_handoff, symbol, thresholds, watch_axes = monitor_entry_cascade_handoff(_first_trace_dict=_first_trace_dict, monitor_no_trade_surface=monitor_no_trade_surface, entry_info=entry_info, scanner_selected_snapshot=scanner_selected_snapshot, selected=selected, state=state, monitor_output=monitor_output, _first_trace_list=_first_trace_list, monitor=monitor, exit_info=exit_info, monitor_focus_state=monitor_focus_state, facade=_r3_sys.modules[__name__])
    if not monitor_focus_context:
        monitor_focus_context = monitor_focus_context_projection(monitor_output=monitor_output, entry_info=entry_info, selected=selected, scanner_monitor_handoff=scanner_monitor_handoff, exit_info=exit_info, open_position_count=open_position_count, monitor=monitor, monitor_focus_context=monitor_focus_context)[0]
    blocked_rules, decision_action, decision_phase, decision_reason_chain, decision_status, entry_chart_structure_features, entry_minute_refetch_attempted, entry_minute_refetch_failure_detail, entry_minute_refetch_failure_reason, entry_minute_refetch_runner_source, entry_minute_refetch_succeeded, entry_minute_source_present, entry_minute_source_used, entry_policy_alignment_summary, entry_policy_interpreter_trace, evidence_quality, feature_source, missing_inputs, posture, price_source, primary_reason_code, secondary_reason_codes, threshold_snapshot, triggered_rules = monitor_decision_rule_evidence(exit_info=exit_info, entry_info=entry_info, state=state, transition=transition, monitor_output=monitor_output, entry_detail=entry_detail, symbol=symbol, intent_side=intent_side, open_position_count=open_position_count, exit_detail=exit_detail, thresholds=thresholds, monitor=monitor, _first_trace_value=_first_trace_value, facade=_r3_sys.modules[__name__])
    commander_memory_application_trace, decision_summary, market_snapshot_refs, monitor_memory_bias, monitor_memory_bias_applied, monitor_memory_bias_deltas, monitor_memory_bias_exit_applied, monitor_memory_bias_exit_deltas, monitor_memory_bias_hold_applied, monitor_memory_bias_hold_deltas, monitor_memory_bias_summary, signal_snapshot = monitor_memory_bias_application(_first_trace_value=_first_trace_value, threshold_snapshot=threshold_snapshot, policy_trace=policy_trace, _first_trace_dict=_first_trace_dict, entry_info=entry_info, exit_info=exit_info, decision_phase=decision_phase, missing_inputs=missing_inputs, primary_reason_code=primary_reason_code, symbol=symbol, price_source=price_source, feature_source=feature_source, selected=selected, facade=_r3_sys.modules[__name__])
    artifact = _base_output(state, agent="monitor", symbol=symbol)
    artifact.update(
        {
            **monitor_artifact_decision_fields(decision_action=decision_action, decision_phase=decision_phase, decision_status=decision_status, decision_summary=decision_summary, exit_info=exit_info, exit_vs_strategy_intent=exit_vs_strategy_intent, monitor_output=monitor_output, open_position_count=open_position_count, primary_reason_code=primary_reason_code, secondary_reason_codes=secondary_reason_codes, state=state, symbol=symbol, thresholds=thresholds),
            **monitor_artifact_no_trade_fields(monitor_no_trade_surface=monitor_no_trade_surface),
            **monitor_artifact_handoff_focus_fields(entry_blocker_surface=entry_blocker_surface, entry_candidate_cascade=entry_candidate_cascade, monitor_focus_context=monitor_focus_context, scanner_monitor_handoff=scanner_monitor_handoff, threshold_snapshot=threshold_snapshot),
            **monitor_artifact_policy_memory_fields(commander_memory_application_trace=commander_memory_application_trace, entry_info=entry_info, monitor_memory_bias=monitor_memory_bias, monitor_memory_bias_applied=monitor_memory_bias_applied, monitor_memory_bias_deltas=monitor_memory_bias_deltas, monitor_memory_bias_exit_applied=monitor_memory_bias_exit_applied, monitor_memory_bias_exit_deltas=monitor_memory_bias_exit_deltas, monitor_memory_bias_hold_applied=monitor_memory_bias_hold_applied, monitor_memory_bias_hold_deltas=monitor_memory_bias_hold_deltas, monitor_memory_bias_summary=monitor_memory_bias_summary, policy_trace=policy_trace),
            **monitor_artifact_signal_entry_fields(entry_chart_structure_features=entry_chart_structure_features, entry_info=entry_info, entry_minute_refetch_attempted=entry_minute_refetch_attempted, entry_minute_refetch_failure_detail=entry_minute_refetch_failure_detail, entry_minute_refetch_failure_reason=entry_minute_refetch_failure_reason, entry_minute_refetch_runner_source=entry_minute_refetch_runner_source, entry_minute_refetch_succeeded=entry_minute_refetch_succeeded, entry_minute_source_present=entry_minute_source_present, entry_minute_source_used=entry_minute_source_used, entry_policy_alignment_summary=entry_policy_alignment_summary, entry_policy_interpreter_trace=entry_policy_interpreter_trace, market_snapshot_refs=market_snapshot_refs, policy_trace=policy_trace, signal_snapshot=signal_snapshot),
            **monitor_artifact_trace_evaluation_fields(blocked_rules=blocked_rules, decision_reason_chain=decision_reason_chain, entry_info=entry_info, evidence_quality=evidence_quality, exit_info=exit_info, exit_vs_strategy_intent=exit_vs_strategy_intent, first_intent=first_intent, intents=intents, missing_inputs=missing_inputs, monitor_output=monitor_output, policy_trace=policy_trace, posture=posture, thresholds=thresholds, triggered_rules=triggered_rules, watch_axes=watch_axes, facade=_r3_sys.modules[__name__]),
            **monitor_artifact_price_exit_metric_fields(exit_info=exit_info, feature_source=feature_source, price_source=price_source),
            **monitor_artifact_pnl_hold_exit_fields(exit_info=exit_info, watch_axes=watch_axes),
        }
    )
    artifact["validation"] = validate_artifact(artifact)
    return artifact


def build_supervisor_output_artifact(
    state: Dict[str, Any],
    *,
    order: Dict[str, Any],
    allowed: bool,
    reason: str,
    details: Dict[str, Any] | None = None,
    strategy_policy_summary: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    symbol = str(order.get("symbol") or order.get("stk_cd") or "").strip()
    artifact = _base_output(state, agent="supervisor", symbol=symbol, status="ok" if allowed else "blocked")
    artifact.update(
        {
            "invoked_agents": ["supervisor"],
            "intent_id": str(order.get('intent_id') or ''),
            "command": str(order.get("action") or "").strip().upper(),
            "decision": "approve" if allowed else "block",
            "approval_result": bool(allowed),
            "reason": _clip(reason, max_len=220),
            "blocked_allowed_details": _dict(details),
            "supervisor_allow": bool(allowed),
            "verdict": "approve" if allowed else "block",
            "supervisor_reason": _clip(reason, max_len=220),
            "guard_reason": _clip(reason, max_len=220),
            "action": str(order.get("action") or "").strip().upper(),
            "symbol": symbol,
            "order_request_summary": {
                "action": str(order.get("action") or "").strip().upper(),
                "symbol": symbol,
                "qty": _safe_int(order.get("qty")),
                "order_type": _clip(order.get("order_type"), max_len=32),
            },
            "strategy_policy_summary": _dict(strategy_policy_summary),
        }
    )
    artifact["validation"] = validate_artifact(artifact)
    return artifact


def build_executor_output_artifact(
    state: Dict[str, Any],
    *,
    execution: Dict[str, Any],
    order: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    execution = _dict(execution)
    order = _dict(order)
    execution_payload = _dict(execution.get("payload"))
    response_payload = _dict(execution_payload.get("response_payload"))
    quote_snapshot = _dict(execution.get("quote_snapshot"))
    symbol = str(execution.get("symbol") or order.get("symbol") or "").strip()
    if "execution_ok" in execution:
        execution_ok = bool(execution.get("execution_ok"))
    elif "ok" in execution:
        execution_ok = bool(execution.get("ok"))
    else:
        execution_ok = bool(execution.get("allowed"))
    artifact = _base_output(
        state,
        agent="executor",
        symbol=symbol,
        status="ok" if bool(execution.get("allowed")) and execution_ok else "error",
    )
    artifact.update(
        {
            "action": str(execution.get("action") or order.get("action") or "").strip().upper(),
            "allowed": bool(execution.get("allowed")),
            "symbol": symbol,
            "qty": _safe_int(order.get("qty") or execution.get("qty")),
            "status": _clip(
                execution.get("status")
                or execution_payload.get("status")
                or response_payload.get("return_msg"),
                max_len=80,
            ),
            "reason": _clip(execution.get("reason"), max_len=220),
            "broker_env": _clip(execution.get("broker_env") or execution_payload.get("broker_env"), max_len=32),
            "effective_mode": _clip(execution.get("effective_mode") or execution_payload.get("effective_mode"), max_len=64),
            "broker_message": _clip(
                execution.get("broker_message")
                or execution_payload.get("broker_message")
                or response_payload.get("return_msg"),
                max_len=200,
            ),
            "ord_no": _clip(
                execution.get("ord_no")
                or execution.get("order_id")
                or execution_payload.get("ord_no")
                or execution_payload.get("order_id")
                or response_payload.get("ord_no")
                or response_payload.get("order_id"),
                max_len=64,
            ),
            "execution_ok": execution_ok,
            # Phase 1 Step 5B: additive BrokerOutcome provenance. `execution_ok`
            # stays a plain bool for backward compatibility; `broker_outcome`
            # lets downstream consumers tell UNKNOWN (broker acceptance
            # unconfirmed, must not be treated as a firm reject) apart from a
            # true NOT_SENT/REJECTED.
            "broker_outcome": _clip(execution.get("broker_outcome"), max_len=32),
            "intent_id": str(execution.get('intent_id') or order.get('intent_id') or ''),
            "intent_claim": _dict(execution.get('intent_claim')),
            "intent_state_persistence_error": str(execution.get('intent_state_persistence_error') or ''),
            "submission_phase": _clip(execution.get("submission_phase"), max_len=64),
            "submission_attempts": _safe_int(execution.get("submission_attempts")),
            "exception_type": _clip(execution.get("exception_type"), max_len=120),
            "reconciliation_required": bool(execution.get("reconciliation_required")),
            "broker_reference_missing": bool(execution.get("broker_reference_missing")),
            "quote_snapshot": quote_snapshot,
            "opening_alpha_execution_price_guard": _dict(execution.get("opening_alpha_execution_price_guard")),
            "best_bid": _safe_float(execution.get("best_bid") if execution.get("best_bid") not in (None, "") else quote_snapshot.get("best_bid")),
            "best_ask": _safe_float(execution.get("best_ask") if execution.get("best_ask") not in (None, "") else quote_snapshot.get("best_ask")),
            "spread_bps": _safe_float(execution.get("spread_bps") if execution.get("spread_bps") not in (None, "") else quote_snapshot.get("spread_bps")),
            "order_request_summary": {
                "action": str(order.get("action") or execution.get("action") or "").strip().upper(),
                "symbol": symbol,
                "qty": _safe_int(order.get("qty") or execution.get("qty")),
                "order_type": _clip(order.get("order_type"), max_len=32),
                "best_bid": _safe_float(execution.get("best_bid") if execution.get("best_bid") not in (None, "") else quote_snapshot.get("best_bid")),
                "best_ask": _safe_float(execution.get("best_ask") if execution.get("best_ask") not in (None, "") else quote_snapshot.get("best_ask")),
                "spread_bps": _safe_float(execution.get("spread_bps") if execution.get("spread_bps") not in (None, "") else quote_snapshot.get("spread_bps")),
            },
            "execution_enabled": bool(execution.get("allowed")),
            "approval_mode": _clip(execution.get("approval_mode"), max_len=32),
            "broker_result": {
                "status": _clip(
                    execution.get("status")
                    or execution_payload.get("status")
                    or response_payload.get("return_msg"),
                    max_len=80,
                ),
                "broker_message": _clip(
                    execution.get("broker_message")
                    or execution_payload.get("broker_message")
                    or response_payload.get("return_msg"),
                    max_len=200,
                ),
                "ord_no": _clip(
                    execution.get("ord_no")
                    or execution.get("order_id")
                    or execution_payload.get("ord_no")
                    or execution_payload.get("order_id")
                    or response_payload.get("ord_no")
                    or response_payload.get("order_id"),
                    max_len=64,
                ),
                "effective_mode": _clip(execution.get("effective_mode") or execution_payload.get("effective_mode"), max_len=64),
                "broker_env": _clip(execution.get("broker_env") or execution_payload.get("broker_env"), max_len=32),
            },
            "final_execution_status": _clip(
                execution.get("status")
                or execution_payload.get("status")
                or response_payload.get("return_msg"),
                max_len=80,
            ) or ("allowed" if execution.get("allowed") else "blocked"),
            "failure_reason": _clip(execution.get("reason"), max_len=220),
            "strategy_policy_summary": _dict(execution.get("strategy_policy_summary")),
        }
    )
    artifact["validation"] = validate_artifact(artifact)
    return artifact


def _build_commander_shadow_artifact_summary(
    state: Dict[str, Any],
    *,
    mode: str,
    phase: str,
    path: str,
    status: str,
    reason: str = "",
) -> Dict[str, Any]:
    try:
        return build_commander_shadow_artifact(
            state,
            mode=str(mode or ""),
            phase=str(phase or ""),
            path=str(path or ""),
            status=str(status or "ok"),
            reason=str(reason or ""),
        )
    except Exception:
        return {}


def build_commander_output_artifact(
    state: Dict[str, Any],
    *,
    mode: str,
    phase: str,
    path: str,
    status: str,
    reason: str = "",
) -> Dict[str, Any]:
    allowed_playbooks, banned_playbooks, commander_decision, commander_market_regime, commander_risk_mode, commander_session_bias, cooldown_applied, cooldown_until_epoch, decision_frame, handoff_instruction, open_symbols, phase_text, portfolio_snapshot, positions, preflight, resilience, route_reason_codes, runtime_fast_path, runtime_plan, selected_route, shadow_assessment, strategist_blocked, strategist_cache_used, strategist_output = commander_route_runtime_facts(state=state, mode=mode, phase=phase, path=path, status=status, reason=reason, facade=_r3_sys.modules[__name__])
    decision_summary, llm_invocation_policy, monitor_mission, post_scanner_refresh_context, post_scanner_refresh_reason, post_scanner_refresh_requested, runtime_cache_reuse_context, runtime_cache_reuse_reason, runtime_refresh_context, runtime_refresh_reason, runtime_refresh_requested, scanner_mission, shadow_alignment, shadow_assessment_summary, shadow_reason_code, shadow_runtime, source_priority, strategist_cache_preference_context, strategist_cache_preference_reason, strategist_cache_preferred, strategist_fallback_used, strategist_refresh_context, strategist_refresh_reason, strategist_refresh_requested = commander_decision_refresh_facts(commander_decision=commander_decision, reason=reason, decision_frame=decision_frame, state=state, shadow_assessment=shadow_assessment, runtime_fast_path=runtime_fast_path, strategist_cache_used=strategist_cache_used)
    applied_policy, applied_policy_source_chain, commander_applied_policy_summary, commander_horizon_policy, horizon_context, llm_policy_source, override_action, override_context, override_reason, override_triggered, policy_default_filled_fields, policy_fallback_reason, policy_fallback_used, policy_partial_normalized, policy_source, policy_sources, policy_validation_invalid_fields, policy_validation_missing_fields, policy_validation_status, reporter_feedback_mode, reporter_feedback_mode_reason, reporter_feedback_mode_source, reporter_feedback_semantics, strategist_runtime_policy_source = commander_applied_policy_provenance(commander_decision=commander_decision, state=state)
    llm_execution_profile_source = _clip(commander_decision.get("llm_execution_profile_source"), max_len=80)
    reporter_policy_source = _clip(commander_decision.get("reporter_policy_source"), max_len=80)
    monitor_policy_source = _clip(commander_decision.get("monitor_policy_source"), max_len=80)
    scanner_policy_source = _clip(commander_decision.get("scanner_policy_source"), max_len=80)
    execution_policy_source = _clip(commander_decision.get("execution_policy_source"), max_len=80)
    route_observability = (
        _dict(state.get("commander_route_observability"))
        or build_commander_route_observability_surface(
            selected_route=selected_route,
            route_reason=decision_summary,
            commander_decision=commander_decision,
            runtime_fast_path=runtime_fast_path,
            resilience=resilience,
            runtime_status=state.get("runtime_status"),
            runtime_transition=state.get("runtime_transition"),
        )
    )
    observations = {
        **_dict(commander_decision.get("observations")),
        **_commander_shadow_observations(state, path=path),
    }
    
    # Determine actual invocation and strategy source for explicit ownership
    actual_strategist_invocation = shadow_runtime.get("strategist_executed")
    if actual_strategist_invocation is None:
        actual_strategist_invocation = not strategist_cache_used and selected_route not in ("monitor_only", "blocked")
    actual_strategy_source = "cached_strategist" if strategist_cache_used else ("fresh_strategist" if actual_strategist_invocation else "none")

    artifact = _base_output(state, agent="commander", status=status or "ok")
    artifact.update(
        {
            **commander_artifact_route_fields(actual_strategist_invocation=actual_strategist_invocation, actual_strategy_source=actual_strategy_source, cooldown_applied=cooldown_applied, cooldown_until_epoch=cooldown_until_epoch, decision_frame=decision_frame, mode=mode, open_symbols=open_symbols, path=path, phase=phase, phase_text=phase_text, portfolio_snapshot=portfolio_snapshot, positions=positions, preflight=preflight, reason=reason, resilience=resilience, route_reason_codes=route_reason_codes, runtime_plan=runtime_plan, selected_route=selected_route, state=state, strategist_blocked=strategist_blocked, strategist_cache_used=strategist_cache_used, facade=_r3_sys.modules[__name__]),
            **commander_artifact_decision_fields(allowed_playbooks=allowed_playbooks, banned_playbooks=banned_playbooks, commander_decision=commander_decision, commander_market_regime=commander_market_regime, commander_risk_mode=commander_risk_mode, commander_session_bias=commander_session_bias, decision_summary=decision_summary, llm_invocation_policy=llm_invocation_policy, monitor_mission=monitor_mission, route_observability=route_observability, scanner_mission=scanner_mission, strategist_output=strategist_output),
            **commander_artifact_shadow_refresh_fields(commander_decision=commander_decision, post_scanner_refresh_context=post_scanner_refresh_context, post_scanner_refresh_reason=post_scanner_refresh_reason, post_scanner_refresh_requested=post_scanner_refresh_requested, runtime_cache_reuse_context=runtime_cache_reuse_context, runtime_cache_reuse_reason=runtime_cache_reuse_reason, runtime_refresh_context=runtime_refresh_context, runtime_refresh_reason=runtime_refresh_reason, runtime_refresh_requested=runtime_refresh_requested, shadow_alignment=shadow_alignment, shadow_assessment=shadow_assessment, shadow_assessment_summary=shadow_assessment_summary, shadow_reason_code=shadow_reason_code, source_priority=source_priority, strategist_cache_preference_context=strategist_cache_preference_context, strategist_cache_preference_reason=strategist_cache_preference_reason, strategist_cache_preferred=strategist_cache_preferred, strategist_fallback_used=strategist_fallback_used, strategist_refresh_context=strategist_refresh_context, strategist_refresh_reason=strategist_refresh_reason, strategist_refresh_requested=strategist_refresh_requested),
            **commander_artifact_policy_fields(applied_policy=applied_policy, applied_policy_source_chain=applied_policy_source_chain, commander_applied_policy_summary=commander_applied_policy_summary, commander_horizon_policy=commander_horizon_policy, execution_policy_source=execution_policy_source, horizon_context=horizon_context, llm_execution_profile_source=llm_execution_profile_source, llm_policy_source=llm_policy_source, monitor_policy_source=monitor_policy_source, override_action=override_action, override_context=override_context, override_reason=override_reason, override_triggered=override_triggered, policy_default_filled_fields=policy_default_filled_fields, policy_fallback_reason=policy_fallback_reason, policy_fallback_used=policy_fallback_used, policy_partial_normalized=policy_partial_normalized, policy_source=policy_source, policy_sources=policy_sources, policy_validation_invalid_fields=policy_validation_invalid_fields, policy_validation_missing_fields=policy_validation_missing_fields, policy_validation_status=policy_validation_status, reporter_feedback_mode=reporter_feedback_mode, reporter_feedback_mode_reason=reporter_feedback_mode_reason, reporter_feedback_mode_source=reporter_feedback_mode_source, reporter_feedback_semantics=reporter_feedback_semantics, reporter_policy_source=reporter_policy_source, scanner_policy_source=scanner_policy_source, strategist_runtime_policy_source=strategist_runtime_policy_source),
            **commander_artifact_observability_fields(commander_decision=commander_decision, decision_frame=decision_frame, handoff_instruction=handoff_instruction, mode=mode, observations=observations, path=path, phase=phase, policy_source=policy_source, preflight=preflight, reason=reason, route_observability=route_observability, runtime_fast_path=runtime_fast_path, runtime_plan=runtime_plan, state=state, status=status, strategist_cache_used=strategist_cache_used),
        }
    )
    artifact["validation"] = validate_artifact(artifact)
    return artifact


def _commander_shadow_has_open_order(state: Dict[str, Any]) -> Any:
    monitor = _dict(state.get("monitor"))
    order_lifecycle = _dict(monitor.get("order_lifecycle"))
    if not order_lifecycle:
        return None
    stage = _clip(order_lifecycle.get("stage"), max_len=40).lower()
    terminal = order_lifecycle.get("terminal")
    if stage:
        return stage not in {"filled", "cancelled", "canceled", "rejected"} and terminal is not True
    if terminal in (True, False):
        return not bool(terminal)
    return None


def _commander_shadow_actual_runtime(state: Dict[str, Any], *, path: str) -> Dict[str, Any]:
    shadow_runtime = _dict(state.get("commander_shadow_runtime"))
    strategist_llm = _dict(state.get("strategist_llm"))
    monitor_output = _dict(state.get("monitor_output"))
    monitor_action = _dict(state.get("monitor_action_decision"))
    execution = _dict(state.get("execution"))
    packet = _dict(state.get("decision_packet"))
    packet_intent = _dict(packet.get("intent"))
    runtime_fast_path = _dict(state.get("runtime_fast_path"))

    strategist_executed_raw = shadow_runtime.get("strategist_executed")
    strategist_executed = strategist_executed_raw if isinstance(strategist_executed_raw, bool) else None
    strategist_called_raw = shadow_runtime.get("strategist_called")
    strategist_called = strategist_called_raw if isinstance(strategist_called_raw, bool) else strategist_executed
    llm_called_raw = shadow_runtime.get("llm_called_by_strategist")
    if isinstance(llm_called_raw, bool):
        llm_called = llm_called_raw
    else:
        llm_called = None
        llm_status = _clip(strategist_llm.get("status") or strategist_llm.get("llm_status"), max_len=40).lower()
        if strategist_executed is True:
            llm_called = bool(
                llm_status not in {"", "disabled"}
                or _clip(strategist_llm.get("prompt_ref"), max_len=40)
                or _clip(strategist_llm.get("response_ref"), max_len=40)
            )
    runtime_path = _clip(path, max_len=80)
    selected_route = "cached_strategist" if "cached" in str(runtime_path or "") else ""
    used_cached_strategist = bool(shadow_runtime.get("used_cached_strategist"))
    if selected_route == "cached_strategist":
        if strategist_executed is None:
            strategist_executed = False
        if strategist_called is None:
            strategist_called = False
        if llm_called is None:
            llm_called = False
    if selected_route == "cached_strategist" and strategist_executed is False and llm_called is False:
        used_cached_strategist = True
        strategist_called = False
    elif strategist_called is None and llm_called is True:
        strategist_called = True

    monitor_decision = _clip(
        shadow_runtime.get("monitor_decision")
        or monitor_action.get("decision")
        or monitor_output.get("intent_side"),
        max_len=24,
    ).upper()
    if monitor_decision == "NOOP":
        monitor_decision = "WAIT"

    executor_action = _clip(
        shadow_runtime.get("executor_action")
        or _dict(execution.get("order")).get("action")
        or packet_intent.get("action"),
        max_len=24,
    ).upper()
    executor_status = _clip(
        shadow_runtime.get("executor_status")
        or execution.get("reason")
        or _dict(execution.get("payload")).get("broker_message")
        or execution.get("ok_source"),
        max_len=80,
    )
    post_scanner_refresh_requested = bool(shadow_runtime.get("post_scanner_refresh_requested"))
    post_scanner_refresh_reason = _clip(shadow_runtime.get("post_scanner_refresh_reason"), max_len=80)
    if not post_scanner_refresh_requested and _clip(runtime_fast_path.get("reason"), max_len=80) == "post_scanner_selected_symbol_refresh":
        post_scanner_refresh_requested = True
        post_scanner_refresh_reason = _clip(runtime_fast_path.get("strategist_refresh_reason"), max_len=80)

    return {
        "strategist_executed": strategist_executed,
        "strategist_called": strategist_called,
        "llm_called_by_strategist": llm_called,
        "used_cached_strategist": used_cached_strategist,
        "pre_buy_refresh_requested": bool(shadow_runtime.get("pre_buy_refresh_requested")),
        "pre_buy_refresh_reason": _clip(shadow_runtime.get("pre_buy_refresh_reason"), max_len=80),
        "post_scanner_refresh_requested": post_scanner_refresh_requested,
        "post_scanner_refresh_reason": post_scanner_refresh_reason,
        "monitor_decision": monitor_decision or "",
        "executor_action": executor_action or "",
        "executor_status": executor_status,
        "runtime_path": runtime_path,
    }


def _commander_shadow_observations(state: Dict[str, Any], *, path: str) -> Dict[str, Any]:
    shadow_runtime = _dict(state.get("commander_shadow_runtime"))
    strategist_llm = _dict(state.get("strategist_llm"))
    strategist_output = _dict(state.get("strategist_output"))
    selected = _dict(state.get("selected"))
    portfolio_snapshot = _dict(state.get("portfolio_snapshot"))
    positions = [row for row in list(portfolio_snapshot.get("positions") or []) if isinstance(row, dict)]
    risk_context = _dict(state.get("risk_context"))
    monitor = _dict(state.get("monitor"))
    runtime_fast_path = _dict(state.get("runtime_fast_path"))
    stress_flags = _listify(_dict(strategist_output.get("macro_stress_overlay")).get("stress_flags"), limit=6, max_len=60)
    post_scanner_refresh_requested = bool(shadow_runtime.get("post_scanner_refresh_requested"))
    post_scanner_refresh_reason = _clip(shadow_runtime.get("post_scanner_refresh_reason"), max_len=80)
    post_scanner_refresh_selected_symbol = _clip(_dict(shadow_runtime.get("post_scanner_refresh_context")).get("selected_symbol"), max_len=32)
    if not post_scanner_refresh_requested and _clip(runtime_fast_path.get("reason"), max_len=80) == "post_scanner_selected_symbol_refresh":
        post_scanner_refresh_requested = True
        post_scanner_refresh_reason = _clip(runtime_fast_path.get("strategist_refresh_reason"), max_len=80)
        post_scanner_refresh_selected_symbol = _clip(runtime_fast_path.get("selected_symbol"), max_len=32)

    score_total = selected.get("score_total")
    if score_total in (None, ""):
        score_total = selected.get("score")
    signal_strength = score_total
    if signal_strength in (None, ""):
        signal_strength = selected.get("confidence")

    retry_count_estimate = _safe_int(shadow_runtime.get("retry_count_estimate"), -1)
    if retry_count_estimate < 0:
        retry_count_estimate = max(0, _safe_int(strategist_llm.get("attempts"), 1) - 1)

    position_state = "open_position" if len(positions) > 0 else "flat"
    if "monitor_only" in str(path or ""):
        position_state = "open_position_monitor_only" if len(positions) > 0 else position_state

    return {
        "market_changed": shadow_runtime.get("market_changed"),
        "signal_strength": signal_strength,
        "risk_score": selected.get("risk_score") if selected.get("risk_score") not in (None, "") else risk_context.get("score"),
        "capital_available_for_sizing": risk_context.get("capital_available_for_sizing"),
        "cash_truth_source": _clip(risk_context.get("cash_truth_source"), max_len=80),
        "cash_truth_available": risk_context.get("cash_truth_available"),
        "broker_orderable_amount": risk_context.get("broker_orderable_amount"),
        "broker_withdrawable_cash": risk_context.get("broker_withdrawable_cash"),
        "broker_deposit": risk_context.get("broker_deposit"),
        "post_scanner_refresh_requested": post_scanner_refresh_requested,
        "post_scanner_refresh_reason": post_scanner_refresh_reason,
        "post_scanner_refresh_selected_symbol": post_scanner_refresh_selected_symbol,
        "macro_stress": float(len(stress_flags)) if stress_flags else (1.0 if bool(_dict(strategist_output.get("macro_stress_overlay")).get("active")) else 0.0),
        "last_llm_status": _clip(strategist_llm.get("status") or strategist_output.get("llm_frame_status"), max_len=40),
        "retry_count_estimate": int(max(0, retry_count_estimate)),
        "position_state": position_state,
        "has_open_order": _commander_shadow_has_open_order(state),
        "runtime_fast_path_reason": _clip(runtime_fast_path.get("reason"), max_len=80),
        "repeated_same_context": shadow_runtime.get("repeated_same_context"),
    }


def _gate_pass(metrics: Dict[str, Any], passed_checks: List[str], failed_checks: List[str], key: str) -> Any:
    if key in metrics:
        value = metrics.get(key)
        if isinstance(value, bool):
            return value
    if key in passed_checks:
        return True
    if key in failed_checks:
        return False
    return None


def _score_from_checks(*, passed_checks: List[str], failed_checks: List[str], fallback: Any) -> Any:
    try:
        if fallback not in (None, ""):
            return round(float(fallback), 4)
    except Exception:
        pass
    total = len(passed_checks) + len(failed_checks)
    if total <= 0:
        return None
    return round(float(len(passed_checks)) / float(total), 4)


def _commander_shadow_monitor_gate_details(state: Dict[str, Any]) -> Dict[str, Any]:
    monitor_entry = _dict(state.get("monitor_entry"))
    monitor_output = _dict(state.get("monitor_output"))
    metrics = _dict(monitor_entry.get("metrics"))
    thresholds = _dict(monitor_entry.get("thresholds"))
    passed_checks = [str(x or "").strip() for x in list(monitor_entry.get("passed_checks") or []) if str(x or "").strip()]
    failed_checks = [str(x or "").strip() for x in list(monitor_entry.get("failed_checks") or []) if str(x or "").strip()]
    pullback_flags = [key for key in ("pullback_ok", "pullback_mature", "pullback_not_too_deep") if key in metrics]
    pullback_values = [bool(metrics.get(key)) for key in pullback_flags if isinstance(metrics.get(key), bool)]

    pullback_passed: Any = None
    if pullback_values:
        pullback_passed = all(pullback_values)
    elif "pullback_ok" in passed_checks:
        pullback_passed = True
    elif "pullback_ok" in failed_checks:
        pullback_passed = False

    entry_block_reason = _clip(
        monitor_entry.get("guard_reason")
        or monitor_entry.get("reason")
        or monitor_output.get("entry_exit_reason"),
        max_len=180,
    )
    observed_features = {
        "price": metrics.get("price") if metrics.get("price") not in (None, "") else metrics.get("current_price"),
        "current_price": metrics.get("current_price"),
        "minute_source_present": metrics.get("minute_source_present"),
        "minute_source_used": metrics.get("minute_source_used"),
        "latest_candle_ts": metrics.get("latest_candle_ts"),
        "minute_snapshot_age_minutes": metrics.get("minute_snapshot_age_minutes"),
        "minute_snapshot_was_stale": metrics.get("minute_snapshot_was_stale"),
        "minute_refetch_attempted": metrics.get("minute_refetch_attempted"),
        "minute_refetch_succeeded": metrics.get("minute_refetch_succeeded"),
        "minute_refetch_reason": metrics.get("minute_refetch_reason"),
        "minute_refetch_trigger_reason": metrics.get("minute_refetch_trigger_reason"),
        "minute_refetch_failure_reason": metrics.get("minute_refetch_failure_reason"),
        "minute_refetch_produced_fresh_snapshot": metrics.get("minute_refetch_produced_fresh_snapshot"),
        "volume_ratio": metrics.get("volume_ratio"),
        "vwap_distance": metrics.get("vwap_distance") if metrics.get("vwap_distance") not in (None, "") else metrics.get("extended_from_vwap_pct"),
        "extended_from_vwap_pct": metrics.get("extended_from_vwap_pct"),
        "pullback_depth_pct": metrics.get("pullback_depth_pct") if metrics.get("pullback_depth_pct") not in (None, "") else metrics.get("pullback_pct"),
        "pullback_pct": metrics.get("pullback_pct"),
        "recent_high": metrics.get("recent_high"),
        "breakout_level": metrics.get("breakout_level"),
        "bar_count": metrics.get("bar_count"),
        "timeframe_minutes": metrics.get("timeframe_minutes"),
        "inferred_spacing_minutes": metrics.get("inferred_spacing_minutes"),
        "series_class": metrics.get("series_class"),
    }
    return {
        "breakout_passed": _gate_pass(metrics, passed_checks, failed_checks, "breakout_ok"),
        "volume_passed": _gate_pass(metrics, passed_checks, failed_checks, "volume_ok"),
        "vwap_extension_passed": _gate_pass(metrics, passed_checks, failed_checks, "extension_ok"),
        "pullback_passed": pullback_passed,
        "entry_score": _score_from_checks(
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            fallback=monitor_entry.get("confidence"),
        ),
        "entry_block_reason": entry_block_reason or "",
        "used_thresholds": thresholds,
        "observed_features": {k: v for k, v in observed_features.items() if v not in (None, "")},
        "passed_gates": passed_checks[:8],
        "failed_gates": failed_checks[:8],
        "primary_failure_axis": _clip(monitor_entry.get("primary_failure_axis"), max_len=80),
    }


def _commander_shadow_context_delta_summary(state: Dict[str, Any], *, observations: Dict[str, Any]) -> Dict[str, Any]:
    shadow_runtime = _dict(state.get("commander_shadow_runtime"))
    prior = _dict(shadow_runtime.get("prior_context"))
    strategist_output = _dict(state.get("strategist_output"))
    selected = _dict(state.get("selected"))
    monitor_output = _dict(state.get("monitor_output"))
    global_signal = _dict(state.get("global_signal"))
    fear_index = _dict(global_signal.get("fear_index"))
    overlay = _dict(strategist_output.get("macro_stress_overlay"))

    current_symbol = _clip(selected.get("symbol") or monitor_output.get("selected_symbol"), max_len=24)
    last_symbol = _clip(prior.get("selected_symbol"), max_len=24)
    current_score = selected.get("score_total")
    if current_score in (None, ""):
        current_score = selected.get("score")
    if current_score in (None, ""):
        current_score = selected.get("confidence")
    last_score = prior.get("selected_score_total")

    current_playbook = _clip(strategist_output.get("playbook"), max_len=40)
    last_playbook = _clip(prior.get("playbook"), max_len=40)
    current_regime = _clip(strategist_output.get("market_regime"), max_len=40)
    last_regime = _clip(prior.get("market_regime"), max_len=40)
    current_sentiment = _clip(strategist_output.get("market_sentiment"), max_len=40)
    last_sentiment = _clip(prior.get("market_sentiment"), max_len=40)
    current_sentiment_score = strategist_output.get("global_sentiment_score")
    last_sentiment_score = prior.get("global_sentiment_score")
    current_vix = fear_index.get("level") if fear_index.get("level") not in (None, "") else overlay.get("vix_level")
    last_vix = prior.get("vix_level")
    current_stress_flags = [str(x or "").strip() for x in list(overlay.get("stress_flags") or []) if str(x or "").strip()]
    last_stress_flags = [str(x or "").strip() for x in list(prior.get("stress_flags") or []) if str(x or "").strip()]

    symbol_same_as_last = None if not current_symbol or not last_symbol else (current_symbol == last_symbol)
    playbook_same_as_last = None if not current_playbook or not last_playbook else (current_playbook == last_playbook)
    market_regime_changed = None if not current_regime or not last_regime else (current_regime != last_regime)

    sentiment_changed: Any = None
    if current_sentiment and last_sentiment:
        sentiment_changed = current_sentiment != last_sentiment
    try:
        if current_sentiment_score not in (None, "") and last_sentiment_score not in (None, ""):
            sentiment_changed = abs(float(current_sentiment_score) - float(last_sentiment_score)) >= 0.03
    except Exception:
        pass

    volatility_changed: Any = None
    try:
        if current_vix not in (None, "") and last_vix not in (None, ""):
            volatility_changed = abs(float(current_vix) - float(last_vix)) >= 1.0
    except Exception:
        pass
    if volatility_changed is None and current_stress_flags and last_stress_flags:
        volatility_changed = sorted(current_stress_flags) != sorted(last_stress_flags)

    signal_changed: Any = None
    try:
        if current_score not in (None, "") and last_score not in (None, ""):
            signal_changed = abs(float(current_score) - float(last_score)) >= 0.05
    except Exception:
        signal_changed = None
    if signal_changed is None and symbol_same_as_last is not None:
        signal_changed = not symbol_same_as_last

    return {
        "symbol_same_as_last": symbol_same_as_last,
        "playbook_same_as_last": playbook_same_as_last,
        "market_regime_changed": market_regime_changed,
        "sentiment_changed": sentiment_changed,
        "volatility_changed": volatility_changed,
        "signal_changed": signal_changed,
        "last_llm_status": _clip(prior.get("llm_status") or observations.get("last_llm_status"), max_len=40),
        "repeated_same_context": observations.get("repeated_same_context"),
        "market_changed": observations.get("market_changed"),
    }


def _commander_shadow_no_trade_reason_code(
    state: Dict[str, Any],
    *,
    observations: Dict[str, Any],
    actual_runtime: Dict[str, Any],
    path: str,
) -> str:
    monitor = _dict(state.get("monitor"))
    monitor_entry = _dict(state.get("monitor_entry"))
    monitor_output = _dict(state.get("monitor_output"))
    execution = _dict(state.get("execution"))
    portfolio_preflight = _dict(state.get("portfolio_preflight"))
    runtime_fast_path = _dict(state.get("runtime_fast_path"))
    strategist_llm = _dict(state.get("strategist_llm"))
    selected = _dict(state.get("selected"))
    symbol = _clip(selected.get("symbol") or monitor_output.get("selected_symbol"), max_len=24)

    monitor_decision = _clip(actual_runtime.get("monitor_decision"), max_len=24).upper()
    executor_action = _clip(actual_runtime.get("executor_action"), max_len=24).upper()
    if monitor_decision in {"BUY", "SELL"} or executor_action in {"BUY", "SELL"}:
        return "NONE"

    if _safe_int(monitor.get("open_position_count"), 0) > 0 and (
        bool(monitor.get("buy_blocked_open_position"))
        or "monitor_only" in str(path or "")
    ):
        return "POSITION_ALREADY_OPEN"

    if bool(portfolio_preflight.get("blocked")) or _clip(state.get("decision_reason"), max_len=80) in {"risk_too_high", "portfolio_preflight_blocked"}:
        return "RISK_BLOCKED"

    if execution and execution.get("allowed") is False:
        reason = _clip(execution.get("reason"), max_len=120).lower()
        if reason not in {"", "noop_intent_skipped"}:
            return "EXECUTION_BLOCKED"

    failed_checks = [str(x or "").strip().lower() for x in list(monitor_entry.get("failed_checks") or []) if str(x or "").strip()]
    combined_reason = " ".join(
        [
            _clip(monitor_entry.get("guard_reason"), max_len=120),
            _clip(monitor_entry.get("reason"), max_len=120),
            _clip(monitor_output.get("entry_exit_reason"), max_len=120),
        ]
    ).strip().lower()
    if any(token in combined_reason for token in ("minute_candle_missing", "data_incomplete", "insufficient_data", "missing_data")):
        return "DATA_INSUFFICIENT"
    if any(token in failed_checks for token in ("data_incomplete", "minute_candle_missing", "vwap_missing", "volume_missing")):
        return "DATA_INSUFFICIENT"
    if not symbol and not combined_reason and not failed_checks and not execution and not strategist_llm:
        return "DATA_INSUFFICIENT"

    llm_status = _clip(strategist_llm.get("status") or strategist_llm.get("llm_status"), max_len=40).lower()
    if bool(strategist_llm.get("blocked")) or llm_status in {"error", "fallback"}:
        return "LLM_UNSTABLE"

    if observations.get("repeated_same_context") is True:
        return "REPEATED_SAME_CONTEXT"
    if observations.get("market_changed") is False or _clip(runtime_fast_path.get("reason"), max_len=80) == "flat_position_cached_strategist":
        return "NO_MARKET_CHANGE"

    confidence = selected.get("confidence")
    try:
        confidence_value = float(confidence)
    except Exception:
        confidence_value = None
    if confidence_value is not None and confidence_value < 0.55:
        return "LOW_CONFIDENCE"

    if failed_checks or any(token in combined_reason for token in ("confirmation", "too_extended", "breakout", "pullback", "reclaim", "entry_wait", "wait")):
        return "WAIT_FOR_CONFIRMATION"

    if combined_reason:
        return "LOW_SIGNAL_QUALITY"
    return "NONE"


def _commander_shadow_strategist_recommendation(
    *,
    no_trade_reason_code: str,
    observations: Dict[str, Any],
) -> str:
    llm_status = str(observations.get("last_llm_status") or "").strip().lower()
    if no_trade_reason_code in {
        "POSITION_ALREADY_OPEN",
        "NO_MARKET_CHANGE",
        "REPEATED_SAME_CONTEXT",
        "DATA_INSUFFICIENT",
        "WAIT_FOR_CONFIRMATION",
        "LOW_SIGNAL_QUALITY",
        "LOW_CONFIDENCE",
        "RISK_BLOCKED",
        "EXECUTION_BLOCKED",
    }:
        return "SKIP"
    if no_trade_reason_code == "LLM_UNSTABLE":
        if llm_status in {"partial", "salvaged", "repaired"}:
            return "RETRY_COMPACT"
        if llm_status == "fallback":
            return "USE_FALLBACK"
        if llm_status == "error":
            return "RETRY_MINIMAL"
    return "RUN"


def _commander_shadow_llm_call_advice(
    *,
    strategist_action_recommendation: str,
    observations: Dict[str, Any],
    state: Dict[str, Any],
) -> str:
    strategist_llm = _dict(state.get("strategist_llm"))
    llm_status = str(observations.get("last_llm_status") or strategist_llm.get("status") or "").strip().lower()
    if strategist_action_recommendation == "SKIP" and observations.get("market_changed") is False:
        return "SKIP"
    if strategist_action_recommendation == "SKIP" and observations.get("repeated_same_context") is True:
        return "SKIP"
    if bool(strategist_llm.get("blocked")) or llm_status in {"error", "fallback"}:
        return "RETRY_MINIMAL"
    if llm_status in {"partial", "salvaged", "repaired"}:
        return "RETRY_COMPACT"
    if strategist_action_recommendation == "SKIP":
        return "SKIP"
    return "ALLOW"


def _commander_shadow_suggested_action(
    *,
    strategist_action_recommendation: str,
    llm_call_advice: str,
    no_trade_reason_code: str,
) -> str:
    if strategist_action_recommendation == "SKIP" and no_trade_reason_code == "POSITION_ALREADY_OPEN":
        return "monitor_only_observe"
    if strategist_action_recommendation == "SKIP" and no_trade_reason_code in {"NO_MARKET_CHANGE", "REPEATED_SAME_CONTEXT"}:
        return "skip_strategist_reuse_context"
    if llm_call_advice == "RETRY_COMPACT":
        return "compact_strategist_retry"
    if llm_call_advice == "RETRY_MINIMAL":
        return "minimal_strategist_retry"
    return "allow_current_flow"


def _commander_shadow_next_action_recommendation(
    *,
    strategist_action_recommendation: str,
    llm_call_advice: str,
    no_trade_reason_code: str,
    actual_runtime: Dict[str, Any],
) -> str:
    if no_trade_reason_code == "POSITION_ALREADY_OPEN":
        return "HOLD_OBSERVE"
    if strategist_action_recommendation in {"RETRY_COMPACT", "RETRY_MINIMAL", "USE_FALLBACK"} or llm_call_advice in {
        "RETRY_COMPACT",
        "RETRY_MINIMAL",
    }:
        return "RETRY_COMPACT_NEXT"
    if no_trade_reason_code in {"WAIT_FOR_CONFIRMATION", "LOW_SIGNAL_QUALITY", "LOW_CONFIDENCE", "DATA_INSUFFICIENT"}:
        return "WAIT_NEXT_BAR"
    monitor_decision = _clip(actual_runtime.get("monitor_decision"), max_len=24).upper()
    if monitor_decision in {"BUY", "SELL", "HOLD"}:
        return "HOLD_OBSERVE"
    return "NO_ACTION"


def _commander_shadow_reason_summary(
    *,
    no_trade_reason_code: str,
    observations: Dict[str, Any],
    actual_runtime: Dict[str, Any],
) -> str:
    llm_status = _clip(observations.get("last_llm_status"), max_len=40) or "unknown"
    monitor_decision = _clip(actual_runtime.get("monitor_decision"), max_len=24) or "WAIT"
    executor_action = _clip(actual_runtime.get("executor_action"), max_len=24) or "NONE"
    mapping = {
        "NONE": f"Observed runtime ended with monitor={monitor_decision} and executor={executor_action} without a stronger commander block signal.",
        "POSITION_ALREADY_OPEN": "Open position state already existed, so monitor-only observation was more appropriate than a fresh strategist cycle.",
        "RISK_BLOCKED": "Risk or portfolio guard signals were stronger than any need to refresh strategist context in this cycle.",
        "EXECUTION_BLOCKED": "Execution or approval constraints were the main reason to stand down, independent of strategist quality.",
        "DATA_INSUFFICIENT": "Available minute, feature, or symbol data was too thin to justify a fresh strategist-driven trade attempt.",
        "NO_MARKET_CHANGE": "The cycle looked materially similar to the prior context, so a new strategist run likely added little value.",
        "LLM_UNSTABLE": f"Recent strategist LLM status was {llm_status}, so a compact or minimal retry would have been safer than a full refresh.",
        "LOW_CONFIDENCE": "Signal confidence was weak enough that waiting for stronger confirmation looked safer than acting now.",
        "LOW_SIGNAL_QUALITY": "Monitor signal quality was too weak to justify a trade, even if strategist context was available.",
        "REPEATED_SAME_CONTEXT": "The cycle repeated nearly the same strategist context, suggesting reuse or skip would have been reasonable.",
        "WAIT_FOR_CONFIRMATION": "Monitor gates were not fully aligned yet, so waiting for another bar or clearer confirmation looked appropriate.",
    }
    return mapping.get(no_trade_reason_code, "Shadow commander observed the cycle, but the evidence was limited and should be treated as advisory only.")


def _commander_shadow_recommendation_gap(
    *,
    strategist_action_recommendation: str,
    llm_call_advice: str,
    actual_runtime: Dict[str, Any],
) -> str:
    strategist_executed = actual_runtime.get("strategist_executed")
    llm_called = actual_runtime.get("llm_called_by_strategist")
    if strategist_action_recommendation == "SKIP" and strategist_executed is True:
        return "strategist_ran_despite_skip_recommendation"
    if strategist_action_recommendation in {"RUN", "RETRY_COMPACT", "RETRY_MINIMAL", "USE_FALLBACK"} and strategist_executed is False:
        return "strategist_not_run_despite_refresh_recommendation"
    if llm_call_advice == "SKIP" and llm_called is True:
        return "llm_called_despite_skip_advice"
    if llm_call_advice in {"ALLOW", "RETRY_COMPACT", "RETRY_MINIMAL"} and llm_called is False and strategist_executed is True:
        return "llm_not_called_despite_refresh_advice"
    return "aligned"


def _commander_shadow_pre_strategist_snapshot(
    *,
    state: Dict[str, Any],
    observations: Dict[str, Any],
    context_delta_summary: Dict[str, Any],
    strategist_action_recommendation: str,
    llm_call_advice: str,
) -> Dict[str, Any]:
    prior = _dict(_dict(state.get("commander_shadow_runtime")).get("prior_context"))
    return {
        "market_changed": observations.get("market_changed"),
        "repeated_same_context": observations.get("repeated_same_context"),
        "last_llm_status": observations.get("last_llm_status"),
        "prior_symbol": _clip(prior.get("selected_symbol"), max_len=24),
        "prior_playbook": _clip(prior.get("playbook"), max_len=40),
        "strategist_action_recommendation": strategist_action_recommendation,
        "llm_call_advice": llm_call_advice,
        "reason": _clip(
            f"context_delta={context_delta_summary.get('signal_changed')} market_changed={observations.get('market_changed')} repeated={observations.get('repeated_same_context')}",
            max_len=180,
        ),
    }


def _commander_shadow_post_strategist_assessment(
    *,
    state: Dict[str, Any],
    actual_runtime: Dict[str, Any],
    context_delta_summary: Dict[str, Any],
    recommendation_gap: str,
) -> Dict[str, Any]:
    strategist_output = _dict(state.get("strategist_output"))
    strategist_llm = _dict(state.get("strategist_llm"))
    return {
        "strategist_executed": actual_runtime.get("strategist_executed"),
        "llm_called_by_strategist": actual_runtime.get("llm_called_by_strategist"),
        "used_cached_strategist": actual_runtime.get("used_cached_strategist"),
        "llm_status": _clip(strategist_llm.get("status") or strategist_output.get("llm_frame_status"), max_len=40),
        "playbook": _clip(strategist_output.get("playbook"), max_len=40),
        "market_regime": _clip(strategist_output.get("market_regime"), max_len=40),
        "market_sentiment": _clip(strategist_output.get("market_sentiment"), max_len=40),
        "recommendation_gap": recommendation_gap,
        "context_delta_summary": context_delta_summary,
    }


def _commander_shadow_post_monitor_assessment(
    *,
    actual_runtime: Dict[str, Any],
    monitor_gate_details: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "monitor_decision": _clip(actual_runtime.get("monitor_decision"), max_len=24),
        "entry_block_reason": _clip(monitor_gate_details.get("entry_block_reason"), max_len=180),
        "failed_gates": list(monitor_gate_details.get("failed_gates") or [])[:8],
        "passed_gates": list(monitor_gate_details.get("passed_gates") or [])[:8],
        "primary_failure_axis": _clip(monitor_gate_details.get("primary_failure_axis"), max_len=80),
        "monitor_gate_details": monitor_gate_details,
    }


def _commander_shadow_end_of_cycle_summary(
    *,
    no_trade_reason_code: str,
    reason_summary: str,
    actual_runtime: Dict[str, Any],
    next_action_recommendation: str,
    recommendation_gap: str,
) -> Dict[str, Any]:
    return {
        "no_trade_reason_code": no_trade_reason_code,
        "reason_summary": reason_summary,
        "actual_runtime": actual_runtime,
        "next_action_recommendation": next_action_recommendation,
        "recommendation_gap": recommendation_gap,
    }


def build_commander_shadow_artifact(
    state: Dict[str, Any],
    *,
    mode: str,
    phase: str,
    path: str,
    status: str,
    reason: str = "",
) -> Dict[str, Any]:
    observations = _commander_shadow_observations(state, path=path)
    actual_runtime = _commander_shadow_actual_runtime(state, path=path)
    monitor_gate_details = _commander_shadow_monitor_gate_details(state)
    context_delta_summary = _commander_shadow_context_delta_summary(state, observations=observations)
    no_trade_reason_code = _commander_shadow_no_trade_reason_code(
        state,
        observations=observations,
        actual_runtime=actual_runtime,
        path=path,
    )
    strategist_action_recommendation = _commander_shadow_strategist_recommendation(
        no_trade_reason_code=no_trade_reason_code,
        observations=observations,
    )
    llm_call_advice = _commander_shadow_llm_call_advice(
        strategist_action_recommendation=strategist_action_recommendation,
        observations=observations,
        state=state,
    )
    suggested_action = _commander_shadow_suggested_action(
        strategist_action_recommendation=strategist_action_recommendation,
        llm_call_advice=llm_call_advice,
        no_trade_reason_code=no_trade_reason_code,
    )
    next_action_recommendation = _commander_shadow_next_action_recommendation(
        strategist_action_recommendation=strategist_action_recommendation,
        llm_call_advice=llm_call_advice,
        no_trade_reason_code=no_trade_reason_code,
        actual_runtime=actual_runtime,
    )
    reason_summary = _commander_shadow_reason_summary(
        no_trade_reason_code=no_trade_reason_code,
        observations=observations,
        actual_runtime=actual_runtime,
    )
    recommendation_gap = _commander_shadow_recommendation_gap(
        strategist_action_recommendation=strategist_action_recommendation,
        llm_call_advice=llm_call_advice,
        actual_runtime=actual_runtime,
    )
    pre_strategist_shadow_snapshot = _commander_shadow_pre_strategist_snapshot(
        state=state,
        observations=observations,
        context_delta_summary=context_delta_summary,
        strategist_action_recommendation=strategist_action_recommendation,
        llm_call_advice=llm_call_advice,
    )
    post_strategist_assessment = _commander_shadow_post_strategist_assessment(
        state=state,
        actual_runtime=actual_runtime,
        context_delta_summary=context_delta_summary,
        recommendation_gap=recommendation_gap,
    )
    post_monitor_assessment = _commander_shadow_post_monitor_assessment(
        actual_runtime=actual_runtime,
        monitor_gate_details=monitor_gate_details,
    )
    end_of_cycle_summary = _commander_shadow_end_of_cycle_summary(
        no_trade_reason_code=no_trade_reason_code,
        reason_summary=reason_summary,
        actual_runtime=actual_runtime,
        next_action_recommendation=next_action_recommendation,
        recommendation_gap=recommendation_gap,
    )
    symbol = _clip(
        _dict(state.get("selected")).get("symbol")
        or _dict(state.get("monitor_output")).get("selected_symbol")
        or _dict(state.get("monitor_exit")).get("symbol"),
        max_len=24,
    )
    artifact = _base_output(state, agent="commander", symbol=symbol, status=status or "ok")
    artifact.update(
        {
            "schema_version": "commander_shadow.v1",
            "mode": "shadow",
            "cycle_id": _clip(state.get("cycle_id"), max_len=80),
            "observed_runtime_mode": _clip(mode, max_len=40),
            "observed_runtime_path": _clip(path, max_len=80),
            "decision": "OBSERVE_ONLY",
            "strategist_action_recommendation": strategist_action_recommendation,
            "llm_call_advice": llm_call_advice,
            "suggested_action": suggested_action,
            "next_action_recommendation": next_action_recommendation,
            "no_trade_reason_code": no_trade_reason_code,
            "reason_summary": reason_summary,
            "observations": observations,
            "actual_runtime": actual_runtime,
            "monitor_gate_details": monitor_gate_details,
            "context_delta_summary": context_delta_summary,
            "pre_strategist_shadow_snapshot": pre_strategist_shadow_snapshot,
            "post_strategist_assessment": post_strategist_assessment,
            "post_monitor_assessment": post_monitor_assessment,
            "end_of_cycle_summary": end_of_cycle_summary,
            "comparison_summary": (
                f"recommended={strategist_action_recommendation}/{llm_call_advice}, "
                f"next={next_action_recommendation}, "
                f"observed_monitor={actual_runtime.get('monitor_decision') or 'WAIT'}, "
                f"observed_executor={actual_runtime.get('executor_action') or 'NONE'}, "
                f"gap={recommendation_gap}"
            ),
            "integrated_into_commander_decision": True,
            "integration_version": "phase1_2",
            "integration_role": "upstream_assessment",
            "reason": _clip(reason or state.get("runtime_status") or "", max_len=220),
            "shadow_only": True,
            "generated_at": _utc_now_iso(),
        }
    )
    artifact["validation"] = validate_artifact(artifact)
    return artifact
