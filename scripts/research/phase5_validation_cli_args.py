from __future__ import annotations

from typing import Any


def _build_parser(*, facade: Any):
    parser = facade.argparse.ArgumentParser(
        description="Generate a read-only validation bundle for phase 5 reporting/policy artifacts."
    )
    parser.add_argument("--event-log-path", default="data/logs/events.jsonl")
    parser.add_argument("--reports-root", default="reports")
    parser.add_argument("--output-dir", default="reports/dev/analysis/phase5_validation")
    parser.add_argument("--day", default=None)
    parser.add_argument("--max-runs", type=int, default=120)
    parser.add_argument("--max-executions", type=int, default=120)
    parser.add_argument("--max-news-titles", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    return parser
