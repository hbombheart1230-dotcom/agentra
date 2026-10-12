"""Strategist monitor-entry policy seed, rationale and provenance (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _build_strategist_monitor_entry_policy_seed_r3_impl(
    *,
    playbook,
    market_regime,
    monitor_guidance,
    risk_tone,
    trade_aggressiveness,
    facade,
):
    policy = facade.build_default_monitor_entry_policy().to_dict()
    policy["policy_source"] = "strategist"
    policy["adjustments"] = [
        f"seed_playbook:{str(playbook or 'defensive')}",
        f"seed_regime:{str(market_regime or 'neutral')}",
        f"seed_guidance:{str(monitor_guidance or 'defensive_exit')}",
        f"seed_risk_tone:{str(risk_tone or 'normal')}",
        f"seed_trade_aggressiveness:{str(trade_aggressiveness or 'medium')}",
    ]
    return policy


def _build_monitor_entry_policy_rationale_r3_impl(
    *,
    playbook,
    market_regime,
    market_sentiment,
    monitor_guidance,
    risk_tone,
    trade_aggressiveness,
    validation_meta,
    facade,
):
    summary = (
        f"Strategist drafted {str(playbook or 'defensive')} entry policy for "
        f"{str(market_regime or 'neutral')} / {str(market_sentiment or 'neutral')} conditions "
        f"with guidance {str(monitor_guidance or 'defensive_exit')}, "
        f"risk tone {str(risk_tone or 'normal')}, and aggressiveness {str(trade_aggressiveness or 'medium')}."
    )
    if bool(validation_meta.get("fallback_used")):
        reason = str(validation_meta.get("fallback_reason") or "validation_fallback")
        return f"{summary} Policy fallback used: {reason}."
    return summary


def _build_strategy_policy_provenance_r3_impl(*, commander_context, facade):
    source = str(commander_context.get("source") or "strategist_node_fallback")
    merged_from = ["strategist_node"]
    if source == "commander_decision":
        merged_from.insert(0, "commander_decision")
    else:
        merged_from.insert(0, source)
    return {
        "market_policy_owner": "commander",
        "scanner_policy_owner": "strategist",
        "monitor_policy_owner": "strategist",
        "decision_policy_owner": "strategist",
        "merged_from": merged_from,
        "commander_context_source": source,
        "strategist_plan_source": "strategist_node",
        "monitor_entry_policy_source": "strategist",
        "scanner_bias_source": "strategist",
        "shadow_used": bool(commander_context.get("shadow_used")),
        "strategist_fallback_used": bool(commander_context.get("strategist_fallback_used")),
    }
