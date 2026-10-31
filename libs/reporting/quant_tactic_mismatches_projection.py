"""quant_tactic_report projections (moved verbatim from quant_tactic_report).

Module globals and helpers are resolved on ``facade`` (the quant_tactic_report module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Dict, List


def _tactic_mismatches(sources: List[tuple[str, str]], tactic_id: str) -> List[Dict[str, str]]:
    return [
        {"source": source, "tactic_id": value}
        for source, value in sources
        if tactic_id and value != tactic_id and source != "exit_quant_decision"
    ]
