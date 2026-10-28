"""RF-031 reporter_feedback: pure extraction/analysis helpers (no files except tmp, no network, no AI)."""
from __future__ import annotations

import json

from libs.reporting import reporter_feedback as rf


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


def test_primitive_helpers_and_read_json(tmp_path):
    _eq((rf._normalize_day(None), rf._normalize_day(" 2026-10-28 ")), ("", "2026-10-28"))
    _eq((rf._safe_int("5"), rf._safe_int(None, 7), rf._safe_int("5.5", 2)), (5, 7, 2))         # int() of a float string falls back
    _eq((rf._safe_float("1.5"), rf._safe_float("x", 3.0)), (1.5, 3.0))
    _eq((rf._safe_total({"a": "2", "b": 3, "c": "bad"}), rf._safe_total(None), rf._safe_total([1])), (5, 0, 0))
    _eq((rf._ratio(1, 3), rf._ratio(1, 0), rf._ratio(2, -1)), (0.3333, 0.0, 0.0))
    _eq(rf._read_json(tmp_path / "none.json"), {})
    p = tmp_path / "o.json"
    p.write_text("{x", encoding="utf-8")
    _eq(rf._read_json(p), {})
    p.write_text(json.dumps([1]), encoding="utf-8")
    _eq(rf._read_json(p), {})
    p.write_text(json.dumps({"ok": True}), encoding="utf-8")
    _eq(rf._read_json(p), {"ok": True})


def test_route_summary_prefers_nested_then_flat_keys_and_defaults():
    nested = rf._extract_route_summary({"route_summary": {"route_source": "events", "route_source_run_count": "3",
                                                          "route_selected_total": {"full_cycle": 2}, "strategist_fallback_total": "1"},
                                        "route_source": "ignored"})
    _eq((nested["route_source"], nested["route_source_run_count"], nested["route_selected_total"], nested["strategist_fallback_total"]),
        ("events", 3, {"full_cycle": 2}, 1))
    flat = rf._extract_route_summary({"route_selected_total": {"monitor_only": 4}, "strategist_mode_total": {"llm": 1},
                                      "strategist_fallback_total": 2, "route_source_missing_count": "x"})
    _eq((flat["route_source"], flat["route_selected_total"], flat["strategy_generation_mode_total"], flat["strategist_fallback_total"], flat["route_source_missing_count"]),
        ("unavailable", {"monitor_only": 4}, {"llm": 1}, 2, 0))
    empty = rf._extract_route_summary(None)
    _eq((empty["route_source"], empty["route_selected_total"], empty["strategist_fallback_total"]), ("unavailable", {}, 0))


def test_blocker_totals_direct_wins_else_topn_with_blank_and_non_dict_rows_dropped():
    _eq(rf._extract_blocker_totals({"dominant_blocker_total": {"a": "2", "b": "x"}, "no_trade_summary": {"dominant_blocker_topN": [{"reason": "z", "count": 9}]}}),
        {"a": 2, "b": 0})
    top = {"no_trade_summary": {"dominant_blocker_topN": [{"reason": "r1", "count": "3"}, {"reason": " ", "count": 5}, "junk", {"reason": "r2"}]}}
    _eq(rf._extract_blocker_totals(top), {"r1": 3, "r2": 0})
    _eq(rf._extract_blocker_totals(None), {})


def test_freshness_declared_or_derived():
    declared = {"freshness_status": "fresh", "stale": False}
    _eq(rf._extract_freshness({"data_freshness": declared, "generated_at": "x"}), declared)
    derived = rf._extract_freshness({"generated_at": "2026-10-28T09:00:00", "source_run_count": "2", "latest_run_id": "r"})
    _eq((derived["freshness_status"], derived["stale_reason"], derived["source_run_count"], derived["latest_run_id"]), ("fresh", "aligned_with_source_window", 2, "r"))
    unknown = rf._extract_freshness({})
    _eq((unknown["freshness_status"], unknown["stale_reason"], unknown["stale"]), ("unknown", "source_not_declared", False))


def test_reporter_analysis_blockers_merge_sources_and_skip_monitor_prefixed_intent_reasons():
    payload = {"monitor_evaluation": {"monitor_reason_top": {"trail": 2, "": 5}},
               "supervisor_activity": {"blocked_reason_top": {"trail": "1", "risk": 3}},
               "intent_flow_analysis": {"reason_top": {"risk": 1, "monitor:trail": 9, " ": 4, "guard": 2}}}
    _eq(rf._extract_reporter_analysis_blocker_totals(payload), {"trail": 3, "risk": 4, "guard": 2})
    _eq(rf._extract_reporter_analysis_blocker_totals({"monitor_evaluation": "x"}), {})


def test_recommendations_prefer_direct_suggestions_and_cap_at_four():
    _eq(rf._extract_reporter_analysis_recommendations({"improvement_suggestions": ["a", " ", "b", "c", "d", "e"], "operator_facing_summary": {"recommended_actions": ["z"]}}),
        ["a", "b", "c", "d"])
    _eq(rf._extract_reporter_analysis_recommendations({"operator_facing_summary": {"recommended_actions": ["z", "", "y"]}}), ["z", "y"])
    _eq(rf._extract_reporter_analysis_recommendations({}), [])


def test_blocker_and_route_analysis_rank_and_ratios():
    ranked = rf._build_blocker_analysis({"b": 2, "a": 2, "c": 5, "d": 1, "e": 1, "f": 1})
    _eq([r["blocker"] for r in ranked], ["c", "a", "b", "d", "e"])                    # count desc, then name; top 5 only
    _eq(ranked[0], {"blocker": "c", "count": 5, "ratio": round(5 / 12, 4)})
    _eq(rf._build_blocker_analysis({}), [])
    route = rf._build_route_analysis({"route_selected_total": {"monitor_only": 1, "cached_strategist": 1, "full_cycle": 2}, "route_source": ""})
    _eq((route["route_source"], route["monitor_only_ratio"], route["cached_strategist_ratio"], route["full_cycle_ratio"]), ("unavailable", 0.25, 0.25, 0.5))
    _eq(rf._build_route_analysis({})["full_cycle_ratio"], 0.0)


def test_confidence_levels_follow_the_documented_thresholds():
    blockers3 = [{"count": 1}] * 3
    cases = [
        ({"route_selected_total": {"x": 50}}, blockers3, None, "high"),
        ({"route_selected_total": {"x": 50}}, [{"count": 1}], None, "medium"),                      # 50 routes but <3 blockers falls to the >=10 rule
        ({"route_selected_total": {"x": 10}}, [], None, "medium"),
        ({}, [], {"closed_trade_count": 3, "broker_truth_count": 2}, "high"),
        ({}, [], {"closed_trade_count": 1, "broker_truth_count": 1}, "medium"),
        ({}, [{"count": 10}, {"count": 10}], None, "high"),
        ({}, [{"count": 5}], None, "medium"),
        ({}, [{"count": 4}], None, "low"),
        ({"route_selected_total": "bad"}, [], None, "low"),
    ]
    for route, blockers, trade, expected in cases:
        _eq(rf._build_confidence(route_analysis=route, blocker_analysis=blockers, trade_report_summary=trade), expected)
