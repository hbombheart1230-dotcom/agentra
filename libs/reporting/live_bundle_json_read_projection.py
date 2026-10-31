"""live_execution_bundle_runner projections (moved verbatim from live_execution_bundle_runner).

Module globals and helpers are resolved on ``facade`` (the live_execution_bundle_runner module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def _read_json(path: Path, *, facade: Any) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        obj = facade.json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return obj if isinstance(obj, dict) else {}
