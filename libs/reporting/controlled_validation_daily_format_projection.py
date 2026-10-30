"""Controlled validation daily markdown lines (moved verbatim from controlled_validation_daily).

Globals/helpers are resolved on ``facade`` (the controlled_validation_daily module) at call time; this module never imports it.
Pure formatting; no IO.
"""
from __future__ import annotations

from typing import Any, Mapping


def render_controlled_validation_daily_lines(payload: Mapping[str, Any], *, facade: Any) -> list[str]:
    lanes = [dict(row) for row in list(payload.get("lanes") or []) if isinstance(row, facade.Mapping)]
    opening = dict(payload.get("opening_alpha") or {})
    lines = ["", "## Controlled Validation Lanes", ""]
    for row in lanes:
        lines.append(
            f"- {row.get('label')}: `{row.get('evaluation_status')}`"
            f" / reason `{row.get('reason') or '-'}`"
            f" / attempts {int(row.get('attempt_count') or 0)}"
            f" / accepted {int(row.get('submission_count') or 0)}"
        )
    reasons = ", ".join(
        f"{key}={value}" for key, value in dict(opening.get("reason_counts") or {}).items()
    )
    lines.append(
        "- Opening Alpha: "
        f"evaluated {int(opening.get('evaluation_count') or 0)}"
        f" / eligible {int(opening.get('eligible_count') or 0)}"
        f" / applied {int(opening.get('applied_count') or 0)}"
        f" / submitted {int(opening.get('submission_count') or 0)}"
        f" / reasons {reasons or '-'}"
    )
    if "broker_submission_attempted_count" in opening:
        # P1-B (2026-09-03 daily audit, additive): clarifies that
        # "submitted" above counts probe-reservation claims (Monitor
        # decision time), not actual broker HTTP submissions.
        broker_outcomes = ", ".join(
            f"{key}={value}" for key, value in dict(opening.get("broker_outcome_counts") or {}).items()
        )
        lines.append(
            "- Opening Alpha submissions (detail): "
            f"probe_reservation_claimed {int(opening.get('submission_candidate_count') or 0)}"
            f" / broker_submission_attempted {int(opening.get('broker_submission_attempted_count') or 0)}"
            f" / broker_outcomes {broker_outcomes or '-'}"
        )
    return lines
