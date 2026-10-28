"""RF-051 C1/C2 evidence: korea_bond_yields (fake urlopen) and korea_index_sanity (pure).

Every test runs with socket.connect denied, so a regression that reaches the
real KOFIA endpoint fails loudly instead of touching the network.
"""
from __future__ import annotations

import socket

import pytest

from libs.market import korea_bond_yields as kb
from libs.market import korea_index_sanity as ks


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    def deny(*_a, **_k):
        raise AssertionError("real network attempted")

    monkeypatch.setattr(socket.socket, "connect", deny)
    monkeypatch.setattr(socket, "create_connection", deny)
    monkeypatch.delenv("KOREA_BOND_YIELD_PROVIDER_ENABLED", raising=False)
    monkeypatch.delenv("KOREA_BOND_YIELD_TIMEOUT_SEC", raising=False)
    monkeypatch.delenv("KOREA_BOND_YIELD_LOOKBACK_DAYS", raising=False)


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


XML = (
    "<message><BISComDspDatDTO><val1>2026/10/27</val1><val2>3.10</val2><val3>3.40</val3></BISComDspDatDTO>"
    "<BISComDspDatDTO><val1>2026/10/28</val1><val2>3.20</val2><val3></val3></BISComDspDatDTO>"
    "<BISComDspDatDTO><val1>합계</val1><val2>9</val2></BISComDspDatDTO></message>"
)


class _Resp:
    def __init__(self, body):
        self._b = body

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_to_float_and_date_range_and_request_body():
    _eq(kb._to_float(" 3.5 "), 3.5)
    for bad in (None, "", "  ", "x"):
        _eq(kb._to_float(bad), None)
    start, end = kb._date_range(14)
    if not (len(start) == len(end) == 8 and start < end):
        raise AssertionError((start, end))
    s3, e3 = kb._date_range(0)            # lookback is floored at 3 days
    from datetime import datetime

    _eq((datetime.strptime(e3, "%Y%m%d") - datetime.strptime(s3, "%Y%m%d")).days, 3)
    body = kb._request_body("20261001", "20261028", ["A", "B"]).decode("utf-8")
    for token in ("<val2>20261001</val2>", "<val3>20261028</val3>", "<val5>A</val5>", "<val6>B</val6>"):
        if token not in body:
            raise AssertionError(token)


def test_rows_sorted_desc_and_non_date_rows_dropped():
    rows = kb._rows_from_xml(XML)
    _eq([r["val1"] for r in rows], ["2026/10/28", "2026/10/27"])


def test_indicator_from_rows_current_previous_delta_and_missing():
    rows = kb._rows_from_xml(XML)
    ok = kb._indicator_from_rows(key="kr_3y_yield", code_index=2, rows=rows)
    _eq((ok["status"], ok["current"], ok["previous"], ok["asof"], ok["previous_asof"]),
        ("ok", 3.2, 3.1, "2026/10/28", "2026/10/27"))
    if abs(ok["delta"] - 0.1) > 1e-9:
        raise AssertionError(ok["delta"])
    # latest row has an empty val3 -> unavailable, not a stale previous value
    miss = kb._indicator_from_rows(key="kr_10y_yield", code_index=3, rows=rows)
    _eq((miss["status"], miss["reason"]), ("unavailable", "kofia_value_missing"))
    only = kb._indicator_from_rows(key="kr_3y_yield", code_index=2, rows=rows[:1])
    _eq("previous" in only, False)
    _eq(kb._indicator_from_rows(key="kr_3y_yield", code_index=2, rows=[])["status"], "unavailable")


def test_fetch_overrides_with_fake_urlopen_records_one_request(monkeypatch):
    seen = []

    def fake_urlopen(req, timeout):
        seen.append((req.full_url, req.data, timeout))
        return _Resp(XML.encode("utf-8"))

    monkeypatch.setattr(kb.urllib.request, "urlopen", fake_urlopen)
    out = kb.fetch_korea_bond_yield_overrides({"korea_bond_yield_timeout_sec": 1})
    _eq(len(seen), 1)
    _eq(seen[0][0], "https://www.kofiabond.or.kr/proframeWeb/XMLSERVICES/")
    _eq(seen[0][2], 3.0)                   # timeout floored at 3s
    _eq(out["kr_3y_yield"]["status"], "ok")
    _eq(out["kr_10y_yield"]["status"], "unavailable")


def test_fetch_overrides_disabled_by_policy_or_env_never_calls_urlopen(monkeypatch):
    def boom(*_a, **_k):
        raise AssertionError("urlopen must not be called")

    monkeypatch.setattr(kb.urllib.request, "urlopen", boom)
    for value in (False, "false", "0", "No", "off", "N"):
        _eq(kb.fetch_korea_bond_yield_overrides({"korea_bond_yield_provider_enabled": value}), {})
    monkeypatch.setenv("KOREA_BOND_YIELD_PROVIDER_ENABLED", "off")
    _eq(kb.fetch_korea_bond_yield_overrides(None), {})


def test_default_is_enabled_so_unset_policy_reaches_the_provider(monkeypatch):
    # Current contract: with no policy and no env the provider is ON (this is why
    # un-isolated global_sentiment tests hit the network).
    calls = []
    monkeypatch.setattr(kb.urllib.request, "urlopen", lambda req, timeout: calls.append(1) or _Resp(XML.encode()))
    kb.fetch_korea_bond_yield_overrides(None)
    _eq(calls, [1])


def test_fetch_error_maps_to_unavailable_with_exception_name(monkeypatch):
    def fail(req, timeout):
        raise TimeoutError("slow")

    monkeypatch.setattr(kb.urllib.request, "urlopen", fail)
    out = kb.fetch_korea_bond_yield_overrides({})
    for key in ("kr_3y_yield", "kr_10y_yield"):
        _eq((out[key]["status"], out[key]["reason"]), ("unavailable", "kofia_fetch_error:TimeoutError"))
    monkeypatch.setattr(kb.urllib.request, "urlopen", lambda req, timeout: _Resp(b"<not-xml"))
    out2 = kb.fetch_korea_bond_yield_overrides({})
    _eq(out2["kr_3y_yield"]["reason"], "kofia_fetch_error:ParseError")


def test_index_sanity_to_float_and_row_helpers():
    _eq(ks._to_float("1.5"), 1.5)
    _eq(ks._to_float(None, 9.0), 9.0)
    _eq(ks._to_float("", None), None)
    _eq(ks._to_float("abc", 2.0), 2.0)
    _eq(ks._row({"indices": "bad"}, "KOSPI"), {})
    _eq(ks._row({"indices": {"KOSPI": 5}}, "KOSPI"), {})
    _eq(ks._row({}, "KOSPI"), {})


def test_index_sanity_flags_and_severity_thresholds():
    ok = ks.korea_index_sanity({"indices": {"KOSPI": {"change_pct": 5.99, "current": 100, "high": 101, "low": 99}}})
    _eq((ok["status"], ok["warning_count"], ok["extreme_move_requires_confirmation"]), ("ok", 0, False))
    warn = ks.korea_index_sanity({"indices": {"KOSPI": {"change_pct": -6.0}}})
    _eq(warn["warnings"][0]["severity"], "warning")
    crit = ks.korea_index_sanity({"indices": {"KOSDAQ": {"change_pct": "10"}}})
    _eq((crit["status"], crit["warnings"][0]["severity"], crit["warnings"][0]["index"]), ("warning", "critical", "KOSDAQ"))
    skip = ks.korea_index_sanity({"indices": {"KOSPI": {"change_pct": None, "current": 1}, "NASDAQ": {"change_pct": 50}}})
    _eq(skip["warning_count"], 0)           # missing change_pct skips the row; unknown names ignored


def test_index_sanity_high_below_low_and_current_outside_range():
    out = ks.korea_index_sanity({"indices": {"KOSPI200": {"change_pct": 0.1, "current": 100, "high": 90, "low": 95}}})
    codes = [w["code"] for w in out["warnings"]]
    if "index_high_below_low" not in codes:
        raise AssertionError(codes)
    out2 = ks.korea_index_sanity({"indices": {"KOSPI": {"change_pct": 0.1, "current": 102, "high": 100, "low": 99}}})
    _eq([w["code"] for w in out2["warnings"]], ["index_current_outside_high_low"])
    inside = ks.korea_index_sanity({"indices": {"KOSPI": {"change_pct": 0.1, "current": 100.05, "high": 100, "low": 99}}})
    _eq(inside["warning_count"], 0)         # within the 0.1% tolerance
    nonpos = ks.korea_index_sanity({"indices": {"KOSPI": {"change_pct": 0.1, "current": 5, "high": 0, "low": -1}}})
    _eq(nonpos["warning_count"], 0)         # non-positive high/low ignored
    src_in = {"indices": {"KOSPI": {"change_pct": 7.0}}}
    snapshot = repr(src_in)
    ks.korea_index_sanity(src_in)
    _eq(repr(src_in), snapshot)             # input is never mutated
