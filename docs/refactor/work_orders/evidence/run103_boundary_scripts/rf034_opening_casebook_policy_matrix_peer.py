# RF-034 short_alpha_discriminator/opening_casebook.py + opening_policy_matrix.py (pure report producers; first coverage),
# fed through the real cohorts.join_opening_to_feature_mart. No writes/network: guards installed, inputs deep-compared before/after.
import os, sys, json, copy, socket, builtins, importlib
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo); sys.dont_write_bytecode = True
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
cb = importlib.import_module(pk + "opening_casebook"); pm = importlib.import_module(pk + "opening_policy_matrix")
co = importlib.import_module(pk + "cohorts"); ct = importlib.import_module(pk + "contracts")
H = ct.HORIZONS
def ep(did, day, sym, epoch, fixed=None, mfe=None, asset="common_stock", recurrent=False, extra=None):
    cps = {}
    for h, v in (fixed or {}).items(): cps.setdefault(h, {})["live_net_return_pct"] = v
    for h, v in (mfe or {}).items(): cps.setdefault(h, {})["mfe_pct"] = v
    e = {"decision_id": did, "day": day, "symbol": sym, "decision_epoch": epoch, "checkpoints": cps,
         "opening_observability": {"asset_observation": {"asset_class": asset, "symbol_name": "N_" + sym},
                                   "conditional_lanes": {"CONFIRMED_RECURRENT_RANK": {"eligible": recurrent}},
                                   "decision_from_open_sec": 30, "opening_relative_volume": 2.0}}
    e["decision_from_open_sec"] = 30
    e.update(extra or {})
    return e
def feat(did, risk="LOW", setup="OTHER", horizon="INTRADAY", tactic="T1", score=1.0):
    return {"identity": {"decision_id": did}, "scanner": {"risk_band": risk, "candidate_setup": setup, "score_total": score, "sources": ["b", "a"]},
            "strategy": {"entry_horizon": horizon, "tactic_id": tactic}, "market": {"kospi_pct": 0.5}}
opening = [
    ep("A1", "D1", "A", 100, {"+5m": 1.5, "+15m": 0.2, "+30m": -0.1}, {"+5m": 2.0, "+15m": 1.0}),
    ep("A2", "D1", "A", 200, {"+5m": 9.0}),                                               # duplicate day-symbol, later -> dropped
    ep("B1", "D1", "B", 150, {"+5m": 0.5, "+15m": -1.0}, {"+5m": 0.4}, recurrent=True),
    ep("C1", "D2", "C", 300, {"+5m": -0.5, "+15m": -0.2, "+30m": -1.0}, {"+15m": 1.5}),
    ep("D1", "D2", "D", 310, None, {"+5m": 1.0}),
    ep("E1", "D3", "E", 400, {"+30m": 1.0}, asset="etf_leveraged"),                      # boundary: >= 1.0
    ep("F1", "D3", "F", 410, {"+5m": 0.0, "+15m": 0.0}, {"+30m": 1.28}),                  # best_fixed 0.0 (not >0), mfe net == 1.0
    ep("G1", "D3", "G", 420, {"+5m": 5.0}),                                               # no feature mate
]
features = [feat("A1", "HIGH", "DIRECTIONAL_BREADTH", "INTRADAY", "T1", 2.5), feat("A2", "HIGH", "DIRECTIONAL_BREADTH"), feat("B1", "MID", "PULLBACK", "SWING"),
            feat("C1"), feat("D1"), feat("E1", "HIGH", "DIRECTIONAL_BREADTH"), feat("F1", "LOW", "PULLBACK"), {"identity": {}}]
o0, f0 = copy.deepcopy(opening), copy.deepcopy(features)
joined, jmeta = co.join_opening_to_feature_mart(opening, features)
check(jmeta["joined_episode_count"] == 7 and jmeta["missing_join_count"] == 1 and jmeta["missing_decision_ids"] == ["G1"], "join: %r" % jmeta)
lanes = {r["decision_id"]: r["opening_alpha_lane_condition"] for r in joined}
check(lanes["A1"] == "HIGH_COMMON_DIRECTIONAL" and lanes["B1"] == "CONFIRMED_RECURRENT_RANK" and lanes["E1"] == "NOT_ELIGIBLE", "lane conditions (etf HIGH DIRECTIONAL is not common_stock): %r" % lanes)
j0 = copy.deepcopy(joined)
# ---- classify_opening_case
cl = {k: cb.classify_opening_case(e) for k, e in {r["decision_id"]: r["episode"] for r in joined}.items()}
check(cl["A1"]["label"] == "FIXED_HORIZON_SUCCESS" and cl["A1"]["best_fixed_horizon"] == "+5m" and cl["A1"]["best_fixed_net_return_pct"] == 1.5 and cl["A1"]["best_mfe_gross_pct"] == 2.0 and cl["A1"]["best_mfe_net_proxy_pct"] == 1.72, "A1 success: %r" % cl["A1"])
check(cl["B1"]["label"] == "POSITIVE_SUBTHRESHOLD" and cl["B1"]["best_fixed_horizon"] == "+5m", "B1 subthreshold")
check(cl["C1"]["label"] == "MFE_NEAR_SUCCESS_PROFIT_FADE" and cl["C1"]["best_fixed_net_return_pct"] == -0.2 and cl["C1"]["best_mfe_net_proxy_pct"] == 1.22, "C1 fade: %r" % cl["C1"])
check(cl["D1"]["label"] == "NON_QUALIFYING" and cl["D1"]["best_fixed_horizon"] == "" and cl["D1"]["best_fixed_net_return_pct"] is None and cl["D1"]["best_mfe_net_proxy_pct"] == 0.72, "D1 non-qualifying (no fixed, mfe 0.72)")
check(cl["E1"]["label"] == "FIXED_HORIZON_SUCCESS" and cl["E1"]["best_fixed_net_return_pct"] == 1.0 and cl["E1"]["best_mfe_gross_pct"] is None, "E1 boundary >=1.0")
check(cl["F1"]["label"] == "MFE_NEAR_SUCCESS_PROFIT_FADE" and cl["F1"]["best_fixed_net_return_pct"] == 0.0 and cl["F1"]["best_mfe_net_proxy_pct"] == 1.0, "F1 best_fixed 0.0 not positive; mfe net == 1.0 inclusive: %r" % cl["F1"])
check(cb.classify_opening_case({}) == {"label": "NON_QUALIFYING", "best_fixed_horizon": "", "best_fixed_net_return_pct": None, "best_mfe_gross_pct": None, "best_mfe_net_proxy_pct": None, "fixed_returns": {"+5m": None, "+15m": None, "+30m": None}}, "empty episode")
# ---- casebook
cs = cb.build_opening_overshoot_casebook(joined)
check(joined == j0, "joined immutable (casebook)")
check(cs["schema_version"] == "opening_overshoot_casebook.v1" and cs["behavior_effect"] == "NONE_OBSERVATION_ONLY" and cs["dedup_policy"] == "FIRST_EPISODE_PER_DAY_SYMBOL", "casebook header")
check(cs["source_episode_count"] == 7 and cs["independent_case_count"] == 6 and cs["qualifying_case_count"] == 5 and cs["non_qualifying_count"] == 1, "counts: %r" % {k: cs[k] for k in ("source_episode_count", "independent_case_count", "qualifying_case_count")})
check(cs["label_counts"] == {"FIXED_HORIZON_SUCCESS": 2, "POSITIVE_SUBTHRESHOLD": 1, "MFE_NEAR_SUCCESS_PROFIT_FADE": 2, "NON_QUALIFYING": 1}, "label counts (A2 duplicate excluded): %r" % cs["label_counts"])
check([r["symbol"] for r in cs["cases"]][:2] in (["A", "E"],) and cs["cases"][0]["outcome"]["best_fixed_net_return_pct"] == 1.5, "cases sorted by best fixed net desc")
# OBSERVATION (not changed): sort key is `number(best_fixed) or -999.0`, so a legit best_fixed of exactly 0.0 (F) is falsy -> -999.0 and sorts BELOW the negative C (-0.2).
check([r["symbol"] for r in cs["cases"]] == ["A", "E", "B", "C", "F"], "sorted order (0.0 demoted by `or -999.0`): %r" % [r["symbol"] for r in cs["cases"]])
fs = {r["label"]: r for r in cs["feature_summary"]}
check(list(fs) == ["FIXED_HORIZON_SUCCESS", "POSITIVE_SUBTHRESHOLD", "MFE_NEAR_SUCCESS_PROFIT_FADE", "NON_QUALIFYING"] and fs["FIXED_HORIZON_SUCCESS"]["case_count"] == 2 and fs["FIXED_HORIZON_SUCCESS"]["avg_best_fixed_net_return_pct"] == 1.25, "feature summary avg 1.5/1.0 -> 1.25")
check(fs["FIXED_HORIZON_SUCCESS"]["avg_scanner_score"] == 1.75 and fs["NON_QUALIFYING"]["avg_best_fixed_net_return_pct"] is None, "avg scanner (2.5,1.0)=1.75; empty avg None")
c0 = cs["cases"][0]
check(c0["scanner"]["sources"] == ["a", "b"] and c0["strategy"]["tactic_id"] == "T1" and c0["symbol_name"] == "N_A" and c0["market"]["kospi_pct"] == 0.5, "case row mapping")
check(cb.build_opening_overshoot_casebook([])["independent_case_count"] == 0 and cb.build_opening_overshoot_casebook([])["feature_summary"][0]["case_count"] == 0, "empty casebook")
cmd = cb.render_opening_overshoot_casebook(cs)
check(cmd.startswith("# Opening Overshoot") and "`FIXED_HORIZON_SUCCESS`" in cmd and "+1.5000%" in cmd and cmd.endswith("\n") and cmd == cb.render_opening_overshoot_casebook(copy.deepcopy(cs)), "casebook markdown")
check(cb.render_opening_overshoot_casebook({}).startswith("# Opening Overshoot") , "render empty payload")
# ---- policy matrix
pmx = pm.build_opening_policy_matrix(joined)
check(joined == j0, "joined immutable (matrix)")
check(pmx["schema_version"] == "opening_policy_matrix.v1" and pmx["behavior_change_authorized"] is False and pmx["behavior_effect"] == "NONE_OBSERVATION_ONLY", "matrix header")
check(pmx["source_episode_count"] == 7 and pmx["independent_day_symbol_count"] == 6, "matrix counts")
af = {r["asset_family"]: r for r in pmx["asset_class"]}
check(sorted(af) == ["COMMON_STOCK", "ETF"] and af["ETF"]["day_symbol_count"] == 1 and af["COMMON_STOCK"]["day_symbol_count"] == 5, "asset families (etf_leveraged -> ETF)")
lc = {r["lane_condition"]: r for r in pmx["lane_condition"]}
check(sorted(lc) == ["CONFIRMED_RECURRENT_RANK", "HIGH_COMMON_DIRECTIONAL", "NOT_ELIGIBLE"], "lanes")
h = af["COMMON_STOCK"]["horizons"]
check(list(h) == list(H) and h["+5m"]["sample_count"] == 4 and h["+5m"]["avg_net_return_pct"] == round((1.5 + 0.5 - 0.5 + 0.0) / 4, 4), "common +5m perf over independent rows (A1,B1,C1,F1)=%r" % h["+5m"])
check(h["EOD"]["sample_count"] == 0 and h["EOD"]["win_rate"] is None and h["EOD"]["profit_factor"] == 0.0, "EOD none observed")
check(len(pmx["combined"]) == 5 and pmx["combined"] == sorted(pmx["combined"], key=lambda r: (r["lane_condition"], r["asset_family"], r["risk_band"], r["candidate_setup"], r["entry_horizon"])), "combined 5 cells (C,D share one), sorted")
check(sum(r["day_symbol_count"] for r in pmx["combined"]) == 6, "cells partition independent rows")
pmd = pm.render_opening_policy_matrix(pmx)
check(pmd.startswith("# Opening Alpha Policy Matrix") and pmd.count("\n| ") == 6 and "N=1, WR=100.0%, avg=+1.5000%, PF=999.0000" in pmd and pmd.endswith("\n"), "matrix markdown (PF 999 sentinel)")
check(pm.render_opening_policy_matrix({}).count("|") > 0, "render empty payload")
# empty matrix
em = pm.build_opening_policy_matrix([])
check(em["independent_day_symbol_count"] == 0 and em["combined"] == [] and em["asset_class"] == [], "empty matrix")
# ---- exception contract
exc = {"casebook_none": exc_of(cb.build_opening_overshoot_casebook, None), "matrix_none": exc_of(pm.build_opening_policy_matrix, None),
       "casebook_str_rows": exc_of(cb.build_opening_overshoot_casebook, ["x"]), "classify_none": exc_of(cb.classify_opening_case, None),
       "classify_bad_checkpoint": exc_of(cb.classify_opening_case, {"checkpoints": {"+5m": "x"}}), "render_casebook_none": exc_of(cb.render_opening_overshoot_casebook, None)}
check(opening == o0 and features == f0 and joined == j0, "inputs immutable")
check(not bad, "blocked effects attempted: %r" % bad)
print("RF034_OPENING_CASEBOOK_POLICY_MATRIX_OK labels=%s independent=%d qualifying=%d lanes=3 combined_cells=%d boundary=gte1.0/mfe_net_inclusive/best0_not_positive sort_zero_demoted=yes state_mutation=none write_attempts=0 exc=%s debug=%s" % (json.dumps(cs["label_counts"], sort_keys=True), cs["independent_case_count"], cs["qualifying_case_count"], len(pmx["combined"]), json.dumps(exc, sort_keys=True), __debug__))
