"""P15: strategist_llm_summary ``_directive_line`` moved to strategist_llm_summary_directive_line.directive_line; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_directive_line as owner

GOLDEN = ["78110cc8b2d2344184743b5a6c4f9861a39ffbdf341fce5dd958c6a27c9a53b3", "78110cc8b2d2344184743b5a6c4f9861a39ffbdf341fce5dd958c6a27c9a53b3", "3df7cc2aea84e87417fb0d48c06318252eb685b410183b646e819affc1371703", "301ab590036fb81cef32bc886383794f7196aca1348f22e077f1b9699528c92f", "5320595ddf59ab39ccdf163f1fbf889b9861d56988079896a5f67d92445ee0ce", "231fb0667443bdb0665537518aef2afafdf595fe1ac42060c22592f8f7846418", "8984b29734b12e8a8124902207767cd15294325997d0e9be40c44355fdbd6a60", "5f8949f134557ddb1a76912782fed46a4c314423535a3d470bfbf754668ee0eb", "6d67f5bca3fe027814213a8bde29d69ffe79fecdb530083c6b198d1ed4ae74b1", "a3058a3ae74782116c7482d468530db1840b59f3b1f9cb553fb0fbfbbad0994f", "3df7cc2aea84e87417fb0d48c06318252eb685b410183b646e819affc1371703"]

DIRECTIVE = [("L", {}), ("L", None), ("L", {"action": "A"}), ("L", {"action": "A", "target": ["x", "y"], "reason": "r"}), ("L", {"action": "A", "target": None, "target_fields": ["f"], "reason": ""}),
             ("L", {"action": "A", "target_axes": ["ax"], "reason": "r"}), ("L", {"action": "A", "target": "tx"}), ("L", {"action": "A", "reason": "r"}), ("L", {"target": [], "target_fields": ["f"], "reason": "한글"}), ("L", {"action": "A", "target": 5}), ("L", {"action": "A", "target": 0, "target_fields": ["f"]})
]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(DIRECTIVE)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_unchanged(i):
    a = DIRECTIVE[i]
    snap = copy.deepcopy(a)
    assert _safe(lambda: m._directive_line(*a)) == GOLDEN[i]
    assert _safe(lambda: owner.directive_line(*a, facade=m)) == GOLDEN[i]
    assert a == snap


def test_exact_lines_and_fallback_precedence():
    f = m._directive_line
    assert f("L", {}) == "- L: -" and f("L", None) == "- L: -" and f("L", {"action": "A"}) == "- L: **A**"
    assert f("L", {"action": "A", "target": ["x", "y"], "reason": "r"}) == "- L: **A** -> x, y; r"
    assert f("L", {"action": "A", "target": None, "target_fields": ["f"], "reason": ""}) == "- L: **A** -> f"                    # target None -> target_fields
    assert f("L", {"action": "A", "target_axes": ["ax"], "reason": "r"}) == "- L: **A** -> ax; r"                               # then target_axes
    assert f("L", {"action": "A", "target": "tx"}) == "- L: **A** -> tx" and f("L", {"action": "A", "reason": "r"}) == "- L: **A**; r"
    assert f("L", {"target": [], "target_fields": ["f"], "reason": "한글"}) == "- L: **-**; 한글"                                  # empty list is not None -> no fallback; missing action -> "-"
    assert f("L", {"action": "A", "target": 5}) == "- L: **A** -> 5" and f("L", {"action": "A", "target": 0, "target_fields": ["f"]}) == "- L: **A**"


def test_facade_text_use_time_patch_reaches_the_owner(monkeypatch):
    monkeypatch.setattr(m, "_text", lambda v, d="-": "T")
    assert m._directive_line("L", {"action": "a", "target": "t", "reason": "r"}) == "- L: **T** -> T; T"


def test_owner_does_not_import_the_summary_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.strategist_llm_summary import" not in src and "import strategist_llm_summary\n" not in src
    assert len(inspect.getsource(m._directive_line).splitlines()) <= 3
