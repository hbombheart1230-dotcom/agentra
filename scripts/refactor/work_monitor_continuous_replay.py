"""Synthetic BASE-first proof for registered continuous Monitor whole-blob moves.

The BASE bodies are read from Git, not from FEATURE. Entry callbacks exercise the
unchanged real in-memory skill/ETF/config extractors. Network/runtime execution is
not part of this tool; nothing here invokes a Broker, LLM, writer or skill runner.
"""
from __future__ import annotations

import ast
import copy
import hashlib
import importlib
import inspect
import json
import sys
import types
from pathlib import Path

import work_monitor_contracts as O
import work_monitor_current_tree as T

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/work_monitor/m001.json"


class ReadFacade:
    def __init__(self):
        from graphs.nodes.skill_contracts import extract_market_quotes, extract_minute_ohlcv_by_symbol
        from libs.core.symbols import normalize_symbol
        from libs.runtime.etf_deviation import extract_etf_deviation_signal
        from libs.runtime.monitor_entry_policy_context import resolve_monitor_entry_scoring_config
        self.targets = {"extract_market_quotes": extract_market_quotes,
                        "extract_minute_ohlcv_by_symbol": extract_minute_ohlcv_by_symbol,
                        "_norm_symbol": normalize_symbol,
                        "extract_etf_deviation_signal": extract_etf_deviation_signal,
                        "_resolve_monitor_entry_scoring_config": resolve_monitor_entry_scoring_config}
        self.calls = []

    def __getattr__(self, name):
        if name not in self.targets:
            raise AssertionError("Unapproved Monitor replay callback: " + name)

        def call(*args, **kwargs):
            self.calls.append([name, copy.deepcopy(args), copy.deepcopy(kwargs)])
            return self.targets[name](*args, **kwargs)
        return call


def baseline_module(path):
    source = T.base_source(path)
    tree = ast.parse(source)
    for n in tree.body:
        if isinstance(n, ast.ImportFrom) and n.module in ("__future__", "typing"):
            continue
        if isinstance(n, ast.FunctionDef):
            continue
        if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str):
            continue
        if isinstance(n, ast.Assign):
            ast.literal_eval(n.value)  # fixed text constant only; no top-level effect
            continue
        raise AssertionError("Unexpected baseline module dependency/statement")
    mod = types.ModuleType("_monitor_continuous_base_" + Path(path).stem)
    exec(compile(source, path, "exec"), mod.__dict__)
    return mod


def inputs_for(name, fn):
    if name in ("_to_int", "normalize_status"):
        for i, val in enumerate((None, "", "2.5", -1, True, [], {}, "PARTIAL", "CANCELLED")):
            yield str(i), {"value": val}
    elif name == "derive_order_lifecycle":
        for i, value in enumerate((None, {}, [], "bad")):
            yield "empty" + str(i), {"order_status": value}
        for status in ("", "CANCELLED", "REJECT", "FILLED", "PARTIAL", "WORKING"):
            for filled in (0, 2, 3):
                yield status + str(filled), {"order_status": {"status": status, "filled_qty": filled,
                     "order_qty": 3, "remaining_qty": None, "ord_remnq": 1, "symbol": "MOCK001",
                     "ord_no": "synthetic-only"}}
        yield "remaining_precedence", {"order_status": {"status": "FILLED", "order_qty": 3,
             "filled_qty": 0, "remaining_qty": 2, "ord_remnq": 0, "rmnd_qty": 0}}
    elif name == "build_monitor_exit_payload":
        empty = {p: {} for p in inspect.signature(fn).parameters}
        yield "empty", empty
        for guard in (False, True):
            rich = copy.deepcopy(empty)
            rich["context"] = {"qty": 2, "hold_sec": 60, "now_epoch": 100, "lock_until": 120,
                               "exit_signal_detected": True, "sell_guard_blocked": guard,
                               "sell_guard_reason": "mock_guard" if guard else "", "avg_price": 100.5}
            rich["decision"] = {"evaluated": True, "reason": "stop_loss", "exit_qty": 1,
                                "thresholds": {"stop_loss_pct": 0.02, "nested": [1]}, "partial_exit": True}
            yield "guard" + str(guard), rich
        for key in ("qty", "avg_price", "now_epoch", "lock_until"):
            bad = copy.deepcopy(empty)
            bad["context"][key] = "malformed"
            yield "bad_" + key, bad
        bad = copy.deepcopy(empty)
        bad["decision"] = None
        yield "null_decision", bad
    elif name == "entry_evidence_entry_features_entry_row_source":
        empty = {"state": {}, "policy": {}, "symbol": "MOCK001", "selected": {}, "selected_features": {}}
        yield "empty", empty
        for source in ("minute_ohlcv_by_symbol", "monitor_minute_ohlcv_by_symbol", "intraday_ohlcv_by_symbol"):
            rich = copy.deepcopy(empty)
            rich["state"] = {source: {"MOCK001": [{"close": 100.0, "nested": [1]}]},
                             "market_quote": {"MOCK001": {"price": 100.0}},
                             "applied_policy": {"monitor": {"entry": {"scoring": {"threshold": 4.0}}}}}
            rich["selected_features"] = {"asset_class_detected": "etf", "etf_deviation_pct": -0.015}
            yield source, rich
        for key in ("state", "policy", "selected", "selected_features"):
            bad = copy.deepcopy(empty)
            bad[key] = None
            yield "null_" + key, bad
        for source in ("state", "policy"):
            rich = copy.deepcopy(empty)
            rich[source]["monitor_entry_scoring"] = {"entry_threshold": 5.0}
            yield "scoring_" + source, rich
    else:
        raise AssertionError("No registered replay case producer for " + name)


def observe(fn, inputs):
    values = copy.deepcopy(inputs)
    before = O.wire(values)
    kw = dict(values)
    facade = ReadFacade() if "facade" in inspect.signature(fn).parameters else None
    if facade is not None:
        kw["facade"] = facade
    returned, error = None, None
    try:
        returned = fn(**kw)
    except Exception as exc:
        error = [type(exc).__name__, str(exc)]
    record = {"result": O.wire(returned), "before": before, "after": O.wire(values),
              "exception": error, "aliases": O.alias_paths([values, returned]),
              "calls": O.wire(facade.calls if facade else [])}
    return {"sha256": O.sha(record), "exception": error, "alias_count": len(record["aliases"]),
            "mutated": before != O.wire(values), "callbacks": len(facade.calls) if facade else 0}


def freeze():
    rows, blobs = [], {}
    for old, new in T.WHOLE_MOVES.items():
        mod = baseline_module(old)
        blobs[old] = hashlib.sha256(T.base_source(old).encode("utf-8")).hexdigest()
        funcs = [n.name for n in ast.parse(T.base_source(old)).body if isinstance(n, ast.FunctionDef)]
        for name in funcs:
            fn = getattr(mod, name)
            for variant, data in inputs_for(name, fn):
                rows.append({"id": Path(old).stem + ":" + name + ":" + variant,
                             "legacy": old, "function": name, "input": data, "expected": observe(fn, data)})
    doc = {"schema": "monitor.m001.frozen.v1", "BASE": T.BASE, "producer_python": sys.version,
           "producer_source_sha256": hashlib.sha256(Path(__file__).read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
           "source_sha256": blobs, "records": rows}
    FIXTURE.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return {"records": len(rows), "bytes": FIXTURE.stat().st_size,
            "sha256": hashlib.sha256(FIXTURE.read_bytes()).hexdigest()}


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    if sys.argv[1:] != ["freeze"]:
        raise SystemExit("Only explicit BASE-first freeze is supported")
    print(json.dumps(freeze()))
