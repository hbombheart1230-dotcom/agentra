"""Strategist candidate-watch policy and AI override merging (post-processing).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _normalize_candidate_watch_policy_r3_impl(
    raw,
    *,
    tactical_strategy,
    playbook,
    market_regime,
    risk_tone,
    trade_aggressiveness,
    facade,
):
    src = dict(raw or {}) if isinstance(raw, dict) else {}
    strategy = facade._normalize_tactical_strategy(tactical_strategy, playbook=playbook)
    default_rank = int(facade._CANDIDATE_WATCH_DEFAULT_RANK.get(strategy, 5))
    regime = str(market_regime or "").strip().lower()
    tone = str(risk_tone or "").strip().lower()
    aggr = str(trade_aggressiveness or "").strip().lower()

    if regime == "risk_off" or strategy == "defensive_observe":
        default_rank = min(default_rank, 3)
    elif facade._norm_playbook(playbook) == "breakout" and aggr == "high" and regime in {"risk_on", "neutral"}:
        default_rank = max(default_rank, 10 if regime == "risk_on" else 7)
    elif facade._norm_playbook(playbook) == "pullback" and regime == "risk_on":
        default_rank = max(default_rank, 7)
    if tone == "conservative":
        default_rank = min(default_rank, 5)

    raw_rank = src.get("max_priority_rank")
    max_rank = int(facade._clamp(facade._to_int(raw_rank, default_rank), 1, 10))
    if regime == "risk_off":
        max_rank = min(max_rank, 3)
    if strategy == "defensive_observe":
        max_rank = min(max_rank, 3)

    raw_runner_ups = src.get("max_runner_ups")
    max_runner_ups = int(facade._clamp(facade._to_int(raw_runner_ups, max(0, max_rank - 1)), 0, max(0, max_rank - 1)))
    cascade_enabled_default = strategy != "defensive_observe" and max_runner_ups > 0
    cascade_enabled = facade._is_trueish(src.get("cascade_enabled")) if src.get("cascade_enabled") is not None else cascade_enabled_default
    if max_runner_ups <= 0 or strategy == "defensive_observe":
        cascade_enabled = False

    return {
        "schema_version": "candidate_watch_policy.v1",
        "source": "strategist_visibility_proposal",
        "behavior_effect": "visibility_only",
        "tactical_strategy": strategy,
        "tactical_subtype": facade._normalize_tactical_subtype(
            src.get("tactical_subtype"),
            tactical_strategy=strategy,
        ),
        "playbook": facade._norm_playbook(playbook, default="defensive"),
        "market_regime": str(market_regime or ""),
        "risk_tone": str(risk_tone or ""),
        "trade_aggressiveness": str(trade_aggressiveness or ""),
        "max_priority_rank": int(max_rank),
        "max_runner_ups": int(max_runner_ups),
        "cascade_enabled": bool(cascade_enabled),
        "cascade_allowed_reasons": facade._sanitize_reason_list(
            src.get("cascade_allowed_reasons"),
            facade._CANDIDATE_WATCH_CASCADE_ALLOWED_REASONS,
        ),
        "cascade_blocked_reasons": facade._sanitize_reason_list(
            src.get("cascade_blocked_reasons"),
            facade._CANDIDATE_WATCH_CASCADE_BLOCKED_REASONS,
        ),
        "reason": facade._clean_directive_reason(
            src.get("reason"),
            default=f"{strategy}:proposed_watch_depth_visibility_only",
        ),
    }


def _extract_ai_overrides_r3_impl(state, policy, *, facade):
    for key in ("ai_strategist_output", "strategist_ai_output", "strategic_brief"):
        raw = state.get(key)
        if isinstance(raw, dict):
            return dict(raw)
    raw_policy = policy.get("strategist_ai_output") if isinstance(policy.get("strategist_ai_output"), dict) else {}
    return dict(raw_policy)


def _merge_override_text_list_r3_impl(base, override_values, *, limit, facade):
    if not isinstance(override_values, list):
        return list(base)[:limit]
    merged: List[str] = []
    seen = set()
    for row in list(override_values) + list(base):
        s = str(row or "").strip()
        if not s or s in seen:
            continue
        seen.add(s)
        merged.append(s)
        if len(merged) >= limit:
            break
    return merged
