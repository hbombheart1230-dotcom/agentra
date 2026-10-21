"""FAST07 A7.1 smoke tests: Q9 evidence normalization, entry timing and horizon alignment."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pytest

from libs.reporting.evaluation import entry_timing_attribution as timing
from libs.reporting.evaluation import fast07_chain_render_projection as render
from libs.reporting.evaluation import fast07_trade_projection as proj
from libs.reporting.evaluation import horizon_alignment as horizon
from libs.reporting.evaluation.trade_read_model import build_q9_trade_read_model


def _write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def build_trade_dir(root: Path, kind: str) -> Path:
    """kind: realized | open | stale_order | missing."""
    trade_dir = root / "reports" / "trades" / "2026-06-08" / "RUN1" / f"TRD_{kind}"
    trade_dir.mkdir(parents=True, exist_ok=True)
    if kind == "missing":
        return trade_dir
    entry = {
        "timestamp": "2026-06-08T09:10:00+00:00",
        "filled_price": 1000,
        "qty": 3,
        "scanner_context": {"selected_symbol": "005930", "q9_decision_id": "D1", "raw_scanner_top10": [{"symbol": "000660"}]},
        "strategist_context": {"playbook": "breakout"},
    }
    exit_row: Dict[str, Any] = {}
    if kind == "realized":
        exit_row = {"timestamp": "2026-06-08T09:40:00+00:00", "action": "SELL", "price": 1010,
                    "execution_details": {"broker_realized_pnl_pct": 0.01, "broker_realized_pnl": 30}}
    if kind == "stale_order":
        exit_row = {"timestamp": "2026-06-08T09:00:00+00:00", "action": "SELL"}
    _write(trade_dir / "lifecycle_bundle.json", {"trade_id": f"TRD_{kind}", "day": "2026-06-08", "symbol": "005930",
                                                 "lifecycle": {"entry": entry, "exit": exit_row}})
    _write(trade_dir / "evidence" / "scanner_evidence.json", {"candidate_ranking_tables": [
        {"payload": {"rows": [{"symbol": "000660", "rank": 1, "pre_adjust_score_total": 2},
                              {"symbol": "005930", "rank": 2, "pre_adjust_score_total": 5}]}}]})
    _write(trade_dir / "evidence" / "monitor_evidence.json", {"state_transitions": [1, 2]})
    _write(root / "reports" / "operator_summary" / "daily" / "2026-06-08" / "q9_decision_windows.json",
           {"windows": [{"decision_id": "D1", "decision_epoch": 1780909500, "run_id": "RUN1"}]})
    return trade_dir


@pytest.mark.parametrize("kind", ["realized", "open", "stale_order", "missing"])
def test_trade_read_model_evidence_states(tmp_path: Path, kind: str) -> None:
    model = build_q9_trade_read_model(build_trade_dir(tmp_path, kind))
    integrity = model["integrity"]
    if kind == "realized":
        assert model["evidence_class"] == "REALIZED"
        assert model["outcome"]["net_return_pct"] == 1.0 and model["outcome"]["holding_seconds"] == 1800
        assert model["outcome"]["pnl_source"] == "exit.execution_details.broker_realized_pnl_pct"
        assert model["selection"]["q9_snapshot_source"] == "daily_q9_window.decision_id"
        assert model["selection"]["selected_rank"] == 2
        assert model["selection"]["reconstructed_pre_adjust_top10"][0]["symbol"] == "005930"
        assert model["monitor"]["state_transition_count"] == 2
    elif kind == "open":
        assert model["outcome"]["net_return_pct"] is None
        assert "trade_open_or_exit_missing" in integrity["watch_items"]
    elif kind == "stale_order":
        assert "exit_before_entry" in integrity["defects"] and integrity["status"] == "BLOCKER"
    else:
        assert "entry_missing" in integrity["defects"]
        assert model["outcome"]["net_return_pct"] is None and model["evidence_class"] == "UNAVAILABLE"


def test_normalizers_keep_unknown_and_missing_distinct() -> None:
    assert proj.parse_ts("unknown") is None and proj.parse_ts("") is None
    assert proj.epoch("not-a-date") == 0 and proj.iso(0) == ""
    assert proj.meaningful("unknown", "NaN", None, 0, "x") == "x"
    assert proj.holding_seconds("2026-06-08T10:00:00", "2026-06-08T09:00:00", None) is None
    assert proj.deep_value({"a": [{"qty": ""}, {"b": {"qty": 4}}]}, "qty") == 4


def _model(trade_id: str, *, ts: str, defects=(), horizon: str = "") -> Dict[str, Any]:
    return {
        "trade_id": trade_id,
        "symbol": "005930",
        "entry": {"timestamp": ts, "price": 101.0},
        "outcome": {"net_return_pct": 0.5},
        "selection": {"q9_decision_id": "D1", "selected_rank": 2, "raw_scanner_top1": {"symbol": "000660"}},
        "integrity": {"defects": list(defects)},
        "horizon_contract": {"strategy_horizon": horizon},
    }


def test_entry_timing_rows_exclusions_and_missing_stage(tmp_path: Path) -> None:
    _write(tmp_path / "operator_summary" / "daily" / "2026-06-08" / "q9_decision_windows.json",
           {"windows": [{"decision_id": "D1", "decision_epoch": 1780909200}]})
    minute_rows = {"005930": [{"ts": 1780909140, "close": 100.0}]}
    report = timing.build_entry_timing_attribution_report(
        day="2026-06-08",
        models=[_model("T1", ts="1780909500"), _model("T2", ts="1780909500", defects=["confirmed_runtime_defect"]),
                _model("T3", ts="1780909500", horizon="swing")],
        reports_root=tmp_path,
        minute_rows_by_symbol=minute_rows,
    )
    assert report["excluded_trade_count"] == 1 and report["trade_count"] == 2
    row = report["rows"][0]
    assert row["scanner_to_entry_delay_sec"] == 300 and row["pre_entry_move_pct"] == 1.0
    assert row["stage_timing_status"] == "PARTIAL"
    assert row["label"] == "INSUFFICIENT_EVIDENCE" and row["scanner_top1_symbol"] == "000660"
    assert report["rows"][1]["label_reasons"] == ["strategy_horizon_exceeds_entry_timing_observation_window"]
    assert [r["label"] for r in report["label_summary"]] == list(timing.LABELS)
    md = timing.render_entry_timing_attribution_report(report)
    assert md.startswith("# Q13 Entry Timing Attribution - 2026-06-08") and md.endswith("\n")


def test_entry_timing_without_windows_or_minutes(tmp_path: Path) -> None:
    report = timing.build_entry_timing_attribution_report(
        day="2026-06-09", models=[_model("T1", ts="")], reports_root=tmp_path, minute_rows_by_symbol={}
    )
    row = report["rows"][0]
    assert row["decision_anchor_time"] == "" and row["scanner_to_entry_delay_sec"] is None
    assert row["pre_entry_move_meta"]["reason"] == "missing_symbol_time_or_entry_price"
    assert row["entry_forward_quality"]["forward_available"] is False


def _candidate(day: str, symbol: str, ret: float) -> Dict[str, Any]:
    return {"symbol": symbol, "generated_at": f"{day}T09:30:00+09:00", "quant_tactic_id": "t1",
            "entry_lane_observation": {"time_bucket": "open"},
            "shadow_forward_outcome": {"checkpoints": {"+5m": {"status": "observed", "return_pct": ret}}}}


def test_horizon_combo_thresholds_stay_in_facade() -> None:
    candidates = [_candidate(f"2026-06-0{d}", f"S{i}", 1.5) for d in range(1, 6) for i in range(5)]
    rows = horizon._combo_rows(candidates, dimensions=("time_bucket", "tactic"), cost_pct=0.2)
    assert rows[0]["decision"] == "CONTROLLED_ADOPTION_CANDIDATE" and rows[0]["observed_count"] == 25
    thin = horizon._combo_rows(candidates[:3], dimensions=("time_bucket",), cost_pct=0.2)
    assert thin[0]["decision"] == "INSUFFICIENT_EVIDENCE" and thin[0]["evidence_eligible"] is False
    md = render.render_horizon_alignment_review({"range": {}, "cost_model": {}, "time_tactic": rows[:1]})
    assert "| open | t1 | +5m |" in md and "behavior change authorized: **False**" in md


def test_a71_owners_are_pure() -> None:
    allowed = {"__future__", "array", "bisect", "collections", "datetime", "json", "typing", ".contracts", ".metrics"}
    for module in (proj, render):
        source = Path(module.__file__).read_text(encoding="utf-8")
        imports = [line for line in source.splitlines() if line.startswith(("import ", "from "))]
        assert all(line.split()[1] in allowed for line in imports), imports
        for banned in ("open(", "write_text", "read_text", "read_json", "os.environ", "subprocess", "now("):
            assert banned not in source, (module.__name__, banned)
