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
    reason_counter: Counter[str] = Counter()
    role_counter: Counter[str] = Counter()
    tactic_counter: Counter[str] = Counter()
    below_vwap_subtype_counter: Counter[str] = Counter()
    below_vwap_subtype_v2_counter: Counter[str] = Counter()
    vwap_reclaim_subtype_forward: Dict[str, ForwardAccumulator] = defaultdict(ForwardAccumulator)
    vwap_reclaim_subtype_forward_days: set[str] = set()
    group_acc: Dict[str, GroupAccumulator] = defaultdict(GroupAccumulator)
    q_days = 0
    q8_group_days = 0
    for day in _iter_days(start, end):
        path = reports_root / "operator_summary" / "daily" / day / "daily_summary.json"
        if not path.exists():
            continue
        payload = _read_json(path)
        q = payload.get("quant_shadow_candidate_evaluation") if isinstance(payload.get("quant_shadow_candidate_evaluation"), dict) else {}
        if q.get("candidate_count") is not None:
            q_days += 1
        for row in list(q.get("by_reason") or []):
            if isinstance(row, Mapping):
                reason_counter[_text(row.get("name"))] += _int(row.get("count"))
        for row in list(q.get("by_role") or []):
            if isinstance(row, Mapping):
                role_counter[_text(row.get("name"))] += _int(row.get("count"))
        for row in list(q.get("by_tactic_id") or []):
            if isinstance(row, Mapping):
                tactic_counter[_text(row.get("name"))] += _int(row.get("count"))
        below_vwap = (
            q.get("below_vwap_reclaim_observation")
            if isinstance(q.get("below_vwap_reclaim_observation"), Mapping)
            else {}
        )
        for row in list(below_vwap.get("by_subtype") or []):
            if isinstance(row, Mapping):
                below_vwap_subtype_counter[_text(row.get("name"))] += _int(row.get("count"))
        for row in list(below_vwap.get("by_subtype_v2") or []):
            if isinstance(row, Mapping):
                below_vwap_subtype_v2_counter[_text(row.get("name"))] += _int(row.get("count"))
        lane_forward = (
            q.get("entry_lane_forward_outcomes")
            if isinstance(q.get("entry_lane_forward_outcomes"), Mapping)
            else {}
        )
        for row in list(lane_forward.get("by_lane_subtype") or []):
            if not isinstance(row, Mapping):
                continue
            name = _text(row.get("name"))
            if not name.startswith("vwap_reclaim:"):
                continue
            vwap_reclaim_subtype_forward[name].add(row)
            vwap_reclaim_subtype_forward_days.add(day)
        q8 = payload.get("q8_shadow_blocker_review") if isinstance(payload.get("q8_shadow_blocker_review"), dict) else {}
        groups = list(q8.get("groups") or [])
        if groups:
            q8_group_days += 1
        for row in groups:
            if not isinstance(row, Mapping):
                continue
            reason = _text(row.get("reason") or row.get("name"))
            if not reason:
                continue
            group_acc[reason].add(day, row)
    if not below_vwap_subtype_v2_counter:
        for row in _iter_quant_shadow_candidate_rows(reports_root, start=start, end=end):
            observation = classify_below_vwap_reclaim_observation(row)
            if not bool(observation.get("applies")):
                continue
            below_vwap_subtype_v2_counter[_text(observation.get("subtype_v2"))] += 1
    subtype_forward_rows = [
        acc.to_dict(name)
        for name, acc in sorted(
            vwap_reclaim_subtype_forward.items(),
            key=lambda item: (item[1].candidate_count, item[0]),
            reverse=True,
        )
    ]
    for row in subtype_forward_rows:
        row["decision"] = _decision_for_reclaim_subtype(row)
    return {
        "q_shadow_day_count": q_days,
        "q8_group_day_count": q8_group_days,
        "by_reason": [{"name": name, "count": count} for name, count in reason_counter.most_common(20) if name],
        "by_role": [{"name": name, "count": count} for name, count in role_counter.most_common(12) if name],
        "by_tactic_id": [{"name": name, "count": count} for name, count in tactic_counter.most_common(12) if name],
        "below_vwap_reclaim_by_subtype": [
            {"name": name, "count": count}
            for name, count in below_vwap_subtype_counter.most_common(12)
            if name
        ],
        "below_vwap_reclaim_by_subtype_v2": [
            {"name": name, "count": count}
            for name, count in below_vwap_subtype_v2_counter.most_common(12)
            if name
        ],
        "below_vwap_reclaim_subtype_forward_day_count": len(vwap_reclaim_subtype_forward_days),
        "below_vwap_reclaim_subtype_forward": subtype_forward_rows,
        "q8_blocker_groups": [
            acc.to_dict(reason)
            for reason, acc in sorted(group_acc.items(), key=lambda item: item[1].candidate_count, reverse=True)
        ],
    }


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


def _md_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> List[str]:
    return _table_owner._md_table(headers, rows)


def render_q8_historical_review_markdown(payload: Mapping[str, Any]) -> str:
    trade = payload.get("trade_summary") if isinstance(payload.get("trade_summary"), Mapping) else {}
    lines: List[str] = [
        f"# Q8 Historical Review: {payload.get('start')} to {payload.get('end')}",
        "",
        "Purpose: reuse prior live and shadow evidence without mixing incompatible artifact eras.",
        "",
        "This review is evaluation-only. It does not change entry, exit, scanner, Strategist, or execution behavior.",
        "",
        "## Data Windows",
        "",
        "- Live trade performance: usable from 2026-05-18 onward when truth-surface PnL exists.",
        "- Q8 shadow evaluation: most useful from 2026-05-26 onward when candidate shadow summaries are populated.",
        "- Market regime rail: most useful from 2026-06-02 onward when rail IDs are attached to daily summaries.",
        "- Broker truth reconciliation: strongest from 2026-06-08 onward after post-close order-pair repair.",
        "",
        "## Live Trade Summary",
        "",
        f"- Trade report files: **{trade.get('trade_report_count', 0)}**",
        f"- Return samples: **{trade.get('return_sample_count', 0)}**",
        f"- Win rate: **{float(trade.get('win_rate') or 0.0) * 100:.2f}%**",
        f"- Average return: **{float(trade.get('avg_return_pct') or 0.0):.4f}%**",
        "",
    ]
    daily_rows = list(payload.get("daily_rows") or [])
    if daily_rows:
        lines.extend(
            _md_table(
                ["Day", "Trades", "Closed", "Returns", "Missing", "Win", "Avg", "Raw", "Deduped", "Trusted", "Gate", "Allowed", "Rail"],
                [
                    [
                        row.get("day"),
                        row.get("trade_count"),
                        row.get("closed_trade_count"),
                        row.get("return_sample_count"),
                        row.get("unavailable_return_count"),
                        f"{float(row.get('win_rate') or 0.0) * 100:.1f}%",
                        f"{float(row.get('avg_return_pct') or 0.0):.2f}%",
                        row.get("shadow_candidate_count") or 0,
                        row.get("shadow_deduped_candidate_count") or 0,
                        row.get("q8_trusted_forward_count") or 0,
                        row.get("q8_trust_gate_status") or "legacy/no_gate",
                        bool(row.get("q8_promotion_allowed")),
                        row.get("market_regime_rail") or "-",
                    ]
                    for row in daily_rows
                ],
            )
        )
        lines.append("")
    eligibility = payload.get("q8_promotion_eligibility") if isinstance(payload.get("q8_promotion_eligibility"), Mapping) else {}
    lines.extend(
        [
            "## Q8 Promotion Eligibility",
            "",
            f"- status: `{eligibility.get('status') or 'unknown'}`",
            f"- trusted gate days: **{eligibility.get('trusted_gate_day_count') or 0}**",
            f"- promotion allowed days: **{eligibility.get('promotion_allowed_day_count') or 0}**",
            f"- rule: {eligibility.get('rule') or '-'}",
            "",
        ]
    )
    lines.extend(["## Trade Pattern Evidence", ""])
    for title, key in (
        ("By Tactic", "trade_by_tactic"),
        ("By Entry Reason", "trade_by_entry_reason"),
        ("By Exit Reason", "trade_by_exit_reason"),
    ):
        rows = list(payload.get(key) or [])
        lines.extend([f"### {title}", ""])
        lines.extend(
            _md_table(
                ["Name", "Count", "Win", "Avg"],
                [
                    [
                        row.get("name"),
                        row.get("count"),
                        f"{float(row.get('win_rate') or 0.0) * 100:.1f}%",
                        f"{float(row.get('avg_return_pct') or 0.0):.3f}%",
                    ]
                    for row in rows[:10]
                ],
            )
        )
        lines.append("")
    lines.extend(
        [
            "## Q8 Shadow Summary",
            "",
            f"- Q8 shadow summary days: **{payload.get('q_shadow_day_count', 0)}**",
            f"- Q8 blocker forward-review days: **{payload.get('q8_group_day_count', 0)}**",
            "",
            "### Top Shadow Reasons",
            "",
        ]
    )
    lines.extend(
        _md_table(
            ["Reason", "Count"],
            [[row.get("name"), row.get("count")] for row in list(payload.get("by_reason") or [])[:15]],
        )
    )
    lines.extend(["", "### Forward Blocker Review", ""])
    lines.extend(
        _md_table(
            ["Reason", "n", "obs", "Latest", "MFE", "MAE", "Missed", "Adverse", "Decision"],
            [
                [
                    row.get("reason"),
                    row.get("candidate_count"),
                    row.get("observed_count"),
                    f"{float(row.get('avg_latest_return_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_max_favorable_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_max_adverse_pct') or 0.0):.4f}%",
                    f"{float(row.get('missed_opportunity_rate') or 0.0) * 100:.1f}%",
                    f"{float(row.get('adverse_rate') or 0.0) * 100:.1f}%",
                    row.get("dominant_decision") or "-",
                ]
                for row in list(payload.get("q8_blocker_groups") or [])[:10]
            ],
        )
    )
    subtype_rows = list(payload.get("below_vwap_reclaim_by_subtype") or [])
    subtype_v2_rows = list(payload.get("below_vwap_reclaim_by_subtype_v2") or [])
    subtype_forward_rows = list(payload.get("below_vwap_reclaim_subtype_forward") or [])
    lines.extend(
        [
            "",
            "## Below-VWAP Reclaim Subtype Review",
            "",
            f"- Subtype count days: **{payload.get('q_shadow_day_count', 0)}**",
            f"- Subtype forward days: **{payload.get('below_vwap_reclaim_subtype_forward_day_count', 0)}**",
            "- Note: subtype forward evidence is available only after the entry-lane observation fields were added.",
            "",
            "### Subtype Counts",
            "",
        ]
    )
    lines.extend(
        _md_table(
            ["Subtype", "Count"],
            [[row.get("name"), row.get("count")] for row in subtype_rows[:10]],
        )
    )
    lines.extend(["", "### Subtype V2 Counts", ""])
    lines.extend(
        _md_table(
            ["Subtype V2", "Count"],
            [[row.get("name"), row.get("count")] for row in subtype_v2_rows[:12]],
        )
    )
    lines.extend(["", "### Subtype Forward Outcomes", ""])
    lines.extend(
        _md_table(
            ["Subtype", "n", "obs", "3m", "5m", "15m", "30m", "60m", "MFE5", "MAE5", "Decision"],
            [
                [
                    row.get("name"),
                    row.get("candidate_count"),
                    row.get("observed_count"),
                    f"{float(row.get('avg_return_3m_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_return_5m_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_return_15m_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_return_30m_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_return_60m_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_mfe_5m_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_mae_5m_pct') or 0.0):.4f}%",
                    row.get("decision") or "-",
                ]
                for row in subtype_forward_rows[:10]
            ],
        )
    )
    lines.extend(["", "## Recommendations", ""])
    lines.extend(
        _md_table(
            ["Candidate", "Decision", "Evidence"],
            [
                [
                    row.get("candidate"),
                    row.get("decision"),
                    row.get("reason")
                    or (
                        f"n={row.get('candidate_count')}, obs={row.get('observed_count')}, "
                        f"latest={float(row.get('avg_latest_return_pct') or 0.0):.4f}%, "
                        f"missed={float(row.get('missed_opportunity_rate') or 0.0) * 100:.1f}%, "
                        f"adverse={float(row.get('adverse_rate') or 0.0) * 100:.1f}%"
                    ),
                ]
                for row in list(payload.get("promotion_recommendations") or [])
            ],
        )
    )
    lines.extend(
        [
            "",
            "## Operator Conclusion",
            "",
            "- Prior data is useful, but it must be sliced by artifact era.",
            "- Live trade PnL already shows persistent negative expectancy in stop/trend-break/low-break exits.",
            "- Q8 shadow raw sample size alone is not promotion evidence.",
            "- Promotion review requires trusted same-day forward outcomes, canonical dedupe, and evaluation_trust_gate.promotion_allowed=true.",
            "- Historical reports generated before the trust gate are legacy observation material, not policy-promotion evidence.",
            "",
        ]
    )
    return "\n".join(lines)


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
