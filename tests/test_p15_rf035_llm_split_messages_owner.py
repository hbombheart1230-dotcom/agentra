"""P15 RF-035: llm_artifacts split_prompt_messages moved to llm_artifacts_prompt_projection; parity with the pre-move body."""
from __future__ import annotations

from libs.reporting import llm_artifacts as m
from libs.reporting import llm_artifacts_prompt_projection as owner


def _both():
    return (m.split_prompt_messages, owner.split_prompt_messages)


def test_system_user_order_and_joins():
    rows = [{"role": "system", "content": "S1"}, {"role": "user", "content": "U"}, {"role": "system", "content": "S2"}]
    snap = [dict(r) for r in rows]
    for fn in _both():
        assert fn(rows) == ("S1\n\nS2", "U")
    assert rows == snap


def test_type_gates_and_skips():
    for fn in _both():
        assert fn(None) == ("", "")
        assert fn("x") == ("", "")
        assert fn({"role": "user", "content": "x"}) == ("", "")
        assert fn([{"role": "assistant", "content": "a"}, "x", 3, None]) == ("", "")
        assert fn([{"role": " SYSTEM ", "content": "s"}, {"role": "user", "content": ""}, {"role": "USER", "content": "u"}]) == ("s", "u")


def test_strip_semantics():
    for fn in _both():
        assert fn([{"role": "user", "content": "  p  "}, {"role": "user", "content": "q  "}]) == ("", "p  \n\nq")


def test_wrapper_thin_and_owner_no_source_import():
    import inspect
    assert len(inspect.getsource(m.split_prompt_messages).strip().splitlines()) <= 3
    assert "import llm_artifacts " not in inspect.getsource(owner)
