from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from libs.core.settings import load_env_file
from libs.market.yfinance_support import DataSourceDependencyError
from libs.reporting.baseline_samsung_hynix.forward_validation import (
    capture_q10_preopen_snapshot,
)


# Exit codes: 0 = CAPTURED, 2 = not captured (incl. DATA_UNAVAILABLE), 3 = required dependency missing.
EXIT_DEPENDENCY_MISSING = 3


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture immutable Q10 08:50 lead-market inputs.")
    parser.add_argument("--day", default=date.today().isoformat())
    parser.add_argument("--reports-root", default="reports")
    parser.add_argument("--state-path", default="data/state.json")
    parser.add_argument("--env-path", default=".env")
    args = parser.parse_args()
    load_env_file(Path(args.env_path))
    try:
        result = capture_q10_preopen_snapshot(
            day=str(args.day)[:10],
            reports_root=Path(args.reports_root),
            state_path=Path(args.state_path),
        )
    except DataSourceDependencyError as exc:
        # Nothing is persisted, so a re-run inside the capture window can still succeed.
        failure = {
            "q10_preopen_capture_status": "DEPENDENCY_MISSING",
            "day": str(args.day)[:10],
            "reason": exc.reason,
            "error": str(exc),
        }
        print(json.dumps(failure, ensure_ascii=False, indent=2), flush=True)
        print(f"ERROR: Q10 capture failed: {exc}", file=sys.stderr, flush=True)
        return EXIT_DEPENDENCY_MISSING
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 0 if result.get("q10_preopen_capture_status") == "CAPTURED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
