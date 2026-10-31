"""quant_shadow_candidate_evaluation projections (moved verbatim from quant_shadow_candidate_evaluation).

Module globals and helpers are resolved on ``facade`` (the quant_shadow_candidate_evaluation module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


def shadow_candidate_root_for_reports(reports_root: Path, *, facade: Any) -> Path:
    return facade.Path(reports_root).parent / "data" / "logs" / "quant_shadow_candidates"
