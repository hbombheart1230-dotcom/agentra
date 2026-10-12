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


def entry_quality_quant_entry_decision_quant_entry_enforce(plan, strategy_frame, entry_info, selected, state, *, facade):
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
    return (quant_entry_decision, quant_entry_enforcement, quant_entry_factor_snapshot, tactic_id_for_quant_entry)
