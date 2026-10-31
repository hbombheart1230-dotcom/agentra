"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, List, Mapping, Sequence


def _format_forward_rows(rows: Sequence[Mapping[str, Any]], *, limit: int = 4, facade: Any) -> str:
    parts: List[str] = []
    for row in list(rows)[:limit]:
        name = facade._text(row.get("name"))
        if not name:
            continue
        observed = int(row.get("observed_count") or 0)
        count = int(row.get("candidate_count") or 0)
        ret5 = row.get("avg_return_5m_pct")
        ret15 = row.get("avg_return_15m_pct")
        mfe5 = row.get("avg_mfe_5m_pct")
        mae5 = row.get("avg_mae_5m_pct")
        parts.append(
            f"{name} ({observed}/{count}, "
            f"+5m {float(ret5):.4f}%"
            if ret5 is not None
            else f"{name} ({observed}/{count}, +5m n/a"
        )
        if parts:
            last = parts[-1]
            if ret15 is not None:
                last += f", +15m {float(ret15):.4f}%"
            if mfe5 is not None:
                last += f", mfe5 {float(mfe5):.4f}%"
            if mae5 is not None:
                last += f", mae5 {float(mae5):.4f}%"
            parts[-1] = last + ")"
    return "; ".join(parts) if parts else "none"
