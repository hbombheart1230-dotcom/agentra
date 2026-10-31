from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

from libs.reporting.q8_evaluation_contract import (
    CANONICAL_DEDUPE_KEY_FIELDS,
    build_q8_trust_gate,
    dedupe_q8_candidates,
)
from libs.reporting.quant_shadow_candidate_evaluation import (
    CANDIDATE_EVALUATION_PAYLOAD_KEYS,
    build_quant_shadow_candidate_evaluation,
    load_quant_shadow_candidate_payloads,
)
from libs.reporting.quant_shadow_forward_outcomes import attach_forward_outcomes
from libs.reporting.market_regime_rail_review import classify_market_regime_rail, load_latest_macro_snapshot
from libs.reporting import q8_shadow_blocker_scalar_projection as _scalar_owner
from libs.reporting import q8_shadow_blocker_candidate_projection as _candidate_owner
from libs.reporting import q8_shadow_blocker_checkpoint_projection as _checkpoint_owner
from libs.reporting import q8_shadow_blocker_decision_projection as _decision_owner
from libs.reporting import q8_shadow_blocker_group_projection as _group_owner


DEFAULT_REVIEW_REASONS = (
    "breakout_not_ready",
    "pullback_not_mature",
    "human_chart_sanity_guard_blocked",
    "volume_confirmation_missing",
    "below_vwap_reclaim_not_ready",
)


def _text(value: Any) -> str:
    return _scalar_owner._text(value)


def _to_float(value: Any) -> float | None:
    return _scalar_owner._to_float(value)


def _bool(value: Any) -> bool:
    return _scalar_owner._bool(value)


def _candidate_rows(payloads: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    return _candidate_owner._candidate_rows(payloads, facade=sys.modules[__name__])


def _dedupe_rows(rows: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    return dedupe_q8_candidates(rows)


def _checkpoint_values(outcome: Mapping[str, Any]) -> Dict[str, Any]:
    return _checkpoint_owner._checkpoint_values(outcome, facade=sys.modules[__name__])


def _avg(values: Sequence[float]) -> float:
    return _scalar_owner._avg(values)


def _decision_for_row(row: Mapping[str, Any]) -> str:
    return _decision_owner._decision_for_row(row, facade=sys.modules[__name__])


def _summarize_group(
    reason: str,
    rows: Sequence[Mapping[str, Any]],
    *,
    promotion_allowed: bool,
) -> Dict[str, Any]:
    return _group_owner._summarize_group(reason, rows, promotion_allowed=promotion_allowed, facade=sys.modules[__name__])


def build_q8_shadow_blocker_review(
    payloads: Iterable[Mapping[str, Any]],
    *,
    minute_rows_by_symbol: Mapping[str, list[Mapping[str, Any]]] | None = None,
    review_reasons: Sequence[str] = DEFAULT_REVIEW_REASONS,
    market_regime_rail: Mapping[str, Any] | None = None,
    quant_shadow_evaluation: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    raw_rows = attach_forward_outcomes(_candidate_rows(payloads), minute_rows_by_symbol=minute_rows_by_symbol)
    rows = _dedupe_rows(raw_rows)
    trusted_forward_count = 0
    for row in rows:
        outcome = row.get("shadow_forward_outcome") if isinstance(row.get("shadow_forward_outcome"), Mapping) else {}
        if _bool(_checkpoint_values(outcome).get("available")):
            trusted_forward_count += 1
    trusted_forward_coverage = round(float(trusted_forward_count) / float(len(rows)), 4) if rows else 0.0
    evaluation_gate = (
        quant_shadow_evaluation.get("evaluation_trust_gate")
        if isinstance(quant_shadow_evaluation, Mapping)
        and isinstance(quant_shadow_evaluation.get("evaluation_trust_gate"), Mapping)
        else {}
    )
    trust_gate = (
        dict(evaluation_gate)
        if evaluation_gate
        else build_q8_trust_gate(
            raw_candidate_count=len(raw_rows),
            deduped_candidate_count=len(rows),
            trusted_forward_count=trusted_forward_count,
            trusted_forward_coverage=trusted_forward_coverage,
            candidate_watchlist=[],
        )
    )
    promotion_allowed = bool(trust_gate.get("promotion_allowed"))
    review_reason_set = {str(reason) for reason in review_reasons}
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        reason = _text(row.get("reason"))
        if reason in review_reason_set:
            grouped[reason].append(row)
    groups = [
        _summarize_group(reason, grouped.get(reason, []), promotion_allowed=promotion_allowed)
        for reason in review_reasons
    ]
    observed_total = sum(int(group.get("observed_count") or 0) for group in groups)
    return {
        "schema_version": "q8_shadow_blocker_review.v1",
        "behavior_effect": "evaluation_only",
        "market_regime_rail": dict(market_regime_rail or {}),
        "raw_candidate_count": len(raw_rows),
        "deduped_candidate_count": len(rows),
        "duplicate_count": max(0, len(raw_rows) - len(rows)),
        "dedupe_key": list(CANONICAL_DEDUPE_KEY_FIELDS),
        "evaluation_trust_gate": trust_gate,
        "promotion_allowed": promotion_allowed,
        "candidate_count": len(rows),
        "review_reason_count": len(groups),
        "observed_review_candidate_count": observed_total,
        "groups": groups,
    }


def render_q8_shadow_blocker_review_markdown(review: Mapping[str, Any], *, day: str) -> str:
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
    gate = review.get("evaluation_trust_gate") if isinstance(review.get("evaluation_trust_gate"), Mapping) else {}
    if gate:
        lines.extend(
            [
                f"- trust_gate: `{gate.get('status') or '-'}`",
                f"- promotion_allowed: `{bool(gate.get('promotion_allowed'))}`",
                f"- trust_block_reasons: `{', '.join(list(gate.get('block_reasons') or gate.get('reasons') or [])) or '-'}`",
            ]
        )
    rail = review.get("market_regime_rail") if isinstance(review.get("market_regime_rail"), Mapping) else {}
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
        if not isinstance(group, Mapping):
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
        if not isinstance(group, Mapping) or not group.get("examples"):
            continue
        lines += ["", f"## Examples: {group.get('reason')}", ""]
        for example in list(group.get("examples") or [])[:5]:
            if not isinstance(example, Mapping):
                continue
            lines.append(
                f"- `{example.get('symbol') or '-'}` role `{example.get('role') or '-'}` "
                f"rank `{example.get('rank') if example.get('rank') is not None else '-'}` "
                f"latest {float(example.get('latest_return_pct') or 0.0):.4f}% "
                f"MFE {float(example.get('max_favorable_pct') or 0.0):.4f}% "
                f"MAE {float(example.get('max_adverse_pct') or 0.0):.4f}%"
            )
    return "\n".join(lines).rstrip() + "\n"


def generate_q8_shadow_blocker_review(
    *,
    reports_root: Path,
    day: str,
) -> Dict[str, Any]:
    # Only `candidates`/`generated_at` are read from each payload below; projecting
    # at load time keeps a trading day's worth of unused payload keys out of memory.
    payloads = load_quant_shadow_candidate_payloads(
        reports_root=reports_root, days=[day], keys=CANDIDATE_EVALUATION_PAYLOAD_KEYS
    )
    market_regime_rail = classify_market_regime_rail(load_latest_macro_snapshot(day))
    quant_shadow_evaluation = build_quant_shadow_candidate_evaluation(payloads)
    review = build_q8_shadow_blocker_review(
        payloads,
        market_regime_rail=market_regime_rail,
        quant_shadow_evaluation=quant_shadow_evaluation,
    )
    out_dir = Path(reports_root) / "operator_summary" / "daily" / day
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "q8_shadow_blocker_review.json"
    md_path = out_dir / "q8_shadow_blocker_review.md"
    json_path.write_text(json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_q8_shadow_blocker_review_markdown(review, day=day), encoding="utf-8")
    return {**review, "report_json_path": str(json_path), "report_md_path": str(md_path)}


__all__ = [
    "DEFAULT_REVIEW_REASONS",
    "build_q8_shadow_blocker_review",
    "generate_q8_shadow_blocker_review",
    "render_q8_shadow_blocker_review_markdown",
]
