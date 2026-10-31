"""execution_truth_surface projections (moved verbatim from execution_truth_surface).

Module globals and helpers are resolved on ``facade`` (the execution_truth_surface module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any


def _clip(value: Any, *, max_len: int = 120) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return text[:max_len]



def _fmt_price(value: Any) -> str:
    try:
        if value in (None, ""):
            return "-"
        return f"{float(value):.2f}"
    except Exception:
        return str(value or "-")



def _fmt_pct(value: Any) -> str:
    try:
        if value in (None, ""):
            return "-"
        return f"{float(value) * 100:.2f}%"
    except Exception:
        return str(value or "-")



def _is_available(value: Any) -> bool:
    text = str(value or "").strip().lower()
    return text not in {"", "unavailable", "not_available", "none", "-"}
