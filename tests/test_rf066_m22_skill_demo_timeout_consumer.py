"""RF-066 C2/C3: M22 skill demo forwards timeout state through fake nodes."""

from __future__ import annotations

import json

from scripts.examples import demo_m22_skill_flow as demo


def test_rf066_mr22_skill_demo_timeout_json_uses_fake_scanner_and_monitor(monkeypatch, capsys):
    calls = []

    def fake_scanner(state):
        calls.append(("scanner", state))
        assert state["skill_results"]["market.quote"]["meta"]["error_type"] == "TimeoutError"
        return {
            **state,
            "selected": {"symbol": "000660", "score": 0.4, "risk_score": 0.3, "confidence": 0.7},
            "scan_results": [{"symbol": "000660", "features": {"skill_quote_price": None, "skill_open_orders": 0}}],
            "scanner_skill": {"contract_version": "m22.skill.v1", "fallback": True, "source": "fake-scanner"},
        }

    def fake_monitor(state):
        calls.append(("monitor", state))
        assert state["scanner_skill"]["fallback"] is True
        return {
            **state,
            "monitor": {
                "skill_contract_version": "m22.skill.v1",
                "order_status_fallback": True,
                "source": "fake-monitor",
            },
        }

    monkeypatch.setattr(demo, "scanner_node", fake_scanner)
    monkeypatch.setattr(demo, "monitor_node", fake_monitor)

    assert demo.main(["--simulate-timeout", "--json"]) == 0

    output = json.loads(capsys.readouterr().out)
    assert output["selected"]["symbol"] == "000660"
    assert output["scanner_skill"]["source"] == "fake-scanner"
    assert output["monitor"]["source"] == "fake-monitor"
    assert output["order_lifecycle"] is None
    assert [name for name, _state in calls] == ["scanner", "monitor"]
