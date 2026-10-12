"""Monitor entry candidate cascade and intent-selection evidence (evidence only; no ordering or intent creation change).

Second Pass (P1.5) intra-function extraction from `graphs/nodes/monitor_node.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def entry_cascade_entry_candidate_cascade_entry_cascade_co(selected, commander_entry_control, open_position_count, max_positions, held_symbols_for_entry, pending_buy_symbols_for_entry, *, facade):
    intents = []
    sizing_info: facade.Dict[str, facade.Any] = {
        "enabled": False,
        "evaluated": False,
        "qty": 1,
        "reason": "disabled",
        "price": None,
        "cash": None,
        "inputs": {},
    }
    scanner_selected_snapshot = dict(selected) if isinstance(selected, dict) else {}
    entry_cascade_config = facade._resolve_entry_candidate_cascade_config(commander_entry_control)
    entry_cascade_max_rank = int(entry_cascade_config.get("max_priority_rank") if entry_cascade_config.get("max_priority_rank") not in (None, "") else 10)
    entry_cascade_max_runner_ups = int(entry_cascade_config.get("max_runner_ups") if entry_cascade_config.get("max_runner_ups") not in (None, "") else 9)
    entry_candidate_cascade: facade.Dict[str, facade.Any] = {
        "attempted": False,
        "eligible": False,
        "reason": "",
        "top_pick_symbol": "",
        "max_priority_rank": int(entry_cascade_max_rank),
        "max_runner_ups": int(entry_cascade_max_runner_ups),
        "cascade_enabled": bool(entry_cascade_config.get("cascade_enabled", True)),
        "cascade_allowed_reasons": list(entry_cascade_config.get("cascade_allowed_reasons") or []),
        "cascade_blocked_reasons": list(entry_cascade_config.get("cascade_blocked_reasons") or []),
        "control_source": str(entry_cascade_config.get("source") or "default"),
        "control_mode": str(entry_cascade_config.get("mode") or "default"),
        "runner_up_symbols": [],
        "skipped": [],
        "fallback_used": False,
        "fallback_to_symbol": "",
        "fallback_trace": [],
        "open_position_count": int(open_position_count),
        "max_positions": int(max_positions),
        "capacity_remaining": max(0, int(max_positions) - int(open_position_count)),
        "excluded_symbols": sorted(held_symbols_for_entry | pending_buy_symbols_for_entry),
    }
    return (entry_candidate_cascade, entry_cascade_config, entry_cascade_max_runner_ups, intents, scanner_selected_snapshot, sizing_info)


def entry_cascade_buy_blocked_closeout_window_buy_blocked(state, plan, policy, monitor_policy, strategy_monitor_policy, strategy_frame, commander_context, entry_policy_contract, entry_policy_input, entry_policy_origin, all_pos_map, open_position_count, block_buy_open_position, post_exit_cooldown_sec, entry_cooldown_map, now_epoch_for_entry, selected, sizing_info, entry_info, entry_candidate_cascade, *, facade):
    if True:
        top_pick_result = facade._evaluate_monitor_entry_candidate(
            state=state,
            selected=dict(selected),
            plan=plan,
            policy=policy,
            monitor_policy=monitor_policy,
            strategy_monitor_policy=strategy_monitor_policy,
            strategy_frame=strategy_frame,
            commander_context=commander_context,
            entry_policy_contract=entry_policy_contract,
            entry_policy_input=entry_policy_input,
            entry_policy_origin=entry_policy_origin,
            all_pos_map=all_pos_map,
            open_position_count=open_position_count,
            block_buy_open_position=block_buy_open_position,
            post_exit_cooldown_sec=post_exit_cooldown_sec,
            entry_cooldown_map=entry_cooldown_map,
            now_epoch_for_entry=now_epoch_for_entry,
            prefer_fresh_minute_runner=False,
            allow_opening_rank1_controlled_probe=True,
        )
        state = top_pick_result.get("state") if isinstance(top_pick_result.get("state"), dict) else state
        selected = dict(top_pick_result.get("selected") or selected)
        sizing_info = dict(top_pick_result.get("sizing_info") or sizing_info)
        entry_info = dict(top_pick_result.get("entry_info") or entry_info)
        entry_guard_blocked = bool(top_pick_result.get("entry_guard_blocked"))
        entry_guard_reason = str(top_pick_result.get("entry_guard_reason") or "")
        buy_blocked_open_position = bool(top_pick_result.get("buy_blocked_open_position"))
        buy_blocked_same_symbol = bool(top_pick_result.get("buy_blocked_same_symbol"))
        buy_blocked_pending_buy = bool(top_pick_result.get("buy_blocked_pending_buy"))
        max_positions_reached = bool(top_pick_result.get("max_positions_reached"))
        buy_blocked_post_exit_cooldown = bool(top_pick_result.get("buy_blocked_post_exit_cooldown"))
        buy_blocked_closeout_window = bool(top_pick_result.get("buy_blocked_closeout_window"))
        post_exit_cooldown_remaining_sec = int(top_pick_result.get("post_exit_cooldown_remaining_sec") or 0)
        entry_received_policy = dict(top_pick_result.get("entry_received_policy") or {})
        entry_applied_policy = dict(top_pick_result.get("entry_applied_policy") or {})
        effective_policy_trace = dict(top_pick_result.get("effective_policy_trace") or {})
        entry_cooldown_map = dict(top_pick_result.get("entry_cooldown_map") or entry_cooldown_map)
        entry_signal_detected = bool(top_pick_result.get("entry_signal_detected"))
        symbol = str(top_pick_result.get("symbol") or "")
        qty = int(top_pick_result.get("qty") or 0)
        entry_candidate_cascade["top_pick_symbol"] = symbol
        entry_candidate_cascade["top_pick_triggered"] = bool(entry_info.get("triggered"))
        entry_candidate_cascade["top_pick_reason"] = str(entry_info.get("reason") or "")
        entry_candidate_cascade["top_pick_guard_blocked"] = bool(entry_guard_blocked)
    return (buy_blocked_closeout_window, buy_blocked_open_position, buy_blocked_pending_buy, buy_blocked_post_exit_cooldown, buy_blocked_same_symbol, entry_applied_policy, entry_cooldown_map, entry_guard_blocked, entry_guard_reason, entry_info, entry_received_policy, max_positions_reached, post_exit_cooldown_remaining_sec, qty, selected, sizing_info, state, symbol)


def entry_cascade_entry_cooldown_map_runner_entry(state, runner_symbol, runner_row, plan, policy, monitor_policy, strategy_monitor_policy, strategy_frame, commander_context, entry_policy_contract, entry_policy_input, entry_policy_origin, all_pos_map, open_position_count, block_buy_open_position, post_exit_cooldown_sec, entry_cooldown_map, now_epoch_for_entry, fallback_trace, *, facade):
    if True:
                runner_selected = facade._monitor_selected_snapshot_for_symbol(state, runner_symbol, dict(runner_row))
                runner_result = facade._evaluate_monitor_entry_candidate(
                    state=state,
                    selected=runner_selected,
                    plan=plan,
                    policy=policy,
                    monitor_policy=monitor_policy,
                    strategy_monitor_policy=strategy_monitor_policy,
                    strategy_frame=strategy_frame,
                    commander_context=commander_context,
                    entry_policy_contract=entry_policy_contract,
                    entry_policy_input=entry_policy_input,
                    entry_policy_origin=entry_policy_origin,
                    all_pos_map=all_pos_map,
                    open_position_count=open_position_count,
                    block_buy_open_position=block_buy_open_position,
                    post_exit_cooldown_sec=post_exit_cooldown_sec,
                    entry_cooldown_map=entry_cooldown_map,
                    now_epoch_for_entry=now_epoch_for_entry,
                    prefer_fresh_minute_runner=True,
                    allow_opening_rank1_controlled_probe=False,
                )
                state = runner_result.get("state") if isinstance(runner_result.get("state"), dict) else state
                entry_cooldown_map = dict(runner_result.get("entry_cooldown_map") or entry_cooldown_map)
                runner_entry = dict(runner_result.get("entry_info") or {})
                runner_metrics = (
                    dict(runner_entry.get("metrics") or {})
                    if isinstance(runner_entry.get("metrics"), dict)
                    else {}
                )
                runner_scores = (
                    dict(runner_entry.get("condition_scores") or {})
                    if isinstance(runner_entry.get("condition_scores"), dict)
                    else {}
                )
                fallback_trace.append(
                    {
                        "symbol": runner_symbol,
                        "rank": runner_row.get("rank") or runner_row.get("priority_rank"),
                        "score_total": runner_row.get("score_total") or runner_row.get("score"),
                        "triggered": bool(runner_entry.get("triggered")),
                        "reason": str(runner_entry.get("reason") or ""),
                        "primary_failure_axis": str(runner_entry.get("primary_failure_axis") or ""),
                        "transition_readiness_score": runner_entry.get("transition_readiness_score")
                        or runner_metrics.get("transition_readiness_score")
                        or runner_scores.get("transition_readiness_score"),
                        "vwap_distance": runner_metrics.get("vwap_distance"),
                        "max_extended_from_vwap_pct": (
                            (runner_entry.get("thresholds") or {}).get("max_extended_from_vwap_pct")
                            if isinstance(runner_entry.get("thresholds"), dict)
                            else None
                        ),
                        "volume_ratio": runner_metrics.get("volume_ratio"),
                        "breakout_ok": runner_metrics.get("breakout_ok"),
                        "pullback_ok": runner_metrics.get("pullback_ok"),
                        "extension_ok": runner_metrics.get("extension_ok"),
                        "confidence_score": runner_scores.get("confidence_score")
                        or runner_metrics.get("confidence_score"),
                        "confidence_threshold": runner_scores.get("confidence_threshold")
                        or runner_metrics.get("confidence_threshold"),
                        "minute_source_present": runner_metrics.get("minute_source_present"),
                        "minute_refetch_succeeded": runner_metrics.get("minute_refetch_succeeded"),
                        "minute_cache_fallback_used": runner_metrics.get("minute_cache_fallback_used"),
                        "guard_blocked": bool(runner_result.get("entry_guard_blocked")),
                        "guard_reason": str(runner_result.get("entry_guard_reason") or ""),
                        "entry_cost_filter": dict(
                            runner_entry.get("entry_cost_filter") or {}
                        ),
                        "directional_edge_estimate": dict(
                            runner_entry.get("directional_edge_estimate") or {}
                        ),
                        "intent_submitted": bool(runner_entry.get("intent_submitted")),
                        "buy_blocked_open_position": bool(runner_result.get("buy_blocked_open_position")),
                        "buy_blocked_same_symbol": bool(runner_result.get("buy_blocked_same_symbol")),
                        "buy_blocked_pending_buy": bool(runner_result.get("buy_blocked_pending_buy")),
                        "buy_blocked_post_exit_cooldown": bool(runner_result.get("buy_blocked_post_exit_cooldown")),
                        "buy_blocked_closeout_window": bool(runner_result.get("buy_blocked_closeout_window")),
                    }
                )
    return (entry_cooldown_map, runner_entry, runner_metrics, runner_result, runner_scores, runner_selected, state)


def entry_cascade_buy_blocked_closeout_window_buy_blocked_2(entry_candidate_cascade, runner_symbol, runner_row, runner_subtype, symbol, runner_selected, runner_result, sizing_info, runner_entry, *, facade):
    if True:
                entry_candidate_cascade["fallback_used"] = True
                entry_candidate_cascade["fallback_to_symbol"] = runner_symbol
                entry_candidate_cascade["fallback_to_rank"] = runner_row.get("rank") or runner_row.get("priority_rank")
                entry_candidate_cascade["pullback_evidence_profile"] = dict(runner_subtype)
                entry_candidate_cascade["fallback_candidate_subtype"] = str(runner_subtype.get("subtype") or "")
                entry_candidate_cascade["fallback_from_symbol"] = symbol
                selected = dict(runner_result.get("selected") or runner_selected)
                sizing_info = dict(runner_result.get("sizing_info") or sizing_info)
                entry_info = runner_entry
                entry_guard_blocked = bool(runner_result.get("entry_guard_blocked"))
                entry_guard_reason = str(runner_result.get("entry_guard_reason") or "")
                buy_blocked_open_position = bool(runner_result.get("buy_blocked_open_position"))
                buy_blocked_same_symbol = bool(runner_result.get("buy_blocked_same_symbol"))
                buy_blocked_pending_buy = bool(runner_result.get("buy_blocked_pending_buy"))
                max_positions_reached = bool(runner_result.get("max_positions_reached"))
                buy_blocked_post_exit_cooldown = bool(runner_result.get("buy_blocked_post_exit_cooldown"))
                buy_blocked_closeout_window = bool(runner_result.get("buy_blocked_closeout_window"))
                post_exit_cooldown_remaining_sec = int(runner_result.get("post_exit_cooldown_remaining_sec") or 0)
                entry_received_policy = dict(runner_result.get("entry_received_policy") or {})
                entry_applied_policy = dict(runner_result.get("entry_applied_policy") or {})
                effective_policy_trace = dict(runner_result.get("effective_policy_trace") or {})
                entry_signal_detected = bool(runner_result.get("entry_signal_detected"))
                symbol = str(runner_result.get("symbol") or runner_symbol)
                qty = int(runner_result.get("qty") or 0)
    return (buy_blocked_closeout_window, buy_blocked_open_position, buy_blocked_pending_buy, buy_blocked_post_exit_cooldown, buy_blocked_same_symbol, entry_applied_policy, entry_guard_blocked, entry_info, entry_received_policy, max_positions_reached, post_exit_cooldown_remaining_sec, qty, selected, sizing_info, symbol)


def entry_cascade_intent(symbol, qty, order_price, order_price_source, entry_candidate_cascade, selected, entry_info, plan, *, facade):
    if True:
            intent = {
                "symbol": symbol,
                "side": "BUY",
                "qty": int(qty),
                "price": order_price if order_price > 0.0 else None,
                "thesis": str(plan.get("thesis") or ""),
                "meta": {
                    "score": selected.get("score"),
                    "risk_score": selected.get("risk_score"),
                    "confidence": selected.get("confidence"),
                    "price": order_price if order_price > 0.0 else None,
                    "current_price": order_price if order_price > 0.0 else None,
                    "price_source": order_price_source,
                    "order_price_source": order_price_source,
                    "entry_signal_source": "monitor_intraday_entry",
                    "entry_pattern": str(entry_info.get("pattern") or ""),
                    "entry_reason": str(entry_info.get("reason") or ""),
                    "entry_signal_chain": list(entry_info.get("signal_chain") or []),
                    "entry_condition_path": str(entry_info.get("entry_condition_path") or ""),
                    "entry_condition_paths_passed": list(entry_info.get("entry_condition_paths_passed") or []),
                    "entry_condition_scores": dict(entry_info.get("condition_scores") or {}),
                    "entry_grouped_logic_trace": dict(entry_info.get("grouped_logic_trace") or {}),
                    "entry_metrics": dict(entry_info.get("metrics") or {}),
                    "entry_policy_interpretation": dict(entry_info.get("policy_interpretation") or {}),
                    "entry_signal_evidence": dict(entry_info.get("signal_evidence") or {}),
                    "entry_chart_structure_features": dict(entry_info.get("chart_structure_features") or {}),
                    "entry_policy_interpreter_trace": dict(entry_info.get("policy_interpreter_trace") or {}),
                    "entry_policy_alignment_summary": dict(entry_info.get("policy_alignment_summary") or {}),
                    "entry_policy_aware_gating": dict(entry_info.get("policy_aware_gating") or {}),
                    "entry_chart_structure_decision_hint": dict(entry_info.get("chart_structure_decision_hint") or {}),
                    "entry_lane": str(entry_info.get("entry_lane") or "strict"),
                    "entry_cost_filter": dict(entry_info.get("entry_cost_filter") or {}),
                    "entry_quality_gate": dict(entry_info.get("entry_quality_gate") or {}),
                    "cost_adjusted_edge_ok": bool(entry_info.get("cost_adjusted_edge_ok")),
                    "cost_adjusted_edge_pct": entry_info.get("cost_adjusted_edge_pct"),
                    "cost_drag_pct": entry_info.get("cost_drag_pct"),
                    "entry_scoring": {
                        "hard_filter_passed": bool(entry_info.get("hard_filter_passed")),
                        "hard_filter_fail_reasons": list(entry_info.get("hard_filter_fail_reasons") or []),
                        "total_score": entry_info.get("total_score"),
                        "score_breakdown": dict(entry_info.get("score_breakdown") or {}),
                        "entry_threshold": entry_info.get("entry_threshold"),
                        "score_passed": bool(entry_info.get("score_passed")),
                        "scoring_mode": str(entry_info.get("scoring_mode") or "disabled"),
                        "legacy_entry_decision": str(entry_info.get("legacy_entry_decision") or "WAIT"),
                        "scoring_entry_decision": str(entry_info.get("scoring_entry_decision") or "WAIT"),
                    },
                    "entry_candidate_cascade": dict(entry_candidate_cascade),
                    "quant_factor_snapshot": dict(entry_info.get("quant_factor_snapshot") or {}),
                    "entry_quant_decision": dict(entry_info.get("entry_quant_decision") or {}),
                    "quant_entry_enforcement": dict(entry_info.get("quant_entry_enforcement") or {}),
                    "market_rail_translation": dict(entry_info.get("market_rail_translation") or {}),
                    "risk_off_defensive_observe_policy": dict(
                        entry_info.get("risk_off_defensive_observe_policy") or {}
                    ),
                    "opening_rank1_controlled_probe": dict(
                        entry_info.get("opening_rank1_controlled_probe") or {}
                    ),
                },
            }
    return (intent,)
