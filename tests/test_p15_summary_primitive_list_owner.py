"""P15: strategist_llm_summary _as_list moved to strategist_llm_summary_primitives.as_list; parity with the pre-move body."""
from __future__ import annotations


from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_primitives as owner


def test_list_shallow_copy_and_type_gate():
    inner = {"x": 1}
    src = [inner]
    for fn in (m._as_list, owner.as_list):
        out = fn(src)
        assert out == [{"x": 1}] and out is not src and out[0] is inner
        assert fn((1, 2)) == [] and fn(None) == [] and fn({"a": 1}) == []
        e1, e2 = fn([]), fn([])
        assert e1 == [] and e1 is not e2
    assert src == [inner]


def test_wrapper_thin():
    import inspect
    assert len(inspect.getsource(m._as_list).strip().splitlines()) <= 3
