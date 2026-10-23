"""Metrics report aggregation projection.

The pure per-event counter fold and the ``metrics.v1`` summary assembly from ``generate_metrics_report``.
``resolve_runtime_write_path``, directory creation, the event reader (``iter_jsonl_events``/``_iter_events``),
row building and day selection, ``build_commander_route_summary`` (reads report files), the clock
(``generated_at`` is passed in), freshness/provenance, Markdown rendering and both file writes stay in
``metrics_report_generator``. Extractor/aggregator helpers resolve on the injected facade module at call time.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict

from libs.agents.reporter.read_models import metrics_event_fold as _event_fold


def aggregate_day_metrics(
    *,
    day_rows: Any,
    facade: Any,
) -> Any:
    """Fold the selected day's event rows into the metrics counters/summaries (pure, original order)."""
    run_ids = {str(r.get("run_id") or "") for r in day_rows if r.get("run_id")}

    intents_created = 0
    intents_approved = 0
    intents_blocked = 0
    intents_executed = 0
    blocks_by_reason: Counter[str] = Counter()
    api_errors_by_id: Counter[str] = Counter()
    api_429_total = 0
    llm_fold = _event_fold.new_llm_fold()
    skill_hydration_total = 0
    skill_hydration_used_runner_total = 0
    skill_hydration_fallback_hint_total = 0
    skill_hydration_errors_total_sum = 0
    skill_hydration_runner_source_total: Counter[str] = Counter()
    skill_hydration_attempted_total: Counter[str] = Counter()
    skill_hydration_ready_total: Counter[str] = Counter()
    skill_hydration_errors_by_skill: Counter[str] = Counter()
    commander_total = 0
    commander_cooldown_transition_total = 0
    commander_intervention_total = 0
    commander_error_total = 0
    commander_transition_total: Counter[str] = Counter()
    commander_runtime_status_total: Counter[str] = Counter()
    commander_cooldown_reason_total: Counter[str] = Counter()
    portfolio_guard_total = 0
    portfolio_guard_applied_total = 0
    portfolio_guard_approved_total_sum = 0
    portfolio_guard_blocked_total_sum = 0
    portfolio_guard_reason_total: Counter[str] = Counter()
    monitor_total = 0
    monitor_exit_policy_enabled_total = 0
    monitor_exit_evaluated_total = 0
    monitor_exit_trigger_total = 0
    monitor_exit_reason_total: Counter[str] = Counter()
    monitor_position_sizing_enabled_total = 0
    monitor_position_sizing_evaluated_total = 0
    monitor_position_sizing_computed_qty_sum = 0
    monitor_position_sizing_zero_qty_total = 0
    monitor_position_sizing_reason_total: Counter[str] = Counter()
    no_trade_reason_total: Counter[str] = Counter()
    dominant_blocker_total: Counter[str] = Counter()
    strategist_mode_total: Counter[str] = Counter()
    route_selected_total: Counter[str] = Counter()
    scanner_monitor_alignment_total: Counter[str] = Counter()
    near_ready_total = 0
    strategist_fallback_total = 0
    pre_intent_wait_total = 0
    pre_intent_noop_total = 0
    guard_block_total = 0
    route_selected_by_run: Dict[str, str] = {}
    latest_run_id = ""
    latest_run_epoch = 0

    for r in day_rows:
        stage = str(r.get("stage") or "")
        event = str(r.get("event") or "")
        run_id = str(r.get("run_id") or "").strip()
        epoch = int(r.get("_epoch") or 0)
        if run_id and epoch >= latest_run_epoch:
            latest_run_epoch = epoch
            latest_run_id = run_id

        if stage == "decision" and event == "trace":
            action = facade._extract_intent_action(r)
            if action in {"BUY", "SELL"}:
                intents_created += 1

        if stage == "execute_from_packet" and event == "verdict":
            payload = r.get("payload") if isinstance(r.get("payload"), dict) else {}
            allowed = payload.get("allowed")
            if allowed is True:
                intents_approved += 1
            elif allowed is False:
                intents_blocked += 1
                blocks_by_reason[facade._extract_guard_reason(r)] += 1

        if stage == "execute_from_packet" and event == "execution":
            intents_executed += 1

        if event == "error":
            api_errors_by_id[facade._extract_api_id(r)] += 1
            if facade._is_429_error_row(r):
                api_429_total += 1

        if stage == "strategist_llm" and event == "result":
            _event_fold.fold_llm_result(r, llm_fold=llm_fold)

        if stage == "strategist" and event == "policy_resolution":
            payload = r.get("payload") if isinstance(r.get("payload"), dict) else {}
            mode = str(payload.get("strategy_generation_mode") or "").strip()
            if mode:
                strategist_mode_total[mode] += 1
            if bool(payload.get("fallback_used")):
                strategist_fallback_total += 1

        if stage == "monitor" and event == "entry_decision_detail":
            payload = r.get("payload") if isinstance(r.get("payload"), dict) else {}
            no_trade = payload.get("no_trade_surface") if isinstance(payload.get("no_trade_surface"), dict) else {}
            handoff = payload.get("scanner_monitor_handoff") if isinstance(payload.get("scanner_monitor_handoff"), dict) else {}
            if no_trade:
                reason_code = str(no_trade.get("no_trade_reason_code") or "").strip()
                dominant_blocker = str(no_trade.get("dominant_blocker") or "").strip()
                if reason_code:
                    no_trade_reason_total[reason_code] += 1
                if dominant_blocker:
                    dominant_blocker_total[dominant_blocker] += 1
                if bool(no_trade.get("near_ready_flag")):
                    near_ready_total += 1
                no_trade_stage = str(no_trade.get("no_trade_stage") or "").strip()
                if no_trade_stage == "pre_intent_wait":
                    pre_intent_wait_total += 1
                elif no_trade_stage == "pre_intent_noop":
                    pre_intent_noop_total += 1
                elif no_trade_stage == "guard_block":
                    guard_block_total += 1
            alignment = str(handoff.get("scanner_vs_monitor_alignment") or "").strip()
            if alignment:
                scanner_monitor_alignment_total[alignment] += 1

        if stage == "skill_hydration" and event == "summary":
            payload = r.get("payload") if isinstance(r.get("payload"), dict) else {}
            skill_hydration_total += 1
            if payload.get("used_runner") is True:
                skill_hydration_used_runner_total += 1

            runner_source = str(payload.get("runner_source") or "unknown")
            skill_hydration_runner_source_total[runner_source] += 1

            errors_total = facade._to_non_negative_int(payload.get("errors_total"))
            skill_hydration_errors_total_sum += errors_total

            fallback_hint = bool(payload.get("fallback_hint")) or errors_total > 0
            if fallback_hint:
                skill_hydration_fallback_hint_total += 1

            attempted = payload.get("attempted")
            if isinstance(attempted, dict):
                for k, v in attempted.items():
                    skill_hydration_attempted_total[str(k)] += facade._to_non_negative_int(v)

            ready = payload.get("ready")
            if isinstance(ready, dict):
                for k, v in ready.items():
                    skill_hydration_ready_total[str(k)] += facade._to_non_negative_int(v)

            errors = payload.get("errors")
            if isinstance(errors, list):
                for e in errors:
                    skill_hydration_errors_by_skill[facade._extract_skill_error_tag(e)] += 1

        if stage == "commander_router":
            payload = r.get("payload") if isinstance(r.get("payload"), dict) else {}
            commander_total += 1

            if event in {"route_selected", "end"} and run_id:
                route_obs = payload.get("route_observability") if isinstance(payload.get("route_observability"), dict) else {}
                route_selected = str(
                    payload.get("route_selected")
                    or route_obs.get("route_selected")
                    or ""
                ).strip()
                if route_selected:
                    route_selected_by_run[run_id] = route_selected

            status = str(payload.get("status") or "").strip()
            if status:
                commander_runtime_status_total[status] += 1

            pg = payload.get("portfolio_guard")
            if isinstance(pg, dict):
                portfolio_guard_total += 1
                if pg.get("applied") is True:
                    portfolio_guard_applied_total += 1
                portfolio_guard_approved_total_sum += facade._to_non_negative_int(pg.get("approved_total"))
                portfolio_guard_blocked_total_sum += facade._to_non_negative_int(pg.get("blocked_total"))
                reason_counts = pg.get("blocked_reason_counts")
                if isinstance(reason_counts, dict):
                    for k, v in reason_counts.items():
                        portfolio_guard_reason_total[str(k)] += facade._to_non_negative_int(v)

            if event == "transition":
                tr = str(payload.get("transition") or "unknown").strip().lower() or "unknown"
                commander_transition_total[tr] += 1
                if tr == "cooldown" or str(payload.get("reason") or "") == "cooldown_active":
                    commander_cooldown_transition_total += 1

            if event == "intervention":
                commander_intervention_total += 1

            if event == "error":
                commander_error_total += 1

            if event == "resilience":
                reason = str(payload.get("reason") or "unknown").strip() or "unknown"
                commander_cooldown_reason_total[reason] += 1

        if stage == "monitor" and event == "summary":
            payload = r.get("payload") if isinstance(r.get("payload"), dict) else {}
            monitor_total += 1

            if payload.get("exit_policy_enabled") is True:
                monitor_exit_policy_enabled_total += 1
            if payload.get("exit_evaluated") is True:
                monitor_exit_evaluated_total += 1
            if payload.get("exit_triggered") is True:
                monitor_exit_trigger_total += 1

            exit_reason = str(payload.get("exit_reason") or "").strip()
            if exit_reason:
                monitor_exit_reason_total[exit_reason] += 1

            if payload.get("position_sizing_enabled") is True:
                monitor_position_sizing_enabled_total += 1
            if payload.get("position_sizing_evaluated") is True:
                monitor_position_sizing_evaluated_total += 1

            sizing_qty = facade._to_non_negative_int(payload.get("position_sizing_qty"))
            monitor_position_sizing_computed_qty_sum += sizing_qty
            if payload.get("position_sizing_evaluated") is True and sizing_qty == 0:
                monitor_position_sizing_zero_qty_total += 1

            sizing_reason = str(payload.get("position_sizing_reason") or "").strip()
            if sizing_reason:
                monitor_position_sizing_reason_total[sizing_reason] += 1

    llm_total = llm_fold["llm_total"]
    llm_ok_total = llm_fold["llm_ok_total"]
    llm_fail_total = llm_fold["llm_fail_total"]
    llm_circuit_open_total = llm_fold["llm_circuit_open_total"]
    llm_prompt_tokens_total = llm_fold["llm_prompt_tokens_total"]
    llm_completion_tokens_total = llm_fold["llm_completion_tokens_total"]
    llm_total_tokens_total = llm_fold["llm_total_tokens_total"]
    llm_estimated_cost_usd_total = llm_fold["llm_estimated_cost_usd_total"]
    llm_error_by_type = llm_fold["llm_error_by_type"]
    llm_prompt_version_total = llm_fold["llm_prompt_version_total"]
    llm_schema_version_total = llm_fold["llm_schema_version_total"]
    llm_circuit_state_total = llm_fold["llm_circuit_state_total"]
    llm_latency_ms_values = llm_fold["llm_latency_ms_values"]
    llm_attempt_values = llm_fold["llm_attempt_values"]
    latency = facade._latency_summary(day_rows)
    llm_latency_ms = facade._numeric_summary(llm_latency_ms_values)
    llm_attempts = facade._numeric_summary(llm_attempt_values)
    llm_success_rate = (float(llm_ok_total) / float(llm_total)) if llm_total > 0 else 0.0
    llm_circuit_open_rate = (float(llm_circuit_open_total) / float(llm_total)) if llm_total > 0 else 0.0
    api_error_total = int(sum(int(v) for v in api_errors_by_id.values()))
    api_429_rate = (float(api_429_total) / float(api_error_total)) if api_error_total > 0 else 0.0
    skill_hydration_fallback_rate = (
        float(skill_hydration_fallback_hint_total) / float(skill_hydration_total)
        if skill_hydration_total > 0
        else 0.0
    )
    return {
        "run_ids": run_ids,
        "latest_run_id": latest_run_id,
        "latest_run_epoch": latest_run_epoch,
        "intents_created": intents_created,
        "intents_approved": intents_approved,
        "intents_blocked": intents_blocked,
        "intents_executed": intents_executed,
        "blocks_by_reason": blocks_by_reason,
        "latency": latency,
        "llm_total": llm_total,
        "llm_ok_total": llm_ok_total,
        "llm_fail_total": llm_fail_total,
        "llm_success_rate": llm_success_rate,
        "llm_circuit_open_total": llm_circuit_open_total,
        "llm_circuit_open_rate": llm_circuit_open_rate,
        "llm_circuit_state_total": llm_circuit_state_total,
        "llm_latency_ms": llm_latency_ms,
        "llm_attempts": llm_attempts,
        "llm_error_by_type": llm_error_by_type,
        "llm_prompt_version_total": llm_prompt_version_total,
        "llm_schema_version_total": llm_schema_version_total,
        "llm_prompt_tokens_total": llm_prompt_tokens_total,
        "llm_completion_tokens_total": llm_completion_tokens_total,
        "llm_total_tokens_total": llm_total_tokens_total,
        "llm_estimated_cost_usd_total": llm_estimated_cost_usd_total,
        "skill_hydration_total": skill_hydration_total,
        "skill_hydration_used_runner_total": skill_hydration_used_runner_total,
        "skill_hydration_fallback_hint_total": skill_hydration_fallback_hint_total,
        "skill_hydration_fallback_rate": skill_hydration_fallback_rate,
        "skill_hydration_errors_total_sum": skill_hydration_errors_total_sum,
        "skill_hydration_runner_source_total": skill_hydration_runner_source_total,
        "skill_hydration_attempted_total": skill_hydration_attempted_total,
        "skill_hydration_ready_total": skill_hydration_ready_total,
        "skill_hydration_errors_by_skill": skill_hydration_errors_by_skill,
        "commander_total": commander_total,
        "commander_cooldown_transition_total": commander_cooldown_transition_total,
        "commander_intervention_total": commander_intervention_total,
        "commander_error_total": commander_error_total,
        "commander_transition_total": commander_transition_total,
        "commander_runtime_status_total": commander_runtime_status_total,
        "commander_cooldown_reason_total": commander_cooldown_reason_total,
        "portfolio_guard_total": portfolio_guard_total,
        "portfolio_guard_applied_total": portfolio_guard_applied_total,
        "portfolio_guard_approved_total_sum": portfolio_guard_approved_total_sum,
        "portfolio_guard_blocked_total_sum": portfolio_guard_blocked_total_sum,
        "portfolio_guard_reason_total": portfolio_guard_reason_total,
        "monitor_total": monitor_total,
        "monitor_exit_policy_enabled_total": monitor_exit_policy_enabled_total,
        "monitor_exit_evaluated_total": monitor_exit_evaluated_total,
        "monitor_exit_trigger_total": monitor_exit_trigger_total,
        "monitor_exit_reason_total": monitor_exit_reason_total,
        "monitor_position_sizing_enabled_total": monitor_position_sizing_enabled_total,
        "monitor_position_sizing_evaluated_total": monitor_position_sizing_evaluated_total,
        "monitor_position_sizing_computed_qty_sum": monitor_position_sizing_computed_qty_sum,
        "monitor_position_sizing_zero_qty_total": monitor_position_sizing_zero_qty_total,
        "monitor_position_sizing_reason_total": monitor_position_sizing_reason_total,
        "no_trade_reason_total": no_trade_reason_total,
        "dominant_blocker_total": dominant_blocker_total,
        "near_ready_total": near_ready_total,
        "scanner_monitor_alignment_total": scanner_monitor_alignment_total,
        "pre_intent_wait_total": pre_intent_wait_total,
        "pre_intent_noop_total": pre_intent_noop_total,
        "guard_block_total": guard_block_total,
        "api_errors_by_id": api_errors_by_id,
        "api_429_total": api_429_total,
        "api_429_rate": api_429_rate,
    }
