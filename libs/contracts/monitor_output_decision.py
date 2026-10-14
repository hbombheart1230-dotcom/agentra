"""Monitor output artifact decision-rule evidence and memory-bias application facts.

T3.5 (P1.5 Third Pass): contiguous statement runs / dict item ranges of `libs/contracts/agent_outputs.py::build_monitor_output_artifact` moved verbatim into
contract-owned projection stages. Locals enter as explicit parameters and leave as the returned record or dict; value
helpers are imported from `libs.contracts.agent_output_values`; remaining module globals of the public facade are
resolved at use time as `facade.NAME`. Final artifact assembly and `validate_artifact` stay in the public builder.
"""
from __future__ import annotations

from typing import Any, NamedTuple

from libs.contracts.agent_output_values import (
    _clip,
    _dedupe_text,
    _dict,
    _listify,
    _safe_int,
)


class MonitorDecisionRuleEvidence(NamedTuple):
    """Result of `monitor_decision_rule_evidence` (positional order is the pre-T3.5 tuple order)."""

    blocked_rules: Any
    decision_action: Any
    decision_phase: Any
    decision_reason_chain: Any
    decision_status: Any
    entry_chart_structure_features: Any
    entry_minute_refetch_attempted: Any
    entry_minute_refetch_failure_detail: Any
    entry_minute_refetch_failure_reason: Any
    entry_minute_refetch_runner_source: Any
    entry_minute_refetch_succeeded: Any
    entry_minute_source_present: Any
    entry_minute_source_used: Any
    entry_policy_alignment_summary: Any
    entry_policy_interpreter_trace: Any
    evidence_quality: Any
    feature_source: Any
    missing_inputs: Any
    posture: Any
    price_source: Any
    primary_reason_code: Any
    secondary_reason_codes: Any
    threshold_snapshot: Any
    triggered_rules: Any

def monitor_decision_rule_evidence(exit_info, entry_info, state, transition, monitor_output, entry_detail, symbol, intent_side, open_position_count, exit_detail, thresholds, monitor, _first_trace_value, *, facade):
    triggered_rules: facade.List[str] = []
    if bool(exit_info.get("triggered")) and str(exit_info.get("reason") or "").strip():
        triggered_rules.append(str(exit_info.get("reason") or "").strip())
    if bool(entry_info.get("triggered")) and str(entry_info.get("pattern") or "").strip():
        triggered_rules.append(f"entry:{str(entry_info.get('pattern') or '').strip()}")
    blocked_rules: facade.List[str] = []
    if bool(entry_info.get("guard_blocked")) and str(entry_info.get("guard_reason") or "").strip():
        blocked_rules.append(str(entry_info.get("guard_reason") or "").strip())
    if bool(exit_info.get("sell_guard_blocked")) and str(exit_info.get("sell_guard_reason") or "").strip():
        blocked_rules.append(str(exit_info.get("sell_guard_reason") or "").strip())
    blocked_rules.extend([str(x or "").strip() for x in list(entry_info.get("failed_checks") or []) if str(x or "").strip()])
    posture = _clip(state.get("monitor_posture") or transition.get("current_posture"), max_len=60)
    decision_reason_chain = [
        _clip(exit_info.get("monitor_reason"), max_len=180),
        _clip(exit_info.get("reason"), max_len=180),
        _clip(entry_info.get("reason"), max_len=180),
        _clip(monitor_output.get("entry_exit_reason"), max_len=180),
    ]
    decision_reason_chain = [x for x in decision_reason_chain if x]
    entry_reason_code = _clip(
        entry_detail.get("reason")
        or entry_info.get("guard_reason")
        or entry_info.get("reason"),
        max_len=160,
    )
    entry_metrics_seed = _dict(entry_info.get("metrics"))
    entry_has_structural_evidence = bool(
        bool(entry_info.get("evaluated"))
        or bool(entry_info.get("failed_checks"))
        or bool(entry_reason_code)
        or bool(entry_metrics_seed.get("minute_source_present"))
        or bool(entry_metrics_seed.get("minute_refetch_attempted"))
        or entry_metrics_seed.get("current_price") not in (None, "")
        or entry_metrics_seed.get("price") not in (None, "")
    )
    missing_inputs: facade.List[str] = []
    if not symbol:
        missing_inputs.append("selected_symbol_missing")
    if not bool(entry_info.get("evaluated")) and entry_reason_code in {"minute_candle_missing", "data_incomplete"}:
        missing_inputs.append(entry_reason_code)
    if (
        exit_info.get("price") in (None, "")
        and not bool(entry_info.get("triggered"))
        and not entry_has_structural_evidence
    ):
        missing_inputs.append("price_unavailable")
    if intent_side == "BUY":
        decision_phase = "entry"
        decision_action = "buy"
    elif intent_side == "SELL":
        decision_phase = "exit"
        decision_action = "sell"
    elif open_position_count > 0:
        decision_phase = "hold"
        decision_action = "hold"
    else:
        decision_phase = "no_intent"
        decision_action = "none"
    if intent_side in {"BUY", "SELL"}:
        decision_status = "ok"
    elif missing_inputs:
        decision_status = "unavailable"
    elif blocked_rules:
        decision_status = "blocked"
    else:
        decision_status = "skipped"
    if decision_phase == "no_intent" and open_position_count <= 0 and entry_reason_code:
        primary_reason_raw = entry_reason_code
    else:
        primary_reason_raw = (
            exit_detail.get("triggered_rule")
            or exit_info.get("reason")
            or entry_detail.get("reason")
            or entry_info.get("guard_reason")
            or entry_info.get("reason")
            or monitor_output.get("entry_exit_reason")
            or exit_info.get("monitor_reason")
        )
    primary_reason_code = _clip(primary_reason_raw, max_len=180)
    secondary_reason_codes = _dedupe_text(
        [text for text in blocked_rules + decision_reason_chain if text and text != primary_reason_code],
        limit=12,
        max_len=160,
    )
    price_source = _clip(exit_info.get("price_source"), max_len=120)
    feature_source = _clip(exit_info.get("feature_source"), max_len=120)
    evidence_quality = "unavailable"
    if decision_status == "ok" and (bool(entry_info.get("evaluated")) or bool(exit_info.get("evaluated"))):
        evidence_quality = "strong"
    elif bool(entry_info.get("evaluated")) or bool(exit_info.get("evaluated")) or bool(secondary_reason_codes):
        evidence_quality = "partial"
    elif decision_reason_chain:
        evidence_quality = "weak"
    threshold_snapshot = {
        "applied_policy": _dict(entry_info.get("applied_policy")) or _dict(entry_info.get("thresholds")),
        "received_policy": _dict(entry_info.get("received_policy")),
        "received_policy_source": _clip(entry_info.get("received_policy_source"), max_len=120),
        "effective_policy": _dict(entry_info.get("effective_policy")) or _dict(entry_info.get("applied_policy")) or _dict(entry_info.get("thresholds")),
        "effective_policy_source": _clip(entry_info.get("effective_policy_source"), max_len=120),
        "effective_policy_source_chain": _listify(entry_info.get("effective_policy_source_chain"), limit=6, max_len=80),
        "policy_adjustments": _dict(entry_info.get("policy_adjustments")),
        "policy_adjustment_summary": _clip(entry_info.get("policy_adjustment_summary"), max_len=220),
        "policy_adjustment_reasoning": _clip(entry_info.get("policy_adjustment_reasoning"), max_len=260),
        "monitor_memory_bias_applied": bool(entry_info.get("monitor_memory_bias_applied")),
        "monitor_memory_bias": _dict(entry_info.get("monitor_memory_bias")),
        "monitor_memory_bias_summary": _dict(entry_info.get("monitor_memory_bias_summary")),
        "monitor_memory_bias_deltas": [
            {
                "field": _clip((row or {}).get("field"), max_len=80),
                "delta": (row or {}).get("delta"),
                "from": (row or {}).get("from"),
                "to": (row or {}).get("to"),
            }
            for row in list(entry_info.get("monitor_memory_bias_deltas") or [])[:8]
            if isinstance(row, dict)
        ],
        "commander_memory_application_trace": _dict(entry_info.get("commander_memory_application_trace")),
        "monitor_memory_application_trace": _dict(entry_info.get("monitor_memory_application_trace")),
        "effective_policy_deltas": [
            {
                "field": _clip((row or {}).get("field"), max_len=80),
                "from": (row or {}).get("from"),
                "to": (row or {}).get("to"),
            }
            for row in list(entry_info.get("effective_policy_deltas") or [])[:8]
            if isinstance(row, dict)
        ],
        "entry_thresholds": _dict(entry_info.get("thresholds")),
        "entry_threshold_margins": _dict(entry_info.get("threshold_margins")),
        "entry_condition_path": _clip(entry_info.get("entry_condition_path"), max_len=80),
        "entry_condition_paths_passed": _listify(entry_info.get("entry_condition_paths_passed"), limit=4, max_len=80),
        "entry_condition_scores": _dict(entry_info.get("condition_scores")),
        "entry_grouped_logic_trace": _dict(entry_info.get("grouped_logic_trace")),
        "entry_latest_candle_ts": entry_info.get("metrics", {}).get("latest_candle_ts") if isinstance(entry_info.get("metrics"), dict) else None,
        "entry_minute_snapshot_age_minutes": entry_info.get("metrics", {}).get("minute_snapshot_age_minutes") if isinstance(entry_info.get("metrics"), dict) else None,
        "entry_minute_snapshot_was_stale": entry_info.get("metrics", {}).get("minute_snapshot_was_stale") if isinstance(entry_info.get("metrics"), dict) else None,
        "entry_minute_refetch_attempted": entry_info.get("metrics", {}).get("minute_refetch_attempted") if isinstance(entry_info.get("metrics"), dict) else None,
        "entry_minute_refetch_succeeded": entry_info.get("metrics", {}).get("minute_refetch_succeeded") if isinstance(entry_info.get("metrics"), dict) else None,
        "entry_minute_refetch_reason": entry_info.get("metrics", {}).get("minute_refetch_reason") if isinstance(entry_info.get("metrics"), dict) else None,
        "entry_minute_refetch_trigger_reason": entry_info.get("metrics", {}).get("minute_refetch_trigger_reason") if isinstance(entry_info.get("metrics"), dict) else None,
        "entry_minute_refetch_failure_reason": entry_info.get("metrics", {}).get("minute_refetch_failure_reason") if isinstance(entry_info.get("metrics"), dict) else None,
        "entry_minute_refetch_produced_fresh_snapshot": entry_info.get("metrics", {}).get("minute_refetch_produced_fresh_snapshot") if isinstance(entry_info.get("metrics"), dict) else None,
        "entry_inferred_spacing_minutes": entry_info.get("metrics", {}).get("inferred_spacing_minutes") if isinstance(entry_info.get("metrics"), dict) else None,
        "entry_series_class": entry_info.get("metrics", {}).get("series_class") if isinstance(entry_info.get("metrics"), dict) else None,
        "exit_thresholds": thresholds,
        "exit_confirm_ticks": _safe_int(exit_info.get("exit_confirm_ticks")),
        "exit_confirm_count": _safe_int(exit_info.get("exit_confirm_count")),
    }
    entry_metrics = (
        _dict(entry_info.get("metrics"))
        or _dict(entry_detail.get("metrics"))
        or _dict(monitor.get("entry_metrics"))
    )
    entry_chart_structure_features = (
        _dict(monitor_output.get("chart_structure_features"))
        or _dict(entry_info.get("chart_structure_features"))
        or _dict(monitor.get("entry_chart_structure_features"))
    )
    entry_policy_interpreter_trace = (
        _dict(monitor_output.get("policy_interpreter_trace"))
        or _dict(entry_info.get("policy_interpreter_trace"))
        or _dict(monitor.get("entry_policy_interpreter_trace"))
    )
    entry_policy_alignment_summary = (
        _dict(monitor_output.get("policy_alignment_summary"))
        or _dict(entry_info.get("policy_alignment_summary"))
        or _dict(monitor.get("entry_policy_alignment_summary"))
    )
    entry_minute_source_present = threshold_snapshot.get("entry_minute_source_present")
    if entry_minute_source_present is None:
        entry_minute_source_present = entry_metrics.get("minute_source_present")
    if entry_minute_source_present is None:
        entry_minute_source_present = _first_trace_value("entry_minute_source_present")
    entry_minute_source_used = threshold_snapshot.get("entry_minute_source_used")
    if entry_minute_source_used in (None, ""):
        entry_minute_source_used = entry_metrics.get("minute_source_used")
    if entry_minute_source_used in (None, ""):
        entry_minute_source_used = _first_trace_value("entry_minute_source_used")
    entry_minute_refetch_attempted = threshold_snapshot.get("entry_minute_refetch_attempted")
    if entry_minute_refetch_attempted is None:
        entry_minute_refetch_attempted = entry_metrics.get("minute_refetch_attempted")
    if entry_minute_refetch_attempted is None:
        entry_minute_refetch_attempted = _first_trace_value("entry_minute_refetch_attempted")
    entry_minute_refetch_succeeded = threshold_snapshot.get("entry_minute_refetch_succeeded")
    if entry_minute_refetch_succeeded is None:
        entry_minute_refetch_succeeded = entry_metrics.get("minute_refetch_succeeded")
    if entry_minute_refetch_succeeded is None:
        entry_minute_refetch_succeeded = _first_trace_value("entry_minute_refetch_succeeded")
    entry_minute_refetch_failure_reason = threshold_snapshot.get("entry_minute_refetch_failure_reason")
    if entry_minute_refetch_failure_reason in (None, ""):
        entry_minute_refetch_failure_reason = entry_metrics.get("minute_refetch_failure_reason")
    if entry_minute_refetch_failure_reason in (None, ""):
        entry_minute_refetch_failure_reason = _first_trace_value("entry_minute_refetch_failure_reason")
    entry_minute_refetch_failure_detail = entry_metrics.get("minute_refetch_failure_detail")
    if entry_minute_refetch_failure_detail in (None, ""):
        entry_minute_refetch_failure_detail = _first_trace_value("entry_minute_refetch_failure_detail")
    entry_minute_refetch_runner_source = entry_metrics.get("minute_refetch_runner_source")
    if entry_minute_refetch_runner_source in (None, ""):
        entry_minute_refetch_runner_source = _first_trace_value("entry_minute_refetch_runner_source")
    return MonitorDecisionRuleEvidence(blocked_rules, decision_action, decision_phase, decision_reason_chain, decision_status, entry_chart_structure_features, entry_minute_refetch_attempted, entry_minute_refetch_failure_detail, entry_minute_refetch_failure_reason, entry_minute_refetch_runner_source, entry_minute_refetch_succeeded, entry_minute_source_present, entry_minute_source_used, entry_policy_alignment_summary, entry_policy_interpreter_trace, evidence_quality, feature_source, missing_inputs, posture, price_source, primary_reason_code, secondary_reason_codes, threshold_snapshot, triggered_rules)
