# RF-034 short_alpha_discriminator/profit_lock.py::build_profit_fade_review + strategist_roi.py::build_strategist_stage2_review
# (pure report producers; first coverage). No writes/network: guards installed, inputs deep-compared before/after.
import os, sys, json, copy, socket, builtins, importlib, tempfile
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo); sys.dont_write_bytecode = True
tmp = Path(tempfile.mkdtemp(prefix="rf034_pl_")).resolve()
bad = []
def blocked(name):
    def f(*a, **k): bad.append(name); raise OSError("blocked " + name)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("create_connection")
_open = builtins.open
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+"): bad.append("write_open:" + str(f)); raise OSError("blocked write")
    return _open(f, mode, *a, **k)
builtins.open = gopen
for n in ("write_text", "write_bytes", "mkdir"): setattr(Path, n, blocked("Path." + n))
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED: " + m)
def exc_of(f, *a, **k):
    try: f(*a, **k); return "no_raise"
    except Exception as e: return type(e).__name__
pk = "libs.reporting.short_alpha_discriminator."
pl = importlib.import_module(pk + "profit_lock"); sr = importlib.import_module(pk + "strategist_roi"); ct = importlib.import_module(pk + "contracts")
H = ct.HORIZONS
def cp(**kw): return {h: v for h, v in kw.items()}
def ep(rets, mfe=None):
    cps = {h: {"live_net_return_pct": r} for h, r in rets.items()}
    if mfe is not None: cps.setdefault("EOD", {})["mfe_pct"] = mfe
    return {"checkpoints": cps}
rows = [
    {"day": "2026-09-01", "symbol": "A", "candidate_setup": "s1", "entry_horizon": "h", "episode": ep({"+5m": 1.0, "+15m": 2.5, "+30m": 3.0, "EOD": -0.5}, mfe=3.5)},
    {"day": "2026-09-01", "symbol": "B", "episode": ep({"+5m": -1.0, "EOD": 1.0}, mfe=1.5)},
    {"day": "2026-09-02", "symbol": "C", "episode": ep({"+5m": 0.4})},
    {"day": "2026-09-02", "symbol": "D", "episode": ep({"EOD": "2.0"})},
]
orig = copy.deepcopy(rows)
r = pl.build_profit_fade_review(rows)
check(rows == orig, "input immutable")
check(r["cohort_episode_count"] == 4 and r["behavior_change_authorized"] is False and [d["symbol"] for d in r["details"]] == list("ABCD"), "shape/order")
dA, dB, dC, dD = r["details"]
check(dA["best_checkpoint_return_pct"] == 3.0 and dA["checkpoint_to_eod_fade_pct"] == 3.5 and dA["positive_5m_to_negative_eod"] is True and dA["eod_mfe_pct"] == 3.5, "A fade 3.5, +5m>0 & EOD<=0")
check(dB["checkpoint_to_eod_fade_pct"] == 0.0 and dB["positive_5m_to_negative_eod"] is False, "B")
check(dC["checkpoint_to_eod_fade_pct"] is None and dC["positive_5m_to_negative_eod"] is False and dC["returns"]["EOD"] is None, "C no EOD -> fade None")
check(dD["returns"]["EOD"] == 2.0 and dD["eod_mfe_pct"] is None and dD["candidate_setup"] is None, "D numeric-string EOD coerced; missing fields -> None")
check(r["positive_5m_to_negative_eod_count"] == 1 and r["avg_checkpoint_to_eod_fade_pct"] == round((3.5 + 0.0 + 0.0) / 3, 4), "aggregate fade avg over non-None")
check(set(r["fixed_horizon_comparison"]) == set(H) and r["fixed_horizon_comparison"]["+60m"]["sample_count"] == 0 and r["fixed_horizon_comparison"]["+60m"]["win_rate"] is None, "all 5 horizons; empty -> None")
check(r["fixed_horizon_comparison"]["EOD"]["sample_count"] == 3 and r["fixed_horizon_comparison"]["+5m"]["sample_count"] == 3, "sample counts")
p2, p3 = r["profit_lock_proxies"]
check(p2["policy_id"] == "MFE_2_LOCK_0_5_PROXY" and p2["triggered_count"] == 1 and p2["metrics"]["sample_count"] == 3 and p2["metrics"]["avg_net_return_pct"] == round((0.5 + 1.0 + 2.0) / 3, 4), "proxy 2/0.5: A lifted -0.5->0.5")
check(p3["policy_id"] == "MFE_3_LOCK_1_0_PROXY" and p3["triggered_count"] == 1 and p3["metrics"]["avg_net_return_pct"] == round((1.0 + 1.0 + 2.0) / 3, 4) and "Optimistic" in p3["limitation"], "proxy 3/1.0: A lifted to 1.0")
# trigger boundary: mfe exactly at trigger triggers; just below does not
b = pl.build_profit_fade_review([{"episode": ep({"EOD": -1.0}, mfe=2.0)}, {"episode": ep({"EOD": -1.0}, mfe=1.9999)}])
check(b["profit_lock_proxies"][0]["triggered_count"] == 1 and b["profit_lock_proxies"][0]["metrics"]["avg_net_return_pct"] == round((0.5 - 1.0) / 2, 4), "trigger boundary >=")
# floor never lowers a better EOD (max)
c = pl.build_profit_fade_review([{"episode": ep({"EOD": 4.0}, mfe=5.0)}])
check(c["profit_lock_proxies"][0]["metrics"]["avg_net_return_pct"] == 4.0 and c["profit_lock_proxies"][0]["triggered_count"] == 1, "max(eod, floor)")
e = pl.build_profit_fade_review([])
check(e["cohort_episode_count"] == 0 and e["avg_checkpoint_to_eod_fade_pct"] is None and all(p["triggered_count"] == 0 and p["metrics"]["sample_count"] == 0 for p in e["profit_lock_proxies"]), "empty")
check(json.loads(json.dumps(r)) == r, "JSON-serialisable")
# +5m==0 is not positive; EOD==0 counts as <= 0
z = pl.build_profit_fade_review([{"episode": ep({"+5m": 0.0001, "EOD": 0.0})}, {"episode": ep({"+5m": 0.0, "EOD": -1.0})}])
check(z["positive_5m_to_negative_eod_count"] == 1, "strict +5m>0, EOD<=0")
pl_exc = {"episode_none": exc_of(pl.build_profit_fade_review, [{"episode": None}]), "row_not_mapping": exc_of(pl.build_profit_fade_review, ["x"]), "rows_none": exc_of(pl.build_profit_fade_review, None),
          "checkpoint_none": exc_of(pl.build_profit_fade_review, [{"episode": {"checkpoints": {"EOD": None}}}]), "bad_number_str": exc_of(pl.build_profit_fade_review, [{"episode": ep({"EOD": "abc"})}])}
# ---- strategist_roi
def fe(day, sym, status="OBSERVED", changed=None, default=None, mode=None, net=None):
    cps = {h: {"status": "OBSERVED", "net_return_pct": v} for h, v in (net or {}).items()}
    return {"identity": {"day": day, "symbol": sym}, "strategy": {"canonical_evidence_status": status},
            "strategy_choice_observation": {"playbook_choice": {"changed_from_pre_llm": changed}, "tactic_choice": {"selected_is_playbook_default": default}, "generation": {"mode": mode} if mode else {}},
            "outcomes": {"checkpoints": cps}}
eps = [fe("d1", "A", changed=True, default=False, mode="LLM", net={"+5m": 1.0, "EOD": 2.0}),
       fe("d1", "A", changed=False, default=True, mode="RULE", net={"+5m": 99.0}),          # duplicate (day, symbol) -> first kept
       fe("d1", "B", changed=False, default=True, mode="RULE", net={"+5m": -1.0, "EOD": 0.5}),
       fe("d2", "C", status="MISSING", changed=True, default=True, mode="LLM", net={"+5m": 50.0}),  # not OBSERVED -> skipped
       fe("d2", "D", net={"+5m": 3.0}),                                                          # missing choices
       {"identity": {"day": "d3", "symbol": "E"}, "strategy": {"canonical_evidence_status": "OBSERVED"}, "outcomes": {"checkpoints": {"+5m": {"status": "PENDING", "net_return_pct": 9.0}}}}]
sc = {"range": {"start": "s", "end": "e"}, "components": {"strategist": {"ranking_overlay": {"x": 1}, "post_scanner_refresh": {"y": 2}}}}
eo, so = copy.deepcopy(eps), copy.deepcopy(sc)
s = sr.build_strategist_stage2_review(eps, sc)
check(eps == eo and sc == so, "inputs immutable")
check(s["authority_change_applied"] is False and s["behavior_change_authorized"] is False and s["official_scorecard_range"] == {"start": "s", "end": "e"} and s["official_ranking_overlay"] == {"x": 1} and s["official_post_scanner_refresh"] == {"y": 2}, "official passthrough + flags")
sp = {(x["dimension"], x["value"]): x for x in s["observational_splits"]}
check([(x["dimension"], x["value"]) for x in s["observational_splits"]] == sorted(sp), "splits sorted by (dimension,value)")
check(sp[("changed_from_pre_llm", "True")]["episode_count"] == 1 and sp[("changed_from_pre_llm", "False")]["episode_count"] == 1 and sp[("changed_from_pre_llm", "None")]["episode_count"] == 2, "changed_from_pre_llm: dup first-wins, MISSING-status dropped, absent -> 'None'")
check(sp[("generation_mode", "LLM")]["episode_count"] == 1 and sp[("generation_mode", "RULE")]["episode_count"] == 1 and sp[("generation_mode", "MISSING")]["episode_count"] == 2, "generation_mode default MISSING")
check(sp[("default_tactic", "True")]["episode_count"] == 1 and sp[("default_tactic", "False")]["episode_count"] == 1 and sp[("default_tactic", "None")]["episode_count"] == 2, "default_tactic")
check(sp[("changed_from_pre_llm", "True")]["horizons"]["+5m"]["avg_net_return_pct"] == 1.0 and sp[("changed_from_pre_llm", "True")]["horizons"]["EOD"]["avg_net_return_pct"] == 2.0, "first duplicate's outcomes used (not 99)")
none_grp = sp[("changed_from_pre_llm", "None")]["horizons"]
check(none_grp["+5m"]["sample_count"] == 1 and none_grp["+5m"]["avg_net_return_pct"] == 3.0, "PENDING checkpoint excluded from outcomes")
check(all(set(x["horizons"]) == set(H) for x in s["observational_splits"]) and "confounded" in s["interpretation_boundary"], "all horizons + boundary text")
s0 = sr.build_strategist_stage2_review([], {})
check(s0["observational_splits"] == [] and s0["official_scorecard_range"] == {} and s0["official_ranking_overlay"] == {} and s0["official_post_scanner_refresh"] == {}, "empty/{} scorecard")
check(json.loads(json.dumps(s)) == s, "JSON-serialisable")
sr_exc = {"episodes_none": exc_of(sr.build_strategist_stage2_review, None, {}), "scorecard_none": exc_of(sr.build_strategist_stage2_review, [], None),
          "strategy_none": exc_of(sr.build_strategist_stage2_review, [{"strategy": None}], {}), "components_none": exc_of(sr.build_strategist_stage2_review, [], {"components": None}),
          "strategist_none": exc_of(sr.build_strategist_stage2_review, [], {"components": {"strategist": None}}), "row_not_mapping": exc_of(sr.build_strategist_stage2_review, ["x"], {})}
check(not bad and not tmp.exists() is False, "no blocked effect")
print("RF034_PROFIT_LOCK_STRATEGIST_ROI_OK fade_avg=%.4f proxies=2(trigger=1,1) trigger_boundary=gte floor=max splits=%d dedupe=first_wins pending_excluded=yes state_mutation=none write_attempts=%d exc=%s debug=%s"
      % (r["avg_checkpoint_to_eod_fade_pct"], len(s["observational_splits"]), len(bad), json.dumps({**{"pl_" + k: v for k, v in pl_exc.items()}, **{"sr_" + k: v for k, v in sr_exc.items()}}, sort_keys=True, separators=(",", ":")), __debug__))
