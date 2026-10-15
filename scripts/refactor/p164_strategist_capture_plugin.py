"""pytest plugin (T4-C fixture generator): records INPUTS of the Strategist targets while an existing offline suite runs.

Target: `graphs.nodes.strategist_node.strategist_node` (State in/out). Offline only; used once on BASE. Writes JSON lines
to $T4C_CAPTURE_OUT. Un-freezable values (objects, callables) are replaced by `{"__opaque__": <type>}` and the record is
flagged. Usage: PYTHONPATH=scripts/refactor T4C_CAPTURE_OUT=out.jsonl pytest -p p164_strategist_capture_plugin <tests>
"""
from __future__ import annotations

import copy
import importlib
import json
import os

import p162_scanner_capture_plugin as CAP

_OUT = os.environ.get("T4C_CAPTURE_OUT", "")
_CURRENT = {"test": ""}
TARGETS = {
    "strategist_node": ("graphs.nodes.strategist_node", "strategist_node"),
}


def pytest_configure(config):
    if not _OUT:
        return
    for key, (modname, attr) in TARGETS.items():
        mod = importlib.import_module(modname)
        original = getattr(mod, attr)

        def make(key, original):
            def wrapper(*a, **k):
                try:
                    opaque = []
                    rec = {"target": key, "test": _CURRENT["test"],
                           "args": CAP._enc(copy.deepcopy(list(a)), "args", opaque),
                           "kwargs": CAP._enc(copy.deepcopy(k), "kwargs", opaque), "opaque_paths": opaque}
                    with open(_OUT, "a", encoding="utf-8") as fh:
                        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                except Exception:
                    pass
                return original(*a, **k)
            wrapper.__wrapped__ = original
            return wrapper
        setattr(mod, attr, make(key, original))


def pytest_runtest_setup(item):
    _CURRENT["test"] = item.nodeid
