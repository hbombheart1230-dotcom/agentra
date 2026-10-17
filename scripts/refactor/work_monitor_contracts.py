"""Offline Monitor role proof; only synthetic inputs, no runtime/Broker/LLM imports.

Freeze reads implementation bytes directly from the pinned runtime BASE Git object.
Replay imports the FEATURE canonical owner. Outputs include ordered keys, exceptions,
input mutation, container aliases and the exact stub-facade call stream. This does
not replace the existing T4-B native runtime/effect replay or real report parity.
"""
from __future__ import annotations

import ast
import copy
import hashlib
import importlib
import inspect
import json
import platform
import subprocess
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "docs/refactor/work_projects/evidence/monitor/path_ledger.json"
FIXTURE = ROOT / "tests/fixtures/work_monitor/contracts.json"
BASE = "d773709ba2f70471fad9badba4f92400f7818319"


def ledger():
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def git_bytes(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)


def sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, separators=(",", ":"),
                                     allow_nan=False).encode("utf-8")).hexdigest()


def wire(value):
    if isinstance(value, dict):
        return ["dict", [[k, wire(v)] for k, v in value.items()]]
    if isinstance(value, (tuple, list)):
        return [type(value).__name__, [wire(v) for v in value]]
    return value


def alias_paths(value):
    seen, aliases = {}, []

    def visit(obj, path):
        if not isinstance(obj, (dict, list, tuple)):
            return
        if id(obj) in seen:
            aliases.append([seen[id(obj)], path])
            return
        seen[id(obj)] = path
        seq = obj.items() if isinstance(obj, dict) else enumerate(obj)
        for key, child in seq:
            visit(child, path + [key])
    visit(value, [])
    return aliases


class StubFacade:
    """Fixed allowlist, fake read-model callbacks only; unknown capability fails."""

    SKILL_CONTRACT_VERSION = "synthetic-monitor.v1"
    BUILDERS = frozenset(("_build_monitor_policy_trace", "build_monitor_no_trade_surface",
                          "build_scanner_monitor_handoff_surface", "build_factor_snapshot_from_monitor_entry",
                          "build_entry_quant_decision", "build_entry_quant_enforcement", "build_exit_quant_decision"))

    def __init__(self):
        self.calls = []

    def _to_float(self, value, default=0.0):
        self.calls.append(["_to_float", copy.deepcopy(value), default])
        try:
            return float(value)
        except (TypeError, ValueError):
            return float(default)

    def _to_int(self, value, default=0):
        self.calls.append(["_to_int", copy.deepcopy(value), default])
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return int(default)

    def __getattr__(self, name):
        if name not in self.BUILDERS:
            raise AssertionError(f"unapproved mock facade capability: {name}")

        def build(*args, **kwargs):
            self.calls.append([name, copy.deepcopy(args), copy.deepcopy(kwargs)])
            # Fresh outer mapping, deliberately shared nested input for alias coverage.
            return {"stub": name, "policy_ref": {}, "input_alias": kwargs.get("entry_info", {})}
        return build


def base_module(row):
    source = git_bytes(row["source"])
    tree = ast.parse(source)
    # Never run arbitrary imports or top-level runtime code from the baseline.
    if any(not isinstance(n, (ast.FunctionDef, ast.ImportFrom, ast.Expr)) for n in tree.body):
        raise AssertionError("unexpected baseline owner structure")
    if any(isinstance(n, ast.ImportFrom) and n.module != "__future__" for n in tree.body):
        raise AssertionError("unexpected baseline dependency")
    mod = types.ModuleType("_work_monitor_base_" + Path(row["source"]).stem)
    exec(compile(source, row["source"], "exec"), mod.__dict__)
    return mod


def default_kwargs(fn):
    numeric = {"open_position_count": 1, "max_positions": 3, "post_exit_cooldown_sec": 30,
               "post_exit_cooldown_remaining_sec": 0, "entry_quality_score": 0.7,
               "breakout_score": 0.2, "etf_deviation_entry_score": 0.123456}
    strings = {"current_posture", "current_reason", "previous_posture", "previous_reason",
               "final_entry_decision", "buy_skipped_reason", "monitor_symbol", "entry_symbol",
               "scanner_selected_symbol", "entry_candidate_symbol", "entry_final_symbol",
               "position_focus_symbol", "monitor_output_symbol", "monitor_focus_mode",
               "entry_policy_origin", "monitor_entry_exit_reason", "entry_condition_path",
               "entry_quality_tier", "entry_quality_path"}
    sequences = {"fallback_reasons", "intents", "held_symbols_for_entry", "pending_buy_symbols_for_entry",
                 "triggered_rules", "blocked_rules", "reason_chain", "entry_hard_gate_blockers"}
    out = {}
    for name in inspect.signature(fn).parameters:
        if name == "facade":
            continue
        if name in numeric:
            out[name] = numeric[name]
        elif name in strings:
            out[name] = "SYN001" if "symbol" in name else "WAIT"
        elif name in sequences:
            out[name] = []
        elif name.startswith(("buy_blocked", "block_buy", "max_positions_reached")) or name in {
                "buy_submitted", "sell_submitted", "state_changed", "entry_hard_gate_passed"}:
            out[name] = False
        else:
            out[name] = {}
    return out


def cases_for(fn):
    basic = default_kwargs(fn)
    yield "empty", basic
    rich = copy.deepcopy(basic)
    payload = {"symbol": "SYN001", "reason": "synthetic_reason", "guard_reason": "synthetic_guard",
               "triggered": True, "enabled": True, "evaluated": True, "pattern": "mock_pattern",
               "guard_blocked": True, "sell_guard_blocked": True, "sell_guard_reason": "mock_sell_guard",
               "exit_signal_detected": True, "metrics": {"current_price": 101.5, "nested": ["한글", 2]},
               "confidence": "0.75", "failed_checks": ["guard_a", "guard_b"],
               "thresholds": {"stop_loss_pct": 0.02}, "score_breakdown": {"a": 1.0},
               "policy_ref": {"policy_source": "synthetic"}, "selected_symbol": "SYN002"}
    for name, val in rich.items():
        if isinstance(val, dict) and name != "score_breakdown":
            rich[name] = copy.deepcopy(payload)
    if "all_pos_map" in rich:
        rich["all_pos_map"] = {"SYN001": {"qty": 2, "avg_price": 100.0}}
    if "score_breakdown" in rich:
        rich["score_breakdown"] = {"a": 1.5, "b": 1.6}
    if "intents" in rich:
        rich["intents"] = [{"side": "BUY", "symbol": "SYN001", "qty": 2}]
    if "state" in rich:
        rich["state"] = {"run_id": "synthetic", "monitor_output": {"intent_side": "BUY"},
                         "peak_update_events": [{"price": 103}], "ranked_candidates": [{"symbol": "SYN001"}]}
    for name in ("held_symbols_for_entry", "pending_buy_symbols_for_entry", "triggered_rules", "blocked_rules"):
        if name in rich:
            rich[name] = ["SYN002", "SYN001", "SYN002"]
    yield "rich", rich
    names = list(basic)
    if names:
        for bad in (None, "malformed"):
            mutated = copy.deepcopy(basic)
            mutated[names[0]] = bad
            yield "first_" + ("null" if bad is None else "scalar"), mutated
    # Explicit branch precedence: ordered display reasons, no trading selection change.
    for name in ("buy_blocked_post_exit_cooldown", "buy_blocked_closeout_window", "buy_submitted", "sell_submitted"):
        if name in basic:
            d = copy.deepcopy(basic)
            d[name] = True
            yield name, d


def observe(fn, inputs):
    values = copy.deepcopy(inputs)
    before = wire(values)
    facade = StubFacade()
    kw = dict(values)
    if "facade" in inspect.signature(fn).parameters:
        kw["facade"] = facade
    result, error = None, None
    try:
        result = fn(**kw)
    except Exception as exc:  # Preserve BASE exceptions; never hide them as successful outputs.
        error = [type(exc).__name__, str(exc)]
    detail = {"result": wire(result), "before": before, "after": wire(values),
              "exception": error, "aliases": alias_paths([values, result]), "calls": wire(facade.calls)}
    return {"sha256": sha(detail), "exception": error, "mutated": before != wire(values),
            "alias_count": len(detail["aliases"]), "facade_calls": len(facade.calls)}


def freeze():
    records, sources = [], {}
    for row in ledger()["maps"]:
        mod = base_module(row)
        sources[row["source"]] = hashlib.sha256(git_bytes(row["source"])).hexdigest()
        for name in row["symbols"]:
            fn = getattr(mod, name)
            for variant, inp in cases_for(fn):
                records.append({"id": Path(row["source"]).stem + ":" + name + ":" + variant,
                                "source": row["source"], "function": name, "input": inp,
                                "expected": observe(fn, inp)})
    doc = {"schema": "work.monitor.synthetic_frozen.v1", "base_sha": BASE,
           "producer": {"python": sys.version, "platform": platform.platform(),
                        "tool_sha256": hashlib.sha256(Path(__file__).read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
                        "tool_hash_encoding": "Git-style LF UTF-8 source bytes"},
           "source_sha256": sources, "records": records}
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return {"records": len(records), "bytes": FIXTURE.stat().st_size,
            "exceptions": sum(r["expected"]["exception"] is not None for r in records),
            "sha256": hashlib.sha256(FIXTURE.read_bytes()).hexdigest()}


def replay():
    doc = json.loads(FIXTURE.read_text(encoding="utf-8"))
    maps = {r["source"]: r for r in ledger()["maps"]}
    bad = []
    for record in doc["records"]:
        path = maps[record["source"]]["destination"]
        mod = importlib.import_module(path[:-3].replace("/", "."))
        actual = observe(getattr(mod, record["function"]), record["input"])
        if actual != record["expected"]:
            bad.append({"id": record["id"], "actual": actual, "expected": record["expected"]})
    return {"records": len(doc["records"]), "mismatches": bad}


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    command = sys.argv[1] if len(sys.argv) > 1 else "replay"
    result = freeze() if command == "freeze" else replay()
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(bool(result.get("mismatches")))
