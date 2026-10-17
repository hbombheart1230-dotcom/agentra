from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List
import sys as _r3_sys
from libs.agents.reporter.read_models.memory_application_bodies_01 import (  # R-4 owner bodies (facade-injected)
    _first_non_empty_text_r4_impl,
    _normalize_adjustments_r4_impl,
    _scanner_bias_carrier_r4_impl,
    _walk_dicts_r4_impl,
    _is_application_trace_r4_impl,
    _application_trace_score_r4_impl,
    _select_application_trace_r4_impl,
    _select_symbol_adjustment_r4_impl,
    build_trade_memory_application_surface_r4_impl,
)


def _dict(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _list(value: Any) -> List[Any]:
    return list(value) if isinstance(value, list) else []


def _text(value: Any, *, max_len: int = 120) -> str:
    text = str(value or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max(0, max_len - 3)] + "..."


def _safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except Exception:
        return None


def _load_json_artifact(path_value: Any) -> Dict[str, Any]:
    path_text = str(path_value or "").strip()
    if not path_text:
        return {}
    path = Path(path_text)
    if not path.is_absolute():
        path = Path.cwd() / path
    try:
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _first_non_empty_dict(*values: Any) -> Dict[str, Any]:
    for value in values:
        if isinstance(value, dict) and value:
            return dict(value)
    return {}


def _first_non_empty_text(*values: Any, max_len: int = 120) -> str:
    return _first_non_empty_text_r4_impl(*values, max_len=max_len, facade=_r3_sys.modules[__name__])


def _normalize_adjustments(values: Any) -> List[Dict[str, Any]]:
    return _normalize_adjustments_r4_impl(values, facade=_r3_sys.modules[__name__])


def _scanner_bias_carrier(canonical_scanner: Dict[str, Any]) -> Dict[str, Any]:
    return _scanner_bias_carrier_r4_impl(canonical_scanner, facade=_r3_sys.modules[__name__])


def _monitor_bias_carrier(canonical_monitor: Dict[str, Any]) -> Dict[str, Any]:
    return _first_non_empty_dict(
        canonical_monitor.get("threshold_snapshot"),
        canonical_monitor.get("policy_ref"),
        canonical_monitor,
    )


def _walk_dicts(value: Any) -> List[Dict[str, Any]]:
    return _walk_dicts_r4_impl(value, facade=_r3_sys.modules[__name__])


def _is_application_trace(value: Dict[str, Any], *, agent: str) -> bool:
    return _is_application_trace_r4_impl(value, agent=agent, facade=_r3_sys.modules[__name__])


def _application_trace_score(value: Dict[str, Any], *, agent: str) -> tuple[int, int, int, int, int, int]:
    return _application_trace_score_r4_impl(value, agent=agent, facade=_r3_sys.modules[__name__])


def _select_application_trace(*values: Any, agent: str) -> Dict[str, Any]:
    return _select_application_trace_r4_impl(*values, agent=agent, facade=_r3_sys.modules[__name__])


def _select_symbol_adjustment(rows: Any, symbol: str) -> Dict[str, Any]:
    return _select_symbol_adjustment_r4_impl(rows, symbol, facade=_r3_sys.modules[__name__])


def build_trade_memory_application_surface(story_input: Dict[str, Any] | None) -> Dict[str, Any]:
    return build_trade_memory_application_surface_r4_impl(story_input, facade=_r3_sys.modules[__name__])


__all__ = ["build_trade_memory_application_surface"]
