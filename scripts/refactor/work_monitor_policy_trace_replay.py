"""BASE-first read-model proof; actual policy application is deliberately absent."""
from __future__ import annotations

import ast
import copy
import hashlib
import inspect
import json
import sys
import types
from pathlib import Path

import work_monitor_contracts as O
import work_monitor_current_tree as T

PATHS = ("libs/runtime/monitor_strategy_frame.py", "libs/runtime/monitor_entry_policy_context.py", "libs/runtime/monitor/entry_candidate_policy.py")
NAMES = ("build_monitor_policy_trace", "build_monitor_effective_policy_trace", "build_entry_effective_policy_trace")
HELPERS = ("libs/runtime/monitor_policy.py", "libs/runtime/chart_structure_features.py")
FIXTURE = T.ROOT / "tests/fixtures/work_monitor/m005.json"


def baseline(path):
    if path not in PATHS:
        raise AssertionError("unregistered BASE source")
    tree = T._tree(T.base_source(path))
    wanted = {NAMES[PATHS.index(path)], "monitor_policy_adjustment_inputs"}
    tree.body = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in wanted
                 or isinstance(n, ast.ImportFrom) and n.module in {"__future__", "typing"}]
    module = types.ModuleType("_monitor_trace_base_" + Path(path).stem)
    if path == PATHS[1]:
        # Same unchanged pure read callback on both sides. Prove entire dependency
        # sources against raw BASE before import; do not execute policy effects.
        for helper in HELPERS:
            if (T.ROOT / helper).read_text(encoding="utf-8") != T.base_source(helper):
                raise AssertionError("callback BASE provenance changed")
        from libs.runtime.monitor_policy import summarize_monitor_policy_deltas
        module.summarize_monitor_policy_deltas = summarize_monitor_policy_deltas
    exec(compile(tree, path, "exec"), module.__dict__)
    return module


def inputs(name):
    if name == NAMES[0]:
        empty = {"commander_context": {}, "monitor_policy": {}, "strategist_plan": {}, "policy_provenance": {}, "entry_info": {}, "exit_info": {}, "current_reason": ""}
        yield empty
        rich = copy.deepcopy(empty)
        rich.update(commander_context={"monitor_mission": "observe", "flow_instruction": "mock flow", "source_priority": ["commander"], "policy_source": "commander", "policy_fallback_used": False, "entry_control": {"nested": [1]}},
                    monitor_policy={"policy_source": "monitor", "policy_fallback_used": True},
                    strategist_plan={"selected_playbook": "mock", "entry_plan": {"nested": [1]}, "exit_plan": {"nested": [2]}, "symbol_constraints": {"MOCK001": [3]}},
                    entry_info={"triggered": True, "guard_reason": "repeated", "reason": "repeated", "failed_checks": ["repeated", "volume", ""]},
                    exit_info={"reason": "stop_loss", "final_exit_thresholds": {"stop_loss_pct": 0.03}, "max_runup_pct": {"nested": [4]}}, current_reason="mock reason")
        yield rich
        for key in empty:
            for value in (None, [], "bad"):
                data = copy.deepcopy(rich)
                data[key] = value
                yield data
        for value in (None, "", False, [], {}, 0, "commander"):
            data = copy.deepcopy(rich)
            data["commander_context"]["policy_source"] = value
            yield data
        data = copy.deepcopy(rich)
        data["entry_info"]["failed_checks"] = [str(i) for i in range(20)]
        yield data
    elif name == NAMES[1]:
        for before, after in (({}, {}), ({"volume_ratio_min": 1}, {"volume_ratio_min": 2}), ({"confidence_threshold": 0.7}, {"confidence_threshold": 0.4, "adjustments": ["mock", ""]})):
            for frame in ({}, {"playbook": "mock", "monitor_guidance": "hold", "risk_tone": "low", "trade_aggressiveness": "low"}):
                yield {"received_policy": before, "effective_policy": after, "frame": frame, "received_policy_source": "synthetic"}
        for key in ("received_policy", "effective_policy", "frame"):
            for value in (None, [], "bad"):
                data = {"received_policy": {}, "effective_policy": {}, "frame": {}, "received_policy_source": ""}
                data[key] = value
                yield data
    elif name == NAMES[2]:
        for applied in (False, True):
            for policy in ({}, {"volume_ratio_min": 2, "adjustments": ["mock"]}):
                yield {"entry_applied_policy": policy, "entry_policy_origin": "mock", "entry_received_policy": {"volume_ratio_min": 1}, "monitor_memory_bias_result": {"applied": applied}, "strategy_frame": {"playbook": "mock"}}
        for value in (None, [], "bad"):
            yield {"entry_applied_policy": {}, "entry_policy_origin": None, "entry_received_policy": {}, "monitor_memory_bias_result": value, "strategy_frame": {}}
    else:
        raise AssertionError(name)


def observe(fn, data):
    values = copy.deepcopy(data)
    before, calls = O.wire(values), []
    kwargs = dict(values)
    if "facade" in inspect.signature(fn).parameters:
        helper = baseline(PATHS[1])
        def build(**kw):
            calls.append(O.wire(kw))
            return helper.build_monitor_effective_policy_trace(**kw)
        kwargs["facade"] = types.SimpleNamespace(_build_monitor_effective_policy_trace=build)
    result, error = None, None
    try:
        result = fn(**kwargs)
    except Exception as exc:
        error = [type(exc).__name__, str(exc)]
    evidence = {"result": O.wire(result), "before": before, "after": O.wire(values), "error": error,
                "aliases": O.alias_paths([values, result]), "calls": calls}
    return {"sha256": O.sha(evidence), "error": error, "mutated": before != evidence["after"], "callbacks": len(calls)}


def produce():
    rows = []
    for path, name in zip(PATHS, NAMES):
        module = baseline(path)
        for i, data in enumerate(inputs(name)):
            rows.append({"id": name + ":" + str(i), "path": path, "function": name, "input": data, "expected": observe(getattr(module, name), data)})
    return {"schema": "monitor.m005.frozen.v1", "BASE": T.BASE, "python": sys.version,
            "producer_sha256": hashlib.sha256(Path(__file__).read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
            "source_sha256": {p: hashlib.sha256(T.base_source(p).encode()).hexdigest() for p in PATHS + HELPERS}, "records": rows}


if __name__ == "__main__":
    if sys.argv[1:] != ["freeze"]:
        raise SystemExit("Explicit BASE-only freeze required")
    FIXTURE.write_text(json.dumps(produce(), separators=(",", ":")) + "\n", encoding="utf-8")
    print(len(json.loads(FIXTURE.read_text(encoding="utf-8"))["records"]), FIXTURE.stat().st_size)
