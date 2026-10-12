"""Canonical responsibility name for the runtime tick pipeline (P1.5.8 compatibility alias).

Implementation stays in ``graphs.pipelines.m13_tick`` and is resolved at call time.
"""
from __future__ import annotations

from typing import Any

from graphs.pipelines import m13_tick as _legacy


def run_runtime_tick(*args: Any, **kwargs: Any) -> Any:
    """Canonical name of ``run_m13_tick`` (same signature and behaviour)."""
    return _legacy.run_m13_tick(*args, **kwargs)


__all__ = ["run_runtime_tick"]
