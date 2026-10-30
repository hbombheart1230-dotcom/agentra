from graphs.nodes.strategist_node import _stage_specific_task_requirement
from libs.runtime.strategist.llm.stage_prompt_contracts import stage_specific_task_requirement


def test_stage2_exact_owner_wrapper_parity():
    assert _stage_specific_task_requirement("selected_symbol_tactical_refresh") == stage_specific_task_requirement("selected_symbol_tactical_refresh")
    assert "target_rank" in stage_specific_task_requirement("selected_symbol_tactical_refresh")


def test_stage3_stage4_default_requirements():
    assert "same-session" in stage_specific_task_requirement("stale_intraday_hold_review")
    assert "portfolio_level_decision" in stage_specific_task_requirement("end_of_day_carry_review")
    assert "exactly ONE playbook" in stage_specific_task_requirement(None)
