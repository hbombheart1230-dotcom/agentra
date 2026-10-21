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


def test_missing_monitor_context_fallback_keeps_documented_unbound_name_behavior(tmp_path: Path) -> None:
    # Preserved quirk: the recovery branch reads holding_phase_summary before it is assigned.
    root = tmp_path / "reports"
    tdir = trade(root, "T9", {"entry": {"monitor_context": {"k": 1}}})
    with pytest.raises(UnboundLocalError):
        recovery.read_trade_diagnostic_row(tdir)


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
