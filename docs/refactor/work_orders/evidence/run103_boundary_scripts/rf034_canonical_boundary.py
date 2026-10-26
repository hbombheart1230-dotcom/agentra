import socket, subprocess, sqlite3, sys, tempfile, copy, builtins, os, json
from pathlib import Path
sys.path.insert(0, os.getcwd())
from libs.reporting.alpha_research_board import canonical as K
from libs.reporting.alpha_research_board.contracts import CANDIDATE_IDS, ROW_COLUMNS, FEATURE_COLUMNS


def check(c, m="check"):
    if not c:
        raise SystemExit("CHECK_FAILED: " + str(m))


def _blocked(*a, **k):
    raise RuntimeError("BLOCKED_EFFECT")


socket.socket = _blocked
socket.create_connection = _blocked
subprocess.Popen = _blocked
sqlite3.connect = _blocked
_open = builtins.open


def _guard_open(f, mode="r", *a, **k):
    if any(c in mode for c in "wax+"):
        raise RuntimeError("BLOCKED_WRITE")
    return _open(f, mode, *a, **k)


builtins.open = _guard_open
_wt = Path.write_text  # test-fixture writer into TemporaryDirectory only
Path.write_text = lambda *a, **k: _blocked()

ns = K._normalize_status
check(ns("DISLOCATION_REBOUND", {"source_status": "PROMOTED"}) == "CLOSED", "permanent closed wins")
check(ns("X", {"final_offline_review": {"decision": "PROMOTE_ME"}}) == "PROMOTED")
check(ns("X", {"final_offline_review": {"decision": "PROMOTE_REVIEW"}}) == "DISCOVERY", "PROMOTE_REVIEW falls through")
check(ns("X", {"final_offline_review": {"decision": "REVIEW_READY_PROMOTE"}}) == "REVIEW_READY")
check(ns("X", {"sensitivity_review": {"decision": "FAIL_X"}}) == "CLOSED")
check(ns("X", {"board_bucket": "closed_x"}) == "CLOSED")
check(ns("X", {"source_status": "PASS"}) == "REVIEW_READY")
check(ns("X", {"board_bucket": "OBSERVE_FIXED"}) == "PROSPECTIVE")
check(ns("X", {}) == "DISCOVERY")
check(ns("X", {"final_offline_review": "bad", "source_status": None, "board_bucket": None}) == "DISCOVERY", "bad types")
check(ns("X", {"final_offline_review": {"decision": 7}}) == "DISCOVERY", "non-str decision")

fv = K._fixed_validation_status
check(fv("A", {}) == "FIXED_VALIDATION_NOT_YET_RUN")
check(fv("A", {"candidate_id": "A"}) == "FIXED_VALIDATION_PENDING")
base = {"candidate_id": "A", "window_complete": True}
check(fv("A", {**base, "decision": "PASS_RUNTIME_VALIDATION"}) == "FIXED_VALIDATION_PASSED")
check(fv("A", {**base, "decision": "FAIL_RUNTIME_EFFECT"}) == "FIXED_VALIDATION_FAILED")
check(fv("A", {**base, "decision": "INSUFFICIENT_RUNTIME_SAMPLE"}) == "FIXED_VALIDATION_INSUFFICIENT_EVIDENCE")
check(fv("A", {**base, "decision": None}) == "FIXED_VALIDATION_INSUFFICIENT_EVIDENCE")
truthy = fv("A", {"candidate_id": "A", "window_complete": "no", "decision": "PASS_RUNTIME_VALIDATION"})

pp = K._production_promotion_status
check(pp("PROMOTED", "FIXED_VALIDATION_PASSED") == "PRODUCTION_PROMOTION_ALLOWED")
for st in ("REVIEW_READY", "PROMOTED"):
    for fs in ("FIXED_VALIDATION_FAILED", "FIXED_VALIDATION_PENDING", "FIXED_VALIDATION_NOT_YET_RUN", "FIXED_VALIDATION_INSUFFICIENT_EVIDENCE"):
        check(pp(st, fs) == "PRODUCTION_PROMOTION_NOT_ALLOWED", (st, fs))
check(pp("REVIEW_READY", "FIXED_VALIDATION_PASSED") == "PRODUCTION_PROMOTION_NOT_ALLOWED")

exc = {}
with tempfile.TemporaryDirectory() as t:
    root = Path(t)
    s2 = root / "evaluation" / "agent_effectiveness" / "cumulative_20261001_20261020"
    s2.mkdir(parents=True)
    _wt(s2 / "strategist_stage2_effectiveness_deep_dive.json", json.dumps({
        "changed_symbol_by_horizon": {"+30m": {"comparison_count": 3, "observation_count": 4, "after_positive_rate": 0.5}},
        "coverage": {"refresh_records": 9}}), encoding="utf-8")
    legacy = {
        "candidates": [
            {"candidate_id": "IMMEDIATE_OPENING_PROBE", "final_offline_review": {"decision": "PROMOTED"},
             "operation_authority": {"enabled": True, "mode": "controlled_mock"},
             "prospective": {"sample_count": 5, "win_rate": 0.6}, "source_keys": ["feature_candidates", "nope"]},
            {"candidate_id": "BTC_STRONG_BULL_LOCAL_CONFIRMATION_V1", "source_status": "PROSPECTIVE_SHADOW_FROM_2026_08_25"},
            "garbage", None, {"candidate_id": "DISLOCATION_REBOUND", "source_status": "PROMOTED"},
        ],
        "sources": {"feature_candidates": {"path": "p", "available": True, "error": None}},
        "runtime_validation": {"candidate_id": "IMMEDIATE_OPENING_PROBE", "window_complete": True, "decision": "PASS_RUNTIME_VALIDATION"},
        "short_alpha_discriminator": {"cohort_review": {"cohorts": [{"cohort_id": "TOP_VALUE_VOLUME_NEGATIVE_CONTROL_V1", "horizons": {"+5m": {"count": 2}}}]}},
        "settled_findings": None,
    }
    snap = copy.deepcopy(legacy)
    out = K.canonicalize_board(legacy, reports_root=root, through_day="2026-10-20")
    check(legacy == snap, "legacy mutated")
    check(tuple(out["candidate_ids"]) == CANDIDATE_IDS and out["candidate_count"] == 14)
    check(all(tuple(r.keys()) == ROW_COLUMNS and tuple(r["feature_evidence"]) == FEATURE_COLUMNS for r in out["candidates"]))
    rows = {r["candidate_id"]: r for r in out["candidates"]}
    p = rows["IMMEDIATE_OPENING_PROBE"]
    check(p["status"] == "PROMOTED" and p["production_promotion_status"] == "PRODUCTION_PROMOTION_ALLOWED"
          and p["operation_status"] == "CONTROLLED_MOCK_CONTINUES", p)
    check(rows["DISLOCATION_REBOUND"]["status"] == "CLOSED" and rows["DISLOCATION_REBOUND"]["operation_status"] == "NOT_RUNNING")
    check(rows["BTC_STRONG_BULL_LOCAL_CONFIRMATION_V1"]["operation_status"] == "SHADOW_CONTINUES")
    check(rows["STRATEGIST_STAGE2_REFRESH_AUTHORITY_V1"]["historical_evidence"]["sample_count"] == 3)
    sh = rows["SAMSUNG_HYNIX_FIXED_UNIVERSE_TOP1"]
    check(sh["status"] == "DISCOVERY" and sh["operation_status"] == "UNKNOWN_OPERATION_STATUS")
    check(out["integrity"]["status"] == "PASS", out["integrity"]["status"])
    check(out["settled_findings"] == [])

    empty = root / "empty"
    empty.mkdir()
    out2 = K.canonicalize_board({}, reports_root=empty, through_day="2026-10-20")
    check(out2["integrity"]["status"] == "PASS_WITH_MISSING_SOURCES"
          and out2["sources"]["strategist_stage2_effectiveness"]["error"] == "MISSING_ARTIFACT")
    check(out2["integrity"]["candidate_registry_matches"] is True)

    bad = root / "bad" / "evaluation" / "agent_effectiveness" / "2026-10-20"
    bad.mkdir(parents=True)
    _wt(bad / "strategist_stage2_effectiveness_deep_dive.json", "{x", encoding="utf-8")
    out3 = K.canonicalize_board({}, reports_root=root / "bad", through_day="2026-10-20")
    check(out3["sources"]["strategist_stage2_effectiveness"]["error"].startswith("INVALID_ARTIFACT"))

    for name, leg in (
        ("bad_sample_count", {"candidates": [{"candidate_id": "IMMEDIATE_OPENING_PROBE", "historical": {"sample_count": "abc"}}]}),
        ("candidates_int", {"candidates": 5}),
    ):
        try:
            K.canonicalize_board(leg, reports_root=empty, through_day="d")
            exc[name] = "no_raise"
        except Exception as e:
            exc[name] = type(e).__name__
    before = sorted(str(q) for q in root.rglob("*"))
    K.canonicalize_board(legacy, reports_root=root, through_day="2026-10-20")
    check(before == sorted(str(q) for q in root.rglob("*")), "reader wrote files")

print(f"RF034_CANONICAL_OK status_fns=3 board_rows=14 mutation=none truthy_window={truthy} "
      f"exc={exc['bad_sample_count']}/{exc['candidates_int']} io=net_write_blocked debug={__debug__}")
