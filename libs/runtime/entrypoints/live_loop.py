"""Canonical responsibility name for the live-loop entrypoint (P1.5.8 compatibility alias).

Implementation stays in ``libs.runtime.entrypoints.m13_live_loop``; ``main`` is resolved at call time.
"""
from __future__ import annotations

from typing import Optional

from libs.runtime.entrypoints import m13_live_loop as _legacy

ROOT = _legacy.ROOT


def main(argv: Optional[list[str]] = None) -> int:
    """Canonical name of the live-loop CLI ``main`` (same arguments and exit codes)."""
    return _legacy.main(argv)


__all__ = ["ROOT", "main"]
