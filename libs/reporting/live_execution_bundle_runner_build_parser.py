"""``_build_parser`` moved verbatim from live_execution_bundle_runner.py.

Helpers are resolved on ``facade`` (the source module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import argparse


def _build_parser(*, facade: Any) -> argparse.ArgumentParser:
    p = facade.argparse.ArgumentParser(description="Generate run-level aggregated execution bundles and per-trade reports.")
    p.add_argument("--env-path", default=".env")
    p.add_argument("--event-log-path", default="data/logs/events.jsonl")
    p.add_argument("--evidence-log-path", default="data/evidence_ledger/events.jsonl")
    p.add_argument("--report-dir", default="reports/dev/analysis/live_execution_bundles")
    p.add_argument("--reports-root", default="reports")
    p.add_argument("--intents-path", default="data/logs/intents.jsonl")
    p.add_argument("--day", default=None)
    p.add_argument("--max-runs", type=int, default=50)
    p.add_argument("--target-run-id", default=None)
    p.add_argument("--target-symbol", default=None)
    p.add_argument("--role", default="intraday_trade_report_bundle")
    ai = p.add_mutually_exclusive_group()
    ai.add_argument("--trade-report-ai", dest="trade_report_ai", action="store_true")
    ai.add_argument("--no-trade-report-ai", dest="trade_report_ai", action="store_false")
    p.set_defaults(trade_report_ai=None)
    p.add_argument("--trade-report-ai-model", default=None)
    p.add_argument("--trade-report-ai-temperature", type=float, default=None)
    p.add_argument("--trade-report-ai-max-tokens", type=int, default=None)
    p.add_argument("--json", action="store_true")
    return p
