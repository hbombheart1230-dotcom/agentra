from __future__ import annotations

from graphs.nodes import strategist_node
from libs.runtime.strategist.llm.repair_messages import build_repair_messages


def test_repair_owner_wrapper_parity_with_korean_payload():
    payload = {"call_kind": "selected_symbol_tactical_refresh", "available_themes": ["반도체"]}
    wrapped = strategist_node._build_strategist_llm_repair_messages(payload, "{bad")
    owner = build_repair_messages(payload, "{bad", facade=strategist_node)
    assert wrapped == owner and len(wrapped) == 2
    assert "selected_symbol_decision" in wrapped[1]["content"]


def test_repair_owner_empty_raw_and_late_bound_failure(monkeypatch):
    monkeypatch.setattr(strategist_node, "_classify_llm_parse_failure", lambda raw: "SPY_FAILURE")
    output = build_repair_messages({}, None, facade=strategist_node)
    assert "SPY_FAILURE" in output[1]["content"]
    assert output[0]["role"] == "system" and output[1]["role"] == "user"
