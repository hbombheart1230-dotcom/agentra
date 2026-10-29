"""``_latest_stage2_source`` moved verbatim from canonical.py as ``latest_stage2_source``.

Helpers are resolved on ``facade`` (the source module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


def latest_stage2_source(reports_root: Path, through_day: str, *, facade: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    root = reports_root / "evaluation" / "agent_effectiveness"
    candidates = []
    for path in root.glob("cumulative_*/strategist_stage2_effectiveness_deep_dive.json"):
        end_day = path.parent.name.rsplit("_", 1)[-1]
        if end_day <= through_day.replace("-", ""):
            candidates.append((end_day, path))
    if not candidates:
        daily = root / through_day / "strategist_stage2_effectiveness_deep_dive.json"
        return facade.load_json(daily)
    return facade.load_json(max(candidates, key=lambda item: item[0])[1])
