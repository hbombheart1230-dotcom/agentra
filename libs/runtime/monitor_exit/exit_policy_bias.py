"""Monitor exit cycle: strategy-frame and memory-bias application to the base exit policy.

T4-B (P1.5 Third Pass): contiguous statement run / value expression of `graphs/nodes/monitor_node.py::monitor_node` moved verbatim into a
Monitor Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
source module are resolved at use time as `facade.NAME`. State writes, event emission, logging and persistence stay in the
orchestrator at their original boundaries.
"""
from __future__ import annotations

from typing import Any, NamedTuple


class ExitPolicyBiasResolution(NamedTuple):
    """Result of `apply_exit_policy_memory_bias` (positional order = sorted output names)."""

    effective_exit_policy_base: Any
    exit_bias_observed_result: Any
    exit_bias_result: Any

def apply_exit_policy_memory_bias(effective_exit_policy_base, exit_policy_guard_adjustments, frame_applied, hold_bias_result, monitor_memory_bias, monitor_memory_bias_observation_only, pos_map, selected_snapshot, selected_symbol, state, *, facade):
    exit_policy_strategy = facade._apply_exit_policy_strategy_frame(
        state=state,
        exit_policy_base=effective_exit_policy_base,
        selected=selected_snapshot,
        position=pos_map.get(selected_symbol, {}) if selected_symbol else {},
        frame=frame_applied,
    )
    effective_exit_policy_base = dict(exit_policy_strategy.get("policy") or effective_exit_policy_base)
    effective_exit_policy_base["policy_source"] = str(
        effective_exit_policy_base.get("policy_source")
        or effective_exit_policy_base.get("effective_policy_source")
        or "monitor_effective_exit_policy"
    )
    effective_exit_policy_base["effective_policy_source"] = str(
        effective_exit_policy_base.get("effective_policy_source")
        or effective_exit_policy_base.get("policy_source")
        or "monitor_effective_exit_policy"
    )
    exit_policy_guard_adjustments.extend(list(exit_policy_strategy.get("adjustments") or []))
    exit_bias_result = facade.apply_monitor_memory_bias_to_exit_policy(
        exit_policy=effective_exit_policy_base,
        monitor_memory_bias=monitor_memory_bias,
    )
    exit_bias_observed_result = dict(exit_bias_result)
    if monitor_memory_bias_observation_only:
        exit_bias_result = {
            "policy": dict(effective_exit_policy_base),
            "applied": False,
            "deltas": [],
            "observation_only": True,
            "observed_deltas": list(exit_bias_observed_result.get("deltas") or []),
        }
    effective_exit_policy_base = dict(exit_bias_result.get("policy") or effective_exit_policy_base)
    if bool(hold_bias_result.get("applied")):
        for row in list(hold_bias_result.get("deltas") or [])[:6]:
            exit_policy_guard_adjustments.append(
                f"commander_memory_bias_hold:{str((row or {}).get('field') or '')}:{(row or {}).get('from')}->{(row or {}).get('to')}"
            )
    if bool(exit_bias_result.get("applied")):
        for row in list(exit_bias_result.get("deltas") or [])[:6]:
            exit_policy_guard_adjustments.append(
                f"commander_memory_bias_exit:{str((row or {}).get('field') or '')}:{(row or {}).get('from')}->{(row or {}).get('to')}"
            )
    return ExitPolicyBiasResolution(effective_exit_policy_base, exit_bias_observed_result, exit_bias_result)
