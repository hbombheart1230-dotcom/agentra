from graphs.nodes.strategist_node import _stage_specific_role_boundary
from libs.runtime.strategist.llm.stage_prompt_contracts import stage_specific_role_boundary


def test_selected_symbol_exact_owner_wrapper_parity():
    assert _stage_specific_role_boundary("selected_symbol_tactical_refresh") == stage_specific_role_boundary("selected_symbol_tactical_refresh")
    assert "do not approve orders" in stage_specific_role_boundary("selected_symbol_tactical_refresh")


def test_hold_and_eod_and_default_boundaries():
    assert "hard exit authority" in stage_specific_role_boundary("stale_intraday_hold_review")
    assert "deterministic closeout" in stage_specific_role_boundary("end_of_day_carry_review")
    assert _stage_specific_role_boundary("") == "Do not select final stock and do not produce order instructions. "
