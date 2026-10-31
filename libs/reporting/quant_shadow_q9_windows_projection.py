"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def _q9_windows_by_id(reports_root: Path, day: str, *, facade: Any) -> Dict[str, Dict[str, Any]]:
    # `_augment_missing_q9_commander_candidate` reads only `commander_final` from a window, so
    # the ~120 MB windows file is streamed and reduced to that field (id -> {"commander_final"}).
    path = (
        facade.Path(reports_root)
        / "operator_summary"
        / "daily"
        / str(day)[:10]
        / "q9_decision_windows.json"
    )
    out: Dict[str, Dict[str, Any]] = {}
    try:
        for row in facade.iter_json_array(path, "windows", strict=True):
            if isinstance(row, facade.Mapping) and str(row.get("decision_id") or ""):
                out[str(row.get("decision_id") or "")] = {"commander_final": row.get("commander_final")}
    except (OSError, ValueError):
        return {}
    return out
