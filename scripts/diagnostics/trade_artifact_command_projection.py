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
