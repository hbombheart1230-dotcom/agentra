"""Monitor entry sizing/cost/quality/quant constraint summaries.

Second Pass (P1.5) intra-function extraction from `graphs/nodes/monitor_node.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def entry_quality_qty_sizing_info(state, symbol, selected, position_sizing_policy, policy, entry_info, *, facade):
    if True:
        px = facade._resolve_price(state, symbol, selected)
        cash = facade._resolve_cash(state)
        sizing_risk_context = facade._build_sizing_risk_context(state, selected, symbol)
        effective_sizing_policy = dict(position_sizing_policy if position_sizing_policy else policy)
        stop_context = facade._derive_position_sizing_stop_context(
            state=state,
            symbol=symbol,
            selected=selected,
            entry_info=entry_info,
            price=px,
            sizing_policy=effective_sizing_policy,
        )
        if bool(stop_context.get("applied")):
            effective_sizing_policy["stop_loss_pct"] = stop_context.get("stop_loss_pct")
            effective_sizing_policy["stop_loss_source"] = stop_context.get("stop_loss_source")
            effective_sizing_policy["invalidation_price"] = stop_context.get("invalidation_price")
            effective_sizing_policy["raw_structure_stop_loss_pct"] = stop_context.get("raw_stop_loss_pct")
            effective_sizing_policy["min_structure_stop_loss_pct"] = stop_context.get("min_structure_stop_loss_pct")
        sz = facade.evaluate_position_size(
            price=px,
            cash=cash if cash > 0.0 else None,
            policy=effective_sizing_policy,
            risk_context=sizing_risk_context,
        )
        qty = max(0, facade._to_int(sz.get("qty")))
        sizing_info = {
            "enabled": True,
            "evaluated": bool(sz.get("evaluated")),
            "qty": int(qty),
            "reason": str(sz.get("reason") or ""),
            "price": sz.get("price"),
            "cash": sz.get("cash"),
            "inputs": sz.get("inputs") if isinstance(sz.get("inputs"), dict) else {},
            "stop_context": dict(stop_context),
        }
    return (qty, sizing_info)


def entry_quality_entry_cost_filter_entry_quality_gate(entry_info, selected, entry_cost_filter_config, qty, plan, strategy_frame, state, commander_context, *, facade):
    entry_cost_filter = facade._evaluate_entry_cost_filter(
        entry_info=entry_info,
        selected=selected,
        qty=int(qty),
        config=entry_cost_filter_config,
    )
    entry_info["entry_cost_filter"] = dict(entry_cost_filter)
    entry_info["cost_adjusted_edge_ok"] = bool(entry_cost_filter.get("cost_adjusted_edge_ok"))
    entry_info["cost_adjusted_edge_pct"] = entry_cost_filter.get("cost_adjusted_edge_pct")
    entry_info["cost_drag_pct"] = entry_cost_filter.get("cost_drag_pct")
    entry_quality_gate = facade._evaluate_entry_quality_gate(
        selected=selected,
        entry_info=entry_info,
        entry_cost_filter=entry_cost_filter,
    )
    entry_info["entry_quality_gate"] = dict(entry_quality_gate)
    entry_info["entry_lane"] = "strict"
    entry_info["scoring_mode"] = str(entry_info.get("scoring_mode") or "disabled")
    tactic_id_for_quant_entry = str(
        plan.get("tactical_strategy")
        or strategy_frame.get("tactical_strategy")
        or ""
    )
    playbook_for_quant_entry = str(
        plan.get("selected_playbook")
        or plan.get("playbook")
        or strategy_frame.get("playbook")
        or ""
    )
    quant_entry_factor_snapshot = facade.build_factor_snapshot_from_monitor_entry(
        entry_info,
        selected=selected,
        tactic_id=tactic_id_for_quant_entry,
        playbook=playbook_for_quant_entry,
    )
    quant_entry_decision = facade.build_entry_quant_decision(
        entry_info,
        selected=selected,
        factor_snapshot=quant_entry_factor_snapshot,
        state=state,
        tactic_id=tactic_id_for_quant_entry,
        playbook=playbook_for_quant_entry,
    )
    quant_entry_enforcement = facade.build_entry_quant_enforcement(quant_entry_decision)
    entry_info["quant_factor_snapshot"] = dict(quant_entry_factor_snapshot)
    entry_info["entry_quant_decision"] = dict(quant_entry_decision)
    entry_info["quant_entry_enforcement"] = dict(quant_entry_enforcement)
    strategist_output = state.get("strategist_output") if isinstance(state.get("strategist_output"), dict) else {}
    market_regime_for_entry = (
        strategy_frame.get("market_regime")
        or commander_context.get("market_regime")
        or strategist_output.get("market_regime")
        or state.get("market_regime")
        or ""
    )
    commander_rail_shadow = (
        commander_context.get("market_regime_rail_shadow")
        if isinstance(commander_context.get("market_regime_rail_shadow"), dict)
        else {}
    )
    strategist_rail_shadow = (
        strategist_output.get("market_regime_rail_shadow")
        if isinstance(strategist_output.get("market_regime_rail_shadow"), dict)
        else {}
    )
    market_regime_rail_for_entry = (
        strategy_frame.get("market_regime_rail")
        or commander_context.get("market_regime_rail")
        or commander_rail_shadow.get("market_regime_rail")
        or commander_rail_shadow.get("rail_id")
        or strategist_output.get("market_regime_rail")
        or strategist_rail_shadow.get("market_regime_rail")
        or strategist_rail_shadow.get("rail_id")
        or state.get("market_regime_rail")
        or ""
    )
    market_rail_translation = facade.evaluate_market_rail_translation(
        entry_info=entry_info,
        entry_quant_decision=quant_entry_decision,
        factor_snapshot=quant_entry_factor_snapshot,
        market_regime=market_regime_for_entry,
        market_regime_rail=market_regime_rail_for_entry,
    )
    entry_info["market_rail_translation"] = dict(market_rail_translation)
    return (entry_cost_filter, entry_quality_gate, market_rail_translation, market_regime_for_entry, market_regime_rail_for_entry, quant_entry_decision, quant_entry_enforcement, tactic_id_for_quant_entry)
