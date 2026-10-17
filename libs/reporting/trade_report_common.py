from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List
import sys as _r3_sys
from libs.agents.reporter.narrative.trade_report_common_r9_bodies_01 import (  # R-4 owner bodies (facade-injected)
    list_text_r4_impl,
    listify_r4_impl,
    dedupe_list_r4_impl,
    compact_named_rows_r4_impl,
    compact_scalar_dict_r4_impl,
    merge_missing_values_r4_impl,
    is_empty_placeholder_r4_impl,
    fmt_pct_r4_impl,
    fmt_price_r4_impl,
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except Exception:
        return int(default)


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def clip_text(value: Any, *, max_len: int = 220) -> str:
    text = str(value or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max(0, max_len - 3)] + "..."


def report_clip(value: Any, *, max_len: int = 400) -> str:
    return clip_text(value, max_len=max_len)


def list_text(values: Any, *, limit: int = 6, max_len: int = 220) -> List[str]:
    return list_text_r4_impl(values, limit=limit, max_len=max_len, facade=_r3_sys.modules[__name__])


def listify(values: Any, *, max_items: int = 6, max_len: int = 240) -> List[str]:
    return listify_r4_impl(values, max_items=max_items, max_len=max_len, facade=_r3_sys.modules[__name__])


def dedupe_list(values: List[str], *, max_items: int = 12, max_len: int = 260) -> List[str]:
    return dedupe_list_r4_impl(values, max_items=max_items, max_len=max_len, facade=_r3_sys.modules[__name__])


def compact_named_rows(values: Any, *, max_items: int = 3) -> List[Dict[str, Any]]:
    return compact_named_rows_r4_impl(values, max_items=max_items, facade=_r3_sys.modules[__name__])


def compact_scalar_dict(values: Any, *, max_items: int = 8, max_len: int = 160) -> Dict[str, Any]:
    return compact_scalar_dict_r4_impl(values, max_items=max_items, max_len=max_len, facade=_r3_sys.modules[__name__])


def merge_missing_values(base: Dict[str, Any], fallback: Dict[str, Any]) -> Dict[str, Any]:
    return merge_missing_values_r4_impl(base, fallback, facade=_r3_sys.modules[__name__])


def is_empty_placeholder(value: Any) -> bool:
    return is_empty_placeholder_r4_impl(value, facade=_r3_sys.modules[__name__])


def format_pct(value: Any) -> str:
    if value in (None, ""):
        return "not_captured"
    return f"{safe_float(value, 0.0):.2f}"


def format_ratio_pct(value: Any) -> str:
    if value in (None, ""):
        return "not_captured"
    return f"{safe_float(value, 0.0) * 100.0:.2f}"


def format_exit_label(value: Any) -> str:
    text = str(value or "").strip().replace("_", " ")
    if not text:
        return "not_captured"
    return " ".join(part.capitalize() for part in text.split())


def fmt_pct(value: Any) -> str:
    return fmt_pct_r4_impl(value, facade=_r3_sys.modules[__name__])


def fmt_price(value: Any) -> str:
    return fmt_price_r4_impl(value, facade=_r3_sys.modules[__name__])
