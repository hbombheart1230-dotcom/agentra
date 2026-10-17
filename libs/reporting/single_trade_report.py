from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

from libs.reporting.llm_artifacts import (
    build_compact_input_artifact,
    iter_trade_dirs,
    persist_llm_artifact_refs,
    trade_artifact_paths,
    write_json,
)
from libs.reporting.intraday_trade_reports import build_same_day_reporter_linkage
from libs.reporting.intraday_trade_reports import build_holding_phase_observability
from libs.reporting.controlled_mock_lane_report import (
    attach_controlled_lane_report_surface,
    build_controlled_lane_report_surface,
)
from libs.reporting.trade_execution_snapshot import build_execution_details
from libs.reporting.trade_report_ai import (
    build_ai_trade_report,
    build_ai_trade_report_compact_input,
    build_trade_summary_input,
    build_trade_summary_report,
    render_trade_report_markdown,
    render_trade_summary_markdown_with_evaluation,
)
from libs.reporting.trade_story_pipeline import (
    _build_monitor_blocker_trace,
    _build_monitor_stop_policy_trace,
    _build_scanner_selection_trace,
    build_execution_outcome_human,
    build_filters_human,
    build_guard_reason_human,
    build_lifecycle_bundle,
    build_market_context_human,
    build_monitor_reason_human,
    build_operator_conclusion_human,
    build_reporter_status_human,
    build_scanner_reason_human,
    build_story_contract,
    build_timeline,
    build_trade_story_input_from_bundle,
)
import sys as _r3_sys
from libs.agents.reporter.narrative.single_trade_report_bodies_01 import (  # R-4 owner bodies (facade-injected)
    _safe_float_r4_impl,
    _safe_int_r4_impl,
    _trade_report_policy_r4_impl,
    _null_execution_details_r4_impl,
    _execution_details_from_state_r4_impl,
    _entry_strategist_context_r4_impl,
    _build_monitor_snapshot_r4_impl,
    _format_duration_r4_impl,
)
from libs.agents.reporter.narrative.single_trade_report_r8_bodies_01 import (  # R-4 owner bodies (facade-injected)
    _same_day_reporter_paths_r4_impl,
    _find_open_trade_id_r4_impl,
    _build_trade_report_inputs_r4_impl,
)


def _root_dir() -> Path:
    return Path(__file__).resolve().parents[2]


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _normalize_symbol(value: Any) -> str:
    return str(value or "").strip().upper()


def _safe_float(value: Any) -> float | None:
    return _safe_float_r4_impl(value, facade=_r3_sys.modules[__name__])


def _safe_int(value: Any) -> int | None:
    return _safe_int_r4_impl(value, facade=_r3_sys.modules[__name__])


def _json_sha256(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()


def _execution_payload(state: Dict[str, Any]) -> Dict[str, Any]:
    return state.get("execution") if isinstance(state.get("execution"), dict) else {}


def _execution_order(state: Dict[str, Any]) -> Dict[str, Any]:
    execution = _execution_payload(state)
    return execution.get("order") if isinstance(execution.get("order"), dict) else {}


def _execution_action(state: Dict[str, Any]) -> str:
    execution = _execution_payload(state)
    order = _execution_order(state)
    return str(order.get("action") or execution.get("action") or "").strip().upper()


def _execution_symbol(state: Dict[str, Any]) -> str:
    execution = _execution_payload(state)
    order = _execution_order(state)
    return _normalize_symbol(order.get("symbol") or execution.get("symbol") or state.get("symbol") or "")


def _load_json_dict(path: Path) -> Dict[str, Any]:
    try:
        if not path.exists():
            return {}
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _resolve_trade_day(state: Dict[str, Any], *, root: Path | None = None) -> str:
    raw_day = str(state.get("day") or "").strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw_day):
        return raw_day
    execution = _execution_payload(state)
    ts_candidates = [
        execution.get("ts"),
        state.get("ts"),
        ((state.get("monitor_output") or {}) if isinstance(state.get("monitor_output"), dict) else {}).get("ts"),
        ((state.get("scanner_output") or {}) if isinstance(state.get("scanner_output"), dict) else {}).get("ts"),
    ]
    for candidate in ts_candidates:
        text = str(candidate or "").strip()
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
            return text
        match = re.match(r"^(\d{4}-\d{2}-\d{2})[T\s]", text)
        if match:
            return match.group(1)
    run_id = str(state.get("run_id") or "").strip()
    repo_root = Path(root) if root is not None else _root_dir()
    if run_id:
        canonical_root = repo_root / "reports" / "canonical"
        if canonical_root.exists():
            for day_dir in sorted(canonical_root.iterdir(), key=lambda path: path.name, reverse=True):
                if day_dir.is_dir() and re.fullmatch(r"\d{4}-\d{2}-\d{2}", day_dir.name):
                    if (day_dir / run_id).exists():
                        return day_dir.name
    return datetime.now().astimezone().date().isoformat()


def _same_day_reporter_paths(*, root: Path, day: str) -> tuple[Path, Path]:
    return _same_day_reporter_paths_r4_impl(root=root, day=day, facade=_r3_sys.modules[__name__])


def _build_canonical_context(
    *,
    root: Path,
    day: str,
    run_id: str,
    commander: Dict[str, Any],
    strategist: Dict[str, Any],
    scanner: Dict[str, Any],
    monitor: Dict[str, Any],
    supervisor: Dict[str, Any],
    execution: Dict[str, Any],
) -> Dict[str, Any]:
    canonical_root = root / "reports" / "canonical" / day / run_id if day and run_id else None
    file_map = {
        "commander": "commander.json",
        "strategist": "strategist.json",
        "scanner": "scanner.json",
        "monitor": "monitor.json",
        "supervisor": "supervisor.json",
        "executor": "executor.json",
    }
    direct_map = {
        "commander": dict(commander),
        "strategist": dict(strategist),
        "scanner": dict(scanner),
        "monitor": dict(monitor),
        "supervisor": dict(supervisor),
        "executor": dict(execution),
    }
    artifacts: Dict[str, Any] = {}
    canonical_agent_artifacts: Dict[str, Any] = {}
    evidence_provenance: Dict[str, str] = {}
    for agent, filename in file_map.items():
        path = canonical_root / filename if canonical_root is not None else None
        path_text = str(path) if path is not None and path.exists() else ""
        payload = _load_json_dict(path) if path is not None else {}
        direct_payload = direct_map.get(agent) if isinstance(direct_map.get(agent), dict) else {}
        artifacts[f"canonical_{agent}_json"] = path_text
        if payload:
            canonical_agent_artifacts[agent] = dict(payload)
            evidence_provenance[agent] = "canonical"
        elif direct_payload:
            canonical_agent_artifacts[agent] = dict(direct_payload)
            evidence_provenance[agent] = "direct_artifact"
    agent_trace_path = (
        root
        / "reports"
        / "dev"
        / "analysis"
        / "live_execution_bundles"
        / "agent_pipeline_trace"
        / f"agent_pipeline_trace_{run_id[:20]}.json"
    )
    artifacts["agent_pipeline_trace_json"] = str(agent_trace_path) if run_id and agent_trace_path.exists() else ""
    return {
        "artifacts": artifacts,
        "canonical_agent_artifacts": canonical_agent_artifacts,
        "evidence_provenance": evidence_provenance,
    }


def _execution_ok(state: Dict[str, Any]) -> bool:
    execution = _execution_payload(state)
    return bool(execution.get("ok")) and bool(execution.get("allowed", True))


def _trade_report_policy(state: Dict[str, Any]) -> Dict[str, Any]:
    return _trade_report_policy_r4_impl(state, facade=_r3_sys.modules[__name__])


def _null_execution_details() -> Dict[str, Any]:
    return _null_execution_details_r4_impl(facade=_r3_sys.modules[__name__])


def _execution_details_from_state(state: Dict[str, Any]) -> Dict[str, Any]:
    return _execution_details_from_state_r4_impl(state, facade=_r3_sys.modules[__name__])


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        if not path.exists():
            return {}
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _matching_trade_dirs(trade_day_root: Path, symbol: str) -> Iterable[Path]:
    compact_day = trade_day_root.name.replace("-", "")
    pattern = re.compile(rf"^TRD_{re.escape(compact_day)}_{re.escape(symbol)}_(\d+)$")
    if not trade_day_root.exists():
        return []
    return sorted(
        (
            path
            for path in iter_trade_dirs(trade_day_root)
            if path.is_dir() and pattern.match(path.name)
        ),
        key=lambda path: path.name,
    )


def _find_open_trade_id(trade_day_root: Path, symbol: str) -> str:
    return _find_open_trade_id_r4_impl(trade_day_root, symbol, facade=_r3_sys.modules[__name__])


def build_single_trade_report_id(state: Dict[str, Any], *, root: Path | None = None) -> str:
    repo_root = Path(root) if root is not None else _root_dir()
    day = _resolve_trade_day(state, root=repo_root)
    symbol = _execution_symbol(state)
    compact_day = day.replace("-", "")
    trade_day_root = repo_root / "reports" / "trades" / day
    if _execution_action(state) == "SELL":
        existing_open = _find_open_trade_id(trade_day_root, symbol)
        if existing_open:
            return existing_open
    seq = 0
    pattern = re.compile(rf"^TRD_{re.escape(compact_day)}_{re.escape(symbol)}_(\d+)$")
    for trade_dir in _matching_trade_dirs(trade_day_root, symbol):
        match = pattern.match(trade_dir.name)
        if not match:
            continue
        seq = max(seq, int(match.group(1)))
    return f"TRD_{compact_day}_{symbol}_{seq + 1:02d}"


def _entry_strategist_context(state: Dict[str, Any], symbol: str) -> Dict[str, Any]:
    return _entry_strategist_context_r4_impl(state, symbol, facade=_r3_sys.modules[__name__])


def _build_monitor_snapshot(monitor: Dict[str, Any], *, symbol: str, run_id: str, ts: str) -> Dict[str, Any]:
    return _build_monitor_snapshot_r4_impl(monitor, symbol=symbol, run_id=run_id, ts=ts, facade=_r3_sys.modules[__name__])


def _format_duration(seconds: int | None) -> str:
    return _format_duration_r4_impl(seconds, facade=_r3_sys.modules[__name__])


def _build_trade_report_inputs(
    trade_id: str,
    state: Dict[str, Any],
    *,
    root: Path,
) -> Dict[str, Any]:
    return _build_trade_report_inputs_r4_impl(trade_id, state, root=root, facade=_r3_sys.modules[__name__])


def generate_single_trade_report(
    trade_id: str,
    *,
    state: Dict[str, Any],
    root: Path | None = None,
) -> Dict[str, Any]:
    repo_root = Path(root) if root is not None else _root_dir()
    reports_root = repo_root / "reports"
    policy = _trade_report_policy(state)
    if policy and policy.get("enabled") is False:
        return {
            "ok": False,
            "status": "disabled",
            "reason": "reporter.trade_report.enabled is false",
            "policy_source": str(policy.get("policy_source") or "commander_applied_policy"),
        }
    if not _execution_ok(state):
        return {"ok": False, "status": "skipped", "reason": "execution_not_successful"}
    action = _execution_action(state)
    if action not in {"BUY", "SELL"}:
        return {"ok": False, "status": "skipped", "reason": "non_trade_action"}
    generate_on_open = bool(policy.get("generate_on_open", False))
    if action == "BUY" and not generate_on_open:
        return {
            "ok": True,
            "status": "skipped",
            "reason": "trade_report_generate_on_open_disabled",
            "report_status": "pending",
            "symbol": _execution_symbol(state),
            "trade_id": str(trade_id or ""),
            "policy_source": str(policy.get("policy_source") or "commander_applied_policy"),
        }

    inputs = _build_trade_report_inputs(str(trade_id or "").strip(), state, root=repo_root)
    trade_paths = inputs.get("trade_paths") if isinstance(inputs.get("trade_paths"), dict) else {}
    story_input = dict(inputs.get("story_input") or {})
    lifecycle = dict(inputs.get("lifecycle") or {})
    lifecycle_bundle = dict(inputs.get("lifecycle_bundle") or {})
    day = _resolve_trade_day(story_input if isinstance(story_input, dict) else state, root=repo_root)
    run_id = str(story_input.get("run_id") or state.get("run_id") or "").strip()
    symbol = str(story_input.get("symbol") or _execution_symbol(state)).strip()
    if not trade_paths:
        trade_paths = trade_artifact_paths(reports_root, day, trade_id)
    trade_paths["trade_root"].mkdir(parents=True, exist_ok=True)
    trade_paths["reports_dir"].mkdir(parents=True, exist_ok=True)

    write_json(trade_paths["entry_json"], dict(lifecycle.get("entry") or {}))
    write_json(trade_paths["hold_json"], dict(lifecycle.get("holding") or {}))
    write_json(trade_paths["exit_json"], dict(lifecycle.get("exit") or {}))
    write_json(trade_paths["lifecycle_bundle_json"], lifecycle_bundle)
    write_json(trade_paths["ai_trade_report_input_json"], story_input)

    compact_input = build_ai_trade_report_compact_input(story_input)
    compact_artifact = build_compact_input_artifact(
        component="ai_trade_report",
        run_id=run_id,
        trade_id=trade_id,
        story_id=str(story_input.get("story_id") or trade_id),
        day=day,
        source_artifact_path=str(trade_paths["ai_trade_report_input_json"]),
        source_input=story_input,
        compact_input=compact_input,
    )
    write_json(trade_paths["ai_trade_report_compact_input_json"], compact_artifact)

    report = build_ai_trade_report(story_input, enabled=True)
    report = attach_controlled_lane_report_surface(report, story_input)
    llm_artifact = report.get("llm_response_artifact") if isinstance(report.get("llm_response_artifact"), dict) else {}
    generation = report.get("generation") if isinstance(report.get("generation"), dict) else {}
    report_status = str(generation.get("status") or report.get("ai_trade_report_status") or report.get("status") or "").strip()
    trade_paths["ai_trade_report_json"].write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    trade_paths["ai_trade_report_md"].write_text(
        render_trade_report_markdown(report),
        encoding="utf-8",
    )
    summary_input = build_trade_summary_input(report)
    summary_report = build_trade_summary_report(summary_input, enabled=True)
    write_json(trade_paths["ai_trade_summary_input_json"], summary_input)
    write_json(trade_paths["ai_trade_summary_json"], summary_report)
    trade_paths["ai_trade_summary_md"].write_text(
        render_trade_summary_markdown_with_evaluation(report, summary_report),
        encoding="utf-8-sig",
        newline="\n",
    )
    summary_llm_artifact = (
        summary_report.get("llm_response_artifact")
        if isinstance(summary_report.get("llm_response_artifact"), dict)
        else {}
    )
    if summary_llm_artifact:
        summary_llm_compact = persist_llm_artifact_refs(
            artifact=summary_llm_artifact,
            reports_root=reports_root,
            day=day,
            run_id=run_id,
            component="ai_trade_summary",
        )
        write_json(trade_paths["ai_trade_summary_llm_response_json"], summary_llm_compact)
    llm_written = ""
    if llm_artifact:
        compact_llm = persist_llm_artifact_refs(
            artifact=llm_artifact,
            reports_root=reports_root,
            day=day,
            run_id=run_id,
            component="ai_trade_report",
        )
        llm_written = str(write_json(trade_paths["ai_trade_report_llm_response_json"], compact_llm))
        llm_artifact = compact_llm

    report_generation_state = {
        "schema_version": "report_generation_state.v1",
        "components": {
            "ai_trade_report": {
                "fingerprint": _json_sha256(
                    {
                        "component": "ai_trade_report",
                        "trade_id": trade_id,
                        "run_id": run_id,
                        "story_input_sha256": _json_sha256(story_input),
                        "compact_input_sha256": _json_sha256(compact_input),
                    }
                ),
                "component": "ai_trade_report",
                "status": report_status,
                "report_status": "available",
                "skip_reason": "",
                "trade_id": trade_id,
                "run_id": run_id,
                "updated_at": _utc_iso(),
                "model": str(
                    ((report.get("generation") or {}) if isinstance(report.get("generation"), dict) else {}).get("model")
                    or llm_artifact.get("model")
                    or ((llm_artifact.get("model_info") or {}) if isinstance(llm_artifact.get("model_info"), dict) else {}).get("model")
                    or ""
                ),
                "report_json_path": str(trade_paths["ai_trade_report_json"]),
                "report_md_path": str(trade_paths["ai_trade_report_md"]),
                "llm_response_path": llm_written,
                "source_inputs": {
                    "story_input_sha256": _json_sha256(story_input),
                    "compact_input_sha256": _json_sha256(compact_input),
                },
            }
        },
    }
    write_json(trade_paths["reports_dir"] / "report_generation_state.json", report_generation_state)
    return {
        "ok": True,
        "status": report_status or "ok",
        "reason": "",
        "trade_id": trade_id,
        "report_status": "available",
        "report_path": str(trade_paths["ai_trade_report_json"]),
        "symbol": symbol,
        "llm_calls": 1,
        "bundle_used": False,
    }
