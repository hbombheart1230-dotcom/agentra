from types import SimpleNamespace
from graphs.nodes import strategist_node as facade
from libs.runtime.strategist.llm.adjustment_directives import _infer_policy_adjustment_direction_r3_impl as wrapper
from libs.runtime.strategist.llm.adjustment_directives_infer_policy_adjustment_direction_r3 import _infer_policy_adjustment_direction_r3_impl as owner


def test_tighten_relax_and_wrapper_owner_parity():
    baseline, current = {"volume_ratio_min": 1}, {"volume_ratio_min": 2}
    assert wrapper(baseline, current, facade=facade) == owner(baseline, current, facade=facade) == "tighten"
    assert owner({"pullback_max_pct": 2}, {"pullback_max_pct": 3}, facade=facade) == "relax"


def test_mixed_none_special_zero_and_malformed_parity():
    assert owner({"volume_ratio_min": 1, "pullback_max_pct": 2}, {"volume_ratio_min": 2, "pullback_max_pct": 3}, facade=facade) == "mixed"
    assert owner({}, {}, facade=facade) == "none"
    assert owner({"min_extended_from_vwap_pct": 0}, {"min_extended_from_vwap_pct": 1}, facade=facade) == "tighten"
    try: owner({"volume_ratio_min": "x"}, {"volume_ratio_min": 1}, facade=facade)
    except ValueError: pass
    else: raise AssertionError("expected ValueError")
