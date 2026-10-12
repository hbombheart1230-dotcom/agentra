"""Monitor entry-cycle context: portfolio/strategy/policy-contract snapshots derived before the entry cascade.

Second Pass (P1.5) intra-function extraction from `graphs/nodes/monitor_node.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def entry_cycle_all_pos_map_monitor_policy(state, *, facade):
    """Graph node: Monitor.

    Responsibility:
      - emit at most one intent from selected candidate
      - attach optional order status/lifecycle observation from skill DTOs
      - keep stock-selection and execution out of monitor scope
    """
    run_id = str(state.get("run_id") or "").strip() or "monitor-unknown"
    selected = state.get("selected")
    plan = state.get("plan") or {}
    if isinstance(selected, dict) and selected.get("symbol"):
        selected = facade._monitor_selected_snapshot_for_symbol(state, str(selected.get("symbol") or ""), selected)

    policy = state.get("policy") if isinstance(state.get("policy"), dict) else {}
    strategist_output = state.get("strategist_output") if isinstance(state.get("strategist_output"), dict) else {}
    strategy_policy = (
        dict(strategist_output.get("strategy_policy") or {})
        if isinstance(strategist_output.get("strategy_policy"), dict)
        else {}
    )
    strategy_monitor_policy = (
        dict(strategy_policy.get("monitor_policy") or {})
        if isinstance(strategy_policy.get("monitor_policy"), dict)
        else {}
    )
    monitor_policy: facade.Dict[str, facade.Any] = {}
    if isinstance(policy.get("monitor_policy"), dict):
        monitor_policy.update(dict(policy.get("monitor_policy") or {}))
    if isinstance(strategy_monitor_policy.get("position_guards"), dict):
        monitor_policy.update(dict(strategy_monitor_policy.get("position_guards") or {}))
    if isinstance(strategist_output.get("monitor_policy"), dict):
        monitor_policy.update(dict(strategist_output.get("monitor_policy") or {}))
    if isinstance(state.get("monitor_policy"), dict):
        monitor_policy.update(dict(state.get("monitor_policy") or {}))
    all_pos_map = facade._position_by_symbol(state)
    return (all_pos_map, monitor_policy, plan, policy, run_id, selected, strategist_output, strategy_monitor_policy)


def entry_cycle_buy_blocked_closeout_window_buy_blocked(strategy_monitor_policy, commander_context, state, strategy_frame, strategist_output, commander_entry_control, open_position_count, max_positions, *, facade):
    monitor_memory_bias = facade._resolve_monitor_memory_bias_payload(
        strategy_monitor_policy=strategy_monitor_policy,
        commander_context=commander_context,
        state=state,
    )
    monitor_memory_bias_summary = facade.summarize_monitor_memory_bias(monitor_memory_bias)
    monitor_memory_bias_observation_only = facade._memory_bias_observation_only(state)
    strategist_plan = (
        dict(strategy_frame.get("strategist_plan") or {})
        if isinstance(strategy_frame.get("strategist_plan"), dict)
        else {}
    )
    policy_provenance = (
        dict(strategy_frame.get("policy_provenance") or {})
        if isinstance(strategy_frame.get("policy_provenance"), dict)
        else {}
    )
    commander_applied_policy = {}
    if isinstance(strategy_monitor_policy.get("applied_policy"), dict) and strategy_monitor_policy.get("applied_policy"):
        commander_applied_policy = dict(strategy_monitor_policy.get("applied_policy") or {})
    elif isinstance(commander_context.get("applied_policy"), dict) and commander_context.get("applied_policy"):
        commander_applied_policy = dict(commander_context.get("applied_policy") or {})
    elif isinstance(state.get("commander_applied_policy"), dict) and state.get("commander_applied_policy"):
        commander_applied_policy = dict(state.get("commander_applied_policy") or {})
    elif isinstance((state.get("commander_decision") or {}).get("applied_policy"), dict):
        commander_applied_policy = dict((state.get("commander_decision") or {}).get("applied_policy") or {})

    entry_policy_contract = facade.build_monitor_entry_policy_contract(
        commander_applied_policy=commander_applied_policy,
        strategist_monitor_entry_policy=(
            dict(strategist_output.get("monitor_entry_policy") or {})
            if isinstance(strategist_output.get("monitor_entry_policy"), dict)
            else {}
        ),
        state_monitor_entry_policy=(
            dict(state.get("monitor_entry_policy") or {})
            if isinstance(state.get("monitor_entry_policy"), dict)
            else {}
        ),
        strategy_monitor_entry_policy=(
            dict(strategy_monitor_policy.get("entry_policy") or {})
            if isinstance(strategy_monitor_policy.get("entry_policy"), dict)
            else {}
        ),
    )
    entry_policy_input: facade.Dict[str, facade.Any] = dict(entry_policy_contract.get("selected_policy") or {})
    if commander_entry_control:
        entry_policy_input["commander_entry_control"] = dict(commander_entry_control)
        entry_policy_input["entry_control"] = dict(commander_entry_control)
    entry_policy_origin = str(entry_policy_contract.get("selected_source") or "monitor_policy")
    buy_blocked_open_position = False
    buy_blocked_same_symbol = False
    buy_blocked_pending_buy = False
    max_positions_reached = bool(open_position_count >= max_positions)
    buy_blocked_post_exit_cooldown = False
    buy_blocked_closeout_window = False
    post_exit_cooldown_remaining_sec = 0
    entry_info: facade.Dict[str, facade.Any] = {
        "enabled": True,
        "evaluated": False,
        "triggered": False,
        "reason": "",
        "pattern": "",
        "signal_chain": [],
        "metrics": {},
        "thresholds": {},
        "guard_blocked": False,
        "guard_reason": "",
        "intent_cooldown_sec": 0,
        "intent_cooldown_until": None,
        "intent_submitted": False,
        "legacy_fallback_used": False,
    }
    entry_signal_detected = False
    entry_guard_blocked = False
    entry_guard_reason = ""
    entry_applied_policy: facade.Dict[str, facade.Any] = {}
    entry_received_policy: facade.Dict[str, facade.Any] = {}
    effective_policy_trace: facade.Dict[str, facade.Any] = {}
    hold_bias_result: facade.Dict[str, facade.Any] = {"controls": {}, "applied": False, "deltas": []}
    exit_bias_result: facade.Dict[str, facade.Any] = {"policy": {}, "applied": False, "deltas": []}
    return (buy_blocked_closeout_window, buy_blocked_open_position, buy_blocked_pending_buy, buy_blocked_post_exit_cooldown, buy_blocked_same_symbol, entry_applied_policy, entry_guard_blocked, entry_guard_reason, entry_info, entry_policy_contract, entry_policy_input, entry_policy_origin, entry_received_policy, exit_bias_result, hold_bias_result, max_positions_reached, monitor_memory_bias, monitor_memory_bias_observation_only, monitor_memory_bias_summary, policy_provenance, post_exit_cooldown_remaining_sec, strategist_plan)
