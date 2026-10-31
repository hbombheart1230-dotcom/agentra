"""q8_shadow_blocker_review projections (moved verbatim from q8_shadow_blocker_review).

Module globals and helpers are resolved on ``facade`` (the q8_shadow_blocker_review module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Mapping


def render_q8_shadow_blocker_review_markdown(review: Mapping[str, Any], *, day: str, facade: Any) -> str:
    lines = [
        f"# Q8 Shadow Blocker Review ({day})",
        "",
        "This report is read-only evaluation output. It does not change trading behavior.",
        "",
        "## Summary",
        "",
        f"- candidate_count: **{int(review.get('candidate_count') or 0)}**",
        f"- raw_candidate_count: **{int(review.get('raw_candidate_count') or review.get('candidate_count') or 0)}**",
        f"- duplicate_count: **{int(review.get('duplicate_count') or 0)}**",
        f"- dedupe_key: `{', '.join(list(review.get('dedupe_key') or []))}`",
        f"- review_reason_count: **{int(review.get('review_reason_count') or 0)}**",
        f"- observed_review_candidate_count: **{int(review.get('observed_review_candidate_count') or 0)}**",
    ]
    gate = review.get("evaluation_trust_gate") if isinstance(review.get("evaluation_trust_gate"), facade.Mapping) else {}
    if gate:
        lines.extend(
            [
                f"- trust_gate: `{gate.get('status') or '-'}`",
                f"- promotion_allowed: `{bool(gate.get('promotion_allowed'))}`",
                f"- trust_block_reasons: `{', '.join(list(gate.get('block_reasons') or gate.get('reasons') or [])) or '-'}`",
            ]
        )
    rail = review.get("market_regime_rail") if isinstance(review.get("market_regime_rail"), facade.Mapping) else {}
    if rail:
        lines.append(
            f"- market_regime_rail: `{rail.get('rail_id') or 'not_available'}` "
            f"({rail.get('rail_confidence') or 'none'})"
        )
        lines.append(f"- market_regime_rationale: {rail.get('rationale') or '-'}")
        focus = [str(x) for x in list(rail.get("q8_review_focus") or []) if str(x or "").strip()]
        if focus:
            lines.append(f"- market_regime_q8_focus: `{', '.join(focus)}`")
    lines += [
        "",
        "## Blocker Outcomes",
        "",
        "| Reason | Candidates | Observed | Avg Latest | Avg MFE | Avg MAE | Missed Opp | Adverse | Decision |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    groups = review.get("groups") if isinstance(review.get("groups"), list) else []
    for group in groups:
        if not isinstance(group, facade.Mapping):
            continue
        lines.append(
            f"| `{group.get('reason') or '-'}` "
            f"| {int(group.get('candidate_count') or 0)} "
            f"| {int(group.get('observed_count') or 0)} "
            f"| {float(group.get('avg_latest_return_pct') or 0.0):.4f}% "
            f"| {float(group.get('avg_max_favorable_pct') or 0.0):.4f}% "
            f"| {float(group.get('avg_max_adverse_pct') or 0.0):.4f}% "
            f"| {int(group.get('missed_opportunity_count') or 0)} "
            f"| {int(group.get('adverse_count') or 0)} "
            f"| `{group.get('decision') or 'retain_under_observation'}` |"
        )
    for group in groups:
        if not isinstance(group, facade.Mapping) or not group.get("examples"):
            continue
        lines += ["", f"## Examples: {group.get('reason')}", ""]
        for example in list(group.get("examples") or [])[:5]:
            if not isinstance(example, facade.Mapping):
                continue
            lines.append(
                f"- `{example.get('symbol') or '-'}` role `{example.get('role') or '-'}` "
                f"rank `{example.get('rank') if example.get('rank') is not None else '-'}` "
                f"latest {float(example.get('latest_return_pct') or 0.0):.4f}% "
                f"MFE {float(example.get('max_favorable_pct') or 0.0):.4f}% "
                f"MAE {float(example.get('max_adverse_pct') or 0.0):.4f}%"
            )
    return "\n".join(lines).rstrip() + "\n"
