"""Emergency RF-041: non-finite limit prices must never produce actionable intents.

Pure normalization only. No Broker, executor, network or live order calls.
"""
from __future__ import annotations

import math

import pytest

from libs.ai.intent_schema import normalize_intent


@pytest.mark.parametrize("action", ["BUY", "SELL"])
@pytest.mark.parametrize("bad_price", [float("nan"), float("inf"), -float("inf"), "nan", "inf", "-inf"])
def test_limit_nonfinite_price_fails_closed(action: str, bad_price: object) -> None:
    source = {"action": action, "symbol": "005930", "qty": 2, "price": bad_price, "order_type": "limit"}
    out, _ = normalize_intent(source)
    if out["action"] != "NOOP":
        raise AssertionError(f"actionable intent with nonfinite price: {out}")
    if out.get("reason") != "invalid_intent_missing_price_for_limit":
        raise AssertionError(out)
    if not math.isfinite(float(out["price"])):
        raise AssertionError(out)
    if source["action"] != action or source["price"] != bad_price and not (
        isinstance(bad_price, float) and math.isnan(bad_price) and math.isnan(source["price"])
    ):
        raise AssertionError("source was mutated")


@pytest.mark.parametrize("action", ["BUY", "SELL"])
def test_nonfinite_fallback_default_price_fails_closed(action: str) -> None:
    source = {"action": action, "symbol": "005930", "qty": 1, "order_type": "limit"}
    out, _ = normalize_intent(source, default_price=float("nan"))
    if out["action"] != "NOOP" or out.get("reason") != "invalid_intent_missing_price_for_limit":
        raise AssertionError(out)


@pytest.mark.parametrize("action", ["BUY", "SELL"])
def test_market_nonfinite_input_does_not_preserve_nan_inf(action: str) -> None:
    out, _ = normalize_intent(
        {"action": action, "symbol": "005930", "qty": 1, "order_type": "market", "price": float("inf")}
    )
    if out["action"] != action or out["price"] != 0.0:
        raise AssertionError(out)


@pytest.mark.parametrize("action", ["BUY", "SELL"])
def test_valid_finite_limit_price_preserved(action: str) -> None:
    out, _ = normalize_intent(
        {"action": action, "symbol": "005930", "qty": 2, "order_type": "limit", "price": 1234.5}
    )
    if out["action"] != action or out["price"] != 1234.5 or out["qty"] != 2:
        raise AssertionError(out)
