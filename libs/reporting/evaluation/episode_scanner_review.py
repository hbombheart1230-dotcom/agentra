from __future__ import annotations

from typing import Any, Mapping, Sequence

from libs.reporting.q8_evaluation_contract import candidate_day

from . import fast08_scanner_attribution as _sa
from .metrics import performance_metrics
from .scanner_quality import SCANNER_HORIZONS, pre_strategist_candidate_rows


RANK_BUCKETS = ("rank1", "rank2_3", "rank4_plus", "unknown")


_number = _sa.number
_mapping = _sa.mapping
_checkpoint_return = _sa.observed_return
_epoch = _sa.baseline_epoch
_setup_key = _sa.setup_key
_rank_bucket = _sa.episode_rank_bucket


def _day(row: Mapping[str, Any]) -> str:
    return _sa.compact_day(row, candidate_day)


def _episode_representatives(
    rows: Sequence[Mapping[str, Any]],
    *,
    episode_gap_sec: int,
) -> list[dict[str, Any]]:
    return _sa.episode_representatives(
        rows, episode_gap_sec=episode_gap_sec, horizons=SCANNER_HORIZONS, day_of=candidate_day
    )


def build_episode_scanner_review(
    payloads: list[dict[str, Any]],
    *,
    mock_drag_pct: float,
    live_drag_pct: float,
    episode_gap_sec: int = 900,
    prepared_rows: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    rows = (
        [dict(row) for row in prepared_rows]
        if prepared_rows is not None
        else pre_strategist_candidate_rows(payloads)
    )
    episodes = _episode_representatives(rows, episode_gap_sec=episode_gap_sec)
    output = _sa.rank_horizon_rows(
        episodes,
        buckets=RANK_BUCKETS,
        horizons=SCANNER_HORIZONS,
        mock_drag_pct=mock_drag_pct,
        live_drag_pct=live_drag_pct,
    )
    observed_30m_episodes = [row for row in episodes if row["returns"].get("+30m") is not None]
    component_covered = [row for row in observed_30m_episodes if row.get("score_breakdown")]
    component_rows = _sa.score_component_rows(component_covered, live_drag_pct=live_drag_pct)
    component_coverage = (
        len(component_covered) / len(observed_30m_episodes)
        if observed_30m_episodes
        else 0.0
    )
    rank1_value = _sa.bucket_expectancy(output, "rank1", "+30m")
    rank23_value = _sa.bucket_expectancy(output, "rank2_3", "+30m")
    return {
        "schema_version": "episode_scanner_review.v1",
        "behavior_effect": "evaluation_only",
        "episode_gap_sec": int(episode_gap_sec),
        "raw_candidate_row_count": len(rows),
        "episode_count": len(episodes),
        "compression_ratio": round(len(episodes) / len(rows), 4) if rows else 0.0,
        "cost_drag_pct": {
            "mock": round(float(mock_drag_pct), 6),
            "live": round(float(live_drag_pct), 6),
        },
        "rank_horizon_rows": output,
        "score_component_review": {
            "status": (
                "READY"
                if len(component_covered) >= 20 and component_coverage >= 0.70
                else "NOT_READY_MISSING_SCORE_COMPONENT_ARTIFACT"
            ),
            "forward_observed_episode_count": len(observed_30m_episodes),
            "component_covered_episode_count": len(component_covered),
            "coverage": round(component_coverage, 4),
            "rows": component_rows,
        },
        "rank1_minus_rank2_3_gross_30m_pct": (
            round(rank1_value - rank23_value, 4)
            if rank1_value is not None and rank23_value is not None
            else None
        ),
        "episodes": episodes,
        "limitations": [
            "An episode is the first observation after a 15-minute same-symbol/setup gap.",
            "Episodes reduce serial duplication but are not randomized independent trades.",
            "This report does not change Scanner ranking or execution.",
        ],
    }


def build_same_symbol_reentry_review(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    series = _sa.reentry_series(rows)
    grouped_count = series["group_count"]
    repeated_groups = series["repeated_group_count"]
    first_values = series["first"]
    repeat_values = series["repeat"]
    repeat_after_loss_values = series["after_loss"]
    repeat_after_non_loss_values = series["after_non_loss"]

    first_metrics = performance_metrics(first_values)
    repeat_metrics = performance_metrics(repeat_values)
    repeat_after_loss_metrics = performance_metrics(repeat_after_loss_values)
    repeat_after_non_loss_metrics = performance_metrics(repeat_after_non_loss_values)
    return {
        "schema_version": "same_symbol_reentry_review.v1",
        "behavior_effect": "evaluation_only",
        "day_symbol_group_count": grouped_count,
        "repeated_day_symbol_group_count": repeated_groups,
        "first_entry": first_metrics,
        "repeat_entry": repeat_metrics,
        "repeat_after_loss": repeat_after_loss_metrics,
        "repeat_after_non_loss": repeat_after_non_loss_metrics,
        "repeat_minus_first_expectancy_pct": round(
            float(repeat_metrics.get("expectancy_pct") or 0.0)
            - float(first_metrics.get("expectancy_pct") or 0.0),
            4,
        ),
        "behavior_candidate_eligible": bool(
            len(repeat_after_loss_values) >= 20
            and float(repeat_after_loss_metrics.get("expectancy_pct") or 0.0)
            < float(first_metrics.get("expectancy_pct") or 0.0) - 0.20
            and float(repeat_after_loss_metrics.get("win_rate") or 0.0)
            < float(first_metrics.get("win_rate") or 0.0)
        ),
        "limitations": [
            "This is an observational prior-outcome-conditioned comparison.",
            "It supports damage reduction, not a claim that a cooldown creates alpha.",
        ],
    }


__all__ = [
    "build_episode_scanner_review",
    "build_same_symbol_reentry_review",
]
