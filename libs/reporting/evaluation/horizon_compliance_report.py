from __future__ import annotations

from collections import Counter
from typing import Any, Mapping, Sequence

from . import fast08_cumulative_projection as _cp


_mapping = _cp.mapping
_num = _cp.number
_bucket_key = _cp.horizon_bucket_key


def build_horizon_compliance_report(
    evaluations: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    keyed: list[tuple[tuple[str, str], dict[str, Any]]] = []
    horizon_counts: Counter[str] = Counter()
    excluded_count = 0
    exit_incident_excluded_count = 0
    for evaluation in evaluations:
        integrity = _mapping(evaluation.get("integrity"))
        if integrity.get("promotion_metric_eligible") is False:
            excluded_count += 1
            continue
        if integrity.get("exit_metric_eligible") is False:
            exit_incident_excluded_count += 1
            continue
        row = _cp.horizon_compliance_row(evaluation)
        rows.append(row)
        horizon_counts[row["strategy_horizon"]] += 1
        keyed.append((_bucket_key(evaluation), row))
    group_rows = _cp.horizon_group_rows(keyed)

    return {
        "schema_version": "horizon_compliance_report.v1",
        "behavior_effect": "observation_only",
        "trade_count": len(rows),
        "excluded_trade_count": excluded_count,
        "exit_incident_excluded_trade_count": exit_incident_excluded_count,
        "horizon_counts": dict(horizon_counts),
        "group_rows": group_rows,
        "rows": rows,
        "policy_warning": (
            "Do not convert this into delayed exits directly. Promotion requires "
            "target-hold improvement by horizon and exit reason."
        ),
    }


render_horizon_compliance_report = _cp.render_horizon_compliance_report


__all__ = ["build_horizon_compliance_report", "render_horizon_compliance_report"]
