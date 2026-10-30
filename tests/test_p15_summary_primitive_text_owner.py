"""P15: strategist_llm_summary _text moved to strategist_llm_summary_primitives.text; parity with the pre-move body."""
from __future__ import annotations

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_primitives as owner


class Boom:
    def __str__(self):
        raise RuntimeError("boom")


def test_text_values():
    for fn in (m._text, owner.text):
        assert fn("  한글  ") == "한글"
        assert fn(0) == "-" and fn(False) == "-" and fn(None, "NA") == "NA"
        assert fn("   ", "d") == "d"
        assert fn(5) == "5"
        assert fn("x", "d") == "x"


def test_text_exception_retained():
    for fn in (m._text, owner.text):
        with pytest.raises(RuntimeError):
            fn(Boom())
