import pytest
from types import SimpleNamespace
from libs.contracts.agent_output_parts.commander_shadow_advice_extended import llm_call_advice

@pytest.mark.parametrize('rec,obs,state,expected', [
    ('SKIP', {'market_changed': False, 'last_llm_status': 'error'}, {'strategist_llm': {'blocked': True}}, 'SKIP'),
    ('RUN', {}, {'strategist_llm': {'blocked': True}}, 'RETRY_MINIMAL'),
    ('RUN', {'last_llm_status': 'repaired'}, {}, 'RETRY_COMPACT'),
    ('RUN', {}, {'strategist_llm': None}, 'ALLOW'),
])
def test_precedence(rec, obs, state, expected):
    seen = []
    facade = SimpleNamespace(_dict=lambda x: seen.append(x) or (x if isinstance(x, dict) else {}))
    before = repr((obs, state))
    if not (llm_call_advice(strategist_action_recommendation=rec, observations=obs, state=state, facade=facade) == expected): raise AssertionError('failed: test_p15_shadow_llm_call_advice_owner')
    if not (repr((obs, state)) == before): raise AssertionError('failed: test_p15_shadow_llm_call_advice_owner')
    if not (len(seen) == 1): raise AssertionError('failed: test_p15_shadow_llm_call_advice_owner')
