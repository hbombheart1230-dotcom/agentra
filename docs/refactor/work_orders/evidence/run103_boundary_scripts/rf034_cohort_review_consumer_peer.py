# RF-034: short_alpha_discriminator/cohorts.py remaining pure producers -- join_opening_to_feature_mart -> build_cohort_review (6 predicates, historical/prospective split,
# leave-one-out, without_best) -> group_feature_metrics, then consumed by report.render_short_alpha_discriminator (cohort table / sensitivity / prospective sections).
# Pure in-memory synthetic episodes; no file/network/subprocess/sqlite is touched (all blocked and counted).
import os, sys, copy, builtins, socket, subprocess, sqlite3, importlib, json
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
co = importlib.import_module("libs.reporting.short_alpha_discriminator.cohorts")
rp = importlib.import_module("libs.reporting.short_alpha_discriminator.report")
ct = importlib.import_module("libs.reporting.short_alpha_discriminator.contracts")
bad = []
def blocked(n):
    def f(*a, **k): bad.append(n); raise OSError("blocked " + n)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("cc"); socket.getaddrinfo = blocked("gai")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
os.system = blocked("os.system"); sqlite3.connect = blocked("sqlite")
_open = builtins.open
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+"): bad.append("write:" + str(f)); raise OSError("blocked write")
    return _open(f, mode, *a, **k)
builtins.open = gopen; Path.write_text = blocked("write_text"); Path.mkdir = blocked("mkdir")
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED@%d: %s" % (sys._getframe(1).f_lineno, m))
def attempt(fn, *a, **k):
    try: return fn(*a, **k), None
    except Exception as e: return None, type(e).__name__
check(ct.PROSPECTIVE_START_DAY == "2026-08-25" and ct.PRIMARY_COHORT_ID == "HIGH_COMMON_SHORT_ALPHA_V1" and ct.HORIZONS == ("+5m", "+15m", "+30m", "+60m", "EOD"), "contract constants")
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
O = [
    ep("e2", "2026-08-20", "A", 200, "common_stock", sec=30, ret5=9.0, ret30=9.0),       # later duplicate of (day,A): listed FIRST to prove epoch ordering
    ep("e1", "2026-08-20", "A", 100, "common_stock", sec=30, ret5=1.0, ret30=2.0),
    ep("e3", "2026-08-20", "B", 150, "common_stock", sec=120, ret5=-2.0, ret30=0.5, recurrent=True),
    ep("e4", "2026-08-21", "C", 300, "etf", sec=10, ret5=3.0),
    ep("e5", "2026-08-21", "D", 310, "common_stock", ret5=0.5, ret30=1.5),                # no decision_from_open_sec -> 999999
    ep("e6", "2026-08-25", "A", 400, "common_stock", sec=60, ret5=4.0, ret30=1.0),         # first prospective day (>=) ; sec==60 is immediate
    ep("e7", "2026-08-26", "E", 410, "common_stock", sec=61, ret5="bad", ret30=-1.0),
    ep("e8", "2026-08-26", "F", 420, "common_stock", ret5=1.0),                            # no feature -> missing
    ep("", "2026-08-26", "G", 430, "common_stock", ret5=1.0),                              # empty decision_id -> missing
    ep("e10", "2026-08-26", "", 440, "common_stock", ret5=1.0),                            # empty symbol: joins but never independent
]
F = [
    ft("e1", "HIGH", "DIRECTIONAL_BREADTH", ["top_volume", "top_value"], 70.5),
    ft("e2", "HIGH", "DIRECTIONAL_BREADTH", ["top_value", "top_volume"], 71),
    ft("e3", "HIGH", "OTHER", ["top_value"], "80"),
    ft("e4", "HIGH", "DIRECTIONAL_BREADTH", ["top_value", "top_volume"]),
    ft("e5", "MID", "OTHER", []),
    ft("e6", "HIGH", "OTHER", ["top_value", "top_volume", "x"]),
    ft("e7", "HIGH", "DIRECTIONAL_BREADTH", ["top_value", "top_volume"], "n/a"),
    ft("e10", "HIGH", "OTHER", []),
    {"identity": {}, "scanner": {}},                                                        # no decision_id -> not indexable
]
O0, F0 = copy.deepcopy(O), copy.deepcopy(F)
joined, jm = co.join_opening_to_feature_mart(O, F)
check(O == O0 and F == F0, "inputs mutated by join")
check(jm == {"opening_episode_count": 10, "feature_episode_count": 9, "joined_episode_count": 8, "missing_join_count": 2, "missing_decision_ids": ["e8", ""]}, jm)
by = {r["decision_id"]: r for r in joined}
check(by["e1"]["opening_alpha_lane_condition"] == "HIGH_COMMON_DIRECTIONAL" and by["e3"]["opening_alpha_lane_condition"] == "CONFIRMED_RECURRENT_RANK" and by["e4"]["opening_alpha_lane_condition"] == "NOT_ELIGIBLE", "lane condition")
check(by["e1"]["sources"] == ["top_value", "top_volume"] and by["e1"]["score_total"] == 70.5 and by["e3"]["score_total"] == 80.0 and by["e7"]["score_total"] is None, "sources/score")
check(by["e5"]["entry_horizon"] == "E1" and by["e5"]["tactic_id"] == "T1", "strategy fields")
# --- independent_day_symbol_rows: earliest decision_epoch per (day, symbol), empty keys dropped
ind = co.independent_day_symbol_rows(joined)
check(sorted((r["day"], r["symbol"], r["decision_id"]) for r in ind) == [("2026-08-20", "A", "e1"), ("2026-08-20", "B", "e3"), ("2026-08-21", "C", "e4"), ("2026-08-21", "D", "e5"), ("2026-08-25", "A", "e6"), ("2026-08-26", "E", "e7")], [(r["day"], r["symbol"], r["decision_id"]) for r in ind])
# --- build_cohort_review
J0 = copy.deepcopy(joined)
rv = co.build_cohort_review(joined); check(joined == J0, "joined mutated")
check(rv == co.build_cohort_review(copy.deepcopy(joined)), "nondeterministic")
cs = {c["cohort_id"]: c for c in rv["cohorts"]}
check([c["cohort_id"] for c in rv["cohorts"]] == ["HIGH_COMMON_SHORT_ALPHA_V1", "HIGH_NON_COMMON_CONTROL", "NON_HIGH_COMMON_CONTROL", "HIGH_COMMON_DIRECTIONAL", "IMMEDIATE_COMMON", "TOP_VALUE_VOLUME_NEGATIVE_CONTROL_V1"], list(cs))
P = cs["HIGH_COMMON_SHORT_ALPHA_V1"]
check(P["episode_count"] == 6 and P["independent_day_symbol_count"] == 4 and P["day_count"] == 3 and P["conditions"] == ["asset_class=common_stock", "risk_band=HIGH"], P)   # e1,e2,e3,e6,e7,e10; empty-symbol e10 never independent
check(P["largest_day_share"] == 0.5 and P["largest_symbol_share"] == 0.5, (P["largest_day_share"], P["largest_symbol_share"]))
h5 = P["horizons"]["+5m"]; check(h5["sample_count"] == 3 and h5["avg_net_return_pct"] == 1.0 and h5["win_count"] == 2 and h5["loss_count"] == 1, h5)   # e1 1.0, e3 -2.0, e6 4.0 ; e7 'bad'->None dropped ; e2 (9.0) deduped away
check(P["horizons"]["+15m"]["sample_count"] == 0 and P["horizons"]["+15m"]["win_rate"] is None and P["horizons"]["+30m"]["sample_count"] == 4, P["horizons"]["+30m"])
check((cs["HIGH_NON_COMMON_CONTROL"]["episode_count"], cs["HIGH_NON_COMMON_CONTROL"]["independent_day_symbol_count"]) == (1, 1) and (cs["NON_HIGH_COMMON_CONTROL"]["episode_count"], cs["NON_HIGH_COMMON_CONTROL"]["independent_day_symbol_count"]) == (1, 1), "controls")
check((cs["HIGH_COMMON_DIRECTIONAL"]["episode_count"], cs["HIGH_COMMON_DIRECTIONAL"]["independent_day_symbol_count"]) == (3, 2), cs["HIGH_COMMON_DIRECTIONAL"])
check((cs["IMMEDIATE_COMMON"]["episode_count"], cs["IMMEDIATE_COMMON"]["independent_day_symbol_count"]) == (3, 2), cs["IMMEDIATE_COMMON"])   # sec<=60 (e1,e2,e6); missing sec -> 999999 not immediate
check((cs["TOP_VALUE_VOLUME_NEGATIVE_CONTROL_V1"]["episode_count"], cs["TOP_VALUE_VOLUME_NEGATIVE_CONTROL_V1"]["independent_day_symbol_count"]) == (4, 3), cs["TOP_VALUE_VOLUME_NEGATIVE_CONTROL_V1"])
c = rv["prospective_contract"]; check(c == {"candidate_id": "HIGH_COMMON_SHORT_ALPHA_V1", "first_eligible_day": "2026-08-25", "selection_rule_frozen": True, "conditions": ["asset_class=common_stock", "risk_band=HIGH"], "behavior_effect": "NONE_OBSERVATION_ONLY"}, c)
hr, pr = rv["historical_reference"], rv["prospective"]
check((hr["episode_count"], hr["independent_day_symbol_count"], pr["episode_count"], pr["independent_day_symbol_count"]) == (3, 2, 3, 2), (hr["episode_count"], pr["episode_count"]))   # 08-25 is prospective (>=)
hs = rv["historical_sensitivity"]
sym = {r["excluded_symbol"]: r for r in hs["by_symbol_leave_one_out"]}
check(sorted(sym) == ["A", "B"] and sym["A"]["+5m"]["avg_net_return_pct"] == -2.0 and sym["B"]["+5m"]["avg_net_return_pct"] == 1.0 and sym["A"]["+30m"]["avg_net_return_pct"] == 0.5, sym)
dy = hs["by_day_leave_one_out"]; check(len(dy) == 1 and dy[0]["excluded_day"] == "2026-08-20" and dy[0]["+5m"]["sample_count"] == 0 and dy[0]["+5m"]["profit_factor"] == 0.0, dy)
wb = hs["without_best_observation"]; check(wb["excluded_day"] == "2026-08-20" and wb["excluded_symbol"] == "A" and wb["+5m"]["avg_net_return_pct"] == -2.0 and wb["+30m"]["sample_count"] == 1, wb)
out = {"cohorts": {k: (v["episode_count"], v["independent_day_symbol_count"]) for k, v in cs.items()}}
# --- empty / degenerate inputs
rv0 = co.build_cohort_review([]); check(rv0["historical_sensitivity"]["by_symbol_leave_one_out"] == [] and rv0["historical_sensitivity"]["without_best_observation"]["excluded_day"] is None and rv0["historical_sensitivity"]["without_best_observation"]["excluded_symbol"] is None, "empty")
check(all(c["episode_count"] == 0 and c["largest_day_share"] is None and c["largest_symbol_share"] is None for c in rv0["cohorts"]), "empty cohorts share None")
check(co.join_opening_to_feature_mart([], []) == ([], {"opening_episode_count": 0, "feature_episode_count": 0, "joined_episode_count": 0, "missing_join_count": 0, "missing_decision_ids": []}), "empty join")
# --- observations (unchanged behavior): sec==0 is not 'immediate' (0 or 999999); a 0.0 best return is ranked below negatives
q = co.build_cohort_review([{"episode": {"opening_observability": {"decision_from_open_sec": 0}}, "day": "2026-08-01", "symbol": "Z", "asset_class": "common_stock", "risk_band": "LOW"}])
imm = [c for c in q["cohorts"] if c["cohort_id"] == "IMMEDIATE_COMMON"][0]; out["sec0_immediate_episodes"] = imm["episode_count"]; check(imm["episode_count"] == 0, "sec=0 treated as missing (observation)")
Z = lambda d, s, v: {"episode": {"decision_epoch": 1, "checkpoints": {"+5m": {"live_net_return_pct": v}}}, "day": d, "symbol": s, "asset_class": "common_stock", "risk_band": "HIGH"}
zq = co.build_cohort_review([Z("2026-08-01", "X", 0.0), Z("2026-08-02", "Y", -2.0)])["historical_sensitivity"]["without_best_observation"]
out["zero_best"] = (zq["excluded_symbol"], zq["+5m"]["avg_net_return_pct"]); check(zq["excluded_symbol"] == "Y", "0.0 best-return is ranked as -999 so the -2.0 row is removed (observation)")
# --- group_feature_metrics
g = co.group_feature_metrics(joined, "risk_band", "+5m"); gd = {r["risk_band"]: r for r in g}
check([r["risk_band"] for r in g] == ["HIGH", "MID"] and gd["HIGH"]["sample_count"] == 6 and gd["HIGH"]["avg_net_return_pct"] == 2.6667 and gd["MID"]["avg_net_return_pct"] == 0.5, g)   # episodes, not independent rows (e2's 9.0 counted)
gm = co.group_feature_metrics(joined, "nonexistent_field", "+30m"); check(len(gm) == 1 and gm[0]["nonexistent_field"] == "MISSING" and gm[0]["sample_count"] == 6, gm)
check(co.group_feature_metrics([], "risk_band", "+5m") == [] and co.group_feature_metrics(joined, "symbol", "+99m")[0]["sample_count"] == 0, "empty/unknown horizon")
# --- consumed by the report renderer (cohort table, sensitivity, prospective sections)
payload = {"through_day": "2026-08-26", "behavior_effect": "NONE_OBSERVATION_ONLY", "integrity": {"status": "OK"}, "cohort_review": rv}
md = rp.render_short_alpha_discriminator(payload); check(md == rp.render_short_alpha_discriminator(copy.deepcopy(payload)) and md.endswith("\n"), "render determinism")
check("| `HIGH_COMMON_SHORT_ALPHA_V1` | 4 | N=3, WR 66.7%, avg +1.0000%, PF 2.5000 |" in md, [l for l in md.splitlines() if "HIGH_COMMON_SHORT" in l])
check("| `HIGH_NON_COMMON_CONTROL` | 1 | N=1, WR 100.0%, avg +3.0000%, PF 999.0000 | - | - | - |" in md and "| `IMMEDIATE_COMMON` | 2 |" in md, "table rows")
check("- Removed best observation: `2026-08-20` / `A`" in md and "- Without best +5m: N=1, WR 0.0%, avg -2.0000%, PF 0.0000" in md and "- Leave-one-symbol cases: **2**" in md and "- Leave-one-day cases: **1**" in md, "sensitivity lines")
check("- Candidate: `HIGH_COMMON_SHORT_ALPHA_V1`" in md and "- Prospective episodes: **3**" in md and "- Conditions: `asset_class=common_stock, risk_band=HIGH`" in md, "prospective lines")
md0 = rp.render_short_alpha_discriminator({"cohort_review": rv0}); check("- Removed best observation: `None` / `None`" in md0 and "- Prospective episodes: **0**" in md0, "empty review render")
# --- exceptions
ex = {
    "open_none": attempt(co.join_opening_to_feature_mart, None, F)[1], "feat_none": attempt(co.join_opening_to_feature_mart, O, None)[1],
    "identity_str": attempt(co.join_opening_to_feature_mart, O, [{"identity": "xx"}])[1], "episode_str": attempt(co.join_opening_to_feature_mart, ["xx"], F)[1],
    "scanner_str": attempt(co.join_opening_to_feature_mart, [ep("s1", "d", "S", 1, "common_stock")], [{"identity": {"decision_id": "s1"}, "scanner": "zz"}])[1],
    "review_none": attempt(co.build_cohort_review, None)[1],
    "epoch_str": attempt(co.independent_day_symbol_rows, [{"episode": {"decision_epoch": "x"}, "day": "d", "symbol": "s"}])[1],
    "checkpoints_list": attempt(co.build_cohort_review, [{"episode": {"checkpoints": []}, "day": "2026-08-01", "symbol": "Q", "asset_class": "common_stock", "risk_band": "HIGH"}])[1],
    "render_none": attempt(rp.render_short_alpha_discriminator, None)[1],
}
out["exc"] = ex
check(ex["open_none"] == "TypeError" and ex["feat_none"] == "TypeError" and ex["identity_str"] == "ValueError" and ex["episode_str"] == "ValueError" and ex["scanner_str"] == "ValueError", ex)
check(ex["review_none"] == "TypeError" and ex["epoch_str"] == "ValueError" and ex["checkpoints_list"] == "AttributeError" and ex["render_none"] == "AttributeError", ex)
check(not bad, bad)
print("RF034_COHORT_REVIEW_CONSUMER_OK", "joined=%d missing=%d" % (jm["joined_episode_count"], jm["missing_join_count"]), "cohorts=6 independent_primary=%d" % P["independent_day_symbol_count"], "hist=2 prosp=2 loo_sym=2 loo_day=1", "render=yes writes=0 net_attempts=0", "debug=" + str(__debug__))
print(json.dumps(out, sort_keys=True))
