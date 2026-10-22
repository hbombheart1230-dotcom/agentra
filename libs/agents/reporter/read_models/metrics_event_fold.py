"""Metrics report event fold: strategist LLM result counters.

The ``strategist_llm``/``result`` slice of the per-event counter fold moved from ``aggregate_day_metrics``; the
accumulator is created by ``new_llm_fold`` and mutated in place in the original statement order. No reads or writes.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict


def new_llm_fold() -> Dict[str, Any]:
    return {
        "llm_total": 0,
        "llm_ok_total": 0,
        "llm_fail_total": 0,
        "llm_circuit_open_total": 0,
        "llm_prompt_tokens_total": 0,
        "llm_completion_tokens_total": 0,
        "llm_total_tokens_total": 0,
        "llm_estimated_cost_usd_total": 0.0,
        "llm_error_by_type": Counter(),
        "llm_prompt_version_total": Counter(),
        "llm_schema_version_total": Counter(),
        "llm_circuit_state_total": Counter(),
        "llm_latency_ms_values": [],
        "llm_attempt_values": [],
    }


def fold_llm_result(r: Dict[str, Any], *, llm_fold: Dict[str, Any]) -> None:
    """Fold one ``strategist_llm``/``result`` row into the accumulators (in place, original order)."""
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
    payload = r.get("payload") if isinstance(r.get("payload"), dict) else {}
    llm_total += 1
    ok = payload.get("ok") is True
    if ok:
        llm_ok_total += 1
    else:
        llm_fail_total += 1
        llm_error_by_type[str(payload.get("error_type") or "unknown")] += 1

    c_state = str(payload.get("circuit_state") or "").strip().lower()
    if c_state:
        llm_circuit_state_total[c_state] += 1
    if c_state == "open" or str(payload.get("error_type") or "") == "CircuitOpen":
        llm_circuit_open_total += 1

    llm_prompt_version_total[str(payload.get("prompt_version") or "unknown")] += 1
    llm_schema_version_total[str(payload.get("schema_version") or "unknown")] += 1

    latency_ms = payload.get("latency_ms")
    try:
        latency_val = float(latency_ms)
        if latency_val >= 0:
            llm_latency_ms_values.append(latency_val)
    except Exception:
        pass

    attempts = payload.get("attempts")
    try:
        attempts_val = float(attempts)
        if attempts_val >= 0:
            llm_attempt_values.append(attempts_val)
    except Exception:
        pass

    prompt_tokens = payload.get("prompt_tokens")
    try:
        prompt_tokens_val = int(float(prompt_tokens))
        if prompt_tokens_val >= 0:
            llm_prompt_tokens_total += prompt_tokens_val
    except Exception:
        pass

    completion_tokens = payload.get("completion_tokens")
    try:
        completion_tokens_val = int(float(completion_tokens))
        if completion_tokens_val >= 0:
            llm_completion_tokens_total += completion_tokens_val
    except Exception:
        pass

    total_tokens = payload.get("total_tokens")
    try:
        total_tokens_val = int(float(total_tokens))
        if total_tokens_val >= 0:
            llm_total_tokens_total += total_tokens_val
    except Exception:
        pass

    estimated_cost_usd = payload.get("estimated_cost_usd")
    try:
        estimated_cost_usd_val = float(estimated_cost_usd)
        if estimated_cost_usd_val >= 0.0:
            llm_estimated_cost_usd_total += estimated_cost_usd_val
    except Exception:
        pass
    llm_fold["llm_total"] = llm_total
    llm_fold["llm_ok_total"] = llm_ok_total
    llm_fold["llm_fail_total"] = llm_fail_total
    llm_fold["llm_circuit_open_total"] = llm_circuit_open_total
    llm_fold["llm_prompt_tokens_total"] = llm_prompt_tokens_total
    llm_fold["llm_completion_tokens_total"] = llm_completion_tokens_total
    llm_fold["llm_total_tokens_total"] = llm_total_tokens_total
    llm_fold["llm_estimated_cost_usd_total"] = llm_estimated_cost_usd_total
