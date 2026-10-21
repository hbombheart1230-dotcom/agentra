from __future__ import annotations

import json
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
from libs.reporting import q8_historical_projection_fast06 as _proj
from libs.reporting.q8_review_render_fast06 import render_q8_shadow_blocker_review_markdown


DEFAULT_REVIEW_REASONS = (
    "breakout_not_ready",
    "pullback_not_mature",
    "human_chart_sanity_guard_blocked",
    "volume_confirmation_missing",
    "below_vwap_reclaim_not_ready",
)


def _text(value: Any) -> str:
    return str(value or "").strip()


def _to_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except Exception:
        return None


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def _candidate_rows(payloads: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for payload in payloads:
        if not isinstance(payload, Mapping):
            continue
        for raw in list(payload.get("candidates") or []):
            if not isinstance(raw, Mapping):
                continue
            row = dict(raw)
            row.setdefault("_payload_generated_at", payload.get("generated_at"))
            rows.append(row)
    return rows


def _dedupe_rows(rows: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    return dedupe_q8_candidates(rows)


_checkpoint_values = _proj.checkpoint_values


def _avg(values: Sequence[float]) -> float:
    return round(sum(values) / len(values), 4) if values else 0.0


def _decision_for_row(row: Mapping[str, Any]) -> str:
    reason = _text(row.get("reason"))
    if reason == "volume_confirmation_missing":
        return "retain_under_observation"
    if reason in {"breakout_not_ready", "pullback_not_mature"}:
        return "adjust_and_retest"
    if reason == "human_chart_sanity_guard_blocked":
        return "promotion_review_target"
    return "retain_under_observation"


def _summarize_group(
    reason: str,
    rows: Sequence[Mapping[str, Any]],
    *,
    promotion_allowed: bool,
) -> Dict[str, Any]:
    return _proj.summarize_blocker_group(reason, rows, promotion_allowed=promotion_allowed, decide=_decision_for_row)


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
    trusted_forward_count = _proj.trusted_forward_count(rows, truthy=_bool)
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
    groups = _proj.group_blocker_rows(rows, review_reasons, promotion_allowed=promotion_allowed, decide=_decision_for_row)
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
