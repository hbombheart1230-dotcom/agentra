"""Canonical responsibility name for the live-cycle pipeline (P1.5.8 compatibility alias).

The implementation stays in ``graphs.pipelines.m13_live_loop``; this module resolves it at call time so that
monkeypatching the legacy module keeps working. Legacy import path and behaviour are unchanged.
"""
from __future__ import annotations

from typing import Any

from graphs.pipelines import m13_live_loop as _legacy


def run_live_cycle_once(*args: Any, **kwargs: Any) -> Any:
    """Canonical name of ``run_m13_once`` (same signature and behaviour)."""
    return _legacy.run_m13_once(*args, **kwargs)


__all__ = ["run_live_cycle_once"]
