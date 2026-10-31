"""quant_tactic_report projections (moved verbatim from quant_tactic_report).

Module globals and helpers are resolved on ``facade`` (the quant_tactic_report module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping


def _first_nested_mapping(root: Mapping[str, Any], key: str, *, facade: Any) -> Dict[str, Any]:
    for item in facade._nested_dicts(root):
        found = facade._mapping(item.get(key))
        if found:
            return found
    return {}
