# RF-034: short_alpha_discriminator/pipeline.py::build_short_alpha_discriminator -- source-artifact integrity: missing / corrupt / non-object / non-utf8 / directory JSON for the 3 sources
# (opening_rank1 cumulative, feature_mart, latest cumulative agent scorecard) -> integrity.status / source_errors / sources / State and exception boundaries. Read-only fixtures under a tmp reports root.
# Reuses nothing from the write_short_alpha partial-failure harness (that one covers the 10-file writer); this one is the pure-read build() with fake read-only fixtures. Writes outside tmp, network, subprocess, sqlite blocked.
import os, sys, json, copy, shutil, socket, subprocess, sqlite3, builtins, importlib, tempfile
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
pkg = importlib.import_module("libs.reporting.short_alpha_discriminator.pipeline")
tmp = Path(tempfile.mkdtemp(prefix="rf034_bsa_")).resolve(); os.chdir(tmp)
bad = []
def blocked(n):
    def f(*a, **k): bad.append(n); raise OSError("blocked " + n)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("cc"); socket.getaddrinfo = blocked("gai")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite")
_open = builtins.open; _wt = Path.write_text; _wb = Path.write_bytes; _mk = Path.mkdir
def inside(p):
    try: Path(p).resolve().relative_to(tmp); return True
    except Exception: return False
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+") and not inside(f): bad.append("write:" + str(f)); raise OSError("blocked write")
    return _open(f, mode, *a, **k)
builtins.open = gopen
def mk(self, *a, **k):
    if not inside(self): bad.append("mkdir:" + str(self)); raise OSError("blocked mkdir")
    return _mk(self, *a, **k)
Path.mkdir = mk
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED@%d: " % sys._getframe(1).f_lineno + str(m))
def attempt(fn, *a, **k):
    try: return fn(*a, **k), None
    except Exception as e: return None, type(e).__name__
def put(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True); _wt(p, json.dumps(obj), encoding="utf-8")
def putraw(p, data):
    p.parent.mkdir(parents=True, exist_ok=True); _wb(p, data)
def ep(did, day, sym, epoch, cls, sec=None, ret5=None):
    obs = {"asset_observation": {"asset_class": cls}}
    if sec is not None: obs["decision_from_open_sec"] = sec
    cps = {"+5m": {"live_net_return_pct": ret5}} if ret5 is not None else {}
    return {"decision_id": did, "day": day, "symbol": sym, "decision_epoch": epoch, "opening_observability": obs, "checkpoints": cps}
def ft(did, band="HIGH", setup="DIRECTIONAL_BREADTH"):
    return {"identity": {"decision_id": did}, "scanner": {"risk_band": band, "candidate_setup": setup, "sources": ["top_value"], "score_total": 70.0}, "strategy": {"entry_horizon": "E1", "tactic_id": "T1"}}
O = [ep("e1", "2026-08-20", "A", 100, "common_stock", sec=30, ret5=1.0), ep("e2", "2026-08-21", "B", 200, "common_stock", sec=40, ret5=-1.0)]
F = [ft("e1"), ft("e2")]
R = tmp / "reports"; EV = R / "evaluation"
OP = EV / "opening_rank1_shadow" / "opening_rank1_shadow_cumulative.json"; FP = EV / "feature_mart" / "opening_rank1" / "feature_mart.json"
SC = lambda n: EV / "agent_effectiveness" / n / "agent_effectiveness_scorecard.json"
def reset(opening=O, feature=F, scorecard="cumulative_a"):
    shutil.rmtree(R, ignore_errors=True)
    put(OP, {"schema_version": "op.v1", "episodes": opening}); put(FP, {"schema_version": "fm.v1", "episodes": feature})
    if scorecard: put(SC(scorecard), {"schema_version": "sc.v1"})
def B(**kw): return pkg.build_short_alpha_discriminator(reports_root=kw.pop("reports_root", R), through_day=kw.pop("through_day", "2026-10-26T23:59"))
snap = lambda: {str(p.relative_to(tmp).as_posix()): p.read_bytes() for p in tmp.rglob("*") if p.is_file()}
out = {}
# ---- all good -> PASS, read-only, deterministic
reset(); s0 = snap(); p = B()
check(p["integrity"] == {"status": "PASS", "source_errors": [], "join": {"opening_episode_count": 2, "feature_episode_count": 2, "joined_episode_count": 2, "missing_join_count": 0, "missing_decision_ids": []}}, p["integrity"])
check(p["through_day"] == "2026-10-26" and p["behavior_change_authorized"] is False and p["sources"]["opening_rank1"] == {"path": str(OP), "available": True, "error": None, "schema_version": "op.v1"}, p["sources"])
check(p["sources"]["feature_mart"]["schema_version"] == "fm.v1" and p["sources"]["agent_effectiveness"]["path"] == str(SC("cumulative_a")) and p["sources"]["agent_effectiveness"]["schema_version"] == "sc.v1", p["sources"])
check(snap() == s0 and json.dumps(B(), sort_keys=True, default=str) == json.dumps(p, sort_keys=True, default=str), "read-only + deterministic")
check(p["cohort_review"] and p["opening_policy_matrix"] is not None, "sections present")
# ---- each required source x corruption kind -> INVALID_REQUIRED_SOURCE, never an exception; sections built from {} for that source
KINDS = {"missing": (None, "MISSING_ARTIFACT"), "invalid_json": (b"{not json", "INVALID_ARTIFACT:JSONDecodeError"), "empty_file": (b"", "INVALID_ARTIFACT:JSONDecodeError"),
         "non_utf8": (b"\xff\xfe\x00bad", "INVALID_ARTIFACT:UnicodeDecodeError"), "root_array": (b"[1,2]", "SCHEMA_MISMATCH:ROOT_NOT_OBJECT"), "root_null": (b"null", "SCHEMA_MISMATCH:ROOT_NOT_OBJECT"), "root_str": (b'"x"', "SCHEMA_MISMATCH:ROOT_NOT_OBJECT")}
results = {}
for which, path, key in (("opening", OP, "opening_rank1"), ("feature", FP, "feature_mart")):
    for kind, (data, want) in KINDS.items():
        reset()
        if data is None: path.unlink()
        else: putraw(path, data)
        got = B(); src = got["sources"][key]
        check(got["integrity"]["status"] == "INVALID_REQUIRED_SOURCE" and got["integrity"]["source_errors"] == [want] and src["error"] == want and src["available"] == (data is not None) and "schema_version" not in src, (which, kind, got["integrity"], src))
        check(got["integrity"]["join"]["joined_episode_count"] == 0 and got["behavior_change_authorized"] is False, (which, kind, got["integrity"]["join"]))
        results[(which, kind)] = want
out["required_cases"] = len(results)
# directory in place of the file: exists() True, read_text raises an OSError subclass (platform-specific name) -> INVALID_ARTIFACT:<name>
reset(); OP.unlink(); OP.mkdir()
got = B(); e = got["sources"]["opening_rank1"]["error"]
check(got["integrity"]["status"] == "INVALID_REQUIRED_SOURCE" and e.startswith("INVALID_ARTIFACT:") and e.split(":")[1] in ("IsADirectoryError", "PermissionError") and got["sources"]["opening_rank1"]["available"] is True, e)
out["directory_error"] = e.split(":")[1]
# both required missing -> two errors in source order (opening, feature) + optional scorecard error appended third
reset(scorecard=None); OP.unlink(); FP.unlink()
got = B(); check(got["integrity"]["source_errors"] == ["MISSING_ARTIFACT"] * 3 and got["integrity"]["status"] == "INVALID_REQUIRED_SOURCE" and got["sources"]["agent_effectiveness"] == {"path": str(EV / "agent_effectiveness"), "available": False, "error": "MISSING_ARTIFACT"}, got["integrity"])
reset(); putraw(OP, b"[]"); putraw(FP, b"{x"); putraw(SC("cumulative_a"), b"7")
got = B(); check(got["integrity"]["source_errors"] == ["SCHEMA_MISMATCH:ROOT_NOT_OBJECT", "INVALID_ARTIFACT:JSONDecodeError", "SCHEMA_MISMATCH:ROOT_NOT_OBJECT"], got["integrity"]["source_errors"])
# required invalid wins over join gaps; empty required objects are NOT errors (PASS with zero episodes)
reset(); put(OP, {"schema_version": "op.v1", "episodes": O + [ep("e9", "2026-08-22", "Z", 300, "common_stock")]}); putraw(FP, b"nope")
check(B()["integrity"]["status"] == "INVALID_REQUIRED_SOURCE", "required beats join gap")
reset(); put(OP, {}); put(FP, {}); got = B()
check(got["integrity"]["status"] == "PASS" and got["integrity"]["join"]["opening_episode_count"] == 0 and got["sources"]["opening_rank1"]["schema_version"] is None, got["integrity"])
out["empty_objects"] = got["integrity"]["status"]
# ---- optional scorecard: missing / corrupt only -> PASS_WITH_OPTIONAL_SOURCE_GAP; join gap beats optional gap
reset(scorecard=None); got = B(); check(got["integrity"]["status"] == "PASS_WITH_OPTIONAL_SOURCE_GAP" and got["integrity"]["source_errors"] == ["MISSING_ARTIFACT"], got["integrity"])
reset(); putraw(SC("cumulative_a"), b"{{"); got = B(); check(got["integrity"]["status"] == "PASS_WITH_OPTIONAL_SOURCE_GAP" and got["integrity"]["source_errors"] == ["INVALID_ARTIFACT:JSONDecodeError"], got["integrity"])
reset(scorecard=None); put(OP, {"episodes": O + [ep("e9", "2026-08-22", "Z", 300, "common_stock")]}); got = B()
check(got["integrity"]["status"] == "PASS_WITH_JOIN_GAPS" and got["integrity"]["join"]["missing_decision_ids"] == ["e9"] and got["integrity"]["source_errors"] == ["MISSING_ARTIFACT"], got["integrity"])
# latest cumulative scorecard = lexicographically LAST cumulative_* dir; a corrupt latest is NOT skipped in favour of an older valid one; non-matching dirs ignored
reset(); put(SC("cumulative_b"), {"schema_version": "sc.b"}); put(SC("cumulative_9"), {"schema_version": "sc.9"}); put(SC("weekly_z"), {"schema_version": "sc.weekly"}); put(EV / "agent_effectiveness" / "cumulative_c" / "other.json", {"x": 1})
got = B(); check(got["sources"]["agent_effectiveness"]["schema_version"] == "sc.b" and got["sources"]["agent_effectiveness"]["path"] == str(SC("cumulative_b")), got["sources"]["agent_effectiveness"])
putraw(SC("cumulative_z"), b"oops"); got = B(); check(got["integrity"]["status"] == "PASS_WITH_OPTIONAL_SOURCE_GAP" and got["sources"]["agent_effectiveness"]["path"] == str(SC("cumulative_z")), got["integrity"])
out["latest_scorecard"] = "lexicographic_last_no_fallback"
reset(scorecard=None); put(SC("cumulative_10"), {"schema_version": "sc.10"}); put(SC("cumulative_9"), {"schema_version": "sc.9"})
check(B()["sources"]["agent_effectiveness"]["schema_version"] == "sc.9", "string sort: cumulative_9 > cumulative_10")
out["string_sort"] = "cumulative_9>cumulative_10"
# ---- malformed ROWS inside valid objects: non-list episodes tolerated, non-mapping rows filtered, nested non-mapping fields raise (not caught by build)
for name, eps in (("episodes_null", None), ("episodes_dict", {"e1": O[0]}), ("episodes_str", "abc"), ("episodes_int", 5), ("rows_mixed", [1, "x", None, O[0], [2]])):
    reset(); put(OP, {"episodes": eps})
    r_, e_ = attempt(B)
    out["rows_" + name] = e_ or r_["integrity"]["join"]["opening_episode_count"]
check(out["rows_episodes_null"] == 0 and out["rows_episodes_dict"] == 0 and out["rows_rows_mixed"] == 1, {k: v for k, v in out.items() if k.startswith("rows_")})
reset(); put(FP, {"episodes": [{"identity": "str", "scanner": {}}] + F}); _, e1 = attempt(B)
reset(); put(FP, {"episodes": [{"identity": None}] + F}); _, e2 = attempt(B)
reset(); put(OP, {"episodes": [dict(O[0], opening_observability="abc")]}); _, e3 = attempt(B)
reset(); put(FP, {"episodes": [dict(F[0], scanner=5)]}); _, e4 = attempt(B)
reset(); put(FP, {"episodes": [dict(F[0], scanner={"sources": 5})]}); _, e5 = attempt(B)
out["nested_exc"] = {"identity_str": e1, "identity_none": e2, "observability_str": e3, "scanner_int": e4, "sources_int": e5}
check(all(out["nested_exc"].values()) and e2 == "TypeError", out["nested_exc"])   # propagate; no INVALID status is produced for malformed-but-parseable rows
# ---- argument handling
reset(); a = B(reports_root=str(R)); check(a["integrity"]["status"] == "PASS", "str reports_root accepted")
out["args"] = {"root_none": attempt(pkg.build_short_alpha_discriminator, reports_root=None, through_day="2026-10-26")[1], "day_none": attempt(pkg.build_short_alpha_discriminator, reports_root=R, through_day=None)[1], "day_int": attempt(pkg.build_short_alpha_discriminator, reports_root=R, through_day=20261026)[1]}
check(out["args"] == {"root_none": "TypeError", "day_none": "TypeError", "day_int": "TypeError"}, out["args"])
check(B(through_day="")["through_day"] == "" and B(through_day="abc")["through_day"] == "abc", "through_day is only truncated, never validated")
nr = tmp / "nonexistent_root"; got = B(reports_root=nr)
check(got["integrity"]["status"] == "INVALID_REQUIRED_SOURCE" and got["integrity"]["source_errors"] == ["MISSING_ARTIFACT"] * 3 and not nr.exists(), "missing root: no mkdir")
# input mutation: build must not alter the files
reset(); s0 = snap(); B(); check(snap() == s0, "inputs unchanged")
check(not [b for b in bad if b in ("connect", "cc", "gai", "Popen", "run", "call", "check_call", "check_output", "os.system", "sqlite")], bad)
_, e = attempt(builtins.open, str(Path(tempfile.gettempdir()).parent / "rf034_bsa_outside.txt"), "w"); check(e == "OSError" and any(b.startswith("write:") for b in bad), (e, bad))
os.chdir(repo); shutil.rmtree(tmp, ignore_errors=True)
print("RF034_BUILD_SOURCE_INTEGRITY_OK required_cases=%d directory=%s empty_objects=%s latest_scorecard=%s string_sort=%s nested_row_exc=propagate outside_write=OSError net_attempts=0" % (out["required_cases"], out["directory_error"], out["empty_objects"], out["latest_scorecard"], out["string_sort"]))
