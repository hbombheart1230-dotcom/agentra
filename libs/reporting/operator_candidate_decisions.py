from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from libs.reporting.json_array_stream import iter_json_array


def load_candidate_decision_summary(
    *,
    reports_root: Path,
    day: str,
) -> dict[str, Any]:
    path = (
        Path(reports_root)
        / "operator_summary"
        / "daily"
        / str(day)[:10]
        / "q9_decision_windows.json"
    )
    empty = {
        "available": False,
        "source": str(path),
        "window_count": 0,
        "decision_counts": {},
        "reason_counts": {},
        "candidate_rejected_total": 0,
        "candidate_noop_total": 0,
        "candidate_approved_total": 0,
    }
    decision_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    # Streamed: the file is ~120 MB and only commander_final's decision/reason are read, so
    # json.loads of the whole document (~450 MiB of objects) is avoided. Counts are folded in
    # only after the whole file has been read, so an unreadable file still returns `empty`.
    try:
        for raw in iter_json_array(path, "windows", strict=True):
            if not isinstance(raw, Mapping):
                continue
            commander = raw.get("commander_final")
            commander = commander if isinstance(commander, Mapping) else {}
            decision = str(commander.get("decision") or "unknown").strip().lower()
            reason = str(commander.get("reason") or "unspecified").strip()
            decision_counts[decision] += 1
            reason_counts[reason] += 1
    except (OSError, ValueError):
        return empty

    return {
        "available": True,
        "source": str(path),
        "window_count": sum(decision_counts.values()),
        "decision_counts": dict(decision_counts),
        "reason_counts": dict(reason_counts.most_common(10)),
        "candidate_rejected_total": int(decision_counts.get("reject", 0)),
        "candidate_noop_total": int(decision_counts.get("noop", 0)),
        "candidate_approved_total": int(
            decision_counts.get("approve", 0) + decision_counts.get("approved", 0)
        ),
        "semantics": {
            "candidate_rejection": "upstream policy decision before OrderIntent",
            "execution_guard_block": "OrderIntent rejected by execute_from_packet guard",
        },
    }


__all__ = ["load_candidate_decision_summary"]
