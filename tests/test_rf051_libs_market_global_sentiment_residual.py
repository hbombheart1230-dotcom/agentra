"""RF-051 residual: global_sentiment pure/fake branches (no network, no yfinance)."""
from __future__ import annotations

import math

from libs.market import global_sentiment as gs


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


def test_clamp_bounds_and_passthrough():
    _eq(gs._clamp(-5.0), -1.0)
    _eq(gs._clamp(5.0), 1.0)
    _eq(gs._clamp(0.25), 0.25)
    _eq(gs._clamp(7, lo=0.0, hi=3.0), 3.0)
    _eq(gs._clamp(-7, lo=0.0, hi=3.0), 0.0)


def test_compute_global_sentiment_unavailable_is_nan_and_bad_score_is_zero(monkeypatch):
    monkeypatch.setattr(gs, "compute_global_sentiment_signal",
                        lambda state, policy: {"status": gs.SIGNAL_STATUS_UNAVAILABLE, "score": 0.9})
    if not math.isnan(gs.compute_global_sentiment({}, {})):
        raise AssertionError("unavailable must be NaN, never neutral 0")
    monkeypatch.setattr(gs, "compute_global_sentiment_signal",
                        lambda state, policy: {"status": "ok", "score": "not-a-number"})
    _eq(gs.compute_global_sentiment({}, {}), 0.0)
    monkeypatch.setattr(gs, "compute_global_sentiment_signal",
                        lambda state, policy: {"status": "ok", "score": 3.0})
    _eq(gs.compute_global_sentiment({}, {}), 1.0)


def test_override_reason_precedence():
    # the field-copy loop lets an override "reason" overwrite the base reason
    out = gs._indicator_from_override("vix", {"reason": "yfinance_ok"}, {"current": 21.5, "reason": "ovr"})
    _eq((out["current"], out["reason"], out["key"]), (21.5, "ovr", "vix"))
    # without an override reason a real base reason is kept (non-placeholder branch)
    out2 = gs._indicator_from_override("vix", {"reason": "yfinance_ok"}, {"current": 2.0})
    _eq(out2["reason"], "yfinance_ok")
    # placeholder base reason + no override reason -> "override"
    out3 = gs._indicator_from_override("vix", {"reason": "no_provider_configured"}, {"current": 2.0})
    _eq(out3["reason"], "override")
    # no usable value -> status/reason untouched
    out4 = gs._indicator_from_override("vix", {"reason": "x", "status": "unavailable"}, {"current": None})
    _eq((out4["status"], out4["reason"]), ("unavailable", "x"))
