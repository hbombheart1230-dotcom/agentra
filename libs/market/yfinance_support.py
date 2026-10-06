"""Explicit yfinance dependency handling.

yfinance is a declared runtime dependency (requirements.txt). A missing install
used to be swallowed by ``except Exception: return []`` / ``return None`` at many
call sites, so data collectors reported empty-but-healthy results (2026-10-06
Q10/Q12 incident). This module makes the failure explicit and identifiable.

Data-fetch failures (network, empty frame, bad ticker) are NOT dependency errors
and keep their existing per-site "unavailable" handling.
"""

from __future__ import annotations

import logging
from types import ModuleType
from typing import Any, Dict, Optional

_LOG = logging.getLogger(__name__)
_REPORTED: set[str] = set()

DEPENDENCY_MISSING_REASON = "dependency_missing:yfinance"


class DataSourceDependencyError(RuntimeError):
    """A required data-source library is not importable in this environment."""

    def __init__(self, package: str = "yfinance", detail: str = "") -> None:
        self.package = package
        self.reason = f"dependency_missing:{package}"
        message = (
            f"{self.reason}: required package '{package}' is not installed in this "
            "Python environment (declare/install it via requirements.txt)"
        )
        if detail:
            message = f"{message} [{detail}]"
        super().__init__(message)


def require_yfinance() -> ModuleType:
    """Return the yfinance module or raise DataSourceDependencyError."""
    try:
        import yfinance as yf  # type: ignore
    except ImportError as exc:
        raise DataSourceDependencyError("yfinance", f"{type(exc).__name__}: {exc}") from exc
    return yf


def yfinance_dependency_status() -> Dict[str, Any]:
    """Non-raising probe: {"available": bool, "version": str|None, "reason": str}."""
    try:
        yf = require_yfinance()
    except DataSourceDependencyError as exc:
        return {"available": False, "version": None, "reason": exc.reason, "error": str(exc)}
    return {"available": True, "version": str(getattr(yf, "__version__", "") or "") or None, "reason": ""}


def try_yfinance(component: str) -> Optional[ModuleType]:
    """For best-effort, loop-adjacent callers that must keep degrading gracefully.

    Returns the module, or None after logging an explicit ERROR (once per
    component per process) naming the missing dependency. Never silent.
    """
    try:
        return require_yfinance()
    except DataSourceDependencyError as exc:
        if component not in _REPORTED:
            _REPORTED.add(component)
            _LOG.error("DATA_SOURCE_DEPENDENCY_MISSING component=%s %s", component, exc)
        return None
