"""P15: strategist_llm_summary ``_news_usage_lines`` moved to strategist_llm_summary_usage_lines.news_usage_lines; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_usage_lines as owner

GOLDEN = ["44edd8434898d9c1a81083479531262f4c017b068929387f68e5058370e318f0", "44edd8434898d9c1a81083479531262f4c017b068929387f68e5058370e318f0", "c238f34bc2b819054836b2f643d573387694cdc67e26f71c85994aa83587973b", "c72137ef67c1f5169e2a048b819383253cd0946d70ff33ef22d90b07b71cf935", "c72137ef67c1f5169e2a048b819383253cd0946d70ff33ef22d90b07b71cf935", "c72137ef67c1f5169e2a048b819383253cd0946d70ff33ef22d90b07b71cf935", "82680f29c66356a9cedbfe295aa72fee6561034d71cd6ab8477d4164b0ab0831"]

NEWS = [
    {}, {"available": False}, {"available": True, "query_targets": [f"q{i}" for i in range(11)], "human_summary": "요약", "market_effect": "me", "playbook_effect": "pe", "scanner_guidance_effect": "se", "monitor_policy_effect": "mp",
                              "market_headline_count": 3, "candidate_headline_count": 0, "news_query_reasoning": "qr"},
    {"available": True}, {"available": True, "query_targets": "junk", "market_headline_count": None}, {"available": True, "query_targets": []}, {"available": True, "query_targets": [None, "a"]},
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(NEWS)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_unchanged(i):
    a = NEWS[i]
    snap = copy.deepcopy(a)
    assert _safe(lambda: m._news_usage_lines(a)) == GOLDEN[i]
    assert _safe(lambda: owner.news_usage_lines(a, facade=m)) == GOLDEN[i]
    assert a == snap


def test_exact_lines_target_label_and_cap():
    f = m._news_usage_lines
    assert f({}) == ["- 뉴스 사용 trace: -"] and f({"available": False}) == ["- 뉴스 사용 trace: -"]
    out = f(NEWS[2])
    assert out[0] == "- 검색/수집 타깃: q0, q1, q2, q3, q4, q5, q6, q7, q8, q9" and "q10" not in out[0] and len(out) == 8
    assert out[6] == "- 근거 헤드라인 수: market=3, candidate=0" and out[7] == "- query reasoning: qr"
    assert f(NEWS[3])[0] == "- 검색/수집 타깃: -" and f(NEWS[4])[0] == "- 검색/수집 타깃: -" and f(NEWS[5])[0] == "- 검색/수집 타깃: -"
    assert f(NEWS[6])[0] == "- 검색/수집 타깃: None, a"
    assert m._news_usage_lines_clean(NEWS[2])[0].startswith("- 검색/수집 대상:")                      # the sibling variant keeps its own label


def test_facade_helpers_use_time_patches_reach_the_owner(monkeypatch):
    monkeypatch.setattr(m, "_as_list", lambda v: ["A", "B"])
    assert m._news_usage_lines({"available": True})[0] == "- 검색/수집 타깃: A, B"
    monkeypatch.setattr(m, "_text", lambda v, d="-": "TXT")
    assert m._news_usage_lines({"available": True})[1] == "- 사용 요약: TXT"


def test_owner_does_not_import_the_summary_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.strategist_llm_summary import" not in src and "import strategist_llm_summary\n" not in src
    assert len(inspect.getsource(m._news_usage_lines).splitlines()) <= 3
