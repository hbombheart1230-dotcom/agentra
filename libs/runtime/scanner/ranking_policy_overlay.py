"""Scanner ranking policy overlay: commander/applied scanner-policy resolution and the post-sort re-entry, diversification, entry-bias-cap, market-representative-guard and blocker-family overlays (rows mutated in place exactly as before).

T4-A (P1.5 Third Pass): contiguous statement run / value expression of `graphs/nodes/scanner_node.py::scanner_node` moved verbatim into a
scanner projection Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
Scanner node are resolved at use time as `facade.NAME`. State writes, event emission, logging and persistence stay in the
orchestrator at their original boundaries.
"""
from __future__ import annotations

from typing import Any, NamedTuple


class ScannerRankingPolicyOverlay(NamedTuple):
    """Result of `apply_scanner_ranking_policy_overlay` (positional order = sorted output names)."""

    blocker_family_overlay_meta: Any
    diversification_applied: Any
    diversification_bonus_value: Any
    market_representative_guard_meta: Any
    ranking_after_policy: Any
    ranking_before_policy: Any
    reentry_penalty_applied: Any
    reentry_penalty_value: Any
    scan_results_sorted: Any
    score_adjustment_trace: Any
    selected: Any
    selection_veto_enforced: Any

def resolve_commander_scanner_policy(state, *, facade):
    commander_decision = state.get("commander_decision") if isinstance(state.get("commander_decision"), dict) else {}
    commander_scanner_policy = commander_decision.get("scanner_policy") if isinstance(commander_decision.get("scanner_policy"), dict) else {}
    if not commander_scanner_policy:
        applied_policy = state.get("applied_policy") if isinstance(state.get("applied_policy"), dict) else {}
        applied_scanner_policy = applied_policy.get("scanner") if isinstance(applied_policy.get("scanner"), dict) else {}
        if applied_scanner_policy:
            commander_scanner_policy = dict(applied_scanner_policy)
    if not isinstance(commander_scanner_policy.get("market_representative_guard"), dict):
        source_type = str(((commander_scanner_policy.get("source") or {}).get("type") if isinstance(commander_scanner_policy.get("source"), dict) else "") or "").strip().lower()
        if source_type in ("", "kiwoom", "hybrid", "auto"):
            commander_scanner_policy = dict(commander_scanner_policy)
            commander_scanner_policy["market_representative_guard"] = facade._default_market_representative_guard_policy()
    return commander_scanner_policy

def apply_scanner_ranking_policy_overlay(commander_scanner_policy, enforce_blocker_family_veto, pool_meta, scan_results_sorted, state, *, facade):
    avoid_recent_symbol = facade._is_trueish(commander_scanner_policy.get("avoid_recent_symbol", False))
    recent_symbol_penalty = facade._to_float(commander_scanner_policy.get("recent_symbol_penalty", 0.0))
    diversification_bias = facade._to_float(commander_scanner_policy.get("diversification_bias", 0.0))
    entry_bias_cap = facade._to_float(commander_scanner_policy.get("entry_bias_cap", 0.0))
    allow_same_symbol_reentry = facade._is_trueish(commander_scanner_policy.get("allow_same_symbol_reentry", True))
    reentry_score_gap_threshold = facade._to_float(commander_scanner_policy.get("reentry_score_gap_threshold", 0.0))

    persisted = state.get("persisted_state") if isinstance(state.get("persisted_state"), dict) else {}
    last_trade_symbol = facade._norm_symbol(persisted.get("last_trade_symbol", ""))
    positions = state.get("portfolio_snapshot", {}).get("positions", [])
    if isinstance(positions, dict):
        open_position_count = sum(1 for v in positions.values() if isinstance(v, dict) and facade._to_float(v.get("qty")) > 0)
    elif isinstance(positions, list):
        open_position_count = sum(1 for v in positions if isinstance(v, dict) and facade._to_float(v.get("qty")) > 0)
    else:
        open_position_count = 0
    is_flat = open_position_count == 0

    ranking_before_policy = [{"symbol": r.get("symbol"), "score_total": r.get("score_total")} for r in scan_results_sorted]
    
    reentry_penalty_applied = False
    reentry_penalty_value = 0.0
    diversification_applied = False
    diversification_bonus_value = 0.0
    score_adjustment_trace = []
    market_representative_guard_meta = {
        "enabled": False,
        "applied": False,
        "policy": {},
        "symbol": "",
        "penalty": 0.0,
        "score_gap": 0.0,
        "top_value_dominance": False,
        "confirmation_sources": [],
        "before_top": [],
        "after_top": [],
        "skipped_reason": "",
        "reason": "",
    }

    if entry_bias_cap > 0.0:
        for r in scan_results_sorted:
            raw_bias = facade._to_float(r.get("compatibility_bias", 0.0))
            if raw_bias > entry_bias_cap:
                diff = raw_bias - entry_bias_cap
                r["compatibility_bias"] = entry_bias_cap
                r["score_total"] = facade._to_float(r.get("score_total", 0.0)) - diff
                r["score"] = r["score_total"]
                r["entry_bias_cap_applied"] = True
                r["raw_entry_compatibility_bias"] = raw_bias
                r["effective_entry_compatibility_bias"] = entry_bias_cap
                score_adjustment_trace.append(f"entry_bias_cap applied to {r.get('symbol')}: {raw_bias:.3f} -> {entry_bias_cap:.3f}")
        scan_results_sorted.sort(key=lambda r: (float(r.get("score_total") or 0.0), float(r.get("confidence") or 0.0), -float(r.get("risk_score") or 0.0)), reverse=True)

    if len(scan_results_sorted) > 0:
        top1 = scan_results_sorted[0]
        top1_sym = facade._norm_symbol(top1.get("symbol"))
        top1_score = facade._to_float(top1.get("score_total"))
        
        if len(scan_results_sorted) > 1:
            top2 = scan_results_sorted[1]
            top2_score = facade._to_float(top2.get("score_total"))
            score_gap = top1_score - top2_score
            
            if avoid_recent_symbol and is_flat and last_trade_symbol == top1_sym and allow_same_symbol_reentry:
                if score_gap <= reentry_score_gap_threshold:
                    top1["score_total"] = top1_score - recent_symbol_penalty
                    top1["score"] = top1["score_total"]
                    reentry_penalty_applied = True
                    reentry_penalty_value = recent_symbol_penalty
                    score_adjustment_trace.append(f"reentry_dampener applied to {top1_sym}: -{recent_symbol_penalty:.3f} (gap {score_gap:.3f} <= {reentry_score_gap_threshold:.3f})")
            elif diversification_bias > 0.0 and score_gap <= reentry_score_gap_threshold:
                if top2.get("symbol") != last_trade_symbol:
                    top2["score_total"] = top2_score + diversification_bias
                    top2["score"] = top2["score_total"]
                    diversification_applied = True
                    diversification_bonus_value = diversification_bias
                    score_adjustment_trace.append(f"diversification_bonus applied to {top2.get('symbol')}: +{diversification_bias:.3f}")

        scan_results_sorted.sort(key=lambda r: (float(r.get("score_total") or 0.0), float(r.get("confidence") or 0.0), -float(r.get("risk_score") or 0.0)), reverse=True)

    scan_results_sorted, market_representative_guard_meta = facade._apply_market_representative_guard(
        scan_results_sorted,
        raw_policy=commander_scanner_policy.get("market_representative_guard"),
    )
    if bool(market_representative_guard_meta.get("applied")):
        score_adjustment_trace.append(
            "market_representative_guard "
            f"{str(market_representative_guard_meta.get('symbol') or '')} "
            f"-{float(facade._to_float(market_representative_guard_meta.get('penalty'))):.3f}"
        )

    blocker_family_overlay_meta = {
        "applied": False,
        "family": "",
        "penalty": 0.0,
        "candidate_count": 0,
        "top3_symbols_before": [],
        "top3_symbols_after": [],
        "alternative_symbols": [],
        "selection_vetoed": False,
        "selection_veto_reason": "",
    }
    scan_results_sorted, blocker_family_overlay_meta = facade._apply_blocker_family_concentration_overlay(
        scan_results_sorted,
        scan_aggressiveness=float(facade._to_float(pool_meta.get("scan_aggressiveness"))),
    )
    if bool(blocker_family_overlay_meta.get("applied")):
        score_adjustment_trace.append(
            "blocker_family_concentration "
            f"{str(blocker_family_overlay_meta.get('family') or '')} "
            f"-{float(facade._to_float(blocker_family_overlay_meta.get('penalty'))):.3f}"
        )
    if bool(blocker_family_overlay_meta.get("selection_vetoed")):
        score_adjustment_trace.append(
            f"selection_veto:{str(blocker_family_overlay_meta.get('selection_veto_reason') or '')}"
        )
        if not enforce_blocker_family_veto:
            score_adjustment_trace.append("selection_veto_observed_not_enforced")

    ranking_after_policy = [{"symbol": r.get("symbol"), "score_total": r.get("score_total")} for r in scan_results_sorted]

    selected = scan_results_sorted[0] if scan_results_sorted else None
    selection_veto_enforced = bool(blocker_family_overlay_meta.get("selection_vetoed")) and bool(enforce_blocker_family_veto)
    if selection_veto_enforced:
        selected = None
    return ScannerRankingPolicyOverlay(blocker_family_overlay_meta, diversification_applied, diversification_bonus_value, market_representative_guard_meta, ranking_after_policy, ranking_before_policy, reentry_penalty_applied, reentry_penalty_value, scan_results_sorted, score_adjustment_trace, selected, selection_veto_enforced)
