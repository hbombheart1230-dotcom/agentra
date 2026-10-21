from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping

from libs.reporting.q8_evaluation_contract import (
    DUPLICATE_RATE_MAX,
    PROMOTION_CANDIDATE_MIN_DAYS,
    PROMOTION_CANDIDATE_MIN_OBSERVED,
    TRUSTED_FORWARD_MIN_COUNT,
    TRUSTED_FORWARD_MIN_COVERAGE,
)
from libs.reporting import q8_historical_projection_fast06 as _proj
from libs.reporting import q8_review_render_fast06 as _render
from libs.reporting.quant_shadow_candidate_evaluation import (
    build_quant_shadow_candidate_evaluation,
    load_quant_shadow_candidate_payloads,
)


def _iter_days(start: str, end: str) -> Iterable[str]:
    current = date.fromisoformat(str(start)[:10])
    final = date.fromisoformat(str(end)[:10])
    while current <= final:
        yield current.isoformat()
        current += timedelta(days=1)


_fmt_pct = _render._reagg_fmt_pct
_fmt_num = _render._reagg_fmt_num
_watchlist_rows = _proj.watchlist_rows


def build_q8_trusted_reaggregation(*, reports_root: Path, start: str, end: str) -> Dict[str, Any]:
    daily: List[Dict[str, Any]] = []
    all_payloads: List[Dict[str, Any]] = []
    promotion_allowed_day_count = 0
    for day in _iter_days(start, end):
        payloads = load_quant_shadow_candidate_payloads(reports_root=reports_root, days=[day])
        if not payloads:
            continue
        all_payloads.extend(payloads)
        evaluation = build_quant_shadow_candidate_evaluation(payloads)
        row = _proj.reaggregation_day_row(day, evaluation)
        daily.append(row)
        if row["promotion_allowed"]:
            promotion_allowed_day_count += 1

    cumulative_evaluation = build_quant_shadow_candidate_evaluation(all_payloads) if all_payloads else {}
    aggregate = _proj.reaggregation_aggregate(
        cumulative_evaluation, promotion_allowed_day_count=promotion_allowed_day_count
    )
    return {
        "schema_version": "q8_trusted_reaggregation.v2",
        "behavior_effect": "evaluation_only",
        "generated_with": "same_day_max_delay_forward_outcomes_deduped_candidates_and_trust_gate",
        "range": {"start": str(start)[:10], "end": str(end)[:10], "days_with_payloads": len(daily)},
        "aggregate": aggregate,
        "daily": daily,
        "important_note": (
            "Promotion decisions must use trusted same-day forward outcomes, deduped candidates, "
            "and promotion_allowed=true trust-gate rows only."
        ),
    }


def render_q8_trusted_reaggregation_markdown(payload: Mapping[str, Any]) -> str:
    return _render.render_q8_trusted_reaggregation_markdown(
        payload,
        trusted_forward_min_count=TRUSTED_FORWARD_MIN_COUNT,
        trusted_forward_min_coverage=TRUSTED_FORWARD_MIN_COVERAGE,
        duplicate_rate_max=DUPLICATE_RATE_MAX,
        promotion_candidate_min_observed=PROMOTION_CANDIDATE_MIN_OBSERVED,
        promotion_candidate_min_days=PROMOTION_CANDIDATE_MIN_DAYS,
    )


def write_q8_trusted_reaggregation(
    *,
    reports_root: Path,
    start: str,
    end: str,
    output_dir: Path,
) -> Dict[str, Path]:
    payload = build_q8_trusted_reaggregation(reports_root=reports_root, start=start, end=end)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"q8_trusted_reaggregation_{str(start)[:10]}_to_{str(end)[:10]}"
    json_path = output_dir / f"{stem}.json"
    md_path = output_dir / f"{stem}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_q8_trusted_reaggregation_markdown(payload), encoding="utf-8")
    return {"json": json_path, "markdown": md_path}
