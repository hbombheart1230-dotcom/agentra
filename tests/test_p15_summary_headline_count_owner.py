"""P15: strategist_llm_summary ``_headline_count_from_sample_map`` moved to strategist_llm_summary_sample_counts.headline_count_from_sample_map; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json
from pathlib import Path

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_sample_counts as owner

GOLDEN = ["5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9", "5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9", "e7f6c011776e8db7cd330b54174fd76f7d0216b612387a5ffcfb81e6f0919683", "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b", "5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9", "5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9", "5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9", "5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9"]

COUNTS = [None, {}, {"A": {"count": 2}, "B": {"count": "3"}, "C": {"count": None}, "D": {"count": "x"}, "E": "junk", "F": {"count": -1}, "G": {"count": 2.9}, "H": {}, "I": {"count": [1]}}, {"A": {"count": True}}, [1, 2], "str", {"A": {"count": "1e2"}}, {"A": {"count": 0}}]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(COUNTS)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_unchanged(i):
    a = COUNTS[i]
    snap = copy.deepcopy(a)
    assert _safe(lambda: m._headline_count_from_sample_map(a)) == GOLDEN[i]
    assert _safe(lambda: owner.headline_count_from_sample_map(a)) == GOLDEN[i]
    assert a == snap


def test_sums_ints_skips_bad_rows_and_allows_negatives():
    f = m._headline_count_from_sample_map
    assert f(COUNTS[2]) == 6                                                           # 2 + 3 + 0 + 0 + (-1) + 2 ; None/"x"/junk/[1] rows skipped
    assert f(None) == 0 and f({}) == 0 and f([1, 2]) == 0 and f("str") == 0
    assert f(COUNTS[3]) == 1 and f(COUNTS[7]) == 0 and f(COUNTS[6]) == 0              # True -> 1; "1e2" is not an int literal -> skipped


def test_owner_is_pure_and_takes_no_facade():
    assert "facade" not in inspect.signature(owner.headline_count_from_sample_map).parameters


def test_owner_does_not_import_the_summary_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.strategist_llm_summary import" not in src and "import strategist_llm_summary\n" not in src
    assert len(inspect.getsource(m._headline_count_from_sample_map).splitlines()) <= 3
