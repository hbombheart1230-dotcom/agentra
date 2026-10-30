from typing import List

def _build_bundle_repair_command(
    *, day: str, target_run_id: str, role: str, max_runs: int,
    event_log_path: str, evidence_log_path: str, report_dir: str, reports_root: str,
    facade,
) -> List[str]:
    return [
        facade.sys.executable, str(facade.ROOT / "scripts" / "run_live_execution_bundle_report.py"),
        "--day", str(day), "--target-run-id", str(target_run_id), "--max-runs", str(max_runs),
        "--event-log-path", str(event_log_path), "--evidence-log-path", str(evidence_log_path),
        "--report-dir", str(report_dir), "--reports-root", str(reports_root),
        "--no-trade-report-ai", "--role", str(role), "--json",
    ]

def _build_report_regen_command(
    *, day: str, trade_id: str, reports_root: str, local_debug: bool,
    hard_timeout_sec, with_llm: bool = False, facade,
) -> List[str]:
    command = [
        facade.sys.executable,
        str(facade.ROOT / "scripts" / "run_ai_trade_report_batch.py"),
        "--day", str(day), "--trade-id", str(trade_id), "--reports-root", str(reports_root),
        "--retry-max", "0", "--json",
    ]
    if hard_timeout_sec is not None:
        command.extend(["--hard-timeout-sec", str(hard_timeout_sec)])
    if local_debug:
        command.append("--local-debug")
    elif with_llm:
        command.append("--with-llm")
    return command
