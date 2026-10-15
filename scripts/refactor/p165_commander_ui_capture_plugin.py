"""pytest plugin (T4-D fixture generator): records INPUTS of the Strategist targets while an existing offline suite runs.

Targets: Commander `_resolve_commander_behavior_policy`, `_attach_commander_applied_policy`,
`_assess_open_position_commander_override` and Operator UI `_render_operator_brief_markdown`,
`_build_operator_brief_sections`, `_build_operator_brief_input`. Offline only; used once on BASE. Writes JSON lines
to $T4D_CAPTURE_OUT. Un-freezable values are replaced by `{"__opaque__": <type>}` and the record is flagged. Usage: PYTHONPATH=scripts/refactor T4D_CAPTURE_OUT=out.jsonl pytest -p p165_commander_ui_capture_plugin <tests>
"""
from __future__ import annotations

import copy
import importlib
import json
import os

import p162_scanner_capture_plugin as CAP

_OUT = os.environ.get("T4D_CAPTURE_OUT", "")
_CURRENT = {"test": ""}
TARGETS = {
    "commander_policy": ("graphs.commander_runtime", "_resolve_commander_behavior_policy"),
    "operator_markdown": ("apps.operator_ui.data_access_core", "_render_operator_brief_markdown"),
    "commander_attach": ("graphs.commander_runtime", "_attach_commander_applied_policy"),
    "commander_override": ("graphs.commander_runtime", "_assess_open_position_commander_override"),
    "brief_sections": ("apps.operator_ui.data_access_core", "_build_operator_brief_sections"),
    "brief_input": ("apps.operator_ui.data_access_core", "_build_operator_brief_input"),
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
