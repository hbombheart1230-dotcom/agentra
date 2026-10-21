from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from libs.reporting.evaluation import fast07_attribution_projection as _attr
from libs.reporting.evaluation import fast07_chain_render_projection as _render
from libs.reporting.evaluation.trade_read_model import build_q9_trade_read_model
from libs.reporting.evaluation.artifact_inventory import iter_trade_dirs
from libs.reporting.q8_evaluation_contract import candidate_day
from libs.reporting.quant_shadow_candidate_evaluation import (
    Q9_ROW_KEYS_UNUSED_BY_FULL_CHAIN,
    _iter_days,
    load_quant_shadow_candidate_payloads_for_range,
)
from libs.reporting.quant_shadow_forward_outcomes import attach_forward_outcomes
from libs.runtime.broker_cost_profile import load_broker_cost_profile


HORIZONS = _attr.LENS_HORIZONS
BLOCKERS_OF_INTEREST = _attr.BLOCKERS_OF_INTEREST

_text = _attr.text
_num = _attr.lens_num
_as_dict = _attr.as_dict
_metric_avg = _render.lens_metric_avg
_checkpoint = _attr.lens_checkpoint
_checkpoint_return = _attr.lens_checkpoint_return
_checkpoint_mfe = _attr.lens_checkpoint_mfe
_checkpoint_mae = _attr.lens_checkpoint_mae
_rail = _attr.market_rail
_blocker = _attr.blocker_label


def _cost_floor_pct() -> float:
    profile = load_broker_cost_profile()
    for key in ("conservative_round_trip_cost_pct", "round_trip_cost_pct", "ema_round_trip_cost_pct"):
        value = _num(profile.get(key))
        if value is not None and value > 0:
            return value * 100.0 if value < 1 else value
    return 0.0


def _candidate_rows(payloads: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = _attr.raw_candidate_rows(payloads)
    return attach_forward_outcomes(rows)


def _q9_candidate_rows(payloads: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = _attr.raw_candidate_rows(payloads, key="q9_decision_candidates")
    return attach_forward_outcomes(rows)


def _forward_group(rows: list[dict[str, Any]], group_key: str, *, cost_floor_pct: float) -> list[dict[str, Any]]:
    return _attr.lens_forward_group(rows, group_key, cost_floor_pct=cost_floor_pct, day_of=candidate_day)


def _blocker_forward_review(rows: list[dict[str, Any]], *, cost_floor_pct: float) -> dict[str, Any]:
    return _attr.blocker_forward_review(rows, cost_floor_pct=cost_floor_pct, day_of=candidate_day)


_best_role_by_horizon = _attr.best_role_by_horizon
_strategist_delta_review = _attr.strategist_delta_review


def _trade_models(reports_root: Path, start: str, end: str) -> list[dict[str, Any]]:
    from datetime import date, timedelta

    current = date.fromisoformat(start[:10])
    final = date.fromisoformat(end[:10])
    out: list[dict[str, Any]] = []
    while current <= final:
        for trade_dir in iter_trade_dirs(reports_root, current.isoformat()):
            out.append(build_q9_trade_read_model(trade_dir))
        current += timedelta(days=1)
    return out


_exit_counterfactual_review = _attr.exit_counterfactual_review
_ForwardGroupAccumulator = _attr.ForwardGroupAccumulator
_StrategistDeltaAccumulator = _attr.StrategistDeltaAccumulator
_ROLES_FOR_BEST_ROLE = _attr.ROLES_FOR_BEST_ROLE


def _BlockerReviewAccumulator(cost_floor_pct: float) -> _attr.BlockerReviewAccumulator:
    return _attr.BlockerReviewAccumulator(cost_floor_pct, day_of=candidate_day)


def build_evaluation_lens_report(*, reports_root: Path, start: str, end: str) -> dict[str, Any]:
    # q9 rows only feed _strategist_delta_review (forward outcomes/roles); the bulky q9 row keys are
    # read nowhere (the lens's entry_lane_observation use is on the `candidates` rows).
    # The range runs from the freeze start (2026-06-29) to `end` -- every shadow payload since then
    # (tens of GB of JSON). Materialising it all (as this used to) grows without bound and is what
    # exhausted the closeout container; instead each day is loaded, turned into forward-outcome rows,
    # folded into the two accumulators and dropped. The reviews' outputs are unchanged.
    cost_floor = _cost_floor_pct()
    blocker_review = _BlockerReviewAccumulator(cost_floor)
    strategist_review = _StrategistDeltaAccumulator()
    payload_count = candidate_count = q9_candidate_count = 0
    for day in _iter_days(start, end):
        payloads = load_quant_shadow_candidate_payloads_for_range(
            reports_root=reports_root, start=day, end=day, drop_q9_row_keys=Q9_ROW_KEYS_UNUSED_BY_FULL_CHAIN
        )
        payload_count += len(payloads)
        candidates = _candidate_rows(payloads)
        candidate_count += len(candidates)
        blocker_review.add_rows(candidates)
        del candidates
        q9_rows = _q9_candidate_rows(payloads)
        q9_candidate_count += len(q9_rows)
        strategist_review.add_rows(q9_rows)
        del q9_rows, payloads
    models = _trade_models(reports_root, start, end)
    return {
        "schema_version": "evaluation_lens_report.v1",
        "behavior_effect": "evaluation_only",
        "range": {"start": start[:10], "end": end[:10]},
        "freeze_safe": True,
        "behavior_change_authorized": False,
        "evidence": {
            "shadow_payload_count": payload_count,
            "candidate_count": candidate_count,
            "q9_candidate_count": q9_candidate_count,
            "trade_model_count": len(models),
        },
        "blocker_forward_review": blocker_review.result(),
        "strategist_delta_review": strategist_review.result(),
        "exit_hold_counterfactual_review": _exit_counterfactual_review(models),
        "next_required_observations": [
            "blocker forward outcome by market rail",
            "MFE/MAE and cost-floor reachability for every blocked lane",
            "strategist-vs-scanner delta by horizon",
            "commander-vs-strategist delta by horizon",
            "exit hold counterfactual by exit reason",
        ],
    }


render_evaluation_lens_report = _render.render_evaluation_lens_report


def write_evaluation_lens_report(
    *,
    reports_root: Path,
    start: str,
    end: str,
    output_dir: Path | None = None,
) -> dict[str, str]:
    payload = build_evaluation_lens_report(reports_root=Path(reports_root), start=start, end=end)
    out_dir = Path(output_dir) if output_dir else Path(reports_root) / "evaluation" / "lens" / end[:10]
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "evaluation_lens_report.json"
    md_path = out_dir / "evaluation_lens_report.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_evaluation_lens_report(payload), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}
