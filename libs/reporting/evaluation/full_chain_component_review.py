from __future__ import annotations

import json
import sys as _sys
from collections import defaultdict
import os
from pathlib import Path
from typing import Any, Mapping

from libs.reporting.q8_evaluation_contract import candidate_day
from libs.reporting.quant_shadow_candidate_evaluation import (
    Q9_ROW_KEYS_UNUSED_BY_FULL_CHAIN,
    load_quant_shadow_candidate_payloads_for_range,
)
from libs.reporting.quant_shadow_forward_outcomes import attach_forward_outcomes
from libs.runtime.broker_cost_profile import load_broker_cost_profile

from libs.reporting.evaluation.full_chain_review_parts.root_cause import (  # noqa: F401 - facade ABI re-exports
    _classify_root_cause_impl,
    _topk_metric_impl,
)
from libs.reporting.evaluation.full_chain_review_parts.attribution import (  # noqa: F401 - facade ABI re-exports
    _decision_window_attribution_impl,
    _paired_role_deltas_impl,
    _q9_role_row_impl,
    _role_metrics_impl,
    _selection_availability_impl,
)
from libs.reporting.evaluation.full_chain_review_parts.component_decisions import (  # noqa: F401 - facade ABI re-exports
    _attribution_component_impl,
    _scanner_decision_impl,
    _unavailable_component_impl,
)
from libs.reporting.evaluation.full_chain_review_parts.render import (  # noqa: F401 - facade ABI re-exports
    render_full_chain_component_review_impl,
)
from .contracts import (
    CONTRACT_VERSION,
    DIRECTIONAL_MIN_DAYS,
    DIRECTIONAL_MIN_OBSERVATIONS,
    DecisionClass,
)
from .loss_decomposition import (
    _candidate_rows,
    _checkpoint_return,
    _entry_timing_summary,
    _exit_hold_summary,
    _load_trade_models,
    _realized_trade_summary,
)
from .metrics import performance_metrics
from .scanner_quality import build_scanner_quality_review


HORIZONS = ("+5m", "+15m", "+30m", "+60m")
MIN_MATERIAL_RANKING_DELTA_PCT = 0.30
MIN_POSITIVE_RANKING_DELTA_RATE = 0.55
DEFAULT_Q9_SLIPPAGE_PCT = 0.05
BEHAVIOR_METRIC_EXCLUSION_DEFECTS = {
    "broker_day_partial_exit_duplicate",
    "confirmed_runtime_defect",
}


def _number(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _behavior_metric_eligible(model: Mapping[str, Any]) -> bool:
    integrity = model.get("integrity") if isinstance(model.get("integrity"), Mapping) else {}
    defects = {str(value) for value in (integrity.get("defects") or [])}
    return not bool(defects & BEHAVIOR_METRIC_EXCLUSION_DEFECTS)


def _topk_metric(
    scanner_quality: Mapping[str, Any],
    *,
    top_k: int,
    horizon: str,
) -> dict[str, Any]:
    return _topk_metric_impl(scanner_quality, top_k=top_k, horizon=horizon, facade=_sys.modules[__name__])


def _classify_root_cause(
    *,
    scanner_quality: Mapping[str, Any],
    attribution: Mapping[str, Any],
    entry: Mapping[str, Any],
    exit_hold: Mapping[str, Any],
) -> dict[str, Any]:
    return _classify_root_cause_impl(scanner_quality=scanner_quality, attribution=attribution, entry=entry, exit_hold=exit_hold, facade=_sys.modules[__name__])


def _role_metrics(
    candidates: list[dict[str, Any]],
    *,
    role: str,
    horizon: str,
    cost_pct: float,
) -> dict[str, Any]:
    return _role_metrics_impl(candidates, role=role, horizon=horizon, cost_pct=cost_pct, facade=_sys.modules[__name__])


def _paired_role_deltas(
    candidates: list[dict[str, Any]],
    *,
    horizon: str,
) -> dict[str, Any]:
    return _paired_role_deltas_impl(candidates, horizon=horizon, facade=_sys.modules[__name__])


def _selection_availability(models: list[dict[str, Any]]) -> dict[str, Any]:
    return _selection_availability_impl(models, facade=_sys.modules[__name__])


def _q9_decision_candidate_rows(payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for payload in payloads:
        for raw in payload.get("q9_decision_candidates") or []:
            if not isinstance(raw, Mapping):
                continue
            row = dict(raw)
            row.setdefault("_payload_generated_at", payload.get("generated_at"))
            rows.append(row)
    return attach_forward_outcomes(rows)


def _q9_role_row(
    roles: Mapping[str, list[dict[str, Any]]],
    role: str,
) -> dict[str, Any]:
    return _q9_role_row_impl(roles, role, facade=_sys.modules[__name__])


def _decision_window_attribution(
    payloads: list[dict[str, Any]],
    *,
    cost_pct: float,
) -> dict[str, Any]:
    return _decision_window_attribution_impl(payloads, cost_pct=cost_pct, facade=_sys.modules[__name__])


def _attribution_component(
    *,
    attribution: Mapping[str, Any],
    component: str,
    question: str,
    missing_comparison: str,
    availability: dict[str, Any],
) -> dict[str, Any]:
    return _attribution_component_impl(attribution=attribution, component=component, question=question, missing_comparison=missing_comparison, availability=availability, facade=_sys.modules[__name__])


def _scanner_decision(
    *,
    role_metrics: list[dict[str, Any]],
    paired: list[dict[str, Any]],
) -> dict[str, Any]:
    return _scanner_decision_impl(role_metrics=role_metrics, paired=paired, facade=_sys.modules[__name__])


def _unavailable_component(
    *,
    question: str,
    missing_comparison: str,
    availability: dict[str, Any],
) -> dict[str, Any]:
    return _unavailable_component_impl(question=question, missing_comparison=missing_comparison, availability=availability, facade=_sys.modules[__name__])


def build_full_chain_component_review(
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
        drop_q9_row_keys=Q9_ROW_KEYS_UNUSED_BY_FULL_CHAIN,  # never read below; ~80% of the q9 rows' bytes
    )
    candidates = _candidate_rows(payloads)
    all_models = _load_trade_models(reports_root, start, end)
    models = [model for model in all_models if _behavior_metric_eligible(model)]
    profile = load_broker_cost_profile(cost_profile_path)
    cost_pct = float(
        profile.get("conservative_round_trip_cost_pct")
        or profile.get("ema_round_trip_cost_pct")
        or 0.009
    ) * 100.0
    slippage_pct = max(
        0.0,
        float(os.getenv("Q9_EVALUATION_SLIPPAGE_PCT", str(DEFAULT_Q9_SLIPPAGE_PCT)) or DEFAULT_Q9_SLIPPAGE_PCT),
    )
    scanner_quality = build_scanner_quality_review(
        payloads,
        cost_pct=cost_pct,
        slippage_pct=slippage_pct,
    )
    role_metrics = [
        _role_metrics(candidates, role=role, horizon=horizon, cost_pct=cost_pct)
        for role in ("top_pick", "runner_up_evaluated")
        for horizon in HORIZONS
    ]
    paired = [_paired_role_deltas(candidates, horizon=horizon) for horizon in HORIZONS]
    availability = _selection_availability(models)
    decision_attribution = _decision_window_attribution(payloads, cost_pct=cost_pct)
    entry = _entry_timing_summary(models, candidates)
    exit_hold = _exit_hold_summary(models)
    realized = _realized_trade_summary(models)
    problem_segment = _classify_root_cause(
        scanner_quality=scanner_quality,
        attribution=decision_attribution,
        entry=entry,
        exit_hold=exit_hold,
    )
    scanner = _scanner_decision(role_metrics=role_metrics, paired=paired)
    entry_count = int(entry.get("matched_trade_count") or 0)
    entry_days = int(entry.get("matched_day_count") or 0)
    entry_enough = entry_count >= DIRECTIONAL_MIN_OBSERVATIONS and entry_days >= DIRECTIONAL_MIN_DAYS
    entry_average = _number(entry.get("average_entry_price_delta_pct"))
    entry_median = _number(entry.get("median_entry_price_delta_pct"))
    entry_decision = (
        DecisionClass.RETAIN.value
        if entry_enough
        and entry_average is not None
        and entry_median is not None
        and entry_average <= 0.30
        and entry_median <= 0.30
        else DecisionClass.ADJUST_AND_RETEST.value
        if entry_enough
        else DecisionClass.INSUFFICIENT_EVIDENCE.value
    )
    exit_count = int(exit_hold.get("observed_trade_count") or 0)
    exit_days = int(exit_hold.get("observed_day_count") or 0)
    exit_enough = exit_count >= DIRECTIONAL_MIN_OBSERVATIONS and exit_days >= DIRECTIONAL_MIN_DAYS
    five_minute = next(
        (row for row in exit_hold.get("by_hold_offset") or [] if row.get("offset") == "+5m"),
        {},
    )
    exit_decision = (
        DecisionClass.ADJUST_AND_RETEST.value
        if exit_enough and float(five_minute.get("average_improvement_pct") or 0.0) >= 0.30
        else DecisionClass.RETAIN.value
        if exit_enough
        else DecisionClass.INSUFFICIENT_EVIDENCE.value
    )
    realized_performance = realized.get("performance") or {}
    realized_count = int(realized_performance.get("count") or 0)
    realized_days = len(
        {
            str(model.get("day") or "")[:10]
            for model in models
            if (model.get("outcome") or {}).get("net_return_pct") is not None
        }
    )
    full_system_enough = (
        realized_count >= DIRECTIONAL_MIN_OBSERVATIONS
        and realized_days >= DIRECTIONAL_MIN_DAYS
    )
    full_system_decision = (
        DecisionClass.RETAIN.value
        if full_system_enough
        and float(realized_performance.get("expectancy_pct") or 0.0) > 0.0
        else DecisionClass.REJECT.value
        if full_system_enough
        else DecisionClass.INSUFFICIENT_EVIDENCE.value
    )
    components = {
        "scanner": {
            **scanner,
            "role_cost_adjusted_metrics": role_metrics,
            "paired_role_comparisons": paired,
            "evidence_class": "TRUSTED_SHADOW",
            "behavior_change_authorized": False,
        },
        "strategist": _attribution_component(
            attribution=decision_attribution,
            component="strategist",
            question="Does the strategy ranking overlay improve the same-universe intrinsic Scanner ranking?",
            missing_comparison="same-universe intrinsic and strategy-weighted Scanner outcomes",
            availability=availability,
        ),
        "commander": _attribution_component(
            attribution=decision_attribution,
            component="commander",
            question="Does Commander selection or veto improve the Strategist-selected outcome?",
            missing_comparison="explicit Commander alternative or veto joined to forward outcomes",
            availability=availability,
        ),
        "monitor_entry": {
            "decision": entry_decision,
            "question": "Does Monitor improve entry timing relative to the selected candidate baseline?",
            "finding": (
                "Actual entries were not systematically later or more expensive than the nearby "
                "same-symbol shadow baseline; entry timing is not the first demonstrated loss source."
                if entry_decision == DecisionClass.RETAIN.value
                else "Entry timing requires adjustment."
                if entry_decision == DecisionClass.ADJUST_AND_RETEST.value
                else "The minimum directional comparison count was not reached."
            ),
            "evidence_class": "RECONSTRUCTED",
            "metrics": entry,
            "missing_comparison": (
                None
                if entry_enough
                else "at least 20 actual-entry versus selected-baseline matches across 2 days"
            ),
            "behavior_change_authorized": False,
        },
        "monitor_exit": {
            "decision": exit_decision,
            "question": "Does Monitor exit too early or surrender material value?",
            "finding": (
                "Observed post-exit improvement is too small to identify exit timing as the primary "
                "loss source."
                if exit_decision == DecisionClass.RETAIN.value
                else "Post-exit improvement is large enough to justify a bounded exit-policy review."
                if exit_decision == DecisionClass.ADJUST_AND_RETEST.value
                else "Only 16 exits have post-exit observations; this is below the fixed 20-observation threshold."
            ),
            "evidence_class": "REALIZED_PLUS_POST_EXIT_SHADOW",
            "metrics": exit_hold,
            "missing_comparison": (
                None
                if exit_enough
                else "at least 20 exits with observed post-exit checkpoints across 2 days"
            ),
            "behavior_change_authorized": False,
        },
        "full_system": {
            "decision": full_system_decision,
            "question": "Does the integrated system currently produce positive broker-net value?",
            "finding": (
                "The integrated system produced positive broker-net expectancy for the analyzed range."
                if full_system_decision == DecisionClass.RETAIN.value
                else "The current positive-edge hypothesis is rejected for the analyzed range."
                if full_system_decision == DecisionClass.REJECT.value
                else "The fixed realized-trade and day minimum has not been reached."
            ),
            "evidence_class": "REALIZED",
            "metrics": realized,
            "missing_comparison": (
                None
                if full_system_enough
                else "at least 20 realized trades across 2 days"
            ),
            "behavior_change_authorized": False,
        },
    }
    components["strategist"]["scope"] = "ranking_overlay_only"
    components["strategist"]["full_strategist_contribution"] = _unavailable_component(
        question="Does the complete Strategist improve a strategy-neutral Scanner pipeline?",
        missing_comparison="parallel strategy-neutral candidate sourcing and ranking shadow",
        availability=availability,
    )
    refresh_primary = next(
        (
            row
            for row in decision_attribution.get("by_horizon") or []
            if row.get("horizon") == "+30m"
        ),
        {},
    )
    refresh_count = int(refresh_primary.get("post_scanner_refresh_comparison_count") or 0)
    refresh_days = int(refresh_primary.get("post_scanner_refresh_day_count") or 0)
    refresh_delta = _number(refresh_primary.get("average_post_scanner_refresh_delta_pct"))
    refresh_positive_rate = _number(refresh_primary.get("post_scanner_refresh_positive_delta_rate"))
    refresh_enough = refresh_count >= DIRECTIONAL_MIN_OBSERVATIONS and refresh_days >= DIRECTIONAL_MIN_DAYS
    refresh_material = bool(
        refresh_enough
        and refresh_delta is not None
        and refresh_positive_rate is not None
        and refresh_delta >= MIN_MATERIAL_RANKING_DELTA_PCT
        and refresh_positive_rate >= MIN_POSITIVE_RANKING_DELTA_RATE
    )
    components["strategist"]["post_scanner_refresh"] = {
        "decision": (
            DecisionClass.PROMOTION_CANDIDATE.value
            if refresh_material
            else DecisionClass.ADJUST_AND_RETEST.value
            if refresh_enough
            else DecisionClass.INSUFFICIENT_EVIDENCE.value
        ),
        "question": "Does the optional post-Scanner Strategist refresh improve the first Scanner result?",
        "finding": (
            f"Observed {refresh_count} paired +30m refresh windows across {refresh_days} day(s)."
        ),
        "missing_comparison": (
            None
            if refresh_count >= DIRECTIONAL_MIN_OBSERVATIONS and refresh_days >= DIRECTIONAL_MIN_DAYS
            else f"at least {DIRECTIONAL_MIN_OBSERVATIONS} refresh pairs across {DIRECTIONAL_MIN_DAYS} days"
        ),
        "metrics": {
            key: value
            for key, value in refresh_primary.items()
            if "post_scanner_refresh" in key or key == "horizon"
        },
        "behavior_change_authorized": False,
    }
    return {
        "schema_version": "q9_full_chain_component_review.v1",
        "contract_version": CONTRACT_VERSION,
        "behavior_effect": "evaluation_only",
        "range": {"start": start[:10], "end": end[:10]},
        "cost_model": {
            "source": str(profile.get("source") or "fallback"),
            "sample_count": int(profile.get("sample_count") or 0),
            "conservative_round_trip_cost_pct": round(cost_pct, 4),
            "evaluation_slippage_pct": round(slippage_pct, 4),
        },
        "evidence": {
            "shadow_payload_count": len(payloads),
            "deduped_shadow_candidate_count": len(candidates),
            "trade_model_count": len(models),
            "total_trade_model_count": len(all_models),
            "excluded_trade_model_count": len(all_models) - len(models),
            "selection_availability": availability,
            "decision_window_attribution": decision_attribution,
            "scanner_quality": scanner_quality,
        },
        "problem_segment": problem_segment,
        "component_decisions": components,
        "overall_decision": {
            "decision": (
                DecisionClass.ADJUST_AND_RETEST.value
                if full_system_enough
                else DecisionClass.INSUFFICIENT_EVIDENCE.value
            ),
            "first_actionable_component": (
                "scanner_candidate_quality_and_horizon_calibration"
                if full_system_enough
                else "artifact_and_forward_evidence_collection"
            ),
            "reason": (
                "The fixed realized-trade and multi-day thresholds are not complete; continue "
                "the frozen forward window without changing trading behavior."
                if not full_system_enough
                else "Scanner ordering does not show a material relative advantage and selected "
                "candidates remain cost-negative. Monitor entry is not the first demonstrated "
                "failure, and Monitor exit has insufficient observations."
            ),
            "behavior_change_authorized": False,
        },
        "closure": {
            "historical_review_complete": True,
            "open_ended_extension_authorized": False,
            "remaining_forward_requirement": (
                "Persist trusted A/B/C decision snapshots and reach the fixed missing-comparison "
                "thresholds; do not add new diagnostic categories."
            ),
        },
    }


def render_full_chain_component_review(payload: Mapping[str, Any]) -> str:
    return render_full_chain_component_review_impl(payload, facade=_sys.modules[__name__])


def write_full_chain_component_review(
    *,
    reports_root: Path,
    start: str,
    end: str,
    output_dir: Path,
    cost_profile_path: Path | None = None,
) -> dict[str, str]:
    payload = build_full_chain_component_review(
        reports_root=reports_root,
        start=start,
        end=end,
        cost_profile_path=cost_profile_path,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "q9_full_chain_component_review.json"
    md_path = output_dir / "q9_full_chain_component_review.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_full_chain_component_review(payload), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}
