"""Monitor output artifact: applied/effective policy, memory bias and adjustment fields.

T3.5 (P1.5 Third Pass): contiguous statement runs / dict item ranges of `libs/contracts/agent_outputs.py::build_monitor_output_artifact` moved verbatim into
contract-owned projection stages. Locals enter as explicit parameters and leave as the returned record or dict; value
helpers are imported from `libs.contracts.agent_output_values`; remaining module globals of the public facade are
resolved at use time as `facade.NAME`. Final artifact assembly and `validate_artifact` stay in the public builder.
"""
from __future__ import annotations

from libs.contracts.agent_output_values import (
    _clip,
    _dict,
    _listify,
)


def monitor_artifact_policy_memory_fields(commander_memory_application_trace, entry_info, monitor_memory_bias, monitor_memory_bias_applied, monitor_memory_bias_deltas, monitor_memory_bias_exit_applied, monitor_memory_bias_exit_deltas, monitor_memory_bias_hold_applied, monitor_memory_bias_hold_deltas, monitor_memory_bias_summary, policy_trace):
    return {
            "applied_policy": _dict(entry_info.get("applied_policy")) or _dict(entry_info.get("thresholds")),
            "received_policy": _dict(entry_info.get("received_policy")),
            "received_policy_source": _clip(entry_info.get("received_policy_source"), max_len=120),
            "effective_policy": _dict(entry_info.get("effective_policy")) or _dict(entry_info.get("applied_policy")) or _dict(entry_info.get("thresholds")),
            "effective_policy_source": _clip(entry_info.get("effective_policy_source"), max_len=120),
            "effective_policy_source_chain": _listify(entry_info.get("effective_policy_source_chain"), limit=6, max_len=80),
            "monitor_memory_bias_applied": bool(monitor_memory_bias_applied) if monitor_memory_bias_applied is not None else None,
            "monitor_memory_bias": monitor_memory_bias,
            "monitor_memory_bias_summary": monitor_memory_bias_summary,
            "monitor_memory_bias_deltas": [
                {
                    "field": _clip((row or {}).get("field"), max_len=80),
                    "delta": (row or {}).get("delta"),
                    "from": (row or {}).get("from"),
                    "to": (row or {}).get("to"),
                }
                for row in list(monitor_memory_bias_deltas or [])[:8]
                if isinstance(row, dict)
            ],
            "monitor_memory_bias_hold_applied": bool(monitor_memory_bias_hold_applied) if monitor_memory_bias_hold_applied is not None else None,
            "monitor_memory_bias_hold_deltas": [
                {
                    "field": _clip((row or {}).get("field"), max_len=80),
                    "delta": (row or {}).get("delta"),
                    "from": (row or {}).get("from"),
                    "to": (row or {}).get("to"),
                }
                for row in list(monitor_memory_bias_hold_deltas or [])[:8]
                if isinstance(row, dict)
            ],
            "monitor_memory_bias_exit_applied": bool(monitor_memory_bias_exit_applied) if monitor_memory_bias_exit_applied is not None else None,
            "monitor_memory_bias_exit_deltas": [
                {
                    "field": _clip((row or {}).get("field"), max_len=80),
                    "delta": (row or {}).get("delta"),
                    "from": (row or {}).get("from"),
                    "to": (row or {}).get("to"),
                }
                for row in list(monitor_memory_bias_exit_deltas or [])[:8]
                if isinstance(row, dict)
            ],
            "commander_memory_application_trace": commander_memory_application_trace,
            "monitor_memory_application_trace": commander_memory_application_trace,
            "policy_adjustments": _dict(entry_info.get("policy_adjustments")),
            "policy_adjustment_summary": _clip(entry_info.get("policy_adjustment_summary"), max_len=220),
            "policy_adjustment_reasoning": _clip(entry_info.get("policy_adjustment_reasoning"), max_len=260),
            "effective_policy_deltas": [
                {
                    "field": _clip((row or {}).get("field"), max_len=80),
                    "from": (row or {}).get("from"),
                    "to": (row or {}).get("to"),
                }
                for row in list(entry_info.get("effective_policy_deltas") or [])[:8]
                if isinstance(row, dict)
            ],
            "policy_source": _clip(_dict(policy_trace.get("policy_ref")).get("policy_source"), max_len=120),
            "policy_validation_status": _clip(_dict(policy_trace.get("policy_ref")).get("policy_validation_status"), max_len=80),
            "policy_fallback_used": _dict(policy_trace.get("policy_ref")).get("policy_fallback_used"),
            "policy_fallback_reason": _clip(_dict(policy_trace.get("policy_ref")).get("policy_fallback_reason"), max_len=220),
            "policy_partial_normalized": _dict(policy_trace.get("policy_ref")).get("policy_partial_normalized"),
            "policy_default_filled_fields": _listify(_dict(policy_trace.get("policy_ref")).get("policy_default_filled_fields"), limit=12, max_len=80),
            "policy_validation_missing_fields": _listify(_dict(policy_trace.get("policy_ref")).get("policy_validation_missing_fields"), limit=12, max_len=80),
            "policy_validation_invalid_fields": _listify(_dict(policy_trace.get("policy_ref")).get("policy_validation_invalid_fields"), limit=12, max_len=80),
            "override_reason": _clip(_dict(policy_trace.get("policy_ref")).get("override_reason"), max_len=180),
            "applied_policy_source_chain": _listify(_dict(policy_trace.get("policy_ref")).get("applied_policy_source_chain"), limit=6, max_len=80)
    }


def monitor_artifact_signal_entry_fields(entry_chart_structure_features, entry_info, entry_minute_refetch_attempted, entry_minute_refetch_failure_detail, entry_minute_refetch_failure_reason, entry_minute_refetch_runner_source, entry_minute_refetch_succeeded, entry_minute_source_present, entry_minute_source_used, entry_policy_alignment_summary, entry_policy_interpreter_trace, market_snapshot_refs, policy_trace, signal_snapshot):
    return {
            "signal_snapshot": signal_snapshot,
            "entry_minute_source_present": entry_minute_source_present,
            "entry_minute_source_used": _clip(entry_minute_source_used, max_len=80),
            "entry_minute_refetch_attempted": entry_minute_refetch_attempted,
            "entry_minute_refetch_succeeded": entry_minute_refetch_succeeded,
            "entry_minute_refetch_failure_reason": _clip(entry_minute_refetch_failure_reason, max_len=120),
            "entry_minute_refetch_failure_detail": _clip(entry_minute_refetch_failure_detail, max_len=220),
            "entry_minute_refetch_runner_source": _clip(entry_minute_refetch_runner_source, max_len=80),
            "entry_chart_structure_features": entry_chart_structure_features,
            "policy_interpreter_trace": entry_policy_interpreter_trace,
            "policy_alignment_summary": entry_policy_alignment_summary,
            "entry_condition_path": _clip(entry_info.get("entry_condition_path"), max_len=80),
            "entry_condition_paths_passed": _listify(entry_info.get("entry_condition_paths_passed"), limit=4, max_len=80),
            "entry_condition_scores": _dict(entry_info.get("condition_scores")),
            "entry_grouped_logic_trace": _dict(entry_info.get("grouped_logic_trace")),
            "market_snapshot_refs": market_snapshot_refs,
            "policy_ref": dict(policy_trace.get("policy_ref") or {}),
            "entry_check_summary": str(policy_trace.get("entry_check_summary") or ""),
            "entry_blockers": list(policy_trace.get("entry_blockers") or []),
            "timing_assessment": dict(policy_trace.get("timing_assessment") or {}),
            "exit_trigger_basis": dict(policy_trace.get("exit_trigger_basis") or {}),
            "commander_context_consumed": policy_trace.get("commander_context_consumed"),
            "consumed_fields": list(policy_trace.get("consumed_fields") or []),
            "flow_instruction_applied": policy_trace.get("flow_instruction_applied"),
            "no_trade_reason_applied": policy_trace.get("no_trade_reason_applied"),
            "shadow_used": policy_trace.get("shadow_used"),
            "strategist_fallback_used": policy_trace.get("strategist_fallback_used")
    }
