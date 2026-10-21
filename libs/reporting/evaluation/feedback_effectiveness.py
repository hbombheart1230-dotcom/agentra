from __future__ import annotations

from typing import Any

from . import fast08_cumulative_projection as _cp
from .contracts import CONTRACT_VERSION, DecisionClass


def build_feedback_effectiveness(
    trade_models: list[dict[str, Any]],
    q9_windows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    exposed = 0
    adopted = 0
    records: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for window in list(q9_windows or []):
        record = _cp.feedback_window_record(window)
        if record is None:
            continue
        identity = (record["feedback_id"], record["later_decision_id"])
        if identity in seen:
            continue
        seen.add(identity)
        exposed += 1
        adopted += int(record["adoption_candidate"])
        records.append(record)
    for model in trade_models:
        feedback_source = _cp.feedback_model_source(model)
        if not feedback_source:
            continue
        identity = (feedback_source, str(model.get("trade_id") or ""))
        if identity in seen:
            continue
        seen.add(identity)
        exposed += 1
        records.append(
            {
                "trade_id": model.get("trade_id"),
                "feedback_source": feedback_source,
                "adopted": False,
                "performance_delta_pct": None,
            }
        )
    return {
        "schema_version": "feedback_effectiveness.v1",
        "contract_version": CONTRACT_VERSION,
        "decision_class": DecisionClass.INSUFFICIENT_EVIDENCE.value,
        "exposure_count": exposed,
        "adoption_count": adopted,
        "adoption_rate": round(adopted / exposed, 4) if exposed else 0.0,
        "usefulness_score": None,
        "records": records,
        "provenance_linkage_status": "ACTIVE" if records else "AWAITING_NEW_RUNTIME_ARTIFACTS",
        "missing_requirement": "paired feedback-disabled control outcomes for causal performance delta",
        "causal_claim_allowed": False,
    }
