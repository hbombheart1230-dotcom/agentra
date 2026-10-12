"""Commander candidate-watch proposal normalisation, rank cap and entry-control application (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _extract_strategist_candidate_watch_policy_r3_impl(strategist_output, *, facade):
    data = strategist_output if isinstance(strategist_output, dict) else {}
    if not data:
        return {}
    direct = data.get("candidate_watch_policy")
    if isinstance(direct, dict) and direct:
        return dict(direct)
    strategy_policy = data.get("strategy_policy") if isinstance(data.get("strategy_policy"), dict) else {}
    scanner_policy = strategy_policy.get("scanner_policy") if isinstance(strategy_policy.get("scanner_policy"), dict) else {}
    nested = scanner_policy.get("candidate_watch_policy")
    if isinstance(nested, dict) and nested:
        return dict(nested)
    return {}


def _normalize_candidate_watch_proposal_for_commander_r3_impl(raw, *, playbook, tactical_strategy, facade):
    src = dict(raw or {}) if isinstance(raw, dict) else {}
    if not src:
        return {}
    proposed_rank = facade._clamp_int(src.get("max_priority_rank"), 5, 1, 10)
    proposed_runner_ups = facade._clamp_int(src.get("max_runner_ups"), max(0, proposed_rank - 1), 0, max(0, proposed_rank - 1))
    cascade_enabled = (
        facade._is_trueish(src.get("cascade_enabled"))
        if src.get("cascade_enabled") not in (None, "")
        else proposed_runner_ups > 0
    )
    if not cascade_enabled:
        proposed_runner_ups = 0
    return {
        "schema_version": "commander_candidate_watch_proposal.v1",
        "source": str(src.get("source") or "strategist_output.candidate_watch_policy"),
        "original_behavior_effect": str(src.get("behavior_effect") or ""),
        "playbook": str(src.get("playbook") or playbook or ""),
        "tactical_strategy": str(src.get("tactical_strategy") or tactical_strategy or ""),
        "proposed_max_priority_rank": int(proposed_rank),
        "proposed_max_runner_ups": int(proposed_runner_ups),
        "proposed_cascade_enabled": bool(cascade_enabled and proposed_runner_ups > 0),
        "cascade_allowed_reasons": facade._dedupe_reason_list(
            src.get("cascade_allowed_reasons"),
            facade._CANDIDATE_WATCH_DEFAULT_CASCADE_ALLOWED_REASONS,
        ),
        "cascade_blocked_reasons": facade._dedupe_reason_list(
            src.get("cascade_blocked_reasons"),
            facade._CANDIDATE_WATCH_DEFAULT_CASCADE_BLOCKED_REASONS,
        ),
        "reason": str(src.get("reason") or "strategist_candidate_watch_policy"),
        "raw_policy": dict(src),
    }


def _candidate_watch_rank_cap_r3_impl(
    *,
    proposal,
    market_regime,
    market_regime_rail,
    risk_mode,
    stress_flags,
    resilience,
    facade,
):
    tactical = str(proposal.get("tactical_strategy") or "").strip().lower()
    regime = str(market_regime or "").strip().lower()
    rail = str(market_regime_rail or "").strip().lower()
    mode = str(risk_mode or "").strip().lower()
    if mode == "blocked":
        return 1
    if (
        regime == "risk_off"
        or "risk_off" in rail
        or "gap_down" in rail
        or "breadth_collapse" in rail
        or mode == "defensive"
        or bool(stress_flags)
        or str(resilience.get("degrade_mode") or "").strip()
    ):
        return 1
    if tactical == "defensive_observe":
        return 3
    if regime == "risk_on" or mode == "offensive":
        return 10
    return 7


def _apply_candidate_watch_proposal_to_entry_control_r3_impl(
    base,
    proposal,
    *,
    rank_cap,
    force_disable_cascade,
    clamp_reason,
    facade,
):
    if not proposal:
        return base
    out = dict(base or {})
    proposed_rank = facade._clamp_int(proposal.get("proposed_max_priority_rank"), 5, 1, 10)
    proposed_runner_ups = facade._clamp_int(
        proposal.get("proposed_max_runner_ups"),
        max(0, proposed_rank - 1),
        0,
        max(0, proposed_rank - 1),
    )
    final_rank = int(max(1, min(10, int(rank_cap), proposed_rank)))
    final_runner_ups = int(min(proposed_runner_ups, max(0, final_rank - 1)))
    cascade_enabled = bool(proposal.get("proposed_cascade_enabled")) and final_runner_ups > 0 and not bool(force_disable_cascade)
    if not cascade_enabled:
        final_runner_ups = 0
    out.update(
        {
            "candidate_watch_policy_applied": True,
            "candidate_watch_policy_effect": "commander_clamped_execution",
            "candidate_watch_policy_proposal": dict(proposal),
            "candidate_watch_policy_clamp_reason": str(clamp_reason or "commander_strategy_scope_clamp"),
            "proposed_max_priority_rank": int(proposed_rank),
            "proposed_max_runner_ups": int(proposed_runner_ups),
            "max_priority_rank": int(final_rank),
            "max_runner_ups": int(final_runner_ups),
            "cascade_enabled": bool(cascade_enabled),
            "cascade_allowed_reasons": list(proposal.get("cascade_allowed_reasons") or []),
            "cascade_blocked_reasons": list(proposal.get("cascade_blocked_reasons") or []),
        }
    )
    return out
