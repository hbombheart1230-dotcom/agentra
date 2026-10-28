"""RF-033 baseline_btc_woori_tech/crypto_fear_greed: normalization, regime thresholds and fetch fallbacks (fake urlopen only).

``urlopen`` (imported into the module) is replaced and socket.connect is denied for the module, so a regression that
reaches alternative.me fails loudly. No file is written. Explicit raises keep the checks live under ``python -O``.
"""
from __future__ import annotations

import json
import socket
from datetime import datetime, timezone

import pytest

from libs.reporting.baseline_btc_woori_tech import crypto_fear_greed as cfg


@pytest.fixture(autouse=True)
def _offline(monkeypatch):
    def deny(*_a, **_k):
        raise AssertionError("real network attempted")

    monkeypatch.setattr(socket.socket, "connect", deny)
    monkeypatch.setattr(socket, "create_connection", deny)


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


class _Resp:
    def __init__(self, body):
        self._b = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _ts(y, m, d, hour=0):
    # KST = UTC+9: pick UTC hours so the KST calendar day is deterministic
    return int(datetime(y, m, d, hour, tzinfo=timezone.utc).timestamp())


def test_regime_thresholds_and_classification_override():
    _eq([cfg._regime(v) for v in (None, 0, 24, 25, 44, 45, 55, 56, 74, 75, 100)],
        ["unavailable", "extreme_fear", "extreme_fear", "fear", "fear", "neutral", "neutral", "greed", "greed", "extreme_greed", "extreme_greed"])
    _eq(cfg._regime(10, " Very Greedy "), "very_greedy")                    # an explicit classification wins, lower-cased with underscores
    _eq((cfg._to_int("7"), cfg._to_int("x"), cfg._to_int(None)), (7, None, None))


def test_normalize_row_derives_kst_observation_day_and_marks_availability():
    row = cfg._normalize_row({"value": "30", "timestamp": _ts(2026, 10, 27, 16), "value_classification": "Fear", "time_until_update": "100"}, day="2026-10-28")
    _eq((row["available"], row["value"], row["regime"], row["classification"], row["fallback_reason"]), (True, 30, "fear", "Fear", ""))
    _eq(row["observed_day"], "2026-10-28")                                   # 16:00 UTC is 01:00 next day in KST
    _eq((row["schema_version"], row["behavior_effect"], row["source"], row["time_until_update"]), ("q12_crypto_fear_greed.v1", "observation_only", "alternative.me/fng", "100"))
    missing = cfg._normalize_row({"timestamp": "bad"}, day="2026-10-28")
    _eq((missing["available"], missing["value"], missing["observed_day"], missing["fallback_reason"], missing["regime"]), (False, None, "", "crypto_fear_greed_value_missing", "unavailable"))
    _eq(cfg.unavailable("why", day="d")["fallback_reason"], "why")


def test_fetch_prefers_the_exact_day_else_latest_with_a_reason(monkeypatch):
    seen = {}

    def fake(request, timeout):
        seen.update(url=request.full_url, ua=request.get_header("User-agent"), timeout=timeout)
        return _Resp({"data": [
            {"value": "50", "timestamp": _ts(2026, 10, 29, 3), "value_classification": "Neutral"},
            {"value": "20", "timestamp": _ts(2026, 10, 28, 3), "value_classification": "Extreme Fear"},
            "junk",
        ]})

    monkeypatch.setattr(cfg, "urlopen", fake)
    exact = cfg.load_crypto_fear_greed_index(day="2026-10-28", timeout_sec=2.5)
    _eq((exact["value"], exact["regime"], exact["fallback_reason"], exact["observed_day"]), (20, "extreme_fear", "", "2026-10-28"))
    _eq((seen["url"], seen["timeout"], seen["ua"]), (cfg.API_URL, 2.5, "TradingAgentSystem/1.0"))
    latest = cfg.load_crypto_fear_greed_index(day="2026-01-01")
    _eq((latest["value"], latest["fallback_reason"]), (50, "exact_day_not_found_latest_used"))   # first listed row, flagged


def test_fetch_failures_never_raise_and_name_the_reason(monkeypatch):
    def boom(request, timeout):
        raise TimeoutError("slow")

    monkeypatch.setattr(cfg, "urlopen", boom)
    out = cfg.load_crypto_fear_greed_index(day="2026-10-28")
    _eq((out["available"], out["fallback_reason"], out["regime"]), (False, "crypto_fear_greed_fetch_failed:TimeoutError", "unavailable"))
    for body, reason in (({"data": []}, "crypto_fear_greed_empty_response"), ({"nodata": 1}, "crypto_fear_greed_empty_response"), (["x"], "crypto_fear_greed_empty_response")):
        monkeypatch.setattr(cfg, "urlopen", lambda request, timeout, b=body: _Resp(b))
        _eq(cfg.load_crypto_fear_greed_index(day="d")["fallback_reason"], reason)
    monkeypatch.setattr(cfg, "urlopen", lambda request, timeout: _Resp(b"not json"))
    _eq(cfg.load_crypto_fear_greed_index(day="d")["fallback_reason"], "crypto_fear_greed_fetch_failed:JSONDecodeError")
    monkeypatch.setattr(cfg, "urlopen", lambda request, timeout: _Resp({"data": ["junk"]}))
    _eq(cfg.load_crypto_fear_greed_index(day="d")["fallback_reason"], "crypto_fear_greed_no_valid_rows")
    monkeypatch.setattr(cfg, "urlopen", lambda request, timeout: _Resp({"data": [{"timestamp": _ts(2026, 10, 28, 3)}]}))
    row = cfg.load_crypto_fear_greed_index(day="d")
    _eq((row["available"], row["fallback_reason"]), (False, "crypto_fear_greed_value_missing"))   # an unavailable latest row keeps its own reason
