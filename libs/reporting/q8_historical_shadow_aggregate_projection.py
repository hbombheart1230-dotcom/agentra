"""q8_historical_review projections (moved verbatim from q8_historical_review).

Module globals and helpers are resolved on ``facade`` (the q8_historical_review module) at call time; this module never imports it.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Dict, Mapping


def _aggregate_shadow_summaries(reports_root: Path, *, start: str, end: str, facade: Any) -> Dict[str, Any]:
    reason_counter: Counter[str] = facade.Counter()
    role_counter: Counter[str] = facade.Counter()
    tactic_counter: Counter[str] = facade.Counter()
    below_vwap_subtype_counter: Counter[str] = facade.Counter()
    below_vwap_subtype_v2_counter: Counter[str] = facade.Counter()
    vwap_reclaim_subtype_forward: Dict[str, Any] = facade.defaultdict(facade.ForwardAccumulator)
    vwap_reclaim_subtype_forward_days: set[str] = set()
    group_acc: Dict[str, Any] = facade.defaultdict(facade.GroupAccumulator)
    q_days = 0
    q8_group_days = 0
    for day in facade._iter_days(start, end):
        path = reports_root / "operator_summary" / "daily" / day / "daily_summary.json"
        if not path.exists():
            continue
        payload = facade._read_json(path)
        q = payload.get("quant_shadow_candidate_evaluation") if isinstance(payload.get("quant_shadow_candidate_evaluation"), dict) else {}
        if q.get("candidate_count") is not None:
            q_days += 1
        for row in list(q.get("by_reason") or []):
            if isinstance(row, Mapping):
                reason_counter[facade._text(row.get("name"))] += facade._int(row.get("count"))
        for row in list(q.get("by_role") or []):
            if isinstance(row, Mapping):
                role_counter[facade._text(row.get("name"))] += facade._int(row.get("count"))
        for row in list(q.get("by_tactic_id") or []):
            if isinstance(row, Mapping):
                tactic_counter[facade._text(row.get("name"))] += facade._int(row.get("count"))
        below_vwap = (
            q.get("below_vwap_reclaim_observation")
            if isinstance(q.get("below_vwap_reclaim_observation"), Mapping)
            else {}
        )
        for row in list(below_vwap.get("by_subtype") or []):
            if isinstance(row, Mapping):
                below_vwap_subtype_counter[facade._text(row.get("name"))] += facade._int(row.get("count"))
        for row in list(below_vwap.get("by_subtype_v2") or []):
            if isinstance(row, Mapping):
                below_vwap_subtype_v2_counter[facade._text(row.get("name"))] += facade._int(row.get("count"))
        lane_forward = (
            q.get("entry_lane_forward_outcomes")
            if isinstance(q.get("entry_lane_forward_outcomes"), Mapping)
            else {}
        )
        for row in list(lane_forward.get("by_lane_subtype") or []):
            if not isinstance(row, Mapping):
                continue
            name = facade._text(row.get("name"))
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
            reason = facade._text(row.get("reason") or row.get("name"))
            if not reason:
                continue
            group_acc[reason].add(day, row)
    if not below_vwap_subtype_v2_counter:
        for row in facade._iter_quant_shadow_candidate_rows(reports_root, start=start, end=end):
            observation = facade.classify_below_vwap_reclaim_observation(row)
            if not bool(observation.get("applies")):
                continue
            below_vwap_subtype_v2_counter[facade._text(observation.get("subtype_v2"))] += 1
    subtype_forward_rows = [
        acc.to_dict(name)
        for name, acc in sorted(
            vwap_reclaim_subtype_forward.items(),
            key=lambda item: (item[1].candidate_count, item[0]),
            reverse=True,
        )
    ]
    for row in subtype_forward_rows:
        row["decision"] = facade._decision_for_reclaim_subtype(row)
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
