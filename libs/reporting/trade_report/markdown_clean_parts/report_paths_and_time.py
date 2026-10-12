"""Markdown-clean report-path lookup, KST time formatting and duration/carry labels (deterministic, read-only).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _get_report_path_r3_impl(root, path, *, facade):
    current = root
    for part in str(path or "").split("."):
        if not part:
            continue
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def _parse_report_datetime_r3_impl(value, *, facade):
    text = str(value or "").strip()
    if not text:
        return None
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        parsed = facade.datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=facade.timezone.utc)
        return parsed.astimezone(facade.timezone.utc)
    except ValueError:
        return None


def _duration_label_seconds_r3_impl(value, *, facade):
    seconds = facade._num_opt(value)
    if seconds is None or seconds <= 0:
        return ""
    total = int(round(seconds))
    days, rem = divmod(total, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    parts: List[str] = []
    if days:
        parts.append(f"{days}일")
    if hours:
        parts.append(f"{hours}시간")
    if minutes:
        parts.append(f"{minutes}분")
    if seconds or not parts:
        parts.append(f"{seconds}초")
    return " ".join(parts)


def _carry_state_label_r3_impl(value, *, weekend_carry, facade):
    key = str(value or "").strip().lower()
    labels = {
        "multi_session_stale": "전일/주말 이월 보유",
        "overnight_open": "오버나이트 보유",
        "eod_carry_approved": "장마감 이월 승인",
        "carry_overnight_approved": "오버나이트 승인",
        "overnight": "오버나이트 보유",
    }
    if key in labels:
        return labels[key]
    if weekend_carry:
        return "주말 이월 보유"
    return facade._metadata_value(value) if facade._metadata_value(value) != "-" else "오버나이트/이월 보유"


def _carry_risk_label_r3_impl(value, *, facade):
    key = str(value or "").strip().lower()
    labels = {
        "urgent_exit_review": "장기/주말 이월 후 우선 청산 검토",
        "exit_review": "청산 검토",
        "normal": "일반",
    }
    if key in labels:
        return labels[key]
    text = facade._metadata_value(value)
    return "" if text == "-" else text


def _strategy_horizon_report_surface_r3_impl(report, *, facade):
    surface = facade._strategy_horizon_report_surface_impl(
        report,
        as_dict=facade._as_dict,
        first_report_path=facade._first_report_path,
        compact_post_exit_shadow=facade._compact_post_exit_shadow,
        post_exit_shadow_surface=facade._post_exit_shadow_surface,
        carryover_context=facade._carryover_context,
        num_opt=facade._num_opt,
        duration_label_compact_fn=facade._duration_label_compact,
    )
    authoritative_hold_sec = facade._authoritative_hold_duration_seconds(report)
    if authoritative_hold_sec is not None:
        surface = dict(surface)
        surface["actual_hold_sec"] = authoritative_hold_sec
        surface["actual_hold_label"] = facade._duration_label_seconds(authoritative_hold_sec)
        surface["actual_hold_source"] = "entry_exit_execution_timestamps"
    return surface
