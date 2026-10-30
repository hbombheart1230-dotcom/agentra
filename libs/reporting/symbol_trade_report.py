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
from libs.reporting import symbol_trade_read_projection as _read_owner
from libs.reporting import symbol_trade_text_projection as _text_owner
from libs.reporting import symbol_trade_scalar_projection as _scalar_owner
from libs.reporting import symbol_trade_path_projection as _path_owner
from libs.reporting import symbol_trade_lifecycle_projection as _lifecycle_owner
from libs.reporting import symbol_trade_artifact_projection as _artifact_owner
from libs.reporting import symbol_trade_history_projection as _history_owner
from libs.reporting import symbol_trade_symbol_projection as _symbol_owner
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
    return _read_owner._read_json(path, facade=_r3_sys.modules[__name__])


def _iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    return _read_owner._iter_jsonl(path, facade=_r3_sys.modules[__name__])


def _iter_trade_lifecycles(reports_root: Path) -> Iterable[Tuple[Path, Dict[str, Any]]]:
    return _lifecycle_owner._iter_trade_lifecycles(reports_root, facade=_r3_sys.modules[__name__])


def _iter_trade_lifecycles_for_day(reports_root: Path, day: str) -> Iterable[Tuple[Path, Dict[str, Any]]]:
    return _lifecycle_owner._iter_trade_lifecycles_for_day(reports_root, day, facade=_r3_sys.modules[__name__])


def _normalize_lifecycle_bundle(bundle: Dict[str, Any]) -> Dict[str, Any]:
    return _normalize_lifecycle_bundle_r4_impl(bundle, facade=_r3_sys.modules[__name__])


def _result_pct_from_lifecycle(obj: Dict[str, Any]) -> Optional[float]:
    return _result_pct_from_lifecycle_r4_impl(obj, facade=_r3_sys.modules[__name__])


def _list_text(values: Any, *, limit: int = 5) -> List[str]:
    return _list_text_r4_impl(values, limit=limit, facade=_r3_sys.modules[__name__])


def _contains_any(text: str, needles: List[str]) -> bool:
    return _text_owner._contains_any(text, needles)


def _clean_symbol_reason(value: Any, *, axis: str) -> str:
    return _clean_symbol_reason_r4_impl(value, axis=axis, facade=_r3_sys.modules[__name__])


def _clean_symbol_pattern(value: Any, *, axis: str, fallback_reason: Any = "") -> str:
    return _clean_symbol_pattern_r4_impl(value, axis=axis, fallback_reason=fallback_reason, facade=_r3_sys.modules[__name__])


def _clean_symbol_code(value: Any) -> str:
    return _text_owner._clean_symbol_code(value)


def _clean_symbol_free_text(value: Any, *, entry_reason: str = "", exit_reason: str = "") -> str:
    return _clean_symbol_free_text_r4_impl(value, entry_reason=entry_reason, exit_reason=exit_reason, facade=_r3_sys.modules[__name__])


def _classify_entry_pattern(text: str) -> str:
    return _classify_entry_pattern_r4_impl(text, facade=_r3_sys.modules[__name__])


def _classify_exit_pattern(text: str) -> str:
    return _classify_exit_pattern_r4_impl(text, facade=_r3_sys.modules[__name__])


def _dict_at(root: Dict[str, Any], *keys: str) -> Dict[str, Any]:
    return _dict_at_r4_impl(root, *keys, facade=_r3_sys.modules[__name__])


def _summary_input_path_for_report(report_path: Path) -> Path:
    return _path_owner._summary_input_path_for_report(report_path, facade=_r3_sys.modules[__name__])


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
    return _artifact_owner._extract_trade_artifact_snapshot(report_path=report_path, operator_brief_path=operator_brief_path, lifecycle_bundle_path=lifecycle_bundle_path, facade=_r3_sys.modules[__name__])


def _hold_seconds_from_lifecycle(obj: Dict[str, Any]) -> Optional[float]:
    return _hold_seconds_from_lifecycle_r4_impl(obj, facade=_r3_sys.modules[__name__])


def _build_history_index(reports_root: Path, symbol: str) -> List[Dict[str, Any]]:
    return _history_owner._build_history_index(reports_root, symbol, facade=_r3_sys.modules[__name__])


def _collect_symbol_event_insights(events_path: Path, symbol: str) -> Dict[str, List[str]]:
    return _collect_symbol_event_insights_r4_impl(events_path, symbol, facade=_r3_sys.modules[__name__])


def _pattern_rows(history: List[Dict[str, Any]], *, positive: bool) -> List[str]:
    return _pattern_rows_r4_impl(history, positive=positive, facade=_r3_sys.modules[__name__])


def _ratio(numerator: float, denominator: float) -> float:
    return _scalar_owner._ratio(numerator, denominator)


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
    return _symbol_owner.collect_symbols_for_day(events_path, reports_root, day, trade_index, facade=_r3_sys.modules[__name__])


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
