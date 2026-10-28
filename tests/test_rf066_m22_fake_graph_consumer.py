"""RF-066 C2/C3: M22 demo delegates only to an injected graph consumer in tests."""

from __future__ import annotations

import json

from scripts.examples import demo_m22_graph_with_hydration as demo


def test_rf066_m22_demo_json_uses_fake_graph_state_and_timeout_flag(monkeypatch, capsys):
    received = []

    def fake_graph(state, *, strategist):
        received.append(state)
        assert strategist(state) is state
        return {
            **state,
            "decision": "hold",
            "execution_pending": True,
            "selected": {"symbol": "005930", "score": 0.6, "risk_score": 0.2, "confidence": 0.82},
            "skill_fetch": {"action": "error" if state["skill_runner"].fail else "ready"},
            "scanner_skill": {"source": "fake_graph"},
            "monitor": {"decision": "hold"},
        }

    monkeypatch.setattr(demo, "run_trading_graph", fake_graph)
    assert demo.main(["--json", "--simulate-timeout"]) == 0

    output = json.loads(capsys.readouterr().out)
    assert received[0]["skill_runner"].fail is True
    assert output["skill_fetch"] == {"action": "error"}
    assert output["selected"]["symbol"] == "005930"
