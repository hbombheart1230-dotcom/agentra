"""Pure Q8 evaluation-and-review projections (P1.5 FAST06).

Deterministic aggregation of already-loaded Q8 report payloads. File reads,
day iteration, report writes, trust-gate/dedupe contract calls and every
decision/threshold rule stay in the original ``libs.reporting.q8_*`` facades;
those rules are passed in as callables so this module never owns them.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Mapping, Sequence


# --- shared coercion (q8_historical_review semantics) -----------------------


def num(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        text = str(value).strip().replace("%", "").replace(",", "")
        if not text:
            return None
        return float(text)
    except Exception:
        return None


def count(value: Any) -> int:
    try:
        if value in (None, ""):
            return 0
        return int(float(str(value).replace(",", "")))
    except Exception:
        return 0


def pct_from_ratio(value: Any) -> float | None:
    parsed = num(value)
    if parsed is None:
        return None
    return parsed * 100.0 if abs(parsed) <= 1.0 else parsed


def label(value: Any) -> str:
    text = str(value or "").strip()
    return "" if text.lower() in {"", "-", "none", "null", "unknown", "not_captured"} else text


def avg(values: Sequence[float]) -> float:
    return round(sum(values) / len(values), 4) if values else 0.0


def weighted_avg(total: float, weight: int) -> float:
    return round(total / weight, 4) if weight > 0 else 0.0


def _mapping(payload: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = payload.get(key)
    return value if isinstance(value, dict) else {}


# --- A1: historical accumulators and row projections ------------------------


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
        candidates = count(row.get("candidate_count") or row.get("count"))
        observed = count(row.get("observed_count") or row.get("observed_review_candidate_count"))
        self.candidate_count += candidates
        self.observed_count += observed
        self.positive_latest_count += count(row.get("positive_latest_count"))
        self.missed_opportunity_count += count(row.get("missed_opportunity_count"))
        self.adverse_count += count(row.get("adverse_count"))
        self.days.add(day)
        decision = label(row.get("decision"))
        if decision:
            self.decisions[decision] += 1
        latest = num(row.get("avg_latest_return_pct"))
        if latest is not None and observed > 0:
            self.latest_sum += latest * observed
            self.latest_weight += observed
        mfe = num(row.get("avg_max_favorable_pct"))
        if mfe is not None and observed > 0:
            self.mfe_sum += mfe * observed
            self.mfe_weight += observed
        mae = num(row.get("avg_max_adverse_pct"))
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
            "avg_latest_return_pct": weighted_avg(self.latest_sum, self.latest_weight),
            "avg_max_favorable_pct": weighted_avg(self.mfe_sum, self.mfe_weight),
            "avg_max_adverse_pct": weighted_avg(self.mae_sum, self.mae_weight),
            "positive_latest_count": self.positive_latest_count,
            "positive_latest_rate": round(positive_rate, 4),
            "missed_opportunity_count": self.missed_opportunity_count,
            "missed_opportunity_rate": round(missed_rate, 4),
            "adverse_count": self.adverse_count,
            "adverse_rate": round(adverse_rate, 4),
            "dominant_decision": self.decisions.most_common(1)[0][0] if self.decisions else "",
        }


_HORIZON_FIELDS = (
    ("3m", "avg_return_3m_pct"),
    ("5m", "avg_return_5m_pct"),
    ("15m", "avg_return_15m_pct"),
    ("30m", "avg_return_30m_pct"),
    ("60m", "avg_return_60m_pct"),
)
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
        self.candidate_count += count(row.get("candidate_count"))
        self.observed_count += count(row.get("observed_count"))
        self.day_count += 1
        if not any(row.get(f"observed_count_{name}") is not None for name, _ in _HORIZON_FIELDS):
            self.legacy_horizon_count_missing_days += 1
        for horizon, key in _HORIZON_FIELDS:
            horizon_observed = count(row.get(f"observed_count_{horizon}"))
            horizon_days = count(row.get(f"observed_day_count_{horizon}"))
            if horizon_observed > 0:
                self.horizon_observed_counts[horizon] += horizon_observed
                self.horizon_observed_day_counts[horizon] += max(1, horizon_days)
            value = num(row.get(key))
            if value is not None and horizon_observed > 0:
                self.sums[key] += float(value) * horizon_observed
                self.weights[key] += horizon_observed
        for key in ("avg_mfe_5m_pct", "avg_mae_5m_pct"):
            value = num(row.get(key))
            horizon_observed = count(row.get("observed_count_5m"))
            if value is not None and horizon_observed > 0:
                self.sums[key] += float(value) * horizon_observed
                self.weights[key] += horizon_observed

    def to_dict(self, name: str) -> Dict[str, Any]:
        out: Dict[str, Any] = {
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
        for key in _FORWARD_AVG_KEYS:
            weight = int(self.weights.get(key) or 0)
            out[key] = weighted_avg(float(self.sums.get(key) or 0.0), weight) if weight > 0 else None
        for horizon, _ in _HORIZON_FIELDS:
            observed = int(self.horizon_observed_counts.get(horizon) or 0)
            out[f"observed_count_{horizon}"] = observed
            out[f"observed_day_count_{horizon}"] = int(self.horizon_observed_day_counts.get(horizon) or 0)
            out[f"coverage_{horizon}"] = (
                round(float(observed) / float(self.candidate_count), 4) if self.candidate_count else 0.0
            )
        return out


def trade_row_from_summary(day: str, payload: Mapping[str, Any], *, fallback_trade_id: str) -> Dict[str, Any]:
    trade = _mapping(payload, "trade")
    truth = _mapping(payload, "truth_surface")
    decision = _mapping(payload, "decision_flow")
    quant = _mapping(payload, "quant_tactic")
    return {
        "day": day,
        "trade_id": label(trade.get("trade_id")) or fallback_trade_id,
        "symbol": label(trade.get("symbol")),
        "status": label(trade.get("status")),
        "pnl_pct": pct_from_ratio(truth.get("pnl_pct")),
        "truth_source": label(truth.get("truth_source")),
        "tactic": label(
            quant.get("tactic_id")
            or quant.get("selected_tactic")
            or trade.get("tactical_strategy")
            or decision.get("tactical_strategy")
        ),
        "playbook": label(quant.get("playbook") or trade.get("playbook") or decision.get("playbook")),
        "entry_reason": label(decision.get("entry_reason") or decision.get("entry_trigger")),
        "exit_reason": label(decision.get("exit_reason") or decision.get("exit_trigger")),
    }


def aggregate_return_rows(rows: Sequence[Mapping[str, Any]], key: str, *, limit: int = 12) -> List[Dict[str, Any]]:
    grouped: Dict[str, List[float]] = defaultdict(list)
    for row in rows:
        name = label(row.get(key)) or "missing"
        pnl = row.get("pnl_pct")
        if isinstance(pnl, (int, float)):
            grouped[name].append(float(pnl))
    out: List[Dict[str, Any]] = []
    for name, values in grouped.items():
        if not values:
            continue
        wins = sum(1 for value in values if value > 0)
        out.append(
            {
                "name": name,
                "count": len(values),
                "win_count": wins,
                "loss_count": sum(1 for value in values if value < 0),
                "win_rate": round(wins / len(values), 4),
                "avg_return_pct": avg(values),
            }
        )
    out.sort(key=lambda row: (int(row["count"]), abs(float(row["avg_return_pct"]))), reverse=True)
    return out[:limit]


def daily_row_from_summary(day: str, payload: Mapping[str, Any]) -> Dict[str, Any]:
    metrics = _mapping(payload, "metrics")
    q = _mapping(payload, "quant_shadow_candidate_evaluation")
    gate = _mapping(q, "evaluation_trust_gate")
    rail = _mapping(payload, "market_regime_rail_review")
    return {
        "day": day,
        "trade_count": count(metrics.get("trade_count")),
        "closed_trade_count": count(metrics.get("closed_trade_count")),
        "return_sample_count": count(metrics.get("return_sample_count")),
        "unavailable_return_count": count(metrics.get("unavailable_return_count")),
        "win_rate": num(metrics.get("win_rate")) or 0.0,
        "avg_return_pct": num(metrics.get("avg_return_pct")) or 0.0,
        "truth_surface_count": count(metrics.get("truth_surface_count")),
        "shadow_candidate_count": count(q.get("candidate_count")),
        "shadow_deduped_candidate_count": count(q.get("deduped_candidate_count")),
        "shadow_duplicate_candidate_count": count(q.get("duplicate_candidate_count")),
        "shadow_evaluated_count": count(q.get("evaluated_count")),
        "shadow_would_enter_count": count(q.get("would_enter_count")),
        "shadow_forward_outcome_coverage": num(q.get("forward_outcome_coverage")),
        "q8_trust_gate_status": label(gate.get("status")),
        "q8_promotion_allowed": bool(gate.get("promotion_allowed")),
        "q8_trusted_forward_count": count(gate.get("trusted_forward_count")),
        "q8_trusted_forward_coverage": num(gate.get("trusted_forward_coverage")),
        "q8_duplicate_rate": num(gate.get("duplicate_rate")),
        "market_regime_rail": label(rail.get("rail_id") or rail.get("market_regime_rail")),
    }


def _named_counts(counter: Counter[str], limit: int) -> List[Dict[str, Any]]:
    return [{"name": name, "count": n} for name, n in counter.most_common(limit) if name]


class ShadowSummaryAggregator:
    """Folds daily ``daily_summary.json`` payloads into the historical shadow section."""

    def __init__(self) -> None:
        self.reason: Counter[str] = Counter()
        self.role: Counter[str] = Counter()
        self.tactic: Counter[str] = Counter()
        self.subtype: Counter[str] = Counter()
        self.subtype_v2: Counter[str] = Counter()
        self.subtype_forward: Dict[str, ForwardAccumulator] = defaultdict(ForwardAccumulator)
        self.subtype_forward_days: set[str] = set()
        self.groups: Dict[str, GroupAccumulator] = defaultdict(GroupAccumulator)
        self.q_days = 0
        self.q8_group_days = 0

    @staticmethod
    def _fold(counter: Counter[str], rows: Any) -> None:
        for row in list(rows or []):
            if isinstance(row, Mapping):
                counter[label(row.get("name"))] += count(row.get("count"))

    def add_day(self, day: str, payload: Mapping[str, Any]) -> None:
        q = _mapping(payload, "quant_shadow_candidate_evaluation")
        if q.get("candidate_count") is not None:
            self.q_days += 1
        self._fold(self.reason, q.get("by_reason"))
        self._fold(self.role, q.get("by_role"))
        self._fold(self.tactic, q.get("by_tactic_id"))
        below_vwap = q.get("below_vwap_reclaim_observation")
        below_vwap = below_vwap if isinstance(below_vwap, Mapping) else {}
        self._fold(self.subtype, below_vwap.get("by_subtype"))
        self._fold(self.subtype_v2, below_vwap.get("by_subtype_v2"))
        lane_forward = q.get("entry_lane_forward_outcomes")
        lane_forward = lane_forward if isinstance(lane_forward, Mapping) else {}
        for row in list(lane_forward.get("by_lane_subtype") or []):
            if not isinstance(row, Mapping):
                continue
            name = label(row.get("name"))
            if not name.startswith("vwap_reclaim:"):
                continue
            self.subtype_forward[name].add(row)
            self.subtype_forward_days.add(day)
        groups = list(_mapping(payload, "q8_shadow_blocker_review").get("groups") or [])
        if groups:
            self.q8_group_days += 1
        for row in groups:
            if not isinstance(row, Mapping):
                continue
            reason = label(row.get("reason") or row.get("name"))
            if reason:
                self.groups[reason].add(day, row)

    def needs_subtype_v2_fallback(self) -> bool:
        return not self.subtype_v2

    def add_subtype_v2_observation(self, observation: Mapping[str, Any]) -> None:
        if bool(observation.get("applies")):
            self.subtype_v2[label(observation.get("subtype_v2"))] += 1

    def finish(self, *, decide_subtype: Callable[[Mapping[str, Any]], str]) -> Dict[str, Any]:
        forward_rows = [
            acc.to_dict(name)
            for name, acc in sorted(
                self.subtype_forward.items(),
                key=lambda item: (item[1].candidate_count, item[0]),
                reverse=True,
            )
        ]
        for row in forward_rows:
            row["decision"] = decide_subtype(row)
        return {
            "q_shadow_day_count": self.q_days,
            "q8_group_day_count": self.q8_group_days,
            "by_reason": _named_counts(self.reason, 20),
            "by_role": _named_counts(self.role, 12),
            "by_tactic_id": _named_counts(self.tactic, 12),
            "below_vwap_reclaim_by_subtype": _named_counts(self.subtype, 12),
            "below_vwap_reclaim_by_subtype_v2": _named_counts(self.subtype_v2, 12),
            "below_vwap_reclaim_subtype_forward_day_count": len(self.subtype_forward_days),
            "below_vwap_reclaim_subtype_forward": forward_rows,
            "q8_blocker_groups": [
                acc.to_dict(reason)
                for reason, acc in sorted(self.groups.items(), key=lambda item: item[1].candidate_count, reverse=True)
            ],
        }


def pattern_rows(payloads: Iterable[Mapping[str, Any]], *, section: str, group_key: str) -> List[Dict[str, Any]]:
    grouped: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {
            "count": 0,
            "closed_or_realized_count": 0,
            "win_count": 0,
            "loss_count": 0,
            "flat_count": 0,
            "return_sum": 0.0,
            "return_weight": 0,
            "cost_drag_loss_count": 0,
        }
    )
    for payload in payloads:
        section_payload = _mapping(_mapping(payload, "pattern_performance"), section)
        rows = section_payload.get(group_key) if isinstance(section_payload.get(group_key), list) else []
        for row in rows:
            if not isinstance(row, Mapping):
                continue
            bucket = grouped[label(row.get("name")) or "missing"]
            n = count(row.get("count"))
            closed = count(row.get("closed_or_realized_count") or n)
            mean = num(row.get("avg_return_pct"))
            bucket["count"] += n
            bucket["closed_or_realized_count"] += closed
            bucket["win_count"] += count(row.get("win_count"))
            bucket["loss_count"] += count(row.get("loss_count"))
            bucket["flat_count"] += count(row.get("flat_count"))
            bucket["cost_drag_loss_count"] += count(row.get("cost_drag_loss_count"))
            if mean is not None and closed > 0:
                bucket["return_sum"] += float(mean) * closed
                bucket["return_weight"] += closed
    out: List[Dict[str, Any]] = []
    for name, bucket in grouped.items():
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
                "avg_return_pct": weighted_avg(float(bucket.get("return_sum") or 0.0), int(bucket.get("return_weight") or 0)),
                "cost_drag_loss_count": int(bucket.get("cost_drag_loss_count") or 0),
            }
        )
    out.sort(
        key=lambda row: (int(row.get("closed_or_realized_count") or 0), abs(float(row.get("avg_return_pct") or 0.0))),
        reverse=True,
    )
    return out


def assemble_historical_payload(
    *,
    start: str,
    end: str,
    daily_rows: Sequence[Mapping[str, Any]],
    trade_rows: Sequence[Mapping[str, Any]],
    shadow: Mapping[str, Any],
    pattern_by_tactic: Sequence[Mapping[str, Any]],
    pattern_by_exit: Sequence[Mapping[str, Any]],
    recommend: Callable[[Mapping[str, Any]], List[Dict[str, Any]]],
) -> Dict[str, Any]:
    return_rows = [row for row in trade_rows if isinstance(row.get("pnl_pct"), (int, float))]
    allowed_days = sum(1 for row in daily_rows if bool(row.get("q8_promotion_allowed")))
    payload: Dict[str, Any] = {
        "schema_version": "q8_historical_review.v1",
        "behavior_effect": "evaluation_only",
        "start": str(start)[:10],
        "end": str(end)[:10],
        "daily_count": len(daily_rows),
        "daily_rows": list(daily_rows),
        "q8_promotion_eligibility": {
            "promotion_allowed_day_count": allowed_days,
            "trusted_gate_day_count": sum(1 for row in daily_rows if label(row.get("q8_trust_gate_status"))),
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
            "avg_return_pct": avg([float(row["pnl_pct"]) for row in return_rows]),
            "win_rate": round(sum(1 for row in return_rows if float(row["pnl_pct"]) > 0) / len(return_rows), 4)
            if return_rows
            else 0.0,
            "truth_sources": [
                {"name": name, "count": n}
                for name, n in Counter(label(row.get("truth_source")) or "missing" for row in trade_rows).most_common(12)
            ],
        },
        "trade_by_tactic": list(pattern_by_tactic) or aggregate_return_rows(return_rows, "tactic"),
        "trade_by_entry_reason": aggregate_return_rows(return_rows, "entry_reason"),
        "trade_by_exit_reason": list(pattern_by_exit) or aggregate_return_rows(return_rows, "exit_reason"),
        **shadow,
    }
    if allowed_days <= 0:
        payload["promotion_recommendations"] = [
            {
                "candidate": "all_q8_candidates",
                "decision": "retain_under_observation",
                "reason": "no historical day passed the Q8 evaluation trust gate",
            }
        ]
    else:
        payload["promotion_recommendations"] = recommend(payload)
    return payload


# --- A2: shadow blocker group rollups ---------------------------------------


def _strict_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except Exception:
        return None


def checkpoint_values(outcome: Mapping[str, Any]) -> Dict[str, Any]:
    checkpoints = outcome.get("checkpoints") if isinstance(outcome.get("checkpoints"), Mapping) else {}
    observed = [
        checkpoint
        for checkpoint in checkpoints.values()
        if isinstance(checkpoint, Mapping) and str(checkpoint.get("status") or "") == "observed"
    ]
    if not observed:
        return {"available": False}
    returns = [v for v in (_strict_float(row.get("return_pct")) for row in observed) if v is not None]
    mfes = [v for v in (_strict_float(row.get("mfe_pct")) for row in observed) if v is not None]
    maes = [v for v in (_strict_float(row.get("mae_pct")) for row in observed) if v is not None]
    return {
        "available": True,
        "latest_return_pct": returns[-1] if returns else None,
        "max_favorable_pct": max(mfes) if mfes else None,
        "max_adverse_pct": min(maes) if maes else None,
    }


def _outcome(row: Mapping[str, Any]) -> Mapping[str, Any]:
    outcome = row.get("shadow_forward_outcome")
    return outcome if isinstance(outcome, Mapping) else {}


def summarize_blocker_group(
    reason: str,
    rows: Sequence[Mapping[str, Any]],
    *,
    promotion_allowed: bool,
    decide: Callable[[Mapping[str, Any]], str],
) -> Dict[str, Any]:
    observed_rows: List[Dict[str, Any]] = []
    for row in rows:
        values = checkpoint_values(_outcome(row))
        if values.get("available"):
            observed_rows.append({**dict(row), "_q8_forward": values})

    def _series(key: str) -> List[float]:
        return [float(r["_q8_forward"][key]) for r in observed_rows if r["_q8_forward"].get(key) is not None]

    latest_returns = _series("latest_return_pct")
    mfes = _series("max_favorable_pct")
    maes = _series("max_adverse_pct")
    positive_count = sum(1 for value in latest_returns if value > 0)
    missed_count = sum(1 for value in mfes if value >= 1.0)
    adverse_count = sum(1 for value in maes if value <= -0.5)
    examples = sorted(
        observed_rows,
        key=lambda r: float(r["_q8_forward"].get("max_favorable_pct") or 0.0),
        reverse=True,
    )[:5]
    raw_decision = decide(rows[0]) if rows else "retain_under_observation"
    decision = raw_decision if promotion_allowed else "retain_under_observation"
    return {
        "reason": reason,
        "candidate_count": len(rows),
        "observed_count": len(observed_rows),
        "coverage": round(float(len(observed_rows)) / float(len(rows)), 4) if rows else 0.0,
        "avg_latest_return_pct": avg(latest_returns),
        "avg_max_favorable_pct": avg(mfes),
        "avg_max_adverse_pct": avg(maes),
        "positive_latest_count": positive_count,
        "positive_latest_rate": round(float(positive_count) / float(len(latest_returns)), 4) if latest_returns else 0.0,
        "missed_opportunity_count": missed_count,
        "missed_opportunity_rate": round(float(missed_count) / float(len(mfes)), 4) if mfes else 0.0,
        "adverse_count": adverse_count,
        "adverse_rate": round(float(adverse_count) / float(len(maes)), 4) if maes else 0.0,
        "raw_decision": raw_decision,
        "decision": decision,
        "decision_blocked_by_trust_gate": bool(raw_decision != decision),
        "examples": [
            {
                "symbol": str(r.get("symbol") or "").strip(),
                "role": str(r.get("shadow_role") or "").strip(),
                "rank": r.get("rank"),
                "tactic_id": str(r.get("quant_tactic_id") or "").strip(),
                "latest_return_pct": r["_q8_forward"].get("latest_return_pct"),
                "max_favorable_pct": r["_q8_forward"].get("max_favorable_pct"),
                "max_adverse_pct": r["_q8_forward"].get("max_adverse_pct"),
            }
            for r in examples
        ],
    }


def trusted_forward_count(rows: Sequence[Mapping[str, Any]], *, truthy: Callable[[Any], bool]) -> int:
    return sum(1 for row in rows if truthy(checkpoint_values(_outcome(row)).get("available")))


def group_blocker_rows(
    rows: Sequence[Mapping[str, Any]],
    review_reasons: Sequence[str],
    *,
    promotion_allowed: bool,
    decide: Callable[[Mapping[str, Any]], str],
) -> List[Dict[str, Any]]:
    wanted = {str(reason) for reason in review_reasons}
    grouped: Dict[str, List[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        reason = str(row.get("reason") or "").strip()
        if reason in wanted:
            grouped[reason].append(row)
    return [
        summarize_blocker_group(reason, grouped.get(reason, []), promotion_allowed=promotion_allowed, decide=decide)
        for reason in review_reasons
    ]


# --- A3: trusted reaggregation readouts --------------------------------------


def watchlist_rows(scorecard: Mapping[str, Any]) -> List[Dict[str, Any]]:
    return [dict(row) for row in list(scorecard.get("promotion_watchlist") or []) if isinstance(row, Mapping)]


def _section(evaluation: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = evaluation.get(key)
    return value if isinstance(value, Mapping) else {}


def reaggregation_day_row(day: str, evaluation: Mapping[str, Any]) -> Dict[str, Any]:
    scorecard = _section(evaluation, "no_trade_scorecard")
    trust_gate = _section(evaluation, "evaluation_trust_gate")
    return {
        "day": day,
        "payload_count": int(evaluation.get("payload_count") or 0),
        "candidate_count": int(evaluation.get("candidate_count") or 0),
        "deduped_candidate_count": int(evaluation.get("deduped_candidate_count") or 0),
        "duplicate_candidate_count": int(evaluation.get("duplicate_candidate_count") or 0),
        "duplicate_rate": float(trust_gate.get("duplicate_rate") or 0.0),
        "trusted_forward_count": int(evaluation.get("forward_outcome_available_count") or 0),
        "trusted_forward_coverage": float(evaluation.get("forward_outcome_coverage") or 0.0),
        "scorecard_status": scorecard.get("status") or "not_available",
        "trust_gate_status": trust_gate.get("status") or "not_available",
        "promotion_allowed": bool(trust_gate.get("promotion_allowed")),
        "trust_reasons": list(trust_gate.get("block_reasons") or trust_gate.get("reasons") or []),
        "promotion_watchlist": watchlist_rows(scorecard),
    }


def reaggregation_aggregate(cumulative_evaluation: Mapping[str, Any], *, promotion_allowed_day_count: int) -> Dict[str, Any]:
    scorecard = _section(cumulative_evaluation, "no_trade_scorecard")
    trust_gate = _section(cumulative_evaluation, "evaluation_trust_gate")
    return {
        "candidate_count": int(cumulative_evaluation.get("candidate_count") or 0),
        "deduped_candidate_count": int(cumulative_evaluation.get("deduped_candidate_count") or 0),
        "duplicate_candidate_count": int(cumulative_evaluation.get("duplicate_candidate_count") or 0),
        "duplicate_rate": float(trust_gate.get("duplicate_rate") or 0.0),
        "forward_outcome_available_count": int(cumulative_evaluation.get("forward_outcome_available_count") or 0),
        "trusted_forward_coverage": float(cumulative_evaluation.get("forward_outcome_coverage") or 0.0),
        "promotion_allowed_day_count": promotion_allowed_day_count,
        "cumulative_trust_gate_status": trust_gate.get("status") or "not_available",
        "cumulative_promotion_allowed": bool(trust_gate.get("promotion_allowed")),
        "cumulative_trust_reasons": list(trust_gate.get("block_reasons") or trust_gate.get("reasons") or []),
        "promotion_watchlist": watchlist_rows(scorecard),
    }


# --- A4: lane decision table rows -------------------------------------------


def _lane_float(value: Any) -> float:
    try:
        return 0.0 if value in (None, "") else float(value)
    except Exception:
        return 0.0


def _lane_int(value: Any) -> int:
    try:
        return 0 if value in (None, "") else int(float(value))
    except Exception:
        return 0


def lane_rows(value: Any) -> List[Dict[str, Any]]:
    return [dict(row) for row in list(value or []) if isinstance(row, Mapping)]


def lane_counts_by_name(rows: Iterable[Mapping[str, Any]]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for row in rows:
        name = str(row.get("name") or "").strip()
        if name:
            out[name] = _lane_int(row.get("count"))
    return out


def lane_reason_summary(evaluation: Mapping[str, Any], *, limit: int = 6) -> str:
    parts = []
    for row in lane_rows(evaluation.get("by_reason"))[:limit]:
        name = str(row.get("name") or "").strip()
        if name:
            parts.append(f"{name} {row.get('count') or 0}")
    return ", ".join(parts) if parts else "-"


LANE_VERDICT_ORDER = {
    "TRUST_GATE_BLOCKED": 0,
    "MISSED_OPPORTUNITY": 1,
    "BAD_ENTRY": 2,
    "GOOD_BLOCK": 3,
    "DATA_INCOMPLETE": 4,
}

_LANE_FORWARD_KEYS = (
    "avg_return_3m_pct",
    "avg_return_5m_pct",
    "avg_return_15m_pct",
    "avg_return_30m_pct",
    "avg_return_60m_pct",
    "avg_mfe_5m_pct",
    "avg_mae_5m_pct",
)


def lane_decision_rows(
    evaluation: Mapping[str, Any],
    *,
    promotion_allowed: bool,
    verdict: Callable[..., Dict[str, str]],
) -> List[Dict[str, Any]]:
    observation = evaluation.get("entry_lane_observation")
    counts = lane_counts_by_name(lane_rows(observation.get("by_primary_lane") if isinstance(observation, Mapping) else []))
    forward = evaluation.get("entry_lane_forward_outcomes")
    forward_rows = lane_rows(forward.get("by_primary_lane")) if isinstance(forward, Mapping) else []
    rows: List[Dict[str, Any]] = []
    for row in forward_rows:
        decided = verdict(row, promotion_allowed=promotion_allowed)
        lane = str(row.get("name") or "").strip()
        rows.append(
            {
                "lane": lane,
                "candidate_count": _lane_int(row.get("candidate_count")),
                "observed_count": _lane_int(row.get("observed_count")),
                "coverage": round(_lane_float(row.get("coverage")), 4),
                "shadow_count": counts.get(lane, _lane_int(row.get("candidate_count"))),
                **{key: row.get(key) for key in _LANE_FORWARD_KEYS},
                **decided,
            }
        )
    rows.sort(key=lambda item: (LANE_VERDICT_ORDER.get(str(item.get("verdict")), 9), -_lane_int(item.get("observed_count"))))
    return rows


def lane_table_payload(
    evaluation: Mapping[str, Any],
    *,
    day: str,
    verdict: Callable[..., Dict[str, str]],
) -> Dict[str, Any]:
    trust_gate = _section(evaluation, "evaluation_trust_gate")
    promotion_allowed = bool(trust_gate.get("promotion_allowed"))
    rows = lane_decision_rows(evaluation, promotion_allowed=promotion_allowed, verdict=verdict)
    return {
        "schema_version": "q8_lane_decision_table.v1",
        "day": str(day)[:10],
        "payload_count": _lane_int(evaluation.get("payload_count")),
        "candidate_count": _lane_int(evaluation.get("candidate_count")),
        "deduped_candidate_count": _lane_int(evaluation.get("deduped_candidate_count")),
        "duplicate_candidate_count": _lane_int(evaluation.get("duplicate_candidate_count")),
        "dedupe_key": list(evaluation.get("dedupe_key") or []),
        "evaluated_count": _lane_int(evaluation.get("evaluated_count")),
        "forward_outcome_available_count": _lane_int(evaluation.get("forward_outcome_available_count")),
        "forward_outcome_coverage": round(_lane_float(evaluation.get("forward_outcome_coverage")), 4),
        "evaluation_trust_gate": dict(trust_gate),
        "promotion_allowed": promotion_allowed,
        "would_enter_count": _lane_int(evaluation.get("would_enter_count")),
        "reason_summary": lane_reason_summary(evaluation),
        "rows": rows,
    }
