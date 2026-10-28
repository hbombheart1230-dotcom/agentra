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


def _trade(root, trade_id, body):
    path = root / "trades" / "2026-10-28" / trade_id / "reports" / "ai_trade_report.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(body), encoding="utf-8")


def _truth(status="closed", pnl=None, price=None, availability=None, exit_reason="", symbol=""):
    return {"symbol": symbol, "truth_surface": {"status": {"status": status, "exit_reason": exit_reason, "symbol": symbol},
                                                 "price": price or {}, "pnl": pnl or {}, "availability": availability or {}}}


def test_trade_report_summary_classifies_closed_trades_from_tmp_reports(tmp_path):
    root = tmp_path / "reports"
    _eq(rf._build_trade_report_feedback_summary(root, "2026-10-28")["trade_count"], 0)              # no trade root
    _trade(root, "TRD_1", _truth(pnl={"value": 100, "pct": 1.5}, availability={"broker_fill_present": True, "broker_pnl_present": True},
                                 exit_reason="trail", symbol="005930"))
    _trade(root, "TRD_2", _truth(pnl={"value": -50, "pct": "-0.5", "broker_fee": 10},
                                 price={"broker_buy_price": 100, "broker_fill_price": "100"}, exit_reason="trail", symbol="000660"))
    _trade(root, "TRD_3", _truth(pnl={"value": 0}, symbol="005930"))
    _trade(root, "TRD_4", _truth(pnl={"pct": 2}, exit_reason="stop"))
    _trade(root, "TRD_5", _truth())                                                                 # closed with no pnl at all -> unknown
    _trade(root, "TRD_6", _truth(status="open", pnl={"value": 5}))                                  # counted as a trade, never as closed
    _trade(root, "TRD_7", {})                                                                       # empty payload is skipped entirely
    out = rf._build_trade_report_feedback_summary(root, "2026-10-28")
    _eq((out["trade_count"], out["closed_trade_count"]), (6, 5))
    _eq((out["win_count"], out["loss_count"], out["flat_count"], out["unknown_pnl_count"]), (2, 1, 1, 1))
    _eq((out["broker_truth_count"], out["same_price_cost_loss_count"]), (1, 1))
    _eq((out["avg_pnl_pct"], out["pnl_pct_sample_count"]), (round((1.5 - 0.5 + 2) / 3, 4), 3))
    _eq(out["exit_reason_counts"], {"trail": 2, "stop": 1})
    _eq(out["symbols"], ["005930", "000660"])                                                       # most frequent symbol first
    _eq(sorted(p.name for p in tmp_path.iterdir()), ["reports"])


def test_metrics_payload_prefers_an_existing_report_and_survives_generator_failures(tmp_path, monkeypatch):
    root = tmp_path / "reports"
    (root / "metrics").mkdir(parents=True)
    (root / "metrics" / "metrics_2026-10-28.json").write_text(json.dumps({"existing": 1}), encoding="utf-8")
    _eq(rf._load_or_generate_metrics_payload(root, "2026-10-28"), {"existing": 1})
    _eq(rf._load_or_generate_metrics_payload(root, "2026-10-29"), {})                               # nothing on disk, no event logs
    events = tmp_path / "data" / "logs" / "events.jsonl"
    events.parent.mkdir(parents=True)
    events.write_text("", encoding="utf-8")

    import libs.reporting.metrics_report_generator as mg

    def boom(*a, **k):
        raise RuntimeError("generator down")

    monkeypatch.setattr(mg, "generate_metrics_report", boom)
    _eq(rf._load_or_generate_metrics_payload(root, "2026-10-29"), {})                               # generator failure is swallowed

    def fake(events_path, out_dir, day):
        out_dir.mkdir(parents=True, exist_ok=True)
        js = out_dir / f"metrics_{day}.json"
        js.write_text(json.dumps({"generated": True}), encoding="utf-8")
        return out_dir / "x.md", js

    monkeypatch.setattr(mg, "generate_metrics_report", fake)
    _eq(rf._load_or_generate_metrics_payload(root, "2026-10-29"), {"generated": True})


def test_dominant_patterns_cover_route_reclaim_fallback_freshness_and_trade_rows():
    route = {"route_selected_total": {"monitor_only": 3, "cached_strategist": 0, "full_cycle": 1}, "strategist_fallback_total": 2}
    patterns = rf._build_dominant_patterns(route_summary=route, blocker_totals={"vwap_reclaim_fail": 3, "other": 1},
                                           freshness={"freshness_status": "fresh", "source_window_summary": "w"},
                                           trade_report_summary={"closed_trade_count": 4, "avg_pnl_pct": 0.5, "same_price_cost_loss_count": 1})
    _eq([p["name"] for p in patterns], ["monitor_only_ratio", "full_cycle_ratio", "reclaim_blocked_ratio", "strategist_fallback_ratio", "freshness_status", "same_day_closed_trade_count"])
    _eq((patterns[0]["value"], patterns[2]["value"], patterns[3]["value"]), (0.75, 0.75, 0.5))      # list is capped at six rows
    full = rf._build_dominant_patterns(route_summary={}, blocker_totals={}, freshness={},
                                       trade_report_summary={"closed_trade_count": 2, "avg_pnl_pct": 1.0, "same_price_cost_loss_count": 1})
    _eq([p["name"] for p in full], ["same_day_closed_trade_count", "same_day_avg_pnl_pct", "same_price_cost_loss_ratio"])
    _eq(full[2]["value"], 0.5)
    _eq(rf._build_dominant_patterns(route_summary={}, blocker_totals={}, freshness={}), [])


def test_recommendations_triggered_by_route_blocker_and_trade_signals_and_capped_at_four():
    base = {"monitor_only_ratio": 0.5, "cached_strategist_ratio": 0.25}
    recs = rf._build_recommendations(route_analysis=base, blocker_analysis=[{"blocker": "vwap_reclaim_x", "count": 3}],
                                     trade_report_summary={"closed_trade_count": 3, "same_price_cost_loss_count": 1, "win_count": 0, "loss_count": 2})
    _eq(len(recs), 4)                                                                                # six candidates, capped
    if not recs[0].startswith("Monitor-only") or not recs[1].startswith("Cached strategist") or "vwap_reclaim_x" not in recs[2]:
        raise AssertionError(recs)
    only_trade = rf._build_recommendations(route_analysis={}, blocker_analysis=[], trade_report_summary={"closed_trade_count": 3, "win_count": 1, "loss_count": 2})
    _eq(len(only_trade), 1)
    if not only_trade[0].startswith("Same-day closed trades are loss-heavy"):
        raise AssertionError(only_trade)
    balanced = rf._build_recommendations(route_analysis={}, blocker_analysis=[{"blocker": "", "count": 1}])
    if not balanced[0].startswith("Route and blocker mix look balanced"):
        raise AssertionError(balanced)                                                               # a blank top blocker adds nothing


def test_insight_summary_wording_for_route_blocker_and_trade_parts():
    route = {"route_selected_total": {"monitor_only": 1, "full_cycle": 3}}
    text = rf._build_insight_summary(route_analysis=route, blocker_analysis=[{"blocker": "b", "count": 2}],
                                     trade_report_summary={"closed_trade_count": 4, "win_count": 2, "loss_count": 1, "flat_count": 1,
                                                           "unknown_pnl_count": 1, "avg_pnl_pct": 0.4, "pnl_pct_sample_count": 3})
    _eq(text, "Route mix is led by full_cycle 3/4; monitor_only 1/4, cached_strategist 0/4. Top blocker is b (2). "
              "Same-day closed trade reports show 4 trades with 2 wins, 1 losses, 1 flat, 1 unknown pnl, avg pnl pct 0.4.")
    zero_leader = rf._build_insight_summary(route_analysis={"route_selected_total": {"x": "bad", "y": 0}}, blocker_analysis=[])
    _eq(zero_leader, "Feedback packet is available but source evidence is limited.")
    no_avg = rf._build_insight_summary(route_analysis={}, blocker_analysis=[], trade_report_summary={"closed_trade_count": 1, "win_count": 1, "pnl_pct_sample_count": 0})
    _eq(no_avg, "Same-day closed trade reports show 1 trades with 1 wins, 0 losses.")


def _write(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body), encoding="utf-8")


def test_feedback_packet_without_a_day_uses_only_the_current_payload(tmp_path):
    packet = rf.build_strategist_feedback_packet(
        mode="metrics_report", reports_root=tmp_path / "reports",
        payload={"route_selected_total": {"full_cycle": 2}, "dominant_blocker_total": {"gate": 3}, "generated_at": "t", "latest_run_id": "r1"})
    _eq((packet["available"], packet["source_day"], packet["packet_version"], packet["runtime_semantics_unchanged"]), (True, "", "strategist_feedback.v1", True))
    _eq((packet["source_reports"]["metrics"], packet["source_reports"]["current_payload"], packet["route_analysis"]["full_cycle_ratio"]), (True, True, 1.0))
    _eq(packet["blocker_analysis"][0]["blocker"], "gate")
    _eq(packet["confidence"], "low")
    _eq(packet["data_freshness"]["latest_run_id"], "r1")
    _eq(list(tmp_path.iterdir()), [])                                                                 # a day-less call never touches disk
    again = rf.build_strategist_feedback_packet(mode="metrics_report", reports_root=tmp_path / "reports", payload={
        "route_selected_total": {"full_cycle": 2}, "dominant_blocker_total": {"gate": 3}, "generated_at": "t", "latest_run_id": "r1"})
    _eq(again["feedback_id"], packet["feedback_id"])                                                  # content-addressed and stable
    empty = rf.build_strategist_feedback_packet(mode="x", reports_root=tmp_path / "reports", payload=None)
    _eq((empty["available"], empty["confidence"], empty["source_reports"]["current_payload"]), (False, "low", False))


def test_feedback_packet_with_a_day_reads_metrics_and_reporter_analysis_from_tmp_reports(tmp_path):
    root = tmp_path / "reports"
    _write(root / "metrics" / "metrics_2026-10-28.json", {"route_selected_total": {"monitor_only": 6, "full_cycle": 4}, "dominant_blocker_total": {"vwap_reclaim_fail": 5, "risk": 2},
                                                          "data_freshness": {"freshness_status": "fresh", "latest_run_id": "m1"}})
    _write(root / "dev" / "analysis" / "reporter_analysis" / "reporter_analysis_2026-10-28.json",
           {"improvement_suggestions": ["from reporter"], "monitor_evaluation": {"monitor_reason_top": {"x": 1}}})
    packet = rf.build_strategist_feedback_packet(mode="reporter_analysis_unused", payload={"day": "2026-10-28"}, reports_root=root)
    _eq((packet["source_day"], packet["source_reports"]["metrics"], packet["source_reports"]["reporter_analysis"]), ("2026-10-28", True, True))
    _eq(packet["route_analysis"]["monitor_only_ratio"], 0.6)
    _eq(packet["data_freshness"]["latest_run_id"], "m1")
    _eq(packet["confidence"], "medium")
    _eq(packet["recommendation"][0].startswith("Monitor-only share is high"), True)                  # metrics present -> generated recommendations win
    # reporter_analysis mode: its own recommendations replace the generated ones when no metrics exist
    only = rf.build_strategist_feedback_packet(mode="reporter_analysis", reports_root=tmp_path / "other",
                                               payload={"improvement_suggestions": ["fix a", "fix b"], "day": ""})
    _eq(only["recommendation"], ["fix a", "fix b"])
    # a balanced mix falls back to the reporter-analysis recommendations on disk
    _write(root / "metrics" / "metrics_2026-10-29.json", {"route_selected_total": {"full_cycle": 5}})
    _write(root / "dev" / "analysis" / "reporter_analysis" / "reporter_analysis_2026-10-29.json", {"improvement_suggestions": ["disk advice"]})
    balanced = rf.build_strategist_feedback_packet(mode="metrics_report", payload={"day": "2026-10-29"}, reports_root=root)
    _eq(balanced["recommendation"], ["disk advice"])
