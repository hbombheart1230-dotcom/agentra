from __future__ import annotations

import json
from collections import Counter
from datetime import timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

from libs.reporting.evaluation.cost_basis_comparison import build_evaluation_cost_bases
from libs.reporting.evaluation import fast08_qwindow_projection as _qw
from libs.reporting.quant_shadow_forward_outcomes import (
    attach_forward_outcomes,
    load_minute_rows_from_state,
)
from libs.runtime.broker_cost_profile import load_broker_cost_profile


Q16_START_DAY = "2026-07-22"
Q16_CLOSE_DAY = "2026-07-24"
Q16_FINAL_DECISION = "RETAIN"
Q16_FINAL_DECISION_SOURCE = (
    "docs/q13_q14_validation/q16_close_decision_2026-07-24.md"
)
Q17_START_DAY = "2026-07-27"
Q16_HORIZONS = ("+15m", "+30m")
Q17_OBSERVATION_HORIZONS = ("+5m", "+15m", "+30m", "+60m")
KST = timezone(timedelta(hours=9))
Q16_MIN_EXACT_SAMPLES = 20
Q16_MIN_DAYS = 2


def _read(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _candidate_class(row: Mapping[str, Any]) -> str:
    if not bool(row.get("triggered")):
        return ""
    cost_filter = row.get("entry_cost_filter")
    cost_filter = cost_filter if isinstance(cost_filter, Mapping) else {}
    if cost_filter:
        directional_admitted = bool(cost_filter.get("directional_edge_available")) and bool(
            cost_filter.get("passed")
        ) and not bool(row.get("guard_blocked"))
        if directional_admitted:
            return "DIRECTIONAL_ADMITTED"
        proxy_only = bool(cost_filter.get("proxy_edge_available")) and not bool(
            cost_filter.get("directional_edge_available")
        )
        proxy_disallowed = not bool(
            cost_filter.get("allow_triggered_signal_proxy_edge")
            or cost_filter.get("triggered_signal_proxy_edge_allowed")
        )
        rejected = not bool(cost_filter.get("passed"))
        return (
            "EXACT_PROXY_ONLY_REJECTION"
            if proxy_only and proxy_disallowed and rejected and bool(row.get("guard_blocked"))
            else ""
        )
    reason = str(row.get("reason") or "")
    cost_state = str(row.get("entry_quant_cost_floor_state") or "")
    if bool(row.get("guard_blocked")) and "cost_edge_fail" in reason and cost_state == "not_met":
        return "LEGACY_COST_REJECTION_UNATTRIBUTED"
    return ""


def _q17_candidate_class(row: Mapping[str, Any]) -> str:
    if not bool(row.get("triggered")):
        return ""
    estimate = row.get("directional_edge_estimate")
    if not isinstance(estimate, Mapping) or not estimate:
        return "DIRECTIONAL_ESTIMATE_ARTIFACT_MISSING"
    if not bool(estimate.get("available")):
        return "DIRECTIONAL_EVIDENCE_UNAVAILABLE"
    cost_filter = row.get("entry_cost_filter")
    cost_filter = cost_filter if isinstance(cost_filter, Mapping) else {}
    if bool(cost_filter.get("passed")) and not bool(row.get("guard_blocked")):
        return "DIRECTIONAL_ADMITTED"
    fail_reasons = {
        str(value) for value in cost_filter.get("fail_reasons") or []
    }
    if fail_reasons & {
        "estimated_gross_edge_below_cost_floor",
        "cost_adjusted_edge_below_min",
    }:
        return "DIRECTIONAL_BELOW_COST_REJECTION"
    return "DIRECTIONAL_AVAILABLE_OTHER_BLOCK"


def _load_day_rows(reports_root: Path, day: str) -> list[dict[str, Any]]:
    root = reports_root.parent / "data" / "logs" / "quant_shadow_candidates" / day
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for path in sorted(root.glob("*.json")) if root.exists() else []:
        if path.name == "latest.json":
            continue
        payload = _read(path)
        generated_at = str(payload.get("generated_at") or "")
        for raw in payload.get("candidates") or []:
            if not isinstance(raw, Mapping) or str(raw.get("shadow_role") or "") != "top_pick":
                continue
            row = dict(raw)
            candidate_class = _candidate_class(row)
            q17_candidate_class = _q17_candidate_class(row)
            if not candidate_class and not q17_candidate_class:
                continue
            key = (str(row.get("q9_decision_id") or generated_at), str(row.get("symbol") or ""))
            if key in seen:
                continue
            seen.add(key)
            row["q16_candidate_class"] = candidate_class
            row["q17_candidate_class"] = q17_candidate_class
            row["q16_day"] = day
            row.setdefault("_payload_generated_at", generated_at)
            rows.append(row)
    return attach_forward_outcomes(
        rows,
        minute_rows_by_symbol=load_minute_rows_from_state(
            reports_root.parent / "data" / "state.json"
        ),
    )


_metric_bundle = _qw.metric_bundle
_observed_rows = _qw.observed_rows
_epoch_day = _qw.epoch_day
_timestamp_day = _qw.timestamp_day
_forward_integrity = _qw.forward_integrity
_expected_horizon = _qw.expected_horizon


def _q17_expected_horizon_rows(
    rows: list[dict[str, Any]],
    *,
    live_drag: float,
    mock_drag: float,
) -> list[dict[str, Any]]:
    return _qw.expected_horizon_rows(
        rows, live_drag=live_drag, mock_drag=mock_drag, observation_horizons=Q17_OBSERVATION_HORIZONS
    )


def _daily_exact_metrics(rows: list[dict[str, Any]], live_drag: float) -> list[dict[str, Any]]:
    days = sorted({str(row.get("q16_day") or "") for row in rows if row.get("q16_day")})
    daily: list[dict[str, Any]] = []
    for source_day in days:
        day_rows = [row for row in rows if str(row.get("q16_day") or "") == source_day]
        metric = _metric_bundle(day_rows, live_drag, "+30m")["net"]
        count = int(metric.get("count") or 0)
        positive_day = bool(
            count > 0
            and float(metric.get("expectancy_pct") or 0.0) > 0.0
            and float(metric.get("profit_factor") or 0.0) > 1.0
        )
        daily.append(
            {
                "day": source_day,
                "exact_rejection_count": len(day_rows),
                "observed_30m_count": count,
                "live_net_30m": metric,
                "positive_30m_day": positive_day,
            }
        )
    return daily


def _q16_decision(observed_30m: int, daily_exact: list[dict[str, Any]]) -> tuple[bool, str, int, int]:
    observed_day_count = sum(int(row.get("observed_30m_count") or 0) > 0 for row in daily_exact)
    positive_day_count = sum(bool(row.get("positive_30m_day")) for row in daily_exact)
    ready = observed_30m >= Q16_MIN_EXACT_SAMPLES and observed_day_count >= Q16_MIN_DAYS
    if not ready:
        return False, "INSUFFICIENT_EVIDENCE", observed_day_count, positive_day_count
    decision = "ROLL_BACK" if positive_day_count >= Q16_MIN_DAYS else "RETAIN"
    return True, decision, observed_day_count, positive_day_count


def build_q16_proxy_rejection_review(
    *,
    reports_root: Path,
    day: str,
    start_day: str = Q16_START_DAY,
) -> dict[str, Any]:
    reports_root = Path(reports_root)
    day_root = reports_root / "evaluation" / "daily"
    deduped: dict[tuple[str, str, str], dict[str, Any]] = {}

    def _fold(samples) -> None:
        # Folding each file's samples into `deduped` as it is read gives the same dict (same
        # key order, last row per key wins) as collecting every row first and de-duplicating
        # afterwards. Each daily review embeds all earlier days' samples, so collecting first
        # held ~59 overlapping copies (>1 GiB) -- part of the closeout OOM.
        for row in samples:
            key = (
                str(row.get("q16_day") or ""),
                str(row.get("q9_decision_id") or row.get("_payload_generated_at") or ""),
                str(row.get("symbol") or ""),
            )
            deduped[key] = row

    for path in sorted(day_root.glob("*/q16_proxy_rejection_review.json")) if day_root.exists() else []:
        source_day = path.parent.name
        if start_day <= source_day < day:
            prior = _read(path)
            _fold(row for row in prior.get("samples") or [] if isinstance(row, dict))
            del prior
    _fold(_load_day_rows(reports_root, day))
    rows = list(deduped.values())
    for row in rows:
        row.setdefault("q17_candidate_class", _q17_candidate_class(row))
        status, reasons = _forward_integrity(row)
        row["forward_integrity_status"] = status
        row["forward_integrity_reasons"] = reasons
    trusted_rows = [row for row in rows if row.get("forward_integrity_status") == "TRUSTED"]
    integrity_reason_counts = Counter(
        str(reason)
        for row in rows
        if row.get("forward_integrity_status") != "TRUSTED"
        for reason in row.get("forward_integrity_reasons") or []
    )
    exact_all = [row for row in rows if row.get("q16_candidate_class") == "EXACT_PROXY_ONLY_REJECTION"]
    exact = [row for row in trusted_rows if row.get("q16_candidate_class") == "EXACT_PROXY_ONLY_REJECTION"]
    directional_admitted = [row for row in trusted_rows if row.get("q16_candidate_class") == "DIRECTIONAL_ADMITTED"]
    legacy = [row for row in trusted_rows if row.get("q16_candidate_class") == "LEGACY_COST_REJECTION_UNATTRIBUTED"]
    q17_rows = [
        row
        for row in trusted_rows
        if str(row.get("q16_day") or "") >= Q17_START_DAY
        and str(row.get("q17_candidate_class") or "")
    ]
    bases = build_evaluation_cost_bases(load_broker_cost_profile(None))
    live_drag = float(bases["live_deployment_equity"]["total_drag_with_slippage_pct"])
    mock_drag = float(bases["mock_observed"]["total_drag_with_slippage_pct"])
    horizons = _qw.cohort_horizons(
        {
            "exact_proxy_only": exact,
            "legacy_unattributed_cost_rejection": legacy,
            "directional_admitted": directional_admitted,
        },
        Q16_HORIZONS,
        live_drag=live_drag,
        mock_drag=mock_drag,
    )
    observed_30m = int(
        next(row for row in horizons if row["horizon"] == "+30m")["exact_proxy_only"]["live"]["gross"]["count"]
    )
    daily_exact = _daily_exact_metrics(exact, live_drag)
    decision_ready, rolling_diagnostic_decision, observed_day_count, positive_30m_day_count = _q16_decision(
        observed_30m,
        daily_exact,
    )
    decision_is_final = day >= Q16_CLOSE_DAY
    decision = (
        Q16_FINAL_DECISION if decision_is_final else rolling_diagnostic_decision
    )
    if decision_is_final:
        decision_ready = True
    return {
        "schema_version": "q16_proxy_rejection_review.v1",
        "measurement_contract_version": "q16_forward_integrity.v2",
        "behavior_effect": "evaluation_only",
        "start_day": start_day,
        "end_day": day,
        "evidence_status": "DECISION_READY" if decision_ready else "INSUFFICIENT_EVIDENCE",
        "decision": decision,
        "decision_authority": {
            "status": "FINAL_CLOSED" if decision_is_final else "ACTIVE_WINDOW",
            "close_day": Q16_CLOSE_DAY,
            "source": Q16_FINAL_DECISION_SOURCE,
            "rolling_diagnostic_decision": rolling_diagnostic_decision,
            "note": (
                "Post-close samples update diagnostics only and cannot reopen or "
                "reverse the frozen Q16 policy decision."
                if decision_is_final
                else "The fixed Q16 validation window has not closed yet."
            ),
        },
        "decision_rule": {
            "minimum_exact_proxy_only_samples": Q16_MIN_EXACT_SAMPLES,
            "minimum_days": Q16_MIN_DAYS,
            "rollback_requires_positive_30m_expectancy_and_pf_above_one_on_each_minimum_day": True,
            "legacy_unattributed_rows_are_decision_ineligible": True,
        },
        "counts": {
            "exact_proxy_only_rejection_count": len(exact_all),
            "exact_trusted_forward_count": len(exact),
            "forward_integrity_invalid_count": len(rows) - len(trusted_rows),
            "exact_observed_30m_count": observed_30m,
            "exact_observed_day_count": observed_day_count,
            "positive_30m_day_count": positive_30m_day_count,
            "directional_admitted_count": len(directional_admitted),
            "legacy_cost_rejection_unattributed_count": len(legacy),
        },
        "forward_integrity_reason_counts": dict(integrity_reason_counts),
        "cost_bases": bases,
        "horizons": horizons,
        "daily_exact_proxy_only": daily_exact,
        "q17_directional_edge_validation": _qw.q17_validation_block(
            q17_rows,
            start_day=Q17_START_DAY,
            live_drag=live_drag,
            mock_drag=mock_drag,
            observation_horizons=Q17_OBSERVATION_HORIZONS,
        ),
        "samples": rows,
    }


def render_q16_proxy_rejection_review(payload: Mapping[str, Any]) -> str:
    return _qw.render_q16_proxy_rejection_review(payload, default_q17_start=Q17_START_DAY)


__all__ = ["build_q16_proxy_rejection_review", "render_q16_proxy_rejection_review"]
