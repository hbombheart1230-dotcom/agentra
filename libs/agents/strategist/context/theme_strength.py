"""Strategist theme strength map and avoid-theme helpers (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _theme_strength_map_r3_impl(*, themes, candidates, theme_scores, theme_index, facade):
    out: Dict[str, float] = {}
    candidate_symbols = [str((c or {}).get("symbol") or "").strip().upper() for c in list(candidates or [])]
    candidate_symbols = [s for s in candidate_symbols if s]
    denom = max(1, len(candidate_symbols))

    for raw_theme in list(themes or []):
        t = str(raw_theme or "").strip()
        if not t:
            continue
        key = t.lower()
        score_raw = facade._to_float(theme_scores.get(t, theme_scores.get(key, 0.0)), 0.0)
        score_norm = facade._clamp(score_raw / 100.0, -1.0, 1.0) if abs(score_raw) > 1.0 else facade._clamp(score_raw, -1.0, 1.0)
        mapped = theme_index.get(key, set())
        hits = 0
        if mapped:
            mapped_upper = {str(x).strip().upper() for x in mapped if str(x).strip()}
            hits = len([s for s in candidate_symbols if s in mapped_upper])
        hit_ratio = float(hits) / float(denom)
        out[t] = float(facade._clamp((0.70 * score_norm) + (0.30 * hit_ratio), -1.0, 1.0))

    return out


def _avoid_themes_r3_impl(*, market_sentiment, playbook, facade):
    if market_sentiment == "bearish" or playbook == "defensive":
        return ["illiquid_microcap", "headline_only_momentum", "high_gap_speculative"]
    if playbook == "reversal":
        return ["overextended_breakout_without_volume", "late_chasing_moves"]
    if playbook == "pullback":
        return ["counter_trend_low_liquidity"]
    return ["thin_liquidity_names"]
