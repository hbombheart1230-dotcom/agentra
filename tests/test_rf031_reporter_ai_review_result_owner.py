"""P15 A1 (RF-031): reporter AI review result normalization moved to reporter_ai_review_result; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import reporter_ai_review as rv
from libs.reporting import reporter_ai_review_result as owner

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


def results():
    long = "가" * 700
    good = {"ai_summary": long, "ai_findings": [long] * 20, "ai_root_causes": ["a"] * 12, "ai_improvement_suggestions": ["b", "", None, "c"],
            "ai_run_grade": "A+" * 20, "ai_agent_evaluations": {f"k{i}": "v" * 200 for i in range(14)} | {"": "skip"},
            "ai_evidence_links": {"findings": [{"text": "t" * 400, "evidence_keys": [f"e{i}" for i in range(9)]}, "keystr", "", 5, None] * 4,
                                  "root_causes": [{"text": "r"}], "improvements": "notalist"}}
    return [good, {}, {"ai_evidence_links": "junk", "ai_run_grade": ""}, {"ai_findings": "notlist", "ai_agent_evaluations": []}]


LINK_CASES = [[{"text": "x" * 300, "evidence_keys": ["a"] * 9}, "s", 3], None, "x", ["k"] * 15]


@pytest.mark.parametrize("i", range(4))
def test_normalize_result_matches_pre_move_golden(i):
    obj = results()[i]
    snap = copy.deepcopy(obj)
    got = rv._normalize_result(obj, enabled=True, model="m")
    assert obj == snap
    assert _h(got) == GOLDEN["result"][i]
    assert _h(owner.normalize_result(obj, enabled=True, model="m", facade=rv)) == GOLDEN["result"][i]


@pytest.mark.parametrize("i", range(4))
def test_normalize_evidence_link_items_matches_pre_move_golden(i):
    assert _h(rv._normalize_evidence_link_items(LINK_CASES[i])) == GOLDEN["links"][i]
    assert _h(owner.normalize_evidence_link_items(LINK_CASES[i], facade=rv)) == GOLDEN["links"][i]


def test_result_shape_clipping_and_defaults():
    got = rv._normalize_result(results()[0], enabled=1, model=None)
    assert got["enabled"] is True and got["status"] == "ok" and got["llm_status"] == "ok" and got["model"] == "" and got["parse_mode"] == "full"
    assert len(got["ai_summary"]) == 600 and got["ai_summary"].endswith("...") and len(got["ai_findings"]) == 12
    assert got["ai_improvement_suggestions"] == ["b", "c"] and len(got["ai_run_grade"]) == 16 and len(got["ai_agent_evaluations"]) == 10
    links = got["ai_evidence_links"]
    assert len(links["findings"]) == 8 and links["root_causes"] == [{"text": "r", "evidence_keys": []}] and links["improvements"] == []
    assert {"text": "", "evidence_keys": ["keystr"]} in links["findings"]
    empty = rv._normalize_result({}, enabled=False, model="m")
    assert empty["ai_run_grade"] == "N/A" and empty["ai_evidence_links"] == {"findings": [], "root_causes": [], "improvements": []} and empty["ai_summary"] == ""


def test_facade_use_time_patches_reach_the_owner(monkeypatch):
    monkeypatch.setattr(rv, "required_key_metadata", lambda obj, keys: {"required_key_marker": list(keys)[:1]})
    got = rv._normalize_result({}, enabled=True, model="m")
    assert got["required_key_marker"] == ["ai_summary"]
    monkeypatch.setattr(rv, "REPORTER_AI_REVIEW_REQUIRED_KEYS", ["only"])
    assert rv._normalize_result({}, enabled=True, model="m")["required_key_marker"] == ["only"]
    monkeypatch.setattr(rv, "_normalize_evidence_link_items", lambda v, **k: ["PATCHED"])
    assert rv._normalize_result({"ai_evidence_links": {"findings": [1]}}, enabled=True, model="m")["ai_evidence_links"]["findings"] == ["PATCHED"]
    monkeypatch.setattr(rv, "_clip_str", lambda v, *, max_len=400: "CLIP")
    assert rv._normalize_result({"ai_summary": "x"}, enabled=True, model="m")["ai_summary"] == "CLIP"


def test_owner_does_not_import_the_facade_and_wrappers_are_thin():
    assert "import reporter_ai_review\n" not in inspect.getsource(owner)
    for fn in (rv._normalize_result, rv._normalize_evidence_link_items):
        assert len(inspect.getsource(fn).splitlines()) <= 3
