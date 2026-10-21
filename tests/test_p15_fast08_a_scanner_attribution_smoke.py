"""FAST08 A8.2 smoke tests: selection authority, Q14 root cause, Scanner quality and episodes."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from libs.reporting.evaluation import episode_scanner_review as episodes
from libs.reporting.evaluation import fast08_scanner_attribution as sa
from libs.reporting.evaluation import scanner_alignment_root_cause as q14
from libs.reporting.evaluation import scanner_quality
from libs.reporting.evaluation.selection_authority_audit import build_selection_authority_audit, render_selection_authority_audit


def model(trade_id: str, *, raw: str, post: str, selected: str, executed: str, rank: Any = 1, ret: float | None = 0.5,
          defects: List[str] | None = None, commander: str = "") -> Dict[str, Any]:
    return {
        "trade_id": trade_id,
        "symbol": executed,
        "integrity": {"defects": defects or []},
        "selection": {"raw_scanner_top1": {"symbol": raw}, "scanner_top1": {"symbol": post, "score_total": 9},
                      "selected_symbol": selected, "selected_rank": rank,
                      "selected_candidate": {"score_total": 7}, "commander_final": {"selected_symbol": commander}},
        "monitor": {"entry_context": {"selected_symbol": selected}},
        "outcome": {"net_return_pct": ret},
    }


MODELS = [
    model("T1", raw="A", post="A", selected="A", executed="A", ret=-0.5),             # Scanner Ranking Failure
    model("T2", raw="A", post="B", selected="B", executed="B"),                         # Strategist Override
    model("T3", raw="A", post="A", selected="C", executed="C", rank=3),                 # Candidate Filtering
    model("T4", raw="A", post="A", selected="A", executed="Z", commander="A"),          # Symbol Mapping
    model("T5", raw="", post="A", selected="A", executed="A"),                          # Missing Evidence
    model("T6", raw="A", post="A", selected="A", executed="A"),                         # Aligned
    model("T7", raw="A", post="A", selected="A", executed="A", defects=["confirmed_runtime_defect"]),
]


def test_selection_authority_path_and_exclusions() -> None:
    audit = build_selection_authority_audit(MODELS)
    assert audit["trade_count"] == 6
    assert audit["summary"]["excluded:confirmed_runtime_defect"] == 1
    assert audit["summary"]["raw_to_post_changed:unavailable"] == 1
    row = {r["trade_id"]: r for r in audit["rows"]}["T4"]
    assert row["final_to_executed_changed"] is True and row["selected_to_monitor_changed"] is False
    md = render_selection_authority_audit(audit)
    assert "| T4 | A | A | A | A | - | A | Z |" in md
    assert "- No rows." in render_selection_authority_audit({})


def test_q14_root_cause_classification_and_largest_structural() -> None:
    audit = build_selection_authority_audit(MODELS)
    report = q14.build_scanner_alignment_root_cause_report(day="2026-06-08", models=MODELS, evaluations=[], selection_authority=audit)
    causes = {r["trade_id"]: r["root_cause"] for r in report["rows"]}
    assert causes == {"T1": "Scanner Ranking Failure", "T2": "Strategist Override", "T3": "Candidate Filtering",
                      "T4": "Symbol Mapping", "T5": "Missing Evidence", "T6": "Aligned / No Alignment Issue"}
    assert [row["root_cause"] for row in report["cause_summary"]] == list(q14.ROOT_CAUSES)
    assert report["largest_structural_root_cause"]["root_cause"] not in q14.OUTCOME_CONDITIONED_CAUSES | q14.EVIDENCE_GAP_CAUSES
    t3 = next(r for r in report["rows"] if r["trade_id"] == "T3")
    assert t3["score_gap"] == 2.0 and t3["causal_eligible"] is True
    assert report["q15_behavior_patch_candidate"]
    md = q14.render_scanner_alignment_root_cause_report(report)
    assert "| Candidate Filtering | structural | True | 1 |" in md


def test_q14_range_reads_daily_artifacts(tmp_path: Path) -> None:
    import json
    day = tmp_path / "evaluation" / "daily" / "2026-06-08"
    day.mkdir(parents=True)
    (day / "selection_authority_audit.json").write_text(json.dumps(build_selection_authority_audit(MODELS)), encoding="utf-8")
    result = q14.build_scanner_alignment_root_cause_range(reports_root=tmp_path, start="2026-06-07", end="2026-06-09")
    assert result["day_count"] == 1 and result["trade_count"] == 6
    assert result["daily_rows"][0]["day"] == "2026-06-08"
    empty = q14.build_scanner_alignment_root_cause_range(reports_root=tmp_path / "none", start="2026-06-07", end="2026-06-07")
    assert empty["trade_count"] == 0 and empty["largest_root_cause"] == {}


def candidate(decision: str, symbol: str, rank: int, ret: float | None, *, epoch: int = 1780876800, day: str = "2026-06-08",
              sources: List[str] | None = None, breakdown: Dict[str, float] | None = None) -> Dict[str, Any]:
    cps = {} if ret is None else {h: {"status": "observed", "return_pct": ret} for h in scanner_quality.SCANNER_HORIZONS}
    return {"q9_decision_id": decision, "symbol": symbol, "rank": rank, "generated_at": f"{day}T09:00:00+09:00",
            "shadow_forward_base": {"baseline_epoch": epoch}, "shadow_forward_outcome": {"checkpoints": cps},
            "q9_candidate_sources": sources or [], "score_breakdown": breakdown or {}}


def test_topk_and_source_performance_apply_cost_drag() -> None:
    rows = [candidate("D1", "A", 1, 1.0, sources=["vol"]), candidate("D1", "B", 2, 0.0), candidate("D1", "C", 3, None),
            candidate("D2", "A", 1, -1.0)]
    topk = scanner_quality.build_scanner_topk_forward_performance(rows, cost_pct=0.2, slippage_pct=0.05)
    top1 = next(r for r in topk["rows"] if r["top_k"] == 1 and r["horizon"] == "+30m")
    assert topk["decision_window_count"] == 2 and top1["window_count"] == 2
    assert top1["net"]["average_return_pct"] == -0.25
    top3 = next(r for r in topk["rows"] if r["top_k"] == 3 and r["horizon"] == "+5m")
    assert top3["candidate_observation_count"] == 3
    sources = scanner_quality.build_scanner_source_performance(rows, cost_pct=0.0, slippage_pct=0.0)
    assert {(r["source"], r["horizon"]) for r in sources["rows"]} >= {("vol", "+5m"), ("unknown", "EOD")}


def test_episode_dedup_components_and_readiness_threshold() -> None:
    rows = [candidate("D1", "A", 1, 1.0, epoch=1000, breakdown={"momentum": 2.0}),
            candidate("D2", "A", 1, 0.5, epoch=1300, breakdown={"momentum": 1.0}),
            candidate("D3", "A", 2, -0.5, epoch=3000, breakdown={"momentum": 0.5}),
            candidate("D4", "B", 5, None, epoch=1000)]
    review = episodes.build_episode_scanner_review([], mock_drag_pct=0.1, live_drag_pct=0.3, prepared_rows=rows)
    assert review["raw_candidate_row_count"] == 4 and review["episode_count"] == 3
    assert {e["rank_bucket"] for e in review["episodes"]} == {"rank1", "rank2_3", "rank4_plus"}
    assert review["score_component_review"]["status"] == "NOT_READY_MISSING_SCORE_COMPONENT_ARTIFACT"
    assert review["score_component_review"]["rows"][0]["score_return_correlation"] == 1.0
    assert review["rank1_minus_rank2_3_gross_30m_pct"] == 1.5


def test_same_symbol_reentry_split_by_prior_outcome() -> None:
    rows = [{"trade_id": "TRD_20260608_A_01", "symbol": "A", "net_return_pct": -1.0},
            {"trade_id": "TRD_20260608_A_02", "symbol": "A", "net_return_pct": 0.4},
            {"trade_id": "TRD_20260608_A_03", "symbol": "A", "net_return_pct": -0.2},
            {"trade_id": "bad", "symbol": "A", "net_return_pct": 9}]
    review = episodes.build_same_symbol_reentry_review(rows)
    assert review["day_symbol_group_count"] == 1 and review["repeated_day_symbol_group_count"] == 1
    assert review["repeat_after_loss"]["count"] == 1 and review["repeat_after_non_loss"]["count"] == 1
    assert review["behavior_candidate_eligible"] is False


def test_a82_helper_is_pure() -> None:
    source = Path(sa.__file__).read_text(encoding="utf-8")
    imports = [line for line in source.splitlines() if line.startswith(("import ", "from "))]
    assert all(line.split()[1] in {"__future__", "collections", "math", "typing", ".metrics"} for line in imports), imports
    for banned in ("open(", "write_text", "read_text", "read_json", "os.environ", "subprocess", "now("):
        assert banned not in source, banned
