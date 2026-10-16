"""Scanner blocker-family concentration overlay (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _apply_blocker_family_concentration_overlay_r3_impl(rows, *, scan_aggressiveness, facade):
    meta = {
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
    ranked_rows = [dict(row) for row in list(rows or []) if isinstance(row, dict)]
    if len(ranked_rows) < 3:
        return ranked_rows, meta

    top3_rows = ranked_rows[:3]
    top3_family_sets = [set(facade._candidate_blocker_families(row)) for row in top3_rows]
    if any(not family_set for family_set in top3_family_sets):
        return ranked_rows, meta

    common_families = set.intersection(*top3_family_sets) if top3_family_sets else set()
    common_families = {family for family in common_families if family}
    if not common_families:
        return ranked_rows, meta

    family_counter: facade.Counter[str] = facade.Counter()
    for row in ranked_rows:
        for family in facade._candidate_blocker_families(row):
            family_counter[family] += 1
    concentrated_family = sorted(common_families, key=lambda family: (-family_counter.get(family, 0), family))[0]

    affected_rows = [row for row in ranked_rows if concentrated_family in facade._candidate_blocker_families(row)]
    alternative_rows = [row for row in ranked_rows if concentrated_family not in facade._candidate_blocker_families(row)]
    meta.update(
        {
            "applied": True,
            "family": str(concentrated_family),
            "candidate_count": int(len(affected_rows)),
            "top3_symbols_before": [str((row or {}).get("symbol") or "") for row in top3_rows],
            "alternative_symbols": [str((row or {}).get("symbol") or "") for row in alternative_rows[:5]],
        }
    )
    if not alternative_rows:
        meta["selection_vetoed"] = True
        meta["selection_veto_reason"] = "blocker_family_concentration_no_alternative"
        meta["top3_symbols_after"] = list(meta.get("top3_symbols_before") or [])
        return ranked_rows, meta

    third_score = float(facade._to_float(top3_rows[2].get("score_total") or top3_rows[2].get("score")))
    best_alternative_score = max(
        float(facade._to_float((row or {}).get("score_total") or (row or {}).get("score")))
        for row in alternative_rows
    )
    base_penalty = 0.04 + min(0.02, max(0.0, float(scan_aggressiveness)))
    required_penalty = max(0.0, third_score - best_alternative_score + 0.001)
    penalty = min(0.15, max(base_penalty, required_penalty))

    adjusted_rows: List[Dict[str, Any]] = []
    for row in ranked_rows:
        row_copy = dict(row)
        families = facade._candidate_blocker_families(row_copy)
        if concentrated_family in families:
            score_before = float(facade._to_float(row_copy.get("score_total") or row_copy.get("score")))
            score_after = score_before - penalty
            row_copy["score_total"] = float(score_after)
            row_copy["score"] = float(score_after)
            row_copy["blocker_family_concentration_penalty_applied"] = float(penalty)
            row_copy["blocker_family_concentration_family"] = str(concentrated_family)
        adjusted_rows.append(row_copy)

    adjusted_rows.sort(
        key=lambda r: (
            float(r.get("score_total") or 0.0),
            float(r.get("confidence") or 0.0),
            -float(r.get("risk_score") or 0.0),
        ),
        reverse=True,
    )
    post_top3_rows = adjusted_rows[:3]
    meta["penalty"] = float(penalty)
    meta["top3_symbols_after"] = [str((row or {}).get("symbol") or "") for row in post_top3_rows]
    if len(post_top3_rows) >= 3 and all(
        concentrated_family in facade._candidate_blocker_families(row) for row in post_top3_rows
    ):
        meta["selection_vetoed"] = True
        meta["selection_veto_reason"] = "blocker_family_concentration_unresolved"
    return adjusted_rows, meta
