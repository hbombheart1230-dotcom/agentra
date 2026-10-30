"""P15 RF-035 (03h): report_source_helpers._commander_route_from_payload moved to report_source_route_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import report_source_helpers as m
from libs.reporting import report_source_route_projection as owner


def _both(payload, **kw):
    return m._commander_route_from_payload(payload, **kw), owner._commander_route_from_payload(payload, **kw)


def test_route_observability_and_artifact():
    payload = {"route_observability": {"route_selected": "direct", "strategy_generation_mode": "shadow", "fallback_used": True}}
    snap = copy.deepcopy(payload)
    a, b = _both(payload, artifact_path="fake.json")
    assert a == b and payload == snap
    assert a == {"route_selected": "direct", "strategy_generation_mode": "shadow", "strategist_call_decision": "", "strategist_fallback_used": True, "route_source": "canonical_commander", "artifact_path": "fake.json"}
    assert list(a) == ["route_selected", "strategy_generation_mode", "strategist_call_decision", "strategist_fallback_used", "route_source", "artifact_path"]


def test_empty_and_precedence():
    exp = {"route_selected": "", "strategy_generation_mode": "", "strategist_call_decision": "", "strategist_fallback_used": False, "route_source": "", "artifact_path": ""}
    assert _both({}) == (exp, exp)
    payload = {"route_selected": " top ", "selected_route": "alt", "route_observability": {"route_selected": "obs"}, "commander_decision": {"route_selected": "dec", "strategist_call_decision": "call"}, "strategist_fallback_used": False,
               "route_observability_x": 1}
    a, b = _both(payload)
    assert a == b and a["route_selected"] == "top" and a["strategist_call_decision"] == "call" and a["strategist_fallback_used"] is False
    a, b = _both({"selected_route": "alt", "commander_decision": {"strategist_fallback_used": True}})
    assert a == b and a["route_selected"] == "alt" and a["strategist_fallback_used"] is True


def test_non_dict_subsections_ignored_and_non_dict_payload_raises():
    a, b = _both({"route_observability": "x", "commander_decision": 3})
    assert a == b and a["route_selected"] == ""
    for fn in (m._commander_route_from_payload, owner._commander_route_from_payload):
        with pytest.raises(AttributeError):
            fn(None)


def test_keyword_only_artifact_path():
    for fn in (m._commander_route_from_payload, owner._commander_route_from_payload):
        with pytest.raises(TypeError):
            fn({}, "x")
