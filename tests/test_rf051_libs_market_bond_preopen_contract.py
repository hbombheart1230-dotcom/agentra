"""RF-051 libs/market C2/C3: korea_bond_yields and preopen_macro_snapshot, offline.

``urllib.request.urlopen`` and every ``_fetch_kofia_xml`` are replaced by fakes;
``yfinance`` is never imported (an injected ``compute`` is used, or the module is
masked with ``sys.modules['yfinance']=None``). State/env paths live in tmp_path
(the env file does not exist so ``os.environ`` is not mutated).
Complements tests/test_korea_bond_yields.py. Explicit raises keep the checks live under ``python -O``.
"""
from __future__ import annotations

import io
import json
import sys

import pytest

from libs.market import korea_bond_yields as kb
from libs.market import preopen_macro_snapshot as pm
from libs.market.yfinance_support import DataSourceDependencyError


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


XML = """<?xml version="1.0" encoding="UTF-8"?>
<root><message><BISComDspDatListDTO>
<BISComDspDatDTO><val1>최고</val1><val2>9.9</val2><val3>9.9</val3></BISComDspDatDTO>
<BISComDspDatDTO><val1>2026-05-26</val1><val2>3.664</val2><val3></val3></BISComDspDatDTO>
<BISComDspDatDTO><val1>2026-05-27</val1><val2>3.711</val2><val3>4.102</val3></BISComDspDatDTO>
<BISComDspDatDTO><val1>2026-05-25</val1><val2>x</val2><val3>4.000</val3></BISComDspDatDTO>
</BISComDspDatListDTO></message></root>
"""


def test_request_body_and_date_range_shape():
    body = kb._request_body("20261001", "20261014", ["3000", "3013"]).decode("utf-8")
    for token in ("<val1>DD</val1>", "<val2>20261001</val2>", "<val3>20261014</val3>", "<val4>1530</val4>",
                  "<val5>3000</val5>", "<val6>3013</val6>", "BISLastAskPrcROPSrchSO"):
        if token not in body:
            raise AssertionError((token, body))
    s, e = kb._date_range(1)   # lookback floors at 3 days
    _eq((len(s), len(e), s.isdigit(), s <= e), (8, 8, True, True))
    _eq(kb._date_range(30)[0] < kb._date_range(5)[0], True)


def test_rows_sorted_newest_first_and_header_rows_skipped():
    rows = kb._rows_from_xml(XML)
    _eq([r["val1"] for r in rows], ["2026-05-27", "2026-05-26", "2026-05-25"])
    with pytest.raises(Exception):
        kb._rows_from_xml("<not xml")


def test_indicator_values_missing_values_and_previous_fallthrough():
    rows = kb._rows_from_xml(XML)
    y3 = kb._indicator_from_rows(key="kr_3y_yield", code_index=2, rows=rows)
    _eq((y3["status"], y3["current"], y3["previous"], y3["asof"], y3["previous_asof"]), ("ok", 3.711, 3.664, "2026-05-27", "2026-05-26"))
    _eq(round(y3["delta"], 3), 0.047)
    # the previous row for the 10y column has an empty value -> no previous/delta keys at all
    y10 = kb._indicator_from_rows(key="kr_10y_yield", code_index=3, rows=rows)
    _eq((y10["current"], "previous" in y10, "delta" in y10, y10["ticker"]), (4.102, False, False, "3013"))
    miss = kb._indicator_from_rows(key="kr_3y_yield", code_index=7, rows=rows)
    _eq(miss, {"status": "unavailable", "source": "kofia", "ticker": "3000", "reason": "kofia_value_missing"})
    _eq(kb._indicator_from_rows(key="other", code_index=2, rows=[])["ticker"], "")
    _eq([kb._to_float(v) for v in (None, "", " 1.5 ", "x")], [None, None, 1.5, None])


@pytest.mark.parametrize("flag", ["0", "false", "No", "n", "OFF"])
def test_provider_disabled_by_policy_or_env_never_fetches(monkeypatch, flag):
    monkeypatch.setattr(kb, "_fetch_kofia_xml", lambda **k: (_ for _ in ()).throw(AssertionError("must not fetch")))
    _eq(kb.fetch_korea_bond_yield_overrides({"korea_bond_yield_provider_enabled": flag}), {})
    monkeypatch.setenv("KOREA_BOND_YIELD_PROVIDER_ENABLED", flag)
    _eq(kb.fetch_korea_bond_yield_overrides({}), {})
    _eq(kb.fetch_korea_bond_yield_overrides(None), {})


def test_policy_overrides_env_and_passes_codes_timeout_lookback(monkeypatch):
    seen = {}

    def fake(**kw):
        seen.update(kw)
        return XML

    monkeypatch.setattr(kb, "_fetch_kofia_xml", fake)
    monkeypatch.setenv("KOREA_BOND_YIELD_PROVIDER_ENABLED", "false")
    monkeypatch.setenv("KOREA_BOND_YIELD_TIMEOUT_SEC", "20")
    out = kb.fetch_korea_bond_yield_overrides({"korea_bond_yield_provider_enabled": "true", "korea_bond_yield_timeout_sec": 5,
                                               "korea_bond_yield_lookback_days": "30"})
    _eq(list(out), ["kr_3y_yield", "kr_10y_yield"])
    _eq((seen["codes"], seen["timeout_sec"]), (["3000", "3013"], 5.0))
    _eq(len(seen["start_date"]), 8)


def test_fetch_errors_become_per_indicator_unavailable_and_never_raise(monkeypatch):
    monkeypatch.setattr(kb, "_fetch_kofia_xml", lambda **k: "<broken")
    out = kb.fetch_korea_bond_yield_overrides({})
    _eq({k: (v["status"], v["reason"].split(":")[0], v["ticker"]) for k, v in out.items()},
        {"kr_3y_yield": ("unavailable", "kofia_fetch_error", "3000"), "kr_10y_yield": ("unavailable", "kofia_fetch_error", "3013")})
    if not out["kr_3y_yield"]["reason"].startswith("kofia_fetch_error:ParseError"):
        raise AssertionError(out["kr_3y_yield"]["reason"])
    # bad numeric policy value is also caught only if it is inside the try; float() runs BEFORE the try -> raises
    with pytest.raises(ValueError):
        kb.fetch_korea_bond_yield_overrides({"korea_bond_yield_timeout_sec": "abc"})


def test_fetch_kofia_xml_uses_post_headers_floor_timeout_and_decodes(monkeypatch):
    seen = {}

    class Resp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def fake_urlopen(req, timeout):
        seen.update(url=req.full_url, method=req.get_method(), data=req.data, timeout=timeout, ct=req.get_header("Content-type"))
        return Resp("한글".encode("utf-8") + b"\xff")

    monkeypatch.setattr(kb.urllib.request, "urlopen", fake_urlopen)
    text = kb._fetch_kofia_xml(start_date="20261001", end_date="20261014", codes=["3000"], timeout_sec=1)
    _eq((seen["url"], seen["method"], seen["timeout"]), (kb.KOFIA_ENDPOINT, "POST", 3.0))
    _eq(seen["ct"], "application/xml; charset=utf-8")
    _eq(text, "한글�")  # undecodable bytes replaced, not raised
    if b"<val5>3000</val5>" not in seen["data"]:
        raise AssertionError(seen["data"])


def _compute_ok(**kw):
    return {"status": "ok", "source": "fake", "reason": "r", "ts": 123, "ignored": 1}


def test_preopen_snapshot_with_injected_compute_needs_no_yfinance(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "yfinance", None)   # proves the injected path never requires yfinance
    seen = {}

    def compute(*, state, policy):
        seen.update(state=state, policy=policy)
        return _compute_ok()

    st = tmp_path / "state.json"
    st.write_text(json.dumps({"policy": {"keep": 1, "macro_indicator_log_enabled": False}, "x": 1}), encoding="utf-8")
    out = pm.capture_preopen_macro_snapshot(env_path=tmp_path / "no.env", state_path=st, compute=compute)
    _eq(out, {"schema_version": "preopen_macro_snapshot_capture.v1", "phase": "preopen", "status": "ok", "source": "fake", "reason": "r", "signal_ts": 123})
    _eq(seen["policy"], {"keep": 1, "macro_indicator_log_enabled": False})   # setdefault does not override an explicit False
    _eq(seen["state"]["x"], 1)


def test_preopen_snapshot_defaults_for_missing_corrupt_state_and_empty_signal(tmp_path):
    seen = {}

    def compute(*, state, policy):
        seen.update(state=state, policy=policy)
        return {}

    for content in (None, "{bad", "[1]"):
        st = tmp_path / "s.json"
        if content is None:
            st.unlink(missing_ok=True)
        else:
            st.write_text(content, encoding="utf-8")
        out = pm.capture_preopen_macro_snapshot(env_path=tmp_path / "no.env", state_path=st, compute=compute)
        _eq((out["status"], out["source"], out["reason"], out["signal_ts"]), ("unavailable", "", "", None))
        _eq((seen["state"], seen["policy"]), ({}, {"macro_indicator_log_enabled": True}))
    st.write_text(json.dumps({"policy": "notamapping"}), encoding="utf-8")
    pm.capture_preopen_macro_snapshot(env_path=tmp_path / "no.env", state_path=st, compute=compute)
    _eq(seen["policy"], {"macro_indicator_log_enabled": True})


def test_preopen_snapshot_default_compute_fails_loudly_without_yfinance(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "yfinance", None)
    with pytest.raises(DataSourceDependencyError):
        pm.capture_preopen_macro_snapshot(env_path=tmp_path / "no.env", state_path=tmp_path / "s.json")


def test_preopen_snapshot_compute_exception_propagates(tmp_path):
    def boom(**kw):
        raise RuntimeError("compute failed")

    with pytest.raises(RuntimeError):
        pm.capture_preopen_macro_snapshot(env_path=tmp_path / "no.env", state_path=tmp_path / "s.json", compute=boom)
