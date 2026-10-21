from __future__ import annotations

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from . import fast08_evidence_inventory as _ev


KST = ZoneInfo("Asia/Seoul")
MIN_COMPLETE_WINDOWS = 20
MIN_LINKAGE_RATIO = 0.95
MIN_FORWARD_COVERAGE = 0.95


def _parse_kst(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=KST)
    return parsed.astimezone(KST)


def _is_synthetic_window(row: dict[str, Any]) -> bool:
    identity = " ".join(
        str(row.get(key) or "").lower()
        for key in ("decision_id", "run_id", "candidate_pool_id")
    )
    return any(marker in identity for marker in ("test", "fixture", "synthetic"))


def build_q9_day_validity(
    *,
    day: str,
    inventory: dict[str, Any],
    now: datetime | None = None,
) -> dict[str, Any]:
    current = (now or datetime.now(KST)).astimezone(KST)
    signals = _ev.q9_day_signals(inventory)
    decision = signals["decision"]
    complete_count = signals["complete_count"]
    window_count = signals["window_count"]
    linkage_ratio = signals["linkage_ratio"]
    synthetic_count = signals["synthetic_count"]
    missing_selected = signals["missing_selected"]
    invalid_forward = signals["invalid_forward"]
    unavailable_forward = signals["unavailable_forward"]
    pending_forward = signals["pending_forward"]
    forward_total = signals["forward_total"]
    forward_coverage = signals["forward_coverage"]
    comparison_complete = signals["comparison_complete"]

    session_day = datetime.fromisoformat(day).date()
    is_future = session_day > current.date()
    is_complete = session_day < current.date() or (
        session_day == current.date() and (current.hour, current.minute) >= (15, 30)
    )

    blockers: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    if not decision.get("exists"):
        blockers.append({"code": "missing_q9_artifact", "count": 1})
    elif not bool(decision.get("schema_match", True)):
        blockers.append({"code": "q9_schema_mismatch", "count": 1})
    if is_complete and complete_count < MIN_COMPLETE_WINDOWS:
        blockers.append(
            {
                "code": "insufficient_complete_pabc_windows",
                "count": max(0, MIN_COMPLETE_WINDOWS - complete_count),
            }
        )
    if is_complete and window_count and linkage_ratio < MIN_LINKAGE_RATIO:
        blockers.append(
            {
                "code": "pabc_linkage_ratio_below_threshold",
                "count": max(0, window_count - complete_count),
            }
        )
    if synthetic_count:
        warnings.append(
            {
                "code": "synthetic_windows_excluded",
                "count": synthetic_count,
                "invalidates_day": False,
            }
        )
    if missing_selected:
        blockers.append({"code": "missing_selected_candidate", "count": missing_selected})
    if invalid_forward:
        target = blockers if (
            is_complete and forward_coverage < MIN_FORWARD_COVERAGE and not comparison_complete
        ) else warnings
        target.append(
            {
                "code": "invalid_forward_observation",
                "count": invalid_forward,
                "coverage": round(forward_coverage, 4),
                "required_coverage": MIN_FORWARD_COVERAGE,
                "comparison_complete_override": bool(comparison_complete),
                "invalidates_day": bool(
                    is_complete and forward_coverage < MIN_FORWARD_COVERAGE and not comparison_complete
                ),
            }
        )
    if unavailable_forward:
        target = blockers if (
            is_complete and forward_coverage < MIN_FORWARD_COVERAGE and not comparison_complete
        ) else warnings
        target.append(
            {
                "code": "forward_observation_unavailable",
                "count": unavailable_forward,
                "coverage": round(forward_coverage, 4),
                "required_coverage": MIN_FORWARD_COVERAGE,
                "comparison_complete_override": bool(comparison_complete),
                "invalidates_day": bool(
                    is_complete and forward_coverage < MIN_FORWARD_COVERAGE and not comparison_complete
                ),
            }
        )
    if is_complete and forward_total == 0:
        blockers.append({"code": "missing_forward_candidate_rows", "count": 1})
    if pending_forward:
        warnings.append(
            {
                "code": "legitimate_forward_pending",
                "count": pending_forward,
                "invalidates_day": False,
            }
        )
    if not bool(decision.get("full_session_coverage")):
        target = blockers if is_complete else warnings
        target.append(
            {
                "code": "full_session_coverage_not_confirmed",
                "count": 1,
                "invalidates_day": bool(is_complete),
            }
        )

    if is_future:
        status = "PREOPEN"
    elif not is_complete:
        status = "IN_PROGRESS"
    else:
        status = "VALID" if not blockers else "INVALID"

    return {
        "schema_version": "q9_day_validity.v1",
        "behavior_effect": "evaluation_only",
        "day": day,
        "status": status,
        "counts_as_formal_day": status == "VALID",
        "trade_required": False,
        "checks": _ev.q9_day_checks(signals),
        "blockers": blockers,
        "warnings": warnings,
        "rule": (
            "A no-trade day remains eligible when the runtime covered the regular "
            "session and Q9 P/A/B/C plus forward evidence are trustworthy."
        ),
    }


__all__ = ["build_q9_day_validity"]
