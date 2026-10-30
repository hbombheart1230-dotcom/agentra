"""intraday_trade_reports projections (moved verbatim from intraday_trade_reports).

Module globals and helpers are resolved on ``facade`` (the intraday_trade_reports module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


def _build_bundle_argv(root: Path, state: Dict[str, Any] | None = None, *, facade: Any) -> List[str]:
    runtime_state = state if isinstance(state, dict) else {}
    execution = runtime_state.get("execution") if isinstance(runtime_state.get("execution"), dict) else {}
    order = execution.get("order") if isinstance(execution.get("order"), dict) else {}
    run_id = str(runtime_state.get("run_id") or "").strip()
    symbol = facade._normalize_symbol(order.get("symbol") or execution.get("symbol") or runtime_state.get("symbol") or "")
    argv = [
        "--env-path",
        str(facade.Path(facade.os.getenv("ENV_PATH", str(root / ".env")))),
        "--event-log-path",
        str(facade.Path(facade.os.getenv("EVENT_LOG_PATH", str(root / "data" / "logs" / "events.jsonl")))),
        "--evidence-log-path",
        str(facade.Path(facade.os.getenv("EVIDENCE_LOG_PATH", str(root / "data" / "evidence_ledger" / "events.jsonl")))),
        "--report-dir",
        str(root / "reports" / "dev" / "analysis" / "live_execution_bundles"),
        "--reports-root",
        str(root / "reports"),
        "--intents-path",
        str(facade.Path(facade.os.getenv("INTENTS_PATH", str(root / "data" / "logs" / "intents.jsonl")))),
        "--role",
        facade._bundle_role(),
        "--trade-report-ai",
        "--json",
    ]
    if run_id:
        argv.extend(["--target-run-id", run_id])
    if symbol:
        argv.extend(["--target-symbol", symbol])
    day = facade._runtime_trade_day(runtime_state)
    if day:
        argv.extend(["--day", day])
    return argv
