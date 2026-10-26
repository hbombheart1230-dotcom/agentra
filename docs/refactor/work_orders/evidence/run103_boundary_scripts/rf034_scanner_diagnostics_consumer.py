# RF-034: short_alpha_discriminator/scanner_diagnostics.py::build_scanner_diagnostics -> report.render_short_alpha_discriminator consumer. Pure/read-only synthetic joined rows; no file/network effects (writes blocked outside nothing created at all).
import os, sys, json, copy, math, socket, subprocess, sqlite3, builtins, importlib, tempfile
from pathlib import Path
repo = os.getcwd(); sys.path.insert(0, repo)
sd = importlib.import_module("libs.reporting.short_alpha_discriminator.scanner_diagnostics")
rp = importlib.import_module("libs.reporting.short_alpha_discriminator.report")
tmp = Path(tempfile.mkdtemp(prefix="rf034_sd_")).resolve(); os.chdir(tmp)
bad = []
def blocked(n):
    def f(*a, **k): bad.append(n); raise OSError("blocked " + n)
    return f
socket.socket.connect = blocked("connect"); socket.create_connection = blocked("cc"); socket.getaddrinfo = blocked("gai")
for n in ("Popen", "run", "call", "check_call", "check_output"): setattr(subprocess, n, blocked(n))
sqlite3.connect = blocked("sqlite")
_open = builtins.open
def gopen(f, mode="r", *a, **k):
    if isinstance(mode, str) and set(mode) & set("wax+"): bad.append("write:" + str(f)); raise OSError("blocked write")
    return _open(f, mode, *a, **k)
builtins.open = gopen
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED: " + str(m))
def attempt(fn, *a, **k):
    try: return fn(*a, **k), None
    except Exception as e: return None, type(e).__name__
B = sd.build_scanner_diagnostics
def row(day, sym, epoch, score, r5=None, r30=None, reod=None, r15=None, setup="S1", sources=("A",), market=None):
    cps = {}
    for h, v in (("+5m", r5), ("+15m", r15), ("+30m", r30), ("EOD", reod)):
        if v is not None: cps[h] = {"live_net_return_pct": v}
    return {"day": day, "symbol": sym, "score_total": score, "candidate_setup": setup, "sources": list(sources) if sources is not None else None,
            "episode": {"decision_epoch": epoch, "checkpoints": cps}, "feature": {"market": market} if market is not None else {}}
# empty
e = B([]); check(e["sample_count"] == 0 and e["score_quartiles"] == [] and e["by_candidate_setup"] == [] and e["market_snapshot_coverage"] == {"observed_count": 0, "fresh_within_300s_count": 0, "total_count": 0, "coverage": 0.0, "fresh_coverage": 0.0}, "empty")
check(e["score_return_correlation"] == {"+5m": None, "+15m": None, "+30m": None, "EOD": None} and e["behavior_change_authorized"] is False and e["evaluation_unit"] == "first_day_symbol", "empty corr")
# dedupe: first by decision_epoch per (day,symbol); missing day/symbol dropped; None epoch -> 0 sorts first
rows = [row("d1", "X", 200, 9, r30=-5), row("d1", "X", 100, 1, r30=1), row("d1", "Y", 50, 2, r30=2), row("d2", "X", 10, 3, r30=3), row("", "Z", 1, 4, r30=4), row("d1", "", 1, 4, r30=4), row("d3", "W", None, 5, r30=5), ]
d = B(rows); check(d["sample_count"] == 4, "dedupe count " + str(d["sample_count"]))
check(sum(g["sample_count"] for g in d["by_candidate_setup"]) == 4, "group total")
r30 = d["by_candidate_setup"][0]["horizons"]["+30m"]; check(r30["sample_count"] == 4 and r30["total_gain_pct"] == 1 + 2 + 3 + 5, "first rows only (the -5 later row dropped) " + str(r30))
check(B([row("d", "X", 5, 1, r30=7), row("d", "X", 5, 2, r30=8)])["by_candidate_setup"][0]["horizons"]["+30m"]["total_gain_pct"] == 7, "epoch tie: input order (stable)")
_, e = attempt(B, [row("d", "X", "abc", 1)]); check(e == "ValueError", "str epoch raises " + str(e))
check(B([row("d", "X", "100", 1, r30=1)])["sample_count"] == 1, "numeric-string epoch ok")
_, e = attempt(B, [{"day": "d", "symbol": "s", "episode": None}]); check(e == "TypeError", "episode None " + str(e))
_, e = attempt(B, [{"day": "d", "symbol": "s", "episode": {"checkpoints": None}}]); check(e == "AttributeError", "checkpoints None " + str(e))
check(B([{"day": "d", "symbol": "s"}])["sample_count"] == 1, "missing episode/feature tolerated")
# correlation
cr = [row(f"d{i}", "S", i, float(i), r5=float(i), r30=-float(i), reod=1.0) for i in range(1, 6)]
c = B(cr)["score_return_correlation"]; check(c["+5m"] == 1.0 and c["+30m"] == -1.0 and c["EOD"] is None and c["+15m"] is None, "corr " + str(c))
check(B([row("d", "S", 1, 1, r5=1)])["score_return_correlation"]["+5m"] is None, "n<2 none")
_, e = attempt(B, [row("a", "S", 1, "x", r5=1), row("b", "S", 2, 2, r5=2), row("c", "S", 3, 3, r5=4)]); check(e == "ValueError", "non-numeric score: corr drops pair but quartile sort raises " + str(e))
# quartiles
q = B([row(f"d{i}", "S", i, float(i), r30=float(i % 2)) for i in range(1, 9)])["score_quartiles"]
check([x["sample_count"] for x in q] == [2, 2, 2, 2] and q[0]["score_min"] == 1.0 and q[3]["score_max"] == 8.0 and q[0]["+30m"]["sample_count"] == 2, "quartiles 8")
q3 = B([row(f"d{i}", "S", i, float(i)) for i in range(1, 4)])["score_quartiles"]; check([x["sample_count"] for x in q3] == [1, 1, 1] and [x["quartile"] for x in q3] == [2, 3, 4], "3 rows: Q1 empty skipped (quartile numbers 2-4) " + str(q3))
check(len(B([row("d", "S", 1, 1.0)])["score_quartiles"]) == 1 and B([row("d", "S", 1, 1.0)])["score_quartiles"][0]["quartile"] == 4, "1 row -> quartile 4")
check(B([row("d", "S", 1, None), row("e", "S", 2, 3.0)])["score_quartiles"][0]["sample_count"] == 1, "None score excluded from quartiles")
_, e = attempt(B, [row("a", "S", 1, "x"), row("b", "S", 2, 1.0)]); check(e == "ValueError", "str score raises in quartiles " + str(e))
check(B([row("a", "S", 1, "2.5"), row("b", "S", 2, "1.5")])["score_quartiles"][0]["score_min"] in (1.5, 2.5), "numeric-string score ok")
check(B([row("a", "S", 1, 0)])["score_quartiles"][0]["score_min"] == 0.0, "score 0 kept (is not None)")
# grouping
g = B([row("a", "S", 1, 1, setup=None, sources=None), row("b", "S", 2, 1, setup="Z", sources=("B", "A")), row("c", "S", 3, 1, setup="Z", sources=[]), row("d", "S", 4, 1, setup="", sources=("A",))])
check([x["value"] for x in g["by_candidate_setup"]] == ["MISSING", "Z"] and g["by_candidate_setup"][0]["sample_count"] == 2, "setup None/'' -> MISSING, sorted " + str([x["value"] for x in g["by_candidate_setup"]]))
check(sorted(x["value"] for x in g["by_candidate_source"]) == ["A", "B+A", "MISSING"], "sources joined in given order " + str([x["value"] for x in g["by_candidate_source"]]))
check(list(g["by_candidate_setup"][0]["horizons"]) == ["+15m", "+30m", "EOD"] and list(g["by_candidate_source"][0]["horizons"]) == ["+5m", "+30m", "EOD"], "horizon sets")
gs = B([{"day": "a", "symbol": "s", "sources": "AB"}])["by_candidate_source"]; check(gs[0]["value"] == "A+B", "string sources split by char (observation)")
check(B([row("a", "S", 1, 1, setup=5)])["by_candidate_setup"][0]["value"] == "5", "setup str()")
_, e = attempt(B, [{"day": "a", "symbol": "s", "sources": 5}]); check(e == "TypeError", "int sources " + str(e))
# market coverage
m = B([row("a", "S", 1, 1, market={"snapshot_epoch": 1, "snapshot_age_sec": 300}), row("b", "S", 2, 1, market={"snapshot_epoch": 0, "snapshot_age_sec": 300.0001}),
       row("c", "S", 3, 1, market={"snapshot_epoch": 5}), row("d", "S", 4, 1, market={"snapshot_age_sec": 1}), row("e", "S", 5, 1)])["market_snapshot_coverage"]
check(m == {"observed_count": 3, "fresh_within_300s_count": 1, "total_count": 5, "coverage": 0.6, "fresh_coverage": 0.2}, "coverage " + str(m))
_, e = attempt(B, [row("a", "S", 1, 1, market={"snapshot_epoch": 1, "snapshot_age_sec": "x"})]); check(e == "ValueError", "bad age raises " + str(e))
check(B([row("a", "S", 1, 1, market={"snapshot_epoch": 1, "snapshot_age_sec": float("nan")})])["market_snapshot_coverage"]["fresh_within_300s_count"] == 0, "nan age not fresh")
_, e = attempt(B, [{"day": "a", "symbol": "s", "feature": {"market": 5}}]); check(e == "TypeError", "market non-mapping " + str(e))
# inputs unmodified, deterministic, JSON-safe
inp = copy.deepcopy(rows); a = B(rows); check(rows == inp and B(rows) == a, "pure"); json.dumps(a)
# consumer
big = [row(f"d{i}", "S", i, float(i), r5=float(i), r15=float(i % 3) - 1, r30=float(i % 2) * 2 - 1, reod=0.5, setup="gap" if i % 2 else None, market={"snapshot_epoch": i, "snapshot_age_sec": 10}) for i in range(1, 9)]
dg = B(big)
txt, e = attempt(rp.render_short_alpha_discriminator, {"scanner_diagnostics": dg}); check(txt and e is None, "render " + str(e))
check("## Scanner Diagnostics" in txt and "| `+5m` | 1.0000 |" in txt and "| `EOD` | - |" in txt and "| `gap` | 4 |" in txt and "| `MISSING` | 4 |" in txt, "render rows")
check("N=8" not in txt and "Point-in-time market snapshot coverage: **100.0%**" in txt and "Fresh within 300 seconds: **100.0%**" in txt, "render coverage")
check(txt.count("BLOCKED_BY_MARKET_SNAPSHOT_COVERAGE") == 0, "gate not blocked at 100%")
t0 = rp.render_short_alpha_discriminator({"scanner_diagnostics": B([])}); check("coverage: **0.0%**" in t0 and "BLOCKED_BY_MARKET_SNAPSHOT_COVERAGE" in t0, "empty -> blocked gate")
_, e = attempt(rp.render_short_alpha_discriminator, {"scanner_diagnostics": {"score_return_correlation": {"x": "abc"}}}); check(e == "ValueError", "render bad corr " + str(e))
check(not bad, "no effects attempted " + str(bad))
print("RF034_SCANNER_DIAGNOSTICS_CONSUMER_OK dedupe=first_epoch_per_day_symbol(str_epoch=ValueError,tie=stable) corr=pearson(n<2/const=None) quartiles=skip_empty(3rows=Q2-4,1row=Q4) groups=MISSING+source_join(str_sources=per_char) coverage=snapshot_epoch_known,age<=300 render=consumer_ok gate=blocked_at_0 bad_values=Value/TypeError_propagate pure=yes outside_writes=0 net_attempts=0")
