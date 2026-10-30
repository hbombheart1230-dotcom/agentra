"""P15 RF-035 (04h): symbol_trade_report._clean_symbol_code moved to symbol_trade_text_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import symbol_trade_report as m
from libs.reporting import symbol_trade_text_projection as owner


@pytest.mark.parametrize("v,expected", [(" unknown ", ""), (" 005930 ", "005930"), (None, ""), ("-", ""), ("NULL", ""), ("None", ""), ("", ""), ("abC", "abC"), (0, ""), (5930, "5930"), ("007", "007")])
def test_values(v, expected):
    assert m._clean_symbol_code(v) == owner._clean_symbol_code(v) == expected
