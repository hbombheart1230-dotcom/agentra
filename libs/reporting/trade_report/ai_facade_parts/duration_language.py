"""Non-authoritative display-only Korean grammar and duration formatting.

The legacy trade_report_ai facade supplies patchable helper dependencies per call.
"""
from __future__ import annotations

from typing import Any, List, Optional


def _humanize_duration_text_impl(value: Any, *, fallback_seconds: Any = None, _clip, _safe_fullmatch) -> str:
    text = _clip(value, max_len=80).strip()
    lowered = text.lower()
    total_seconds: Optional[int] = None

    if text:
        if _safe_fullmatch(r"\d{1,2}:\d{2}:\d{2}", text):
            hours, minutes, seconds = [int(part) for part in text.split(":")]
            total_seconds = hours * 3600 + minutes * 60 + seconds
        elif _safe_fullmatch(r"\d{1,2}:\d{2}", text):
            minutes, seconds = [int(part) for part in text.split(":")]
            total_seconds = minutes * 60 + seconds
        else:
            hour_match = _safe_fullmatch(r"([0-9]+(?:\.[0-9]+)?)\s*h", lowered)
            minute_match = _safe_fullmatch(r"([0-9]+(?:\.[0-9]+)?)\s*m", lowered)
            second_match = _safe_fullmatch(r"([0-9]+(?:\.[0-9]+)?)\s*s", lowered)
            if hour_match:
                total_seconds = int(round(float(hour_match.group(1)) * 3600))
            elif minute_match:
                total_seconds = int(round(float(minute_match.group(1)) * 60))
            elif second_match:
                total_seconds = int(round(float(second_match.group(1))))

    if total_seconds is None and fallback_seconds not in (None, ""):
        try:
            total_seconds = int(round(float(fallback_seconds)))
        except Exception:
            total_seconds = None

    if total_seconds is None:
        return text

    hours, remainder = divmod(max(total_seconds, 0), 3600)
    minutes, seconds = divmod(remainder, 60)
    parts: List[str] = []
    if hours:
        parts.append(f"{hours}시간")
    if minutes:
        parts.append(f"{minutes}분")
    if seconds or not parts:
        parts.append(f"{seconds}초")
    return " ".join(parts)



def _holding_duration_label_impl(value: Any, *, _humanize_duration_text) -> str:
    text = _humanize_duration_text(value)
    if not text:
        return ""
    return f"보유 시간은 {text}였습니다."



def _korean_predicate_impl(value: str, *, noun_suffix: str = "입니다.") -> str:
    text = str(value or "").strip()
    if not text:
        return noun_suffix
    tail = "입니다." if noun_suffix == "입니다." else noun_suffix
    last = text[-1]
    code = ord(last)
    if 0xAC00 <= code <= 0xD7A3:
        has_batchim = (code - 0xAC00) % 28 != 0
        if tail == "입니다.":
            return "이었습니다." if has_batchim else "였습니다."
    return tail



def _korean_euro_ro_impl(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return "로"
    last = text[-1]
    code = ord(last)
    if 0xAC00 <= code <= 0xD7A3:
        jong = (code - 0xAC00) % 28
        if jong == 0 or jong == 8:
            return "로"
        return "으로"
    return "로"
