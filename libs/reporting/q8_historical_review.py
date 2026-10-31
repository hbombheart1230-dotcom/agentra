from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

from libs.runtime.quant.vwap_reclaim_observation import classify_below_vwap_reclaim_observation
from libs.reporting import q8_historical_scalar_projection as _scalar_owner
from libs.reporting import q8_historical_day_projection as _day_owner
from libs.reporting import q8_historical_aggregate_projection as _aggregate_owner
from libs.reporting import q8_historical_markdown_table_projection as _table_owner
from libs.reporting import q8_historical_decision_projection as _decision_owner
from libs.reporting import q8_historical_read_projection as _read_owner
from libs.reporting import q8_historical_trade_projection as _trade_owner
from libs.reporting import q8_historical_daily_projection as _daily_owner
from libs.reporting import q8_historical_pattern_projection as _pattern_owner
from libs.reporting import q8_historical_shadow_aggregate_projection as _shadow_aggregate_owner
from libs.reporting import q8_historical_recommendation_projection as _recommendation_owner
from libs.reporting import q8_historical_payload_projection as _payload_owner
from libs.reporting import q8_historical_markdown_projection as _markdown_owner


def _read_json(path: Path) -> Dict[str, Any]:
    return _read_owner._read_json(path, facade=sys.modules[__name__])


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), ensure_ascii=False, indent=2), encoding="utf-8")


def _write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(text or ""), encoding="utf-8-sig", newline="\n")


def _float(value: Any) -> float | None:
    return _scalar_owner._float(value)


def _int(value: Any) -> int:
    return _scalar_owner._int(value)


def _pct_from_ratio(value: Any) -> float | None:
    return _scalar_owner._pct_from_ratio(value, facade=sys.modules[__name__])


def _text(value: Any) -> str:
    return _scalar_owner._text(value)


def _avg(values: Sequence[float]) -> float:
    return _scalar_owner._avg(values)


def _weighted_avg(total: float, weight: int) -> float:
    return _scalar_owner._weighted_avg(total, weight)


def _iter_days(start: str, end: str) -> Iterable[str]:
    yield from _day_owner._iter_days(start, end)


def _quant_shadow_candidate_root(reports_root: Path) -> Path:
    return _day_owner._quant_shadow_candidate_root(reports_root, facade=sys.modules[__name__])


def _iter_quant_shadow_candidate_rows(reports_root: Path, *, start: str, end: str) -> Iterable[Dict[str, Any]]:
    yield from _read_owner._iter_quant_shadow_candidate_rows(reports_root, start=start, end=end, facade=sys.modules[__name__])


def _trade_id_from_path(path: Path) -> str:
    return _day_owner._trade_id_from_path(path)


@dataclass
class GroupAccumulator:
    candidate_count: int = 0
    observed_count: int = 0
    positive_latest_count: int = 0
    missed_opportunity_count: int = 0
    adverse_count: int = 0
    latest_sum: float = 0.0
    latest_weight: int = 0
    mfe_sum: float = 0.0
    mfe_weight: int = 0
    mae_sum: float = 0.0
    mae_weight: int = 0
    decisions: Counter[str] = field(default_factory=Counter)
    days: set[str] = field(default_factory=set)

    def add(self, day: str, row: Mapping[str, Any]) -> None:
        candidates = _int(row.get("candidate_count") or row.get("count"))
        observed = _int(row.get("observed_count") or row.get("observed_review_candidate_count"))
        self.candidate_count += candidates
        self.observed_count += observed
        self.positive_latest_count += _int(row.get("positive_latest_count"))
        self.missed_opportunity_count += _int(row.get("missed_opportunity_count"))
        self.adverse_count += _int(row.get("adverse_count"))
        self.days.add(day)
        decision = _text(row.get("decision"))
        if decision:
            self.decisions[decision] += 1
        latest = _float(row.get("avg_latest_return_pct"))
        if latest is not None and observed > 0:
            self.latest_sum += latest * observed
            self.latest_weight += observed
        mfe = _float(row.get("avg_max_favorable_pct"))
        if mfe is not None and observed > 0:
            self.mfe_sum += mfe * observed
            self.mfe_weight += observed
        mae = _float(row.get("avg_max_adverse_pct"))
        if mae is not None and observed > 0:
            self.mae_sum += mae * observed
            self.mae_weight += observed

    def to_dict(self, reason: str) -> Dict[str, Any]:
        coverage = self.observed_count / self.candidate_count if self.candidate_count else 0.0
        positive_rate = self.positive_latest_count / self.observed_count if self.observed_count else 0.0
        missed_rate = self.missed_opportunity_count / self.observed_count if self.observed_count else 0.0
        adverse_rate = self.adverse_count / self.observed_count if self.observed_count else 0.0
        return {
            "reason": reason,
            "day_count": len(self.days),
            "candidate_count": self.candidate_count,
            "observed_count": self.observed_count,
            "coverage": round(coverage, 4),
            "avg_latest_return_pct": _weighted_avg(self.latest_sum, self.latest_weight),
            "avg_max_favorable_pct": _weighted_avg(self.mfe_sum, self.mfe_weight),
            "avg_max_adverse_pct": _weighted_avg(self.mae_sum, self.mae_weight),
            "positive_latest_count": self.positive_latest_count,
            "positive_latest_rate": round(positive_rate, 4),
            "missed_opportunity_count": self.missed_opportunity_count,
            "missed_opportunity_rate": round(missed_rate, 4),
            "adverse_count": self.adverse_count,
            "adverse_rate": round(adverse_rate, 4),
            "dominant_decision": self.decisions.most_common(1)[0][0] if self.decisions else "",
        }


@dataclass
class ForwardAccumulator:
    candidate_count: int = 0
    observed_count: int = 0
    day_count: int = 0
    sums: Dict[str, float] = field(default_factory=lambda: defaultdict(float))
    weights: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    horizon_observed_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    horizon_observed_day_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    legacy_horizon_count_missing_days: int = 0

    def add(self, row: Mapping[str, Any]) -> None:
        candidates = _int(row.get("candidate_count"))
        observed = _int(row.get("observed_count"))
        self.candidate_count += candidates
        self.observed_count += observed
        self.day_count += 1
        horizon_fields = (
            ("3m", "avg_return_3m_pct"),
            ("5m", "avg_return_5m_pct"),
            ("15m", "avg_return_15m_pct"),
            ("30m", "avg_return_30m_pct"),
            ("60m", "avg_return_60m_pct"),
        )
        has_horizon_counts = any(row.get(f"observed_count_{name}") is not None for name, _ in horizon_fields)
        if not has_horizon_counts:
            self.legacy_horizon_count_missing_days += 1
        for horizon, key in horizon_fields:
            horizon_observed = _int(row.get(f"observed_count_{horizon}"))
            horizon_days = _int(row.get(f"observed_day_count_{horizon}"))
            if horizon_observed > 0:
                self.horizon_observed_counts[horizon] += horizon_observed
                self.horizon_observed_day_counts[horizon] += max(1, horizon_days)
            value = _float(row.get(key))
            if value is not None and horizon_observed > 0:
                self.sums[key] += float(value) * horizon_observed
                self.weights[key] += horizon_observed
        for key in (
            "avg_mfe_5m_pct",
            "avg_mae_5m_pct",
        ):
            value = _float(row.get(key))
            horizon_observed = _int(row.get("observed_count_5m"))
            if value is not None and horizon_observed > 0:
                self.sums[key] += float(value) * horizon_observed
                self.weights[key] += horizon_observed

    def to_dict(self, name: str) -> Dict[str, Any]:
        out = {
            "name": name,
            "day_count": int(self.day_count),
            "candidate_count": int(self.candidate_count),
            "observed_count": int(self.observed_count),
            "coverage": round(float(self.observed_count) / float(self.candidate_count), 4)
            if self.candidate_count
            else 0.0,
            "measurement_contract_version": "q8_horizon_coverage.v2",
            "legacy_horizon_count_missing_days": self.legacy_horizon_count_missing_days,
            "horizon_coverage_verified": self.legacy_horizon_count_missing_days == 0,
        }
        for key in (
            "avg_return_3m_pct",
            "avg_return_5m_pct",
            "avg_return_15m_pct",
            "avg_return_30m_pct",
            "avg_return_60m_pct",
            "avg_mfe_5m_pct",
            "avg_mae_5m_pct",
        ):
            weight = int(self.weights.get(key) or 0)
            out[key] = _weighted_avg(float(self.sums.get(key) or 0.0), weight) if weight > 0 else None
        for horizon in ("3m", "5m", "15m", "30m", "60m"):
            count = int(self.horizon_observed_counts.get(horizon) or 0)
            out[f"observed_count_{horizon}"] = count
            out[f"observed_day_count_{horizon}"] = int(
                self.horizon_observed_day_counts.get(horizon) or 0
            )
            out[f"coverage_{horizon}"] = (
                round(float(count) / float(self.candidate_count), 4)
                if self.candidate_count
                else 0.0
            )
        return out


def _decision_for_reclaim_subtype(row: Mapping[str, Any]) -> str:
    return _decision_owner._decision_for_reclaim_subtype(row, facade=sys.modules[__name__])


def _extract_trade_rows(reports_root: Path, *, start: str, end: str) -> List[Dict[str, Any]]:
    return _trade_owner._extract_trade_rows(reports_root, start=start, end=end, facade=sys.modules[__name__])


def _aggregate_return_rows(rows: Sequence[Mapping[str, Any]], key: str, *, limit: int = 12) -> List[Dict[str, Any]]:
    return _aggregate_owner._aggregate_return_rows(rows, key, limit=limit, facade=sys.modules[__name__])


def _daily_summary_rows(reports_root: Path, *, start: str, end: str) -> List[Dict[str, Any]]:
    return _daily_owner._daily_summary_rows(reports_root, start=start, end=end, facade=sys.modules[__name__])


def _aggregate_shadow_summaries(reports_root: Path, *, start: str, end: str) -> Dict[str, Any]:
    return _shadow_aggregate_owner._aggregate_shadow_summaries(reports_root, start=start, end=end, facade=sys.modules[__name__])


def _pattern_rows_from_daily_summaries(
    reports_root: Path,
    *,
    start: str,
    end: str,
    section: str,
    group_key: str,
) -> List[Dict[str, Any]]:
    return _pattern_owner._pattern_rows_from_daily_summaries(reports_root, start=start, end=end, section=section, group_key=group_key, facade=sys.modules[__name__])


def _promotion_recommendations(payload: Mapping[str, Any]) -> List[Dict[str, Any]]:
    return _recommendation_owner._promotion_recommendations(payload)


def build_q8_historical_review_payload(
    *,
    reports_root: Path = Path("reports"),
    start: str,
    end: str,
) -> Dict[str, Any]:
    return _payload_owner.build_q8_historical_review_payload(reports_root=reports_root, start=start, end=end, facade=sys.modules[__name__])


def _md_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> List[str]:
    return _table_owner._md_table(headers, rows)


def render_q8_historical_review_markdown(payload: Mapping[str, Any]) -> str:
    return _markdown_owner.render_q8_historical_review_markdown(payload, facade=sys.modules[__name__])


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
