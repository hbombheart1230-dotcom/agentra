"""LLM status normalization and exception classification (moved verbatim from llm_artifacts).

Helpers are resolved on ``facade`` (the llm_artifacts module) at call time where needed; this module never imports it.
"""
from __future__ import annotations

from typing import Any


def normalize_llm_status(value: Any, *, default: str = "fallback") -> str:
    raw = str(value or "").strip().lower()
    if raw in {"ok", "partial", "salvaged", "repaired", "fallback", "error", "parse_error", "timeout", "network_error", "empty_response"}:
        return raw
    if raw == "line_repaired":
        return "salvaged"
    if raw in {"disabled", "unavailable", "dry_run"}:
        return "fallback"
    return default


def canonical_llm_status(value: Any, *, default: str = "fallback", facade: Any) -> str:
    raw = facade.normalize_llm_status(value, default=default)
    if raw in {"ok", "partial", "salvaged", "repaired", "fallback", "error"}:
        return raw
    if raw in {"parse_error", "timeout", "network_error", "empty_response"}:
        return "error"
    return default


def classify_llm_exception(exc: Exception) -> str:
    text = str(exc or "").strip().lower()
    if isinstance(exc, TimeoutError) or "timeout" in text or "timed out" in text:
        return "timeout"
    if any(marker in text for marker in ("connection", "network", "dns", "ssl", "reset by peer", "temporarily unavailable")):
        return "network_error"
    return "error"
