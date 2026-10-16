"""V4-056 frozen-case generator/replayer for the five relocated Scanner policy modules.

Calls the PUBLIC `graphs.nodes.scanner_node` wrappers (original signatures, injected `facade`) with deterministic inputs
and records canonical-JSON results or exception type/message, plus a mutation check (inputs are deep-compared before/after
so aliasing/mutation behavior is frozen too). `generate` runs once on the pinned BASE tree (PYTHONPATH = git archive of
the BASE commit); the test re-runs `compute` on the current tree. Offline: the SCANNER_* env keys read by the bodies are
cleared (defaults) or set per case, the clock is the state-injected `now_epoch`, cwd is a disposable directory.

  generate <out.json>     compute <out.json>
"""
from __future__ import annotations

import copy
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

NOW = 1_800_000_000
ENV_CASES = [{}, {"SCANNER_REPEAT_LOOKBACK_SEC": "60", "SCANNER_REPEAT_SYMBOL_PENALTY": "0.5", "SCANNER_REPEAT_HISTORY_LIMIT": "2"},
             {"SCANNER_REPEAT_STREAK_THRESHOLD": "x", "SCANNER_REPEAT_BLOCK_LOOKBACK_SEC": "-5"}]
POLICIES = [None, {}, {"lookback_sec": 120, "per_hit_penalty": "0.2", "max_penalty": 0.15, "streak_threshold": 1},
            {"lookback_sec": "bad", "history_limit": 0}, {"enabled": False}]
HIST = [{"symbol": "005930", "epoch": NOW - 30}, {"symbol": " 005930 ", "epoch": NOW - 90}, {"symbol": "000660", "epoch": NOW - 5000},
        {"symbol": "", "epoch": NOW}, {"symbol": "005930", "epoch": 0}, "bad", {"symbol": "035420", "epoch": NOW - 10}]
BHIST = [{"symbol": "005930", "reason": "spread_too_wide", "epoch": NOW - 60}, {"symbol": "005930", "reason": "x", "epoch": NOW - 10},
         {"symbol": "000660", "reason": "volume", "epoch": NOW - 4000}, "bad", {"symbol": "005930", "epoch": NOW}]
STATES = [{}, {"now_epoch": NOW}, {"now_epoch": NOW, "persisted_state": {"recent_scanner_selected": HIST, "recent_scanner_blocked": BHIST,
                                                                           "last_trade_symbol": "005930", "last_trade_epoch": NOW - 600}},
          {"now_epoch": NOW, "persisted_state": {"recent_scanner_selected": "bad"}}]
ROWS = [{"symbol": "A", "blocker_family": "spread", "adjusted_score": 0.6, "risk_score": 0.2},
        {"symbol": "B", "blocker_families": ["spread", "volume"], "adjusted_score": 0.5},
        {"symbol": "C", "reasons": ["liquidity_gap"], "adjusted_score": 0.4}, {"symbol": "D"}, "bad"]
FEAT = [{}, {"return20": 0.05, "ma20_gap": 0.02, "adx14": 30, "rolling_drawdown20": -0.04, "gap_pct": 0.01},
        {"return20": -0.2, "ma20_gap": 0.2, "ma60_gap": 0.1, "trend_strength": 0.6, "volume_spike20": 3, "cross_section_rank": 0.9}]
METRICS = [{}, {"change_pct": 3.2, "trading_value": 5e9, "volume": 1e6, "spread_bps": 8}, {"change_pct": "bad", "spread_bps": -1}]


def _cases():
    c = []
    for st in STATES:
        c.append(("_scanner_recent_selection_history", [st], {}))
        c.append(("_scanner_recent_block_history", [st], {}))
        c.append(("_extract_scanner_guidance", [st], {}))
        for sym in ("005930", " 005930", "000660", "", "zzz"):
            for pol in POLICIES[:4]:
                c.append(("_repeat_symbol_penalty", [st], {"symbol": sym, "policy": pol}))
                c.append(("_repeat_blocker_cooldown_penalty", [st], {"symbol": sym, "policy": pol}))
    for pol in POLICIES:
        c.append(("_resolve_scanner_repeat_guard_policy", [pol], {}))
    for v in (None, "", "Spread_Too_Wide", "volume", "liquidity gap", 12, {"a": 1}, "mixed", "no_signal"):
        c.append(("_normalize_scanner_blocker_family", [v], {}))
        c.append(("_extract_monitor_entry_block_reason", [v if isinstance(v, dict) else {"reason": v, "guard_reason": v}], {}))
    for r in ROWS:
        c.append(("_candidate_blocker_families", [r], {}))
    for agg in (0.0, 0.5, 1.0, 2.5):
        c.append(("_apply_blocker_family_concentration_overlay", [ROWS], {"scan_aggressiveness": agg}))
        c.append(("_apply_blocker_family_concentration_overlay", [[]], {"scan_aggressiveness": agg}))
    for model in ({}, {"avg_pnl_pct": -3.0, "win_rate": 0.2, "trade_count": 9}, {"avg_pnl_pct": 4.0, "win_rate": 0.8, "trade_count": 12,
                                                                               "dominant_playbook": "breakout"}, {"trade_count": "x"}):
        for pb in ("", "breakout", "pullback"):
            c.append(("_compute_symbol_prior_adjustment", [], {"symbol_model": model, "playbook": pb, "current_day": "2026-10-16"}))
    for w in ({}, {"trading_value": 1.0, "volatility_penalty": 1.0, "momentum": 1.0}, None):
        for bias in ("", "large_cap", "leader", "unknown"):
            for pr in ([], ["momentum", "Value"], None):
                c.append(("_apply_scanner_guidance_weights", [w], {"playbook": "breakout", "scanner_bias": bias, "scanner_priority": pr,
                                                                    "trade_aggressiveness": "high", "risk_tone": "risk_off"}))
    for ft in FEAT:
        for m in METRICS:
            for ctx in ({}, {"scanner_bias": "leader"}):
                c.append(("_compute_structured_scanner_bias", [], {"symbol": "005930", "feature_row": ft, "metrics": m, "bias_context": ctx}))
    st = STATES[2]
    for cc in ({}, {"applied_policy": {"a": 1}}, "bad"):
        for mp in ({}, {"entry_policy": {"b": 2}}):
            c.append(("_build_scanner_monitor_policy_input", [], {"state": st, "commander_context": cc if isinstance(cc, dict) else {},
                                                                  "monitor_policy": mp}))
    for pb in ("", " Breakout ", "PULLBACK"):
        c.append(("_build_scanner_monitor_frame", [], {"playbook": pb, "monitor_guidance": " Hold ", "risk_tone": "", "trade_aggressiveness": None}))
    for ft in FEAT:
        for m in METRICS:
            for pol in (None, {}, {"enabled": True}):
                c.append(("_compute_entry_compatibility_signal", [], {"symbol": "005930", "feature_row": ft, "metrics": m,
                                                                       "candidate_rows": [{"symbol": "005930"}], "current_price": 70000.0,
                                                                       "policy": pol, "bias_context": {}}))
    for base in ({}, {"entry_compatibility_score": 0.4, "compatibility_bias": 0.01}):
        for ov in (None, {}, {"entry_compatibility_score": 0.9}, "bad"):
            c.append(("_merge_mock_compatibility_override", [base], {"override": ov}))
    return c


def compute():
    import importlib
    node = importlib.import_module("graphs.nodes.scanner_node")
    keys = [k for k in os.environ if k.startswith("SCANNER_")]
    saved = {k: os.environ.pop(k) for k in keys}
    cwd = os.getcwd()
    tmp = Path(tempfile.mkdtemp(prefix="v4056_"))
    rows = []
    import time as _time
    real_time = _time.time
    _time.time = lambda: float(NOW)  # frozen wall clock for states without an injected now_epoch
    try:
        os.chdir(tmp)
        for idx, (fn, args, kwargs) in enumerate(_cases()):
            env = ENV_CASES[idx % len(ENV_CASES)] if fn.startswith(("_repeat", "_resolve_scanner_repeat", "_scanner_recent")) else {}
            for k in [k for k in os.environ if k.startswith("SCANNER_")]:
                os.environ.pop(k)
            os.environ.update(env)
            a, kw = json.loads(json.dumps(args)), json.loads(json.dumps(kwargs))
            before = copy.deepcopy((a, kw))
            try:
                res = {"ok": getattr(node, fn)(*a, **kw)}
            except Exception as exc:  # noqa: BLE001
                res = {"exc": type(exc).__name__, "msg": str(exc)[:160]}
            res["mutated_inputs"] = (a, kw) != before
            rows.append({"fn": fn, "env": env, "args": args, "kwargs": kwargs,
                         "result": json.loads(json.dumps(res, sort_keys=False, default=repr))})
    finally:
        _time.time = real_time
        os.chdir(cwd)
        shutil.rmtree(tmp, ignore_errors=True)
        for k in [k for k in os.environ if k.startswith("SCANNER_")]:
            os.environ.pop(k)
        os.environ.update(saved)
    return rows


if __name__ == "__main__":
    rows = compute()
    Path(sys.argv[2]).write_text(json.dumps({"cases": rows}, ensure_ascii=False, indent=None, separators=(",", ":")), encoding="utf-8")
    print(sys.argv[1].upper(), len(rows))
