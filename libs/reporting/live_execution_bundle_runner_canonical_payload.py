"""``_prefer_canonical_payload`` moved verbatim from live_execution_bundle_runner.py as ``prefer_canonical_payload``.

Helpers are resolved on ``facade`` (the runner module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, Tuple


def prefer_canonical_payload(
    canonical_sources: Dict[str, Any],
    agent: str,
    fallback: Dict[str, Any],
    *,
    fallback_source: str,
    normalized_payload: Dict[str, Any] | None = None,
    normalized_path: str = "",
    facade: Any,
) -> Tuple[Dict[str, Any], str, str]:
    canonical_payload = (
        (canonical_sources.get("artifacts") or {}).get(agent)
        if isinstance(canonical_sources.get("artifacts"), dict)
        else {}
    )
    canonical_path = (
        str(((canonical_sources.get("paths") or {}).get(agent) or "")).strip()
        if isinstance(canonical_sources.get("paths"), dict)
        else ""
    )
    merged = dict(fallback or {})
    if facade._has_meaningful_payload(normalized_payload):
        merged.update(dict(normalized_payload or {}))
        return merged, "normalized_trade_artifact", str(normalized_path or "")
    if facade._has_meaningful_payload(canonical_payload):
        merged.update(dict(canonical_payload or {}))
        return merged, "canonical", canonical_path
    return dict(fallback or {}), str(fallback_source or "fallback"), canonical_path
