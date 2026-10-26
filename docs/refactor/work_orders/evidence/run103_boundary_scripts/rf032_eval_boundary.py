import socket, subprocess, sqlite3, sys, tempfile, copy, builtins, os, json
from pathlib import Path
sys.path.insert(0, os.getcwd())
from libs.reporting.evaluation import artifact_inventory as AI
from libs.reporting.evaluation import attribution_score_v0 as AS


def check(c, m="check"):
    if not c:
        raise SystemExit("CHECK_FAILED: " + str(m))


def _blocked(*a, **k):
    raise RuntimeError("BLOCKED_EFFECT")


socket.socket = _blocked
socket.create_connection = _blocked
subprocess.Popen = _blocked
subprocess.run = _blocked
sqlite3.connect = _blocked
os.system = _blocked
_open = builtins.open
write_attempts = []


def _guard_open(f, mode="r", *a, **k):
    if any(c in mode for c in "wax+"):
        write_attempts.append(str(f))
        raise RuntimeError("BLOCKED_WRITE")
    return _open(f, mode, *a, **k)


builtins.open = _guard_open
_wt = Path.write_text  # fixture writer used only inside TemporaryDirectory
Path.write_text = lambda *a, **k: _blocked()

# --- artifact_inventory row predicates ---
syn = AI.is_synthetic_evaluation_row
check(syn({"decision_id": "my_TEST_1"}) is True)
check(syn({"run_id": "fixture"}) is True)
check(syn({"candidate_pool_id": "Synthetic-x"}) is True)
check(syn({"symbol": "005930"}) is False)
check(syn({"symbol": "AAPL"}) is True)
check(syn({"ranked": [{"ticker": "000660"}, {"selected_symbol": "BTC"}]}) is True)
check(syn({"layer_packet_ids": {"symbol": "XXX"}}) is False, "packet_ids path ignored")
check(syn({"x_packet_ids": {"symbol": "XXX"}}) is False, "_packet_ids suffix ignored")
check(syn({"symbol": None, "ticker": ""}) is False)
check(syn({}) is False)
row = {"symbol": "005930", "nested": {"symbol": "005930"}}
snap = copy.deepcopy(row)
syn(row)
check(row == snap, "predicate mutated row")
reg = AI.is_regular_session_evaluation_row
check(reg({}) is True and reg({"generated_at": "garbage"}) is True, "unparseable -> regular (fail-open by design)")
check(reg({"generated_at": "2026-10-20T09:00:00+09:00"}) is True)
check(reg({"generated_at": "2026-10-20T15:30:59+09:00"}) is True)
check(reg({"generated_at": "2026-10-20T15:31:00+09:00"}) is False)
check(reg({"generated_at": "2026-10-20T08:59:00+09:00"}) is False)
check(reg({"generated_at": "2026-10-20T00:10:00Z"}) is True, "UTC 00:10 == KST 09:10")
check(reg({"generated_at": "2026-10-20T09:10:00"}) is False, "naive treated as UTC -> KST 18:10")

# --- inventory_trade / build_artifact_inventory on tmp reports ---
with tempfile.TemporaryDirectory() as t:
    base = Path(t)
    reports = base / "reports"
    day = "2026-10-20"
    td = reports / "trades" / day / "T1"
    (td / "evidence").mkdir(parents=True)
    _wt(td / "lifecycle_bundle.json", json.dumps({"schema_version": "x", "forward_windows_complete": 1}), encoding="utf-8")
    _wt(td / "entry.json", "{bad", encoding="utf-8")
    _wt(td / "evidence" / "scanner_evidence.json", "[]", encoding="utf-8")
    tr = AI.inventory_trade(td)
    check(tr["trade_id"] == "T1" and tr["complete"] is False)
    check(set(tr["missing_required"]) == {"strategist_evidence", "commander_evidence", "monitor_evidence"}, tr["missing_required"])
    check(tr["artifacts"]["lifecycle_bundle"]["forward_windows_complete"] is True)
    check(tr["artifacts"]["entry"]["schema_version"] == "" and tr["artifacts"]["entry"]["exists"] is True, "corrupt json -> empty fields")
    check(tr["artifacts"]["exit"]["missing_reason"] == "artifact_not_found")
    inv = AI.build_artifact_inventory(reports, day)
    check(inv["trade_count"] == 1 and inv["schema_version"] == "artifact_inventory.v1")
    check(0 < inv["required_coverage"] < 1, inv["required_coverage"])
    check(inv["required_artifact_count"] == 6 + 2, inv["required_artifact_count"])
    check("q9_decision_windows" in inv["daily_artifacts"] and "q9_vs_samsung_hynix_comparison" in inv["daily_artifacts"])
    empty = AI.build_artifact_inventory(base / "nothing", day)
    check(empty["trade_count"] == 0 and empty["required_artifact_count"] == 2 and empty["required_coverage"] == 0.0, empty["required_artifact_count"])
    check(AI.iter_trade_dirs(base / "nothing", day) == [])
    check(AI.read_json(base / "missing.json") == {})
    tree_before = sorted(str(p) for p in base.rglob("*"))
    AI.build_artifact_inventory(reports, day)
    check(tree_before == sorted(str(p) for p in base.rglob("*")), "inventory wrote files")

    # --- attribution score ---
    sa = {"rows": [
        {"trade_id": "A", "final_to_executed_changed": True, "monitor_to_commander_changed": True,
         "post_to_selected_changed": True, "selected_symbol": "005930", "raw_scanner_top1": "000660", "post_strategy_top1": "035720",
         "raw_to_post_changed": True},
        {"trade_id": "B", "selection_mismatch": {"x": 1}, "selected_symbol": "005930", "raw_scanner_top1": "005930"},
        "junk", None]}
    si = AS._selection_integrity(sa)
    check(si["status"] == "OK" and si["score"] == 55, si)
    check(AS._selection_integrity({})["status"] == "INSUFFICIENT_EVIDENCE" and AS._selection_integrity({})["score"] is None)
    models = [{"trade_id": "A", "selection": {"selected_rank": 4}}, {"trade_id": "B", "selection": {"selected_candidate": {"rank": "x"}}}]
    sc = AS._scanner_alignment(sa, models)
    check(sc["status"] == "OK" and 0 <= sc["score"] <= 100 and any("selected_rank_4" in r for r in sc["reasons"]), sc)
    check(AS._scanner_alignment({"rows": []}, [])["status"] == "INSUFFICIENT_EVIDENCE")
    sa_snap = copy.deepcopy(sa)
    AS._scanner_alignment(sa, models)
    check(sa == sa_snap, "alignment mutated input")

    ledger = reports / "evaluation" / "freeze_window" / "w1"
    ledger.mkdir(parents=True)
    _wt(ledger / "daily_ledger.json", json.dumps({"days": [{"day": day, "evidence_status": "PARTIAL"}, "x"]}), encoding="utf-8")
    out = AS.build_attribution_score_v0(
        day=day, reports_root=reports, models=models,
        daily_scorecard={"artifact_integrity": {"status_counts": {"PASS": 2, "WATCH": 1, "FAIL": 1}}},
        selection_authority=sa, horizon_compliance={}, entry_timing={})
    check(out["schema_version"] == "attribution_score_v0.v1" and out["behavior_effect"] == "observation_only")
    eq = out["scores"]["evidence_quality_score"]
    check(eq["status"] == "OK" and "ledger_evidence_status:PARTIAL" in eq["reasons"] and "fail_integrity_rows_present" in eq["reasons"], eq)
    check(out["weakest_observed_axis"]["name"] in {"selection_integrity_score", "scanner_alignment_score"}, out["weakest_observed_axis"])
    out_empty = AS.build_attribution_score_v0(
        day=day, reports_root=base / "none", models=[], daily_scorecard={}, selection_authority={}, horizon_compliance={}, entry_timing={})
    check(out_empty["weakest_observed_axis"] == {"name": "", "score": None})
    check(all(v["status"] == "INSUFFICIENT_EVIDENCE" for v in out_empty["scores"].values()))
    exc = {}
    for name, kw in (("bad_count", {"daily_scorecard": {"artifact_integrity": {"status_counts": {"PASS": "x"}}}}),
                     ("none_models", {"models": None})):
        args = dict(day=day, reports_root=base / "none", models=[], daily_scorecard={}, selection_authority={},
                    horizon_compliance={}, entry_timing={})
        args.update(kw)
        try:
            AS.build_attribution_score_v0(**args)
            exc[name] = "no_raise"
        except Exception as e:
            exc[name] = type(e).__name__
    check(write_attempts == [], write_attempts)

print(f"RF032_EVAL_OK predicates=2 inventory=2 attribution=3 mutation=none exc={exc['bad_count']}/{exc['none_models']} "
      f"write_attempts={len(write_attempts)} io=net_sqlite_subprocess_write_blocked debug={__debug__}")
