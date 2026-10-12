"""Executor observability / read-model projections: execution trace entry append and strategy-policy summary (pure; no guard verdict, admission, CAS, broker mutation or UNKNOWN handling).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _append_execution_trace_entries_r3_impl(
    state,
    *,
    order,
    execution,
    allow_result,
    strategy_policy_summary,
    facade,
):
    action = str(order.get("action") or "").strip().upper()
    reason = str(execution.get("reason") or "")
    allowed = bool(execution.get("allowed"))
    ok = bool(execution.get("ok"))
    payload = execution.get("payload") if isinstance(execution.get("payload"), dict) else {}

    supervisor_allow: Optional[bool] = None
    supervisor_reason = ""
    supervisor_details: Dict[str, Any] = {}
    if allow_result is not None:
        supervisor_allow = bool(getattr(allow_result, "allowed", getattr(allow_result, "allow", False)))
        supervisor_reason = str(getattr(allow_result, "reason", "") or "")
        raw_details = getattr(allow_result, "details", {})
        if isinstance(raw_details, dict):
            supervisor_details = dict(raw_details)

    facade.append_decision_trace(
        state,
        agent="supervisor",
        event="verdict",
        payload={
            "verdict": "approve" if allowed else "reject",
            "guard_reason": reason or supervisor_reason,
            "supervisor_allow": supervisor_allow,
            "supervisor_reason": supervisor_reason,
            "supervisor_details": supervisor_details,
            "action": action,
            "symbol": str(order.get("symbol") or ""),
            "strategy_policy_summary": dict(strategy_policy_summary or {}),
        },
    )

    execution_attempted = bool(allowed and action in ("BUY", "SELL"))
    if not execution_attempted:
        fill_status = "not_attempted"
    elif ok:
        fill_status = "accepted_or_filled"
    else:
        fill_status = "rejected"

    facade.append_decision_trace(
        state,
        agent="executor",
        event="result",
        payload={
            "execution_attempted": execution_attempted,
            "order_result": {
                "ok": ok,
                "reason": reason,
                "mode": str(payload.get("mode") or ""),
                "broker_code": str(payload.get("broker_code") or ""),
                "broker_message": str(payload.get("broker_message") or ""),
                "order_id": str(payload.get("order_id") or ""),
            },
            "fill_status_summary": fill_status,
            "strategy_policy_summary": dict(strategy_policy_summary or {}),
        },
    )


def _summarize_strategy_policy_r3_impl(strategy_policy, packet, *, facade):
    packet_summary = packet.get("strategy_policy_summary")
    if isinstance(packet_summary, dict) and packet_summary:
        return dict(packet_summary)
    if not isinstance(strategy_policy, dict) or not strategy_policy:
        return {}

    market_policy = strategy_policy.get("market_policy") if isinstance(strategy_policy.get("market_policy"), dict) else {}
    entry_policy = strategy_policy.get("entry_policy") if isinstance(strategy_policy.get("entry_policy"), dict) else {}
    position_sizing = entry_policy.get("position_sizing") if isinstance(entry_policy.get("position_sizing"), dict) else {}
    monitor_policy = strategy_policy.get("monitor_policy") if isinstance(strategy_policy.get("monitor_policy"), dict) else {}
    hard_risk_rails = monitor_policy.get("hard_risk_rails") if isinstance(monitor_policy.get("hard_risk_rails"), dict) else {}
    decision_policy = strategy_policy.get("decision_policy") if isinstance(strategy_policy.get("decision_policy"), dict) else {}
    return {
        "schema_version": str(strategy_policy.get("schema_version") or "strategy_policy.v1"),
        "playbook": str(market_policy.get("playbook") or ""),
        "risk_tone": str(market_policy.get("risk_tone") or ""),
        "trade_aggressiveness": str(market_policy.get("trade_aggressiveness") or ""),
        "defensive_mode": bool(market_policy.get("defensive_mode", False)),
        "max_position_qty": facade._coerce_int(position_sizing.get("max_position_qty"), 0),
        "min_position_qty": facade._coerce_int(position_sizing.get("min_position_qty"), 0),
        "lot_size": facade._coerce_int(position_sizing.get("lot_size"), 0),
        "hard_stop_pct": facade._coerce_float(hard_risk_rails.get("hard_stop_pct"), 0.0),
        "max_stop_pct_cap": facade._coerce_float(hard_risk_rails.get("max_stop_pct_cap"), 0.0),
        "use_strategy_v1_engine": facade._is_trueish(decision_policy.get("use_strategy_v1_engine")),
        "allow_score_override": facade._is_trueish(decision_policy.get("allow_score_override")),
    }


def _extract_strategy_policy_r3_impl(packet, state, *, facade):
    raw = packet.get("strategy_policy")
    if isinstance(raw, dict) and raw:
        return dict(raw)
    strategist_output = state.get("strategist_output")
    if isinstance(strategist_output, dict):
        raw = strategist_output.get("strategy_policy")
        if isinstance(raw, dict) and raw:
            return dict(raw)
    raw = state.get("strategy_policy")
    if isinstance(raw, dict) and raw:
        return dict(raw)
    return {}
