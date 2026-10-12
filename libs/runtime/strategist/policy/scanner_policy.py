"""Strategist scanner-source policy derivation (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _scanner_source_policy_r3_impl(
    *,
    playbook,
    risk_tone,
    trade_aggressiveness,
    market_regime,
    themes,
    fear_index,
    facade,
):
    normalized_playbook = str(playbook or "").strip().lower()
    normalized_tone = str(risk_tone or "").strip().lower()
    normalized_aggr = str(trade_aggressiveness or "").strip().lower()
    normalized_regime = str(market_regime or "").strip().lower()
    has_themes = bool(list(themes or []))
    allow_condition_search = facade._condition_search_source_enabled()
    normalized_fear = dict(fear_index or {}) if isinstance(fear_index, dict) else {}
    vix_level = facade._to_float(normalized_fear.get("level"), 0.0)
    vix_pressure = facade._to_float(normalized_fear.get("level_pressure"), 0.0)
    elevated_fear = vix_level >= 25.0 or vix_pressure >= 0.25

    policy: Dict[str, Any] = {
        "preferred_sources": ["top_value", "top_volume", "sector_theme", "operator_watchlist"],
        "include_top_value": True,
        "include_top_volume": True,
        "include_change_rate": True,
        "include_condition_search": False,
        "include_sector_candidates": has_themes,
        "include_watchlist": True,
        "top_candidate_pool": 30,
        "condition_limit": 0,
        "source_weights": {
            "top_value": 2.0,
            "top_volume": 1.7,
            "condition_search": 0.0,
            "sector_theme": 1.6,
            "operator_watchlist": 0.8,
            "top_change_rate": 1.3,
        },
        "reason": "balanced baseline prefers liquidity and theme/watchlist sources; condition search is opt-in only",
    }

    if normalized_playbook == "defensive" or normalized_tone == "conservative" or normalized_regime == "risk_off":
        policy.update(
            {
                "preferred_sources": ["top_value", "top_volume", "sector_theme", "operator_watchlist"],
                "include_change_rate": False,
                "include_condition_search": False,
                "include_sector_candidates": has_themes,
                "include_watchlist": True,
                "top_candidate_pool": 18,
                "condition_limit": 0,
                "source_weights": {
                    "top_value": 2.2,
                    "top_volume": 1.9,
                    "condition_search": 0.0,
                    "sector_theme": 1.8 if has_themes else 0.0,
                    "operator_watchlist": 1.1,
                    "top_change_rate": 0.0,
                },
                "reason": "defensive frame prioritizes liquid leaders and suppresses fast-mover sources",
            }
        )
    elif normalized_playbook == "breakout":
        policy.update(
            {
                "preferred_sources": ["top_change_rate", "top_volume", "sector_theme", "operator_watchlist"],
                "include_change_rate": True,
                "include_condition_search": False,
                "include_sector_candidates": has_themes,
                "include_watchlist": normalized_aggr != "high",
                "top_candidate_pool": 32,
                "condition_limit": 0,
                "source_weights": {
                    "top_value": 1.4,
                    "top_volume": 1.9,
                    "condition_search": 0.0,
                    "sector_theme": 1.7 if has_themes else 0.0,
                    "operator_watchlist": 0.5 if normalized_aggr == "high" else 0.8,
                    "top_change_rate": 2.2,
                },
                "reason": "breakout baseline prioritizes fast movers and volume expansion; condition search remains optional",
            }
        )
    elif normalized_playbook == "pullback":
        policy.update(
            {
                "preferred_sources": ["top_value", "sector_theme", "top_volume", "operator_watchlist"],
                "include_change_rate": False,
                "include_condition_search": False,
                "include_sector_candidates": has_themes,
                "include_watchlist": True,
                "top_candidate_pool": 24,
                "condition_limit": 0,
                "source_weights": {
                    "top_value": 2.1,
                    "top_volume": 1.5,
                    "condition_search": 0.0,
                    "sector_theme": 1.9 if has_themes else 0.0,
                    "operator_watchlist": 0.9,
                    "top_change_rate": 0.0,
                },
                "reason": "pullback baseline prioritizes liquid leaders and theme/watchlist support; condition search remains optional",
            }
        )
    elif normalized_playbook == "reversal":
        policy.update(
            {
                "preferred_sources": ["top_change_rate", "operator_watchlist", "top_volume", "sector_theme"],
                "include_change_rate": True,
                "include_condition_search": False,
                "include_sector_candidates": has_themes,
                "include_watchlist": True,
                "top_candidate_pool": 22,
                "condition_limit": 0,
                "source_weights": {
                    "top_value": 1.3,
                    "top_volume": 1.5,
                    "condition_search": 0.0,
                    "sector_theme": 1.3 if has_themes else 0.0,
                    "operator_watchlist": 1.0,
                    "top_change_rate": 1.9,
                },
                "reason": "reversal baseline leans on sharp movers and watchlist context; condition search remains optional",
            }
        )

    if allow_condition_search:
        if normalized_playbook == "breakout":
            policy["preferred_sources"] = ["top_change_rate", "condition_search", "top_volume", "sector_theme"]
            policy["condition_limit"] = 240
            cond_weight = 2.4
        elif normalized_playbook == "pullback":
            policy["preferred_sources"] = ["top_value", "condition_search", "sector_theme", "top_volume"]
            policy["condition_limit"] = 180
            cond_weight = 2.0
        elif normalized_playbook == "reversal":
            policy["preferred_sources"] = ["condition_search", "top_change_rate", "operator_watchlist", "top_volume"]
            policy["condition_limit"] = 220
            cond_weight = 2.2
        else:
            policy["preferred_sources"] = ["top_value", "top_volume", "condition_search", "sector_theme"]
            policy["condition_limit"] = 160
            cond_weight = 2.0
        policy["include_condition_search"] = True
        source_weights = dict(policy.get("source_weights") or {})
        source_weights["condition_search"] = cond_weight
        policy["source_weights"] = source_weights
        policy["reason"] = str(policy.get("reason") or "") + "; condition search explicitly enabled"

    if elevated_fear:
        preferred = [str(x).strip() for x in list(policy.get("preferred_sources") or []) if str(x).strip()]
        preferred = [x for x in preferred if x not in ("top_change_rate", "condition_search")]
        reordered: List[str] = []
        for raw in ("top_value", "sector_theme", "top_volume", "operator_watchlist"):
            if raw == "sector_theme" and not has_themes:
                continue
            if raw not in reordered:
                reordered.append(raw)
        for raw in preferred:
            if raw == "sector_theme" and not has_themes:
                continue
            if raw not in reordered:
                reordered.append(raw)
        source_weights = dict(policy.get("source_weights") or {})
        source_weights.update(
            {
                "top_value": max(facade._to_float(source_weights.get("top_value"), 0.0), 2.3),
                "top_volume": max(facade._to_float(source_weights.get("top_volume"), 0.0), 1.8),
                "sector_theme": max(facade._to_float(source_weights.get("sector_theme"), 0.0), 1.9 if has_themes else 0.0),
                "operator_watchlist": max(facade._to_float(source_weights.get("operator_watchlist"), 0.0), 1.1),
                "top_change_rate": 0.0,
                "condition_search": 0.0,
            }
        )
        policy.update(
            {
                "preferred_sources": reordered,
                "include_change_rate": False,
                "include_condition_search": False,
                "top_candidate_pool": min(facade._to_int(policy.get("top_candidate_pool"), 30), 20),
                "condition_limit": 0,
                "source_weights": source_weights,
                "reason": (
                    f"{str(policy.get('reason') or '')}; elevated fear index "
                    f"(vix={vix_level:.2f}, pressure={vix_pressure:.3f}) shifted source policy toward liquid defensive candidates"
                ).strip("; "),
            }
        )

    return policy
