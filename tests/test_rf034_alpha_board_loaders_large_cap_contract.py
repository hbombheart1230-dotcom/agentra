"""RF-034 C3: alpha_research_board loaders and large_cap_review (tmp reports root)."""
from __future__ import annotations

import json

import pytest

from libs.reporting.alpha_research_board import large_cap_review as lc
from libs.reporting.alpha_research_board import loaders as ld


def test_mapping_and_finders():
    assert ld.mapping({"a": 1}) == {"a": 1} and ld.mapping(None) == {} and ld.mapping([1]) == {}
    rows = [{"k": "x"}, {"candidate": {"k": "y"}, "extra": 1}, "junk"]
    assert ld.find_by_id(rows, "k", "x") == {"k": "x"} and ld.find_by_id(rows, "k", "y") == {"candidate": {"k": "y"}, "extra": 1}
    assert ld.find_by_id(rows, "k", "z") == {} and ld.find_by_id(None, "k", "x") == {}
    assert ld.find_horizon([{"horizon": "+5m", "v": 1}, {"horizon": "+30m", "v": 2}], "+30m") == {"horizon": "+30m", "v": 2} and ld.find_horizon([], "+5m") == {}


def test_load_json_error_taxonomy(tmp_path):
    p = tmp_path / "x.json"
    payload, src = ld.load_json(p)
    assert payload == {} and src == {"path": str(p), "available": False, "error": "MISSING_ARTIFACT"}
    p.write_text("{bad", encoding="utf-8")
    assert ld.load_json(p)[1]["error"] == "INVALID_ARTIFACT:JSONDecodeError"
    p.write_text("[1]", encoding="utf-8")
    assert ld.load_json(p)[1]["error"] == "SCHEMA_MISMATCH:ROOT_NOT_OBJECT"
    p.write_text(json.dumps({"schema_version": "s", "day": "2026-09-01", "k": 1}), encoding="utf-8")
    payload, src = ld.load_json(p)
    assert payload["k"] == 1 and src["error"] is None and src["schema_version"] == "s" and src["through_day"] == "2026-09-01"
    p.write_text(json.dumps({"through_day": "T", "day": "D"}), encoding="utf-8")
    assert ld.load_json(p)[1]["through_day"] == "T"
    p.write_bytes(b"\xff\xfe")
    assert ld.load_json(p)[1]["error"].startswith("INVALID_ARTIFACT:")


def test_metric_snapshot_key_fallback_chains():
    m = ld.metric_snapshot({"day_symbol_count": 7, "observed_count": 9, "day_symbol_win_rate": 0.5, "win_rate": 0.9, "average_return_pct": 1.5, "maximum_drawdown_pct": -2.0,
                            "target_coverage": 0.8, "average_mfe_pct": 3.0, "average_mae_pct": -1.0, "profit_factor": 2.0})
    assert m["sample_count"] == 7 and m["window_count"] == 9 and m["win_rate"] == 0.5 and m["avg_net_return_pct"] == 1.5
    assert m["max_drawdown_pct"] == -2.0 and m["coverage"] == 0.8 and m["avg_mfe_pct"] == 3.0 and m["avg_mae_pct"] == -1.0 and m["profit_factor"] == 2.0
    pref = ld.metric_snapshot({"day_symbol_avg_net_return_pct": 1.0, "avg_net_return_pct": 2.0, "avg_return_pct": 3.0, "sample_count": 4, "trade_count": 8, "count": 9, "window_count": 11, "episode_count": 12})
    assert pref["avg_net_return_pct"] == 1.0 and pref["sample_count"] == 4 and pref["window_count"] == 11
    assert ld.metric_snapshot({"avg_return_pct": 3.0})["avg_net_return_pct"] == 3.0 and ld.metric_snapshot({"coverage": 0.3})["coverage"] == 0.3
    empty = ld.metric_snapshot(None)
    assert empty["sample_count"] == 0 and empty["window_count"] == 0 and empty["win_rate"] is None


def _put(root, day, avg, count, *, raw=None, horizon="+180m"):
    p = root / "evaluation" / "baseline_samsung_hynix" / day / "baseline_samsung_hynix_forward_returns.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(raw if raw is not None else json.dumps({"summary": {"horizons": [{"horizon": horizon, "top1_gross": {"average_return_pct": avg, "count": count}}]}}), encoding="utf-8")


def test_collect_rows_boundaries_filters_and_net_cost(tmp_path):
    _put(tmp_path, "2026-08-20", 9.0, 5)                                 # before integrity boundary
    _put(tmp_path, "2026-08-21", 1.0, 3)
    _put(tmp_path, "2026-08-24", 2.0, 0)                                 # count 0 -> skipped
    _put(tmp_path, "2026-08-25", None, 4)                                # no average -> skipped
    _put(tmp_path, "2026-08-26", 3.0, 2, horizon="+30m")                 # wrong horizon -> skipped
    _put(tmp_path, "2026-08-27", 0.0, 2)                                 # zero average is valid
    _put(tmp_path, "2026-09-30", 5.0, 1)                                 # after through_day
    rows, sources = lc.collect_large_cap_daily_rows(reports_root=tmp_path, through_day="2026-08-31")
    assert [(r["day"], r["gross_return_pct"], r["net_return_pct"], r["window_count"]) for r in rows] == [("2026-08-21", 1.0, 0.72, 3), ("2026-08-27", 0.0, -0.28, 2)]
    assert len(sources) == 5 and rows[0]["symbol"] == "SAMSUNG_HYNIX_FIXED_UNIVERSE" and rows[0]["source_path"].endswith("baseline_samsung_hynix_forward_returns.json")
    rows2, _ = lc.collect_large_cap_daily_rows(reports_root=tmp_path, through_day="2026-08-21")
    assert [r["day"] for r in rows2] == ["2026-08-21"]                    # through_day inclusive


def test_review_decision_ladder(tmp_path):
    assert lc.build_large_cap_daily_review(reports_root=tmp_path / "none", through_day="2026-09-30")["decision"] == "RUNTIME_DATA_REQUIRED"
    for i in range(4):
        _put(tmp_path, f"2026-08-{24 + i}", 1.0, 2)
    four = lc.build_large_cap_daily_review(reports_root=tmp_path, through_day="2026-09-30")
    assert four["decision"] == "RUNTIME_DATA_REQUIRED" and "sample is 4" in four["rationale"] and four["base"]["window_count"] == 8
    _put(tmp_path, "2026-08-28", 1.0, 2)
    five = lc.build_large_cap_daily_review(reports_root=tmp_path, through_day="2026-09-30")
    assert five["decision"] == "READY_FOR_OFFLINE_REVIEW" and five["base"]["sample_count"] == 5 and five["source_count"] == 5 and five["invalid_sources"] == []
    assert five["cost_pct"] == 0.28 and five["target_horizon"] == "+180m" and five["integrity_boundary_day"] == "2026-08-21" and five["minimum_independent_days"] == 5
    _put(tmp_path, "2026-08-29", None, 0, raw="{corrupt")
    bad = lc.build_large_cap_daily_review(reports_root=tmp_path, through_day="2026-09-30")
    assert bad["decision"] == "RUNTIME_DATA_INTEGRITY_ERROR" and len(bad["invalid_sources"]) == 1                    # integrity error outranks sample size
