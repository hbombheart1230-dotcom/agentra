from typing import Any


def _build_parser(*, facade: Any) -> Any:
    p = facade.argparse.ArgumentParser(description="Reconstruct incident timelines from JSONL event logs.")
    p.add_argument("--event-log-path", default="data/logs/events.jsonl"); p.add_argument("--report-dir", default="reports/incident_timeline")
    p.add_argument("--day", default=None); p.add_argument("--run-id", default="")
    p.add_argument("--window-before-sec", type=int, default=120); p.add_argument("--window-after-sec", type=int, default=900)
    p.add_argument("--require-incidents", action="store_true"); p.add_argument("--require-recovered", action="store_true"); p.add_argument("--json", action="store_true")
    return p
