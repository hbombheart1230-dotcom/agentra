# RF-014: first safe dynamic rank/reject/NOOP consumers of the scanner owners, driven through the real RF-009 facade
# graphs.nodes.scanner_node (shim libs.runtime.scanner.* -> libs.agents.scanner.*): repeat-symbol rank penalty, blocker-cooldown
# penalty, blocker-family normalisation, candidate base risk. Synthetic State only, tmp cwd, net/sqlite/subprocess/writes blocked.
import os, sys, copy, socket, subprocess, sqlite3, builtins, importlib, tempfile
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL", "SCANNER_REPEAT", "SCANNER_RECENT")): del os.environ[k]
repo = os.getcwd(); sys.path.insert(0, repo)
from pathlib import Path
tmp = Path(tempfile.mkdtemp(prefix="rf014_dyn_")).resolve()
os.environ["EVIDENCE_LEDGER_PATH"] = str(tmp / "ledger.jsonl"); os.environ["EVENT_LOG_PATH"] = str(tmp / "events.jsonl"); os.chdir(tmp)
import ssl, http.client
sn = importlib.import_module("graphs.nodes.scanner_node")
bad = []
def blocked(name):
    def f(*a, **k): bad.append(name); raise OSError("blocked " + name)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("create_connection"); socket.getaddrinfo = blocked("getaddrinfo")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite3.connect")
_open = builtins.open
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+"): bad.append("write_open:" + str(f)); raise OSError("blocked write")
    return _open(f, mode, *a, **k)
builtins.open = gopen
Path.write_text = lambda *a, **k: (bad.append("write_text"), (_ for _ in ()).throw(OSError("blocked")))[1]
Path.mkdir = lambda *a, **k: (bad.append("mkdir"), (_ for _ in ()).throw(OSError("blocked")))[1]
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED: " + m)
import libs.agents.scanner.candidate_risk as cr, libs.runtime.scanner.candidate_risk as cr_shim, libs.agents.scanner.policy.repeat_guard as rg, libs.runtime.scanner.repeat_guard as rg_shim
check(cr is cr_shim and rg is rg_shim, "shim module identity")
NOW = 1_800_000_000
def state(**p): return {"now_epoch": NOW, "persisted_state": p}
sel = [{"symbol": "005930", "epoch": NOW - 100 * i} for i in range(4, 0, -1)]   # 4 recent selections, newest last
# --- repeat symbol penalty
s = state(recent_scanner_selected=sel + ["junk", {"symbol": "", "epoch": 5}, {"symbol": "000660", "epoch": 0}], last_trade_symbol="005930", last_trade_epoch=NOW - 60); s0 = copy.deepcopy(s)
r = sn._repeat_symbol_penalty(s, symbol="005930", policy={})
check(r["repeat_count"] == 4 and r["streak_count"] == 4 and r["recent_trade_same_symbol"] is True and r["history_count"] == 4, "repeat counts %r" % r)
check(abs(r["penalty"] - 0.40) < 1e-9, "penalty capped at max 0.40: %r" % r["penalty"])   # 4*0.06+0.12+0.10=0.46 -> cap 0.40
check(s == s0, "state immutable")
r2 = sn._repeat_symbol_penalty(s, symbol="000660", policy={}); check(r2["penalty"] == 0.0 and r2["repeat_count"] == 0, "other symbol NOOP")
r3 = sn._repeat_symbol_penalty(s, symbol="", policy={}); check(r3["penalty"] == 0.0 and r3["recent_trade_same_symbol"] is False, "blank symbol NOOP")
r4 = sn._repeat_symbol_penalty(state(), symbol="005930", policy={}); check(r4["penalty"] == 0.0 and r4["history_count"] == 0, "empty persisted NOOP")
r5 = sn._repeat_symbol_penalty(state(recent_scanner_selected="x"), symbol="005930", policy={}); check(r5["history_count"] == 0, "non-list history -> empty")
r6 = sn._repeat_symbol_penalty(s, symbol="005930", policy={"scanner_repeat_guard": {"lookback_sec": 0}}); check(r6["repeat_count"] == 0 and r6["streak_count"] == 0, "lookback 0 disables repeats")
r7 = sn._repeat_symbol_penalty(s, symbol="005930", policy={"scanner_repeat_guard": {"per_hit_penalty": -5, "max_penalty": "bad", "streak_threshold": 1, "history_limit": 1}})
check(r7["config"]["per_hit_penalty"] == 0.0 and r7["config"]["streak_threshold"] == 2 and r7["config"]["history_limit"] == 5 and r7["config"]["max_penalty"] == 0.0 and r7["penalty"] == 0.0, "policy clamps: %r" % r7["config"])
os.environ["SCANNER_REPEAT_SYMBOL_PENALTY"] = "0.01"
r8 = sn._repeat_symbol_penalty(s, symbol="005930", policy={}); check(abs(r8["config"]["per_hit_penalty"] - 0.01) < 1e-12, "env override read at use time")
del os.environ["SCANNER_REPEAT_SYMBOL_PENALTY"]
# --- blocker cooldown penalty
blk = [{"symbol": "005930", "reason": "too_extended_from_vwap", "epoch": NOW - 60}, {"symbol": "005930", "reason": "too_extended_from_vwap", "epoch": NOW - 120},
       {"symbol": "005930", "reason": "volume_insufficient", "epoch": NOW - 30}, {"symbol": "005930", "reason": "too_extended_from_vwap", "epoch": NOW - 5000},
       {"symbol": "000660", "reason": "breakout_not_ready", "epoch": NOW - 10}, {"symbol": "005930", "reason": "", "epoch": NOW - 10}, "junk"]
s = state(recent_monitor_blocks=blk); s0 = copy.deepcopy(s)
b = sn._repeat_blocker_cooldown_penalty(s, symbol="005930", policy={})
check(b["reason"] == "too_extended_from_vwap" and b["repeat_count"] == 2 and abs(b["penalty"] - 0.16) < 1e-9, "dominant blocker: %r" % b)
check(abs(sn._repeat_blocker_cooldown_penalty(s, symbol="000660", policy={})["penalty"] - 0.028) < 1e-9, "weight 0.35 reason")
check(sn._repeat_blocker_cooldown_penalty(s, symbol="", policy={})["penalty"] == 0.0, "blank symbol NOOP")
check(sn._repeat_blocker_cooldown_penalty(s, symbol="111111", policy={})["reason"] == "", "unseen symbol NOOP")
check(sn._repeat_blocker_cooldown_penalty(s, symbol="005930", policy={"scanner_repeat_guard": {"blocker_lookback_sec": 0}})["penalty"] == 0.0, "lookback 0 NOOP")
check(sn._repeat_blocker_cooldown_penalty(s, symbol="005930", policy={"scanner_repeat_guard": {"blocker_max_penalty": 0.05}})["penalty"] == 0.05, "blocker cap")
unk = sn._repeat_blocker_cooldown_penalty(state(recent_monitor_blocks=[{"symbol": "005930", "reason": "other_reason", "epoch": NOW - 1}]), symbol="005930", policy={})
check(unk["penalty"] == 0.0 and unk["reason"] == "other_reason", "unweighted reason = 0 penalty")
check(s == s0, "state immutable (blocks)")
# --- blocker family normalisation + candidate families
fam = {v: sn._normalize_scanner_blocker_family(v) for v in ("", " MIXED ", None, "buy_blocked_open_position", "entry_guard_cooldown_x", "pullback_ok", "overextended", "vwap_hold_ok", "volume_ok", "breakout_not_ready", "rebound_ok", "chart_structure_guard", "confidence_gate_ok", "risk_blocked", "unknown", "zzz")}
check(fam == {"": "", " MIXED ": "", None: "", "buy_blocked_open_position": "open_position_guard", "entry_guard_cooldown_x": "cooldown_guard", "pullback_ok": "pullback_timing", "overextended": "overextension_guard", "vwap_hold_ok": "reclaim_readiness",
              "volume_ok": "volume_confirmation", "breakout_not_ready": "breakout_confirmation", "rebound_ok": "rebound_confirmation", "chart_structure_guard": "structure_confirmation", "confidence_gate_ok": "confidence_gate", "risk_blocked": "risk_guard", "unknown": "unknown", "zzz": "other"}, "family map: %r" % fam)
check(sn._candidate_blocker_families({"expected_monitor_block_reason": "pullback_ok", "dominant_block_reason": "pullback_not_mature"}) == ["pullback_timing"], "families dedupe")
check(sn._candidate_blocker_families({"expected_monitor_block_reason": "zzz", "dominant_block_reason": "unknown"}) == [], "unknown/other dropped")
check(sn._candidate_blocker_families("x") == [] and sn._candidate_blocker_families(None) == [], "non-mapping NOOP")
# --- candidate base risk
exp = cr.resolve_candidate_base_risk(scanner_row={"risk_score": 1.7}, candidate={"risk_score": 0.2}); check(exp["risk_score"] == 1.0 and exp["source"] == "scanner_row" and exp["missing_inputs"] == [], "explicit clamp, scanner_row first")
exc = cr.resolve_candidate_base_risk(candidate={"risk_score": "0.4"}); check(exc["risk_score"] == 0.4 and exc["source"] == "candidate", "candidate explicit str->float")
fb = cr.resolve_candidate_base_risk(); check(fb["source"] == "market_data_fallback" and set(fb["missing_inputs"]) == {"atr_ratio", "volatility", "drawdown", "gap", "spread", "volume", "trading_value"} and abs(fb["risk_score"] - (0.12 + 0.18)) < 1e-6, "all-missing fallback %r" % fb["risk_score"])
full = cr.resolve_candidate_base_risk(features={"close_last": 100, "atr14": 8, "volatility20": 0.16, "rolling_drawdown20": -0.16, "gap_pct": 0.2}, quote_metrics={"spread_bps": 100, "volume": 5, "trading_value": 5})
check(full["missing_inputs"] == [] and abs(full["risk_score"] - (0.12 + 0.18 + 0.12 + 0.08 + 0.08 + 0.05)) < 1e-6 and full["risk_score"] < 1.0, "max components saturate: %r" % full["risk_score"])
badt = cr.resolve_candidate_base_risk(scanner_row={"risk_score": "nan-ish"}, features={"close_last": "x"}); check(badt["source"] == "market_data_fallback", "bad explicit -> fallback")
nanr = cr.resolve_candidate_base_risk(scanner_row={"risk_score": float("nan")}); nan_src = nanr["source"]
inp = {"scanner_row": {"k": 1}, "features": {"close_last": 10, "atr14": 1}}; i0 = copy.deepcopy(inp); cr.resolve_candidate_base_risk(**inp); check(inp == i0, "inputs immutable")
check(not bad, "blocked effects: %r" % bad)
print("RF014_SCANNER_DYNAMIC_OK repeat_cap=%.2f blocker_dominant=%s families=%d risk_explicit=%.1f risk_fallback=%.2f nan_source=%s state_mutation=none write_attempts=0 shim_identity=yes debug=%s"
      % (r["penalty"], b["reason"], len(fam), exp["risk_score"], fb["risk_score"], nan_src, __debug__))
