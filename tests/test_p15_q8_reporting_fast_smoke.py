"""FAST06 smoke tests for the Q8 evaluation-and-review report projections."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import pytest

from libs.reporting import q8_historical_projection_fast06 as proj
from libs.reporting import q8_historical_review as hist
from libs.reporting import q8_lane_decision_table as lane
from libs.reporting import q8_review_render_fast06 as render
from libs.reporting import q8_shadow_blocker_review as blocker
from libs.reporting import q8_trusted_reaggregation as reagg


def _write(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def build_reports_root(root: Path, *, allowed: bool) -> Path:
    reports = root / "reports"
    daily = reports / "operator_summary" / "daily"
    _write(
        daily / "2026-06-08" / "daily_summary.json",
        {
            "metrics": {"trade_count": "3", "closed_trade_count": 2, "win_rate": "0.5", "avg_return_pct": "-0.4"},
            "quant_shadow_candidate_evaluation": {
                "candidate_count": 7,
                "evaluation_trust_gate": {"status": "trusted" if allowed else "blocked", "promotion_allowed": allowed},
                "by_reason": [{"name": "breakout_not_ready", "count": 4}, {"name": "unknown", "count": 9}],
                "by_role": [{"name": "leader", "count": 2}],
                "below_vwap_reclaim_observation": {"by_subtype": [{"name": "deep", "count": 3}]},
                "entry_lane_forward_outcomes": {
                    "by_lane_subtype": [
                        {"name": "vwap_reclaim:deep", "candidate_count": 40, "observed_count": 35,
                         "observed_count_5m": 35, "observed_count_15m": 35, "avg_return_5m_pct": 0.3, "avg_return_15m_pct": 0.2,
                         "avg_mae_5m_pct": -0.1},
                        {"name": "breakout:x", "candidate_count": 1},
                    ]
                },
            },
            "q8_shadow_blocker_review": {
                "groups": [
                    {"reason": "breakout_not_ready", "candidate_count": 4, "observed_count": 2,
                     "avg_latest_return_pct": 1.5, "decision": "adjust_and_retest"},
                    {"reason": "below_vwap_reclaim_not_ready", "count": 3, "observed_count": 1},
                ]
            },
            "pattern_performance": {
                "strategist": {"by_tactical_strategy": [
                    {"name": "defensive_observe", "count": 6, "win_count": 1, "avg_return_pct": -0.8},
                ]},
            },
        },
    )
    _write(daily / "2026-06-09" / "daily_summary.json", {"metrics": {}, "market_regime_rail_review": {"rail_id": "risk_off"}})
    trade = reports / "trades" / "2026-06-08" / "T1" / "reports" / "ai_trade_summary.json"
    _write(trade, {"trade": {"symbol": "005930"}, "truth_surface": {"pnl_pct": "0.012", "truth_source": "broker"},
                   "decision_flow": {"entry_reason": "breakout", "exit_reason": "stop"}})
    _write(reports / "trades" / "2026-07-01" / "T9" / "reports" / "ai_trade_summary.json", {"trade": {}})
    return reports


@pytest.mark.parametrize("allowed", [False, True])
def test_historical_payload_gate_and_projection(tmp_path: Path, allowed: bool) -> None:
    reports = build_reports_root(tmp_path, allowed=allowed)
    payload = hist.build_q8_historical_review_payload(reports_root=reports, start="2026-06-08", end="2026-06-10")
    assert payload["behavior_effect"] == "evaluation_only"
    assert [row["day"] for row in payload["daily_rows"]] == ["2026-06-08", "2026-06-09"]
    assert payload["daily_rows"][1]["market_regime_rail"] == "risk_off"
    assert payload["trade_summary"]["trade_report_count"] == 1
    assert payload["trade_summary"]["avg_return_pct"] == 1.2
    assert payload["by_reason"] == [{"name": "breakout_not_ready", "count": 4}]
    assert payload["below_vwap_reclaim_subtype_forward"][0]["decision"] == "adjust_and_retest_candidate"
    assert [g["reason"] for g in payload["q8_blocker_groups"]] == ["breakout_not_ready", "below_vwap_reclaim_not_ready"]
    recs = payload["promotion_recommendations"]
    if allowed:
        assert recs[0]["candidate"] == "risk_off_defensive_observe_no_entry_policy"
        assert recs[-1]["decision"] == "do_not_relax_globally"
    else:
        assert recs == [{"candidate": "all_q8_candidates", "decision": "retain_under_observation",
                         "reason": "no historical day passed the Q8 evaluation trust gate"}]


def test_historical_empty_window_and_writes_stay_in_sandbox(tmp_path: Path) -> None:
    reports = tmp_path / "reports"
    out = hist.write_q8_historical_review(reports_root=reports, docs_root=tmp_path / "docs", start="2026-01-01", end="2026-01-02")
    assert out["payload"]["daily_count"] == 0
    assert out["payload"]["trade_by_tactic"] == []
    assert Path(out["md_path"]).is_relative_to(tmp_path) and Path(out["json_path"]).is_relative_to(tmp_path)
    text = Path(out["md_path"]).read_text(encoding="utf-8-sig")
    assert text.startswith("# Q8 Historical Review: 2026-01-01 to 2026-01-02")


def _candidate(symbol: str, reason: str, ret: float | None) -> Dict[str, Any]:
    checkpoints = {} if ret is None else {"5m": {"status": "observed", "return_pct": ret, "mfe_pct": ret + 1, "mae_pct": ret - 1}}
    return {"symbol": symbol, "reason": reason, "shadow_forward_outcome": {"checkpoints": checkpoints}}


@pytest.mark.parametrize("allowed", [False, True])
def test_shadow_blocker_trust_gate_never_promotes_when_blocked(monkeypatch: pytest.MonkeyPatch, allowed: bool) -> None:
    monkeypatch.setattr(blocker, "attach_forward_outcomes", lambda rows, minute_rows_by_symbol=None: rows)
    monkeypatch.setattr(blocker, "dedupe_q8_candidates", lambda rows: list(rows))
    payloads = [{"candidates": [_candidate("A", "human_chart_sanity_guard_blocked", 0.4),
                                _candidate("B", "human_chart_sanity_guard_blocked", None), "junk"]}]
    review = blocker.build_q8_shadow_blocker_review(
        payloads, quant_shadow_evaluation={"evaluation_trust_gate": {"promotion_allowed": allowed}}
    )
    group = {g["reason"]: g for g in review["groups"]}["human_chart_sanity_guard_blocked"]
    assert (group["candidate_count"], group["observed_count"]) == (2, 1)
    assert group["raw_decision"] == "promotion_review_target"
    assert group["decision"] == ("promotion_review_target" if allowed else "retain_under_observation")
    assert [g["reason"] for g in review["groups"]] == list(blocker.DEFAULT_REVIEW_REASONS)
    md = blocker.render_q8_shadow_blocker_review_markdown(review, day="2026-06-08")
    assert "## Examples: human_chart_sanity_guard_blocked" in md and md.endswith("\n")


def test_trusted_reaggregation_keeps_missing_sources_distinct(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def fake_load(*, reports_root: Path, days: List[str]) -> List[Dict[str, Any]]:
        return [{"day": days[0]}] if days[0] == "2026-06-09" else []

    def fake_eval(payloads: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {"candidate_count": 5, "forward_outcome_available_count": 2,
                "evaluation_trust_gate": {"status": "blocked", "block_reasons": ["coverage_low"]},
                "no_trade_scorecard": {"promotion_watchlist": [{"name": "w", "avg_return_5m_pct": None}, "bad"]}}

    monkeypatch.setattr(reagg, "load_quant_shadow_candidate_payloads", fake_load)
    monkeypatch.setattr(reagg, "build_quant_shadow_candidate_evaluation", fake_eval)
    payload = reagg.build_q8_trusted_reaggregation(reports_root=tmp_path, start="2026-06-08", end="2026-06-10")
    assert payload["range"]["days_with_payloads"] == 1
    day = payload["daily"][0]
    assert (day["scorecard_status"], day["promotion_allowed"], day["trust_reasons"]) == ("not_available", False, ["coverage_low"])
    assert payload["aggregate"]["promotion_watchlist"] == [{"name": "w", "avg_return_5m_pct": None}]
    md = reagg.render_q8_trusted_reaggregation_markdown(payload)
    assert "| cumulative | `w` | 0/0 | 0 | - | - | - | `-` |" in md
    assert "trusted coverage >= " in md and "PROMOTE is not allowed" in md
    empty = reagg.render_q8_trusted_reaggregation_markdown({})
    assert "| - | - | 0/0 | 0 | - | - | - | no_watchlist |" in empty


def _lane_eval(allowed: bool) -> Dict[str, Any]:
    return {
        "candidate_count": 30,
        "evaluation_trust_gate": {"status": "ok", "promotion_allowed": allowed},
        "entry_lane_observation": {"by_primary_lane": [{"name": "breakout", "count": 99}]},
        "entry_lane_forward_outcomes": {"by_primary_lane": [
            {"name": "vwap_reclaim", "candidate_count": 20, "observed_count": 20, "coverage": 1.0,
             "avg_return_5m_pct": -0.2, "avg_return_15m_pct": -0.3},
            {"name": "breakout", "candidate_count": 15, "observed_count": 12, "coverage": 0.9,
             "avg_return_5m_pct": 0.7},
            {"name": "thin", "candidate_count": 3, "observed_count": 2, "coverage": 0.1},
        ]},
        "by_reason": [{"name": "breakout_not_ready", "count": 4}],
    }


@pytest.mark.parametrize("allowed", [False, True])
def test_lane_table_order_and_activation_refusal(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, allowed: bool) -> None:
    monkeypatch.setattr(lane, "load_quant_shadow_candidate_payloads", lambda **_: [])
    monkeypatch.setattr(lane, "build_quant_shadow_candidate_evaluation", lambda payloads: _lane_eval(allowed))
    payload = lane.build_q8_lane_decision_table(reports_root=tmp_path, day="2026-06-08T09:00")
    rows = payload["rows"]
    if allowed:
        assert [(r["lane"], r["verdict"]) for r in rows] == [
            ("breakout", "MISSED_OPPORTUNITY"), ("vwap_reclaim", "GOOD_BLOCK"), ("thin", "DATA_INCOMPLETE")]
        assert rows[0]["shadow_count"] == 99 and rows[1]["shadow_count"] == 20
    else:
        assert {r["verdict"] for r in rows} == {"TRUST_GATE_BLOCKED"}
        assert [r["lane"] for r in rows] == ["vwap_reclaim", "breakout", "thin"]
    md = lane.render_q8_lane_decision_table_markdown(payload)
    assert "No new behavior patch is implied by this table unless the Q8 trust gate allows promotion review." in md
    assert payload["day"] == "2026-06-08" and payload["reason_summary"] == "breakout_not_ready 4"


def test_projection_owners_are_pure() -> None:
    for module in (proj, render):
        source = Path(module.__file__).read_text(encoding="utf-8")
        imports = [line for line in source.splitlines() if line.startswith(("import ", "from "))]
        assert all(line.split()[1] in {"__future__", "collections", "dataclasses", "typing"} for line in imports), imports
        for banned in ("open(", "write_text", "read_text", "os.environ", "subprocess"):
            assert banned not in source, (module.__name__, banned)
