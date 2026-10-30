"""Owner for rejected tactical strategy reason normalization."""
from __future__ import annotations
from typing import Dict


def _normalize_rejected_strategy_reasons_r3_impl(raw, *, tactical_strategy, strategy_scores, facade):
    out: Dict[str, str] = {}
    if isinstance(raw, dict):
        for key, value in raw.items():
            name = facade.canonical_tactic_key(key)
            if name not in facade._TACTICAL_STRATEGIES or name == tactical_strategy:
                continue
            reason = facade._clean_directive_reason(value, default="")
            if reason:
                out[name] = reason
            if len(out) >= 6:
                break
    if out:
        return out
    selected_score = facade._unit_score(strategy_scores.get(tactical_strategy), 0.0)
    ordered = sorted([(name, facade._unit_score(score, 0.0)) for name, score in dict(strategy_scores or {}).items() if name in facade._TACTICAL_STRATEGIES and name != tactical_strategy], key=lambda row: row[1], reverse=True)
    for name, score in ordered[:4]:
        if score <= selected_score:
            out[name] = "score_below_selected_tactical_strategy"
        else:
            out[name] = "not_selected_after_playbook_and_risk_clamp"
    return out
