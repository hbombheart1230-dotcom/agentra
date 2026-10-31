"""post_exit_shadow_recap projections (moved verbatim from post_exit_shadow_recap).

Module globals and helpers are resolved on ``facade`` (the post_exit_shadow_recap module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, List


def _as_dict(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _as_list(value: Any) -> List[Any]:
    return list(value) if isinstance(value, list) else []
