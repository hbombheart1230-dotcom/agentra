from __future__ import annotations


def _build_parser(*, facade):
    parser = facade.argparse.ArgumentParser(description="Replay and validate trade report runtime regression cases.")
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
