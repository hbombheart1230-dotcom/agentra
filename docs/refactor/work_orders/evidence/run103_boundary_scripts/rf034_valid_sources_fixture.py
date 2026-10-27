# RF-034 OWNER FIXTURE (A, for B's independent peer): writes a minimal SCHEMA-VALID source set for
# libs.reporting.short_alpha_discriminator.pipeline.build_short_alpha_discriminator and SELF-VERIFIES integrity PASS on it.
# B reported "supplied-source fixture fail-closed; schema-valid source still missing". Call write_valid_sources(reports_root) from a peer harness, or run this file.
# Sources (paths are what pipeline reads): evaluation/opening_rank1_shadow/opening_rank1_shadow_cumulative.json, evaluation/feature_mart/opening_rank1/feature_mart.json,
# evaluation/agent_effectiveness/<cumulative_*>/agent_effectiveness_scorecard.json. tmp root only; network/subprocess/sqlite blocked; writes confined to tmp.
import os, sys, io, json, socket, subprocess, sqlite3, builtins, importlib, tempfile, shutil
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL", "PROXY")): del os.environ[k]
tmp = Path(tempfile.mkdtemp(prefix="rf034_fix_")).resolve(); os.chdir(tmp)
bad = []
def blocked(n):
    def f(*a, **k): bad.append(n); raise OSError("blocked " + n)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("cc"); socket.getaddrinfo = blocked("gai")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite")
def inside(p):
    try:
        if isinstance(p, int): return True
        ap = os.path.abspath(os.fspath(p)); return ap == str(tmp) or ap.startswith(str(tmp) + os.sep)
    except Exception: return False
_open = io.open
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+") and not inside(f): bad.append("write:" + str(f)); raise OSError("blocked write outside tmp")
    return _open(f, mode, *a, **k)
builtins.open = gopen; io.open = gopen
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED@%d: %s" % (sys._getframe(1).f_lineno, m))
pipe = importlib.import_module("libs.reporting.short_alpha_discriminator.pipeline")

def _episode(did, day, sym, epoch, cls, sec, ret5):
    return {"decision_id": did, "day": day, "symbol": sym, "decision_epoch": epoch,
            "opening_observability": {"asset_observation": {"asset_class": cls}, "decision_from_open_sec": sec},
            "checkpoints": {"+5m": {"live_net_return_pct": ret5}}}
def _feature(did, band="HIGH", setup="DIRECTIONAL_BREADTH"):
    return {"identity": {"decision_id": did}, "scanner": {"risk_band": band, "candidate_setup": setup, "sources": ["top_value"], "score_total": 70.0},
            "strategy": {"entry_horizon": "E1", "tactic_id": "T1"}}
def write_valid_sources(reports_root):
    """Writes the 3 required sources; returns their paths. Episodes span historical (<2026-08-25) and prospective days, common stock + ETF."""
    ev = Path(reports_root) / "evaluation"
    eps = [_episode("e1", "2026-08-20", "A", 100, "common_stock", 30, 1.0), _episode("e2", "2026-08-21", "B", 200, "common_stock", 40, -1.0),
           _episode("e3", "2026-09-01", "C", 300, "etf", 25, 0.5), _episode("e4", "2026-09-02", "A", 400, "common_stock", 35, 2.0)]
    feats = [_feature("e1"), _feature("e2", band="LOW"), _feature("e3"), _feature("e4")]
    paths = {"opening": ev / "opening_rank1_shadow" / "opening_rank1_shadow_cumulative.json", "feature": ev / "feature_mart" / "opening_rank1" / "feature_mart.json",
             "scorecard": ev / "agent_effectiveness" / "cumulative_2026-09-02" / "agent_effectiveness_scorecard.json"}
    payloads = {"opening": {"schema_version": "opening_rank1_shadow_cumulative.v1", "episodes": eps}, "feature": {"schema_version": "opening_rank1_feature_mart.v1", "episodes": feats},
                "scorecard": {"schema_version": "agent_effectiveness_scorecard.v1", "components": {}}}
    for k, p in paths.items():
        p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(payloads[k]), encoding="utf-8")
    return paths

R = tmp / "reports"; paths = write_valid_sources(R)
before = {str(p): p.read_bytes() for p in R.rglob("*") if p.is_file()}
res = pipe.build_short_alpha_discriminator(reports_root=R, through_day="2026-10-26")
integ = res["integrity"]
check(integ["status"] == "PASS" and integ["source_errors"] == [] and integ["join"]["joined_episode_count"] == 4 and integ["join"]["missing_join_count"] == 0, integ)
check(all(res["sources"][k]["available"] and res["sources"][k]["error"] is None for k in ("opening_rank1", "feature_mart", "agent_effectiveness")), res["sources"])
check(res["sources"]["agent_effectiveness"]["path"] == str(paths["scorecard"]) and res["behavior_change_authorized"] is False, res["sources"]["agent_effectiveness"])
check({str(p): p.read_bytes() for p in R.rglob("*") if p.is_file()} == before, "build is read-only")
check(res.get("cohort_review") and res.get("opening_policy_matrix") is not None, "downstream sections present")
# negative control: removing one required source flips to fail-closed
paths["feature"].unlink(); neg = pipe.build_short_alpha_discriminator(reports_root=R, through_day="2026-10-26")
check(neg["integrity"]["status"] == "INVALID_REQUIRED_SOURCE" and neg["integrity"]["source_errors"] == ["MISSING_ARTIFACT"], neg["integrity"])
check(not bad, bad)
out = {"status": integ["status"], "joined": integ["join"]["joined_episode_count"], "negative_control": neg["integrity"]["status"], "sections": sorted(k for k in res if k not in ("sources", "integrity"))[:12]}
shutil.rmtree(tmp, ignore_errors=True)
print(json.dumps(out, sort_keys=True))
print("RF034_VALID_SOURCES_FIXTURE_OK integrity=PASS joined=4 negative_control=INVALID_REQUIRED_SOURCE read_only=yes network=0 debug=%s" % __debug__)
