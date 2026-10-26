# RF-034: short_alpha_discriminator/pipeline.py::write_short_alpha_discriminator -- the 10-file sequential write: partial OSError / render failure / build failure / rewrite-over-old State. tmp-only.
# Reuses the already-verified normal 10-file success path only as the baseline (rf034_render_consumer_peer.py); this harness adds: per-file failure injection at every one of the 10 positions
# (prefix written, remainder absent), mixed-generation State on a rewrite over older outputs, render() exceptions mid-sequence, build failure before any mkdir, output_dir edge cases.
# Real episodes flow through the real cohorts/profit_lock/scanner_diagnostics/casebook/policy_matrix builders. Writes outside tmp, network, subprocess, sqlite blocked.
import os, sys, json, copy, socket, subprocess, sqlite3, builtins, importlib, tempfile
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
pkg = importlib.import_module("libs.reporting.short_alpha_discriminator.pipeline")
rep = importlib.import_module("libs.reporting.short_alpha_discriminator.report")
tmp = Path(tempfile.mkdtemp(prefix="rf034_wsa_")).resolve(); os.chdir(tmp)
os.environ["EVIDENCE_LEDGER_PATH"] = str(tmp / "ledger" / "events.jsonl")
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
FAIL = {}  # output file name -> exception class (injected, tmp only)
def wt(self, *a, **k):
    if not inside(self): bad.append("write_text:" + str(self)); raise OSError("blocked write")
    if self.name in FAIL: raise FAIL[self.name]("injected " + self.name)
    return _wt(self, *a, **k)
def mk(self, *a, **k):
    if not inside(self): bad.append("mkdir:" + str(self)); raise OSError("blocked mkdir")
    return _mk(self, *a, **k)
Path.write_text = wt; Path.mkdir = mk
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED@%d: " % sys._getframe(1).f_lineno + str(m))
def attempt(fn, *a, **k):
    try: return fn(*a, **k), None
    except Exception as e: return None, type(e).__name__
def put(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True); _wt(p, json.dumps(obj), encoding="utf-8")
def ep(did, day, sym, epoch, cls, sec=None, ret5=None, ret30=None, recurrent=None):
    obs = {"asset_observation": {"asset_class": cls}}
    if sec is not None: obs["decision_from_open_sec"] = sec
    if recurrent is not None: obs["conditional_lanes"] = {"CONFIRMED_RECURRENT_RANK": {"eligible": recurrent}}
    cps = {}
    if ret5 is not None: cps["+5m"] = {"live_net_return_pct": ret5}
    if ret30 is not None: cps["+30m"] = {"live_net_return_pct": ret30}
    return {"decision_id": did, "day": day, "symbol": sym, "decision_epoch": epoch, "opening_observability": obs, "checkpoints": cps}
def ft(did, band, setup, sources, score=None, entry="E1", tactic="T1"):
    return {"identity": {"decision_id": did}, "scanner": {"risk_band": band, "candidate_setup": setup, "sources": sources, "score_total": score}, "strategy": {"entry_horizon": entry, "tactic_id": tactic}}
O = [ep("e1", "2026-08-20", "A", 100, "common_stock", sec=30, ret5=1.0, ret30=2.0), ep("e3", "2026-08-20", "B", 150, "common_stock", sec=120, ret5=-2.0, ret30=0.5, recurrent=True),
     ep("e4", "2026-08-21", "C", 300, "etf", sec=10, ret5=3.0), ep("e6", "2026-08-25", "A", 400, "common_stock", sec=60, ret5=4.0, ret30=1.0),
     ep("e7", "2026-08-26", "E", 410, "common_stock", sec=61, ret5="bad", ret30=-1.0), ep("e8", "2026-08-26", "F", 420, "common_stock", ret5=1.0)]
F = [ft("e1", "HIGH", "DIRECTIONAL_BREADTH", ["top_volume", "top_value"], 70.5), ft("e3", "HIGH", "OTHER", ["top_value"], "80"), ft("e4", "HIGH", "DIRECTIONAL_BREADTH", ["top_value", "top_volume"]),
     ft("e6", "HIGH", "OTHER", ["top_value", "top_volume", "x"]), ft("e7", "HIGH", "DIRECTIONAL_BREADTH", ["top_value", "top_volume"], "n/a")]
R = tmp / "reports"; EVAL = R / "evaluation"
put(EVAL / "opening_rank1_shadow" / "opening_rank1_shadow_cumulative.json", {"schema_version": "s", "episodes": O})
put(EVAL / "feature_mart" / "opening_rank1" / "feature_mart.json", {"schema_version": "s", "episodes": F})
put(EVAL / "agent_effectiveness" / "cumulative_a" / "agent_effectiveness_scorecard.json", {"schema_version": "s"})
ORDER = [("summary_json_path", "short_alpha_discriminator.json"), ("summary_markdown_path", "short_alpha_discriminator.md"), ("cohort_json_path", "short_alpha_cohorts.json"),
         ("profit_fade_json_path", "profit_fade_shadow.json"), ("strategist_roi_json_path", "strategist_stage2_roi.json"), ("scanner_diagnostics_json_path", "scanner_diagnostics.json"),
         ("opening_casebook_json_path", "opening_overshoot_casebook.json"), ("opening_casebook_markdown_path", "opening_overshoot_casebook.md"),
         ("opening_policy_matrix_json_path", "opening_policy_matrix.json"), ("opening_policy_matrix_markdown_path", "opening_policy_matrix.md")]
NAMES = [n for _, n in ORDER]
def listing(d): return sorted(p.name for p in Path(d).iterdir()) if Path(d).exists() else None
def W(out, **kw): return pkg.write_short_alpha_discriminator(reports_root=kw.pop("reports_root", R), through_day=kw.pop("through_day", "2026-10-26"), output_dir=out, **kw)
out = {}
src_snap = lambda: {str(p.relative_to(tmp)): p.read_bytes() for p in R.rglob("*") if p.is_file()}
s0 = src_snap()
# ---- baseline: real episodes -> build payload, sections feed the files
payload = pkg.build_short_alpha_discriminator(reports_root=R, through_day="2026-10-26")
check(payload["integrity"]["status"] in ("PASS", "PASS_WITH_JOIN_GAPS") and payload["integrity"]["join"].get("missing_join_count") == 1, payload["integrity"])  # e8 has no feature row
check(payload["cohort_review"] and payload["opening_overshoot_casebook"] and payload["opening_policy_matrix"] and payload["scanner_diagnostics"], "sections built from real episodes")
out["status"] = payload["integrity"]["status"]; out["missing_join"] = payload["integrity"]["join"]["missing_join_count"]
d_ok = tmp / "ok"; res = W(d_ok)
check([k for k in res if k.endswith("_path")] == [k for k, _ in ORDER] and listing(d_ok) == sorted(NAMES), "10 outputs, result key order = write order")
check(res["integrity_status"] == payload["integrity"]["status"] and res["behavior_change_authorized"] is False, res)
sections = {"short_alpha_cohorts.json": "cohort_review", "profit_fade_shadow.json": "profit_fade_review", "strategist_stage2_roi.json": "strategist_stage2_review", "scanner_diagnostics.json": "scanner_diagnostics",
            "opening_overshoot_casebook.json": "opening_overshoot_casebook", "opening_policy_matrix.json": "opening_policy_matrix"}
for fname, sec in sections.items(): check(json.loads((d_ok / fname).read_text(encoding="utf-8")) == json.loads(json.dumps(payload[sec])), fname)
check(json.loads((d_ok / "short_alpha_discriminator.json").read_text(encoding="utf-8")) == json.loads(json.dumps(payload)), "summary json == payload")
check((d_ok / "short_alpha_discriminator.md").read_text(encoding="utf-8") == rep.render_short_alpha_discriminator(payload), "summary md == render(payload)")
check((d_ok / "opening_overshoot_casebook.md").read_text(encoding="utf-8") == pkg.render_opening_overshoot_casebook(payload["opening_overshoot_casebook"]) and (d_ok / "opening_policy_matrix.md").read_text(encoding="utf-8") == pkg.render_opening_policy_matrix(payload["opening_policy_matrix"]), "section md == render")
gen1 = {n: (d_ok / n).read_bytes() for n in NAMES}
W(d_ok); check({n: (d_ok / n).read_bytes() for n in NAMES} == gen1, "rewrite idempotent (bytes)")
check(src_snap() == s0, "inputs untouched")
# ---- failure at every position i: fresh dir -> exactly the first i files exist (no cleanup/rollback), exception propagates
prefix = {}
for i, (key, name) in enumerate(ORDER):
    d = tmp / f"fresh_{i}"; FAIL.clear(); FAIL[name] = OSError
    _, e = attempt(W, d); FAIL.clear()
    got = listing(d); want = sorted(NAMES[:i])
    check(e == "OSError" and got == want, (i, name, e, got, want)); prefix[name] = len(got)
out["fresh_prefix_len_by_failed_file"] = prefix
# PermissionError variant at the casebook JSON (position 6)
d = tmp / "perm"; FAIL["opening_overshoot_casebook.json"] = PermissionError; _, e = attempt(W, d); FAIL.clear(); check(e == "PermissionError" and listing(d) == sorted(NAMES[:6]), (e, listing(d)))
# ---- rewrite over an OLDER generation: failure at position k leaves NEW prefix + OLD suffix (mixed generations; summary json says new, later files old)
put(EVAL / "feature_mart" / "opening_rank1" / "feature_mart.json", {"schema_version": "s", "episodes": F + [ft("e8", "HIGH", "OTHER", ["top_value"], 60)]})  # e8 now joins -> different payload
payload2 = pkg.build_short_alpha_discriminator(reports_root=R, through_day="2026-10-27")
d_new = tmp / "gen2_ref"; W(d_new, through_day="2026-10-27"); gen2 = {n: (d_new / n).read_bytes() for n in NAMES}
changed = [n for n in NAMES if gen1[n] != gen2[n]]; check(len(changed) >= 4, changed); out["files_changing_between_generations"] = len(changed)
for k in (1, 4, 7, 9):
    d = tmp / f"mixed_{k}"; W(d)  # gen2 inputs now -> establish "old" by copying gen1 bytes in
    for n in NAMES: (d / n).write_bytes(gen1[n])
    FAIL[NAMES[k]] = OSError; _, e = attempt(W, d, through_day="2026-10-27"); FAIL.clear()
    now_b = {n: (d / n).read_bytes() for n in NAMES}
    new_prefix = all(now_b[n] == gen2[n] for n in NAMES[:k]); old_suffix = all(now_b[n] == gen1[n] for n in NAMES[k:])
    check(e == "OSError" and new_prefix and old_suffix, (k, NAMES[k], e))
    # the summary json (position 0) carries new through_day while the later files are old generation
    check(json.loads(now_b[NAMES[0]].decode("utf-8"))["through_day"] == "2026-10-27", "summary new")
out["mixed_generation_on_failure"] = "new_prefix+old_suffix (no temp-file/atomic replace, no manifest)"
put(EVAL / "feature_mart" / "opening_rank1" / "feature_mart.json", {"schema_version": "s", "episodes": F})  # restore
# ---- renderer failure mid-sequence (render_* are called inline when the file is reached)
def boom(n): return lambda *a, **k: (_ for _ in ()).throw(RuntimeError("render boom " + n))
for label, attr, fn_name, keep in (("summary_md", "render_short_alpha_discriminator", None, 1), ("casebook_md", "render_opening_overshoot_casebook", None, 7), ("matrix_md", "render_opening_policy_matrix", None, 9)):
    d = tmp / f"render_{label}"; old = getattr(pkg, attr); setattr(pkg, attr, boom(label)); _, e = attempt(W, d); setattr(pkg, attr, old)
    check(e == "RuntimeError" and listing(d) == sorted(NAMES[:keep]), (label, e, listing(d)))
out["render_failure"] = "prefix written, later files absent, RuntimeError propagates"
# ---- build failure: nothing created (build precedes mkdir); build is read-only
put(EVAL / "feature_mart" / "opening_rank1" / "feature_mart.json", {"schema_version": "s", "episodes": [{"identity": "str", "scanner": {}}]})
d = tmp / "never"; _, e = attempt(W, d); check(e == "ValueError" and not d.exists(), (e, d.exists())); out["build_failure"] = e + ":no_dir"
put(EVAL / "feature_mart" / "opening_rank1" / "feature_mart.json", {"schema_version": "s", "episodes": F})
# missing required sources -> INVALID_REQUIRED_SOURCE but still writes all 10 files (status in result, no exception)
d = tmp / "invalid"; r = W(d, reports_root=tmp / "empty_reports"); check(r["integrity_status"] == "INVALID_REQUIRED_SOURCE" and listing(d) == sorted(NAMES), (r["integrity_status"], listing(d))); out["invalid_required_writes_all_files"] = True
check(json.loads((d / "short_alpha_discriminator.json").read_text(encoding="utf-8"))["integrity"]["source_errors"] == ["MISSING_ARTIFACT"] * 2 + ["MISSING_ARTIFACT"], "source errors recorded")
# ---- output_dir / argument edges
_, e_none = attempt(W, None); out["output_dir_none"] = e_none; check(e_none == "TypeError", e_none)
(tmp / "afile").write_text("x"); _, e_file = attempt(W, tmp / "afile"); out["output_dir_is_file"] = e_file; check(e_file in ("FileExistsError", "NotADirectoryError"), e_file)
r = W(str(tmp / "strdir")); check(listing(tmp / "strdir") == sorted(NAMES), "str output_dir accepted")
r = pkg.write_short_alpha_discriminator(reports_root=str(R), through_day="2026-10-26T23:59:59", output_dir=tmp / "strroot"); check(json.loads((tmp / "strroot/short_alpha_discriminator.json").read_text(encoding="utf-8"))["through_day"] == "2026-10-26", "reports_root str, through_day truncated to date")
out["arg_exc"] = {"through_day_none": attempt(pkg.write_short_alpha_discriminator, reports_root=R, through_day=None, output_dir=tmp / "x1")[1], "reports_root_none": attempt(pkg.write_short_alpha_discriminator, reports_root=None, through_day="2026-10-26", output_dir=tmp / "x2")[1],
                  "positional": attempt(pkg.write_short_alpha_discriminator, R, "d", tmp / "x3")[1]}
check(not (tmp / "x1").exists() and not (tmp / "x2").exists(), "argument errors happen before mkdir")
exo = attempt(W, Path("/proc/nonexistent_rf034"))[1]; out["outside_write"] = exo; check(exo == "OSError", exo)
net = [b for b in bad if not b.startswith(("write:", "write_text:", "mkdir:"))]; check(not net, bad)
check(not any(b.startswith(("write:", "write_text:")) and b.split(":", 1)[1].startswith(repo) for b in bad), "no write into repo")
print(json.dumps(out, sort_keys=True, ensure_ascii=False, default=str))
print("RF034_WRITE_SHORT_ALPHA_PARTIAL_OK files=10 fail_positions=10 prefix_state=exact mixed_generation=yes render_fail=prefix build_fail=no_dir invalid_required=writes_10 idempotent=yes outside_write=%s net_attempts=%d debug=%s" % (out["outside_write"], len(net), __debug__))
