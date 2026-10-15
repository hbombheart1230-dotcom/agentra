"""Monitor entry candidate: market-rail translation evidence applied to the quant entry decision.

T4-B (P1.5 Third Pass): contiguous statement run / value expression of `graphs/nodes/monitor_node.py::_evaluate_monitor_entry_candidate` moved verbatim into a
Monitor Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
source module are resolved at use time as `facade.NAME`. State writes, event emission, logging and persistence stay in the
orchestrator at their original boundaries.
"""
from __future__ import annotations

from typing import Any, NamedTuple


class EntryGuardOverrides(NamedTuple):
    """Result of `apply_entry_guard_overrides` (positional order = sorted output names)."""

    entry_guard_blocked: Any
    entry_guard_reason: Any
    qty: Any

def apply_market_rail_translation_to_quant_decision(market_rail_translation, quant_entry_decision):
    if isinstance(quant_entry_decision, dict):
        quant_entry_decision["market_rail_translation"] = dict(market_rail_translation)
        if bool(market_rail_translation.get("applied")):
            warnings = list(quant_entry_decision.get("warnings") or [])
            if "market_rail_translation_probe" not in warnings:
                warnings.append("market_rail_translation_probe")
            positives = list(quant_entry_decision.get("positive_reasons") or [])
            if "supportive_market_rail_probe_allowed" not in positives:
                positives.append("supportive_market_rail_probe_allowed")
            quant_entry_decision["warnings"] = warnings[:10]
            quant_entry_decision["positive_reasons"] = positives[:10]
            quant_entry_decision["decision"] = "entry_probe_allowed"
            quant_entry_decision["commander_override_required"] = False
            quant_entry_decision["override_reason_required_for"] = []
    return None

def resolve_entry_intent_cooldown(all_pos_map, entry_cooldown_map, entry_info, entry_intent_cooldown_sec, now_epoch_for_entry, symbol, *, facade):
    cooldown_until = max(0, facade._to_int(entry_cooldown_map.get(symbol)))
    if cooldown_until > 0 and cooldown_until <= now_epoch_for_entry:
        entry_cooldown_map.pop(symbol, None)
        cooldown_until = 0
    if max(0, facade._to_int((all_pos_map.get(symbol) or {}).get("qty"))) > 0:
        entry_cooldown_map.pop(symbol, None)
        cooldown_until = 0
    entry_info["intent_cooldown_sec"] = int(entry_intent_cooldown_sec)
    entry_info["intent_cooldown_until"] = int(cooldown_until) if cooldown_until > 0 else None
    return cooldown_until

def apply_entry_guard_overrides(entry_guard_blocked, entry_guard_reason, entry_info, market_rail_translation, qty, quant_entry_enforcement, risk_off_defensive_policy, sizing_info, *, facade):
    if bool(market_rail_translation.get("applied")):
        if (
            entry_guard_blocked
            and entry_guard_reason in {"cost_adjusted_edge_not_ready", "entry_quality_gate_blocked"}
        ):
            entry_guard_blocked = False
            entry_guard_reason = ""
            entry_info["guard_blocked"] = False
            entry_info["guard_reason"] = ""
            entry_info["market_rail_translation_unblocked_guard"] = True
        entry_info["triggered"] = True
        entry_info["market_rail_translation_probe"] = True
        probe_max_qty = max(1, facade._to_int(market_rail_translation.get("probe_max_qty") or 1))
        if qty > 0:
            qty = max(1, min(int(qty), int(probe_max_qty)))
            sizing_info["qty"] = int(qty)
            sizing_info["market_rail_translation_probe_max_qty"] = int(probe_max_qty)
            sizing_info["market_rail_translation_applied"] = True
    if (
        bool(quant_entry_enforcement.get("blocked"))
        and not entry_guard_blocked
        and bool(entry_info.get("triggered"))
    ):
        entry_guard_blocked = True
        entry_guard_reason = str(quant_entry_enforcement.get("reason") or "quant_entry_block")
        entry_info["guard_blocked"] = True
        entry_info["guard_reason"] = entry_guard_reason
        entry_info["reason"] = entry_guard_reason
    if bool(risk_off_defensive_policy.get("blocked")) and not entry_guard_blocked:
        entry_guard_blocked = True
        entry_guard_reason = str(risk_off_defensive_policy.get("reason") or "risk_off_defensive_observe_no_entry")
        failed_checks = list(entry_info.get("failed_checks") or [])
        if entry_guard_reason not in failed_checks:
            failed_checks.append(entry_guard_reason)
        entry_info["failed_checks"] = failed_checks
        entry_info["guard_blocked"] = True
        entry_info["guard_reason"] = entry_guard_reason
        entry_info["reason"] = entry_guard_reason
        entry_info["primary_failure_axis"] = "risk_off_defensive_observe_policy"
    return EntryGuardOverrides(entry_guard_blocked, entry_guard_reason, qty)
