"""P15: strategist_llm_summary _directive moved to strategist_llm_summary_directive_projection.directive; parity with the pre-move body."""
from __future__ import annotations


from libs.reporting import strategist_llm_summary as m
from libs.reporting import strategist_llm_summary_directive_projection as owner


def test_values_and_distinct_dict():
    d = {"v": 1}
    payload = {"strategy_adjustment_directives": {"x": d}}
    for out in (m._directive(payload, "x"), owner.directive(payload, "x", facade=m)):
        assert out == {"v": 1} and out is not d
    for fn in (lambda p: m._directive(p, "x"), lambda p: owner.directive(p, "x", facade=m)):
        assert fn({"strategy_adjustment_directives": {}}) == {}
        assert fn({"strategy_adjustment_directives": [1]}) == {}
        assert fn({"strategy_adjustment_directives": {"x": 3}}) == {}
        assert fn({}) == {}


def test_facade_patch_seam_two_calls(monkeypatch):
    calls = []
    orig = m._as_dict

    def spy(v):
        calls.append(v)
        return orig(v)

    monkeypatch.setattr(m, "_as_dict", spy)
    m._directive({"strategy_adjustment_directives": {"x": {"v": 1}}}, "x")
    assert len(calls) == 2
    calls.clear()
    owner.directive({"strategy_adjustment_directives": {"x": {"v": 1}}}, "x", facade=m)
    assert len(calls) == 2


def test_owner_does_not_import_source():
    import inspect
    src = inspect.getsource(owner)
    assert "import strategist_llm_summary " not in src and "from libs.reporting import strategist_llm_summary\n" not in src
