from __future__ import annotations

import calendar
import json
import os
import re
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from libs.performance.strategy_memory import sync_strategy_memory_artifacts
from libs.reporting.llm_artifacts import (
    canonical_trade_day_root,
    daily_artifact_paths,
    find_trade_dir,
    monthly_artifact_paths,
    operator_summary_artifact_root,
    symbol_artifact_paths,
    weekly_artifact_paths,
)
from libs.reporting.quant_tactic_evaluation import (
    build_quant_tactic_evaluation,
    render_quant_tactic_evaluation_lines,
)
from libs.reporting.json_array_stream import iter_json_array
from libs.reporting.quant_shadow_candidate_evaluation import (
    CANDIDATE_EVALUATION_PAYLOAD_KEYS,
    build_quant_shadow_candidate_evaluation,
    load_quant_shadow_candidate_payloads,
    load_quant_shadow_candidate_payloads_for_range,
    render_quant_shadow_candidate_evaluation_lines,
)
from libs.reporting.quant_tactic_report import quant_tactic_surface as build_quant_tactic_surface
from libs.reporting.strategist_llm_evaluation import (
    build_strategist_llm_evaluation,
    render_strategist_llm_evaluation_lines,
)
from libs.reporting.market_regime_rail_review import (
    classify_market_regime_rail,
    load_latest_macro_snapshot,
)
from libs.reporting.q8_shadow_blocker_review import (
    build_q8_shadow_blocker_review,
)
from libs.reporting.controlled_validation_daily import (
    build_controlled_validation_daily,
    render_controlled_validation_daily_lines,
)
from libs.reporting.kiwoom_day_trade_diary_truth import match_trade_diary_row
import sys as _r3_sys
from libs.reporting.operator_period_summary_parts.period_payloads import (
    build_operator_period_summary_r3_impl,
    build_operator_symbol_summary_artifact_payload_r3_impl,
    _period_from_week_r3_impl,
    _period_from_month_r3_impl,
    _decision_is_weekend_carry_r3_impl,
    _is_carryover_exit_marker_r3_impl,
    _find_key_recursive_r3_impl,
    _iso_to_kst_dt_r3_impl,
    _epoch_to_kst_text_r3_impl,
    _epoch_day_kst_r3_impl,
    _parse_day_r3_impl,
    _trade_id_day_r3_impl,
    _dig_r3_impl,
)
from libs.reporting.operator_period_summary_parts.markdown_daily_summary import (
    render_operator_daily_summary_markdown_r3_impl,
    _render_q8_shadow_blocker_review_lines_r3_impl,
    _render_market_regime_rail_lines_r3_impl,
    _render_pattern_performance_lines_r3_impl,
    _pattern_perf_line_r3_impl,
)
from libs.reporting.operator_period_summary_parts.markdown_period_symbol_summary import (
    render_operator_period_summary_markdown_r3_impl,
    render_operator_symbol_summary_markdown_r3_impl,
)
from libs.reporting.operator_period_summary_parts.residual_positions import (
    _build_residual_positions_payload_r3_impl,
    _residual_position_status_r3_impl,
    _snapshot_position_symbols_r3_impl,
    _overnight_missing_context_r3_impl,
    _overnight_recorded_context_r3_impl,
)
from libs.reporting.operator_period_summary_parts.closeout_reconciliation import (
    _account_snapshot_closeout_reconciliation_r3_impl,
    _same_day_sell_guard_reconciliation_r3_impl,
    _closeout_state_metadata_r3_impl,
    _snapshot_day_trade_diary_rows_r3_impl,
    _broker_day_trade_diary_truth_metrics_r3_impl,
)
from libs.reporting.operator_period_summary_parts.pattern_naming import (
    _operator_reason_name_r3_impl,
    _operator_pattern_name_r3_impl,
    _operator_pattern_from_reason_name_r3_impl,
    _operator_signal_basis_name_r3_impl,
    _combined_pattern_key_r3_impl,
)
from libs.reporting.operator_period_summary_parts.pattern_buckets_and_performance import (
    _pattern_performance_payload_r3_impl,
    _pattern_counters_r3_impl,
    _performance_rows_by_field_r3_impl,
    _performance_field_value_r3_impl,
    _pattern_payload_r3_impl,
    _pattern_perf_rows_r3_impl,
    _top_counter_r3_impl,
    _return_count_payload_r3_impl,
    _score_bucket_r3_impl,
    _rank_bucket_r3_impl,
    _pct_bucket_r3_impl,
    _mismatch_bucket_r3_impl,
    _confirmation_bucket_r3_impl,
    _bool_bucket_r3_impl,
)
from libs.reporting.operator_period_summary_parts.trade_decision_fields import (
    _extract_trade_decision_fields_r3_impl,
)
from libs.reporting.operator_period_summary_parts.trade_rows_and_metrics import (
    _daily_trade_index_rows_r3_impl,
    _trade_metrics_r3_impl,
    _symbol_rows_r3_impl,
    _extract_truth_surface_metrics_r3_impl,
    _merge_daily_trade_index_with_symbol_history_r3_impl,
    _enrich_rows_with_truth_surface_r3_impl,
    _entry_reason_from_decision_flow_r3_impl,
    _is_closed_trade_r3_impl,
    _entry_truth_hints_r3_impl,
)
from libs.reporting.operator_period_summary_parts.operator_readouts import (
    _operator_readout_r3_impl,
    _operator_label_fallback_r3_impl,
)


_WEEK_RE = re.compile(r"^(\d{4})-W(\d{2})$")
_MONTH_RE = re.compile(r"^(\d{4})-(\d{2})$")


def _write_operator_markdown(path: Path, text: str) -> None:
    path.write_text(str(text or ""), encoding="utf-8-sig", newline="\n")


def _write_validated_json(path: Path, payload: Dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    json.loads(text)
    path.write_text(text, encoding="utf-8")
    json.loads(path.read_text(encoding="utf-8"))


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _safe_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:
        return None


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except Exception:
        return int(default)


def _read_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _text_value(value: Any) -> str:
    text = str(value or "").strip()
    if text.lower() in {"", "-", "none", "null", "unknown", "not_captured"}:
        return ""
    return text


def _looks_like_mojibake(text: str) -> bool:
    if not text:
        return False
    if "\ufffd" in text:
        return True
    compatibility_count = sum(1 for ch in text if "\uf900" <= ch <= "\ufaff")
    if compatibility_count:
        return True
    question_count = text.count("?")
    return question_count >= 2 and any(ord(ch) > 127 for ch in text)


def _operator_label_fallback(value: Any, *, axis: str = "") -> str:
    return _operator_label_fallback_r3_impl(value, axis=axis, facade=_r3_sys.modules[__name__])


def _first_text(*values: Any) -> str:
    for value in values:
        text = _text_value(value)
        if text:
            return text
    return ""


def _dig(source: Dict[str, Any], *keys: str) -> Any:
    return _dig_r3_impl(source, *keys, facade=_r3_sys.modules[__name__])


def _find_key_recursive(source: Any, key: str, *, max_nodes: int = 800) -> Any:
    return _find_key_recursive_r3_impl(source, key, max_nodes=max_nodes,
        facade=_r3_sys.modules[__name__])


def _score_bucket(value: Any) -> str:
    return _score_bucket_r3_impl(value, facade=_r3_sys.modules[__name__])


def _pct_bucket(value: Any) -> str:
    return _pct_bucket_r3_impl(value, facade=_r3_sys.modules[__name__])


def _rank_bucket(value: Any) -> str:
    return _rank_bucket_r3_impl(value, facade=_r3_sys.modules[__name__])


def _bool_bucket(value: Any) -> str:
    return _bool_bucket_r3_impl(value, facade=_r3_sys.modules[__name__])


def _first_dict(*values: Any) -> Dict[str, Any]:
    for value in values:
        if isinstance(value, dict) and value:
            return dict(value)
    return {}


def _first_recursive_dict(*roots: Any, key: str) -> Dict[str, Any]:
    for root in roots:
        found = _find_key_recursive(root, key)
        if isinstance(found, dict) and found:
            return dict(found)
    return {}


def _first_nonempty_list(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    return [str(item or "").strip() for item in value if str(item or "").strip()]


def _first_reason_bucket(values: Any) -> str:
    rows = _first_nonempty_list(values)
    return rows[0] if rows else ""


def _confirmation_bucket(value: Any) -> str:
    return _confirmation_bucket_r3_impl(value, facade=_r3_sys.modules[__name__])


def _mismatch_bucket(value: Any) -> str:
    return _mismatch_bucket_r3_impl(value, facade=_r3_sys.modules[__name__])


_UNAVAILABLE_PNL_VALUES = {"", "-", "none", "null", "unavailable", "not_available"}


def _is_unavailable_pnl(value: Any) -> bool:
    if value is None:
        return True
    return str(value).strip().lower() in _UNAVAILABLE_PNL_VALUES


def _ratio_to_pct(value: Any) -> float | None:
    parsed = _safe_float(value)
    if parsed is None:
        return None
    return float(parsed) * 100.0


def _truth_surface_candidate_paths(row: Dict[str, Any], reports_root: Path) -> List[Path]:
    candidates: List[Path] = []
    for key in ("trade_root_path",):
        raw = str(row.get(key) or "").strip()
        if raw:
            candidates.append(Path(raw) / "reports" / "ai_trade_summary.json")
            candidates.append(Path(raw) / "reports" / "ai_trade_summary_input.json")
    report_path = str(row.get("report_path") or "").strip()
    if report_path:
        report_dir = Path(report_path).parent
        candidates.append(report_dir / "ai_trade_summary.json")
        candidates.append(report_dir / "ai_trade_summary_input.json")
    lifecycle_path = str(row.get("lifecycle_bundle_path") or "").strip()
    if lifecycle_path:
        trade_root = Path(lifecycle_path).parent
        candidates.append(trade_root / "reports" / "ai_trade_summary.json")
        candidates.append(trade_root / "reports" / "ai_trade_summary_input.json")
    trade_id = str(row.get("trade_id") or "").strip()
    day = str(row.get("date") or row.get("day") or "").strip()[:10]
    if trade_id and day:
        trade_root = find_trade_dir(canonical_trade_day_root(Path(reports_root), day), trade_id)
        if trade_root is None:
            trade_root = Path(reports_root) / "trades" / day / trade_id
        candidates.append(trade_root / "reports" / "ai_trade_summary.json")
        candidates.append(trade_root / "reports" / "ai_trade_summary_input.json")
    out: List[Path] = []
    seen: set[str] = set()
    for path in candidates:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        out.append(path)
    return out


def _extract_truth_surface_metrics(row: Dict[str, Any], reports_root: Path) -> Dict[str, Any]:
    return _extract_truth_surface_metrics_r3_impl(row, reports_root,
        facade=_r3_sys.modules[__name__])


def _closeout_broker_skip_for_row(row: Dict[str, Any], reports_root: Path) -> Dict[str, Any]:
    day = str(row.get("date") or row.get("day") or "").strip()[:10]
    trade_id = str(row.get("trade_id") or "").strip()
    if not day or not trade_id:
        return {}
    closeout = _read_json(Path(reports_root) / "operator_summary" / "daily" / day / "closeout_maintenance.json")
    if not isinstance(closeout, dict):
        return {}
    steps = closeout.get("steps") if isinstance(closeout.get("steps"), dict) else {}
    broker = (
        steps.get("broker_closed_trade_reconciliation")
        if isinstance(steps.get("broker_closed_trade_reconciliation"), dict)
        else {}
    )
    for skipped in broker.get("skipped") or []:
        if not isinstance(skipped, dict):
            continue
        if str(skipped.get("trade_id") or "") != trade_id:
            continue
        return {
            "broker_reconciliation_status": "skipped_unresolved",
            "broker_reconciliation_reason": str(skipped.get("reason") or ""),
            "broker_reconciliation_snapshot_path": str(broker.get("snapshot_path") or ""),
        }
    return {}


def _state_snapshot_candidate_paths(reports_root: Path) -> List[Path]:
    candidates: List[Path] = []
    raw = str(os.getenv("STATE_STORE_PATH") or "").strip()
    if raw:
        candidates.append(Path(raw))
    candidates.append(Path(reports_root).parent / "data" / "state.json")
    out: List[Path] = []
    seen: set[str] = set()
    for path in candidates:
        try:
            key = str(path.resolve())
        except Exception:
            key = str(path)
        if key in seen:
            continue
        seen.add(key)
        out.append(path)
    return out


def _load_state_snapshot(reports_root: Path) -> Tuple[Dict[str, Any], str]:
    for path in _state_snapshot_candidate_paths(reports_root):
        payload = _read_json(path)
        if isinstance(payload, dict):
            return payload, str(path)
    return {}, ""


def _normalize_symbol_code(value: Any) -> str:
    text = str(value or "").strip().upper()
    if text.startswith("A") and len(text) == 7:
        text = text[1:]
    return text


def _latest_account_snapshot_path(reports_root: Path, day: str | None) -> Path:
    return Path(reports_root).parent / "data" / "logs" / "kiwoom_account_snapshots" / str(day or "").strip() / "latest.json"


def _snapshot_position_symbols(snapshot: Dict[str, Any]) -> set[str]:
    return _snapshot_position_symbols_r3_impl(snapshot, facade=_r3_sys.modules[__name__])


def _account_snapshot_closeout_reconciliation(reports_root: Path, day: str | None) -> Dict[str, Any]:
    return _account_snapshot_closeout_reconciliation_r3_impl(reports_root, day,
        facade=_r3_sys.modules[__name__])


def _latest_account_snapshot(reports_root: Path, day: str | None) -> Dict[str, Any]:
    normalized_day = str(day or "").strip()[:10]
    path = _latest_account_snapshot_path(reports_root, normalized_day)
    payload = _read_json(path)
    return payload if isinstance(payload, dict) else {}


def _first_snapshot_call_payload(snapshot: Dict[str, Any], api_id: str) -> Dict[str, Any]:
    for call in list(snapshot.get("calls") or []):
        if not isinstance(call, dict):
            continue
        if str(call.get("api_id") or "").strip() != api_id:
            continue
        payload = call.get("payload")
        return payload if isinstance(payload, dict) else {}
    return {}


def _snapshot_day_trade_diary_rows(snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
    return _snapshot_day_trade_diary_rows_r3_impl(snapshot, facade=_r3_sys.modules[__name__])


def _entry_truth_hints(row: Dict[str, Any], reports_root: Path) -> Dict[str, Any]:
    return _entry_truth_hints_r3_impl(row, reports_root, facade=_r3_sys.modules[__name__])


def _broker_day_trade_diary_truth_metrics(row: Dict[str, Any], reports_root: Path) -> Dict[str, Any]:
    return _broker_day_trade_diary_truth_metrics_r3_impl(row, reports_root,
        facade=_r3_sys.modules[__name__])


def _residual_position_status(row: Dict[str, Any], decision: Dict[str, Any], closeout: Dict[str, Any]) -> str:
    return _residual_position_status_r3_impl(row, decision, closeout,
        facade=_r3_sys.modules[__name__])


def _decision_is_weekend_carry(decision: Dict[str, Any]) -> bool:
    return _decision_is_weekend_carry_r3_impl(decision, facade=_r3_sys.modules[__name__])


def _epoch_to_kst_text(epoch: Any) -> str:
    return _epoch_to_kst_text_r3_impl(epoch, facade=_r3_sys.modules[__name__])


def _iso_to_kst_dt(value: Any) -> datetime | None:
    return _iso_to_kst_dt_r3_impl(value, facade=_r3_sys.modules[__name__])


def _iso_to_kst_text(value: Any) -> str:
    dt = _iso_to_kst_dt(value)
    if dt is None:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M:%S KST")


def _closeout_state_metadata(closeout: Dict[str, Any], day: str | None) -> Dict[str, Any]:
    return _closeout_state_metadata_r3_impl(closeout, day, facade=_r3_sys.modules[__name__])


def _overnight_missing_context(raw_row: Dict[str, Any], monitor_state: Dict[str, Any]) -> Dict[str, Any]:
    return _overnight_missing_context_r3_impl(raw_row, monitor_state,
        facade=_r3_sys.modules[__name__])


_FLATTEN_BEFORE_CLOSE_ACTIONS = {
    "closeout_flatten",
    "eod_flat",
    "flatten_before_close",
    "force_exit",
    "sell_before_close",
}


def _overnight_recorded_context(decision: Dict[str, Any]) -> Dict[str, Any]:
    return _overnight_recorded_context_r3_impl(decision, facade=_r3_sys.modules[__name__])


def _price_matches(left: Any, right: Any) -> bool:
    left_value = _safe_float(left)
    right_value = _safe_float(right)
    if left_value is None or right_value is None or left_value <= 0 or right_value <= 0:
        return False
    tolerance = max(1.0, abs(left_value) * 0.001)
    return abs(left_value - right_value) <= tolerance


def _same_day_flatten_reconciliation(
    *,
    reports_root: Path,
    day: str | None,
    symbol: str,
    qty: int,
    avg_price: Any,
) -> Dict[str, Any]:
    normalized_day = str(day or "").strip()
    normalized_symbol = str(symbol or "").strip().upper()
    if not normalized_day or not normalized_symbol or qty <= 0:
        return {}
    day_root = Path(reports_root) / "trades" / normalized_day
    if not day_root.exists():
        return {}

    day_token = normalized_day.replace("-", "")
    pattern = f"TRD_{day_token}_{normalized_symbol}_*/lifecycle_bundle.json"
    for path in sorted(day_root.rglob(pattern)):
        payload = _read_json(path)
        if not isinstance(payload, dict):
            continue
        entry = payload.get("entry") if isinstance(payload.get("entry"), dict) else {}
        exit_row = payload.get("exit") if isinstance(payload.get("exit"), dict) else {}
        if str(exit_row.get("action") or "").strip().upper() != "SELL":
            continue
        entry_qty = _safe_int(entry.get("qty"))
        exit_qty = _safe_int(exit_row.get("qty"))
        if entry_qty < qty or exit_qty < qty:
            continue
        entry_price = entry.get("price")
        if _safe_float(avg_price) is not None and not _price_matches(avg_price, entry_price):
            continue
        return {
            "symbol": normalized_symbol,
            "trade_id": str(payload.get("trade_id") or path.parent.name),
            "lifecycle_bundle_path": str(path),
            "reason": "same_day_lifecycle_full_sell_after_flatten_decision",
            "exit_reason": str(exit_row.get("reason_human") or ""),
            "exit_ts": str(exit_row.get("ts") or ""),
            "exit_qty": exit_qty,
        }
    return {}


def _sell_guard_candidate_paths(*, reports_root: Path, state_path: str) -> List[Path]:
    candidates: List[Path] = []
    state_raw = str(state_path or "").strip()
    if state_raw:
        state_file = Path(state_raw)
        candidates.append(state_file.parent / "state" / "execution_recent_sell_guard.json")
    candidates.append(Path(reports_root).parent / "data" / "state" / "execution_recent_sell_guard.json")
    out: List[Path] = []
    seen: set[str] = set()
    for path in candidates:
        try:
            key = str(path.resolve())
        except Exception:
            key = str(path)
        if key in seen:
            continue
        seen.add(key)
        out.append(path)
    return out


def _epoch_day_kst(epoch: Any) -> str:
    return _epoch_day_kst_r3_impl(epoch, facade=_r3_sys.modules[__name__])


def _same_day_sell_guard_reconciliation(
    *,
    reports_root: Path,
    state_path: str,
    day: str | None,
    symbol: str,
    qty: int,
) -> Dict[str, Any]:
    return _same_day_sell_guard_reconciliation_r3_impl(reports_root=reports_root,
        state_path=state_path, day=day, symbol=symbol, qty=qty, facade=_r3_sys.modules[__name__])


def _build_residual_positions_payload(*, reports_root: Path, day: str | None = None) -> Dict[str, Any]:
    return _build_residual_positions_payload_r3_impl(reports_root=reports_root, day=day,
        facade=_r3_sys.modules[__name__])


def build_residual_positions_payload(*, reports_root: Path, day: str | None = None) -> Dict[str, Any]:
    return _build_residual_positions_payload(reports_root=reports_root, day=day)


def _extract_trade_decision_fields(row: Dict[str, Any], reports_root: Path) -> Dict[str, Any]:
    return _extract_trade_decision_fields_r3_impl(row, reports_root,
        facade=_r3_sys.modules[__name__])


def _operator_reason_name(value: Any) -> str:
    return _operator_reason_name_r3_impl(value, facade=_r3_sys.modules[__name__])


def _operator_signal_basis_name(value: Any) -> str:
    return _operator_signal_basis_name_r3_impl(value, facade=_r3_sys.modules[__name__])


def _operator_pattern_name(value: Any, *, axis: str, fallback_reason: Any = "") -> str:
    return _operator_pattern_name_r3_impl(value, axis=axis, fallback_reason=fallback_reason,
        facade=_r3_sys.modules[__name__])


def _operator_pattern_from_reason_name(reason_name: str, *, axis: str) -> str:
    return _operator_pattern_from_reason_name_r3_impl(reason_name, axis=axis,
        facade=_r3_sys.modules[__name__])


def _enrich_rows_with_truth_surface(rows: Iterable[Dict[str, Any]], reports_root: Path) -> List[Dict[str, Any]]:
    return _enrich_rows_with_truth_surface_r3_impl(rows, reports_root,
        facade=_r3_sys.modules[__name__])


def _metric_return_pct(row: Dict[str, Any]) -> float | None:
    if bool(row.get("truth_surface_available")):
        return _safe_float(row.get("truth_net_return_pct"))
    return _safe_float(row.get("result_pct"))


def _metric_observed_return_pct(row: Dict[str, Any]) -> float | None:
    if bool(row.get("truth_surface_available")):
        return _safe_float(row.get("truth_observed_return_pct"))
    return None


def _parse_day(value: Any) -> date | None:
    return _parse_day_r3_impl(value, facade=_r3_sys.modules[__name__])


def _period_from_week(week: str) -> Tuple[str, date, date]:
    return _period_from_week_r3_impl(week, facade=_r3_sys.modules[__name__])


def _period_from_month(month: str) -> Tuple[str, date, date]:
    return _period_from_month_r3_impl(month, facade=_r3_sys.modules[__name__])


def default_week_key(day: date | None = None) -> str:
    target = day or date.today()
    iso = target.isocalendar()
    return f"{iso.year:04d}-W{iso.week:02d}"


def default_month_key(day: date | None = None) -> str:
    target = day or date.today()
    return f"{target.year:04d}-{target.month:02d}"


def _iter_symbol_trade_history(reports_root: Path) -> Iterable[Dict[str, Any]]:
    symbol_root = operator_summary_artifact_root(reports_root) / "symbols"
    if not symbol_root.exists():
        return []

    def gen() -> Iterable[Dict[str, Any]]:
        seen: set[tuple[str, str]] = set()
        for path in sorted(symbol_root.glob("*/trade_history.json")):
            payload = _read_json(path)
            if not isinstance(payload, list):
                continue
            symbol_hint = path.parent.name.upper()
            for row in payload:
                if not isinstance(row, dict):
                    continue
                symbol = str(row.get("symbol") or symbol_hint).strip().upper()
                trade_id = str(row.get("trade_id") or "").strip()
                key = (symbol, trade_id or f"{path}:{len(seen)}")
                if key in seen:
                    continue
                seen.add(key)
                out = dict(row)
                out["symbol"] = symbol
                yield out

    return gen()


def _top_counter(counter: Counter[str], limit: int = 5) -> List[Dict[str, Any]]:
    return _top_counter_r3_impl(counter, limit, facade=_r3_sys.modules[__name__])


def _trade_status(row: Dict[str, Any]) -> str:
    return str(row.get("last_status") or row.get("status") or "").strip().lower()


def _trade_action(row: Dict[str, Any]) -> str:
    return str(row.get("last_action") or row.get("action") or "").strip().upper()


def _has_partial_lifecycle_marker(row: Dict[str, Any]) -> bool:
    return (
        _trade_status(row) == "partial"
        or str(row.get("trade_origin") or "").strip().lower() == "recovered_partial"
    )


def _is_closed_trade(row: Dict[str, Any]) -> bool:
    return _is_closed_trade_r3_impl(row, facade=_r3_sys.modules[__name__])


def _is_recovered_partial_marker(row: Dict[str, Any]) -> bool:
    return _has_partial_lifecycle_marker(row)


def _trade_id_day(value: Any) -> str:
    return _trade_id_day_r3_impl(value, facade=_r3_sys.modules[__name__])


def _row_report_day(row: Dict[str, Any]) -> str:
    return str(row.get("date") or row.get("day") or "").strip()[:10]


def _is_carryover_exit_marker(row: Dict[str, Any]) -> bool:
    return _is_carryover_exit_marker_r3_impl(row, facade=_r3_sys.modules[__name__])


def _same_day_new_trade_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [row for row in rows if not _is_carryover_exit_marker(row)]


def _is_realized_nonclosed_exit(row: Dict[str, Any]) -> bool:
    if str(row.get("broker_reconciliation_status") or "") == "skipped_unresolved":
        return False
    if _is_closed_trade(row) or _trade_action(row) != "SELL":
        return False
    return _is_recovered_partial_marker(row)


def _return_count_payload(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    return _return_count_payload_r3_impl(rows, facade=_r3_sys.modules[__name__])


def _symbol_rows(rows: List[Dict[str, Any]], limit: int = 8) -> List[Dict[str, Any]]:
    return _symbol_rows_r3_impl(rows, limit, facade=_r3_sys.modules[__name__])


def _trade_metrics(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    return _trade_metrics_r3_impl(rows, facade=_r3_sys.modules[__name__])


def _pattern_counters(rows: List[Dict[str, Any]]) -> Dict[str, Counter[str]]:
    return _pattern_counters_r3_impl(rows, facade=_r3_sys.modules[__name__])


def _pattern_payload(counters: Dict[str, Counter[str]]) -> Dict[str, Any]:
    return _pattern_payload_r3_impl(counters, facade=_r3_sys.modules[__name__])


def _performance_source_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [row for row in rows if _is_closed_trade(row) or _is_realized_nonclosed_exit(row)]


def _performance_field_value(row: Dict[str, Any], field: str) -> Any:
    return _performance_field_value_r3_impl(row, field, facade=_r3_sys.modules[__name__])


def _performance_rows_by_field(rows: List[Dict[str, Any]], field: str, *, limit: int = 8) -> List[Dict[str, Any]]:
    return _performance_rows_by_field_r3_impl(rows, field, limit=limit,
        facade=_r3_sys.modules[__name__])


def _combined_pattern_key(row: Dict[str, Any]) -> str:
    return _combined_pattern_key_r3_impl(row, facade=_r3_sys.modules[__name__])


def _pattern_performance_payload(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    return _pattern_performance_payload_r3_impl(rows, facade=_r3_sys.modules[__name__])


def _trade_dir_for_row(row: Dict[str, Any], reports_root: Path) -> Path | None:
    explicit_path = str(row.get("trade_root_path") or "").strip()
    if explicit_path:
        explicit = Path(explicit_path)
        if explicit.exists() and explicit.is_dir():
            return explicit
    trade_id = str(row.get("trade_id") or "").strip()
    day = str(row.get("date") or row.get("day") or "").strip()[:10]
    if not trade_id or not day:
        return None
    found = find_trade_dir(canonical_trade_day_root(Path(reports_root), day), trade_id)
    if found is not None:
        return found
    fallback = Path(reports_root) / "trades" / day / trade_id
    return fallback if fallback.exists() else None


def _daily_trade_index_rows(
    *,
    reports_root: Path,
    trade_index: List[Any],
) -> List[Dict[str, Any]]:
    return _daily_trade_index_rows_r3_impl(reports_root=reports_root, trade_index=trade_index,
        facade=_r3_sys.modules[__name__])


def _daily_symbol_history_rows(reports_root: Path, day: str) -> List[Dict[str, Any]]:
    normalized_day = str(day or "").strip()
    return [
        row
        for row in _iter_symbol_trade_history(reports_root)
        if str(row.get("date") or "").strip() == normalized_day
    ]


def _merge_daily_trade_index_with_symbol_history(
    trade_rows: List[Dict[str, Any]],
    history_rows: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    return _merge_daily_trade_index_with_symbol_history_r3_impl(trade_rows, history_rows,
        facade=_r3_sys.modules[__name__])


def _entry_reason_from_decision_flow(decision_flow: Dict[str, Any], *, fallback: Any = "") -> str:
    return _entry_reason_from_decision_flow_r3_impl(decision_flow, fallback=fallback,
        facade=_r3_sys.modules[__name__])


def _latest_live_summary_payload(reports_root: Path, day: str) -> Tuple[Dict[str, Any], str]:
    day_key = re.sub(r"[^0-9]", "", str(day or ""))[:8]
    if len(day_key) != 8:
        return {}, ""
    live_root = Path(reports_root) / "live_summary"
    if not live_root.exists():
        return {}, ""
    candidates = sorted(
        live_root.glob(f"live_summary_{day_key}_*.json"),
        key=lambda path: (path.stat().st_mtime if path.exists() else 0.0, path.name),
        reverse=True,
    )
    for path in candidates:
        payload = _read_json(path)
        if isinstance(payload, dict):
            return payload, str(path)
    return {}, ""


def _runtime_activity_payload(
    *,
    reports_root: Path,
    day: str,
    source_payload: Dict[str, Any],
) -> Dict[str, Any]:
    explicit_runtime_keys = {
        "events",
        "approvals",
        "blocks",
        "symbols_observed",
        "generated_symbol_report_count",
    }
    q9_path = (
        Path(reports_root)
        / "operator_summary"
        / "daily"
        / day
        / "q9_decision_windows.json"
    )
    # Streamed one window at a time: only the three filter ids and `commander_final`'s
    # decision/monitor_intent are read, and the file is ~120 MB (see json_array_stream).
    q9_window_count = 0
    decisions: list[str] = []
    monitor_intents: list[str] = []
    try:
        for row in iter_json_array(q9_path, "windows"):
            if not isinstance(row, dict):
                continue
            if any(
                marker in " ".join(
                    str(row.get(key) or "").lower()
                    for key in ("decision_id", "run_id", "candidate_pool_id")
                )
                for marker in ("test", "fixture", "synthetic")
            ):
                continue
            q9_window_count += 1
            commander_final = row.get("commander_final")
            if isinstance(commander_final, dict):
                decisions.append(str(commander_final.get("decision") or "").strip().lower())
                monitor_intents.append(str(commander_final.get("monitor_intent") or "").strip().upper())
    except ValueError:
        q9_window_count, decisions, monitor_intents = 0, [], []  # unreadable file == no windows (as _read_json did)
    if q9_window_count:
        return {
            "source": "q9_decision_windows",
            "source_path": str(q9_path),
            "events": q9_window_count,
            "commander_decision_count": len(decisions),
            "missing_commander_decision_count": max(0, q9_window_count - len(decisions)),
            "approvals": sum(value in {"approve", "approved", "allow"} for value in decisions),
            "blocks": sum(value in {"reject", "blocked", "veto"} for value in decisions),
            "noops": sum(value in {"noop", "no_trade"} for value in decisions),
            "monitor_buy_count": sum(value == "BUY" for value in monitor_intents),
            "monitor_noop_count": sum(value == "NOOP" for value in monitor_intents),
            "symbols_observed_count": 0,
            "generated_symbol_report_count": 0,
        }

    if source_payload and any(key in source_payload for key in explicit_runtime_keys):
        return {
            "source": "daily_report_payload",
            "events": _safe_int(source_payload.get("events")),
            "approvals": _safe_int(source_payload.get("approvals")),
            "blocks": _safe_int(source_payload.get("blocks")),
            "symbols_observed_count": len(list(source_payload.get("symbols_observed") or [])),
            "generated_symbol_report_count": _safe_int(source_payload.get("generated_symbol_report_count")),
        }

    live_payload, live_path = _latest_live_summary_payload(reports_root, day)
    if not live_payload:
        return {
            "source": "not_available",
            "events": 0,
            "approvals": 0,
            "blocks": 0,
            "symbols_observed_count": 0,
            "generated_symbol_report_count": 0,
        }

    events = live_payload.get("events") if isinstance(live_payload.get("events"), dict) else {}
    execution = live_payload.get("execution") if isinstance(live_payload.get("execution"), dict) else {}
    return {
        "source": "live_summary_fallback",
        "source_path": live_path,
        "lookback_min": _safe_int(live_payload.get("lookback_min")),
        "events": _safe_int(events.get("window_total")),
        "events_scanned_total": _safe_int(events.get("scanned_total")),
        "approvals": _safe_int(execution.get("allowed_total")),
        "blocks": _safe_int(execution.get("blocked_total")),
        "executed_total": _safe_int(execution.get("executed_total")),
        "broker_fail_total": _safe_int(execution.get("executed_broker_fail_total")),
        "symbols_observed_count": 0,
        "generated_symbol_report_count": 0,
    }


def _operator_readout(
    *,
    trade_count: int,
    avg_return_pct: float,
    win_rate: float,
    exit_counts: Counter[str],
    entry_counts: Counter[str],
) -> Dict[str, Any]:
    return _operator_readout_r3_impl(trade_count=trade_count, avg_return_pct=avg_return_pct,
        win_rate=win_rate, exit_counts=exit_counts, entry_counts=entry_counts,
        facade=_r3_sys.modules[__name__])


def build_operator_period_summary(
    *,
    reports_root: Path,
    period_type: str,
    period_key: str,
) -> Dict[str, Any]:
    return build_operator_period_summary_r3_impl(reports_root=reports_root, period_type=period_type,
        period_key=period_key, facade=_r3_sys.modules[__name__])


def build_operator_daily_summary_artifact_payload(
    *,
    reports_root: Path,
    day: str,
    daily_report_payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    normalized_day = str(day or "").strip()
    source_payload = dict(daily_report_payload or {})
    trade_index = source_payload.get("trade_index") if isinstance(source_payload.get("trade_index"), list) else []
    if not trade_index:
        carryover_index = _read_json(
            canonical_trade_day_root(reports_root, normalized_day) / "carryover_exit_index.json"
        ) or {}
        trade_index = [
            dict(row)
            for row in list(carryover_index.get("rows") or [])
            if isinstance(row, dict)
        ]
    history_rows = _daily_symbol_history_rows(reports_root, normalized_day)
    if trade_index:
        rows = _merge_daily_trade_index_with_symbol_history(
            _daily_trade_index_rows(reports_root=reports_root, trade_index=trade_index),
            history_rows,
        )
    else:
        rows = history_rows
    rows = _enrich_rows_with_truth_surface(rows, reports_root)
    metrics = _trade_metrics(rows)
    counters = _pattern_counters(rows)
    # shadow_payloads feeds only build_quant_shadow_candidate_evaluation,
    # build_q8_shadow_blocker_review and build_strategist_llm_evaluation, which read
    # nothing but `candidates`/`generated_at`; project at load time to bound memory.
    shadow_payloads = load_quant_shadow_candidate_payloads(
        reports_root=reports_root,
        days=[normalized_day],
        keys=CANDIDATE_EVALUATION_PAYLOAD_KEYS,
    )
    market_regime_rail = classify_market_regime_rail(
        load_latest_macro_snapshot(
            normalized_day,
            root=Path(reports_root).parent / "data" / "logs" / "macro_indicators",
        )
    )
    quant_shadow_evaluation = build_quant_shadow_candidate_evaluation(shadow_payloads)
    if metrics["trade_count"] == 0 and trade_index:
        metrics["trade_count"] = len(trade_index)

    summary = {
        "schema_version": "operator_daily_summary.v1",
        "period_type": "daily",
        "day": normalized_day,
        "generated_at": _utc_now_iso(),
        "source": {
            "type": "daily_report_plus_operator_symbol_trade_history",
            "daily_report_json": str(daily_artifact_paths(reports_root, normalized_day)["daily_report_json"]),
            "symbol_history_root": str(operator_summary_artifact_root(reports_root) / "symbols"),
        },
        "runtime_activity": _runtime_activity_payload(
            reports_root=reports_root,
            day=normalized_day,
            source_payload=source_payload,
        ),
        "metrics": metrics,
        "patterns": _pattern_payload(counters),
        "pattern_performance": _pattern_performance_payload(rows),
        "quant_tactic_evaluation": build_quant_tactic_evaluation(rows),
        "quant_shadow_candidate_evaluation": quant_shadow_evaluation,
        "market_regime_rail_review": market_regime_rail,
        "q8_shadow_blocker_review": build_q8_shadow_blocker_review(
            shadow_payloads,
            market_regime_rail=market_regime_rail,
            quant_shadow_evaluation=quant_shadow_evaluation,
        ),
        "strategist_llm_evaluation": build_strategist_llm_evaluation(rows, shadow_payloads),
        "controlled_validation": build_controlled_validation_daily(
            reports_root=reports_root,
            day=normalized_day,
        ),
        "symbol_summary": _symbol_rows(rows),
        "residual_positions": _build_residual_positions_payload(reports_root=reports_root, day=normalized_day),
    }
    summary["operator_readout"] = _operator_readout(
        trade_count=int(metrics.get("trade_count") or 0),
        avg_return_pct=float(metrics.get("avg_return_pct") or 0.0),
        win_rate=float(metrics.get("win_rate") or 0.0),
        exit_counts=counters.get("exit_reasons") or Counter(),
        entry_counts=counters.get("entry_reasons") or Counter(),
    )
    residual_risk = (
        summary.get("residual_positions", {}).get("closeout_operational_risk")
        if isinstance(summary.get("residual_positions"), dict)
        else {}
    )
    if isinstance(residual_risk, dict) and str(residual_risk.get("severity") or "").lower() == "critical":
        readout = summary["operator_readout"]
        symbols_text = ", ".join(str(x) for x in list(residual_risk.get("unresolved_symbols") or []) if str(x).strip())
        readout["issues"] = [
            f"CRITICAL closeout issue: broker truth still has unclosed position(s): {symbols_text or '-'}",
            *list(readout.get("issues") or []),
        ]
        readout["recommended_actions"] = [
            "Next open: flatten unresolved position(s) at market before new BUY evaluation.",
            *list(readout.get("recommended_actions") or []),
        ]
        readout["root_cause"] = "장마감 청산/검증 루프가 broker truth 잔여 포지션을 완전히 닫지 못했습니다."
    return summary


def build_operator_symbol_summary_artifact_payload(
    *,
    reports_root: Path,
    symbol: str,
    symbol_trade_report_payload: Dict[str, Any] | None = None,
    symbol_memory_payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return build_operator_symbol_summary_artifact_payload_r3_impl(reports_root=reports_root,
        symbol=symbol, symbol_trade_report_payload=symbol_trade_report_payload,
        symbol_memory_payload=symbol_memory_payload, facade=_r3_sys.modules[__name__])


def _pattern_perf_rows(pattern_performance: Dict[str, Any], *path: str) -> List[Dict[str, Any]]:
    return _pattern_perf_rows_r3_impl(pattern_performance, *path, facade=_r3_sys.modules[__name__])


def _pattern_perf_line(label: str, rows: List[Dict[str, Any]], *, limit: int = 3) -> str:
    return _pattern_perf_line_r3_impl(label, rows, limit=limit, facade=_r3_sys.modules[__name__])


def _render_pattern_performance_lines(payload: Dict[str, Any]) -> List[str]:
    return _render_pattern_performance_lines_r3_impl(payload, facade=_r3_sys.modules[__name__])


def _render_quant_shadow_candidate_lines(payload: Dict[str, Any]) -> List[str]:
    shadow_eval = payload.get("quant_shadow_candidate_evaluation")
    if not isinstance(shadow_eval, dict):
        return []
    return render_quant_shadow_candidate_evaluation_lines(shadow_eval)


def _render_strategist_llm_evaluation_lines(payload: Dict[str, Any]) -> List[str]:
    evaluation = payload.get("strategist_llm_evaluation")
    if not isinstance(evaluation, dict):
        return []
    return render_strategist_llm_evaluation_lines(evaluation)


def _render_market_regime_rail_lines(payload: Dict[str, Any]) -> List[str]:
    return _render_market_regime_rail_lines_r3_impl(payload, facade=_r3_sys.modules[__name__])


def _render_q8_shadow_blocker_review_lines(payload: Dict[str, Any]) -> List[str]:
    return _render_q8_shadow_blocker_review_lines_r3_impl(payload, facade=_r3_sys.modules[__name__])


def render_operator_period_summary_markdown(payload: Dict[str, Any]) -> str:
    return render_operator_period_summary_markdown_r3_impl(payload,
        facade=_r3_sys.modules[__name__])


def render_operator_daily_summary_markdown(payload: Dict[str, Any]) -> str:
    return render_operator_daily_summary_markdown_r3_impl(payload, facade=_r3_sys.modules[__name__])


def render_operator_symbol_summary_markdown(payload: Dict[str, Any]) -> str:
    return render_operator_symbol_summary_markdown_r3_impl(payload,
        facade=_r3_sys.modules[__name__])


def generate_operator_period_summary(
    *,
    reports_root: Path,
    period_type: str,
    period_key: str,
) -> Tuple[Path, Path, Dict[str, Any]]:
    payload = build_operator_period_summary(
        reports_root=reports_root,
        period_type=period_type,
        period_key=period_key,
    )
    if payload["period_type"] == "weekly":
        paths = weekly_artifact_paths(reports_root, payload["period_key"])
        json_path = paths["weekly_summary_json"]
        md_path = paths["weekly_summary_md"]
    else:
        paths = monthly_artifact_paths(reports_root, payload["period_key"])
        json_path = paths["monthly_summary_json"]
        md_path = paths["monthly_summary_md"]

    md_path.parent.mkdir(parents=True, exist_ok=True)
    _write_validated_json(json_path, payload)
    _write_operator_markdown(md_path, render_operator_period_summary_markdown(payload))
    return md_path, json_path, payload


def generate_operator_daily_summary_artifact(
    *,
    reports_root: Path,
    day: str,
    daily_report_payload: Dict[str, Any] | None = None,
) -> Tuple[Path, Path, Dict[str, Any]]:
    if daily_report_payload is None:
        daily_report_path = daily_artifact_paths(reports_root, str(day or "").strip())["daily_report_json"]
        loaded = _read_json(daily_report_path)
        daily_report_payload = loaded if isinstance(loaded, dict) else None
    payload = build_operator_daily_summary_artifact_payload(
        reports_root=reports_root,
        day=day,
        daily_report_payload=daily_report_payload,
    )
    paths = daily_artifact_paths(reports_root, payload["day"])
    json_path = paths["daily_summary_json"]
    md_path = paths["daily_summary_md"]
    md_path.parent.mkdir(parents=True, exist_ok=True)
    payload["performance_memory_sync"] = sync_strategy_memory_artifacts(
        reports_root=reports_root,
        day=payload["day"],
        source="operator_daily_summary",
    )
    _write_validated_json(json_path, payload)
    _write_operator_markdown(md_path, render_operator_daily_summary_markdown(payload))
    return md_path, json_path, payload


def generate_operator_symbol_summary_artifact(
    *,
    reports_root: Path,
    symbol: str,
    symbol_trade_report_payload: Dict[str, Any] | None = None,
    symbol_memory_payload: Dict[str, Any] | None = None,
) -> Tuple[Path, Path, Dict[str, Any]]:
    payload = build_operator_symbol_summary_artifact_payload(
        reports_root=reports_root,
        symbol=symbol,
        symbol_trade_report_payload=symbol_trade_report_payload,
        symbol_memory_payload=symbol_memory_payload,
    )
    paths = symbol_artifact_paths(reports_root, payload["symbol"])
    json_path = paths["symbol_summary_json"]
    md_path = paths["symbol_summary_md"]
    md_path.parent.mkdir(parents=True, exist_ok=True)
    _write_validated_json(json_path, payload)
    _write_operator_markdown(md_path, render_operator_symbol_summary_markdown(payload))
    return md_path, json_path, payload
