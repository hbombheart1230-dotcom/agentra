"""P15 RF-035 (02h): trade_explain._safe_float moved to trade_explain_scalar_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json
import math

import pytest

from libs.reporting import trade_explain as m
from libs.reporting import trade_explain_scalar_projection as owner


@pytest.mark.parametrize("v,kw,expected", [("2.5", {}, 2.5), ("bad", {}, 0.0), ("bad", {"default": 3.25}, 3.25), (None, {"default": 1}, 1.0), (True, {}, 1.0), (3, {}, 3.0)])
def test_values(v, kw, expected):
    assert m._safe_float(v, **kw) == owner._safe_float(v, **kw) == expected


def test_nan_inf_and_invalid_default():
    for fn in (m._safe_float, owner._safe_float):
        assert math.isnan(fn("nan")) and fn("inf") == float("inf")
        with pytest.raises(ValueError):
            fn("bad", default="x")
