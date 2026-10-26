# RF-032: evaluation/agent_effectiveness_scorecard.py (build/render/write) -- pure build/render called directly; writer run with build_full_chain_component_review swapped for a fake (plus one run with the real collaborator on an empty tmp reports root). Writes only under tmp. Network/subprocess/sqlite/outside writes blocked.
import os, sys, json, socket, subprocess, sqlite3, builtins, importlib, tempfile
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
mod = importlib.import_module("libs.reporting.evaluation.agent_effectiveness_scorecard")
tmp = Path(tempfile.mkdtemp(prefix="rf032_aes_")).resolve(); os.chdir(tmp)
bad = []
def blocked(n):
    def f(*a, **k): bad.append(n); raise OSError("blocked " + n)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("cc"); socket.getaddrinfo = blocked("gai")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
sqlite3.connect = blocked("sqlite")
def inside(p):
    try: Path(p).resolve().relative_to(tmp); return True
    except Exception: return False
_open = builtins.open; _wt = Path.write_text; _mk = Path.mkdir
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+") and not inside(f): bad.append("write:" + str(f)); raise OSError("blocked write")
    return _open(f, mode, *a, **k)
builtins.open = gopen
def wt(self, *a, **k):
    if not inside(self): bad.append("wt:" + str(self)); raise OSError("blocked write")
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
B = mod.build_agent_effectiveness_scorecard
# 1 empty/garbage input
p = B({}); c = p["components"]
check(p["integrity"]["state"] == "PASS", "integrity empty")
check(c["scanner"]["relative_ranking_state"] == "DEGRADING", "empty scanner decision '' != INSUFFICIENT -> measurable -> DEGRADING")
check(c["monitor_entry"]["state"] == "NEUTRAL" and c["full_system"]["state"] == "NEUTRAL", "empty decision NEUTRAL")
check(c["commander"]["state"] == "NOT_MEASURABLE" and p["behavior_change_authorized" if False else "behavior_change_authorized"] is False, "commander/authorized")
_, e = attempt(B, None); check(e == "AttributeError", "None review " + str(e))
check(B({"evidence": "x", "component_decisions": [1]})["components"]["scanner"]["absolute_edge_state"] == "DEGRADING", "non-mapping tolerated")
# 2 delta states and thresholds
def rev(row, **ev):
    return {"evidence": {"decision_window_attribution": {"by_horizon": [row]}, **ev}, "component_decisions": {}}
row = lambda **k: {"horizon": "+30m", **k}
def st(r, key="commander"):
    return B(rev(r))["components"][key]["state"]
base = dict(commander_comparison_count=30, commander_day_count=5, average_commander_delta_pct=0.30, commander_positive_delta_rate=0.55)
check(st(row(**base)) == "VALUE_ADD", "boundary +0.30/0.55 inclusive VALUE_ADD")
check(st(row(**{**base, "average_commander_delta_pct": 0.2999})) == "NEUTRAL", "just below")
check(st(row(**{**base, "average_commander_delta_pct": -0.30, "commander_positive_delta_rate": 0.45})) == "DEGRADING", "boundary degrade")
check(st(row(**{**base, "average_commander_delta_pct": -0.30, "commander_positive_delta_rate": 0.46})) == "NEUTRAL", "neg delta rate .46")
n = mod.DIRECTIONAL_MIN_OBSERVATIONS; d = mod.DIRECTIONAL_MIN_DAYS
check(st(row(**{**base, "commander_comparison_count": n - 1})) == "NOT_MEASURABLE", "n-1")
check(st(row(**{**base, "commander_day_count": d - 1})) == "NOT_MEASURABLE", "d-1")
nm = B(rev(row(**{**base, "commander_comparison_count": 0})))["components"]["commander"]
check(nm["missing_control"] and "Commander" in nm["missing_control"], "missing control present")
check(B(rev(row(**base)))["components"]["commander"]["missing_control"] is None, "missing_control None when measurable")
check(st(row(**{**base, "average_commander_delta_pct": "abc"})) == "NOT_MEASURABLE", "non-numeric delta")
_, e = attempt(B, rev(row(commander_comparison_count="abc"))); check(e == "ValueError", "str count raises " + str(e))
_, e = attempt(B, rev(row(commander_comparison_count=[1]))); check(e == "TypeError", "list count raises " + str(e))
check(st(row(**{**base, "average_commander_delta_pct": float("nan")})) == "NEUTRAL", "nan delta -> NEUTRAL (no comparison true)")
# 3 overlay legacy fallback + +30m selection
leg = row(strategist_comparison_count=30, strategist_day_count=5, average_strategist_delta_pct=0.5, strategist_positive_delta_rate=0.6)
check(B(rev(leg))["components"]["strategist"]["ranking_overlay"]["state"] == "VALUE_ADD", "legacy strategist keys fallback")
new = row(strategy_ranking_overlay_comparison_count=0, strategist_comparison_count=30, strategist_day_count=5, average_strategist_delta_pct=0.5, strategist_positive_delta_rate=0.6)
check(B(rev(new))["components"]["strategist"]["ranking_overlay"]["state"] == "NOT_MEASURABLE", "explicit 0 new key not overridden by legacy (key present)")
other = {"evidence": {"decision_window_attribution": {"by_horizon": [{"horizon": "+10m", **base}, "x", None]}}}
check(B(other)["components"]["commander"]["state"] == "NOT_MEASURABLE", "non +30m ignored")
# 4 decisions mapping
for dec, want in (("INSUFFICIENT_EVIDENCE", "NOT_MEASURABLE"), ("REJECT", "DEGRADING"), ("DEPRECATE_CANDIDATE", "DEGRADING"), ("ADJUST_AND_RETEST", "DEGRADING"), ("PROMOTION_CANDIDATE", "VALUE_ADD"), ("KEEP", "NEUTRAL"), (None, "NEUTRAL")):
    r = B({"component_decisions": {"monitor_entry": {"decision": dec, "finding": "f"}, "scanner": {"decision": dec, "relative_ranking_effect_positive": 1}}})
    check(r["components"]["monitor_entry"]["state"] == want, ("map", dec))
    check(r["components"]["scanner"]["relative_ranking_state"] == ("NOT_MEASURABLE" if dec == "INSUFFICIENT_EVIDENCE" else "VALUE_ADD"), ("scanner", dec))
check(B({"component_decisions": {"scanner": {"decision": "KEEP", "relative_ranking_effect_positive": "no"}}})["components"]["scanner"]["relative_ranking_state"] == "VALUE_ADD", "string 'no' truthy -> VALUE_ADD (observation)")
check(B({"component_decisions": {"monitor_exit": {"decision": "REJECT"}}})["components"]["monitor_exit_horizon"]["source_decision"] == "REJECT", "exit key mapping")
# 5 integrity
check(B({"evidence": {"total_trade_model_count": 5, "excluded_trade_model_count": 2}})["integrity"] == {"state": "PASS_WITH_EXCLUSIONS", "trade_model_count": 5, "excluded_trade_model_count": 2}, "integrity")
_, e = attempt(B, {"evidence": {"total_trade_model_count": "x"}}); check(e == "ValueError", "bad total " + str(e))
# 6 render
R = mod.render_agent_effectiveness_scorecard
txt = R(B({})); check(txt.endswith("\n") and "Evidence Shortfalls" in txt and "Commander:" in txt and "None ~ None" in txt, "render empty")
check("Strategist full:" in txt and "Strategist scenario:" in txt, "shortfalls")
txt2 = R(B(rev(row(**base)))); check("- Commander:" not in txt2, "measurable commander omitted from shortfalls")
check(R({}) and R({"components": "x", "range": 3}).startswith("# Agent Effectiveness"), "render tolerant")
# 7 writer with fake review
reports = tmp / "reports"; out = tmp / "out" / "nested"
calls = []
real = mod.build_full_chain_component_review
def fake(**k): calls.append(k); return rev(row(**base), total_trade_model_count=3) | {"range": {"start": k["start"], "end": k["end"]}}
mod.build_full_chain_component_review = fake
snap = lambda: {str(p.relative_to(tmp).as_posix()): (p.read_bytes() if p.is_file() else None) for p in tmp.rglob("*")}
r = mod.write_agent_effectiveness_scorecard(reports_root=str(reports), start="2026-10-01", end="2026-10-05", output_dir=str(out))
check(calls == [{"reports_root": reports, "start": "2026-10-01", "end": "2026-10-05"}], ("call kwargs", calls))
check(set(r) == {"json_path", "markdown_path", "range"} and r["range"] == {"start": "2026-10-01", "end": "2026-10-05"}, "writer result")
js = json.loads(Path(r["json_path"]).read_text(encoding="utf-8")); check(js["components"]["commander"]["state"] == "VALUE_ADD" and js["integrity"]["trade_model_count"] == 3, "json content")
check(Path(r["markdown_path"]).read_text(encoding="utf-8").startswith("# Agent Effectiveness Scorecard (2026-10-01 ~ 2026-10-05)"), "md header")
check(not reports.exists(), "reports root not created by writer (fake)")
s1 = snap(); mod.write_agent_effectiveness_scorecard(reports_root=reports, start="2026-10-01", end="2026-10-05", output_dir=out); check(snap() == s1, "idempotent")
# 8 failure/State
out2 = tmp / "out2"
def boom(**k): raise RuntimeError("review")
mod.build_full_chain_component_review = boom
_, e = attempt(mod.write_agent_effectiveness_scorecard, reports_root=reports, start="a", end="b", output_dir=out2); check(e == "RuntimeError" and not out2.exists(), "review failure: no dir")
mod.build_full_chain_component_review = fake
out3 = tmp / "out3"; (out3 / "agent_effectiveness_scorecard.md").mkdir(parents=True)
_, e = attempt(mod.write_agent_effectiveness_scorecard, reports_root=reports, start="a", end="b", output_dir=out3)
check(e in ("PermissionError", "IsADirectoryError") and (out3 / "agent_effectiveness_scorecard.json").is_file(), "partial md fail json left " + str(e))
out4 = tmp / "out4"; (out4 / "agent_effectiveness_scorecard.json").mkdir(parents=True)
_, e = attempt(mod.write_agent_effectiveness_scorecard, reports_root=reports, start="a", end="b", output_dir=out4); check(e in ("PermissionError", "IsADirectoryError") and not (out4 / "agent_effectiveness_scorecard.md").exists(), "json fail: no md")
(tmp / "afile").write_text("x"); _, e = attempt(mod.write_agent_effectiveness_scorecard, reports_root=reports, start="a", end="b", output_dir=tmp / "afile"); check(e == "FileExistsError", "dir is file " + str(e))
_, e = attempt(mod.write_agent_effectiveness_scorecard, reports_root=reports, start="a", end="b", output_dir=Path(repo) / "zz_outside"); check(e == "OSError" and not (Path(repo) / "zz_outside").exists(), "outside blocked " + str(e))
# 9 real collaborator on empty tmp root
mod.build_full_chain_component_review = real
out5 = tmp / "out5"; (tmp / "empty_reports").mkdir()
rr, e = attempt(mod.write_agent_effectiveness_scorecard, reports_root=tmp / "empty_reports", start="2026-10-01", end="2026-10-05", output_dir=out5)
real_res = e or "ok"
if rr: check(json.loads(Path(rr["json_path"]).read_text(encoding="utf-8"))["behavior_change_authorized"] is False, "real json")
check(not [b for b in bad if not b.startswith(("write:", "wt:", "mkdir:"))], "network/subprocess attempts: " + str(bad))
check(all("zz_outside" in b for b in bad), "unexpected outside writes " + str(bad))
print("RF032_AGENT_EFFECTIVENESS_SCORECARD_OK thresholds=inclusive(0.30/0.55,0.45) legacy_fallback=key_presence decisions=mapped integrity=ok render=tolerant writer=json_then_md partial=json_left_on_md_fail review_fail=no_dir idempotent=yes real_empty_root=" + real_res + " outside_write=OSError net_attempts=0")
