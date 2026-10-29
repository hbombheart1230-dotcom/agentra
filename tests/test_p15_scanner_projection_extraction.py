from __future__ import annotations

import json

from libs.contracts import agent_outputs


def test_scanner_projection_owner_preserves_event_payload_and_empty_candidates():
    ranking = agent_outputs._build_scanner_candidate_ranking_table(state={"scanner_candidate_ranking_table": {"tie_break_rule": "explicit", "rows": [{"symbol": "A"}, "bad"]}}, candidate_preview=[])
    if ranking != {"tie_break_rule": "explicit", "rows": [{"symbol": "A"}]}:
        raise AssertionError(ranking)
    reason = agent_outputs._build_scanner_candidate_selection_reason(state={}, selected_symbol="", selected_rank=0, selected_score_total=0.0, margin_vs_second=0.0, critical_positive_factors=[], critical_negative_factors=[], selection_summary="", runner_ups=[], selected={})
    if reason["selected_symbol"] or not reason["why_selected"]:
        raise AssertionError(reason)


def test_scanner_projection_edge_contracts_and_owner_facade(monkeypatch):
    calls = []
    original_safe_float = agent_outputs._safe_float
    monkeypatch.setattr(agent_outputs, "_safe_float", lambda value, default=0.0: calls.append(value) or original_safe_float(value, default))
    trace = agent_outputs._build_scanner_trace_summary(symbol="A", selected_rank=1, universe_size=3, selected_score_total=0.0, margin_vs_second=0.0, selected_score_breakdown={"up": 1, "down": -1, "zero": 0}, selected={"candidate": {"sources": ["x"]}}, candidate_preview=[{"symbol": "A"}, "not-a-row", {"symbol": "B", "score_total": 2}, {"symbol": "C"}], selection_summary="")
    if trace["critical_positive_factors"] != ["up:1.000"] or trace["critical_negative_factors"] != ["down:-1.000"]:
        raise AssertionError(trace)
    if [row["symbol"] for row in trace["runner_ups"]] != ["B"] or not calls:
        raise AssertionError(trace)
    table = agent_outputs._build_scanner_candidate_ranking_table(state={"scanner_candidate_ranking_table": {"tie_break_rule": "custom", "rows": [{"symbol": "A"}, "bad"]}}, candidate_preview=[])
    if table != {"tie_break_rule": "custom", "rows": [{"symbol": "A"}]}:
        raise AssertionError(table)


def test_scanner_public_artifact_is_json_serializable_and_keeps_input_unchanged():
    state = {"scanner_output": {"candidate_pool_size": 1}, "ranked_candidates": [{"symbol": "A", "score_total": 1.0}], "selected": {"symbol": "A", "candidate": {"sources": ["x"]}}}
    before = json.dumps(state, sort_keys=True)
    artifact = agent_outputs.build_scanner_output_artifact(state)
    json.dumps(artifact, sort_keys=True)
    if json.dumps(state, sort_keys=True) != before:
        raise AssertionError(state)
