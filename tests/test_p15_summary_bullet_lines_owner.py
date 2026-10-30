"""P15: strategist_llm_summary _bullet_lines moved to strategist_llm_summary_markdown_helpers.bullet_lines; parity with the pre-move body."""
from __future__ import annotations

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_markdown_helpers as owner


class Boom:
    def __str__(self):
        raise RuntimeError("boom")


def test_values():
    for fn in (m._bullet_lines, owner.bullet_lines):
        assert fn([" hi ", 0, None, "x"]) == ["-  hi ", "- x"]
        assert fn([]) == ["- -"]
        assert fn([None], empty="없음") == ["- 없음"]


def test_exception_unchanged():
    for fn in (m._bullet_lines, owner.bullet_lines):
        with pytest.raises(RuntimeError):
            fn([Boom()])
