"""Alpha research board: ``_attention_order`` (pure; moved verbatim from builder)."""
from __future__ import annotations

from typing import Any


def _attention_order(candidates: list[dict[str, Any]]) -> list[str]:
    order = {
        "RUNTIME_VALIDATION_NEXT": 0,
        "BACKGROUND_RUNTIME_REQUIRED": 1,
        "ACTION_REVIEW": 2,
        "OBSERVE_FIXED": 3,
        "DATA_REPAIR_BOUNDARY": 4,
        "CLOSED_AFTER_SENSITIVITY_REVIEW": 5,
        "CLOSED_NEGATIVE_PROSPECTIVE": 6,
        "CLOSED": 7,
    }
    return [
        row["candidate_id"]
        for row in sorted(
            candidates,
            key=lambda row: (order.get(str(row.get("board_bucket")), 9), row["candidate_id"]),
        )
    ]
