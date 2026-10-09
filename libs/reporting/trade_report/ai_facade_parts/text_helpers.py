from __future__ import annotations

from typing import Any


def _is_low_information_bullet_impl(value: Any, *, _safe_fullmatch) -> bool:
    text = str(value or "").strip().lower()
    if not text:
        return True
    if text in {"hold", "wait", "buy", "sell", "noop", "monitor", "monitoring"}:
        return True
    if len(text) <= 12 and _safe_fullmatch(r"[a-z_\- ]+", text):
        return True
    return False


def _count_hangul_impl(text: Any) -> int:
    raw = str(text or "")
    return sum(1 for ch in raw if "\uac00" <= ch <= "\ud7a3")


def _count_latin_impl(text: Any) -> int:
    raw = str(text or "")
    return sum(1 for ch in raw if ("a" <= ch.lower() <= "z"))


def _first_nonempty_text_impl(*values: Any, max_len: int = 240, _clip) -> str:
    for value in values:
        text = _clip(value, max_len=max_len)
        if text:
            return text
    return ""


def _has_evidence_payload_impl(value: Any) -> bool:
    if isinstance(value, dict):
        return bool(value)
    if isinstance(value, list):
        return bool(value)
    return bool(str(value or "").strip())


def _as_action_impl(value: Any, *, _clip) -> str:
    text = _clip(value, max_len=24).upper()
    if text in {"NOOP", "NONE"}:
        return "WAIT"
    return text
