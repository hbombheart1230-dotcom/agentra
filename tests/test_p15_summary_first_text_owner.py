"""P15: strategist_llm_summary ``_first_text`` moved to strategist_llm_summary_first_values.first_text; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json
from pathlib import Path

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_first_values as owner

GOLDEN = ["3fa5834dc920d385ca9b099c9fe55dcca163a6b256a261f8f147291b0e7cf633", "3fa5834dc920d385ca9b099c9fe55dcca163a6b256a261f8f147291b0e7cf633", "ac8d8342bbb2362d13f0a559a3621bb407011368895164b628a54f7fc33fc43c", "ba2df4903a2c14e86dc3bcca58911b44ac1d2514b7227bf6eb08cfb978f55a1b", "20c400557af0eddc0be4d9e0ae86f7ccc2890e8a285005aea2a752951ed94bed", "d10a4bc9e0c1fa4e8f3d7ce2512b8756e47ca5fa451f373c39a1431bb88db49f", "12ae32cb1ec02d01eda3581b127c1fee3b0dc53572ed6baf239721a03d82e126", "4d251a69d5dfca9708c59e85e7e25376b41dbc3e01893193d8c3079dab9308cb", "aeb0b9ce3e43f64c7b56a388efac1514166c4cf5c92df5c6a4dd9f867bf35f83"]

FIRST_TEXT = [("d", ()), ("d", ("", None, "  ")), ("d", ("", " a ", "b")), ("d", (0, "x")), ("d", ([], {}, "z")), ("d", (5,)), ("", ("",)), ("d", (None, False, "한글")), ("def", ([1],))]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(FIRST_TEXT)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_unchanged(i):
    a = FIRST_TEXT[i]
    snap = copy.deepcopy(a)
    assert _safe(lambda: m._first_text(a[0], *a[1])) == GOLDEN[i]
    assert _safe(lambda: owner.first_text(a[0], *a[1], facade=m)) == GOLDEN[i]
    assert a == snap


def test_first_truthy_text_and_default():
    f = m._first_text
    assert f("d") == "d" and f("d", "", None, "  ") == "d" and f("d", "", " a ", "b") == "a" and f("d", 0, "x") == "x" and f("d", [], {}, "z") == "z" and f("", "") == ""
    assert f("d", 5) == "5" and f("d", None, False, "한글") == "한글" and f("def", [1]) == "[1]"


def test_facade_text_use_time_patch_and_call_order(monkeypatch):
    seen = []
    monkeypatch.setattr(m, "_text", lambda v, d="-": (seen.append(v), "" if v in ("a", "b") else "HIT")[1])
    assert m._first_text("d", "a", "b", "c", "e") == "HIT" and seen == ["a", "b", "c"]                   # left-to-right, stops at the first non-empty text
    monkeypatch.setattr(m, "_text", lambda v, d="-": (_ for _ in ()).throw(RuntimeError("boom")))
    with pytest.raises(RuntimeError):
        m._first_text("d", "x")


def test_owner_does_not_import_the_summary_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.strategist_llm_summary import" not in src and "import strategist_llm_summary\n" not in src
    assert len(inspect.getsource(m._first_text).splitlines()) <= 3
