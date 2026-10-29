from __future__ import annotations

import json

from libs.contracts import agent_outputs


def test_strategist_projection_owner_preserves_event_payload_and_facade_monkeypatch(monkeypatch):
    monkeypatch.setattr(agent_outputs, "_clip", lambda value, **_: f"clip:{value or ''}")
    result = agent_outputs._build_global_sentiment_signal_payload(state={"strategist_global_sentiment_breakdown": {"event": "kept"}}, global_signal={}, macro_overlay={})
    if result != {"event": "kept"}:
        raise AssertionError(result)
    result = agent_outputs._build_global_sentiment_signal_payload(state={}, global_signal={"status": "ok", "source": "fake", "fear_index": {}}, macro_overlay={})
    if result["status"] != "clip:ok" or result["source"] != "clip:fake":
        raise AssertionError(result)


def test_strategist_projection_edge_contracts_and_owner_facade(monkeypatch):
    calls = []
    original_clip = agent_outputs._clip
    monkeypatch.setattr(agent_outputs, "_clip", lambda value, **kw: calls.append((value, kw)) or original_clip(value, **kw))
    trace = agent_outputs._build_strategist_trace_summary(strategist_output={"global_sentiment_score": 0, "reason_chain": []}, global_signal={"fear_index": {"level": 0}}, macro_overlay={}, news_context={}, themes=[], avoid_themes=[], market_regime="", market_sentiment="", playbook="")
    if trace["headline_count"] != 0 or trace["vix_level"] != 0 or trace["reason_chain"]:
        raise AssertionError(trace)
    if set(trace["missing_flags"]) != {"news_headlines_missing", "reason_chain_missing"}:
        raise AssertionError(trace)
    ranked = agent_outputs._build_strategist_news_evidence_ranked(state={}, strategist_output={"news_query_targets": ["one"]}, news_context={"count": 1}, market_news_context={"ranked_rows": [{"title": "m"}]}, candidate_news_context={"ranked_rows": [{"title": "c"}]})
    if ranked["news_query_targets"] != ["one"] or ranked["market_news_ranked"] != [{"title": "m"}]:
        raise AssertionError(ranked)
    frame = agent_outputs._build_strategist_decision_frame(state={}, strategist_output={"selected_themes": ["AI"], "reason_chain": ["evidence"]}, market_regime="risk_on", market_sentiment="positive", playbook="trend", themes=["AI"], avoid_themes=[])
    if frame["selected_themes"] != ["AI"] or frame["reason_chain"] != ["evidence"] or not calls:
        raise AssertionError(frame)


def test_strategist_public_artifact_is_json_serializable_and_keeps_input_unchanged():
    state = {"strategist_output": {"selected_themes": ["AI"], "reason_chain": ["signal"]}, "global_signal": {"fear_index": {"level": 19}}}
    before = json.dumps(state, sort_keys=True)
    artifact = agent_outputs.build_strategist_output_artifact(state)
    json.dumps(artifact, sort_keys=True)
    if json.dumps(state, sort_keys=True) != before:
        raise AssertionError(state)
