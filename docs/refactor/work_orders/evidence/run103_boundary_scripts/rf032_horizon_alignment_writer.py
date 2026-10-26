# RF-032: libs/reporting/evaluation/horizon_alignment.py (pure evaluation writer, not covered by run 105/108):
# build_horizon_alignment_review / render_horizon_alignment_review / write_horizon_alignment_review on a fully tmp tree
# (reports_root, data/logs/quant_shadow_candidates, data/state.json minute rows, cost profile). No UEF, no live, no network.
import os, sys, json, copy, socket, subprocess, sqlite3, builtins, importlib, tempfile, hashlib
from datetime import datetime, timezone, timedelta
for k in list(os.environ):
    if any(s in k.upper() for s in ("KIWOOM", "OPENROUTER", "API_KEY", "SECRET", "TOKEN", "ACCOUNT", "ALLOW_REAL")): del os.environ[k]
repo = os.getcwd(); sys.path.insert(0, repo)
import ssl, http.client
from pathlib import Path
tmp = Path(tempfile.mkdtemp(prefix="rf032_ha_")).resolve()
os.environ["BROKER_COST_PROFILE_PATH"] = str(tmp / "missing_profile.json")
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
_wt, _mk, _rp, _ul = Path.write_text, Path.mkdir, Path.replace, Path.unlink
def g(orig, tag):
    def f(self, *a, **k):
        if not inside(self): bad.append(tag + ":" + str(self)); raise OSError("blocked")
        return orig(self, *a, **k)
    return f
Path.write_text, Path.mkdir, Path.replace, Path.unlink = g(_wt, "write_text"), g(_mk, "mkdir"), g(_rp, "replace"), g(_ul, "unlink")
def check(c, m):
    if not c: raise SystemExit("CHECK_FAILED: " + m)
def tree(root): return sorted((str(p.relative_to(root)), hashlib.sha1(p.read_bytes()).hexdigest()) for p in Path(root).rglob("*") if p.is_file())
KST = timezone(timedelta(hours=9))
os.chdir(tmp)
ha = importlib.import_module("libs.reporting.evaluation.horizon_alignment")
# ---- fixture: 4 KST days x 6 symbols x 3 tactics; reports_root=tmp/reports; shadow root = tmp/data/logs/quant_shadow_candidates
reports = tmp / "reports"; reports.mkdir()
shadow = tmp / "data" / "logs" / "quant_shadow_candidates"
days = ["2026-06-22", "2026-06-23", "2026-06-24", "2026-06-25"]
symbols = ["005930", "000660", "035420", "051910", "068270", "207940"]
minute = {}
def epoch(day, hh, mm): return int(datetime.strptime(day, "%Y-%m-%d").replace(hour=hh, minute=mm, tzinfo=KST).timestamp())
def rawts(day, hh, mm): return day.replace("-", "") + "%02d%02d00" % (hh, mm)
# tactic "up" gains ~+1.2% at every checkpoint (cost 0.9 -> net ~+0.3..); "down" loses; "mixed" gains except one day
payload_by_day = {d: [] for d in days}
for di, day in enumerate(days):
    for si, sym in enumerate(symbols):
        tactic = ("up", "down", "mixed")[si % 3]
        base_price = 10000.0
        drift = {"up": 0.015, "down": -0.01, "mixed": (0.015 if di != 3 else -0.02)}[tactic]
        rows = []
        for m in range(0, 80):
            hh, mm = 9 + (10 + m) // 60, (10 + m) % 60
            px = round(base_price * (1 + drift * min(m, 60) / 60.0), 2)
            rows.append({"ts": epoch(day, hh, mm), "close": px, "high": px, "low": px, "raw_ts": rawts(day, hh, mm)})
        minute.setdefault(sym, []).extend(rows)
        payload_by_day[day].append({"symbol": sym, "quant_tactic_id": tactic, "shadow_role": "primary",
            "entry_lane_observation": {"time_bucket": "open_30m", "primary_lane": "breakout" if si < 3 else "pullback", "market_regime_rail": "calm", "subtype": "s%d" % si},
            "shadow_forward_base": {"available": True, "baseline_epoch": epoch(day, 9, 10), "baseline_price": base_price, "baseline_raw_ts": rawts(day, 9, 10)}})
# the 'up' tactic gets two more symbols per day so it passes MIN_OBSERVATIONS(20)/symbol-share (<=0.40)
extra = ["055550", "105560", "086790", "316140"]
for di, day in enumerate(days):
    for ei, sym in enumerate(extra):
        base_price = 10000.0
        rows = []
        for m in range(0, 80):
            hh, mm = 9 + (10 + m) // 60, (10 + m) % 60
            px = round(base_price * (1 + 0.016 * min(m, 60) / 60.0), 2)
            rows.append({"ts": epoch(day, hh, mm), "close": px, "high": px, "low": px, "raw_ts": rawts(day, hh, mm)})
        minute.setdefault(sym, []).extend(rows)
        payload_by_day[day].append({"symbol": sym, "quant_tactic_id": "up", "shadow_role": "primary",
            "entry_lane_observation": {"time_bucket": "open_30m", "primary_lane": "breakout", "market_regime_rail": "calm", "subtype": "e%d" % ei},
            "shadow_forward_base": {"available": True, "baseline_epoch": epoch(day, 9, 10), "baseline_price": base_price, "baseline_raw_ts": rawts(day, 9, 10)}})
for day, cands in payload_by_day.items():
    d = shadow / day; d.mkdir(parents=True)
    (d / "a.json").write_text(json.dumps({"generated_at": day + "T09:10:30+09:00", "candidates": cands + ["not-a-mapping", None]}), encoding="utf-8")
    (d / "latest.json").write_text(json.dumps({"generated_at": "ignored", "candidates": [{"symbol": "999999"}]}), encoding="utf-8")   # latest.json is skipped by loader
    (d / "broken.json").write_text("{nope", encoding="utf-8")
(tmp / "data" / "state.json").write_text(json.dumps({"recent_minute_ohlcv_by_symbol": minute}), encoding="utf-8")
(tmp / "cost.json").write_text(json.dumps({"source": "tmp_profile", "sample_count": 7, "ema_round_trip_cost_pct": 0.004, "conservative_round_trip_cost_pct": 0.009}), encoding="utf-8")
(tmp / "cost_bad.json").write_text("[1,2]", encoding="utf-8")
cost = tmp / "cost.json"
before_inputs = tree(tmp)
# ---- build
out = ha.build_horizon_alignment_review(reports_root=reports, start=days[0], end=days[-1], cost_profile_path=cost)
check(tree(tmp) == before_inputs, "build wrote nothing (pure read)")
check(out["schema_version"] == "horizon_alignment_review.v2" and out["behavior_effect"] == "evaluation_only", "schema/effect")
check(out["range"] == {"start": days[0], "end": days[-1]}, "range")
check(out["cost_model"]["source"] == "tmp_profile" and abs(out["cost_model"]["conservative_round_trip_cost_pct"] - 0.9) < 1e-9 and out["cost_model"]["sample_count"] == 7, "cost model from profile")
check(out["candidate_count"] == 4 * (6 + 4), "candidates: non-mapping/latest/broken skipped, got %s" % out["candidate_count"])
tt = {(r["dimensions"]["tactic"], r["horizon"]): r for r in out["time_tactic"]}
up60 = tt[("up", "+60m")]
check(up60["observed_count"] == 4 * (2 + 4) and up60["observed_day_count"] == 4, "up observations")
check(up60["evidence_eligible"] is True and up60["cost_positive"] is True and up60["decision"] == "CONTROLLED_ADOPTION_CANDIDATE", "up cost-positive @+60m: %r" % up60["decision"])
dn60 = tt[("down", "+60m")]
check(dn60["decision"] == "INSUFFICIENT_EVIDENCE" or dn60["decision"] == "REJECT_COST_NEGATIVE", "down not adopted")
check(dn60["average_net_return_pct"] < 0, "down net negative")
check(out["decision"] == "CONTROLLED_ADOPTION_CANDIDATE_FOUND" and out["next_action"]["decision"] == "PREPARE_SHADOW_POLICY_SPEC" and out["next_action"]["behavior_change_authorized"] is False, "decision chain")
check(out["controlled_adoption_candidates"] and all(r["cost_positive"] for r in out["controlled_adoption_candidates"]), "adoption list")
# sort order: cost_positive first, then avg net desc
keys = [(not r["cost_positive"], -r["average_net_return_pct"], -r["observed_count"]) for r in out["time_tactic"]]
check(keys == sorted(keys), "sorted")
check(out["time_lane"] and out["time_tactic_market_rail"], "other dimensions present")
# leave-one-day-out for up60 has 4 days, all positive
check(sorted(up60["leave_one_day_out_net_returns_pct"]) == sorted(d.replace("-", "") for d in days) and up60["robust_across_days"] is True, "LODO")
# ---- rail: not robust when one day negative (mixed) -> never adopted
mx = [r for r in out["time_tactic"] if r["dimensions"]["tactic"] == "mixed"]
check(all(not r["cost_positive"] for r in mx), "mixed never adopted")
# ---- empty range / missing cost profile / bad cost profile
empty = ha.build_horizon_alignment_review(reports_root=reports, start="2026-07-01", end="2026-07-02", cost_profile_path=None)
check(empty["candidate_count"] == 0 and empty["decision"] == "NO_COST_POSITIVE_COMBINATION" and empty["next_action"]["decision"] == "REJECT_CURRENT_HYPOTHESIS_AND_RESEARCH_NEW_ALPHA", "empty -> NO_COST_POSITIVE")
check(empty["cost_model"]["source"] == "fallback" and abs(empty["cost_model"]["conservative_round_trip_cost_pct"] - 0.9) < 1e-9 and empty["cost_model"]["profile_path"] == "data/state/broker_cost_profile.json", "fallback cost 0.9 / default path text")
bad_cost = ha.build_horizon_alignment_review(reports_root=reports, start=days[0], end=days[0], cost_profile_path=tmp / "cost_bad.json")
check(bad_cost["cost_model"]["source"] == "fallback", "non-dict profile -> fallback")
# ---- exception contract
exc = {}
for name, kw in (("bad_start", dict(start="nope", end="2026-06-25")), ("end_before_start", dict(start="2026-06-25", end="2026-06-22"))):
    try: r = ha.build_horizon_alignment_review(reports_root=reports, cost_profile_path=cost, **kw); exc[name] = "no_raise:%d" % r["candidate_count"]
    except Exception as e: exc[name] = type(e).__name__
check(exc["bad_start"] == "ValueError" and exc["end_before_start"] == "no_raise:0", "exc contract: %r" % exc)
# ---- render
md = ha.render_horizon_alignment_review(out)
check(md.endswith("\n") and "## Decision: **CONTROLLED_ADOPTION_CANDIDATE_FOUND**" in md and "behavior change authorized: **False**" in md and "| open_30m | up | +60m |" in md, "render content")
md_empty = ha.render_horizon_alignment_review(empty)
check(md_empty.count("- None") == 2, "empty render shows None x2")
md_min = ha.render_horizon_alignment_review({})
check("Decision: **None**" in md_min, "render of {} does not raise")
# ---- writer (tmp output only)
od = tmp / "out" / "nested"
w = ha.write_horizon_alignment_review(reports_root=reports, start=days[0], end=days[-1], output_dir=od, cost_profile_path=cost)
check(set(w) == {"json", "markdown"} and Path(w["json"]).name == "horizon_alignment_review.json" and Path(w["markdown"]).name == "horizon_alignment_review.md", "writer return")
written = json.loads(Path(w["json"]).read_text(encoding="utf-8"))
check(written == json.loads(json.dumps(out)), "written JSON == build output")
check(Path(w["json"]).read_text(encoding="utf-8").endswith("}\n") and Path(w["markdown"]).read_text(encoding="utf-8") == md, "written md == render")
after1 = tree(tmp)
w2 = ha.write_horizon_alignment_review(reports_root=reports, start=days[0], end=days[-1], output_dir=od, cost_profile_path=cost)
check(tree(tmp) == after1 and w2 == w, "idempotent rewrite")
check(sorted(set(p for p, _ in after1) - set(p for p, _ in before_inputs)) == sorted([os.path.join("out", "nested", "horizon_alignment_review.json"), os.path.join("out", "nested", "horizon_alignment_review.md")]), "only 2 new files")
# ---- outside write is blocked (guard check) and writer propagates OSError
try: ha.write_horizon_alignment_review(reports_root=reports, start=days[0], end=days[0], output_dir=tmp.parent / "rf032_ha_outside_x", cost_profile_path=cost); wo = "no_raise"
except OSError: wo = "OSError_blocked"
check(wo == "OSError_blocked", "outside write blocked")
blocked_outside = [b for b in bad if b.startswith("mkdir:")]
bad = [b for b in bad if not b.startswith("mkdir:")]
check(not bad and len(blocked_outside) == 1, "no other blocked effects: %r" % bad)
print("RF032_HORIZON_ALIGNMENT_OK candidates=%d adoption=%d up60=%s decision=%s empty=%s exc=%s files=2 idempotent=yes outside_write=%s net_sqlite_subprocess_blocked=yes debug=%s"
      % (out["candidate_count"], len(out["controlled_adoption_candidates"]), up60["decision"], out["decision"], empty["decision"], "/".join(f"{k}:{v}" for k, v in sorted(exc.items())), wo, __debug__))
