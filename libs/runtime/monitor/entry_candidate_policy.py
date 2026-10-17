"""Monitor entry candidate: commander memory-bias resolution and entry policy resolution.

T4-B (P1.5 Third Pass): contiguous statement run / value expression of `graphs/nodes/monitor_node.py::_evaluate_monitor_entry_candidate` moved verbatim into a
Monitor Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
source module are resolved at use time as `facade.NAME`. State writes, event emission, logging and persistence stay in the
orchestrator at their original boundaries.
"""
from __future__ import annotations

from typing import Any, NamedTuple


import sys as _monitor_view_sys
import libs.agents.monitor.projections.policy_trace_views as _monitor_views

class MemoryBiasPolicyResolution(NamedTuple):
    """Result of `resolve_entry_memory_bias_policy` (positional order = sorted output names)."""

    commander_entry_control: Any
    entry_policy: Any
    entry_policy_input: Any
    entry_received_policy: Any
    monitor_memory_bias: Any
    monitor_memory_bias_observation_only: Any
    monitor_memory_bias_observed_entry_result: Any
    monitor_memory_bias_result: Any
    monitor_memory_bias_summary: Any

def resolve_entry_memory_bias_policy(commander_context, entry_policy_input, monitor_policy, state, strategy_frame, strategy_monitor_policy, *, facade):
    monitor_memory_bias = facade._resolve_monitor_memory_bias_payload(
        strategy_monitor_policy=strategy_monitor_policy,
        commander_context=commander_context,
        state=state,
    )
    monitor_memory_bias_summary = facade.summarize_monitor_memory_bias(monitor_memory_bias)
    entry_received_policy = facade.MonitorEntryPolicy.from_mapping(entry_policy_input or monitor_policy).to_dict()
    commander_entry_control = (
        dict(commander_context.get("commander_entry_control") or commander_context.get("entry_control") or {})
        if isinstance(commander_context, dict)
        else {}
    )
    if commander_entry_control:
        entry_policy_input = dict(entry_policy_input or monitor_policy or {})
        entry_policy_input["commander_entry_control"] = dict(commander_entry_control)
        entry_policy_input["entry_control"] = dict(commander_entry_control)
    monitor_memory_bias_result = facade.apply_monitor_memory_bias_to_entry_policy(
        entry_policy=entry_policy_input or monitor_policy,
        monitor_memory_bias=monitor_memory_bias,
    )
    monitor_memory_bias_observation_only = facade._memory_bias_observation_only(state)
    monitor_memory_bias_observed_entry_result = dict(monitor_memory_bias_result)
    if monitor_memory_bias_observation_only:
        monitor_memory_bias_result = {
            "policy": facade.MonitorEntryPolicy.from_mapping(entry_policy_input or monitor_policy).to_dict(),
            "applied": False,
            "deltas": [],
            "observation_only": True,
            "observed_deltas": list(monitor_memory_bias_observed_entry_result.get("deltas") or []),
        }
    entry_policy_input = dict(monitor_memory_bias_result.get("policy") or {})
    if commander_entry_control:
        entry_policy_input["commander_entry_control"] = dict(commander_entry_control)
        entry_policy_input["entry_control"] = dict(commander_entry_control)
    entry_policy = facade.resolve_intraday_entry_policy(entry_policy_input or monitor_policy, frame=strategy_frame)
    return MemoryBiasPolicyResolution(commander_entry_control, entry_policy, entry_policy_input, entry_received_policy, monitor_memory_bias, monitor_memory_bias_observation_only, monitor_memory_bias_observed_entry_result, monitor_memory_bias_result, monitor_memory_bias_summary)

def build_entry_effective_policy_trace(entry_applied_policy, entry_policy_origin, entry_received_policy, monitor_memory_bias_result, strategy_frame, *, facade):
    return _monitor_views.build_entry_effective_policy_trace(entry_applied_policy, entry_policy_origin, entry_received_policy, monitor_memory_bias_result, strategy_frame, facade=facade)
