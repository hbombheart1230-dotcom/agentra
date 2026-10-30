"""P15 RF-035: agent_pipeline_trace._safe_int moved to agent_pipeline_trace_scalar_projection; parity with the pre-move body."""
from __future__ import annotations

import pytest

from libs.reporting import agent_pipeline_trace as m
from libs.reporting import agent_pipeline_trace_scalar_projection as owner


@pytest.mark.parametrize("v,kw,expected", [
    ("3.9", {}, 3), ("bad", {"default": 7}, 7), (None, {"default": 4}, 4), (True, {}, 1), (-2.7, {}, -2), ("  5 ", {}, 5),
])
def test_values(v, kw, expected):
    assert m._safe_int(v, **kw) == owner._safe_int(v, **kw) == expected


def test_nan_inf_and_bad_default():
    for fn in (m._safe_int, owner._safe_int):
        assert fn(float("nan"), default=9) == 9
        assert fn(float("inf"), default=8) == 8
        with pytest.raises(ValueError):
            fn("bad", default="x")
        with pytest.raises(TypeError):
            fn("bad", default=None)
