"""FAST08 A8.1 smoke tests: evidence inventory, day validity, trade evaluation and historical prior."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pytest

from libs.reporting.evaluation import fast08_evidence_inventory as ev
from libs.reporting.evaluation import historical_prior
from libs.reporting.evaluation.artifact_inventory import build_artifact_inventory, is_synthetic_evaluation_row
from libs.reporting.evaluation.day_validity import KST, build_q9_day_validity
from libs.reporting.evaluation.trade_evaluator import evaluate_trade

DAY = "2026-06-08"


def _write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def window(ts: str, *, decision: str = "D", symbol: str = "005930", full: bool = True, selected: str = "005930") -> Dict[str, Any]:
    row: Dict[str, Any] = {"decision_id": decision, "generated_at": ts, "scanner_control": {"top1_symbol": symbol}}
    if full:
        row["strategist_selection"] = {"selected_symbol": selected, "post_strategist_top10": [1]}
        row["commander_final"] = {"selected_symbol": selected}
        row["scanner_pre_strategist_universe"] = {"intrinsic_ranked_top20": [1]}
    return row


def build_reports(root: Path, *, closeout_ok: bool = False, windows: List[Dict[str, Any]] | None = None) -> Path:
    reports = root / "reports"
    daily = reports / "operator_summary" / "daily" / DAY
    rows = windows if windows is not None else [
        window("2026-06-08T00:05:00+00:00"),                       # 09:05 KST trusted
        window("2026-06-08T06:15:00+00:00", decision="D2"),        # 15:15 KST trusted, late session
        window("2026-06-08T07:00:00+00:00", decision="D3"),        # 16:00 KST post-session
        window("2026-06-08T01:00:00+00:00", decision="test_D4"),   # synthetic
        window("2026-06-08T02:00:00+00:00", decision="D5", full=False),
        window("2026-06-08T03:00:00+00:00", decision="D6", selected=""),
        {"decision_id": "no_scanner"},
    ]
    _write(daily / "q9_decision_windows.json", {"schema_version": ev.Q9_DECISION_SCHEMA, "windows": rows})
    _write(daily / "daily_summary.json", {"ok": True})
    if closeout_ok:
        _write(daily / "closeout_maintenance.json", {"ok": True, "trigger": "kiwoom_market_status_close",
                                                     "steps": {"account_snapshot": {"ok": True},
                                                               "closeout_residual_position_reconciliation": {"ok": True}}})
    shadow = root / "data" / "logs" / "quant_shadow_candidates" / DAY
    _write(shadow / "0900.json", {"generated_at": "2026-06-08T00:10:00+00:00", "q9_decision_candidates": [
        {"q9_decision_role": "P_SCANNER_PRE_STRATEGIST_UNIVERSE", "symbol": "005930"},
        {"q9_decision_role": "A_SCANNER_CONTROL", "symbol": "000660"}]})
    _write(shadow / "latest.json", {"generated_at": "x"})
    trade = reports / "trades" / DAY / "RUN" / "TRD1"
    _write(trade / "lifecycle_bundle.json", {"trade_id": "TRD1"})
    _write(trade / "entry.json", {"symbol": "005930"})
    return reports


def test_inventory_window_classification_and_coverage(tmp_path: Path) -> None:
    inventory = build_artifact_inventory(build_reports(tmp_path), DAY)
    q9 = inventory["daily_artifacts"]["q9_decision_windows"]
    assert (q9["window_count"], q9["scanner_selection_window_count"]) == (7, 4)
    assert (q9["synthetic_window_count"], q9["post_session_window_count"]) == (1, 1)
    assert (q9["complete_abc_window_count"], q9["missing_selected_candidate_count"]) == (3, 1)
    assert q9["first_scanner_window_kst"].startswith("2026-06-08T09:05")
    assert q9["full_session_coverage"] is True and q9["schema_match"] is True
    assert q9["pre_strategist_forward_candidate_count"] == 1 and q9["shadow_payload_count"] == 1
    assert q9["forward_observed_candidate_count"] == 0
    trade = inventory["trades"][0]
    assert trade["complete"] is False and "scanner_evidence" in trade["missing_required"]
    assert 0 < inventory["required_coverage"] < 1


def test_unreadable_windows_file_reads_as_no_windows(tmp_path: Path) -> None:
    reports = build_reports(tmp_path)
    path = reports / "operator_summary" / "daily" / DAY / "q9_decision_windows.json"
    path.write_text('{"windows": [ {"decision_id": "D", ', encoding="utf-8")
    q9 = build_artifact_inventory(reports, DAY)["daily_artifacts"]["q9_decision_windows"]
    assert q9["window_count"] == 0 and q9["first_scanner_window_kst"] == "" and q9["full_session_coverage"] is False


def test_post_close_account_override_needs_closeout_proof(tmp_path: Path) -> None:
    early_only = [window("2026-06-08T00:05:00+00:00")]
    no_proof = build_artifact_inventory(build_reports(tmp_path / "a", windows=early_only), DAY)
    with_proof = build_artifact_inventory(build_reports(tmp_path / "b", windows=early_only, closeout_ok=True), DAY)
    assert no_proof["daily_artifacts"]["q9_decision_windows"]["full_session_coverage"] is False
    q9 = with_proof["daily_artifacts"]["q9_decision_windows"]
    assert q9["full_session_coverage"] is True
    assert q9["session_coverage_source"] == "post_close_account_snapshot_override"


def test_forward_tally_keeps_pending_unavailable_invalid_distinct() -> None:
    rows = [
        {"shadow_forward_outcome": {"available": True}},
        {"shadow_forward_outcome": {"reason": "forward_window_pending", "checkpoints": {"+5m": {"status": "pending"}}}},
        {"shadow_forward_outcome": {"reason": "minute_rows_unavailable"}},
        {"shadow_forward_outcome": {"reason": "stale_baseline", "checkpoints": {"+5m": {"status": "invalid"}}}},
        {},
    ]
    tally = ev.forward_outcome_tally(rows)
    assert (tally["observed"], tally["pending"], tally["unavailable"], tally["invalid"]) == (1, 2, 1, 1)
    assert tally["signature_counts"]["NO_CHECKPOINT_STATUS"] == 2
    assert is_synthetic_evaluation_row({"decision_id": "ok", "symbol": "AAPL"}) is True


@pytest.mark.parametrize(
    "now,expected",
    [(datetime(2026, 6, 7, 12, tzinfo=KST), "PREOPEN"), (datetime(2026, 6, 8, 12, tzinfo=KST), "IN_PROGRESS"),
     (datetime(2026, 6, 9, 12, tzinfo=KST), "INVALID")],
)
def test_day_validity_status_and_checks(tmp_path: Path, now: datetime, expected: str) -> None:
    inventory = build_artifact_inventory(build_reports(tmp_path), DAY)
    result = build_q9_day_validity(day=DAY, inventory=inventory, now=now)
    assert result["status"] == expected
    assert result["checks"]["synthetic_window_count"] == 1
    if expected == "INVALID":
        codes = {row["code"] for row in result["blockers"]}
        assert {"insufficient_complete_pabc_windows", "missing_selected_candidate"} <= codes
    assert build_q9_day_validity(day=DAY, inventory={}, now=now)["checks"]["artifact_exists"] is False


def test_trade_evaluation_exit_quality_and_labels() -> None:
    model = {"trade_id": "T", "integrity": {"status": "PASS"}, "outcome": {"net_return_pct": -0.4, "holding_seconds": 30},
             "exit": {"reason": "take_profit"}, "entry": {"reason": "breakout"},
             "monitor": {"post_exit": {"best_exit_offset": "+5m", "checkpoints": {
                 "+5m": {"status": "observed", "return_pct": 0.01}, "+15m": {"status": "pending"}}}}}
    result = evaluate_trade(model)
    assert result["realized_outcome"]["result_label"] == "loss"
    assert {"sub_60_second_exit", "exit_reason_outcome_conflict"} <= set(result["integrity"]["watch_items"])
    assert result["exit_quality"]["status"] == "observed" and list(result["exit_quality"]["observed_checkpoints"]) == ["+5m"]
    assert evaluate_trade({})["realized_outcome"]["result_label"] == "unavailable"
    assert evaluate_trade({})["exit_quality"]["post_exit_comparison"] == "unavailable"


def test_historical_prior_summary_and_render() -> None:
    evaluations = [
        {"day": "2026-06-01", "integrity": {"status": "PASS", "promotion_metric_eligible": True, "watch_items": ["w"]},
         "realized_outcome": {"net_return_pct": 1.0}, "horizon_alignment": {"bucket": "intraday"}},
        {"day": "2026-06-02", "integrity": {"status": "FAIL", "defects": ["d"]}, "realized_outcome": {"net_return_pct": None}},
    ]
    models = [{"symbol": "005930", "selection": {"selected_rank": 2, "strategist_playbook": "pb"}}, {"symbol": "000660"}]
    summary = historical_prior.summarize_historical_prior(
        models=models, evaluations=evaluations, attributions=[{"deltas": {"strategist_delta_pct": 0.1}}, {}],
        errors=[], from_day="", before_day="2026-06-29")
    assert summary["coverage"]["eligible_trade_count"] == 1 and summary["coverage"]["source_day_count"] == 2
    assert list(summary["breakdowns"]["selected_rank_bucket"]) == ["rank2-3"]
    assert summary["selection_attribution"] == {"comparison_count": 1, "unavailable_count": 1,
                                                "note": summary["selection_attribution"]["note"]}
    md = historical_prior.render_historical_prior_markdown(summary)
    assert "- rank2-3: count 1" in md and "Official Q9 freeze sample: **False**" in md


def test_a81_helper_is_pure() -> None:
    source = Path(ev.__file__).read_text(encoding="utf-8")
    imports = [line for line in source.splitlines() if line.startswith(("import ", "from "))]
    assert all(line.split()[1] in {"__future__", "re", "collections", "datetime", "typing", "zoneinfo", ".metrics"} for line in imports), imports
    for banned in ("open(", "write_text", "read_text", "read_json", "os.environ", "subprocess", ".now("):
        assert banned not in source, banned
