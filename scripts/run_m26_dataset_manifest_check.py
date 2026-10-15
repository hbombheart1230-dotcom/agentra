"""Compatibility entrypoint for scripts.diagnostics.run_m26_dataset_manifest_check."""
import importlib as _importlib
import runpy as _runpy
import sys as _sys
from pathlib import Path as _Path

_ROOT = _Path(__file__).resolve().parents[1]
if str(_ROOT) not in _sys.path:
    _sys.path.insert(0, str(_ROOT))

if __name__ == "__main__":
    _runpy.run_module("scripts.diagnostics.run_m26_dataset_manifest_check", run_name="__main__")
else:
    _sys.modules[__name__] = _importlib.import_module("scripts.diagnostics.run_m26_dataset_manifest_check")
