from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from libs.reporting.quant_shadow_forward_outcomes import (
    attach_forward_outcomes,
    load_minute_rows_from_state,
)

from . import fast07_trade_projection as _proj
from . import fast07_chain_render_projection as _render


HORIZONS = ("+5m", "+15m", "+30m", "+60m")
LABELS = (
    "ENTRY_TOO_EARLY",
    "ENTRY_TOO_LATE",
    "ENTRY_APPROPRIATE",
    "INSUFFICIENT_EVIDENCE",
)


_mapping = _proj.mapping
_num = _proj.num
_epoch = _proj.epoch
_iso = _proj.iso
_stage_epoch = _proj.stage_epoch


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _daily_windows_by_id(reports_root: Path, day: str) -> dict[str, dict[str, Any]]:
    path = reports_root / "operator_summary" / "daily" / day / "q9_decision_windows.json"
    return _proj.windows_by_decision_id(_read_json(path))


_candidate_symbol = _proj.candidate_symbol
_candidate_rank = _proj.candidate_rank
_row_at_or_before = _proj.row_at_or_before
_pre_entry_move_pct = _proj.pre_entry_move_pct


def _entry_forward(
    *,
    trade_id: str,
    symbol: str,
    entry_epoch: int,
    entry_price: float | None,
    minute_rows_by_symbol: Mapping[str, list[Mapping[str, Any]]],
) -> dict[str, Any]:
    if not symbol or entry_epoch <= 0 or entry_price is None or entry_price <= 0:
        return {"available": False, "reason": "entry_baseline_unavailable", "checkpoints": {}}
    rows = attach_forward_outcomes(
        [{
            "symbol": symbol,
            "trade_id": trade_id,
            "generated_at": _iso(entry_epoch),
            "shadow_forward_base": {
                "available": True,
                "baseline_epoch": entry_epoch,
                "baseline_price": entry_price,
                "source": "actual_entry",
            },
        }],
        minute_rows_by_symbol=minute_rows_by_symbol,
    )
    return _proj.forward_from_outcome(_mapping((rows[0] if rows else {}).get("shadow_forward_outcome")))


_checkpoint = _proj.checkpoint


def _label(
    *,
    scanner_to_entry_delay_sec: int | None,
    pre_entry_move_pct: float | None,
    forward: Mapping[str, Any],
    strategy_horizon: str = "",
) -> tuple[str, list[str]]:
    cp5 = _checkpoint(forward, "+5m")
    cp15 = _checkpoint(forward, "+15m")
    cp30 = _checkpoint(forward, "+30m")
    ret5 = _num(cp5.get("return_pct"))
    mfe5 = _num(cp5.get("mfe_pct"))
    mae5 = _num(cp5.get("mae_pct"))
    ret15 = _num(cp15.get("return_pct"))
    normalized_horizon = str(strategy_horizon or "").strip().lower()
    if normalized_horizon in {"swing", "overnight", "position", "1-2day", "1_2day"}:
        return "INSUFFICIENT_EVIDENCE", ["strategy_horizon_exceeds_entry_timing_observation_window"]
    if normalized_horizon == "intraday":
        ret30 = _num(cp30.get("return_pct"))
        mfe15 = _num(cp15.get("mfe_pct"))
        mae15 = _num(cp15.get("mae_pct"))
        if ret15 is None or ret30 is None or mfe15 is None or mae15 is None:
            return "INSUFFICIENT_EVIDENCE", ["missing_intraday_forward_quality"]
        reasons: list[str] = []
        if pre_entry_move_pct is not None and pre_entry_move_pct >= 0.35 and ret15 <= 0.0 and ret30 <= 0.0:
            return "ENTRY_TOO_LATE", ["pre_entry_move>=0.35pct_then_intraday_forward_weak"]
        if mae15 <= -0.75 and ret15 < 0.0 and (pre_entry_move_pct is None or pre_entry_move_pct < 0.20):
            return "ENTRY_TOO_EARLY", ["intraday_adverse_move_without_prior_alpha"]
        if ret15 > 0.0 or ret30 > 0.0 or mfe15 >= 0.70:
            return "ENTRY_APPROPRIATE", ["favorable_intraday_forward_response"]
        return "INSUFFICIENT_EVIDENCE", ["intraday_forward_weak_but_not_classifiable"]
    if ret5 is None or mfe5 is None or mae5 is None:
        return "INSUFFICIENT_EVIDENCE", ["missing_5m_forward_quality"]
    reasons: list[str] = []
    if scanner_to_entry_delay_sec is not None and scanner_to_entry_delay_sec >= 180:
        reasons.append("scanner_to_entry_delay>=180s")
    if pre_entry_move_pct is not None and pre_entry_move_pct >= 0.35 and (ret5 <= 0.0 or (ret15 is not None and ret15 <= 0.0)):
        reasons.append("pre_entry_move>=0.35pct_then_forward_weak")
        return "ENTRY_TOO_LATE", reasons
    if mae5 <= -0.55 and ret5 < 0.0 and (pre_entry_move_pct is None or pre_entry_move_pct < 0.20):
        reasons.append("immediate_adverse_move_without_prior_alpha")
        return "ENTRY_TOO_EARLY", reasons
    if ret5 > 0.0 or (ret15 is not None and ret15 > 0.0) or mfe5 >= 0.50:
        reasons.append("favorable_forward_response")
        return "ENTRY_APPROPRIATE", reasons
    reasons.append("forward_weak_but_not_classifiable")
    return "INSUFFICIENT_EVIDENCE", reasons


def build_entry_timing_attribution_report(
    *,
    day: str,
    models: Sequence[Mapping[str, Any]],
    reports_root: Path = Path("reports"),
    minute_rows_by_symbol: Mapping[str, list[Mapping[str, Any]]] | None = None,
) -> dict[str, Any]:
    rows_by_symbol = (
        minute_rows_by_symbol
        if minute_rows_by_symbol is not None
        else load_minute_rows_from_state()
    )
    windows = _daily_windows_by_id(Path(reports_root), day)
    rows: list[dict[str, Any]] = []
    excluded_count = 0
    for model in models:
        if _proj.is_excluded_model(model):
            excluded_count += 1
            continue
        selection = _mapping(model.get("selection"))
        window = windows.get(str(selection.get("q9_decision_id") or ""), {})
        timing = _proj.entry_stage_timing(model, window)
        symbol = str(model.get("symbol") or "")
        pre_move, pre_move_meta = _pre_entry_move_pct(
            symbol=symbol,
            decision_epoch=timing["decision_epoch"],
            entry_price=timing["entry_price"],
            minute_rows_by_symbol=rows_by_symbol,
        )
        forward = _entry_forward(
            trade_id=str(model.get("trade_id") or ""),
            symbol=symbol,
            entry_epoch=timing["entry_epoch"],
            entry_price=timing["entry_price"],
            minute_rows_by_symbol=rows_by_symbol,
        )
        scanner_delay = _proj.delay_seconds(timing["entry_epoch"], timing["scanner_time"])
        label, reasons = _label(
            scanner_to_entry_delay_sec=scanner_delay,
            pre_entry_move_pct=pre_move,
            forward=forward,
            strategy_horizon=timing["strategy_horizon"],
        )
        rows.append(
            _proj.entry_timing_row(
                model,
                timing,
                label=label,
                reasons=reasons,
                pre_move=pre_move,
                pre_move_meta=pre_move_meta,
                forward=forward,
            )
        )
    label_rows = _proj.entry_timing_label_summary(rows, LABELS)

    return {
        "schema_version": "entry_timing_attribution_report.v1",
        "measurement_contract_version": "q13_stage_timing.v2",
        "evaluation_program_id": "Q13_ENTRY_TIMING_ATTRIBUTION",
        "behavior_effect": "observation_only",
        "day": day,
        "trade_count": len(rows),
        "excluded_trade_count": excluded_count,
        "label_summary": label_rows,
        "rows": rows,
        "limitations": [
            "Scanner time uses the Q9 decision snapshot. Strategist and selected-candidate times remain empty unless an explicit stage timestamp exists.",
            "Labels are attribution hypotheses, not trading behavior.",
            "INSUFFICIENT_EVIDENCE is used when forward minute observations are missing or ambiguous.",
        ],
    }


_fmt = _render.timing_fmt
render_entry_timing_attribution_report = _render.render_entry_timing_attribution_report


__all__ = [
    "build_entry_timing_attribution_report",
    "render_entry_timing_attribution_report",
]
