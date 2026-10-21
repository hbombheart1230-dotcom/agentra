"""FAST07 A7.3 smoke tests: full-chain component review, operator summary mining, agent scorecard."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import pytest

from libs.reporting.evaluation import agent_effectiveness_scorecard as scorecard
from libs.reporting.evaluation import fast07_attribution_projection as attr
from libs.reporting.evaluation import fast07_chain_render_projection as render
from libs.reporting.evaluation import full_chain_component_review as full_chain
from libs.reporting.evaluation import operator_summary_mining as mining


def _write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _obs(ret: float | None) -> Dict[str, Any]:
    if ret is None:
        return {"checkpoints": {}}
    return {"checkpoints": {h: {"status": "observed", "return_pct": ret} for h in ("+5m", "+15m", "+30m", "+60m")}}


def shadow_row(window: str, role: str, ret: float | None, day: str = "2026-06-08") -> Dict[str, Any]:
    return {"shadow_role": role, "_payload_generated_at": window, "generated_at": f"{day}T09:00:00+09:00",
            "shadow_forward_outcome": _obs(ret)}


def q9_row(decision: str, role: str, ret: float | None, *, rank: int = 1, day: str = "2026-06-08", **extra: Any) -> Dict[str, Any]:
    return {"q9_decision_id": decision, "q9_decision_role": role, "rank": rank, "generated_at": f"{day}T09:00:00+09:00",
            "shadow_forward_outcome": _obs(ret), **extra}


def chain_rows(days: int = 3, per_day: int = 8) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for d in range(days):
        day = f"2026-06-0{d + 1}"
        for i in range(per_day):
            dec = f"{day}-{i}"
            rows += [
                q9_row(dec, "A_SCANNER_CONTROL", 0.1, day=day),
                q9_row(dec, "B_STRATEGIST_RANKED", 0.9, day=day, rank=3, q9_selected=True),
                q9_row(dec, "B_STRATEGIST_RANKED", -5.0, day=day, rank=1),
                q9_row(dec, "R1_PRE_REFRESH_SCANNER", 0.2, day=day),
                q9_row(dec, "R2_POST_REFRESH_SCANNER", None, day=day),
                q9_row(dec, "C_COMMANDER_FINAL", 0.0, day=day, q9_commander_no_trade=(i % 2 == 0)),
            ]
    return rows


def test_decision_window_attribution_roles_and_missing_pairs() -> None:
    result = attr.decision_window_attribution(chain_rows(), cost_pct=0.2, day_of=lambda r: r["generated_at"][:10])
    row = next(item for item in result["by_horizon"] if item["horizon"] == "+30m")
    assert result["decision_window_count"] == 24 and result["candidate_row_count"] == 144
    assert row["strategist_comparison_count"] == 24 and row["average_strategist_delta_pct"] == 0.8
    assert row["strategist_day_count"] == 3
    assert row["post_scanner_refresh_comparison_count"] == 0 and row["average_post_scanner_refresh_delta_pct"] is None
    assert row["commander_comparison_count"] == 24
    assert result["full_strategist_contribution_status"] == "NOT_MEASURABLE"


def test_role_scoring_thresholds_stay_in_facade() -> None:
    attribution = attr.decision_window_attribution(chain_rows(), cost_pct=0.2, day_of=lambda r: r["generated_at"][:10])
    strategist = full_chain._attribution_component(
        attribution=attribution, component="strategist", question="q", missing_comparison="m", availability={}
    )
    assert strategist["decision"] == "PROMOTION_CANDIDATE" and strategist["behavior_change_authorized"] is False
    thin = attr.decision_window_attribution(chain_rows(days=1, per_day=2), cost_pct=0.2, day_of=lambda r: r["generated_at"][:10])
    assert full_chain._attribution_component(
        attribution=thin, component="commander", question="q", missing_comparison="m", availability={}
    )["decision"] == "INSUFFICIENT_EVIDENCE"


def test_paired_roles_availability_and_exclusions() -> None:
    rows = [shadow_row("w1", "top_pick", 1.0), shadow_row("w1", "runner_up_evaluated", 0.4),
            shadow_row("w2", "top_pick", 0.5), shadow_row("", "top_pick", 9.0), shadow_row("w3", "runner_up_evaluated", None)]
    paired = full_chain._paired_role_deltas(rows, horizon="+30m")
    assert paired["paired_window_count"] == 1 and paired["average_delta_pct"] == 0.6
    metrics = full_chain._role_metrics(rows, role="top_pick", horizon="+30m", cost_pct=0.5)
    assert metrics["observed_count"] == 3 and metrics["cost_adjusted"] is True
    availability = full_chain._selection_availability([
        {"selection": {"raw_scanner_snapshot_source": "control_snapshot", "raw_scanner_top10": [1],
                       "strategist_run_id": "s", "post_strategist_top10": [1], "commander_final_explicit": True}},
        {"selection": None},
    ])
    assert availability["scanner_vs_strategist_comparable_count"] == 1
    assert availability["missing_fields"] == {"explicit_commander_selection_or_veto": 1,
                                              "strategist_run_and_post_ranking": 1, "trusted_raw_scanner_top10": 1}
    assert not full_chain._behavior_metric_eligible({"integrity": {"defects": ["confirmed_runtime_defect"]}})
    assert full_chain._behavior_metric_eligible({"integrity": None})


def test_full_chain_build_scorecard_and_render(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    payloads = [{"generated_at": "2026-06-08T09:00:00+09:00",
                 "candidates": [shadow_row("w1", "top_pick", 0.4), shadow_row("w1", "runner_up_evaluated", 0.1)],
                 "q9_decision_candidates": chain_rows(days=1, per_day=2)}]
    monkeypatch.setattr(full_chain, "load_quant_shadow_candidate_payloads_for_range", lambda **_: payloads)
    monkeypatch.setattr(full_chain, "attach_forward_outcomes", lambda rows: rows)
    monkeypatch.setattr(full_chain, "_candidate_rows", lambda p: [dict(r) for r in p[0]["candidates"]])
    monkeypatch.setattr(full_chain, "_load_trade_models", lambda *_: [
        {"trade_id": "T1", "day": "2026-06-08", "outcome": {"net_return_pct": -0.5}, "integrity": {"defects": []}},
        {"trade_id": "T2", "day": "2026-06-08", "integrity": {"defects": ["broker_day_partial_exit_duplicate"]}}])
    monkeypatch.setattr(full_chain, "load_broker_cost_profile", lambda path=None: {"conservative_round_trip_cost_pct": 0.002})
    review = full_chain.build_full_chain_component_review(reports_root=tmp_path, start="2026-06-08", end="2026-06-08")
    assert review["evidence"]["excluded_trade_model_count"] == 1
    assert review["overall_decision"]["decision"] == "INSUFFICIENT_EVIDENCE"
    assert review["component_decisions"]["strategist"]["full_strategist_contribution"]["decision"] == "INSUFFICIENT_EVIDENCE"
    md = full_chain.render_full_chain_component_review(review)
    assert "| scanner | `INSUFFICIENT_EVIDENCE` |" in md and "- behavior change authorized: **False**" in md
    card = scorecard.build_agent_effectiveness_scorecard(review)
    assert card["integrity"]["state"] == "PASS_WITH_EXCLUSIONS"
    assert card["components"]["strategist"]["ranking_overlay"]["state"] == "NOT_MEASURABLE"
    assert card["components"]["full_system"]["state"] == "NOT_MEASURABLE"
    assert card["behavior_change_authorized"] is False
    assert "- Commander:" in scorecard.render_agent_effectiveness_scorecard(card)


def test_scorecard_legacy_overlay_keys_fall_back() -> None:
    legacy = {"strategist_comparison_count": 30, "strategist_day_count": 3,
              "average_strategist_delta_pct": -0.5, "strategist_positive_delta_rate": 0.2}
    metrics = render.scorecard_overlay_metrics(legacy)
    assert scorecard._delta_state(metrics, prefix="strategy_ranking_overlay", missing_control="x")["state"] == "DEGRADING"


def test_operator_summary_mining_coverage_and_errors(tmp_path: Path) -> None:
    root = tmp_path / "reports"
    daily = root / "operator_summary" / "daily"
    _write(daily / "2026-06-08" / "daily_summary.json", {"metrics": {"trade_count": 2}})
    _write(daily / "2026-06-08" / "trade_index.json", [{"t": 1}])
    (daily / "2026-06-09").mkdir(parents=True)
    (daily / "2026-06-09" / "q9_decision_windows.json").write_text("{bad", encoding="utf-8")
    _write(root / "operator_summary" / "weekly" / "2026-W23" / "weekly_summary.json",
           {"metrics": {"trade_count": "3"}, "pattern_performance": {"a": 1}})
    _write(root / "operator_summary" / "symbols" / "005930" / "symbol_memory.json",
           {"symbol_memory": {"trade_stats": {"trade_count": 6, "win_rate": 0.5}}})
    payload = mining.build_operator_summary_mining(root)
    assert payload["daily_presence"]["json_error_count"] == 1
    assert payload["daily_quality"]["trade_index_mismatch_examples"] == [
        {"day": "2026-06-08", "daily_trade_count": 2, "trade_index_count": 1}]
    assert payload["daily_quality"]["missing_runtime_surface_days"] == ["2026-06-08"]
    assert payload["weekly_quality"]["usable_week_count"] == 0
    assert payload["symbol_quality"]["symbols_with_trade_count_ge_5"] == 1
    assert payload["readiness"]["status"] == "NEEDS_REPAIR"
    md = mining.render_operator_summary_mining_markdown(payload)
    assert md.startswith("# Operator Summary Mining Report") and "NEEDS_REPAIR" in md


def test_mining_empty_root(tmp_path: Path) -> None:
    payload = mining.build_operator_summary_mining(tmp_path / "missing")
    assert payload["daily_presence"]["daily_count"] == 0 and payload["daily_presence"]["first_day"] == ""
    assert payload["weekly_quality"] == {"weekly_count": 0, "recent_weeks": [], "usable_week_count": 0}
    assert payload["readiness"]["status"] == "NEEDS_REPAIR"


def test_fast07_owners_are_pure() -> None:
    allowed = {"__future__", "array", "collections", "datetime", "json", "typing", ".contracts", ".metrics"}
    for module in (attr, render):
        source = Path(module.__file__).read_text(encoding="utf-8")
        imports = [line for line in source.splitlines() if line.startswith(("import ", "from "))]
        assert all(line.split()[1] in allowed for line in imports), imports
        for banned in ("open(", "write_text", "read_text", "read_json", "os.environ", "getenv", "subprocess", "now("):
            assert banned not in source, (module.__name__, banned)
