"""Monitor entry candidate: policy/memory-bias fields written onto entry_info.

T4-B (P1.5 Third Pass): contiguous statement run / value expression of `graphs/nodes/monitor_node.py::_evaluate_monitor_entry_candidate` moved verbatim into a
Monitor Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
source module are resolved at use time as `facade.NAME`. State writes, event emission, logging and persistence stay in the
orchestrator at their original boundaries.
"""
from __future__ import annotations


def annotate_entry_policy_fields(effective_policy_trace, entry_info, entry_policy_contract, monitor_memory_bias, monitor_memory_bias_observation_only, monitor_memory_bias_observed_entry_result, monitor_memory_bias_result, monitor_memory_bias_summary, *, facade):
    entry_info["received_policy"] = dict(effective_policy_trace.get("received_policy") or {})
    entry_info["received_policy_source"] = str(effective_policy_trace.get("received_policy_source") or "")
    entry_info["policy_contract"] = dict(entry_policy_contract)
    entry_info["effective_policy"] = dict(effective_policy_trace.get("effective_policy") or {})
    entry_info["effective_policy_source"] = str(effective_policy_trace.get("effective_policy_source") or "")
    entry_info["effective_policy_source_chain"] = list(effective_policy_trace.get("effective_policy_source_chain") or [])
    entry_info["policy_adjustments"] = dict(effective_policy_trace.get("policy_adjustments") or {})
    entry_info["policy_adjustment_summary"] = str(effective_policy_trace.get("policy_adjustment_summary") or "")
    entry_info["policy_adjustment_reasoning"] = str(effective_policy_trace.get("policy_adjustment_reasoning") or "")
    entry_info["effective_policy_deltas"] = list(effective_policy_trace.get("effective_policy_deltas") or [])
    entry_info["monitor_memory_bias_applied"] = bool(monitor_memory_bias_result.get("applied"))
    entry_info["monitor_memory_bias_observation_only"] = bool(monitor_memory_bias_observation_only)
    entry_info["monitor_memory_bias"] = dict(monitor_memory_bias)
    entry_info["monitor_memory_bias_summary"] = dict(monitor_memory_bias_summary)
    entry_info["monitor_memory_bias_deltas"] = list(monitor_memory_bias_result.get("deltas") or [])
    entry_info["monitor_memory_bias_observed_deltas"] = list(
        monitor_memory_bias_observed_entry_result.get("deltas") or []
    )
    entry_memory_application_trace = facade.build_monitor_commander_memory_application_trace(
        monitor_memory_bias=monitor_memory_bias,
        entry_result=monitor_memory_bias_result,
        hold_result={"applied": False, "deltas": []},
        exit_result={"applied": False, "deltas": []},
        monitor_memory_bias_summary=monitor_memory_bias_summary,
        effective_policy_source=str(effective_policy_trace.get("effective_policy_source") or ""),
        effective_policy_source_chain=list(effective_policy_trace.get("effective_policy_source_chain") or []),
    )
    entry_info["commander_memory_application_trace"] = dict(entry_memory_application_trace)
    entry_info["monitor_memory_application_trace"] = dict(entry_memory_application_trace)
    return None

def annotate_entry_minute_metrics(entry_info, entry_row_source, entry_rows, minute_fetch_meta, minute_ohlcv_meta):
    entry_metrics = entry_info.get("metrics") if isinstance(entry_info.get("metrics"), dict) else {}
    entry_metrics["minute_source_present"] = bool(entry_rows)
    entry_metrics["minute_source_used"] = entry_row_source or ""
    latest_candle_ts = None
    if entry_rows and isinstance(entry_rows[-1], dict):
        latest_candle_ts = entry_rows[-1].get("ts")
    entry_metrics["latest_candle_ts"] = latest_candle_ts
    entry_metrics["minute_snapshot_age_minutes"] = minute_fetch_meta.get("minute_snapshot_age_minutes")
    entry_metrics["minute_snapshot_was_stale"] = bool(minute_fetch_meta.get("minute_snapshot_was_stale"))
    entry_metrics["minute_refetch_attempted"] = bool(minute_fetch_meta.get("minute_refetch_attempted"))
    entry_metrics["minute_refetch_succeeded"] = bool(minute_fetch_meta.get("minute_refetch_succeeded"))
    entry_metrics["minute_refetch_reason"] = str(minute_fetch_meta.get("minute_refetch_reason") or "")
    entry_metrics["minute_refetch_trigger_reason"] = str(minute_fetch_meta.get("minute_refetch_trigger_reason") or "")
    entry_metrics["minute_refetch_failure_reason"] = str(minute_fetch_meta.get("minute_refetch_failure_reason") or "")
    entry_metrics["minute_refetch_failure_detail"] = str(minute_fetch_meta.get("minute_refetch_failure_detail") or "")
    entry_metrics["minute_refetch_runner_source"] = str(minute_fetch_meta.get("minute_refetch_runner_source") or "")
    entry_metrics["minute_refetch_produced_fresh_snapshot"] = bool(
        minute_fetch_meta.get("minute_refetch_produced_fresh_snapshot")
    )
    entry_metrics["minute_cache_fallback_used"] = bool(minute_fetch_meta.get("minute_cache_fallback_used"))
    entry_metrics["minute_cache_fallback_source"] = str(minute_fetch_meta.get("minute_cache_fallback_source") or "")
    entry_info["metrics"] = entry_metrics
    entry_info["minute_source_meta"] = dict(minute_ohlcv_meta or {})
    entry_info["minute_fetch_meta"] = minute_fetch_meta
    return None
