import pytest
from libs.contracts.agent_output_parts.commander_shadow_advice_extended import recommendation_gap

@pytest.mark.parametrize('rec,llm,runtime,expected', [
    ('SKIP', 'SKIP', {'strategist_executed': True, 'llm_called_by_strategist': True}, 'strategist_ran_despite_skip_recommendation'),
    ('RUN', 'ALLOW', {'strategist_executed': False}, 'strategist_not_run_despite_refresh_recommendation'),
    ('SKIP', 'SKIP', {'strategist_executed': None, 'llm_called_by_strategist': True}, 'llm_called_despite_skip_advice'),
    ('RUN', 'ALLOW', {'strategist_executed': True, 'llm_called_by_strategist': False}, 'llm_not_called_despite_refresh_advice'),
    ('RUN', 'ALLOW', {'strategist_executed': None, 'llm_called_by_strategist': None}, 'aligned'),
])
def test_boolean_identity(rec, llm, runtime, expected):
    if not (recommendation_gap(strategist_action_recommendation=rec, llm_call_advice=llm, actual_runtime=runtime, facade=None) == expected): raise AssertionError('failed: test_p15_shadow_recommendation_gap_owner')
