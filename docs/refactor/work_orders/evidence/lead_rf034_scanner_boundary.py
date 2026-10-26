"""RF-034 first-time independent scanner_diagnostics pure boundary; no broker/network.

Run from directory containing scanner_diagnostics.py, metrics.py, cohorts.py:
  PYTHONDONTWRITEBYTECODE=1 python -S lead_rf034_scanner_boundary.py
  PYTHONDONTWRITEBYTECODE=1 python -O -S lead_rf034_scanner_boundary.py

Source: scanner_diagnostics.py=b8de71424ec64e8a14e94039b2c0054b0f591dd7
        metrics.py=c2a64b2bdec26c42eabaab6326324066a1417f85
cohorts.py is an isolated extraction of independent_day_symbol_rows, not full blob.
"""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import pathlib
import sys
import types

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parent
count = 0

def check(condition, msg):
    global count
    if not condition:
        raise SystemExit("FAIL: " + msg)
    count += 1

def blob(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

check(blob(ROOT / "scanner_diagnostics.py") == "b8de71424ec64e8a14e94039b2c0054b0f591dd7", "scanner exact blob")
check(blob(ROOT / "metrics.py") == "c2a64b2bdec26c42eabaab6326324066a1417f85", "metrics exact blob")

pkg = types.ModuleType("rf034_boundary")
pkg.__path__ = [str(ROOT)]
sys.modules[pkg.__name__] = pkg

def load(name):
    spec = importlib.util.spec_from_file_location("rf034_boundary." + name, ROOT / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

load("cohorts")
load("metrics")
mod = load("scanner_diagnostics")
empty = mod.build_scanner_diagnostics([])
check(empty["sample_count"] == 0 and empty["score_quartiles"] == [], "empty sample")
check(empty["market_snapshot_coverage"]["coverage"] == 0.0, "empty coverage")
check(all(v is None for v in empty["score_return_correlation"].values()), "empty correlation")
check(empty["behavior_change_authorized"] is False, "behavior authorization stays false")

def row(symbol, epoch, score, age, source, setup="S", day="2026-10-26", snapshot=True):
    return {"day": day, "symbol": symbol, "score_total": score,
            "candidate_setup": setup, "sources": source,
            "episode": {"decision_epoch": epoch,
                        "checkpoints": {h: {"live_net_return_pct": score}
                                        for h in ("+5m", "+15m", "+30m", "EOD")}},
            "feature": {"market": {"snapshot_epoch": epoch if snapshot else None,
                                   "snapshot_age_sec": age}}}

rows = [row("A", 100, 1, 300, ["A"]), row("A", 200, 99, 0, ["B"]),
        row("B", 150, 2, 301, ["B"], "S2"),
        row("C", 120, 3, -1, [], ""),
        row("D", 300, 4, None, ["A", "B"], snapshot=False),
        row("E", 400, 5, 50, ["A"], "S2")]
original = copy.deepcopy(rows)
result = mod.build_scanner_diagnostics(rows)
check(rows == original, "input mutation")
check(result["sample_count"] == 5, "earliest duplicate first-day-symbol")
check(result["score_return_correlation"]["+30m"] == 1.0, "real metrics pearson")
check(result["score_quartiles"][-1]["sample_count"] == 2, "quartile remainder")
check([g["value"] for g in result["by_candidate_setup"]] == ["MISSING", "S", "S2"], "setup grouping")
check([g["value"] for g in result["by_candidate_source"]] == ["A", "A+B", "B", "MISSING"], "source grouping")
coverage = result["market_snapshot_coverage"]
check(coverage["observed_count"] == 4 and coverage["coverage"] == 0.8, "observed coverage")
check(coverage["fresh_within_300s_count"] == 3 and coverage["fresh_coverage"] == 0.6, "fresh boundary 300 inclusive, negative age observed")
check(result["evaluation_unit"] == "first_day_symbol", "unit")
check(result["behavior_change_authorized"] is False, "no behavior authority")

bad = row("Z", 1, "invalid", 1, ["A"])
try:
    mod.build_scanner_diagnostics([bad])
except ValueError:
    check(True, "bad score ValueError")
else:
    check(False, "bad score should raise")
bad = row("Z", 1, 1, "invalid", ["A"])
try:
    mod.build_scanner_diagnostics([bad])
except ValueError:
    check(True, "bad age ValueError")
else:
    check(False, "bad age should raise")
bad = row("Z", 1, 1, 1, ["A", 3])
try:
    mod.build_scanner_diagnostics([bad])
except TypeError:
    check(True, "mixed sources TypeError")
else:
    check(False, "mixed sources should raise")

print(f"RF034_SCANNER_DIAGNOSTICS_OK cases={count} source=exact2+extracted1 external_effects=0")
