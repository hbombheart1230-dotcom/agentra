from __future__ import annotations

from typing import Any, Dict


def build_actual_runtime(state: Dict[str, Any], *, path: str, facade: Any) -> Dict[str, Any]:
    shadow_runtime = facade._dict(state.get("commander_shadow_runtime"))
    strategist_llm = facade._dict(state.get("strategist_llm"))
    monitor_output = facade._dict(state.get("monitor_output"))
    monitor_action = facade._dict(state.get("monitor_action_decision"))
    execution = facade._dict(state.get("execution"))
    packet = facade._dict(state.get("decision_packet"))
    packet_intent = facade._dict(packet.get("intent"))
    runtime_fast_path = facade._dict(state.get("runtime_fast_path"))

    strategist_executed_raw = shadow_runtime.get("strategist_executed")
    strategist_executed = strategist_executed_raw if isinstance(strategist_executed_raw, bool) else None
    strategist_called_raw = shadow_runtime.get("strategist_called")
    strategist_called = strategist_called_raw if isinstance(strategist_called_raw, bool) else strategist_executed
    llm_called_raw = shadow_runtime.get("llm_called_by_strategist")
    if isinstance(llm_called_raw, bool):
        llm_called = llm_called_raw
    else:
        llm_called = None
        llm_status = facade._clip(strategist_llm.get("status") or strategist_llm.get("llm_status"), max_len=40).lower()
        if strategist_executed is True:
            llm_called = bool(
                llm_status not in {"", "disabled"}
                or facade._clip(strategist_llm.get("prompt_ref"), max_len=40)
                or facade._clip(strategist_llm.get("response_ref"), max_len=40)
            )
    runtime_path = facade._clip(path, max_len=80)
    selected_route = "cached_strategist" if "cached" in str(runtime_path or "") else ""
    used_cached_strategist = bool(shadow_runtime.get("used_cached_strategist"))
    if selected_route == "cached_strategist":
        if strategist_executed is None:
            strategist_executed = False
        if strategist_called is None:
            strategist_called = False
        if llm_called is None:
            llm_called = False
    if selected_route == "cached_strategist" and strategist_executed is False and llm_called is False:
        used_cached_strategist = True
        strategist_called = False
    elif strategist_called is None and llm_called is True:
        strategist_called = True

    monitor_decision = facade._clip(
        shadow_runtime.get("monitor_decision") or monitor_action.get("decision") or monitor_output.get("intent_side"),
        max_len=24,
    ).upper()
    if monitor_decision == "NOOP":
        monitor_decision = "WAIT"
    executor_action = facade._clip(
        shadow_runtime.get("executor_action") or facade._dict(execution.get("order")).get("action") or packet_intent.get("action"),
        max_len=24,
    ).upper()
    executor_status = facade._clip(
        shadow_runtime.get("executor_status") or execution.get("reason") or facade._dict(execution.get("payload")).get("broker_message") or execution.get("ok_source"),
        max_len=80,
    )
    post_scanner_refresh_requested = bool(shadow_runtime.get("post_scanner_refresh_requested"))
    post_scanner_refresh_reason = facade._clip(shadow_runtime.get("post_scanner_refresh_reason"), max_len=80)
    if not post_scanner_refresh_requested and facade._clip(runtime_fast_path.get("reason"), max_len=80) == "post_scanner_selected_symbol_refresh":
        post_scanner_refresh_requested = True
        post_scanner_refresh_reason = facade._clip(runtime_fast_path.get("strategist_refresh_reason"), max_len=80)
    return {
        "strategist_executed": strategist_executed, "strategist_called": strategist_called,
        "llm_called_by_strategist": llm_called, "used_cached_strategist": used_cached_strategist,
        "pre_buy_refresh_requested": bool(shadow_runtime.get("pre_buy_refresh_requested")),
        "pre_buy_refresh_reason": facade._clip(shadow_runtime.get("pre_buy_refresh_reason"), max_len=80),
        "post_scanner_refresh_requested": post_scanner_refresh_requested,
        "post_scanner_refresh_reason": post_scanner_refresh_reason,
        "monitor_decision": monitor_decision or "", "executor_action": executor_action or "",
        "executor_status": executor_status, "runtime_path": runtime_path,
    }


def build_observations(state: Dict[str, Any], *, path: str, facade: Any) -> Dict[str, Any]:
    shadow_runtime = facade._dict(state.get("commander_shadow_runtime"))
    strategist_llm = facade._dict(state.get("strategist_llm"))
    strategist_output = facade._dict(state.get("strategist_output"))
    selected = facade._dict(state.get("selected"))
    portfolio_snapshot = facade._dict(state.get("portfolio_snapshot"))
    positions = [row for row in list(portfolio_snapshot.get("positions") or []) if isinstance(row, dict)]
    risk_context = facade._dict(state.get("risk_context"))
    runtime_fast_path = facade._dict(state.get("runtime_fast_path"))
    stress_flags = facade._listify(facade._dict(strategist_output.get("macro_stress_overlay")).get("stress_flags"), limit=6, max_len=60)
    post_scanner_refresh_requested = bool(shadow_runtime.get("post_scanner_refresh_requested"))
    post_scanner_refresh_reason = facade._clip(shadow_runtime.get("post_scanner_refresh_reason"), max_len=80)
    post_scanner_refresh_selected_symbol = facade._clip(facade._dict(shadow_runtime.get("post_scanner_refresh_context")).get("selected_symbol"), max_len=32)
    if not post_scanner_refresh_requested and facade._clip(runtime_fast_path.get("reason"), max_len=80) == "post_scanner_selected_symbol_refresh":
        post_scanner_refresh_requested = True
        post_scanner_refresh_reason = facade._clip(runtime_fast_path.get("strategist_refresh_reason"), max_len=80)
        post_scanner_refresh_selected_symbol = facade._clip(runtime_fast_path.get("selected_symbol"), max_len=32)
    score_total = selected.get("score_total")
    if score_total in (None, ""):
        score_total = selected.get("score")
    signal_strength = score_total if score_total not in (None, "") else selected.get("confidence")
    retry_count_estimate = facade._safe_int(shadow_runtime.get("retry_count_estimate"), -1)
    if retry_count_estimate < 0:
        retry_count_estimate = max(0, facade._safe_int(strategist_llm.get("attempts"), 1) - 1)
    position_state = "open_position" if positions else "flat"
    if "monitor_only" in str(path or ""):
        position_state = "open_position_monitor_only" if positions else position_state
    return {
        "market_changed": shadow_runtime.get("market_changed"), "signal_strength": signal_strength,
        "risk_score": selected.get("risk_score") if selected.get("risk_score") not in (None, "") else risk_context.get("score"),
        "capital_available_for_sizing": risk_context.get("capital_available_for_sizing"),
        "cash_truth_source": facade._clip(risk_context.get("cash_truth_source"), max_len=80),
        "cash_truth_available": risk_context.get("cash_truth_available"),
        "broker_orderable_amount": risk_context.get("broker_orderable_amount"), "broker_withdrawable_cash": risk_context.get("broker_withdrawable_cash"),
        "broker_deposit": risk_context.get("broker_deposit"), "post_scanner_refresh_requested": post_scanner_refresh_requested,
        "post_scanner_refresh_reason": post_scanner_refresh_reason, "post_scanner_refresh_selected_symbol": post_scanner_refresh_selected_symbol,
        "macro_stress": float(len(stress_flags)) if stress_flags else (1.0 if bool(facade._dict(strategist_output.get("macro_stress_overlay")).get("active")) else 0.0),
        "last_llm_status": facade._clip(strategist_llm.get("status") or strategist_output.get("llm_frame_status"), max_len=40),
        "retry_count_estimate": int(max(0, retry_count_estimate)), "position_state": position_state,
        "has_open_order": facade._commander_shadow_has_open_order(state),
        "runtime_fast_path_reason": facade._clip(runtime_fast_path.get("reason"), max_len=80),
        "repeated_same_context": shadow_runtime.get("repeated_same_context"),
    }
