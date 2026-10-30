"""P15: strategist_llm_summary ``_first_dict`` moved to strategist_llm_summary_first_values.first_dict; parity with the pre-move output."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json
from pathlib import Path

import pytest

from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_first_values as owner

GOLDEN = ["44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a", "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a", "f9d86028c6e0d64e225186f96acb69338b2c59764df79162107f5c4bb34d1310", "f9d86028c6e0d64e225186f96acb69338b2c59764df79162107f5c4bb34d1310", "7433b26feba2b9cc7e497b8941eec056eba9041fba1260c3e5aa35ee283c9c03", "4e54b58e52f9bd33a2a2d09ee885d96b7f6f7bd05cf90ca4636fc3161ad390aa", "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a", "04bec6dadaa90850d2a10f6fb7b44c6747b7e622ceb385f011c4eb0e6e514234"]

FIRST_DICT = [(), (None, {}, []), ({}, {"a": 1}, {"b": 2}), ({"a": 1},), ("junk", {"z": 1}), ([("k", "v")], {"y": 1}), (None, None), ({"nested": {"x": [1]}},)]


def _h(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=False, default=repr).encode()).hexdigest()


def _safe(fn):
    try:
        return _h(fn())
    except Exception as exc:
        return "EXC:" + type(exc).__name__


@pytest.mark.parametrize("i", range(len(FIRST_DICT)))
def test_wrapper_and_owner_match_pre_move_golden_and_inputs_unchanged(i):
    a = FIRST_DICT[i]
    snap = copy.deepcopy(a)
    assert _safe(lambda: m._first_dict(*a)) == GOLDEN[i]
    assert _safe(lambda: owner.first_dict(*a, facade=m)) == GOLDEN[i]
    assert a == snap


def test_first_nonempty_mapping_copy_semantics():
    f = m._first_dict
    assert f() == {} and f(None, {}, []) == {} and f({}, {"a": 1}, {"b": 2}) == {"a": 1} and f("junk", {"z": 1}) == {"z": 1} and f([("k", "v")], {"y": 1}) == {"y": 1}
    src = {"nested": {"x": [1]}}
    out = f(src)
    assert out == src and out is not src and out["nested"] is src["nested"]                               # _as_dict shallow copy; nested alias kept


def test_facade_as_dict_use_time_patch(monkeypatch):
    seen = []
    monkeypatch.setattr(m, "_as_dict", lambda v: (seen.append(v), {"hit": 1} if v == "second" else {})[1])
    assert m._first_dict("first", "second", "third") == {"hit": 1} and seen == ["first", "second"]


def test_owner_does_not_import_the_summary_module_and_wrapper_is_thin():
    src = inspect.getsource(owner)
    assert "from libs.reporting.strategist_llm_summary import" not in src and "import strategist_llm_summary\n" not in src
    assert len(inspect.getsource(m._first_dict).splitlines()) <= 3
