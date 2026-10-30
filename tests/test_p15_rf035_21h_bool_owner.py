"""P15 RF-035 (21h): strategist_llm_evaluation._bool moved to strategist_llm_evaluation_extra_projection; parity with the pre-move body."""
from __future__ import annotations

import copy

import pytest

from libs.reporting import strategist_llm_evaluation as m
from libs.reporting import strategist_llm_evaluation_extra_projection as owner


class Boom:
    def __bool__(self):
        return True

    def __str__(self):
        raise RuntimeError("x")


@pytest.mark.parametrize("v,expected", [
    (True, True), (False, False), (1, True), (0, False), (0.0, False), (2.5, True), ("yes", True), (" ON ", True), ("Y", True), ("1", True),
    ("off", False), ("no", False), (None, False), ("", False), ([], False), ("true", True),
])
def test_values(v, expected):
    a, b = m._bool(v), owner._bool(v)
    assert a is expected and b is expected


def test_exception_parity():
    for fn in (m._bool, owner._bool):
        with pytest.raises(RuntimeError):
            fn(Boom())
