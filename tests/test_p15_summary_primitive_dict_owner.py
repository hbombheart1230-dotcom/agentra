"""P15: strategist_llm_summary _as_dict moved to strategist_llm_summary_primitives.as_dict; parity with the pre-move body."""
from __future__ import annotations

import copy

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_primitives as owner


class Sub(dict):
    pass


def test_dict_copy_and_type_gate():
    src = {"x": 1}
    for fn in (m._as_dict, owner.as_dict):
        out = fn(src)
        assert out == {"x": 1} and out is not src
        assert fn([]) == {} and fn(None) == {} and fn("x") == {}
        sub = fn(Sub(a=1))
        assert sub == {"a": 1} and type(sub) is dict
    assert src == {"x": 1}


def test_shallow_copy_keeps_nested_identity():
    inner = {"k": 1}
    assert m._as_dict({"n": inner})["n"] is inner
    assert owner.as_dict({"n": inner})["n"] is inner


def test_wrapper_thin_and_owner_does_not_import_source():
    import inspect
    assert len(inspect.getsource(m._as_dict).strip().splitlines()) <= 3
    assert "strategist_llm_summary import" not in inspect.getsource(owner).replace("strategist_llm_summary_primitives", "")
