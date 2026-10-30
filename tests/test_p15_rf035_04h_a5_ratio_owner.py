"""P15 RF-035 (04h): symbol_trade_report._ratio moved to symbol_trade_scalar_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import symbol_trade_report as m
from libs.reporting import symbol_trade_scalar_projection as owner


@pytest.mark.parametrize("n,d,expected", [(4, 2, 2.0), (4, 0, 0.0), (4, -2, 0.0), (1.5, 0.5, 3.0), (0, 5, 0.0), (1, 3, 1 / 3)])
def test_values(n, d, expected):
    assert m._ratio(n, d) == owner._ratio(n, d) == expected


def test_exception_parity():
    for fn in (m._ratio, owner._ratio):
        with pytest.raises(TypeError):
            fn(1, None)
        with pytest.raises(TypeError):
            fn("a", 1)
