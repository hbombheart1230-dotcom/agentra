from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .contracts import (
    CONTRACT_VERSION,
    DIRECTIONAL_MIN_DAYS,
    DIRECTIONAL_MIN_OBSERVATIONS,
)
from . import fast07_chain_render_projection as _render
from .full_chain_component_review import build_full_chain_component_review


MIN_MATERIAL_DELTA_PCT = 0.30
MIN_POSITIVE_RATE = 0.55
MAX_DEGRADING_POSITIVE_RATE = 0.45


_mapping = _render.score_mapping


def _number(value: Any) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _delta_state(
    metrics: Mapping[str, Any],
    *,
    prefix: str,
    missing_control: str,
) -> dict[str, Any]:
    count = int(metrics.get(f"{prefix}_comparison_count") or 0)
    days = int(metrics.get(f"{prefix}_day_count") or 0)
    delta = _number(metrics.get(f"average_{prefix}_delta_pct"))
    positive_rate = _number(metrics.get(f"{prefix}_positive_delta_rate"))
    enough = count >= DIRECTIONAL_MIN_OBSERVATIONS and days >= DIRECTIONAL_MIN_DAYS
    if not enough or delta is None or positive_rate is None:
        state = "NOT_MEASURABLE"
        reason = (
            f"requires {DIRECTIONAL_MIN_OBSERVATIONS} paired observations across "
            f"{DIRECTIONAL_MIN_DAYS} days; current={count}/{days}"
        )
    elif delta >= MIN_MATERIAL_DELTA_PCT and positive_rate >= MIN_POSITIVE_RATE:
        state = "VALUE_ADD"
        reason = "paired cost-adjusted effect meets the fixed positive materiality contract"
    elif delta <= -MIN_MATERIAL_DELTA_PCT and positive_rate <= MAX_DEGRADING_POSITIVE_RATE:
        state = "DEGRADING"
        reason = "paired cost-adjusted effect meets the fixed negative materiality contract"
    else:
        state = "NEUTRAL"
        reason = "paired effect is measurable but does not meet positive or negative materiality"
    return {
        "state": state,
        "reason": reason,
        "comparison_count": count,
        "day_count": days,
        "average_delta_pct": delta,
        "positive_delta_rate": positive_rate,
        "missing_control": missing_control if state == "NOT_MEASURABLE" else None,
    }


def _decision_state(component: Mapping[str, Any]) -> str:
    decision = str(component.get("decision") or "")
    if decision == "INSUFFICIENT_EVIDENCE":
        return "NOT_MEASURABLE"
    if decision in {"REJECT", "DEPRECATE_CANDIDATE"}:
        return "DEGRADING"
    if decision == "ADJUST_AND_RETEST":
        return "DEGRADING"
    if decision == "PROMOTION_CANDIDATE":
        return "VALUE_ADD"
    return "NEUTRAL"


def build_agent_effectiveness_scorecard(
    full_chain_review: Mapping[str, Any],
) -> dict[str, Any]:
    evidence = _mapping(full_chain_review.get("evidence"))
    attribution = _mapping(evidence.get("decision_window_attribution"))
    primary = next(
        (
            dict(row)
            for row in attribution.get("by_horizon") or []
            if isinstance(row, Mapping) and row.get("horizon") == "+30m"
        ),
        {},
    )
    components = _mapping(full_chain_review.get("component_decisions"))
    scanner = _mapping(components.get("scanner"))
    scanner_measurable = str(scanner.get("decision") or "") != "INSUFFICIENT_EVIDENCE"
    scanner_relative = (
        "VALUE_ADD"
        if scanner_measurable and bool(scanner.get("relative_ranking_effect_positive"))
        else "DEGRADING"
        if scanner_measurable
        else "NOT_MEASURABLE"
    )
    scanner_absolute = (
        "VALUE_ADD"
        if scanner_measurable and bool(scanner.get("absolute_cost_adjusted_edge_positive"))
        else "DEGRADING"
        if scanner_measurable
        else "NOT_MEASURABLE"
    )
    overlay_metrics = _render.scorecard_overlay_metrics(primary)
    overlay = _delta_state(
        overlay_metrics,
        prefix="strategy_ranking_overlay",
        missing_control="paired same-universe intrinsic and strategy-weighted outcomes",
    )
    refresh = _delta_state(
        primary,
        prefix="post_scanner_refresh",
        missing_control="paired first-Scanner and post-refresh Scanner outcomes",
    )
    commander = _delta_state(
        primary,
        prefix="commander",
        missing_control="paired presented-candidate and Commander approve/veto outcomes",
    )
    return _render.assemble_agent_effectiveness_scorecard(
        contract_version=CONTRACT_VERSION,
        date_range=_mapping(full_chain_review.get("range")),
        trade_total=int(evidence.get("total_trade_model_count") or 0),
        excluded=int(evidence.get("excluded_trade_model_count") or 0),
        scanner_relative=scanner_relative,
        scanner_absolute=scanner_absolute,
        overlay=overlay,
        refresh=refresh,
        commander=commander,
        monitor_entry=_mapping(components.get("monitor_entry")),
        monitor_exit=_mapping(components.get("monitor_exit")),
        full_system=_mapping(components.get("full_system")),
        decision_state=_decision_state,
    )


render_agent_effectiveness_scorecard = _render.render_agent_effectiveness_scorecard


def write_agent_effectiveness_scorecard(
    *,
    reports_root: Path,
    start: str,
    end: str,
    output_dir: Path,
) -> dict[str, Any]:
    review = build_full_chain_component_review(
        reports_root=Path(reports_root),
        start=start,
        end=end,
    )
    payload = build_agent_effectiveness_scorecard(review)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "agent_effectiveness_scorecard.json"
    md_path = output_dir / "agent_effectiveness_scorecard.md"
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    md_path.write_text(render_agent_effectiveness_scorecard(payload), encoding="utf-8")
    return {
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "range": payload.get("range"),
    }
