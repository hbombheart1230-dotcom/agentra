from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from libs.core.evidence_identity import stable_evidence_id
from libs.reporting.llm_artifacts import iter_trade_dirs, resolve_trade_day_root
from libs.reporting import reporter_feedback_analysis as _reporter_feedback_analysis_owner
from libs.reporting import reporter_feedback_summary as _reporter_feedback_summary_owner
from libs.reporting import reporter_feedback_route_summary as _reporter_feedback_route_summary_owner
from libs.reporting import reporter_feedback_blocker_totals as _reporter_feedback_blocker_totals_owner
from libs.reporting import reporter_feedback_freshness as _reporter_feedback_freshness_owner
from libs.reporting import reporter_feedback_analysis_blockers as _reporter_feedback_analysis_blockers_owner
from libs.reporting import reporter_feedback_dominant_patterns as _reporter_feedback_dominant_patterns_owner
from libs.reporting import reporter_feedback_recommendations as _reporter_feedback_recommendations_owner


def _normalize_day(day: Optional[str]) -> str:
    return str(day or "").strip()


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _safe_total(counter_like: Mapping[str, Any] | None) -> int:
    total = 0
    if not isinstance(counter_like, Mapping):
        return 0
    for value in counter_like.values():
        total += _safe_int(value, 0)
    return total


def _ratio(count: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round(float(count) / float(total), 4)


def _extract_route_summary(payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    return _reporter_feedback_route_summary_owner.extract_route_summary(payload, facade=sys.modules[__name__])


def _extract_blocker_totals(payload: Mapping[str, Any] | None) -> Dict[str, int]:
    return _reporter_feedback_blocker_totals_owner.extract_blocker_totals(payload, facade=sys.modules[__name__])


def _extract_freshness(payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    return _reporter_feedback_freshness_owner.extract_freshness(payload, facade=sys.modules[__name__])


def _metrics_report_path(reports_root: Path, day: str) -> Path:
    return reports_root / "metrics" / f"metrics_{day}.json"


def _reporter_analysis_report_path(reports_root: Path, day: str) -> Path:
    return reports_root / "dev" / "analysis" / "reporter_analysis" / f"reporter_analysis_{day}.json"


def _events_log_candidates(reports_root: Path) -> list[Path]:
    root = Path(reports_root)
    return [
        root.parent / "data" / "logs" / "events.jsonl",
        root / "data" / "logs" / "events.jsonl",
    ]


def _load_or_generate_metrics_payload(reports_root: Path, day: str) -> Dict[str, Any]:
    existing = _read_json(_metrics_report_path(reports_root, day))
    if existing:
        return existing
    for events_path in _events_log_candidates(reports_root):
        if not events_path.exists():
            continue
        try:
            from libs.reporting.metrics_report_generator import generate_metrics_report

            _, js_path = generate_metrics_report(events_path, reports_root / "metrics", day=day)
        except Exception:
            continue
        generated = _read_json(js_path)
        if generated:
            return generated
    return {}


def _trade_report_paths(reports_root: Path, day: str) -> list[Path]:
    trade_root = resolve_trade_day_root(reports_root, day)
    if not trade_root.exists():
        return []
    return sorted(
        path
        for trade_dir in iter_trade_dirs(trade_root)
        for path in [trade_dir / "reports" / "ai_trade_report.json"]
        if path.is_file()
    )


def _build_trade_report_feedback_summary(reports_root: Path, day: str) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "trade_count": 0,
        "closed_trade_count": 0,
        "win_count": 0,
        "loss_count": 0,
        "flat_count": 0,
        "unknown_pnl_count": 0,
        "avg_pnl_pct": 0.0,
        "pnl_pct_sample_count": 0,
        "same_price_cost_loss_count": 0,
        "broker_truth_count": 0,
        "exit_reason_counts": {},
        "symbols": [],
    }
    symbol_counts: Dict[str, int] = {}
    exit_reason_counts: Dict[str, int] = {}
    pnl_pct_values: list[float] = []

    for path in _trade_report_paths(reports_root, day):
        payload = _read_json(path)
        if not payload:
            continue
        summary["trade_count"] += 1
        truth_surface = dict(payload.get("truth_surface") or {})
        status = dict(truth_surface.get("status") or {})
        price = dict(truth_surface.get("price") or {})
        pnl = dict(truth_surface.get("pnl") or {})
        availability = dict(truth_surface.get("availability") or {})
        if str(status.get("status") or "").strip().lower() != "closed":
            continue

        summary["closed_trade_count"] += 1
        symbol = str(payload.get("symbol") or status.get("symbol") or "").strip()
        if symbol:
            symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1

        exit_reason = str(status.get("exit_reason") or "").strip()
        if exit_reason:
            exit_reason_counts[exit_reason] = exit_reason_counts.get(exit_reason, 0) + 1

        pnl_value = pnl.get("value")
        pnl_pct = pnl.get("pct")
        pnl_value_known = pnl_value not in (None, "")
        pnl_pct_known = pnl_pct not in (None, "")
        pnl_value_num = _safe_float(pnl_value, 0.0) if pnl_value_known else 0.0
        classification_value = pnl_value_num if pnl_value_known else (_safe_float(pnl_pct, 0.0) if pnl_pct_known else None)
        if classification_value is None:
            summary["unknown_pnl_count"] += 1
        else:
            if classification_value > 0.0:
                summary["win_count"] += 1
            elif classification_value < 0.0:
                summary["loss_count"] += 1
            else:
                summary["flat_count"] += 1
        if pnl_pct_known:
            pnl_pct_values.append(_safe_float(pnl_pct, 0.0))

        if bool(availability.get("broker_fill_present")) and bool(availability.get("broker_pnl_present")):
            summary["broker_truth_count"] += 1

        buy_price = price.get("broker_buy_price")
        sell_price = price.get("broker_fill_price")
        fee = _safe_float(pnl.get("broker_fee"), 0.0)
        tax = _safe_float(pnl.get("broker_tax"), 0.0)
        if (
            buy_price not in (None, "")
            and sell_price not in (None, "")
            and _safe_float(buy_price, 0.0) == _safe_float(sell_price, 0.0)
            and pnl_value_num < 0.0
            and (fee > 0.0 or tax > 0.0)
        ):
            summary["same_price_cost_loss_count"] += 1

    if pnl_pct_values:
        summary["avg_pnl_pct"] = round(sum(pnl_pct_values) / len(pnl_pct_values), 4)
        summary["pnl_pct_sample_count"] = len(pnl_pct_values)
    summary["exit_reason_counts"] = exit_reason_counts
    summary["symbols"] = [name for name, _count in sorted(symbol_counts.items(), key=lambda item: (-item[1], item[0]))[:5]]
    return summary


def _extract_reporter_analysis_blocker_totals(payload: Mapping[str, Any] | None) -> Dict[str, int]:
    return _reporter_feedback_analysis_blockers_owner.extract_reporter_analysis_blocker_totals(payload, facade=sys.modules[__name__])


def _extract_reporter_analysis_recommendations(payload: Mapping[str, Any] | None) -> list[str]:
    return _reporter_feedback_analysis_owner.extract_reporter_analysis_recommendations(payload)


def _build_dominant_patterns(
    *,
    route_summary: Mapping[str, Any],
    blocker_totals: Mapping[str, int],
    freshness: Mapping[str, Any],
    trade_report_summary: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    return _reporter_feedback_dominant_patterns_owner.build_dominant_patterns(route_summary=route_summary, blocker_totals=blocker_totals, freshness=freshness, trade_report_summary=trade_report_summary, facade=sys.modules[__name__])


def _build_blocker_analysis(blocker_totals: Mapping[str, int]) -> list[dict[str, Any]]:
    return _reporter_feedback_analysis_owner.build_blocker_analysis(blocker_totals, facade=sys.modules[__name__])


def _build_route_analysis(route_summary: Mapping[str, Any]) -> Dict[str, Any]:
    return _reporter_feedback_analysis_owner.build_route_analysis(route_summary, facade=sys.modules[__name__])


def _build_recommendations(
    *,
    route_analysis: Mapping[str, Any],
    blocker_analysis: list[dict[str, Any]],
    trade_report_summary: Mapping[str, Any] | None = None,
) -> list[str]:
    return _reporter_feedback_recommendations_owner.build_recommendations(route_analysis=route_analysis, blocker_analysis=blocker_analysis, trade_report_summary=trade_report_summary, facade=sys.modules[__name__])


def _build_insight_summary(
    *,
    route_analysis: Mapping[str, Any],
    blocker_analysis: list[dict[str, Any]],
    trade_report_summary: Mapping[str, Any] | None = None,
) -> str:
    return _reporter_feedback_summary_owner.build_insight_summary(route_analysis=route_analysis, blocker_analysis=blocker_analysis, trade_report_summary=trade_report_summary, facade=sys.modules[__name__])


def _build_confidence(
    *,
    route_analysis: Mapping[str, Any],
    blocker_analysis: list[dict[str, Any]],
    trade_report_summary: Mapping[str, Any] | None = None,
) -> str:
    return _reporter_feedback_summary_owner.build_confidence(route_analysis=route_analysis, blocker_analysis=blocker_analysis, trade_report_summary=trade_report_summary, facade=sys.modules[__name__])


def build_strategist_feedback_packet(
    *,
    mode: str,
    payload: Mapping[str, Any] | None,
    reports_root: str | Path,
    day: Optional[str] = None,
) -> Dict[str, Any]:
    row = dict(payload or {})
    root = Path(str(reports_root))
    normalized_day = _normalize_day(day or row.get("day"))

    metrics_payload = row if str(mode or "") == "metrics_report" else {}
    trade_explain_payload = row if str(mode or "") == "trade_explain" else {}
    reporter_analysis_payload = row if str(mode or "") == "reporter_analysis" else {}
    if normalized_day:
        if not metrics_payload:
            metrics_payload = _load_or_generate_metrics_payload(root, normalized_day)
        if not reporter_analysis_payload:
            reporter_analysis_payload = _read_json(_reporter_analysis_report_path(root, normalized_day))
    trade_report_summary = _build_trade_report_feedback_summary(root, normalized_day) if normalized_day else {}

    route_summary = _extract_route_summary(row)
    metrics_route_summary = _extract_route_summary(metrics_payload)
    trade_route_summary = _extract_route_summary(trade_explain_payload)
    reporter_route_summary = _extract_route_summary(reporter_analysis_payload)
    if not route_summary.get("route_selected_total"):
        if metrics_route_summary.get("route_selected_total"):
            route_summary = metrics_route_summary
        elif trade_route_summary.get("route_selected_total"):
            route_summary = trade_route_summary
        else:
            route_summary = reporter_route_summary

    blocker_totals = _extract_blocker_totals(metrics_payload)
    if not blocker_totals:
        blocker_totals = _extract_blocker_totals(trade_explain_payload)
    if not blocker_totals:
        blocker_totals = _extract_reporter_analysis_blocker_totals(reporter_analysis_payload)
    if not blocker_totals:
        blocker_totals = _extract_blocker_totals(row)

    freshness = _extract_freshness(row)
    if not freshness.get("latest_run_id"):
        freshness = _extract_freshness(metrics_payload) if metrics_payload else freshness
    if not freshness.get("latest_run_id"):
        freshness = _extract_freshness(trade_explain_payload) if trade_explain_payload else freshness
    if not freshness.get("latest_run_id"):
        freshness = _extract_freshness(reporter_analysis_payload) if reporter_analysis_payload else freshness

    route_analysis = _build_route_analysis(route_summary)
    blocker_analysis = _build_blocker_analysis(blocker_totals)
    dominant_patterns = _build_dominant_patterns(
        route_summary=route_summary,
        blocker_totals=blocker_totals,
        freshness=freshness,
        trade_report_summary=trade_report_summary,
    )
    recommendations = _build_recommendations(
        route_analysis=route_analysis,
        blocker_analysis=blocker_analysis,
        trade_report_summary=trade_report_summary,
    )
    reporter_analysis_recommendations = _extract_reporter_analysis_recommendations(reporter_analysis_payload)
    if reporter_analysis_recommendations and not metrics_payload:
        recommendations = reporter_analysis_recommendations[:4]
    elif not recommendations or recommendations == ["Route and blocker mix look balanced; continue observing for stable multi-session patterns before changing strategy."]:
        if reporter_analysis_recommendations:
            recommendations = reporter_analysis_recommendations[:4]
    confidence = _build_confidence(
        route_analysis=route_analysis,
        blocker_analysis=blocker_analysis,
        trade_report_summary=trade_report_summary,
    )

    packet = {
        "available": bool(route_analysis.get("route_selected_total")) or bool(blocker_analysis) or _safe_int(trade_report_summary.get("closed_trade_count"), 0) > 0,
        "packet_version": "strategist_feedback.v1",
        "source_day": normalized_day,
        "feedback_mode": "deterministic",
        "source_mode": str(mode or ""),
        "source_reports": {
            "metrics": bool(metrics_payload),
            "trade_explain": bool(trade_explain_payload),
            "reporter_analysis": bool(reporter_analysis_payload),
            "trade_reports": _safe_int(trade_report_summary.get("closed_trade_count"), 0) > 0,
            "current_payload": bool(row),
        },
        "insight_summary": _build_insight_summary(
            route_analysis=route_analysis,
            blocker_analysis=blocker_analysis,
            trade_report_summary=trade_report_summary,
        ),
        "dominant_patterns": dominant_patterns,
        "blocker_analysis": blocker_analysis,
        "route_analysis": route_analysis,
        "recommendation": recommendations,
        "confidence": confidence,
        "data_freshness": freshness,
        "trade_report_analysis": trade_report_summary,
        "runtime_semantics_unchanged": True,
    }
    packet["feedback_id"] = stable_evidence_id(
        "feedback",
        {
            "source_day": normalized_day,
            "source_mode": packet.get("source_mode"),
            "dominant_patterns": packet.get("dominant_patterns"),
            "blocker_analysis": packet.get("blocker_analysis"),
            "route_analysis": packet.get("route_analysis"),
            "recommendation": packet.get("recommendation"),
            "confidence": packet.get("confidence"),
        },
    )
    return packet
