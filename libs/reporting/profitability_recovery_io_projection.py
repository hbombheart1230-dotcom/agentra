"""profitability_recovery_day1 projections (moved verbatim from profitability_recovery_day1).

Module globals and helpers are resolved on ``facade`` (the profitability_recovery_day1 module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def _read_json(path: Path, *, facade: Any) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = facade.json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}
