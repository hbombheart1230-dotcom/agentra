from __future__ import annotations

import copy

from libs.contracts import agent_outputs
from libs.contracts.agent_output_parts.commander_shadow_evidence import (
    build_context_delta_summary,
    build_monitor_gate_details,
)


def test_gate_owner_wrapper_and_boundaries(monkeypatch):
    state = {"monitor_entry": {"metrics": {"pullback_ok": False, "current_price": 11}, "passed_checks": ["breakout_ok"] + ["p"] * 9, "failed_checks": ["volume_ok"] + ["f"] * 9, "thresholds": {"a": 1}}}
    before = copy.deepcopy(state)
    wrapped = agent_outputs._commander_shadow_monitor_gate_details(state)
    owner = build_monitor_gate_details(state, facade=agent_outputs)
    assert wrapped == owner and wrapped["pullback_passed"] is False
    assert len(wrapped["passed_gates"]) == len(wrapped["failed_gates"]) == 8
    assert wrapped["observed_features"]["price"] == 11 and state == before
    calls = []
    monkeypatch.setattr(agent_outputs, "_gate_pass", lambda *args: calls.append(args[-1]) or "spy")
    assert build_monitor_gate_details({}, facade=agent_outputs)["breakout_passed"] == "spy"
    assert calls == ["breakout_ok", "volume_ok", "extension_ok"]


def test_delta_owner_wrapper_thresholds_and_fallback():
    def state(delta):
        return {"commander_shadow_runtime": {"prior_context": {"selected_symbol": "A", "global_sentiment_score": 0, "vix_level": 10, "selected_score_total": 1}}, "selected": {"symbol": "A", "score_total": 1 + delta}, "strategist_output": {"global_sentiment_score": delta, "macro_stress_overlay": {"vix_level": 10 + delta}}}
    observations = {"last_llm_status": "ok"}
    for delta, expected in ((0.029, False), (0.030, True), (1.0, True)):
        value = state(delta)
        wrapped = agent_outputs._commander_shadow_context_delta_summary(value, observations=observations)
        owner = build_context_delta_summary(value, observations=observations, facade=agent_outputs)
        assert wrapped == owner
        if delta < 1:
            assert wrapped["sentiment_changed"] is expected
    assert build_context_delta_summary({}, observations=observations, facade=agent_outputs)["symbol_same_as_last"] is None
