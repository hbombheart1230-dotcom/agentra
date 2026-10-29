"""``_question_summaries`` moved verbatim from canonical.py as ``question_summaries``.

Helpers are resolved on ``facade`` (the source module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any


def question_summaries(rows: list[dict[str, Any]], *, facade: Any) -> list[dict[str, Any]]:
    summaries = []
    for question in facade.QUESTIONS:
        question_id = str(question["question_id"])
        grouped = [row for row in rows if row["question_id"] == question_id]
        counts = {
            status: sum(row["status"] == status for row in grouped)
            for status in facade.ALLOWED_STATUSES
        }
        summaries.append(
            {
                **dict(question),
                "candidate_count": len(grouped),
                "status_counts": counts,
                "active_candidate_ids": [
                    row["candidate_id"]
                    for row in grouped
                    if row["status"] in {"DISCOVERY", "PROSPECTIVE", "REVIEW_READY"}
                ],
                "closed_candidate_ids": [
                    row["candidate_id"] for row in grouped if row["status"] == "CLOSED"
                ],
            }
        )
    return summaries
