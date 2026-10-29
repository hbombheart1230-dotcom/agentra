"""P15 C02-3: Korea index inputs ignore non-finite numbers but keep valid values; public unavailable->NaN untouched."""
from __future__ import annotations

import copy
import inspect
import math
import socket

import pytest

from libs.market import global_sentiment as gs


@pytest.mark.parametrize("v", ["nan", "inf", "-inf", float("nan"), float("inf"), "x", None, [], {}])
def test_as_float_nonfinite_and_garbage_use_default(v):
    assert gs._as_float(v, 0.0) == 0.0 and gs._as_float(v, 7.5) == 7.5


def test_as_float_valid_values_pass_through():
    assert gs._as_float("1.5") == 1.5 and gs._as_float(3) == 3.0 and gs._as_float(" -2 ") == -2.0 and gs._as_float("1e3") == 1000.0


def _mixed():
    return {"indices": {"KOSPI": {"change_pct": "nan", "rising": "inf", "falling": "2"},
                        "KOSDAQ": {"change_pct": "1.5", "rising": "1", "falling": "0"}}}


def test_normalize_packet_keeps_valid_kosdaq_and_zeroes_nonfinite_kospi():
    raw = _mixed()
    snap = copy.deepcopy(raw)
    out = gs._normalize_korea_index_packet(raw)
    assert raw == snap                                                       # input untouched
    assert out["rising"] == 1 and out["falling"] == 2 and out["unchanged"] == 0
    assert out["breadth"] == pytest.approx((1 - 2) / 3)
    assert out["average_change_pct"] == pytest.approx(0.75)                  # KOSPI nan -> 0, KOSDAQ 1.5
    assert out["indices"]["KOSDAQ"]["change_pct"] == "1.5" and out["indices"]["KOSPI"]["change_pct"] == "nan"   # original fields preserved
    assert math.isfinite(out["breadth"]) and math.isfinite(out["average_change_pct"])


@pytest.mark.parametrize("bad", ["inf", "-inf", "nan"])
def test_every_count_field_tolerates_nonfinite(bad):
    raw = {"indices": {"KOSPI": {"change_pct": 1.0, "rising": bad, "falling": bad, "unchanged": bad}}}
    out = gs._normalize_korea_index_packet(raw)
    assert (out["rising"], out["falling"], out["unchanged"]) == (0, 0, 0) and out["breadth"] is None and out["average_change_pct"] == 1.0


def test_normal_packet_parity():
    raw = {"source": "s", "indices": {"KOSPI": {"change_pct": "1.0", "rising": 300, "falling": 100, "unchanged": 100},
                                      "KOSDAQ": {"change_pct": -0.5, "rising": "200", "falling": 400, "unchanged": 0},
                                      "KOSPI200": {"change_pct": 0.5}}}
    out = gs._normalize_korea_index_packet(raw)
    assert (out["rising"], out["falling"], out["unchanged"]) == (500, 500, 100)
    assert out["breadth"] == pytest.approx(0.0) and out["average_change_pct"] == pytest.approx((1.0 - 0.5 + 0.5) / 3)
    assert out["source"] == "s" and out["status"] == "ok" and set(out["indices"]) == {"KOSPI", "KOSDAQ", "KOSPI200"}
    assert gs._normalize_korea_index_packet({}) is None and gs._normalize_korea_index_packet({"indices": {"X": {}}}) is None


def test_compute_korea_raw_treats_nonfinite_as_zero_and_keeps_valid():
    got = gs._compute_korea_raw(_mixed(), w_kospi=0.3, w_kosdaq=0.25)
    assert got == pytest.approx(0.25 * 0.015) and math.isfinite(got)
    assert gs._compute_korea_raw({"indices": {"KOSPI": {"change_pct": "2"}, "KOSDAQ": {"change_pct": "-1"}}}, w_kospi=0.3, w_kosdaq=0.25) == pytest.approx(0.3 * 0.02 - 0.25 * 0.01)
    assert gs._compute_korea_raw(None, w_kospi=1, w_kosdaq=1) == 0.0


def test_dry_run_signal_makes_no_socket_calls(monkeypatch):
    def deny(*a, **k):
        raise AssertionError("socket used")
    monkeypatch.setattr(socket, "socket", deny)
    monkeypatch.setattr(socket, "create_connection", deny)
    monkeypatch.setenv("DRY_RUN", "1")
    sig = gs.compute_global_sentiment_signal({})
    assert sig["status"] == "fallback" and sig["source"] == "dry_run_policy" and sig["score"] == 0.0
    assert gs.compute_global_sentiment({}) == 0.0


def test_public_unavailable_nan_contract_is_statically_unchanged():
    src = inspect.getsource(gs.compute_global_sentiment)
    assert "SIGNAL_STATUS_UNAVAILABLE" in src and 'return float("nan")' in src
