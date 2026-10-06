from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from libs.market.preopen_macro_snapshot import capture_preopen_macro_snapshot
from libs.market.yfinance_support import DataSourceDependencyError

# Exit codes: 0 = ok/fallback, 2 = not captured, 3 = required dependency missing.
EXIT_DEPENDENCY_MISSING = 3


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture macro/index evidence before market open.")
    parser.add_argument("--env-path", type=Path, default=ROOT / ".env")
    parser.add_argument("--state-path", type=Path, default=ROOT / "data" / "state.json")
    args = parser.parse_args()
    os.chdir(ROOT)
    try:
        result = capture_preopen_macro_snapshot(
            env_path=args.env_path,
            state_path=args.state_path,
        )
    except DataSourceDependencyError as exc:
        print(json.dumps({"status": "dependency_missing", "reason": exc.reason, "error": str(exc)}, ensure_ascii=False), flush=True)
        print(f"ERROR: macro snapshot failed: {exc}", file=sys.stderr, flush=True)
        return EXIT_DEPENDENCY_MISSING
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return 0 if result.get("status") in {"ok", "fallback"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
