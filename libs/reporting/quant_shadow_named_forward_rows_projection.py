"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence


def _named_forward_rows(rows: Sequence[Mapping[str, Any]], names: set[str], *, facade: Any) -> List[Dict[str, Any]]:
    by_name = {str(row.get("name") or ""): row for row in rows}
    selected: List[Dict[str, Any]] = []
    for name in sorted(names):
        row = by_name.get(name)
        if not isinstance(row, facade.Mapping):
            continue
        observed_count = int(row.get("observed_count") or 0)
        ret5 = row.get("avg_return_5m_pct")
        ret15 = row.get("avg_return_15m_pct")
        try:
            ret5_f = float(ret5) if ret5 not in (None, "") else None
        except Exception:
            ret5_f = None
        try:
            ret15_f = float(ret15) if ret15 not in (None, "") else None
        except Exception:
            ret15_f = None
        if observed_count < 20:
            review_state = "sample_insufficient"
        elif int(row.get("observed_day_count") or 0) < 2:
            review_state = "sample_concentrated_single_day"
        elif ret15_f is not None and ret15_f <= 0:
            review_state = "observe_only_negative_15m"
        elif ret5_f is not None and ret5_f <= 0:
            review_state = "observe_only_negative_5m"
        elif observed_count < facade.PROMOTION_CANDIDATE_MIN_OBSERVED:
            review_state = "sample_insufficient"
        else:
            review_state = "promotion_watch"
        selected.append(
            {
                "name": name,
                "candidate_count": int(row.get("candidate_count") or 0),
                "observed_count": observed_count,
                "observed_day_count": int(row.get("observed_day_count") or 0),
                "sample_concentration": row.get("sample_concentration"),
                "avg_return_5m_pct": row.get("avg_return_5m_pct"),
                "avg_return_15m_pct": row.get("avg_return_15m_pct"),
                "avg_mfe_5m_pct": row.get("avg_mfe_5m_pct"),
                "avg_mae_5m_pct": row.get("avg_mae_5m_pct"),
                "review_state": review_state,
            }
        )
    return selected
