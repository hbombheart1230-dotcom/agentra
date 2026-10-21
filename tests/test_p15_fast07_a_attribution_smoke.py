"""FAST07 A7.2 smoke tests: loss decomposition, no-trade attribution and evaluation lens."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import pytest

from libs.reporting.evaluation import evaluation_lens_report as lens
from libs.reporting.evaluation import fast07_attribution_projection as attr
from libs.reporting.evaluation import loss_decomposition as loss
from libs.reporting.evaluation import no_trade_attribution as no_trade


def _write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _cp(ret: float | None, mfe: float | None = None, mae: float | None = None) -> Dict[str, Any]:
    if ret is None:
        return {"status": "pending"}
    return {"status": "observed", "return_pct": ret, "mfe_pct": mfe, "mae_pct": mae}


def candidate(symbol: str, *, rank: Any, role: str, ret5: float | None, epoch: int = 1780909200, **extra: Any) -> Dict[str, Any]:
    return {
        "symbol": symbol,
        "rank": rank,
        "shadow_role": role,
        "quant_tactic_id": "t1",
        "generated_at": "2026-06-08T09:00:00+09:00",
        "shadow_forward_base": {"baseline_epoch": epoch, "baseline_price": 100.0},
        "shadow_forward_outcome": {"checkpoints": {"+5m": _cp(ret5, 0.9, -0.2), "+15m": _cp(None), "EOD": _cp(ret5)}},
        **extra,
    }


def trade_model(trade_id: str, *, ret: float | None, entry_price: float = 100.5, post5: float | None = None) -> Dict[str, Any]:
    return {
        "trade_id": trade_id,
        "symbol": "005930",
        "day": "2026-06-08",
        "entry": {"timestamp": "2026-06-08T00:05:00+00:00", "price": entry_price},
        "outcome": {"net_return_pct": ret},
        "selection": {"selected_rank": 2, "selected_symbol": "005930", "scanner_top1": {"symbol": "000660"}},
        "monitor": {"post_exit": {"checkpoints": {"+5m": _cp(post5)}} if post5 is not None else {}},
        "exit": {"reason": "stop"},
    }


def test_loss_decomposition_end_to_end(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    payloads = [{"generated_at": "g", "candidates": [
        candidate("005930", rank=1, role="top_pick", ret5=0.4, epoch=1780876800),
        candidate("000660", rank="7", role="runner_up", ret5=-0.2),
        candidate("035720", rank=None, role="", ret5=None),
        "junk",
    ]}]
    monkeypatch.setattr(loss, "load_quant_shadow_candidate_payloads_for_range", lambda **_: payloads)
    monkeypatch.setattr(loss, "build_quant_shadow_candidate_evaluation", lambda p: {
        "candidate_count": 3, "entry_lane_forward_outcomes": {"by_time_bucket": [
            {"name": "open_20_60m", "observed_days": ["2026-06-08"], "avg_return_30m_pct": 0.2}]}})
    monkeypatch.setattr(loss, "attach_forward_outcomes", lambda rows: rows)
    monkeypatch.setattr(loss, "dedupe_q8_candidates", lambda rows: list(rows))
    monkeypatch.setattr(loss, "_load_trade_models", lambda *_: [
        trade_model("T1", ret=-1.0, post5=0.002), trade_model("T2", ret=None), trade_model("T3", ret=0.5, entry_price=0)])
    payload = loss.build_loss_decomposition(reports_root=tmp_path, start="2026-06-08", end="2026-06-08")
    ranks = {row["name"]: row for row in payload["scanner_ranking"]["by_rank_bucket"]}
    assert set(ranks) == {"rank1", "rank6-10", "unknown"}
    assert ranks["unknown"]["observed_count"] == 0 and ranks["unknown"]["avg_return_5m_pct"] is None
    realized = payload["realized_system"]
    assert realized["comparable_trade_count"] == 2 and realized["scanner_top1_execution_mismatch_count"] == 2
    assert payload["monitor_entry"]["matched_trade_count"] == 2  # T2 has no return but a valid entry price
    assert payload["monitor_entry"]["late_entry_count"] == 2
    assert payload["monitor_exit"]["by_hold_offset"][0]["average_improvement_pct"] == 0.2
    assert payload["evidence"]["trusted_forward_observed_days"] == ["2026-06-08"]
    assert payload["next_action"]["behavior_change_authorized"] is False
    assert payload["strategist_commander"]["status"] == "UNAVAILABLE"
    md = loss.render_loss_decomposition(payload)
    assert "| rank1 | 1 | 0.4 | None | None | None |" in md and "behavior change authorized: **False**" in md


def test_missing_forward_never_counts_as_gain() -> None:
    rows = [candidate("A", rank=1, role="r", ret5=None), candidate("B", rank=1, role="r", ret5=None)]
    grouped = attr.group_forward(rows, lambda row: row.get("shadow_role"))
    assert grouped[0]["observed_count"] == 0 and grouped[0]["coverage"] == 0.0
    assert all(grouped[0][f"avg_return_{h}m_pct"] is None for h in (5, 15, 30, 60))
    assert attr.exit_hold_summary([trade_model("T", ret=1.0)])["observed_trade_count"] == 0


def _windows(root: Path, rows: List[Dict[str, Any]]) -> None:
    _write(root / "operator_summary" / "daily" / "2026-06-08" / "q9_decision_windows.json", {"windows": rows})


def _window(decision: str, intent: str, reason: str = "") -> Dict[str, Any]:
    return {"generated_at": "2026-06-08T01:00:00+00:00",
            "scanner_control": {"top1_symbol": "005930"},
            "commander_final": {"decision": decision, "monitor_intent": intent, "selected_symbol": "005930",
                                "monitor_observation": {"reason": reason}}}


@pytest.mark.parametrize(
    "windows,q11,expected",
    [
        ([], None, "MISSING_Q9_EVIDENCE"),
        ([_window("approve", "NOOP", "spread")], {"trade_count": 2, "summary": {"average_net_return_pct": 0.4}}, "POSSIBLE_OVER_FILTERING"),
        ([_window("approve", "NOOP", "spread")], {"trade_count": 2, "summary": {"average_net_return_pct": None}}, "FILTERING_REVIEW_REQUIRED"),
        ([_window("reject", "")], None, "UPSTREAM_REJECTED"),
        ([_window("hold", "")], None, "NO_ACTIONABLE_CANDIDATE"),
    ],
)
def test_no_trade_classification_unchanged(tmp_path: Path, windows, q11, expected) -> None:
    _windows(tmp_path, windows)
    if q11 is not None:
        _write(tmp_path / "evaluation" / "opportunity_engine_shadow" / "2026-06-08" / "opportunity_engine_virtual_trades.json", q11)
    report = no_trade.build_no_trade_attribution_report(day="2026-06-08", reports_root=tmp_path, trade_count=0)
    assert report["no_trade_class"] == expected
    if windows and windows[0]["commander_final"]["monitor_intent"] == "NOOP":
        assert report["monitor_noop_reasons"] == [{"name": "spread", "count": 1}]
    md = no_trade.render_no_trade_attribution_report(report)
    assert "| Q10 Samsung/Hynix | - | 0 | - | - | - |" in md


def test_no_trade_on_trading_day_and_unreadable_windows(tmp_path: Path) -> None:
    path = tmp_path / "operator_summary" / "daily" / "2026-06-08" / "q9_decision_windows.json"
    path.parent.mkdir(parents=True)
    path.write_text("{not json", encoding="utf-8")
    report = no_trade.build_no_trade_attribution_report(day="2026-06-08", reports_root=tmp_path, trade_count=3)
    assert report["no_trade_class"] == "NOT_NO_TRADE_DAY" and report["q9_window_count"] == 0
    assert report["shadow_opportunity_status"] == "UNAVAILABLE"


def _q9_row(decision_id: str, role: str, rank: int, ret: float | None, selected: bool = False) -> Dict[str, Any]:
    row = candidate("S", rank=rank, role="", ret5=ret, q9_decision_id=decision_id, q9_decision_role=role)
    if selected:
        row["q9_selected"] = True
    return row


def test_lens_streaming_accumulators_match_batch_reviews() -> None:
    rows = [
        candidate("A", rank=1, role="r", ret5=1.2, reason="breakout_not_ready",
                  entry_lane_observation={"market_regime_rail": "risk_on"}),
        candidate("B", rank=2, role="r", ret5=-0.3, guard_reason="human_chart_sanity_guard_blocked"),
        candidate("C", rank=3, role="r", ret5=None, entry_quant_decision={"blockers": ["other"]}),
    ]
    acc = attr.BlockerReviewAccumulator(0.5, day_of=lambda row: "2026-06-08")
    acc.add_rows(rows)
    assert acc.result() == attr.blocker_forward_review(rows, cost_floor_pct=0.5, day_of=lambda row: "2026-06-08")
    q9 = [_q9_row("D1", "A_SCANNER_CONTROL", 2, 0.1), _q9_row("D1", "A_SCANNER_CONTROL", 1, 0.2),
          _q9_row("D1", "B_STRATEGIST_RANKED", 1, 0.5), _q9_row("D1", "B_STRATEGIST_RANKED", 3, 0.9, selected=True),
          _q9_row("D1", "C_COMMANDER_FINAL", 1, None), _q9_row("D2", "P_SCANNER_PRE_STRATEGIST_UNIVERSE", 1, 0.3)]
    delta = attr.StrategistDeltaAccumulator()
    delta.add_rows(q9)
    batch = attr.strategist_delta_review(q9)
    assert delta.result() == batch
    first = batch["deltas_by_horizon"][0]["strategist_minus_scanner_control"]
    assert first["count"] == 1 and round(first["average_return_pct"], 4) == 0.7
    assert batch["deltas_by_horizon"][0]["commander_minus_strategist"]["count"] == 0


def test_lens_report_build_and_render(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(lens, "_cost_floor_pct", lambda: 0.5)
    monkeypatch.setattr(lens, "load_quant_shadow_candidate_payloads_for_range", lambda **_: [
        {"generated_at": "g", "candidates": [candidate("A", rank=1, role="r", ret5=0.7, reason="pullback_not_mature")],
         "q9_decision_candidates": [_q9_row("D1", "A_SCANNER_CONTROL", 1, 0.1), _q9_row("D1", "B_STRATEGIST_RANKED", 1, 0.4)]}])
    monkeypatch.setattr(lens, "attach_forward_outcomes", lambda rows: rows)
    monkeypatch.setattr(lens, "_trade_models", lambda *_: [trade_model("T1", ret=-0.5, post5=0.001)])
    payload = lens.build_evaluation_lens_report(reports_root=tmp_path, start="2026-06-08", end="2026-06-09")
    assert payload["evidence"] == {"shadow_payload_count": 2, "candidate_count": 2, "q9_candidate_count": 4, "trade_model_count": 1}
    assert payload["blocker_forward_review"]["focused_candidate_count"] == 2
    assert payload["exit_hold_counterfactual_review"]["by_exit_reason"][0]["exit_reason"] == "stop"
    assert payload["behavior_change_authorized"] is False
    md = lens.render_evaluation_lens_report(payload)
    assert md.startswith("# ") and "pullback_not_mature" in md


def test_a72_owner_is_pure() -> None:
    source = Path(attr.__file__).read_text(encoding="utf-8")
    imports = [line for line in source.splitlines() if line.startswith(("import ", "from "))]
    assert all(line.split()[1] in {"__future__", "array", "collections", "typing", ".metrics"} for line in imports), imports
    for banned in ("open(", "write_text", "read_text", "read_json", "os.environ", "subprocess", "now("):
        assert banned not in source, banned
