from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from libs.reporting.event_log_reader import iter_jsonl_events
from libs.reporting.llm_artifacts import resolve_trade_day_root
from libs.reporting.llm_artifacts import symbol_artifact_paths
from libs.reporting.operator_period_summary import (
    _operator_pattern_name,
    _operator_reason_name,
    generate_operator_symbol_summary_artifact,
)
import sys as _r3_sys
from libs.agents.reporter.narrative.symbol_trade_report_bodies_01 import (  # R-4 owner bodies (facade-injected)
    _safe_float_r4_impl,
    _normalize_pct_like_r4_impl,
    _pick_result_pct_r4_impl,
    _safe_int_r4_impl,
    _normalize_ts_r4_impl,
    _to_epoch_r4_impl,
    _normalize_lifecycle_bundle_r4_impl,
    _result_pct_from_lifecycle_r4_impl,
    _list_text_r4_impl,
    _clean_symbol_pattern_r4_impl,
    _clean_symbol_free_text_r4_impl,
    _classify_entry_pattern_r4_impl,
    _classify_exit_pattern_r4_impl,
    _dict_at_r4_impl,
    _should_prefer_artifact_entry_reason_r4_impl,
    _clean_lifecycle_summary_r4_impl,
    _hold_seconds_from_lifecycle_r4_impl,
    _pattern_rows_r4_impl,
    _derive_playbook_stats_r4_impl,
    _derive_dominant_exit_failure_axis_r4_impl,
    _derive_bias_recommendation_r4_impl,
)
from libs.agents.reporter.narrative.symbol_trade_report_bodies_02 import (  # R-4 owner bodies (facade-injected)
    build_symbol_memory_payload_r4_impl,
    _render_symbol_trade_markdown_r4_impl,
)
from libs.agents.reporter.narrative.symbol_trade_report_r8_bodies_01 import (  # R-4 owner bodies (facade-injected)
    _clean_symbol_reason_r4_impl,
    _actual_entry_reason_from_artifacts_r4_impl,
    _collect_symbol_event_insights_r4_impl,
    build_symbol_trade_summary_r4_impl,
    build_daily_trade_index_r4_impl,
)


def _safe_float(value: Any) -> Optional[float]:
    return _safe_float_r4_impl(value, facade=_r3_sys.modules[__name__])


def _normalize_pct_like(value: Any) -> Optional[float]:
    return _normalize_pct_like_r4_impl(value, facade=_r3_sys.modules[__name__])


def _pick_result_pct(*values: Any) -> Optional[float]:
    return _pick_result_pct_r4_impl(*values, facade=_r3_sys.modules[__name__])


def _safe_int(value: Any) -> int:
    return _safe_int_r4_impl(value, facade=_r3_sys.modules[__name__])


def _normalize_ts(value: Any) -> str:
    return _normalize_ts_r4_impl(value, facade=_r3_sys.modules[__name__])


def _to_epoch(value: Any) -> int:
    return _to_epoch_r4_impl(value, facade=_r3_sys.modules[__name__])


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return obj if isinstance(obj, dict) else {}


def _iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []

    def _gen() -> Iterable[Dict[str, Any]]:
        with path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except Exception:
                    continue
                if isinstance(row, dict):
                    yield row

    return _gen()


def _iter_trade_lifecycles(reports_root: Path) -> Iterable[Tuple[Path, Dict[str, Any]]]:
    trades_root = reports_root / "trades"
    if not trades_root.exists():
        return []

    def _gen() -> Iterable[Tuple[Path, Dict[str, Any]]]:
        seen_trade_ids: set[str] = set()
        for path in sorted(trades_root.rglob("lifecycle/trade_lifecycle.json")):
            obj = _read_json(path)
            if obj:
                trade_id = str(obj.get("trade_id") or "").strip()
                if trade_id:
                    seen_trade_ids.add(trade_id)
                yield path, obj

        for path in sorted(trades_root.rglob("lifecycle_bundle.json")):
            bundle = _read_json(path)
            if not bundle:
                continue
            trade_id = str(bundle.get("trade_id") or "").strip()
            if trade_id and trade_id in seen_trade_ids:
                continue
            normalized = _normalize_lifecycle_bundle(bundle)
            if normalized:
                if trade_id:
                    seen_trade_ids.add(trade_id)
                yield path, normalized

    return _gen()


def _iter_trade_lifecycles_for_day(reports_root: Path, day: str) -> Iterable[Tuple[Path, Dict[str, Any]]]:
    day_root = resolve_trade_day_root(reports_root, str(day or "").strip())
    if not day_root.exists():
        return []

    def _gen() -> Iterable[Tuple[Path, Dict[str, Any]]]:
        seen_trade_ids: set[str] = set()
        for path in sorted(day_root.rglob("lifecycle/trade_lifecycle.json")):
            obj = _read_json(path)
            if obj:
                trade_id = str(obj.get("trade_id") or "").strip()
                if trade_id:
                    seen_trade_ids.add(trade_id)
                yield path, obj

        for path in sorted(day_root.rglob("lifecycle_bundle.json")):
            bundle = _read_json(path)
            if not bundle:
                continue
            trade_id = str(bundle.get("trade_id") or "").strip()
            if trade_id and trade_id in seen_trade_ids:
                continue
            normalized = _normalize_lifecycle_bundle(bundle)
            if normalized:
                if trade_id:
                    seen_trade_ids.add(trade_id)
                yield path, normalized

    return _gen()


def _normalize_lifecycle_bundle(bundle: Dict[str, Any]) -> Dict[str, Any]:
    return _normalize_lifecycle_bundle_r4_impl(bundle, facade=_r3_sys.modules[__name__])


def _result_pct_from_lifecycle(obj: Dict[str, Any]) -> Optional[float]:
    return _result_pct_from_lifecycle_r4_impl(obj, facade=_r3_sys.modules[__name__])


def _list_text(values: Any, *, limit: int = 5) -> List[str]:
    return _list_text_r4_impl(values, limit=limit, facade=_r3_sys.modules[__name__])


def _contains_any(text: str, needles: List[str]) -> bool:
    lowered = str(text or "").strip().lower()
    return any(needle in lowered for needle in needles)


def _clean_symbol_reason(value: Any, *, axis: str) -> str:
    return _clean_symbol_reason_r4_impl(value, axis=axis, facade=_r3_sys.modules[__name__])


def _clean_symbol_pattern(value: Any, *, axis: str, fallback_reason: Any = "") -> str:
    return _clean_symbol_pattern_r4_impl(value, axis=axis, fallback_reason=fallback_reason, facade=_r3_sys.modules[__name__])


def _clean_symbol_code(value: Any) -> str:
    text = str(value or "").strip()
    if text.lower() in {"", "unknown", "none", "null", "-"}:
        return ""
    return text


def _clean_symbol_free_text(value: Any, *, entry_reason: str = "", exit_reason: str = "") -> str:
    return _clean_symbol_free_text_r4_impl(value, entry_reason=entry_reason, exit_reason=exit_reason, facade=_r3_sys.modules[__name__])


def _classify_entry_pattern(text: str) -> str:
    return _classify_entry_pattern_r4_impl(text, facade=_r3_sys.modules[__name__])


def _classify_exit_pattern(text: str) -> str:
    return _classify_exit_pattern_r4_impl(text, facade=_r3_sys.modules[__name__])


def _dict_at(root: Dict[str, Any], *keys: str) -> Dict[str, Any]:
    return _dict_at_r4_impl(root, *keys, facade=_r3_sys.modules[__name__])


def _summary_input_path_for_report(report_path: Path) -> Path:
    return Path(report_path).with_name("ai_trade_summary_input.json")


def _actual_entry_reason_from_artifacts(
    *,
    report_path: Path,
    report_entry_summary: str,
    bundle: Dict[str, Any],
    feedback: Dict[str, Any],
) -> str:
    return _actual_entry_reason_from_artifacts_r4_impl(report_path=report_path, report_entry_summary=report_entry_summary, bundle=bundle, feedback=feedback, facade=_r3_sys.modules[__name__])


def _should_prefer_artifact_entry_reason(raw_reason: Any, artifact_reason: Any) -> bool:
    return _should_prefer_artifact_entry_reason_r4_impl(raw_reason, artifact_reason, facade=_r3_sys.modules[__name__])


def _clean_lifecycle_summary(
    *,
    trade_id: str,
    status: str,
    entry_reason: str,
    exit_reason: str,
) -> str:
    return _clean_lifecycle_summary_r4_impl(trade_id=trade_id, status=status, entry_reason=entry_reason, exit_reason=exit_reason, facade=_r3_sys.modules[__name__])


def _extract_trade_artifact_snapshot(
    *,
    report_path: Path,
    operator_brief_path: Path,
    lifecycle_bundle_path: Path,
) -> Dict[str, Any]:
    report = _read_json(report_path)
    brief = _read_json(operator_brief_path)
    bundle = _read_json(lifecycle_bundle_path)
    report_executive = report.get("executive_summary") if isinstance(report.get("executive_summary"), dict) else {}
    report_market = report.get("market_context_at_entry") if isinstance(report.get("market_context_at_entry"), dict) else {}
    report_entry = report.get("entry_decision") if isinstance(report.get("entry_decision"), dict) else {}
    report_final = report.get("final_operator_conclusion") if isinstance(report.get("final_operator_conclusion"), dict) else {}
    feedback = (
        bundle.get("strategist_feedback_input")
        if isinstance(bundle.get("strategist_feedback_input"), dict)
        else report.get("strategist_feedback_input")
        if isinstance(report.get("strategist_feedback_input"), dict)
        else {}
    )
    shared_facts = (
        bundle.get("shared_facts")
        if isinstance(bundle.get("shared_facts"), dict)
        else report.get("shared_facts")
        if isinstance(report.get("shared_facts"), dict)
        else {}
    )
    trade_outcome = bundle.get("trade_outcome") if isinstance(bundle.get("trade_outcome"), dict) else {}
    report_shared_facts = report.get("shared_facts") if isinstance(report.get("shared_facts"), dict) else {}
    artifact_result_pct = _pick_result_pct(
        trade_outcome.get("return_pct"),
        shared_facts.get("return_pct"),
        shared_facts.get("pnl_pct"),
        report_shared_facts.get("return_pct"),
        report_shared_facts.get("pnl_pct"),
    )
    entry_reason_text = str(report_entry.get("summary") or "").strip()
    actual_entry_reason_text = _actual_entry_reason_from_artifacts(
        report_path=Path(report_path),
        report_entry_summary=entry_reason_text,
        bundle=bundle,
        feedback=feedback,
    )
    exit_reason_text = str(shared_facts.get("exit_reason") or "").strip()
    if not exit_reason_text:
        exit_reason_text = str(report_final.get("summary") or "").strip()
    entry_pattern_type = str(feedback.get("entry_pattern_type") or "").strip() or _classify_entry_pattern(actual_entry_reason_text or entry_reason_text)
    exit_pattern_type = str(feedback.get("exit_pattern_type") or "").strip() or _classify_exit_pattern(exit_reason_text)
    clean_entry_reason = _clean_symbol_reason(actual_entry_reason_text or entry_reason_text, axis="entry")
    clean_exit_reason = _clean_symbol_reason(exit_reason_text, axis="exit")
    return {
        "report_headline": _clean_symbol_free_text(report_executive.get("headline") or report.get("headline"), entry_reason=clean_entry_reason, exit_reason=clean_exit_reason),
        "report_executive_summary": _clean_symbol_free_text(report_executive.get("summary"), entry_reason=clean_entry_reason, exit_reason=clean_exit_reason),
        "report_market_summary": str(report_market.get("summary") or "").strip(),
        "report_entry_summary": clean_entry_reason,
        "actual_entry_reason": clean_entry_reason,
        "report_final_conclusion": _clean_symbol_free_text(report_final.get("summary"), entry_reason=clean_entry_reason, exit_reason=clean_exit_reason),
        "brief_headline": _clean_symbol_free_text(brief.get("headline"), entry_reason=clean_entry_reason, exit_reason=clean_exit_reason),
        "brief_executive_summary": _clean_symbol_free_text(brief.get("executive_summary"), entry_reason=clean_entry_reason, exit_reason=clean_exit_reason),
        "brief_risk_summary": _clean_symbol_free_text(brief.get("risk_summary"), entry_reason=clean_entry_reason, exit_reason=clean_exit_reason),
        "brief_next_checkpoints": _list_text(brief.get("next_checkpoints"), limit=3),
        "entry_pattern_type": _clean_symbol_pattern(entry_pattern_type, axis="entry", fallback_reason=clean_entry_reason),
        "exit_pattern_type": _clean_symbol_pattern(exit_pattern_type, axis="exit", fallback_reason=clean_exit_reason),
        "thesis_invalidation_code": _clean_symbol_code(feedback.get("thesis_invalidation_code")),
        "improvement_tags": _list_text(feedback.get("improvement_tags"), limit=6),
        "review_flags": _list_text(feedback.get("review_flags"), limit=6),
        "artifact_result_pct": artifact_result_pct,
    }


def _hold_seconds_from_lifecycle(obj: Dict[str, Any]) -> Optional[float]:
    return _hold_seconds_from_lifecycle_r4_impl(obj, facade=_r3_sys.modules[__name__])


def _build_history_index(reports_root: Path, symbol: str) -> List[Dict[str, Any]]:
    history: List[Dict[str, Any]] = []
    normalized_symbol = str(symbol or "").strip().upper()
    for path, obj in _iter_trade_lifecycles(reports_root):
        if str(obj.get("symbol") or "").strip().upper() != normalized_symbol:
            continue
        summary = obj.get("summary") if isinstance(obj.get("summary"), dict) else {}
        entry = obj.get("entry") if isinstance(obj.get("entry"), dict) else {}
        exit_row = obj.get("exit") if isinstance(obj.get("exit"), dict) else {}
        artifacts = obj.get("artifacts") if isinstance(obj.get("artifacts"), dict) else {}
        trade_id = str(obj.get("trade_id") or "")
        trade_day = str(obj.get("day") or "")
        trade_root = (
            path.parent
            if path.name == "lifecycle_bundle.json"
            else path.parent.parent
        )
        expected_report_path = trade_root / "reports" / "ai_trade_report.json"
        expected_operator_brief_path = trade_root / "reports" / "operator_brief.json"
        lifecycle_bundle_path = trade_root / "lifecycle_bundle.json"
        artifact_snapshot = _extract_trade_artifact_snapshot(
            report_path=Path(str(artifacts.get("ai_trade_report_json") or expected_report_path)),
            operator_brief_path=Path(str(artifacts.get("operator_brief_json") or expected_operator_brief_path)),
            lifecycle_bundle_path=Path(str(artifacts.get("lifecycle_bundle_json") or lifecycle_bundle_path)),
        )
        trade_status = str(obj.get("status") or "").strip()
        if exit_row:
            last_action = "SELL"
        elif trade_status.lower() == "open":
            last_action = "HOLD"
        elif entry:
            last_action = "BUY"
        else:
            last_action = ""
        run_id = (
            str(entry.get("run_id") or "").strip()
            or str(exit_row.get("run_id") or "").strip()
            or str(obj.get("entry_strategist_run_id") or "").strip()
        )
        result_pct = _result_pct_from_lifecycle(obj)
        if result_pct is None:
            result_pct = _safe_float(artifact_snapshot.get("artifact_result_pct"))
        raw_entry_reason = str(summary.get("entry_reason_human") or "")
        artifact_entry_reason = str(artifact_snapshot.get("actual_entry_reason") or "")
        entry_reason_raw = (
            artifact_entry_reason
            if _should_prefer_artifact_entry_reason(raw_entry_reason, artifact_entry_reason)
            else raw_entry_reason
        )
        entry_reason = _clean_symbol_reason(entry_reason_raw, axis="entry")
        exit_reason = _clean_symbol_reason(summary.get("exit_reason_human"), axis="exit")
        entry_pattern_type = _clean_symbol_pattern(
            artifact_snapshot.get("entry_pattern_type"),
            axis="entry",
            fallback_reason=entry_reason,
        )
        exit_pattern_type = _clean_symbol_pattern(
            artifact_snapshot.get("exit_pattern_type"),
            axis="exit",
            fallback_reason=exit_reason,
        )
        history.append(
            {
                "trade_id": trade_id,
                "date": trade_day,
                "run_id": run_id,
                "status": trade_status,
                "last_status": trade_status,
                "last_action": last_action,
                "entry_reason": entry_reason,
                "exit_reason": exit_reason,
                "lifecycle_summary": _clean_lifecycle_summary(
                    trade_id=trade_id,
                    status=trade_status,
                    entry_reason=entry_reason,
                    exit_reason=exit_reason,
                ),
                "operator_conclusion": str(summary.get("operator_conclusion_human") or ""),
                "playbook": str((((entry.get("strategist_context") or {}) if isinstance(entry.get("strategist_context"), dict) else {}).get("playbook")) or ""),
                "hold_seconds": _hold_seconds_from_lifecycle(obj),
                "result_pct": result_pct,
                "trade_origin": str(obj.get("trade_origin") or ""),
                "lifecycle_completeness": str(obj.get("lifecycle_completeness") or ""),
                "evidence_recovery_used": bool(obj.get("evidence_recovery_used")),
                "report_path": str(artifacts.get("ai_trade_report_json") or expected_report_path),
                "operator_brief_path": str(artifacts.get("operator_brief_json") or expected_operator_brief_path),
                "lifecycle_bundle_path": str(artifacts.get("lifecycle_bundle_json") or lifecycle_bundle_path),
                "trade_root_path": str(trade_root),
                "report_headline": str(artifact_snapshot.get("report_headline") or ""),
                "report_executive_summary": str(artifact_snapshot.get("report_executive_summary") or ""),
                "report_market_summary": str(artifact_snapshot.get("report_market_summary") or ""),
                "report_entry_summary": str(artifact_snapshot.get("report_entry_summary") or entry_reason or ""),
                "report_final_conclusion": str(artifact_snapshot.get("report_final_conclusion") or ""),
                "brief_headline": str(artifact_snapshot.get("brief_headline") or ""),
                "brief_executive_summary": str(artifact_snapshot.get("brief_executive_summary") or ""),
                "brief_risk_summary": str(artifact_snapshot.get("brief_risk_summary") or ""),
                "brief_next_checkpoints": list(artifact_snapshot.get("brief_next_checkpoints") or []),
                "entry_pattern_type": entry_pattern_type,
                "exit_pattern_type": exit_pattern_type,
                "thesis_invalidation_code": _clean_symbol_code(artifact_snapshot.get("thesis_invalidation_code")),
                "improvement_tags": list(artifact_snapshot.get("improvement_tags") or []),
                "review_flags": list(artifact_snapshot.get("review_flags") or []),
            }
        )
    history.sort(key=lambda row: (str(row.get("date") or ""), str(row.get("trade_id") or "")))
    return history


def _collect_symbol_event_insights(events_path: Path, symbol: str) -> Dict[str, List[str]]:
    return _collect_symbol_event_insights_r4_impl(events_path, symbol, facade=_r3_sys.modules[__name__])


def _pattern_rows(history: List[Dict[str, Any]], *, positive: bool) -> List[str]:
    return _pattern_rows_r4_impl(history, positive=positive, facade=_r3_sys.modules[__name__])


def _ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def _derive_playbook_stats(history: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return _derive_playbook_stats_r4_impl(history, facade=_r3_sys.modules[__name__])


def _derive_dominant_exit_failure_axis(history: List[Dict[str, Any]]) -> str:
    return _derive_dominant_exit_failure_axis_r4_impl(history, facade=_r3_sys.modules[__name__])


def _derive_bias_recommendation(
    *,
    avg_return_pct: float,
    playbook_stats: Dict[str, Dict[str, Any]],
    repeated_blockers: List[str],
) -> Dict[str, Any]:
    return _derive_bias_recommendation_r4_impl(avg_return_pct=avg_return_pct, playbook_stats=playbook_stats, repeated_blockers=repeated_blockers, facade=_r3_sys.modules[__name__])


def build_symbol_memory_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    return build_symbol_memory_payload_r4_impl(payload, facade=_r3_sys.modules[__name__])


def build_symbol_trade_summary(events_path: Path, reports_root: Path, symbol: str) -> Dict[str, Any]:
    return build_symbol_trade_summary_r4_impl(events_path, reports_root, symbol, facade=_r3_sys.modules[__name__])


def build_daily_trade_index(reports_root: Path, day: str) -> List[Dict[str, Any]]:
    return build_daily_trade_index_r4_impl(reports_root, day, facade=_r3_sys.modules[__name__])


def collect_symbols_for_day(
    events_path: Path,
    reports_root: Path,
    day: str,
    trade_index: Optional[List[Dict[str, Any]]] = None,
) -> List[str]:
    target_day = str(day or "").strip()
    symbols: List[str] = []
    seen: set[str] = set()

    index_rows = trade_index if trade_index is not None else build_daily_trade_index(reports_root, target_day)
    for row in index_rows:
        symbol = str(row.get("symbol") or "").strip().upper()
        if symbol and symbol not in seen:
            seen.add(symbol)
            symbols.append(symbol)

    for row in iter_jsonl_events(events_path, day=target_day):
        ts_day = datetime.fromtimestamp(_to_epoch(row.get("ts") or (row.get("payload") or {}).get("ts")), tz=timezone.utc).strftime("%Y-%m-%d") if _to_epoch(row.get("ts") or (row.get("payload") or {}).get("ts")) > 0 else ""
        if ts_day != target_day:
            continue
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
        detail = payload.get("payload") if isinstance(payload.get("payload"), dict) else {}
        order = payload.get("order") if isinstance(payload.get("order"), dict) else {}
        for candidate in (
            detail.get("symbol"),
            payload.get("symbol"),
            order.get("symbol"),
            order.get("stk_cd"),
        ):
            symbol = str(candidate or "").strip().upper()
            if symbol and symbol not in seen:
                seen.add(symbol)
                symbols.append(symbol)
    return symbols


def _render_symbol_trade_markdown(payload: Dict[str, Any]) -> str:
    return _render_symbol_trade_markdown_r4_impl(payload, facade=_r3_sys.modules[__name__])


def generate_symbol_trade_report(events_path: Path, reports_root: Path, symbol: str) -> Dict[str, Any]:
    payload = build_symbol_trade_summary(events_path, reports_root, symbol)
    symbol_memory = build_symbol_memory_payload(payload)
    paths = symbol_artifact_paths(reports_root, symbol)
    root_dir = paths["root_dir"]
    root_dir.mkdir(parents=True, exist_ok=True)

    history_index = payload.get("history_index") if isinstance(payload.get("history_index"), list) else []
    latest_trade = dict(history_index[-1]) if history_index else {}
    latest_snapshot = {
        "schema_version": "symbol_latest_snapshot.v1",
        "symbol": str(payload.get("symbol") or ""),
        "summary": dict(payload.get("summary") or {}),
        "last_trade_id": str(latest_trade.get("trade_id") or ""),
        "last_trade_date": str(latest_trade.get("date") or ""),
        "last_action": str(latest_trade.get("last_action") or ""),
        "last_status": str(latest_trade.get("last_status") or latest_trade.get("status") or ""),
        "report_path": str(latest_trade.get("report_path") or ""),
        "trade_origin": str(latest_trade.get("trade_origin") or ""),
        "lifecycle_completeness": str(latest_trade.get("lifecycle_completeness") or ""),
        "evidence_recovery_used": bool(latest_trade.get("evidence_recovery_used")),
        "latest_trade": latest_trade,
    }
    daily_index = sorted({str(row.get("date") or "") for row in history_index if str(row.get("date") or "").strip()})

    paths["symbol_trade_report_json"].write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    paths["symbol_memory_json"].write_text(json.dumps(symbol_memory, ensure_ascii=False, indent=2), encoding="utf-8")
    paths["trade_history_json"].write_text(json.dumps(history_index, ensure_ascii=False, indent=2), encoding="utf-8")
    paths["latest_snapshot_json"].write_text(json.dumps(latest_snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    paths["daily_index_json"].write_text(json.dumps({"symbol": payload.get("symbol"), "days": daily_index}, ensure_ascii=False, indent=2), encoding="utf-8")
    paths["symbol_trade_report_md"].write_text(_render_symbol_trade_markdown(payload), encoding="utf-8")
    summary_md, summary_json, _summary_payload = generate_operator_symbol_summary_artifact(
        reports_root=reports_root,
        symbol=symbol,
        symbol_trade_report_payload=payload,
        symbol_memory_payload=symbol_memory,
    )

    return {
        "symbol": str(payload.get("symbol") or ""),
        "report_json_path": str(paths["symbol_trade_report_json"]),
        "report_md_path": str(paths["symbol_trade_report_md"]),
        "symbol_summary_json_path": str(summary_json),
        "symbol_summary_md_path": str(summary_md),
        "symbol_memory_path": str(paths["symbol_memory_json"]),
        "trade_history_path": str(paths["trade_history_json"]),
        "latest_snapshot_path": str(paths["latest_snapshot_json"]),
        "daily_index_path": str(paths["daily_index_json"]),
        "summary": payload.get("summary") if isinstance(payload.get("summary"), dict) else {},
    }
