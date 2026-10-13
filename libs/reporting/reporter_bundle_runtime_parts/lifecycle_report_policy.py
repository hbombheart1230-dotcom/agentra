"""Closed-sell summary refresh and report-generation policy gate projection.

Third Pass T2 (P1.5) intra-function extraction from `libs/reporting/live_execution_bundle_runner.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def closed_sell_execution_details(lifecycle, live_trade_context, lifecycle_bundle, summary_obj, *, facade):
    if True:
        lifecycle = dict(live_trade_context.get("lifecycle") or lifecycle)
        lifecycle_bundle = dict(live_trade_context.get("lifecycle_bundle") or lifecycle_bundle)
        summary_obj = dict(live_trade_context.get("summary_obj") or summary_obj)
        entry_execution_details = dict(live_trade_context.get("entry_execution_details") or {})
        exit_execution_details = dict(live_trade_context.get("exit_execution_details") or {})
        execution_details = dict(live_trade_context.get("execution_details") or {})
        status = facade._reconcile_partial_full_sell_lifecycle(
            lifecycle=lifecycle,
            lifecycle_bundle=lifecycle_bundle,
            execution_details=execution_details,
        )
        summary_obj = facade._refresh_closed_sell_lifecycle_summary(
            lifecycle=lifecycle,
            lifecycle_bundle=lifecycle_bundle,
            summary_obj=summary_obj,
            execution_details=execution_details,
            status=status,
        )
        holding_phase_observability = dict(live_trade_context.get("holding_phase_observability") or {})
    return (entry_execution_details, execution_details, exit_execution_details, holding_phase_observability, lifecycle, lifecycle_bundle, status, summary_obj)


def report_generation_policy_gate(trade_story_input, trace_context, lifecycle_bundle, runtime_state, status, lifecycle, lifecycle_monitor_reason_human, story_type, report_requested, configured_report_model, *, facade):
    if True:
        trade_story_input = dict(trace_context.get("trade_story_input") or trade_story_input)
        lifecycle_bundle = dict(trace_context.get("lifecycle_bundle") or lifecycle_bundle)
        trade_report_policy = facade._resolve_trade_report_policy(
            runtime_state=runtime_state,
            story_input=trade_story_input,
        )
        generate_before_full_close_reason = facade._report_before_full_close_reason(
            lifecycle_status=status,
            lifecycle=lifecycle,
            lifecycle_bundle=lifecycle_bundle,
            monitor_reason_human=lifecycle_monitor_reason_human,
        )
        generate_on_open_effective = bool(
            trade_report_policy.get("generate_on_open")
            or generate_before_full_close_reason
        )
        policy_gate = facade._seed_diagnostics_for_policy(
            lifecycle_status=status,
            story_type=story_type,
            report_requested=report_requested,
            story_input_available=bool(trade_story_input),
            model_hint=configured_report_model,
            generate_on_open=generate_on_open_effective,
        )
        diagnostics = dict(policy_gate.get("diagnostics") or {})
        should_attempt_generation = bool(policy_gate.get("should_attempt_generation"))
    return (diagnostics, generate_before_full_close_reason, generate_on_open_effective, lifecycle_bundle, policy_gate, should_attempt_generation, trade_report_policy, trade_story_input)
