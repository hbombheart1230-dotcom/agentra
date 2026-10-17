"""Reporter read-model owner (decomposed from libs/reporting/trade_report_symbol_metadata.py; bodies verbatim). Text/list helpers."""
from __future__ import annotations

import re
from typing import Any, Callable, Dict, List


def clip_text(value: Any, max_len: int = 200) -> str:
    text = str(value or "").strip()
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def listify(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def append_unique_text(
    out: List[str],
    value: Any,
    *,
    max_len: int = 80,
    metadata_value: Callable[[Any], str],
    translate_text: Callable[[Any], str],
) -> None:
    text = metadata_value(translate_text(value)).strip()
    if not text:
        return
    if text == "not_captured" or text.lower() in {"none", "null", "unknown", "unavailable"}:
        return
    if re.fullmatch(r"\d{6}", text):
        return
    if text not in out:
        out.append(clip_text(text, max_len))


def append_theme_values(
    out: List[str],
    raw_theme: Any,
    *,
    metadata_value: Callable[[Any], str],
    translate_text: Callable[[Any], str],
) -> None:
    if isinstance(raw_theme, dict):
        append_unique_text(
            out,
            raw_theme.get("theme")
            or raw_theme.get("theme_name")
            or raw_theme.get("name")
            or raw_theme.get("value"),
            metadata_value=metadata_value,
            translate_text=translate_text,
        )
        return
    for item in listify(raw_theme):
        if isinstance(item, dict):
            append_unique_text(
                out,
                item.get("theme")
                or item.get("theme_name")
                or item.get("name")
                or item.get("value"),
                metadata_value=metadata_value,
                translate_text=translate_text,
            )
        else:
            append_unique_text(out, item, metadata_value=metadata_value, translate_text=translate_text)
