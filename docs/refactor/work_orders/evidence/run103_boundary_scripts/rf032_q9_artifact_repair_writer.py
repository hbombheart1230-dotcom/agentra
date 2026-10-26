# RF-032: evaluation/q9_artifact_repair.py::repair_q9_day_artifacts -- tmp only. Reads <tmp>/reports/operator_summary/daily/<d>/q9_decision_windows.json, <tmp>/reports/canonical/<d>/<run>/scanner.json,
# <tmp>/data/logs/quant_shadow_candidates/<d>/*.json; rewrites windows json + shadow payloads via .tmp+replace. Writes outside tmp, network, subprocess, sqlite blocked.
import os, sys, json, copy, shutil, socket, subprocess, sqlite3, builtins, importlib, tempfile
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
mod = importlib.import_module("libs.reporting.evaluation.q9_artifact_repair")
tmp = Path(tempfile.mkdtemp(prefix="rf032_q9repair_")).resolve(); os.chdir(tmp)
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
def wt(self, *a, **k):
    if not inside(self): bad.append("write_text:" + str(self)); raise OSError("blocked write")
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
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(obj if raw else json.dumps(obj), encoding="utf-8")
root = tmp / "reports"; shadow_base = tmp / "data/logs/quant_shadow_candidates"
snap = lambda: {str(p.relative_to(tmp).as_posix()): (p.read_bytes() if p.is_file() else None) for p in tmp.rglob("*")}
rd = lambda p: json.loads(p.read_text(encoding="utf-8"))
D = "2026-10-05"
dpath = lambda d=D: root / "operator_summary/daily" / d / "q9_decision_windows.json"
spath = lambda n, d=D: shadow_base / d / n
def cand(sym, role, rank=1, **kw): return dict({"symbol": sym, "rank": rank, "q9_decision_role": role, "score_total": 1.5, "q9_selected": rank == 1, "compact_feature_snapshot": {"quote_source": "x", "skill_quote_price": 10}}, **kw)
def shadow(did, with_cmd=False, gen="2026-10-05T01:02:03Z"):
    rows = [cand("AAA", "A_SCANNER_CONTROL"), cand("BBB", "A_SCANNER_CONTROL", 2), cand("AAA", "P_SCANNER_PRE_STRATEGIST_UNIVERSE"), cand("AAA", "B_STRATEGIST_RANKED")]
    if with_cmd: rows.append(cand("AAA", "C_COMMANDER_FINAL", q9_commander_decision="approve", q9_monitor_intent="BUY"))
    return {"q9_decision_id": did, "generated_at": gen, "run_id": "r1", "q9_decision_candidates": rows, "candidates": [{"shadow_role": "top_pick", "intent_submitted": True, "triggered": True, "guard_reason": "g", "entry_cost_filter": {"passed": True, "fail_reasons": ["a"]}}]}
out = {}
# 1. nothing at all -> ok, no write
s0 = snap(); r = mod.repair_q9_day_artifacts(reports_root=root, day=D)
check(r["ok"] and r["window_count"] == 0 and snap() == s0 and not dpath().exists(), r)
# 2. missing decision file + shadow payloads -> decision file CREATED from shadow; latest.json skipped; corrupt shadow skipped
put(spath("d1.json"), shadow("D1")); put(spath("latest.json"), shadow("LATEST")); put(spath("bad.json"), "{nope", raw=True); put(spath("d2.json"), shadow("D2", with_cmd=True, gen="1790000000"))
r = mod.repair_q9_day_artifacts(reports_root=root, day=D)
dp = rd(dpath()); ids = [w["decision_id"] for w in dp["windows"]]
check(r["ok"] and r["recovered_window_count"] == 2 and sorted(ids) == ["D1", "D2"], (r, ids))
check("LATEST" not in ids and dp["window_count"] == 2 and dp["schema_version"] == "q9_decision_windows.v1" and dp["day"] == D, list(dp.keys()))
w1 = next(w for w in dp["windows"] if w["decision_id"] == "D1"); w2 = next(w for w in dp["windows"] if w["decision_id"] == "D2")
check(w1["window_type"] == "scanner_selection" and w1["generated_at"] == "2026-10-05T01:02:03+00:00" and w1["decision_epoch"] > 0, w1)
check("commander_final" not in w1 and w2["commander_final"]["decision"] == "approve" and w2["commander_final"]["selected_symbol"] == "AAA" and w2["commander_final"]["monitor_intent"] == "BUY", (list(w1.keys()), w2.get("commander_final")))
check(r["shadow_payload_complete_count"] == 1 and rd(spath("d2.json"))["q9_sync_status"]["status"] == "complete" and "q9_sync_status" not in rd(spath("d1.json")), r)
check(spath("bad.json").read_text() == "{nope" and rd(spath("latest.json")) == shadow("LATEST"), "bad/latest untouched")
out["created_from_shadow"] = len(ids)
# 3. commander backfill: shadow without C role; window (from D2) has commander_final -> C row appended
put(spath("d3.json"), shadow("D1"))
r = mod.repair_q9_day_artifacts(reports_root=root, day=D)
check("q9_sync_status" not in rd(spath("d3.json")), "D1 has no commander -> not complete")
put(spath("d4.json"), shadow("D2"))
r = mod.repair_q9_day_artifacts(reports_root=root, day=D)
p4 = rd(spath("d4.json")); c4 = [x for x in p4["q9_decision_candidates"] if x["q9_decision_role"] == "C_COMMANDER_FINAL"]
check(len(c4) == 1 and c4[0]["q9_backfill_source"] == "daily_q9_decision_window" and c4[0]["q9_commander_decision"] == "approve" and p4["q9_sync_status"]["role_count"] == 4 and p4["q9_sync_status"]["source"] == "q9_artifact_repair", p4.get("q9_sync_status"))
out["commander_backfill"] = "yes"
# 4. idempotency: structure equal apart from timestamps
def strip(o):
    if isinstance(o, dict): return {k: strip(v) for k, v in o.items() if k not in ("repaired_at", "synced_at")}
    if isinstance(o, list): return [strip(v) for v in o]
    return o
def state(): return strip({"d": rd(dpath()), "s": [rd(p) for p in sorted((shadow_base / D).glob("*.json")) if p.name != "bad.json"]})
a = state(); r2 = mod.repair_q9_day_artifacts(reports_root=root, day=D); b = state()
check(a == b and r2["recovered_window_count"] == 0 and r2["enriched_window_count"] == 0 and r2["canonical_enriched_window_count"] == 0, r2)
check(not list(tmp.rglob("*.tmp")), "tmp leftover")
out["idempotent"] = "yes"
# 5. canonical enrichment of existing window lacking compact_feature_snapshot
win = {"decision_id": "E1", "run_id": "run9", "generated_at": "2026-10-06T00:00:00Z", "scanner_control": {"top20": [{"symbol": "AAA"}, {"symbol": "ZZZ", "compact_feature_snapshot": {"keep": 1}}]}, "strategist_selection": {"post_strategist_top10": [{"symbol": "AAA"}]}, "scanner_pre_strategist_universe": {"intrinsic_ranked_top20": "notalist"}}
put(dpath("2026-10-06"), {"schema_version": "q9_decision_windows.v1", "keep_me": {"x": 1}, "windows": [win, "not-a-dict", {"no_id": 1}]})
put(root / "canonical/2026-10-06/run9/scanner.json", {"ranking_table": [{"symbol": "AAA", "compact_feature_snapshot": {"quote_source": "c", "engine_close_last": 7, "skill_quote_price": ""}}, {"symbol": ""}, "x"], "selected_candidate": {"symbol": "SEL", "feature_snapshot": {"quote_best_bid": 3, "intraday_change_pct": 0}}})
r = mod.repair_q9_day_artifacts(reports_root=root, day="2026-10-06")
d6 = rd(dpath("2026-10-06")); w = d6["windows"][1]   # sorted by decision_epoch: id-less window (epoch 0) first
check(r["canonical_enriched_window_count"] == 1 and r["window_count"] == 2 and d6["keep_me"] == {"x": 1} and d6["window_count"] == 2 and d6["windows"][0] == {"no_id": 1, "window_type": "commander_monitor_only"}, (r, d6["windows"][0]))
check(w["scanner_control"]["top20"][0]["compact_feature_snapshot"] == {"engine_close_last": 7, "quote_source": "c"} and w["scanner_control"]["top20"][1]["compact_feature_snapshot"] == {"keep": 1} and w["strategist_selection"]["post_strategist_top10"][0]["compact_feature_snapshot"]["engine_close_last"] == 7, w)
check(w["scanner_pre_strategist_universe"]["intrinsic_ranked_top20"] == "notalist" and r["normalized_window_count"] == 2 and "SEL" not in json.dumps(w), w)
out["canonical_enrich"] = "yes"
# 6. corrupt decision file: no shadow -> untouched; with shadow -> corrupt content REPLACED by recovered windows
put(dpath("2026-10-07"), "{broken", raw=True); s0 = snap()
r = mod.repair_q9_day_artifacts(reports_root=root, day="2026-10-07")
check(r["window_count"] == 0 and snap() == s0 and dpath("2026-10-07").read_text() == "{broken", r)
put(spath("s.json", "2026-10-07"), shadow("S1"))
r = mod.repair_q9_day_artifacts(reports_root=root, day="2026-10-07")
check(r["recovered_window_count"] == 1 and rd(dpath("2026-10-07"))["window_count"] == 1, r)
out["corrupt_overwritten"] = "yes"
# 7. day normalization / odd input
r = mod.repair_q9_day_artifacts(reports_root=root, day="2026-10-06T23:59:59")
check(r["day"] == "2026-10-06" and r["window_count"] == 2, r)
r_none, e_none = attempt(mod.repair_q9_day_artifacts, reports_root=root, day=None)
check(e_none is None and r_none["day"] == "" and r_none["window_count"] == 0, (r_none, e_none))
out["day_none"] = "empty_day_ok"
_, e = attempt(mod.repair_q9_day_artifacts, reports_root=None, day=D)
check(e == "TypeError", e)
r = mod.repair_q9_day_artifacts(reports_root=str(root), day=D); check(r["ok"], r)
n = mod._normalized_generated_at
check(n("1790000000")[1] == 1790000000 and n("2026-10-05T01:02:03Z")[0] == "2026-10-05T01:02:03+00:00" and n("garbage") == ("garbage", None) and n(None) == ("", None), "gen_at")
# 8. partial failure: replace() fails for shadow file after decision file written
put(dpath("2026-10-08"), {"windows": [{"decision_id": "F1", "generated_at": "1790000000", "commander_final": {"decision": "approve", "selected_symbol": "AAA"}}]})
put(spath("f.json", "2026-10-08"), shadow("F1")); before_f = spath("f.json", "2026-10-08").read_bytes(); before_d = dpath("2026-10-08").read_bytes()
_rep = Path.replace
hit = []
def rep(self, target):
    if self.name == "f.json.tmp": hit.append(1); raise OSError("replace boom")
    return _rep(self, target)
Path.replace = rep
_, e = attempt(mod.repair_q9_day_artifacts, reports_root=root, day="2026-10-08")
Path.replace = _rep
check(e == "OSError" and hit and dpath("2026-10-08").read_bytes() != before_d and spath("f.json", "2026-10-08").read_bytes() == before_f and spath("f.json.tmp", "2026-10-08").exists(), (e, hit))
check(rd(dpath("2026-10-08"))["window_count"] == 1 and rd(dpath("2026-10-08"))["windows"][0]["commander_final"]["decision"] == "approve", "decision written")
out["partial"] = "decision_new_shadow_old_tmp_left"
spath("f.json.tmp", "2026-10-08").unlink()
r = mod.repair_q9_day_artifacts(reports_root=root, day="2026-10-08")
check(r["shadow_payload_repaired_count"] == 1 and r["shadow_payload_complete_count"] == 1, r)
# 9. replace fails on decision file: original kept, shadow untouched, .tmp left
put(dpath("2026-10-09"), {"windows": [{"decision_id": "G1", "generated_at": "1"}], "k": 1}); before_g = dpath("2026-10-09").read_bytes()
put(spath("g.json", "2026-10-09"), shadow("G1")); sg = spath("g.json", "2026-10-09").read_bytes()
def rep2(self, target):
    if self.name == "q9_decision_windows.json.tmp": raise OSError("boom2")
    return _rep(self, target)
Path.replace = rep2
_, e = attempt(mod.repair_q9_day_artifacts, reports_root=root, day="2026-10-09")
Path.replace = _rep
check(e == "OSError" and dpath("2026-10-09").read_bytes() == before_g and spath("g.json", "2026-10-09").read_bytes() == sg and dpath("2026-10-09").with_name("q9_decision_windows.json.tmp").exists(), e)
out["decision_replace_fail"] = "orig_kept_tmp_left"
# 10. outside write blocked; no network/subprocess/sqlite attempts
_, e = attempt(mod._write_json_atomic, Path(tempfile.gettempdir()).parent / "rf032_q9_outside" / "x.json", {"a": 1})
check(e == "OSError" and any(b.startswith("mkdir:") for b in bad), (e, bad))
net = [b for b in bad if b in ("connect", "cc", "gai", "Popen", "run", "call", "check_call", "check_output", "os.system", "sqlite")]
check(not net and not [b for b in bad if b.startswith(("write:", "write_text:"))], bad)
os.chdir(repo); shutil.rmtree(tmp, ignore_errors=True)
print("RF032_Q9_ARTIFACT_REPAIR_OK created=%d commander_backfill=%s idempotent=%s canonical_enrich=%s corrupt_overwritten=%s partial=%s decision_replace_fail=%s day_none=%s outside_write=OSError net_attempts=%d" % (out["created_from_shadow"], out["commander_backfill"], out["idempotent"], out["canonical_enrich"], out["corrupt_overwritten"], out["partial"], out["decision_replace_fail"], out["day_none"], len(net)))
