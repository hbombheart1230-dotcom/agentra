"""P15 RF-035 (23h): market_regime_rail_review._to_float moved to market_regime_rail_review_scalar_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json
import math

import pytest

from libs.reporting import market_regime_rail_review as m
from libs.reporting import market_regime_rail_review_scalar_projection as owner


@pytest.mark.parametrize("v,kw,expected", [("2.5", {}, 2.5), (None, {"default": 1}, 1.0), ("", {"default": 2}, 2.0), ("bad", {"default": 3}, 3.0), (0, {"default": 9}, 0.0), (True, {}, 1.0)])
def test_values(v, kw, expected):
    assert m._to_float(v, **kw) == owner._to_float(v, **kw) == expected


def test_nan_inf_and_invalid_default():
    for fn in (m._to_float, owner._to_float):
        assert math.isnan(fn(float("nan"))) and fn("inf") == float("inf")
        with pytest.raises(ValueError):
            fn(None, default="x")
        with pytest.raises(ValueError):
            fn("bad", default="x")
