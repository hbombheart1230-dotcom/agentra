"""P15 RF-035 (02h): trade_explain._safe_int moved to trade_explain_scalar_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import trade_explain as m
from libs.reporting import trade_explain_scalar_projection as owner


@pytest.mark.parametrize("v,kw,expected", [("2.9", {}, 2), ("bad", {}, 0), ("bad", {"default": 7}, 7), (None, {"default": 4}, 4), (True, {}, 1), (-2.7, {}, -2)])
def test_values(v, kw, expected):
    assert m._safe_int(v, **kw) == owner._safe_int(v, **kw) == expected


def test_nan_inf_and_invalid_default():
    for fn in (m._safe_int, owner._safe_int):
        assert fn(float("nan"), default=9) == 9 and fn(float("inf"), default=8) == 8
        with pytest.raises(ValueError):
            fn("bad", default="x")
        with pytest.raises(TypeError):
            fn("bad", default=None)
