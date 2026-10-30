"""P15 RF-035 (03h): report_source_helpers._event_route_rows moved to report_source_route_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import report_source_helpers as m
from libs.reporting import report_source_route_projection as owner


def _both(rows):
    return m._event_route_rows(iter(copy.deepcopy(rows))), owner._event_route_rows(iter(copy.deepcopy(rows)), facade=m)


ROWS = [
    {"run_id": "r1", "stage": "commander_router", "event": "route_selected", "payload": {"route_selected": "direct", "strategist_call_decision": "call"}},
    {"run_id": "r1", "stage": "strategist", "event": "policy_resolution", "payload": {"strategy_generation_mode": "shadow", "fallback_used": True}},
    {"run_id": "", "stage": "commander_router", "event": "route", "payload": {"route_selected": "ignored"}},
    {"run_id": "r2", "stage": "other", "event": "x", "payload": {}},
    {"run_id": "r3", "stage": "commander_router", "event": "end", "payload": "bad"},
]


def test_fold_and_defaults():
    a, b = _both(ROWS)
    assert a == b and list(a) == ["r1", "r3"]
    assert a["r1"] == {"route_selected": "direct", "strategy_generation_mode": "shadow", "strategist_call_decision": "call", "strategist_fallback_used": True, "route_source": "event_fallback", "artifact_path": ""}
    assert a["r3"]["route_selected"] == "" and a["r3"]["route_source"] == "event_fallback"


def test_empty_and_no_input_mutation():
    assert _both([]) == ({}, {})
    rows = copy.deepcopy(ROWS)
    m._event_route_rows(iter(rows))
    assert rows == ROWS


def test_iterator_consumed_in_order_once():
    seen = []

    def gen():
        for r in ROWS:
            seen.append(r["run_id"])
            yield copy.deepcopy(r)

    out = owner._event_route_rows(gen(), facade=m)
    assert seen == [r["run_id"] for r in ROWS] and "r1" in out


def test_facade_commander_route_seam(monkeypatch):
    calls = []
    monkeypatch.setattr(m, "_commander_route_from_payload", lambda payload, **kw: (calls.append(payload), {"route_selected": "SEAM", "strategy_generation_mode": "", "strategist_call_decision": "", "strategist_fallback_used": True})[1])
    a, b = _both(ROWS)
    assert a == b and a["r1"]["route_selected"] == "SEAM" and a["r1"]["strategist_fallback_used"] is True and len(calls) == 4
