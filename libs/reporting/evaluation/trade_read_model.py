from __future__ import annotations

from pathlib import Path
from typing import Any

from libs.reporting.json_array_stream import iter_json_array
from libs.reporting.trade_read_model import build_trade_read_model as build_legacy_trade_read_model

from .artifact_inventory import inventory_trade, read_json
from . import fast07_trade_projection as _proj
from .horizon_contract import build_horizon_contract
from .scanner_score_decomposition import decompose_scanner_score


_parse_ts = _proj.parse_ts
_meaningful = _proj.meaningful
_deep_value = _proj.deep_value
_lifecycle_sections = _proj.lifecycle_sections
_is_realized_exit = _proj.is_realized_exit
_holding_seconds = _proj.holding_seconds
_candidate_by_symbol = _proj.candidate_by_symbol


def _as_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _trade_has_summary(trade_dir: Path) -> bool:
    return (
        (trade_dir / "reports" / "ai_trade_summary.json").exists()
        or (trade_dir / "reports" / "ai_trade_summary.md").exists()
    )


def _is_broker_day_partial_exit_duplicate(
    trade_dir: Path,
    *,
    trade_id: str,
    symbol: str,
    bundle: dict[str, Any],
    entry_artifact: dict[str, Any],
    exit_artifact: dict[str, Any],
) -> dict[str, Any]:
    """Detect a broker-day diary child row from a split sell, not a new trade.

    Kiwoom/MTS may report one entry position as multiple same-symbol sell rows.
    The closeout recovery can materialize the extra sell row as a TRD_* child
    without a trade summary. That row must remain auditable, but it must not be
    counted as an independent trade in Q9/Q13/Q14 performance.
    """
    health = read_json(trade_dir / "_health.json")
    broker_reconciliation = (
        health.get("broker_reconciliation")
        if isinstance(health.get("broker_reconciliation"), dict)
        else {}
    )
    health_status = str(
        health.get("status")
        or broker_reconciliation.get("status")
        or health.get("recovery_source")
        or ""
    ).strip().lower()
    if health_status != "closed_by_broker_day_trade_diary":
        source_text = " ".join(
            str(_deep_value(obj, "source", "broker_day_truth_source") or "")
            for obj in (bundle, entry_artifact, exit_artifact, broker_reconciliation)
        ).lower()
        if "kiwoom.order_pair_snapshot" not in source_text:
            return {}
    if _trade_has_summary(trade_dir):
        return {}
    if not symbol:
        return {}

    child_qty = _as_float(
        _deep_value(exit_artifact, "filled_qty", "quantity", "qty")
        or _deep_value(bundle, "filled_qty", "quantity", "qty")
        or _deep_value(entry_artifact, "filled_qty", "quantity", "qty")
    )
    child_pnl = _as_float(_deep_value(bundle, "pnl_pct"))
    try:
        day_dir = trade_dir.parents[1]
    except IndexError:
        return {}

    for sibling in sorted(day_dir.glob("*/*")):
        if not sibling.is_dir() or sibling == trade_dir:
            continue
        sibling_bundle = read_json(sibling / "lifecycle_bundle.json")
        sibling_symbol = str(
            sibling_bundle.get("symbol")
            or _deep_value(read_json(sibling / "entry.json"), "symbol")
            or ""
        ).strip()
        if sibling_symbol != symbol or not _trade_has_summary(sibling):
            continue
        sibling_entry = read_json(sibling / "entry.json")
        sibling_exit = read_json(sibling / "exit.json")
        parent_entry_qty = _as_float(
            _deep_value(sibling_entry, "filled_qty", "quantity", "qty")
            or _deep_value(sibling_bundle, "filled_qty", "quantity", "qty")
        )
        parent_exit_qty = _as_float(
            _deep_value(sibling_exit, "filled_qty", "quantity", "qty")
            or _deep_value(sibling_bundle, "quantity", "qty")
        )
        parent_pnl = _as_float(_deep_value(sibling_bundle, "pnl_pct"))
        qty_links = (
            child_qty is not None
            and parent_entry_qty is not None
            and parent_exit_qty is not None
            and parent_entry_qty > parent_exit_qty
            and abs(parent_entry_qty - (parent_exit_qty + child_qty)) <= 1.0
        )
        pnl_links = (
            child_pnl is not None
            and parent_pnl is not None
            and abs(child_pnl - parent_pnl) <= 0.0001
        )
        if qty_links or (pnl_links and child_qty is not None and parent_exit_qty == child_qty):
            return {
                "status": "duplicate_partial_exit_child",
                "parent_trade_id": sibling.name,
                "child_trade_id": trade_id,
                "symbol": symbol,
                "health_status": health_status,
                "child_quantity": child_qty,
                "parent_entry_quantity": parent_entry_qty,
                "parent_exit_quantity": parent_exit_qty,
                "reason": "broker_day_diary_split_sell_child",
            }
    return {}


def _scanner_evidence_context(trade_dir: Path, selected_symbol: str) -> dict[str, Any]:
    return _proj.scanner_evidence_context(read_json(trade_dir / "evidence" / "scanner_evidence.json"), selected_symbol)


def _monitor_evidence_context(trade_dir: Path) -> dict[str, Any]:
    return _proj.monitor_evidence_counts(read_json(trade_dir / "evidence" / "monitor_evidence.json"))


def _closeout_broker_skip(trade_dir: Path, *, day: str, trade_id: str) -> dict[str, Any]:
    try:
        reports_root = trade_dir.parents[3]
    except IndexError:
        return {}
    closeout = read_json(
        reports_root / "operator_summary" / "daily" / day[:10] / "closeout_maintenance.json"
    )
    return _proj.closeout_broker_skip_row(closeout, trade_id=trade_id)


def _daily_q9_snapshot(
    trade_dir: Path,
    *,
    day: str,
    entry: dict[str, Any],
    scanner_context: dict[str, Any],
    selected_symbol: str,
) -> tuple[dict[str, Any], str]:
    try:
        reports_root = trade_dir.parents[3]
    except IndexError:
        return {}, ""
    windows_path = reports_root / "operator_summary" / "daily" / day[:10] / "q9_decision_windows.json"

    decision_id = str(scanner_context.get("q9_decision_id") or "").strip()
    run_ids = {
        str(value or "").strip()
        for value in (
            entry.get("run_id"),
            scanner_context.get("run_id"),
            scanner_context.get("entry_run_id"),
        )
        if str(value or "").strip()
    }
    entry_ts = _parse_ts(entry.get("timestamp") or entry.get("ts"))
    # One streamed pass over the (~120 MB) windows file instead of parsing it whole for every trade.
    # Priority is unchanged: an exact decision_id match anywhere wins (so the scan stops there), else the
    # first run_id match in file order, else the nearest same-symbol window within 600 s (first of equals).
    first_run_match: dict[str, Any] | None = None
    nearest: tuple[float, dict[str, Any]] | None = None
    try:
        for raw in iter_json_array(windows_path, "windows"):
            if not isinstance(raw, dict):
                continue
            if decision_id and str(raw.get("decision_id") or "") == decision_id:
                return dict(raw), "daily_q9_window.decision_id"
            if first_run_match is None and str(raw.get("run_id") or "").strip() in run_ids:
                first_run_match = dict(raw)
            if entry_ts is None or not selected_symbol:
                continue
            strategist = raw.get("strategist_selection")
            strategist = strategist if isinstance(strategist, dict) else {}
            commander = raw.get("commander_final")
            commander = commander if isinstance(commander, dict) else {}
            if selected_symbol not in {
                str(strategist.get("selected_symbol") or ""),
                str(commander.get("selected_symbol") or ""),
                str(commander.get("candidate_symbol") or ""),
            }:
                continue
            generated_at = _parse_ts(raw.get("generated_at"))
            if generated_at is None:
                continue
            delta = abs((generated_at - entry_ts).total_seconds())
            if delta <= 600 and (nearest is None or delta < nearest[0]):
                nearest = (delta, dict(raw))
    except ValueError:
        return {}, ""  # unreadable windows file == no windows (what read_json -> {} gave)
    if first_run_match is not None:
        return first_run_match, "daily_q9_window.run_id"
    if entry_ts is None or not selected_symbol:
        return {}, ""
    return (nearest[1], "daily_q9_window.nearest_symbol_time") if nearest else ({}, "")


def build_q9_trade_read_model(trade_dir: Path) -> dict[str, Any]:
    legacy = build_legacy_trade_read_model(str(trade_dir))
    bundle = read_json(trade_dir / "lifecycle_bundle.json")
    ai_report = read_json(trade_dir / "reports" / "ai_trade_report.json")
    legacy_facts = legacy.get("facts") if isinstance(legacy.get("facts"), dict) else {}
    trade_id = str(legacy_facts.get("trade_id") or bundle.get("trade_id") or trade_dir.name)
    day = str(bundle.get("day") or trade_dir.parts[-3])
    lifecycle, entry, exit_row = _lifecycle_sections(bundle)
    entry_artifact = read_json(trade_dir / "entry.json")
    exit_artifact = read_json(trade_dir / "exit.json")
    if entry_artifact:
        entry = {**entry, **entry_artifact}
    if exit_artifact:
        exit_row = {**exit_row, **exit_artifact}
    realized_exit = _is_realized_exit(exit_row, bundle)
    inventory = inventory_trade(trade_dir)
    facts = legacy.get("facts") if isinstance(legacy.get("facts"), dict) else legacy
    symbol = str(facts.get("symbol") or bundle.get("symbol") or "")
    partial_exit_duplicate = _is_broker_day_partial_exit_duplicate(
        trade_dir,
        trade_id=trade_id,
        symbol=symbol,
        bundle=bundle,
        entry_artifact=entry_artifact,
        exit_artifact=exit_artifact,
    )
    closeout_broker_skip = _closeout_broker_skip(trade_dir, day=day, trade_id=trade_id)
    evaluation_exclusion = read_json(trade_dir / "evaluation_exclusion.json")
    scanner_context, strategist_context, monitor_context, selected_symbol = _proj.entry_contexts(entry, facts)
    scanner_evidence = _scanner_evidence_context(trade_dir, selected_symbol)
    monitor_evidence = _monitor_evidence_context(trade_dir)
    q9_snapshot = (
        scanner_context.get("q9_decision_snapshot")
        if isinstance(scanner_context.get("q9_decision_snapshot"), dict)
        else {}
    )
    q9_snapshot_source = "entry.scanner_context.q9_decision_snapshot" if q9_snapshot else ""
    if not q9_snapshot:
        q9_snapshot, q9_snapshot_source = _daily_q9_snapshot(
            trade_dir,
            day=str(bundle.get("day") or trade_dir.parts[-3]),
            entry=entry,
            scanner_context=scanner_context,
            selected_symbol=selected_symbol,
        )
    horizon_contract = build_horizon_contract(
        bundle=bundle,
        entry=entry,
        exit_row=exit_row,
        entry_artifact=entry_artifact,
        exit_artifact=exit_artifact,
        scanner_context=scanner_context,
        strategist_context=strategist_context,
        monitor_context=monitor_context,
    )
    return _proj.assemble_q9_trade_read_model(
        trade_dir=str(trade_dir),
        legacy=legacy,
        facts=facts,
        bundle=bundle,
        ai_report=ai_report,
        trade_id=trade_id,
        day=day,
        symbol=symbol,
        lifecycle=lifecycle,
        entry=entry,
        exit_row=exit_row,
        exit_artifact=exit_artifact,
        realized_exit=realized_exit,
        inventory=inventory,
        partial_exit_duplicate=partial_exit_duplicate,
        closeout_broker_skip=closeout_broker_skip,
        evaluation_exclusion=evaluation_exclusion,
        scanner_context=scanner_context,
        strategist_context=strategist_context,
        monitor_context=monitor_context,
        selected_symbol=selected_symbol,
        scanner_evidence=scanner_evidence,
        monitor_evidence=monitor_evidence,
        q9_snapshot=q9_snapshot,
        q9_snapshot_source=q9_snapshot_source,
        horizon_contract=horizon_contract,
        decompose=decompose_scanner_score,
    )
