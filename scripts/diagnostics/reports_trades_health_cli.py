from __future__ import annotations

from typing import Any


def _build_parser(*, facade: Any) -> Any:
    parser = facade.argparse.ArgumentParser(description="Read-only health audit for reports/trades artifacts.")
    parser.add_argument("--reports-root", default="reports")
    parser.add_argument("--day", default="")
    parser.add_argument("--json", action="store_true")
    return parser
