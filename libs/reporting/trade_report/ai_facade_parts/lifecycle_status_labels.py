"""AI report lifecycle/exit placeholder and status-label classification helpers (deterministic, read-only).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _as_status_r3_impl(value, *, facade):
    text = facade._clip(value, max_len=32).lower()
    if text == "opened":
        return "open"
    if text == "closed_out":
        return "closed"
    return text


def _action_from_exit_reason_r3_impl(value, *, facade):
    text = str(value or "").strip().lower()
    if not text:
        return ""
    if "sell" in text or "매도" in text or "청산" in text:
        return "SELL"
    return ""


def _is_open_position_placeholder_reason_r3_impl(value, *, facade):
    text = str(value or "").strip().lower()
    if not text:
        return False
    markers = (
        "no_position",
        "no position",
        "position is still open",
        "monitor is watching for exit",
        "still open",
        "포지션이 아직",
    )
    return any(token in text for token in markers)


def _is_hold_placeholder_exit_reason_r3_impl(value, *, facade):
    text = str(value or "").strip()
    if not text:
        return False
    normalized = facade.re.sub(r"^sell\s+was\s+triggered\s+because\s*", "", text, flags=facade.re.IGNORECASE)
    normalized = normalized.strip().strip(".").strip().lower()
    return normalized in {"hold", "hold_position", "holding", "보유", "보유 유지"} or "because hold" in text.lower()


def _lifecycle_summary_conflicts_with_status_r3_impl(value, status, *, facade):
    text = str(value or "").strip().lower()
    status_text = str(status or "").strip().lower()
    if not text or not status_text:
        return False
    if status_text == "closed" and (" is partial" in text or "status is partial" in text):
        return True
    if status_text == "partial" and (" is closed" in text or "status is closed" in text):
        return True
    return False


def _story_post_exit_shadow_r3_impl(story_input, *, facade):
    for candidate in (
        facade._as_dict(story_input.get("post_exit_shadow")),
        facade._as_dict(facade._as_dict(story_input.get("lifecycle_bundle")).get("post_exit_shadow")),
        facade._as_dict(facade._as_dict(story_input.get("trade_lifecycle")).get("post_exit_shadow")),
        facade._as_dict(facade._as_dict(facade._as_dict(story_input.get("trade_lifecycle")).get("exit")).get("post_exit_shadow")),
        facade._as_dict(facade._as_dict(facade._as_dict(story_input.get("lifecycle_bundle")).get("exit")).get("post_exit_shadow")),
    ):
        if candidate:
            return candidate
    return {}


def _canonical_ai_report_status_r3_impl(value, *, facade):
    raw = str(value or "").strip().lower()
    if raw in {"ok", "partial", "salvaged", "error", "skipped"}:
        return raw
    if raw in {"repaired"}:
        return "ok"
    if raw in {"disabled", "fallback", "unavailable", "dry_run"}:
        return "skipped"
    return "error"
