from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from libs.reporting.q8_historical_review import build_q8_historical_review_payload
from libs.reporting.quant_shadow_candidate_evaluation import (
    iter_quant_shadow_candidate_payloads_for_range,
)
from libs.reporting.quant_shadow_forward_outcomes import attach_forward_outcomes
from libs.runtime.broker_cost_profile import load_broker_cost_profile

from . import fast08_cumulative_projection as _cp
from .cost_basis_comparison import build_evaluation_cost_bases
from .episode_scanner_review import (
    build_episode_scanner_review,
    build_same_symbol_reentry_review,
)
from .post_reclaim_shadow_review import build_post_reclaim_shadow_review
from .scanner_quality import extract_pre_strategist_candidate_rows
from .scanner_alignment_root_cause import (
    build_scanner_alignment_root_cause_range,
)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _strategist_weighting_review(
    reports_root: Path,
    *,
    start: str,
    end: str,
) -> dict[str, Any]:
    daily_deltas: dict[str, list[float]] = {name: [] for name in _cp.DELTA_HORIZONS}
    source_root = reports_root / "evaluation" / "baseline_samsung_hynix"
    if source_root.exists():
        for day_dir in sorted(path for path in source_root.iterdir() if path.is_dir()):
            if not start <= day_dir.name <= end:
                continue
            payload = _read_json(day_dir / "q9_vs_samsung_hynix_daily_comparison.json")
            for name, delta in _cp.strategist_day_delta(payload).items():
                daily_deltas[name].append(delta)
    return _cp.strategist_weighting_review(daily_deltas)


_rank_row = _cp.rank_row


def _candidate_rows(
    *,
    episode_review: Mapping[str, Any],
    reentry_review: Mapping[str, Any],
    post_reclaim_review: Mapping[str, Any],
    strategist_review: Mapping[str, Any],
) -> list[dict[str, Any]]:
    rank1 = _rank_row(episode_review, bucket="rank1", horizon="+30m")
    rank23 = _rank_row(episode_review, bucket="rank2_3", horizon="+30m")
    rank1_live = float(
        (rank1.get("live_net") or {}).get("expectancy_pct") or 0.0
    )
    rank23_live = float(
        (rank23.get("live_net") or {}).get("expectancy_pct") or 0.0
    )
    strategist_30 = next(
        (
            row
            for row in strategist_review.get("rows") or []
            if isinstance(row, Mapping) and row.get("horizon") == "+30m"
        ),
        {},
    )
    return [
        {
            "priority": 1,
            "candidate": "same_symbol_loss_reentry_control",
            "class": "damage_reduction",
            "status": (
                "APPLIED_2026_07_29"
                if reentry_review.get("behavior_candidate_eligible")
                else "INSUFFICIENT_EVIDENCE"
            ),
            "evidence": {
                "repeat_count": (reentry_review.get("repeat_entry") or {}).get("count"),
                "repeat_expectancy_pct": (
                    reentry_review.get("repeat_entry") or {}
                ).get("expectancy_pct"),
                "repeat_minus_first_expectancy_pct": reentry_review.get(
                    "repeat_minus_first_expectancy_pct"
                ),
                "repeat_after_loss": reentry_review.get("repeat_after_loss"),
                "repeat_after_non_loss": reentry_review.get(
                    "repeat_after_non_loss"
                ),
            },
        },
        {
            "priority": 2,
            "candidate": "confirmed_post_reclaim_pullback_subtype",
            "class": "alpha_research",
            "status": post_reclaim_review.get("promotion_status"),
            "evidence": {
                "observed_count": post_reclaim_review.get("observed_count"),
                "observed_day_count": post_reclaim_review.get("observed_day_count"),
                "horizon_rows": post_reclaim_review.get("rows"),
            },
        },
        {
            "priority": 3,
            "candidate": "scanner_rank_ordering_component_review",
            "class": "ranking_diagnosis",
            "status": (
                "DIAGNOSTIC_CANDIDATE"
                if rank1_live <= 0 and rank23_live <= 0
                and (episode_review.get("score_component_review") or {}).get(
                    "status"
                )
                == "READY"
                else "OBSERVABILITY_NOT_READY"
                if (episode_review.get("score_component_review") or {}).get(
                    "status"
                )
                != "READY"
                else "RETAIN_UNDER_OBSERVATION"
            ),
            "evidence": {
                "rank1_live_net_30m_pct": rank1_live,
                "rank2_3_live_net_30m_pct": rank23_live,
                "rank1_minus_rank2_3_gross_30m_pct": episode_review.get(
                    "rank1_minus_rank2_3_gross_30m_pct"
                ),
                "score_component_review": episode_review.get(
                    "score_component_review"
                ),
            },
        },
        {
            "priority": 4,
            "candidate": "strategist_ranking_weight_guard",
            "class": "strategist_effectiveness",
            "status": (
                "DIAGNOSTIC_CANDIDATE"
                if float(
                    strategist_30.get("avg_strategist_minus_scanner_pct") or 0.0
                )
                < 0
                else "RETAIN_UNDER_OBSERVATION"
            ),
            "evidence": dict(strategist_30),
        },
    ]


def build_cumulative_improvement_review(
    *,
    reports_root: Path,
    start: str,
    end: str,
    payloads: list[dict[str, Any]] | None = None,
    historical_review: Mapping[str, Any] | None = None,
    q14_range: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    reports_root = Path(reports_root)
    cost_bases = build_evaluation_cost_bases(load_broker_cost_profile(None))
    mock_drag = float(
        (cost_bases.get("mock_observed") or {}).get(
            "total_drag_with_slippage_pct"
        )
        or 0.0
    )
    live_drag = float(
        (cost_bases.get("live_deployment_equity") or {}).get(
            "total_drag_with_slippage_pct"
        )
        or 0.0
    )
    prepared_scanner_rows: list[dict[str, Any]] | None = None
    if payloads is not None:
        source_payloads = payloads
    else:
        source_payloads = []
        deduped_rows: dict[tuple[str, str, int], dict[str, Any]] = {}
        for payload in iter_quant_shadow_candidate_payloads_for_range(
            reports_root=reports_root,
            start=start,
            end=end,
        ):
            for row in extract_pre_strategist_candidate_rows([payload]):
                key = (
                    str(row.get("q9_decision_id") or ""),
                    str(row.get("symbol") or ""),
                    int(float(row.get("rank") or 0)),
                )
                deduped_rows[key] = row
        prepared_scanner_rows = attach_forward_outcomes(list(deduped_rows.values()))
    q8 = (
        dict(historical_review)
        if historical_review is not None
        else build_q8_historical_review_payload(
            reports_root=reports_root,
            start=start,
            end=end,
        )
    )
    q14 = (
        dict(q14_range)
        if q14_range is not None
        else build_scanner_alignment_root_cause_range(
            reports_root=reports_root,
            start=start,
            end=end,
        )
    )
    episode_review = build_episode_scanner_review(
        source_payloads,
        mock_drag_pct=mock_drag,
        live_drag_pct=live_drag,
        prepared_rows=prepared_scanner_rows,
    )
    reentry_review = build_same_symbol_reentry_review(q14.get("rows") or [])
    post_reclaim_review = build_post_reclaim_shadow_review(
        q8,
        mock_drag_pct=mock_drag,
        live_drag_pct=live_drag,
    )
    strategist_review = _strategist_weighting_review(
        reports_root,
        start=start,
        end=end,
    )
    candidates = _candidate_rows(
        episode_review=episode_review,
        reentry_review=reentry_review,
        post_reclaim_review=post_reclaim_review,
        strategist_review=strategist_review,
    )
    outcome_conditioned_count = _cp.outcome_conditioned_trade_count(q14)
    return {
        "schema_version": "cumulative_improvement_review.v1",
        "behavior_effect": "evaluation_only",
        "range": {"start": start, "end": end},
        "active_validation": "same_symbol_loss_reentry_control",
        "behavior_patch_authorized": bool(
            reentry_review.get("behavior_candidate_eligible")
        ),
        "cost_bases": cost_bases,
        "q14_causal_interpretation": {
            "largest_legacy_behavior_root_cause": q14.get(
                "largest_behavior_root_cause"
            ),
            "largest_structural_root_cause": q14.get(
                "largest_structural_root_cause"
            ),
            "outcome_conditioned_trade_count": outcome_conditioned_count,
            "rule": (
                "Outcome-conditioned Q14 labels cannot independently authorize "
                "a Scanner behavior patch."
            ),
        },
        "episode_scanner_review": episode_review,
        "same_symbol_reentry_review": reentry_review,
        "post_reclaim_shadow_review": post_reclaim_review,
        "strategist_weighting_review": strategist_review,
        "improvement_candidates": candidates,
        "next_decision": (
            "Run one full-day contract smoke test for the Q17 repair and the "
            "same-symbol loss reentry control. Do not add another behavior patch."
        ),
    }


render_cumulative_improvement_review = _cp.render_cumulative_improvement_review


def write_cumulative_improvement_review(
    *,
    reports_root: Path,
    start: str,
    end: str,
) -> dict[str, str]:
    payload = build_cumulative_improvement_review(
        reports_root=reports_root,
        start=start,
        end=end,
    )
    output_dir = (
        Path(reports_root) / "evaluation" / "range" / f"{start}_{end}"
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "cumulative_improvement_review.json"
    markdown_path = output_dir / "cumulative_improvement_review.md"
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    markdown_path.write_text(
        render_cumulative_improvement_review(payload),
        encoding="utf-8",
    )
    return {"json": str(json_path), "markdown": str(markdown_path)}


__all__ = [
    "build_cumulative_improvement_review",
    "render_cumulative_improvement_review",
    "write_cumulative_improvement_review",
]
