"""FAST08 A8.5 smoke tests: profitability-recovery diagnostics and market regime rail."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pytest

from libs.reporting import fast08_shadow_projection as sp
from libs.reporting import market_regime_rail_review as rail
from libs.reporting import profitability_recovery_day1 as recovery


def _write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def trade(root: Path, name: str, bundle: Dict[str, Any], *, llm: bool = False, state: Dict[str, Any] | None = None) -> Path:
    tdir = root / "trades" / "2026-07-01" / "RUN" / name
    _write(tdir / "lifecycle_bundle.json", bundle)
    if llm:
        _write(tdir / "reports" / "ai_trade_report_llm_response.json", {})
    if state is not None:
        _write(tdir / "reports" / "report_generation_state.json", state)
    return tdir


FULL_EXECUTION = {"order_status": "filled", "order_id": "1", "execution_mode": "simulation", "broker_env": "mock", "filled_qty": 1, "avg_price": 10}


def test_closed_trade_diagnostics_and_missing_evidence_stay_visible(tmp_path: Path) -> None:
    root = tmp_path / "reports"
    trade(root, "T1", {"trade_id": "T1", "status": "closed", "symbol": "005930", "trade_outcome": {"return_pct": -1.5},
                       "same_day_reporter_linkage": {"status": "linked", "linkage_reason": "r"}, "hold_events_count": 3,
                       "holding_phase_summary": "held", "execution_details": FULL_EXECUTION}, llm=True)
    trade(root, "T2", {"trade_id": "T2", "exit": {"action": "sell"}, "story_contract": {"story_type": "Decision_Only"}},
          state={"components": {"ai_trade_report": {"status": "FAILED"}}})
    trade(root, "T3", {"status": "open"})
    rows = {r["trade_id"]: r for r in recovery.iter_trade_diagnostic_rows(root, "2026-07-01")}
    t1, t2, t3 = rows["T1"], rows["T2"], rows["T3"]
    assert t1["closed_trade"] and t1["loss_trade"] and t1["return_pct"] == -1.5
    assert t1["same_day_linkage_missing"] is False and t1["holding_evidence_thin"] is False
    assert t1["execution_fields_missing"] == [] and t1["ai_trade_report_status"] == "ok"
    assert t2["closed_trade_decision_only_misclassification"] and t2["closed_trade_report_generation_regression"]
    assert t2["same_day_linkage_missing"] and t2["holding_evidence_thin"] and t2["execution_missing_fields_count"] == 6
    assert t3["closed_trade"] is False and t3["closed_trade_report_generation_regression"] is False
    assert t3["trade_id"] == "T3"
    audit = recovery.audit_profitability_recovery_day(root, "2026-07-01")
    assert (audit["trade_count"], audit["closed_trade_count"], audit["closed_trade_report_generation_regression_count"]) == (3, 2, 1)
    assert audit["execution_fields_missing_count"] == 6 + 6
    card = recovery.build_daily_profitability_scorecard(root, "2026-07-01")
    assert card["loss_trades"] == 1 and card["total_trades"] == 3 and card["rows"] == audit["rows"]
    assert recovery.audit_profitability_recovery_day(tmp_path / "none", "2026-07-01")["top_recurring_diagnostic_weakness"] == "none"


def test_predicates_do_not_invent_state() -> None:
    assert sp.safe_float("") is None and sp.safe_float("x") is None and sp.safe_float("1.5") == 1.5
    assert sp.linkage_surface_present({"status": "missing"}) is False
    assert sp.linkage_surface_present({"status": "missing", "linkage_reason": "r"}) is True
    assert sp.is_closed_trade_report_generation_regression(closed_trade=True, ai_trade_report_llm_exists=True, ai_status="") is False
    assert sp.is_closed_trade_report_generation_regression(closed_trade=False, ai_trade_report_llm_exists=False, ai_status="failed") is False
    assert sp.resolve_ai_trade_report_status({}, {}, False) == "" and sp.resolve_ai_trade_report_status({}, {}, True) == "ok"
    assert sp.execution_missing_fields({"order_id": []}, ("order_id", "avg_price")) == ["order_id", "avg_price"]


def test_entry_exit_monitor_context_fallback_no_longer_crashes_and_invents_nothing(tmp_path: Path) -> None:
    # A9: this path used to raise UnboundLocalError (holding_phase_summary read before assignment).
    root = tmp_path / "reports"
    row = recovery.read_trade_diagnostic_row(trade(root, "T9", {"entry": {"monitor_context": {"k": 1}}}))
    assert row["monitor_context_snapshots_count"] == 1 and row["monitor_context_source"] == "entry_exit_context"
    assert row["holding_summary_source"] == "entry_exit_context_fallback"
    assert row["holding_phase_summary"] == sp.ENTRY_EXIT_CONTEXT_SUMMARY
    assert row["hold_events_count"] == 0 and row["holding_evidence_thin"] is True  # no hold facts were invented
    assert row["hold_duration"] == "" and row["hold_duration_sec"] is None


def snapshot(**over: Any) -> Dict[str, Any]:
    base = {"available": True, "schema_version": "v1", "korea_indices": {"breadth": -0.5},
            "index_moves": {"kospi_pct": -0.9, "kosdaq_pct": -1.2, "nasdaq_pct": 0.5, "sp500_pct": 0.1, "krx_night_futures_pct": 0.0},
            "macro_moves": {"vix_level": 22, "vix_pct": 9}, "macro_indicators": {"indicators": {"usdkrw": {"change_pct": 0.6}}}}
    base.update(over)
    return base


@pytest.mark.parametrize("snap,expected", [
    ({"available": False}, "not_available"),
    (snapshot(index_moves={"krx_night_futures_pct": -2.5}), "krx_night_futures_gap_down"),
    (snapshot(index_moves={"krx_night_futures_pct": 1.5, "kospi_pct": 0.1, "kosdaq_pct": 0.0}, korea_indices={"breadth": 0.1}), "krx_night_futures_gap_up"),
    (snapshot(), "us_tech_risk_on_korea_weak"),
    (snapshot(index_moves={"kospi_pct": -0.9, "kosdaq_pct": -1.2}), "risk_off_breadth_collapse"),
    (snapshot(index_moves={"kospi_pct": -0.9}, macro_moves={}, macro_indicators={}, korea_indices={"breadth": 0}), "defensive_rotation"),
    (snapshot(index_moves={"nasdaq_pct": 0.5, "sp500_pct": 0.2}, korea_indices={"breadth": 0.2}), "liquidity_leader_rotation"),
    (snapshot(index_moves={}, korea_indices={"breadth": 0.2}, macro_moves={"vix_level": 30}), "macro_pressure_no_trade"),
    (snapshot(index_moves={}, korea_indices={"breadth": 0.2}, macro_moves={}, macro_indicators={}), "neutral_observation"),
])
def test_regime_thresholds_stay_in_facade(snap: Dict[str, Any], expected: str) -> None:
    result = rail.classify_market_regime_rail(snap)
    assert result["rail_id"] == expected and result["behavior_effect"] == "evaluation_only"


def test_market_inputs_fall_back_to_indicators_and_render(tmp_path: Path) -> None:
    inputs = sp.market_inputs({"macro_indicators": {"indicators": {"kospi": {"change_pct": "-0.4"}, "dxy": {"change_pct": 0.3},
                                                                    "krx_night_futures": {"status": "ok", "direction_pressure": "down"}}}})
    assert inputs["kospi_pct"] == -0.4 and inputs["dxy_pct"] == 0.3 and inputs["breadth"] == 0.0
    assert (inputs["krx_night_futures_status"], inputs["krx_night_futures_pressure"]) == ("ok", "down")
    md = rail.render_market_regime_rail_markdown(rail.classify_market_regime_rail(snapshot()), day="2026-07-01")
    assert md.startswith("# Market Regime Rail Review (2026-07-01)") and "## Q8 Review Focus" in md
    generated = rail.generate_market_regime_rail_review(reports_root=tmp_path / "reports", day="2026-07-01")
    assert generated["rail_id"] == "not_available" and Path(generated["report_json_path"]).is_relative_to(tmp_path)


def test_a85_helper_is_pure() -> None:
    source = Path(sp.__file__).read_text(encoding="utf-8")
    imports = [line for line in source.splitlines() if line.startswith(("import ", "from "))]
    assert all(line.split()[1] in {"__future__", "collections", "typing"} for line in imports), imports
    for banned in ("open(", "write_text", "read_text", "read_json", "os.environ", "subprocess", "now(", "Path("):
        assert banned not in source, banned


# --- A9: holding / execution evidence correctness and fallback provenance -----------------------------


def _hold_file(tdir: Path, payload: Any) -> None:
    _write(tdir / "hold.json", payload)


def _snapshot_tree(root: Path) -> Dict[str, bytes]:
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


def test_a9_absent_versus_present_but_empty_snapshot(tmp_path: Path) -> None:
    root = tmp_path / "reports"
    absent = recovery.read_trade_diagnostic_row(trade(root, "T1", {"status": "closed"}))
    empty = recovery.read_trade_diagnostic_row(trade(root, "T2", {"status": "closed", "monitor_context_snapshots": [],
                                                                  "entry": {"monitor_context": {}}, "exit": {"monitor_context": None}}))
    junk = recovery.read_trade_diagnostic_row(trade(root, "T3", {"status": "closed", "monitor_context_snapshots": ["x", 3, None]}))
    for row in (absent, empty, junk):
        assert row["monitor_context_snapshots_count"] == 0 and row["monitor_context_source"] == ""
        assert row["holding_summary_source"] == "" and row["holding_phase_summary"] == "" and row["holding_evidence_thin"] is True


def test_a9_confirmed_hold_precedence_over_entry_exit_context(tmp_path: Path) -> None:
    root = tmp_path / "reports"
    bundle = {"status": "closed", "monitor_context_snapshots": [{"a": 1}], "hold_events_count": 4, "holding_phase_summary": " recorded ",
              "hold_duration": "5m", "hold_duration_sec": 300, "exit": {"monitor_context": {"b": 2}}}
    row = recovery.read_trade_diagnostic_row(trade(root, "T1", bundle))
    assert (row["monitor_context_source"], row["holding_summary_source"]) == ("bundle", "bundle")
    assert row["holding_phase_summary"] == "recorded" and row["hold_events_count"] == 4 and row["holding_evidence_thin"] is False
    assert (row["hold_duration"], row["hold_duration_sec"]) == ("5m", 300)
    tdir = trade(root, "T2", {"status": "closed", "exit": {"monitor_context": {"b": 2}}})
    _hold_file(tdir, {"summary": "from hold file", "holding_events": [{"monitor_reason": "r1", "monitor_context": {"c": 3}}], "hold_duration_sec": 90})
    row2 = recovery.read_trade_diagnostic_row(tdir)
    assert (row2["monitor_context_source"], row2["holding_summary_source"]) == ("hold_payload", "hold_payload_summary")
    assert row2["holding_phase_summary"] == "from hold file" and row2["hold_events_count"] == 1 and row2["hold_duration_sec"] == 90
    tdir3 = trade(root, "T3", {"status": "closed"})
    _hold_file(tdir3, {"holding_events": [{"monitor_reason": "a"}, {"exit_reason": "a"}, {"monitor_reason": "b"}, "bad"]})
    row3 = recovery.read_trade_diagnostic_row(tdir3)
    assert row3["holding_summary_source"] == "hold_events_derived" and row3["hold_events_count"] == 4
    assert row3["holding_phase_summary"] == "Holding observed across 4 monitor updates: a, b."


def test_a9_exit_only_and_entry_only_context_prefers_exit(tmp_path: Path) -> None:
    root = tmp_path / "reports"
    both = recovery._resolve_holding_evidence({"exit": {"monitor_context": {"side": "exit"}}, "entry": {"monitor_context": {"side": "entry"}}},
                                              trade(root, "T1", {}))
    assert both["monitor_context_snapshots"] == [{"side": "exit"}]
    entry_only = recovery._resolve_holding_evidence({"entry": {"monitor_context": {"side": "entry"}}}, trade(root, "T2", {}))
    assert entry_only["monitor_context_snapshots"] == [{"side": "entry"}] and entry_only["monitor_context_source"] == "entry_exit_context"
    with_events = recovery._resolve_holding_evidence({"exit": {"monitor_context": {"x": 1}}, "timeline": [{"event": "Holding"}, {"event": "exit"}]},
                                                     trade(root, "T3", {}))
    assert with_events["hold_events_count"] == 1 and with_events["holding_summary_source"] == "hold_events_derived"
    assert with_events["holding_phase_summary"] == "Holding observed across 1 monitor updates."


@pytest.mark.parametrize("bundle", [
    {"status": "closed", "hold_events_count": "many", "timeline": "oops", "monitor_context_snapshots": "oops"},
    {"status": "closed", "exit": "SELL", "entry": ["x"], "trade_outcome": "bad", "execution": "bad", "story_contract": 7},
    {"status": "closed", "exit_execution_details": "x", "entry_execution_details": [1], "monitor_snapshot": "x"},
    {"status": "closed", "hold_events_count": 2.7, "execution_details": "not-a-dict", "same_day_reporter_linkage": "bad"},
])
def test_a9_malformed_evidence_degrades_instead_of_aborting(tmp_path: Path, bundle: Dict[str, Any]) -> None:
    root = tmp_path / "reports"
    tdir = trade(root, "T1", bundle)
    _hold_file(tdir, {"holding_events": "oops", "summary": ["x"]})
    row = recovery.read_trade_diagnostic_row(tdir)
    assert row["closed_trade"] is True
    # 2.7 is read as int(2.7) == 2 recorded hold events, exactly as before; every other case has no usable hold evidence.
    assert row["hold_events_count"] == (2 if bundle.get("hold_events_count") == 2.7 else 0)
    assert row["holding_evidence_thin"] is (bundle.get("hold_events_count") != 2.7)
    assert row["execution_missing_fields_count"] == 6  # nothing invented for the required execution fields
    assert recovery.audit_profitability_recovery_day(root, "2026-07-01")["trade_count"] == 1


def test_a9_execution_details_precedence_and_no_invented_values(tmp_path: Path) -> None:
    root = tmp_path / "reports"
    explicit = recovery._resolve_execution_details({"execution_details": FULL_EXECUTION, "execution": {"qty": 9}}, trade(root, "T1", {}))
    assert explicit == FULL_EXECUTION
    from_ctx = recovery._resolve_execution_details({"exit_execution_details": {"order_id": "E1", "avg_price": 7}}, trade(root, "T2", {}))
    assert from_ctx["order_id"] == "E1" and from_ctx["avg_price"] == 7 and from_ctx["order_status"] is None
    from_exit = recovery._resolve_execution_details({"exit": {"price": "12.5"}, "execution": {"qty": 3, "action": "SELL"}}, trade(root, "T3", {}))
    assert from_exit["avg_price"] == 12.5 and from_exit["order_status"] == "filled" and from_exit["filled_qty"] == 3
    assert from_exit["order_id"] is None and from_exit["execution_mode"] is None and from_exit["broker_env"] is None
    bare = recovery._resolve_execution_details({}, trade(root, "T4", {}))
    assert all(value is None for value in bare.values())


def test_a9_diagnosis_is_read_only(tmp_path: Path) -> None:
    root = tmp_path / "reports"
    tdir = trade(root, "T1", {"status": "closed", "exit": {"monitor_context": {"k": 1}}})
    _hold_file(tdir, {"holding_events": []})
    before = _snapshot_tree(tmp_path)
    recovery.read_trade_diagnostic_row(tdir)
    recovery.audit_profitability_recovery_day(root, "2026-07-01")
    recovery.build_daily_profitability_scorecard(root, "2026-07-01")
    assert _snapshot_tree(tmp_path) == before


def test_a9_error_paths_missing_and_corrupt_artifacts(tmp_path: Path) -> None:
    root = tmp_path / "reports"
    tdir = root / "trades" / "2026-07-01" / "RUN" / "TBAD"
    tdir.mkdir(parents=True)
    (tdir / "lifecycle_bundle.json").write_text("{not json", encoding="utf-8")
    (tdir / "hold.json").write_text("[1, 2]", encoding="utf-8")
    row = recovery.read_trade_diagnostic_row(tdir)
    assert row["trade_id"] == "TBAD" and row["closed_trade"] is False and row["holding_evidence_thin"] is True
    assert row["monitor_context_source"] == "" and row["execution_missing_fields_count"] == 6
    assert recovery.read_trade_diagnostic_row(tmp_path / "does_not_exist")["trade_id"] == "does_not_exist"


def test_a9_malformed_summary_and_duration_read_as_absent_not_stringified(tmp_path: Path) -> None:
    root = tmp_path / "reports"
    tdir = trade(root, "T1", {"status": "closed", "holding_phase_summary": ["x"], "hold_duration": {"a": 1},
                              "trade_outcome": {"holding_time": ["5m"]}})
    _hold_file(tdir, {"summary": {"k": "v"}, "holding_events": []})
    evidence = recovery._resolve_holding_evidence(
        {"holding_phase_summary": ["x"], "hold_duration": {"a": 1}, "trade_outcome": {"holding_time": ["5m"]}}, tdir)
    assert evidence["holding_phase_summary"] == "" and evidence["holding_summary_source"] == ""
    assert evidence["hold_duration"] == ""
    row = recovery.read_trade_diagnostic_row(tdir)
    assert row["holding_phase_summary"] == "" and row["hold_duration"] == "" and row["holding_evidence_thin"] is True
    # a malformed bundle summary must not outrank a valid recorded hold-file summary
    tdir2 = trade(root, "T2", {"status": "closed", "holding_phase_summary": 7})
    _hold_file(tdir2, {"summary": "recorded in hold file"})
    row2 = recovery.read_trade_diagnostic_row(tdir2)
    assert row2["holding_phase_summary"] == "recorded in hold file" and row2["holding_summary_source"] == "hold_payload_summary"
    # numeric durations that used to read fine keep reading fine
    assert recovery._resolve_holding_evidence({"hold_duration": 90}, tdir2)["hold_duration"] == "90"


def test_a9_malformed_exit_context_does_not_block_valid_entry_context(tmp_path: Path) -> None:
    root = tmp_path / "reports"
    for bad in ("garbage", ["x"], 5, {}, None):
        evidence = recovery._resolve_holding_evidence(
            {"exit": {"monitor_context": bad}, "entry": {"monitor_context": {"side": "entry"}}}, trade(root, "T%s" % abs(hash(str(bad))), {}))
        assert evidence["monitor_context_snapshots"] == [{"side": "entry"}], bad
        assert evidence["monitor_context_source"] == "entry_exit_context"
    both_bad = recovery._resolve_holding_evidence({"exit": {"monitor_context": "x"}, "entry": {"monitor_context": ["y"]}}, trade(root, "TB", {}))
    assert both_bad["monitor_context_snapshots"] == [] and both_bad["monitor_context_source"] == "" and both_bad["holding_phase_summary"] == ""
