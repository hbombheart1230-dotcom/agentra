"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping


def _augment_missing_q9_commander_candidate(
    payload: Dict[str, Any],
    *,
    windows_by_id: Mapping[str, Mapping[str, Any]],
    facade: Any,
) -> Dict[str, Any]:
    rows = [
        dict(row)
        for row in payload.get("q9_decision_candidates") or []
        if isinstance(row, facade.Mapping)
    ]
    if any(str(row.get("q9_decision_role") or "") == "C_COMMANDER_FINAL" for row in rows):
        return payload
    decision_id = str(payload.get("q9_decision_id") or "").strip()
    window = windows_by_id.get(decision_id)
    if not isinstance(window, facade.Mapping):
        return payload
    commander = window.get("commander_final")
    commander = commander if isinstance(commander, facade.Mapping) else {}
    symbol = str(
        commander.get("selected_symbol")
        or commander.get("candidate_symbol")
        or ""
    ).strip()
    if not symbol:
        return payload
    source = next(
        (
            row
            for row in rows
            if str(row.get("symbol") or "") == symbol
            and str(row.get("q9_decision_role") or "")
            in {"B_STRATEGIST_RANKED", "A_SCANNER_CONTROL"}
        ),
        None,
    )
    if source is None:
        return payload
    commander_row = dict(source)
    commander_row.update(
        {
            "rank": 1,
            "q9_decision_role": "C_COMMANDER_FINAL",
            "q9_selected": False,
            "q9_commander_decision": str(commander.get("decision") or ""),
            "q9_commander_no_trade": bool(commander.get("no_trade")),
            "q9_backfill_source": "daily_q9_decision_window",
        }
    )
    payload["q9_decision_candidates"] = rows + [commander_row]
    return payload
