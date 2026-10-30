"""P15 RF-035: agent_pipeline_trace._safe_float moved to agent_pipeline_trace_scalar_projection; parity with the pre-move body."""
from __future__ import annotations

import math

import pytest

from libs.reporting import agent_pipeline_trace as m
from libs.reporting import agent_pipeline_trace_scalar_projection as owner


@pytest.mark.parametrize("v,kw,expected", [
    ("1.25", {}, 1.25), ("bad", {"default": 2.5}, 2.5), (None, {"default": 0.0}, 0.0), (True, {}, 1.0), (3, {}, 3.0),
])
def test_values(v, kw, expected):
    assert m._safe_float(v, **kw) == owner._safe_float(v, **kw) == expected


def test_nan_inf_and_bad_default():
    for fn in (m._safe_float, owner._safe_float):
        assert math.isnan(fn("nan"))
        assert fn("inf") == float("inf")
        with pytest.raises(ValueError):
            fn("bad", default="x")
