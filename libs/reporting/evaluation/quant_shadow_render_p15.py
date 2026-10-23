"""Pure Q8 shadow-candidate evaluation Markdown lines (P1.5 DEV-A).

Render-only text for the already built evaluation payload behind
``libs.reporting.quant_shadow_candidate_evaluation``. No payload building, decisions or I/O. ``*_impl`` bodies call
the row formatters and ``_text`` on the injected ``facade`` at call time.
"""
from __future__ import annotations

from typing import Any, List, Mapping, Sequence


def _format_rows_impl(rows: Sequence[Mapping[str, Any]], *, limit: int = 4, facade: Any) -> str:
    parts: List[str] = []
    for row in list(rows)[:limit]:
        name = facade._text(row.get("name"))
        if not name:
            continue
        parts.append(f"{name} ({row.get('count') or 0})")
    return ", ".join(parts) if parts else "none"


def _format_forward_rows_impl(rows: Sequence[Mapping[str, Any]], *, limit: int = 4, facade: Any) -> str:
    parts: List[str] = []
    for row in list(rows)[:limit]:
        name = facade._text(row.get("name"))
        if not name:
            continue
        observed = int(row.get("observed_count") or 0)
        count = int(row.get("candidate_count") or 0)
        ret5 = row.get("avg_return_5m_pct")
        ret15 = row.get("avg_return_15m_pct")
        mfe5 = row.get("avg_mfe_5m_pct")
        mae5 = row.get("avg_mae_5m_pct")
        parts.append(
            f"{name} ({observed}/{count}, "
            f"+5m {float(ret5):.4f}%"
            if ret5 is not None
            else f"{name} ({observed}/{count}, +5m n/a"
        )
        if parts:
            last = parts[-1]
            if ret15 is not None:
                last += f", +15m {float(ret15):.4f}%"
            if mfe5 is not None:
                last += f", mfe5 {float(mfe5):.4f}%"
            if mae5 is not None:
                last += f", mae5 {float(mae5):.4f}%"
            parts[-1] = last + ")"
    return "; ".join(parts) if parts else "none"


def _format_scorecard_rows_impl(rows: Sequence[Mapping[str, Any]], *, limit: int = 4, facade: Any) -> str:
    parts: List[str] = []
    for row in list(rows)[:limit]:
        name = facade._text(row.get("name"))
        if not name:
            continue
        observed = int(row.get("observed_count") or 0)
        count = int(row.get("candidate_count") or 0)
        ret5 = row.get("avg_return_5m_pct")
        ret15 = row.get("avg_return_15m_pct")
        mfe5 = row.get("avg_mfe_5m_pct")
        mae5 = row.get("avg_mae_5m_pct")
        state = facade._text(row.get("review_state"))
        text = (
            f"{name} ({observed}/{count}, "
            f"+5m {float(ret5):.4f}%"
            if ret5 is not None
            else f"{name} ({observed}/{count}, +5m n/a"
        )
        if ret15 is not None:
            text += f", +15m {float(ret15):.4f}%"
        if mfe5 is not None:
            text += f", mfe5 {float(mfe5):.4f}%"
        if mae5 is not None:
            text += f", mae5 {float(mae5):.4f}%"
        if state:
            text += f", state {state}"
        parts.append(text + ")")
    return "; ".join(parts) if parts else "none"


def render_quant_shadow_candidate_evaluation_lines_impl(payload: Mapping[str, Any] | None, *, facade: Any) -> List[str]:
    evaluation = dict(payload or {})
    if not evaluation or int(evaluation.get("candidate_count") or 0) <= 0:
        return []
    lines = [
        "",
        "## Quant Shadow Candidates",
        "",
        "- Q8 shadow candidates: "
        f"{evaluation.get('candidate_count') or 0} candidates / "
        f"deduped {evaluation.get('deduped_candidate_count') or evaluation.get('candidate_count') or 0} / "
        f"duplicates {evaluation.get('duplicate_candidate_count') or 0} / "
        f"{evaluation.get('payload_count') or 0} payloads / "
        f"evaluated {evaluation.get('evaluated_count') or 0} / "
        f"would-enter {evaluation.get('would_enter_count') or 0} / "
        f"opening-probe {evaluation.get('opening_momentum_probe_would_enter_count') or 0} / "
        f"largecap-surge {evaluation.get('opening_largecap_surge_would_enter_count') or 0} / "
        f"guard-blocked {evaluation.get('guard_blocked_count') or 0} "
        f"(actionable {evaluation.get('actionable_guard_blocked_count') or 0})",
        f"- Q8 shadow forward base: {evaluation.get('forward_base_available_count') or 0}/"
        f"{evaluation.get('candidate_count') or 0} candidates have baseline minute price "
        f"(coverage {float(evaluation.get('forward_base_coverage') or 0.0):.1%})",
        f"- Q8 shadow forward outcome: {evaluation.get('forward_outcome_available_count') or 0}/"
        f"{evaluation.get('deduped_candidate_count') or evaluation.get('candidate_count') or 0} deduped candidates have "
        "at least one trusted forward checkpoint "
        f"(coverage {float(evaluation.get('forward_outcome_coverage') or 0.0):.1%})",
        f"- Roles: {facade._format_rows(list(evaluation.get('by_role') or []))}",
        f"- Reasons: {facade._format_rows(list(evaluation.get('by_reason') or []))}",
        f"- Tactics: {facade._format_rows(list(evaluation.get('by_tactic_id') or []))}",
        f"- Suitability: {facade._format_rows(list(evaluation.get('by_tactic_suitability_tier') or []))}",
        f"- Cost floor: {facade._format_rows(list(evaluation.get('by_cost_floor_state') or []))}",
        f"- Failure axis: {facade._format_rows(list(evaluation.get('by_primary_failure_axis') or []))}",
    ]
    trust_gate = (
        evaluation.get("evaluation_trust_gate")
        if isinstance(evaluation.get("evaluation_trust_gate"), Mapping)
        else {}
    )
    if trust_gate:
        lines += [
            "",
            "### Q8 Evaluation Trust Gate",
            "",
            "- Trust gate: "
            f"`{trust_gate.get('status') or 'unknown'}` / "
            f"promotion_allowed `{bool(trust_gate.get('promotion_allowed'))}`",
            "- Trust evidence: "
            f"raw {trust_gate.get('raw_candidate_count') or 0}, "
            f"deduped {trust_gate.get('deduped_candidate_count') or 0}, "
            f"duplicates {trust_gate.get('duplicate_count') or 0} "
            f"({float(trust_gate.get('duplicate_rate') or 0.0):.1%}), "
            f"trusted forward {trust_gate.get('trusted_forward_count') or 0} "
            f"({float(trust_gate.get('trusted_forward_coverage') or 0.0):.1%})",
            f"- Trust block reasons: {', '.join(str(x) for x in list(trust_gate.get('reasons') or [])) or 'none'}",
            "- Promotion-ready candidates: "
            f"{facade._format_scorecard_rows(list(trust_gate.get('promotion_ready_candidates') or []), limit=4)}",
        ]
    readiness = evaluation.get("shadow_readiness") if isinstance(evaluation.get("shadow_readiness"), Mapping) else {}
    if readiness:
        lines.append(
            "- Q8 shadow readiness: "
            f"`{readiness.get('status') or 'not_available'}` / "
            f"action `{readiness.get('action') or 'hold'}` / "
            f"scope `{readiness.get('promotion_scope') or 'none'}` / "
            f"sample {readiness.get('evaluated_count') or 0}/"
            f"{readiness.get('candidate_count') or 0}"
        )
    promotion = evaluation.get("promotion_candidate") if isinstance(evaluation.get("promotion_candidate"), Mapping) else {}
    if promotion:
        lines.append(
            "- Q8 promotion candidate: "
            f"{promotion.get('candidate') or 'hold'} / "
            f"confidence {promotion.get('confidence') or 'none'} / "
            f"{promotion.get('reason') or '-'} / "
            f"action {promotion.get('recommended_action') or 'hold'}"
        )
        if promotion.get("promotion_state"):
            lines.append(
                "- Q8 promotion state: "
                f"{promotion.get('promotion_state') or 'unknown'} / "
                f"effect {promotion.get('behavior_effect') or 'unknown'} / "
                f"guard {promotion.get('active_guard_reason') or '-'}"
            )
        counts = promotion.get("counts") if isinstance(promotion.get("counts"), Mapping) else {}
        if counts:
            lines.append(
                "- Q8 promotion counts: "
                f"cost-edge {counts.get('cost_edge') or 0}, "
                f"runner-up {counts.get('runner_up') or 0}, "
                f"entry-guard {counts.get('entry_guard') or 0}"
            )
    no_trade = evaluation.get("no_trade_scorecard") if isinstance(evaluation.get("no_trade_scorecard"), Mapping) else {}
    if no_trade:
        lines += [
            "",
            "### Q8 No-Trade Scorecard",
            "",
            "- No-trade scorecard: "
            f"`{no_trade.get('status') or 'unknown'}` / "
            f"evidence `{no_trade.get('evidence_quality') or 'unknown'}` / "
            f"forward {no_trade.get('forward_outcome_available_count') or 0}/"
            f"{no_trade.get('candidate_count') or 0} "
            f"({float(no_trade.get('forward_outcome_coverage') or 0.0):.1%})",
            f"- Verdict: {no_trade.get('verdict') or '-'}",
            "- Correctly blocked signals: "
            f"{facade._format_scorecard_rows(list(no_trade.get('correctly_blocked_signals') or []), limit=4)}",
            "- Missed-opportunity candidates: "
            f"{facade._format_scorecard_rows(list(no_trade.get('missed_opportunity_candidates') or []), limit=4)}",
            "- Promotion watchlist: "
            f"{facade._format_scorecard_rows(list(no_trade.get('promotion_watchlist') or []), limit=4)}",
            f"- Next review action: `{no_trade.get('next_review_action') or 'continue_observation'}`",
        ]
    opening_probe = evaluation.get("opening_momentum_probe") if isinstance(evaluation.get("opening_momentum_probe"), Mapping) else {}
    if opening_probe:
        lines += [
            "- Opening momentum probe shadow: "
            f"{opening_probe.get('would_enter_count') or 0}/"
            f"{opening_probe.get('candidate_count') or 0} would-probe "
            f"(observation only)",
            f"- Opening probe reasons: {facade._format_rows(list(opening_probe.get('by_reason') or []))}",
            f"- Opening probe symbols: {facade._format_rows(list(opening_probe.get('by_would_enter_symbol') or []))}",
        ]
        if opening_probe.get("zero_would_enter_explanation"):
            lines.append(f"- Opening probe zero-pass note: {opening_probe.get('zero_would_enter_explanation')}")
    largecap_probe = evaluation.get("opening_largecap_surge") if isinstance(evaluation.get("opening_largecap_surge"), Mapping) else {}
    if largecap_probe:
        lines += [
            "- Opening largecap surge shadow: "
            f"{largecap_probe.get('would_enter_count') or 0}/"
            f"{largecap_probe.get('candidate_count') or 0} would-probe "
            f"(observation only)",
            f"- Opening largecap reasons: {facade._format_rows(list(largecap_probe.get('by_reason') or []))}",
            f"- Opening largecap symbols: {facade._format_rows(list(largecap_probe.get('by_would_enter_symbol') or []))}",
        ]
        if largecap_probe.get("zero_would_enter_explanation"):
            lines.append(f"- Opening largecap zero-pass note: {largecap_probe.get('zero_would_enter_explanation')}")
    entry_shape = evaluation.get("entry_shape_diagnostics") if isinstance(evaluation.get("entry_shape_diagnostics"), Mapping) else {}
    if entry_shape:
        lines += [
            "- Entry shape diagnostics: "
            f"pullback/vwap blocked {entry_shape.get('pullback_or_vwap_blocked_count') or 0}, "
            f"breakout ready-like {entry_shape.get('breakout_ready_like_count') or 0}, "
            f"breakout not-ready {entry_shape.get('breakout_not_ready_count') or 0}",
            f"- Entry shapes: {facade._format_rows(list(entry_shape.get('by_shape') or []))}",
        ]
    entry_lane = (
        evaluation.get("entry_lane_observation")
        if isinstance(evaluation.get("entry_lane_observation"), Mapping)
        else {}
    )
    if entry_lane and int(entry_lane.get("candidate_count") or 0) > 0:
        lines += [
            "- Entry lane observation: "
            f"{entry_lane.get('candidate_count') or 0} candidates / "
            f"{facade._format_rows(list(entry_lane.get('by_primary_lane') or []), limit=8)}",
            f"- Entry lane subtypes: {facade._format_rows(list(entry_lane.get('by_lane_subtype') or []), limit=8)}",
            f"- Entry lane time buckets: {facade._format_rows(list(entry_lane.get('by_time_bucket') or []), limit=6)}",
            f"- Entry lane market rails: {facade._format_rows(list(entry_lane.get('by_market_regime_rail') or []), limit=6)}",
        ]
    lane_forward = (
        evaluation.get("entry_lane_forward_outcomes")
        if isinstance(evaluation.get("entry_lane_forward_outcomes"), Mapping)
        else {}
    )
    if lane_forward:
        lines += [
            "- Entry lane forward outcomes: "
            f"{facade._format_forward_rows(list(lane_forward.get('by_primary_lane') or []), limit=5)}",
            "- Entry lane subtype forward outcomes: "
            f"{facade._format_forward_rows(list(lane_forward.get('by_lane_subtype') or []), limit=5)}",
            "- Entry lane market-rail forward outcomes: "
            f"{facade._format_forward_rows(list(lane_forward.get('by_market_regime_rail') or []), limit=5)}",
        ]
    below_vwap = (
        evaluation.get("below_vwap_reclaim_observation")
        if isinstance(evaluation.get("below_vwap_reclaim_observation"), Mapping)
        else {}
    )
    if below_vwap and int(below_vwap.get("candidate_count") or 0) > 0:
        lines.append(
            "- Below-VWAP reclaim observation: "
            f"{below_vwap.get('candidate_count') or 0} candidates / "
            f"{facade._format_rows(list(below_vwap.get('by_subtype') or []), limit=8)}"
        )
    return lines
