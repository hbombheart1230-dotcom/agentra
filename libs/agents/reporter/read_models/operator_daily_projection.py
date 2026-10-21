"""Operator daily visibility readout projection.

The pure parts of the operator daily summary: the per-run story fold (``build_run_contexts``, streamed in file
order exactly as before) and the post-traversal readout of ``build_operator_daily_summary_payload`` (system health
escalation, issues, recommended actions, NOOP/fallback story counters, summary lines and the ``operator_summary.v1``
body). The two day-row passes, metrics/artifact/trading-health reads, candidate and route summaries and the
policy surface snapshot stay in ``operator_visibility``. Module
helpers resolve on the injected facade module at call time; ``day_rows`` is passed through unchanged so
its truthiness check keeps the original semantics.
"""
from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List


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


def build_run_contexts(day_rows: Iterable[Dict[str, Any]], *, facade: Any) -> List[Dict[str, Any]]:
    # OOM RCA follow-up (2026-09-23): day_rows used to be pre-sorted here
    # (sorted(day_rows, key=epoch)), which required the caller to already
    # hold the whole day as a materialized list -- fine for the small
    # fixtures this was validated against, but a real busy trading day's
    # own JSON can be tens of MB, and retaining every row as a live Python
    # dict for the whole function scales linearly toward the 1GiB container
    # limit on its own, independent of the (already-fixed) unbounded
    # total-history bug. events.jsonl has exactly one active writer at a
    # time (SQLiteRuntimeOwnershipStore's single-owner lease), so file
    # order already IS chronological order for all practical purposes; the
    # final `stories.sort(key=first_epoch)` below independently
    # re-establishes correct STORY ordering regardless of fold order, and
    # within a single run_id the fold's per-stage fields only get
    # overwritten by a same-stage-same-event repeat, which does not happen
    # in this system's normal one-decision-per-run flow. So this now folds
    # directly off the iterator in file/stream order, discarding each row
    # right after folding it, instead of pre-sorting a fully materialized list.
    by_run: Dict[str, Dict[str, Any]] = {}
    for row in day_rows:
        run_id = str(row.get("run_id") or "").strip()
        if not run_id:
            continue
        ctx = by_run.setdefault(run_id, facade._run_context_default(run_id))
        epoch = int(row.get("_epoch") or 0)
        if ctx["first_epoch"] <= 0 or epoch < int(ctx["first_epoch"]):
            ctx["first_epoch"] = epoch
        if epoch > int(ctx["last_epoch"]):
            ctx["last_epoch"] = epoch

        stage = str(row.get("stage") or "").strip()
        event = str(row.get("event") or "").strip()
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}

        if stage == "strategist_llm" and event == "result":
            ctx["llm"] = dict(payload)
            continue

        if stage == "strategist" and event == "policy_resolution":
            ctx["strategist_policy_resolution"] = dict(payload)
            continue

        if stage == "decision" and event == "trace":
            packet = payload.get("decision_packet") if isinstance(payload.get("decision_packet"), dict) else {}
            trace = payload.get("trace") if isinstance(payload.get("trace"), dict) else {}
            intent = packet.get("intent") if isinstance(packet.get("intent"), dict) else {}
            why = packet.get("why") if isinstance(packet.get("why"), dict) else {}
            llm_ctx = trace.get("llm_context") if isinstance(trace.get("llm_context"), dict) else {}
            technical = why.get("technical") if isinstance(why.get("technical"), dict) else {}
            news = why.get("news") if isinstance(why.get("news"), dict) else {}
            policy = why.get("policy") if isinstance(why.get("policy"), dict) else {}
            if not technical:
                technical = llm_ctx.get("technical") if isinstance(llm_ctx.get("technical"), dict) else {}
            if not news:
                news = llm_ctx.get("news") if isinstance(llm_ctx.get("news"), dict) else {}
            if not policy:
                policy = llm_ctx.get("decision_policy") if isinstance(llm_ctx.get("decision_policy"), dict) else {}
            symbol_status = str(news.get("symbol_sentiment_status") or "").strip().lower()
            global_status = str(news.get("global_sentiment_status") or "").strip().lower()

            action = str(intent.get("action") or "").strip().upper()
            symbol = str(intent.get("symbol") or "").strip().upper()
            qty = facade._safe_int(intent.get("qty"), 0)

            if action:
                ctx["action"] = action
            if symbol:
                ctx["symbol"] = symbol
            if qty > 0:
                ctx["qty"] = qty

            reason_raw = facade._reason_text(intent, trace, ctx.get("llm") if isinstance(ctx.get("llm"), dict) else {})
            ctx["key_reason_raw"] = reason_raw
            ctx["key_reason"] = facade._humanize_reason(reason_raw)
            ctx["technical_evidence"] = facade._compact_kv_text(technical, topn=6)
            ctx["sentiment_evidence"] = facade._compact_kv_text(news, topn=6)
            ctx["policy_evidence"] = facade._compact_kv_text(policy, topn=6)
            ctx["invalidation"] = packet.get("invalidation") if isinstance(packet.get("invalidation"), dict) else {}
            ctx["news_status"] = {
                "symbol_sentiment_status": symbol_status,
                "global_sentiment_status": global_status,
            }
            if symbol_status and symbol_status != "ok":
                ctx["risk_flags"].append(f"symbol_sentiment_{symbol_status}")
            if global_status and global_status != "ok":
                ctx["risk_flags"].append(f"global_sentiment_{global_status}")
            ctx["decision"] = dict(payload)
            continue

        if stage == "decision_trace":
            inner = facade._decision_trace_inner(payload)

            if event == "strategic_frame":
                ctx["strategy_frame"] = dict(inner)
                if not str(ctx.get("key_reason_raw") or "").strip():
                    key_events = inner.get("key_events") if isinstance(inner.get("key_events"), list) else []
                    if key_events:
                        ctx["key_reason_raw"] = str(key_events[0])
                        ctx["key_reason"] = facade._humanize_reason(ctx["key_reason_raw"])
                continue

            if event == "candidate_selection":
                symbol = str(inner.get("selected_symbol") or "").strip().upper()
                if symbol:
                    ctx["symbol"] = symbol
                selected = inner.get("selected_candidate") if isinstance(inner.get("selected_candidate"), dict) else {}
                score_summary = inner.get("score_breakdown_summary") if isinstance(inner.get("score_breakdown_summary"), dict) else {}
                reason_raw = str(
                    selected.get("why")
                    or inner.get("candidate_source")
                    or ctx.get("key_reason_raw")
                    or ""
                ).strip()
                if reason_raw:
                    ctx["key_reason_raw"] = reason_raw
                    ctx["key_reason"] = facade._humanize_reason(reason_raw)
                if not str(ctx.get("technical_evidence") or "").strip():
                    technical_bits = {
                        "playbook": inner.get("playbook"),
                        "candidate_pool_size": inner.get("candidate_pool_size"),
                        "score_total": selected.get("score_total") or inner.get("top_score"),
                        "risk_score": selected.get("risk_score"),
                    }
                    if score_summary:
                        technical_bits["score_breakdown"] = facade._compact_kv_text(score_summary, topn=5)
                    ctx["technical_evidence"] = facade._compact_kv_text(technical_bits, topn=6)
                continue

            if event == "entry_exit_decision":
                symbol = str(inner.get("selected_symbol") or "").strip().upper()
                if symbol:
                    ctx["symbol"] = symbol
                exit_reason = str(inner.get("exit_reason") or "").strip()
                entry_reason = str(inner.get("entry_reason") or "").strip()
                reason_raw = exit_reason or entry_reason
                if reason_raw:
                    ctx["key_reason_raw"] = reason_raw
                    ctx["key_reason"] = facade._humanize_reason(reason_raw)
                thresholds = inner.get("thresholds") if isinstance(inner.get("thresholds"), dict) else {}
                if thresholds:
                    ctx["technical_evidence"] = facade._compact_kv_text(thresholds, topn=6)
                if bool(inner.get("min_hold_blocked")):
                    ctx["risk_flags"].append("min_hold_blocked")
                if bool(inner.get("sell_cooldown_blocked")):
                    ctx["risk_flags"].append("sell_cooldown_blocked")
                continue

        if stage == "scanner" and event == "candidate_selection_reason":
            ctx["scanner_selection"] = dict(payload)
            continue

        if stage == "scanner" and event == "selection_output":
            existing = ctx.get("scanner_selection") if isinstance(ctx.get("scanner_selection"), dict) else {}
            ctx["scanner_selection"] = {**dict(existing), **dict(payload)}
            continue

        if stage == "monitor" and event == "entry_decision_detail":
            ctx["monitor_entry"] = dict(payload)
            continue

        if stage == "commander_router" and event in {"route", "route_selected", "end"}:
            existing = ctx.get("commander_route") if isinstance(ctx.get("commander_route"), dict) else {}
            merged = {**dict(existing), **dict(payload)}
            route_obs = payload.get("route_observability") if isinstance(payload.get("route_observability"), dict) else {}
            if route_obs:
                merged.update(dict(route_obs))
            ctx["commander_route"] = merged
            continue

        if stage == "execute_from_packet" and event == "verdict":
            ctx["verdict"] = dict(payload)
            allowed = payload.get("allowed")
            if allowed is False:
                ctx["execution_status"] = "BLOCKED"
                ctx["guard_status"] = "intervened"
                ctx["guard_reason"] = str(payload.get("reason") or "blocked_by_guard")
                ctx["guard_reason_human"] = facade._humanize_reason(ctx.get("guard_reason"))
            continue

        if stage == "execute_from_packet" and event == "execution":
            order = payload.get("order") if isinstance(payload.get("order"), dict) else {}
            ex_payload = payload.get("payload") if isinstance(payload.get("payload"), dict) else {}
            action = str(order.get("action") or "").strip().upper()
            symbol = str(order.get("symbol") or "").strip().upper()
            qty = facade._safe_int(order.get("qty"), 0)
            if action:
                ctx["action"] = action
            if symbol:
                ctx["symbol"] = symbol
            if qty > 0:
                ctx["qty"] = qty

            broker_ok = facade._broker_code_success(ex_payload.get("broker_code"))
            if broker_ok is True:
                ctx["execution_status"] = "EXECUTED_OK"
            elif broker_ok is False:
                ctx["execution_status"] = "EXECUTED_FAIL"
            else:
                ctx["execution_status"] = "EXECUTED"
            ctx["execution"] = dict(payload)
            continue

        if stage == "commander_router" and event == "intervention":
            p_type = str(payload.get("type") or "operator_intervention").strip()
            if p_type:
                ctx["operator_intervention"].append(p_type)
            continue

        if event == "error":
            st = str(row.get("stage") or "unknown").strip() or "unknown"
            ctx["risk_flags"].append(f"error:{st}")
            continue

        if stage == "commander_router" and event == "transition":
            transition = str(payload.get("transition") or "").strip().lower()
            if transition == "cooldown":
                ctx["risk_flags"].append("cooldown_transition")

    stories: List[Dict[str, Any]] = []
    for ctx in by_run.values():
        action = str(ctx.get("action") or "").strip().upper()
        if not action:
            llm = ctx.get("llm") if isinstance(ctx.get("llm"), dict) else {}
            action = str(llm.get("intent_action") or "").strip().upper()
            if action:
                ctx["action"] = action

        if not str(ctx.get("execution_status") or "").strip() or str(ctx.get("execution_status")) == "UNKNOWN":
            if str(ctx.get("guard_status")) == "intervened":
                ctx["execution_status"] = "BLOCKED"
            elif action == "NOOP":
                ctx["execution_status"] = "NOOP"
            elif action in ("BUY", "SELL"):
                ctx["execution_status"] = "INTENT_ONLY"
            else:
                ctx["execution_status"] = "UNKNOWN"

        if not str(ctx.get("guard_reason") or "").strip():
            ctx["guard_reason"] = "none"
        ctx["guard_reason_human"] = facade._humanize_reason(ctx.get("guard_reason") or "none")
        if not str(ctx.get("key_reason") or "").strip():
            llm = ctx.get("llm") if isinstance(ctx.get("llm"), dict) else {}
            raw_reason = str(llm.get("intent_reason") or llm.get("intent_rationale") or "unspecified")
            ctx["key_reason_raw"] = raw_reason

        normalized_reason = facade._normalize_reason_code(
            ctx.get("key_reason_raw"),
            action=str(ctx.get("action") or "").strip().upper(),
            execution_status=str(ctx.get("execution_status") or "").strip().upper(),
            guard_status=str(ctx.get("guard_status") or "").strip().lower(),
        )
        ctx["key_reason_raw"] = normalized_reason
        ctx["key_reason"] = facade._humanize_reason(normalized_reason)

        monitor_entry = ctx.get("monitor_entry") if isinstance(ctx.get("monitor_entry"), dict) else {}
        no_trade_surface = monitor_entry.get("no_trade_surface") if isinstance(monitor_entry.get("no_trade_surface"), dict) else {}
        scanner_handoff = monitor_entry.get("scanner_monitor_handoff") if isinstance(monitor_entry.get("scanner_monitor_handoff"), dict) else {}
        scanner_selection = ctx.get("scanner_selection") if isinstance(ctx.get("scanner_selection"), dict) else {}
        strategist_resolution = (
            ctx.get("strategist_policy_resolution") if isinstance(ctx.get("strategist_policy_resolution"), dict) else {}
        )
        commander_route = ctx.get("commander_route") if isinstance(ctx.get("commander_route"), dict) else {}
        if no_trade_surface:
            ctx["no_trade_surface"] = dict(no_trade_surface)
            dominant_blocker = str(no_trade_surface.get("dominant_blocker") or no_trade_surface.get("no_trade_reason_code") or "").strip()
            if dominant_blocker and normalized_reason in {"NO_CANDIDATE", "GUARD_BLOCK", "unspecified"}:
                ctx["key_reason_raw"] = dominant_blocker
                ctx["key_reason"] = facade._humanize_reason(dominant_blocker)
            ctx["decision_outcome"] = str(no_trade_surface.get("decision_outcome") or "")
            ctx["dominant_blocker"] = dominant_blocker
            ctx["near_ready_flag"] = bool(no_trade_surface.get("near_ready_flag"))
            ctx["distance_to_ready_text"] = facade._compact_distance_to_ready_text(no_trade_surface.get("distance_to_ready"))
            ctx["no_trade_summary"] = str(no_trade_surface.get("no_trade_reason_summary") or "")
        merged_handoff = facade._merge_scanner_handoff_with_selection(scanner_handoff, scanner_selection)
        if merged_handoff:
            ctx["scanner_monitor_handoff"] = merged_handoff
            if not str(ctx.get("symbol") or "").strip():
                ctx["symbol"] = str(
                    merged_handoff.get("scanner_selected_symbol")
                    or merged_handoff.get("selected_symbol")
                    or ""
                ).strip().upper()
        if strategist_resolution:
            ctx["strategist_policy_resolution"] = dict(strategist_resolution)
        if commander_route:
            ctx["commander_route"] = dict(commander_route)

        if not str(ctx.get("final_outcome") or "").strip():
            if str(ctx.get("execution_status")) == "EXECUTED_OK":
                ctx["final_outcome"] = "order accepted"
            elif str(ctx.get("execution_status")) == "EXECUTED_FAIL":
                ctx["final_outcome"] = "order rejected"
            elif str(ctx.get("execution_status")) == "BLOCKED":
                ctx["final_outcome"] = f"blocked:{ctx.get('guard_reason')}"
            elif no_trade_surface:
                ctx["final_outcome"] = str(no_trade_surface.get("no_trade_reason_summary") or "no trade")
            elif str(ctx.get("execution_status")) == "NOOP":
                ctx["final_outcome"] = "no trade"
            else:
                ctx["final_outcome"] = str(ctx.get("execution_status")).lower()

        if ctx.get("operator_intervention"):
            dedup = []
            seen = set()
            for item in ctx.get("operator_intervention") or []:
                s = str(item)
                if s and s not in seen:
                    seen.add(s)
                    dedup.append(s)
            ctx["operator_intervention"] = dedup

        risk_flags = [str(x) for x in (ctx.get("risk_flags") or []) if str(x).strip()]
        if str(ctx.get("execution_status")) == "EXECUTED_FAIL":
            risk_flags.append("broker_reject")
        if str(ctx.get("guard_status")) == "intervened":
            risk_flags.append("guard_block")
        ctx["risk_flags"] = sorted(set(risk_flags))

        stories.append(ctx)

    stories.sort(key=lambda x: int(x.get("first_epoch") or 0))
    return stories
