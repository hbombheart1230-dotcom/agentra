from types import SimpleNamespace
from libs.contracts.agent_output_parts.commander_shadow_assessments import pre_strategist_snapshot

def test_key_order_alias_and_patch():
    calls = []
    facade = SimpleNamespace(_dict=lambda x: x if isinstance(x, dict) else {}, _clip=lambda value, max_len: calls.append(max_len) or str(value or '')[:max_len])
    state = {'commander_shadow_runtime': {'prior_context': {'selected_symbol': 'X'*30, 'playbook': 'P'*50}}}
    delta = {'signal_changed': True}
    result = pre_strategist_snapshot(state=state, observations={'market_changed': False, 'repeated_same_context': True}, context_delta_summary=delta, strategist_action_recommendation='SKIP', llm_call_advice='SKIP', facade=facade)
    if not (list(result) == ['market_changed', 'repeated_same_context', 'last_llm_status', 'prior_symbol', 'prior_playbook', 'strategist_action_recommendation', 'llm_call_advice', 'reason']): raise AssertionError('failed: test_p15_shadow_pre_strategist_owner')
    if not (result['prior_symbol'] == 'X'*24 and result['prior_playbook'] == 'P'*40): raise AssertionError('failed: test_p15_shadow_pre_strategist_owner')
    if not (result['reason'] == 'context_delta=True market_changed=False repeated=True'): raise AssertionError('failed: test_p15_shadow_pre_strategist_owner')
    if not (calls == [24, 40, 180]): raise AssertionError('failed: test_p15_shadow_pre_strategist_owner')

def test_missing_context():
    facade = SimpleNamespace(_dict=lambda x: x if isinstance(x, dict) else {}, _clip=lambda value, max_len: str(value or '')[:max_len])
    result = pre_strategist_snapshot(state={}, observations={}, context_delta_summary={}, strategist_action_recommendation='RUN', llm_call_advice='ALLOW', facade=facade)
    if not (result['prior_symbol'] == '' and result['last_llm_status'] is None): raise AssertionError('failed: test_p15_shadow_pre_strategist_owner')
