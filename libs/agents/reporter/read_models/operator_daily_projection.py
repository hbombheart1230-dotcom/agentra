"""Operator daily visibility readout projection.

The post-traversal readout of ``build_operator_daily_summary_payload`` (system health
escalation, issues, recommended actions, NOOP/fallback story counters, summary lines and the ``operator_summary.v1``
body). The two day-row passes, metrics/artifact/trading-health reads, candidate and route summaries and the
policy surface snapshot stay in ``operator_visibility``. Module
helpers resolve on the injected facade module at call time; ``day_rows`` is passed through unchanged so
its truthiness check keeps the original semantics.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List


def build_daily_summary_readout(
    *,
    metrics: Any,
    duplicate_execution_total: Any,
    guard_precedence_violation_total: Any,
    m30_policy: Any,
    m31_slo: Any,
    day_rows: Any,
    trading_health_status: Any,
    blocked_reason_counts: Any,
    run_ids_seen: Any,
    run_stories: Any,
    noop_reason_counts: Any,
    fallback_signal_status_counts: Any,
    action_counts: Any,
    candidate_decision_summary: Any,
    executions_total: Any,
    executions_ok: Any,
    executions_fail: Any,
    operator_intervention_total: Any,
    cooldown_transition_total: Any,
    route_summary: Any,
    target_day: Any,
    freshness: Any,
    events_path: Any,
    metrics_dir: Any,
    m30_post_dir: Any,
    m30_go_dir: Any,
    m31_dir: Any,
    strategy_counts: Any,
    m30_signoff: Any,
    stage_error_counts: Any,
    facade: Any,
) -> Any:
    """Daily health/issues/actions/summary readout and operator_summary.v1 body from already computed inputs."""
    metrics_exec = metrics.get("execution") if isinstance(metrics.get("execution"), dict) else {}
    metrics_broker = metrics.get("broker_api") if isinstance(metrics.get("broker_api"), dict) else {}
    metrics_commander = metrics.get("commander_resilience") if isinstance(metrics.get("commander_resilience"), dict) else {}

    intents_created = facade._safe_int(metrics_exec.get("intents_created"), 0)
    intents_blocked = facade._safe_int(metrics_exec.get("intents_blocked"), 0)
    blocked_rate = (float(intents_blocked) / float(intents_created)) if intents_created > 0 else 0.0
    api_429_rate = facade._safe_float(metrics_broker.get("api_429_rate"), 0.0)

    issues: List[Dict[str, str]] = []
    health = "GREEN"

    def _raise_health(level: str) -> None:
        nonlocal health
        order = {"GREEN": 0, "YELLOW": 1, "RED": 2}
        if order.get(level, 0) > order.get(health, 0):
            health = level

    if duplicate_execution_total > 0:
        _raise_health("RED")
        issues.append({"code": "duplicate_execution_detected", "severity": "RED", "detail": f"duplicate_execution={duplicate_execution_total}"})
    if guard_precedence_violation_total > 0:
        _raise_health("RED")
        issues.append({"code": "guard_precedence_violation", "severity": "RED", "detail": f"guard_precedence_violation={guard_precedence_violation_total}"})
    if api_429_rate > 0.20:
        _raise_health("YELLOW")
        issues.append({"code": "high_api_error_rate", "severity": "YELLOW", "detail": f"api_429_rate={api_429_rate:.2%}"})
    if intents_created >= 5 and blocked_rate > 0.60:
        _raise_health("YELLOW")
        issues.append({"code": "excessive_blocked_orders", "severity": "YELLOW", "detail": f"blocked_rate={blocked_rate:.2%} ({intents_blocked}/{intents_created})"})

    escalation_level = str(m30_policy.get("escalation_level") or "").strip().lower()
    if escalation_level == "incident":
        _raise_health("RED")
        issues.append({"code": "policy_escalation_incident", "severity": "RED", "detail": "m30_post_golive escalation_level=incident"})
    elif escalation_level == "watch":
        _raise_health("YELLOW")
        issues.append({"code": "policy_escalation_watch", "severity": "YELLOW", "detail": "m30_post_golive escalation_level=watch"})

    if m31_slo and not bool(m31_slo.get("ok")):
        slo_payload = m31_slo.get("slo") if isinstance(m31_slo.get("slo"), dict) else {}
        m31_event_total = facade._safe_int(slo_payload.get("event_total"), 0)
        m31_run_total = facade._safe_int(slo_payload.get("run_total"), 0)
        m31_unmeasurable = bool(day_rows and m31_event_total == 0 and m31_run_total == 0)
        if m31_unmeasurable:
            _raise_health("YELLOW")
            issues.append(
                {
                    "code": "slo_incident_artifact_unmeasurable",
                    "severity": "YELLOW",
                    "detail": "m31_slo_incident has no measurable events/runs while operator events exist; treating as stale diagnostic artifact, not live runtime failure",
                }
            )
        else:
            _raise_health("RED")
            issues.append({"code": "slo_incident_gate_failed", "severity": "RED", "detail": f"m31_slo_incident failure_total={facade._safe_int(m31_slo.get('failure_total'), 0)}"})
    trading_health_level = str(trading_health_status.get("trading_health_level") or "").strip().upper()
    trading_health_detail = "; ".join(
        str(x) for x in list(trading_health_status.get("reasoning") or [])[:2] if str(x).strip()
    )
    if trading_health_level == "RED":
        _raise_health("RED")
        issues.append({"code": "trading_health_red", "severity": "RED", "detail": trading_health_detail})
    elif trading_health_level == "YELLOW":
        _raise_health("YELLOW")
        issues.append({"code": "trading_health_yellow", "severity": "YELLOW", "detail": trading_health_detail})
    if not issues:
        issues.append({"code": "none", "severity": "GREEN", "detail": "no critical or warning issues detected"})

    recommended_actions: List[str] = []
    issue_codes = {str(i.get("code") or "") for i in issues}
    if "duplicate_execution_detected" in issue_codes or "guard_precedence_violation" in issue_codes:
        recommended_actions.append("Pause auto execution and run guard/idempotency diagnostic checks before next session.")
    if "high_api_error_rate" in issue_codes:
        recommended_actions.append("Lower request burst, verify broker/API quota, and inspect 429 retry configuration.")
    if "excessive_blocked_orders" in issue_codes:
        recommended_actions.append("Review allowlist, notional limits, and decision thresholds causing frequent guard blocks.")
    if "policy_escalation_incident" in issue_codes:
        recommended_actions.append("Switch to manual approval only and complete incident review with clear owner/action items.")
    if "slo_incident_artifact_unmeasurable" in issue_codes:
        recommended_actions.append("Refresh the SLO incident artifact from the current event log before treating it as a runtime failure.")
    if "trading_health_red" in issue_codes:
        recommended_actions.append("Reduce or pause new entries until weak intraday playbook/exit combinations recover.")
    if "trading_health_yellow" in issue_codes:
        recommended_actions.append("Keep candidate scope narrow until win-rate and average return recover.")
    if "none" in issue_codes:
        recommended_actions.append("Continue current configuration and monitor next session for regression signals.")
    if not recommended_actions:
        recommended_actions.append("Inspect top issues and run closeout checks before enabling broader automation.")

    top_block_reason = blocked_reason_counts.most_common(1)
    run_total = len(run_ids_seen)
    blocked_total = int(sum(int(v) for v in blocked_reason_counts.values()))
    llm_metrics = metrics.get("strategist_llm") if isinstance(metrics.get("strategist_llm"), dict) else {}
    llm_total = facade._safe_int(llm_metrics.get("total"), 0)
    llm_success_rate = facade._safe_float(llm_metrics.get("success_rate"), 0.0)

    for story in run_stories:
        action = str(story.get("action") or "").strip().upper()
        execution_status = str(story.get("execution_status") or "").strip().upper()
        if action == "NOOP" or execution_status == "NOOP":
            reason_raw = str(story.get("key_reason_raw") or story.get("key_reason") or "unspecified").strip() or "unspecified"
            noop_reason_counts[reason_raw] += 1
        news_status = story.get("news_status") if isinstance(story.get("news_status"), dict) else {}
        symbol_status = str(news_status.get("symbol_sentiment_status") or "").strip().lower()
        global_status = str(news_status.get("global_sentiment_status") or "").strip().lower()
        if symbol_status and symbol_status != "ok":
            fallback_signal_status_counts[f"symbol_sentiment_status:{symbol_status}"] += 1
        if global_status and global_status != "ok":
            fallback_signal_status_counts[f"global_sentiment_status:{global_status}"] += 1

    blocked_reason_top_human = facade._render_reason_top(blocked_reason_counts, topn=5)
    noop_reason_top_human = facade._render_reason_top(noop_reason_counts, topn=5)
    fallback_signal_status_top = facade._render_reason_top(fallback_signal_status_counts, topn=5)

    if not action_counts:
        for story in run_stories:
            action = str(story.get("action") or "").strip().upper()
            if action:
                action_counts[action] += 1

    llm_summary = (
        f"LLM success_rate={llm_success_rate:.2%} ({llm_total} calls)"
        if llm_total > 0
        else "LLM success_rate=not_measured (0 metric events)"
    )
    candidate_rejected_total = int(candidate_decision_summary.get("candidate_rejected_total") or 0)
    candidate_noop_total = int(candidate_decision_summary.get("candidate_noop_total") or 0)
    summary_lines = [
        f"{facade._health_badge(health)} runs={run_total}, executions={executions_total} (ok={executions_ok}, fail={executions_fail}), execution_guard_blocks={blocked_total}, commander_rejections={candidate_rejected_total}.",
        f"Top guard block: {facade._humanize_reason(top_block_reason[0][0])} ({top_block_reason[0][1]})" if top_block_reason else "Top guard block: none",
        f"{llm_summary}, interventions={operator_intervention_total}, cooldowns={cooldown_transition_total}.",
    ]
    route_selected_total = dict(route_summary.get("route_selected_total") or {})
    if route_selected_total:
        summary_lines.append(f"Route source={route_summary.get('route_source') or 'canonical_commander_preferred'} route_total={json.dumps(route_selected_total, ensure_ascii=False)}")
    summary_lines.append("Narrative display policy: exit-first for SELL/EXIT, entry-first for BUY/WAIT/NO_TRADE.")

    reasoning_lines = [str(i.get("detail") or "") for i in issues if str(i.get("detail") or "").strip()]
    system_health_status = {"system_health_level": health, "reasoning": reasoning_lines, "recommended_action": recommended_actions[:3]}

    out: Dict[str, Any] = {
        "schema_version": "operator_summary.v1",
        "day": target_day,
        "generated_at": freshness["generated_at"],
        "source_run_count": int(freshness["source_run_count"]),
        "latest_run_id": freshness["latest_run_id"],
        "latest_run_ts": freshness["latest_run_ts"],
        "data_freshness": facade.build_data_freshness(
            generated_at=freshness["generated_at"],
            source_run_count=freshness["source_run_count"],
            latest_run_id=freshness["latest_run_id"],
            latest_run_ts=freshness["latest_run_ts"],
            stale=False,
        ),
        "inputs": {
            "event_log_path": str(events_path),
            "metrics_json_path": str((metrics_dir / f"metrics_{target_day}.json")),
            "m30_post_golive_json_path": str((m30_post_dir / f"m30_post_golive_policy_{target_day}.json")),
            "m30_golive_json_path": str((m30_go_dir / f"m30_final_golive_signoff_{target_day}.json")),
            "m31_slo_incident_json_path": str((m31_dir / f"m31_slo_incident_{target_day}.json")),
        },
        "executive_summary": {"system_status": health, "summary_lines": summary_lines},
        "system_health_status": system_health_status,
        "trading_health_status": trading_health_status,
        "trading_activity_summary": {
            "run_total": int(run_total),
            "decision_action_counts": dict(action_counts),
            "strategy_counts": dict(strategy_counts),
            "executions_total": int(executions_total),
            "executions_ok_total": int(executions_ok),
            "executions_fail_total": int(executions_fail),
            "blocked_total": int(blocked_total),
            "execution_guard_blocked_total": int(blocked_total),
            "commander_candidate_rejected_total": candidate_rejected_total,
            "commander_candidate_noop_total": candidate_noop_total,
            "blocked_reason_top": dict(blocked_reason_counts.most_common(5)),
            "blocked_reason_top_human": blocked_reason_top_human,
            "noop_reason_top_human": noop_reason_top_human,
            "fallback_signal_status_top_human": fallback_signal_status_top,
        },
        "candidate_decision_summary": candidate_decision_summary,
        "route_summary": {
            "route_source": str(route_summary.get("route_source") or "canonical_commander_preferred"),
            "route_source_run_count": int(route_summary.get("route_source_run_count") or 0),
            "route_source_missing_count": int(route_summary.get("route_source_missing_count") or 0),
            "route_source_breakdown": dict(route_summary.get("route_source_breakdown") or {}),
            "route_selected_total": dict(route_summary.get("route_selected_total") or {}),
            "strategy_generation_mode_total": dict(route_summary.get("strategy_generation_mode_total") or {}),
            "strategist_fallback_total": int(route_summary.get("strategist_fallback_total") or 0),
        },
        "route_provenance": facade.build_route_provenance(route_summary),
        "safety_guard_interventions": {
            "blocked_total": int(blocked_total),
            "execution_guard_blocked_total": int(blocked_total),
            "blocked_reason_top": dict(blocked_reason_counts.most_common(5)),
            "blocked_reason_top_human": blocked_reason_top_human,
            "operator_intervention_total": int(operator_intervention_total),
            "cooldown_transition_total": int(cooldown_transition_total),
            "duplicate_execution_total": int(duplicate_execution_total),
            "guard_precedence_violation_total": int(guard_precedence_violation_total),
        },
        "top_issues": issues[:10],
        "recommended_operator_actions": recommended_actions[:5],
        "narrative_axis_policy": facade.narrative_axis_policy(),
        "raw_snapshot": {
            "metrics_execution": metrics_exec,
            "metrics_commander_resilience": metrics_commander,
            "metrics_broker_api": metrics_broker,
            "m30_post_golive": m30_policy,
            "m30_golive": m30_signoff,
            "m31_slo_incident": m31_slo,
            "stage_error_top": dict(stage_error_counts.most_common(5)),
            "run_story_total": len(run_stories),
        },
    }
    return out
