"""RF-066 C1/C2: the graph demo explicitly disables market fallback."""

from __future__ import annotations

import json

from scripts.examples import demo_m22_graph_with_hydration as demo


def test_rf066_graph_demo_passes_offline_policy_to_graph(monkeypatch, capsys):
    observed = {}

    def fake_graph(state, *, strategist):
        observed["policy"] = dict(state["policy"])
        observed["symbols"] = [row["symbol"] for row in state["candidates"]]
        assert strategist(state) is state
        return {
            **state,
            "decision": "noop",
            "execution_pending": False,
            "selected": {"symbol": "005930", "score": 0.6, "risk_score": 0.2, "confidence": 0.82},
            "skill_fetch": {"source": "fake-graph"},
            "scanner_skill": {"fallback": False},
            "monitor": {"source": "fake-monitor"},
        }

    monkeypatch.setattr(demo, "run_trading_graph", fake_graph)

    assert demo.main(["--json"]) == 0

    assert observed == {
        "policy": {"scanner_feature_seed_with_yf": False},
        "symbols": ["005930", "000660", "035420"],
    }
    payload = json.loads(capsys.readouterr().out)
    assert payload["selected"]["symbol"] == "005930"
    assert payload["scanner_skill"]["fallback"] is False
