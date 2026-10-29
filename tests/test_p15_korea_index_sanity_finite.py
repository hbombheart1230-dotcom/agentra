"""P15 C02-2 (FAST-3): Korea index sanity ignores non-finite numbers; thresholds and keys unchanged."""
from __future__ import annotations

import copy
import json

import pytest

from libs.market.korea_index_sanity import korea_index_sanity as sanity


@pytest.mark.parametrize("v", ["nan", "inf", "-inf", float("nan"), float("inf")])
def test_to_float_nonfinite_gives_default(v):
    from libs.market import korea_index_sanity as m
    assert m._to_float(v) is None and m._to_float(v, 1.5) == 1.5
    assert m._to_float("2.5") == 2.5 and m._to_float("") is None and m._to_float(None, 3.0) == 3.0


def test_nonfinite_kospi_gives_no_false_warning_and_kosdaq_two_warnings():
    packet = {"indices": {"KOSPI": {"change_pct": "nan", "high": "inf", "low": "10", "current": "10"},
                          "KOSDAQ": {"change_pct": "6.5", "current": "101", "high": "100", "low": "99"}}}
    snap = copy.deepcopy(packet)
    out = sanity(packet)
    assert packet == snap
    assert [w["index"] for w in out["warnings"]] == ["KOSDAQ", "KOSDAQ"]
    assert [w["code"] for w in out["warnings"]] == ["extreme_index_change_pct", "index_current_outside_high_low"]
    assert out["warnings"][0]["severity"] == "warning" and out["status"] == "warning" and out["warning_count"] == 2
    assert out["extreme_move_requires_confirmation"] is True
    json.dumps(out, allow_nan=False)


def test_nonfinite_fields_inside_a_valid_extreme_row_become_none():
    out = sanity({"indices": {"KOSPI": {"change_pct": "7", "high": "inf", "low": "nan", "current": "100", "open": "-inf"}}})
    w = out["warnings"][0]
    assert w["severity"] == "warning" and w["high"] is None and w["low"] is None and w["open"] is None and w["current"] == 100.0
    json.dumps(out, allow_nan=False)


def test_valid_critical_high_below_low_and_thresholds():
    c = sanity({"indices": {"KOSPI": {"change_pct": "10.1"}}})["warnings"][0]
    assert c["severity"] == "critical"
    assert sanity({"indices": {"KOSPI": {"change_pct": "9.99"}}})["warnings"][0]["severity"] == "warning"
    assert sanity({"indices": {"KOSPI": {"change_pct": "-6.0"}}})["warnings"][0]["severity"] == "warning"
    assert sanity({"indices": {"KOSPI": {"change_pct": "5.99"}}})["status"] == "ok"
    h = sanity({"indices": {"KOSDAQ": {"change_pct": "1", "high": "90", "low": "100"}}})["warnings"]
    assert [(x["code"], x["severity"]) for x in h] == [("index_high_below_low", "critical")]


def test_empty_and_non_mapping_indices_are_ok():
    expected = {"status": "ok", "warning_count": 0, "warnings": [], "extreme_move_requires_confirmation": False}
    for packet in ({}, {"indices": []}, {"indices": "x"}, {"indices": {"KOSPI": "bad"}}, {"indices": {"OTHER": {"change_pct": "50"}}}):
        assert sanity(packet) == expected
