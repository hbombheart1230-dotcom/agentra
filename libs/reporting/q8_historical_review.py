from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

from libs.reporting import q8_historical_projection_fast06 as _proj
from libs.reporting.q8_historical_projection_fast06 import ForwardAccumulator, GroupAccumulator
from libs.reporting.q8_review_render_fast06 import _md_table, render_q8_historical_review_markdown
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


_float = _proj.num
_int = _proj.count
_pct_from_ratio = _proj.pct_from_ratio
_text = _proj.label
_avg = _proj.avg
_weighted_avg = _proj.weighted_avg


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


def _decision_for_reclaim_subtype(row: Mapping[str, Any]) -> str:
    name = _text(row.get("name"))
    observed = _int(row.get("observed_count"))
    ret5 = _float(row.get("avg_return_5m_pct")) or 0.0
    ret15 = _float(row.get("avg_return_15m_pct")) or 0.0
    ret60 = _float(row.get("avg_return_60m_pct")) or 0.0
    mae5 = _float(row.get("avg_mae_5m_pct")) or 0.0
    if observed < 30:
        return "retain_observation_sample_small"
    if name.endswith("true_below_vwap_failure") and ret5 > 0 and ret15 > 0:
        return "review_classifier_or_label"
    if ret5 > 0 and ret15 > 0 and mae5 > -0.5:
        return "adjust_and_retest_candidate"
    if ret5 < 0 and ret15 < 0:
        return "keep_blocked"
    if ret60 > 0 and ret5 <= 0:
        return "hold_observation_longer_horizon_only"
    return "retain_under_observation"


def _extract_trade_rows(reports_root: Path, *, start: str, end: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for path in sorted((reports_root / "trades").glob("*/**/reports/ai_trade_summary.json")):
        try:
            day = path.parts[path.parts.index("trades") + 1]
        except Exception:
            continue
        if day < start or day > end:
            continue
        rows.append(_proj.trade_row_from_summary(day, _read_json(path), fallback_trade_id=_trade_id_from_path(path)))
    return rows


_aggregate_return_rows = _proj.aggregate_return_rows


def _daily_summary_rows(reports_root: Path, *, start: str, end: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for day in _iter_days(start, end):
        path = reports_root / "operator_summary" / "daily" / day / "daily_summary.json"
        if not path.exists():
            continue
        rows.append(_proj.daily_row_from_summary(day, _read_json(path)))
    return rows


def _aggregate_shadow_summaries(reports_root: Path, *, start: str, end: str) -> Dict[str, Any]:
    aggregator = _proj.ShadowSummaryAggregator()
    for day in _iter_days(start, end):
        path = reports_root / "operator_summary" / "daily" / day / "daily_summary.json"
        if not path.exists():
            continue
        aggregator.add_day(day, _read_json(path))
    if aggregator.needs_subtype_v2_fallback():
        for row in _iter_quant_shadow_candidate_rows(reports_root, start=start, end=end):
            aggregator.add_subtype_v2_observation(classify_below_vwap_reclaim_observation(row))
    return aggregator.finish(decide_subtype=_decision_for_reclaim_subtype)


def _pattern_rows_from_daily_summaries(
    reports_root: Path,
    *,
    start: str,
    end: str,
    section: str,
    group_key: str,
) -> List[Dict[str, Any]]:
    payloads = []
    for day in _iter_days(start, end):
        path = reports_root / "operator_summary" / "daily" / day / "daily_summary.json"
        if not path.exists():
            continue
        payloads.append(_read_json(path))
    return _proj.pattern_rows(payloads, section=section, group_key=group_key)


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
    return _proj.assemble_historical_payload(
        start=start,
        end=end,
        daily_rows=daily_rows,
        trade_rows=trade_rows,
        shadow=shadow,
        pattern_by_tactic=pattern_by_tactic,
        pattern_by_exit=pattern_by_exit,
        recommend=_promotion_recommendations,
    )


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
