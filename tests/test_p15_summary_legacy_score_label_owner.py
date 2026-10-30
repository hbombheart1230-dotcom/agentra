"""P15: strategist_llm_summary ``_score_label`` moved to strategist_llm_summary_legacy_scores.score_label; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json
from pathlib import Path

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_legacy_scores as owner

GOLDEN = ["391552c099c101b131feaf24c5795a6a15bc8ec82015424e0d2b4274a369a0bf", "391552c099c101b131feaf24c5795a6a15bc8ec82015424e0d2b4274a369a0bf", "24c74279834561bd8e2846f7eebd4a3cd158413fcf88c604c081cd040d871614", "98089e6d36f78e9766c9ea34d5acb3611f3a92cd81c5eb102095d924ffc7d08b", "8a385a89628a3d35a3e8d10e5f6e2fa14a7264ddaa4dc3cc637f9b41922692ae", "fa7484677d99b81bf4b15d11050e36e9c920aff33837dde062ea880b4da99458", "cbfeda2b1f044ccca4ea9dac0fe08a34af201914e29adf982262f1d735d08996", "0933fb667296882d8c45abca58ac52e01c8db6f19e626b30de88f0f4ed143ec5", "0933fb667296882d8c45abca58ac52e01c8db6f19e626b30de88f0f4ed143ec5", "7bf38eea04927d8320a7efef572722e9d034b8fcd1c72b483cd55d92eb7828e0", "32beb723f043a95ffd8dcf85a3b4f8c49e17cad88ce2d44d5df4465a5bcd4e02", "0e97c61044ac582761b9bf9b5ca9bf3a3b7b6ba1a198e00d83e51348dd603895", "391552c099c101b131feaf24c5795a6a15bc8ec82015424e0d2b4274a369a0bf", "6d759f8c2fc28d0a361935a3729383dbeefc6524993d130376c85a2129cb7950", "7685b103fbcd22c84fa70c5e139b0abc4c9f3a44b7bb6925ed2329d045180ad9", "aeb0b9ce3e43f64c7b56a388efac1514166c4cf5c92df5c6a4dd9f867bf35f83", "ea33dc847d962e75874bfed11cf65b69acebbfa3cabec313effeb7c8b4fc90e1", "266aa5886067fbbc1a3a39fe432fc5bbf561abc90e4b8a322215ac17df6ce012"]

LABEL = [1, 1.0, 1.5, 0, -2.25, "3.10", "bad", None, "", float("inf"), float("-inf"), float("nan"), True, "0.005", 123456.789, [1], "1e3", " 7 "]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(LABEL)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_unchanged(i):
    a = LABEL[i]
    snap = copy.deepcopy(a)
    assert _safe(lambda: m._score_label(a)) == GOLDEN[i]
    assert _safe(lambda: owner.score_label(a, facade=m)) == GOLDEN[i]
    assert repr(a) == repr(snap)                                                       # nan != nan, so compare reprs


def test_formatting_trailing_zero_strip_and_invalid_fallback():
    f = m._score_label
    assert [f(v) for v in (1, 1.0, 1.5, 0, -2.25, "3.10", 123456.789, "1e3", " 7 ", True)] == ["1", "1", "1.5", "0", "-2.25", "3.1", "123456.79", "1000", "7", "1"]
    assert [f(v) for v in ("bad", None, "", [1])] == ["bad", "-", "-", "[1]"]                                  # unparsable -> facade._text(value)
    assert f(float("inf")) == "inf" and f(float("-inf")) == "-inf" and f(float("nan")) == "nan"                # only -inf takes the text path, and it renders the same


def test_facade_helpers_use_time_patches_reach_the_owner(monkeypatch):
    monkeypatch.setattr(m, "_score_value", lambda v: 2.5)
    assert m._score_label("anything") == "2.5"
    monkeypatch.setattr(m, "_score_value", lambda v: float("-inf"))
    monkeypatch.setattr(m, "_text", lambda v, d="-": "TXT")
    assert m._score_label("x") == "TXT"


def test_owner_does_not_import_the_summary_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.strategist_llm_summary import" not in src and "import strategist_llm_summary\n" not in src
    assert len(inspect.getsource(m._score_label).splitlines()) <= 3
