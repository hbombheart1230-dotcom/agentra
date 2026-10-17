"""BASE-only input-mutation evidence for the two Monitor observation annotators."""
from __future__ import annotations
import copy
import hashlib
import importlib
import inspect
import json
import sys
import types
from pathlib import Path
import work_monitor_current_tree as T
import work_monitor_contracts as O

SOURCE = "libs/runtime/monitor/entry_candidate_annotation.py"
HELPER = "libs/runtime/commander_memory_application_trace.py"
NAMES = ("annotate_entry_policy_fields", "annotate_entry_minute_metrics")
FIXTURE = T.ROOT / "tests/fixtures/work_monitor/m008.json"


def baseline(path=SOURCE):
    if path not in (SOURCE, HELPER):
        raise AssertionError("unregistered BASE module")
    # Both exact modules have only typing/future imports, definitions and fixed
    # metadata constants. No runtime package/graph is imported to build BASE.
    module = types.ModuleType("_monitor_annotation_base_" + Path(path).stem)
    exec(compile(T.base_source(path), path, "exec"), module.__dict__)
    return module


def inputs(name):
    fn = getattr(baseline(), name)
    empty = {p: {} for p in inspect.signature(fn).parameters if p != "facade"}
    if name == NAMES[0]:
        empty["monitor_memory_bias_observation_only"] = False
        rich = copy.deepcopy(empty)
        rich["effective_policy_trace"] = {"effective_policy_source": "commander", "effective_policy_source_chain": ["commander", "monitor"], "policy_adjustments": {"nested": [1]}}
        rich["monitor_memory_bias_result"] = {"applied": True, "deltas": [{"field": "mock", "from": 1, "to": 2}]}
    else:
        empty.update(entry_row_source="", entry_rows=[])
        rich = copy.deepcopy(empty)
        rich.update(entry_row_source="synthetic", entry_rows=[{"ts": "fixed", "close": 100}], minute_fetch_meta={"minute_refetch_attempted": True, "minute_snapshot_age_minutes": 2}, entry_info={"metrics": {"existing": [1]}})
    yield empty
    yield rich
    for field in empty:
        for value in (None, [], "bad"):
            data = copy.deepcopy(rich)
            data[field] = value
            yield data


def observe(fn, data, *, feature=False):
    values = copy.deepcopy(data)
    before, calls, writes = O.wire(values), [], []
    if isinstance(values.get("entry_info"), dict):
        class Trace(dict):
            def __setitem__(self, key, value):
                writes.append(key)
                super().__setitem__(key, value)
        values["entry_info"] = Trace(values["entry_info"])
    kwargs = dict(values)
    if "facade" in inspect.signature(fn).parameters:
        if feature:
            if (T.ROOT / HELPER).read_text(encoding="utf-8") != T.base_source(HELPER):
                raise AssertionError("helper source changed")
            callback = importlib.import_module(HELPER[:-3].replace("/", ".")).build_monitor_commander_memory_application_trace
        else:
            callback = baseline(HELPER).build_monitor_commander_memory_application_trace
        def trace(**kw):
            calls.append(O.wire(kw))
            return callback(**kw)
        kwargs["facade"] = types.SimpleNamespace(build_monitor_commander_memory_application_trace=trace)
    result, error = None, None
    try:
        result = fn(**kwargs)
    except Exception as exc:
        error = [type(exc).__name__, str(exc)]
    observation = {"result": O.wire(result), "error": error, "before": before, "after": O.wire(values),
                   "aliases": O.alias_paths([values, result]), "calls": calls, "writes": writes}
    return {"sha256": O.sha(observation), "error": error, "writes": writes, "callbacks": len(calls)}


def produce():
    module = baseline()
    records = [{"id": name + ":" + str(i), "function": name, "input": data, "expected": observe(getattr(module, name), data)} for name in NAMES for i, data in enumerate(inputs(name))]
    return {"schema": "monitor.m008.frozen.v1", "BASE": T.BASE, "python": sys.version,
            "producer_sha256": hashlib.sha256(Path(__file__).read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
            "source_sha256": {p: hashlib.sha256(T.base_source(p).encode()).hexdigest() for p in (SOURCE, HELPER)}, "records": records}


if __name__ == "__main__":
    if sys.argv[1:] != ["freeze"]:
        raise SystemExit("Explicit BASE freeze required")
    FIXTURE.write_text(json.dumps(produce(), separators=(",", ":")) + "\n", encoding="utf-8")
    print(len(json.loads(FIXTURE.read_text(encoding="utf-8"))["records"]), FIXTURE.stat().st_size)
