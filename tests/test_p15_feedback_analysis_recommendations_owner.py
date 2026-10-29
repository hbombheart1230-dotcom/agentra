"""P15 A1: reporter_feedback ``_extract_reporter_analysis_recommendations`` moved to reporter_feedback_analysis; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import reporter_feedback as F
from libs.reporting import reporter_feedback_analysis as owner

GOLDEN = ["4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945", "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945", "3554d2b8a1e34099053865de8576d1460b807430ec8c6b85315c9607ba93d308", "ef469e5222d9f44c176d564a9302be9beca634bf01141376970298dd2f3bf0a1", "2a434ff107ef5d75b67636b0216a41a8930468705e3d3bf8606009f3b217e852", "d33b202c020cbde1c4a7bb26d0b02e66645407dcef42c63543cff899b8f979c8", "EXC:TypeError", "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945", "EXC:TypeError", "8d79cf00c75f03fba6c6dd6f395ed5cb9a76039316ce5b89d47e0c20c99cc6b5"]

RECOMM = [
    None, {}, {"improvement_suggestions": [" a ", "", None, "b"], "operator_facing_summary": {"recommended_actions": ["op1"]}},
    {"operator_facing_summary": {"recommended_actions": [" x ", "", "y", "z", "w", "v", "u"]}}, {"improvement_suggestions": ["1", "2", "3", "4", "5", "6"]},
    {"improvement_suggestions": "abc"}, {"improvement_suggestions": 5}, {"operator_facing_summary": "junk"}, {"operator_facing_summary": {"recommended_actions": 7}}, {"improvement_suggestions": [], "operator_facing_summary": {"recommended_actions": ["o"]}},
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(RECOMM)))
def test_wrapper_and_owner_match_pre_move_golden_and_input_unchanged(i):
    payload = RECOMM[i]
    snap = copy.deepcopy(payload)
    assert _safe(lambda: F._extract_reporter_analysis_recommendations(payload)) == GOLDEN[i]
    assert _safe(lambda: owner.extract_reporter_analysis_recommendations(payload)) == GOLDEN[i]
    assert payload == snap


def test_priority_strip_and_cap():
    f = F._extract_reporter_analysis_recommendations
    assert f(None) == [] and f({}) == []
    assert f(RECOMM[2]) == ["a", "b"]                                                  # direct suggestions win over operator actions; blanks dropped, stripped
    assert f(RECOMM[3]) == ["x", "y", "z", "w"]                                        # operator fallback, cap 4
    assert f(RECOMM[4]) == ["1", "2", "3", "4"]
    assert f(RECOMM[9]) == ["o"]                                                       # empty direct list falls through


def test_malformed_values_keep_original_exceptions():
    for bad in (RECOMM[6], RECOMM[8]):
        with pytest.raises(TypeError):
            F._extract_reporter_analysis_recommendations(bad)
    assert F._extract_reporter_analysis_recommendations(RECOMM[7]) == []
    assert F._extract_reporter_analysis_recommendations(RECOMM[5]) == ["a", "b", "c"]  # a bare string iterates by character


def test_owner_does_not_import_the_facade_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.reporter_feedback import" not in src and "import reporter_feedback\n" not in src
    assert len(inspect.getsource(F._extract_reporter_analysis_recommendations).splitlines()) <= 3
