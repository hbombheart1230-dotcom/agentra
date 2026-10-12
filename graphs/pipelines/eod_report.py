"""Canonical responsibility name for the end-of-day report pipeline (P1.5.8 compatibility alias).

Implementation stays in ``graphs.pipelines.m13_eod_report`` and is resolved at call time.
"""
from __future__ import annotations

from typing import Any

from graphs.pipelines import m13_eod_report as _legacy


def run_eod_report(*args: Any, **kwargs: Any) -> Any:
    """Canonical name of ``run_m13_eod_report`` (same signature and behaviour)."""
    return _legacy.run_m13_eod_report(*args, **kwargs)


__all__ = ["run_eod_report"]
