from __future__ import annotations

import json
import os
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from libs.llm.model_catalog import resolve_policy_llm_execution_slot, resolve_policy_llm_slot
from libs.llm.model_names import normalize_openrouter_model_name
from libs.reporting.event_log_reader import iter_jsonl_events
from libs.reporting.llm_artifacts import daily_artifact_paths
from libs.reporting.narrative_axes import build_narrative_explanation, narrative_axis_policy
from libs.reporting.operator_candidate_decisions import load_candidate_decision_summary
from libs.reporting.controlled_validation_daily import (
    build_controlled_validation_daily,
    render_controlled_validation_daily_lines,
)
from libs.reporting.report_metadata import (
    build_data_freshness,
    build_route_provenance,
    render_data_freshness_markdown,
)
from libs.reporting.report_source_helpers import (
    build_commander_route_summary,
    build_policy_surface_quality_snapshot,
)
import sys as _r3_sys
from libs.reporting.operator_visibility_parts.summary_snapshot_and_bundle import (
    build_operator_summary_snapshot_from_payload_r3_impl,
    build_separated_operator_brief_r3_impl,
    generate_operator_visibility_bundle_r3_impl,
    _run_context_default_r3_impl,
    _build_report_freshness_r3_impl,
    _canonical_report_root_r3_impl,
    _apply_commander_route_overlay_r3_impl,
    _merge_scanner_handoff_with_selection_r3_impl,
    _is_trade_story_r3_impl,
    _iter_day_rows_with_epoch_r3_impl,
)
from libs.reporting.operator_visibility_parts.reason_text_and_time import (
    _story_explanation_r3_impl,
    _normalize_reason_code_r3_impl,
    _humanize_reason_r3_impl,
    _reason_text_r3_impl,
    _render_reason_top_r3_impl,
    _format_reason_rows_r3_impl,
    _decision_axis_r3_impl,
    _to_epoch_r3_impl,
    _epoch_to_iso_r3_impl,
    _compact_kv_text_r3_impl,
    _broker_code_success_r3_impl,
    _compact_distance_to_ready_text_r3_impl,
)
import sys as _visibility_sys
from libs.agents.reporter.read_models import operator_daily_projection as _visibility_projection
from libs.agents.reporter.read_models import operator_run_context_projection as _run_context_projection


_REASON_LABELS: Dict[str, str] = {
    "none": "none",
    "unspecified": "UNSPECIFIED",
    "NO_CANDIDATE": "NO_CANDIDATE (no candidate met entry conditions)",
    "MARKET_CLOSED": "MARKET_CLOSED (outside session window)",
    "GUARD_BLOCK": "GUARD_BLOCK (blocked by safety guard)",
    "noop_intent_skipped": "NOOP intent skipped (no order sent)",
    "denied_by_test": "Blocked by supervisor test rule",
    "duplicate_buy_position_exists": "Blocked duplicate buy (position already open)",
    "duplicate_buy_recent_order_exists": "Blocked duplicate buy (recent same-symbol order still pending reflection)",
    "insufficient_mock_cash": "Insufficient mock cash",
    "position_already_open": "Position already open",
    "model_no_signal": "Model returned no trade signal",
    "missing_rationale": "Trade rationale missing",
    "strategist_error": "Strategist runtime error",
    "post_exit_cooldown": "Post-exit cooldown active",
    "strategy_v1_noop": "Strategy-v1 returned NOOP",
    "conditions_not_met": "Rule entry conditions not met",
}


def _write_operator_markdown(path: Path, text: str) -> None:
    path.write_text(str(text or ""), encoding="utf-8-sig", newline="\n")


def _to_epoch(ts: Any) -> Optional[int]:
    return _to_epoch_r3_impl(ts, facade=_r3_sys.modules[__name__])


def _utc_day(ts: Any) -> Optional[str]:
    epoch = _to_epoch(ts)
    if epoch is None:
        return None
    return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("%Y-%m-%d")


def _iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []

    def _gen() -> Iterable[Dict[str, Any]]:
        with path.open("r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if isinstance(obj, dict):
                    yield obj

    return _gen()


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return obj if isinstance(obj, dict) else {}


def _safe_int(v: Any, default: int = 0) -> int:
    try:
        return int(float(v))
    except Exception:
        return int(default)


def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return float(default)


def _pick_day(rows: List[Dict[str, Any]], requested_day: Optional[str]) -> str:
    if requested_day:
        return str(requested_day).strip()
    days = sorted({str(r.get("_day")) for r in rows if r.get("_day")})
    if days:
        return days[-1]
    return date.today().isoformat()


def _find_day_artifact(base_dir: Path, prefix: str, day: str) -> Dict[str, Any]:
    path = base_dir / f"{prefix}_{day}.json"
    return _read_json(path)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _epoch_to_iso(epoch: Any) -> str:
    return _epoch_to_iso_r3_impl(epoch, facade=_r3_sys.modules[__name__])


def _build_report_freshness(day_rows: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    # Single streaming pass (day_rows may be a one-shot iterator) -- was two
    # separate passes over a materialized list before the OOM RCA follow-up.
    return _build_report_freshness_r3_impl(day_rows, facade=_r3_sys.modules[__name__])

def _load_or_build_metrics(events_path: Path, metrics_report_dir: Path, day: str) -> Dict[str, Any]:
    metrics_report_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = metrics_report_dir / f"metrics_{day}.json"
    obj = _read_json(metrics_path)
    if obj:
        return obj

    try:
        from libs.reporting.metrics_report_generator import generate_metrics_report

        _, js = generate_metrics_report(events_path, metrics_report_dir, day=day)
        return _read_json(js)
    except Exception:
        return {}


def _build_trading_health_status(reports_root: Path, day: str) -> Dict[str, Any]:
    summary_path = Path(reports_root) / "performance" / str(day or "").strip() / "summary.json"
    summary = _read_json(summary_path)
    sample_count = _safe_int(summary.get("return_sample_count"), 0)
    total_trades = _safe_int(summary.get("total_trades"), 0)
    win_rate = _safe_float(summary.get("win_rate"), 0.0)
    avg_return = _safe_float(summary.get("avg_return"), 0.0)
    profit_factor = _safe_float(summary.get("profit_factor"), 0.0)
    level = "GREEN"
    reasons: List[str] = []
    if not summary:
        level = "UNKNOWN"
        reasons.append("performance summary artifact is missing")
    elif sample_count <= 0:
        level = "UNKNOWN"
        reasons.append("no realized return samples; trading performance is not evaluable")
    elif sample_count >= 3 and (win_rate < 0.25 or avg_return <= -0.008):
        level = "RED"
        reasons.append(
            f"trade performance weak: sample={sample_count}, win_rate={win_rate:.2%}, avg_return={avg_return:.2%}"
        )
    elif avg_return < 0.0 or (sample_count >= 2 and win_rate < 0.40):
        level = "YELLOW"
        reasons.append(
            f"trade performance watch: sample={sample_count}, win_rate={win_rate:.2%}, avg_return={avg_return:.2%}"
        )
    else:
        reasons.append(
            f"trade performance acceptable: sample={sample_count}, win_rate={win_rate:.2%}, avg_return={avg_return:.2%}"
        )
    return {
        "schema_version": "trading_health_status.v1",
        "trading_health_level": level,
        "sample_count": int(sample_count),
        "total_trades": int(total_trades),
        "win_rate": float(win_rate),
        "avg_return": float(avg_return),
        "profit_factor": float(profit_factor),
        "reasoning": reasons,
        "source_path": str(summary_path),
    }


def _compact_kv_text(raw: Any, *, topn: int = 4) -> str:
    return _compact_kv_text_r3_impl(raw, topn=topn, facade=_r3_sys.modules[__name__])


def _reason_text(intent: Dict[str, Any], trace: Dict[str, Any], llm: Dict[str, Any]) -> str:
    return _reason_text_r3_impl(intent, trace, llm, facade=_r3_sys.modules[__name__])


def _humanize_reason(raw: Any) -> str:
    return _humanize_reason_r3_impl(raw, facade=_r3_sys.modules[__name__])


def _normalize_reason_code(
    raw_reason: Any,
    *,
    action: str,
    execution_status: str,
    guard_status: str,
) -> str:
    return _normalize_reason_code_r3_impl(raw_reason, action=action,
        execution_status=execution_status, guard_status=guard_status,
        facade=_r3_sys.modules[__name__])


def _health_badge(level: str) -> str:
    lv = str(level or "").strip().upper()
    if lv not in ("GREEN", "YELLOW", "RED"):
        return f"[{lv or 'UNKNOWN'}]"
    return f"[{lv}]"


def _render_reason_top(counter: Counter[str], *, topn: int = 5) -> List[Dict[str, Any]]:
    return _render_reason_top_r3_impl(counter, topn=topn, facade=_r3_sys.modules[__name__])


def _format_reason_rows(rows: List[Dict[str, Any]]) -> str:
    return _format_reason_rows_r3_impl(rows, facade=_r3_sys.modules[__name__])


def _compact_distance_to_ready_text(raw: Any) -> str:
    return _compact_distance_to_ready_text_r3_impl(raw, facade=_r3_sys.modules[__name__])


def _compact_blocking_features(raw: Any, *, limit: int = 3) -> str:
    values = raw if isinstance(raw, list) else []
    clipped = [str(v or "").strip() for v in values if str(v or "").strip()]
    return ", ".join(clipped[:limit]) if clipped else "-"


def _merge_scanner_handoff_with_selection(
    handoff: Any,
    selection: Any,
) -> Dict[str, Any]:
    return _merge_scanner_handoff_with_selection_r3_impl(handoff, selection,
        facade=_r3_sys.modules[__name__])


def _broker_code_success(value: Any) -> Optional[bool]:
    return _broker_code_success_r3_impl(value, facade=_r3_sys.modules[__name__])


def _decision_axis(story: Dict[str, Any]) -> str:
    return _decision_axis_r3_impl(story, facade=_r3_sys.modules[__name__])


def _story_explanation(story: Dict[str, Any]) -> Dict[str, str]:
    return _story_explanation_r3_impl(story, facade=_r3_sys.modules[__name__])


def _canonical_report_root(report_dir: Path) -> Path:
    return _canonical_report_root_r3_impl(report_dir, facade=_r3_sys.modules[__name__])


def _apply_commander_route_overlay(
    stories: List[Dict[str, Any]],
    route_summary: Dict[str, Any],
) -> List[Dict[str, Any]]:
    return _apply_commander_route_overlay_r3_impl(stories, route_summary,
        facade=_r3_sys.modules[__name__])


def build_operator_summary_snapshot_from_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    return build_operator_summary_snapshot_from_payload_r3_impl(payload,
        facade=_r3_sys.modules[__name__])


def _run_context_default(run_id: str) -> Dict[str, Any]:
    return _run_context_default_r3_impl(run_id, facade=_r3_sys.modules[__name__])


def _is_trade_story(story: Dict[str, Any]) -> bool:
    return _is_trade_story_r3_impl(story, facade=_r3_sys.modules[__name__])


def _decision_trace_inner(payload: Dict[str, Any]) -> Dict[str, Any]:
    inner = payload.get("payload") if isinstance(payload.get("payload"), dict) else {}
    return inner if isinstance(inner, dict) else {}


def _iter_day_rows_with_epoch(events_path: Path, day: str) -> Iterable[Dict[str, Any]]:
    """Streams one day's rows with _epoch/_day attached, without ever
    materializing the day into a list -- backs the day-scoped calls in
    generate_decision_story_report/generate_run_card_report. Relies on
    iter_jsonl_events's own per-day disk cache, so multiple calls for the
    same (events_path, day) within one report -- one per consumer -- only
    pay the full-file scan once; the rest stream the much smaller day cache.
    """
    return _iter_day_rows_with_epoch_r3_impl(events_path, day, facade=_r3_sys.modules[__name__])


class _RestreamedDayRows:
    """A day's event rows that is re-read from the per-day event cache on every iteration.

    `build_operator_daily_summary_payload` used to materialise the whole day (~6.5M parsed
    objects, ~400 MiB for 10-06) and hand that list to six consumers. This yields the same
    rows in the same order but keeps none of them: each consumer streams the (already built)
    day cache. `bool()` is true iff the day has at least one row, like the list it replaces.
    """

    def __init__(self, events_path: Path, day: Any, target_day: str) -> None:
        self._events_path = events_path
        self._day = day
        self._target_day = target_day

    def __iter__(self) -> Iterable[Dict[str, Any]]:
        for row in _iter_day_rows_with_epoch(self._events_path, self._day):
            if str(row.get("_day") or "") == self._target_day:
                yield row

    def __bool__(self) -> bool:
        return next(iter(self), None) is not None


def _build_run_contexts(day_rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return _run_context_projection.build_run_contexts(day_rows, facade=_visibility_sys.modules[__name__])


def build_operator_daily_summary_payload(
    events_path: Path,
    report_dir: Path,
    *,
    day: Optional[str] = None,
    metrics_report_dir: Optional[Path] = None,
    m30_post_golive_dir: Optional[Path] = None,
    m30_golive_dir: Optional[Path] = None,
    m31_slo_incident_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    report_dir.mkdir(parents=True, exist_ok=True)

    if day:
        # `_pick_day` returns the requested day unchanged when one is given, so the day is
        # known up front and the rows never need to be materialised (see _RestreamedDayRows).
        target_day = str(day).strip()
        day_rows: Any = _RestreamedDayRows(events_path, day, target_day)
    else:
        rows: List[Dict[str, Any]] = []
        for raw in _iter_jsonl(events_path):
            ts = raw.get("ts") or (raw.get("payload") or {}).get("ts")
            rows.append({**raw, "_epoch": _to_epoch(ts), "_day": _utc_day(ts)})
        target_day = _pick_day(rows, day)
        day_rows = [r for r in rows if str(r.get("_day") or "") == target_day]
        del rows
    canonical_report_root = _canonical_report_root(report_dir)
    candidate_decision_summary = load_candidate_decision_summary(
        reports_root=canonical_report_root,
        day=target_day,
    )
    route_summary = build_commander_route_summary(
        reports_root=canonical_report_root,
        day=target_day,
        day_rows=day_rows,
    )
    run_stories = _apply_commander_route_overlay(_build_run_contexts(day_rows), route_summary)
    freshness = _build_report_freshness(day_rows)

    metrics_dir = metrics_report_dir or (Path("reports") / "metrics")
    metrics = _load_or_build_metrics(events_path, metrics_dir, target_day)
    trading_health_status = _build_trading_health_status(canonical_report_root, target_day)
    m30_post_dir = m30_post_golive_dir or (Path("reports") / "milestones" / "m30_post_golive")
    m30_go_dir = m30_golive_dir or (Path("reports") / "milestones" / "m30_golive")
    m31_dir = m31_slo_incident_dir or (Path("reports") / "m31_slo_incident")
    m30_policy = _find_day_artifact(m30_post_dir, "m30_post_golive_policy", target_day)
    m30_signoff = _find_day_artifact(m30_go_dir, "m30_final_golive_signoff", target_day)
    m31_slo = _find_day_artifact(m31_dir, "m31_slo_incident", target_day)

    action_counts: Counter[str] = Counter()
    strategy_counts: Counter[str] = Counter()
    blocked_reason_counts: Counter[str] = Counter()
    noop_reason_counts: Counter[str] = Counter()
    fallback_signal_status_counts: Counter[str] = Counter()
    stage_error_counts: Counter[str] = Counter()
    executions_ok = 0
    executions_fail = 0
    executions_total = 0
    operator_intervention_total = 0
    cooldown_transition_total = 0
    duplicate_execution_total = 0
    guard_precedence_violation_total = 0

    run_ids_seen: set[str] = set()
    for row in day_rows:
        run_id_seen = str(row.get("run_id") or "").strip()
        if run_id_seen:
            run_ids_seen.add(run_id_seen)
        stage = str(row.get("stage") or "").strip()
        event = str(row.get("event") or "").strip()
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
        payload_text = json.dumps(payload, ensure_ascii=False).lower()

        if stage == "decision" and event == "trace":
            packet = payload.get("decision_packet") if isinstance(payload.get("decision_packet"), dict) else {}
            intent = packet.get("intent") if isinstance(packet.get("intent"), dict) else {}
            action = str(intent.get("action") or "").strip().upper()
            if action:
                action_counts[action] += 1
            trace = payload.get("trace") if isinstance(payload.get("trace"), dict) else {}
            strategy = str(trace.get("strategy") or "").strip()
            if strategy:
                strategy_counts[strategy] += 1
        if stage == "decision_trace" and event == "strategic_frame":
            inner = _decision_trace_inner(payload)
            strategy = str(inner.get("playbook") or inner.get("market_regime") or "").strip()
            if strategy:
                strategy_counts[strategy] += 1

        if stage == "execute_from_packet" and event == "verdict" and payload.get("allowed") is False:
            blocked_reason_counts[str(payload.get("reason") or "blocked")] += 1

        if stage == "execute_from_packet" and event == "execution":
            executions_total += 1
            ex_payload = payload.get("payload") if isinstance(payload.get("payload"), dict) else {}
            broker_ok = _broker_code_success(ex_payload.get("broker_code"))
            if broker_ok is True:
                executions_ok += 1
            elif broker_ok is False:
                executions_fail += 1

        if stage == "commander_router" and event == "intervention":
            operator_intervention_total += 1
        if stage == "commander_router" and event == "transition":
            if str(payload.get("transition") or "").strip().lower() == "cooldown":
                cooldown_transition_total += 1

        if event == "error":
            stage_error_counts[str(stage or "unknown")] += 1
        if "duplicate_execution" in payload_text:
            duplicate_execution_total += 1
        if "guard_precedence_violation" in payload_text:
            guard_precedence_violation_total += 1

    out = _visibility_projection.build_daily_summary_readout(
        metrics=metrics,
        duplicate_execution_total=duplicate_execution_total,
        guard_precedence_violation_total=guard_precedence_violation_total,
        m30_policy=m30_policy,
        m31_slo=m31_slo,
        day_rows=day_rows,
        trading_health_status=trading_health_status,
        blocked_reason_counts=blocked_reason_counts,
        run_ids_seen=run_ids_seen,
        run_stories=run_stories,
        noop_reason_counts=noop_reason_counts,
        fallback_signal_status_counts=fallback_signal_status_counts,
        action_counts=action_counts,
        candidate_decision_summary=candidate_decision_summary,
        executions_total=executions_total,
        executions_ok=executions_ok,
        executions_fail=executions_fail,
        operator_intervention_total=operator_intervention_total,
        cooldown_transition_total=cooldown_transition_total,
        route_summary=route_summary,
        target_day=target_day,
        freshness=freshness,
        events_path=events_path,
        metrics_dir=metrics_dir,
        m30_post_dir=m30_post_dir,
        m30_go_dir=m30_go_dir,
        m31_dir=m31_dir,
        strategy_counts=strategy_counts,
        m30_signoff=m30_signoff,
        stage_error_counts=stage_error_counts,
        facade=_visibility_sys.modules[__name__],
    )

    policy_snapshot = build_policy_surface_quality_snapshot(events_path, canonical_report_root, target_day)
    policy_surface_executive_summary = dict(policy_snapshot.get("executive_summary") or {})
    chart_structure_decision_hint_executive_summary = dict(policy_snapshot.get("chart_structure_executive_summary") or {})
    executive_headline = str(policy_surface_executive_summary.get("headline") or "").strip()
    chart_structure_headline = str(chart_structure_decision_hint_executive_summary.get("headline") or "").strip()
    if executive_headline:
        out["executive_summary"]["summary_lines"].append(executive_headline)
    if chart_structure_headline:
        out["executive_summary"]["summary_lines"].append(chart_structure_headline)
    out["policy_surface_quality_summary"] = dict(policy_snapshot.get("summary") or {})
    out["policy_surface_quality_executive_summary"] = policy_surface_executive_summary
    out["chart_structure_decision_hint_summary"] = dict(policy_snapshot.get("chart_structure_summary") or {})
    out["chart_structure_decision_hint_executive_summary"] = chart_structure_decision_hint_executive_summary
    out["policy_surface_quality_source"] = dict(policy_snapshot.get("source") or {})
    out["chart_structure_decision_hint_source"] = dict(policy_snapshot.get("source") or {})
    return out


def generate_operator_daily_summary(
    events_path: Path,
    report_dir: Path,
    *,
    day: Optional[str] = None,
    metrics_report_dir: Optional[Path] = None,
    m30_post_golive_dir: Optional[Path] = None,
    m30_golive_dir: Optional[Path] = None,
    m31_slo_incident_dir: Optional[Path] = None,
) -> Tuple[Path, Path]:
    report_dir.mkdir(parents=True, exist_ok=True)
    out = build_operator_daily_summary_payload(
        events_path,
        report_dir,
        day=day,
        metrics_report_dir=metrics_report_dir,
        m30_post_golive_dir=m30_post_golive_dir,
        m30_golive_dir=m30_golive_dir,
        m31_slo_incident_dir=m31_slo_incident_dir,
    )

    target_day = str(out.get("day") or day or "")
    canonical_report_root = _canonical_report_root(report_dir)
    out["controlled_validation"] = build_controlled_validation_daily(
        reports_root=canonical_report_root,
        day=target_day,
    )
    paths = daily_artifact_paths(canonical_report_root, target_day)
    js_path = paths["operator_summary_json"]
    md_path = paths["operator_summary_md"]
    out["report_json_path"] = str(js_path)
    out["report_md_path"] = str(md_path)
    health = str((out.get("executive_summary") if isinstance(out.get("executive_summary"), dict) else {}).get("system_status") or "UNKNOWN")
    system_health_status = out.get("system_health_status") if isinstance(out.get("system_health_status"), dict) else {}
    trading_health_status = out.get("trading_health_status") if isinstance(out.get("trading_health_status"), dict) else {}
    reasoning_lines = list(system_health_status.get("reasoning") or [])

    md_lines = [
        f"# Operator Daily Summary ({target_day})",
        "",
    ]
    md_lines += render_data_freshness_markdown(out.get("data_freshness") if isinstance(out.get("data_freshness"), dict) else {})
    md_lines += [
        "",
        "## Executive Summary",
        "",
        f"- system_status: **{_health_badge(health)}**",
    ]
    for line in list(((out.get("executive_summary") if isinstance(out.get("executive_summary"), dict) else {}).get("summary_lines") or [])):
        md_lines.append(f"- {line}")

    md_lines += ["", "## Top Issues", ""]
    for issue in list(out.get("top_issues") or []):
        if not isinstance(issue, dict):
            continue
        md_lines.append(f"- [{issue.get('severity')}] {issue.get('code')}: {_humanize_reason(issue.get('detail') or issue.get('code'))}")

    md_lines += ["", "## Recommended Operator Actions", ""]
    for action in list(out.get("recommended_operator_actions") or []):
        md_lines.append(f"- {action}")

    md_lines += [
        "",
        "## System Health Status",
        "",
        f"- system_health_level: **{_health_badge(system_health_status.get('system_health_level') or 'UNKNOWN')}**",
        "- reasoning:",
    ]
    if reasoning_lines:
        for line in reasoning_lines[:5]:
            md_lines.append(f"  - {line}")
    else:
        md_lines.append("  - (none)")
    md_lines.append("- recommended_action:")
    for line in list(system_health_status.get("recommended_action") or []):
        md_lines.append(f"  - {line}")

    md_lines += [
        "",
        "## Trading Health Status",
        "",
        f"- trading_health_level: **{_health_badge(trading_health_status.get('trading_health_level') or 'UNKNOWN')}**",
        f"- sample_count: **{int(trading_health_status.get('sample_count') or 0)}**",
        f"- win_rate: **{_safe_float(trading_health_status.get('win_rate'), 0.0):.2%}**",
        f"- avg_return: **{_safe_float(trading_health_status.get('avg_return'), 0.0):.2%}**",
        "- reasoning:",
    ]
    for line in list(trading_health_status.get("reasoning") or [])[:5]:
        md_lines.append(f"  - {line}")

    tas = out.get("trading_activity_summary") if isinstance(out.get("trading_activity_summary"), dict) else {}
    route_summary = out.get("route_summary") if isinstance(out.get("route_summary"), dict) else {}
    md_lines += [
        "",
        "## Trading Activity Summary",
        "",
        f"- run_total: **{tas.get('run_total') or 0}**",
        f"- decision_action_counts: `{json.dumps(tas.get('decision_action_counts') or {}, ensure_ascii=False)}`",
        f"- strategy_counts: `{json.dumps(tas.get('strategy_counts') or {}, ensure_ascii=False)}`",
        f"- executions_total: **{tas.get('executions_total') or 0}**",
        f"- execution_guard_blocked_total: **{tas.get('execution_guard_blocked_total') or tas.get('blocked_total') or 0}**",
        f"- commander_candidate_rejected_total: **{tas.get('commander_candidate_rejected_total') or 0}**",
        f"- commander_candidate_noop_total: **{tas.get('commander_candidate_noop_total') or 0}**",
        f"- noop_reason_top_human: {_format_reason_rows(list(tas.get('noop_reason_top_human') or []))}",
        f"- fallback_signal_status_top_human: {_format_reason_rows(list(tas.get('fallback_signal_status_top_human') or []))}",
        "",
        "## Route Provenance",
        "",
        f"- route_source: `{route_summary.get('route_source') or '-'}`",
        f"- route_source_run_count: **{int(route_summary.get('route_source_run_count') or 0)}**",
        f"- route_source_missing_count: **{int(route_summary.get('route_source_missing_count') or 0)}**",
        f"- route_source_breakdown: `{json.dumps(route_summary.get('route_source_breakdown') or {}, ensure_ascii=False)}`",
        f"- route_selected_total: `{json.dumps(route_summary.get('route_selected_total') or {}, ensure_ascii=False)}`",
        f"- strategy_generation_mode_total: `{json.dumps(route_summary.get('strategy_generation_mode_total') or {}, ensure_ascii=False)}`",
    ]

    sgi = out.get("safety_guard_interventions") if isinstance(out.get("safety_guard_interventions"), dict) else {}
    cds = out.get("candidate_decision_summary") if isinstance(out.get("candidate_decision_summary"), dict) else {}
    md_lines += [
        "",
        "## Safety Guard Interventions",
        "",
        f"- execution_guard_blocked_total: **{sgi.get('execution_guard_blocked_total') or sgi.get('blocked_total') or 0}**",
        f"- blocked_reason_top_human: {_format_reason_rows(list(sgi.get('blocked_reason_top_human') or []))}",
        f"- operator_intervention_total: **{sgi.get('operator_intervention_total') or 0}**",
        f"- cooldown_transition_total: **{sgi.get('cooldown_transition_total') or 0}**",
        f"- duplicate_execution_total: **{sgi.get('duplicate_execution_total') or 0}**",
        f"- guard_precedence_violation_total: **{sgi.get('guard_precedence_violation_total') or 0}**",
        "",
        "## Commander Candidate Decisions",
        "",
        f"- available: **{bool(cds.get('available'))}**",
        f"- evaluated_windows: **{int(cds.get('window_count') or 0)}**",
        f"- candidate_rejected_total: **{int(cds.get('candidate_rejected_total') or 0)}**",
        f"- candidate_noop_total: **{int(cds.get('candidate_noop_total') or 0)}**",
        f"- candidate_approved_total: **{int(cds.get('candidate_approved_total') or 0)}**",
        f"- decision_counts: `{json.dumps(cds.get('decision_counts') or {}, ensure_ascii=False)}`",
        f"- reason_counts: `{json.dumps(cds.get('reason_counts') or {}, ensure_ascii=False)}`",
        "- semantics: candidate rejection occurs before OrderIntent; it is not an execution guard block.",
        "",
    ]
    md_lines += render_controlled_validation_daily_lines(
        out.get("controlled_validation")
        if isinstance(out.get("controlled_validation"), dict)
        else {}
    )
    narrative_policy = out.get("narrative_axis_policy") if isinstance(out.get("narrative_axis_policy"), dict) else {}
    md_lines += [
        "## Narrative Axis Policy",
        "",
        f"- entry_primary_for: `{narrative_policy.get('entry_primary_for') or []}`",
        f"- exit_primary_for: `{narrative_policy.get('exit_primary_for') or []}`",
        f"- mixed_only_for_ambiguous_cases: **{bool(narrative_policy.get('mixed_only_for_ambiguous_cases'))}**",
        f"- runtime_semantics_unchanged: **{bool(narrative_policy.get('runtime_semantics_unchanged'))}**",
        "",
    ]

    policy_surface_executive_summary = out.get("policy_surface_quality_executive_summary") if isinstance(out.get("policy_surface_quality_executive_summary"), dict) else {}
    chart_structure_decision_hint_executive_summary = out.get("chart_structure_decision_hint_executive_summary") if isinstance(out.get("chart_structure_decision_hint_executive_summary"), dict) else {}
    executive_headline = str(policy_surface_executive_summary.get("headline") or "").strip()
    chart_structure_headline = str(chart_structure_decision_hint_executive_summary.get("headline") or "").strip()
    if executive_headline:
        md_lines += ["", "## Policy Surface Executive Summary", "", f"- status: **{str(policy_surface_executive_summary.get('status') or 'unknown').upper()}**", f"- headline: {executive_headline}"]
    if chart_structure_headline:
        md_lines += ["", "## Chart Structure Decision Hint Executive Summary", "", f"- status: **{str(chart_structure_decision_hint_executive_summary.get('status') or 'unknown').upper()}**", f"- headline: {chart_structure_headline}"]
        chart_structure_examples = chart_structure_decision_hint_executive_summary.get("applied_examples") if isinstance(chart_structure_decision_hint_executive_summary.get("applied_examples"), list) else []
        if chart_structure_examples:
            md_lines += ["", "## Chart Structure Decision Hint Applied Examples", ""]
            for example in chart_structure_examples[:3]:
                if not isinstance(example, dict):
                    continue
                md_lines.append(
                    f"- `{example.get('run_id') or '-'}` "
                    f"[{str(example.get('entry_style') or '-').upper()}] "
                    f"{example.get('reason_transition') or '-'} "
                    f"blockers=`{json.dumps(example.get('blocking_features') or [], ensure_ascii=False)}`"
                )

    js_path.parent.mkdir(parents=True, exist_ok=True)
    js_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_operator_markdown(md_path, "\n".join(md_lines))
    return md_path, js_path


def generate_decision_story_report(
    events_path: Path,
    report_dir: Path,
    *,
    day: Optional[str] = None,
    max_runs: Optional[int] = 120,
    trade_only: bool = True,
) -> Tuple[Path, Dict[str, Any]]:
    report_dir.mkdir(parents=True, exist_ok=True)

    if day:
        # Day-scoped fast path: three independent, bounded streaming passes
        # over iter_jsonl_events's own per-day disk cache (built once on
        # the first pass, reused cheaply by the rest) instead of
        # materializing the whole day as one list held for the entire
        # function. See _build_run_contexts's own comment for the OOM RCA
        # this follows up on (2026-09-23 day-axis finding: a single busy
        # trading day's own JSON, independent of total history size, was
        # itself enough to approach/exceed the 1GiB container limit).
        target_day = str(day).strip()
        route_summary = build_commander_route_summary(
            reports_root=_canonical_report_root(report_dir),
            day=target_day,
            day_rows=_iter_day_rows_with_epoch(events_path, target_day),
        )
        stories_all = _apply_commander_route_overlay(
            _build_run_contexts(_iter_day_rows_with_epoch(events_path, target_day)),
            route_summary,
        )
        freshness = _build_report_freshness(_iter_day_rows_with_epoch(events_path, target_day))
    else:
        # No day requested (manual/CLI "auto-detect latest day" usage, not
        # the EOD-critical path -- see _pick_day) -- unchanged full-file
        # behavior, since there is no day to scope the read to yet.
        rows: List[Dict[str, Any]] = []
        for raw in _iter_jsonl(events_path):
            ts = raw.get("ts") or (raw.get("payload") or {}).get("ts")
            rows.append({**raw, "_epoch": _to_epoch(ts), "_day": _utc_day(ts)})
        target_day = _pick_day(rows, day)
        day_rows = [r for r in rows if str(r.get("_day") or "") == target_day]
        route_summary = build_commander_route_summary(
            reports_root=_canonical_report_root(report_dir),
            day=target_day,
            day_rows=day_rows,
        )
        stories_all = _apply_commander_route_overlay(_build_run_contexts(day_rows), route_summary)
        freshness = _build_report_freshness(day_rows)
    if bool(trade_only):
        stories_all = [s for s in stories_all if _is_trade_story(s)]
    limit = int(max_runs or 0)
    stories = stories_all[:limit] if limit > 0 else stories_all

    md_lines = [f"# Decision Story Report ({target_day})", ""]
    md_lines += render_data_freshness_markdown(
        build_data_freshness(
            generated_at=freshness["generated_at"],
            source_run_count=freshness["source_run_count"],
            latest_run_id=freshness["latest_run_id"],
            latest_run_ts=freshness["latest_run_ts"],
            stale=False,
        )
    )
    md_lines += [
        f"- story_total: **{int(len(stories_all))}**",
        f"- rendered_story_total: **{int(len(stories))}**",
    ]
    if len(stories) < len(stories_all):
        md_lines.append(f"- note: output truncated to first {len(stories)} runs")
    md_lines.append("")

    if not stories:
        md_lines += ["No decision stories found.", ""]
    else:
        for s in stories:
            action = str(s.get("action") or "UNKNOWN")
            qty = _safe_int(s.get("qty"), 0)
            final_action = f"{action} {qty}" if (qty > 0 and action in ("BUY", "SELL")) else action
            operator_int = s.get("operator_intervention") if isinstance(s.get("operator_intervention"), list) else []
            no_trade = s.get("no_trade_surface") if isinstance(s.get("no_trade_surface"), dict) else {}
            handoff = s.get("scanner_monitor_handoff") if isinstance(s.get("scanner_monitor_handoff"), dict) else {}
            strategist_resolution = s.get("strategist_policy_resolution") if isinstance(s.get("strategist_policy_resolution"), dict) else {}
            commander_route = s.get("commander_route") if isinstance(s.get("commander_route"), dict) else {}
            explanation = _story_explanation(s)
            md_lines += [
                f"## Run {s.get('run_id')}",
                "",
                f"- run_id: `{s.get('run_id')}`",
                f"- symbol: **{s.get('symbol') or 'N/A'}**",
                f"- final_action: **{final_action}**",
                f"- execution_status: **{s.get('execution_status')}**",
                f"- final_outcome: {s.get('final_outcome') or '-'}",
                f"- decision_axis: {explanation.get('axis') or '-'}",
                f"- primary_explanation: {explanation.get('primary_summary') or '-'}",
                f"- explanation_mode: {explanation.get('explanation_mode') or '-'}",
                f"- explanation_source: {explanation.get('explanation_source') or '-'}",
                f"- narrative_order: {explanation.get('narrative_order_text') or '-'}",
                f"- narrative_consistency_flag: {bool(explanation.get('narrative_consistency_flag'))}",
                f"- pre_intent_decision: {str(no_trade.get('pre_intent_decision') or '-')}",
                f"- guard_decision: {str(no_trade.get('no_trade_stage') or '-')}",
                f"- decision_reason_summary: {s.get('key_reason') or _humanize_reason('unspecified')}",
                f"- entry_narrative: {explanation.get('entry_narrative') or '-'}",
                f"- exit_narrative: {explanation.get('exit_narrative') or '-'}",
                f"- why_not_buy_summary: {explanation.get('why_not_buy_summary') or '-'}",
                f"- why_exit_summary: {explanation.get('exit_trigger_basis') if explanation.get('axis') == 'exit' else '-'}",
                f"- dominant_blocker: {explanation.get('dominant_blocker') or '-'}",
                f"- entry_context_blocker: {explanation.get('entry_context_blocker') if explanation.get('axis') == 'exit' else '-'}",
                f"- distance_to_ready: {explanation.get('distance_to_ready') or '-'}",
                f"- technical_evidence: {s.get('technical_evidence') or '-'}",
                f"- sentiment_evidence: {s.get('sentiment_evidence') or '-'}",
                f"- scanner_monitor_handoff: top1={handoff.get('scanner_selected_symbol') or '-'} "
                f"(rank={handoff.get('scanner_rank') or '-'}) -> "
                f"alignment={handoff.get('scanner_vs_monitor_alignment') or '-'} / "
                f"monitor_reason={handoff.get('monitor_rejection_reason_code') or '-'}",
                f"- strategist_provenance: mode={strategist_resolution.get('strategy_generation_mode') or '-'} / "
                f"llm_ok={strategist_resolution.get('llm_ok')} / "
                f"fallback_used={strategist_resolution.get('fallback_used')} / "
                f"fallback_source={strategist_resolution.get('fallback_source') or '-'}",
                f"- commander_route_provenance: route={commander_route.get('route_selected') or '-'} / "
                f"call_decision={commander_route.get('strategist_call_decision') or '-'} / "
                f"call_reason={commander_route.get('strategist_call_reason') or commander_route.get('strategist_skip_reason') or '-'} / "
                f"source={commander_route.get('route_source') or '-'}",
                f"- guard_intervention: {s.get('guard_reason_human') or _humanize_reason(s.get('guard_reason') or 'none')}",
                f"- operator_intervention: {', '.join(operator_int) if operator_int else 'none'}",
                "",
            ]

    md_path = report_dir / f"decision_story_{target_day}.md"
    _write_operator_markdown(md_path, "\n".join(md_lines))

    out = {
        "schema_version": "decision_story.v1",
        "day": target_day,
        "generated_at": freshness["generated_at"],
        "source_run_count": int(freshness["source_run_count"]),
        "latest_run_id": freshness["latest_run_id"],
        "latest_run_ts": freshness["latest_run_ts"],
        "data_freshness": build_data_freshness(
            generated_at=freshness["generated_at"],
            source_run_count=freshness["source_run_count"],
            latest_run_id=freshness["latest_run_id"],
            latest_run_ts=freshness["latest_run_ts"],
            stale=False,
        ),
        "route_source": str(route_summary.get("route_source") or "canonical_commander_preferred"),
        "route_source_run_count": int(route_summary.get("route_source_run_count") or 0),
        "route_source_missing_count": int(route_summary.get("route_source_missing_count") or 0),
        "route_provenance": build_route_provenance(route_summary),
        "story_total": int(len(stories_all)),
        "rendered_story_total": int(len(stories)),
        "truncated": bool(len(stories) < len(stories_all)),
        "trade_only": bool(trade_only),
        "report_md_path": str(md_path),
    }
    return md_path, out


def generate_run_card_report(
    events_path: Path,
    report_dir: Path,
    *,
    day: Optional[str] = None,
    max_runs: Optional[int] = 120,
    trade_only: bool = True,
) -> Tuple[Path, Dict[str, Any]]:
    report_dir.mkdir(parents=True, exist_ok=True)

    if day:
        # See generate_decision_story_report's matching comment: day-scoped
        # fast path, three independent bounded streaming passes instead of
        # one materialized day_rows list held for the whole function.
        target_day = str(day).strip()
        route_summary = build_commander_route_summary(
            reports_root=_canonical_report_root(report_dir),
            day=target_day,
            day_rows=_iter_day_rows_with_epoch(events_path, target_day),
        )
        stories_all = _apply_commander_route_overlay(
            _build_run_contexts(_iter_day_rows_with_epoch(events_path, target_day)),
            route_summary,
        )
        freshness = _build_report_freshness(_iter_day_rows_with_epoch(events_path, target_day))
    else:
        rows: List[Dict[str, Any]] = []
        for raw in _iter_jsonl(events_path):
            ts = raw.get("ts") or (raw.get("payload") or {}).get("ts")
            rows.append({**raw, "_epoch": _to_epoch(ts), "_day": _utc_day(ts)})
        target_day = _pick_day(rows, day)
        day_rows = [r for r in rows if str(r.get("_day") or "") == target_day]
        route_summary = build_commander_route_summary(
            reports_root=_canonical_report_root(report_dir),
            day=target_day,
            day_rows=day_rows,
        )
        stories_all = _apply_commander_route_overlay(_build_run_contexts(day_rows), route_summary)
        freshness = _build_report_freshness(day_rows)
    if bool(trade_only):
        stories_all = [s for s in stories_all if _is_trade_story(s)]
    stories_all = sorted(stories_all, key=lambda s: int(s.get("first_epoch") or 0))
    limit = int(max_runs or 0)
    stories = stories_all[:limit] if limit > 0 else stories_all

    lines = [f"# Run Cards ({target_day})", ""]
    lines += render_data_freshness_markdown(
        build_data_freshness(
            generated_at=freshness["generated_at"],
            source_run_count=freshness["source_run_count"],
            latest_run_id=freshness["latest_run_id"],
            latest_run_ts=freshness["latest_run_ts"],
            stale=False,
        )
    )
    lines += [
        f"- card_total: **{int(len(stories_all))}**",
        f"- rendered_card_total: **{int(len(stories))}**",
    ]
    if len(stories) < len(stories_all):
        lines.append(f"- note: output truncated to first {len(stories)} runs")
    lines.append("")

    if not stories:
        lines += ["No run cards found.", ""]
    else:
        for s in stories:
            risk_flags = s.get("risk_flags") if isinstance(s.get("risk_flags"), list) else []
            risk_text = ", ".join(str(x) for x in risk_flags) if risk_flags else "none"
            action = str(s.get("action") or "UNKNOWN")
            qty = max(0, _safe_int(s.get("qty"), 0))
            action_text = f"{action} {qty}" if (action in ("BUY", "SELL") and qty > 0) else action
            no_trade = s.get("no_trade_surface") if isinstance(s.get("no_trade_surface"), dict) else {}
            handoff = s.get("scanner_monitor_handoff") if isinstance(s.get("scanner_monitor_handoff"), dict) else {}
            strategist_resolution = s.get("strategist_policy_resolution") if isinstance(s.get("strategist_policy_resolution"), dict) else {}
            commander_route = s.get("commander_route") if isinstance(s.get("commander_route"), dict) else {}
            explanation = _story_explanation(s)
            lines += [
                f"Run: {s.get('run_id')}",
                f"Symbol: {s.get('symbol') or 'N/A'}",
                f"Route: {commander_route.get('route_selected') or '-'}",
                f"Route Source: {commander_route.get('route_source') or '-'}",
                f"Decision Axis: {explanation.get('axis') or '-'}",
                f"Scanner Top-1: {(handoff.get('scanner_selected_symbol') or '-')}/{handoff.get('scanner_score_total') if handoff else '-'}",
                f"Monitor Outcome: {no_trade.get('decision_outcome') or s.get('execution_status') or '-'}",
                f"Primary Explanation: {explanation.get('primary_summary') or '-'}",
                f"Narrative Order: {explanation.get('narrative_order_text') or '-'}",
                f"Entry Narrative: {explanation.get('entry_narrative') or '-'}",
                f"Exit Narrative: {explanation.get('exit_narrative') or '-'}",
                f"Dominant Blocker: {explanation.get('dominant_blocker') or '-'}",
                f"Entry Context Blocker: {explanation.get('entry_context_blocker') if explanation.get('axis') == 'exit' else '-'}",
                f"Near Ready: {bool(no_trade.get('near_ready_flag'))}",
                f"Strategist Mode: {strategist_resolution.get('strategy_generation_mode') or '-'}",
                f"Action: {action_text}",
                f"Status: {s.get('execution_status')}",
                f"Guard: {s.get('guard_status')} ({s.get('guard_reason_human') or _humanize_reason(s.get('guard_reason') or 'none')})",
                f"Reason: {s.get('key_reason') or _humanize_reason('unspecified')}",
                f"Risk Flags: {risk_text}",
                "",
            ]

    md_path = report_dir / f"run_cards_{target_day}.md"
    _write_operator_markdown(md_path, "\n".join(lines))
    out = {
        "schema_version": "run_cards.v1",
        "day": target_day,
        "generated_at": freshness["generated_at"],
        "source_run_count": int(freshness["source_run_count"]),
        "latest_run_id": freshness["latest_run_id"],
        "latest_run_ts": freshness["latest_run_ts"],
        "data_freshness": build_data_freshness(
            generated_at=freshness["generated_at"],
            source_run_count=freshness["source_run_count"],
            latest_run_id=freshness["latest_run_id"],
            latest_run_ts=freshness["latest_run_ts"],
            stale=False,
        ),
        "route_source": str(route_summary.get("route_source") or "canonical_commander_preferred"),
        "route_source_run_count": int(route_summary.get("route_source_run_count") or 0),
        "route_source_missing_count": int(route_summary.get("route_source_missing_count") or 0),
        "route_provenance": build_route_provenance(route_summary),
        "card_total": int(len(stories_all)),
        "rendered_card_total": int(len(stories)),
        "truncated": bool(len(stories) < len(stories_all)),
        "trade_only": bool(trade_only),
        "report_md_path": str(md_path),
    }
    return md_path, out


def generate_operator_visibility_bundle(
    *,
    events_path: Path,
    report_root: Path,
    day: Optional[str] = None,
) -> Dict[str, Any]:
    return generate_operator_visibility_bundle_r3_impl(events_path=events_path,
        report_root=report_root, day=day, facade=_r3_sys.modules[__name__])


def _operator_brief_trade_model_is_valid(trade_model: Dict[str, Any]) -> bool:
    if not isinstance(trade_model, dict) or not trade_model:
        return False
    facts = trade_model.get("facts") if isinstance(trade_model.get("facts"), dict) else {}
    provenance = trade_model.get("provenance") if isinstance(trade_model.get("provenance"), dict) else {}
    return bool(facts) and bool(provenance)


def build_separated_operator_brief(trade_dir: str, symbol: str, trades_root: str, *, model: Optional[str] = None) -> Dict[str, Any]:
    """Phase 6-1 Task 4: Fact/Narrative separated operator brief."""
    return build_separated_operator_brief_r3_impl(trade_dir, symbol, trades_root, model=model,
        facade=_r3_sys.modules[__name__])
