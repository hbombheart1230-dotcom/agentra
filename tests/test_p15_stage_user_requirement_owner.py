from graphs.nodes.strategist_node import _stage_specific_user_requirement
from libs.runtime.strategist.llm.stage_prompt_contracts import stage_specific_user_requirement


def test_stage2_exact_owner_wrapper_parity():
    assert _stage_specific_user_requirement("selected_symbol_tactical_refresh") == stage_specific_user_requirement("selected_symbol_tactical_refresh")
    assert "direct BUY/SELL" in stage_specific_user_requirement("selected_symbol_tactical_refresh")


def test_stage3_stage4_default_user_requirements():
    assert "Do not output a direct SELL order" in stage_specific_user_requirement("stale_intraday_hold_review")
    assert "Do not bypass hard closeout" in stage_specific_user_requirement("end_of_day_carry_review")
    assert "strategy_adjustment_directives" in stage_specific_user_requirement("unknown")
