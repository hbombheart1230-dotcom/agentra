"""P15 RF-035 (04h): symbol_trade_report._contains_any moved to symbol_trade_text_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import symbol_trade_report as m
from libs.reporting import symbol_trade_text_projection as owner


@pytest.mark.parametrize("text,needles,expected", [("AbC", ["bc"], True), ("AbC", ["BC"], False), ("", ["x"], False), (None, ["x"], False), ("  Hello ", ["hello"], True), ("abc", [], False), ("abc", [""], True)])
def test_values(text, needles, expected):
    snap = copy.deepcopy(needles)
    assert m._contains_any(text, needles) is expected and owner._contains_any(text, needles) is expected and needles == snap


def test_non_iterable_needles_exception_parity():
    for fn in (m._contains_any, owner._contains_any):
        with pytest.raises(TypeError):
            fn("abc", 5)
