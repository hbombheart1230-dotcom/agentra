"""Controlled validation daily payload builder (moved verbatim from controlled_validation_daily).

Globals/helpers are resolved on ``facade`` (the controlled_validation_daily module) at call time; this module never imports it.
Read-only; reads only through facade helpers.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


def build_controlled_validation_daily(
    *, reports_root: Path, day: str, facade: Any
) -> dict[str, Any]:
    reports_root = facade.Path(reports_root)
    workspace_root = reports_root.parent if reports_root.name.lower() == "reports" else reports_root
    controlled_root = workspace_root / "data" / "logs" / "controlled_mock_lanes" / day
    opening_root = workspace_root / "data" / "logs" / "opening_rank1_controlled_probe" / day
    evaluations = facade._rows(facade._read(controlled_root / "lane_evaluations.json"), "evaluations")
    attempts = facade._rows(facade._read(controlled_root / "lane_attempts.json"), "attempts")
    submissions = facade._rows(facade._read(controlled_root / "lane_submissions.json"), "submissions")
    opening_evaluations = facade._rows(facade._read(opening_root / "probe_evaluations.json"), "evaluations")
    opening_submissions = facade._rows(facade._read(opening_root / "probe_submissions.json"), "submissions")

    # P1-B (additive, read-only): cross-reference each probe-reservation
    # row against its own executor.json for the ACTUAL broker outcome.
    # `submission_count` below is left completely unchanged for backward
    # compatibility -- these are new, separately-named fields only.
    broker_submission_attempted_count = 0
    broker_outcome_counts: dict[str, int] = {}
    for row in opening_submissions:
        outcome = facade._executor_broker_outcome(reports_root, day, str(row.get("run_id") or ""))
        if outcome["submission_attempts"] > 0:
            broker_submission_attempted_count += 1
        label = outcome["broker_outcome"] or "UNKNOWN_ARTIFACT"
        broker_outcome_counts[label] = broker_outcome_counts.get(label, 0) + 1

    lane_rows: list[dict[str, Any]] = []
    for lane_id in ("Q10_SEMICONDUCTOR", "Q10_INDEX", "BTC_WOORI"):
        lane_evaluations = [row for row in evaluations if str(row.get("lane_id") or "") == lane_id]
        latest = lane_evaluations[-1] if lane_evaluations else {}
        lane_attempts = [row for row in attempts if str(row.get("lane_id") or "") == lane_id]
        lane_submissions = [row for row in submissions if str(row.get("lane_id") or "") == lane_id]
        # 2026-09-05 Codex audit: `status` on each attempt row now honestly
        # distinguishes PRE_SUBMISSION_BLOCKED (guard blocked before any
        # broker call, Step5B NOT_SENT) from BROKER_REJECTED (an actual
        # broker-side rejection) -- see coordinator.py::_resolve_broker_outcome.
        # This additive breakdown lets a "rejected count" be read directly
        # without it silently absorbing NOT_SENT attempts.
        attempt_status_counts: dict[str, int] = {}
        for row in lane_attempts:
            label = str(row.get("status") or "") or "UNKNOWN"
            attempt_status_counts[label] = attempt_status_counts.get(label, 0) + 1
        evaluation_status, evaluation_reason = facade._display_evaluation_status(
            lane_id=lane_id,
            day=day,
            status=str(latest.get("status") or "NOT_EVALUATED"),
            reason=str(latest.get("reason") or ""),
        )
        lane_rows.append(
            {
                "lane_id": lane_id,
                "label": facade.LANE_LABELS[lane_id],
                "evaluation_status": evaluation_status,
                "reason": evaluation_reason,
                "observation_count": int(latest.get("observation_count") or 0),
                "attempt_count": len(lane_attempts),
                "attempt_status_counts": attempt_status_counts,
                "submission_count": len(lane_submissions),
                "latest_submission_status": str((lane_submissions[-1] if lane_submissions else {}).get("status") or ""),
            }
        )

    return {
        "schema_version": "controlled_validation_daily.v1",
        "day": day,
        "lanes": lane_rows,
        "opening_alpha": {
            "evaluation_count": len(opening_evaluations),
            "eligible_count": sum(bool(row.get("eligible")) for row in opening_evaluations),
            "applied_count": sum(bool(row.get("applied")) for row in opening_evaluations),
            "submission_count": len(opening_submissions),
            # P1-B (2026-09-03 daily audit): `submission_count` above has
            # always meant "probe reservation claimed" (Monitor-decision-time
            # commit point), not "broker HTTP submission attempted". These
            # two fields make that distinction explicit without touching the
            # existing field's name or meaning.
            "submission_candidate_count": len(opening_submissions),
            "broker_submission_attempted_count": broker_submission_attempted_count,
            "broker_outcome_counts": broker_outcome_counts,
            "reason_counts": {
                reason: sum(1 for row in opening_evaluations if str(row.get("reason") or "") == reason)
                for reason in sorted({str(row.get("reason") or "") for row in opening_evaluations if str(row.get("reason") or "")})
            },
        },
    }
