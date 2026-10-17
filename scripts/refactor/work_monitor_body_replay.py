"""Small BASE-first deterministic observation-view corpus; no runtime/IO runner."""
from __future__ import annotations

import ast
import copy
import hashlib
import importlib
import json
import sys
import types
from pathlib import Path

import work_monitor_contracts as O
import work_monitor_current_tree as T

PATHS = ("libs/runtime/monitor_exit/selected_snapshot.py", "libs/runtime/monitor_entry_state.py")
FIXTURE = T.ROOT / "tests/fixtures/work_monitor/m002.json"


def baseline(path):
    tree = T._tree(T.base_source(path))
    # Imports outside typing/future are not executed. The selected functions and
    # the scalar converter have no other runtime globals; test that closure.
    names = set(T.BODY_MOVES[path]["functions"]) | {"_optional_float"}
    tree.body = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names
                 or isinstance(n, ast.ImportFrom) and n.module in {"typing", "__future__"}]
    module = types.ModuleType("_monitor_m002_base_" + Path(path).stem)
    exec(compile(tree, path, "exec"), module.__dict__)
    return module


def inputs(name):
    if name == "feature_alias_map":
        for row in ({}, {"rsi14": 20, "engine_rsi14": None, "volume_ratio": 1, "day_high": [2]},
                    {"rsi14": 40, "high_price": 100, "execution_strength": {"nested": [1]}}):
            for quote in (None, {}, {"price": None, "cur": 100, "volume": [3], "value": 40}):
                yield {"feature_row": row, "quote": quote}
        yield {"feature_row": None, "quote": None}
        yield {"feature_row": "malformed", "quote": {}}
    elif name == "feature_context_from_state":
        for state in ({}, None, {"market_context": None}, {"global_sentiment": {"score": 0}},
                      {"market_context": {"global_sentiment": 0, "market_breadth": [1], "index_trend": "", "realized_volatility": None}, "global_sentiment": {"score": 8}}):
            yield {"state": state}
    elif name == "monitor_posture_for_cycle":
        for intents in ([], [{"side": "BUY"}], [{"side": "buy"}, {"side": " sell "}], [None], ["bad"]):
            for count in (0, 1):
                yield {"open_position_count": count, "intents": intents, "exit_info": {"triggered": count == 0}, "buy_blocked_open_position": False, "buy_blocked_post_exit_cooldown": True}
    else:
        for info in ({}, None, {"metrics": None}, {"metrics": {"volume_ratio": "bad"}},
                     {"metrics": {"volume_ratio": "1.5", "extended_from_vwap_pct": -0.1}, "thresholds": {"volume_ratio_min": 2}, "threshold_margins": {"breakout_gap_pct": {"actual": 0.2}}, "triggered": True, "primary_failure_axis": "", "transition_readiness_score": {"nested": [1]}}):
            row = {"entry_info": info}
            if name == "build_monitor_entry_transition_trace":
                for previous in ({}, None, {"entry_state": {"volume_ratio": 1, "extended_from_vwap_pct": -0.2, "breakout_gap_pct": 0.1, "triggered": False, "current_blocking_axis": "volume"}}):
                    yield dict(row, previous_monitor_state=previous)
            else:
                yield row


def observe(fn, data):
    values = copy.deepcopy(data)
    before = O.wire(values)
    result, error = None, None
    try:
        result = fn(**values)
    except Exception as exc:
        error = [type(exc).__name__, str(exc)]
    evidence = {"result": O.wire(result), "before": before, "after": O.wire(values),
                "error": error, "aliases": O.alias_paths([values, result])}
    return {"sha256": O.sha(evidence), "error": error, "mutated": before != evidence["after"]}


def produce():
    records = []
    for path in PATHS:
        module = baseline(path)
        for name in T.BODY_MOVES[path]["functions"]:
            for i, data in enumerate(inputs(name)):
                records.append({"id": name + ":" + str(i), "path": path, "function": name,
                                "input": data, "expected": observe(getattr(module, name), data)})
    return {"schema": "monitor.m002.frozen.v1", "BASE": T.BASE, "python": sys.version,
            "producer_sha256": hashlib.sha256(Path(__file__).read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
            "source_sha256": {p: hashlib.sha256(T.base_source(p).encode()).hexdigest() for p in PATHS}, "records": records}


if __name__ == "__main__":
    if sys.argv[1:] != ["freeze"]:
        raise SystemExit("Explicit BASE-first freeze only")
    FIXTURE.write_text(json.dumps(produce(), separators=(",", ":")) + "\n", encoding="utf-8")
    print(len(json.loads(FIXTURE.read_text(encoding="utf-8"))["records"]))
