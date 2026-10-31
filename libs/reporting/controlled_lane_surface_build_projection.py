"""controlled_mock_lane_report projections (moved verbatim from controlled_mock_lane_report).

Module globals and helpers are resolved on ``facade`` (the controlled_mock_lane_report module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping


def build_controlled_lane_report_surface(
    state: Mapping[str, Any], *, day: str = "", root: Path | str | None = None,
    prior_entry: Mapping[str, Any] | None = None,
    facade: Any,
) -> dict[str, Any]:
    """Recover controlled-lane entry evidence without same-symbol guessing."""
    execution = facade._mapping(state.get("execution"))
    order = facade._mapping(execution.get("order"))
    meta = facade._mapping(order.get("meta"))
    prior = facade._mapping(prior_entry)
    lane = facade._first_mapping(meta.get("controlled_mock_lane"), prior.get("controlled_mock_lane"))
    symbol = facade._text(order.get("symbol") or execution.get("symbol") or prior.get("symbol") or state.get("symbol"))
    strategy = facade._first_mapping(meta.get("position_strategy_snapshot"), prior.get("position_strategy_snapshot"))
    if not strategy and symbol:
        strategy = facade._position_strategy(state, symbol)
    if not lane and day and root is not None and symbol:
        order_id = facade._deep_first(prior, "order_id", "ord_no")
        entry_run_id = facade._text(prior.get("run_id"))
        lane = facade._ledger_row(root=facade.Path(root), day=day, symbol=symbol, order_id=order_id, run_id=entry_run_id)
        if lane and not strategy:
            strategy = facade._fixed_lane_strategy()
    if not lane or not strategy.get("controlled_mock_lane"):
        return {}
    lane_id = facade._text(lane.get("lane_id"))
    return {
        "schema_version": "controlled_mock_lane_report.v2",
        "lane_id": lane_id,
        "lane_label": facade.LANE_LABELS.get(lane_id, lane_id),
        "symbol": facade._text(lane.get("symbol") or symbol),
        "signal_id": facade._text(lane.get("signal_id")),
        "signal_epoch": lane.get("signal_epoch"),
        "entry_run_id": facade._text(lane.get("run_id") or prior.get("run_id")),
        "entry_order_id": facade._text(lane.get("order_id") or facade._deep_first(prior, "order_id", "ord_no")),
        "score": lane.get("score"),
        "evidence": facade._mapping(lane.get("evidence")),
        "daily_limit": lane.get("daily_limit"),
        "reservation": facade._mapping(lane.get("reservation")),
        "strategy_horizon": facade._text(strategy.get("strategy_horizon")),
        "expected_hold_window": facade._mapping(strategy.get("expected_hold_window")),
        "llm_used": bool(strategy.get("llm_used")),
        "stage3_horizon_review_allowed": bool(strategy.get("horizon_revision_allowed", True)),
        "selection_authority": "deterministic_independent_lane",
        "scanner_rank_applicable": False,
        "execution_scope": "kiwoom_mock_only",
    }
