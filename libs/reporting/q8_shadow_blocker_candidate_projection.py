"""q8_shadow_blocker_review projections (moved verbatim from q8_shadow_blocker_review).

Module globals and helpers are resolved on ``facade`` (the q8_shadow_blocker_review module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping


def _candidate_rows(payloads: Iterable[Mapping[str, Any]], *, facade: Any) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for payload in payloads:
        if not isinstance(payload, facade.Mapping):
            continue
        for raw in list(payload.get("candidates") or []):
            if not isinstance(raw, facade.Mapping):
                continue
            row = dict(raw)
            row.setdefault("_payload_generated_at", payload.get("generated_at"))
            rows.append(row)
    return rows
