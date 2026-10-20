"""Strategist LLM summary quality/readout projection (P1.5 BATCH04-A, DEV-A).

Deterministic news/memory usage, news and output quality audits, stage decision, operator readout, strategy
detail and the ``strategist_llm_summary.v1`` payload assembly moved from ``libs.reporting.strategist_llm_summary``.
Response/meta/canonical reads, the clock (``generated_at`` is passed in), ``classify_market_regime_rail`` and
``build_risk_off_exception_policy`` stay in the facade module; helpers resolve on the injected facade at call time.
"""
from __future__ import annotations

from typing import Any, Dict, List


def _headline_count_from_sample_map(value: Any, *, facade: Any) -> int:
    total = 0
    if not isinstance(value, dict):
        return total
    for row in value.values():
        if not isinstance(row, dict):
            continue
        try:
            total += int(row.get("count") or 0)
        except Exception:
            pass
    return total


def _directive(payload: Dict[str, Any], key: str, *, facade: Any) -> Dict[str, Any]:
    directives = facade._as_dict(payload.get("strategy_adjustment_directives"))
    return facade._as_dict(directives.get(key))


def _compact_operator_summary(value: Dict[str, Any], *, facade: Any) -> Dict[str, Any]:
    return {
        "available": bool(value.get("available")),
        "status": facade._text(value.get("status"), ""),
        "artifact_path": facade._text(value.get("artifact_path"), ""),
        "trade_count": value.get("trade_count"),
        "closed_trade_count": value.get("closed_trade_count"),
        "win_rate": value.get("win_rate"),
        "avg_return_pct": value.get("avg_return_pct"),
    }


def _memory_usage_from_canonical(canonical: Dict[str, Any], *, facade: Any) -> Dict[str, Any]:
    trace = facade._as_dict(canonical.get("memory_usage_trace"))
    visibility = facade._as_dict(canonical.get("memory_packet_visibility"))
    layer_decisions = facade._as_dict(trace.get("layer_decisions"))
    compact_layers: Dict[str, Any] = {}
    for layer in ("daily", "weekly", "monthly", "symbol"):
        row = facade._as_dict(layer_decisions.get(layer))
        if not row:
            continue
        compact_layers[layer] = {
            "status": facade._text(row.get("status"), ""),
            "active": bool(row.get("active")),
            "used": bool(row.get("used")),
            "confidence": row.get("confidence"),
            "effect": facade._text(row.get("effect"), ""),
            "reason": facade._text(row.get("reason"), ""),
            "gate_reason": facade._text(row.get("gate_reason"), ""),
            "operator_summary": facade._compact_operator_summary(facade._as_dict(row.get("operator_summary"))),
        }

    return {
        "available": bool(trace or visibility),
        "active_layers": facade._as_list(trace.get("active_layers")),
        "priority_order": facade._as_list(trace.get("priority_order")),
        "human_summary": facade._text(trace.get("human_summary"), ""),
        "applied_to_strategy": facade._as_dict(trace.get("applied_to_strategy")),
        "scanner_application": facade._as_dict(trace.get("scanner_application")),
        "monitor_application": facade._as_dict(trace.get("monitor_application")),
        "layer_decisions": compact_layers,
        "memory_packet_visibility": {
            "reporter_feedback_packet": facade._as_dict(visibility.get("reporter_feedback_packet")),
            "selected_symbol_memory": facade._as_dict(visibility.get("selected_symbol_memory")),
            "commander_refresh_context": facade._as_dict(visibility.get("commander_refresh_context")),
        },
    }


def _news_usage_from_canonical(canonical: Dict[str, Any], *, facade: Any) -> Dict[str, Any]:
    trace = facade._as_dict(canonical.get("news_usage_trace"))
    context = facade._as_dict(canonical.get("news_context"))
    query_targets = facade._as_list(trace.get("query_targets")) or facade._as_list(canonical.get("news_query_targets"))
    market_headlines = facade._as_list(trace.get("market_headlines_used"))
    candidate_headlines = facade._as_list(trace.get("candidate_headlines_used"))
    market_count = len(market_headlines)
    candidate_count = len(candidate_headlines)
    if market_count <= 0:
        market_count = int(context.get("market_headline_count") or 0) or facade._headline_count_from_sample_map(canonical.get("market_news_sample"))
    if candidate_count <= 0:
        candidate_count = int(context.get("candidate_headline_count") or 0) or facade._headline_count_from_sample_map(canonical.get("candidate_news_sample"))
    headline_count = int(context.get("headline_count") or 0)
    if headline_count and market_count <= 0 and candidate_count <= 0:
        market_count = int(context.get("market_signal_total") or 0)
        candidate_count = max(0, headline_count - market_count)
    return {
        "available": bool(trace or context or canonical.get("news_evidence_summary") or query_targets),
        "query_targets": query_targets,
        "human_summary": facade._text(trace.get("human_summary") or context.get("summary"), ""),
        "market_effect": facade._text(trace.get("market_effect"), ""),
        "playbook_effect": facade._text(trace.get("playbook_effect"), ""),
        "scanner_guidance_effect": facade._text(trace.get("scanner_guidance_effect"), ""),
        "monitor_policy_effect": facade._text(trace.get("monitor_policy_effect"), ""),
        "confidence": facade._text(trace.get("confidence") or ("medium" if context else ""), ""),
        "news_evidence_summary": facade._text(canonical.get("news_evidence_summary"), ""),
        "news_query_reasoning": facade._text(canonical.get("news_query_reasoning"), ""),
        "market_headline_count": market_count,
        "candidate_headline_count": candidate_count,
        "market_headlines_sample": market_headlines[:3],
        "candidate_headlines_sample": candidate_headlines[:3],
    }


def _news_quality_audit(canonical: Dict[str, Any], news_usage: Dict[str, Any], *, facade: Any) -> Dict[str, Any]:
    ranked = facade._as_dict(canonical.get("news_evidence_ranked"))
    candidate_ranked = facade._as_list(ranked.get("candidate_news_ranked"))
    market_ranked = facade._as_list(ranked.get("market_news_ranked"))
    query_targets = facade._as_list(news_usage.get("query_targets"))
    market_count = int(news_usage.get("market_headline_count") or len(market_ranked) or 0)
    candidate_count = int(news_usage.get("candidate_headline_count") or len(candidate_ranked) or 0)
    total = market_count + candidate_count
    confidence = facade._text(news_usage.get("confidence"), "")
    summary = facade._text(news_usage.get("human_summary") or news_usage.get("news_evidence_summary"), "")
    no_effect = not any(
        facade._text(news_usage.get(key), "")
        for key in ("market_effect", "playbook_effect", "scanner_guidance_effect", "monitor_policy_effect")
    )
    issues: List[str] = []
    if total <= 0:
        issues.append("news_headlines_missing")
    if not query_targets:
        issues.append("news_query_targets_missing")
    if no_effect:
        issues.append("news_effect_trace_missing")
    if confidence.lower() in {"", "-", "low", "none", "unknown"}:
        issues.append("news_confidence_low_or_missing")
    if not summary:
        issues.append("news_summary_missing")
    if total > 0 and candidate_count <= 0:
        issues.append("candidate_news_missing")
    if total > 0 and market_count <= 0:
        issues.append("market_news_missing")
    if not issues:
        status = "ok"
    elif total > 0:
        status = "partial"
    else:
        status = "weak"
    return {
        "schema_version": "strategist_news_quality_audit.v1",
        "status": status,
        "headline_count": total,
        "market_headline_count": market_count,
        "candidate_headline_count": candidate_count,
        "query_target_count": len(query_targets),
        "query_targets": query_targets[:10],
        "confidence": confidence,
        "issues": issues,
        "market_effect": facade._text(news_usage.get("market_effect"), ""),
        "playbook_effect": facade._text(news_usage.get("playbook_effect"), ""),
        "scanner_guidance_effect": facade._text(news_usage.get("scanner_guidance_effect"), ""),
        "monitor_policy_effect": facade._text(news_usage.get("monitor_policy_effect"), ""),
    }


def _strategist_output_quality_audit(
    *,
    payload: Dict[str, Any],
    canonical: Dict[str, Any],
    stage_decision: Dict[str, Any],
    strategy_detail: Dict[str, Any],
    market_rail: Dict[str, Any],
    news_quality: Dict[str, Any],
    facade: Any,
) -> Dict[str, Any]:
    candidate_watch = facade._as_dict(strategy_detail.get("candidate_watch_policy"))
    memory_usage = facade._memory_usage_from_canonical(canonical)
    is_stage_specific = bool(stage_decision.get("is_stage_specific"))
    decision = facade._text(stage_decision.get("decision") or payload.get("decision"), "")
    confidence = stage_decision.get("confidence")
    if confidence in (None, ""):
        confidence = payload.get("confidence")
    issues: List[str] = []
    if not decision:
        issues.append("decision_missing")
    if confidence in (None, ""):
        issues.append("confidence_missing")
    if is_stage_specific:
        if not facade._as_dict(stage_decision.get("monitor_instruction")) and not facade._as_dict(stage_decision.get("entry_policy_delta")):
            issues.append("stage_control_fields_missing")
    else:
        if not facade._text(strategy_detail.get("final_playbook"), ""):
            issues.append("final_playbook_missing")
        if not facade._text(strategy_detail.get("tactical_strategy"), ""):
            issues.append("tactical_strategy_missing")
        if not candidate_watch:
            issues.append("candidate_watch_policy_missing")
    if facade._text(market_rail.get("market_regime_rail"), "") in {"", "macro_packet_unavailable"}:
        issues.append("market_regime_rail_missing")
    if news_quality.get("status") != "ok":
        issues.append("news_quality_not_ok")
    if not bool(memory_usage.get("available")):
        issues.append("memory_trace_missing_or_disabled")
    elif not facade._as_list(memory_usage.get("active_layers")):
        issues.append("memory_active_layers_empty")
    if not issues:
        status = "ok"
    elif len(issues) <= 2:
        status = "watch"
    else:
        status = "needs_review"
    return {
        "schema_version": "strategist_output_quality_audit.v1",
        "status": status,
        "issues": issues,
        "decision": decision,
        "confidence": confidence,
        "final_playbook": facade._text(strategy_detail.get("final_playbook"), ""),
        "tactical_strategy": facade._text(strategy_detail.get("tactical_strategy"), ""),
        "market_regime": facade._text(market_rail.get("market_regime"), ""),
        "market_regime_rail": facade._text(market_rail.get("market_regime_rail"), ""),
        "candidate_watch_policy_present": bool(candidate_watch),
        "memory_available": bool(memory_usage.get("available")),
        "memory_active_layers": facade._as_list(memory_usage.get("active_layers")),
        "news_quality_status": facade._text(news_quality.get("status"), ""),
    }


def _stage_decision_from_payload(
    payload: Dict[str, Any],
    raw: Dict[str, Any],
    meta: Dict[str, Any] | None = None,
    *,
    facade: Any,
) -> Dict[str, Any]:
    stage_meta = facade._stage_meta(payload, raw, meta)
    call_kind = facade._text(stage_meta.get("call_kind"), "")
    stage_name = facade._text(stage_meta.get("stage_name") or payload.get("stage_name"), "")
    try:
        stage_index = int(stage_meta.get("stage_index") or payload.get("stage_index") or 0)
    except (TypeError, ValueError):
        stage_index = 0
    is_market_frame = stage_index in (0, 1) and call_kind in {"", "market_strategy_frame", "theme_selection", "strategic_frame"}
    if is_market_frame:
        return {"is_stage_specific": False}

    selected_symbol_review = facade._as_dict(payload.get("selected_symbol_tactical_review"))
    candidate_watch = facade._as_dict(payload.get("candidate_watch_policy"))
    refresh_trace = facade._as_dict(payload.get("strategy_refresh_trace"))
    decision = facade._first_text(
        "",
        selected_symbol_review.get("selected_symbol_decision"),
        payload.get("hold_review_decision"),
        payload.get("carry_review_decision"),
        payload.get("tactical_refresh_decision"),
        payload.get("selected_symbol_decision"),
        payload.get("decision"),
    )
    monitor_adjustment = facade._first_dict(payload.get("monitor_adjustment"), selected_symbol_review.get("monitor_adjustment"))
    priority_exit_triggers = facade._as_list(payload.get("priority_exit_triggers"))
    runner_up_order = facade._as_list(payload.get("runner_up_order")) or facade._as_list(selected_symbol_review.get("runner_up_order"))
    commander_actionability = facade._first_dict(
        payload.get("commander_actionability"),
        selected_symbol_review.get("commander_actionability"),
    )
    if not commander_actionability:
        actionability_text = facade._first_text("", payload.get("commander_actionability"), selected_symbol_review.get("commander_actionability"))
        commander_actionability = {"value": actionability_text} if actionability_text else {}
    return {
        "is_stage_specific": True,
        "stage_index": stage_index,
        "stage_name": stage_name,
        "call_kind": call_kind,
        "stage_component": facade._text(stage_meta.get("stage_component"), ""),
        "decision": decision,
        "target_symbol": facade._first_text("", selected_symbol_review.get("target_symbol"), payload.get("target_symbol")),
        "target_rank": selected_symbol_review.get("target_rank") or payload.get("target_rank"),
        "runner_up_order": runner_up_order,
        "monitor_instruction": facade._first_dict(payload.get("monitor_instruction"), selected_symbol_review.get("monitor_instruction")),
        "entry_policy_delta": facade._first_dict(payload.get("entry_policy_delta"), selected_symbol_review.get("entry_policy_delta")),
        "commander_actionability": commander_actionability,
        "confidence": selected_symbol_review.get("confidence") if selected_symbol_review.get("confidence") is not None else payload.get("confidence"),
        "exit_pressure": facade._text(payload.get("exit_pressure"), ""),
        "thesis_status": facade._text(payload.get("thesis_status"), ""),
        "next_check_minutes": payload.get("next_check_minutes"),
        "priority_exit_triggers": priority_exit_triggers,
        "monitor_adjustment": monitor_adjustment,
        "reason": facade._first_text("", payload.get("reason"), selected_symbol_review.get("reason"), candidate_watch.get("reason"), refresh_trace.get("summary")),
        "raw_payload_keys": sorted(str(key) for key in payload.keys()),
    }


def _first_text(default: str, *values: Any, facade: Any) -> str:
    for value in values:
        text = facade._text(value, "")
        if text:
            return text
    return default


def _operator_readout_clean(payload: Dict[str, Any], stage_decision: Dict[str, Any] | None = None, *, facade: Any) -> Dict[str, Any]:
    stage_decision = facade._as_dict(stage_decision)
    if bool(stage_decision.get("is_stage_specific")):
        stage_name = facade._text(stage_decision.get("stage_name"), "stage_specific")
        decision = facade._text(stage_decision.get("decision"), "-")
        reason = facade._text(stage_decision.get("reason"), "")
        return {
            "headline": f"{stage_name} / decision={decision}",
            "good_points": [
                "단계별 전략가 응답이 파싱됐습니다.",
                "이 단계는 시장 프레임이 아니므로 selected_themes 같은 1차 필드는 필수가 아닙니다.",
            ],
            "issues": [] if reason else ["단계별 응답의 reason이 비어 있습니다."],
            "root_cause": reason or "단계별 응답에 reason이 포함되지 않았습니다.",
            "recommended_actions": ["시장 프레임 섹션이 아니라 단계별 decision 필드를 확인합니다."],
            "validation_questions": ["모니터/집행 흐름이 이 단계별 decision을 따랐는지 확인합니다."],
        }

    theme_strategy = facade._as_dict(payload.get("theme_strategy"))
    rationale = facade._text(payload.get("rationale"), "")
    selected_themes = facade._as_list(payload.get("selected_themes"))
    fallback_reason = facade._text(theme_strategy.get("fallback_reason"), "")
    selected_symbol_bias = facade._directive(payload, "selected_symbol_bias_action")
    entry_policy = facade._directive(payload, "entry_policy_action")
    monitor_focus = facade._directive(payload, "monitor_focus_action")
    refresh_action = facade._directive(payload, "refresh_action")

    good_points: List[str] = []
    issues: List[str] = []
    actions: List[str] = []
    validation: List[str] = []

    if entry_policy:
        good_points.append("최근 손실/과매매 피드백을 진입 정책 조정 근거로 명시했습니다.")
    if monitor_focus:
        good_points.append("모니터가 집중할 축을 volume/reclaim처럼 실행 가능한 형태로 넘겼습니다.")
    if refresh_action:
        good_points.append("전략 refresh 요청 사유와 최종 적용 단계를 분리해 남겼습니다.")
    if not selected_themes:
        issues.append("selected_themes가 비어 있어 테마 기반 전략 분기가 약합니다.")
        actions.append("다음 실행에서 Commander가 available_themes/theme_strength_packet을 전략가 호출 전에 채우는지 확인합니다.")
        validation.append("다음 전략가 요약에서 selected_themes가 실제 테마명으로 채워지는지 확인합니다.")
    if ("best" in rationale.lower() and "worst" in rationale.lower()) or "best 諛?worst" in rationale:
        issues.append("전략 메모리에서 같은 플레이북이 best/worst에 동시에 잡혀 방향 신호가 혼합됩니다.")
        actions.append("best/worst 중복 플레이북은 방향성 bias가 아니라 memory_quality_flag로만 표시합니다.")
    if str(selected_symbol_bias.get("action") or "").strip().lower() == "none":
        issues.append("성과 메모리 근거가 없어 특정 종목 영향 조정은 적용되지 않았습니다.")
        validation.append("성과 summary/memory가 누적돼도 selected_symbol_bias_action이 계속 none인지 확인합니다.")

    if not good_points:
        good_points.append("전략가 출력은 파싱 가능하며 playbook, entry policy, refresh trace를 포함합니다.")
    if not issues:
        issues.append("즉시 확인할 구조적 문제는 요약에서 감지되지 않았습니다.")
    if not actions:
        actions.append("다음 실행 결과를 비교해 같은 playbook 반복 여부를 확인합니다.")
    if not validation:
        validation.append("다음 실행에서 playbook/theme/entry policy가 시장 입력에 따라 달라지는지 확인합니다.")

    headline_parts = [facade._text(payload.get("playbook"), "unknown")]
    if selected_themes:
        headline_parts.append(f"themes={', '.join(str(x) for x in selected_themes[:3])}")
    else:
        headline_parts.append("theme=none")
    if theme_strategy.get("selection_mode"):
        headline_parts.append(f"mode={theme_strategy.get('selection_mode')}")

    return {
        "headline": " / ".join(headline_parts),
        "good_points": good_points[:4],
        "issues": issues[:4],
        "root_cause": fallback_reason or rationale or "전략가 출력의 rationale 확인 필요",
        "recommended_actions": actions[:4],
        "validation_questions": validation[:4],
    }


def _first_dict(*values: Any, facade: Any) -> Dict[str, Any]:
    for value in values:
        row = facade._as_dict(value)
        if row:
            return row
    return {}


def _strategy_detail_from_sources(payload: Dict[str, Any], canonical: Dict[str, Any], *, facade: Any) -> Dict[str, Any]:
    canonical_detail = facade._as_dict(canonical.get("strategy_detail"))
    strategy_policy = facade._as_dict(canonical.get("strategy_policy"))
    market_policy = facade._as_dict(strategy_policy.get("market_policy"))
    scanner_policy = facade._as_dict(strategy_policy.get("scanner_policy"))
    return {
        "pre_llm_playbook": facade._first_text(
            "",
            canonical_detail.get("pre_llm_playbook"),
            canonical.get("pre_llm_playbook"),
            market_policy.get("pre_llm_playbook"),
            payload.get("pre_llm_playbook"),
        ),
        "llm_requested_playbook": facade._first_text(
            "",
            canonical_detail.get("llm_requested_playbook"),
            canonical.get("llm_requested_playbook"),
            market_policy.get("llm_requested_playbook"),
            payload.get("llm_requested_playbook"),
        ),
        "requested_playbook": facade._first_text(
            "",
            canonical_detail.get("requested_playbook"),
            canonical.get("requested_playbook"),
            market_policy.get("requested_playbook"),
            payload.get("requested_playbook"),
        ),
        "requested_playbook_source": facade._first_text(
            "",
            canonical_detail.get("requested_playbook_source"),
            canonical.get("requested_playbook_source"),
            market_policy.get("requested_playbook_source"),
            payload.get("requested_playbook_source"),
        ),
        "final_playbook": facade._first_text(
            "",
            canonical_detail.get("final_playbook"),
            canonical.get("final_playbook"),
            market_policy.get("final_playbook"),
            canonical.get("playbook"),
            payload.get("final_playbook"),
            payload.get("playbook"),
        ),
        "tactical_strategy": facade._first_text(
            "",
            canonical_detail.get("tactical_strategy"),
            canonical.get("tactical_strategy"),
            market_policy.get("tactical_strategy"),
            payload.get("tactical_strategy"),
        ),
        "tactical_subtype": facade._first_text(
            "",
            canonical_detail.get("tactical_subtype"),
            canonical.get("tactical_subtype"),
            market_policy.get("tactical_subtype"),
            payload.get("tactical_subtype"),
        ),
        "strategy_scores": facade._first_dict(
            canonical_detail.get("strategy_scores"),
            canonical.get("strategy_scores"),
            market_policy.get("strategy_scores"),
            payload.get("strategy_scores"),
        ),
        "rejected_strategy_reasons": facade._first_dict(
            canonical_detail.get("rejected_strategy_reasons"),
            canonical.get("rejected_strategy_reasons"),
            market_policy.get("rejected_strategy_reasons"),
            payload.get("rejected_strategy_reasons"),
        ),
        "candidate_watch_policy": facade._first_dict(
            canonical_detail.get("candidate_watch_policy"),
            canonical.get("candidate_watch_policy"),
            scanner_policy.get("candidate_watch_policy"),
            payload.get("candidate_watch_policy"),
        ),
    }


def assemble_summary_payload(
    *,
    source_path: Any,
    canonical_path: Any,
    raw: Any,
    sidecar_meta: Any,
    payload: Any,
    canonical: Any,
    theme_strategy: Any,
    refresh_trace: Any,
    horizon: Any,
    strategy_detail: Any,
    stage_decision: Any,
    stage_meta: Any,
    news_usage: Any,
    market_regime_rail: Any,
    news_quality: Any,
    risk_off_exception_policy: Any,
    output_quality: Any,
    generated_at: Any,
    facade: Any,
) -> Dict[str, Any]:
    """Assemble ``strategist_llm_summary.v1`` from already-read inputs; field helpers run in the original dict order."""
    return {
        "schema_version": "strategist_llm_summary.v1",
        "artifact_type": "strategist_llm_summary",
        "source_response_json": str(source_path),
        "source_canonical_strategist_json": str(canonical_path) if canonical_path else "",
        "generated_at": generated_at,
        "llm_meta": {
            "stage": facade._first_text("", raw.get("stage"), sidecar_meta.get("stage")),
            "stage_index": stage_meta.get("stage_index"),
            "stage_name": facade._text(stage_meta.get("stage_name"), ""),
            "call_kind": facade._text(stage_meta.get("call_kind"), ""),
            "stage_component": facade._text(stage_meta.get("stage_component"), ""),
            "provider": facade._first_text("", raw.get("provider"), sidecar_meta.get("provider")),
            "model": facade._first_text("", raw.get("model"), sidecar_meta.get("model")),
            "status": facade._first_text("", raw.get("status"), raw.get("llm_status"), sidecar_meta.get("status"), sidecar_meta.get("llm_status")),
            "reason": facade._first_text("", raw.get("reason"), sidecar_meta.get("reason")),
            "run_id": facade._first_text("", raw.get("run_id"), sidecar_meta.get("run_id")),
            "day": facade._first_text("", raw.get("day"), sidecar_meta.get("day")),
            "saved_at": facade._first_text("", raw.get("saved_at"), sidecar_meta.get("saved_at")),
            "repair_used": bool(raw.get("repair_used") or sidecar_meta.get("repair_used")),
            "profile_name": facade._first_text("", raw.get("llm_execution_profile_name"), sidecar_meta.get("llm_execution_profile_name")),
            "profile_source": facade._first_text("", raw.get("llm_execution_profile_source"), sidecar_meta.get("llm_execution_profile_source")),
        },
        "operator_readout": facade._operator_readout_clean(payload, stage_decision),
        "stage_decision": stage_decision,
        "strategy_frame": {
            "playbook": facade._text(payload.get("playbook")),
            "selected_themes": facade._as_list(payload.get("selected_themes")),
            "theme_selection_mode": facade._text(theme_strategy.get("selection_mode")),
            "fallback_reason": facade._text(theme_strategy.get("fallback_reason"), ""),
            "rationale": facade._text(payload.get("rationale"), ""),
        },
        "strategy_detail": strategy_detail,
        "policy_changes": {
            "playbook_action": facade._directive(payload, "playbook_action"),
            "entry_policy_action": facade._directive(payload, "entry_policy_action"),
            "monitor_focus_action": facade._directive(payload, "monitor_focus_action"),
            "selected_symbol_bias_action": facade._directive(payload, "selected_symbol_bias_action"),
            "refresh_action": facade._directive(payload, "refresh_action"),
        },
        "monitor_entry_policy": facade._as_dict(payload.get("monitor_entry_policy")),
        "memory_usage": facade._memory_usage_from_canonical(canonical),
        "news_usage": news_usage,
        "news_event_intelligence": facade._as_dict(
            payload.get("news_event_intelligence") or canonical.get("news_event_intelligence")
        ),
        "news_event_intelligence_usage": facade._as_dict(payload.get("news_event_intelligence_usage")),
        "market_regime_rail": market_regime_rail,
        "news_quality_audit": news_quality,
        "risk_off_exception_policy": risk_off_exception_policy,
        "risk_off_exception_conditions": facade._as_list(payload.get("risk_off_exception_conditions")),
        "strategist_output_quality_audit": output_quality,
        "strategy_refresh_trace": {
            "summary": facade._text(refresh_trace.get("summary"), ""),
            "bullets": facade._as_list(refresh_trace.get("bullets")),
            "stages": facade._as_list(refresh_trace.get("stages")),
        },
        "strategy_horizon_feedback": horizon,
    }
