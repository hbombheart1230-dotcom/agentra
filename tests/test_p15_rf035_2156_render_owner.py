"""P15 RF-035 (2156): controlled_validation_daily.render_controlled_validation_daily_lines moved to controlled_validation_daily_format_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import controlled_validation_daily as m
from libs.reporting import controlled_validation_daily_format_projection as owner


def _both(payload):
    return m.render_controlled_validation_daily_lines(payload), owner.render_controlled_validation_daily_lines(payload, facade=m)


def test_empty_payload():
    exp = ["", "## Controlled Validation Lanes", "", "- Opening Alpha: evaluated 0 / eligible 0 / applied 0 / submitted 0 / reasons -"]
    assert _both({"lanes": [], "opening_alpha": {}}) == (exp, exp)
    assert _both({}) == (exp, exp)


def test_lane_and_broker_detail():
    payload = {
        "lanes": [{"label": "L1", "evaluation_status": "OK", "reason": "", "attempt_count": 2, "submission_count": 1}, "x"],
        "opening_alpha": {"evaluation_count": 3, "eligible_count": 2, "applied_count": 1, "submission_count": 2, "reason_counts": {"a": 1, "b": 2},
                          "broker_submission_attempted_count": 2, "submission_candidate_count": 4, "broker_outcome_counts": {"R": 1}},
    }
    snap = copy.deepcopy(payload)
    a, b = _both(payload)
    assert a == b and payload == snap
    assert a[3] == "- L1: `OK` / reason `-` / attempts 2 / accepted 1"
    assert a[4] == "- Opening Alpha: evaluated 3 / eligible 2 / applied 1 / submitted 2 / reasons a=1, b=2"
    assert a[5] == "- Opening Alpha submissions (detail): probe_reservation_claimed 4 / broker_submission_attempted 2 / broker_outcomes R=1"
    assert len(a) == 6


def test_malformed_count_raises_same():
    payload = {"lanes": [{"attempt_count": "x"}], "opening_alpha": {}}
    for fn in (lambda: m.render_controlled_validation_daily_lines(payload), lambda: owner.render_controlled_validation_daily_lines(payload, facade=m)):
        with pytest.raises(ValueError):
            fn()
