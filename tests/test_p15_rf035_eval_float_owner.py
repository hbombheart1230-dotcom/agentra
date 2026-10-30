"""P15 RF-035: strategist_llm_evaluation._float moved to strategist_llm_evaluation_scalar; parity with the pre-move body."""
from __future__ import annotations

import math

import pytest

from libs.reporting import strategist_llm_evaluation as m
from libs.reporting import strategist_llm_evaluation_scalar as owner


@pytest.mark.parametrize("v,kw,expected", [("2.5", {}, 2.5), (None, {"default": 4}, 4.0), ("", {"default": 1}, 1.0), ("bad", {"default": 3}, 3.0), (0, {"default": 9}, 0.0), (True, {}, 1.0)])
def test_values(v, kw, expected):
    assert m._float(v, **kw) == owner._float(v, **kw) == expected


def test_nan_inf_and_invalid_default():
    for fn in (m._float, owner._float):
        assert math.isnan(fn("nan")) and fn("inf") == float("inf")
        with pytest.raises(ValueError):
            fn(None, default="x")
        with pytest.raises(ValueError):
            fn("bad", default="x")
