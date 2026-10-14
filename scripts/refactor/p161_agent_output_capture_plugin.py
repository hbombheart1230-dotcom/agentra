"""pytest plugin (T3.5 fixture generator): records (input, output) of the four large builders in
`libs/contracts/agent_outputs.py` while an existing offline suite runs. Offline only; used once on BASE to freeze
golden fixtures. Writes JSON lines to $T35_CAPTURE_OUT. The real call is returned to the test untouched; the record
comes from a second call on deep copies under a frozen clock (builders are pure functions of `state`).

Usage: PYTHONPATH=scripts/refactor T35_CAPTURE_OUT=out.jsonl pytest -p p161_agent_output_capture_plugin <tests>
"""
from __future__ import annotations

import copy
import json
import os
import sys

import p161_agent_output_freeze as F

BUILDERS = ("build_strategist_output_artifact", "build_scanner_output_artifact", "build_monitor_output_artifact",
            "build_commander_output_artifact", "build_supervisor_output_artifact", "build_executor_output_artifact",
            "build_commander_shadow_artifact")
_OUT = os.environ.get("T35_CAPTURE_OUT", "")
_CURRENT = {"test": ""}


def _record(builder, name, args, kwargs):
    rec = {"builder": name, "test": _CURRENT["test"]}
    try:
        a, k = copy.deepcopy(args), copy.deepcopy(kwargs)
        rec["args"] = F.encode(list(a))
        rec["kwargs"] = F.encode(k)
    except Exception as exc:  # not freezable -> skipped, never fatal
        return
    a2, k2 = copy.deepcopy(a), copy.deepcopy(k)
    mod = sys.modules["libs.contracts.agent_outputs"]
    with F.frozen_clock(mod):
        try:
            out = builder(*a2, **k2)
            rec["result"] = F.encode(out)
        except Exception as exc:
            rec["exception"] = {"type": type(exc).__name__, "message": str(exc)[:200]}
    rec["input_mutated"] = F.canonical(F.encode(list(a2))) != F.canonical(rec["args"]) or \
        F.canonical(F.encode(k2)) != F.canonical(rec["kwargs"])
    try:
        with open(_OUT, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError:
        pass


def pytest_configure(config):
    if not _OUT:
        return
    import libs.contracts.agent_outputs as ao

    def wrap(name):
        original = getattr(ao, name)

        def wrapper(*args, **kwargs):
            _record(original, name, args, kwargs)
            return original(*args, **kwargs)
        wrapper.__name__ = original.__name__
        wrapper.__wrapped__ = original
        return wrapper

    for n in BUILDERS:
        setattr(ao, n, wrap(n))


def pytest_runtest_setup(item):
    _CURRENT["test"] = item.nodeid
