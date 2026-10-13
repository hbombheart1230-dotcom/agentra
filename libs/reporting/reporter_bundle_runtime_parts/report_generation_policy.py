"""Report-generation policy gate: seeded diagnostics and generate-on-open / before-full-close decision inputs.

Third Pass T2/T3 (P1.5): pure projection extracted verbatim from `libs/reporting/live_execution_bundle_runner.py::main`.
Inputs are explicit parameters; module dependencies resolve at call time through the injected runner module
(`facade`, TEMPORARY_COMPATIBILITY, keeps monkeypatch seams). No file, clock, env, lock or LLM access; the result is a
named record whose field order equals the legacy positional tuple.
"""
from __future__ import annotations

from typing import Any, NamedTuple


class ReportGenerationPolicyGate(NamedTuple):
    """Result of `report_generation_policy_gate` (positional order is the legacy tuple order; unpacking call-sites are unchanged)."""

    diagnostics: Any
    generate_before_full_close_reason: Any
    generate_on_open_effective: Any
    lifecycle_bundle: Any
    policy_gate: Any
    should_attempt_generation: Any
    trade_report_policy: Any
    trade_story_input: Any


def report_generation_policy_gate(trade_story_input, trace_context, lifecycle_bundle, runtime_state, status, lifecycle, lifecycle_monitor_reason_human, story_type, report_requested, configured_report_model, *, facade):
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
    return ReportGenerationPolicyGate(diagnostics, generate_before_full_close_reason, generate_on_open_effective, lifecycle_bundle, policy_gate, should_attempt_generation, trade_report_policy, trade_story_input)
