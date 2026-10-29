"""``_has_meaningful_payload`` moved verbatim from live_execution_bundle_runner.py as ``has_meaningful_payload``.

Helpers are resolved on ``facade`` (the runner module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any


def has_meaningful_payload(payload: Any, *, facade: Any) -> bool:
    if not isinstance(payload, dict) or not payload:
        return False
    for value in payload.values():
        if isinstance(value, dict) and facade._has_meaningful_payload(value):
            return True
        if isinstance(value, list) and any(item not in ({}, [], None, "") for item in value):
            return True
        if value not in ({}, [], None, ""):
            return True
    return False
