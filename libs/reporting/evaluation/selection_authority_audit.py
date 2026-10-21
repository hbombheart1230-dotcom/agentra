from __future__ import annotations

from collections import Counter
from typing import Any, Mapping, Sequence

from . import fast08_scanner_attribution as _sa


_mapping = _sa.mapping
_symbol = _sa.symbol_of
_changed = _sa.changed


def build_selection_authority_audit(
    models: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    counters: Counter[str] = Counter()
    for model in models:
        integrity = _mapping(model.get("integrity"))
        defects = {str(value) for value in (integrity.get("defects") or [])}
        if "broker_day_partial_exit_duplicate" in defects:
            counters["excluded:broker_day_partial_exit_duplicate"] += 1
            continue
        if "confirmed_runtime_defect" in defects:
            counters["excluded:confirmed_runtime_defect"] += 1
            continue
        row = _sa.selection_path_row(model)
        rows.append(row)
        _sa.count_selection_changes(counters, row)

    return {
        "schema_version": "selection_authority_audit.v1",
        "behavior_effect": "observation_only",
        "trade_count": len(rows),
        "summary": dict(counters),
        "interpretation": {
            "commander_scope": "final approval/veto unless symbol deltas prove otherwise",
            "strategist_scope": "post-strategy scanner/ranking state, not pure LLM stock picker by default",
        },
        "rows": rows,
    }


render_selection_authority_audit = _sa.render_selection_authority_audit


__all__ = ["build_selection_authority_audit", "render_selection_authority_audit"]
