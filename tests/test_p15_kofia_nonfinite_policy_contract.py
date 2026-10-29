"""P15 C02-2: KOFIA yields reject non-finite numbers and malformed policy values locally; no real network."""
from __future__ import annotations

import math
from datetime import datetime

import pytest

from libs.market import korea_bond_yields as kb

XML = ('<message><BISComDspDatDTO><val1>20261028</val1><val2>3.5</val2><val3>3.6</val3></BISComDspDatDTO>'
       '<BISComDspDatDTO><val1>20261027</val1><val2>3.4</val2><val3>3.5</val3></BISComDspDatDTO></message>')


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for k in ("KOREA_BOND_YIELD_PROVIDER_ENABLED", "KOREA_BOND_YIELD_TIMEOUT_SEC", "KOREA_BOND_YIELD_LOOKBACK_DAYS"):
        monkeypatch.delenv(k, raising=False)


@pytest.fixture
def spy(monkeypatch):
    calls = []

    def fake(**kw):
        calls.append(kw)
        return XML

    monkeypatch.setattr(kb, "_fetch_kofia_xml", fake)

    def no_net(*a, **k):
        raise AssertionError("real network call")

    monkeypatch.setattr(kb.urllib.request, "urlopen", no_net)
    return calls


@pytest.mark.parametrize("v", ["nan", "inf", "-inf", "NaN", float("nan"), float("inf"), "", None, "x"])
def test_to_float_rejects_nonfinite_and_garbage(v):
    assert kb._to_float(v) is None


def test_to_float_keeps_finite_values():
    assert kb._to_float("3.5") == 3.5 and kb._to_float(" -0.25 ") == -0.25 and kb._to_float(2) == 2.0


def test_nonfinite_current_is_unavailable():
    rows = [{"val1": "20261028", "val2": "nan", "val3": "inf"}, {"val1": "20261027", "val2": "3.5", "val3": "3.4"}]
    for idx, key in ((2, "kr_3y_yield"), (3, "kr_10y_yield")):
        assert kb._indicator_from_rows(key=key, code_index=idx, rows=rows) == {
            "status": "unavailable", "source": "kofia", "ticker": kb.KOFIA_BOND_CODES[key], "reason": "kofia_value_missing"}


def test_nonfinite_previous_keeps_current_and_drops_delta():
    rows = [{"val1": "20261028", "val2": "3.5", "val3": "3.6"}, {"val1": "20261027", "val2": "nan", "val3": "inf"}]
    out = kb._indicator_from_rows(key="kr_3y_yield", code_index=2, rows=rows)
    assert out["status"] == "ok" and out["current"] == 3.5 and out["current_yield_pct"] == 3.5
    assert not {"previous", "previous_yield_pct", "delta", "previous_asof"} & set(out)


def test_finite_pair_delta_parity():
    rows = [{"val1": "20261028", "val2": "3.5"}, {"val1": "20261027", "val2": "3.4"}]
    out = kb._indicator_from_rows(key="kr_3y_yield", code_index=2, rows=rows)
    assert out == {"status": "ok", "source": "kofia", "reason": "kofia_latest_available", "ticker": "3000", "current": 3.5,
                   "current_yield_pct": 3.5, "asof": "20261028", "unit": "yield_pct", "previous": 3.4, "previous_yield_pct": 3.4,
                   "delta": float(3.5 - 3.4), "previous_asof": "20261027"}
    assert math.isfinite(out["delta"])


def _span(call):
    return (datetime.strptime(call["end_date"], "%Y%m%d") - datetime.strptime(call["start_date"], "%Y%m%d")).days


@pytest.mark.parametrize("timeout,lookback", [("bad", "nan"), ("nan", "inf"), (float("inf"), float("nan")), ("-inf", "x"), (-3, [])])
def test_malformed_policy_falls_back_to_defaults_without_raising(spy, timeout, lookback):
    out = kb.fetch_korea_bond_yield_overrides({"korea_bond_yield_timeout_sec": timeout, "korea_bond_yield_lookback_days": lookback})
    assert set(out) == {"kr_3y_yield", "kr_10y_yield"} and out["kr_3y_yield"]["status"] == "ok"
    assert len(spy) == 1 and spy[0]["timeout_sec"] == 8.0 and _span(spy[0]) == 14
    assert list(spy[0]["codes"]) == ["3000", "3013"]


def test_valid_policy_is_forwarded_unchanged(spy):
    out = kb.fetch_korea_bond_yield_overrides({"korea_bond_yield_timeout_sec": 4, "korea_bond_yield_lookback_days": 7})
    assert spy[0]["timeout_sec"] == 4.0 and _span(spy[0]) == 7
    assert out["kr_3y_yield"]["delta"] == pytest.approx(0.1) and out["kr_10y_yield"]["current"] == 3.6


def test_env_fallback_and_defaults_unchanged(spy, monkeypatch):
    kb.fetch_korea_bond_yield_overrides({})
    assert spy[0]["timeout_sec"] == 8.0 and _span(spy[0]) == 14
    monkeypatch.setenv("KOREA_BOND_YIELD_TIMEOUT_SEC", "5")
    monkeypatch.setenv("KOREA_BOND_YIELD_LOOKBACK_DAYS", "9")
    kb.fetch_korea_bond_yield_overrides(None)
    assert spy[1]["timeout_sec"] == 5.0 and _span(spy[1]) == 9


@pytest.mark.parametrize("flag", [False, "false", "0", "off", "No"])
def test_disabled_provider_makes_no_call(spy, flag):
    assert kb.fetch_korea_bond_yield_overrides({"korea_bond_yield_provider_enabled": flag}) == {} and spy == []


def test_fetch_error_still_returns_unavailable_rows(monkeypatch):
    def boom(**kw):
        raise OSError("down")
    monkeypatch.setattr(kb, "_fetch_kofia_xml", boom)
    out = kb.fetch_korea_bond_yield_overrides({"korea_bond_yield_timeout_sec": "bad"})
    assert out["kr_3y_yield"]["reason"] == "kofia_fetch_error:OSError" and out["kr_10y_yield"]["ticker"] == "3013"
