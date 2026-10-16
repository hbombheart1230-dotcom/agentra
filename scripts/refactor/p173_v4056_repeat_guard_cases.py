"""P15-058 Gate A: separate BASE-first `repeat_guard` / compatibility cases (immutable V4 318-case fixture untouched).

Covers the REAL consumed history key `persisted_state.recent_monitor_blocks`, the NESTED policy key
`policy["scanner_repeat_guard"]`, repeat_count > 0 for selections and blocks, absent/default, malformed history,
clock/cooldown edges, penalty 0 / non-zero / capped, input mutability, exception type, JSON key order, and the number of
calls to the (wrapped, real) Monitor entry-signal evaluator made by the compatibility wrapper.

  generate <out>   (run once on the pinned BASE tree)      compute <out>   (current tree)
"""
from __future__ import annotations

import copy
import json
import os
import shutil
import sys
import tempfile
import time as _time
from pathlib import Path

NOW = 1_800_000_000
SEL = [{"symbol": "005930", "epoch": NOW - 30}, {"symbol": "005930", "epoch": NOW - 90}, {"symbol": "000660", "epoch": NOW - 4000},
       {"symbol": "bad"}, "bad"]
BLK = [{"symbol": "005930", "reason": "spread_too_wide", "epoch": NOW - 60}, {"symbol": "005930", "reason": "volume", "epoch": NOW - 120},
       {"symbol": "005930", "reason": "x", "epoch": NOW - 5000}, {"symbol": "000660", "reason": "spread", "epoch": NOW - 10},
       {"symbol": "005930", "reason": "", "epoch": NOW - 1}, {"symbol": "", "reason": "r", "epoch": NOW}, {"symbol": "005930", "reason": "r"}, 5]
STATES = {
    "blocks_and_selects": {"now_epoch": NOW, "persisted_state": {"recent_scanner_selected": SEL, "recent_monitor_blocks": BLK}},
    "blocks_only": {"now_epoch": NOW, "persisted_state": {"recent_monitor_blocks": BLK}},
    "empty_lists": {"now_epoch": NOW, "persisted_state": {"recent_scanner_selected": [], "recent_monitor_blocks": []}},
    "absent_key": {"now_epoch": NOW, "persisted_state": {}},
    "malformed_blocks": {"now_epoch": NOW, "persisted_state": {"recent_monitor_blocks": "bad"}},
    "future_epoch": {"now_epoch": NOW, "persisted_state": {"recent_monitor_blocks": [{"symbol": "005930", "reason": "r", "epoch": NOW + 500}]}},
    "boundary_epoch": {"now_epoch": NOW, "persisted_state": {"recent_monitor_blocks": [{"symbol": "005930", "reason": "r", "epoch": NOW - 900}],
                                                              "recent_scanner_selected": [{"symbol": "005930", "epoch": NOW - 1800}]}},
    "recent_trade": {"now_epoch": NOW, "persisted_state": {"last_trade_symbol": "005930", "last_trade_epoch": NOW - 600,
                                                           "recent_scanner_selected": SEL}},
    "no_clock_key": {"persisted_state": {"recent_monitor_blocks": BLK, "recent_scanner_selected": SEL}},
}
POLICIES = {
    "none": None,
    "empty": {},
    "nested_default": {"scanner_repeat_guard": {}},
    "nested_tuned": {"scanner_repeat_guard": {"lookback_sec": 300, "per_hit_penalty": 0.05, "max_penalty": 0.4, "streak_threshold": 1,
                                              "streak_penalty": 0.1, "blocker_lookback_sec": 600, "blocker_per_hit_penalty": 0.04,
                                              "history_limit": 10}},
    "nested_capped": {"scanner_repeat_guard": {"per_hit_penalty": 0.5, "max_penalty": 0.12, "blocker_per_hit_penalty": 0.5}},
    "nested_zero": {"scanner_repeat_guard": {"per_hit_penalty": 0, "blocker_per_hit_penalty": 0, "recent_trade_penalty": 0, "streak_penalty": 0}},
    "nested_bad": {"scanner_repeat_guard": {"lookback_sec": "x", "per_hit_penalty": None, "history_limit": -1}},
    "nested_not_dict": {"scanner_repeat_guard": "bad"},
    "top_level_only_ignored": {"lookback_sec": 1, "per_hit_penalty": 9.0},
    "disabled_window": {"scanner_repeat_guard": {"lookback_sec": 0, "blocker_lookback_sec": 0}},
}
PEN_POLICIES = ("none", "nested_default", "nested_tuned", "nested_capped", "nested_zero", "nested_bad", "top_level_only_ignored")
FEAT = {"return20": 0.05, "ma20_gap": 0.02, "adx14": 30, "rolling_drawdown20": -0.04, "gap_pct": 0.01}
METR = {"change_pct": 3.2, "trading_value": 5e9, "volume": 1e6, "spread_bps": 8}


def _cases():
    c = []
    for sn in STATES:
        c.append(("_scanner_recent_block_history", [sn], {}))
        c.append(("_scanner_recent_selection_history", [sn], {}))
        for pn in PEN_POLICIES:
            for sym in ("005930", "999999"):
                c.append(("_repeat_symbol_penalty", [sn], {"symbol": sym, "pn": pn}))
                c.append(("_repeat_blocker_cooldown_penalty", [sn], {"symbol": sym, "pn": pn}))
    for pn in POLICIES:
        c.append(("_resolve_scanner_repeat_guard_policy", [], {"pn": pn}))
    for pol in (None, {}, {"enabled": True}):
        for ft, m in ((FEAT, METR), ({}, {})):
            c.append(("_compute_entry_compatibility_signal", [], {"symbol": "005930", "feature_row": ft, "metrics": m,
                                                                   "candidate_rows": [{"symbol": "005930"}], "current_price": 70000.0,
                                                                   "policy": pol, "bias_context": {}}))
    return c


def compute():
    import importlib
    node = importlib.import_module("graphs.nodes.scanner_node")
    saved = {k: os.environ.pop(k) for k in [k for k in os.environ if k.startswith("SCANNER_")]}
    cwd = os.getcwd()
    tmp = Path(tempfile.mkdtemp(prefix="p058_"))
    real_time, real_eval = _time.time, node.evaluate_intraday_entry_signal
    calls = []

    def counting(*a, **k):
        calls.append(1)
        return real_eval(*a, **k)
    _time.time = lambda: float(NOW)
    node.evaluate_intraday_entry_signal = counting
    rows = []
    try:
        os.chdir(tmp)
        for fn, args, kwargs in _cases():
            args, kwargs = copy.deepcopy(args), copy.deepcopy(kwargs)
            if "pn" in kwargs:
                pol = copy.deepcopy(POLICIES[kwargs.pop("pn")])
                if fn == "_resolve_scanner_repeat_guard_policy":
                    args = [pol]
                else:
                    kwargs["policy"] = pol
            if fn.startswith(("_repeat", "_scanner_recent")):
                args = [copy.deepcopy(STATES[args[0]])] + args[1:]
            before = copy.deepcopy((args, kwargs))
            del calls[:]
            try:
                res = {"ok": getattr(node, fn)(*args, **kwargs)}
            except Exception as exc:  # noqa: BLE001
                res = {"exc": type(exc).__name__, "msg": str(exc)[:160]}
            res["mutated_inputs"] = (args, kwargs) != before
            res["monitor_eval_calls"] = len(calls)
            rows.append({"fn": fn, "args": json.loads(json.dumps(args)), "kwargs": json.loads(json.dumps(kwargs)),
                         "result": json.loads(json.dumps(res, default=repr))})
    finally:
        node.evaluate_intraday_entry_signal = real_eval
        _time.time = real_time
        os.chdir(cwd)
        shutil.rmtree(tmp, ignore_errors=True)
        os.environ.update(saved)
    return rows


if __name__ == "__main__":
    rows = compute()
    Path(sys.argv[2]).write_text(json.dumps({"cases": rows}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(sys.argv[1].upper(), len(rows))
