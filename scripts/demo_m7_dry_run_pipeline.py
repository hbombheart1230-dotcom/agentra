"""Compatibility entrypoint for scripts.examples.demo_m7_dry_run_pipeline."""

import importlib as _importlib
import sys as _sys
from pathlib import Path as _Path

_ROOT = _Path(__file__).resolve().parents[1]
if str(_ROOT) not in _sys.path:
    _sys.path.insert(0, str(_ROOT))

_impl = _importlib.import_module("scripts.examples.demo_m7_dry_run_pipeline")
if __name__ == "__main__":
    raise SystemExit(_impl.main())
else:
    _sys.modules[__name__] = _impl
