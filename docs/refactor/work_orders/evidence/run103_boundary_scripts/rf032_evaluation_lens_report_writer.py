# RF-032: evaluation/evaluation_lens_report.py (cost floor / streaming accumulators / build / render / write) -- tmp reports root only.
# Real loaders over a tmp tree: <tmp>/data/logs/quant_shadow_candidates/<day>/*.json (shadow payloads), <tmp>/reports/trades/<day>/**/lifecycle_bundle.json.
# Only two collaborators are replaced: state minute rows (`load_minute_rows_from_state`, otherwise data/state.json) and
# `build_q9_trade_read_model` (another owner's heavy legacy reader; the lens consumes its dict). Writes outside tmp, network, subprocess, sqlite blocked.
import os, sys, json, copy, socket, subprocess, sqlite3, builtins, importlib, tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
mod = importlib.import_module("libs.reporting.evaluation.evaluation_lens_report")
fwd = importlib.import_module("libs.reporting.quant_shadow_forward_outcomes")
tmp = Path(tempfile.mkdtemp(prefix="rf032_elr_")).resolve(); os.chdir(tmp)
bad = []
def blocked(n):
    def f(*a, **k): bad.append(n); raise OSError("blocked " + n)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("cc"); socket.getaddrinfo = blocked("gai")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite")
_open = builtins.open; _wt = Path.write_text; _mk = Path.mkdir
def inside(p):
    try: Path(p).resolve().relative_to(tmp); return True
    except Exception: return False
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+") and not inside(f): bad.append("write:" + str(f)); raise OSError("blocked write")
    return _open(f, mode, *a, **k)
builtins.open = gopen
FAIL = {}  # file name -> exception class raised by Path.write_text (partial-failure injection, tmp only)
def wt(self, *a, **k):
    if not inside(self): bad.append("write_text:" + str(self)); raise OSError("blocked write")
    if self.name in FAIL: raise FAIL[self.name]("injected " + self.name)
    return _wt(self, *a, **k)
def mk(self, *a, **k):
    if not inside(self): bad.append("mkdir:" + str(self)); raise OSError("blocked mkdir")
    return _mk(self, *a, **k)
Path.write_text = wt; Path.mkdir = mk
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED: " + str(m))
def attempt(fn, *a, **k):
    try: return fn(*a, **k), None
    except Exception as e: return None, type(e).__name__
def put(p, obj, raw=False):
    p.parent.mkdir(parents=True, exist_ok=True); _wt(p, obj if raw else json.dumps(obj, ensure_ascii=False), encoding="utf-8")
snap = lambda: {str(p.relative_to(tmp).as_posix()): (p.read_bytes() if p.is_file() else None) for p in tmp.rglob("*")}

KST = timezone(timedelta(hours=9))
def epoch(h, m): return int(datetime(2026, 7, 1, h, m, tzinfo=KST).timestamp())
E0 = epoch(10, 0)
def minute_rows(slope):
    rows = []
    for m in range(0, 331):  # 10:00 .. 15:30
        c = round(100 + slope * m, 4)
        rows.append({"ts": E0 + 60 * m, "raw_ts": datetime.fromtimestamp(E0 + 60 * m, tz=KST).strftime("%Y%m%d%H%M%S"), "close": c, "high": round(c + 0.05, 4), "low": round(c - 0.05, 4)})
    return rows
STATE = {"AAA": minute_rows(0.1), "BBB": minute_rows(-0.1)}
fwd.load_minute_rows_from_state = lambda *a, **k: STATE  # no data/state.json read
BASE = {"baseline_epoch": E0, "baseline_price": 100.0, "baseline_raw_ts": "20260701100000"}
def cand(symbol, **kw): return dict({"symbol": symbol, "shadow_forward_base": dict(BASE)}, **kw)
GEN = "2026-07-01T10:00:30+09:00"
cost_path = tmp / "cost_profile.json"; os.environ["BROKER_COST_PROFILE_PATH"] = str(cost_path)
def set_cost(obj, raw=False):
    if obj is None:
        if cost_path.exists(): cost_path.unlink()
    else: _wt(cost_path, obj if raw else json.dumps(obj), encoding="utf-8")
out = {}
# ---- _cost_floor_pct: key order, fraction-vs-percent heuristic, non-positive/non-numeric/missing -> 0.0
cf = mod._cost_floor_pct
cases = [({"conservative_round_trip_cost_pct": 0.005}, 0.5), ({"conservative_round_trip_cost_pct": 0.5}, 50.0), ({"conservative_round_trip_cost_pct": 1}, 1.0),
         ({"conservative_round_trip_cost_pct": 0, "round_trip_cost_pct": 1.2}, 1.2), ({"conservative_round_trip_cost_pct": -1, "ema_round_trip_cost_pct": "x", "round_trip_cost_pct": None}, 0.0),
         ({"ema_round_trip_cost_pct": 0.01}, 1.0), ({}, 0.0)]
for prof, want in cases:
    set_cost(prof); got = cf(); check(abs(got - want) < 1e-9, (prof, got, want))
set_cost(None); check(cf() == 0.0, "missing profile"); set_cost("[1]", raw=True); check(cf() == 0.0, "list profile"); set_cost("{bad", raw=True); check(cf() == 0.0, "broken profile")
out["cost_floor_obs"] = "0.5 is read as a fraction -> 50.0; 1 stays 1.0"
# ---- helpers
check(mod._num("1.5") == 1.5 and mod._num("") is None and mod._num(None, 7) == 7 and mod._num("x") is None and mod._num(0) == 0.0 and mod._num([1]) is None, "_num")
check(mod._blocker({"guard_reason": " g ", "reason": "r"}) == "g" and mod._blocker({"reason": "r"}) == "r" and mod._blocker({"primary_failure_axis": "ax"}) == "ax"
      and mod._blocker({"entry_quant_decision": {"blockers": ["b1", "b2"]}}) == "b1" and mod._blocker({"entry_quant_decision": {"blockers": []}}) == "unknown" and mod._blocker({}) == "unknown", "_blocker order")
check(mod._rail({"entry_lane_observation": {"market_regime_rail": "bull"}}) == "bull" and mod._rail({"entry_lane_observation": {"market_regime_rail_shadow": {"market_regime_rail": "bear"}}}) == "bear"
      and mod._rail({}) == "unknown" and mod._rail({"entry_lane_observation": "str"}) == "unknown", "_rail")
check(mod._metric_avg({"count": 0}) == "-" and mod._metric_avg({"count": 2, "average_return_pct": 1.25}) == "1.25" and mod._metric_avg(None) == "-", "_metric_avg")
out["metric_avg_exc"] = attempt(mod._metric_avg, {"count": "x"})[1]  # int("x") -> ValueError

# ---- fixture tree (real loaders): shadow payloads for 2026-07-01 (outcomes available) and 07-02 (no minute rows -> pending), trades 07-01..07-02
root = tmp / "reports"; shadow = tmp / "data" / "logs" / "quant_shadow_candidates"
Q = lambda **kw: dict(kw, shadow_forward_base=dict(BASE), entry_lane_observation={"market_regime_rail": "dropped"})
payload1 = {"generated_at": GEN, "candidates": [
    cand("AAA", guard_reason="below_vwap_reclaim_not_ready:한글", entry_lane_observation={"market_regime_rail": "bull"}),
    cand("BBB", reason="pullback_not_mature", entry_lane_observation={"market_regime_rail_shadow": {"market_regime_rail": "bear"}}),
    cand("AAA", reason="other_reason"),
    cand("AAA", entry_quant_decision={"blockers": ["volume_confirmation_missing"]}, entry_lane_observation={"market_regime_rail": "bull"}),
    {"shadow_forward_base": dict(BASE), "reason": "breakout_not_ready"},  # no symbol
    "junk", 7],
    "q9_decision_candidates": [
    Q(symbol="BBB", q9_decision_id="d1", q9_decision_role="A_SCANNER_CONTROL", rank=2),
    Q(symbol="AAA", q9_decision_id="d1", q9_decision_role="A_SCANNER_CONTROL", rank=1),
    Q(symbol="AAA", q9_decision_id="d1", q9_decision_role="B_STRATEGIST_RANKED", rank=1, q9_selected=False),
    Q(symbol="BBB", q9_decision_id="d1", q9_decision_role="B_STRATEGIST_RANKED", rank=2, q9_selected=True),
    Q(symbol="AAA", q9_decision_id="d1", q9_decision_role="C_COMMANDER_FINAL", rank="1"),
    Q(symbol="AAA", q9_decision_id="d2", q9_decision_role="A_SCANNER_CONTROL"),           # rank missing -> 999
    Q(symbol="BBB", q9_decision_id="d2", q9_decision_role="B_STRATEGIST_RANKED", rank=1),  # no selected -> lowest rank
    Q(symbol="AAA", q9_decision_id="d3", q9_decision_role="P_SCANNER_PRE_STRATEGIST_UNIVERSE", rank=1),  # counted for best role only
    Q(symbol="AAA", q9_decision_id="d3", q9_decision_role="OTHER", rank=1),
    Q(symbol="AAA", q9_decision_id="", q9_decision_role="A_SCANNER_CONTROL", rank=1),       # no decision id: role stats only
    "junk"]}
payload2 = {"generated_at": "2026-07-02T10:00:30+09:00", "candidates": [{"symbol": "AAA", "reason": "pullback_not_mature", "shadow_forward_base": {"baseline_epoch": E0 + 86400, "baseline_price": 100.0, "baseline_raw_ts": "20260702100000"}}]}
put(shadow / "2026-07-01" / "a.json", payload1); put(shadow / "2026-07-01" / "latest.json", {"generated_at": GEN, "candidates": [cand("AAA", reason="pullback_not_mature")]})
put(shadow / "2026-07-01" / "broken.json", "{bad", raw=True); put(shadow / "2026-07-01" / "list.json", [1, 2])
put(shadow / "2026-07-02" / "a.json", payload2)
for rel in ("2026-07-01/T1", "2026-07-01/grp/T2", "2026-07-01/T3", "2026-07-02/T4"): put(root / "trades" / rel / "lifecycle_bundle.json", {"trade_id": rel.rsplit("/", 1)[1]})
put(root / "trades" / "2026-07-01" / "T1" / "other.json", {"x": 1})  # no bundle in sibling dirs
MODELS = {
    "T1": {"trade_id": "T1", "symbol": "AAA", "exit": {"reason": "stop"}, "outcome": {"net_return_pct": -1.0}, "post_exit_shadow": {"checkpoints": {"+5m": {"return_pct": 0.5}, "EOD": {"return_pct": "x"}}}},
    "T2": {"trade_id": "T2", "symbol": "BBB", "exit": {"reason": "stop"}, "outcome": {"net_return_pct": 0, "return_pct": 2.0}, "monitor": {"post_exit": {"checkpoints": {"+5m": {"return_pct": 3.0}, "+60m": {"return_pct": 1.0}}}}},
    "T3": {"trade_id": "T3", "symbol": "AAA", "exit": {}, "outcome": {"exit_reason": "tp", "net_return_pct": 1.0}, "post_exit_shadow": {"checkpoints": {"+15m": {"return_pct": 0.0}}}},
    "T4": {"trade_id": "T4", "symbol": "BBB", "exit": "str", "outcome": None},
}
calls = []
def fake_model(trade_dir): calls.append(Path(trade_dir).name); return copy.deepcopy(MODELS[Path(trade_dir).name])
mod.build_q9_trade_read_model = fake_model

# ---- build (cost floor 0.5%): evidence counts, blocker/rail groups, streaming == legacy non-streaming helpers
set_cost({"conservative_round_trip_cost_pct": 0.005}); s0 = snap()
rep = mod.build_evaluation_lens_report(reports_root=root, start="2026-07-01", end="2026-07-02")
check(snap() == s0, "build mutated tree")
check(rep["schema_version"] == "evaluation_lens_report.v1" and rep["freeze_safe"] is True and rep["behavior_change_authorized"] is False and rep["behavior_effect"] == "evaluation_only", rep["schema_version"])
check(rep["evidence"]["candidate_count"] == 6 and rep["evidence"]["q9_candidate_count"] == 10 and rep["evidence"]["trade_model_count"] == 4, rep["evidence"])  # junk/non-mapping rows skipped; latest/broken/list files skipped
br = rep["blocker_forward_review"]; by = {r["name"]: r for r in br["by_blocker"]}; rail = {r["name"]: r for r in br["by_market_rail"]}
check(br["cost_floor_pct"] == 0.5 and br["candidate_count"] == 6 and br["focused_candidate_count"] == 5, br["focused_candidate_count"])  # 'other_reason' is the only unfocused one
check(set(by) == {"below_vwap_reclaim_not_ready:한글", "pullback_not_mature", "volume_confirmation_missing", "breakout_not_ready"}, set(by))
check(by["pullback_not_mature"]["candidate_count"] == 2 and by["pullback_not_mature"]["observed_days"] == ["20260701", "20260702"], by["pullback_not_mature"]["observed_days"])
a = by["below_vwap_reclaim_not_ready:한글"]
check(a["+5m"]["observed_count"] == 1 and a["+5m"]["return"]["average_return_pct"] == 0.5 and a["+5m"]["avg_mfe_pct"] == 0.55 and a["+5m"]["avg_mae_pct"] == -0.05, a["+5m"])
check(a["+5m"]["cost_floor_reachable_count"] == 1 and a["+5m"]["cost_floor_reachable_rate"] == 1.0 and a["+15m"]["return"]["average_return_pct"] == 1.5 and a["EOD"]["observed_count"] == 1, a["EOD"])
check(by["breakout_not_ready"]["+5m"]["observed_count"] == 0 and by["breakout_not_ready"]["+5m"]["avg_mfe_pct"] is None and by["breakout_not_ready"]["+5m"]["cost_floor_reachable_rate"] == 0.0, "no-symbol candidate has no outcome")
p = by["pullback_not_mature"]  # BBB 07-01 observed negative, AAA 07-02 pending (no minute rows that day)
check(p["+5m"]["observed_count"] == 1 and p["+5m"]["return"]["average_return_pct"] == -0.5 and p["+5m"]["cost_floor_reachable_count"] == 0, p["+5m"])
check(set(rail) == {"bull", "bear", "unknown"} and rail["bull"]["candidate_count"] == 2 and rail["unknown"]["candidate_count"] == 3 and rail["bear"]["candidate_count"] == 1, {k: v["candidate_count"] for k, v in rail.items()})
out["blocker_order"] = [r["name"] for r in br["by_blocker"]]  # sorted by -max observed count, then name
check([r["name"] for r in br["by_blocker"]][0] != "" and br["by_blocker"][0]["+5m"]["observed_count"] >= br["by_blocker"][-1]["+5m"]["observed_count"], "ordering")
sd = rep["strategist_delta_review"]; d5 = sd["deltas_by_horizon"][0]
check(sd["decision_window_count"] == 3 and d5["horizon"] == "+5m", sd["decision_window_count"])  # d1,d2,d3 (blank-id row excluded)
check(d5["strategist_minus_scanner_control"]["count"] == 2 and d5["strategist_minus_scanner_control"]["average_return_pct"] == -1.0, d5)  # d1: BBB(selected)-AAA(rank1) = -0.5-0.5 ; d2: BBB-AAA = -0.5-0.5 -> avg -1.0
check(d5["commander_minus_strategist"]["count"] == 1 and d5["commander_minus_strategist"]["average_return_pct"] == 1.0, d5["commander_minus_strategist"])
roles = {r["horizon"]: r for r in sd["best_role_by_horizon"]}
check(roles["+5m"]["best_role"] in ("A_SCANNER_CONTROL", "P_SCANNER_PRE_STRATEGIST_UNIVERSE", "C_COMMANDER_FINAL") and {r["role"] for r in roles["+5m"]["roles"]} == {"P_SCANNER_PRE_STRATEGIST_UNIVERSE", "A_SCANNER_CONTROL", "B_STRATEGIST_RANKED", "C_COMMANDER_FINAL"}, roles["+5m"])
out["best_role_5m"] = roles["+5m"]["best_role"]
# streaming accumulators == the non-streaming reference helpers on the same loaded rows
cfp = mod._cost_floor_pct()
payloads = mod.load_quant_shadow_candidate_payloads_for_range(reports_root=root, start="2026-07-01", end="2026-07-02", drop_q9_row_keys=mod.Q9_ROW_KEYS_UNUSED_BY_FULL_CHAIN)
ref_b = mod._blocker_forward_review(mod._candidate_rows(payloads), cost_floor_pct=cfp); ref_s = mod._strategist_delta_review(mod._q9_candidate_rows(payloads))
check(json.dumps(ref_b, sort_keys=True, ensure_ascii=False) == json.dumps(br, sort_keys=True, ensure_ascii=False), "blocker streaming != reference")
check(json.dumps(ref_s, sort_keys=True, ensure_ascii=False) == json.dumps(sd, sort_keys=True, ensure_ascii=False), "strategist streaming != reference")
# q9 row keys named in Q9_ROW_KEYS_UNUSED_BY_FULL_CHAIN are dropped from q9 rows before use (entry_lane_observation on q9 rows is not read)
check(all("entry_lane_observation" not in r for pl in payloads for r in pl.get("q9_decision_candidates") or [] if isinstance(r, dict)), "q9 keys not dropped")
# exit review (stubbed trade models)
ex = rep["exit_hold_counterfactual_review"]; exr = {r["exit_reason"]: r for r in ex["by_exit_reason"]}
check(ex["trade_count"] == 4 and calls.count("T2") >= 1 and sorted(set(calls)) == ["T1", "T2", "T3", "T4"] and "T1" in calls, calls)
check([r["exit_reason"] for r in ex["by_exit_reason"]] == ["stop", "tp", "unknown"] and exr["stop"]["trade_count"] == 2, [r["exit_reason"] for r in ex["by_exit_reason"]])
check(exr["stop"]["+5m"]["count"] == 2 and exr["stop"]["+5m"]["average_return_pct"] == 1.25 and exr["stop"]["+60m"]["count"] == 1 and exr["stop"]["EOD"]["count"] == 0, exr["stop"]["+5m"])  # T1: 0.5-(-1.0)=1.5 ; T2: 3.0-2.0=1.0 (net_return 0 falls through to return_pct)
check(exr["tp"]["+15m"]["count"] == 1 and exr["tp"]["+15m"]["average_return_pct"] == -1.0 and exr["unknown"]["+5m"]["count"] == 0, exr["tp"])  # 0.0 - 1.0 ; T4: actual None -> no improvements
out["exit_obs"] = "net_return_pct==0 falls through to return_pct (or-chain); EOD return 'x' -> None"
# determinism
rep_b = mod.build_evaluation_lens_report(reports_root=root, start="2026-07-01", end="2026-07-02"); check(rep_b == rep, "build nondeterministic")
# cost floor 0 -> nothing reachable; range edges
set_cost(None); r0 = mod.build_evaluation_lens_report(reports_root=root, start="2026-07-01", end="2026-07-01")
check(r0["blocker_forward_review"]["cost_floor_pct"] == 0.0 and all(r[h]["cost_floor_reachable_count"] == 0 for r in r0["blocker_forward_review"]["by_blocker"] for h in mod.HORIZONS) and r0["evidence"]["trade_model_count"] == 3, r0["evidence"])
set_cost({"conservative_round_trip_cost_pct": 0.005})
rrev = mod.build_evaluation_lens_report(reports_root=root, start="2026-07-03", end="2026-07-01")
check(rrev["evidence"] == {"shadow_payload_count": 0, "candidate_count": 0, "q9_candidate_count": 0, "trade_model_count": 0} and rrev["blocker_forward_review"]["by_blocker"] == [] and rrev["range"] == {"start": "2026-07-03", "end": "2026-07-01"}, "start>end -> empty, no error")
rts = mod.build_evaluation_lens_report(reports_root=root, start="2026-07-01T09:00", end="2026-07-01T23:59"); check(rts["range"] == {"start": "2026-07-01", "end": "2026-07-01"} and rts["evidence"]["shadow_payload_count"] == 1, "timestamps truncated to date")
rno = mod.build_evaluation_lens_report(reports_root=tmp / "iso" / "reports", start="2026-07-01", end="2026-07-01"); check(rno["evidence"]["candidate_count"] == 0 and rno["exit_hold_counterfactual_review"]["by_exit_reason"] == [], "missing root")
bad_q = copy.deepcopy(payload1); bad_q["q9_decision_candidates"][0]["rank"] = "x"
put(shadow / "2026-07-05" / "a.json", bad_q)  # rank non-numeric -> int(float('x'))
out["build_exc"] = {"rank_x": attempt(mod.build_evaluation_lens_report, reports_root=root, start="2026-07-05", end="2026-07-05")[1],
                    "ref_rank_x": attempt(mod._strategist_delta_review, mod._q9_candidate_rows([bad_q]))[1],
                    "bad_date": attempt(mod.build_evaluation_lens_report, reports_root=root, start="x", end="2026-07-01")[1],
                    "end_short": attempt(mod.build_evaluation_lens_report, reports_root=root, start="2026-07-01", end="2026")[1],
                    "none_start": attempt(mod.build_evaluation_lens_report, reports_root=root, start=None, end="2026-07-01")[1],
                    "none_root": attempt(mod.build_evaluation_lens_report, reports_root=None, start="2026-07-01", end="2026-07-01")[1],
                    "kw_missing": attempt(mod.build_evaluation_lens_report, reports_root=root, start="2026-07-01")[1]}
(shadow / "2026-07-05" / "a.json").unlink(); (shadow / "2026-07-05").rmdir()
s_clean = snap()

# ---- render
md = mod.render_evaluation_lens_report(rep); check(md == mod.render_evaluation_lens_report(copy.deepcopy(rep)), "render nondeterministic")
check(md.startswith("# Evaluation Lens Report (2026-07-01 ~ 2026-07-02)\n") and md.endswith("\n") and "- shadow candidates: 6" in md and "- trade models: 4" in md, md[:120])
check("| below_vwap_reclaim_not_ready:한글 | 1 | 0.5 | 1.5 |" in md and "| pullback_not_mature | 2 |" in md and "## Strategist Delta" in md and "| +5m | " in md and "| stop | 2 | 1.25 |" in md and "| unknown | 1 | - | - | - | - |" in md, md)
mde = mod.render_evaluation_lens_report({}); check("None ~ None" in mde and "- shadow payloads: None" in mde and "## Rules" in mde, mde[:120])
out["render_exc"] = {"none": attempt(mod.render_evaluation_lens_report, None)[1], "list": attempt(mod.render_evaluation_lens_report, [1])[1], "bad_count": attempt(mod.render_evaluation_lens_report, {"strategist_delta_review": {"deltas_by_horizon": [{"horizon": "+5m", "strategist_minus_scanner_control": {"count": "x"}}]}})[1]}
check(out["render_exc"]["none"] == "AttributeError" and out["render_exc"]["list"] == "AttributeError", out["render_exc"])

# ---- write: default dir, content == build/render, idempotent, nothing else touched
r, e = attempt(mod.write_evaluation_lens_report, reports_root=root, start="2026-07-01", end="2026-07-02"); check(e is None, e)
jp, mp = Path(r["json"]), Path(r["markdown"])
check(jp == root / "evaluation/lens/2026-07-02/evaluation_lens_report.json" and mp.name == "evaluation_lens_report.md", r)
check(json.loads(jp.read_text(encoding="utf-8")) == rep and mp.read_text(encoding="utf-8") == md and jp.read_bytes().rstrip(b"\r\n").endswith(b"}"), "written != built")  # Windows text mode writes CRLF
b1 = (jp.read_bytes(), mp.read_bytes()); r2, e2 = attempt(mod.write_evaluation_lens_report, reports_root=str(root), start="2026-07-01", end="2026-07-02", output_dir=""); check(e2 is None and (jp.read_bytes(), mp.read_bytes()) == b1 and r2 == r, "str root / empty output_dir -> default, idempotent")
new = {k for k in snap() if k not in s_clean}; check(new == {"reports/evaluation", "reports/evaluation/lens", "reports/evaluation/lens/2026-07-02", "reports/evaluation/lens/2026-07-02/evaluation_lens_report.json", "reports/evaluation/lens/2026-07-02/evaluation_lens_report.md"}, new)
check(all(snap().get(k) == v for k, v in s_clean.items()), "inputs mutated")
out["files"] = 2
custom = tmp / "custom_out" / "x"; r3 = mod.write_evaluation_lens_report(reports_root=root, start="2026-07-01", end="2026-07-02", output_dir=str(custom))
check(Path(r3["json"]) == custom / "evaluation_lens_report.json" and (custom / "evaluation_lens_report.md").is_file(), r3)
# ---- partial failure / State
o1 = tmp / "o_fresh"; FAIL["evaluation_lens_report.md"] = OSError
_, e = attempt(mod.write_evaluation_lens_report, reports_root=root, start="2026-07-01", end="2026-07-02", output_dir=o1)
check(e == "OSError" and (o1 / "evaluation_lens_report.json").is_file() and not (o1 / "evaluation_lens_report.md").exists(), ("md OSError -> json only", e)); out["md_fail_fresh"] = "json_written_md_absent"
FAIL.clear(); FAIL["evaluation_lens_report.json"] = PermissionError; o2 = tmp / "o_fresh2"
_, e = attempt(mod.write_evaluation_lens_report, reports_root=root, start="2026-07-01", end="2026-07-02", output_dir=o2)
check(e == "PermissionError" and o2.is_dir() and not list(o2.iterdir()), ("json PermissionError -> empty dir created", e)); out["json_fail_fresh"] = "dir_created_no_files"
# pre-existing outputs: json failure preserves both; md failure leaves new json + old md (non-atomic pair)
FAIL.clear(); o3 = tmp / "o_old"; put(o3 / "evaluation_lens_report.json", {"old": 1}); put(o3 / "evaluation_lens_report.md", "old md", raw=True); old = (o3 / "evaluation_lens_report.json").read_bytes(), (o3 / "evaluation_lens_report.md").read_bytes()
FAIL["evaluation_lens_report.json"] = PermissionError; _, e = attempt(mod.write_evaluation_lens_report, reports_root=root, start="2026-07-01", end="2026-07-02", output_dir=o3)
check(e == "PermissionError" and ((o3 / "evaluation_lens_report.json").read_bytes(), (o3 / "evaluation_lens_report.md").read_bytes()) == old, "json fail preserves both old files")
FAIL.clear(); FAIL["evaluation_lens_report.md"] = OSError; _, e = attempt(mod.write_evaluation_lens_report, reports_root=root, start="2026-07-01", end="2026-07-02", output_dir=o3)
check(e == "OSError" and json.loads((o3 / "evaluation_lens_report.json").read_text(encoding="utf-8")) == rep and (o3 / "evaluation_lens_report.md").read_text() == "old md", "md fail: NEW json + OLD md (mixed generation)")
out["md_fail_existing"] = "new_json_old_md"; FAIL.clear()
# render failure after json written
_render = mod.render_evaluation_lens_report; mod.render_evaluation_lens_report = lambda payload: (_ for _ in ()).throw(RuntimeError("render boom")); o4 = tmp / "o_render"
_, e = attempt(mod.write_evaluation_lens_report, reports_root=root, start="2026-07-01", end="2026-07-02", output_dir=o4); mod.render_evaluation_lens_report = _render
check(e == "RuntimeError" and (o4 / "evaluation_lens_report.json").is_file() and not (o4 / "evaluation_lens_report.md").exists(), "render RuntimeError -> json only"); out["render_fail"] = "json_only"
# build failure -> nothing created (mkdir happens after build)
put(shadow / "2026-07-05" / "a.json", bad_q); o5 = tmp / "o_build_fail"
_, e = attempt(mod.write_evaluation_lens_report, reports_root=root, start="2026-07-05", end="2026-07-05", output_dir=o5)
check(e == "ValueError" and not o5.exists() and not (root / "evaluation/lens/2026-07-05").exists(), ("build ValueError -> no dir", e)); out["build_fail"] = "no_output_dir"
(shadow / "2026-07-05" / "a.json").unlink(); (shadow / "2026-07-05").rmdir()
# errors / outside write / dir collision
out["write_exc"] = {"none_root": attempt(mod.write_evaluation_lens_report, reports_root=None, start="2026-07-01", end="2026-07-01")[1],
                    "bad_date": attempt(mod.write_evaluation_lens_report, reports_root=root, start="x", end="2026-07-01")[1],
                    "positional": attempt(mod.write_evaluation_lens_report, root, "2026-07-01", "2026-07-01")[1]}
exo = attempt(mod.write_evaluation_lens_report, reports_root=Path("/proc/nonexistent_rf032"), start="2026-07-01", end="2026-07-01")[1]; out["outside_write"] = exo; check(exo == "OSError", exo)
(tmp / "collide").write_text("x"); exc = attempt(mod.write_evaluation_lens_report, reports_root=root, start="2026-07-01", end="2026-07-01", output_dir=tmp / "collide")[1]; out["dir_collision"] = exc; check(exc in ("FileExistsError", "NotADirectoryError"), exc)
net = [b for b in bad if not b.startswith(("write:", "write_text:", "mkdir:"))]; check(not net, bad)
check(not (repo and any(b.startswith(("write:" + repo, "write_text:" + repo)) for b in bad)), "tried writing inside repo")
print(json.dumps(out, sort_keys=True, ensure_ascii=False, default=str))
print("RF032_EVALUATION_LENS_REPORT_OK cost_cases=%d blockers=%d rails=%d decisions=%d exit_reasons=%d stream_eq_ref=yes idempotent=yes files=%d outside_write=%s dir_collision=%s net_attempts=%d debug=%s"
      % (len(cases) + 3, len(by), len(rail), sd["decision_window_count"], len(exr), out["files"], out["outside_write"], out["dir_collision"], len(net), __debug__))

