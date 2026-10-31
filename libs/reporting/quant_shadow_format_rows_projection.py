"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, List, Mapping, Sequence


def _format_rows(rows: Sequence[Mapping[str, Any]], *, limit: int = 4, facade: Any) -> str:
    parts: List[str] = []
    for row in list(rows)[:limit]:
        name = facade._text(row.get("name"))
        if not name:
            continue
        parts.append(f"{name} ({row.get('count') or 0})")
    return ", ".join(parts) if parts else "none"
