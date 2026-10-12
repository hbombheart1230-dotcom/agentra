from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import re
import time
import unicodedata

from libs.reporting.trade_read_model import (
    brief_collect_top_headlines as _read_model_brief_collect_top_headlines,
    brief_headline_matches_symbol as _read_model_brief_headline_matches_symbol,
    brief_headline_text as _read_model_brief_headline_text,
    brief_norm_symbol_text as _read_model_brief_norm_symbol_text,
    brief_top_numeric_drivers as _read_model_brief_top_numeric_drivers,
    build_operator_brief_detail_view as _read_model_build_operator_brief_detail_view,
    build_linked_trade_report_card as _read_model_build_linked_trade_report_card,
    build_trade_report_detail_view as _read_model_build_trade_report_detail_view,
    build_unlinked_trade_report_card as _read_model_build_unlinked_trade_report_card,
    extract_labeled_bullet as _read_model_extract_labeled_bullet,
    extract_labeled_int as _read_model_extract_labeled_int,
    load_operator_brief_detail_payloads,
    load_reporter_snippet_for_run as _read_model_load_reporter_snippet_for_run,
    load_trade_report_detail_payloads,
    load_trade_report_payloads,
    normalize_canonical_monitor_snapshot as _read_model_normalize_canonical_monitor_snapshot,
    normalize_trade_report_section as _read_model_normalize_trade_report_section,
    parse_canonical_filter_bullets as _read_model_parse_canonical_filter_bullets,
    prefer_richer_trade_report_section as _read_model_prefer_richer_trade_report_section,
    trade_report_artifact_payload as _read_model_trade_report_artifact_payload,
    trade_report_section_bullets as _read_model_trade_report_section_bullets,
    trade_report_section_summary as _read_model_trade_report_section_summary,
)
from apps.operator_ui.data_access_runs import load_run_canonical_sources, prefer_canonical_agent_payload
from apps.operator_ui.data_access_linkage import (
    existing_trade_path as _link_existing_trade_path,
    trade_paths_from_bundle as _link_trade_paths_from_bundle,
    trade_root_from_bundle_path as _link_trade_root_from_bundle_path,
)
from apps.operator_ui.data_access_status import (
    build_portfolio_sync_card as _status_build_portfolio_sync_card,
    normalize_ai_report_diagnostics as _status_normalize_ai_report_diagnostics,
    normalize_report_status as _status_normalize_report_status,
    portfolio_reconciliation_label as _status_portfolio_reconciliation_label,
    portfolio_positions_source_label as _status_portfolio_positions_source_label,
    portfolio_sync_badge_class as _status_portfolio_sync_badge_class,
    portfolio_sync_label as _status_portfolio_sync_label,
    portfolio_sync_sentence as _status_portfolio_sync_sentence,
    report_next_step as _status_report_next_step,
    report_reason_human as _status_report_reason_human,
    report_status_badge_class as _status_report_status_badge_class,
    report_status_label as _status_report_status_label,
    story_type_badge_class as _status_story_type_badge_class,
    story_type_label as _status_story_type_label,
)
from apps.operator_ui.data_access_brief import (
    OPERATOR_BRIEF_REQUIRED_KEYS as BRIEF_REQUIRED_KEYS_MODULE,
    clean_brief_list as _brief_clean_list,
    clean_brief_text as _brief_clean_text,
    is_retryable_brief_failure as _brief_is_retryable_failure,
    operator_brief_is_complete as _brief_is_complete,
    operator_brief_parse_meta as _brief_parse_meta,
)
from libs.llm.llm_router import LLMRouter
from libs.llm.json_response import parse_llm_json_response, required_key_metadata
from libs.llm.model_names import normalize_openrouter_model_name
from libs.core.symbols import normalize_symbol
from libs.reporting.llm_artifacts import (
    build_compact_input_artifact,
    build_llm_response_artifact,
    canonical_llm_status,
    classify_llm_exception,
    daily_artifact_paths,
    iter_trade_day_roots,
    iter_trade_dirs,
    list_misplaced_trade_day_roots,
    make_attempt,
    persist_llm_artifact_refs,
    trade_artifact_paths,
)
from libs.reporting.trade_report_ai import resolve_shared_trade_facts
import sys as _r3_sys
from apps.operator_ui.data_access_brief_canonical_input import (
    _build_canonical_trade_brief_input_r3_impl,
)
from apps.operator_ui.data_access_brief_compaction import (
    _compact_operator_brief_input_for_llm_r3_impl,
    _compact_canonical_trade_for_brief_r3_impl,
    _compact_ranked_symbols_r3_impl,
    _compact_monitor_thresholds_r3_impl,
    _compact_scalar_map_r3_impl,
)
from apps.operator_ui.data_access_brief_monitor_notes import (
    _brief_build_stop_policy_trace_r3_impl,
    _monitor_threshold_shortfall_notes_r3_impl,
    _monitor_watch_axes_r3_impl,
    _monitor_row_summary_r3_impl,
    _should_replace_brief_monitor_summary_r3_impl,
    _prefer_richer_brief_text_r3_impl,
    _strategist_nested_value_r3_impl,
)
from apps.operator_ui.data_access_brief_fallback import (
    _fallback_operator_brief_r3_impl,
    _failure_operator_brief_r3_impl,
    _salvage_operator_brief_fields_r3_impl,
)
from apps.operator_ui.data_access_brief_sanitation import (
    _normalize_operator_brief_payload_r3_impl,
    _sanitize_operator_brief_result_r3_impl,
    _sanitize_operator_brief_text_r3_impl,
    _operator_brief_language_ok_r3_impl,
    _operator_brief_label_ko_r3_impl,
)
from apps.operator_ui.data_access_brief_prompts import (
    _build_operator_brief_messages_r3_impl,
    _build_operator_brief_repair_messages_r3_impl,
    _build_operator_brief_line_messages_r3_impl,
    _parse_operator_brief_lines_r3_impl,
    _build_operator_brief_kr_facts_r3_impl,
    _truncate_json_r3_impl,
)
from apps.operator_ui.data_access_trade_read_models import (
    load_recent_trades_for_day_r3_impl,
    summarize_trades_by_symbol_r3_impl,
    build_overtrading_warning_r3_impl,
    _build_top_candidates_r3_impl,
    load_latest_strategist_prompt_summary_r3_impl,
    load_health_r3_impl,
    load_trade_report_detail_r3_impl,
)
from apps.operator_ui.data_access_value_formatting import (
    _to_datetime_r3_impl,
    _to_epoch_r3_impl,
    _format_percent_r3_impl,
    _format_duration_r3_impl,
    _format_float_r3_impl,
    _friendly_exit_reason_r3_impl,
    _friendly_feature_name_r3_impl,
    _feature_coverage_r3_impl,
    _normalized_feature_coverage_r3_impl,
    _chart_filter_status_and_note_r3_impl,
    _quote_metrics_snapshot_r3_impl,
    _normalize_execution_payload_r3_impl,
    _clean_str_list_r3_impl,
    _latest_evidence_r3_impl,
    _count_stages_r3_impl,
)
from apps.operator_ui.data_access_run_read_models import (
    load_recent_runs_r3_impl,
    _extract_portfolio_guard_payload_from_run_rows_r3_impl,
    _run_activity_meta_r3_impl,
)
from apps.operator_ui.data_access_symbol_run_chain import (
    load_symbol_run_chain_r3_impl,
)
from apps.operator_ui.data_access_brief_facts import (
    brief_facts_canonical_monitor_snapshot_execution,
    brief_facts_confidence_execution_action,
)
from apps.operator_ui.data_access_brief_market_sections import (
    brief_market_candidate_hints_defensive_mode,
    brief_market_anomaly_note_anomaly_status,
    brief_market_active_exit_axis_avg_price_monitor,
)
from apps.operator_ui.data_access_brief_monitor_sections import (
    brief_monitor_canonical_active_exit_axis_canonical_ave,
    brief_monitor_decision_reason_execution_quality,
    brief_monitor_execution_status_label_next_expected_ste,
)
from apps.operator_ui.data_access_brief_input_projection import (
    brief_input_candidate_hints_market_headlines,
    brief_input_scanner_selection_trace,
    brief_input_canonical_monitor_snapshot_stop_policy_t,
    brief_input_commander_applied_policy_monitor_applied,
)
from apps.operator_ui.data_access_brief_render_sections import (
    brief_render_lines,
    brief_render_current_snapshot_entry,
    brief_render_lines_market_headlines,
    brief_render_effect_free_block_3748,
)
from apps.operator_ui.data_access_brief_render_fallback import (
    brief_fallback_comparison_reasons_display_symbol,
    brief_fallback_lines,
)


KST = timezone(timedelta(hours=9), name="KST")


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


def _filled_strategy_scalar(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip().lower() not in {"", "-", "none", "null", "n/a"}
    return True


def _strategist_nested_value(payload: Any, key: str) -> Any:
    return _strategist_nested_value_r3_impl(payload, key, facade=_r3_sys.modules[__name__])


def _strategist_risk_tone(payload: Any) -> str:
    value = _strategist_nested_value(payload, "risk_tone")
    if value is None:
        value = _strategist_nested_value(payload, "risk_mode")
    return str(value or "").strip()


def _strategist_monitor_guidance(payload: Any) -> str:
    value = _strategist_nested_value(payload, "monitor_guidance")
    return str(value or "").strip()


def _env_int_with_fallback(*names: str, default: int) -> int:
    for name in names:
        raw = str(os.getenv(name, "") or "").strip()
        if not raw:
            continue
        try:
            value = int(float(raw))
        except Exception:
            continue
        if value > 0:
            return value
    return int(default)


def _to_epoch(ts: Any) -> Optional[int]:
    return _to_epoch_r3_impl(ts, facade=_r3_sys.modules[__name__])


def _to_datetime(ts: Any) -> Optional[datetime]:
    return _to_datetime_r3_impl(ts, facade=_r3_sys.modules[__name__])


def _iso_to_display(ts: Any) -> str:
    dt = _to_datetime(ts)
    if dt is None:
        return str(ts or "")
    return dt.strftime("%Y-%m-%d %H:%M:%S KST")


def _event_day(ts: Any) -> str:
    dt = _to_datetime(ts)
    if dt is None:
        return ""
    return dt.strftime("%Y-%m-%d")


def _iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
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
                rows.append(obj)
    return rows


def _iter_jsonl_reverse(path: Path, *, block_size: int = 64 * 1024) -> Iterable[Dict[str, Any]]:
    """Yield JSONL objects newest-first without materializing the whole file."""
    if not path.exists():
        return []

    def _gen() -> Iterable[Dict[str, Any]]:
        with path.open("rb") as handle:
            handle.seek(0, os.SEEK_END)
            position = handle.tell()
            remainder = b""
            while position > 0:
                read_size = min(block_size, position)
                position -= read_size
                handle.seek(position)
                chunk = handle.read(read_size)
                lines = (chunk + remainder).split(b"\n")
                remainder = lines[0]
                for raw in reversed(lines[1:]):
                    line = raw.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line.decode("utf-8"))
                    except Exception:
                        continue
                    if isinstance(obj, dict):
                        yield obj
            line = remainder.strip()
            if not line:
                return
            try:
                obj = json.loads(line.decode("utf-8"))
            except Exception:
                return
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


def _latest_matching(path: Path, prefix: str) -> Dict[str, Any]:
    if not path.exists():
        return {}
    files = sorted(path.glob(f"{prefix}_*.json"))
    if not files:
        return {}
    return _read_json(files[-1])


def _read_day_or_latest(path: Path, prefix: str, day: str) -> Dict[str, Any]:
    if path.exists() and day:
        exact = path / f"{prefix}_{day}.json"
        if exact.exists():
            return _read_json(exact)
    return _latest_matching(path, prefix)


def _latest_matching_path(path: Path, prefix: str) -> str:
    if not path.exists():
        return ""
    files = sorted(path.glob(f"{prefix}_*.json"))
    if not files:
        return ""
    return str(files[-1])


def _day_or_latest_path(path: Path, prefix: str, day: str) -> str:
    if path.exists() and day:
        exact = path / f"{prefix}_{day}.json"
        if exact.exists():
            return str(exact)
    return _latest_matching_path(path, prefix)


def _latest_event_day(event_log_path: Path) -> str:
    latest_day = ""
    latest_epoch = -1
    for row in _iter_jsonl(event_log_path):
        ts = row.get("ts_kst") or row.get("ts")
        epoch = _to_epoch(ts)
        if epoch is None or epoch < latest_epoch:
            continue
        latest_epoch = epoch
        latest_day = _event_day(ts)
    return latest_day


def _feature_coverage(feature_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    return _feature_coverage_r3_impl(feature_snapshot, facade=_r3_sys.modules[__name__])


def _normalized_feature_coverage(reported: Dict[str, Any], feature_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    return _normalized_feature_coverage_r3_impl(reported, feature_snapshot,
        facade=_r3_sys.modules[__name__])


def _chart_filter_status_and_note(feature_coverage: Dict[str, Any]) -> tuple[str, str]:
    return _chart_filter_status_and_note_r3_impl(feature_coverage, facade=_r3_sys.modules[__name__])


def _quote_metrics_snapshot(feature_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    return _quote_metrics_snapshot_r3_impl(feature_snapshot, facade=_r3_sys.modules[__name__])


def _truncate_json(v: Any, max_len: int = 800) -> str:
    return _truncate_json_r3_impl(v, max_len, facade=_r3_sys.modules[__name__])


def _clean_brief_text(v: Any) -> str:
    return _brief_clean_text(v)


def _clean_brief_list(v: Any, *, limit: int) -> List[str]:
    return _brief_clean_list(v, limit=limit)


def _extract_json_object(text: Any) -> Dict[str, Any]:
    parsed = parse_llm_json_response(text)
    obj = parsed.get("full_object") if isinstance(parsed.get("full_object"), dict) else parsed.get("partial_object")
    return dict(obj) if isinstance(obj, dict) else {}


def _salvage_operator_brief_fields(text: Any) -> Dict[str, Any]:
    return _salvage_operator_brief_fields_r3_impl(text, facade=_r3_sys.modules[__name__])


def _is_free_model(model: str) -> bool:
    raw = str(model or "").strip().lower()
    return ":free" in raw or raw.endswith("/free")


def _normalize_role_model_name(model: str) -> str:
    return normalize_openrouter_model_name(model)


def _parse_operator_brief_lines(text: Any) -> Dict[str, Any]:
    return _parse_operator_brief_lines_r3_impl(text, facade=_r3_sys.modules[__name__])


def _read_exact_day(path: Path, prefix: str, day: str) -> Dict[str, Any]:
    if not path.exists() or not day:
        return {}
    exact = path / f"{prefix}_{day}.json"
    return _read_json(exact)


def _read_daily_artifact_day(reports_root: Path, day: str, artifact_name: str) -> Dict[str, Any]:
    if not day:
        return {}
    paths = daily_artifact_paths(reports_root, day)
    canonical = Path(paths.get(f"{artifact_name}_json") or "")
    obj = _read_json(canonical)
    if obj:
        return obj
    legacy_canonical = reports_root / "daily" / day / f"{artifact_name}.json"
    obj = _read_json(legacy_canonical)
    if obj:
        return obj
    if artifact_name == "daily_report":
        for key in ("legacy_daily_json", "root_daily_json"):
            obj = _read_json(Path(paths.get(key) or ""))
            if obj:
                return obj
        return _read_exact_day(reports_root / "daily", "daily", day)
    return {}


def _trade_root_from_bundle_path(bundle_path: Path) -> Path:
    return _link_trade_root_from_bundle_path(bundle_path)


def _trade_paths_from_bundle(bundle_path: Path, *, day_hint: str = "", trade_id_hint: str = "") -> Dict[str, Path]:
    return _link_trade_paths_from_bundle(bundle_path, day_hint=day_hint, trade_id_hint=trade_id_hint)


def _existing_trade_path(paths: Dict[str, Path], *keys: str) -> Path:
    return _link_existing_trade_path(paths, *keys)


def _normalize_execution_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _normalize_execution_payload_r3_impl(payload, facade=_r3_sys.modules[__name__])


def _trim_text(value: Any, *, max_len: int = 220) -> str:
    text = str(value or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max(0, max_len - 3)] + "..."


def _clean_str_list(values: Any, *, limit: int = 8, max_len: int = 220) -> List[str]:
    return _clean_str_list_r3_impl(values, limit=limit, max_len=max_len,
        facade=_r3_sys.modules[__name__])


def _story_type_label(story_type: Any) -> str:
    return _status_story_type_label(story_type)


def _story_type_badge_class(story_type: Any) -> str:
    return _status_story_type_badge_class(story_type)


def _normalize_report_status(value: Any) -> str:
    return _status_normalize_report_status(value)


def _report_status_label(status: Any) -> str:
    return _status_report_status_label(status)


def _report_status_badge_class(status: Any) -> str:
    return _status_report_status_badge_class(status)


def _report_reason_human(code: Any) -> str:
    return _status_report_reason_human(code)


def _report_next_step(code: Any) -> str:
    return _status_report_next_step(code)


def _portfolio_sync_badge_class(status: Any) -> str:
    return _status_portfolio_sync_badge_class(status)


def _portfolio_sync_label(status: Any) -> str:
    return _status_portfolio_sync_label(status)


def _portfolio_sync_sentence(status: Any) -> str:
    return _status_portfolio_sync_sentence(status)


def _portfolio_positions_source_label(value: Any) -> str:
    return _status_portfolio_positions_source_label(value)


def _portfolio_reconciliation_label(value: Any) -> str:
    return _status_portfolio_reconciliation_label(value)


def _build_portfolio_sync_card(raw: Any) -> Dict[str, Any]:
    return _status_build_portfolio_sync_card(raw)


def _run_activity_meta(runtime_path: Any, execution: Dict[str, Any], guard_reason: Any, monitor_reason: Any) -> Dict[str, str]:
    return _run_activity_meta_r3_impl(runtime_path, execution, guard_reason, monitor_reason,
        facade=_r3_sys.modules[__name__])


def _extract_portfolio_guard_payload_from_run_rows(run_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    return _extract_portfolio_guard_payload_from_run_rows_r3_impl(run_rows,
        facade=_r3_sys.modules[__name__])


def _normalize_ai_report_diagnostics(
    raw: Any,
    *,
    report_exists: bool,
    lifecycle_status: Any,
    story_type: Any,
    model_hint: Any = "",
    generation: Any = None,
) -> Dict[str, Any]:
    return _status_normalize_ai_report_diagnostics(
        raw,
        report_exists=report_exists,
        lifecycle_status=lifecycle_status,
        story_type=story_type,
        model_hint=model_hint,
        generation=generation,
    )


def _short_run_id(run_id: Any) -> str:
    text = str(run_id or "").strip()
    if len(text) <= 12:
        return text
    return text[:8] + "..."


def _trade_report_index(config: OperatorUIConfig) -> Dict[str, Dict[str, Any]]:
    day_roots = iter_trade_day_roots(config.reports_root)
    if not day_roots:
        return {"by_run_id": {}, "by_story_id": {}}

    by_run_id: Dict[str, Dict[str, Any]] = {}
    by_story_id: Dict[str, Dict[str, Any]] = {}
    seen_bundle_paths: set[str] = set()
    bundle_candidates = sorted(
        [
            path
            for day_root in day_roots
            for trade_dir in iter_trade_dirs(day_root)
            for path in (
                trade_dir / "lifecycle_bundle.json",
                trade_dir / "aggregated_execution_bundle.json",
            )
            if path.exists()
        ],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for bundle_path in bundle_candidates:
        key_path = str(bundle_path.resolve())
        if key_path in seen_bundle_paths:
            continue
        seen_bundle_paths.add(key_path)
        bundle = _read_json(bundle_path)
        if not bundle:
            continue

        bundle_day = str(bundle.get("day") or "").strip()
        lifecycle_status_hint = str(bundle.get("trade_lifecycle_status") or "").strip()
        trade_id_hint = str(bundle.get("trade_id") or bundle.get("story_id") or "").strip()
        paths = _trade_paths_from_bundle(bundle_path, day_hint=bundle_day, trade_id_hint=trade_id_hint)
        lifecycle_path = _existing_trade_path(
            paths,
            "lifecycle_bundle_json",
            "trade_lifecycle_json",
            "legacy_normalized_trade_lifecycle_json",
            "legacy_trade_lifecycle_json",
        )
        lifecycle = _read_json(lifecycle_path) if lifecycle_path.exists() else {}
        trade_id = str(
            lifecycle.get("trade_id")
            or bundle.get("trade_id")
            or bundle.get("story_id")
            or paths.get("trade_root", bundle_path.parent).name
        ).strip()
        story_id = trade_id
        run_id = str(bundle.get("run_id") or "").strip()
        linked_run_ids: List[str] = []
        for rid in list(bundle.get("linked_run_ids") or []):
            text = str(rid or "").strip()
            if text:
                linked_run_ids.append(text)
        if isinstance(lifecycle, dict):
            for rid in list(lifecycle.get("run_ids_all") or []):
                text = str(rid or "").strip()
                if text and text not in linked_run_ids:
                    linked_run_ids.append(text)
            entry = lifecycle.get("entry") if isinstance(lifecycle.get("entry"), dict) else {}
            exit_ctx = lifecycle.get("exit") if isinstance(lifecycle.get("exit"), dict) else {}
            for rid in (entry.get("run_id"), exit_ctx.get("run_id")):
                text = str(rid or "").strip()
                if text and text not in linked_run_ids:
                    linked_run_ids.append(text)
        if run_id and run_id not in linked_run_ids:
            linked_run_ids.append(run_id)

        execution = bundle.get("execution") if isinstance(bundle.get("execution"), dict) else {}
        story_contract = bundle.get("story_contract") if isinstance(bundle.get("story_contract"), dict) else {}
        reporter_status_human = bundle.get("reporter_status_human") if isinstance(bundle.get("reporter_status_human"), dict) else {}
        operator_conclusion_human = bundle.get("operator_conclusion_human") if isinstance(bundle.get("operator_conclusion_human"), dict) else {}
        execution_outcome_human = bundle.get("execution_outcome_human") if isinstance(bundle.get("execution_outcome_human"), dict) else {}

        report_json_path = _existing_trade_path(paths, "ai_trade_report_json", "legacy_trade_report_json")
        report_md_path = _existing_trade_path(paths, "ai_trade_report_md", "legacy_trade_report_md")
        story_input_path = _existing_trade_path(paths, "ai_trade_report_input_json", "legacy_trade_story_input_json")
        operator_brief_json_path = _existing_trade_path(paths, "brief_json")
        operator_brief_md_path = _existing_trade_path(paths, "brief_md")
        strategist_llm_response_path = _existing_trade_path(paths, "strategist_llm_response_json")
        ai_trade_report_llm_response_path = _existing_trade_path(paths, "ai_trade_report_llm_response_json")
        brief_llm_response_path = _existing_trade_path(paths, "brief_llm_response_json")
        trade_provenance_path = _existing_trade_path(paths, "trade_provenance_json")
        trade_health_path = _existing_trade_path(paths, "trade_health_json")
        trade_artifact_links_path = _existing_trade_path(paths, "trade_artifact_links_json")
        trade_provenance = _read_json(trade_provenance_path) if trade_provenance_path.exists() else {}
        trade_health = _read_json(trade_health_path) if trade_health_path.exists() else {}
        report = _read_json(report_json_path)
        executive = report.get("executive_summary") if isinstance(report.get("executive_summary"), dict) else {}
        reporter_eval = report.get("reporter_evaluation") if isinstance(report.get("reporter_evaluation"), dict) else {}
        final_conclusion = report.get("final_operator_conclusion") if isinstance(report.get("final_operator_conclusion"), dict) else {}
        generation = report.get("generation") if isinstance(report.get("generation"), dict) else {}
        lifecycle_summary_obj = lifecycle.get("summary") if isinstance(lifecycle.get("summary"), dict) else {}
        lifecycle_status = str(lifecycle.get("status") or bundle.get("trade_lifecycle_status") or report.get("status") or "").strip().lower()
        lifecycle_summary = (
            _trim_text(lifecycle_summary_obj.get("lifecycle_summary_human"), max_len=260)
            or _trim_text(bundle.get("trade_lifecycle_summary"), max_len=260)
            or _trim_text(final_conclusion.get("summary"), max_len=260)
        )

        story_type = str(story_contract.get("story_type") or lifecycle.get("story_type") or report.get("story_type") or "").strip().lower()
        execution_mode_label = str(story_contract.get("execution_mode_label") or lifecycle.get("execution_mode_label") or report.get("execution_mode_label") or "").strip()
        report_summary = (
            _trim_text(executive.get("summary"), max_len=260)
            or _trim_text(final_conclusion.get("summary"), max_len=260)
            or _trim_text(operator_conclusion_human.get("summary"), max_len=260)
            or _trim_text(execution_outcome_human.get("summary"), max_len=260)
        )
        reporter_summary = (
            _trim_text(reporter_eval.get("summary"), max_len=220)
            or _trim_text(reporter_status_human.get("summary"), max_len=220)
            or "Reporter linkage summary is not available yet."
        )

        ts_epoch = _to_epoch(bundle.get("ts"))
        if ts_epoch is None:
            ts_epoch = int(bundle_path.stat().st_mtime)
        path_priority = 2 if bundle_path.name == "lifecycle_bundle.json" else (2 if bundle_path.parent.name == "lifecycle" else 1)
        symbol = normalize_symbol(
            execution.get("symbol") or report.get("symbol") or "",
            allow_test_symbols=True,
        )
        action = str(execution.get("action") or report.get("action") or "").upper()
        report_exists = bool(report_json_path.exists() or report_md_path.exists())
        raw_diagnostics = (
            report.get("ai_report_diagnostics")
            if isinstance(report.get("ai_report_diagnostics"), dict)
            else bundle.get("ai_report_diagnostics")
            if isinstance(bundle.get("ai_report_diagnostics"), dict)
            else lifecycle.get("ai_report_diagnostics")
            if isinstance(lifecycle.get("ai_report_diagnostics"), dict)
            else trade_health.get("ai_report_diagnostics")
            if isinstance(trade_health.get("ai_report_diagnostics"), dict)
            else {}
        )
        diagnostics = _normalize_ai_report_diagnostics(
            raw_diagnostics,
            report_exists=report_exists,
            lifecycle_status=lifecycle_status,
            story_type=story_type,
            model_hint=generation.get("model"),
            generation=generation,
        )
        report_available = bool(report_exists)
        record = {
            "trade_id": trade_id,
            "story_id": story_id,
            "run_id": run_id,
            "run_id_short": _short_run_id(run_id),
            "linked_run_ids": linked_run_ids,
            "symbol": symbol,
            "action": action,
            "story_type": story_type,
            "story_type_label": _story_type_label(story_type),
            "story_type_badge_class": _story_type_badge_class(story_type),
            "lifecycle_status": lifecycle_status or "unknown",
            "lifecycle_status_label": (lifecycle_status or "unknown").upper(),
            "lifecycle_summary": lifecycle_summary or "Lifecycle summary is not available yet.",
            "execution_mode_label": execution_mode_label or "not captured",
            "report_available": report_available,
            "report_status": str(diagnostics.get("report_status") or ""),
            "report_status_label": str(diagnostics.get("report_status_label") or _report_status_label("")),
            "report_status_badge_class": str(diagnostics.get("report_status_badge_class") or "status-badge"),
            "report_reason_code": str(diagnostics.get("report_reason_code") or ""),
            "report_reason_human": str(diagnostics.get("report_reason_human") or ""),
            "report_next_expected_step": str(diagnostics.get("next_expected_step") or ""),
            "report_generation_attempted": bool(diagnostics.get("generation_attempted")),
            "report_generation_ts": str(diagnostics.get("generation_ts") or ""),
            "report_generation_model": str(diagnostics.get("llm_model_used") or ""),
            "report_generation_provider": str(diagnostics.get("llm_provider") or "OpenRouter"),
            "ai_report_diagnostics": diagnostics,
            "report_summary": report_summary or "Per-trade report summary was not generated yet.",
            "reporter_status_human": reporter_summary,
            "report_link": f"/reports/trade/{trade_id}" if trade_id and report_exists else "",
            "operator_brief_available": bool(trade_id),
            "operator_brief_link": f"/reports/trade/{trade_id}/brief" if trade_id else "",
            "trade_report_json_path": str(report_json_path) if report_json_path.exists() else "",
            "trade_report_md_path": str(report_md_path) if report_md_path.exists() else "",
            "trade_story_input_path": str(story_input_path) if story_input_path.exists() else "",
            "ai_trade_report_json_path": str(report_json_path) if report_json_path.exists() else "",
            "ai_trade_report_md_path": str(report_md_path) if report_md_path.exists() else "",
            "ai_trade_report_input_path": str(story_input_path) if story_input_path.exists() else "",
            "trade_lifecycle_json_path": str(lifecycle_path) if lifecycle_path.exists() else "",
            "operator_brief_json_path": str(operator_brief_json_path) if operator_brief_json_path.exists() else "",
            "operator_brief_md_path": str(operator_brief_md_path) if operator_brief_md_path.exists() else "",
            "strategist_llm_response_path": str(strategist_llm_response_path) if strategist_llm_response_path.exists() else "",
            "ai_trade_report_llm_response_path": str(ai_trade_report_llm_response_path) if ai_trade_report_llm_response_path.exists() else "",
            "brief_llm_response_path": str(brief_llm_response_path) if brief_llm_response_path.exists() else "",
            "trade_provenance_json_path": str(trade_provenance_path) if trade_provenance_path.exists() else "",
            "trade_health_json_path": str(trade_health_path) if trade_health_path.exists() else "",
            "trade_artifact_links_json_path": str(trade_artifact_links_path) if trade_artifact_links_path.exists() else "",
            "section_provenance": (
                dict(trade_provenance.get("section_provenance") or {})
                if isinstance(trade_provenance, dict)
                else {}
            ),
            "aggregated_bundle_path": str(bundle_path),
            "trade_root_path": str(paths.get("trade_root") or ""),
            "ts_epoch": ts_epoch,
            "_path_priority": path_priority,
        }

        if story_id:
            current_story = by_story_id.get(story_id)
            if (not current_story) or (
                int(record.get("_path_priority") or 0) > int(current_story.get("_path_priority") or 0)
                or (
                    int(record.get("_path_priority") or 0) == int(current_story.get("_path_priority") or 0)
                    and int(record.get("ts_epoch") or 0) >= int(current_story.get("ts_epoch") or 0)
                )
            ):
                by_story_id[story_id] = record
        for rid in linked_run_ids:
            current = by_run_id.get(rid)
            if (not current) or (
                int(record.get("_path_priority") or 0) > int(current.get("_path_priority") or 0)
                or (
                    int(record.get("_path_priority") or 0) == int(current.get("_path_priority") or 0)
                    and int(record.get("ts_epoch") or 0) >= int(current.get("ts_epoch") or 0)
                )
            ):
                by_run_id[rid] = record

    return {"by_run_id": by_run_id, "by_story_id": by_story_id}


def _trade_report_meta_for_run(config: OperatorUIConfig, run_id: str) -> Dict[str, Any]:
    index = _trade_report_index(config)
    return dict((index.get("by_run_id") or {}).get(str(run_id or "").strip()) or {})


def _trade_report_meta_for_story(config: OperatorUIConfig, story_id: str) -> Dict[str, Any]:
    index = _trade_report_index(config)
    return dict((index.get("by_story_id") or {}).get(str(story_id or "").strip()) or {})


@dataclass(frozen=True)
class OperatorUIConfig:
    repo_root: Path
    reports_root: Path
    event_log_path: Path
    evidence_log_path: Path
    strategy_memory_path: Path
    operator_ui_cache_path: Path

    @staticmethod
    def from_env(repo_root: Optional[Path] = None) -> "OperatorUIConfig":
        root = Path(repo_root or Path(__file__).resolve().parents[2])
        return OperatorUIConfig(
            repo_root=root,
            reports_root=Path(os.getenv("OPERATOR_UI_REPORTS_ROOT", str(root / "reports"))),
            event_log_path=Path(os.getenv("OPERATOR_UI_EVENT_LOG_PATH", str(root / "data" / "logs" / "events.jsonl"))),
            evidence_log_path=Path(os.getenv("OPERATOR_UI_EVIDENCE_LOG_PATH", str(root / "data" / "evidence_ledger" / "events.jsonl"))),
            strategy_memory_path=Path(os.getenv("OPERATOR_UI_STRATEGY_MEMORY_PATH", str(root / "data" / "strategy_memory" / "daily"))),
            operator_ui_cache_path=Path(os.getenv("OPERATOR_UI_CACHE_PATH", str(root / "data" / "operator_ui" / "brief_cache"))),
        )


def load_overview(config: OperatorUIConfig) -> Dict[str, Any]:
    latest_day = _latest_event_day(config.event_log_path)
    daily = _read_daily_artifact_day(config.reports_root, latest_day, "daily_report")
    operator_summary = _read_daily_artifact_day(config.reports_root, latest_day, "operator_summary")
    reporter = _read_exact_day(config.reports_root / "dev" / "analysis" / "reporter_analysis", "reporter_analysis", latest_day)
    reconciliation = _read_exact_day(config.reports_root / "reconciliation", "broker_trade_reconciliation", latest_day)

    executive = operator_summary.get("executive_summary") if isinstance(operator_summary.get("executive_summary"), dict) else {}
    health = operator_summary.get("system_health_status") if isinstance(operator_summary.get("system_health_status"), dict) else {}
    trading = operator_summary.get("trading_activity_summary") if isinstance(operator_summary.get("trading_activity_summary"), dict) else {}
    recon_summary = reconciliation.get("summary") if isinstance(reconciliation.get("summary"), dict) else {}
    ai_review = reporter.get("ai_review") if isinstance(reporter.get("ai_review"), dict) else {}
    trade_summary = reporter.get("trade_summary") if isinstance(reporter.get("trade_summary"), dict) else {}
    strategy_memory_timeline = load_strategy_memory_timeline(config, limit=7)
    latest_day = str(latest_day or "")
    all_today_trades = load_recent_trades_for_day(config, latest_day, limit=200)
    today_trades = all_today_trades[:8]
    traded_symbol_summary = summarize_trades_by_symbol(all_today_trades)
    overtrading_warning = build_overtrading_warning(all_today_trades, traded_symbol_summary, reporter)
    latest_prompt = load_latest_strategist_prompt_summary(config, latest_day)
    today_rows = list(_iter_jsonl(config.event_log_path))
    today_rows = [row for row in today_rows if not latest_day or _event_day(row.get("ts_kst") or row.get("ts")) == latest_day]
    live_route_rows = [
        row
        for row in today_rows
        if str(row.get("stage") or "") == "commander_router"
        and str(row.get("event") or "") == "route"
    ]
    live_verdict_rows = [
        row
        for row in today_rows
        if str(row.get("stage") or "") == "execute_from_packet"
        and str(row.get("event") or "") == "verdict"
        and isinstance(row.get("payload"), dict)
    ]
    live_allowed_total = 0
    live_blocked_total = 0
    live_noop_total = 0
    live_block_reason_top: Dict[str, int] = {}
    for row in live_verdict_rows:
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
        allowed = payload.get("allowed")
        reason = str(payload.get("reason") or "").strip()
        if allowed is True:
            live_allowed_total += 1
            continue
        if reason == "noop_intent_skipped":
            live_noop_total += 1
            continue
        if allowed is False:
            live_blocked_total += 1
            if reason:
                live_block_reason_top[reason] = _safe_int(live_block_reason_top.get(reason), 0) + 1
    live_run_total = len(live_route_rows)
    live_execution_total = len(all_today_trades)
    live_action_counts: Dict[str, int] = {}
    for row in all_today_trades:
        action = str(row.get("action") or "").upper().strip()
        if not action:
            continue
        live_action_counts[action] = _safe_int(live_action_counts.get(action), 0) + 1
    live_events_total = live_run_total
    live_symbols_traded = [str(row.get("symbol") or "") for row in traded_symbol_summary[:8] if str(row.get("symbol") or "").strip()]

    reported_run_total = _safe_int(trading.get("run_total"), 0)
    reported_exec_total = _safe_int(trading.get("executions_total"), 0)
    reported_blocked_total = _safe_int(trading.get("blocked_total"), 0)
    reported_daily_events = _safe_int(daily.get("events"), 0)
    reported_daily_approvals = _safe_int(daily.get("approvals"), 0)
    reported_daily_blocks = _safe_int(daily.get("blocks"), 0)
    reported_reporter_trade_count = _safe_int(trade_summary.get("trade_count"), 0)
    reported_reporter_symbols = [str(v or "") for v in list(trade_summary.get("symbols_traded") or []) if str(v or "").strip()]
    live_snapshot_mismatch = any(
        [
            live_run_total > reported_run_total,
            live_execution_total > reported_exec_total,
            live_allowed_total > reported_daily_approvals,
            live_blocked_total != reported_blocked_total and live_execution_total > 0,
            live_events_total > reported_daily_events,
            live_execution_total > reported_reporter_trade_count,
            live_symbols_traded != reported_reporter_symbols[: len(live_symbols_traded)],
        ]
    )

    if latest_day and live_snapshot_mismatch:
        top_block_reason = ""
        if live_block_reason_top:
            top_block_reason = sorted(live_block_reason_top.items(), key=lambda item: (-_safe_int(item[1]), str(item[0])))[0][0]
        executive = {
            "system_status": str(executive.get("system_status") or health.get("system_health_level") or "LIVE"),
            "summary_lines": [
                f"[LIVE] runs={live_run_total}, executions={live_execution_total} (approved={live_allowed_total}, blocked={live_blocked_total}, noop={live_noop_total}).",
                f"Top guard block: {top_block_reason or 'none'}",
            ] + list(executive.get("summary_lines") or []),
        }
        trading = {
            **trading,
            "run_total": live_run_total,
            "executions_total": live_execution_total,
            "blocked_total": live_blocked_total,
        }
        daily = {
            **daily,
            "events": live_events_total,
            "decision_actions": live_action_counts,
            "approvals": live_allowed_total,
            "blocks": live_blocked_total,
        }
        if reporter:
            reporter = {
                **reporter,
                "trade_summary": {
                    **trade_summary,
                    "trade_count": live_execution_total,
                    "symbols_traded": live_symbols_traded,
                },
            }
            ai_review = reporter.get("ai_review") if isinstance(reporter.get("ai_review"), dict) else {}
            trade_summary = reporter.get("trade_summary") if isinstance(reporter.get("trade_summary"), dict) else {}
            if ai_review:
                reporter["ai_review"] = {
                    **ai_review,
                    "status": "snapshot" if str(ai_review.get("status") or "").strip().lower() == "ok" else ai_review.get("status"),
                }

    reported_recon_local = _safe_int(recon_summary.get("local_total"), 0)
    reported_recon_broker = _safe_int(recon_summary.get("broker_total"), 0)
    reported_recon_matched = _safe_int(recon_summary.get("matched_by_ord_no"), 0)
    recon_stale_vs_live = live_execution_total > max(reported_recon_local, reported_recon_broker, reported_recon_matched)
    if latest_day and live_execution_total > 0 and (not reconciliation or recon_stale_vs_live):
        reconciliation = {
            "summary": {
                "local_total": live_execution_total,
                "broker_total": reported_recon_broker,
                "matched_by_ord_no": reported_recon_matched,
                "broker_window_limited": bool(recon_summary.get("broker_window_limited")),
                "pending": True,
                "sentence": "Intraday reconciliation has not been generated yet. Local executions are ahead of broker matching.",
            }
        }
        recon_summary = reconciliation.get("summary") if isinstance(reconciliation.get("summary"), dict) else {}

    if not operator_summary and latest_day:
        operator_summary_live_lines: List[str] = []
        if live_run_total:
            operator_summary_live_lines.append(f"live event log fallback active for {latest_day}")
        if live_execution_total:
            operator_summary_live_lines.append(f"today executions observed in log: {live_execution_total}")
        if live_blocked_total:
            operator_summary_live_lines.append(f"today blocked verdicts observed in log: {live_blocked_total}")
        live_status = "LIVE" if (live_run_total or live_execution_total or live_blocked_total) else "UNKNOWN"
        executive = {
            "system_status": live_status,
            "summary_lines": operator_summary_live_lines[:4],
        }
        health = {
            "system_health_level": live_status,
            "recommended_action": (
                [f"review same-day overtrading warning: {overtrading_warning.get('level')}"]
                if str(overtrading_warning.get("level") or "normal") in {"elevated", "high"}
                else ["generate operator summary after closeout to replace live fallback"]
            )[:4],
        }
        trading = {
            "run_total": live_run_total,
            "executions_total": live_execution_total,
            "blocked_total": live_blocked_total,
        }

    if not reporter and latest_day:
        reporter = {
            "ai_review": {"status": "not_generated_yet"},
            "ai_run_grade": "-",
            "ai_summary": "Same-day reporter analysis has not been generated yet.",
            "trade_summary": {
                "trade_count": live_execution_total,
                "symbols_traded": [str(row.get("symbol") or "") for row in traded_symbol_summary[:8]],
            },
        }
    ai_review = reporter.get("ai_review") if isinstance(reporter.get("ai_review"), dict) else {}
    trade_summary = reporter.get("trade_summary") if isinstance(reporter.get("trade_summary"), dict) else {}
    recent_runs = load_recent_runs(config, limit=200)
    latest_run_sync = next(
        (
            dict((row or {}).get("portfolio_sync") or {})
            for row in recent_runs
            if isinstance(row, dict)
            and str(((row.get("portfolio_sync") or {}).get("status") or "")).strip().lower() not in {"", "unavailable"}
        ),
        (
            dict((recent_runs[0] or {}).get("portfolio_sync") or {})
            if recent_runs and isinstance(recent_runs[0], dict)
            else _build_portfolio_sync_card({})
        ),
    )
    sync_runs_today = [
        row for row in recent_runs
        if latest_day and str(row.get("ts") or "").startswith(latest_day)
    ]
    sync_summary = {
        "today_total": len(sync_runs_today),
        "aligned_total": sum(1 for row in sync_runs_today if str((row.get("portfolio_sync") or {}).get("status") or "") == "aligned"),
        "reconciled_total": sum(1 for row in sync_runs_today if str((row.get("portfolio_sync") or {}).get("status") or "") == "reconciled"),
        "alert_total": sum(1 for row in sync_runs_today if str((row.get("portfolio_sync") or {}).get("status") or "") in {"mismatch", "reader_error"}),
    }
    daily_paths = daily_artifact_paths(config.reports_root, latest_day) if latest_day else {}
    daily_report_path = Path(daily_paths.get("daily_report_json") or "") if daily_paths else Path()
    legacy_operator_daily_path = Path(daily_paths.get("legacy_daily_json") or "") if daily_paths else Path()
    root_operator_daily_path = Path(daily_paths.get("root_daily_json") or "") if daily_paths else Path()
    legacy_daily_report_path = config.reports_root / "daily" / latest_day / "daily_report.json" if latest_day else Path()
    flat_daily_report_path = config.reports_root / "daily" / f"daily_{latest_day}.json" if latest_day else Path()
    operator_summary_path = Path(daily_paths.get("operator_summary_json") or "") if daily_paths else Path()
    legacy_operator_summary_path = config.reports_root / "daily" / latest_day / "operator_summary.json" if latest_day else Path()

    return {
        "latest_day": latest_day,
        "daily": {
            "events": _safe_int(daily.get("events"), 0),
            "decision_actions": dict(daily.get("decision_actions") or {}),
            "approvals": _safe_int(daily.get("approvals"), 0),
            "blocks": _safe_int(daily.get("blocks"), 0),
            "path": (
                str(daily_report_path)
                if latest_day and daily_report_path.exists()
                else (
                    str(legacy_operator_daily_path)
                    if latest_day and legacy_operator_daily_path.exists()
                    else (
                        str(root_operator_daily_path)
                        if latest_day and root_operator_daily_path.exists()
                        else (
                            str(legacy_daily_report_path)
                            if latest_day and legacy_daily_report_path.exists()
                            else (str(flat_daily_report_path) if latest_day and flat_daily_report_path.exists() else "")
                        )
                    )
                )
            ),
        },
        "operator_summary": {
            "system_status": str(executive.get("system_status") or "UNKNOWN"),
            "summary_lines": list(executive.get("summary_lines") or [])[:4],
            "health_level": str(health.get("system_health_level") or "UNKNOWN"),
            "recommended_action": list(health.get("recommended_action") or [])[:4],
            "run_total": _safe_int(trading.get("run_total"), 0),
            "executions_total": _safe_int(trading.get("executions_total"), 0),
            "blocked_total": _safe_int(trading.get("blocked_total"), 0),
            "path": (
                str(operator_summary_path)
                if latest_day and operator_summary_path.exists()
                else (
                    str(legacy_operator_summary_path)
                    if latest_day and legacy_operator_summary_path.exists()
                    else ""
                )
            ),
        },
        "reporter": {
            "trade_count": _safe_int(trade_summary.get("trade_count"), 0),
            "symbols_traded": list(trade_summary.get("symbols_traded") or [])[:8],
            "ai_status": str(ai_review.get("status") or "disabled"),
            "ai_run_grade": str(reporter.get("ai_run_grade") or "N/A"),
            "ai_summary": str(reporter.get("ai_summary") or ""),
            "path": str(config.reports_root / "dev" / "analysis" / "reporter_analysis" / f"reporter_analysis_{latest_day}.json") if latest_day else "",
        },
        "reconciliation": {
            "local_total": _safe_int(recon_summary.get("local_total"), 0),
            "broker_total": _safe_int(recon_summary.get("broker_total"), 0),
            "matched_by_ord_no": _safe_int(recon_summary.get("matched_by_ord_no"), 0),
            "broker_window_limited": bool(recon_summary.get("broker_window_limited")),
            "pending": bool(recon_summary.get("pending")),
            "sentence": str(recon_summary.get("sentence") or ""),
            "path": str(config.reports_root / "reconciliation" / f"broker_trade_reconciliation_{latest_day}.json") if latest_day else "",
        },
        "today_trades": today_trades,
        "today_traded_symbols": traded_symbol_summary,
        "overtrading_warning": overtrading_warning,
        "latest_strategist_prompt": latest_prompt,
        "strategy_memory_timeline": strategy_memory_timeline,
        "portfolio_sync": latest_run_sync,
        "portfolio_sync_summary": sync_summary,
    }


def load_recent_trades_for_day(config: OperatorUIConfig, day: str, *, limit: int = 8) -> List[Dict[str, Any]]:
    return load_recent_trades_for_day_r3_impl(config, day, limit=limit,
        facade=_r3_sys.modules[__name__])


def summarize_trades_by_symbol(trades: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return summarize_trades_by_symbol_r3_impl(trades, facade=_r3_sys.modules[__name__])


def build_overtrading_warning(
    trades: List[Dict[str, Any]],
    traded_symbols: List[Dict[str, Any]],
    reporter_report: Dict[str, Any],
) -> Dict[str, Any]:
    return build_overtrading_warning_r3_impl(trades, traded_symbols, reporter_report,
        facade=_r3_sys.modules[__name__])


def load_symbol_run_chain(config: OperatorUIConfig, day: str, symbol: str, *, limit: int = 3) -> List[Dict[str, Any]]:
    return load_symbol_run_chain_r3_impl(config, day, symbol, limit=limit,
        facade=_r3_sys.modules[__name__])


def load_latest_strategist_prompt_summary(config: OperatorUIConfig, day: str) -> Dict[str, Any]:
    return load_latest_strategist_prompt_summary_r3_impl(config, day,
        facade=_r3_sys.modules[__name__])


def load_recent_runs(
    config: OperatorUIConfig,
    *,
    limit: int = 50,
    mismatch_only: bool = False,
    activity_view: str = "all",
) -> List[Dict[str, Any]]:
    return load_recent_runs_r3_impl(config, limit=limit, mismatch_only=mismatch_only,
        activity_view=activity_view, facade=_r3_sys.modules[__name__])


OPERATOR_BRIEF_REQUIRED_KEYS = [
    *list(BRIEF_REQUIRED_KEYS_MODULE),
]

OPERATOR_BRIEF_OPTIONAL_KEYS = [
    "executive_summary",
    "scanner_reason",
    "entry_summary",
    "holding_summary",
    "exit_plan_summary",
    "risk_summary",
    "next_checkpoints",
]

OPERATOR_BRIEF_ARTIFACT_VERSION = 14


def _operator_brief_parse_meta(raw: Any, parsed: Dict[str, Any] | None) -> Dict[str, Any]:
    return _brief_parse_meta(raw, parsed)


def _operator_brief_is_complete(parsed: Dict[str, Any]) -> bool:
    return _brief_is_complete(parsed)


def _is_retryable_brief_failure(status: str, reason: str = "") -> bool:
    return _brief_is_retryable_failure(status, reason)


def _latest_evidence(rows: List[Dict[str, Any]], *, agent: str, stage: str) -> Dict[str, Any]:
    return _latest_evidence_r3_impl(rows, agent=agent, stage=stage,
        facade=_r3_sys.modules[__name__])


def _reporter_snippet_for_run(config: OperatorUIConfig, run_id: str, run_day: str) -> Dict[str, Any]:
    return _read_model_load_reporter_snippet_for_run(
        config.reports_root,
        run_id,
        run_day,
        read_json=_read_json,
    )


def _report_section(report: Dict[str, Any], key: str, fallback_summary: str = "") -> Dict[str, Any]:
    return _read_model_normalize_trade_report_section(
        report,
        key,
        fallback_summary,
        trim_text=_trim_text,
        clean_str_list=_clean_str_list,
    )


def load_trade_report_detail(config: OperatorUIConfig, story_id: str) -> Dict[str, Any]:
    return load_trade_report_detail_r3_impl(config, story_id, facade=_r3_sys.modules[__name__])


def load_operator_brief_detail(config: OperatorUIConfig, story_id: str) -> Dict[str, Any]:
    meta = _trade_report_meta_for_story(config, story_id)
    if not meta:
        return {"found": False, "story_id": str(story_id or "")}

    run_id = str(meta.get("run_id") or "").strip()
    payloads = load_operator_brief_detail_payloads(
        meta,
        read_json=_read_json,
        allow_saved_brief=not _operator_brief_force_regenerate_enabled(),
    )
    brief = payloads.get("brief_data") if isinstance(payloads.get("brief_data"), dict) else {}
    json_path = Path(str((payloads.get("paths") or {}).get("operator_brief_json") or ""))
    md_path = Path(str((payloads.get("paths") or {}).get("operator_brief_md") or ""))

    if not isinstance(brief, dict) or not brief:
        if run_id:
            detail = load_run_detail(config, run_id)
            if not detail.get("found"):
                return {"found": False, "story_id": str(story_id or ""), "trade_id": str(meta.get("trade_id") or "")}
            trade_report = detail.get("trade_report") if isinstance(detail.get("trade_report"), dict) else {}
            brief = detail.get("operator_brief") if isinstance(detail.get("operator_brief"), dict) else {}
            json_path = Path(str(trade_report.get("operator_brief_json_path") or ""))
            md_path = Path(str(trade_report.get("operator_brief_md_path") or ""))

    if not isinstance(brief, dict) or not brief:
        return {
            "found": False,
            "story_id": str(meta.get("story_id") or story_id),
            "trade_id": str(meta.get("trade_id") or ""),
            "reason": "operator_brief_not_available",
        }

    detail = _read_model_build_operator_brief_detail_view(
        meta,
        brief,
        json_path=str(json_path) if json_path.exists() else "",
        md_path=str(md_path) if md_path.exists() else "",
        normalize_symbol=normalize_symbol,
        clean_str_list=_clean_str_list,
    )
    detail["trade_id"] = str(detail.get("trade_id") or meta.get("trade_id") or meta.get("story_id") or story_id)
    detail["story_id"] = str(detail.get("story_id") or meta.get("story_id") or story_id)
    return detail


_FEATURE_NAME_MAP: Dict[str, str] = {
    "engine_ma20_gap": "MA20 gap support",
    "engine_ma60": "MA60 trend anchor",
    "engine_ma120": "MA120 long trend",
    "engine_adx14": "ADX trend strength",
    "engine_trend_strength": "trend strength score",
    "engine_volume_spike20": "volume expansion",
    "engine_volatility20": "volatility profile",
    "engine_vwap_distance": "VWAP distance",
    "engine_sector_relative_strength": "sector relative strength",
    "engine_cross_section_rank": "cross-sectional rank",
    "engine_regime": "regime detection",
    "engine_signal_score": "composite signal score",
}


def _format_float(v: Any, digits: int = 2) -> str:
    return _format_float_r3_impl(v, digits, facade=_r3_sys.modules[__name__])


def _format_percent(v: Any, digits: int = 1) -> str:
    return _format_percent_r3_impl(v, digits, facade=_r3_sys.modules[__name__])


def _format_duration(seconds: Any) -> str:
    return _format_duration_r3_impl(seconds, facade=_r3_sys.modules[__name__])


def _friendly_feature_name(key: str) -> str:
    return _friendly_feature_name_r3_impl(key, facade=_r3_sys.modules[__name__])


def _friendly_exit_reason(reason: Any) -> str:
    return _friendly_exit_reason_r3_impl(reason, facade=_r3_sys.modules[__name__])


def _monitor_watch_axes(thresholds: Dict[str, Any]) -> List[str]:
    return _monitor_watch_axes_r3_impl(thresholds, facade=_r3_sys.modules[__name__])


def _monitor_row_summary(monitor_summary: Dict[str, Any], monitor_trace: Dict[str, Any]) -> Dict[str, Any]:
    return _monitor_row_summary_r3_impl(monitor_summary, monitor_trace,
        facade=_r3_sys.modules[__name__])


def _build_top_candidates(scanner_summary: Dict[str, Any], scanner_trace: Dict[str, Any], selected_symbol: str) -> List[Dict[str, Any]]:
    return _build_top_candidates_r3_impl(scanner_summary, scanner_trace, selected_symbol,
        facade=_r3_sys.modules[__name__])


def _trade_report_artifact_payload(trade_report: Dict[str, Any], key: str) -> Dict[str, Any]:
    return _read_model_trade_report_artifact_payload(trade_report, key)


def _trade_report_section_payload(*sections: Any) -> Dict[str, Any]:
    for section in sections:
        if isinstance(section, dict) and section:
            return section
    return {}


def _prefer_richer_trade_report_section(*sections: Any) -> Dict[str, Any]:
    return _read_model_prefer_richer_trade_report_section(*sections)


def _trade_report_section_summary(section: Dict[str, Any], fallback: str = "") -> str:
    return _read_model_trade_report_section_summary(section, fallback)


def _trade_report_section_bullets(section: Dict[str, Any], *, limit: int = 6) -> List[str]:
    return _read_model_trade_report_section_bullets(section, limit=limit)


def _extract_labeled_bullet(bullets: List[str], labels: List[str]) -> str:
    return _read_model_extract_labeled_bullet(bullets, labels)


def _extract_labeled_int(bullets: List[str], labels: List[str]) -> Optional[int]:
    return _read_model_extract_labeled_int(bullets, labels)


def _parse_canonical_filter_bullets(bullets: List[str]) -> List[Dict[str, str]]:
    return _read_model_parse_canonical_filter_bullets(bullets)


def _prefer_runtime_reporter_state(reporter: Dict[str, Any]) -> bool:
    if not isinstance(reporter, dict):
        return False
    return bool(reporter.get("reason") or reporter.get("ai_summary") or reporter.get("found"))


def _normalize_canonical_monitor_snapshot(snapshot: Dict[str, Any], story_monitor: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return _read_model_normalize_canonical_monitor_snapshot(
        snapshot,
        story_monitor,
        format_duration=_format_duration,
        format_percent=_format_percent,
        format_float=_format_float,
        friendly_exit_reason=_friendly_exit_reason,
    )


def _brief_headline_text(row: Any) -> str:
    return _read_model_brief_headline_text(row, trim_text=_trim_text)


def _brief_norm_symbol_text(value: Any) -> str:
    return _read_model_brief_norm_symbol_text(value, normalize_symbol=normalize_symbol)


def _brief_headline_matches_symbol(row: Any, symbol: str) -> bool:
    return _read_model_brief_headline_matches_symbol(
        row,
        symbol,
        normalize_symbol=normalize_symbol,
    )


def _brief_collect_top_headlines(rows: Any, *, limit: int = 3, symbol: str = "") -> List[str]:
    return _read_model_brief_collect_top_headlines(
        rows,
        limit=limit,
        symbol=symbol,
        trim_text=_trim_text,
        normalize_symbol=normalize_symbol,
    )


def _brief_top_numeric_drivers(values: Any, *, limit: int = 4) -> Dict[str, float]:
    return _read_model_brief_top_numeric_drivers(values, limit=limit)


def _brief_build_stop_policy_trace(monitor: Dict[str, Any]) -> Dict[str, Any]:
    return _brief_build_stop_policy_trace_r3_impl(monitor, facade=_r3_sys.modules[__name__])


def _build_canonical_trade_brief_input(trade_report: Dict[str, Any]) -> Dict[str, Any]:
    return _build_canonical_trade_brief_input_r3_impl(trade_report,
        facade=_r3_sys.modules[__name__])


def _build_operator_brief_sections(detail: Dict[str, Any]) -> Dict[str, Any]:
    strategist = detail.get("strategist") if isinstance(detail.get("strategist"), dict) else {}
    scanner = detail.get("scanner") if isinstance(detail.get("scanner"), dict) else {}
    monitor = detail.get("monitor") if isinstance(detail.get("monitor"), dict) else {}
    supervisor = detail.get("supervisor") if isinstance(detail.get("supervisor"), dict) else {}
    executor = detail.get("executor") if isinstance(detail.get("executor"), dict) else {}
    reporter = detail.get("reporter") if isinstance(detail.get("reporter"), dict) else {}
    trade_report = detail.get("trade_report") if isinstance(detail.get("trade_report"), dict) else {}
    trade_report_data = trade_report.get("report_data") if isinstance(trade_report.get("report_data"), dict) else {}
    trade_story_input = trade_report_data.get("trade_story_input") if isinstance(trade_report_data.get("trade_story_input"), dict) else {}
    canonical_trade = _build_canonical_trade_brief_input(trade_report)
    canonical_monitor_snapshot, execution, feature_coverage, feature_snapshot, live_exit_reason, live_monitor_reason, monitor_summary, monitor_trace, path_label, phase, quote_metrics, scanner_summary, scanner_trace, score_breakdown, selected_candidate, selected_symbol, source_scores, strategist_raw_input, strategist_summary, strategist_trace, supervisor_reason, thresholds, top_candidates, verdict = brief_facts_canonical_monitor_snapshot_execution(canonical_trade=canonical_trade, strategist=strategist, scanner=scanner, monitor=monitor, supervisor=supervisor, executor=executor, detail=detail, facade=_r3_sys.modules[__name__])
    selected_rank = _safe_int(
        canonical_trade.get("selected_rank"),
        next((int(row.get("rank") or 0) for row in top_candidates if str(row.get("symbol") or "") == selected_symbol), 0),
    )
    confidence, execution_action, exit_reason, final_action, monitor_reason, report_lifecycle_status, selected_why, selection_reasons, shared_facts, universe_size = brief_facts_confidence_execution_action(canonical_trade=canonical_trade, scanner_summary=scanner_summary, top_candidates=top_candidates, scanner_trace=scanner_trace, execution=execution, live_monitor_reason=live_monitor_reason, live_exit_reason=live_exit_reason, selected_candidate=selected_candidate, facade=_r3_sys.modules[__name__])
    for reason in list(canonical_trade.get("why_selected") or [])[:4]:
        cleaned = _clean_brief_text(reason)
        if cleaned and cleaned not in selection_reasons:
            selection_reasons.append(cleaned)
    if selected_why and selected_why not in selection_reasons:
        selection_reasons.append(selected_why)
    for bullet in list(canonical_trade.get("selection_bullets") or [])[:4]:
        text = str(bullet or "").strip()
        if text.lower().startswith("chart / feature coverage:"):
            continue
        if text and text not in selection_reasons:
            selection_reasons.append(text)
    if feature_coverage.get("total"):
        selection_reasons.append(
            f"chart feature coverage {feature_coverage.get('present')}/{feature_coverage.get('total')} ({feature_coverage.get('quality') or '-'})"
        )
    if quote_metrics.get("quote_trading_value") is not None:
        selection_reasons.append("acceptable turnover and tradability")
    if strategist_summary.get("playbook"):
        selection_reasons.append(f"aligned with playbook {strategist_summary.get('playbook')}")

    comparison_reasons: List[str] = []
    canonical_runner_ups_lost = [dict(row) for row in list(canonical_trade.get("runner_ups_lost") or []) if isinstance(row, dict)]
    if canonical_runner_ups_lost:
        for row in canonical_runner_ups_lost[:3]:
            symbol = str(row.get("symbol") or "").strip()
            summary = _clean_brief_text(row.get("summary") or "; ".join(list(row.get("why_lost") or [])))
            if symbol and summary:
                comparison_reasons.append(f"{symbol} was weaker: {summary}")
    elif len(top_candidates) >= 2:
        for row in top_candidates[1:3]:
            reason = _clean_brief_text(row.get("reason"))
            if reason:
                comparison_reasons.append(f"{row.get('symbol')} was weaker: {reason}")
        if not comparison_reasons:
            comparison_reasons.append("other candidates had lower composite rank or weaker feature coverage")
    else:
        comparison_reasons.append("only one ranked candidate was persisted for this run")

    candidate_hints, defensive_mode, detected_themes, global_score, macro_moves, market_headlines, news_summary, news_targets, playbook, symbol_headlines, theme_match, vix_level = brief_market_candidate_hints_defensive_mode(strategist_raw_input=strategist_raw_input, canonical_trade=canonical_trade, strategist_summary=strategist_summary, strategist=strategist, selected_symbol=selected_symbol, strategist_trace=strategist_trace, selected_candidate=selected_candidate, facade=_r3_sys.modules[__name__])
    if not theme_match and selected_why and detected_themes:
        lowered = selected_why.lower()
        for theme in detected_themes:
            if str(theme).lower() in lowered:
                theme_match = theme
                break
    anomaly_note, anomaly_status, chart_note, chart_status, liquidity_note, liquidity_status, priority_alignment, ranking_basis, risk_note, risk_status, sector_note, sector_status, sentiment_gate_note, sentiment_gate_status, spread_note, spread_status, theme_priority, turnover_note, turnover_status = brief_market_anomaly_note_anomaly_status(detected_themes=detected_themes, theme_match=theme_match, selected_symbol=selected_symbol, feature_snapshot=feature_snapshot, global_score=global_score, quote_metrics=quote_metrics, feature_coverage=feature_coverage, verdict=verdict, selected_candidate=selected_candidate, facade=_r3_sys.modules[__name__])
    for key in list(score_breakdown.keys())[:6]:
        ranking_basis.append(_friendly_feature_name(key))
    if not ranking_basis:
        for key in list(source_scores.keys())[:6]:
            ranking_basis.append(str(key).replace("_", " "))
    if not ranking_basis:
        ranking_basis = ["trading value", "volume", "sector strength", "chart feature coverage"]

    component_scores: List[str] = []
    for key, value in list(score_breakdown.items())[:6]:
        component_scores.append(f"{_friendly_feature_name(str(key))}: {_format_float(value, 3)}")
    if not component_scores:
        for key, value in list(source_scores.items())[:6]:
            component_scores.append(f"{str(key).replace('_', ' ')}: {_format_float(value, 3)}")
    active_exit_axis, avg_price_monitor, canonical_current_price, canonical_holding_time, canonical_posture, chart_interpretation, current_drawdown_raw, current_price, effective_stop_reason, effective_stop_text, holding_time, missing_feature_names, peak_drawdown_raw, peak_price, positive_factors, present_feature_names, scanner_selection_trace, stop_loss, stop_loss_text, take_profit, take_profit_text, vwap_distance_raw, watch_axes, weak_factors = brief_market_active_exit_axis_avg_price_monitor(trade_story_input=trade_story_input, canonical_trade=canonical_trade, selected_why=selected_why, quote_metrics=quote_metrics, chart_status=chart_status, sector_status=sector_status, feature_coverage=feature_coverage, feature_snapshot=feature_snapshot, sentiment_gate_status=sentiment_gate_status, thresholds=thresholds, monitor_trace=monitor_trace, monitor_summary=monitor_summary, live_exit_reason=live_exit_reason, live_monitor_reason=live_monitor_reason, exit_reason=exit_reason, monitor_reason=monitor_reason, canonical_monitor_snapshot=canonical_monitor_snapshot, shared_facts=shared_facts, facade=_r3_sys.modules[__name__])
    canonical_active_exit_axis, canonical_average_price, canonical_current_drawdown, canonical_effective_stop, canonical_effective_stop_reason, canonical_exit_triggers, canonical_feature_source, canonical_hold_reasons, canonical_peak_drawdown, canonical_peak_price, canonical_price_source, canonical_price_source_policy, canonical_stop_loss, canonical_take_profit, canonical_vwap_distance, canonical_watch_axes, entry_evaluated, entry_guard_reason, entry_metrics, entry_pattern, entry_reason_code, entry_signal_chain, entry_triggered, hold_reasons = brief_monitor_canonical_active_exit_axis_canonical_ave(canonical_monitor_snapshot=canonical_monitor_snapshot, monitor_summary=monitor_summary, monitor_trace=monitor_trace, facade=_r3_sys.modules[__name__])
    if final_action == "HOLD":
        hold_reasons.append("no explicit exit trigger was hit yet")
        hold_reasons.append(f"monitor reason: {monitor_reason or '-'} / exit reason: {exit_reason or '-'}")
    elif final_action == "WAIT":
        hold_reasons.append("entry is waiting because no active position or execution signal is confirmed")
        hold_reasons.append(f"monitor reason: {monitor_reason or '-'}")
    elif final_action == "BUY":
        hold_reasons.append("scanner selection passed gating and execution was approved")
    elif final_action == "SELL":
        hold_reasons.append("monitor/supervisor flow reached sell execution condition")
    if chart_status in {"PASS", "PARTIAL"}:
        hold_reasons.append(f"chart coverage state: {feature_coverage.get('quality') or '-'}")

    exit_triggers = [
        "stop-loss breach",
        "take-profit hit",
        "monitor quality deterioration",
    ]
    if stop_loss_text != "-" or take_profit_text != "-":
        exit_triggers = [
            f"stop-loss trigger ({stop_loss_text})" if stop_loss_text != "-" else "stop-loss trigger",
            f"take-profit trigger ({take_profit_text})" if take_profit_text != "-" else "take-profit trigger",
            "risk gate failure or abnormal volatility expansion",
        ]

    prefer_runtime_reporter = _prefer_runtime_reporter_state(reporter)
    decision_reason, execution_quality, focus_symbol, key_finding, monitor_consistency, report_available, report_lifecycle_status, report_lifecycle_summary, report_link, report_mode, report_model, report_next_step, report_reason, report_status, report_story_type, report_summary, report_trade_id, reporter_reason, reporter_status, run_grade, strategy_alignment, thesis_invalidation, trade_quality, watch_next = brief_monitor_decision_reason_execution_quality(prefer_runtime_reporter=prefer_runtime_reporter, reporter=reporter, canonical_trade=canonical_trade, execution_action=execution_action, monitor_reason=monitor_reason, exit_reason=exit_reason, final_action=final_action, selected_rank=selected_rank, universe_size=universe_size, feature_coverage=feature_coverage, selected_symbol=selected_symbol, take_profit_text=take_profit_text, stop_loss_text=stop_loss_text, vix_level=vix_level, detected_themes=detected_themes, trade_report=trade_report, scanner_summary=scanner_summary, facade=_r3_sys.modules[__name__])
    execution_status_label, next_expected_step, selection_reason_text, stop_policy_summary, strategist_evidence_summary, supervisor_allowed = brief_monitor_execution_status_label_next_expected_ste(verdict=verdict, execution=execution, canonical_trade=canonical_trade, thresholds=thresholds, stop_loss=stop_loss, stop_loss_text=stop_loss_text, canonical_monitor_snapshot=canonical_monitor_snapshot, effective_stop_text=effective_stop_text, take_profit=take_profit, take_profit_text=take_profit_text, canonical_effective_stop_reason=canonical_effective_stop_reason, effective_stop_reason=effective_stop_reason, watch_next=watch_next, final_action=final_action, selected_symbol=selected_symbol, active_exit_axis=active_exit_axis, playbook=playbook, global_score=global_score, vix_level=vix_level, strategist_summary=strategist_summary, selection_reasons=selection_reasons, selected_why=selected_why, facade=_r3_sys.modules[__name__])
    score_driver_preview = list(component_scores[:4]) or [
        f"{key}={value}"
        for key, value in list((scanner_selection_trace.get("selected_symbol_score_drivers") or {}).items())[:4]
    ]
    top_monitor_blocker = (
        entry_guard_reason
        or monitor_reason
        or live_monitor_reason
        or live_exit_reason
        or "No explicit blocker or trigger was persisted."
    )
    monitor_guard_summary = top_monitor_blocker if final_action == "WAIT" else (live_exit_reason or monitor_reason or top_monitor_blocker)
    guard_status = "approved" if supervisor_allowed else "blocked"
    execution_status_summary = execution_status_label or str(canonical_trade.get("execution_summary") or "not captured")
    operator_takeaway_items = watch_next[:3] or weak_factors[:3] or thesis_invalidation[:3]

    macro_summary: List[str] = []
    if macro_moves.get("dxy_pct") is not None:
        macro_summary.append(f"DXY change {_format_percent(macro_moves.get('dxy_pct'), 2)}")
    if macro_moves.get("tnx_delta") is not None:
        macro_summary.append(f"US10Y delta {_format_float(macro_moves.get('tnx_delta'), 3)}")
    for bullet in list(canonical_trade.get("market_context_bullets") or [])[:4]:
        if bullet not in macro_summary:
            macro_summary.append(bullet)

    filter_rows = [dict(row) for row in list(canonical_trade.get("filter_rows") or []) if isinstance(row, dict)]
    if filter_rows:
        for row in filter_rows:
            name = str(row.get("name") or "").strip().lower()
            if name == "chart completeness filter":
                row["status"] = chart_status
                row["note"] = chart_note
                break
    if filter_rows:
        filters_and_gates = filter_rows[:8]
    else:
        filters_and_gates = [
            {"name": "Liquidity filter", "status": liquidity_status, "note": liquidity_note},
            {"name": "Turnover filter", "status": turnover_status, "note": turnover_note},
            {"name": "Sector strength filter", "status": sector_status, "note": sector_note},
            {"name": "Chart completeness filter", "status": chart_status, "note": chart_note},
            {"name": "Sentiment gate", "status": sentiment_gate_status, "note": sentiment_gate_note},
            {"name": "Risk gate", "status": risk_status, "note": risk_note},
            {"name": "Price anomaly filter", "status": anomaly_status, "note": anomaly_note},
            {"name": "Spread/slippage filter", "status": spread_status, "note": spread_note},
        ]

    hold_reason_rows = list(canonical_trade.get("monitor_bullets") or [])
    if hold_reason_rows:
        hold_reasons = hold_reason_rows[:4]

    return {
        "executive_decision": {
            "final_action": final_action,
            "symbol": selected_symbol or "-",
            "reason": decision_reason,
            "confidence": confidence,
            "selected_rank": selected_rank or None,
            "universe_size": universe_size or None,
        },
        "current_snapshot": {
            "summary": decision_reason,
            "phase": phase,
            "path": path_label,
            "final_action": final_action,
            "selected_symbol": focus_symbol,
            "current_focus": focus_symbol,
            "posture": canonical_posture or final_action or "-",
            "monitor_reason": monitor_reason or live_monitor_reason or "-",
            "guard_status": guard_status,
            "execution_status": execution_status_summary,
            "next_expected_step": next_expected_step or "-",
        },
        "strategist_evidence": {
            "summary": strategist_evidence_summary,
            "market_regime": str(canonical_trade.get("market_regime") or strategist_summary.get("market_regime") or "-"),
            "playbook": playbook or "-",
            "global_sentiment": _format_float(global_score, 2) if global_score is not None else "-",
            "vix": _format_float(vix_level, 2) if vix_level is not None else "-",
            "candidate_hints": _clean_brief_list(candidate_hints, limit=6),
            "news_targets": _clean_brief_list(news_targets, limit=6),
            "market_headlines": _clean_str_list(market_headlines, limit=3, max_len=160),
            "symbol_headlines": _clean_str_list(symbol_headlines, limit=3, max_len=160),
        },
        "scanner_focus": {
            "summary": selection_reason_text,
            "selected_symbol": focus_symbol,
            "selected_rank": selected_rank or None,
            "universe_size": universe_size or None,
            "top_candidates": list(canonical_trade.get("top_candidates") or top_candidates[:3])[:3],
            "selection_reason": selection_reason_text,
            "score_drivers": score_driver_preview[:4],
        },
        "monitor_guard_snapshot": {
            "summary": monitor_guard_summary,
            "monitor_reason": monitor_reason or live_monitor_reason or "-",
            "entry_reason": entry_reason_code or "-",
            "entry_guard_reason": entry_guard_reason or "-",
            "active_exit_axis": active_exit_axis or "-",
            "stop_policy_summary": stop_policy_summary[:4],
            "guard_status": guard_status,
            "guard_reason": supervisor_reason or "-",
            "execution_status": execution_status_summary,
        },
        "next_step": {
            "summary": next_expected_step or "-",
            "watch_next": watch_next[:4],
            "operator_takeaways": operator_takeaway_items[:4],
        },
        "why_symbol_chosen": {
            "selected": bool(selected_symbol),
            "universe_size": universe_size or None,
            "selected_rank": selected_rank or None,
            "selection_reasons": selection_reasons or ["selection rationale was not explicitly persisted"],
            "comparison_reasons": comparison_reasons,
            "top_candidates": list(canonical_trade.get("top_candidates") or top_candidates[:3])[:3],
        },
        "entry_timing": {
            "decision": "BUY" if entry_triggered or final_action == "BUY" else "WAIT",
            "evaluated": entry_evaluated,
            "triggered": entry_triggered,
            "reason_code": entry_reason_code,
            "reason_text": str(canonical_trade.get("entry_reason") or ""),
            "pattern": entry_pattern,
            "signal_chain": entry_signal_chain[:5],
            "metrics": dict(entry_metrics or {}),
            "guard_reason": entry_guard_reason,
        },
        "market_context": {
            "market_regime": str(canonical_trade.get("market_regime") or strategist_summary.get("market_regime") or strategist_trace.get("market_regime") or "-"),
            "global_sentiment": _format_float(global_score, 2) if global_score is not None else "-",
            "vix": _format_float(vix_level, 2) if vix_level is not None else "-",
            "macro_summary": macro_summary,
            "news_summary": news_summary,
            "news_targets": _clean_brief_list(news_targets, limit=6),
            "defensive_mode": "enabled" if defensive_mode else "disabled",
        },
        "theme_detection": {
            "detected_themes": detected_themes,
            "symbol_theme_match": theme_match or "not explicitly tagged",
            "priority_alignment": priority_alignment,
            "theme_priority_bucket": theme_priority,
        },
        "filters_and_gates": filters_and_gates,
        "scanner_ranking_explanation": {
            "ranking_basis": ranking_basis,
            "component_scores": component_scores,
            "tie_break_rule": str(canonical_trade.get("tie_break_rule") or scanner_trace.get("tie_break_rule") or "higher composite score, then stronger feature coverage"),
            "positive_factors": positive_factors[:5],
            "weak_factors": weak_factors[:4],
        },
        "chart_feature_coverage": {
            "present": _safe_int(feature_coverage.get("present"), 0),
            "total": _safe_int(feature_coverage.get("total"), 0),
            "quality": str(feature_coverage.get("quality") or "missing"),
            "confirmed_features": present_feature_names,
            "missing_features": missing_feature_names,
            "interpretation": chart_interpretation,
        },
        "position_monitor_reasoning": {
            "posture": canonical_posture or final_action,
            "holding_time": canonical_holding_time or holding_time,
            "stop_loss": canonical_stop_loss or stop_loss_text,
            "effective_stop": canonical_effective_stop or effective_stop_text,
            "effective_stop_reason": (
                canonical_effective_stop_reason
                or (_friendly_exit_reason(effective_stop_reason or "stop_loss") if effective_stop_text != "-" else "-")
            ),
            "take_profit": canonical_take_profit or take_profit_text,
            "current_price": canonical_current_price or (_format_float(current_price, 2) if current_price not in (None, "") else "-"),
            "average_price": canonical_average_price or (_format_float(avg_price_monitor, 2) if avg_price_monitor not in (None, "") else "-"),
            "peak_price": canonical_peak_price or (_format_float(peak_price, 2) if peak_price not in (None, "") else "-"),
            "current_drawdown": canonical_current_drawdown or (_format_percent(current_drawdown_raw, 2) if current_drawdown_raw not in (None, "") else "-"),
            "peak_drawdown": canonical_peak_drawdown or (_format_percent(peak_drawdown_raw, 2) if peak_drawdown_raw not in (None, "") else "-"),
            "vwap_distance": canonical_vwap_distance or (_format_percent(vwap_distance_raw, 2) if vwap_distance_raw not in (None, "") else "-"),
            "price_source": canonical_price_source or str(monitor_trace.get("price_source") or monitor_summary.get("price_source") or "-"),
            "feature_source": canonical_feature_source or str(monitor_trace.get("feature_source") or monitor_summary.get("feature_source") or "-"),
            "price_source_policy": canonical_price_source_policy or str(monitor_trace.get("price_source_policy") or monitor_summary.get("price_source_policy") or ""),
            "active_exit_axis": (_friendly_exit_reason(canonical_active_exit_axis) if canonical_active_exit_axis else "") or active_exit_axis,
            "watch_axes": canonical_watch_axes or watch_axes,
            "hold_reasons": canonical_hold_reasons or hold_reasons[:4],
            "exit_triggers": canonical_exit_triggers or exit_triggers[:3],
        },
        "exit_plan": {
            "current_action": final_action,
            "summary": str(canonical_trade.get("exit_reason") or exit_reason or monitor_reason or ""),
            "effective_stop": canonical_effective_stop or effective_stop_text,
            "effective_stop_reason": (
                canonical_effective_stop_reason
                or (_friendly_exit_reason(effective_stop_reason or "stop_loss") if effective_stop_text != "-" else "-")
            ),
            "take_profit": canonical_take_profit or take_profit_text,
            "active_exit_axis": (_friendly_exit_reason(canonical_active_exit_axis) if canonical_active_exit_axis else "") or active_exit_axis,
            "exit_triggers": canonical_exit_triggers or exit_triggers[:3],
            "watch_axes": canonical_watch_axes or watch_axes,
        },
        "reporter_evaluation": {
            "status": reporter_status,
            "reason": reporter_reason,
            "strategy_alignment": strategy_alignment,
            "execution_quality": execution_quality,
            "monitor_consistency": monitor_consistency,
            "run_grade": run_grade or "-",
            "trade_quality": trade_quality,
            "key_finding": key_finding,
        },
        "ai_trade_report": {
            "status": report_status,
            "status_label": _report_status_label(report_status),
            "status_badge_class": _report_status_badge_class(report_status),
            "reason": report_reason or "AI report diagnostics were not captured.",
            "next_step": report_next_step or "Continue with Operator Brief while report diagnostics are resolved.",
            "model": report_model or "-",
            "available": report_available,
            "trade_id": report_trade_id,
            "lifecycle_status": report_lifecycle_status or "-",
            "lifecycle_summary": report_lifecycle_summary or "-",
            "story_type": report_story_type,
            "execution_mode_label": report_mode,
            "summary": report_summary or "No per-trade AI report is linked to this run yet.",
            "link": report_link,
        },
        "operator_conclusion": {
            "current_action": final_action,
            "watch_next": watch_next[:4],
            "thesis_invalidation": thesis_invalidation,
        },
        "risk_alerts": {
            "defensive_mode": defensive_mode,
            "weak_factors": weak_factors[:4],
            "thesis_invalidation": thesis_invalidation[:3],
        },
    }


def _attach_operator_brief_sections(brief: Dict[str, Any], detail: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(brief or {})
    out["sections"] = _build_operator_brief_sections(detail)
    return _normalize_operator_brief_payload(out, detail)


def _normalize_operator_brief_payload(
    brief: Dict[str, Any],
    detail: Dict[str, Any],
    *,
    llm_response_artifact: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return _normalize_operator_brief_payload_r3_impl(brief, detail,
        llm_response_artifact=llm_response_artifact, facade=_r3_sys.modules[__name__])





def _fallback_operator_brief(detail: Dict[str, Any]) -> Dict[str, Any]:
    return _fallback_operator_brief_r3_impl(detail, facade=_r3_sys.modules[__name__])

def _failure_operator_brief(
    detail: Dict[str, Any],
    *,
    status: str,
    model: str,
    reason: str,
    failure_status: str = "",
) -> Dict[str, Any]:
    return _failure_operator_brief_r3_impl(detail, status=status, model=model, reason=reason,
        failure_status=failure_status, facade=_r3_sys.modules[__name__])

def _build_operator_brief_input(detail: Dict[str, Any]) -> Dict[str, Any]:
    strategist = detail.get("strategist") if isinstance(detail.get("strategist"), dict) else {}
    scanner = detail.get("scanner") if isinstance(detail.get("scanner"), dict) else {}
    monitor = detail.get("monitor") if isinstance(detail.get("monitor"), dict) else {}
    commander = detail.get("commander") if isinstance(detail.get("commander"), dict) else {}
    commander_artifact = commander.get("artifact") if isinstance(commander.get("artifact"), dict) else {}
    commander_decision = commander_artifact.get("commander_decision") if isinstance(commander_artifact.get("commander_decision"), dict) else {}
    reporter = detail.get("reporter") if isinstance(detail.get("reporter"), dict) else {}
    trade_report = detail.get("trade_report") if isinstance(detail.get("trade_report"), dict) else {}
    trade_report_data = trade_report.get("report_data") if isinstance(trade_report.get("report_data"), dict) else {}
    trade_story_input = trade_report_data.get("trade_story_input") if isinstance(trade_report_data.get("trade_story_input"), dict) else {}
    canonical_trade = _build_canonical_trade_brief_input(trade_report)
    prefer_runtime_reporter = _prefer_runtime_reporter_state(reporter)
    strategist_summary = strategist.get("summary") if isinstance(strategist.get("summary"), dict) else {}
    strategist_artifact = strategist.get("artifact") if isinstance(strategist.get("artifact"), dict) else {}
    strategist_evidence = strategist.get("evidence") if isinstance(strategist.get("evidence"), dict) else {}
    raw_input = strategist_evidence.get("raw_input") if isinstance(strategist_evidence.get("raw_input"), dict) else {}
    scanner_trace = scanner.get("decision_trace") if isinstance(scanner.get("decision_trace"), dict) else {}
    scanner_artifact = scanner.get("artifact") if isinstance(scanner.get("artifact"), dict) else {}
    selected = scanner_trace.get("selected_candidate") if isinstance(scanner_trace.get("selected_candidate"), dict) else {}
    score_breakdown = selected.get("score_breakdown") if isinstance(selected.get("score_breakdown"), dict) else {}
    component_snapshot = selected.get("component_snapshot") if isinstance(selected.get("component_snapshot"), dict) else {}
    feature_snapshot = selected.get("feature_snapshot") if isinstance(selected.get("feature_snapshot"), dict) else {}
    feature_coverage = _normalized_feature_coverage(
        scanner.get("feature_coverage") if isinstance(scanner.get("feature_coverage"), dict) else {},
        feature_snapshot,
    )
    chart_status, chart_note = _chart_filter_status_and_note(feature_coverage)
    canonical_filter_bullets = list(canonical_trade.get("filter_bullets") or [])[:8]
    canonical_selection_bullets = list(canonical_trade.get("selection_bullets") or [])[:6]
    if _safe_int(feature_coverage.get("total"), 0) > 0:
        updated_bullets: List[str] = []
        replaced_chart_bullet = False
        for bullet in canonical_filter_bullets:
            text = str(bullet or "").strip()
            if text.lower().startswith("chart completeness filter:"):
                updated_bullets.append(f"chart completeness filter: {chart_status} - {chart_note}")
                replaced_chart_bullet = True
            else:
                updated_bullets.append(text)
        if not replaced_chart_bullet:
            updated_bullets.append(f"chart completeness filter: {chart_status} - {chart_note}")
        canonical_filter_bullets = updated_bullets[:8]
        canonical_filters_summary = (
            f"Scanner and guard checks used normalized chart coverage with {feature_coverage.get('present')}/{feature_coverage.get('total')} captured features."
        )
        updated_selection_bullets: List[str] = []
        replaced_selection_chart_bullet = False
        for bullet in canonical_selection_bullets:
            text = str(bullet or "").strip()
            if text.lower().startswith("chart / feature coverage:"):
                updated_selection_bullets.append(
                    f"Chart / feature coverage: {feature_coverage.get('present')}/{feature_coverage.get('total')}"
                )
                replaced_selection_chart_bullet = True
            else:
                updated_selection_bullets.append(text)
        if not replaced_selection_chart_bullet:
            updated_selection_bullets.append(
                f"Chart / feature coverage: {feature_coverage.get('present')}/{feature_coverage.get('total')}"
            )
        canonical_selection_bullets = updated_selection_bullets[:6]
    else:
        canonical_filters_summary = canonical_trade.get("filters_summary")
    candidate_hints, market_headlines, monitor_artifact, monitor_entry_metrics, monitor_entry_thresholds, monitor_policy_ref, monitor_summary, monitor_thresholds_used, monitor_timing_assessment, monitor_trace, scanner_selection_trace, selected_symbol, symbol_headlines = brief_input_candidate_hints_market_headlines(monitor=monitor, scanner_trace=scanner_trace, selected=selected, canonical_trade=canonical_trade, strategist_artifact=strategist_artifact, raw_input=raw_input, strategist_summary=strategist_summary, trade_story_input=trade_story_input, facade=_r3_sys.modules[__name__])
    if not scanner_selection_trace:
        scanner_selection_trace = brief_input_scanner_selection_trace(scanner_artifact=scanner_artifact, selected_symbol=selected_symbol, score_breakdown=score_breakdown, scanner_trace=scanner_trace, selected=selected, canonical_trade=canonical_trade, facade=_r3_sys.modules[__name__])[0]
    canonical_monitor_snapshot_stop_policy_trace, canonical_monitor_stop_policy_trace, monitor_stop_policy_trace = brief_input_canonical_monitor_snapshot_stop_policy_t(monitor_artifact=monitor_artifact, monitor_summary=monitor_summary, monitor_trace=monitor_trace, canonical_trade=canonical_trade, facade=_r3_sys.modules[__name__])
    if not any(value not in (None, "", []) for value in monitor_stop_policy_trace.values()):
        monitor_stop_policy_trace = dict(canonical_monitor_stop_policy_trace or {})
    elif canonical_monitor_stop_policy_trace:
        for key, value in canonical_monitor_stop_policy_trace.items():
            if monitor_stop_policy_trace.get(key) in (None, "", []):
                monitor_stop_policy_trace[key] = value
    if canonical_monitor_snapshot_stop_policy_trace:
        for key, value in canonical_monitor_snapshot_stop_policy_trace.items():
            if monitor_stop_policy_trace.get(key) in (None, "", []):
                monitor_stop_policy_trace[key] = value
    commander_applied_policy, monitor_applied_policy, monitor_effective_policy, monitor_received_policy = brief_input_commander_applied_policy_monitor_applied(commander_artifact=commander_artifact, commander_decision=commander_decision, monitor_trace=monitor_trace, monitor_policy_ref=monitor_policy_ref, facade=_r3_sys.modules[__name__])
    return {
        "run_id": detail.get("run_id"),
        "commander": {
            "mode": commander.get("mode"),
            "phase": commander.get("phase"),
            "path": commander.get("path"),
            "status": commander.get("status"),
            "command_intent": commander_decision.get("command_intent"),
            "strategist_invocation": commander_decision.get("strategist_invocation"),
            "llm_policy": commander_decision.get("llm_policy") or commander_decision.get("llm_invocation_policy"),
            "selected_route": commander_artifact.get("selected_route"),
            "route_reason_text": commander_artifact.get("route_reason_text"),
            "strategist_cache_used": commander_artifact.get("strategist_cache_used"),
            "strategist_called": commander_artifact.get("strategist_called"),
            "cooldown_applied": commander_artifact.get("cooldown_applied"),
            "applied_policy": commander_applied_policy,
            "policy_source": commander_artifact.get("policy_source") or commander_decision.get("policy_source"),
            "policy_validation_status": commander_artifact.get("policy_validation_status")
            or commander_decision.get("policy_validation_status"),
            "policy_fallback_used": commander_artifact.get("policy_fallback_used")
            if commander_artifact.get("policy_fallback_used") is not None
            else commander_decision.get("policy_fallback_used"),
            "policy_fallback_reason": commander_artifact.get("policy_fallback_reason")
            or commander_decision.get("policy_fallback_reason"),
            "policy_partial_normalized": commander_artifact.get("policy_partial_normalized")
            if commander_artifact.get("policy_partial_normalized") is not None
            else commander_decision.get("policy_partial_normalized"),
            "policy_default_filled_fields": list(
                commander_artifact.get("policy_default_filled_fields")
                or commander_decision.get("policy_default_filled_fields")
                or []
            )[:12],
            "policy_validation_missing_fields": list(
                commander_artifact.get("policy_validation_missing_fields")
                or commander_decision.get("policy_validation_missing_fields")
                or []
            )[:12],
            "policy_validation_invalid_fields": list(
                commander_artifact.get("policy_validation_invalid_fields")
                or commander_decision.get("policy_validation_invalid_fields")
                or []
            )[:12],
            "override_reason": commander_artifact.get("override_reason") or commander_decision.get("override_reason"),
            "applied_policy_source_chain": list(
                commander_artifact.get("applied_policy_source_chain")
                or commander_decision.get("applied_policy_source_chain")
                or []
            )[:6],
        },
        "strategist": {
            "market_regime": strategist_summary.get("market_regime") or canonical_trade.get("market_regime"),
            "market_sentiment": strategist_summary.get("market_sentiment") or canonical_trade.get("market_sentiment"),
            "themes": list(strategist_summary.get("themes") or canonical_trade.get("themes") or [])[:5],
            "playbook": strategist_summary.get("playbook") or canonical_trade.get("playbook"),
            "scanner_bias": strategist_summary.get("scanner_bias"),
            "risk_tone": _strategist_risk_tone(strategist_summary)
            or _strategist_risk_tone(strategist_artifact)
            or _strategist_risk_tone(trade_story_input)
            or _strategist_risk_tone(canonical_trade),
            "monitor_guidance": _strategist_monitor_guidance(strategist_summary)
            or _strategist_monitor_guidance(strategist_artifact)
            or _strategist_monitor_guidance(trade_story_input)
            or _strategist_monitor_guidance(canonical_trade),
            "news_query_targets": list(strategist_summary.get("news_query_targets") or canonical_trade.get("news_query_targets") or [])[:8],
            "news_query_reasoning": strategist_summary.get("news_query_reasoning"),
            "global_sentiment_inputs": raw_input.get("global_sentiment_inputs") if isinstance(raw_input.get("global_sentiment_inputs"), dict) else {},
            "candidate_hints": [str(x or "") for x in candidate_hints if str(x or "").strip()],
            "market_headlines": [str(x or "") for x in market_headlines if str(x or "").strip()][:3],
            "symbol_headlines": [str(x or "") for x in symbol_headlines if str(x or "").strip()][:3],
            "market_news_titles": [str((x or {}).get("title") or "") for x in list(raw_input.get("collected_market_news") or [])[:4] if isinstance(x, dict)] or list(canonical_trade.get("market_news_titles") or [])[:4],
            "candidate_news_titles": [str((x or {}).get("title") or "") for x in list(raw_input.get("collected_candidate_news") or [])[:4] if isinstance(x, dict)] or list(canonical_trade.get("candidate_news_titles") or [])[:4],
            "llm_status": strategist_summary.get("llm_frame_status"),
            "llm_low_confidence": strategist_summary.get("llm_frame_low_confidence"),
            "canonical_summary": canonical_trade.get("market_context_summary"),
            "canonical_bullets": list(canonical_trade.get("market_context_bullets") or [])[:6],
        },
        "scanner": {
            "candidate_source": scanner.get("summary", {}).get("candidate_source") if isinstance(scanner.get("summary"), dict) else "",
            "candidate_pool_before_filter": (scanner.get("summary") or {}).get("candidate_pool_before_filter") if isinstance(scanner.get("summary"), dict) else None,
            "candidate_pool_after_filter": (scanner.get("summary") or {}).get("candidate_pool_after_filter") if isinstance(scanner.get("summary"), dict) else None,
            "top_ranked_symbols": list(canonical_trade.get("top_candidates") or [])[:5]
            or (
                list((scanner.get("summary") or {}).get("top_ranked_symbols") or [])[:5]
                if isinstance(scanner.get("summary"), dict)
                else []
            ),
            "source_mix": scanner_trace.get("kiwoom_pool_source_mix") if isinstance(scanner_trace.get("kiwoom_pool_source_mix"), dict) else {},
            "selected_symbol": scanner_trace.get("selected_symbol") or selected.get("symbol"),
            "selected_reason": canonical_trade.get("selection_basis")
            or canonical_trade.get("selection_summary")
            or selected.get("why"),
            "source_scores": selected.get("source_scores") if isinstance(selected.get("source_scores"), dict) else {},
            "score_total": selected.get("score_total"),
            "confidence": selected.get("confidence"),
            "feature_coverage": feature_coverage,
            "quote_metrics": scanner.get("quote_metrics") if isinstance(scanner.get("quote_metrics"), dict) else {},
            "score_breakdown": score_breakdown,
            "component_snapshot": component_snapshot,
            "feature_snapshot": feature_snapshot,
            "why_selected": list(canonical_trade.get("why_selected") or [])[:4],
            "selection_trace": dict(scanner_selection_trace or {}),
            "selected_symbol_score_drivers": dict(scanner_selection_trace.get("selected_symbol_score_drivers") or {}),
            "tie_break_rule": canonical_trade.get("tie_break_rule"),
            "runner_ups": list(canonical_trade.get("runner_ups") or [])[:3],
            "runner_ups_lost": list(canonical_trade.get("runner_ups_lost") or [])[:3],
            "playbook": scanner_trace.get("playbook") or canonical_trade.get("playbook"),
            "policy_source": scanner_trace.get("policy_source") or canonical_trade.get("policy_source"),
            "applied_policy_present": (
                scanner_trace.get("applied_policy_present")
                if scanner_trace.get("applied_policy_present") is not None
                else canonical_trade.get("applied_policy_present")
            ),
            "monitor_entry_policy_summary": (
                scanner_trace.get("monitor_entry_policy_summary")
                if isinstance(scanner_trace.get("monitor_entry_policy_summary"), dict)
                else (
                    canonical_trade.get("monitor_entry_policy_summary")
                    if isinstance(canonical_trade.get("monitor_entry_policy_summary"), dict)
                    else {}
                )
            ),
            "scanner_bias_applied": scanner_trace.get("scanner_bias_applied"),
            "scanner_bias_summary": scanner_trace.get("scanner_bias_summary") if isinstance(scanner_trace.get("scanner_bias_summary"), dict) else {},
            "candidate_bias_adjustments": list(scanner_trace.get("candidate_bias_adjustments") or [])[:5],
            "selection_reason_with_bias": scanner_trace.get("selection_reason_with_bias") or selected.get("why"),
            "canonical_bullets": canonical_selection_bullets,
            "canonical_filters_summary": canonical_filters_summary,
            "canonical_filter_bullets": canonical_filter_bullets,
        },
        "monitor": {
            "monitor_reason": monitor_summary.get("monitor_reason") or monitor_trace.get("monitor_reason") or canonical_trade.get("monitor_summary"),
            "exit_reason": monitor_summary.get("exit_reason") or monitor_trace.get("exit_reason") or canonical_trade.get("exit_reason"),
            "position_age_seconds": monitor_summary.get("position_age_seconds"),
            "entry_evaluated": monitor_summary.get("entry_evaluated"),
            "entry_triggered": monitor_summary.get("entry_triggered"),
            "entry_reason": monitor_summary.get("entry_reason") or monitor_trace.get("entry_reason"),
            "entry_pattern": monitor_summary.get("entry_pattern") or monitor_trace.get("entry_pattern"),
            "entry_guard_reason": monitor_summary.get("entry_guard_reason") or monitor_trace.get("entry_guard_reason"),
            "entry_intent_submitted": monitor_summary.get("entry_intent_submitted"),
            "entry_metrics": monitor_summary.get("entry_metrics") if isinstance(monitor_summary.get("entry_metrics"), dict) else {},
            "entry_thresholds": monitor_summary.get("entry_thresholds") if isinstance(monitor_summary.get("entry_thresholds"), dict) else {},
            "thresholds": monitor_trace.get("thresholds") if isinstance(monitor_trace.get("thresholds"), dict) else {},
            "entry_check_summary": monitor_trace.get("entry_check_summary"),
            "entry_blockers": list(monitor_trace.get("entry_blockers") or [])[:8],
            "policy_ref": monitor_policy_ref,
            "timing_assessment": monitor_timing_assessment,
            "thresholds_guards_used": monitor_thresholds_used,
            "threshold_shortfalls": _monitor_threshold_shortfall_notes(monitor_entry_metrics, monitor_entry_thresholds),
            "stop_policy_trace": dict(monitor_stop_policy_trace or {}),
            "received_policy": monitor_received_policy,
            "received_policy_source": monitor_trace.get("received_policy_source") or monitor_policy_ref.get("received_policy_source"),
            "effective_policy": monitor_effective_policy,
            "effective_policy_source": monitor_trace.get("effective_policy_source") or monitor_policy_ref.get("effective_policy_source"),
            "effective_policy_source_chain": list(
                monitor_trace.get("effective_policy_source_chain")
                or monitor_policy_ref.get("effective_policy_source_chain")
                or []
            )[:6],
            "policy_adjustments": monitor_trace.get("policy_adjustments")
            if isinstance(monitor_trace.get("policy_adjustments"), dict)
            else (monitor_policy_ref.get("policy_adjustments") if isinstance(monitor_policy_ref.get("policy_adjustments"), dict) else {}),
            "policy_adjustment_summary": monitor_trace.get("policy_adjustment_summary") or monitor_policy_ref.get("policy_adjustment_summary"),
            "policy_adjustment_reasoning": monitor_trace.get("policy_adjustment_reasoning") or monitor_policy_ref.get("policy_adjustment_reasoning"),
            "effective_policy_deltas": list(
                monitor_trace.get("effective_policy_deltas")
                or monitor_policy_ref.get("effective_policy_deltas")
                or []
            )[:8],
            "applied_policy": monitor_applied_policy,
            "policy_source": monitor_trace.get("policy_source") or monitor_policy_ref.get("policy_source"),
            "policy_validation_status": monitor_trace.get("policy_validation_status")
            or monitor_policy_ref.get("policy_validation_status"),
            "policy_fallback_used": monitor_trace.get("policy_fallback_used")
            if monitor_trace.get("policy_fallback_used") is not None
            else monitor_policy_ref.get("policy_fallback_used"),
            "policy_fallback_reason": monitor_trace.get("policy_fallback_reason")
            or monitor_policy_ref.get("policy_fallback_reason"),
            "policy_partial_normalized": monitor_trace.get("policy_partial_normalized")
            if monitor_trace.get("policy_partial_normalized") is not None
            else monitor_policy_ref.get("policy_partial_normalized"),
            "policy_default_filled_fields": list(
                monitor_trace.get("policy_default_filled_fields")
                or monitor_policy_ref.get("policy_default_filled_fields")
                or []
            )[:12],
            "policy_validation_missing_fields": list(
                monitor_trace.get("policy_validation_missing_fields")
                or monitor_policy_ref.get("policy_validation_missing_fields")
                or []
            )[:12],
            "policy_validation_invalid_fields": list(
                monitor_trace.get("policy_validation_invalid_fields")
                or monitor_policy_ref.get("policy_validation_invalid_fields")
                or []
            )[:12],
            "override_reason": monitor_trace.get("override_reason") or monitor_policy_ref.get("override_reason"),
            "applied_policy_source_chain": list(
                monitor_trace.get("applied_policy_source_chain")
                or monitor_policy_ref.get("applied_policy_source_chain")
                or []
            )[:6],
            "strategy_frame_adjustments": list(monitor_trace.get("strategy_frame_adjustments") or [])[:6],
            "exit_policy_guard_adjustments": list(monitor_trace.get("exit_policy_guard_adjustments") or [])[:6],
            "canonical_bullets": list(canonical_trade.get("monitor_bullets") or [])[:6],
            "canonical_snapshot": dict(canonical_trade.get("monitor_snapshot") or {}),
        },
        "supervisor": {
            **((((detail.get("supervisor") or {}).get("verdict") or {}) if isinstance(detail.get("supervisor"), dict) else {})),
            "canonical_summary": canonical_trade.get("guard_summary"),
        },
        "executor": {
            **((((detail.get("executor") or {}).get("execution") or {}) if isinstance(detail.get("executor"), dict) else {})),
            "canonical_summary": canonical_trade.get("execution_summary"),
            "canonical_bullets": list(canonical_trade.get("execution_bullets") or [])[:6],
        },
        "reporter": {
            "ai_summary": reporter.get("ai_summary") if prefer_runtime_reporter else (canonical_trade.get("reporter_summary") or reporter.get("ai_summary")),
            "ai_run_grade": reporter.get("ai_run_grade") if prefer_runtime_reporter else (canonical_trade.get("reporter_grade") or reporter.get("ai_run_grade")),
            "found": reporter.get("found"),
            "status": canonical_trade.get("reporter_status"),
            "reason": reporter.get("reason"),
        },
        "trade_report": {
            "report_available": trade_report.get("report_available"),
            "trade_id": trade_report.get("trade_id"),
            "lifecycle_status": trade_report.get("lifecycle_status"),
            "lifecycle_summary": trade_report.get("lifecycle_summary"),
            "story_type": trade_report.get("story_type_label") or trade_report.get("story_type"),
            "execution_mode_label": trade_report.get("execution_mode_label"),
            "summary": trade_report.get("report_summary"),
            "reporter_status_human": trade_report.get("reporter_status_human"),
        },
        "shared_facts": dict(canonical_trade.get("shared_facts") or {}),
        "canonical_trade": canonical_trade,
    }


def _compact_scalar_map(data: Any, *, limit: int = 8, max_len: int = 120) -> Dict[str, Any]:
    return _compact_scalar_map_r3_impl(data, limit=limit, max_len=max_len,
        facade=_r3_sys.modules[__name__])


def _monitor_threshold_shortfall_notes(entry_metrics: Any, entry_thresholds: Any) -> List[str]:
    return _monitor_threshold_shortfall_notes_r3_impl(entry_metrics, entry_thresholds,
        facade=_r3_sys.modules[__name__])


def _compact_ranked_symbols(rows: Any, *, limit: int = 3) -> List[Dict[str, Any]]:
    return _compact_ranked_symbols_r3_impl(rows, limit=limit, facade=_r3_sys.modules[__name__])


def _compact_monitor_thresholds(data: Any) -> Dict[str, Any]:
    return _compact_monitor_thresholds_r3_impl(data, facade=_r3_sys.modules[__name__])


def _compact_canonical_trade_for_brief(data: Any) -> Dict[str, Any]:
    return _compact_canonical_trade_for_brief_r3_impl(data, facade=_r3_sys.modules[__name__])


def _compact_operator_brief_input_for_llm(prepared_input: Dict[str, Any]) -> Dict[str, Any]:
    return _compact_operator_brief_input_for_llm_r3_impl(prepared_input,
        facade=_r3_sys.modules[__name__])


_BRIEF_INTERNAL_TEXT_MARKERS = (
    "canonical_trade.available",
    "reports/trades",
    "source of truth",
    "run-level",
    "1차 source of truth",
)


def _contains_internal_brief_marker(text: Any) -> bool:
    raw = str(text or "").strip().lower()
    if not raw:
        return False
    return any(marker in raw for marker in _BRIEF_INTERNAL_TEXT_MARKERS)


def _sanitize_operator_brief_text(text: Any) -> str:
    return _sanitize_operator_brief_text_r3_impl(text, facade=_r3_sys.modules[__name__])


def _operator_brief_label_ko(value: Any) -> str:
    return _operator_brief_label_ko_r3_impl(value, facade=_r3_sys.modules[__name__])


def _build_operator_brief_kr_facts(
    strategist: Dict[str, Any],
    scanner: Dict[str, Any],
    monitor: Dict[str, Any],
    trade_report: Dict[str, Any],
) -> Dict[str, Any]:
    return _build_operator_brief_kr_facts_r3_impl(strategist, scanner, monitor, trade_report,
        facade=_r3_sys.modules[__name__])


def _count_hangul_chars(text: Any) -> int:
    raw = str(text or "")
    return sum(1 for ch in raw if "\uac00" <= ch <= "\ud7a3")


def _contains_forbidden_brief_script(text: Any) -> bool:
    raw = str(text or "")
    # Disallow Japanese/Katakana/Hiragana and CJK ideographs for operator-facing Korean brief text.
    return bool(re.search(r"[\u3040-\u30ff\u4e00-\u9fff]", raw))


def _operator_brief_language_ok(candidate: Dict[str, Any]) -> bool:
    return _operator_brief_language_ok_r3_impl(candidate, facade=_r3_sys.modules[__name__])


def _prefer_richer_brief_text(primary: Any, fallback: Any, *, min_primary_len: int = 48) -> str:
    return _prefer_richer_brief_text_r3_impl(primary, fallback, min_primary_len=min_primary_len,
        facade=_r3_sys.modules[__name__])


def _should_replace_brief_monitor_summary(detail: Dict[str, Any], summary_text: str) -> bool:
    return _should_replace_brief_monitor_summary_r3_impl(detail, summary_text,
        facade=_r3_sys.modules[__name__])


def _sanitize_operator_brief_result(detail: Dict[str, Any], candidate: Dict[str, Any], fallback: Dict[str, Any]) -> Dict[str, Any]:
    return _sanitize_operator_brief_result_r3_impl(detail, candidate, fallback,
        facade=_r3_sys.modules[__name__])


def _build_operator_brief_messages(compact_input: Dict[str, Any]) -> List[Dict[str, str]]:
    return _build_operator_brief_messages_r3_impl(compact_input, facade=_r3_sys.modules[__name__])

def _build_operator_brief_repair_messages(raw_text: str) -> List[Dict[str, str]]:
    return _build_operator_brief_repair_messages_r3_impl(raw_text, facade=_r3_sys.modules[__name__])

def _build_operator_brief_line_messages(compact_input: Dict[str, Any]) -> List[Dict[str, str]]:
    return _build_operator_brief_line_messages_r3_impl(compact_input,
        facade=_r3_sys.modules[__name__])

def _operator_brief_force_regenerate_enabled() -> bool:
    raw = str(os.getenv("OPERATOR_UI_RUN_BRIEF_FORCE_REGENERATE", "") or "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def _load_operator_brief(detail: Dict[str, Any]) -> Dict[str, Any]:
    fallback = _fallback_operator_brief(detail)
    trade_report = detail.get("trade_report") if isinstance(detail.get("trade_report"), dict) else {}
    run_id = str(detail.get("run_id") or "").strip()
    trade_id = str(trade_report.get("trade_id") or trade_report.get("story_id") or "").strip()
    day_match = re.search(r"\d{4}-\d{2}-\d{2}", str(detail.get("started_at") or ""))
    day = day_match.group(0) if day_match else ""
    attempts: List[Dict[str, Any]] = []

    def finalize(result: Dict[str, Any]) -> Dict[str, Any]:
        out = _sanitize_operator_brief_result(detail, result, fallback)
        headline = str(out.get("headline") or "").strip()
        fallback_headline = str(fallback.get("headline") or "").strip()
        expected_date = ""
        headline_date = ""
        started_at = str(detail.get("started_at") or "").strip()
        started_match = re.search(r"\d{4}-\d{2}-\d{2}", started_at)
        headline_match = re.search(r"\d{4}-\d{2}-\d{2}", headline)
        if started_match:
            expected_date = started_match.group(0)
        if headline_match:
            headline_date = headline_match.group(0)
        if not headline:
            out["headline"] = fallback_headline
        elif expected_date and headline_date and headline_date != expected_date:
            out["headline"] = fallback_headline
        parsed_output = {
            "headline": str(out.get("headline") or ""),
            "commander_summary": str(out.get("commander_summary") or ""),
            "strategist_summary": str(out.get("strategist_summary") or ""),
            "scanner_summary": str(out.get("scanner_summary") or ""),
            "monitor_summary": str(out.get("monitor_summary") or ""),
            "supervisor_summary": str(out.get("supervisor_summary") or ""),
            "executor_summary": str(out.get("executor_summary") or ""),
            "reporter_summary": str(out.get("reporter_summary") or ""),
            "operator_takeaways": [str(x or "") for x in list(out.get("operator_takeaways") or []) if str(x or "").strip()],
            "executive_summary": str(out.get("executive_summary") or ""),
            "scanner_reason": str(out.get("scanner_reason") or ""),
            "entry_summary": str(out.get("entry_summary") or ""),
            "holding_summary": str(out.get("holding_summary") or ""),
            "exit_plan_summary": str(out.get("exit_plan_summary") or ""),
            "risk_summary": str(out.get("risk_summary") or ""),
            "next_checkpoints": [str(x or "") for x in list(out.get("next_checkpoints") or []) if str(x or "").strip()],
        }
        latency_ms = 0
        if attempts:
            latency_ms = sum(int(row.get("latency_ms") or 0) for row in attempts)
        out["llm_response_artifact"] = build_llm_response_artifact(
            component="brief",
            run_id=run_id,
            trade_id=trade_id,
            story_id=trade_id,
            day=day,
            status=str(out.get("status") or "fallback"),
            attempts=attempts,
            parsed_output=parsed_output,
            model_info={"provider": "OpenRouter", "model": str(out.get("model") or "")},
            latency_ms=latency_ms,
            meta={
                "reason": str(out.get("reason") or ""),
                "parse_mode": str(out.get("parse_mode") or ""),
                "required_keys_expected": list(out.get("required_keys_expected") or []),
                "required_keys_present": list(out.get("required_keys_present") or []),
                "required_keys_missing": list(out.get("required_keys_missing") or []),
                "completeness_score": float(out.get("completeness_score") or 0.0),
                "used_fallback_sections": list(out.get("used_fallback_sections") or []),
                "finish_reason": str(out.get("finish_reason") or ""),
                "error": str((out.get("failure") or {}).get("reason") or out.get("reason") or ""),
            },
        )
        return out

    router = LLMRouter.from_env()
    if router.client is None:
        return finalize(
            {
                **_failure_operator_brief(detail, status="fallback", model="", reason="llm_client_unavailable", failure_status="error"),
                "parse_mode": "none",
                "required_keys_expected": list(OPERATOR_BRIEF_REQUIRED_KEYS),
                "required_keys_present": [],
                "required_keys_missing": list(OPERATOR_BRIEF_REQUIRED_KEYS),
                "completeness_score": 0.0,
                "used_fallback_sections": list(OPERATOR_BRIEF_REQUIRED_KEYS),
            }
        )
    explicit_model = str(
        os.getenv("OPERATOR_UI_RUN_BRIEF_MODEL", "")
        or os.getenv("OPENROUTER_MODEL_OPERATOR_UI", "")
        or ""
    ).strip()
    if hasattr(router, "resolve"):
        route = router.resolve("operator_ui", policy={"model": explicit_model} if explicit_model else None)
        model = str(getattr(route, "model", "") or explicit_model or "").strip()
    else:
        model = _normalize_role_model_name(
            explicit_model
            or os.getenv("OPENROUTER_DEFAULT_MODEL", "")
            or ""
        )
    prepared_input = _build_operator_brief_input(detail)
    compact_input = _compact_operator_brief_input_for_llm(prepared_input)
    _save_operator_brief_input_artifact(detail, prepared_input, compact_input)
    messages = _build_operator_brief_messages(compact_input)
    timeout_sec = int(float(os.getenv("OPERATOR_UI_RUN_BRIEF_TIMEOUT_SEC", "8")))
    retry_max = max(0, int(float(os.getenv("OPERATOR_UI_RUN_BRIEF_RETRY_MAX", "1"))))
    brief_token_budget = _env_int_with_fallback(
        "OPERATOR_UI_RUN_BRIEF_MAX_TOKENS",
        "OPENROUTER_DEFAULT_MAX_TOKENS",
        default=700,
    )
    brief_repair_token_budget = _env_int_with_fallback(
        "OPERATOR_UI_RUN_BRIEF_REPAIR_MAX_TOKENS",
        "OPERATOR_UI_RUN_BRIEF_MAX_TOKENS",
        "OPENROUTER_DEFAULT_MAX_TOKENS",
        default=max(600, brief_token_budget),
    )
    brief_line_token_budget = _env_int_with_fallback(
        "OPERATOR_UI_RUN_BRIEF_LINE_MAX_TOKENS",
        "OPERATOR_UI_RUN_BRIEF_REPAIR_MAX_TOKENS",
        "OPERATOR_UI_RUN_BRIEF_MAX_TOKENS",
        "OPENROUTER_DEFAULT_MAX_TOKENS",
        default=max(500, brief_token_budget),
    )
    primary_policy = {
        "temperature": float(os.getenv("OPERATOR_UI_RUN_BRIEF_TEMPERATURE", "0.1")),
        "max_tokens": brief_token_budget,
        "timeout_sec": timeout_sec,
        "response_format": {"type": "json_object"},
        "plugins": [{"id": "response-healing"}],
        **({"model": model} if model else {}),
    }
    primary_status = "error"
    primary_reason = ""
    primary_raw = ""
    primary_partial: Dict[str, Any] = {}
    primary_parse_meta: Dict[str, Any] = {
        "parse_mode": "none",
        "required_keys_expected": list(OPERATOR_BRIEF_REQUIRED_KEYS),
        "required_keys_present": [],
        "required_keys_missing": list(OPERATOR_BRIEF_REQUIRED_KEYS),
        "completeness_score": 0.0,
    }
    for attempt_index in range(retry_max + 1):
        step = "first_attempt" if attempt_index == 0 else f"retry_{attempt_index}"
        primary_t0 = time.perf_counter()
        try:
            raw = router.chat("operator_ui", messages, policy=primary_policy)
        except Exception as exc:
            status = classify_llm_exception(exc)
            reason = f"{type(exc).__name__}:{exc}"
            primary_status = status
            primary_reason = reason
            attempts.append(
                make_attempt(
                    step=step,
                    messages=messages,
                    raw_response_text=f"ERROR:{reason}",
                    parsed_output={},
                    model=model,
                    latency_ms=int((time.perf_counter() - primary_t0) * 1000),
                    status=status,
                    meta={
                        "role": "brief",
                        "error": reason,
                        "parse_mode": "none",
                        "required_keys_expected": list(OPERATOR_BRIEF_REQUIRED_KEYS),
                        "required_keys_present": [],
                        "required_keys_missing": list(OPERATOR_BRIEF_REQUIRED_KEYS),
                        "completeness_score": 0.0,
                    },
                )
            )
            if attempt_index < retry_max and _is_retryable_brief_failure(status, reason):
                continue
            break
        primary_latency_ms = int((time.perf_counter() - primary_t0) * 1000)
        primary_raw = raw
        parsed_result = parse_llm_json_response(raw)
        parsed_candidate = (
            parsed_result.get("full_object")
            if isinstance(parsed_result.get("full_object"), dict)
            else parsed_result.get("partial_object")
        )
        parsed_candidate = dict(parsed_candidate) if isinstance(parsed_candidate, dict) else {}
        parse_meta = _operator_brief_parse_meta(raw, parsed_candidate)
        primary_parse_meta = dict(parse_meta)
        # Mixed-language output is treated as a failure because this document is
        # the operator-facing single source for fast review, and partial Korean
        # mixed with Chinese/Japanese/English reads like a broken brief rather
        # than a usable status update.
        language_ok = _operator_brief_language_ok(parsed_candidate)
        if bool(parsed_result.get("is_full")) and _operator_brief_is_complete(parsed_candidate) and language_ok:
            attempts.append(
                make_attempt(
                    step=step,
                    messages=messages,
                    raw_response_text=raw,
                    parsed_output=parsed_candidate,
                    model=model,
                    latency_ms=primary_latency_ms,
                    status="ok",
                    meta={"role": "brief", "language_ok": True, **parse_meta},
                )
            )
            return finalize({
                "status": "ok",
                "model": model,
                "headline": str(parsed_candidate.get("headline") or fallback.get("headline") or ""),
                "commander_summary": str(parsed_candidate.get("commander_summary") or fallback.get("commander_summary") or ""),
                "strategist_summary": str(parsed_candidate.get("strategist_summary") or fallback.get("strategist_summary") or ""),
                "scanner_summary": str(parsed_candidate.get("scanner_summary") or fallback.get("scanner_summary") or ""),
                "monitor_summary": str(parsed_candidate.get("monitor_summary") or fallback.get("monitor_summary") or ""),
                "supervisor_summary": str(parsed_candidate.get("supervisor_summary") or fallback.get("supervisor_summary") or ""),
                "executor_summary": str(parsed_candidate.get("executor_summary") or fallback.get("executor_summary") or ""),
                "reporter_summary": str(parsed_candidate.get("reporter_summary") or fallback.get("reporter_summary") or ""),
                "operator_takeaways": [str(x or "") for x in list(parsed_candidate.get("operator_takeaways") or [])[:5] if str(x or "").strip()] or list(fallback.get("operator_takeaways") or []),
                "executive_summary": str(parsed_candidate.get("executive_summary") or ""),
                "scanner_reason": str(parsed_candidate.get("scanner_reason") or ""),
                "entry_summary": str(parsed_candidate.get("entry_summary") or ""),
                "holding_summary": str(parsed_candidate.get("holding_summary") or ""),
                "exit_plan_summary": str(parsed_candidate.get("exit_plan_summary") or ""),
                "risk_summary": str(parsed_candidate.get("risk_summary") or ""),
                "next_checkpoints": [str(x or "") for x in list(parsed_candidate.get("next_checkpoints") or [])[:5] if str(x or "").strip()],
                **parse_meta,
                "used_fallback_sections": [],
            })
        primary_partial = dict(parsed_candidate) if parsed_candidate else {}
        if parsed_candidate and not language_ok:
            primary_status = "partial"
            primary_reason = "language_policy_failed"
        elif not bool(parsed_result.get("raw_nonempty")):
            primary_status = "empty_response"
            primary_reason = "empty_response"
        elif parsed_candidate:
            primary_status = "partial"
            primary_reason = "brief_json_incomplete_or_partial"
        else:
            primary_status = "parse_error"
            primary_reason = "parse_error"
        attempts.append(
            make_attempt(
                step=step,
                messages=messages,
                raw_response_text=raw,
                parsed_output=parsed_candidate,
                model=model,
                latency_ms=primary_latency_ms,
                status=primary_status,
                meta={"role": "brief", "error": primary_reason, "language_ok": language_ok, **parse_meta},
            )
        )
        if attempt_index < retry_max and _is_retryable_brief_failure(primary_status, primary_reason):
            continue
        break

    repair_messages = _build_operator_brief_repair_messages(primary_raw)
    repair_policy = {
        "temperature": 0.0,
        "max_tokens": brief_repair_token_budget,
        "timeout_sec": timeout_sec,
        "response_format": {"type": "json_object"},
        "plugins": [{"id": "response-healing"}],
        **({"model": model} if model else {}),
    }
    repair_t0 = time.perf_counter()
    try:
        repair_raw = router.chat(
            "operator_ui",
            repair_messages,
            policy=repair_policy,
        )
    except Exception as exc:
        repair_raw = ""
        repair_error = f"{type(exc).__name__}:{exc}"
    else:
        repair_error = ""
    repair_latency_ms = int((time.perf_counter() - repair_t0) * 1000)
    repair_result = parse_llm_json_response(repair_raw)
    repaired = repair_result.get("full_object") if isinstance(repair_result.get("full_object"), dict) else repair_result.get("partial_object")
    repaired = dict(repaired) if isinstance(repaired, dict) else {}
    repair_meta = _operator_brief_parse_meta(repair_raw, repaired)
    repair_language_ok = _operator_brief_language_ok(repaired)
    if bool(repair_result.get("is_full")) and _operator_brief_is_complete(repaired) and repair_language_ok:
        attempts.append(
            make_attempt(
                step="repaired_attempt",
                messages=repair_messages,
                raw_response_text=repair_raw,
                parsed_output=repaired,
                model=model,
                latency_ms=repair_latency_ms,
                status="repaired",
                meta={"role": "brief", "language_ok": True, **repair_meta},
            )
        )
        return finalize({
            "status": "repaired",
            "model": model,
            "headline": str(repaired.get("headline") or fallback.get("headline") or ""),
            "commander_summary": str(repaired.get("commander_summary") or fallback.get("commander_summary") or ""),
            "strategist_summary": str(repaired.get("strategist_summary") or fallback.get("strategist_summary") or ""),
            "scanner_summary": str(repaired.get("scanner_summary") or fallback.get("scanner_summary") or ""),
            "monitor_summary": str(repaired.get("monitor_summary") or fallback.get("monitor_summary") or ""),
            "supervisor_summary": str(repaired.get("supervisor_summary") or fallback.get("supervisor_summary") or ""),
            "executor_summary": str(repaired.get("executor_summary") or fallback.get("executor_summary") or ""),
            "reporter_summary": str(repaired.get("reporter_summary") or fallback.get("reporter_summary") or ""),
            "operator_takeaways": [str(x or "") for x in list(repaired.get("operator_takeaways") or [])[:5] if str(x or "").strip()] or list(fallback.get("operator_takeaways") or []),
            "executive_summary": str(repaired.get("executive_summary") or ""),
            "scanner_reason": str(repaired.get("scanner_reason") or ""),
            "entry_summary": str(repaired.get("entry_summary") or ""),
            "holding_summary": str(repaired.get("holding_summary") or ""),
            "exit_plan_summary": str(repaired.get("exit_plan_summary") or ""),
            "risk_summary": str(repaired.get("risk_summary") or ""),
            "next_checkpoints": [str(x or "") for x in list(repaired.get("next_checkpoints") or [])[:5] if str(x or "").strip()],
            "reason": "llm_repair_pass",
            **repair_meta,
            "used_fallback_sections": [],
        })
    attempts.append(
        make_attempt(
            step="repaired_attempt",
            messages=repair_messages,
            raw_response_text=repair_raw,
            parsed_output=repaired,
            model=model,
            latency_ms=repair_latency_ms,
            status="empty_response" if not str(repair_raw or "").strip() else ("partial" if repaired else "parse_error"),
            meta={
                "role": "brief",
                "error": repair_error or ("language_policy_failed" if repaired and not repair_language_ok else ("repair_empty_response" if not str(repair_raw or "").strip() else "repair_parse_error")),
                "language_ok": repair_language_ok,
                **repair_meta,
            },
        )
    )
    if _is_free_model(model) or primary_reason in {"language_policy_failed", "parse_error", "brief_json_incomplete_or_partial"}:
        line_messages = _build_operator_brief_line_messages(compact_input)
        line_policy = {
            "temperature": 0.0,
            "max_tokens": brief_line_token_budget,
            "timeout_sec": timeout_sec,
            **({"model": model} if model else {}),
        }
        line_t0 = time.perf_counter()
        try:
            line_raw = router.chat(
                "operator_ui",
                line_messages,
                policy=line_policy,
            )
        except Exception as exc:
            line_raw = ""
            line_error = f"{type(exc).__name__}:{exc}"
        else:
            line_error = ""
        line_latency_ms = int((time.perf_counter() - line_t0) * 1000)
        line_parsed = _parse_operator_brief_lines(line_raw)
        line_meta = required_key_metadata(line_parsed, OPERATOR_BRIEF_REQUIRED_KEYS)
        line_language_ok = _operator_brief_language_ok(line_parsed)
        if line_parsed and not line_meta.get("required_keys_missing") and line_language_ok:
            attempts.append(
                make_attempt(
                    step="line_repair_attempt",
                    messages=line_messages,
                    raw_response_text=line_raw,
                    parsed_output=line_parsed,
                    model=model,
                    latency_ms=line_latency_ms,
                    status="salvaged",
                    meta={
                        "role": "brief",
                        "parse_mode": "none",
                        "language_ok": True,
                        **line_meta,
                        "used_fallback_sections": [],
                    },
                )
            )
            return finalize({
                "status": "salvaged",
                "model": model,
                "headline": str(line_parsed.get("headline") or fallback.get("headline") or ""),
                "commander_summary": str(line_parsed.get("commander_summary") or fallback.get("commander_summary") or ""),
                "strategist_summary": str(line_parsed.get("strategist_summary") or fallback.get("strategist_summary") or ""),
                "scanner_summary": str(line_parsed.get("scanner_summary") or fallback.get("scanner_summary") or ""),
                "monitor_summary": str(line_parsed.get("monitor_summary") or fallback.get("monitor_summary") or ""),
                "supervisor_summary": str(line_parsed.get("supervisor_summary") or fallback.get("supervisor_summary") or ""),
                "executor_summary": str(line_parsed.get("executor_summary") or fallback.get("executor_summary") or ""),
                "reporter_summary": str(line_parsed.get("reporter_summary") or fallback.get("reporter_summary") or ""),
                "operator_takeaways": [str(x or "") for x in list(line_parsed.get("operator_takeaways") or [])[:5] if str(x or "").strip()] or list(fallback.get("operator_takeaways") or []),
                "executive_summary": str(line_parsed.get("executive_summary") or ""),
                "scanner_reason": str(line_parsed.get("scanner_reason") or ""),
                "entry_summary": str(line_parsed.get("entry_summary") or ""),
                "holding_summary": str(line_parsed.get("holding_summary") or ""),
                "exit_plan_summary": str(line_parsed.get("exit_plan_summary") or ""),
                "risk_summary": str(line_parsed.get("risk_summary") or ""),
                "next_checkpoints": [str(x or "") for x in list(line_parsed.get("next_checkpoints") or [])[:5] if str(x or "").strip()],
                "reason": "llm_line_repair_pass",
                "parse_mode": "none",
                **line_meta,
                "used_fallback_sections": [],
            })
        attempts.append(
            make_attempt(
                step="line_repair_attempt",
                messages=line_messages,
                raw_response_text=line_raw,
                parsed_output=line_parsed,
                model=model,
                latency_ms=line_latency_ms,
                status="empty_response" if not str(line_raw or "").strip() else ("partial" if line_parsed else "parse_error"),
                meta={
                    "role": "brief",
                    "error": line_error or ("language_policy_failed" if line_parsed and not line_language_ok else ("line_repair_empty_response" if not str(line_raw or "").strip() else "line_repair_parse_error")),
                    "parse_mode": "none",
                    "language_ok": line_language_ok,
                    **line_meta,
                },
            )
        )

    fallback_brief = _failure_operator_brief(
        detail,
        status="fallback",
        model=model,
        reason=primary_reason or "brief_generation_failed",
        failure_status=primary_status,
    )
    fallback_brief.update(
        {
            "fallback_rendered": True,
            "parse_mode": str(primary_parse_meta.get("parse_mode") or "none"),
            "required_keys_expected": list(primary_parse_meta.get("required_keys_expected") or OPERATOR_BRIEF_REQUIRED_KEYS),
            "required_keys_present": list(primary_parse_meta.get("required_keys_present") or []),
            "required_keys_missing": list(primary_parse_meta.get("required_keys_missing") or OPERATOR_BRIEF_REQUIRED_KEYS),
            "completeness_score": float(primary_parse_meta.get("completeness_score") or 0.0),
            "used_fallback_sections": list(OPERATOR_BRIEF_REQUIRED_KEYS),
        }
    )
    if primary_partial:
        fallback_brief["failure"]["partial_fields_recovered"] = sorted(primary_partial.keys())
    return finalize(fallback_brief)


def _load_cached_operator_brief(config: OperatorUIConfig, run_id: str) -> Dict[str, Any]:
    if _operator_brief_force_regenerate_enabled():
        return {}
    if not run_id:
        return {}
    path = config.operator_ui_cache_path / f"{run_id}.json"
    cached = _read_json(path)
    if not isinstance(cached, dict):
        return {}
    if int(cached.get("version") or 0) < OPERATOR_BRIEF_ARTIFACT_VERSION:
        return {}
    return cached


def _save_cached_operator_brief(config: OperatorUIConfig, run_id: str, brief: Dict[str, Any]) -> None:
    if not run_id or not isinstance(brief, dict):
        return
    path = config.operator_ui_cache_path / f"{run_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(brief)
    payload["version"] = OPERATOR_BRIEF_ARTIFACT_VERSION
    payload["cached_at"] = datetime.now(tz=KST).isoformat()
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _operator_brief_artifact_paths(detail: Dict[str, Any]) -> tuple[Path | None, Path | None]:
    trade_report = detail.get("trade_report") if isinstance(detail.get("trade_report"), dict) else {}
    trade_root_path = Path(str(trade_report.get("trade_root_path") or "")).resolve() if str(trade_report.get("trade_root_path") or "").strip() else None
    if trade_root_path is not None:
        return trade_root_path / "reports" / "operator_brief.json", trade_root_path / "reports" / "operator_brief.md"
    candidate_paths = [
        str(trade_report.get("operator_brief_json_path") or ""),
        str(trade_report.get("trade_report_json_path") or ""),
        str(trade_report.get("trade_story_input_path") or ""),
        str(trade_report.get("trade_lifecycle_json_path") or ""),
        str(trade_report.get("aggregated_bundle_path") or ""),
    ]
    for raw in candidate_paths:
        text = str(raw or "").strip()
        if not text:
            continue
        path = Path(text)
        if path.name == "operator_brief.json":
            return path, path.with_suffix(".md")
        if path.suffix:
            parent = path.parent
            if parent.name in {"ai_trade_report", "lifecycle", "strategist", "brief", "evidence"}:
                parent = parent.parent
        else:
            parent = path
        brief_json = parent / "reports" / "operator_brief.json"
        brief_md = parent / "reports" / "operator_brief.md"
        return brief_json, brief_md
    return None, None


def _operator_brief_input_artifact_path(detail: Dict[str, Any]) -> Path | None:
    trade_report = detail.get("trade_report") if isinstance(detail.get("trade_report"), dict) else {}
    trade_root_path = Path(str(trade_report.get("trade_root_path") or "")).resolve() if str(trade_report.get("trade_root_path") or "").strip() else None
    if trade_root_path is not None:
        return trade_root_path / "brief_input.json"
    brief_json, _brief_md = _operator_brief_artifact_paths(detail)
    if brief_json is None:
        return None
    return brief_json.parent.parent / "brief_input.json"


def _operator_brief_compact_input_artifact_path(detail: Dict[str, Any]) -> Path | None:
    trade_report = detail.get("trade_report") if isinstance(detail.get("trade_report"), dict) else {}
    trade_root_path = Path(str(trade_report.get("trade_root_path") or "")).resolve() if str(trade_report.get("trade_root_path") or "").strip() else None
    if trade_root_path is not None:
        return trade_root_path / "brief_compact_input.json"
    brief_json, _brief_md = _operator_brief_artifact_paths(detail)
    if brief_json is None:
        return None
    return brief_json.parent.parent / "brief_compact_input.json"


def _save_operator_brief_input_artifact(detail: Dict[str, Any], prepared_input: Dict[str, Any], llm_compact_input: Dict[str, Any] | None = None) -> None:
    input_path = _operator_brief_input_artifact_path(detail)
    compact_path = _operator_brief_compact_input_artifact_path(detail)
    if input_path is None and compact_path is None:
        return

    trade_report = detail.get("trade_report") if isinstance(detail.get("trade_report"), dict) else {}
    run_id = str(detail.get("run_id") or trade_report.get("run_id") or "").strip()
    trade_id = str(
        trade_report.get("trade_id")
        or trade_report.get("story_id")
        or detail.get("trade_id")
        or detail.get("story_id")
        or ""
    ).strip()
    day = str(trade_report.get("day") or detail.get("day") or "").strip()
    source_artifact_path = str(
        trade_report.get("trade_story_input_path")
        or trade_report.get("ai_trade_report_input_path")
        or ""
    ).strip()

    if input_path is not None:
        try:
            input_payload = {
                "schema_version": "operator_brief_input.v1",
                "component": "brief",
                "role": "brief",
                "run_id": run_id,
                "trade_id": trade_id,
                "story_id": trade_id,
                "day": day,
                "saved_at": datetime.now(timezone.utc).isoformat(),
                "input_variant": "full_input",
                "source_artifact_path": source_artifact_path,
                "input": dict(prepared_input or {}),
            }
            input_path.parent.mkdir(parents=True, exist_ok=True)
            input_path.write_text(json.dumps(input_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    if compact_path is not None:
        try:
            compact_artifact = build_compact_input_artifact(
                component="brief",
                run_id=run_id,
                trade_id=trade_id,
                story_id=trade_id,
                day=day,
                source_artifact_path=str(input_path or ""),
                source_input=prepared_input if isinstance(prepared_input, dict) else {},
                compact_input=llm_compact_input if isinstance(llm_compact_input, dict) else {},
            )
            compact_path.parent.mkdir(parents=True, exist_ok=True)
            compact_path.write_text(json.dumps(compact_artifact, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass


def _render_operator_brief_markdown(brief: Dict[str, Any]) -> str:
    def _action_label(action: Any) -> str:
        mapping = {
            "BUY": "매수",
            "SELL": "매도",
            "HOLD": "보유 유지",
            "WAIT": "진입 보류",
        }
        return mapping.get(str(action or "").strip().upper(), str(action or "-").strip() or "-")

    def _metric_text(value: Any) -> str:
        text = _sanitize_operator_brief_text(value)
        return text or "-"

    def _axis_label(value: Any) -> str:
        raw = _sanitize_operator_brief_text(value)
        lowered = raw.lower()
        mapping = {
            "고정 손절 기준": "고정 손절 기준",
            "상황 대응형 손절 기준": "상황 대응형 손절 기준",
            "목표 수익 실현 기준": "목표 수익 실현 기준",
            "hard stop": "고정 손절 기준",
            "adaptive stop": "상황 대응형 손절 기준",
            "take profit": "목표 수익 실현 기준",
            "vwap breakdown": "VWAP 이탈",
            "vwap_breakdown": "VWAP 이탈",
            "peak drawdown": "고점 대비 하락폭 확대",
            "peak_drawdown": "고점 대비 하락폭 확대",
            "prior low break": "직전 저점 이탈",
            "prior_low_break": "직전 저점 이탈",
            "intraday low break": "장중 저점 이탈",
            "intraday_low_break": "장중 저점 이탈",
            "confirmed_exit_signal": "청산 확인 신호",
            "defensive exit": "방어형 청산 신호",
            "defensive_exit": "방어형 청산 신호",
            "방어형 청산": "방어형 청산 신호",
            "기록되지 않음": "기록된 기준 축 없음",
            "확인되지 않음": "기록된 기준 축 없음",
            "판단 정보 없음": "기록된 기준 축 없음",
            "포지션 없음": "포지션 없음",
        }
        return mapping.get(lowered, raw or "감시 조건 변화")

    def _axis_is_explicit(value: str) -> bool:
        return str(value or "").strip() not in {"", "-", "감시 조건 변화", "기록된 기준 축 없음", "포지션 없음", "판단 정보 없음"}

    def _narrative_text(text: Any) -> str:
        raw_source = _trim_text(text, max_len=1000)
        cleaned = _sanitize_operator_brief_text(text)
        if not cleaned:
            return ""
        raw_lower = raw_source.lower()
        m = re.fullmatch(r"universe scanned\s*:\s*(\d+)", raw_lower)
        if m:
            return f"총 {m.group(1)}개 후보를 비교했습니다."
        m = re.fullmatch(r"selected rank\s*:\s*#?(\d+)", raw_lower)
        if m:
            return f"비교 대상 중 {m.group(1)}순위로 선정되었습니다."
        m = re.fullmatch(r"posture\s*:\s*(buy|sell|hold|wait)", raw_lower)
        if m:
            return f"현재 포지션 판단은 {_action_label(m.group(1))}입니다."
        m = re.fullmatch(r"trigger\s*:\s*(.+)", raw_lower)
        if m:
            trigger = m.group(1).strip()
            if trigger in {"-", "no", "none"}:
                return "추가 진입 또는 청산을 확정할 신호는 아직 확인되지 않았습니다."
            return f"현재 감시 신호는 {cleaned.split(':', 1)[-1].strip()}입니다."
        m = re.fullmatch(r"exit trigger\s*:\s*(.+)", raw_lower)
        if m:
            trigger = m.group(1).strip()
            if trigger in {"-", "no", "none"}:
                return "아직 청산 신호는 확인되지 않았습니다."
            return f"현재 확인된 청산 신호는 {cleaned.split(':', 1)[-1].strip()}입니다."
        if raw_lower.startswith("runner-up symbols had weaker coverage"):
            return "후순위 후보는 차트 완성도와 보조 신호가 더 약했습니다."
        m = re.fullmatch(r"chart / feature coverage\s*:\s*(\d+)/(\d+)", raw_lower)
        if m:
            return f"차트와 피처 확인 항목은 {m.group(1)}/{m.group(2)} 수준으로 확보되었습니다."
        m = re.fullmatch(r"chart completeness filter\s*:\s*pass\s*-\s*(.+)", raw_lower)
        if m:
            return f"차트 확인 조건은 {m.group(1).strip()} 수준으로 충족되었습니다."
        if raw_lower.startswith("liquidity filter:"):
            return "유동성 조건은 충족되었습니다."
        if raw_lower.startswith("turnover filter:"):
            return "거래대금 조건은 충족되었습니다."
        if re.match(r"^[A-Za-z][A-Za-z0-9 /_-]*:\s*", raw_source):
            return ""
        return cleaned

    def _append_list(lines: List[str], items: List[str], *, limit: int = 3) -> None:
        appended = 0
        for item in items:
            text = _narrative_text(item)
            if not text or _count_hangul_chars(text) <= 0:
                continue
            lines.append(f"- {text}")
            appended += 1
            if appended >= limit:
                break

    def _vwap_interpretation(value: Any) -> str:
        raw = _safe_float(value, None)
        if raw is None:
            return "-"
        if raw >= 0.02:
            return f"{_format_percent(raw, 2)} (과도 확장으로 추격 진입에 주의가 필요한 구간입니다.)"
        if raw >= 0.0:
            return f"+{abs(raw) * 100:.2f}% (VWAP 위에서 흐름을 유지하고 있습니다.)"
        if raw <= -0.01:
            return f"{_format_percent(raw, 2)} (VWAP 아래로 밀리며 약세 압력이 커진 구간입니다.)"
        return f"{_format_percent(raw, 2)} (중립 범위 안에서 움직이고 있습니다.)"

    def _entry_reason_text(reason_code: str, pattern: str, metrics: Dict[str, Any], posture_action: str) -> str:
        reason = str(reason_code or "").strip().lower()
        metric_map = metrics if isinstance(metrics, dict) else {}
        recent_high = metric_map.get("recent_high")
        vwap = metric_map.get("vwap")
        volume_ratio = metric_map.get("volume_ratio")
        vwap_distance = metric_map.get("vwap_distance")
        pullback_pct = metric_map.get("pullback_pct")
        executed_trade = posture_action in {"BUY", "HOLD", "SELL"}
        if pattern in {"breakout_vwap_hold", "breakout"}:
            parts = ["분봉 기준으로 최근 고점 돌파와 VWAP 상회 유지, 거래량 확인이 함께 맞물려 진입했습니다."]
            if recent_high not in (None, ""):
                parts.append(f"최근 고점 기준값은 {_format_float(recent_high, 2)}였습니다.")
            if vwap not in (None, ""):
                parts.append(f"당시 VWAP 기준값은 {_format_float(vwap, 2)}였습니다.")
            if volume_ratio not in (None, ""):
                parts.append(f"거래량은 평시 대비 {_format_float(volume_ratio, 2)}배 수준으로 확인됐습니다.")
            return " ".join(parts)
        if pattern in {"pullback_rebound", "pullback_vwap_hold"}:
            parts = ["분봉 기준으로 눌림 이후 반등이 확인됐고, VWAP 재안착 흐름까지 확인되어 진입했습니다."]
            if pullback_pct not in (None, ""):
                parts.append(f"눌림 폭은 {_format_percent(pullback_pct, 2)} 수준이었습니다.")
            if volume_ratio not in (None, ""):
                parts.append(f"거래량은 평시 대비 {_format_float(volume_ratio, 2)}배 수준으로 확인됐습니다.")
            return " ".join(parts)
        mapping = {
            "minute_candle_missing": "이번 거래는 분봉 데이터가 확보되지 않아 진입 근거를 확인할 수 없었습니다. 따라서 신규 진입은 보류 대상으로 해석했습니다.",
            "data_incomplete": "체결 이전 분봉 기록이 충분하지 않아 진입 시점을 확정하기 어렵습니다. 현재 문서는 보유 관리와 청산 기준 중심으로 정리했습니다.",
            "no_breakout_signal": "저장된 분봉 범위에서는 최근 고점 돌파나 첫 눌림목 반등 신호가 확인되지 않았습니다. 따라서 진입은 보류 판단으로 정리했습니다.",
            "vwap_not_confirmed": "분봉 흐름에서 VWAP 상회 유지나 재안착이 확인되지 않았습니다. 추격 진입 위험을 피하기 위해 진입 보류로 해석했습니다.",
            "volume_insufficient": "분봉 거래량이 돌파 신호를 뒷받침할 만큼 충분하지 않았습니다. 따라서 이번 구간은 보수적으로 진입 보류로 판단했습니다.",
            "too_extended_from_vwap": "VWAP 대비 과도하게 확장된 상태여서 추격 진입을 피했습니다.",
            "post_exit_cooldown": "직전 청산 직후 재진입 쿨다운 구간이라 신규 진입을 보류했습니다.",
            "buy_blocked_open_position": "기존 보유 포지션이 있어 신규 진입을 차단했습니다.",
            "no_position": "저장된 데이터 범위 안에서는 체결 직전 분봉 진입 근거가 충분히 남아 있지 않았습니다. 이번 문서는 진입 해석보다 이후 보유 관리 기록을 중심으로 정리했습니다.",
            "peak_drawdown": "이번 저장값에는 진입 근거보다 청산 관리 신호가 더 선명하게 남아 있습니다. 진입 시점의 분봉 근거는 별도로 확인되지 않아 보수적으로 정리했습니다.",
            "hard_stop": "이번 저장값에는 진입 근거보다 손절 관리 신호가 더 분명하게 남아 있습니다. 진입 시점의 분봉 근거는 별도로 확인되지 않아 보수적으로 정리했습니다.",
            "pullback_structure_above_vwap_with_confirmation": "분봉 기준으로 VWAP 상단 눌림 이후 재확인 신호가 확인되어 진입했습니다.",
        }
        if mapping.get(reason):
            return mapping[reason]
        if str(reason_code or "").strip():
            reason_text = _sanitize_operator_brief_text(str(reason_code or "").strip())
            if executed_trade:
                return f"분봉 조건 점검 결과 {reason_text} 신호가 확인되어 진입했습니다."
            return f"분봉 조건 점검 결과 {reason_text} 상태로 해석되어 진입을 보류했습니다."
        if vwap_distance not in (None, ""):
            return f"분봉 조건을 점검 중이며 현재 VWAP 이격은 {_format_percent(vwap_distance, 2)} 수준입니다. 추가 확인 전까지는 보수적으로 접근합니다."
        return "분봉 데이터와 체결 근거를 보수적으로 점검한 결과, 당장 진입을 확정하기보다 추가 확인이 필요한 상태로 해석했습니다."

    def _default_next_checkpoints(entry: Dict[str, Any], monitor: Dict[str, Any], exit_plan: Dict[str, Any], posture_action: str) -> List[str]:
        metrics = entry.get("metrics") if isinstance(entry.get("metrics"), dict) else {}
        watch_axes = [str(x or "").strip() for x in list(exit_plan.get("watch_axes") or monitor.get("watch_axes") or []) if str(x or "").strip()]
        derived: List[str] = []
        if posture_action == "WAIT":
            if metrics.get("recent_high") not in (None, ""):
                derived.append("분봉 기준으로 최근 고점 재돌파 여부를 다음 체크포인트로 확인합니다.")
            if metrics.get("volume_ratio") not in (None, ""):
                derived.append("거래량 증가가 다시 동반되는지 확인합니다.")
            if not derived:
                derived.append("분봉 기준으로 재돌파 여부와 거래량 증가 여부를 다음 체크포인트로 설정합니다.")
        elif posture_action in {"BUY", "HOLD"}:
            derived.append("분봉 기준으로 지지선 유지 여부와 거래량 둔화 여부를 먼저 확인합니다.")
            if any("vwap" in axis.lower() for axis in watch_axes):
                derived.append("VWAP 재이탈 여부와 거래량 감소 여부를 중심으로 모니터링합니다.")
            derived.append("현재 보유 상태에서는 고점 대비 하락폭과 거래량 둔화를 주요 확인 지표로 봅니다.")
        else:
            derived.append("다음 거래에서는 분봉 진입 근거와 후보 비교 데이터가 충분히 남는지 먼저 확인합니다.")
            derived.append("청산 이후에는 동일 종목의 재돌파 여부와 거래대금 회복 여부를 다시 확인합니다.")
        return derived[:3]

    valid_statuses = {"", "ok", "partial", "salvaged", "repaired", "fallback"}
    status = str(brief.get("status") or "").strip().lower()
    if status not in valid_statuses:
        lines = brief_render_lines(brief=brief, _metric_text=_metric_text, facade=_r3_sys.modules[__name__])[0]
        return "\n".join(lines)

    current_snapshot, entry, executive, exit_plan, final_action, headline, market, monitor, monitor_guard_snapshot, next_step_section, operator_conclusion, posture_action, risk_alerts, scanner_focus, selected_symbol, selection, strategist_evidence = brief_render_current_snapshot_entry(brief=brief, facade=_r3_sys.modules[__name__])

    def _usable_narrative_text(text: Any) -> str:
        cleaned = _narrative_text(text)
        return cleaned if _count_hangul_chars(cleaned) >= 4 else ""

    def _summary_text(section: Dict[str, Any], *extra: Any) -> str:
        candidates: List[Any] = [section.get("summary")] if isinstance(section, dict) else []
        candidates.extend(extra)
        for candidate in candidates:
            text = _usable_narrative_text(candidate) or _narrative_text(candidate)
            if text:
                return text
        return ""

    def _compact_items(values: Any, *, limit: int = 3, max_len: int = 180) -> List[str]:
        items = _clean_str_list(values, limit=limit, max_len=max_len)
        out: List[str] = []
        for item in items:
            text = _sanitize_operator_brief_text(item)
            if text:
                out.append(text)
        return out

    if any(
        isinstance(section, dict) and section
        for section in (
            current_snapshot,
            strategist_evidence,
            scanner_focus,
            monitor_guard_snapshot,
            next_step_section,
        )
    ):
        lines, market_headlines, monitor_reason, monitor_summary, next_step_summary, next_watch, scanner_summary, score_driver_items, selection_reason, stop_policy_summary, symbol_headlines, takeaways, top_candidates_summary = brief_render_lines_market_headlines(_summary_text=_summary_text, current_snapshot=current_snapshot, brief=brief, strategist_evidence=strategist_evidence, scanner_focus=scanner_focus, monitor_guard_snapshot=monitor_guard_snapshot, next_step_section=next_step_section, operator_conclusion=operator_conclusion, executive=executive, _compact_items=_compact_items, facade=_r3_sys.modules[__name__])
        if market_headlines:
            lines.append("- 시장 헤드라인:")
            for item in market_headlines:
                lines.append(f"  - {item}")
        if symbol_headlines:
            lines.append("- 선택 종목 관련 헤드라인:")
            for item in symbol_headlines:
                lines.append(f"  - {item}")

        brief_render_effect_free_block_3748(lines=lines, scanner_summary=scanner_summary, scanner_focus=scanner_focus, top_candidates_summary=top_candidates_summary, selection_reason=selection_reason, score_driver_items=score_driver_items, monitor_summary=monitor_summary, monitor_reason=monitor_reason, facade=_r3_sys.modules[__name__])
        if stop_policy_summary:
            lines.append("- 활성 스톱 정책:")
            for item in stop_policy_summary:
                lines.append(f"  - {item}")

        lines.extend([
            "",
            "## 5. 다음 예상 단계",
            "",
            f"- {next_step_summary}",
        ])
        for item in next_watch:
            lines.append(f"- {item}")

        lines.extend([
            "",
            "## 6. 운영자 포인트",
            "",
        ])
        if takeaways:
            for item in takeaways:
                lines.append(f"- {item}")
        else:
            lines.append("- 현재 snapshot 기준 핵심 판단과 다음 체크포인트를 우선 확인합니다.")

        if lines[-1] != "":
            lines.append("")
        return "\n".join(lines)

    comparison_reasons, display_symbol, entry_summary, executive_summary, exit_plan_summary, holding_summary, next_checkpoints, risk_summary, scanner_reason, selection_reasons, takeaways = brief_fallback_comparison_reasons_display_symbol(selected_symbol=selected_symbol, _usable_narrative_text=_usable_narrative_text, _narrative_text=_narrative_text, brief=brief, status=status, headline=headline, posture_action=posture_action, selection=selection, facade=_r3_sys.modules[__name__])
    if not entry_summary:
        entry_reason_text = _narrative_text(str(entry.get("reason_text") or "").strip())
        if _count_hangul_chars(entry_reason_text) > 0 and status != "fallback":
            entry_summary = entry_reason_text
        else:
            entry_summary = _entry_reason_text(
                str(entry.get("reason_code") or ""),
                str(entry.get("pattern") or ""),
                entry.get("metrics") if isinstance(entry.get("metrics"), dict) else {},
                posture_action,
            )

    if not executive_summary:
        if posture_action == "SELL":
            executive_summary = f"{display_symbol} \uac70\ub798\ub294 \uccad\uc0b0\uae4c\uc9c0 \ub9c8\ubb34\ub9ac\ub418\uc5c8\uace0, \ud655\uc778\ub41c \uc190\uc775\uacfc \ud558\ub77d\ud3ed \uae30\uc900\uc73c\ub85c \ub9e4\ub3c4 \ud310\ub2e8\uc774 \uc2e4\ud589\ub418\uc5c8\uc2b5\ub2c8\ub2e4."
        elif posture_action == "WAIT":
            executive_summary = f"{display_symbol}\uc5d0 \ub300\ud574\uc11c\ub294 \uc2e0\uaddc \uc9c4\uc785\uc744 \ubcf4\ub958\ud558\uace0 \ucd94\uac00 \ud655\uc778\uc744 \uc774\uc5b4\uac00\ub294 \ud310\ub2e8\uc785\ub2c8\ub2e4."
        else:
            executive_summary = f"{display_symbol}\uc758 \ud604\uc7ac \ucd5c\uc885 \ud310\ub2e8\uc740 {_action_label(posture_action)}\uc785\ub2c8\ub2e4."

    if not holding_summary:
        if posture_action == "SELL":
            holding_summary = (
                f"{display_symbol} \uac70\ub798\ub294 \uc774\ubbf8 \ub9e4\ub3c4\ub85c \uc885\ub8cc\ub418\uc5c8\uc2b5\ub2c8\ub2e4. \ud3c9\uade0 \ub9e4\uc218\uac00\ub294 {_metric_text(monitor.get('average_price'))}\uc600\uace0, "
                f"\uccad\uc0b0 \ud310\ub2e8 \ub2f9\uc2dc \uac00\uaca9\uc740 {_metric_text(monitor.get('current_price'))}\uc600\uc2b5\ub2c8\ub2e4. "
                f"\uace0\uc810 \ub300\ube44 \ud558\ub77d\ud3ed\uc740 {_metric_text(monitor.get('peak_drawdown'))} \uc218\uc900\uc73c\ub85c \ud655\uc778\ub429\ub2c8\ub2e4."
            )
        elif posture_action == "WAIT":
            holding_summary = (
                f"{display_symbol}\uc5d0 \ub300\ud574\uc11c\ub294 \uc544\uc9c1 \uc2e0\uaddc \uc9c4\uc785\uc744 \uc2e4\ud589\ud558\uc9c0 \uc54a\uc558\uc2b5\ub2c8\ub2e4. "
                f"\ud604\uc7ac \ubb38\uc11c\ub294 \ubcf4\uc720 \uad00\ub9ac \uae30\ub85d\ubcf4\ub2e4 \uc9c4\uc785 \ubcf4\ub958 \uc0ac\uc720\uc640 \ub2e4\uc74c \ud655\uc778 \ud56d\ubaa9\uc744 \uc911\uc2ec\uc73c\ub85c \uc815\ub9ac\ud588\uc2b5\ub2c8\ub2e4."
            )
        else:
            active_axis = _axis_label(monitor.get("active_exit_axis") or "-")
            active_axis_text = (
                f"현재 관리는 {active_axis} 기준으로 이어가고 있습니다."
                if _axis_is_explicit(active_axis)
                else "현재 관리는 저장된 손절·청산 기준을 중심으로 이어가고 있습니다."
            )
            holding_summary = (
                f"{display_symbol}\uc740 \ud604\uc7ac {_action_label(monitor.get('posture') or final_action)} \uc0c1\ud0dc\uc785\ub2c8\ub2e4. "
                f"\ud604\uc7ac\uac00\ub294 {_metric_text(monitor.get('current_price'))}, \ud3c9\uade0 \ub2e8\uac00\ub294 {_metric_text(monitor.get('average_price'))}\uc774\uba70, "
                f"{active_axis_text}"
            )

    if not exit_plan_summary:
        effective_stop = _metric_text(exit_plan.get("effective_stop") or monitor.get("effective_stop"))
        effective_stop_reason = _axis_label(exit_plan.get("effective_stop_reason") or monitor.get("effective_stop_reason"))
        take_profit = _metric_text(exit_plan.get("take_profit") or monitor.get("take_profit"))
        watch_axes = [_axis_label(x) for x in list(exit_plan.get("watch_axes") or monitor.get("watch_axes") or [])[:2] if str(x or "").strip()]
        axes_text = ", ".join(watch_axes) if watch_axes else "\uc8fc\uc694 \uac10\uc2dc \uc870\uac74 \ubcc0\ud654"
        if posture_action == "SELL":
            axis_prefix = (
                f"{effective_stop_reason} 기준과"
                if _axis_is_explicit(effective_stop_reason)
                else "저장된 손절 기준과"
            )
            exit_plan_summary = (
                f"\uc774\ubc88 \uac70\ub798\ub294 {axis_prefix} \uace0\uc810 \ub300\ube44 \ud558\ub77d\ud3ed \uc870\uac74\uc744 \uc6b0\uc120 \ud655\uc778\ud55c \ub4a4 \uccad\uc0b0\uc744 \uc2e4\ud589\ud588\uc2b5\ub2c8\ub2e4. "
                f"\ucc38\uace0 \uc190\uc808 \uae30\uc900\uc740 {effective_stop} \uc218\uc900\uc774\uc5c8\uace0, \ubaa9\ud45c \uc218\uc775 \uc2e4\ud604 \uae30\uc900\uc740 {take_profit} \uc218\uc900\uc774\uc5c8\uc2b5\ub2c8\ub2e4."
            )
        elif posture_action == "WAIT":
            exit_plan_summary = (
                f"\uc2e0\uaddc \uc9c4\uc785 \uc804\uae4c\uc9c0\ub294 {axes_text}\ub97c \uba3c\uc800 \uc810\uac80\ud558\uace0, \ubd84\ubd09 \uae30\uc900\uc774 \ub2e4\uc2dc \ub9de\uc544\ub5a8\uc5b4\uc9c8 \ub54c\uae4c\uc9c0 \ubcf4\uc218\uc801\uc73c\ub85c \ub300\uae30\ud569\ub2c8\ub2e4."
            )
        else:
            axis_prefix = (
                f"\uc6b0\uc120 {effective_stop_reason}\uc744 \uae30\uc900\uc73c\ub85c \ub300\uc751\ud558\uace0"
                if _axis_is_explicit(effective_stop_reason)
                else "\uc6b0\uc120 \uc800\uc7a5\ub41c \uc190\uc808 \uae30\uc900\uc744 \uc911\uc2ec\uc73c\ub85c \ub300\uc751\ud558\uace0"
            )
            exit_plan_summary = (
                f"{axis_prefix} \uae30\uc900\uac12\uc740 {effective_stop} \uc218\uc900\uc73c\ub85c \ubcf4\uace0 \uc788\uc2b5\ub2c8\ub2e4. "
                f"\ubaa9\ud45c \uc218\uc775 \uc2e4\ud604 \uae30\uc900\uc740 {take_profit} \uc218\uc900\uc774\uba70, {axes_text}\uac00 \ud754\ub4e4\ub9ac\uba74 \ub2e4\uc2dc \ud310\ub2e8\ud569\ub2c8\ub2e4."
            )

    if not risk_summary:
        weak_factors = [_narrative_text(x) for x in list(risk_alerts.get("weak_factors") or []) if _narrative_text(x)]
        if weak_factors and status != "fallback":
            risk_summary = " ".join(weak_factors[:3])
        elif bool(risk_alerts.get("defensive_mode")):
            risk_summary = "\uac70\uc2dc \uc2a4\ud2b8\ub808\uc2a4 \uc2e0\ud638\uac00 \ub192\uc544 \uc788\uc5b4 \ubc29\uc5b4\uc801\uc73c\ub85c \ub300\uc751\ud560 \ud544\uc694\uac00 \uc788\uc2b5\ub2c8\ub2e4."
        else:
            risk_summary = "\ud604\uc7ac \uc815\ubcf4 \ubc94\uc704\uc5d0\uc11c\ub294 \ucd94\uac00 \ub9ac\uc2a4\ud06c\uac00 \uc81c\ud55c\uc801\uc774\uc9c0\ub9cc \ubd84\ubd09 \uad6c\uc870 \ubcc0\ud654\uc640 \uac70\ub798\ub7c9 \ub454\ud654 \uc5ec\ubd80\ub97c \uacc4\uc18d \ud655\uc778\ud574\uc57c \ud569\ub2c8\ub2e4."

    lines = brief_fallback_lines(next_checkpoints=next_checkpoints, _narrative_text=_narrative_text, operator_conclusion=operator_conclusion, takeaways=takeaways, _default_next_checkpoints=_default_next_checkpoints, entry=entry, monitor=monitor, exit_plan=exit_plan, posture_action=posture_action, executive_summary=executive_summary, scanner_reason=scanner_reason, _append_list=_append_list, selection_reasons=selection_reasons, comparison_reasons=comparison_reasons, entry_summary=entry_summary, _vwap_interpretation=_vwap_interpretation, holding_summary=holding_summary, _action_label=_action_label, _metric_text=_metric_text, final_action=final_action, exit_plan_summary=exit_plan_summary, _axis_is_explicit=_axis_is_explicit, _axis_label=_axis_label, risk_summary=risk_summary, risk_alerts=risk_alerts, market=market, facade=_r3_sys.modules[__name__])[0]
    return "\n".join(lines)
def _operator_brief_source_signature(detail: Dict[str, Any]) -> str:
    trade_report = detail.get("trade_report") if isinstance(detail.get("trade_report"), dict) else {}
    candidate_paths = [
        trade_report.get("trade_report_json_path"),
        trade_report.get("trade_story_input_path"),
        trade_report.get("trade_lifecycle_json_path"),
        trade_report.get("ai_trade_report_llm_response_path"),
    ]
    parts: List[str] = []
    for raw in candidate_paths:
        text = str(raw or "").strip()
        if not text:
            continue
        path = Path(text)
        if not path.exists() or path.is_dir():
            continue
        stat = path.stat()
        parts.append(f"{path.name}:{stat.st_mtime_ns}:{stat.st_size}")
    if not parts:
        parts.extend(
            [
                f"run_id:{str(detail.get('run_id') or '').strip()}",
                f"trade_id:{str(trade_report.get('trade_id') or '').strip()}",
                f"report_status:{str(trade_report.get('report_status') or '').strip()}",
                f"lifecycle_status:{str(trade_report.get('lifecycle_status') or '').strip()}",
            ]
        )
    return "|".join(parts)


def _saved_operator_brief_matches_detail(saved: Dict[str, Any], detail: Dict[str, Any]) -> bool:
    trade_report = detail.get("trade_report") if isinstance(detail.get("trade_report"), dict) else {}
    if str(saved.get("run_id") or "").strip() != str(detail.get("run_id") or "").strip():
        return False
    if str(saved.get("trade_id") or "").strip() != str(trade_report.get("trade_id") or "").strip():
        return False
    if str(saved.get("story_id") or "").strip() != str(trade_report.get("story_id") or "").strip():
        return False
    if str(saved.get("lifecycle_status") or "").strip() != str(trade_report.get("lifecycle_status") or "").strip():
        return False
    if str(saved.get("report_status") or "").strip() != str(trade_report.get("report_status") or "").strip():
        return False
    if str(saved.get("source_signature") or "").strip() != _operator_brief_source_signature(detail):
        return False
    return True


def _load_saved_operator_brief(detail: Dict[str, Any]) -> Dict[str, Any]:
    if _operator_brief_force_regenerate_enabled():
        return {}
    json_path, _ = _operator_brief_artifact_paths(detail)
    if json_path is None or not json_path.exists():
        return {}
    payload = _read_json(json_path)
    if not isinstance(payload, dict):
        return {}
    if int(payload.get("version") or 0) < OPERATOR_BRIEF_ARTIFACT_VERSION:
        return {}
    if not _saved_operator_brief_matches_detail(payload, detail):
        return {}
    return payload


def _sync_trade_health_after_operator_brief_save(
    trade_root: Path,
    *,
    reports_dir: Path,
    brief_payload: Dict[str, Any],
    brief_json_path: Path,
    brief_md_path: Path,
    brief_llm_path: Path,
) -> None:
    health_path = trade_root / "_health.json"
    if not health_path.exists():
        return
    health = _read_json(health_path)
    if not isinstance(health, dict) or not health:
        return

    ai_report_json_path = reports_dir / "ai_trade_report.json"
    ai_report_md_path = reports_dir / "ai_trade_report.md"
    ai_report_payload = _read_json(ai_report_json_path) if ai_report_json_path.exists() else {}
    ai_generation = ai_report_payload.get("generation") if isinstance(ai_report_payload.get("generation"), dict) else {}

    operator_brief_status = canonical_llm_status(
        brief_payload.get("llm_brief_status")
        or (brief_payload.get("generation") or {}).get("status")
        or "fallback",
        default="fallback",
    )
    if ai_report_json_path.exists() or ai_report_md_path.exists():
        llm_trade_report_status = canonical_llm_status(
            ai_report_payload.get("ai_trade_report_status")
            or ai_generation.get("ai_trade_report_status")
            or health.get("llm_trade_report_status")
            or health.get("ai_trade_report_status")
            or "skipped",
            default="skipped",
        )
        report_generation_status = "available"
    else:
        llm_trade_report_status = canonical_llm_status(
            health.get("llm_trade_report_status")
            or health.get("ai_trade_report_status")
            or "skipped",
            default="skipped",
        )
        report_generation_status = str(health.get("report_generation_status") or health.get("report_status") or "missing")

    artifact_presence = dict(health.get("artifact_presence") or {})
    artifact_presence.update(
        {
            "operator_brief_json": brief_json_path.exists(),
            "operator_brief_md": brief_md_path.exists(),
            "brief_llm_response_json": brief_llm_path.exists(),
            "ai_trade_report_json": ai_report_json_path.exists(),
            "ai_trade_report_md": ai_report_md_path.exists(),
        }
    )

    health["artifact_presence"] = artifact_presence
    health["llm_brief_status"] = operator_brief_status
    health["operator_brief_status"] = operator_brief_status
    health["ai_trade_report_status"] = llm_trade_report_status
    health["llm_trade_report_status"] = llm_trade_report_status
    health["report_generation_status"] = report_generation_status
    report_generation = health.get("report_generation") if isinstance(health.get("report_generation"), dict) else {}
    report_generation["status"] = report_generation_status
    health["report_generation"] = report_generation
    health_path.write_text(json.dumps(health, ensure_ascii=False, indent=2), encoding="utf-8")


def _save_operator_brief_artifact(detail: Dict[str, Any], brief: Dict[str, Any]) -> None:
    if not isinstance(brief, dict) or not brief:
        return
    json_path, md_path = _operator_brief_artifact_paths(detail)
    if json_path is None or md_path is None:
        return
    trade_report = detail.get("trade_report") if isinstance(detail.get("trade_report"), dict) else {}
    payload = _normalize_operator_brief_payload(brief, detail)
    sections = payload.get("sections") if isinstance(payload.get("sections"), dict) else {}
    monitor_section = (
        sections.get("position_monitor_reasoning")
        if isinstance(sections.get("position_monitor_reasoning"), dict)
        else {}
    )
    payload["monitor_snapshot"] = {
        "posture": str(monitor_section.get("posture") or ""),
        "holding_time": str(monitor_section.get("holding_time") or ""),
        "stop_loss": str(monitor_section.get("stop_loss") or ""),
        "effective_stop": str(monitor_section.get("effective_stop") or ""),
        "effective_stop_reason": str(monitor_section.get("effective_stop_reason") or ""),
        "take_profit": str(monitor_section.get("take_profit") or ""),
        "current_price": str(monitor_section.get("current_price") or ""),
        "average_price": str(monitor_section.get("average_price") or ""),
        "peak_price": str(monitor_section.get("peak_price") or ""),
        "current_drawdown": str(monitor_section.get("current_drawdown") or ""),
        "peak_drawdown": str(monitor_section.get("peak_drawdown") or ""),
        "vwap_distance": str(monitor_section.get("vwap_distance") or ""),
        "price_source": str(monitor_section.get("price_source") or ""),
        "feature_source": str(monitor_section.get("feature_source") or ""),
        "price_source_policy": str(monitor_section.get("price_source_policy") or ""),
        "active_exit_axis": str(monitor_section.get("active_exit_axis") or ""),
        "watch_axes": [str(x or "") for x in list(monitor_section.get("watch_axes") or []) if str(x or "").strip()][:6],
        "hold_reasons": [str(x or "") for x in list(monitor_section.get("hold_reasons") or []) if str(x or "").strip()][:6],
        "exit_triggers": [str(x or "") for x in list(monitor_section.get("exit_triggers") or []) if str(x or "").strip()][:6],
    }
    payload["version"] = OPERATOR_BRIEF_ARTIFACT_VERSION
    payload["saved_at"] = datetime.now(tz=KST).isoformat()
    payload["run_id"] = str(detail.get("run_id") or "")
    payload["trade_id"] = str(trade_report.get("trade_id") or "")
    payload["story_id"] = str(trade_report.get("story_id") or "")
    payload["lifecycle_status"] = str(trade_report.get("lifecycle_status") or "")
    payload["report_status"] = str(trade_report.get("report_status") or "")
    payload["source_signature"] = _operator_brief_source_signature(detail)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    trade_root = json_path.parent.parent if json_path.parent.name in {"brief", "reports"} else json_path.parent
    brief_llm_path = json_path.parent / "brief_llm_response.json"
    llm_response_artifact = payload.get("llm_response_artifact") if isinstance(payload.get("llm_response_artifact"), dict) else {}
    llm_response_compact: Dict[str, Any] = {}
    if llm_response_artifact:
        reports_root = trade_root.parents[2] if len(trade_root.parents) >= 3 else Path("reports")
        run_day = trade_root.parent.name if re.fullmatch(r"\d{4}-\d{2}-\d{2}", trade_root.parent.name) else str(payload.get("saved_at") or "")[:10]
        llm_response_compact = persist_llm_artifact_refs(
            artifact=llm_response_artifact,
            reports_root=reports_root,
            day=run_day,
            run_id=str(detail.get("run_id") or ""),
            component="brief",
        )
        llm_response_compact["llm_status"] = canonical_llm_status(
            llm_response_compact.get("llm_status") or llm_response_compact.get("status") or "fallback",
            default="fallback",
        )
        brief_llm_path.write_text(json.dumps(llm_response_compact, ensure_ascii=False, indent=2), encoding="utf-8")
    if llm_response_compact:
        payload["llm_response_artifact"] = dict(llm_response_compact)
    payload = _normalize_operator_brief_payload(payload, detail, llm_response_artifact=llm_response_compact)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(_render_operator_brief_markdown(payload), encoding="utf-8")
    _sync_trade_health_after_operator_brief_save(
        trade_root,
        reports_dir=json_path.parent,
        brief_payload=payload,
        brief_json_path=json_path,
        brief_md_path=md_path,
        brief_llm_path=brief_llm_path,
    )
    bundle_candidates = [
        trade_root / "lifecycle_bundle.json",
        trade_root / "aggregated_execution_bundle.json",
        trade_root / "lifecycle" / "aggregated_execution_bundle.json",
    ]
    for bundle_path in bundle_candidates:
        if not bundle_path.exists():
            continue
        bundle = _read_json(bundle_path)
        if not isinstance(bundle, dict) or not bundle:
            continue
        artifacts = bundle.get("artifacts") if isinstance(bundle.get("artifacts"), dict) else {}
        artifacts["brief_json"] = str(json_path)
        artifacts["brief_md"] = str(md_path)
        artifacts["operator_brief_json"] = str(json_path)
        brief_input_path = _operator_brief_input_artifact_path(detail)
        brief_compact_path = _operator_brief_compact_input_artifact_path(detail)
        artifacts["brief_input_json"] = (
            str(brief_input_path)
            if isinstance(brief_input_path, Path) and brief_input_path.exists()
            else ""
        )
        artifacts["brief_compact_input_json"] = (
            str(brief_compact_path)
            if isinstance(brief_compact_path, Path) and brief_compact_path.exists()
            else ""
        )
        artifacts["brief_llm_response_json"] = str(json_path.parent / "brief_llm_response.json") if llm_response_compact else ""
        bundle["artifacts"] = artifacts
        llm_summary = bundle.get("llm_summary") if isinstance(bundle.get("llm_summary"), dict) else {}
        llm_summary["brief_llm_status"] = str(payload.get("llm_brief_status") or "fallback")
        bundle["llm_summary"] = llm_summary
        # Compatibility bridge: nested llm_summary/artifacts remain authoritative.
        # These flat fields stay in sync for older readers that still expect them.
        bundle["brief_llm_status"] = str(payload.get("llm_brief_status") or "fallback")
        bundle["operator_brief"] = str(json_path)
        bundle["lifecycle_bundle"] = str(bundle_path)
        bundle_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
        break


def _load_operator_brief_with_cache(config: OperatorUIConfig, detail: Dict[str, Any]) -> Dict[str, Any]:
    run_id = str(detail.get("run_id") or "").strip()
    saved = _load_saved_operator_brief(detail)
    if saved:
        _save_cached_operator_brief(config, run_id, saved)
        return _attach_operator_brief_sections(saved, detail)
    cached = _load_cached_operator_brief(config, run_id)
    if cached and _saved_operator_brief_matches_detail(cached, detail):
        _save_operator_brief_artifact(detail, _attach_operator_brief_sections(cached, detail))
        return _attach_operator_brief_sections(cached, detail)
    brief = _attach_operator_brief_sections(_load_operator_brief(detail), detail)
    _save_cached_operator_brief(config, run_id, brief)
    _save_operator_brief_artifact(detail, brief)
    return brief


def load_run_detail(config: OperatorUIConfig, run_id: str) -> Dict[str, Any]:
    all_rows = [row for row in _iter_jsonl(config.event_log_path) if str(row.get("run_id") or "").strip() == str(run_id or "").strip()]
    all_rows = sorted(all_rows, key=lambda row: _to_epoch(row.get("ts")) or 0)
    evidence_rows = [row for row in _iter_jsonl(config.evidence_log_path) if str(row.get("run_id") or "").strip() == str(run_id or "").strip()]
    evidence_rows = sorted(evidence_rows, key=lambda row: _to_epoch(row.get("timestamp")) or 0)

    if not all_rows:
        return {"run_id": str(run_id or ""), "found": False}

    route_row = next((r for r in all_rows if str(r.get("stage") or "") == "commander_router" and str(r.get("event") or "") == "route"), {})
    end_row = next((r for r in reversed(all_rows) if str(r.get("stage") or "") == "commander_router" and str(r.get("event") or "") == "end"), {})
    strategist_summary = next((r.get("payload") for r in reversed(all_rows) if str(r.get("stage") or "") == "strategist" and str(r.get("event") or "") == "summary" and isinstance(r.get("payload"), dict)), {})
    strategist_llm = next((r.get("payload") for r in reversed(all_rows) if str(r.get("stage") or "") == "strategist_llm" and str(r.get("event") or "") == "result" and isinstance(r.get("payload"), dict)), {})
    scanner_summary = next((r.get("payload") for r in reversed(all_rows) if str(r.get("stage") or "") == "scanner" and str(r.get("event") or "") == "summary" and isinstance(r.get("payload"), dict)), {})
    monitor_summary = next((r.get("payload") for r in reversed(all_rows) if str(r.get("stage") or "") == "monitor" and str(r.get("event") or "") == "summary" and isinstance(r.get("payload"), dict)), {})
    verdict_payload = next((r.get("payload") for r in reversed(all_rows) if str(r.get("stage") or "") == "execute_from_packet" and str(r.get("event") or "") == "verdict" and isinstance(r.get("payload"), dict)), {})
    execution_payload = next((r.get("payload") for r in reversed(all_rows) if str(r.get("stage") or "") == "execute_from_packet" and str(r.get("event") or "") == "execution" and isinstance(r.get("payload"), dict)), {})
    portfolio_sync = _build_portfolio_sync_card(_extract_portfolio_guard_payload_from_run_rows(all_rows))

    strategic_frame = next(
        (
            (r.get("payload") or {}).get("payload")
            for r in reversed(all_rows)
            if str(r.get("stage") or "") == "decision_trace"
            and str(r.get("event") or "") == "strategic_frame"
            and isinstance(r.get("payload"), dict)
            and str((r.get("payload") or {}).get("agent") or "") == "strategist"
        ),
        {},
    )
    candidate_selection = next(
        (
            (r.get("payload") or {}).get("payload")
            for r in reversed(all_rows)
            if str(r.get("stage") or "") == "decision_trace"
            and str(r.get("event") or "") == "candidate_selection"
            and isinstance(r.get("payload"), dict)
            and str((r.get("payload") or {}).get("agent") or "") == "scanner"
        ),
        {},
    )
    entry_exit_decision = next(
        (
            (r.get("payload") or {}).get("payload")
            for r in reversed(all_rows)
            if str(r.get("stage") or "") == "decision_trace"
            and str(r.get("event") or "") == "entry_exit_decision"
            and isinstance(r.get("payload"), dict)
            and str((r.get("payload") or {}).get("agent") or "") == "monitor"
        ),
        {},
    )
    selected_candidate = candidate_selection.get("selected_candidate") if isinstance(candidate_selection.get("selected_candidate"), dict) else {}
    feature_snapshot = selected_candidate.get("feature_snapshot") if isinstance(selected_candidate.get("feature_snapshot"), dict) else {}
    feature_coverage = _feature_coverage(feature_snapshot)
    quote_metrics = _quote_metrics_snapshot(feature_snapshot)

    strategist_evidence = _latest_evidence(evidence_rows, agent="strategist", stage="theme_selection")
    reporter_evidence = _latest_evidence(evidence_rows, agent="reporter", stage="post_run_analysis")
    first_dt = _to_datetime(all_rows[0].get("ts"))
    run_day = first_dt.strftime("%Y-%m-%d") if first_dt else ""
    canonical_sources = load_run_canonical_sources(config.reports_root, str(run_id or ""), run_day)
    commander_summary, commander_provenance = prefer_canonical_agent_payload(
        canonical_sources,
        "commander",
        {
            "mode": str((route_row.get("payload") or {}).get("mode") or ""),
            "phase": str((route_row.get("payload") or {}).get("phase") or ""),
            "status": str((end_row.get("payload") or {}).get("status") or ""),
            "path": str((end_row.get("payload") or {}).get("path") or ""),
        },
        fallback_source="event_log",
    )
    strategist_summary, strategist_provenance = prefer_canonical_agent_payload(
        canonical_sources,
        "strategist",
        strategist_summary if isinstance(strategist_summary, dict) else {},
        fallback_source="event_log",
    )
    scanner_summary, scanner_provenance = prefer_canonical_agent_payload(
        canonical_sources,
        "scanner",
        scanner_summary if isinstance(scanner_summary, dict) else {},
        fallback_source="event_log",
    )
    monitor_summary, monitor_provenance = prefer_canonical_agent_payload(
        canonical_sources,
        "monitor",
        monitor_summary if isinstance(monitor_summary, dict) else {},
        fallback_source="event_log",
    )
    verdict_payload, supervisor_provenance = prefer_canonical_agent_payload(
        canonical_sources,
        "supervisor",
        verdict_payload if isinstance(verdict_payload, dict) else {},
        fallback_source="event_log",
    )
    execution_payload, executor_provenance = prefer_canonical_agent_payload(
        canonical_sources,
        "executor",
        execution_payload if isinstance(execution_payload, dict) else {},
        fallback_source="event_log",
    )
    normalized_execution = _normalize_execution_payload(execution_payload if isinstance(execution_payload, dict) else {})
    if not strategist_llm and isinstance(strategist_summary.get("llm_metadata_summary"), dict):
        strategist_llm = dict(strategist_summary.get("llm_metadata_summary") or {})
    if not isinstance(strategic_frame, dict) or not strategic_frame:
        strategic_frame = dict(strategist_summary or {})
    if (not isinstance(candidate_selection, dict) or not candidate_selection) and isinstance(scanner_summary.get("selected_candidate"), dict):
        candidate_selection = {
            "selected_symbol": scanner_summary.get("selected_symbol") or scanner_summary.get("top_stock"),
            "candidate_pool_size": scanner_summary.get("candidate_pool_after_filter") or scanner_summary.get("universe_size"),
            "selected_candidate": dict(scanner_summary.get("selected_candidate") or {}),
        }
    elif scanner_provenance == "canonical":
        candidate_selection = dict(candidate_selection or {})
        selected_candidate = (
            candidate_selection.get("selected_candidate")
            if isinstance(candidate_selection.get("selected_candidate"), dict)
            else {}
        )
        merged_selected_candidate = dict(selected_candidate or {})
        merged_selected_candidate.update(
            dict(scanner_summary.get("selected_candidate") or {})
            if isinstance(scanner_summary.get("selected_candidate"), dict)
            else {}
        )
        candidate_selection["selected_symbol"] = (
            scanner_summary.get("selected_symbol")
            or scanner_summary.get("top_stock")
            or candidate_selection.get("selected_symbol")
        )
        candidate_selection["candidate_pool_size"] = (
            scanner_summary.get("candidate_pool_after_filter")
            or scanner_summary.get("universe_size")
            or candidate_selection.get("candidate_pool_size")
        )
        candidate_selection["selected_candidate"] = merged_selected_candidate
    if not isinstance(entry_exit_decision, dict) or not entry_exit_decision:
        entry_exit_decision = dict(monitor_summary or {})
    elif monitor_provenance == "canonical":
        entry_exit_decision = {**dict(entry_exit_decision or {}), **dict(monitor_summary or {})}
    primary_symbol = normalize_symbol(
        normalized_execution.get("symbol")
        or scanner_summary.get("top_stock")
        or candidate_selection.get("selected_symbol")
        or "",
        allow_test_symbols=True,
    ).strip()
    same_day_symbol_trades = []
    if primary_symbol:
        same_day_symbol_trades = [
            trade
            for trade in load_recent_trades_for_day(config, run_day, limit=500)
            if str(trade.get("symbol") or "").strip() == primary_symbol
        ]
    same_day_symbol_run_chain = load_symbol_run_chain(config, run_day, primary_symbol, limit=3) if primary_symbol else []
    trade_report_meta = _trade_report_meta_for_run(config, str(run_id or ""))
    if trade_report_meta:
        report_payloads = load_trade_report_payloads(trade_report_meta, read_json=_read_json)
        trade_report_card = _read_model_build_linked_trade_report_card(
            trade_report_meta,
            report_payloads,
            primary_symbol=primary_symbol,
            execution_action=str(normalized_execution.get("action") or ""),
            normalize_ai_report_diagnostics=_normalize_ai_report_diagnostics,
        )
    else:
        trade_report_card = _read_model_build_unlinked_trade_report_card(
            execution_action=str(normalized_execution.get("action") or ""),
            monitor_reason_text=str(monitor_summary.get("monitor_reason") or entry_exit_decision.get("monitor_reason") or ""),
            symbol=primary_symbol or str(normalized_execution.get("symbol") or scanner_summary.get("top_stock") or ""),
            normalize_ai_report_diagnostics=_normalize_ai_report_diagnostics,
            report_reason_human=_report_reason_human,
            report_next_step=_report_next_step,
        )

    detail = {
        "found": True,
        "run_id": str(run_id or ""),
        "started_at": _iso_to_display(route_row.get("ts")),
        "completed_at": _iso_to_display(end_row.get("ts")),
        "commander": {
            "mode": str(commander_summary.get("mode") or commander_summary.get("command") or (route_row.get("payload") or {}).get("mode") or ""),
            "phase": str(commander_summary.get("phase") or ((commander_summary.get("blocked_allowed_details") or {}) if isinstance(commander_summary.get("blocked_allowed_details"), dict) else {}).get("phase") or (route_row.get("payload") or {}).get("phase") or ""),
            "agents": list(commander_summary.get("invoked_agents") or (route_row.get("payload") or {}).get("agents") or []),
            "status": str(commander_summary.get("status") or (end_row.get("payload") or {}).get("status") or ""),
            "path": str(commander_summary.get("path") or commander_summary.get("decision") or (end_row.get("payload") or {}).get("path") or ""),
            "reason": str(commander_summary.get("reason") or ""),
            "provenance": commander_provenance,
            "artifact": commander_summary if isinstance(commander_summary, dict) else {},
        },
        "strategist": {
            "summary": strategist_summary,
            "llm": strategist_llm,
            "decision_trace": strategic_frame if isinstance(strategic_frame, dict) else {},
            "provenance": strategist_provenance,
            "evidence": {
                "raw_input": strategist_evidence.get("raw_input") if isinstance(strategist_evidence.get("raw_input"), dict) else {},
                "llm_prompt": str(strategist_evidence.get("llm_prompt") or ""),
                "llm_response": str(strategist_evidence.get("llm_response") or ""),
                "parsed_output": strategist_evidence.get("parsed_output") if isinstance(strategist_evidence.get("parsed_output"), dict) else {},
            },
        },
        "scanner": {
            "summary": scanner_summary,
            "decision_trace": candidate_selection if isinstance(candidate_selection, dict) else {},
            "feature_coverage": feature_coverage,
            "quote_metrics": quote_metrics,
            "provenance": scanner_provenance,
        },
        "monitor": {
            "summary": monitor_summary,
            "decision_trace": entry_exit_decision if isinstance(entry_exit_decision, dict) else {},
            "provenance": monitor_provenance,
        },
        "supervisor": {
            "verdict": verdict_payload,
            "provenance": supervisor_provenance,
        },
        "executor": {
            "execution": execution_payload,
            "provenance": executor_provenance,
        },
        "portfolio_sync": portfolio_sync,
        "same_day_symbol_trade_history": {
            "day": run_day,
            "symbol": primary_symbol,
            "trade_count": len(same_day_symbol_trades),
            "trades": same_day_symbol_trades[:20],
        },
        "same_day_symbol_run_chain": {
            "day": run_day,
            "symbol": primary_symbol,
            "run_count": len(same_day_symbol_run_chain),
            "runs": same_day_symbol_run_chain,
        },
        "trade_report": trade_report_card,
        "reporter": _reporter_snippet_for_run(config, str(run_id or ""), run_day),
        "canonical_sources": canonical_sources,
        "artifact_provenance": {
            "commander": commander_provenance,
            "strategist": strategist_provenance,
            "scanner": scanner_provenance,
            "monitor": monitor_provenance,
            "supervisor": supervisor_provenance,
            "executor": executor_provenance,
            "reporter": "direct_artifact",
        },
        "raw_event_count": len(all_rows),
        "stage_counts": _count_stages(all_rows),
        "event_preview": [
            {
                "ts": _iso_to_display(row.get("ts")),
                "stage": str(row.get("stage") or ""),
                "event": str(row.get("event") or ""),
                "payload": _truncate_json(row.get("payload")),
            }
            for row in all_rows[:120]
        ],
    }
    detail["operator_brief"] = _load_operator_brief_with_cache(config, detail)
    trade_report = detail.get("trade_report") if isinstance(detail.get("trade_report"), dict) else {}
    if trade_report:
        brief_json_path, brief_md_path = _operator_brief_artifact_paths(detail)
        trade_report["operator_brief_json_path"] = (
            str(brief_json_path) if brief_json_path is not None and brief_json_path.exists() else ""
        )
        trade_report["operator_brief_md_path"] = (
            str(brief_md_path) if brief_md_path is not None and brief_md_path.exists() else ""
        )
    return detail


def load_strategy_memory_timeline(config: OperatorUIConfig, *, limit: int = 7) -> List[Dict[str, Any]]:
    root = config.strategy_memory_path
    if not root.exists():
        return []
    files = sorted(root.glob("*.json"), reverse=True)[: max(1, int(limit))]
    out: List[Dict[str, Any]] = []
    for path in files:
        obj = _read_json(path)
        latest = obj.get("latest_feedback") if isinstance(obj.get("latest_feedback"), dict) else {}
        out.append(
            {
                "day": str(obj.get("day") or path.stem),
                "updated_at": str(obj.get("updated_at") or ""),
                "latest_run_id": str(obj.get("latest_run_id") or ""),
                "trade_count": _safe_int((latest.get("trade_summary") or {}).get("trade_count"), 0) if isinstance(latest.get("trade_summary"), dict) else 0,
                "monitor_status": str((latest.get("monitor_evaluation") or {}).get("monitor_status") or "") if isinstance(latest.get("monitor_evaluation"), dict) else "",
                "theme_alignment_status": str((latest.get("strategist_evaluation") or {}).get("theme_alignment_status") or "") if isinstance(latest.get("strategist_evaluation"), dict) else "",
                "ai_findings": list(latest.get("ai_findings") or [])[:2],
                "path": str(path),
            }
        )
    return out


def _count_stages(rows: List[Dict[str, Any]]) -> Dict[str, int]:
    return _count_stages_r3_impl(rows, facade=_r3_sys.modules[__name__])


def load_health(config: OperatorUIConfig) -> Dict[str, Any]:
    return load_health_r3_impl(config, facade=_r3_sys.modules[__name__])

