from __future__ import annotations

import json
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from statistics import median
from typing import Any, Iterable, Mapping

from libs.reporting.q8_evaluation_contract import dedupe_q8_candidates
from libs.reporting.quant_shadow_candidate_evaluation import (
    build_quant_shadow_candidate_evaluation,
    load_quant_shadow_candidate_payloads_for_range,
)
from libs.reporting.quant_shadow_forward_outcomes import attach_forward_outcomes

from .artifact_inventory import iter_trade_dirs
from . import fast07_attribution_projection as _attr
from . import fast07_chain_render_projection as _render
from .trade_read_model import build_q9_trade_read_model


_to_float = _attr.to_float


def _parse_ts(value: Any) -> datetime | None:
    try:
        return datetime.fromisoformat(str(value or "").replace("Z", "+00:00"))
    except ValueError:
        return None


def _iter_days(start: str, end: str) -> Iterable[str]:
    current = date.fromisoformat(start[:10])
    final = date.fromisoformat(end[:10])
    while current <= final:
        yield current.isoformat()
        current += timedelta(days=1)


_checkpoint_return = _attr.checkpoint_return
_rank_bucket = _attr.rank_bucket


def _candidate_rows(payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = _attr.raw_candidate_rows(payloads)
    return dedupe_q8_candidates(attach_forward_outcomes(rows))


_group_forward = _attr.group_forward


def _load_trade_models(reports_root: Path, start: str, end: str) -> list[dict[str, Any]]:
    models: list[dict[str, Any]] = []
    for day in _iter_days(start, end):
        models.extend(build_q9_trade_read_model(path) for path in iter_trade_dirs(reports_root, day))
    return models


_realized_trade_summary = _attr.realized_trade_summary


def _entry_timing_summary(
    models: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    by_symbol: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in candidates:
        base = row.get("shadow_forward_base")
        base = base if isinstance(base, Mapping) else {}
        epoch = int(_to_float(base.get("baseline_epoch")) or 0)
        price = _to_float(base.get("baseline_price"))
        if epoch > 0 and price and price > 0:
            by_symbol[str(row.get("symbol") or "")].append(row)
    for rows in by_symbol.values():
        rows.sort(key=lambda row: int((row.get("shadow_forward_base") or {}).get("baseline_epoch") or 0))

    deltas: list[float] = []
    matched: list[dict[str, Any]] = []
    matched_days: set[str] = set()
    for model in models:
        entry = model.get("entry") or {}
        entry_ts = _parse_ts(entry.get("timestamp"))
        entry_price = _to_float(entry.get("price"))
        symbol = str(model.get("symbol") or "")
        if entry_ts is None or entry_price is None or entry_price <= 0:
            continue
        epoch = int(entry_ts.timestamp())
        eligible = []
        for row in by_symbol.get(symbol, []):
            base = row.get("shadow_forward_base") or {}
            base_epoch = int(base.get("baseline_epoch") or 0)
            if 0 <= epoch - base_epoch <= 15 * 60:
                eligible.append(row)
        if not eligible:
            continue
        candidate = eligible[-1]
        base = candidate.get("shadow_forward_base") or {}
        baseline_price = _to_float(base.get("baseline_price"))
        if baseline_price is None or baseline_price <= 0:
            continue
        delta = ((entry_price / baseline_price) - 1.0) * 100.0
        deltas.append(delta)
        matched_days.add(str(model.get("day") or "")[:10])
        matched.append({
            "trade_id": model.get("trade_id"),
            "symbol": symbol,
            "baseline_epoch": base.get("baseline_epoch"),
            "baseline_price": baseline_price,
            "entry_price": entry_price,
            "entry_price_delta_pct": round(delta, 4),
            "candidate_reason": candidate.get("reason"),
        })
    return {
        "matched_trade_count": len(matched),
        "matched_day_count": len({day for day in matched_days if day}),
        "average_entry_price_delta_pct": round(sum(deltas) / len(deltas), 4) if deltas else None,
        "median_entry_price_delta_pct": round(median(deltas), 4) if deltas else None,
        "late_entry_count": sum(1 for value in deltas if value > 0.3),
        "better_entry_count": sum(1 for value in deltas if value < -0.3),
        "examples": matched[:20],
        "limitation": "matched to nearest same-symbol shadow baseline within 15 minutes; diagnostic only",
    }


_exit_hold_summary = _attr.exit_hold_summary


def _diagnosis(
    *,
    shadow: dict[str, Any],
    candidate_rank: list[dict[str, Any]],
    realized: dict[str, Any],
    entry: dict[str, Any],
    exit_hold: dict[str, Any],
) -> list[dict[str, Any]]:
    lane_rows = ((shadow.get("entry_lane_forward_outcomes") or {}).get("by_time_bucket") or [])
    buckets = {row.get("name"): row for row in lane_rows if isinstance(row, Mapping)}
    opening = buckets.get("open_20_60m") or {}
    mid = buckets.get("mid_session") or {}
    findings = [
        {
            "stage": "raw_candidate_edge",
            "status": "CONDITIONAL_EDGE",
            "finding": (
                "Candidate edge is horizon- and time-bucket dependent, not universally absent. "
                f"open_20_60m +30m={opening.get('avg_return_30m_pct')}%, "
                f"+60m={opening.get('avg_return_60m_pct')}%; "
                f"mid_session +30m={mid.get('avg_return_30m_pct')}%, "
                f"+60m={mid.get('avg_return_60m_pct')}%."
            ),
        },
        {
            "stage": "scanner_ranking",
            "status": "PARTIAL_RECONSTRUCTION",
            "finding": (
                "Shadow rank/role outcomes are available, but a true pre-Strategist Scanner "
                "control universe is unavailable. Ranking quality can be diagnosed but not "
                "causally attributed to Strategist yet."
            ),
        },
        {
            "stage": "strategist_commander",
            "status": "MISSING_CONTROL",
            "finding": (
                "Historical raw Scanner and explicit Commander alternatives were not persisted. "
                "No value-add claim is allowed."
            ),
        },
        {
            "stage": "monitor_entry",
            "status": "DIAGNOSTIC",
            "finding": (
                f"{entry.get('matched_trade_count')} trades matched a nearby shadow baseline; "
                f"average entry price delta={entry.get('average_entry_price_delta_pct')}%."
            ),
        },
        {
            "stage": "monitor_exit",
            "status": "DIAGNOSTIC",
            "finding": (
                f"Post-exit hold alternatives were observed for {exit_hold.get('observed_trade_count')} trades."
            ),
        },
        {
            "stage": "realized_system",
            "status": "NEGATIVE",
            "finding": (
                f"Realized count={realized.get('performance', {}).get('count')}, "
                f"expectancy={realized.get('performance', {}).get('expectancy_pct')}%, "
                f"profit_factor={realized.get('performance', {}).get('profit_factor')}."
            ),
        },
    ]
    return findings


def _next_action(
    *,
    role_rows: list[dict[str, Any]],
    realized: dict[str, Any],
    exit_hold: dict[str, Any],
) -> dict[str, Any]:
    roles = {str(row.get("name") or ""): row for row in role_rows}
    top_pick = roles.get("top_pick") or {}
    realized_expectancy = _to_float((realized.get("performance") or {}).get("expectancy_pct"))
    five_minute_exit = next(
        (
            row for row in exit_hold.get("by_hold_offset") or []
            if row.get("offset") == "+5m"
        ),
        {},
    )
    return {
        "priority": 1,
        "component": "candidate_edge_and_horizon_alignment",
        "decision": "FIX_BEFORE_ENTRY_OR_EXIT_TUNING",
        "reason": (
            "Top-pick gross forward edge is economically trivial relative to current round-trip "
            "cost, while the realized system is deeply negative. Exit delay improvement is too "
            "small to rescue the deficit."
        ),
        "evidence": {
            "top_pick_15m_pct": top_pick.get("avg_return_15m_pct"),
            "top_pick_30m_pct": top_pick.get("avg_return_30m_pct"),
            "top_pick_60m_pct": top_pick.get("avg_return_60m_pct"),
            "realized_expectancy_pct": realized_expectancy,
            "post_exit_5m_average_improvement_pct": five_minute_exit.get("average_improvement_pct"),
        },
        "required_follow_up": [
            "separate candidate scoring by time bucket and intended holding horizon",
            "treat mid-session candidate generation as a distinct negative-edge segment",
            "evaluate open_20_60m continuation against 30-60 minute holding targets",
            "do not tune exits first",
            "do not attribute the problem to Strategist until a trusted raw Scanner control exists",
        ],
        "behavior_change_authorized": False,
    }


def build_loss_decomposition(*, reports_root: Path, start: str, end: str) -> dict[str, Any]:
    payloads = load_quant_shadow_candidate_payloads_for_range(
        reports_root=reports_root,
        start=start,
        end=end,
    )
    shadow = build_quant_shadow_candidate_evaluation(payloads)
    candidates = _candidate_rows(payloads)
    models = _load_trade_models(reports_root, start, end)
    rank_rows = _group_forward(candidates, lambda row: _rank_bucket(row.get("rank")))
    role_rows = _group_forward(candidates, lambda row: row.get("shadow_role"))
    tactic_rows = _group_forward(candidates, lambda row: row.get("quant_tactic_id"))
    realized = _realized_trade_summary(models)
    entry = _entry_timing_summary(models, candidates)
    exit_hold = _exit_hold_summary(models)
    return _attr.assemble_loss_decomposition(
        start=start,
        end=end,
        payload_count=len(payloads),
        shadow=shadow,
        model_count=len(models),
        rank_rows=rank_rows,
        role_rows=role_rows,
        tactic_rows=tactic_rows,
        entry=entry,
        exit_hold=exit_hold,
        realized=realized,
        diagnosis=_diagnosis(
            shadow=shadow,
            candidate_rank=rank_rows,
            realized=realized,
            entry=entry,
            exit_hold=exit_hold,
        ),
        next_action=_next_action(
            role_rows=role_rows,
            realized=realized,
            exit_hold=exit_hold,
        ),
    )


render_loss_decomposition = _render.render_loss_decomposition


def write_loss_decomposition(
    *,
    reports_root: Path,
    start: str,
    end: str,
    output_dir: Path,
) -> dict[str, str]:
    payload = build_loss_decomposition(reports_root=reports_root, start=start, end=end)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "full_chain_loss_decomposition.json"
    md_path = output_dir / "full_chain_loss_decomposition.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_loss_decomposition(payload), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}
