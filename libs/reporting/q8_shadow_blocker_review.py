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
from libs.reporting import q8_shadow_blocker_review_build_projection as _build_review_owner
from libs.reporting import q8_shadow_blocker_markdown_projection as _markdown_review_owner


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
    return _build_review_owner.build_q8_shadow_blocker_review(payloads, minute_rows_by_symbol=minute_rows_by_symbol, review_reasons=review_reasons, market_regime_rail=market_regime_rail, quant_shadow_evaluation=quant_shadow_evaluation, facade=sys.modules[__name__])


def render_q8_shadow_blocker_review_markdown(review: Mapping[str, Any], *, day: str) -> str:
    return _markdown_review_owner.render_q8_shadow_blocker_review_markdown(review, day=day, facade=sys.modules[__name__])


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
