"""P15: strategist_llm_summary _monitor_adjustment_lines moved to strategist_llm_summary_markdown_helpers.monitor_adjustment_lines; parity with the pre-move body."""
from __future__ import annotations

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_markdown_helpers as owner


def test_values():
    for fn in (m._monitor_adjustment_lines, owner.monitor_adjustment_lines):
        assert fn({"b": 2, "a": 1}) == ["- a: 1", "- b: 2"]
        assert fn({}) == ["- -"]
        assert fn({"a": None}) == ["- a: None"]
        with pytest.raises(TypeError):
            fn({1: "x", "a": 2})
