from __future__ import annotations

from libs.contracts import agent_outputs


def test_scanner_projection_owner_preserves_event_payload_and_empty_candidates():
    ranking = agent_outputs._build_scanner_candidate_ranking_table(
        state={"scanner_candidate_ranking_table": {"tie_break_rule": "explicit", "rows": [{"symbol": "A"}, "bad"]}},
        candidate_preview=[],
    )
    if ranking != {"tie_break_rule": "explicit", "rows": [{"symbol": "A"}]}:
        raise AssertionError(ranking)
    reason = agent_outputs._build_scanner_candidate_selection_reason(
        state={},
        selected_symbol="",
        selected_rank=0,
        selected_score_total=0.0,
        margin_vs_second=0.0,
        critical_positive_factors=[],
        critical_negative_factors=[],
        selection_summary="",
        runner_ups=[],
        selected={},
    )
    if reason["selected_symbol"] or not reason["why_selected"]:
        raise AssertionError(reason)
