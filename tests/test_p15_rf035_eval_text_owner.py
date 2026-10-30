"""P15 RF-035: strategist_llm_evaluation._text moved to strategist_llm_evaluation_scalar; parity with the pre-move body."""
from __future__ import annotations

import pytest

from libs.reporting import strategist_llm_evaluation as m
from libs.reporting import strategist_llm_evaluation_scalar as owner


@pytest.mark.parametrize("v,expected", [(None, ""), (" unknown ", ""), ("  BUY  ", "BUY"), (0, ""), ("-", ""), ("NONE", ""), ("null", ""), ("not_captured", ""), (5, "5"), ("한글 ", "한글")])
def test_values(v, expected):
    assert m._text(v) == owner._text(v) == expected


def test_str_exception_retained():
    class Boom:
        def __bool__(self):
            return True

        def __str__(self):
            raise RuntimeError("x")

    for fn in (m._text, owner._text):
        with pytest.raises(RuntimeError):
            fn(Boom())
