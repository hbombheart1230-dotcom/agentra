"""P15 RF-035 (21h): strategist_llm_evaluation._row_closed moved to strategist_llm_evaluation_extra_projection; parity with the pre-move body."""
from __future__ import annotations

import copy

import pytest

from libs.reporting import strategist_llm_evaluation as m
from libs.reporting import strategist_llm_evaluation_extra_projection as owner


@pytest.mark.parametrize("row,expected", [
    ({"status": "closed"}, True), ({"action": "SELL"}, True), ({}, False), ({"last_status": "open", "last_action": "BUY"}, False),
    ({"last_status": " CLOSED "}, True), ({"is_closed_trade": 1}, True), ({"is_realized_nonclosed_exit": True}, True),
    ({"status": "open", "last_status": "closed"}, False), ({"last_action": "buy", "action": "sell"}, False), ({"action": "sell"}, True),
])
def test_values(row, expected):
    snap = copy.deepcopy(row)
    a, b = m._row_closed(row), owner._row_closed(row)
    assert a is expected and b is expected and row == snap


def test_non_mapping_exception_parity():
    for fn in (m._row_closed, owner._row_closed):
        with pytest.raises(AttributeError):
            fn("x")
