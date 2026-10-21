"""Pure shadow / exit-context projections (P1.5 FAST08 A8.5).

Trade diagnostic predicates, row assembly and the day audit/scorecard roll-ups for
``profitability_recovery_day1``, and macro-input extraction, the unavailable
payload and the Markdown renderer for ``market_regime_rail_review``. Every file
and market-source read, the regime classification thresholds and branches, the
required execution field list, closed-trade and regression rules and all report
writes stay in the original modules. Nothing here decides a trade or a regime.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, List, Mapping, Sequence


# --- A8.5a: profitability recovery diagnostics -----------------------------------------


def safe_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except Exception:
        return None


def is_closed_trade(lifecycle_bundle: Dict[str, Any]) -> bool:
    status = str(lifecycle_bundle.get("trade_lifecycle_status") or lifecycle_bundle.get("status") or "").strip().lower()
    if status == "closed":
        return True
    exit_obj = lifecycle_bundle.get("exit") if isinstance(lifecycle_bundle.get("exit"), dict) else {}
    return str(exit_obj.get("action") or "").strip().upper() == "SELL"


def linkage_surface_present(linkage: Dict[str, Any]) -> bool:
    if not linkage:
        return False
    status = str(linkage.get("status") or "").strip().lower()
    reason = str(linkage.get("linkage_reason") or "").strip()
    return bool(status) and (status != "missing" or bool(reason))


def execution_missing_fields(execution_details: Dict[str, Any], required: Sequence[str]) -> List[str]:
    execution_details = execution_details if isinstance(execution_details, dict) else {}
    return [
        str(key)
        for key in required
        if key not in execution_details or execution_details.get(key) in (None, "", [])
    ]


def bundle_artifacts(lifecycle_bundle: Dict[str, Any]) -> Dict[str, Any]:
    artifacts = lifecycle_bundle.get("artifacts")
    return artifacts if isinstance(artifacts, dict) else {}


def section_provenance(lifecycle_bundle: Dict[str, Any]) -> Dict[str, Any]:
    value = lifecycle_bundle.get("section_provenance")
    return value if isinstance(value, dict) else {}


def resolve_ai_trade_report_status(
    lifecycle_bundle: Dict[str, Any], ai_component: Dict[str, Any], ai_trade_report_llm_exists: bool
) -> str:
    diagnostics = lifecycle_bundle.get("ai_report_diagnostics")
    diagnostics = diagnostics if isinstance(diagnostics, dict) else {}
    for candidate in (
        ai_component.get("status"),
        diagnostics.get("ai_trade_report_status"),
        lifecycle_bundle.get("ai_trade_report_status"),
    ):
        value = str(candidate or "").strip().lower()
        if value:
            return value
    return "ok" if ai_trade_report_llm_exists else ""


def is_closed_trade_report_generation_regression(*, closed_trade: bool, ai_trade_report_llm_exists: bool, ai_status: str) -> bool:
    if not closed_trade:
        return False
    if not ai_trade_report_llm_exists:
        return True
    normalized = str(ai_status or "").strip().lower()
    if not normalized:
        return False
    return normalized in {"failed", "error", "skipped"}


def diagnostic_row(
    *,
    trade_dir_name: str,
    day_dir_name: str,
    lifecycle_bundle: Dict[str, Any],
    lifecycle_path: Any,
    generation_state_path: Any,
    same_day_linkage: Dict[str, Any],
    holding_evidence: Dict[str, Any],
    execution_details: Dict[str, Any],
    ai_trade_report_llm_exists: bool,
    ai_status: str,
    required_execution_fields: Sequence[str],
) -> Dict[str, Any]:
    holding_phase_summary = str(holding_evidence.get("holding_phase_summary") or "").strip()
    hold_events_count = int(holding_evidence.get("hold_events_count") or 0)
    monitor_context_snapshots = [
        dict(row) for row in list(holding_evidence.get("monitor_context_snapshots") or []) if isinstance(row, dict)
    ]
    closed_trade = is_closed_trade(lifecycle_bundle)
    story_contract = lifecycle_bundle.get("story_contract") if isinstance(lifecycle_bundle.get("story_contract"), dict) else {}
    story_type = str(lifecycle_bundle.get("story_type") or story_contract.get("story_type") or "").strip().lower()
    outcome = lifecycle_bundle.get("trade_outcome") if isinstance(lifecycle_bundle.get("trade_outcome"), dict) else {}
    return_pct = safe_float(outcome.get("return_pct"))
    missing = execution_missing_fields(execution_details, required_execution_fields)
    return {
        "trade_id": str(lifecycle_bundle.get("trade_id") or trade_dir_name),
        "day": str(lifecycle_bundle.get("day") or day_dir_name),
        "symbol": str(lifecycle_bundle.get("symbol") or ""),
        "story_type": story_type,
        "lifecycle_status": str(lifecycle_bundle.get("trade_lifecycle_status") or lifecycle_bundle.get("status") or ""),
        "closed_trade": closed_trade,
        "loss_trade": bool(return_pct is not None and return_pct < 0),
        "return_pct": return_pct,
        "hold_duration": str(holding_evidence.get("hold_duration") or ""),
        "hold_duration_sec": holding_evidence.get("hold_duration_sec"),
        "holding_evidence_thin": bool(
            lifecycle_bundle.get("hold_evidence_thin")
            or hold_events_count <= 0
            or (not monitor_context_snapshots and not holding_phase_summary)
        ),
        "holding_phase_summary": holding_phase_summary,
        "hold_events_count": hold_events_count,
        "monitor_context_snapshots_count": len(monitor_context_snapshots),
        "same_day_linkage_status": str(same_day_linkage.get("status") or ""),
        "same_day_linkage_reason": str(same_day_linkage.get("linkage_reason") or ""),
        "same_day_linkage_missing": not linkage_surface_present(same_day_linkage),
        "execution_fields_missing": missing,
        "execution_missing_fields_count": len(missing),
        "ai_trade_report_llm_response_exists": ai_trade_report_llm_exists,
        "ai_trade_report_status": ai_status,
        "closed_trade_report_generation_regression": is_closed_trade_report_generation_regression(
            closed_trade=closed_trade, ai_trade_report_llm_exists=ai_trade_report_llm_exists, ai_status=ai_status
        ),
        "closed_trade_decision_only_misclassification": bool(closed_trade and story_type == "decision_only"),
        "report_generation_state_path": str(generation_state_path),
        "lifecycle_bundle_path": str(lifecycle_path),
    }


def top_recurring_weakness(rows: Iterable[Dict[str, Any]]) -> str:
    counter: Counter[str] = Counter()
    for row in rows:
        if bool(row.get("closed_trade_report_generation_regression")):
            counter["closed_trade_report_generation_regression"] += 1
        if bool(row.get("closed_trade_decision_only_misclassification")):
            counter["closed_trade_decision_only_misclassification"] += 1
        if bool(row.get("holding_evidence_thin")):
            counter["holding_evidence_thin"] += 1
        if bool(row.get("same_day_linkage_missing")):
            counter["same_day_linkage_missing"] += 1
        if int(row.get("execution_missing_fields_count") or 0) > 0:
            counter["execution_fields_missing"] += 1
    if not counter:
        return "none"
    return str(counter.most_common(1)[0][0])


def day_audit(day: str, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "schema_version": "profitability_recovery_day1_audit.v1",
        "day": str(day),
        "trade_count": len(rows),
        "closed_trade_count": sum(1 for row in rows if bool(row.get("closed_trade"))),
        "closed_trade_report_generation_regression_count": sum(
            1 for row in rows if bool(row.get("closed_trade_report_generation_regression"))
        ),
        "closed_trade_decision_only_misclassification_count": sum(
            1 for row in rows if bool(row.get("closed_trade_decision_only_misclassification"))
        ),
        "holding_evidence_thin_count": sum(1 for row in rows if bool(row.get("holding_evidence_thin"))),
        "same_day_linkage_missing_count": sum(1 for row in rows if bool(row.get("same_day_linkage_missing"))),
        "execution_fields_missing_count": sum(int(row.get("execution_missing_fields_count") or 0) for row in rows),
        "top_recurring_diagnostic_weakness": top_recurring_weakness(rows),
        "rows": rows,
    }


def day_scorecard(day: str, audit: Mapping[str, Any]) -> Dict[str, Any]:
    rows = list(audit.get("rows") or [])
    return {
        "schema_version": "daily_profitability_scorecard.v1",
        "day": str(day),
        "total_trades": int(audit.get("trade_count") or 0),
        "closed_trades": int(audit.get("closed_trade_count") or 0),
        "loss_trades": sum(1 for row in rows if bool(row.get("loss_trade"))),
        "lifecycle_linkage_missing_count": int(audit.get("same_day_linkage_missing_count") or 0),
        "holding_evidence_thin_count": int(audit.get("holding_evidence_thin_count") or 0),
        "execution_fields_missing_count": int(audit.get("execution_fields_missing_count") or 0),
        "closed_trade_report_generation_regression_count": int(
            audit.get("closed_trade_report_generation_regression_count") or 0
        ),
        "closed_trade_decision_only_misclassification_count": int(
            audit.get("closed_trade_decision_only_misclassification_count") or 0
        ),
        "top_recurring_diagnostic_weakness": str(audit.get("top_recurring_diagnostic_weakness") or "none"),
        "rows": rows,
    }


# --- A8.5b: market regime rail inputs and rendering -------------------------------------


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def indicator(snapshot: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    macro = snapshot.get("macro_indicators") if isinstance(snapshot.get("macro_indicators"), Mapping) else {}
    indicators = macro.get("indicators") if isinstance(macro.get("indicators"), Mapping) else {}
    return indicators.get(key) if isinstance(indicators.get(key), Mapping) else {}


def change_pct(snapshot: Mapping[str, Any], key: str) -> float:
    index_moves = snapshot.get("index_moves") if isinstance(snapshot.get("index_moves"), Mapping) else {}
    move_key = f"{key}_pct"
    if move_key in index_moves:
        return to_float(index_moves.get(move_key), 0.0)
    return to_float(indicator(snapshot, key).get("change_pct"), 0.0)


def unavailable_rail() -> Dict[str, Any]:
    return {
        "schema_version": "market_regime_rail_observation.v1",
        "behavior_effect": "evaluation_only",
        "available": False,
        "rail_id": "not_available",
        "rail_confidence": "none",
        "rationale": "macro snapshot unavailable",
        "market_inputs": {},
        "expected_tactical_behavior": [],
        "q8_review_focus": [],
    }


def market_inputs(snapshot: Mapping[str, Any]) -> Dict[str, Any]:
    """Numeric macro/market inputs read from one snapshot; missing values read as 0.0 / ''."""
    korea = snapshot.get("korea_indices") if isinstance(snapshot.get("korea_indices"), Mapping) else {}
    macro_moves = snapshot.get("macro_moves") if isinstance(snapshot.get("macro_moves"), Mapping) else {}
    global_sentiment = snapshot.get("global_sentiment") if isinstance(snapshot.get("global_sentiment"), Mapping) else {}
    inputs: Dict[str, Any] = {
        "kospi_pct": change_pct(snapshot, "kospi"),
        "kosdaq_pct": change_pct(snapshot, "kosdaq"),
        "kospi200_pct": change_pct(snapshot, "kospi200"),
        "krx_night_futures_pct": change_pct(snapshot, "krx_night_futures"),
        "breadth": to_float(korea.get("breadth"), 0.0),
        "nasdaq_pct": change_pct(snapshot, "nasdaq"),
        "sp500_pct": change_pct(snapshot, "sp500"),
        "dxy_pct": to_float(macro_moves.get("dxy_pct"), to_float(indicator(snapshot, "dxy").get("change_pct"), 0.0)),
        "usdkrw_pct": to_float(indicator(snapshot, "usdkrw").get("change_pct"), 0.0),
        "vix_level": to_float(macro_moves.get("vix_level"), 0.0),
        "vix_pct": to_float(macro_moves.get("vix_pct"), 0.0),
        "us_10y_delta": to_float(indicator(snapshot, "us_10y_yield").get("delta"), 0.0),
        "global_sentiment_score": to_float(global_sentiment.get("score"), 0.0),
    }
    night = snapshot.get("krx_night_futures") if isinstance(snapshot.get("krx_night_futures"), Mapping) else {}
    inputs["krx_night_futures_status"] = str(night.get("status") or indicator(snapshot, "krx_night_futures").get("status") or "")
    inputs["krx_night_futures_pressure"] = str(
        night.get("direction_pressure") or indicator(snapshot, "krx_night_futures").get("direction_pressure") or ""
    )
    return inputs


def render_market_regime_rail_markdown(rail: Mapping[str, Any], *, day: str) -> str:
    inputs = rail.get("market_inputs") if isinstance(rail.get("market_inputs"), Mapping) else {}
    lines = [
        f"# Market Regime Rail Review ({day})",
        "",
        "This report is read-only evaluation output. It does not change trading behavior.",
        "",
        "## Rail",
        "",
        f"- rail_id: `{rail.get('rail_id') or 'not_available'}`",
        f"- confidence: `{rail.get('rail_confidence') or 'none'}`",
        f"- behavior_effect: `{rail.get('behavior_effect') or 'evaluation_only'}`",
        f"- source: `{rail.get('source') or '-'}`",
        f"- rationale: {rail.get('rationale') or '-'}",
        "",
        "## Market Inputs",
        "",
    ]
    for key in (
        "kospi_pct",
        "kosdaq_pct",
        "kospi200_pct",
        "krx_night_futures_pct",
        "breadth",
        "nasdaq_pct",
        "sp500_pct",
        "usdkrw_pct",
        "dxy_pct",
        "vix_level",
        "vix_pct",
        "global_sentiment_score",
    ):
        lines.append(f"- {key}: **{float(inputs.get(key) or 0.0):.4f}**")
    if inputs.get("krx_night_futures_status") or inputs.get("krx_night_futures_pressure"):
        lines.append(f"- krx_night_futures_status: `{inputs.get('krx_night_futures_status') or '-'}`")
        lines.append(f"- krx_night_futures_pressure: `{inputs.get('krx_night_futures_pressure') or '-'}`")
    sanity = rail.get("market_input_sanity") if isinstance(rail.get("market_input_sanity"), Mapping) else {}
    warnings = sanity.get("warnings") if isinstance(sanity.get("warnings"), list) else []
    if warnings:
        lines += ["", "## Market Input Sanity", ""]
        lines.append(f"- status: `{sanity.get('status') or 'warning'}`")
        lines.append(f"- extreme_move_requires_confirmation: `{bool(sanity.get('extreme_move_requires_confirmation'))}`")
        for row in warnings[:8]:
            if not isinstance(row, Mapping):
                continue
            lines.append(
                "- warning: "
                f"`{row.get('code')}` {row.get('index') or '-'} "
                f"change_pct={float(row.get('change_pct') or 0.0):.4f} "
                f"severity=`{row.get('severity') or '-'}`"
            )
    lines += ["", "## Expected Tactical Behavior", ""]
    for item in list(rail.get("expected_tactical_behavior") or []):
        lines.append(f"- {item}")
    lines += ["", "## Q8 Review Focus", ""]
    for item in list(rail.get("q8_review_focus") or []):
        lines.append(f"- `{item}`")
    return "\n".join(lines).rstrip() + "\n"
