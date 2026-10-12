from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Canonical CLI name (P1.5.8). Behaviour is identical to scripts/run_m13_live_loop.py, which remains supported.
from libs.runtime.entrypoints.live_loop import ROOT as RUNTIME_ROOT, main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
