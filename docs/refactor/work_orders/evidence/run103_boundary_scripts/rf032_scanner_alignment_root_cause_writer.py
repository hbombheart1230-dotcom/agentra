# RF-032: evaluation/scanner_alignment_root_cause.py (classify/build/render/range/write) -- tmp reports root only. Reads evaluation/daily/<d>/selection_authority_audit.json and evaluation/trades/<d>/*/trade_{read_model,evaluation}.json;
# writes <root>/evaluation/range/<start>_<end>/scanner_alignment_root_cause_report.{json,md}. Writes outside tmp, network, subprocess, sqlite blocked. Default reports_root never used.
import os, sys, json, copy, shutil, socket, subprocess, sqlite3, builtins, importlib, tempfile
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
mod = importlib.import_module("libs.reporting.evaluation.scanner_alignment_root_cause")
tmp = Path(tempfile.mkdtemp(prefix="rf032_sarc_")).resolve(); os.chdir(tmp)
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
root = tmp / "reports"
snap = lambda: {str(p.relative_to(tmp).as_posix()): (p.read_bytes() if p.is_file() else None) for p in tmp.rglob("*")}
def mdl(sel_rank=None, top=None, sel=None, ret=None):
    m = {"selection": {}}
    if sel_rank is not None: m["selection"]["selected_rank"] = sel_rank
    if top is not None: m["selection"]["scanner_top1"] = {"score_total": top}
    if sel is not None: m["selection"]["selected_candidate"] = {"score_total": sel}
    if ret is not None: m["outcome"] = {"net_return_pct": ret}
    return m
def R(raw="A", post="A", selected="A", executed="A", **kw): return {"raw_scanner_top1": raw, "post_strategy_top1": post, "selected_symbol": selected, "executed_symbol": executed, **kw}
cl = mod.classify_scanner_alignment_root_cause
out = {}
# ---- classify: priority order and boundaries
cases = {
    "missing_raw": (R(raw=""), mdl(), None, "Missing Evidence", "high"),
    "missing_exec": (R(executed=""), mdl(), None, "Missing Evidence", "high"),
    "sym_final": (R(final_to_executed_changed=True), mdl(), None, "Symbol Mapping", "high"),
    "sym_monitor": (R(monitor_to_commander_changed=True), mdl(), None, "Symbol Mapping", "high"),
    "sym_selmon": (R(selected_to_monitor_changed=True, raw="B"), mdl(), -1.0, "Symbol Mapping", "high"),
    "filtering": (R(raw="A", post="A", selected="B", executed="B"), mdl(sel_rank=3, top=0.9, sel=0.5), None, "Candidate Filtering", "high"),
    "filter_rank1_not": (R(selected="B", executed="B"), mdl(sel_rank=1), None, "Aligned / No Alignment Issue", "medium"),  # selected!=post but rank 1 -> falls through
    "filter_norank": (R(selected="B", executed="B"), mdl(), None, "Aligned / No Alignment Issue", "medium"),
    "override": (R(raw="A", post="B", selected="B", executed="B"), mdl(), None, "Strategist Override", "medium"),
    "drift_raw_post": (R(raw="A", post="B", selected="C", executed="C"), mdl(), None, "Rank Drift", "medium"),
    "drift_rank2": (R(raw="A", post="A", selected="A", executed="A"), mdl(sel_rank=2), None, "Rank Drift", "medium"),
    "ranking_failure": (R(), mdl(sel_rank=1), -0.01, "Scanner Ranking Failure", "medium"),
    "zero_return_aligned": (R(), mdl(sel_rank=1), 0.0, "Aligned / No Alignment Issue", "medium"),
    "positive_aligned": (R(), mdl(), 2.0, "Aligned / No Alignment Issue", "medium"),
}
for name, (row, m, nr, cause, conf) in cases.items():
    r = cl(row=row, model=m, net_return_pct=nr)
    check(r["root_cause"] == cause and r["confidence"] == conf, (name, r))
    out.setdefault("causes", {})[name] = r["root_cause"]
r = cl(row=R(selected="B", executed="B"), model=mdl(sel_rank=3, top=0.9, sel=0.5), net_return_pct=None); check(r["score_gap"] == 0.4 and r["selected_rank"] == 3 and r["reasons"] == ["selected candidate is below post-strategy top1", "selected_rank=3", "score_gap=0.4"], r)
r = cl(row=R(selected="B", executed="B"), model=mdl(sel_rank=3, top="x", sel=0.5), net_return_pct=None); check(r["score_gap"] is None and r["reasons"][-1] == "selected_rank=3", r)  # non-numeric score -> no gap
m_sel = {"selection": {"selected_candidate": {"rank": "2", "score_total": 1}, "scanner_top1": {"score_total": 3}}}
r = cl(row=R(), model=m_sel, net_return_pct=None); check(r["selected_rank"] == 2 and r["root_cause"] == "Rank Drift" and r["score_gap"] == 2, r)  # candidate.rank string
r = cl(row=R(), model={}, net_return_pct=None); check(r["root_cause"] == "Aligned / No Alignment Issue" and r["selected_rank"] is None, r)
r = cl(row=R(), model={"selection": "str"}, net_return_pct=None); check(r["root_cause"] == "Aligned / No Alignment Issue", r)
r = cl(row={}, model={}, net_return_pct=None); check(r["root_cause"] == "Missing Evidence", r)
out["classify_exc"] = {"none_row": attempt(cl, row=None, model={}, net_return_pct=None)[1], "none_model": attempt(cl, row=R(), model=None, net_return_pct=None)[1], "kw_missing": attempt(cl, row=R())[1]}
# ---- per-day build
sa = {"rows": [
    dict(R(), trade_id="T1", symbol="A"),  # aligned, +ret from evaluation
    dict(R(selected="B", executed="B"), trade_id="T2"),  # filtering via model rank 3
    dict(R(raw="A", post="B", selected="B", executed="B"), trade_id="T3"),  # override
    dict(R(), trade_id="T4"),  # aligned + negative -> ranking failure
    dict(R(raw=""), trade_id="T5"),  # missing evidence
    "junk", None,
    dict(R(selected="C", executed="C", raw="A", post="B"), trade_id="NOTRADE"),  # drift, model/eval absent
]}
models = [dict(mdl(sel_rank=3, top=0.9, sel=0.5), trade_id="T2"), dict(mdl(ret=-1.5), trade_id="T4"), dict(mdl(), trade_id="T1")]
evals = [{"trade_id": "T1", "realized_outcome": {"net_return_pct": "2.5"}}, {"trade_id": "T4", "realized_outcome": {"net_return_pct": -0.5}}, {"trade_id": "T3", "realized_outcome": {"net_return_pct": "bad"}}]
inp = copy.deepcopy((models, evals, sa))
rp = mod.build_scanner_alignment_root_cause_report(day="2026-09-01", models=models, evaluations=evals, selection_authority=sa)
check((models, evals, sa) == inp, "build mutated input")
check(rp["schema_version"] == "scanner_alignment_root_cause.v1" and rp["behavior_effect"] == "observation_only" and rp["trade_count"] == 6, (rp["schema_version"], rp["trade_count"]))
rows = {r["trade_id"]: r for r in rp["rows"]}
check(rows["T1"]["net_return_pct"] == 2.5 and rows["T4"]["net_return_pct"] == -0.5, (rows["T1"]["net_return_pct"], rows["T4"]["net_return_pct"]))  # evaluation overrides model outcome (-1.5)
check(rows["T3"]["net_return_pct"] is None and rows["NOTRADE"]["net_return_pct"] is None, "non-numeric/absent -> None")
check(rows["T4"]["root_cause"] == "Scanner Ranking Failure" and rows["T4"]["diagnostic_kind"] == "outcome_conditioned" and rows["T4"]["causal_eligible"] is False, rows["T4"])
check(rows["T2"]["root_cause"] == "Candidate Filtering" and rows["T2"]["causal_eligible"] is True, rows["T2"])
check(rows["T5"]["diagnostic_kind"] == "evidence_gap" and rows[""]["root_cause"] == "Missing Evidence" if "" in rows else True, "evidence gap")
cs = {c["root_cause"]: c for c in rp["cause_summary"]}
check(list(c["root_cause"] for c in rp["cause_summary"]) == list(mod.ROOT_CAUSES), "cause order")
check(cs["Scanner Ranking Failure"]["negative_impact_pct"] == -0.5 and cs["Aligned / No Alignment Issue"]["return_observation_count"] == 1 and cs["Aligned / No Alignment Issue"]["trade_count"] == 1, cs["Aligned / No Alignment Issue"])
check(rp["largest_structural_root_cause"].get("root_cause") in ("Candidate Filtering", "Strategist Override", "Rank Drift"), rp["largest_structural_root_cause"])
check(rp["q15_behavior_patch_candidate"] == mod._patch_candidate(rp["largest_structural_root_cause"]["root_cause"]), "q15 candidate")
out["day_cause_counts"] = {k: v["trade_count"] for k, v in cs.items()}
out["largest"] = (rp["largest_root_cause"].get("root_cause"), rp["largest_behavior_root_cause"].get("root_cause"), rp["largest_structural_root_cause"].get("root_cause"))
pe = mod.build_scanner_alignment_root_cause_report(day="d", models=[], evaluations=[], selection_authority={})
check(pe["trade_count"] == 0 and pe["largest_root_cause"] == {} and pe["q15_behavior_patch_candidate"].startswith("No scanner-alignment"), pe["q15_behavior_patch_candidate"])
out["build_exc"] = {"none_sa": attempt(mod.build_scanner_alignment_root_cause_report, day="d", models=[], evaluations=[], selection_authority=None)[1],
                    "none_models": attempt(mod.build_scanner_alignment_root_cause_report, day="d", models=None, evaluations=[], selection_authority={})[1],
                    "models_str": attempt(mod.build_scanner_alignment_root_cause_report, day="d", models=["x"], evaluations=[], selection_authority={})[1],
                    "sa_rows_none": attempt(mod.build_scanner_alignment_root_cause_report, day="d", models=[], evaluations=[], selection_authority={"rows": None})[1]}
# ---- render
md = mod.render_scanner_alignment_root_cause_report(rp); check(md == mod.render_scanner_alignment_root_cause_report(copy.deepcopy(rp)), "render nondeterministic")
check(md.startswith("# Q14 Scanner Alignment Root Cause - 2026-09-01") and "## Root Cause Summary" in md and "## Rows" in md and "| T4 | A |" in md and "-0.5000%" in md and md.endswith("\n"), md[:160])
check("| T3 |" in md and "| - |" in md, "none return rendered as -")
mde = mod.render_scanner_alignment_root_cause_report({}); check("Trades: 0" in mde and "`-`" in mde, mde[:200])
out["render_exc"] = {"none": attempt(mod.render_scanner_alignment_root_cause_report, None)[1], "bad_win_rate": attempt(mod.render_scanner_alignment_root_cause_report, {"cause_summary": [{"win_rate": "x"}]})[1]}
# ---- range from tmp tree
def W(d, name, obj, raw=False): put(root / "evaluation" / d / name, obj, raw)
W("daily/2026-09-01", "selection_authority_audit.json", sa)
for tid, m_, e_ in (("T1", models[2], evals[0]), ("T2", models[0], None), ("T4", models[1], evals[1])):
    W(f"trades/2026-09-01/{tid}", "trade_read_model.json", m_)
    if e_: W(f"trades/2026-09-01/{tid}", "trade_evaluation.json", e_)
W("trades/2026-09-01/BROKEN", "trade_read_model.json", "{bad", raw=True)
(root / "evaluation/trades/2026-09-01/afile").write_text("x")  # file entry, skipped
W("daily/2026-09-02", "selection_authority_audit.json", [1])  # list -> {} ; no models -> day skipped
W("trades/2026-09-03/TX", "trade_evaluation.json", {"trade_id": "TX"})  # evaluation only -> day included with 0 rows
W("daily/2026-09-04", "selection_authority_audit.json", {"rows": [dict(R(selected="B", executed="B", raw="A", post="B"), trade_id="Z1")]})
s0 = snap()
rg = mod.build_scanner_alignment_root_cause_range(reports_root=root, start="2026-08-31", end="2026-09-05")
check(snap() == s0, "range build mutated tree")
check(rg["schema_version"] == "scanner_alignment_root_cause_range.v1" and rg["day_count"] == 3 and rg["trade_count"] == 7 and [d["day"] for d in rg["daily_rows"]] == ["2026-09-01", "2026-09-03", "2026-09-04"], (rg["day_count"], rg["trade_count"], rg["daily_rows"]))
rcs = {c["root_cause"]: c["trade_count"] for c in rg["cause_summary"]}
check(rcs["Strategist Override"] == 2 and rcs["Candidate Filtering"] == 1 and sum(rcs.values()) == 7, rcs)
out["range_cause_counts"] = rcs
out["range_daily"] = [(d["day"], d["trade_count"], d["largest_root_cause"]) for d in rg["daily_rows"]]
rg0 = mod.build_scanner_alignment_root_cause_range(reports_root=tmp / "nope", start="2026-09-01", end="2026-09-03"); check(rg0["day_count"] == 0 and rg0["trade_count"] == 0 and rg0["largest_root_cause"] == {}, rg0["day_count"])
rg_rev = mod.build_scanner_alignment_root_cause_range(reports_root=root, start="2026-09-05", end="2026-09-01"); check(rg_rev["day_count"] == 0, "start>end -> empty (no error)")
out["range_exc"] = {"bad_date": attempt(mod.build_scanner_alignment_root_cause_range, reports_root=root, start="x", end="2026-09-01")[1], "none_end": attempt(mod.build_scanner_alignment_root_cause_range, reports_root=root, start="2026-09-01", end=None)[1], "none_root": attempt(mod.build_scanner_alignment_root_cause_range, reports_root=None, start="2026-09-01", end="2026-09-01")[1]}
# ---- write
r, e = attempt(mod.write_scanner_alignment_root_cause_range, reports_root=root, start="2026-08-31", end="2026-09-05"); check(e is None, e)
jp, mp = Path(r["json"]), Path(r["markdown"])
check(jp == root / "evaluation/range/2026-08-31_2026-09-05/scanner_alignment_root_cause_report.json" and mp.name == "scanner_alignment_root_cause_report.md", r)
check(json.loads(jp.read_text(encoding="utf-8")) == rg and mp.read_text(encoding="utf-8") == mod.render_scanner_alignment_root_cause_report(rg), "written != built")
b1 = (jp.read_bytes(), mp.read_bytes()); r2, e2 = attempt(mod.write_scanner_alignment_root_cause_range, reports_root=root, start="2026-08-31", end="2026-09-05"); check(e2 is None and (jp.read_bytes(), mp.read_bytes()) == b1, "not idempotent")
new = {k for k in snap() if k not in s0}; check(new == {"reports/evaluation/range", "reports/evaluation/range/2026-08-31_2026-09-05", "reports/evaluation/range/2026-08-31_2026-09-05/scanner_alignment_root_cause_report.json", "reports/evaluation/range/2026-08-31_2026-09-05/scanner_alignment_root_cause_report.md"}, new)
check(all(snap().get(k) == v for k, v in s0.items()), "inputs mutated")
out["files"] = len(new) - 2
ex = attempt(mod.write_scanner_alignment_root_cause_range, reports_root=Path("/proc/nonexistent_rf032"), start="2026-09-01", end="2026-09-01")[1]; out["outside_write"] = ex; check(ex == "OSError", ex)
(root / "evaluation/range").mkdir(exist_ok=True); (root / "evaluation/range/2026-09-09_2026-09-09").write_text("x")
ex2 = attempt(mod.write_scanner_alignment_root_cause_range, reports_root=root, start="2026-09-09", end="2026-09-09")[1]; out["dir_collision"] = ex2; check(ex2 in ("FileExistsError", "NotADirectoryError"), ex2)
net = [b for b in bad if not b.startswith(("write:", "mkdir:"))]; check(not net, bad)
print(json.dumps(out, sort_keys=True, ensure_ascii=False, default=str))
print("RF032_SCANNER_ALIGNMENT_ROOT_CAUSE_OK classify=%d day_trades=%d range_days=%d range_trades=%d idempotent=yes files=%d outside_write=%s dir_collision=%s net_attempts=%d debug=%s" % (len(cases) + 4, rp["trade_count"], rg["day_count"], rg["trade_count"], out["files"], out["outside_write"], out["dir_collision"], len(net), __debug__))
