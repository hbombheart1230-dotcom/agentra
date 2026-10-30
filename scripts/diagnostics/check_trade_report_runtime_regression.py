from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from libs.reporting.llm_artifacts import trade_artifact_paths
from scripts.diagnostics import trade_artifact_command_projection as trade_commands
from scripts.diagnostics import trade_artifact_validation_read_projection as trade_read
from scripts.diagnostics import trade_artifact_context_projection as trade_context


DEFAULT_GOLDEN_CASES: Tuple[Tuple[str, str], ...] = (
    ("2026-04-15", "TRD_20260415_000660_04"),
    ("2026-04-16", "TRD_20260416_000660_01"),
    ("2026-04-16", "TRD_20260416_047040_01"),
)


def _emit_text(text: str) -> None:
    payload = str(text or "")
    try:
        sys.stdout.write(payload)
        if not payload.endswith("\n"):
            sys.stdout.write("\n")
        sys.stdout.flush()
        return
    except UnicodeEncodeError:
        pass
    sys.stdout.buffer.write(payload.encode("utf-8", errors="replace"))
    if not payload.endswith("\n"):
        sys.stdout.buffer.write(b"\n")
    sys.stdout.buffer.flush()


def _read_json(path: Path) -> Dict[str, Any]:
    return trade_read._read_json(path, facade=sys.modules[__name__])


def _safe_int(value: Any, default: int = 0) -> int:
    from scripts.diagnostics import trade_artifact_evidence_predicates as _owner
    return _owner._safe_int(value=value, default=default, facade=sys.modules[__name__])


def _is_closed_trade(lifecycle_bundle: Dict[str, Any], exit_payload: Dict[str, Any]) -> bool:
    from scripts.diagnostics import trade_artifact_evidence_predicates as _owner
    return _owner._is_closed_trade(lifecycle_bundle=lifecycle_bundle, exit_payload=exit_payload, facade=sys.modules[__name__])


def _is_empty_placeholder(value: Any) -> bool:
    from scripts.diagnostics import trade_artifact_evidence_predicates as _owner
    return _owner._is_empty_placeholder(value=value, facade=sys.modules[__name__])


def _has_substantive_entry_evidence(entry_payload: Dict[str, Any]) -> bool:
    from scripts.diagnostics import trade_artifact_evidence_predicates as _owner
    return _owner._has_substantive_entry_evidence(entry_payload=entry_payload, facade=sys.modules[__name__])


def _has_substantive_exit_evidence(exit_payload: Dict[str, Any]) -> bool:
    from scripts.diagnostics import trade_artifact_evidence_predicates as _owner
    return _owner._has_substantive_exit_evidence(exit_payload=exit_payload, facade=sys.modules[__name__])


def _section_provenance_all_fallback(report: Dict[str, Any]) -> bool:
    from scripts.diagnostics import trade_artifact_evidence_predicates as _owner
    return _owner._section_provenance_all_fallback(report=report, facade=sys.modules[__name__])


def _parse_case(raw: str) -> Dict[str, str]:
    from scripts.diagnostics import trade_artifact_case_projection as _owner
    return _owner._parse_case(raw=raw, facade=sys.modules[__name__])


def _normalize_cases(values: List[str]) -> List[Dict[str, str]]:
    from scripts.diagnostics import trade_artifact_case_projection as _owner
    return _owner._normalize_cases(values=values, facade=sys.modules[__name__])


def _resolve_trade_context(reports_root: Path, day: str, trade_id: str) -> Dict[str, Any]:
    return trade_context._resolve_trade_context(reports_root, day, trade_id, facade=sys.modules[__name__])


def _command_to_text(command: List[str]) -> str:
    from scripts.diagnostics import trade_artifact_command_text as _owner
    return _owner._command_to_text(command=command, facade=sys.modules[__name__])


def _run_python_json(command: List[str]) -> Dict[str, Any]:
    proc = subprocess.run(
        command,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    stdout = str(proc.stdout or "").strip()
    payload: Dict[str, Any] = {}
    if stdout:
        for line in reversed(stdout.splitlines()):
            try:
                candidate = json.loads(line)
            except Exception:
                continue
            if isinstance(candidate, dict):
                payload = candidate
                break
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": stdout,
        "stderr": str(proc.stderr or "").strip(),
        "json": payload,
        "command": _command_to_text(command),
    }


def _build_bundle_repair_command(
    *,
    day: str,
    target_run_id: str,
    role: str,
    max_runs: int,
    event_log_path: str,
    evidence_log_path: str,
    report_dir: str,
    reports_root: str,
) -> List[str]:
    return trade_commands._build_bundle_repair_command(
        day=day, target_run_id=target_run_id, role=role, max_runs=max_runs,
        event_log_path=event_log_path, evidence_log_path=evidence_log_path,
        report_dir=report_dir, reports_root=reports_root, facade=sys.modules[__name__],
    )


def _build_report_regen_command(
    *,
    day: str,
    trade_id: str,
    reports_root: str,
    local_debug: bool,
    hard_timeout_sec: Optional[float],
    with_llm: bool = False,
) -> List[str]:
    command = [
        sys.executable,
        str(ROOT / "scripts" / "run_ai_trade_report_batch.py"),
        "--day",
        str(day),
        "--trade-id",
        str(trade_id),
        "--reports-root",
        str(reports_root),
        "--retry-max",
        "0",
        "--json",
    ]
    if hard_timeout_sec is not None:
        command.extend(["--hard-timeout-sec", str(hard_timeout_sec)])
    if local_debug:
        command.append("--local-debug")
    elif with_llm:
        command.append("--with-llm")
    return command


def validate_trade_artifact_chain(reports_root: Path, day: str, trade_id: str) -> Dict[str, Any]:
    ctx = _resolve_trade_context(reports_root, day, trade_id)
    trade_paths = ctx["trade_paths"]
    entry_payload = ctx["entry_payload"]
    exit_payload = ctx["exit_payload"]
    hold_payload = ctx["hold_payload"]
    lifecycle_bundle = ctx["lifecycle_bundle"]
    story_input = ctx["story_input"]
    report = ctx["report"]
    provenance = ctx["provenance"]
    health = ctx["health"]

    failures: List[str] = []
    warnings: List[str] = []
    artifact_exists = {
        "entry_json": trade_paths["entry_json"].exists(),
        "hold_json": trade_paths["hold_json"].exists(),
        "exit_json": trade_paths["exit_json"].exists(),
        "lifecycle_bundle_json": trade_paths["lifecycle_bundle_json"].exists(),
        "ai_trade_report_input_json": trade_paths["ai_trade_report_input_json"].exists(),
        "ai_trade_report_json": trade_paths["ai_trade_report_json"].exists(),
        "ai_trade_report_md": trade_paths["ai_trade_report_md"].exists(),
    }
    for key, exists in artifact_exists.items():
        if not exists:
            failures.append(f"missing_artifact:{key}")

    authoritative_status = str(
        provenance.get("lifecycle_status")
        or health.get("lifecycle_status")
        or lifecycle_bundle.get("trade_lifecycle_status")
        or lifecycle_bundle.get("status")
        or ""
    ).strip().lower()
    closed_trade = _is_closed_trade(
        {
            **lifecycle_bundle,
            "trade_lifecycle_status": authoritative_status or lifecycle_bundle.get("trade_lifecycle_status"),
        },
        exit_payload,
    )
    entry_evidence = _has_substantive_entry_evidence(entry_payload)
    exit_evidence = _has_substantive_exit_evidence(exit_payload)
    linked_run_ids = [
        str(value or "").strip()
        for value in list(lifecycle_bundle.get("linked_run_ids") or [])
        if str(value or "").strip()
    ]
    selected_rank = _safe_int(
        story_input.get("selected_rank"),
        _safe_int(((story_input.get("scanner_selection_trace") or {}) if isinstance(story_input.get("scanner_selection_trace"), dict) else {}).get("selected_rank")),
    )
    candidate_count = _safe_int(
        story_input.get("candidate_count"),
        _safe_int(((story_input.get("scanner_selection_trace") or {}) if isinstance(story_input.get("scanner_selection_trace"), dict) else {}).get("candidate_count")),
    )
    selected_symbol = str(
        story_input.get("selected_symbol")
        or ((story_input.get("scanner_selection_trace") or {}) if isinstance(story_input.get("scanner_selection_trace"), dict) else {}).get("selected_symbol")
        or story_input.get("symbol")
        or ""
    ).strip()
    hold_duration = str(hold_payload.get("hold_duration") or lifecycle_bundle.get("hold_duration") or story_input.get("hold_duration") or "").strip()
    hold_duration_sec = hold_payload.get("hold_duration_sec")
    if hold_duration_sec in (None, ""):
        hold_duration_sec = lifecycle_bundle.get("hold_duration_sec")
    if hold_duration_sec in (None, ""):
        hold_duration_sec = story_input.get("hold_duration_sec")
    hold_duration_sec_int = _safe_int(hold_duration_sec, default=-1)
    story_status = str(story_input.get("status") or "").strip().lower()
    story_action = str(story_input.get("action") or "").strip().upper()

    if closed_trade and not str(exit_payload.get("run_id") or "").strip():
        failures.append("closed_trade_missing_exit_run_id")
    if closed_trade and not linked_run_ids:
        failures.append("closed_trade_missing_linked_run_ids")
    if closed_trade and entry_evidence and not str(entry_payload.get("run_id") or "").strip():
        failures.append("closed_trade_missing_entry_run_id")
    if closed_trade and entry_evidence and not str(entry_payload.get("ts") or "").strip():
        failures.append("closed_trade_missing_entry_ts")
    if closed_trade and not str(exit_payload.get("ts") or "").strip():
        failures.append("closed_trade_missing_exit_ts")
    if closed_trade and entry_evidence:
        if hold_duration in {"", "00:00:00", "0초", "0.0m", "0m"}:
            failures.append("closed_trade_fake_or_missing_hold_duration")
        if hold_duration_sec_int == 0:
            failures.append("closed_trade_zero_hold_duration_sec")
    if closed_trade and selected_rank <= 0:
        failures.append("closed_trade_selected_rank_zero")
    if closed_trade and candidate_count <= 0:
        failures.append("closed_trade_candidate_count_zero")
    if authoritative_status and story_status and story_status != authoritative_status:
        failures.append("story_input_status_conflicts_with_authoritative_status")
    if authoritative_status == "open" and not exit_evidence and story_action == "SELL":
        failures.append("story_input_action_conflicts_with_open_trade")
    if selected_symbol and selected_symbol != str(story_input.get("symbol") or "").strip():
        failures.append("selected_symbol_mismatch_story_symbol")
    generation = report.get("generation") if isinstance(report.get("generation"), dict) else {}
    generation_status = str(generation.get("status") or "").strip().lower()
    if report and generation_status not in {"ok", "partial", "salvaged", "repaired"}:
        failures.append("ai_trade_report_generation_status_bad")
    if report and _section_provenance_all_fallback(report):
        failures.append("ai_trade_report_all_section_provenance_fallback")

    linkage = lifecycle_bundle.get("same_day_reporter_linkage") if isinstance(lifecycle_bundle.get("same_day_reporter_linkage"), dict) else {}
    if linkage:
        linkage_status = str(linkage.get("status") or "").strip().lower()
        json_path = str(linkage.get("reporter_analysis_json_path") or "").strip()
        md_path = str(linkage.get("reporter_analysis_md_path") or "").strip()
        if linkage_status == "missing" and (json_path or md_path):
            failures.append("reporter_linkage_missing_but_artifact_path_populated")

    trade_origin = str(provenance.get("trade_origin") or lifecycle_bundle.get("trade_origin") or "").strip()
    completeness = str(provenance.get("lifecycle_completeness") or lifecycle_bundle.get("lifecycle_completeness") or "").strip()
    if closed_trade and entry_evidence and trade_origin == "recovered_partial":
        warnings.append("trade_origin_is_recovered_partial_even_with_entry_evidence")
    if closed_trade and not entry_evidence and completeness != "partial":
        failures.append("thin_entry_evidence_not_marked_partial")

    return {
        "day": day,
        "trade_id": trade_id,
        "closed_trade": closed_trade,
        "authoritative_status": authoritative_status,
        "entry_run_id": str(entry_payload.get("run_id") or "").strip(),
        "exit_run_id": str(exit_payload.get("run_id") or "").strip(),
        "linked_run_ids": linked_run_ids,
        "selected_symbol": selected_symbol,
        "selected_rank": selected_rank,
        "candidate_count": candidate_count,
        "hold_duration": hold_duration,
        "hold_duration_sec": None if hold_duration_sec in (None, "") else hold_duration_sec_int,
        "trade_origin": trade_origin,
        "lifecycle_completeness": completeness,
        "artifact_exists": artifact_exists,
        "failures": failures,
        "warnings": warnings,
        "ok": len(failures) == 0,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Replay and validate trade report runtime regression cases.")
    parser.add_argument("--reports-root", default="reports")
    parser.add_argument("--event-log-path", default="data/logs/events.jsonl")
    parser.add_argument("--evidence-log-path", default="data/evidence_ledger/events.jsonl")
    parser.add_argument("--report-dir", default="reports/dev/analysis/live_execution_bundles")
    parser.add_argument("--case", action="append", default=[], help="DAY:TRADE_ID[:RUN_ID]. Defaults to the golden trade matrix.")
    parser.add_argument("--role", default="manual_repair_bundle")
    parser.add_argument("--max-runs", type=int, default=200)
    parser.add_argument("--skip-repair", action="store_true")
    parser.add_argument("--skip-local-debug", action="store_true")
    parser.add_argument("--llm-acceptance", action="store_true")
    parser.add_argument("--llm-hard-timeout-sec", type=float, default=900.0)
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    reports_root = Path(str(args.reports_root or "reports")).resolve()
    cases = _normalize_cases(args.case)
    rows: List[Dict[str, Any]] = []
    overall_failures = 0

    for case in cases:
        day = str(case.get("day") or "").strip()
        trade_id = str(case.get("trade_id") or "").strip()
        requested_run_id = str(case.get("target_run_id") or "").strip()
        before_ctx = _resolve_trade_context(reports_root, day, trade_id)
        target_run_id = requested_run_id or str(before_ctx.get("target_run_id") or "").strip()

        repair_result: Dict[str, Any] = {"skipped": bool(args.skip_repair), "ok": False, "command": ""}
        if not args.skip_repair and target_run_id:
            repair_command = _build_bundle_repair_command(
                day=day,
                target_run_id=target_run_id,
                role=str(args.role or "manual_repair_bundle"),
                max_runs=int(args.max_runs or 200),
                event_log_path=str(args.event_log_path or "data/logs/events.jsonl"),
                evidence_log_path=str(args.evidence_log_path or "data/evidence_ledger/events.jsonl"),
                report_dir=str(args.report_dir or "reports/dev/analysis/live_execution_bundles"),
                reports_root=str(args.reports_root or "reports"),
            )
            repair_result = _run_python_json(repair_command)
        elif not args.skip_repair:
            repair_result = {
                "skipped": True,
                "ok": False,
                "command": "",
                "stderr": "",
                "stdout": "",
                "json": {},
                "returncode": 0,
                "reason": "target_run_id_missing",
            }

        local_debug_result: Dict[str, Any] = {"skipped": bool(args.skip_local_debug), "ok": False, "command": ""}
        if not args.skip_local_debug:
            local_debug_result = _run_python_json(
                _build_report_regen_command(
                    day=day,
                    trade_id=trade_id,
                    reports_root=str(args.reports_root or "reports"),
                    local_debug=True,
                    with_llm=False,
                    hard_timeout_sec=5.0,
                )
            )

        llm_result: Dict[str, Any] = {"skipped": not bool(args.llm_acceptance), "ok": False, "command": ""}
        if bool(args.llm_acceptance):
            llm_result = _run_python_json(
                _build_report_regen_command(
                    day=day,
                    trade_id=trade_id,
                    reports_root=str(args.reports_root or "reports"),
                    local_debug=False,
                    with_llm=True,
                    hard_timeout_sec=float(args.llm_hard_timeout_sec or 900.0),
                )
            )

        validation = validate_trade_artifact_chain(reports_root, day, trade_id)
        row = {
            "day": day,
            "trade_id": trade_id,
            "requested_target_run_id": requested_run_id,
            "resolved_target_run_id": target_run_id,
            "repair": repair_result,
            "local_debug_regen": local_debug_result,
            "llm_acceptance": llm_result,
            "validation": validation,
        }
        if not validation.get("ok"):
            overall_failures += 1
        rows.append(row)

    payload = {
        "ok": overall_failures == 0,
        "case_count": len(rows),
        "failed_case_count": overall_failures,
        "rows": rows,
    }

    if args.json:
        _emit_text(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for row in rows:
            validation = row["validation"]
            status = "PASS" if validation.get("ok") else "FAIL"
            _emit_text(f"[{status}] {row['day']} {row['trade_id']}")
            _emit_text(f"  target_run_id={row.get('resolved_target_run_id') or '-'}")
            _emit_text(
                f"  repair={'ok' if row['repair'].get('ok') else 'skip' if row['repair'].get('skipped') else 'fail'} "
                f"local_debug={'ok' if row['local_debug_regen'].get('ok') else 'skip' if row['local_debug_regen'].get('skipped') else 'fail'} "
                f"llm={'ok' if row['llm_acceptance'].get('ok') else 'skip' if row['llm_acceptance'].get('skipped') else 'fail'}"
            )
            _emit_text(
                f"  entry={validation.get('entry_run_id') or '-'} exit={validation.get('exit_run_id') or '-'} "
                f"linked={len(validation.get('linked_run_ids') or [])} selected_rank={validation.get('selected_rank')} "
                f"candidate_count={validation.get('candidate_count')} hold={validation.get('hold_duration') or '-'}"
            )
            if validation.get("failures"):
                _emit_text("  failures: " + ", ".join(str(item) for item in validation["failures"]))
            if validation.get("warnings"):
                _emit_text("  warnings: " + ", ".join(str(item) for item in validation["warnings"]))
        _emit_text(f"[summary] cases={len(rows)} failed={overall_failures}")
    return 0 if overall_failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
