"""Bounded BASE-only replay of empty observations and exit labels, never guards."""
from __future__ import annotations

import ast
import hashlib
import json
import sys
import types
from pathlib import Path

import work_monitor_current_tree as T
from work_monitor_body_replay import observe

SPECS = {
    "m003": ("libs/runtime/intraday_monitor_signals.py", (
        "_empty_entry_transition_trace", "_empty_monitor_signal_evidence",
        "_empty_monitor_policy_interpretation", "_empty_monitor_policy_interpreter_trace",
        "_empty_monitor_policy_alignment_summary", "_empty_monitor_policy_aware_gating",
        "_empty_chart_structure_decision_hint", "_empty_human_chart_detail_context")),
    "m004": ("libs/runtime/monitor_exit/reasons.py", ("friendly_exit_axis", "monitor_watch_axes")),
}
RECLAIM = {"_RECLAIM_TUNING_VERSION", "_RECLAIM_TUNING_SCOPE", "_RECLAIM_NEAR_READY_DISTANCE_MIN_BASE"}


def baseline(batch):
    path, names = SPECS[batch]
    tree = T._tree(T.base_source(path))
    wanted = set(names) | ({"_build_monitor_signal_evidence", "_to_float", "_clamp_score", "_entry_quality_tier"} if batch == "m003" else {"_is_trueish"})
    selected = []
    for n in tree.body:
        if isinstance(n, ast.ImportFrom) and n.module in {"__future__", "typing"}:
            selected.append(n)
        elif isinstance(n, ast.FunctionDef) and n.name in wanted:
            selected.append(n)
        elif isinstance(n, ast.Assign) and any(isinstance(a, ast.Name) and a.id in RECLAIM for a in n.targets):
            ast.literal_eval(n.value)
            selected.append(n)
    if batch == "m004":
        numeric = T._tree(T.base_source("libs/runtime/monitor_exit/numeric.py"))
        selected += [n for n in numeric.body if isinstance(n, ast.FunctionDef) and n.name == "to_float"]
    tree.body = selected
    module = types.ModuleType("_monitor_observation_base_" + batch)
    exec(compile(tree, path, "exec"), module.__dict__)
    return module


def inputs(name):
    if name == "_empty_monitor_signal_evidence":
        for threshold in (3.0, -1, 0, 1, None, "bad", []):
            yield {"score_threshold": threshold}
    elif name.startswith("_empty_"):
        yield {}
    elif name == "friendly_exit_axis":
        for value in (None, "", "  ", "stop_loss", " STOP_loss ", "mixed__Label", "unicode_한글", [1], 0):
            yield {"reason": value}
    elif name == "monitor_watch_axes":
        for value in (None, [], "bad", {}, {"trend_strength_floor": -0.1},
                      {"risk_reward_take_profit_r": 1, "risk_reward_take_profit_rungs": [1]},
                      {"cost_aware_profit_floor_enabled": "yes", "cost_aware_profit_floor_pct": 0.01},
                      {"cost_aware_profit_floor_enabled": False, "cost_aware_profit_floor_pct": 0.01}):
            yield {"thresholds": value}
        for field in ("hard_stop_pct", "stop_loss_pct", "take_profit_pct", "partial_take_profit_pct",
                      "risk_reward_take_profit_r", "vwap_extension_take_profit_pct", "resistance_take_profit_near_pct",
                      "volume_exhaustion_take_profit_min_pct", "opening_gap_profit_take_min_pct", "profit_time_stop_sec",
                      "trailing_stop_pct", "peak_drawdown_exit_pct", "vwap_breakdown_pct", "intraday_low_break_pct",
                      "trend_strength_floor", "vol_expansion_ratio", "news_shock_threshold", "use_eod_flat",
                      "profit_ladder_levels_pct", "risk_reward_take_profit_rungs"):
            for value in (0, 1, "bad", [1]):
                yield {"thresholds": {field: value}}
    else:
        raise AssertionError(name)


def produce(batch):
    path, names = SPECS[batch]
    module = baseline(batch)
    rows = [{"id": name + ":" + str(i), "function": name, "input": data,
             "expected": observe(getattr(module, name), data)}
            for name in names for i, data in enumerate(inputs(name))]
    sources = [path] + (["libs/runtime/monitor_exit/numeric.py"] if batch == "m004" else [])
    return {"schema": "monitor." + batch + ".frozen.v1", "BASE": T.BASE, "python": sys.version,
            "producer_sha256": hashlib.sha256(Path(__file__).read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
            "source_sha256": {p: hashlib.sha256(T.base_source(p).encode()).hexdigest() for p in sources}, "records": rows}


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] != "freeze" or sys.argv[2] not in SPECS:
        raise SystemExit("Explicit BASE-only batch freeze required")
    batch = sys.argv[2]
    target = T.ROOT / ("tests/fixtures/work_monitor/" + batch + ".json")
    target.write_text(json.dumps(produce(batch), ensure_ascii=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print(batch, len(json.loads(target.read_text(encoding="utf-8"))["records"]), target.stat().st_size)
