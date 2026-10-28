"""RF-033 C3: BTC vnext storage (atomic/immutable publish) and pipeline preopen-context branches.

Only tmp_path is written; equity/alignment loaders are injected so yfinance is never reached; sockets are denied.
"""
from __future__ import annotations

import json
import os
import socket
from datetime import datetime

import pytest

from libs.reporting.baseline_btc_woori_tech.vnext import pipeline as pl
from libs.reporting.baseline_btc_woori_tech.vnext import storage as st
from libs.reporting.baseline_btc_woori_tech.vnext.contract import KST, PREVIOUS_VERSION, START_DAY, VERSION

DAY = "2026-10-28"


@pytest.fixture(autouse=True)
def _deny_network(monkeypatch):
    def _boom(*a, **k):
        raise AssertionError("network attempt")

    monkeypatch.setattr(socket.socket, "connect", _boom)
    monkeypatch.setattr(socket, "create_connection", _boom)


# ---------- storage ----------

def test_encoded_is_canonical_and_rejects_nan():
    assert st.encoded({"b": 1, "a": "한"}) == '{"a": "한", "b": 1}'.encode("utf-8")
    assert st.digest({"a": 1, "b": 2}) == st.digest({"b": 2, "a": 1})
    assert st.digest({"a": 1}) != st.digest({"a": 2})
    assert len(st.digest({})) == 64
    with pytest.raises(ValueError):
        st.encoded({"x": float("nan")})
    assert json.loads(st.encoded({"p": __import__("pathlib").Path("x")})) == {"p": "x"}  # default=str


def test_publish_mutable_replaces_and_leaves_no_temp(tmp_path):
    p = tmp_path / "a" / "b" / "v.json"
    assert st.publish(p, {"n": 1}) == {"n": 1}
    assert st.read(p) == {"n": 1}
    assert st.publish(p, {"n": 2}) == {"n": 2}
    assert st.read(p) == {"n": 2}
    assert sorted(x.name for x in p.parent.iterdir()) == ["v.json"]


def test_publish_immutable_never_overwrites_and_returns_existing(tmp_path):
    p = tmp_path / "i.json"
    assert st.publish(p, {"n": 1}, immutable=True) == {"n": 1}
    assert st.publish(p, {"n": 2}, immutable=True) == {"n": 1}          # existing evidence wins
    assert st.read(p) == {"n": 1}
    assert sorted(x.name for x in tmp_path.iterdir()) == ["i.json"]      # temp hardlink source removed


def test_publish_failure_cleans_temp_and_keeps_target(tmp_path):
    p = tmp_path / "f.json"
    st.publish(p, {"n": 1})
    with pytest.raises(ValueError):
        st.publish(p, {"x": float("nan")})
    assert st.read(p) == {"n": 1}
    assert sorted(x.name for x in tmp_path.iterdir()) == ["f.json"]


def test_publish_writes_only_under_target_parent(tmp_path, monkeypatch):
    seen = []
    real = os.replace
    monkeypatch.setattr(os, "replace", lambda a, b: (seen.append((str(a), str(b))), real(a, b))[1])
    p = tmp_path / "d" / "x.json"
    st.publish(p, {"k": 1})
    (src, dst), = seen
    assert os.path.dirname(src) == str(p.parent) and dst == str(p) and os.path.basename(src).startswith(".q12-")


# ---------- pipeline ----------

def _now(day=DAY, clock="08:30:00"):
    return datetime.fromisoformat(f"{day}T{clock}").replace(tzinfo=KST)


def _daily(n):
    return [{"ts": 1000 + i, "close": 1.0 + i} for i in range(n)]


def _call(root, **kw):
    args = dict(day=DAY, reports_root=root, signals={}, candles={}, control_payload={}, cost_pct=0.1, slippage_pct=0.05, now=_now())
    args.update(kw)
    return pl.build_vnext(**args)


def _folder(root):
    return root / "evaluation/baseline_btc_woori_tech/vnext" / VERSION / DAY


def test_skips_non_today_and_pre_start_day(tmp_path):
    want = {"status": "SKIPPED", "reason": "forward_only_no_historical_rebuild"}
    assert _call(tmp_path, day="2026-10-27") == want                      # not "today"
    assert _call(tmp_path, day="2026-01-01", now=_now("2026-01-01")) == want   # before START_DAY
    assert "2026-01-01" < START_DAY
    assert list(tmp_path.iterdir()) == []


def test_preopen_context_published_once_and_immutable(tmp_path):
    calls = []

    def eq(day):
        calls.append(("eq", day))
        return {"COIN": {"status": "UNKNOWN"}}

    def al(day, e):
        calls.append(("al", day))
        return {"status": "UNKNOWN", "reason": "stub"}

    out = _call(tmp_path, allow_fetch=True, equity_loader=eq, alignment_loader=al,
                signals={"research_context": {"btc_usd_daily": _daily(200), "woori_daily": _daily(30)}})
    assert out["status"] == "INSUFFICIENT_EVIDENCE"
    ctx = json.loads((_folder(tmp_path) / "preopen_context.json").read_text(encoding="utf-8"))
    assert ctx["day"] == DAY and ctx["version"] == VERSION and ctx["observed_at"].startswith(DAY)
    assert ctx["daily_context"]["btc_usd_daily"] == _daily(200)[70:]   # last 130
    assert ctx["daily_context"]["woori_daily"] == _daily(30)[20:]      # last 10
    assert ctx["crypto_time_alignment"] == {"status": "UNKNOWN", "reason": "stub"}
    for name in ("validation.json", "comparison.json", "daily_report.md"):
        assert (_folder(tmp_path) / name).exists()
    # second run: context exists -> loaders are not consulted again, context file unchanged
    before = (_folder(tmp_path) / "preopen_context.json").read_bytes()
    _call(tmp_path, allow_fetch=True, equity_loader=lambda d: pytest.fail("refetch"), alignment_loader=lambda d, e: pytest.fail("refetch"))
    assert (_folder(tmp_path) / "preopen_context.json").read_bytes() == before
    assert calls == [("eq", DAY), ("al", DAY)]


def test_loader_failures_are_recorded_as_unknown_not_raised(tmp_path):
    def eq(day):
        raise RuntimeError("x")

    def al(day, e):
        raise KeyError("y")

    _call(tmp_path, allow_fetch=True, equity_loader=eq, alignment_loader=al)
    ctx = json.loads((_folder(tmp_path) / "preopen_context.json").read_text(encoding="utf-8"))
    assert ctx["equities"] == {"status": "UNKNOWN", "reason": "RuntimeError"}
    assert ctx["crypto_time_alignment"] == {"status": "UNKNOWN", "reason": "KeyError"}


def test_equity_loader_without_alignment_loader_uses_signal_alignment(tmp_path):
    _call(tmp_path, allow_fetch=True, equity_loader=lambda d: {}, alignment_loader=None,
          signals={"crypto_time_alignment": {"status": "FROM_SIGNALS"}})
    ctx = json.loads((_folder(tmp_path) / "preopen_context.json").read_text(encoding="utf-8"))
    assert ctx["crypto_time_alignment"] == {"status": "FROM_SIGNALS"}


def test_no_fetch_after_deadline_or_without_allow_fetch_means_no_backfill(tmp_path):
    for kw in ({"allow_fetch": False}, {"allow_fetch": True, "now": _now(clock="09:05:00")}):
        root = tmp_path / str(len(kw))
        kw = dict(kw, equity_loader=lambda d: pytest.fail("fetch not allowed"), alignment_loader=lambda d, e: pytest.fail("fetch not allowed"))
        _call(root, **kw)
        assert not (_folder(root) / "preopen_context.json").exists()
        assert (_folder(root) / "validation.json").exists()


def test_existing_context_schema_mismatch_raises_and_is_not_replaced(tmp_path):
    f = _folder(tmp_path)
    f.mkdir(parents=True)
    bad = json.dumps({"day": "2020-01-01", "version": VERSION})
    (f / "preopen_context.json").write_text(bad, encoding="utf-8")
    with pytest.raises(ValueError, match="vnext_context_schema_mismatch"):
        _call(tmp_path, allow_fetch=True, equity_loader=lambda d: {}, alignment_loader=lambda d, e: {})
    assert (f / "preopen_context.json").read_text(encoding="utf-8") == bad
    (f / "preopen_context.json").write_text("{corrupt", encoding="utf-8")
    with pytest.raises(ValueError):                                       # corruption never authorizes replacement
        _call(tmp_path, allow_fetch=True, equity_loader=lambda d: {}, alignment_loader=lambda d, e: {})
    assert (f / "preopen_context.json").read_text(encoding="utf-8") == "{corrupt"


def _write_v1(root, *, observed_at, day=DAY):
    prior = root / "evaluation/baseline_btc_woori_tech/vnext" / PREVIOUS_VERSION / DAY / "preopen_context.json"
    prior.parent.mkdir(parents=True)
    prior.write_text(json.dumps({"day": day, "version": PREVIOUS_VERSION, "observed_at": observed_at,
                                 "equities": {"COIN": {"status": "UNKNOWN"}}, "daily_context": {"btc_usd_daily": []}}), encoding="utf-8")
    return prior


def test_v1_preopen_context_is_carried_with_unknown_alignment(tmp_path, monkeypatch):
    monkeypatch.setattr(pl, "session_context", lambda day: {"status": "AVAILABLE", "session": "S"})
    prior = _write_v1(tmp_path, observed_at=_now(clock="08:40:00").isoformat())
    _call(tmp_path, now=_now(clock="09:30:00"))                           # after the deadline: carry, never fetch
    ctx = json.loads((_folder(tmp_path) / "preopen_context.json").read_text(encoding="utf-8"))
    assert ctx["version"] == VERSION and ctx["carried_from"] == str(prior)
    assert ctx["crypto_time_alignment"] == {"status": "UNKNOWN", "reason": "V1_did_not_capture_matched_BTC_interval", "session": "S"}
    assert ctx["equities"] == {"COIN": {"status": "UNKNOWN"}}


def test_v1_context_captured_after_deadline_is_not_carried(tmp_path):
    _write_v1(tmp_path, observed_at=_now(clock="09:30:00").isoformat())
    _call(tmp_path, now=_now(clock="09:45:00"))
    assert not (_folder(tmp_path) / "preopen_context.json").exists()


def test_v1_carry_tolerates_calendar_failure(tmp_path, monkeypatch):
    def boom(day):
        raise RuntimeError("cal")

    monkeypatch.setattr(pl, "session_context", boom)
    _write_v1(tmp_path, observed_at=_now(clock="08:40:00").isoformat())
    _call(tmp_path, now=_now(clock="09:30:00"))
    ctx = json.loads((_folder(tmp_path) / "preopen_context.json").read_text(encoding="utf-8"))
    assert ctx["crypto_time_alignment"] == {"status": "UNKNOWN", "reason": "V1_did_not_capture_matched_BTC_interval"}


def test_concurrent_context_writer_wins_and_is_not_overwritten(tmp_path):
    winner = {"day": DAY, "version": VERSION, "observed_at": _now().isoformat(), "equities": {"WIN": 1}, "daily_context": {},
              "crypto_time_alignment": {"status": "WINNER"}}

    def eq(day):
        # another process publishes the immutable context between our exists() check and our publish
        st.publish(_folder(tmp_path) / "preopen_context.json", winner, immutable=True)
        return {"LOSER": 1}

    _call(tmp_path, allow_fetch=True, equity_loader=eq, alignment_loader=lambda d, e: {"status": "LOSER"})
    assert json.loads((_folder(tmp_path) / "preopen_context.json").read_text(encoding="utf-8")) == winner
