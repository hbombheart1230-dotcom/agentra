"""P15 A1 (RF-031): reporter AI review compact input / prompt messages moved to reporter_ai_review_input; byte parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import reporter_ai_review as rv
from libs.reporting import reporter_ai_review_input as owner

GOLDEN = {
    "compact": [
        "40d93010b83b9b8b9dc9b60dc3fe89ea681d83307969e7eabbf1f951311c5e5f",
        "ffc284577adccc9d6f5c55c80365030898ef95b5c56634d0abc56d98fbced887",
        "ffc284577adccc9d6f5c55c80365030898ef95b5c56634d0abc56d98fbced887"
    ],
    "messages": [
        "e8e8adf2d01797d304569e658221b2b58442b992f21d527c0cf02f6a97968e7a",
        "cf507548ea4744f1b401d3360f6d7825ef9f8ba304adb285b41005e035e9d41f",
        "cf507548ea4744f1b401d3360f6d7825ef9f8ba304adb285b41005e035e9d41f"
    ],
    "result": [
        "e54dbb000e4da1f189ef842d71cb602168bb1b9bafb66b88ad5e0969c650ba46",
        "19880a63a92c0f913606ed4f097a8999e20cd956fe629292216d615eb21c0a57",
        "1e4fc7086b9a461c5b4ef059b6084571382b012c68d725dcaa5624dbddead5ce",
        "4bd68dd52a16d1b5cd6a1f2df482a5d8f94f035fd501e325762027c4d5a5f3dc"
    ],
    "links": [
        "412d686e0902862162145d421f63471b9bac506ec40f7c15ab1b6de45945efe9",
        "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
        "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
        "dc47785e10c1925a96b687c8f87e04fae8a4715bebc3abba956ad947f04fab6b"
    ]
}


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False).encode()).hexdigest()


def reporter_outputs():
    full = {
        "trade_summary": {"trade_count": "3", "symbols_traded": list("ABCDEFGHIJ")},
        "strategist_evaluation": {"theme_alignment_status": "ok", "themes_proposed": list("abcdefghij"), "assessment": "한글 평가 " * 60},
        "scanner_evaluation": {"selection_status": "s", "no_candidate_total": "2", "selected_symbol_top": {"005930": 3}, "assessment": "x"},
        "monitor_evaluation": {"monitor_status": "m", "rapid_buy_sell_cycles": 1, "monitor_reason_top": {"r": 1}, "assessment": "y"},
        "supervisor_activity": {"blocked_rate": 0.5, "blocked_total": 4, "blocked_reason_top": {"g": 2}, "assessment": "z"},
        "intent_flow_analysis": {"intents_created": 5, "intents_blocked": 1, "intents_approved": 3, "intents_executed": 2, "reason_top": {"a": 1}},
        "incident_postmortem": {"incidents": [{"id": 1}]},
        "market_context": {"global_sentiment_avg": 0.1, "symbol_sentiment_avg": -0.2, "llm_provider_top": "p", "llm_model_top": "m"},
        "overtrading_diagnostics": {"rapid_buy_sell_cycles": 2, "guard_block_rate": 0.3, "noise_exit_related_count": "7"},
        "decision_trace_chain_summary": {"chains": [
            {"run_id": "r" * 100, "strategist": {"market_regime": "bull", "themes": list("123456"), "playbook": "pb", "risk_tone": "t", "monitor_guidance": "g"},
             "scanner": {"candidate_pool_size": "9", "selected_symbol": "005930", "top_candidates": ["a", "b", "c", "d"]},
             "monitor": {"monitor_reason": "mr", "exit_reason": "er", "min_hold_blocked": 1, "sell_cooldown_blocked": 0},
             "supervisor": {"verdict": "ok", "guard_reason": "gr"}, "executor": {"fill_status_summary": "filled"}, "complete_chain": True},
            "junk", None, {"run_id": "r2"}] + [{"run_id": f"x{i}"} for i in range(15)]},
        "ai_evidence_catalog": {f"k{i}": {"summary": "요약 " * 100} for i in range(12)} | {"bad": "str"},
        "improvement_suggestions": [f"s{i}" for i in range(12)],
    }
    return [full, {}, {"trade_summary": "junk", "decision_trace_chain_summary": {"chains": None}, "ai_evidence_catalog": [], "improvement_suggestions": None}]



DAY = "2026-10-20"


@pytest.mark.parametrize("i", [0, 1, 2])
def test_compact_input_and_messages_match_pre_move_golden(i):
    out = reporter_outputs()[i]
    snap = copy.deepcopy(out)
    compact = rv._build_compact_input(DAY, out)
    assert out == snap                                                     # input untouched
    assert _h(compact) == GOLDEN["compact"][i]
    assert _h(rv._build_messages(DAY, compact)) == GOLDEN["messages"][i]
    assert _h(owner.build_compact_input(DAY, out, facade=rv)) == GOLDEN["compact"][i]
    assert _h(owner.build_messages(DAY, compact, facade=rv)) == GOLDEN["messages"][i]


def test_compact_input_limits_and_key_order():
    c = rv._build_compact_input(DAY, reporter_outputs()[0])
    assert list(c) == ["day", "evidence_catalog_summary", "market_context", "trade_summary", "strategist_evaluation", "scanner_evaluation",
                       "monitor_evaluation", "supervisor_activity", "intent_flow_analysis", "overtrading_diagnostics", "incidents",
                       "improvement_suggestions", "decision_trace_chain_samples"]
    assert len(c["evidence_catalog_summary"]) == 10 and len(c["decision_trace_chain_samples"]) == 10     # first 12 chain rows, non-dict rows skipped
    assert len(c["trade_summary"]["symbols_traded"]) == 8 and len(c["improvement_suggestions"]) == 8 and c["trade_summary"]["trade_count"] == 3
    first = c["decision_trace_chain_samples"][0]
    assert len(first["run_id"]) == 80 and first["run_id"].endswith("...") and first["strategist"]["themes"] == ["1", "2", "3", "4"]


def test_messages_prompt_shape_and_korean_not_escaped():
    msgs = rv._build_messages(DAY, {"한글": "값"})
    assert [m["role"] for m in msgs] == ["system", "user"] and msgs[1]["content"].startswith(f"Day: {DAY}\n")
    assert '"한글": "값"' in msgs[1]["content"] and "\\u" not in msgs[1]["content"]


def test_facade_use_time_patches_reach_the_owner(monkeypatch):
    seen = []
    monkeypatch.setattr(rv, "_clip_str", lambda v, *, max_len=400: (seen.append("clip"), "C")[1])
    monkeypatch.setattr(rv, "_list_str", lambda v, **k: (seen.append("list"), ["L"])[1])
    c = rv._build_compact_input(DAY, reporter_outputs()[0])
    assert c["strategist_evaluation"]["assessment"] == "C" and c["decision_trace_chain_samples"][0]["strategist"]["themes"] == ["L"]
    assert {"clip", "list"} <= set(seen)
    calls = []
    monkeypatch.setattr(rv.json, "dumps", lambda obj, **k: (calls.append(k), "DUMPED")[1])
    msgs = rv._build_messages(DAY, {"a": 1})
    assert "DUMPED" in msgs[1]["content"] and calls and calls[0] == {"ensure_ascii": False}


def test_owner_does_not_import_the_facade_and_wrappers_are_thin():
    assert "reporter_ai_review import" not in inspect.getsource(owner).replace("reporter_ai_review_input", "")
    assert "import reporter_ai_review\n" not in inspect.getsource(owner)
    for fn in (rv._build_compact_input, rv._build_messages):
        assert len(inspect.getsource(fn).splitlines()) <= 3
