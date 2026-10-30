"""P15 RF-035: llm_artifacts split_prompt_text moved to llm_artifacts_prompt_projection; parity with the pre-move body."""
from __future__ import annotations

from libs.reporting import llm_artifacts as m
from libs.reporting import llm_artifacts_prompt_projection as owner

import pytest

CASES = [
    ("[system]\nS\n[user]\nU", ("S", "U")),
    ("plain text", ("", "plain text")),
    ("[SYSTEM]\na\n[system]\nb\n[USER]\nc", ("a\n\nb", "c")),
    (None, ("", "")),
    ("   ", ("", "")),
    ("[user]\nonly", ("", "only")),
    ("pre\n[system]\nx", ("x", "")),
    ("  [ System ]  \nnot a tag", ("", "[ System ]  \nnot a tag")),
]


@pytest.mark.parametrize("raw,expected", CASES)
def test_cases(raw, expected):
    for fn in (m.split_prompt_text, owner.split_prompt_text):
        assert fn(raw) == expected


def test_empty_sections_fall_back_to_raw():
    for fn in (m.split_prompt_text, owner.split_prompt_text):
        assert fn("[system]\n\n[user]\n") == ("", "[system]\n\n[user]")
