"""P15: strategist_llm_summary ``_rejected_strategy_lines`` moved to strategist_llm_summary_strategy_lines.rejected_strategy_lines; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_strategy_lines as owner

GOLDEN = ["44d7110f8d4d19b695347c2538accc6eea64fe6dfda2e7062327218f8314d23b", "44d7110f8d4d19b695347c2538accc6eea64fe6dfda2e7062327218f8314d23b", "c629bcf1d33b02b478c1e7a5737c3a0e2ca9f3d1788c59c57b2784424e9ffe00", "44d7110f8d4d19b695347c2538accc6eea64fe6dfda2e7062327218f8314d23b", "7a4295ff469fbec510b049fddf43cb8f8d82308b09de90bd1a029f51957a1fc1", "44d7110f8d4d19b695347c2538accc6eea64fe6dfda2e7062327218f8314d23b", "f1e14e76489b3a0fd10d7acce8a2afde48fd22342041a1b468ac6c6f99723ba4"]

REJECT = [
    ({}, "a"), ({"a": "only"}, "a"), ({"b": "reason b", "a": {"k": [1, "한글"], "z": 0}, "c": ["x", {"y": 2}], "sel": "skip", "d": None, "e": 0}, "sel"), ({"x": "1"}, "x"), ({1: "a", 2: "b"}, "1"), (None, "a"), ({"a": float("nan")}, ""),
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(REJECT)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_unchanged(i):
    a = REJECT[i]
    snap = copy.deepcopy(a)
    assert _safe(lambda: m._rejected_strategy_lines(a[0], selected=a[1])) == GOLDEN[i]
    assert _safe(lambda: owner.rejected_strategy_lines(a[0], selected=a[1], facade=m)) == GOLDEN[i]
    assert a == snap


def test_sorted_names_selected_filter_and_inline_json():
    f = lambda i: m._rejected_strategy_lines(REJECT[i][0], selected=REJECT[i][1])
    assert f(0) == ["- -"] and f(1) == ["- -"] and f(3) == ["- -"] and f(5) == ["- -"]                  # empty / only the selected name / None
    assert f(2) == ['- a: {"k": [1, "한글"], "z": 0}', "- b: reason b", '- c: ["x", {"y": 2}]', "- d: -", "- e: -"]
    assert f(4) == ["- 2: b"] and f(6) == ["- a: nan"]


def test_facade_json_and_text_helpers_use_time_patches_reach_the_owner(monkeypatch):
    monkeypatch.setattr(m, "_json_inline", lambda v: "JSON")
    monkeypatch.setattr(m, "_text", lambda v, d="-": "TXT")
    assert m._rejected_strategy_lines({"a": {"k": 1}, "b": "s", "c": [1]}, selected="z") == ["- a: JSON", "- b: TXT", "- c: JSON"]


def test_owner_does_not_import_the_summary_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.strategist_llm_summary import" not in src and "import strategist_llm_summary\n" not in src
    assert len(inspect.getsource(m._rejected_strategy_lines).splitlines()) <= 3
