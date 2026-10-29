from __future__ import annotations

from libs.contracts import agent_outputs


def test_strategist_projection_owner_preserves_event_payload_and_facade_monkeypatch(monkeypatch):
    monkeypatch.setattr(agent_outputs, "_clip", lambda value, **_: f"clip:{value or ''}")
    result = agent_outputs._build_global_sentiment_signal_payload(
        state={"strategist_global_sentiment_breakdown": {"event": "kept"}},
        global_signal={},
        macro_overlay={},
    )
    if result != {"event": "kept"}:
        raise AssertionError(result)
    result = agent_outputs._build_global_sentiment_signal_payload(
        state={},
        global_signal={"status": "ok", "source": "fake", "fear_index": {}},
        macro_overlay={},
    )
    if result["status"] != "clip:ok" or result["source"] != "clip:fake":
        raise AssertionError(result)

