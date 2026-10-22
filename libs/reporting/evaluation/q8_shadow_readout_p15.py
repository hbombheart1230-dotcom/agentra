"""Pure Q8 shadow-blocker group readout and lane verdict composition (P1.5 DEV-A).

Shared by ``libs.reporting.q8_shadow_blocker_review`` (per-reason forward summaries) and
``libs.reporting.q8_lane_decision_table`` (lane verdict rows). Payload loading, forward-outcome
attachment, canonical dedupe, trust-gate construction, rendering and writes stay in those facades;
the trust thresholds are read from the READ-ONLY ``q8_evaluation_contract``.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Sequence

from libs.reporting.q8_evaluation_contract import TRUSTED_FORWARD_MIN_COVERAGE


def _text(value: Any) -> str:
    return str(value or "").strip()


# --- shadow blocker review -------------------------------------------------------------------------


def _to_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except Exception:
        return None


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def _checkpoint_values(outcome: Mapping[str, Any]) -> Dict[str, Any]:
    checkpoints = outcome.get("checkpoints") if isinstance(outcome.get("checkpoints"), Mapping) else {}
    observed: List[Mapping[str, Any]] = [
        checkpoint
        for checkpoint in checkpoints.values()
        if isinstance(checkpoint, Mapping) and str(checkpoint.get("status") or "") == "observed"
    ]
    if not observed:
        return {"available": False}
    returns = [_to_float(row.get("return_pct")) for row in observed]
    mfes = [_to_float(row.get("mfe_pct")) for row in observed]
    maes = [_to_float(row.get("mae_pct")) for row in observed]
    returns = [value for value in returns if value is not None]
    mfes = [value for value in mfes if value is not None]
    maes = [value for value in maes if value is not None]
    latest = returns[-1] if returns else None
    return {
        "available": True,
        "latest_return_pct": latest,
        "max_favorable_pct": max(mfes) if mfes else None,
        "max_adverse_pct": min(maes) if maes else None,
    }


def _avg(values: Sequence[float]) -> float:
    return round(sum(values) / len(values), 4) if values else 0.0


def _decision_for_row(row: Mapping[str, Any]) -> str:
    reason = _text(row.get("reason"))
    if reason == "volume_confirmation_missing":
        return "retain_under_observation"
    if reason in {"breakout_not_ready", "pullback_not_mature"}:
        return "adjust_and_retest"
    if reason == "human_chart_sanity_guard_blocked":
        return "promotion_review_target"
    return "retain_under_observation"


def _summarize_group(
    reason: str,
    rows: Sequence[Mapping[str, Any]],
    *,
    promotion_allowed: bool,
) -> Dict[str, Any]:
    observed_rows: List[Dict[str, Any]] = []
    for row in rows:
        outcome = row.get("shadow_forward_outcome") if isinstance(row.get("shadow_forward_outcome"), Mapping) else {}
        values = _checkpoint_values(outcome)
        if values.get("available"):
            observed_rows.append({**dict(row), "_q8_forward": values})
    latest_returns = [
        float(row["_q8_forward"]["latest_return_pct"])
        for row in observed_rows
        if row["_q8_forward"].get("latest_return_pct") is not None
    ]
    mfes = [
        float(row["_q8_forward"]["max_favorable_pct"])
        for row in observed_rows
        if row["_q8_forward"].get("max_favorable_pct") is not None
    ]
    maes = [
        float(row["_q8_forward"]["max_adverse_pct"])
        for row in observed_rows
        if row["_q8_forward"].get("max_adverse_pct") is not None
    ]
    positive_count = sum(1 for value in latest_returns if value > 0)
    missed_opportunity_count = sum(1 for value in mfes if value >= 1.0)
    adverse_count = sum(1 for value in maes if value <= -0.5)
    examples = sorted(
        observed_rows,
        key=lambda row: float(row["_q8_forward"].get("max_favorable_pct") or 0.0),
        reverse=True,
    )[:5]
    raw_decision = _decision_for_row(rows[0]) if rows else "retain_under_observation"
    decision = raw_decision if promotion_allowed else "retain_under_observation"
    return {
        "reason": reason,
        "candidate_count": len(rows),
        "observed_count": len(observed_rows),
        "coverage": round(float(len(observed_rows)) / float(len(rows)), 4) if rows else 0.0,
        "avg_latest_return_pct": _avg(latest_returns),
        "avg_max_favorable_pct": _avg(mfes),
        "avg_max_adverse_pct": _avg(maes),
        "positive_latest_count": positive_count,
        "positive_latest_rate": round(float(positive_count) / float(len(latest_returns)), 4) if latest_returns else 0.0,
        "missed_opportunity_count": missed_opportunity_count,
        "missed_opportunity_rate": round(float(missed_opportunity_count) / float(len(mfes)), 4) if mfes else 0.0,
        "adverse_count": adverse_count,
        "adverse_rate": round(float(adverse_count) / float(len(maes)), 4) if maes else 0.0,
        "raw_decision": raw_decision,
        "decision": decision,
        "decision_blocked_by_trust_gate": bool(raw_decision != decision),
        "examples": [
            {
                "symbol": _text(row.get("symbol")),
                "role": _text(row.get("shadow_role")),
                "rank": row.get("rank"),
                "tactic_id": _text(row.get("quant_tactic_id")),
                "latest_return_pct": row["_q8_forward"].get("latest_return_pct"),
                "max_favorable_pct": row["_q8_forward"].get("max_favorable_pct"),
                "max_adverse_pct": row["_q8_forward"].get("max_adverse_pct"),
            }
            for row in examples
        ],
    }


# --- lane decision table ---------------------------------------------------------------------------


def _float(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def _int(value: Any, default: int = 0) -> int:
    try:
        if value in (None, ""):
            return int(default)
        return int(float(value))
    except Exception:
        return int(default)


def _rows(value: Any) -> List[Dict[str, Any]]:
    return [dict(row) for row in list(value or []) if isinstance(row, Mapping)]


def _forward_rows(evaluation: Mapping[str, Any]) -> List[Dict[str, Any]]:
    forward = evaluation.get("entry_lane_forward_outcomes")
    if not isinstance(forward, Mapping):
        return []
    return _rows(forward.get("by_primary_lane"))


def _counts_by_name(rows: Iterable[Mapping[str, Any]]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for row in rows:
        name = _text(row.get("name"))
        if name:
            out[name] = _int(row.get("count"))
    return out


def _reason_summary(evaluation: Mapping[str, Any], *, limit: int = 6) -> str:
    parts = []
    for row in _rows(evaluation.get("by_reason"))[:limit]:
        name = _text(row.get("name"))
        if name:
            parts.append(f"{name} {row.get('count') or 0}")
    return ", ".join(parts) if parts else "-"


def _verdict(row: Mapping[str, Any], *, promotion_allowed: bool) -> Dict[str, str]:
    observed = _int(row.get("observed_count"))
    coverage = _float(row.get("coverage"))
    ret5 = _float(row.get("avg_return_5m_pct"))
    ret15 = _float(row.get("avg_return_15m_pct"))
    mfe5 = _float(row.get("avg_mfe_5m_pct"))
    mae5 = _float(row.get("avg_mae_5m_pct"))
    lane = _text(row.get("name"))

    if not promotion_allowed:
        return {
            "verdict": "TRUST_GATE_BLOCKED",
            "decision": "retain under observation",
            "rationale": "Q8 trust gate blocked promotion review; lane signal is diagnostic only.",
        }
    if observed < 10 or coverage < TRUSTED_FORWARD_MIN_COVERAGE:
        return {
            "verdict": "DATA_INCOMPLETE",
            "decision": "observe",
            "rationale": "sample or trusted forward coverage is insufficient.",
        }
    if lane == "vwap_reclaim" and ret5 < 0.0 and ret15 < 0.0:
        return {
            "verdict": "GOOD_BLOCK",
            "decision": "keep blocked",
            "rationale": "VWAP reclaim lane showed weak short/mid forward returns.",
        }
    if ret5 >= 0.50 or ret15 >= 0.80 or mfe5 >= 1.50:
        risk_note = " MAE is high, so only small probe or rule review is allowed." if mae5 <= -1.50 else ""
        return {
            "verdict": "MISSED_OPPORTUNITY",
            "decision": "relaxation candidate",
            "rationale": f"Blocked candidates showed positive forward potential.{risk_note}".strip(),
        }
    if ret5 <= 0.0 and ret15 <= 0.0:
        return {
            "verdict": "GOOD_BLOCK",
            "decision": "keep blocked",
            "rationale": "Blocked candidates showed weak forward returns.",
        }
    return {
        "verdict": "DATA_INCOMPLETE",
        "decision": "observe",
        "rationale": "Signal direction is not decisive enough for a policy review.",
    }


_VERDICT_ORDER = {
    "TRUST_GATE_BLOCKED": 0,
    "MISSED_OPPORTUNITY": 1,
    "BAD_ENTRY": 2,
    "GOOD_BLOCK": 3,
    "DATA_INCOMPLETE": 4,
}


def lane_decision_table_payload(evaluation: Mapping[str, Any], *, day: str) -> Dict[str, Any]:
    """Compose the ``q8_lane_decision_table.v1`` payload from an already built shadow evaluation."""
    trust_gate = evaluation.get("evaluation_trust_gate") if isinstance(evaluation.get("evaluation_trust_gate"), Mapping) else {}
    promotion_allowed = bool(trust_gate.get("promotion_allowed"))
    lane_observation = evaluation.get("entry_lane_observation")
    lane_counts = _counts_by_name(
        _rows(lane_observation.get("by_primary_lane") if isinstance(lane_observation, Mapping) else [])
    )
    rows: List[Dict[str, Any]] = []
    for row in _forward_rows(evaluation):
        verdict = _verdict(row, promotion_allowed=promotion_allowed)
        lane = _text(row.get("name"))
        rows.append(
            {
                "lane": lane,
                "candidate_count": _int(row.get("candidate_count")),
                "observed_count": _int(row.get("observed_count")),
                "coverage": round(_float(row.get("coverage")), 4),
                "shadow_count": lane_counts.get(lane, _int(row.get("candidate_count"))),
                "avg_return_3m_pct": row.get("avg_return_3m_pct"),
                "avg_return_5m_pct": row.get("avg_return_5m_pct"),
                "avg_return_15m_pct": row.get("avg_return_15m_pct"),
                "avg_return_30m_pct": row.get("avg_return_30m_pct"),
                "avg_return_60m_pct": row.get("avg_return_60m_pct"),
                "avg_mfe_5m_pct": row.get("avg_mfe_5m_pct"),
                "avg_mae_5m_pct": row.get("avg_mae_5m_pct"),
                **verdict,
            }
        )
    rows.sort(key=lambda item: (_VERDICT_ORDER.get(str(item.get("verdict")), 9), -_int(item.get("observed_count"))))
    return {
        "schema_version": "q8_lane_decision_table.v1",
        "day": str(day)[:10],
        "payload_count": _int(evaluation.get("payload_count")),
        "candidate_count": _int(evaluation.get("candidate_count")),
        "deduped_candidate_count": _int(evaluation.get("deduped_candidate_count")),
        "duplicate_candidate_count": _int(evaluation.get("duplicate_candidate_count")),
        "dedupe_key": list(evaluation.get("dedupe_key") or []),
        "evaluated_count": _int(evaluation.get("evaluated_count")),
        "forward_outcome_available_count": _int(evaluation.get("forward_outcome_available_count")),
        "forward_outcome_coverage": round(_float(evaluation.get("forward_outcome_coverage")), 4),
        "evaluation_trust_gate": dict(trust_gate),
        "promotion_allowed": promotion_allowed,
        "would_enter_count": _int(evaluation.get("would_enter_count")),
        "reason_summary": _reason_summary(evaluation),
        "rows": rows,
    }
