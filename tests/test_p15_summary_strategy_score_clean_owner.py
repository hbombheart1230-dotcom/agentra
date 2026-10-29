"""P15: strategist_llm_summary ``_strategy_score_lines_clean`` moved to strategist_llm_summary_strategy_lines.strategy_score_lines_clean; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_strategy_lines as owner

GOLDEN = ["44d7110f8d4d19b695347c2538accc6eea64fe6dfda2e7062327218f8314d23b", "03af6d88d8d9bb6cb692a4efd5c592349e4de480906ad1c4f1dffebcbfc658c3", "055aa6e9a39cde76cfcd7eb92610684304031634c7e44b4be286bd52bb4fdd81", "afa3e39aa6951bf8b62b342128dc71c1dc561d10983f848e25ca113bde484bc9", "e446dc80e7eb2b453c3f971b6cfd213f239cb2274e7beec0446c3887f0c74937", "44d7110f8d4d19b695347c2538accc6eea64fe6dfda2e7062327218f8314d23b", "a804c426339c8e5823b94a4f614573c7cbdff112cb0cb8cc5d6954655b854040"]

SCORES = [
    ({}, "a"), ({"a": 1, "b": 1, "c": 2.5}, "b"), ({"x": "bad", "y": None, "z": float("-inf"), "w": 0}, "y"), ({"a": "3.0", "b": "10"}, ""), ({"s": 0.12345}, "s"), (None, "a"), ({"a": 1}, "a"),
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(SCORES)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_unchanged(i):
    a = SCORES[i]
    snap = copy.deepcopy(a)
    assert _safe(lambda: m._strategy_score_lines_clean(a[0], selected=a[1])) == GOLDEN[i]
    assert _safe(lambda: owner.strategy_score_lines_clean(a[0], selected=a[1], facade=m)) == GOLDEN[i]
    assert a == snap


def test_sorting_ties_marker_and_invalid_scores():
    f = lambda i: m._strategy_score_lines_clean(SCORES[i][0], selected=SCORES[i][1])
    assert f(0) == ["- -"] and f(5) == ["- -"]
    assert f(1) == ["- c: 2.5", "- b: 1 (선택)", "- a: 1"]                                      # score desc, tie -> name desc (reverse sort)
    assert f(2) == ["- w: 0", "- z: -inf", "- y: - (선택)", "- x: bad"]                           # invalid -> -inf, ordered by name desc among ties
    assert f(3) == ["- b: 10", "- a: 3"] and f(4) == ["- s: 0.12 (선택)"] and f(6) == ["- a: 1 (선택)"]


def test_facade_score_helpers_use_time_patches_reach_the_owner(monkeypatch):
    monkeypatch.setattr(m, "_score_value", lambda v: {"a": 1.0, "b": 2.0}[v])
    monkeypatch.setattr(m, "_score_label", lambda v: f"L{v}")
    assert m._strategy_score_lines_clean({"x": "a", "y": "b"}, selected="x") == ["- y: Lb", "- x: La (선택)"]


def test_owner_does_not_import_the_summary_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.strategist_llm_summary import" not in src and "import strategist_llm_summary\n" not in src
    assert len(inspect.getsource(m._strategy_score_lines_clean).splitlines()) <= 3
