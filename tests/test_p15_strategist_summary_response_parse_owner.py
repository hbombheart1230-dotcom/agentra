"""P15 A3: strategist_llm_summary ``_parse_response_body`` moved to strategist_llm_summary_stage; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_stage as owner

GOLDEN = ["44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a", "f9d86028c6e0d64e225186f96acb69338b2c59764df79162107f5c4bb34d1310", "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a", "c8fe83d1b9e9b56158059f7fd890c50c5b91a75951faaca6774a2f5592356d03", "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a", "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a", "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a", "493a088d72ebad5fa37ca3a056b8461c3145bc88f4e4affaa2892016baa130f9", "613fe5aa65343dbb1b9abe6abac6773f5c91bd60d3f2ffb7e2eae69e1db8b227", "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a", "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a", "0d39f4372258aad0c0428f91e4bd17f49195f847d89ea447106f9dafef6c63f3", "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a", "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"]

PARSE = [
    {}, {"parsed_output": {"a": 1}}, {"parsed_output": {}}, {"response_text": '{"b": 2}'}, {"response_text": "[1]"}, {"response_text": "not json"}, {"response_text": "  "},
    {"attempts": [{"parsed_output": {"old": 1}}, {"raw_response_text": '{"new": 2}'}]}, {"attempts": [{"raw_response_text": '{"x": 1}'}, {"raw_response_text": "bad"}, "junk", {"parsed_output": {}}]},
    {"attempts": [{"raw_response_text": "bad"}]}, {"attempts": "x"}, {"parsed_output": {"p": 1}, "response_text": '{"q": 2}', "attempts": [{"parsed_output": {"r": 3}}]}, {"response_text": 5}, {"response_text": '{"a": 1} trailing'},
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(PARSE)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_unchanged(i):
    a = PARSE[i]
    snap = copy.deepcopy(a)
    assert _safe(lambda: m._parse_response_body(a)) == GOLDEN[i]
    assert _safe(lambda: owner.parse_response_body(a)) == GOLDEN[i]
    assert a == snap


def test_priority_reverse_attempt_scan_and_copy_semantics():
    f = m._parse_response_body
    assert f({}) == {} and f(PARSE[11]) == {"p": 1}                                    # parsed_output beats response_text beats attempts
    parsed = PARSE[1]["parsed_output"]
    out = f(PARSE[1])
    assert out == {"a": 1} and out is not parsed
    assert f(PARSE[3]) == {"b": 2} and f(PARSE[4]) == {} and f(PARSE[5]) == {} and f(PARSE[6]) == {}
    assert f(PARSE[7]) == {"new": 2}                                                    # attempts scanned newest first
    assert f(PARSE[8]) == {"x": 1} and f(PARSE[9]) == {} and f(PARSE[10]) == {}
    assert f(PARSE[13]) == {}                                                           # trailing garbage -> JSONDecodeError swallowed


def test_owner_has_no_facade_parameter():
    assert "facade" not in inspect.signature(owner.parse_response_body).parameters


def test_owner_does_not_import_the_summary_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.strategist_llm_summary import" not in src and "import strategist_llm_summary\n" not in src
    assert len(inspect.getsource(m._parse_response_body).splitlines()) <= 3
