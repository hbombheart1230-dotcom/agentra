"""Pure Q8 historical-review aggregation (P1.5 DEV-A): normalization, accumulators and per-day folds.

No I/O: ``libs.reporting.q8_historical_review`` reads each day and feeds these folds in the original order.
``*_impl`` bodies and folds resolve helpers on the injected ``facade`` at call time (accumulator methods excepted).
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Sequence


def _float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        text = str(value).strip().replace("%", "").replace(",", "")
        if not text:
            return None
        return float(text)
    except Exception:
        return None


def _int(value: Any) -> int:
    try:
        if value in (None, ""):
            return 0
        return int(float(str(value).replace(",", "")))
    except Exception:
        return 0


def _pct_from_ratio_impl(value: Any, *, facade: Any) -> float | None:
    parsed = facade._float(value)
    if parsed is None:
        return None
    return parsed * 100.0 if abs(parsed) <= 1.0 else parsed


def _text(value: Any) -> str:
    text = str(value or "").strip()
    return "" if text.lower() in {"", "-", "none", "null", "unknown", "not_captured"} else text


def _avg(values: Sequence[float]) -> float:
    return round(sum(values) / len(values), 4) if values else 0.0


def _weighted_avg(total: float, weight: int) -> float:
    return round(total / weight, 4) if weight > 0 else 0.0


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
        for key, prefix in (("avg_latest_return_pct", "latest"), ("avg_max_favorable_pct", "mfe"), ("avg_max_adverse_pct", "mae")):
            value = _float(row.get(key))
            if value is not None and observed > 0:
                setattr(self, f"{prefix}_sum", getattr(self, f"{prefix}_sum") + value * observed)
                setattr(self, f"{prefix}_weight", getattr(self, f"{prefix}_weight") + observed)

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


_HORIZON_FIELDS = tuple((horizon, f"avg_return_{horizon}_pct") for horizon in ("3m", "5m", "15m", "30m", "60m"))
_FORWARD_AVG_KEYS = tuple(key for _, key in _HORIZON_FIELDS) + ("avg_mfe_5m_pct", "avg_mae_5m_pct")


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
        self.candidate_count += _int(row.get("candidate_count"))
        self.observed_count += _int(row.get("observed_count"))
        self.day_count += 1
        if not any(row.get(f"observed_count_{name}") is not None for name, _ in _HORIZON_FIELDS):
            self.legacy_horizon_count_missing_days += 1
        for horizon, key in _HORIZON_FIELDS:
            horizon_observed = _int(row.get(f"observed_count_{horizon}"))
            horizon_days = _int(row.get(f"observed_day_count_{horizon}"))
            if horizon_observed > 0:
                self.horizon_observed_counts[horizon] += horizon_observed
                self.horizon_observed_day_counts[horizon] += max(1, horizon_days)
            value = _float(row.get(key))
            if value is not None and horizon_observed > 0:
                self.sums[key] += float(value) * horizon_observed
                self.weights[key] += horizon_observed
        for key in ("avg_mfe_5m_pct", "avg_mae_5m_pct"):
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
            "coverage": round(float(self.observed_count) / float(self.candidate_count), 4) if self.candidate_count else 0.0,
            "measurement_contract_version": "q8_horizon_coverage.v2",
            "legacy_horizon_count_missing_days": self.legacy_horizon_count_missing_days,
            "horizon_coverage_verified": self.legacy_horizon_count_missing_days == 0,
        }
        for key in _FORWARD_AVG_KEYS:
            weight = int(self.weights.get(key) or 0)
            out[key] = _weighted_avg(float(self.sums.get(key) or 0.0), weight) if weight > 0 else None
        for horizon, _ in _HORIZON_FIELDS:
            count = int(self.horizon_observed_counts.get(horizon) or 0)
            out[f"observed_count_{horizon}"] = count
            out[f"observed_day_count_{horizon}"] = int(self.horizon_observed_day_counts.get(horizon) or 0)
            out[f"coverage_{horizon}"] = round(float(count) / float(self.candidate_count), 4) if self.candidate_count else 0.0
        return out


def _decision_for_reclaim_subtype_impl(row: Mapping[str, Any], *, facade: Any) -> str:
    name = facade._text(row.get("name"))
    observed = facade._int(row.get("observed_count"))
    ret5 = facade._float(row.get("avg_return_5m_pct")) or 0.0
    ret15 = facade._float(row.get("avg_return_15m_pct")) or 0.0
    ret60 = facade._float(row.get("avg_return_60m_pct")) or 0.0
    mae5 = facade._float(row.get("avg_mae_5m_pct")) or 0.0
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


def _aggregate_return_rows_impl(rows: Sequence[Mapping[str, Any]], key: str, *, limit: int, facade: Any) -> List[Dict[str, Any]]:
    grouped: Dict[str, List[float]] = defaultdict(list)
    for row in rows:
        value = facade._text(row.get(key)) or "missing"
        pnl = row.get("pnl_pct")
        if isinstance(pnl, (int, float)):
            grouped[value].append(float(pnl))
    out: List[Dict[str, Any]] = []
    for name, values in grouped.items():
        if not values:
            continue
        out.append(
            {
                "name": name,
                "count": len(values),
                "win_count": sum(1 for value in values if value > 0),
                "loss_count": sum(1 for value in values if value < 0),
                "win_rate": round(sum(1 for value in values if value > 0) / len(values), 4),
                "avg_return_pct": facade._avg(values),
            }
        )
    out.sort(key=lambda row: (int(row["count"]), abs(float(row["avg_return_pct"]))), reverse=True)
    return out[:limit]


def _counter_rows(counter: Counter[str], limit: int) -> List[Dict[str, Any]]:
    return [{"name": name, "count": count} for name, count in counter.most_common(limit) if name]


def _named_counts(counter: Counter[str], rows: Any, facade: Any) -> None:
    for row in list(rows or []):
        if isinstance(row, Mapping):
            counter[facade._text(row.get("name"))] += facade._int(row.get("count"))


class ShadowSummaryFold:
    """Folds daily ``quant_shadow_candidate_evaluation`` / ``q8_shadow_blocker_review`` sections."""

    def __init__(self, *, facade: Any) -> None:
        self.facade = facade
        self.reason_counter: Counter[str] = Counter()
        self.role_counter: Counter[str] = Counter()
        self.tactic_counter: Counter[str] = Counter()
        self.below_vwap_subtype_counter: Counter[str] = Counter()
        self.below_vwap_subtype_v2_counter: Counter[str] = Counter()
        self.subtype_forward: Dict[str, ForwardAccumulator] = defaultdict(facade.ForwardAccumulator)
        self.subtype_forward_days: set[str] = set()
        self.group_acc: Dict[str, GroupAccumulator] = defaultdict(facade.GroupAccumulator)
        self.q_days = 0
        self.q8_group_days = 0

    def add_day(self, day: str, payload: Mapping[str, Any]) -> None:
        q = payload.get("quant_shadow_candidate_evaluation") if isinstance(payload.get("quant_shadow_candidate_evaluation"), dict) else {}
        facade = self.facade
        if q.get("candidate_count") is not None:
            self.q_days += 1
        _named_counts(self.reason_counter, q.get("by_reason"), facade)
        _named_counts(self.role_counter, q.get("by_role"), facade)
        _named_counts(self.tactic_counter, q.get("by_tactic_id"), facade)
        below_vwap = q.get("below_vwap_reclaim_observation") if isinstance(q.get("below_vwap_reclaim_observation"), Mapping) else {}
        _named_counts(self.below_vwap_subtype_counter, below_vwap.get("by_subtype"), facade)
        _named_counts(self.below_vwap_subtype_v2_counter, below_vwap.get("by_subtype_v2"), facade)
        lane_forward = q.get("entry_lane_forward_outcomes") if isinstance(q.get("entry_lane_forward_outcomes"), Mapping) else {}
        for row in list(lane_forward.get("by_lane_subtype") or []):
            name = facade._text(row.get("name")) if isinstance(row, Mapping) else ""
            if not name.startswith("vwap_reclaim:"):
                continue
            self.subtype_forward[name].add(row)
            self.subtype_forward_days.add(day)
        q8 = payload.get("q8_shadow_blocker_review") if isinstance(payload.get("q8_shadow_blocker_review"), dict) else {}
        groups = list(q8.get("groups") or [])
        if groups:
            self.q8_group_days += 1
        for row in groups:
            reason = facade._text(row.get("reason") or row.get("name")) if isinstance(row, Mapping) else ""
            if reason:
                self.group_acc[reason].add(day, row)

    def needs_candidate_subtypes(self) -> bool:
        return not self.below_vwap_subtype_v2_counter

    def add_candidate_subtype(self, subtype_v2: Any) -> None:
        self.below_vwap_subtype_v2_counter[self.facade._text(subtype_v2)] += 1

    def to_dict(self) -> Dict[str, Any]:
        ordered = sorted(self.subtype_forward.items(), key=lambda item: (item[1].candidate_count, item[0]), reverse=True)
        subtype_forward_rows = [acc.to_dict(name) for name, acc in ordered]
        for row in subtype_forward_rows:
            row["decision"] = self.facade._decision_for_reclaim_subtype(row)
        groups = sorted(self.group_acc.items(), key=lambda item: item[1].candidate_count, reverse=True)
        return {
            "q_shadow_day_count": self.q_days,
            "q8_group_day_count": self.q8_group_days,
            "by_reason": _counter_rows(self.reason_counter, 20),
            "by_role": _counter_rows(self.role_counter, 12),
            "by_tactic_id": _counter_rows(self.tactic_counter, 12),
            "below_vwap_reclaim_by_subtype": _counter_rows(self.below_vwap_subtype_counter, 12),
            "below_vwap_reclaim_by_subtype_v2": _counter_rows(self.below_vwap_subtype_v2_counter, 12),
            "below_vwap_reclaim_subtype_forward_day_count": len(self.subtype_forward_days),
            "below_vwap_reclaim_subtype_forward": subtype_forward_rows,
            "q8_blocker_groups": [acc.to_dict(reason) for reason, acc in groups],
        }


_PATTERN_INT_FIELDS = ("win_count", "loss_count", "flat_count", "cost_drag_loss_count")


class PatternRowFold:
    """Folds one ``pattern_performance.<section>.<group_key>`` list across daily summaries."""

    def __init__(self, section: str, group_key: str, *, facade: Any) -> None:
        self.facade = facade
        self.section = section
        self.group_key = group_key
        self.grouped: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {"count": 0, "closed_or_realized_count": 0, "win_count": 0, "loss_count": 0, "flat_count": 0,
                     "return_sum": 0.0, "return_weight": 0, "cost_drag_loss_count": 0}
        )

    def add_payload(self, payload: Mapping[str, Any]) -> None:
        pattern = payload.get("pattern_performance") if isinstance(payload.get("pattern_performance"), dict) else {}
        section_payload = pattern.get(self.section) if isinstance(pattern.get(self.section), dict) else {}
        rows = section_payload.get(self.group_key) if isinstance(section_payload.get(self.group_key), list) else []
        _text, _int, _float = self.facade._text, self.facade._int, self.facade._float
        for row in rows:
            if not isinstance(row, Mapping):
                continue
            bucket = self.grouped[_text(row.get("name")) or "missing"]
            count = _int(row.get("count"))
            closed = _int(row.get("closed_or_realized_count") or count)
            avg = _float(row.get("avg_return_pct"))
            bucket["count"] += count
            bucket["closed_or_realized_count"] += closed
            for key in _PATTERN_INT_FIELDS:
                bucket[key] += _int(row.get(key))
            if avg is not None and closed > 0:
                bucket["return_sum"] += float(avg) * closed
                bucket["return_weight"] += closed

    def rows(self) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for name, bucket in self.grouped.items():
            closed = int(bucket.get("closed_or_realized_count") or 0)
            wins = int(bucket.get("win_count") or 0)
            out.append(
                {
                    "name": name,
                    "count": int(bucket.get("count") or 0),
                    "closed_or_realized_count": closed,
                    "win_count": wins,
                    "loss_count": int(bucket.get("loss_count") or 0),
                    "flat_count": int(bucket.get("flat_count") or 0),
                    "win_rate": round(wins / closed, 4) if closed else 0.0,
                    "avg_return_pct": self.facade._weighted_avg(float(bucket.get("return_sum") or 0.0), int(bucket.get("return_weight") or 0)),
                    "cost_drag_loss_count": int(bucket.get("cost_drag_loss_count") or 0),
                }
            )
        out.sort(key=lambda row: (int(row.get("closed_or_realized_count") or 0), abs(float(row.get("avg_return_pct") or 0.0))), reverse=True)
        return out
