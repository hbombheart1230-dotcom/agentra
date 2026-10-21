from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping

from libs.reporting.q8_evaluation_contract import candidate_day
from libs.reporting.quant_shadow_candidate_evaluation import (
    load_quant_shadow_candidate_payloads_for_range,
)
from libs.runtime.broker_cost_profile import load_broker_cost_profile

from .loss_decomposition import _candidate_rows, _checkpoint_return
from . import fast07_chain_render_projection as _render
from . import fast07_trade_projection as _proj
from .metrics import performance_metrics


HORIZONS = ("+5m", "+15m", "+30m", "+60m")
MIN_OBSERVATIONS = 20
MIN_DAYS = 3
MAX_DAY_SHARE = 0.60
MAX_SYMBOL_SHARE = 0.40
MIN_AVERAGE_NET_RETURN_PCT = 0.30
MIN_NET_PROFIT_FACTOR = 1.20


def _text(value: Any, fallback: str = "unknown") -> str:
    text = str(value or "").strip()
    return text if text else fallback


def _lane_observation(row: Mapping[str, Any]) -> dict[str, Any]:
    value = row.get("entry_lane_observation")
    return dict(value) if isinstance(value, Mapping) else {}


_group_key = _proj.horizon_group_key
_profit_factor = _proj.profit_factor


def _row_facts(candidates: list[dict[str, Any]]) -> dict[int, tuple[str, dict[str, float | None]]]:
    """Per-row day and per-horizon returns, converted once and shared by every combination."""
    return {
        id(row): (candidate_day(row) or "unknown", {horizon: _checkpoint_return(row, horizon) for horizon in HORIZONS})
        for row in candidates
    }


def _combo_rows(
    candidates: list[dict[str, Any]],
    *,
    dimensions: tuple[str, ...],
    cost_pct: float,
    facts: dict[int, tuple[str, dict[str, float | None]]] | None = None,
) -> list[dict[str, Any]]:
    facts = facts if facts is not None else _row_facts(candidates)
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in candidates:
        grouped[_group_key(row, dimensions)].append(row)

    output: list[dict[str, Any]] = []
    for key, members in grouped.items():
        for horizon in HORIZONS:
            observations: list[tuple[dict[str, Any], float]] = []
            for row in members:
                gross = facts[id(row)][1][horizon]
                if gross is not None:
                    observations.append((row, gross))
            if not observations:
                continue
            stats = _proj.horizon_observation_stats(observations, cost_pct=cost_pct, day_of=lambda row: facts[id(row)][0])
            count = stats["count"]
            net_values = stats["net_values"]
            days = stats["days"]
            symbols = stats["symbols"]
            max_day_share = stats["max_day_share"]
            max_symbol_share = stats["max_symbol_share"]
            avg_gross = stats["avg_gross"]
            avg_net = stats["avg_net"]
            profit_factor = stats["profit_factor"]
            daily_net_returns = stats["daily_net_returns"]
            leave_one_day_out = stats["leave_one_day_out"]
            worst_lodo = stats["worst_lodo"]
            robust_across_days = stats["robust_across_days"]
            eligible = (
                count >= MIN_OBSERVATIONS
                and len(days) >= MIN_DAYS
                and max_day_share <= MAX_DAY_SHARE
                and max_symbol_share <= MAX_SYMBOL_SHARE
            )
            positive = (
                eligible
                and avg_net >= MIN_AVERAGE_NET_RETURN_PCT
                and profit_factor >= MIN_NET_PROFIT_FACTOR
                and robust_across_days
            )
            output.append({
                "dimensions": dict(zip(dimensions, key)),
                "horizon": horizon,
                "candidate_count": len(members),
                "observed_count": count,
                "observed_day_count": len(days),
                "observed_symbol_count": len(symbols),
                "coverage": round(count / len(members), 4) if members else 0.0,
                "average_gross_return_pct": round(avg_gross, 4),
                "round_trip_cost_pct": round(cost_pct, 4),
                "average_net_return_pct": round(avg_net, 4),
                "net_win_rate": round(sum(1 for value in net_values if value > 0) / count, 4),
                "net_profit_factor": profit_factor,
                "net_maximum_drawdown_pct": performance_metrics(net_values)["maximum_drawdown_pct"],
                "daily_net_returns_pct": daily_net_returns,
                "positive_day_count": sum(
                    1 for value in daily_net_returns.values() if value > 0
                ),
                "leave_one_day_out_net_returns_pct": leave_one_day_out,
                "worst_leave_one_day_out_net_return_pct": worst_lodo,
                "robust_across_days": robust_across_days,
                "maximum_day_share": round(max_day_share, 4),
                "maximum_symbol_share": round(max_symbol_share, 4),
                "top_days": [{"day": name, "count": value} for name, value in days.most_common(3)],
                "top_symbols": [{"symbol": name, "count": value} for name, value in symbols.most_common(5)],
                "evidence_eligible": eligible,
                "cost_positive": positive,
                "decision": (
                    "CONTROLLED_ADOPTION_CANDIDATE"
                    if positive
                    else "INSUFFICIENT_EVIDENCE"
                    if not eligible
                    else "RETAIN_UNDER_OBSERVATION"
                    if avg_net > 0
                    else "REJECT_COST_NEGATIVE"
                ),
            })
    return sorted(
        output,
        key=lambda row: (
            not bool(row["cost_positive"]),
            -float(row["average_net_return_pct"]),
            -int(row["observed_count"]),
        ),
    )


def build_horizon_alignment_review(
    *,
    reports_root: Path,
    start: str,
    end: str,
    cost_profile_path: Path | None = None,
) -> dict[str, Any]:
    payloads = load_quant_shadow_candidate_payloads_for_range(
        reports_root=reports_root,
        start=start,
        end=end,
    )
    candidates = _candidate_rows(payloads)
    facts = _row_facts(candidates)
    profile = load_broker_cost_profile(cost_profile_path)
    cost_ratio = float(
        profile.get("conservative_round_trip_cost_pct")
        or profile.get("ema_round_trip_cost_pct")
        or 0.009
    )
    cost_pct = cost_ratio * 100.0
    time_tactic = _combo_rows(
        candidates,
        dimensions=("time_bucket", "tactic"),
        cost_pct=cost_pct,
        facts=facts,
    )
    time_lane = _combo_rows(
        candidates,
        dimensions=("time_bucket", "primary_lane"),
        cost_pct=cost_pct,
        facts=facts,
    )
    time_tactic_rail = _combo_rows(
        candidates,
        dimensions=("time_bucket", "tactic", "market_regime_rail"),
        cost_pct=cost_pct,
        facts=facts,
    )
    candidates_for_adoption = [
        row for row in time_tactic
        if row.get("cost_positive")
    ]
    observation_candidates = [
        row for row in time_tactic
        if row.get("decision") == "RETAIN_UNDER_OBSERVATION"
    ]
    decision = (
        "CONTROLLED_ADOPTION_CANDIDATE_FOUND"
        if candidates_for_adoption
        else "RETAIN_UNDER_OBSERVATION"
        if observation_candidates
        else "NO_COST_POSITIVE_COMBINATION"
    )
    return {
        "schema_version": "horizon_alignment_review.v2",
        "behavior_effect": "evaluation_only",
        "range": {"start": start[:10], "end": end[:10]},
        "cost_model": {
            "source": str(profile.get("source") or "fallback"),
            "sample_count": int(profile.get("sample_count") or 0),
            "ema_round_trip_cost_pct": float(profile.get("ema_round_trip_cost_pct") or 0.0) * 100.0,
            "conservative_round_trip_cost_pct": cost_pct,
            "profile_path": str(cost_profile_path or "data/state/broker_cost_profile.json"),
        },
        "eligibility_contract": {
            "minimum_observations": MIN_OBSERVATIONS,
            "minimum_days": MIN_DAYS,
            "maximum_day_share": MAX_DAY_SHARE,
            "maximum_symbol_share": MAX_SYMBOL_SHARE,
            "net_profit_factor_min": MIN_NET_PROFIT_FACTOR,
            "average_net_return_min_pct": MIN_AVERAGE_NET_RETURN_PCT,
            "leave_one_day_out_net_return_positive": True,
        },
        "candidate_count": len(candidates),
        "decision": decision,
        "controlled_adoption_candidates": candidates_for_adoption,
        "observation_candidates": observation_candidates,
        "time_tactic": time_tactic,
        "time_lane": time_lane,
        "time_tactic_market_rail": time_tactic_rail,
        "next_action": {
            "behavior_change_authorized": False,
            "decision": (
                "PREPARE_SHADOW_POLICY_SPEC"
                if candidates_for_adoption
                else "KEEP_FIXED_SHADOW_OBSERVATION"
                if observation_candidates
                else "REJECT_CURRENT_HYPOTHESIS_AND_RESEARCH_NEW_ALPHA"
            ),
            "reason": (
                "At least one time/tactic/horizon combination remains materially positive after "
                "observed costs, concentration checks, and leave-one-day-out validation."
                if candidates_for_adoption
                else "A combination is marginally positive after cost but fails the fixed robustness "
                "contract; it is not eligible for controlled adoption."
                if observation_candidates
                else "No time/tactic/horizon combination survives observed cost and robustness checks."
            ),
        },
    }


render_horizon_alignment_review = _render.render_horizon_alignment_review


def write_horizon_alignment_review(
    *,
    reports_root: Path,
    start: str,
    end: str,
    output_dir: Path,
    cost_profile_path: Path | None = None,
) -> dict[str, str]:
    payload = build_horizon_alignment_review(
        reports_root=reports_root,
        start=start,
        end=end,
        cost_profile_path=cost_profile_path,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "horizon_alignment_review.json"
    md_path = output_dir / "horizon_alignment_review.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_horizon_alignment_review(payload), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}
