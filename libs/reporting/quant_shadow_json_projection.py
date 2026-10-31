"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


def _read_json(path: Path, *, facade: Any) -> Any:
    try:
        return facade.json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
