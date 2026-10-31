"""quant_tactic_report projections (moved verbatim from quant_tactic_report).

Module globals and helpers are resolved on ``facade`` (the quant_tactic_report module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, List


def _nested_dicts(value: Any, *, max_depth: int = 9, facade: Any) -> List[Dict[str, Any]]:
    if max_depth < 0:
        return []
    out: List[Dict[str, Any]] = []
    if isinstance(value, facade.Mapping):
        item = dict(value)
        out.append(item)
        for child in item.values():
            out.extend(facade._nested_dicts(child, max_depth=max_depth - 1))
    elif isinstance(value, (list, tuple)):
        for child in value:
            out.extend(facade._nested_dicts(child, max_depth=max_depth - 1))
    return out
