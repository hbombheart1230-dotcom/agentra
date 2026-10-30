from graphs.nodes import strategist_node as facade
from libs.runtime.strategist.llm.adjustment_directives import _normalize_rejected_strategy_reasons_r3_impl as wrapper
from libs.runtime.strategist.llm.adjustment_directives_normalize_rejected_strategy_reasons_ import _normalize_rejected_strategy_reasons_r3_impl as owner


def _strategies():
    return list(facade._TACTICAL_STRATEGIES)


def test_direct_canonical_reasons_cap_and_wrapper_parity():
    strategies = _strategies(); selected = strategies[0]
    raw = {name: name for name in strategies[1:8]}
    expected = owner(raw, tactical_strategy=selected, strategy_scores={}, facade=facade)
    assert wrapper(raw, tactical_strategy=selected, strategy_scores={}, facade=facade) == expected
    assert len(expected) <= 6 and selected not in expected


def test_skip_and_score_fallback_top4_boundary():
    strategies = _strategies(); selected = strategies[0]
    scores = {name: 0.5 for name in strategies[1:7]}; scores[selected] = 0.5
    result = owner({selected: "no", "bogus": "no", strategies[1]: ""}, tactical_strategy=selected, strategy_scores=scores, facade=facade)
    assert len(result) <= 4
    assert set(result.values()) == {"score_below_selected_tactical_strategy"}
