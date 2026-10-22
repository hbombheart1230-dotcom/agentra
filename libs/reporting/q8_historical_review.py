from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping

from libs.reporting.evaluation.q8_historical_aggregation_p15 import (  # noqa: F401 - facade ABI re-exports
    ForwardAccumulator,
    GroupAccumulator,
    PatternRowFold,
    ShadowSummaryFold,
    _aggregate_return_rows,
    _avg,
    _decision_for_reclaim_subtype,
    _float,
    _int,
    _pct_from_ratio,
    _text,
    _weighted_avg,
)
from libs.reporting.evaluation.q8_historical_render_p15 import (  # noqa: F401 - facade ABI re-exports
    _md_table,
    render_q8_historical_review_markdown,
)
from libs.runtime.quant.vwap_reclaim_observation import classify_below_vwap_reclaim_observation


def _read_json(path: Path) -> Dict[str, Any]:
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            payload = json.loads(path.read_text(encoding=encoding))
            return payload if isinstance(payload, dict) else {}
        except Exception:
            continue
    return {}


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), ensure_ascii=False, indent=2), encoding="utf-8")


def _write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(text or ""), encoding="utf-8-sig", newline="\n")


def _iter_days(start: str, end: str) -> Iterable[str]:
    from datetime import date, timedelta

    current = date.fromisoformat(str(start)[:10])
    last = date.fromisoformat(str(end)[:10])
    while current <= last:
        yield current.isoformat()
        current += timedelta(days=1)


def _quant_shadow_candidate_root(reports_root: Path) -> Path:
    return Path(reports_root).parent / "data" / "logs" / "quant_shadow_candidates"


def _iter_quant_shadow_candidate_rows(reports_root: Path, *, start: str, end: str) -> Iterable[Dict[str, Any]]:
    root = _quant_shadow_candidate_root(reports_root)
    for day in _iter_days(start, end):
        day_root = root / day
        if not day_root.exists():
            continue
        for path in sorted(day_root.glob("*.json")):
            if path.name == "latest.json":
                continue
            payload = _read_json(path)
            for row in list(payload.get("candidates") or []):
                if isinstance(row, Mapping):
                    yield dict(row)


def _trade_id_from_path(path: Path) -> str:
    try:
        return path.parents[1].name
    except Exception:
        return ""


def _extract_trade_rows(reports_root: Path, *, start: str, end: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for path in sorted((reports_root / "trades").glob("*/**/reports/ai_trade_summary.json")):
        try:
            day = path.parts[path.parts.index("trades") + 1]
        except Exception:
            continue
        if day < start or day > end:
            continue
        payload = _read_json(path)
        trade = payload.get("trade") if isinstance(payload.get("trade"), dict) else {}
        truth = payload.get("truth_surface") if isinstance(payload.get("truth_surface"), dict) else {}
        decision = payload.get("decision_flow") if isinstance(payload.get("decision_flow"), dict) else {}
        quant = payload.get("quant_tactic") if isinstance(payload.get("quant_tactic"), dict) else {}
        pnl_pct = _pct_from_ratio(truth.get("pnl_pct"))
        rows.append(
            {
                "day": day,
                "trade_id": _text(trade.get("trade_id")) or _trade_id_from_path(path),
                "symbol": _text(trade.get("symbol")),
                "status": _text(trade.get("status")),
                "pnl_pct": pnl_pct,
                "truth_source": _text(truth.get("truth_source")),
                "tactic": _text(
                    quant.get("tactic_id")
                    or quant.get("selected_tactic")
                    or trade.get("tactical_strategy")
                    or decision.get("tactical_strategy")
                ),
                "playbook": _text(quant.get("playbook") or trade.get("playbook") or decision.get("playbook")),
                "entry_reason": _text(decision.get("entry_reason") or decision.get("entry_trigger")),
                "exit_reason": _text(decision.get("exit_reason") or decision.get("exit_trigger")),
            }
        )
    return rows


def _daily_summary_rows(reports_root: Path, *, start: str, end: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for day in _iter_days(start, end):
        path = reports_root / "operator_summary" / "daily" / day / "daily_summary.json"
        if not path.exists():
            continue
        payload = _read_json(path)
        metrics = payload.get("metrics") if isinstance(payload.get("metrics"), dict) else {}
        q = (
            payload.get("quant_shadow_candidate_evaluation")
            if isinstance(payload.get("quant_shadow_candidate_evaluation"), dict)
            else {}
        )
        gate = q.get("evaluation_trust_gate") if isinstance(q.get("evaluation_trust_gate"), dict) else {}
        rail = payload.get("market_regime_rail_review") if isinstance(payload.get("market_regime_rail_review"), dict) else {}
        rows.append(
            {
                "day": day,
                "trade_count": _int(metrics.get("trade_count")),
                "closed_trade_count": _int(metrics.get("closed_trade_count")),
                "return_sample_count": _int(metrics.get("return_sample_count")),
                "unavailable_return_count": _int(metrics.get("unavailable_return_count")),
                "win_rate": _float(metrics.get("win_rate")) or 0.0,
                "avg_return_pct": _float(metrics.get("avg_return_pct")) or 0.0,
                "truth_surface_count": _int(metrics.get("truth_surface_count")),
                "shadow_candidate_count": _int(q.get("candidate_count")),
                "shadow_deduped_candidate_count": _int(q.get("deduped_candidate_count")),
                "shadow_duplicate_candidate_count": _int(q.get("duplicate_candidate_count")),
                "shadow_evaluated_count": _int(q.get("evaluated_count")),
                "shadow_would_enter_count": _int(q.get("would_enter_count")),
                "shadow_forward_outcome_coverage": _float(q.get("forward_outcome_coverage")),
                "q8_trust_gate_status": _text(gate.get("status")),
                "q8_promotion_allowed": bool(gate.get("promotion_allowed")),
                "q8_trusted_forward_count": _int(gate.get("trusted_forward_count")),
                "q8_trusted_forward_coverage": _float(gate.get("trusted_forward_coverage")),
                "q8_duplicate_rate": _float(gate.get("duplicate_rate")),
                "market_regime_rail": _text(rail.get("rail_id") or rail.get("market_regime_rail")),
            }
        )
    return rows


def _aggregate_shadow_summaries(reports_root: Path, *, start: str, end: str) -> Dict[str, Any]:
    fold = ShadowSummaryFold()
    for day in _iter_days(start, end):
        path = reports_root / "operator_summary" / "daily" / day / "daily_summary.json"
        if not path.exists():
            continue
        fold.add_day(day, _read_json(path))
    if fold.needs_candidate_subtypes():
        for row in _iter_quant_shadow_candidate_rows(reports_root, start=start, end=end):
            observation = classify_below_vwap_reclaim_observation(row)
            if not bool(observation.get("applies")):
                continue
            fold.add_candidate_subtype(observation.get("subtype_v2"))
    return fold.to_dict()


def _pattern_rows_from_daily_summaries(
    reports_root: Path,
    *,
    start: str,
    end: str,
    section: str,
    group_key: str,
) -> List[Dict[str, Any]]:
    fold = PatternRowFold(section, group_key)
    for day in _iter_days(start, end):
        path = reports_root / "operator_summary" / "daily" / day / "daily_summary.json"
        if not path.exists():
            continue
        fold.add_payload(_read_json(path))
    return fold.rows()


def _promotion_recommendations(payload: Mapping[str, Any]) -> List[Dict[str, Any]]:
    groups = {str(row.get("reason")): dict(row) for row in list(payload.get("q8_blocker_groups") or []) if isinstance(row, Mapping)}
    recs: List[Dict[str, Any]] = []
    defensive = next(
        (
            row
            for row in list(payload.get("trade_by_tactic") or [])
            if str(row.get("name") or "") == "defensive_observe"
        ),
        {},
    )
    if defensive and int(defensive.get("count") or 0) >= 5 and float(defensive.get("avg_return_pct") or 0.0) < 0:
        recs.append(
            {
                "candidate": "risk_off_defensive_observe_no_entry_policy",
                "decision": "promoted_keep",
                "reason": "defensive_observe live trades are negative and 2026-06-08 showed severe risk-off misuse.",
            }
        )
    for reason, label in (
        ("below_vwap_reclaim_not_ready", "subtype_adjust_review"),
        ("breakout_not_ready", "adjust_and_retest"),
        ("pullback_not_mature", "adjust_and_retest"),
        ("volume_confirmation_missing", "retain_strict_or_observe"),
        ("human_chart_sanity_guard_blocked", "retain_veto_review_missed"),
    ):
        row = groups.get(reason) or {}
        if not row:
            continue
        recs.append(
            {
                "candidate": reason,
                "decision": label,
                "candidate_count": row.get("candidate_count"),
                "observed_count": row.get("observed_count"),
                "avg_latest_return_pct": row.get("avg_latest_return_pct"),
                "missed_opportunity_rate": row.get("missed_opportunity_rate"),
                "adverse_rate": row.get("adverse_rate"),
            }
        )
    subtype_rows = list(payload.get("below_vwap_reclaim_subtype_forward") or [])
    if subtype_rows:
        strongest = max(
            subtype_rows,
            key=lambda row: (
                float(row.get("avg_return_15m_pct") or 0.0),
                float(row.get("avg_return_5m_pct") or 0.0),
                int(row.get("observed_count") or 0),
            ),
        )
        recs.append(
            {
                "candidate": "below_vwap_reclaim_subtype_policy",
                "decision": "do_not_relax_globally",
                "reason": (
                    f"Subtype forward evidence is mixed; strongest={strongest.get('name')} "
                    f"5m={float(strongest.get('avg_return_5m_pct') or 0.0):.4f}%, "
                    f"15m={float(strongest.get('avg_return_15m_pct') or 0.0):.4f}%. "
                    "Review classifier labels before behavior promotion."
                ),
            }
        )
    return recs


def build_q8_historical_review_payload(
    *,
    reports_root: Path = Path("reports"),
    start: str,
    end: str,
) -> Dict[str, Any]:
    daily_rows = _daily_summary_rows(reports_root, start=start, end=end)
    trade_rows = _extract_trade_rows(reports_root, start=start, end=end)
    return_rows = [row for row in trade_rows if isinstance(row.get("pnl_pct"), (int, float))]
    shadow = _aggregate_shadow_summaries(reports_root, start=start, end=end)
    pattern_by_tactic = _pattern_rows_from_daily_summaries(
        reports_root,
        start=start,
        end=end,
        section="strategist",
        group_key="by_tactical_strategy",
    )
    pattern_by_exit = _pattern_rows_from_daily_summaries(
        reports_root,
        start=start,
        end=end,
        section="monitor_exit",
        group_key="by_exit_reason",
    )
    payload: Dict[str, Any] = {
        "schema_version": "q8_historical_review.v1",
        "behavior_effect": "evaluation_only",
        "start": str(start)[:10],
        "end": str(end)[:10],
        "daily_count": len(daily_rows),
        "daily_rows": daily_rows,
        "q8_promotion_eligibility": {
            "promotion_allowed_day_count": sum(1 for row in daily_rows if bool(row.get("q8_promotion_allowed"))),
            "trusted_gate_day_count": sum(1 for row in daily_rows if _text(row.get("q8_trust_gate_status"))),
            "status": (
                "promotion_review_possible"
                if any(bool(row.get("q8_promotion_allowed")) for row in daily_rows)
                else "promotion_blocked_by_trust_gate_or_legacy_data"
            ),
            "rule": "Historical conclusions require daily evaluation_trust_gate.promotion_allowed=true. Legacy daily summaries without trust gate are observation-only.",
        },
        "trade_summary": {
            "trade_report_count": len(trade_rows),
            "return_sample_count": len(return_rows),
            "avg_return_pct": _avg([float(row["pnl_pct"]) for row in return_rows]),
            "win_rate": round(sum(1 for row in return_rows if float(row["pnl_pct"]) > 0) / len(return_rows), 4)
            if return_rows
            else 0.0,
            "truth_sources": [
                {"name": name, "count": count}
                for name, count in Counter(_text(row.get("truth_source")) or "missing" for row in trade_rows).most_common(12)
            ],
        },
        "trade_by_tactic": pattern_by_tactic or _aggregate_return_rows(return_rows, "tactic"),
        "trade_by_entry_reason": _aggregate_return_rows(return_rows, "entry_reason"),
        "trade_by_exit_reason": pattern_by_exit or _aggregate_return_rows(return_rows, "exit_reason"),
        **shadow,
    }
    eligibility = payload.get("q8_promotion_eligibility") if isinstance(payload.get("q8_promotion_eligibility"), Mapping) else {}
    if int(eligibility.get("promotion_allowed_day_count") or 0) <= 0:
        payload["promotion_recommendations"] = [
            {
                "candidate": "all_q8_candidates",
                "decision": "retain_under_observation",
                "reason": "no historical day passed the Q8 evaluation trust gate",
            }
        ]
    else:
        payload["promotion_recommendations"] = _promotion_recommendations(payload)
    return payload


def write_q8_historical_review(
    *,
    reports_root: Path = Path("reports"),
    docs_root: Path = Path("docs/tactics"),
    start: str,
    end: str,
) -> Dict[str, Any]:
    payload = build_q8_historical_review_payload(reports_root=reports_root, start=start, end=end)
    stem = f"q8_historical_review_{str(start)[:10]}_to_{str(end)[:10]}"
    md_path = docs_root / f"{stem}.md"
    json_path = reports_root / "dev" / "analysis" / "q8_historical_review" / f"{stem}.json"
    _write_json(json_path, payload)
    _write_md(md_path, render_q8_historical_review_markdown(payload))
    return {"ok": True, "payload": payload, "md_path": str(md_path), "json_path": str(json_path)}


__all__ = [
    "build_q8_historical_review_payload",
    "render_q8_historical_review_markdown",
    "write_q8_historical_review",
]
