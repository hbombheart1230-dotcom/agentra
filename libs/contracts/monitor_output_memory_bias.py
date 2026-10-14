"""Monitor output artifact memory-bias application facts (hold / exit / entry bias and commander memory trace).

T3.5 (P1.5 Third Pass): contiguous statement run of `libs/contracts/agent_outputs.py::build_monitor_output_artifact` moved
verbatim into a contract-owned projection stage. Remaining module globals of the public facade are resolved at use time
as `facade.NAME`. Final artifact assembly and `validate_artifact` stay in the public builder.
"""
from __future__ import annotations

from typing import Any, NamedTuple

from libs.contracts.agent_output_values import (
    _clip,
    _dict,
    _listify,
)


class MonitorMemoryBiasApplication(NamedTuple):
    """Result of `monitor_memory_bias_application` (positional order is the pre-T3.5 tuple order)."""

    commander_memory_application_trace: Any
    decision_summary: Any
    market_snapshot_refs: Any
    monitor_memory_bias: Any
    monitor_memory_bias_applied: Any
    monitor_memory_bias_deltas: Any
    monitor_memory_bias_exit_applied: Any
    monitor_memory_bias_exit_deltas: Any
    monitor_memory_bias_hold_applied: Any
    monitor_memory_bias_hold_deltas: Any
    monitor_memory_bias_summary: Any
    signal_snapshot: Any


def monitor_memory_bias_application(_first_trace_value, threshold_snapshot, policy_trace, _first_trace_dict, entry_info, exit_info, decision_phase, missing_inputs, primary_reason_code, symbol, price_source, feature_source, selected, *, facade):
    monitor_memory_bias_applied = _first_trace_value("monitor_memory_bias_applied")
    if monitor_memory_bias_applied is None:
        monitor_memory_bias_applied = threshold_snapshot.get("monitor_memory_bias_applied")
    if monitor_memory_bias_applied is None:
        monitor_memory_bias_applied = _dict(policy_trace.get("policy_ref")).get("monitor_memory_bias_applied")
    monitor_memory_bias_summary = _first_trace_value("monitor_memory_bias_summary")
    if not isinstance(monitor_memory_bias_summary, dict) or not monitor_memory_bias_summary:
        monitor_memory_bias_summary = _dict(threshold_snapshot.get("monitor_memory_bias_summary"))
    if not isinstance(monitor_memory_bias_summary, dict) or not monitor_memory_bias_summary:
        monitor_memory_bias_summary = _dict(_dict(policy_trace.get("policy_ref")).get("monitor_memory_bias_summary"))
    monitor_memory_bias_deltas = _first_trace_value("monitor_memory_bias_deltas")
    if not isinstance(monitor_memory_bias_deltas, list) or not monitor_memory_bias_deltas:
        monitor_memory_bias_deltas = list(threshold_snapshot.get("monitor_memory_bias_deltas") or [])
    if not isinstance(monitor_memory_bias_deltas, list) or not monitor_memory_bias_deltas:
        monitor_memory_bias_deltas = list(_dict(policy_trace.get("policy_ref")).get("monitor_memory_bias_deltas") or [])
    monitor_memory_bias = _first_trace_dict("monitor_memory_bias")
    if not monitor_memory_bias:
        monitor_memory_bias = _dict(threshold_snapshot.get("monitor_memory_bias"))
    if not monitor_memory_bias:
        monitor_memory_bias = _dict(_dict(policy_trace.get("policy_ref")).get("monitor_memory_bias"))
    monitor_memory_bias_hold_applied = _first_trace_value("monitor_memory_bias_hold_applied")
    if monitor_memory_bias_hold_applied is None:
        monitor_memory_bias_hold_applied = _dict(policy_trace.get("policy_ref")).get("monitor_memory_bias_hold_applied")
    monitor_memory_bias_hold_deltas = _first_trace_value("monitor_memory_bias_hold_deltas")
    if not isinstance(monitor_memory_bias_hold_deltas, list) or not monitor_memory_bias_hold_deltas:
        monitor_memory_bias_hold_deltas = list(_dict(policy_trace.get("policy_ref")).get("monitor_memory_bias_hold_deltas") or [])
    monitor_memory_bias_exit_applied = _first_trace_value("monitor_memory_bias_exit_applied")
    if monitor_memory_bias_exit_applied is None:
        monitor_memory_bias_exit_applied = _dict(policy_trace.get("policy_ref")).get("monitor_memory_bias_exit_applied")
    monitor_memory_bias_exit_deltas = _first_trace_value("monitor_memory_bias_exit_deltas")
    if not isinstance(monitor_memory_bias_exit_deltas, list) or not monitor_memory_bias_exit_deltas:
        monitor_memory_bias_exit_deltas = list(_dict(policy_trace.get("policy_ref")).get("monitor_memory_bias_exit_deltas") or [])
    commander_memory_application_trace = _first_trace_dict("commander_memory_application_trace")
    if not commander_memory_application_trace:
        commander_memory_application_trace = _first_trace_dict("monitor_memory_application_trace")
    if not commander_memory_application_trace:
        commander_memory_application_trace = _dict(threshold_snapshot.get("commander_memory_application_trace"))
    if not commander_memory_application_trace:
        commander_memory_application_trace = _dict(_dict(policy_trace.get("policy_ref")).get("commander_memory_application_trace"))
    if not commander_memory_application_trace:
        commander_memory_application_trace = facade.build_monitor_commander_memory_application_trace(
            monitor_memory_bias=monitor_memory_bias,
            entry_result={
                "applied": bool(monitor_memory_bias_applied),
                "deltas": list(monitor_memory_bias_deltas or []),
            },
            hold_result={
                "applied": bool(monitor_memory_bias_hold_applied),
                "deltas": list(monitor_memory_bias_hold_deltas or []),
            },
            exit_result={
                "applied": bool(monitor_memory_bias_exit_applied),
                "deltas": list(monitor_memory_bias_exit_deltas or []),
            },
            monitor_memory_bias_summary=monitor_memory_bias_summary,
            effective_policy_source=_clip(entry_info.get("effective_policy_source"), max_len=120),
            effective_policy_source_chain=_listify(entry_info.get("effective_policy_source_chain"), limit=8, max_len=80),
        )
    signal_snapshot = {
        "entry_evaluated": bool(entry_info.get("evaluated")),
        "entry_triggered": bool(entry_info.get("triggered")),
        "entry_pattern": _clip(entry_info.get("pattern"), max_len=80),
        "entry_signal_chain": _listify(entry_info.get("signal_chain"), limit=8, max_len=120),
        "entry_condition_path": _clip(entry_info.get("entry_condition_path"), max_len=80),
        "entry_condition_paths_passed": _listify(entry_info.get("entry_condition_paths_passed"), limit=4, max_len=80),
        "entry_condition_scores": _dict(entry_info.get("condition_scores")),
        "entry_grouped_logic_trace": _dict(entry_info.get("grouped_logic_trace")),
        "exit_signal_detected": bool(exit_info.get("exit_signal_detected")),
        "exit_triggered": bool(exit_info.get("triggered")),
        "exit_triggered_rule": _clip(exit_info.get("reason"), max_len=180),
    }
    decision_summary = facade._monitor_decision_summary(
        decision_phase=decision_phase,
        primary_reason_text=_clip(primary_reason_code.replace("_", " "), max_len=220),
        threshold_snapshot=threshold_snapshot,
        signal_snapshot=signal_snapshot,
        missing_inputs=missing_inputs,
    )
    market_snapshot_refs = {
        "selected_symbol": symbol,
        "selected_price": selected.get("price"),
        "price_source": price_source,
        "feature_source": feature_source,
        "playbook": _clip(exit_info.get("playbook"), max_len=60),
        "monitor_guidance": _clip(exit_info.get("monitor_guidance"), max_len=120),
    }
    return MonitorMemoryBiasApplication(commander_memory_application_trace, decision_summary, market_snapshot_refs, monitor_memory_bias, monitor_memory_bias_applied, monitor_memory_bias_deltas, monitor_memory_bias_exit_applied, monitor_memory_bias_exit_deltas, monitor_memory_bias_hold_applied, monitor_memory_bias_hold_deltas, monitor_memory_bias_summary, signal_snapshot)
