from __future__ import annotations

import copy

from graphs.nodes import strategist_node
from libs.runtime.strategist.context.token_budget import apply_frame_token_budget


def _payload():
    return {"call_kind": "selected_symbol_tactical_refresh", "theme_strength_packet": {"a": 1}, "theme_strength": {"x": 1}, "candidate_news_signal_summary": list(range(7)), "market_news_signal_summary": list(range(6)), "available_themes": [{"component_symbols": list("ABCDE")} for _ in range(5)], "recent_strategy_feedback": {"top_recent_weaknesses": [1, 2, 3]}, "reporter_feedback_packet": {"recommendation": [1, 2, 3]}, "strategy_memory": {"best_playbooks": [1, 2, 3]}, "memory_packets": {"daily_strategy_memory": {"x": 1}}}


def test_owner_matches_wrapper_and_caps_without_input_mutation():
    payload = _payload()
    before = copy.deepcopy(payload)
    wrapped = strategist_node._apply_strategist_llm_token_budget(payload, memory_usage_disabled=True)
    owner = apply_frame_token_budget(payload, memory_usage_disabled=True, facade=strategist_node)
    assert wrapped == owner and payload == before
    assert len(wrapped["candidate_news_signal_summary"]) == 4
    assert len(wrapped["market_news_signal_summary"]) == 3
    assert len(wrapped["available_themes"]) == 4
    assert len(wrapped["available_themes"][0]["component_symbols"]) == 3
    assert wrapped["token_budget_policy"]["memory_usage_disabled"] is True


def test_market_frame_returns_early_and_helper_is_late_bound(monkeypatch):
    calls = []
    monkeypatch.setattr(strategist_node, "_resolve_strategist_llm_call_kind", lambda value: "market_strategy_frame")
    monkeypatch.setattr(strategist_node, "_theme_packet_summary_for_llm", lambda value: calls.append(value) or {"spy": True})
    value = apply_frame_token_budget({"theme_strength_packet": {"raw": 1}}, memory_usage_disabled=False, facade=strategist_node)
    assert value["theme_strength_packet_summary"] == {"spy": True}
    assert "candidate_news_sample" not in value and calls == [{"raw": 1}]
