"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence


def _scorecard_rows(rows: Sequence[Mapping[str, Any]], *, mode: str, limit: int = 5, facade: Any) -> List[Dict[str, Any]]:
    selected: List[Dict[str, Any]] = []
    for row in rows:
        observed = int(row.get("observed_count") or 0)
        if observed < 10:
            continue
        signal = facade._scorecard_return_signal(row)
        if signal is None:
            continue
        mfe5 = row.get("avg_mfe_5m_pct")
        mae5 = row.get("avg_mae_5m_pct")
        try:
            mfe5_f = float(mfe5) if mfe5 not in (None, "") else None
        except Exception:
            mfe5_f = None
        try:
            mae5_f = float(mae5) if mae5 not in (None, "") else None
        except Exception:
            mae5_f = None

        if mode == "missed":
            if signal < 0.10 and not (mfe5_f is not None and mfe5_f >= 0.45 and (mae5_f is None or mae5_f > -0.80)):
                continue
            if mae5_f is not None and mae5_f <= -1.25:
                continue
        elif mode == "blocked":
            if signal > -0.05 and not (mae5_f is not None and mae5_f <= -0.75 and signal <= 0.05):
                continue
        else:
            continue

        selected.append(
            {
                "name": facade._text(row.get("name")),
                "candidate_count": int(row.get("candidate_count") or 0),
                "observed_count": observed,
                "observed_day_count": int(row.get("observed_day_count") or 0),
                "sample_concentration": row.get("sample_concentration"),
                "avg_return_5m_pct": row.get("avg_return_5m_pct"),
                "avg_return_15m_pct": row.get("avg_return_15m_pct"),
                "avg_mfe_5m_pct": row.get("avg_mfe_5m_pct"),
                "avg_mae_5m_pct": row.get("avg_mae_5m_pct"),
                "scorecard_signal_pct": round(signal, 4),
            }
        )

    selected.sort(
        key=lambda item: (
            float(item.get("scorecard_signal_pct") or 0.0),
            int(item.get("observed_count") or 0),
        ),
        reverse=(mode == "missed"),
    )
    return selected[:limit]
