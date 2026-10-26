# RF-034 short_alpha_discriminator render_short_alpha_discriminator <- pipeline consumer (synthetic tmp-only) (synthetic tmp-only, no network, no order).
import os, sys, json, socket, subprocess, sqlite3, builtins, importlib, tempfile, hashlib
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
sys.path.insert(0, os.getcwd())
from pathlib import Path
ROOT = Path(os.getcwd()).resolve()
tmp = Path(tempfile.mkdtemp(prefix="rf034_render_")).resolve()
bad = []
def blocked(name):
    def f(*a, **k): bad.append(name); raise OSError("blocked " + name)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("create_connection"); socket.getaddrinfo = blocked("getaddrinfo")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite3.connect")
def inside(p):
    try: Path(p).resolve().relative_to(tmp); return True
    except Exception: return False
_open = builtins.open
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+") and not inside(f): bad.append("write_open:" + str(f)); raise OSError("blocked write")
    return _open(f, mode, *a, **k)
builtins.open = gopen
_wt, _mk = Path.write_text, Path.mkdir
def wt(self, *a, **k):
    if not inside(self): bad.append("write_text:" + str(self)); raise OSError("blocked")
    return _wt(self, *a, **k)
def mk(self, *a, **k):
    if not inside(self): bad.append("mkdir:" + str(self)); raise OSError("blocked")
    return _mk(self, *a, **k)
Path.write_text, Path.mkdir = wt, mk
def check(cond, msg):
    if not cond: raise SystemExit("CHECK_FAILED: " + msg)
def tree(root):
    return sorted((str(p.relative_to(root)), hashlib.sha1(p.read_bytes()).hexdigest()) for p in Path(root).rglob("*") if p.is_file())


os.chdir(tmp)
sys.path.insert(0, str(ROOT))
os.environ["EVIDENCE_LEDGER_PATH"] = str(tmp / "ledger" / "events.jsonl")
pkg = importlib.import_module("libs.reporting.short_alpha_discriminator.pipeline")
rep = importlib.import_module("libs.reporting.short_alpha_discriminator.report")
R = tmp / "reports"
EVAL = R / "evaluation"
def wj(p, o):
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(o), encoding="utf-8")
# A) render with empty / weird payloads (pure)
md0 = rep.render_short_alpha_discriminator({})
check(md0.startswith("# Short Alpha Discriminator") and "BLOCKED_BY_MARKET_SNAPSHOT_COVERAGE" in md0 and "`None`" in md0, "empty payload render")
check(md0.endswith("\n") is False or True, "n/a")
md_none = rep.render_short_alpha_discriminator({"cohort_review": None, "integrity": "x", "profit_fade_review": [1]})
check(md_none == md0, "non-mapping sections coerced to {} (same bytes as empty)")
check(rep.render_short_alpha_discriminator({}) == md0, "deterministic")
full = {"through_day": "2026-10-26", "behavior_effect": "NONE", "integrity": {"status": "PASS"},
  "cohort_review": {"prospective_contract": {"first_eligible_day": "2026-10-27", "candidate_id": "C1", "conditions": ["a", "b"]}, "prospective": {"episode_count": 3},
     "cohorts": [{"cohort_id": "c", "independent_day_symbol_count": 4, "horizons": {"+5m": {"sample_count": 4, "win_rate": 0.5, "avg_net_return_pct": 0.1, "profit_factor": 1.5}}}],
     "historical_sensitivity": {"without_best_observation": {"excluded_day": "d", "excluded_symbol": "s"}, "by_symbol_leave_one_out": [1, 2], "by_day_leave_one_out": [1]}},
  "profit_fade_review": {"cohort_episode_count": 7, "fixed_horizon_comparison": {"+5m": {"sample_count": 1, "win_rate": 1, "avg_net_return_pct": 1, "profit_factor": 2}}, "profit_lock_proxies": [{"policy_id": "p", "triggered_count": 2}]},
  "scanner_diagnostics": {"score_return_correlation": {"+5m": 0.25, "EOD": None}, "by_candidate_setup": [{"value": "v", "sample_count": 2}], "market_snapshot_coverage": {"coverage": 0.9, "fresh_coverage": 0.5}},
  "strategist_stage2_review": {"official_ranking_overlay": {"state": "S1"}, "observational_splits": [{"dimension": "d", "value": "v", "episode_count": 1}]}}
mdf = rep.render_short_alpha_discriminator(full)
for needle in ("`2026-10-26`", "N=4, WR 50.0%, avg +0.1000%, PF 1.5000", "| `+5m` | 0.2500 |", "| `EOD` | - |", "MARKET_SNAPSHOT_COVERAGE_OK", "`a, b`", "Leave-one-symbol cases: **2**", "`S1`"):
    check(needle in mdf, "missing in render: " + needle)
# render exception boundary: wrong scalar types propagate (no failsoft)
exc = {}
for name, pl in {"corr_str": {"scanner_diagnostics": {"score_return_correlation": {"x": "abc"}}}, "count_str": {"cohort_review": {"cohorts": [{"independent_day_symbol_count": "z"}]}},
                 "cov_str": {"scanner_diagnostics": {"market_snapshot_coverage": {"coverage": "bad"}}}}.items():
    try: rep.render_short_alpha_discriminator(pl); exc[name] = None
    except Exception as e: exc[name] = type(e).__name__
check(set(exc.values()) == {"ValueError"}, "bad scalars raise ValueError: %s" % exc)
# B) pipeline build with no artifacts -> INVALID_REQUIRED_SOURCE, all sources MISSING_ARTIFACT, no write
before = list(tmp.rglob("*"))
p0 = pkg.build_short_alpha_discriminator(reports_root=R, through_day="2026-10-26T09:00")
check(p0["integrity"]["status"] == "INVALID_REQUIRED_SOURCE" and p0["through_day"] == "2026-10-26", "missing sources")
check(all(s["error"] == "MISSING_ARTIFACT" for s in p0["sources"].values()) and p0["behavior_change_authorized"] is False, "source errors")
check(list(tmp.rglob("*")) == before, "build is read-only")
check(rep.render_short_alpha_discriminator(p0).count("`INVALID_REQUIRED_SOURCE`") == 1, "payload->render status shown")
# C) invalid artifact variants
wj(EVAL / "opening_rank1_shadow" / "opening_rank1_shadow_cumulative.json", [1])
(EVAL / "feature_mart" / "opening_rank1").mkdir(parents=True); (EVAL / "feature_mart" / "opening_rank1" / "feature_mart.json").write_text("{bad", encoding="utf-8")
p1 = pkg.build_short_alpha_discriminator(reports_root=R, through_day="2026-10-26")
errs = (p1["sources"]["opening_rank1"]["error"], p1["sources"]["feature_mart"]["error"])
check(errs == ("SCHEMA_MISMATCH:ROOT_NOT_OBJECT", "INVALID_ARTIFACT:JSONDecodeError"), "invalid errs %s" % (errs,))
# D) valid empty-episode sources -> PASS_WITH_OPTIONAL_SOURCE_GAP, then with scorecard -> PASS
wj(EVAL / "opening_rank1_shadow" / "opening_rank1_shadow_cumulative.json", {"schema_version": "s", "episodes": []})
wj(EVAL / "feature_mart" / "opening_rank1" / "feature_mart.json", {"schema_version": "s", "episodes": []})
p2 = pkg.build_short_alpha_discriminator(reports_root=R, through_day="2026-10-26")
check(p2["integrity"]["status"] == "PASS_WITH_OPTIONAL_SOURCE_GAP", "optional gap: %s" % p2["integrity"])
wj(EVAL / "agent_effectiveness" / "cumulative_a" / "agent_effectiveness_scorecard.json", {"schema_version": "s"})
wj(EVAL / "agent_effectiveness" / "cumulative_b" / "agent_effectiveness_scorecard.json", {"schema_version": "s2"})
p3 = pkg.build_short_alpha_discriminator(reports_root=R, through_day="2026-10-26")
check(p3["integrity"]["status"] == "PASS" and p3["sources"]["agent_effectiveness"]["schema_version"] == "s2", "latest cumulative_b picked, PASS")
json.dumps(p3)  # payload JSON-serialisable
md3 = rep.render_short_alpha_discriminator(p3); check("`PASS`" in md3, "render PASS")
# E) write_*: only into tmp output_dir, 10 files, md bytes == render(payload)
out = tmp / "out" / "nested"
res = pkg.write_short_alpha_discriminator(reports_root=R, through_day="2026-10-26", output_dir=out)
check(sorted(p.name for p in out.iterdir()) == sorted(Path(v).name for k, v in res.items() if k.endswith("_path")) and len(list(out.iterdir())) == 10, "10 outputs")
check(res["integrity_status"] == "PASS" and res["behavior_change_authorized"] is False, "write result")
raw_md = (out / "short_alpha_discriminator.md").read_bytes()
want_md = rep.render_short_alpha_discriminator(json.loads((out / "short_alpha_discriminator.json").read_text(encoding="utf-8")))
check(raw_md.decode("utf-8") == want_md.replace(chr(10), os.linesep), "md bytes == render(json payload) with platform newline")
check(not bad, "blocked attempts: %s" % bad)
print("RF034_RENDER_CONSUMER_OK render_cases=empty/coerced/full/exc3 build_status=INVALID/PASS_GAP/PASS write_files=10 md_bytes=match(newline=%r) exc=%s blocked=%d debug=%s" % (os.linesep, sorted(set(exc.values())), len(bad), __debug__))
