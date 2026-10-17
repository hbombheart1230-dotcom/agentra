"""Monitor entry candidate: policy/memory-bias fields written onto entry_info.

T4-B (P1.5 Third Pass): contiguous statement run / value expression of `graphs/nodes/monitor_node.py::_evaluate_monitor_entry_candidate` moved verbatim into a
Monitor Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
source module are resolved at use time as `facade.NAME`. State writes, event emission, logging and persistence stay in the
orchestrator at their original boundaries.
"""
from __future__ import annotations


import sys as _monitor_view_sys
import libs.agents.monitor.projections.policy_trace_views as _monitor_views

def annotate_entry_policy_fields(effective_policy_trace, entry_info, entry_policy_contract, monitor_memory_bias, monitor_memory_bias_observation_only, monitor_memory_bias_observed_entry_result, monitor_memory_bias_result, monitor_memory_bias_summary, *, facade):
    return _monitor_views.annotate_entry_policy_fields(effective_policy_trace, entry_info, entry_policy_contract, monitor_memory_bias, monitor_memory_bias_observation_only, monitor_memory_bias_observed_entry_result, monitor_memory_bias_result, monitor_memory_bias_summary, facade=facade)

def annotate_entry_minute_metrics(entry_info, entry_row_source, entry_rows, minute_fetch_meta, minute_ohlcv_meta):
    return _monitor_views.annotate_entry_minute_metrics(entry_info, entry_row_source, entry_rows, minute_fetch_meta, minute_ohlcv_meta, facade=_monitor_view_sys.modules[__name__])
