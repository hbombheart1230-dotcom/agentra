from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

from libs.reporting.llm_artifacts import (
    build_compact_input_artifact,
    trade_artifact_paths,
    write_json,
)
from libs.reporting.trade_report_ai import build_ai_trade_report_compact_input
from libs.reporting.trade_report_runtime_generation import (
    apply_ai_trade_report_generation_result,
    apply_runtime_diagnostics_context,
    build_live_generation_state_payload,
    execute_ai_trade_report_generation,
    load_report_generation_state,
    plan_live_trade_report_generation,
    report_generation_state_path,
    write_report_generation_state,
)
from libs.reporting.trade_report_runtime_policy import (
    base_report_diagnostics,
    report_next_step,
    report_reason_human,
    resolve_trade_report_policy,
    seed_diagnostics_for_policy,
)
from libs.reporting.monitor_timeline_reconciliation import apply_latest_exit_monitor_context_from_timeline
from libs.reporting.trade_regeneration_truth import rehydrate_lifecycle_bundle_execution_truth
from libs.reporting.trade_story_pipeline import build_trade_story_input_from_bundle, render_bundle_markdown
from libs.runtime.windows_subprocess import background_creationflags, popen_hidden, run_hidden
import sys as _r3_sys
from libs.reporting import intraday_report_read_projection as _read_owner
from libs.reporting import intraday_report_linkage_projection as _linkage_owner
from libs.reporting import intraday_report_quality_projection as _quality_owner
from libs.reporting import intraday_report_payload_projection as _payload_owner
from libs.reporting import intraday_report_diagnostics_projection as _diagnostics_owner
from libs.agents.reporter.read_models.intraday_trade_reports_r9_bodies_01 import (  # R-4 owner bodies (facade-injected)
    _trade_day_from_trade_id_r4_impl,
    _runtime_trade_day_r4_impl,
    _safe_float_r4_impl,
    _to_epoch_r4_impl,
    _null_if_empty_r4_impl,
    normalize_trade_id_filters_r4_impl,
    build_hold_signal_transitions_r4_impl,
    build_holding_phase_observability_r4_impl,
    _execution_truth_surface_r4_impl,
    _apply_ai_report_diagnostics_summary_r4_impl,
    _creation_epoch_from_wmi_r4_impl,
    _cache_run_ids_r4_impl,
)


def _is_trueish(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def _normalize_symbol(value: Any) -> str:
    return str(value or "").strip().upper()


def _trade_day_from_trade_id(trade_id: str) -> str:
    return _trade_day_from_trade_id_r4_impl(trade_id, facade=_r3_sys.modules[__name__])


def _runtime_trade_day(state: Dict[str, Any]) -> str:
    return _runtime_trade_day_r4_impl(state, facade=_r3_sys.modules[__name__])


def _root_dir() -> Path:
    return Path(__file__).resolve().parents[2]


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _bundle_role() -> str:
    return "intraday_trade_report_bundle"


def _script_path(root: Path) -> Path:
    return root / "scripts" / "run_live_execution_bundle_report.py"


def _runner_module_name() -> str:
    return "libs.reporting.live_execution_bundle_runner"


def _brief_cache_dir(root: Path) -> Path:
    return Path(
        os.getenv("OPERATOR_UI_CACHE_PATH", str(root / "data" / "operator_ui" / "brief_cache"))
    )


def _bundle_job_lock_path(root: Path) -> Path:
    return root / "reports" / "runtime" / "intraday_trade_report_bundle.lock"


def _bundle_job_queue_path(root: Path) -> Path:
    return root / "reports" / "runtime" / "intraday_trade_report_bundle.queue.json"


def _read_lock_payload(path: Path) -> Dict[str, Any]:
    try:
        if not path.exists():
            return {}
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _read_json(path: Path) -> Dict[str, Any]:
    return _read_owner._read_json(path, facade=_r3_sys.modules[__name__])


def _stable_json_text(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _payload_fingerprint(payload: Any) -> str:
    return hashlib.sha256(_stable_json_text(payload).encode("utf-8")).hexdigest()


def _safe_float(value: Any, default: Optional[float] = 0.0) -> Optional[float]:
    return _safe_float_r4_impl(value, default, facade=_r3_sys.modules[__name__])


def _to_epoch(ts: Any) -> Optional[int]:
    return _to_epoch_r4_impl(ts, facade=_r3_sys.modules[__name__])


def _null_if_empty(value: Any) -> Any:
    return _null_if_empty_r4_impl(value, facade=_r3_sys.modules[__name__])


def normalize_trade_id_filters(values: Any) -> List[str]:
    return normalize_trade_id_filters_r4_impl(values, facade=_r3_sys.modules[__name__])


def build_hold_signal_transitions(monitor_context_snapshots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return build_hold_signal_transitions_r4_impl(monitor_context_snapshots, facade=_r3_sys.modules[__name__])


def build_holding_phase_observability(
    lifecycle: Dict[str, Any],
    *,
    monitor_timeline: Dict[str, Any],
) -> Dict[str, Any]:
    return build_holding_phase_observability_r4_impl(lifecycle, monitor_timeline=monitor_timeline, facade=_r3_sys.modules[__name__])


def build_same_day_reporter_linkage(
    *,
    reporter_obj: Dict[str, Any],
    reporter_js: Path,
    reporter_md: Path,
    entry_run_id: str,
    exit_run_id: str,
    entry_bundle: Dict[str, Any],
    exit_bundle: Dict[str, Any],
) -> Dict[str, Any]:
    return _linkage_owner.build_same_day_reporter_linkage(reporter_obj=reporter_obj, reporter_js=reporter_js, reporter_md=reporter_md, entry_run_id=entry_run_id, exit_run_id=exit_run_id, entry_bundle=entry_bundle, exit_bundle=exit_bundle, facade=_r3_sys.modules[__name__])


def _load_story_input(trade_dir: Path) -> tuple[Dict[str, Any], str]:
    return _read_owner._load_story_input(trade_dir, facade=_r3_sys.modules[__name__])


def _story_input_quality_score(story_input: Dict[str, Any]) -> int:
    return _quality_owner._story_input_quality_score(story_input, facade=_r3_sys.modules[__name__])


def _execution_truth_surface(details: Any) -> Dict[str, Any]:
    return _execution_truth_surface_r4_impl(details, facade=_r3_sys.modules[__name__])


def _truth_surface_differs(existing_story_input: Dict[str, Any], rebuilt_story_input: Dict[str, Any]) -> bool:
    return _quality_owner._truth_surface_differs(existing_story_input, rebuilt_story_input, facade=_r3_sys.modules[__name__])


def resolve_story_input_for_regeneration(
    trade_dir: Path,
    trade_paths: Dict[str, Path],
) -> tuple[Dict[str, Any], str, str, int, int]:
    existing_story_input, existing_path = _load_story_input(trade_dir)
    existing_score = _story_input_quality_score(existing_story_input)
    lifecycle_bundle = _read_json(trade_paths["lifecycle_bundle_json"])
    if not lifecycle_bundle:
        return existing_story_input, existing_path, "existing_story_input", existing_score, existing_score

    enriched_lifecycle_bundle = rehydrate_lifecycle_bundle_execution_truth(lifecycle_bundle)
    monitor_timeline = _read_json(trade_paths["monitor_evidence_json"])
    if monitor_timeline:
        enriched_lifecycle_bundle = apply_latest_exit_monitor_context_from_timeline(
            enriched_lifecycle_bundle,
            monitor_timeline,
        )
        enriched_lifecycle_bundle["monitor_evidence"] = monitor_timeline
    scanner_evidence = _read_json(trade_paths["scanner_evidence_json"])
    if scanner_evidence:
        enriched_lifecycle_bundle["scanner_evidence"] = scanner_evidence
    if _payload_fingerprint(enriched_lifecycle_bundle) != _payload_fingerprint(lifecycle_bundle):
        write_json(trade_paths["lifecycle_bundle_json"], enriched_lifecycle_bundle)
        lifecycle_bundle = enriched_lifecycle_bundle

    rebuilt_story_input = build_trade_story_input_from_bundle(
        lifecycle_bundle,
        existing_story_input=existing_story_input,
    )
    rebuilt_score = _story_input_quality_score(rebuilt_story_input)
    if rebuilt_story_input and (_truth_surface_differs(existing_story_input, rebuilt_story_input) or rebuilt_score >= existing_score):
        canonical_path = trade_paths["ai_trade_report_input_json"]
        if _payload_fingerprint(rebuilt_story_input) != _payload_fingerprint(existing_story_input):
            write_json(canonical_path, rebuilt_story_input)
        return (
            rebuilt_story_input,
            str(canonical_path),
            "rebuilt_from_lifecycle_bundle",
            existing_score,
            rebuilt_score,
        )
    return existing_story_input, existing_path, "existing_story_input", existing_score, rebuilt_score


def sync_ai_trade_report_generation_state(
    trade_paths: Dict[str, Path],
    *,
    story_input: Dict[str, Any],
    compact_input: Dict[str, Any],
    report: Dict[str, Any],
    llm_artifact: Dict[str, Any],
    llm_response_path: str,
) -> Dict[str, Any]:
    generation = report.get("generation") if isinstance(report.get("generation"), dict) else {}
    state_path = report_generation_state_path(trade_paths)
    state_payload = load_report_generation_state(state_path)
    components = state_payload.get("components") if isinstance(state_payload.get("components"), dict) else {}
    generation_mode = str(generation.get("mode") or "").strip().lower()
    declared_ai_status = str(
        report.get("ai_trade_report_status")
        or generation.get("ai_trade_report_status")
        or ""
    ).strip()
    generation_status = str(
        declared_ai_status
        if generation_mode in {"deterministic", "local_debug"} and declared_ai_status
        else generation.get("status")
        or report.get("ai_trade_report_status")
        or report.get("status")
        or llm_artifact.get("status")
        or ""
    ).strip()
    model = str(
        generation.get("model")
        or llm_artifact.get("model")
        or ((llm_artifact.get("model_info") or {}) if isinstance(llm_artifact.get("model_info"), dict) else {}).get("model")
        or ""
    )
    source_inputs = {
        "story_input_sha256": _payload_fingerprint(story_input),
        "compact_input_sha256": _payload_fingerprint(compact_input),
    }
    components["ai_trade_report"] = {
        "fingerprint": _payload_fingerprint(
            {
                "component": "ai_trade_report",
                "trade_id": str(story_input.get("trade_id") or ""),
                "run_id": str(story_input.get("run_id") or ""),
                **source_inputs,
            }
        ),
        "component": "ai_trade_report",
        "status": generation_status,
        "report_status": "available" if trade_paths["ai_trade_report_json"].exists() else "missing",
        "skip_reason": "deterministic_no_llm" if generation_status == "skipped" and generation_mode == "deterministic" else "",
        "trade_id": str(story_input.get("trade_id") or ""),
        "run_id": str(story_input.get("run_id") or ""),
        "updated_at": _utc_now_iso(),
        "model": model,
        "report_json_path": str(trade_paths["ai_trade_report_json"]),
        "report_md_path": str(trade_paths["ai_trade_report_md"]),
        "llm_response_path": str(llm_response_path or ""),
        "source_inputs": source_inputs,
    }
    state_payload["components"] = components
    write_report_generation_state(state_path, state_payload)
    return state_payload


def build_live_bundle_backfill_payload(
    *,
    trade_id: str,
    status: str,
    story_type: str,
    execution_mode_label: str,
    symbol: str,
    entry_run_id: str,
    hold_run_ids: List[str],
    exit_run_id: str,
    linked_run_ids: List[str],
    lifecycle_summary: str,
    lifecycle_bundle_path: Path,
    story_input_path: Path,
    story_compact_input_path: Path,
    trade_report_json_written: str,
    trade_report_md_written: str,
    strategist_llm_response_path: Path,
    ai_trade_report_llm_response_written: str,
    entry_artifact_path: Path,
    hold_artifact_path: Path,
    exit_artifact_path: Path,
    strategist_evidence_path: Path,
    scanner_evidence_path: Path,
    monitor_evidence_path: Path,
    commander_evidence_path: Path,
    trade_provenance_path: Path,
    trade_health_path: Path,
    trade_artifact_links_path: Path,
    trade_root: Path,
    trade_report_summary: str,
    diagnostics: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    return _payload_owner.build_live_bundle_backfill_payload(trade_id=trade_id, status=status, story_type=story_type, execution_mode_label=execution_mode_label, symbol=symbol, entry_run_id=entry_run_id, hold_run_ids=hold_run_ids, exit_run_id=exit_run_id, linked_run_ids=linked_run_ids, lifecycle_summary=lifecycle_summary, lifecycle_bundle_path=lifecycle_bundle_path, story_input_path=story_input_path, story_compact_input_path=story_compact_input_path, trade_report_json_written=trade_report_json_written, trade_report_md_written=trade_report_md_written, strategist_llm_response_path=strategist_llm_response_path, ai_trade_report_llm_response_written=ai_trade_report_llm_response_written, entry_artifact_path=entry_artifact_path, hold_artifact_path=hold_artifact_path, exit_artifact_path=exit_artifact_path, strategist_evidence_path=strategist_evidence_path, scanner_evidence_path=scanner_evidence_path, monitor_evidence_path=monitor_evidence_path, commander_evidence_path=commander_evidence_path, trade_provenance_path=trade_provenance_path, trade_health_path=trade_health_path, trade_artifact_links_path=trade_artifact_links_path, trade_root=trade_root, trade_report_summary=trade_report_summary, diagnostics=diagnostics, facade=_r3_sys.modules[__name__])


def persist_live_story_input_artifacts(
    *,
    day: str,
    trade_id: str,
    anchor_run_id: str,
    status: str,
    should_attempt_generation: bool,
    trade_story_input: Mapping[str, Any] | None,
    trade_story_compact_input: Mapping[str, Any] | None,
    existing_trade_report_artifact: Mapping[str, Any] | None,
    existing_story_input_artifact: Mapping[str, Any] | None,
    story_input_path: Path,
    story_compact_input_path: Path,
    diagnostics: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    diagnostics_out = dict(diagnostics or {})
    story_input_to_persist = dict(trade_story_input or {})
    existing_report_obj = dict(existing_trade_report_artifact or {})
    existing_story_obj = dict(existing_story_input_artifact or {})
    preserved_closed_story_input = False

    current_status_lower = str(status or "").strip().lower()
    existing_report_status_lower = str(existing_report_obj.get("status") or "").strip().lower()
    existing_story_status_lower = str(existing_story_obj.get("status") or "").strip().lower()

    if (
        current_status_lower == "open"
        and not should_attempt_generation
        and existing_report_status_lower == "closed"
    ):
        if existing_story_status_lower == "closed":
            story_input_to_persist = dict(existing_story_obj)
            preserved_closed_story_input = True
            diagnostics_out["story_input_persist_strategy"] = "preserve_existing_closed_snapshot"
        else:
            repaired_story_input = dict(trade_story_input or {})
            repaired_story_input["status"] = "closed"
            report_action = str(existing_report_obj.get("action") or "").strip().upper()
            report_run_id = str(existing_report_obj.get("run_id") or "").strip()
            if report_action in {"BUY", "SELL", "EXIT", "WAIT", "HOLD"}:
                repaired_story_input["action"] = report_action
            if report_run_id:
                repaired_story_input["run_id"] = report_run_id
            repaired_shared_facts = (
                repaired_story_input.get("shared_facts")
                if isinstance(repaired_story_input.get("shared_facts"), dict)
                else {}
            )
            repaired_shared_facts["status"] = "closed"
            if report_action in {"BUY", "SELL", "EXIT", "WAIT", "HOLD"}:
                repaired_shared_facts["action"] = report_action
                resolved_trade_facts = (
                    repaired_shared_facts.get("resolved_trade_facts")
                    if isinstance(repaired_shared_facts.get("resolved_trade_facts"), dict)
                    else {}
                )
                resolved_trade_facts["status"] = "closed"
                resolved_trade_facts["action"] = report_action
                repaired_shared_facts["resolved_trade_facts"] = resolved_trade_facts
            repaired_story_input["shared_facts"] = repaired_shared_facts
            story_input_to_persist = repaired_story_input
            diagnostics_out["story_input_persist_strategy"] = "repair_closed_snapshot_from_existing_report"
    else:
        diagnostics_out["story_input_persist_strategy"] = "persist_current_runtime_snapshot"

    trade_story_compact_input_to_persist = (
        build_ai_trade_report_compact_input(story_input_to_persist)
        if preserved_closed_story_input
        else dict(trade_story_compact_input or {})
    )

    write_json(story_input_path, story_input_to_persist)
    trade_story_compact_artifact = build_compact_input_artifact(
        component="ai_trade_report",
        run_id=str(anchor_run_id or ""),
        trade_id=trade_id,
        story_id=trade_id,
        day=day,
        source_artifact_path=str(story_input_path),
        source_input=story_input_to_persist,
        compact_input=trade_story_compact_input_to_persist,
    )
    write_json(story_compact_input_path, trade_story_compact_artifact)
    return {
        "story_input_to_persist": story_input_to_persist,
        "trade_story_compact_artifact": trade_story_compact_artifact,
        "trade_story_compact_input_to_persist": trade_story_compact_input_to_persist,
        "preserved_closed_story_input": preserved_closed_story_input,
        "diagnostics": diagnostics_out,
    }


def apply_live_bundle_backfill(
    *,
    linked_run_ids: Iterable[str],
    run_bundle_lookup: Mapping[str, Any] | None,
    run_bundles_by_run: Mapping[str, Any] | None,
    backfill_payload: Mapping[str, Any] | None,
    trade_id: str,
    diagnostics: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    row_patch = dict((backfill_payload or {}).get("run_bundle_row_patch") or {})
    bundle_patch = dict((backfill_payload or {}).get("bundle_artifacts_patch") or {})
    diagnostics_obj = dict(diagnostics or {})
    updated_run_ids: List[str] = []
    rewritten_json_paths: List[str] = []
    rewritten_md_paths: List[str] = []

    for rid in [str(x or "").strip() for x in list(linked_run_ids or []) if str(x or "").strip()]:
        row = (run_bundle_lookup or {}).get(rid)
        if isinstance(row, dict):
            row.update(dict(row_patch))
        bundle = (run_bundles_by_run or {}).get(rid)
        if not isinstance(bundle, dict):
            continue
        bundle["trade_id"] = trade_id
        bundle["story_id"] = trade_id
        bundle["ai_report_diagnostics"] = dict(diagnostics_obj)
        bundle.setdefault("artifacts", {})
        bundle["artifacts"].update(dict(bundle_patch))
        report_json_path = Path(str(bundle.get("report_json_path") or ""))
        if report_json_path.exists():
            report_json_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
            rewritten_json_paths.append(str(report_json_path))
        report_md_path = Path(str(bundle.get("report_md_path") or ""))
        if report_md_path.exists():
            report_md_path.write_text(render_bundle_markdown(bundle), encoding="utf-8")
            rewritten_md_paths.append(str(report_md_path))
        updated_run_ids.append(rid)

    return {
        "updated_run_ids": updated_run_ids,
        "rewritten_json_paths": rewritten_json_paths,
        "rewritten_md_paths": rewritten_md_paths,
    }


def build_live_execution_summary_payload(
    *,
    day: str,
    role: str,
    event_log_path: Path,
    evidence_log_path: Path,
    lifecycle_rows: List[Dict[str, Any]],
    run_bundle_rows: List[Dict[str, Any]],
    lifecycle_story_type_counts: Mapping[str, Any] | None,
    run_story_type_counts: Mapping[str, Any] | None,
    target_ctx: Mapping[str, Any] | None,
    canonical_trades_root: Path,
    trade_js: Path,
    trade_md: Path,
    reporter_js: Path,
    reporter_md: Path,
    operator_summary_json: Path,
    operator_summary_md: Path,
) -> Dict[str, Any]:
    return _payload_owner.build_live_execution_summary_payload(day=day, role=role, event_log_path=event_log_path, evidence_log_path=evidence_log_path, lifecycle_rows=lifecycle_rows, run_bundle_rows=run_bundle_rows, lifecycle_story_type_counts=lifecycle_story_type_counts, run_story_type_counts=run_story_type_counts, target_ctx=target_ctx, canonical_trades_root=canonical_trades_root, trade_js=trade_js, trade_md=trade_md, reporter_js=reporter_js, reporter_md=reporter_md, operator_summary_json=operator_summary_json, operator_summary_md=operator_summary_md, facade=_r3_sys.modules[__name__])


def _report_diagnostics_from_report(report: Dict[str, Any], llm_artifact: Dict[str, Any]) -> Dict[str, Any]:
    return _diagnostics_owner._report_diagnostics_from_report(report, llm_artifact, facade=_r3_sys.modules[__name__])


def _apply_ai_report_diagnostics_summary(payload: Dict[str, Any], diagnostics: Dict[str, Any]) -> Dict[str, Any]:
    return _apply_ai_report_diagnostics_summary_r4_impl(payload, diagnostics, facade=_r3_sys.modules[__name__])


def sync_ai_report_diagnostics(
    trade_paths: Dict[str, Path],
    report: Dict[str, Any],
    llm_artifact: Dict[str, Any],
) -> Dict[str, Any]:
    diagnostics = _report_diagnostics_from_report(report, llm_artifact)
    report["ai_report_diagnostics"] = dict(diagnostics)
    report.update(_apply_ai_report_diagnostics_summary(report, diagnostics))

    for path in (
        trade_paths["lifecycle_bundle_json"],
        trade_paths["ai_trade_report_input_json"],
        trade_paths["trade_health_json"],
    ):
        payload = _read_json(path)
        if not payload:
            continue
        payload["ai_report_diagnostics"] = dict(diagnostics)
        payload = _apply_ai_report_diagnostics_summary(payload, diagnostics)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return diagnostics


def finalize_ai_report_diagnostics(
    trade_paths: Dict[str, Path],
    report_json_path: Path,
    diagnostics: Dict[str, Any],
) -> None:
    for path in (
        report_json_path,
        trade_paths["lifecycle_bundle_json"],
        trade_paths["ai_trade_report_input_json"],
        trade_paths["trade_health_json"],
    ):
        payload = _read_json(path)
        if not payload:
            continue
        payload["ai_report_diagnostics"] = dict(diagnostics)
        payload = _apply_ai_report_diagnostics_summary(payload, diagnostics)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_bundle_queue(path: Path) -> List[Dict[str, Any]]:
    try:
        if not path.exists():
            return []
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            return []
        return [dict(row) for row in payload if isinstance(row, dict)]
    except Exception:
        return []


def _write_bundle_queue(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def _enqueue_bundle_request(
    root: Path,
    *,
    run_id: str,
    symbol: str,
    reason: str,
) -> Dict[str, Any]:
    queue_path = _bundle_job_queue_path(root)
    rows = _load_bundle_queue(queue_path)
    normalized_run_id = str(run_id or "").strip()
    normalized_symbol = _normalize_symbol(symbol)
    for row in rows:
        if (
            str(row.get("target_run_id") or "").strip() == normalized_run_id
            and _normalize_symbol(row.get("target_symbol")) == normalized_symbol
        ):
            row["last_seen_at"] = _utc_iso()
            row["reason"] = str(reason or row.get("reason") or "")
            _write_bundle_queue(queue_path, rows)
            out = dict(row)
            out["queue_path"] = str(queue_path)
            out["queue_length"] = len(rows)
            out["deduped"] = True
            return out
    entry = {
        "target_run_id": normalized_run_id,
        "target_symbol": normalized_symbol,
        "role": _bundle_role(),
        "reason": str(reason or ""),
        "enqueued_at": _utc_iso(),
        "last_seen_at": _utc_iso(),
    }
    rows.append(entry)
    _write_bundle_queue(queue_path, rows)
    out = dict(entry)
    out["queue_path"] = str(queue_path)
    out["queue_length"] = len(rows)
    out["deduped"] = False
    return out


def _pid_active(pid: int) -> bool:
    if int(pid or 0) <= 0:
        return False
    if os.name == "nt":
        try:
            import ctypes

            process_query_limited_information = 0x1000
            handle = ctypes.windll.kernel32.OpenProcess(  # type: ignore[attr-defined]
                process_query_limited_information,
                False,
                int(pid),
            )
            if handle:
                ctypes.windll.kernel32.CloseHandle(handle)  # type: ignore[attr-defined]
                return True
            return False
        except Exception:
            return False
    try:
        os.kill(int(pid), 0)
        return True
    except PermissionError:
        return True
    except OSError:
        return False


def _active_bundle_job(path: Path, *, stale_after_sec: float = 900.0) -> Dict[str, Any]:
    payload = _read_lock_payload(path)
    if not payload:
        return {}
    pid = int(payload.get("pid") or 0)
    touched_at = float(
        payload.get("touched_at_epoch")
        or payload.get("heartbeat_epoch")
        or payload.get("started_at_epoch")
        or 0.0
    )
    age_sec = max(0.0, float(time.time()) - touched_at) if touched_at > 0 else stale_after_sec + 1.0
    active = _pid_active(pid)
    if active and age_sec <= stale_after_sec:
        out = dict(payload)
        out["lock_path"] = str(path)
        out["age_sec"] = age_sec
        return out
    if age_sec > stale_after_sec or not active:
        with contextlib.suppress(Exception):
            path.unlink()
    return {}


def _active_bundle_process(root: Path) -> Dict[str, Any]:
    script_path = str(_script_path(root)).lower()
    runner_module = _runner_module_name().lower()
    current_pid = int(os.getpid())
    try:
        if os.name == "nt":
            probe = (
                "Get-CimInstance Win32_Process | "
                "Where-Object { $_.Name -eq 'python.exe' -and ($_.CommandLine -like '*run_live_execution_bundle_report.py*' -or $_.CommandLine -like '*libs.reporting.live_execution_bundle_runner*') } | "
                "Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"
            )
            completed = run_hidden(
                ["powershell", "-NoProfile", "-Command", probe],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=3.0,
                check=False,
            )
            raw = str(completed.stdout or "").strip()
            if not raw:
                return {}
            payload = json.loads(raw)
            rows = payload if isinstance(payload, list) else [payload]
            for row in rows:
                if not isinstance(row, dict):
                    continue
                pid = int(row.get("ProcessId") or 0)
                cmd = str(row.get("CommandLine") or "").lower()
                if pid <= 0 or pid == current_pid:
                    continue
                if (
                    script_path not in cmd
                    and "run_live_execution_bundle_report.py" not in cmd
                    and runner_module not in cmd
                ):
                    continue
                creation_epoch = _creation_epoch_from_wmi(row.get("CreationDate"))
                return {
                    "pid": pid,
                    "parent_pid": int(row.get("ParentProcessId") or 0),
                    "script": "run_live_execution_bundle_report.py",
                    "entrypoint_module": _runner_module_name() if runner_module in cmd else "",
                    "command_line": str(row.get("CommandLine") or ""),
                    "detection_source": "process_scan",
                    "creation_epoch": creation_epoch,
                    "age_sec": max(0.0, float(time.time()) - creation_epoch) if creation_epoch > 0 else None,
                }
        else:
            completed = run_hidden(
                ["ps", "-eo", "pid=,args="],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=3.0,
                check=False,
            )
            for raw in str(completed.stdout or "").splitlines():
                line = str(raw or "").strip()
                if not line:
                    continue
                try:
                    pid_text, cmd = line.split(None, 1)
                except ValueError:
                    continue
                pid = int(pid_text or 0)
                cmd_lower = str(cmd or "").lower()
                if pid <= 0 or pid == current_pid:
                    continue
                if (
                    script_path not in cmd_lower
                    and "run_live_execution_bundle_report.py" not in cmd_lower
                    and runner_module not in cmd_lower
                ):
                    continue
                return {
                    "pid": pid,
                    "parent_pid": int(parent_pid or 0),
                    "script": "run_live_execution_bundle_report.py",
                    "entrypoint_module": _runner_module_name() if runner_module in cmd_lower else "",
                    "command_line": str(cmd or ""),
                    "detection_source": "process_scan",
                }
    except Exception:
        return {}
    return {}


def _creation_epoch_from_wmi(value: Any) -> float:
    return _creation_epoch_from_wmi_r4_impl(value, facade=_r3_sys.modules[__name__])


def _stale_process_after_sec() -> float:
    try:
        return max(30.0, float(os.getenv("INTRADAY_TRADE_REPORT_STALE_PROCESS_SEC", "180") or 180.0))
    except Exception:
        return 180.0


def _terminate_process_tree(pid: int) -> bool:
    pid = int(pid or 0)
    if pid <= 0:
        return False
    try:
        if os.name == "nt":
            completed = run_hidden(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=5.0,
                check=False,
            )
            return int(completed.returncode or 1) == 0
        os.kill(pid, 15)
        return True
    except Exception:
        return False


def _write_bundle_job_lock(
    path: Path,
    *,
    pid: int,
    argv: List[str],
    target_run_id: str = "",
    target_symbol: str = "",
) -> None:
    now_epoch = float(time.time())
    payload = {
        "pid": int(pid or 0),
        "parent_pid": int(os.getpid()),
        "role": _bundle_role(),
        "status": "running",
        "created_at": _utc_iso(),
        "created_at_epoch": now_epoch,
        "started_at": _utc_iso(),
        "started_at_epoch": now_epoch,
        "touched_at": _utc_iso(),
        "touched_at_epoch": now_epoch,
        "script": "run_live_execution_bundle_report.py",
        "entrypoint_module": _runner_module_name(),
        "argv": list(argv or []),
        "target_run_id": str(target_run_id or ""),
        "target_symbol": _normalize_symbol(target_symbol),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _execution_action(state: Dict[str, Any]) -> str:
    execution = state.get("execution") if isinstance(state.get("execution"), dict) else {}
    order = execution.get("order") if isinstance(execution.get("order"), dict) else {}
    return str(order.get("action") or execution.get("action") or "").strip().upper()


def _execution_ok(state: Dict[str, Any]) -> bool:
    execution = state.get("execution") if isinstance(state.get("execution"), dict) else {}
    return bool(execution.get("ok")) and bool(execution.get("allowed", True))


def _cache_run_ids(summary: Dict[str, Any], current_run_id: str) -> List[str]:
    return _cache_run_ids_r4_impl(summary, current_run_id, facade=_r3_sys.modules[__name__])


def _invalidate_brief_cache(root: Path, run_ids: Iterable[str]) -> List[str]:
    cache_dir = _brief_cache_dir(root)
    removed: List[str] = []
    for run_id in run_ids:
        path = cache_dir / f"{run_id}.json"
        if not path.exists():
            continue
        try:
            path.unlink()
            removed.append(str(path))
        except Exception:
            continue
    return removed


def _build_bundle_argv(root: Path, state: Dict[str, Any] | None = None) -> List[str]:
    runtime_state = state if isinstance(state, dict) else {}
    execution = runtime_state.get("execution") if isinstance(runtime_state.get("execution"), dict) else {}
    order = execution.get("order") if isinstance(execution.get("order"), dict) else {}
    run_id = str(runtime_state.get("run_id") or "").strip()
    symbol = _normalize_symbol(order.get("symbol") or execution.get("symbol") or runtime_state.get("symbol") or "")
    argv = [
        "--env-path",
        str(Path(os.getenv("ENV_PATH", str(root / ".env")))),
        "--event-log-path",
        str(Path(os.getenv("EVENT_LOG_PATH", str(root / "data" / "logs" / "events.jsonl")))),
        "--evidence-log-path",
        str(Path(os.getenv("EVIDENCE_LOG_PATH", str(root / "data" / "evidence_ledger" / "events.jsonl")))),
        "--report-dir",
        str(root / "reports" / "dev" / "analysis" / "live_execution_bundles"),
        "--reports-root",
        str(root / "reports"),
        "--intents-path",
        str(Path(os.getenv("INTENTS_PATH", str(root / "data" / "logs" / "intents.jsonl")))),
        "--role",
        _bundle_role(),
        "--trade-report-ai",
        "--json",
    ]
    if run_id:
        argv.extend(["--target-run-id", run_id])
    if symbol:
        argv.extend(["--target-symbol", symbol])
    day = _runtime_trade_day(runtime_state)
    if day:
        argv.extend(["--day", day])
    return argv


def _make_bundle_event_logger(root: Path):
    try:
        from libs.core.event_logger import EventLogger, resolve_event_log_path
    except Exception:
        return None
    try:
        return EventLogger(log_path=resolve_event_log_path(str(root / "data" / "logs" / "events.jsonl")))
    except Exception:
        return None


def _log_bundle_event(
    root: Path,
    *,
    event: str,
    reason: str = "",
    run_id: str = "",
    trade_id: str = "",
    symbol: str = "",
    payload: Dict[str, Any] | None = None,
) -> None:
    logger = _make_bundle_event_logger(root)
    if logger is None:
        return
    safe_payload = dict(payload or {})
    safe_payload.setdefault("role", _bundle_role())
    if reason:
        safe_payload.setdefault("reason", str(reason))
    safe_payload.setdefault("pid", int(os.getpid()))
    safe_payload.setdefault("parent_pid", int(os.getpid()))
    with contextlib.suppress(Exception):
        logger.log(
            run_id=str(run_id or "runtime-report-bundle"),
            stage="reporting",
            event=event,
            event_name=f"reporting.{event}",
            level="info",
            trade_id=str(trade_id or ""),
            agent="reporting",
            phase="runtime",
            symbol=_normalize_symbol(symbol),
            payload=safe_payload,
        )


def _run_bundle_sync(argv: List[str]) -> tuple[int, str]:
    from libs.reporting.live_execution_bundle_runner import run_live_execution_bundle_inprocess

    return run_live_execution_bundle_inprocess(argv)


def _background_creationflags() -> int:
    return int(background_creationflags())


def _run_bundle_with_timeout(
    root: Path,
    argv: List[str],
    *,
    timeout_sec: float,
    target_run_id: str = "",
    target_symbol: str = "",
) -> tuple[int | None, str, int | None]:
    cmd = [sys.executable, "-m", _runner_module_name(), *argv]
    _log_bundle_event(
        root,
        event="report_bundle_subprocess_start",
        run_id=target_run_id or "runtime-report-bundle",
        symbol=target_symbol,
        payload={
            "spawn_command": list(cmd),
            "spawn_cwd": str(root),
            "spawn_mode": "sync_run_hidden",
        },
    )
    try:
        completed = run_hidden(
            cmd,
            cwd=str(root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=max(0.5, float(timeout_sec)),
            check=False,
        )
        _log_bundle_event(
            root,
            event="report_bundle_subprocess_finished",
            run_id=target_run_id or "runtime-report-bundle",
            symbol=target_symbol,
            payload={
                "returncode": int(completed.returncode or 0),
                "spawn_mode": "sync_run_hidden",
            },
        )
        return int(completed.returncode), str(completed.stdout or "").strip(), None
    except subprocess.TimeoutExpired:
        lock_path = _bundle_job_lock_path(root)
        env = dict(os.environ)
        env["INTRADAY_TRADE_REPORT_JOB_LOCK_PATH"] = str(lock_path)
        env["INTRADAY_TRADE_REPORT_PARENT_SPAWN"] = "1"
        proc = popen_hidden(  # noqa: S603
            cmd,
            background=True,
            cwd=str(root),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        )
        _write_bundle_job_lock(
            lock_path,
            pid=int(getattr(proc, "pid", 0) or 0),
            argv=cmd,
            target_run_id=target_run_id,
            target_symbol=target_symbol,
        )
        _log_bundle_event(
            root,
            event="report_bundle_subprocess_timeout_spawned",
            run_id=target_run_id or "runtime-report-bundle",
            symbol=target_symbol,
            payload={
                "pid": int(getattr(proc, "pid", 0) or 0),
                "spawn_command": list(cmd),
                "spawn_cwd": str(root),
                "spawn_creationflags": int(_background_creationflags()),
                "spawn_mode": "background_popen_hidden",
            },
        )
        return None, "", int(getattr(proc, "pid", 0) or 0)


def _build_generation_result(*, root: Path, summary: Dict[str, Any], run_id: str, return_code: int) -> Dict[str, Any]:
    cache_run_ids = _cache_run_ids(summary, run_id)
    removed_cache = _invalidate_brief_cache(root, cache_run_ids)
    run_bundles = summary.get("run_bundles") if isinstance(summary.get("run_bundles"), list) else []
    matched = next(
        (row for row in run_bundles if isinstance(row, dict) and str(row.get("run_id") or "").strip() == run_id),
        {},
    )
    brief_artifacts: Dict[str, str] = {}
    trade_id = str((matched or {}).get("trade_id") or "").strip()
    trade_day = _trade_day_from_trade_id(trade_id)
    if trade_id and trade_day:
        trade_paths = trade_artifact_paths(root / "reports", trade_day, trade_id)
        brief_json_path = Path(trade_paths.get("brief_json") or Path())
        brief_md_path = Path(trade_paths.get("brief_md") or Path())
        brief_artifacts = {
            "operator_brief_json_path": str(brief_json_path),
            "operator_brief_md_path": str(brief_md_path),
        }

    return {
        "ok": True,
        "status": "generated",
        "reason": "",
        "return_code": int(return_code),
        "summary": summary,
        "trade_id": trade_id,
        "story_id": str((matched or {}).get("story_id") or ""),
        "report_status": str((matched or {}).get("report_status") or ""),
        "report_path": str((matched or {}).get("trade_report_json_path") or ""),
        "symbol": _normalize_symbol((matched or {}).get("symbol") or ""),
        "cache_invalidated": removed_cache,
        **brief_artifacts,
    }


def generate_intraday_trade_artifacts(state: Dict[str, Any], *, root: Path | None = None) -> Dict[str, Any]:
    if not _is_trueish(os.getenv("INTRADAY_TRADE_REPORTS_ENABLED", "true")):
        return {"ok": False, "status": "disabled", "reason": "intraday_trade_reports_disabled"}

    applied_policy = state.get("applied_policy") if isinstance(state.get("applied_policy"), dict) else {}
    reporter = applied_policy.get("reporter") if isinstance(applied_policy.get("reporter"), dict) else {}
    trade_report = reporter.get("trade_report") if isinstance(reporter.get("trade_report"), dict) else {}
    if trade_report and trade_report.get("enabled") is False:
        return {
            "ok": False,
            "status": "disabled",
            "reason": "reporter.trade_report.enabled is false",
            "policy_source": str(trade_report.get("policy_source") or "commander_applied_policy"),
        }

    if not _execution_ok(state):
        return {"ok": False, "status": "skipped", "reason": "execution_not_successful"}

    action = _execution_action(state)
    if action not in {"BUY", "SELL"}:
        return {"ok": False, "status": "skipped", "reason": "non_trade_action"}
    execution = state.get("execution") if isinstance(state.get("execution"), dict) else {}
    repo_root = Path(root) if root is not None else _root_dir()
    run_id = str(state.get("run_id") or "").strip()
    argv = _build_bundle_argv(repo_root, state)
    force_sync = root is not None or _is_trueish(state.get("force_sync_intraday_trade_reports"))

    generate_on_open = bool(trade_report.get("generate_on_open", False))
    if action == "BUY" and not generate_on_open and not force_sync:
        return {
            "ok": True,
            "status": "skipped",
            "reason": "trade_report_generate_on_open_disabled",
            "report_status": "pending",
            "symbol": _normalize_symbol(
                ((execution.get("order") or {}) if isinstance(execution.get("order"), dict) else {}).get("symbol")
                or execution.get("symbol")
                or state.get("symbol")
                or ""
            ),
            "target_run_id": str(state.get("run_id") or "").strip(),
            "target_symbol": _normalize_symbol(
                ((execution.get("order") or {}) if isinstance(execution.get("order"), dict) else {}).get("symbol")
                or execution.get("symbol")
                or state.get("symbol")
                or ""
            ),
            "role": _bundle_role(),
            "policy_source": str(trade_report.get("policy_source") or "commander_applied_policy"),
        }

    order = execution.get("order") if isinstance(execution.get("order"), dict) else {}
    symbol = _normalize_symbol(order.get("symbol") or execution.get("symbol") or state.get("symbol") or "")
    _log_bundle_event(
        repo_root,
        event="report_bundle_spawn_requested",
        run_id=run_id,
        symbol=symbol,
        payload={
            "lock_path": str(_bundle_job_lock_path(repo_root)),
            "target_run_id": run_id,
            "target_symbol": symbol,
            "force_sync": bool(force_sync),
        },
    )
    if not force_sync:
        active_job = _active_bundle_job(_bundle_job_lock_path(repo_root))
        if not active_job:
            active_job = _active_bundle_process(repo_root)
            active_pid = int(active_job.get("pid") or 0) if isinstance(active_job, dict) else 0
            active_age_sec = float(active_job.get("age_sec") or 0.0) if isinstance(active_job, dict) else 0.0
            if active_pid > 0 and active_age_sec >= _stale_process_after_sec():
                terminated = _terminate_process_tree(active_pid)
                _log_bundle_event(
                    repo_root,
                    event="report_bundle_stale_process_terminated",
                    reason="orphan_bundle_process_exceeded_stale_window",
                    run_id=run_id,
                    symbol=symbol,
                    payload={
                        "lock_path": str(_bundle_job_lock_path(repo_root)),
                        "active_pid": active_pid,
                        "active_age_sec": active_age_sec,
                        "terminated": bool(terminated),
                        "target_run_id": run_id,
                        "target_symbol": symbol,
                    },
                )
                if terminated:
                    time.sleep(0.2)
                    active_job = {}
        if active_job:
            queued = _enqueue_bundle_request(
                repo_root,
                run_id=run_id,
                symbol=symbol,
                reason="bundle_busy_queued",
            )
            _log_bundle_event(
                repo_root,
                event="report_bundle_spawn_skipped_existing_process",
                reason="bundle_busy_queued",
                run_id=run_id,
                symbol=symbol,
                payload={
                    "target_run_id": run_id,
                    "target_symbol": symbol,
                    "lock_path": str(active_job.get("lock_path") or _bundle_job_lock_path(repo_root)),
                    "active_pid": int(active_job.get("pid") or 0),
                    "dedupe_source": str(active_job.get("detection_source") or "lock"),
                    "queue_path": str(queued.get("queue_path") or _bundle_job_queue_path(repo_root)),
                    "queue_length": int(queued.get("queue_length") or 0),
                    "queue_deduped": bool(queued.get("deduped")),
                },
            )
            return {
                "ok": True,
                "status": "queued",
                "reason": "bundle_busy_queued",
                "return_code": None,
                "summary": {},
                "trade_id": "",
                "story_id": "",
                "report_status": "queued",
                "report_path": "",
                "symbol": symbol,
                "cache_invalidated": [],
                "background_pid": int(active_job.get("pid") or 0),
                "lock_path": str(active_job.get("lock_path") or ""),
                "dedupe_source": str(active_job.get("detection_source") or "lock"),
                "target_run_id": run_id,
                "target_symbol": symbol,
                "queue_path": str(queued.get("queue_path") or ""),
                "queue_length": int(queued.get("queue_length") or 0),
                "queue_deduped": bool(queued.get("deduped")),
                "role": _bundle_role(),
            }
    if force_sync:
        rc, raw = _run_bundle_sync(argv)
        queued_pid = None
    else:
        rc, raw, queued_pid = _run_bundle_with_timeout(
            repo_root,
            argv,
            timeout_sec=float(os.getenv("INTRADAY_TRADE_REPORT_SYNC_TIMEOUT_SEC", "2.0") or 2.0),
            target_run_id=run_id,
            target_symbol=symbol,
        )

    if queued_pid:
        _log_bundle_event(
            repo_root,
            event="report_bundle_spawned_background",
            run_id=run_id,
            symbol=symbol,
            payload={
                "lock_path": str(_bundle_job_lock_path(repo_root)),
                "background_pid": int(queued_pid),
                "target_run_id": run_id,
                "target_symbol": symbol,
            },
        )
        return {
            "ok": True,
            "status": "queued",
            "reason": "",
            "return_code": None,
            "summary": {},
            "trade_id": "",
            "story_id": "",
            "report_status": "queued",
            "report_path": "",
            "symbol": symbol,
            "cache_invalidated": [],
            "queue_mode": "background_subprocess",
            "background_pid": int(queued_pid),
            "lock_path": str(_bundle_job_lock_path(repo_root)),
            "target_run_id": run_id,
            "target_symbol": symbol,
            "role": _bundle_role(),
        }

    try:
        summary = json.loads(raw) if raw else {}
    except Exception:
        summary = {}

    if rc != 0 or not isinstance(summary, dict):
        return {
            "ok": False,
            "status": "failed",
            "reason": "intraday_bundle_generation_failed",
            "return_code": int(rc),
            "stdout": raw[-1000:],
        }

    result = _build_generation_result(root=repo_root, summary=summary, run_id=run_id, return_code=int(rc))
    result["target_run_id"] = run_id
    result["target_symbol"] = symbol
    result["role"] = _bundle_role()
    return result
